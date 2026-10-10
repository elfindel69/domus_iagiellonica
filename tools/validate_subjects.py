#!/usr/bin/env python3
"""Check explicit starting subject pacts without needing a Victoria 3 install."""

import argparse
from collections import defaultdict
from pathlib import Path
import re
import sys


SUBJECT_TYPES = {
    "colony", "dominion", "personal_union", "puppet", "protectorate",
    "vassal", "tributary", "chartered_company",
}

# Explicit statuses in Leaders 1836(2).odt. Unlisted relationships are preserved.
EXPECTED = {
    "SAF": ("NET", "dominion"), "MOL": ("PLC", "vassal"),
    "CUB": ("SPA", "puppet"), "NOR": ("SWE", "personal_union"),
    "FIN": ("RUS", "personal_union"), "HAN": ("GBR", "personal_union"),
    "UBD": ("RUS", "puppet"), "ALK": ("RUS", "chartered_company"),
    "BOS": ("AUS", "dominion"), "BUL": ("AUS", "dominion"),
    "WAL": ("AUS", "dominion"), "BRZ": ("POR", "dominion"),
    "TIB": ("CHI", "vassal"), "KOR": ("CHI", "tributary"),
    "EGY": ("TUR", "protectorate"), "TUN": ("TUR", "protectorate"),
    "HDJ": ("TUR", "puppet"), "TRI": ("TUR", "puppet"),
    **{tag: ("GBR", "chartered_company") for tag in
       ("BIC", "HBC", "ORG", "ONT", "QUE", "NSW", "WAS", "SAS", "TAS")},
}

STARTING_LOYALTY = {"MOL", "WAL", "BOS", "BUL"}


def parse(text):
    """Parse the assignment/block subset used by diplomacy history."""
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|#[^\n]*|\?=|=|[{}]|[^\s{}=#]+', text)
    tokens = [token for token in tokens if not token.startswith("#")]
    position = 0

    def block(nested=False):
        nonlocal position
        entries = []
        while position < len(tokens):
            if tokens[position] == "}":
                if not nested:
                    raise ValueError("Unexpected closing brace")
                position += 1
                return entries
            key = tokens[position]
            position += 1
            if position >= len(tokens) or tokens[position] not in ("=", "?="):
                raise ValueError(f"Expected assignment after {key}")
            position += 1
            if position >= len(tokens):
                raise ValueError(f"Missing value for {key}")
            value = tokens[position]
            position += 1
            if value == "{":
                value = block(nested=True)
            elif value == "}":
                raise ValueError(f"Missing value for {key}")
            entries.append((key, value))
        if nested:
            raise ValueError("Unclosed block")
        return entries

    return block()


def validate(text):
    errors = []
    subjects = defaultdict(list)
    liberty_adjustments = defaultdict(list)

    def visit(entries, country=None):
        for key, value in entries:
            if key == "add_liberty_desire" and country in STARTING_LOYALTY:
                liberty_adjustments[country].append(value)
            if not isinstance(value, list):
                continue
            if key == "create_diplomatic_pact":
                fields = dict(value)
                kind = fields.get("type")
                if kind in SUBJECT_TYPES:
                    target = fields.get("country", "")
                    if not country or not target.startswith("c:"):
                        errors.append("Subject pact is missing a country scope or target")
                    else:
                        subjects[target[2:]].append((country, kind))
                continue
            visit(value, key[2:] if key.startswith("c:") else country)

    visit(parse(text))
    for subject, pacts in subjects.items():
        if len(pacts) > 1:
            errors.append(f"{subject}: multiple starting subject pacts: {pacts}")
    for subject, expected in EXPECTED.items():
        if subjects[subject] != [expected]:
            errors.append(f"{subject}: expected {expected}, found {subjects[subject]}")
    if subjects.get("ALB"):
        errors.append(f"ALB: should start independent, found {subjects['ALB']}")
    for subject in sorted(STARTING_LOYALTY):
        values = liberty_adjustments[subject]
        if len(values) != 1 or not re.fullmatch(r"-\d+(?:\.\d+)?", str(values[0])):
            errors.append(f"{subject}: expected one negative starting liberty adjustment, found {values}")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, default=
                        Path(__file__).resolve().parents[1] /
                        "common/history/diplomacy/00_subject_relationships.txt")
    args = parser.parse_args()
    try:
        errors = validate(args.path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        errors = [str(exc)]
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Subject history valid: {len(EXPECTED)} canon relationships; Albania independent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
