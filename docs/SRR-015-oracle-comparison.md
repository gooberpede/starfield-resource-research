# SRR-015 oracle and comparison contract

**Offline draft.** An independent seven-slot projection is feasible for
the SRR-012 controls under their screened input assumptions. The current
production CSV exports accepted occurrences. The generation API retains the
per-biome information needed for a separate projection. A population-wide
retail oracle requires an independent eligibility inventory, complete ordered
inputs and retail applicability checks. Strict effective-input attestation
remains open.

## Production interface and coverage

The maintained sibling checkout was clean at
`a8ff1c788bca415f571f06769ab3e712fa674f75` (package 1.0.0).
`starfield-resource-reproducer --validate-only` validates and generates
without writing the product. The normal command writes
`biome-inorganic-resources.csv` with an optional manifest. The CSV contains
accepted resource occurrences at BIOME and ATMOSPHERE locations, with origin
and safe collapse over the product key. The manifest records schema and
reproducer versions, output name, timestamp, counts and input filenames,
extract timestamps, row counts and SHA-256 digests. Component coverage and
active retail load order require separate witnesses.
[Production interface][readme] · [Manifest and projection][product]

The pinned CLI's validation-only run produced 7,780 occurrence rows,
with 7,445 BIOME and 335 ATMOSPHERE rows and no output files.

| Production input | Contribution | Git blob at the pinned commit |
| --- | --- | --- |
| `planet-resource-generation.csv` | PNDT seed, PPBD biome indices, PNDT and BIOM RSGD references, ordered RSGD weights | `418492f44c9b1c2b5d70d57c8e6a93d4cbdd22f1` |
| `ires-hierarchy.csv` | IRES identities, categories and descendant graph | `25bba09fb205d32b392e179e92fc77fdf0db3c36` |
| `planet-atmospheric-resources.csv` | Effective inorganic ATMO inputs and source lineage | `d7a204a8ad23dc12c826952eac7d44b4de5ca8d5` |
| `planet-directory.csv` | PNDT/body identity, including bodies outside terrestrial generation | `7eb7a9dcc8d76220daf35c9683af885f299cc0d0` |

The [loader][load] checks shared metadata across the four extracts.
The [generation exporter][exporter] emits resource-entry rows from
resolved references, preserves authored PPBD order and finds one BIOM-side
reference through a named path or recursive search. A PNDT or biome without
emitted rows can disappear from this corpus. The BIOM column represents
a single reference from the exporter. Effective runtime lists and winners
require independent evidence.

The audit loaded 1,776 directory bodies and modeled 1,444 bodies with
3,210 planet-local biome rows. It found zero repeated BIOM FormID groups
within a modeled body. The 332 directory-only bodies have unsupported
terrestrial predictions from this corpus. The model input boundary leaves
their native membership and values unknown. A projection must include an
admitted biome with seven zero slots even if it emits no occurrence row.
Keep a separate coverage ledger for missing inputs and ambiguous keys.

The four-input generation path excludes `planet-all-resources.csv`.
That fifth file is a body/resource membership validation snapshot with
known atmosphere omissions. The 1,444/1,444 canonical result, targeted CK
biome regressions and 10/10 CK plus retail holdout result validate the
v1.0 scope. The seven-slot correspondence and native population require
their own tests. [Research baseline](v1-research-baseline.md) ·
[Reproducer validation scope][validation]

## Keys and slot projection

Join on normalized owning PNDT and target BIOM. Each identity comprises
the defining plugin, local object ID and record type. Preserve the winning
plugin and content identity separately because an override can preserve
the key. Join the independently resolved runtime forms to the native
owner/generation key, typed edge target and payload BIOM. Keep authored
biome index and processing order as input provenance. Refuse a repeat
BIOM under one owner pending a qualified disambiguation rule. Repeated
BIOMs across owners and overlapping names are expected.
[Native keys](SRR-012-acquisition-evidence.md) ·
[Eligibility](SRR-012-sample-plan.md#eligibility-and-identity)

| Payload offset | Native slot | Independent projection |
| --- | --- | --- |
| `+0x50` | Common root | `BiomeFamilyGenerationResult.common_assignment.family.root`. Use the family assigned to the current biome, including cache reuse and guard fallback. The selector's `common_root` can be empty on a successful guard fallback. |
| `+0x54`, `+0x58`, `+0x5C`, `+0x60` | Uncommon, Rare, Exotic, Unique | Index the assigned family's four `levels` by `rarity`. Write `selected_candidate` only when `emitted` is true. Preserve a zero hole if a structural intermediary was omitted. An admitted no-assignment result gives five zero words. |
| `+0x64` | Special | Project `orchestration.special_selection` after demonstrating native selector parity, the required selected pointer pair and pre-store shared count below eight. Expose count-before in an exporter or replay model state events. The model's shared-state recorder can accept an already occupied resource at capacity. |
| `+0x68` | Everywhere | Select the first nonzero category-6 ID in qualifying native BIOM RNAM list and RSGD-entry order. The native slot store precedes the shared-state helper. Require typed, nonzero RSGD entry resources for this projection and refuse malformed entries. A zero category-6 FormID can reach the native helper before the loop resumes. |
| — | Atmosphere | Supply the effective ordered ATMO inputs to generation. They change shared occupancy. The seven-word payload has no ATMO slot. |

See the [model implementation][generation] and
[retail slot evidence](SRR-012-sample-plan.md#native-slot-checks). In
retail, the Special count branch at `0x140777959–0x14077795D` skips
`0x140777971` before the duplicate-checking shared helper. The
Everywhere store is `0x140779B9F`; the helper call and first-nonzero
stop follow at `0x140779BB8–0x140779BC2`.

## Owner-level admission

1. Build an independent membership ledger from winning PNDT, ordered
   PPBD and BIOM definitions, and any qualified ENAM/CSV source implicated
   by the profile. Record evidence for expecting typed insertion, exclusion
   or unknown eligibility. The 3,210 modeled keys define a declared
   candidate universe. The directory and mixed-index counts have different
   meanings. Keep retained index membership on the observed side.
2. Hash the base master, loaded files, applicable loose/archived inputs,
   production extracts and projection. Record the extract and schema
   versions, command, model commit and executable identity. Use an
   independently authenticated epoch-bound plugin table with implicit
   masters, Creations and full, medium and small FormID mappings. Resolve
   winning records offline and bind PNDT seeds and work-set order, all
   BIOM RNAM entries, PPBD overrides, ordered RSGD inputs, reachable IRES
   links and effective ATMO inheritance. Resolve alternate loader sources
   or prove effective equivalence. A disk inventory leaves runtime
   activation open. [SRR-013 input gate](SRR-013-retail-effective-inputs.md)
3. Admit or refuse the owner's prediction as a unit. Compare native
   sorted edge-key collection against the model's authored input order.
   Qualify primary override selection and same-roll BIOM retry with the
   prior cumulative threshold, BIOM-side Everywhere and Common guard
   fallback, Special count gate, binary32 thresholds, IRES candidate
   order/multiplicity and shared occupancy. Earlier differences can
   change subsequent draws, slots and family-cache state. Unresolved
   consequential differences require a reviewed retail applicability
   adapter. Keep the protected v1.0 generation mode fixed.
   [Retail mapping](SRR-002-retail-static-reconnaissance.md#retail-mapping-on-the-pinned-image) ·
   [Control applicability](SRR-012-sample-plan.md#retail-and-reference-model-boundary)

Retail shuffles before the atmosphere and Everywhere passes
(`0x1407798EB`, `0x140779973`, `0x140779B32`). The model visits
the initial biome order for Everywhere before shuffling. Equal initial
order and candidate sets still leave pre-pass ordering to qualify. For
an admitted owner, demonstrate the independently resolved pre-pass
contributes equivalent identities and occupancy into the per-biome
loop, including any effect of truncation or failed insertion. A
non-random pre-pass can admit differently ordered executions if their
relevant state and local slot effects are established equivalent.

The audit found zero differing authored orders against ascending base
BIOM FormIDs. It found zero differences in selected IDs on recorded
model rolls from finite binary32 primary selection or the available
singleton BIOM retry. The effective Everywhere candidate sequences
matched the available BIOM's first category-6 candidate. Guarded Common
candidate sequences also matched the available BIOM definitions. These
are bounded screens over the CSV-visible states. Full native BIOM lists,
runtime ordering, pointer presence, binary32 descendant decisions and
native IRES child multiplicity remain outside that audit. Retail's selector
uses binary32 multiply and accumulation whereas the model uses Python
floats for weights. Retail's descendant inclusion also uses a binary32
multiply (`0x1407781DE–0x1407781F0`); its append loop has no visible
per-entry duplicate check.

The audit found three selected Specials at count eight, first Schrodinger
VI-c / CrateredNoLife11 (`0005E0BE` / `000C5717`). All three identities
were new to the modeled shared state. The model rejects those occurrences.
A direct `special_selection` export would still make each slot nonzero
where the retail writer skips the store at the same count. A synthetic
already-occupied Special at count eight additionally defeats an
occurrence-only projection. These results combine model events and native
store predicates; the retail values at those keys remain unmeasured.

## Worked controls

The [offline audit](../tools/srr015/audit_oracle.py) computes these rows
from the four production inputs, the generation API and the screened slot
rules. It asserts against the independently derived **offline** tuples
in the [SRR-012 control plan](SRR-012-sample-plan.md#fixed-samples-and-controls).

| PNDT / BIOM | Crossing from model to native words | Seven slots in offset order |
| --- | --- | --- |
| Kreet `0003F59F` / Frozen `000D9BAC` | Argon family root gives `+0x50`, emitted Exotic Neon gives `+0x5C` with earlier rarity holes, BIOM RSGD `000083F0` gives category-6 Water at `+0x68`. Atmospheric Helium-3 affects occupancy. | `[000057EA, 00000000, 00000000, 000057E9, 00000000, 00000000, 000083EC]` |
| Decaran VII-b `0005DF7F` / Cratered `000C5717` | Override `0018CE00` supplies Uranium, with emitted Uncommon Iridium and Unique Vytinium. Terrestrial Helium-3 with count below eight gives `+0x64`. The admitted BIOM source has no category-6 selection. | `[000057EB, 000057EC, 00000000, 00000000, 00005DF8, 000057F5, 00000000]` |

Kreet's two other BIOMs remain regression controls. The prior paired
retail result separately establishes structural population and descriptive
agreement at the checkpoint. Its qualification and provenance remain
as recorded. [SRR-013 paired observation](SRR-013-retail-title-paired-structural-observation.md)

## Extension and comparison contract

The minimum viable extension is a separate opt-in versioned exporter
using `load_production_data` and `generate_all_planets`. Emit a row
per uniquely modeled PNDT/BIOM, including empty results. Keep a coverage
ledger for every owner in scope. Expose assigned family levels, Special
pre-store count and source applicability from the model and independent
input witnesses. Separate the retail adapter and preserve the production
CLI. Represent unsupported tuples with JSON `null` and known empty tuples
with seven explicit zeroes. Use deterministic UTF-8 JSONL with LF, final
newline, stable field order and sort by canonical PNDT and BIOM identities.

Freeze the data and coverage ledger before the comparison. The manifest
includes schema and projection versions, input metadata and content
digests, generator revision, executable build, scope/selection rule,
owner-level admission evidence, counts and deterministic data digest.
Epoch-bound input attestation is a separate witness. Example abbreviated
rows use base-master local object IDs. Volii Alpha is a directory-only
body for this terrestrial projection.

```jsonl
{"owner":"0003F59F","biome":"000D9BAC","authoredIndex":0,"prediction":"CONDITIONAL","slots":["000057EA","00000000","00000000","000057E9","00000000","00000000","000083EC"]}
{"owner":"0005E3A5","biome":null,"prediction":"UNSUPPORTED","slots":null,"reason":"directory_only"}
```

Compare resolved logical identities in native slot order. Preserve raw
u32 words separately. Compare raw words additionally after encoding
expected identities using the independently verified runtime mapping.
Keep runtime mapping, addresses, process IDs, epoch identifiers and
private input inventories in private custody. Sanitized results provide
stable identities, checkpoint labels, scope, counts and slot outcomes.

```text
expected, ledger = freeze_projection(independent_inputs, retail_applicability)
observed = qualify_paired_extraction()
if observed.coverage_invalid:
    return INDETERMINATE with safe diagnostics
for key in sorted_union(ledger.biome_keys, observed.biome_keys):
    verify_unique_identity(key)
    classify_membership_if_decidable(ledger, observed, key)
    classify_present_zero_independently(observed, key)
    compare_all_seven_slots_if_applicable(expected, observed, key)
    record_input_attestation_separately(key)
```

| Case | Classification |
| --- | --- |
| Admitted expected and observed keys agree in all seven words | `EXACT_SLOTS` with conditional/strict provenance. |
| Independently established expected component missing from qualified complete extraction | `MISSING_EXPECTED`. A proposed key with unresolved eligibility remains unsupported. |
| Qualified present seven-zero vector | `PRESENT_ZERO`, plus exact or different if the expected tuple is applicable. Preserve the zero observation when prediction is unsupported. |
| Qualified present nonzero vector differs | `DIFFERENT_SLOTS` with offsets and expected/observed IDs. |
| Observed key outside a decidable independent expected population | `UNEXPECTED_OBSERVED`. Use `NO_APPLICABLE_PREDICTION` if prediction coverage leaves eligibility open. |
| Duplicate native or normalized identity | `DUPLICATE_IDENTITY` with failed extraction qualification. Ambiguity on the oracle side instead blocks prediction for scope. |
| Prediction or source mismatch | `NO_APPLICABLE_PREDICTION`, `RETAIL_APPLICABILITY_UNRESOLVED` or `INPUT_PROVENANCE_MISMATCH`, with exact reason and separate structural status. |
| Incomplete or invalid extraction | `INVALID_EXTRACTION` with refusal detail. Suppress scientific missing/extra findings. |

Use `COMPLETE_MATCH` only for a nonempty declared decidable population
with complete qualified extraction, unique and equal sets of keys in
scope and an applicable exact tuple for every row. Name scope and tier
(conditional or strict) and list uncovered populations. Use
`PARTIAL_MATCH` when a complete extraction has qualified exact slots
for some keys along with coverage gaps or differences. Use `NO_MATCH`
when completely compared, decidable scope has differences and no exact
matches. `INDETERMINATE` covers invalid extraction, unresolved
applicability with no exact comparisons, empty or insufficient scope.
Report structural coverage, membership deltas, all-zero count, slot
differences, ambiguity, unsupported and strict-attestation counts with
denominators. A later checkpoint needs fresh epoch and provenance checks.
Coverage and value deltas can reflect a changed input, context or identity.

## Fixture plan and replay

| Fixture | Required result |
| --- | --- |
| Four controls and reversed export iteration | Identical sorted rows, with sparse holes, Special and Everywhere in the designated slots. |
| Common cache reuse and both guard fallback variants | Use the current assignment across BIOMs. Include missing candidate path and an unqualified empty-cache guard as distinct cases. |
| Identical planet aggregate with biome reassignment or moved slots | Per-key slot differences despite equal unions. |
| Selected duplicate and selected new Special at count eight | Both native projected slots are zero while model occurrence acceptance differs. |
| Multiple BIOM category-6 candidates, differing override and same-roll BIOM retry after override miss | Check native precedence, first nonzero and accumulated threshold. Refuse an unresolved list or malformed zero resource, and test the native versus modeled pre-pass order. |
| Float32 boundary and duplicate root-plus-current child candidate | Demonstrate event parity or refuse the owner. |
| Zero present, absent expected, nonzero differing, extra observed, unsupported row and malformed extraction | Distinct results, with missing/extra suppressed on partial coverage. |
| Shared BIOM across owners, duplicate within owner, remapped ID and winning override retaining ID | Join stable identities via the runtime map, detect duplicate and refuse a mismatched provenance witness. |
| Zero overlap, partly supported extraction, digest/version drift or altered observation data | Reject vacuous complete match. Observation changes leave oracle rows and digest independent. |

From the research checkout, set `$srrPython` to the interpreter,
`$srrReproducer` to the pinned sibling, `$srrExe` to the pinned file in
[provenance](PROVENANCE.md#current-retail-identity) and `$srrScratch`
to a fresh ignored directory in the research checkout. The audit reads
the four CSVs, writes to stdout and leaves the Ghidra project untouched.
The test run disables caches in the sibling and places temporary output
in research scratch space.

```powershell
$env:PYTHONPATH = Join-Path $srrReproducer src
& $srrPython -B tools/srr015/audit_oracle.py (Join-Path $srrReproducer data)
& $srrPython -B tools/srr011/inspect_pe.py $srrExe window 140777949 56
& $srrPython -B tools/srr011/inspect_pe.py $srrExe window 140779b4e 94
Push-Location $srrReproducer
try {
    git rev-parse HEAD
    git status --short
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
    & $srrPython -B -m pytest -q -p no:cacheprovider --basetemp $srrScratch
} finally {
    Pop-Location
}
```

The audit passed four control assertions, the pinned PE windows reproduced
the native gates and the sibling suite passed 183 tests on Python 3.14.
The projection/comparison fixture table defines future implementation tests.

[readme]: https://github.com/gooberpede/starfield-resource-reproducer/blob/a8ff1c788bca415f571f06769ab3e712fa674f75/README.md
[product]: https://github.com/gooberpede/starfield-resource-reproducer/blob/a8ff1c788bca415f571f06769ab3e712fa674f75/src/starfield_resource_reproducer/product.py
[generation]: https://github.com/gooberpede/starfield-resource-reproducer/blob/a8ff1c788bca415f571f06769ab3e712fa674f75/src/starfield_resource_reproducer/generation.py
[load]: https://github.com/gooberpede/starfield-resource-reproducer/blob/a8ff1c788bca415f571f06769ab3e712fa674f75/src/starfield_resource_reproducer/load_data.py
[exporter]: https://github.com/gooberpede/starfield-resource-reproducer/blob/a8ff1c788bca415f571f06769ab3e712fa674f75/xedit-scripts/Starfield%20-%20Export%20Planet%20Resource%20Generation.pas
[validation]: https://github.com/gooberpede/starfield-resource-reproducer/blob/a8ff1c788bca415f571f06769ab3e712fa674f75/docs/V1-VALIDATION-BASELINE.md
