# Startup error repair (Victoria 3 1.13.11)

This patch addresses the uploaded 10 October 2026 startup logs. Start a new
1836 game when testing: existing saves retain their initialized states and pops.

## Province history

- Move 323 unique provinces into the regions that contain them in `map_data`.
- Remove 508 duplicate ownership entries and the Gansu lake `xBD5671`.
- Fill four omitted land provinces in the otherwise entirely BIC-owned Assam.
- Retain 40,717 unique land assignments.

When a misplaced entry conflicts with an entry in its correct region, retain the
correct-region entry. For conflicting entries within one region, retain the
smaller explicit partition, preserving native enclaves covered by large colonial
lists; source order breaks equal-size ties. Every conflicting owner choice and
every province moved is recorded in `sources/doi_startup_provinces.json`.
This resolves malformed overlapping definitions; the remaining political-map
decisions from the map-consolidation audit are still outstanding.

## Population and buildings

Retarget 22 stale population scopes and four building scopes. Absorbed Gujarat
tags map to BER, while KUT retains its existing population. In Rajputana, Alwar
and Gwalior's old scopes map to JAI, Kota and Indore to MEW, and the former BIC
scope to JOD. These are explicit demographic allocation choices for review.

Puerto Rico uses SPA; Amazonas uses BRZ instead of PRA; Mato Grosso's former
BOL population goes to BRZ; Hokkaido's former EZO/Ainu population goes to AIN;
Chechen/Circassian scopes use RUS. Former Danish Togo history follows its
province into the Gold Coast. Former Dutch West Indies scopes use VNZ.

Where province regrouping creates a populated country's new partition with no
population history, divide existing source populations by province counts:
Khiva/Uralsk, Zanzibar/Kenya, North Angola/South Cameroon. For Japanese
Micronesia, divide the existing Micronesian population across four MCR provinces
and one JAP province. These approximations are recorded in
`sources/doi_startup_history.json`; they preserve each explicit culture,
religion and pop-type total rather than inventing additional population.

The recorded population remains **1,037,496,890**, excluding commented template
examples. Remove the state-creation blocks accidentally pasted into Sakhalin's
population file; they were not population data.

Fix dangling building ownership locations, including MOL/ITA ownership in
Austria, Balkan ownership in Eastern Thrace and WUR ownership in Schleswig.
Retain a Polish-owned Hungarian building's foreign ownership by locating its
owning building in Mazovia. Replace ownership by nonexistent William Cramp/EIC
company instances with domestic financial-district ownership, preserving levels.

Use rice farms in Piedmont; move West Galicia's unsupported sulfur mine to Upper
Silesia and unsupported northern Chinese tea plantations to Hunan. Split the
Japanese Hokkaido fishing allocation so its small partition has one level;
place the other level in the Ainu partition, with simple fishing there.
No mineral or agricultural resource definitions are expanded.

## Scripts and starting relationships

- Use `create_bidirectional_truce` in the two Polish events, following the
  syntax already used in the repository's starting truces.
- Replace the unsupported `any_scope_state` filter with a regular owner test.
- Dispatch French succession through a custom on-action; evaluate the monarch
  condition in character scope and write the hook with UTF-8 BOM.
- Rename objective localization files with a DOI prefix so vanilla objective
  localization can load; remove three duplicated character-name entries.
- Correct the five logged illegal homesteading starts to Tenant Farmers, as
  recommended by the engine. Give HAN percussion-cap technology, KAZ Standing
  Army and WLO Enclosure for their existing buildings. Use the engine-suggested
  Isolationism/Right of Assembly alternatives for KAZ and WLO.
- Remove whole treaties involving absent MLD, HAM and ORA.
- Move Britain's two invalid overseas army HQs to Western Europe; recruit Italy's
  Savoy/Provence units from Piedmont, Russia's Kiev units from Kursk and UBD's
  Courland unit from Riga. Preserve unit counts.
- Map Cuba and Sierra Leone to colonies, and North/South Peru to protectorates.
  These replace puppet pacts explicitly rejected by the uploaded log and need
  an in-game persistence check. Keep the tested Balkan protectorates unchanged.

## Validation

Run from the repository root:

```sh
python tools/validate_startup.py
python tools/validate_subjects.py
python tools/audit_map.py
```

The global check verifies province uniqueness, land coverage, region membership,
population/building scopes, building-owner partitions, supported resource types,
the recorded population total, and the recruitment/HQ references in the military
files present in this repository. The nine original transfers and 28 canon
relationships also pass their checks. Population culture/religion/type totals
were compared with the merged base and remain unchanged; complete history and
on-action braces were checked. Static checks do not execute Victoria 3 scripts.

## Remaining source and in-game checks

There are 17 partitions without supplied population data: Dahomey/BRG,
East Sahara/TUG, Florida/SML, Malaya/GBR, Oryol/RUS, Semnan/PER,
Sakhalin/AIN/ALK/EZO/SKH/ULT, and Senegal/BND/DIO/KBU/POR/SIL/SRR.
They need demographic source data; the validator reports them separately.

These logged files are inherited from the game and absent from the repository.
Their **1.13.11 game copies** are needed for precise overrides that preserve the
rest of their content:

- `common/history/military_formations/03_military_formations_north_africa.txt`
- `common/history/military_formations/04_military_formations_middle_east.txt`
- `common/history/military_formations/05_military_formations_india.txt`
- `common/history/military_formations/06_military_formations_asia.txt`
- `common/history/military_deployments/00_military_deployments.txt`
- `common/history/lobbies/00_lobbies.txt`
- `common/journal_entries/00_german_unification.txt`
- `common/laws/00_navy_model.txt`
- Character history for Austria and the eight charter-company rulers named in
  the log (QUE, ONT, NBS, ORG, NSW, WAS, SAS, TAS).

Outstanding examples include Egypt's missing Near East HQ and `soliman_gen`,
Ottoman units in independent Balkan states, BIC units in Gujarat, Patiala units
in Delhi, Qing units in transferred Manchuria, inherited war deployments,
absent-country lobbies and the German journal entry. The inherited TUR/MON
embargo and missing ATL country definition also require their source definitions.

Converter game-rule errors are not referenced by repository scripts and need
a separate check of the active mod set/settings. Missing hub/tooltips and
remaining character-role issues need a fresh log after this patch.
