# Allocation validation

The recovered generation model has strong, bounded output validation. CK live
mechanism recovery, retail retained-state observation and independent effective
input attestation are different evidence domains. Matching outputs corroborate
commonality; they do not establish instruction-level identity across executables.
Build pins and custody boundaries are in [provenance](PROVENANCE.md).

## Canonical and fresh holdout validation

**PROVEN within the tested output scope:** 1,444/1,444 canonical planet-wide
CK/RSGD-visible memberships match, with all targeted pathological CK biome
regressions exact. The historical SurveyAggregator snapshot is validation only
and omits some atmosphere-derived membership. It is not generation input.
The [generation baseline](v1-research-baseline.md) preserves the pathological
cases and recovered CK mechanism.

The [generation baseline](v1-research-baseline.md#validation-baseline)
lists all ten fresh holdouts and their channels: CK biome distributions,
observed atmosphere and retail planet-wide scans matched 10/10. Historical
build hashes, dates and input versions remain unknown. No unrecorded raw
per-biome tables are inferred.

## Bounded execution observations

**SRR-009 — qualified NOT_OBSERVED:** zero four-site hits, focal invocations
or correlated allocator arrivals during 84.281 seconds after title-card
arming on the pinned retail image. The verified windows were journal
intervals [439,483), 52.253 seconds, and [483,500), 32.029 seconds (rounded
durations). Initial readback covered 95 thread generations, then four new
threads. STOP 500 sealed 353,147 bytes, SHA-256
`f4cd672725622db9c3e0d8a74bc5b4c3bb1c7bd1469ddd3b89017a8b33d80967`;
observer SHA-256 `dac1d88aea5b23e9725567b00426bfc3faa940a362e46521d59f15d10d64da88`.
This excludes startup before arming, loading, gameplay and other builds/paths.
Two earlier attempts were incomplete before attachment. The successful
target exited normally; the observer required later administrative closure
after verified game exit. Scientific coverage and cleanup are separate.

**SRR-010 — CLOSED, INCONCLUSIVE:** all four Save2 load windows remain
`INSTRUMENTATION_INCOMPLETE`, ending before confirmed player control or
scientific STOP. Each target exited `0x80000004`; cause is unknown.

| Attempt | Method | Load marker to native exit |
| --- | --- | ---: |
| First, 15 November 2026 | Initial observer, full load-entry sweep | 16.184 s |
| Second, 15 November | Deferred load-period timer sweeps | 16.067 s |
| Third, 15 November | Census-only load entry | 15.349 s |
| Fourth, 16 November | D5B-informed event-held periodic sampling | 15.686 s |

Times include operator save selection. None recorded an owned site hit,
focal invocation, correlated allocator arrival or corresponding delivered
single-step exception. Allocator execution was neither demonstrated nor
excluded. Terminal receipts and phase prefixes are not scientific STOP seals.
Each observer published its terminal receipt without administrative closure;
normal Quit was unexercised. Protection checks reconciled 98 Documents and
95 Steam remote original/backup pairs, both designations and no unknown files.

Control A is the maintainer's report of settled uninstrumented Save2 gameplay
and normal Quit, without an independent receipt. Control B reached reported
settled gameplay under debugger-only attachment with **no allocator sensitivity**.
An independent epoch witness recorded exit zero, but the missing terminal
debugger event/receipt left `CONTROL_INCOMPLETE`; only its observer was
administratively closed. It recorded an incidental Documents exit-save
replacement. Its primary manifest is
`1794504690e29c180f1116ba4e6c2ab52349e9144d2da0c258d30e937a9b798b`;
fourth-attempt manifest is
`7e4a18c7c1d2c25c84f05e4092d6e92338aea5a82b5ff2da4b91f54e32614317`.
Disposable sensitivity controls do not establish retail execution. The
separate D5B Save52/Build Mode success used different sites/workload and
terminal authority; it motivates an event-service method, not a Save2 result.
The [lifecycle subject](retail-execution-lifecycle.md) explains the static
path and timing gap; [tools](../tools/README.md) preserves repeatable methods.

## Selected title-card structural observations

The first SRR-013 title attempt returned four `STATE_INDETERMINATE` outcomes
with `observation_budget`. A complete first collection descriptively matched
all four predicted vectors, but a five-second deadline interrupted the second
at 5.000920400 seconds (1,092 calls, 20,032 requested bytes) before closing
identity. First-pass nonzero counts were 3,2,2,4; they are diagnostic only.
Journal SHA-256 `82ab34550fca287e54155f28a9cf6e628587d5eb3bc212ac7289af7d512392dd`,
prefix `378d81cfc8187913d7074e554d29be05da9358772d931b5983871e0350549563`,
evidence manifest `081614a5994a908db03d4af9dc3f7e53ceb9456459c722a7de7f8c6a2c7adcae`.
Offline replay reproduces the refusal. Later success does not upgrade it.

The later pair verified both complete selected owner ranges: Kreet
`0003F59F` (three components) and Decaran VII-b `0005DF7F` (one).
The published owner/context/registry, unique typed components and every
nonzero BGSResource ID validated independently in both collections.

### Four complete sample vectors

Both collections returned the seven words below in the same order. `0`
denotes the raw word `00000000`. Every listed nonzero FormID independently
resolved as a valid `BGSResource`. The paired reason was
`validated_nonzero_resource_ids` for each sample.

| Sample | Seven observed words, in slot order | Comparison control | Outcome |
| --- | --- | --- | --- |
| Kreet Frozen (`000D9BAC`) | `000057EA, 0, 0, 000057E9, 0, 0, 000083EC` | Decaran VII-b Cratered passed | `STRUCTURALLY_POPULATED` |
| Kreet Mountains (`0023C0CE`) | `000057C7, 000057C9, 0, 0, 0, 0, 0` | Decaran VII-b Cratered passed | `STRUCTURALLY_POPULATED` |
| Kreet Volcanic (`002C9985`) | `000057C1, 000057C3, 0, 0, 0, 0, 0` | Decaran VII-b Cratered passed | `STRUCTURALLY_POPULATED` |
| Decaran VII-b Cratered (`000C5717`) | `000057EB, 000057EC, 0, 0, 00005DF8, 000057F5, 0` | Kreet Frozen passed | `STRUCTURALLY_POPULATED` |

The vectors descriptively match all seven positions of the
[SRR-012 conditional predictions](allocation-validation.md#selected-title-card-structural-observations).
The observation did not attest effective inputs or qualify the strict
exact-tuple contract. Pre-checkpoint allocator execution is the leading
explanation under the [retained-writer evidence](retail-execution-lifecycle.md).
The paired state does not identify the execution time or instruction,
continuous component lifetime, execution frequency, save persistence or
galaxy-wide state. The [first title attempt](allocation-validation.md#selected-title-card-structural-observations)
retains its original four `STATE_INDETERMINATE` verdicts and sealed journal.

The successful collections took 3.816299400 and 3.816864400 seconds,
separated by 25.657600 ms; pair 7.658821400 seconds, receipt overall
7.659543200 seconds. It used 1,796 operations/31,348 requested bytes.
The operator held the responsive title card before any save selection;
an independent epoch-bound exit witness later measured zero. The 98/95
protected pairs, designations and checked transient metadata reconciled.
Steam Cloud/per-game overlay were disabled; NVIDIA state was reported.
Plugins.txt kept content but changed file identity; Steam manifest/config
bytes changed while selected app/settings fields held.
The version-4 sealed journal is
`b4bbef36415776dd7582a5d3e419e8a2067ca9fcaa75844097824fec7ea3309c`,
prefix `98765f162d42479639e7de65d0d2b160cafadf731dc45a94ca701ef1b68c1d2c`.
Checked replay reproduces both collections and classifications.
These are custody-backed observations, not effective-input attestations.
Pair equality permits ABA or a stable intermediate clear/rebuild.

## Complete retail title-card census

**PROVEN — FINISHED / QUALIFIED.** The operator explicitly requested one
extraction after normally launching to the responsive title card. The
command began at 05:13:33 UTC (16:13:33 AEDT), selected PID 52272 and used
clean committed checkout `bd993bebc1376c3a019bc61bc7bd5e16221f6a6c`.
The pinned retail executable, reviewed execution source
`4c958ae9cd557c5e952bfa0c20b48b7fb80e9f344eac2c7f523c219cdafb26f3`
and unchanged work
`490060e6deafda06b4383a3de300c68fa1adaf71691830ba3a5cfb4d0aa20b60`
matched. There was one observation pair and no retry or implementation change.

Each collection declared and visited 18,314 mixed descriptors: 3,211 typed
targets plus 15,103 certified mixed exclusions. Both have verified coverage,
572 tree windows (565 blocks, six leaves and one internal node), and 2,870
reached native FormID-map entries. There were zero mixed/target refusals,
zero unresolved source fields and no acquisition failure. Rooted graph,
typed inputs, slot values, complete form witnesses and namespace identity
all agree. Both collections have opening and closing process identities
and consumed-window revalidation; these do not imply atomicity.

The 3,211 unique edges cover 1,445 normalized PNDT identities (1,437
`starfield.esm`, eight `shatteredspace.esm`), 428 BIOM identities (425/three
respectively), and 45 distinct IRES identities. There are 3,192 rows with a
base-game defining PNDT and 19 with a Shattered Space defining PNDT. All
7,445 nonzero resource occurrences resolve to native `starfield.esm` IRES
records with the required type/vptr. Raw runtime IDs, normalized defining
plugin/local IDs, seeds, RSGD references and all seven slot words survive.
The equal native namespace has 38 assigned plugins: eight full, nine medium
and 21 small; its normalized digest is
`64724895b5a71ebe4ff60305d4cf0bde2d93e18699b5c66ed5705143db77803a`.
This is defining identity, not physical-file or winning-content attribution.

| Slot | Nonzero words | Explicit zero words |
| --- | ---: | ---: |
| Common | 2,985 | 226 |
| Uncommon | 1,425 | 1,786 |
| Rare | 730 | 2,481 |
| Exotic | 364 | 2,847 |
| Unique | 8 | 3,203 |
| Special | 472 | 2,739 |
| Everywhere | 1,461 | 1,750 |
| Total | 7,445 | 15,032 |

All 22,477 words are retained. One all-zero row is explicitly present:
`starfield.esm:05E3A5` → `starfield.esm:120C76`. Its native forms resolve
and its observed BIOM has zero RSGD references; the seven zero words are
observed payload values, not an inferred empty allocation. No generation,
eligibility or comparison conclusion is inferred from that row.

The sealed pair used 44,748 operations and 9,787,692 requested bytes;
backend totals including image authentication were 44,769 process reads,
44,854 region queries and 9,795,947 bytes. Evidence and normalized exports
remain private. All output hashes reconcile; checked offline replay
regenerates byte-identical dataset and comparator projection.

| Evidence | SHA-256 |
| --- | --- |
| Sealed receipt | `3a48b04479bf88a8821a704a77d684cd6941585c075323ce53c0d6a14a1efea3` |
| Qualified normalized dataset | `15711109761112c3ce3b2f5bf2a03966ccdb26a277ea7ec0961f0147b16eedb4` |
| Comparator projection | `496ccd835e2e3de062aa07f812f15f406097c8f8948610a3f7952d6b08ae7c16` |
| Source/work and output manifest | `3441ccf092bef63ed7c9046a21ae99bb343e303443f85b1064d8215b2e971357` |

The command exited successfully and the operator was immediately told they
could Quit normally. No further game access occurred. Process exit and save
preservation are not independently measured by this operator workflow.
The result is complete for the admitted rooted store at this title-card
checkpoint. It establishes neither all-galaxy completeness nor atomicity,
intermediate mutation absence, completed allocator execution or oracle
agreement. No oracle or reproducer comparison was performed during this acquisition; the subsequent SRR-018 comparison is described below.



Independent offline reconstruction checked all 572 native pages and 18,314
positions in each collection, routing minima/fences, links/order/counts,
2,870 reached map entries, 1,950 typed identities, every metadata/slot word
and all namespace assignments. Dataset/projection reproduced byte-for-byte.
Its substantive review SHA-256 is
`ef5a93a1e538fe517466a44fd5212e37b85a8bb5a9859ebe680abac04a83851e`.

### Earlier incomplete census observations

The 03:29:38 UTC attempt on 18 November used checkout `90ff8d6` and
refused the old 8,192-descriptor budget against the declared 18,314 before
traversal. It acquired no targets or lanes. Receipt
`1f9ecbd8da5ac8195912f4da946a97998042e947cc229ca985d3b54291388b23`,
dataset `8991a02eb1937034e211a0c90376216b64222376763fbd29aa6f83b042b0dce0`,
manifest `b346ffe7690ec8f4e02ecaf1e5a706f900f643b09453988d52b48dc79c8c2fc0`.

The 04:17:28 UTC attempt at `8a963710` traversed 1,202 descriptors
(37 exclusions/1,165 typed diagnostic targets) then refused `index_fence`.
Its partial 512 PNDT IDs, 302 BIOM IDs and 8,155 slots/5,480 zeros were
unqualified; no closing witness, namespace or second collection existed.
Receipt `2d43d7aa323cde6c2b5b7743864fbd0d3b160c2823a8da69d0ee30d0b9471508`,
dataset `e794d7e34b6505c7bc375cd08853e326c2a8bef4f0d562c1f0986a4bb5516614`,
manifest `3670b465acaa45d1f72bf0319e9d4b82a94d1a95172a1dbc99f37f8bb01f3500`.
Frozen execution source `062ec189671de1e37e55294083de8da186701ee8ec166b73a9fa91752b0386ae`
replays that refusal. Corrected diagnostics pass former block [0,83] but
need uncaptured operation 4,252 after 4,251 retained operations: no missing
read or pair is invented. The [database subject](component-database.md)
preserves the proven block-minimum correction; current public replay still
requires an exact reader pin. The earlier Steam-registration refusal at
`8321a3b` acquired no native data (console/attempt hash
`c694c2d331349b3ec89658f2b4fdbe29ac332716710865d109314f670c54bf6e`).
These old implementation/admission blockers are superseded for new captures,
while their historical classifications remain incomplete/no-observation.

## Independent base-field controls

These are independently corroborated base definitions, conditional for retail winning inputs. Vectors are listed above.

| Body, PNDT and seed | Biome index, BIOM and EDID | PNDT override and BIOM RSGD |
| --- | --- | --- |
| Kreet `0003F59F`, 2842708811 | 0 · `000D9BAC` · `FrozenLifeKreet` | None · `000083F0` |
| Kreet `0003F59F`, 2842708811 | 1 · `0023C0CE` · `MountainsLifeKreet` | `00244CCB` · `00007EDD` |
| Kreet `0003F59F`, 2842708811 | 2 · `002C9985` · `VolcanicRoughLifeKreet` | `00244CCC` · `000083EA` |
| Decaran VII-b `0005DF7F`, 1633829920 | 0 · `000C5717` · `CrateredNoLife11` | `0018CE00` · `000083E0` |

Kreet shuffle order is 2,0,1, with atmospheric Helium-3. Its override Common weights are 100%; Frozen uses its singleton BIOM RSGD and category-6 Water. Decaran has 100% Common/Special override weights, no category-6 candidate and no inorganic ATMO in the pinned extract. These paths avoid Common guards. The [independent reader procedure](../tools/README.md#offline-oracle-and-comparison) rederives the base fields.

## Independent expected population and strict input contract

### Production interface and coverage

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
[Native keys](component-database.md) ·
[Eligibility](allocation-validation.md#selected-title-card-structural-observations)

| Payload offset | Native slot | Independent projection |
| --- | --- | --- |
| `+0x50` | Common root | `BiomeFamilyGenerationResult.common_assignment.family.root`. Use the family assigned to the current biome, including cache reuse and guard fallback. The selector's `common_root` can be empty on a successful guard fallback. |
| `+0x54`, `+0x58`, `+0x5C`, `+0x60` | Uncommon, Rare, Exotic, Unique | Index the assigned family's four `levels` by `rarity`. Write `selected_candidate` only when `emitted` is true. Preserve a zero hole if a structural intermediary was omitted. An admitted no-assignment result gives five zero words. |
| `+0x64` | Special | Project `orchestration.special_selection` after demonstrating native selector parity, the required selected pointer pair and pre-store shared count below eight. Expose count-before in an exporter or replay model state events. The model's shared-state recorder can accept an already occupied resource at capacity. |
| `+0x68` | Everywhere | Select the first nonzero category-6 ID in qualifying native BIOM RNAM list and RSGD-entry order. The native slot store precedes the shared-state helper. Require typed, nonzero RSGD entry resources for this projection and refuse malformed entries. A zero category-6 FormID can reach the native helper before the loop resumes. |
| — | Atmosphere | Supply the effective ordered ATMO inputs to generation. They change shared occupancy. The seven-word payload has no ATMO slot. |

See the [model implementation][generation] and
[retail slot evidence](allocation-validation.md#selected-title-card-structural-observations). In
retail, the Special count branch at `0x140777959–0x14077795D` skips
`0x140777971` before the duplicate-checking shared helper. The
Everywhere store is `0x140779B9F`; the helper call and first-nonzero
stop follow at `0x140779BB8–0x140779BC2`.

## Independent membership evidence

The default profile transcribes the independent base-master field
corroboration for Kreet and Decaran VII-b. It binds their PNDT FormIDs,
authored PPBD indices, BIOM FormIDs, RSCS seeds, overrides and singleton
BIOM resource-generation references. Ordered atmosphere assumptions use
the pinned generation data. The profile assumes those winners, an admitted
authored submission stream, and no applicable later ENAM or CSV submissions.
Those assumptions define a conditional work set for each control owner.
[Independent field corroboration](allocation-validation.md#selected-title-card-structural-observations)

`resolve_authority` accepts an independently evidenced
`srr016-authored-operations-v1` object. Its source and SHA-256 identify the
reviewed winning inputs and operation evidence. Its `forms` entries are
`[runtime u32, defining plugin and local object ID, PNDT or BIOM]`.
Each owner entry has a runtime ID, a scope reason, a `workset_closed` flag
and ordered operations. A `PPBD` or `ENAM_PPBD` entry carries the authored
index, runtime BIOM, winning plugin, winner digest and admission status.
`ENAM_CLEAR` carries the owner-range removal witness. `CSV` supplies a
runtime BIOM under an independently evidenced accepted-row path. An
admission value of null records unknown guard or execution evidence.

```text
resolve both axes through the independent typed ID map
for each owner and each submission in witnessed order:
    admitted ENAM owner-range removal => clear current owner set
    admitted authored, replacement or CSV insert => add its BIOM
    unresolved admission => withhold the owner's closure
    repeat live key => reject ambiguous duplicate insertion
classify each attributable candidate in the resulting owner set
retain raw IDs, source, operation order and winning digest
```

This reducer needs an independent account of the winners, alternate
sources and relevant command order. The authored builder submits edges at
`0x14076F360`. The ENAM-associated path submits owner-range removal at
`0x14076F751` and replacement at `0x14076FCEA`. The accepted CSV branch at
`0x142341026–0x14234103F` uses the insertion callback. A repeat or
overlapping CSV submission has no inferred replacement rule here.
[Native operation evidence](component-database.md#operation-catalogue)

The directory supplies owner coverage and the generation extract supplies
model-only candidate keys. Their records by themselves leave component
eligibility `UNKNOWN`. The original frozen SRR-016 ledger contains 3,191 joinable candidate keys.
The remaining 19 candidates and 11 directory identities retain extract IDs
in `unresolved_candidates` and `unresolved_owners`. Their non-base
source namespaces need an independently attested mapping before a
defining-plugin/local-ID join. Those entries contribute to unknown
denominators. For the current scope, 1,774 directory owners are unknown
and zero keys were classified `EXCLUDED`. The tests exercise independently
known exclusion and removal. Static insertion capability, retained presence
at a checkpoint and productive allocation have separate evidence.

## Projection and whole-owner screens

The exporter reads the pinned production API and its diagnostic events.
It retains the selected entry and the shared count immediately before the
Special write decision. Common uses the current biome's assigned family
and its four emitted rarity levels. This preserves cache and fallback
assignments and explicit zero holes. The native lanes in ascending address
order are Common, Uncommon, Rare, Exotic, Unique, Special, Everywhere.
Atmosphere contributes to pre-pass occupancy.
[Native slot locators](allocation-validation.md#selected-title-card-structural-observations)

```text
screen the complete owner against authored order, input witnesses and native key order
reconstruct BIOM-side Everywhere in shuffled order and verify initial shared occupancy
for each model selector draw:
    carry the binary32 cumulative weight through an override miss into the BIOM retry
    verify the selected entry and definition agree with the model
    capture Special's count before any shared-state helper
check descendant candidate order and multiplicity and binary32 inclusion decisions
gate the entire owner on the applicable evidence, including the Common fallback pool
emit the five family lanes, the admitted Special word and the first BIOM Everywhere word
```

The native Everywhere pre-pass uses the first nonzero BIOM-side candidate
and follows the shuffle at `0x1407798EB`. The current oracle screens
against one BIOM-side RSGD available in the production extract. It checks
pre-pass occupancy with the atmosphere and both orderings, then checks
the selector on recorded rolls for binary32 and same-roll retry equivalence.
The native descendant pool visits root children followed by distinct
current-node children. The screen compares that ordered pool, including
multiplicity, to the model's deduplicated candidates and checks inclusion
on recorded rolls with the native binary32 threshold.
[Retail routine correspondence](v1-research-baseline.md#pinned-retail-correspondence-and-native-differences)

All 1,444 modeled owners passed these particular corpus-visible ordering,
pre-pass occupancy, selector and descendant screens. For 122 owners,
native Common guard fallback cache order and multiplicity remain
unattested, so the screen records that reason. Only the two control
owners have independently corroborated conditional authored work sets
and matched generation input witnesses. The exporter withholds all
other owner vectors. The tests challenge a same-roll BIOM retry,
a binary32 threshold boundary, and duplicate candidates spanning
distinct root and current lists. [Retail differences](allocation-validation.md)

The Special slot writer needs the selected pair and shared count below
eight. The count branch `0x140777959–0x14077795D` bypasses the store
`0x140777971` at capacity. The three recorded model selections at this
boundary are Helium-3 `000057F5` for `0005E0BE/000C5717`,
`0005E45F/001862BD` and `0005E591/000C5716`. Their projected Special slot
is zero. A separate fixture shows that a selected Special already occupying
the eighth-slot state also projects zero even if the model accepts the
duplicate occurrence. The pinned production occurrence behavior is
preserved. [Count-eight evidence](allocation-validation.md)

| Claim | Evidence | Limit |
| --- | --- | --- |
| Four conditional expected keys | Base-master field corroboration and authored insertion semantics | Applied winner and actual submission or removal for a retail epoch remain unresolved. |
| Four conditional seven-lane tuples | Full-owner production generation and offline reference tuple assertions | Retail historical observations retain their original structural verdicts. |
| Special count-eight write gate | Native branch and store addresses, plus three pinned model regressions | Retail values at those three keys remain unmeasured. |
| Scope and immutability checks | Synthetic fixtures with partial work sets, aliasing, digest drift and altered observations | Runtime map and pre-observation receipt custody need independent authenticated evidence. |
| Full retail universe | Unknown | Requires winning PNDT, PPBD, BIOM, ENAM and CSV inputs, type and runtime ID authority, and applicable submission closure. |
| Full retail slot comparison | Unknown | Requires complete whole-owner inputs, retail-qualified ordering and guard semantics, and matching remap/effective-input attestations. |



Full, medium and small plugin namespaces require independent runtime
attestation (24/16/12 local bits); a configured disk list alone cannot
establish activity or winning content. Resolve effective PNDT/ordered PPBD,
BIOM RNAM lists and optional overrides independently, ordered RSGD weights,
reachable IRES category/child graphs, ATMO RFDP/REFL/RDIF inheritance and any
admitted ENAM/CSV substitutions. The disk-only SRR-013 check found 39 plugin
candidates and no loose Space/BiomeData.csv, which excludes neither inactive
plugins nor archived/alternate CSV input. Its base-master pin was
`1dabed00c3f4282dd3bb54d2e9601e40b577d8742d078b7ccef203adbfef0da7`.
Defining native identity is now observed; historical claims that namespace
decoding itself remains blocked are superseded. Winning contents and ordered
operation closure remain unresolved, so `input_sha256` stays null.

## Comparison qualification and receipts

## Comparator and offline verification

`compare` reports structural and normalized acquisition qualifications
separately. Qualified raw structure can remain visible when typed
normalization or paired value qualification is indeterminate. It checks
the raw key namespace, shared registered discriminator pattern and
one-to-one raw/canonical mapping in both directions. It validates each
zero and nonzero lane before joining the canonical key. Membership
requires bound input provenance and a decidable key scope. Values also
require an exact owner work-set match across the ledger, oracle and
observation. A strict projection requires agreement on an independently
attested runtime remap digest. A complete population match also requires a
bound ledger remap digest. An explicit runtime-key conflict makes membership
and values indeterminate for that owner and preserves unaffected comparisons.
Conditional matches remain scoped.

The receipt is the producer's separate binding of the expected ledger
and oracle. Supply the independently retained **canonical** receipt
SHA-256 to the comparator. Observation input is confined to the
comparison entry point. It cannot be supplied to the freeze command or
replace the previously pinned ledger or oracle. With a full fixture
match the comparator reports `FIXTURE_COMPLETE_MATCH`. It reserves
`COMPLETE_MATCH` for a nonempty, closed, fully applicable universe and an
attested retail observation. A zero-overlap, empty, indeterminate or
unknown universe cannot qualify through vacuous agreement.
Missing or malformed documents receive an axis-specific
`DOCUMENT_READ_FAILED` issue while any independently qualified
structure and population decisions remain visible.



| Artifact | Canonical JSON SHA-256 | File SHA-256 |
| --- | --- | --- |
| `ledger.json` | `01d9337d432bde0b7c2ae9f568fa026c9968976b6db57c9a3fe5779acb2a3839` | `17d2ebf7df96861328f87aa40f937aed8e28f7cf1c3dd58140c5c52afd7b0d1b` |
| `oracle.json` | `bfd0c22c531d7c461fd005838d3c23787aae5edb39de8745b16f243c47b6db0c` | `35f46ec290adb118fb82f4cc2ef2792b78f15f484891c3be3a04268eaa14e362` |
| `freeze.json` | `a484a9d76e7672f1210845654439c81e93b07b494240f8303e5de5868e180fa3` | `7b99661c00ff548d979ce66f198e514a0abd14f77291ccac55d7043af7cfea7d` |



## SRR-018 comparison of the verified SRR-017 title-card capture

**PROVEN, bounded offline comparison:** the 18 November 2026 capture has
3,211 unique normalized PNDT/BIOM keys; the unchanged model has 3,210.
Their intersection is exactly 3,210, with zero model-only keys and zero
ambiguous/duplicate keys. The sole retail-only key is
`starfield.esm:05E3A5` / `starfield.esm:120C76` (Volii Alpha /
OceanLifeVoliiAlpha), also the sole observed all-zero vector. This tests
the key difference directly; it is not an inference from equal counts.
The generation CSV never admitted this owner/biome. Its absence from the
model is an input-coverage limitation, not an engine allocation error.

| Axis | Denominator and result | Applicability |
| --- | --- | --- |
| Model-corpus key overlap | 3,210/3,210 present; one additional observed key | Descriptive corpus comparison, not an independently closed native eligibility ledger |
| Strict seven-slot oracle | 0/3,211 rows admitted; 0 owners | Existing comparator returns `RETAIL_APPLICABILITY_UNRESOLVED` and `INDETERMINATE`; capture `input_sha256` is null |
| Conditional control tuples | 4/4 rows, 28/28 lanes MATCH; zero DIFFERENCE; two owners | Kreet and Decaran VII-b under existing screened base-input assumptions, not attested retail winners |
| Remaining rows | 3,207/3,211 `UNQUALIFIED_ORACLE`, 1,443 owners | Includes Volii Alpha without terrestrial model input |
| Full diagnostic projection | 3,210 corresponding rows, 22,470 ordered lanes equal, zero differing lanes | Arithmetic agreement only; does not promote unqualified rows to oracle matches |
| Derived planet membership | 1,445/1,445 resource sets equal; zero differences | Observed terrestrial union plus independently modelled atmosphere versus production membership; two conditional owners, 1,443 native-unqualified owners |

The capture retains 7,445 nonzero words and 15,032 explicit zeros. Slot
order is Common, Uncommon, Rare, Exotic, Unique, Special, Everywhere.
All seven positions, including zero holes, were compared. The projection
uses assigned cached-family results and the native Special write gate;
it does not use accepted occurrences as retained slots. The three
Special-at-eight cases previously predicted for `05E0BE/0C5717`,
`05E45F/1862BD`, and `05E591/0C5716` all have observed zero Special
lanes, agreeing with the zero projection despite selected Helium-3.
They remain unqualified whole-owner predictions. There is no concrete
value discrepancy requiring an alternate mechanism or algorithm change.

All 1,444 model owners pass the existing corpus-visible ordering,
selector, pre-pass occupancy and descendant screens. The existing
122-owner guard-cache order/multiplicity limitation remains. The
1,776-body directory has 332 owners without terrestrial generation inputs;
331 are absent from the observed allocation population, while Volii Alpha
is present. Native component eligibility for absent directory owners is
not inferred. Defining identity is distinct from a winning-content claim.
The extract namespace uses full-master index 00 for Starfield and 01 for
Shattered Space; normalization is independent of the captured runtime map.
The 19 Shattered Space candidate rows now join by defining identity for
this descriptive comparison; that does not upgrade their native oracle
applicability or retroactively change the original SRR-016 ledger.

Volii Alpha contributes no observed terrestrial IRES. Its independently
modelled effective atmosphere supplies Benzene `starfield.esm:0057E7`
and Water `starfield.esm:0083EC`; their union equals the production
atmosphere-only prediction. Thus the additional zero row explains the
population difference without implying zero planet-wide resources.
Atmosphere was not measured in the seven slots. Equal derived planet
membership proves neither atmospheric acquisition nor identical native
writes; the lane comparison is a separate result.



## Evidence custody and repeatable methods

The original dataset, observation, receipt, result and manifest were
rehashed against all five brief anchors and the original manifest.
Their durable identities are the SRR-017 acquisition hashes, including
receipt `3a48b04479bf88a8821a704a77d684cd6941585c075323ce53c0d6a14a1efea3`
and dataset `15711109761112c3ce3b2f5bf2a03966ccdb26a277ea7ec0961f0147b16eedb4`.
The complete original acquisition files are
retained privately in a SRR-017 ZIP, with member sizes,
SHA-256 identities, source provenance and archive hash. This archive is
not represented as the original temporary attachment.

The compact derivative preserves each canonical owner/biome and seven
ordered resource identities with explicit zero lanes. All 3,211 keys and
22,477 positions reconcile to both original normalized views. The compact
CSV plus frozen model inputs reproduces comparison arithmetic; native
acquisition validation separately requires the sealed receipt, qualified
reader/source identity and checked replay. The CSV cannot replace them.
Checked offline receipt replay regenerated byte-identical dataset and observation.
An independent challenger reconstructed vectors directly from the production
API/event stream, reconciled both original views without the producer's
normalizer, restored every ZIP member and checked all CSV cells. Ten
adversarial fixtures include missing/extra keys, lane movement despite
equal unions, duplicate keys, bad lane count, unknown namespace and
source/applicability refusal; the existing 28 oracle tests also passed.

| Retained artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| SRR-017-2026-11-18-original-evidence.zip | 2,915,400 | `d6ce03c7559e01bdafa78ffafae328d2f9756cea7ce58ea03fbbfbd82a0c8f8f` |
| SRR-017-2026-11-18-biome-slots.csv | 321,445 | `9675d3ac0335c98a17a636000075f76f3eb580944f510c95ff73738155a10bfb` |
| original-evidence.manifest.json | 1,354 | `b085b1493242b956d01eba4604f615d7c8a4833bcffc869da9b59b77ef7f7398` |
| biome-slots.manifest.json | 1,796 | `09a72ccc429bb7b14e7e7196d944bb9c146ec3c9b026c94e869771077045f0d2` |

Manifest filenames use the same SRR-017/date stem as their payload.
The ZIP contains the five original acquisition outputs with unchanged
names and bytes; subsequent editorial backup/summary files add no replay
input and are excluded. CSV columns define lane order, literal `0` denotes
observed zero and each nonzero cell retains its defining-plugin identity.
The preservation helper reads those originals and checks pinned reader
source; it writes the archive, CSV and manifests only to the requested
private directory. Neither helper operates the game or Ghidra.

Keep raw address-bearing evidence private. The compact CSV remains private; any future distribution requires separate review of redistribution rights and scope.



[Offline comparison and preservation commands](../tools/README.md#offline-oracle-and-comparison)
read declared lawful reproducer inputs and an explicitly supplied capture or
compact derivative. They do not require a pre-existing private directory.
The original receipt is necessary to repeat acquisition validation; compact
CSV plus frozen inputs repeats arithmetic only. Neither is distributed here.
No publication approval follows from consolidation. The sole current
[lead register](hypotheses.md) records strict-input and lifecycle questions.

[readme]: https://github.com/gooberpede/starfield-resource-reproducer/blob/a8ff1c788bca415f571f06769ab3e712fa674f75/README.md
[product]: https://github.com/gooberpede/starfield-resource-reproducer/blob/a8ff1c788bca415f571f06769ab3e712fa674f75/src/starfield_resource_reproducer/product.py
[generation]: https://github.com/gooberpede/starfield-resource-reproducer/blob/a8ff1c788bca415f571f06769ab3e712fa674f75/src/starfield_resource_reproducer/generation.py
[load]: https://github.com/gooberpede/starfield-resource-reproducer/blob/a8ff1c788bca415f571f06769ab3e712fa674f75/src/starfield_resource_reproducer/load_data.py
[exporter]: https://github.com/gooberpede/starfield-resource-reproducer/blob/a8ff1c788bca415f571f06769ab3e712fa674f75/xedit-scripts/Starfield%20-%20Export%20Planet%20Resource%20Generation.pas
[validation]: https://github.com/gooberpede/starfield-resource-reproducer/blob/a8ff1c788bca415f571f06769ab3e712fa674f75/docs/V1-VALIDATION-BASELINE.md

<!-- consolidation-review:start -->
## Documentation review disposition

**COMPLETE after rework.** An independent internal challenger checked original
scientific records, pinned native instructions, historical negative outcomes,
CK/retail applicability, routing diagrams/pseudocode, nine current questions,
archive bytes and actual reading-path reduction. The reviewed substantive
172-path manifest SHA-256 is 23a6fa183da6c9e5236686a07a96d2f3e14f0c033463f9647adfd35c2d5acb21.
It hashes sorted UTF-8 lines of file SHA-256, two spaces and repository-relative
path with LF; only this marked block and its preceding blank line are excluded
from this subject. Offline fixture/method checks do not recreate inaccessible
historical SRR-013 receipts or establish strict effective inputs. Existing
evidence grades and publication holds remain unchanged.
<!-- consolidation-review:end -->
