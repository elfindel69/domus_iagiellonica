#!/usr/bin/env python3
"""Compare the DOI map legend with province ownership; never infer split borders."""

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
COUNTRIES = dict(zip(
    ['Alaska','Albania','Argentina','Austrian Empire','Baden','Bavaria','Bolivia',
     'Bosnia','Brandenburg','Brazil','Bukhara','Bulgaria','Burma','Cambodia',
     'Chiang Mai','Chile','Colombia','Constantine','Cuba','Dai Nam','Denmark',
     'Ecuador','Egypt','Finland','France','GBR','Greece','Haiti','Hannover',
     'Hedjaz','Hesse','Holstein','Italy','Jabal Shammar','Japan','Kazakhstan',
     'Khiva','Kishi Zhuz','Kokand','Korea','Laos','Liberia','Madagascar','Mascara',
     'Mexico','Moldova','Montenegro','Morocco','Nejd','Netherlands','Norway',
     'Oregon','Orta Zhuz','Ottomans','Paraguay','Persia','PLC','Portugal',
     'Qing China','Russia','SAF','Saxony','Schlesvig','Serbia','Siam','Spain',
     'Sweden','Switzerland','Tibet','Tripolitania','Tunisia','UBD','Uly Zhuz',
     'Uruguay','USA','USCA','Venezuela','Wallachia','Wurttemberg'],
    ['ALK','ALB','ARG','AUS','BAD','BAV','BOL','BOS','BRB','BRZ','BUK','BUL',
     'BUR','CAM','CMI','CHL','CLM','CON','CUB','DAI','DEN','ECU','EGY','FIN',
     'FRA','GBR','GRE','HAI','HAN','HDJ','HES','HOL','ITA','JAB','JAP','KAZ',
     'KHI','KZH','KOK','KOR','LUA','LIB','MAD','MAS','MEX','MOL','MON','MOR',
     'NEJ','NET','NOR','ORG','OZH','TUR','PRG','PER','PLC','POR','CHI','RUS',
     'SAF','SAX','SCH','SER','SIA','SPA','SWE','SWI','TIB','TRI','TUN','UBD',
     'UZH','URU','USA','UCA','VNZ','WAL','WUR']))
AGGREGATES = {'Australia', 'Canada', 'India', 'Peru'}
ALIASES = {'BURMA': 'MANDALAY', 'CABO_VERDE': 'CAPE_VERDE'}


def blocks(text, pattern):
    """Yield named blocks with byte-character spans, ignoring quoted/comment braces."""
    ignored = re.compile(r'#[^\n]*|"(?:\\.|[^"\\])*"')
    masked = ignored.sub(lambda m: ' ' * len(m.group()), text)
    for match in re.finditer(pattern + r'\s*=\s*\{', masked):
        depth, end = 1, match.end()
        while depth and end < len(masked):
            depth += (masked[end] == '{') - (masked[end] == '}')
            end += 1
        if depth:
            raise ValueError('Unclosed block: ' + match.group())
        yield match.group().split('=')[0].strip(), match.start(), end, text[match.end():end-1]


def history(text):
    result = defaultdict(list)
    for state, _, _, body in blocks(text, r's:STATE_[A-Z_]+'):
        for _, _, _, part in blocks(body, 'create_state'):
            owner = re.search(r'country\s*=\s*"?c:(\w+)', part)
            provinces = re.search(r'owned_provinces\s*=\s*\{([^}]*)\}', part)
            if not owner or not provinces:
                raise ValueError('Incomplete create_state: ' + state)
            result[state[2:]].append((owner[1], re.findall(r'x[0-9A-Fa-f]{6}', provinces[1])))
    return result


def audit(root=ROOT):
    legend = json.loads((root/'docs/sources/doi_1836_legend.json').read_text())
    owners = history((root/'common/history/states/00_states.txt').read_text(encoding='utf-8-sig'))
    entries, labels_by_state = [], defaultdict(set)
    for group in legend['groups'].values():
        for path in dict.fromkeys(group['paths']):
            state = re.sub(r'\d+$', '', path).upper()
            state = 'STATE_' + ALIASES.get(state, state)
            labels_by_state[state].add(group['label'])
            entries.append((group['label'], path, state))
    rows = []
    for label, path, state in entries:
        actual = sorted({tag for tag, _ in owners.get(state, [])})
        if not actual:
            status = 'unresolved_state_name'
        elif label in AGGREGATES:
            status = 'aggregate_review'
        elif len(labels_by_state[state]) > 1:
            status = 'map_split_review'
        elif len(actual) > 1:
            status = 'existing_split_review'
        elif label not in COUNTRIES:
            status = 'unresolved_country'
        elif actual != [COUNTRIES[label]]:
            status = 'owner_mismatch'
        else:
            status = 'aligned'
        rows.append(dict(label=label, map_path=path, state=state,
                         expected_tag=COUNTRIES.get(label), owners=actual, status=status))
    return rows


def validate(root=ROOT):
    """Validate corrected province sets and population/building ownership scopes."""
    errors = []
    owners = history((root/'common/history/states/00_states.txt').read_text(encoding='utf-8-sig'))
    manifest = json.loads((root/'docs/sources/doi_1836_transfers.json').read_text())
    regions = {}
    for path in (root/'map_data/state_regions').glob('*.txt'):
        for state, _, _, body in blocks(path.read_text(encoding='utf-8-sig'), r'STATE_[A-Z_]+'):
            match = re.search(r'\bprovinces\s*=\s*\{([^}]*)\}', body)
            if match:
                regions[state] = set(re.findall(r'x[0-9A-Fa-f]{6}', match[1]))
    for state, transfer in manifest.items():
        parts = owners.get(state, [])
        if len(parts) != 1 or parts[0][0] != transfer['to']:
            errors.append(f'{state}: expected sole owner {transfer["to"]}, found {parts}')
            continue
        provinces = parts[0][1]
        if len(provinces) != len(set(provinces)) or set(provinces) != regions.get(state):
            errors.append(f'{state}: ownership does not cover its exact region province set')
        if set(provinces) != set(transfer['provinces']):
            errors.append(f'{state}: transfer changed the original province allocation')
    assigned = defaultdict(list)
    for state, parts in owners.items():
        for owner, provinces in parts:
            for province in provinces:
                assigned[province].append((state, owner))
    moved = {p for t in manifest.values() for p in t['provinces']}
    for province in sorted(moved):
        if len(assigned[province]) != 1:
            errors.append(f'{province}: multiple history owners {assigned[province]}')
    for kind in ('pops', 'buildings'):
        seen = Counter()
        for path in (root/'common/history'/kind).glob('*.txt'):
            for state, _, _, body in blocks(path.read_text(encoding='utf-8-sig'), r's:STATE_[A-Z_]+'):
                state = state[2:]
                if state not in manifest:
                    continue
                seen[state] += 1
                scopes = re.findall(r'region_state:(\w+)\s*=', body)
                if scopes != [manifest[state]['to']]:
                    errors.append(f'{path.name}/{state}: stale or duplicate {kind} owner scopes {scopes}')
                references = re.findall(r'\bcountry\s*=\s*"?c:(\w+)', body)
                if manifest[state]['from'] in references:
                    errors.append(f'{path.name}/{state}: stale domestic building ownership')
        for state in manifest:
            if seen[state] != 1:
                errors.append(f'{state}: expected one {kind} history block, found {seen[state]}')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', action='store_true', help='Print the complete comparison as JSON')
    args = parser.parse_args()
    rows, errors = audit(), validate()
    if args.json:
        print(json.dumps({'summary':dict(Counter(r['status'] for r in rows)),
                          'rows':rows, 'validation_errors':errors}, indent=2))
    else:
        print('Map audit:', dict(Counter(r['status'] for r in rows)))
        for row in rows:
            if row['status'] == 'owner_mismatch':
                print(f'{row["state"]}: {row["owners"]} -> {row["expected_tag"]}')
        print('\n'.join(errors) if errors else 'Transferred province/pop/building history valid.')
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
