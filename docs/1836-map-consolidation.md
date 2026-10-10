# DOI 1836 map consolidation

The ownership reference is the supplied `DOI 1836 legend(2).json` and
`DOI 1836 map(2).png`. The legend is retained in
`sources/doi_1836_legend.json`; it assigns map paths, not individual game provinces.
Numeric suffixes in map paths are removed for lookup. The explicit aliases
Burma → Mandalay and Cabo Verde → Cape Verde match the mod's state names.
Other missing or composite names remain unresolved rather than guessed.

## First ownership pass

| State | Previous owner | Corrected owner |
| --- | --- | --- |
| Istria | Italy (`ITA`) | Austria (`AUS`) |
| Åland | Finland (`FIN`) | Sweden (`SWE`) |
| Tonkin | Dai Nam (`DAI`) | Qing China (`CHI`) |
| Altai | Qing China (`CHI`) | Russia (`RUS`) |
| Amur | Qing China (`CHI`) | Russia (`RUS`) |
| Outer Manchuria | Qing China (`CHI`) | Russia (`RUS`) |
| Tuva | Qing China (`CHI`) | Russia (`RUS`) |
| Vrystaat | Oranje (`ORA`) | Dutch South Africa (`SAF`) |

Each transfer keeps its exact province list, population cultures and sizes,
and building levels/production methods. Population and building history scopes
follow the new owner. Domestic building ownership references inside the moved
state follow that owner as well. The source province lists are retained in
`sources/doi_1836_transfers.json` so accidental border changes can be detected.
No military formation in the mod's history directly references these eight
state regions; army recruitment and country activation still need an in-game check.

Åland had two identical population history blocks in the west-European and
Russian population files, each containing 25,800 Swedish and 1,200 Finnish pops.
Keep the west-European block and remove the duplicate Russian block.

## Remaining review

The audit covers 578 distinct label/path assignments. Counts below refer to
assignments, not unique states or provinces:

| Result | Assignments |
| --- | ---: |
| Single-owner match | 429 |
| Shared state explicitly present under multiple map labels | 35 |
| Existing split state under one map label | 46 |
| Aggregate country label | 41 |
| Unresolved state name | 21 |
| Single-owner mismatch awaiting interpretation or data | 6 |

The six outstanding single-owner mismatches are:

- Urmia: Persia → Ottomans on the reference map. No `STATE_URMIA` population
  block exists in the mod. Establish its population history before transferring it.
- Arequipa and Tarapaca: `SPU` territories labeled Bolivia. Resolve the intended
  Peru–Bolivia political/territorial structure before transferring their history.
- Ionian Islands: the map labels Greece, while the mod starts `ION` as a British
  protectorate. Decide whether the map aggregates it with Greece or requires annexation.
- Alto Paraguay: `GNI` decentralized territory labeled Paraguay. Decide the
  intended distinction between claimed land and directly administered land.
- Khuzestan: `ARB` territory labeled Persia. Review Arabistan's intended status
  and history before eliminating its starting territory.

Split-state assignments include Brandenburg/Pomerania, North Rhine/Rhineland,
Schleswig-Holstein, Riga, Guayana, Central Asia and mainland Southeast Asia.
Province-level borders need a specific allocation; map colors alone are not a
province list. Also review existing decentralized territories, treaty ports and
enclaves before treating a single map label as exclusive ownership.

Canada, Australia, India and Peru are aggregate labels for this audit. Their
constituent countries stay separate until their intended setup is resolved.
An aggregate review is not a declaration that all its existing owners are valid.
Uncolored map regions are outside the legend's coverage, not instructions to
delete their countries or ownership.

## Validation

```sh
python3 tools/audit_map.py
python3 tools/audit_map.py --json
python3 tools/validate_subjects.py
git diff --check
```

The map checker verifies the eight moved states' full province sets against
both region definitions and the transfer manifest, checks that their provinces
have exactly one history owner, and checks that each has exactly one population
and building history block under the correct owner. It rejects stale domestic
building ownership references. JSON output exposes every comparison and category.
Unresolved comparisons are reported without failing the corrected-state checks.
This is not a complete Paradox script or game-engine validator.

Start a new campaign and inspect the eight states, their populations and buildings,
plus Qing/Russian recruitment, Austria/Italy, Sweden/Finland and South Africa.
Check for landless Oranje startup effects and inspect the error log. No in-game
test of this map patch has been performed here. The earlier subject setup has
been tested by the user and is retained.
