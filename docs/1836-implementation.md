# DOI 1836 implementation

## Sources and compatibility

This pass uses the supplied `Leaders 1836(2).odt`, `DOI 1836 legend(2).json`
and `DOI 1836 map(2).png`. The mod metadata declares Victoria 3 `1.13.*`
compatibility; that declaration is not evidence of a successful game launch.

Keep the internal tags `USA` (FKA), `BIC` (British India), `ORG` (Oregon),
`BRZ` (Brazil), and `SAF` (South Africa). Map labels are not always country tags.

## Subject history alignment

| Subject | Overlord | Starting type | Source status |
| --- | --- | --- | --- |
| South Africa | Netherlands | `dominion` | Dutch Dominion |
| Moldova | PLC | `vassal` | Polish vassal |
| Cuba | Spain | `puppet` | Spanish Puppet |
| Albania | Independent | None | Kingdom |
| Oregon, Ontario, Quebec | Great Britain | `chartered_company` | British Charter Colony |
| Western Australia, New South Wales, South Australia, Tasmania | Great Britain | `chartered_company` | British Charter Colony |

“Charter Colony” is mapped to the existing `chartered_company` pact type,
already used for BIC, HBC and Alaska. This is a gameplay interpretation of the
sheet's wording and should be reviewed during the first in-game smoke test.
Albania's independence follows the sheet's standalone Kingdom status, in
contrast with its explicitly identified subjects.

The redundant nested Spanish scope and duplicate BIC pacts for Beroda (`BER`)
and Mayurbhanj (`MYB`) are removed. South Africa now has one explicit overlord.
Other relationships absent from the sheet retain their existing setup.

## Validation

From the repository root, run:

```sh
python3 tools/validate_subjects.py
git diff --check
```

The validator parses this diplomacy file's assignment/block syntax, checks
27 explicit canon relationships and Albania's independence, and rejects
duplicate subject pacts, including conflicting overlords. It is not a complete
Paradox script validator and does not validate engine effects or vanilla files.

For an in-game check, start a new 1836 campaign with DOI enabled on the target
version. Inspect the relationships above, verify chartered subjects' governments
and rulers, advance one month, and inspect the game error log for subject history
errors. A Victoria 3 installation is required; this has not been performed here.

## Next implementation work

1. Audit state ownership at province level against the map. The JSON assigns
   these states to multiple labels: Akmolinsk, Brandenburg, Cambodia,
   Chelyabinsk, Guayana, Hail, Kirghizia, Laos, North Rhine, Pegu, Pomerania,
   Rhineland, Riga, Schleswig-Holstein, Syrdarya, Tenasserim and Uralsk.
   Some are intentional split states. The JSON alone does not provide the
   province allocations, so it must not be converted to whole-state transfers.
2. Resolve map aggregates against the separate countries in the leaders sheet:
   Canada versus HBC/Ontario/Quebec and Australia versus the four colonies.
   Preserve the separate starting countries until their borders are verified.
3. Audit rulers and political leadership. Jan Jagiełło, Edward Washington,
   Louis-Philippe and the Italian Bonaparte ruler already have character entries;
   Italy's listed Matteo Orsini is absent from its character history. Add missing
   canon characters after deciding their interest groups and whether/how the
   intended heads of government should be represented. The character files
   also contain inherited Russian comments that merit cleanup.
4. Review capitals, government ranks, flags and localized names, then align
   populations and buildings with confirmed province transfers. A visible
   country label on the map does not establish a game's government rank.
