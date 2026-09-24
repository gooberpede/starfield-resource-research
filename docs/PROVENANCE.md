# Research Provenance

This document centralizes the version and source identifiers currently present
in the research record. Unknown values are stated explicitly rather than
inferred. No executable or analysis database is distributed here.

## Creation Kit Static and Live Evidence

| Field | Recorded value |
|---|---|
| Executable | `CreationKit.exe` |
| Product version/build | unknown / not recorded |
| MD5 | `0215f03ec24922dfd4015dcdc5317dc4` |
| SHA-256 | unknown / not recorded |
| Image base | `0x140000000` |
| Ghidra evidence export | 2026-08-31 UTC |
| Ghidra version used for the focused evidence bundles | 12.1.2 PUBLIC |
| x64dbg version used for live observations | unknown / not recorded |

The `pre-biome-resource-state` and `special-common-selector` evidence bundles
correspond to the Creation Kit executable with the MD5 above. Their metadata
records exact per-file export timestamps where available. The live x64dbg
findings in the experiment notes use the same Creation Kit address space, but
the debugger version and a separately captured executable hash were not
recorded.

Creation Kit addresses and control flow are not retail `Starfield.exe`
addresses. Retail checks are independent output validation; they do not map or
prove equivalent retail native addresses.

## Retail and Data Validation

| Field | Recorded value |
|---|---|
| Retail Starfield version/build used for the recorded checks | unknown / not recorded |
| Retail `Starfield.exe` hashes | unknown / not recorded |
| Base-game/plugin/DLC versions for the canonical snapshot | unknown / not recorded |
| xEdit version | unknown / not recorded |
| Historical PNDT/BIOM/RSGD/IRES extraction timestamp | 2026-08-30 11:40:41 |
| Focused Ghidra export date | 2026-08-31 UTC |
| Canonical 1,444-body validation run date | unknown / not recorded |
| Fresh 10-body CK + retail holdout date | unknown / not recorded |

The older research-tree CSV snapshots were removed from `HEAD` in the
2026-09-24 public-release remediation after confirming no active script or
workflow depended on them. Their historical presence and use remain described
in the audit and research record. Maintained canonical data, executable model,
tests, and xEdit extraction tooling belong to the
[`starfield-resource-reproducer`](https://github.com/gooberpede/starfield-resource-reproducer).

The historical `planet-all-resources.csv` snapshot was a `SurveyAggregator`
validation oracle/proxy, not generation input, and was incomplete for
atmosphere-derived final membership. The historical
`PlanetResourceGeneration_v5.csv` and `Starfield_IRES_Hierarchy.csv` snapshots
were older than the maintained reproducer inputs.

## Validation-to-Source Mapping

- The `1,444 / 1,444` canonical result belongs to the maintained reproducer's
  canonical source-data snapshot. The exact plugin versions and run timestamp
  were not recorded in this repository.
- The `10 / 10` fresh holdout compares reproducer atmosphere and biome output
  with Creation Kit biome assignments and retail planetary scans. It is
  corroboration, not retail address mapping.
- Focused static evidence exported on 2026-08-31 supports the documented CK
  control-flow anchors. Live x64dbg observations govern where later live
  evidence conflicts with earlier static interpretation.

Future captures should record executable product version, SHA-256, tool
version, plugin load order/version, UTC timestamp, scenario, and the evidence
bundle or validation run produced.
