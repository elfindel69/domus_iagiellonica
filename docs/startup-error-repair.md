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

The first-pass recorded population remained **1,037,496,890**, excluding commented template
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
  Savoy/Provence units from Piedmont, Russia's Kiev units from Tambov and UBD's
  Courland unit from Riga. Preserve unit counts.
- Map Cuba and Sierra Leone to colonies, and North/South Peru to colonies.
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

## Follow-up from the new logs and vanilla sources

The fresh log records 73 script errors, down from 321, with zero state-creation
or population-creation errors. These counts describe the tested first pass;
the changes below still require a new-game test.

Adapt four supplied vanilla military history files to the current ownership map.
Egypt uses Nile Basin HQs and recruits its former Syrian units in Upper Egypt
and Sinai; the Soliman template receives the same HQ override. Ottoman Balkan
units recruit in owned Anatolian states, BIC Gujarat units in Bombay, Patiala
Delhi units in Hill Punjab, and Qing Outer Manchuria units in Northern Manchuria.
All army and ship counts by country and type are preserved. Move Russia's
relocated corps from Kursk to Tambov to avoid the logged 25-barracks cap.

Retain vanilla war deployment content behind country-level war guards. Resolve
fronts optionally and run teleport effects in formation scope. Retarget Prussian
lobbies and German unification references to Brandenburg; the papal lobby
references Italy. Guard lobby targets against missing countries.

Correct Piedmont rice-farm methods to the rice-specific farming method and
Disabled Tools. Give BRN Enclosure/Standing Army, and ACH/WLO Standing Army.
Remove Serbia's liberty adjustment because it starts independent. Peru's colonial
country types still reject protectorate pacts in the new log, so try colonies,
as already accepted for Cuba and Sierra Leone; verify Peru's persistence in game.

Create trade centers at the 13 partitions required by the existing startup trade
adjustments. Restore supplied vanilla levels/ownership for Ingria and both
Guangdong partitions; the other ten centers receive one starting level, a
minimal seeding choice requiring review. Preserve all 18 trade adjustments.
Remove the 51 logged duplicate objective keys from the DOI localization copies,
add the missing subject-transfer tooltip in three languages, and correct the
logged UTF-8 BOM warnings in repository files.

For the eight logged colonial governors, override `ig_leader = no` during
creation while retaining their templates, ruler role and governor-term variables.
The Austrian creation error is at line 71, which creates Haynau. The previous
note attributed it to Doblhoff-Dier incorrectly; his creation is at line 62.

Restore 17 missing population partitions from the supplied vanilla population
files: Dahomey/BRG, East Sahara/TUG, Florida/SML, Semnan/PER, five Sakhalin
partitions, six Senegal partitions, Malaya/GBR and Oryol/RUS. They add **4,366,004** people, bringing the
recorded total to **1,041,862,894** without modifying existing populations.
Source hashes, partition totals and military baselines are recorded in
`sources/doi_startup_followup.json`. The supplied building files are used only
for the missing trade-center records; existing mod buildings are retained.

## Remaining source and in-game checks

All 17 previously missing population partitions now have supplied source records.
The validator reports no population gaps.

## Current-log follow-up

The next uploaded 1.13.11 run records **11 script errors**, down from 73.
It no longer reports the military, trade, governor-role or subject-pact errors
addressed in the previous follow-up. This confirms initialization, not long-term
subject stability or every later event path.

Adapt the supplied global history to make the former Dai Nam partition in Laos
optional; do not apply its recently-conquered modifier to independent Laos.
Use optional province-to-state scopes for Fernando Po and Sao Tome naming, so
naming during initialization can skip a partition that is not yet available.
Preserve cultural state names in Posen, Wallonia, Rhineland and North Rhine,
but reset their hubs to localized defaults in the four branches that fail bulk
cultural hub renaming on this legacy map. Cultural hub names can be restored
when matching localization for these map definitions is supplied.

Remove only the four Russian market-owner localization alternatives for
undefined ALA/ATL/SLS/BNN. Remove Atlantis alternatives from the supplied Cuba
event, button and progress-bar scripts; retain the Cuba paths and other content.
Suppress inherited Bannock/Salish country/population startup files because those
tags are undefined in this mod. Correct France's last stale Prussian relation
target to Brandenburg; it was the only absent target for an active country in
repository relation history. Add localization for the mod's Shroder and Schimmer
character surnames. Give Haynau an explicit Southern Europe HQ, which Austria
can support with its current holdings, retaining his template and all other
Austrian character history. The supplied `country_aus.txt` confirms that his
template defaults to `region_eastern_europe`, where Austria owns no states.
The override uses `region_southern_europe`, containing Austrian Istria and
South Tyrol. The source diagnosis is confirmed; creation still needs another
in-game test. Source hashes and compatibility choices are recorded in
`sources/doi_startup_current_errors.json`.

These changes need another new-game log. Remaining items still require source
files or an active-mod/settings check:

- The inherited TUR/MON embargo and ATL country-formation/creation definitions.
- The Kiel canal definition and its adjacent sea endpoints.
- The supplied log's unlocalized GUI text at `gui/custom_tooltip.gui:8801`.
- Converter game-rule settings and variable warnings with no repository setters.

The provided dynamic-name dispatcher needs no override; its called regional
scripts contain the failures. The supplied navy-model law likewise remains
unchanged. Static validation cannot execute Victoria 3 scripts.
