#!/usr/bin/env python3
"""Validate repository startup history against its map; no game install required."""
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import sys

from audit_map import blocks, history, validate

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return path.read_text(encoding='utf-8-sig')


def check(root=ROOT):
    errors = []
    owners = history(read(root/'common/history/states/00_states.txt'))
    active = {tag for parts in owners.values() for tag, ps in parts if ps}
    owned = {state: {tag for tag, ps in parts if ps} for state, parts in owners.items()}
    regions, province_regions, land = {}, {}, set()
    for path in (root/'map_data/state_regions').glob('*.txt'):
        for state, _, _, body in blocks(read(path), r'STATE_[A-Z_]+'):
            regions[state] = body
            match = re.search(r'\bprovinces\s*=\s*\{([^}]*)\}', body)
            if match:
                for province in re.findall(r'x[0-9A-Fa-f]{6}', match[1]):
                    key = province.upper()
                    if key in province_regions:
                        errors.append(f'{province}: multiple map regions')
                    province_regions[key] = state
                    if re.search(r'\barable_land\s*=', body):
                        land.add(key)
    assigned = set()
    for state, parts in owners.items():
        for tag, provinces in parts:
            if not provinces:
                errors.append(f'{state}/{tag}: empty partition')
            for province in provinces:
                key = province.upper()
                if province_regions.get(key) != state:
                    errors.append(f'{state}/{tag}/{province}: wrong or missing map region')
                if key in assigned:
                    errors.append(f'{province}: duplicate assignment')
                assigned.add(key)
    for province in sorted(land-assigned):
        errors.append(f'{province}: unassigned land in {province_regions[province]}')

    populations = set()
    population_total = 0
    building_levels = Counter()
    for kind in ('pops', 'buildings'):
        for path in (root/'common/history'/kind).glob('*.txt'):
            text = read(path)
            if kind == 'pops' and re.search(r'\bcreate_state\s*=', text):
                errors.append(f'{path.name}: state creation in population history')
            for sn, _, _, body in blocks(text, r's:STATE_[A-Z_]+'):
                state = sn[2:]
                for rs, _, _, part in blocks(body, r'region_state:\w+'):
                    tag = rs.split(':')[1]
                    if tag not in owned.get(state, set()):
                        errors.append(f'{path.name}/{state}/{tag}: invalid owner scope')
                    if kind == 'pops':
                        if list(blocks(part, 'create_pop')):
                            populations.add((state, tag))
                        population_total += sum(int(m[1]) for m in re.finditer(r'\bsize\s*=\s*(\d+)', part))
                    else:
                        for _, _, _, building in blocks(part, 'create_building'):
                            match = re.search(r'\bbuilding\s*=\s*"?(building_\w+)', building)
                            if not match:
                                errors.append(f'{path.name}/{state}/{tag}: missing building type')
                                continue
                            kind_name = match[1]
                            levels = re.findall(r'\blevels\s*=\s*(\d+)', building)
                            building_levels[kind_name] += sum(map(int, levels)) if levels else 1
                            if any(x in kind_name for x in ('_farm', '_plantation', '_mine', '_logging', '_fishing', '_whaling')) and kind_name not in regions.get(state, ''):
                                errors.append(f'{state}: unsupported {kind_name}')
                            for _, _, _, ownership in blocks(building, 'building'):
                                country = re.search(r'country\s*=\s*"?c:(\w+)', ownership)
                                region = re.search(r'region\s*=\s*"?(STATE_\w+)', ownership)
                                if country and region and country[1] not in owned.get(region[1], set()):
                                    errors.append(f'{state}: ownership refers to nonexistent {region[1]}/{country[1]} partition')

    manifest = json.loads(read(root/'docs/sources/doi_startup_history.json'))
    if population_total != manifest['population_total']:
        errors.append(f'Population changed: {population_total} != {manifest["population_total"]}')

    strategic = {}
    for path in (root/'common/strategic_regions').glob('*.txt'):
        for region, _, _, body in blocks(read(path), r'region_[a-z_]+'):
            states = re.search(r'\bstates\s*=\s*\{([^}]*)\}', body)
            if states:
                strategic[region] = re.findall(r'STATE_\w+', states[1])
    for path in (root/'common/history/military_formations').glob('*.txt'):
        for country, _, _, body in blocks(read(path), r'c:\w+\s*\?'):
            tag = country.split(':')[1].split()[0]
            if tag not in active:
                continue
            for _, _, _, formation in blocks(body, 'create_military_formation'):
                hq = re.search(r'hq_region\s*=\s*sr:(\w+)', formation)
                if hq and not any(tag in owned.get(state, set()) for state in strategic.get(hq[1], [])):
                    errors.append(f'{tag}: no owned land for HQ {hq[1]}')
                for _, _, _, unit in blocks(formation, r'\b(?:combat_unit|ship)'):
                    state = re.search(r'state_region\s*=\s*s:(STATE_\w+)', unit)
                    if state and tag not in owned.get(state[1], set()):
                        errors.append(f'{tag}: recruitment from unowned {state[1]}')
    followup_path = root/'docs/sources/doi_startup_followup.json'
    if followup_path.exists():
        followup = json.loads(read(followup_path))
        for filename, baseline in followup['military_unit_baselines'].items():
            counts = Counter()
            for country, _, _, body in blocks(read(root/'common/history/military_formations'/filename), r'c:\w+\s*\?'):
                tag = country.split(':')[1].split()[0]
                for _, _, _, unit in blocks(body, r'\b(?:combat_unit|ship)'):
                    kind = re.search(r'type\s*=\s*(\w+:\w+)', unit)
                    amount = re.search(r'count\s*=\s*(\d+)', unit)
                    if kind and amount:
                        counts[(tag, kind[1])] += int(amount[1])
            expected = Counter({(x['country'], x['type']): x['count'] for x in baseline})
            if counts != expected:
                errors.append(f'{filename}: military unit totals changed')
        centers = set()
        for path in (root/'common/history/buildings').glob('*.txt'):
            for sn, _, _, body in blocks(read(path), r's:STATE_[A-Z_]+'):
                for rs, _, _, part in blocks(body, r'region_state:\w+'):
                    if re.search(r'building\s*=\s*"?building_trade_center', part):
                        centers.add((sn[2:], rs.split(':')[1]))
        for center in followup['trade_centers']:
            key = (center['state'], center['country'])
            if key not in centers:
                errors.append(f'{key}: missing starting trade center')
        for path in (root/'common/history/characters').glob('*.txt'):
            for country, _, _, body in blocks(read(path), r'c:\w+\s*\?'):
                tag = country.split(':')[1].split()[0]
                if tag in followup['character_role_overrides']:
                    first = next(blocks(body, 'create_character'))[3]
                    if not re.search(r'ig_leader\s*=\s*no', first):
                        errors.append(f'{tag}: governor still has inherited IG leader role')
        for path in (root/'common/history/military_deployments').glob('*.txt'):
            text = read(path)
            if re.search(r'\?\s+=', text):
                errors.append(f'{path.name}: malformed optional scope operator')
            for front, _, _, body in blocks(text, r'p:x[0-9A-Fa-f]+\.front\s*\?'):
                if not list(blocks(body, 'prev')):
                    errors.append(f'{front}: teleport effect must run in formation scope')
    current_path = root/'docs/sources/doi_startup_current_errors.json'
    if current_path.exists():
        current = json.loads(read(current_path))
        paths = current['cuba_files'] + ['common/customizable_localization/99_ru_custom_loc.txt']
        for filename in paths:
            if re.search(r'c:(ALA|ATL|BNN|SLS)\b', read(root/filename)):
                errors.append(f'{filename}: reference to undefined country')
        africa = read(root/'common/scripted_effects/00_dynamic_state_names_africa.txt')
        for province in current['province_scope_guards']:
            if f'p:{province}.state.owner' in africa or not re.search(r'p:'+province+r'\.state\s*\?=', africa):
                errors.append(f'{province}: missing optional state scope')
        europe = read(root/'common/scripted_effects/00_dynamic_state_names_europe.txt')
        for name, _, _, body in blocks(europe, r'STATE_\w+_state_name_assign'):
            if name in current['hub_default_fallbacks'] and re.search(r'set_hub_names\s*=\s*(polish|french)', body):
                errors.append(f'{name}: unresolved bulk hub localization')
        for override in current.get('commander_hq_overrides', []):
            path = root/'common/history/characters/aus - austria.txt'
            candidates = [body for _, _, _, body in blocks(read(path), 'create_character')
                          if re.search(r'template\s*=\s*'+override['template']+r'\b', body)]
            if len(candidates) != 1 or not re.search(r'hq\s*=\s*'+override['hq']+r'\b', candidates[0]):
                errors.append(f"{override['template']}: missing explicit HQ override")
            if not any(override['country'] in owned.get(state, set()) for state in strategic.get(override['hq'], [])):
                errors.append(f"{override['template']}: no owned land for commander HQ")
        global_history = read(root/'common/history/global/00_global.txt')
        if not re.search(r's:STATE_LAOS\.region_state:DAI\s*\?=', global_history):
            errors.append('Laos/DAI modifier has no optional scope')
        for path in (root/'common/history/diplomacy').glob('*.txt'):
            for country, _, _, body in blocks(read(path), r'c:\w+\s*\?'):
                tag = re.match(r'c:(\w+)', country)[1]
                if tag not in active:
                    continue
                for _, _, _, effect in blocks(body, 'set_relations'):
                    target = re.search(r'country\s*=\s*c:(\w+)', effect)
                    if target and target[1] not in active:
                        errors.append(f'{tag}: relations target {target[1]} does not exist at startup')
    errors += validate(root)
    missing = sorted((state, tag) for state, tags in owned.items() for tag in tags if (state, tag) not in populations)
    known_missing = {tuple(x) for x in manifest['known_missing_population_partitions']}
    for state, tag in sorted(set(missing)-known_missing):
        errors.append(f'{state}/{tag}: new population gap')
    return errors, dict(provinces=len(assigned), population=population_total,
                        missing_population_partitions=missing, building_levels=dict(building_levels))


if __name__ == '__main__':
    errors, summary = check()
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        sys.exit(1)
    print(f'Startup history valid: {summary["provinces"]} unique provinces; {summary["population"]} people preserved.')
    if summary['missing_population_partitions']:
        print('Missing population data (separate content gaps):')
        for state, tag in summary['missing_population_partitions']:
            print(f'  {state}/{tag}')
    else:
        print('All owned state partitions have population records.')
