# Recovered inorganic generation

The v1.0 model recovers PNDT/BIOM/effective-RSGD inputs, IRES hierarchy,
effective inorganic atmosphere, nonzero RSCS MT19937 state, biome shuffle,
Everywhere, Special, Common families, descendants, caching, guards and fallback.
Its scope excludes organics, terrain vein geometry, extractor placement and
unqualified executable or data versions. A biome assignment alone does not
locate an outpost-scale deposit.

**Evidence domain:** the algorithm's live implementation anchors below are
Creation Kit Galaxy View Apply observations. [Provenance](PROVENANCE.md)
separates fingerprinted CK static exports from live traces lacking a
trace-specific executable hash. Static Ghidra bundles are not live traces.
The pinned retail 1.16.244.0 image has separately established native
correspondences; CK addresses must never be used as retail addresses.
[Retail lifecycle](retail-execution-lifecycle.md),
[component database](component-database.md) and
[allocation validation](allocation-validation.md) cover that evidence.
Matching outputs corroborate behavior within tested scope, not instruction-level
identity or a retail-live trace of each recovered CK operation.

The evidence stack combines prior live x64dbg observation, focused read-only
Ghidra exports, authoritative xEdit PNDT/BIOM/RSGD/IRES/ATMO extraction,
pathological CK regressions, 1,444 canonical planet memberships and ten fresh
CK/retail holdouts. Live evidence governs a conflicting static interpretation;
superseded scientific conclusions below preserve the distinction.

## Input Resolution and Biome Order

```text
PNDT
 ├─ RSCS
 └─ ordered biome entries
        ↓
      BIOM
        ↓
      RSGD
```

The **PROVEN within recovered v1 input scope** effective-RSGD rule is:

```text
if PNDT biome Resource Generation != NULL:
    EffectiveRSGD = PNDT override
else:
    EffectiveRSGD = BIOM.RNAM
```

The v1 input abstraction does not merge these sources. Native direct-source
selector retry and the distinct BIOM-list Everywhere/fallback paths are
qualified below; this input rule alone is not proof of every native override
edge case. Biome work objects are constructed in PNDT `BiomeIndex` order before shuffling; Kreet provides direct live proof. Stored `RSGDResourceIndex` order is semantically significant.

The IRES category mapping is:

```text
0 Common
1 Uncommon
2 Rare
3 Exotic
4 Unique
5 Special
6 Everywhere
```

## PRNG Mechanism Register

Nonzero unsigned 32-bit PNDT `RSCS` directly seeds MT19937. The same evolving state drives shuffle and generation.

These mechanisms must remain distinct:

1. biome-shuffle integer rejection/modulo;
2. MT19937 → binary32 probability conversion;
3. Special/Common ordered weighted selection;
4. descendant float32-scaled candidate indexing;
5. guard-fallback float32-scaled cached-family indexing.

The shared probability conversion is:

```python
raw_float = float32(raw_uint32)
unit_value = float32(raw_float * float32(1.0 / 2**32))
probability = float32(unit_value * float32(0.99999))
```

### Biome-shuffle integer helper

The **PROVEN** helper uses rejection and modulo:

```python
while True:
    raw = next_uint32()
    threshold = UINT32_MAX // upper_bound
    if raw // upper_bound < threshold:
        return raw % upper_bound
```

Rejected draws consume MT words. Bound one consumes one word and returns zero.

### Float32-scaled indexes

Descendant selection and guard fallback use the probability conversion but are separate semantic primitives:

```python
index = trunc(float32(probability * float32(candidate_count)))
```

For a nonempty pool, each consumes exactly one MT word. A one-element guard-fallback pool still consumes the draw.

## Enclosing Generation Order

`FUN_14152CBC0` is the **PROVEN STATIC** sole direct caller and enclosing orchestration function for `FUN_1415DCFB0`. The call at `0x14152D28F` receives the shared resource-ID array as argument four and the generated/cached Common-family collection separately.

The native work list is constructed in PNDT order and shuffled before shared-ID prepopulation. Prepopulation consumes no generation RNG. The allocation order after that shuffle is:

```text
effective atmospheric resource IDs
    ↓
shared planet-wide resource-ID state
    ↓
Everywhere/category-6 pre-pass
    ↓
repeated FUN_1415DCFB0 calls in the already shuffled biome order
```

### Atmosphere prepopulation

**PROVEN LIVE:** effective inorganic atmospheric resources enter the shared planet-wide resource-ID state before Everywhere processing and shuffled per-biome generation. Maal VIII tracing observed atmospheric Chlorine `000057D5` entering that state before main generation.

Atmosphere therefore participates in the same guarded shared state used by Everywhere, Special, Common, and emitted descendants. Atmospheric insertion consumes no generation RNG.

Static analysis locates the enclosing path through a planet-keyed type-`0xAD` form, `FUN_1419FE120`, the `+0x1D8` accessor `FUN_141A46660`, and FormIDs loaded from resolved entries at `form +0x70`. Exact engine type and field names should not be invented from the current Ghidra database.

### Everywhere/category 6

**PROVEN LIVE:** `FUN_141548920` scans the biome generation dependency entries in stored order (CK BIOM +0x728/+0x730), checks IRES category `6`, writes the selected FormID to biome/work offset `+0x68`, appends it to shared state, and runs before shuffled per-biome generation.

It does not consult DNAM Everywhere chance and consumes no RNG. Fermi VIII-b `OceanDefaultRes` is the decisive live case.

The earlier idea that Everywhere used a chance field or ordinary weighted selection is **SUPERSEDED**.

## Per-Biome Generator

`FUN_1415DCFB0` is the **PROVEN LIVE** primary per-biome generator in the CK Galaxy View Apply path.

Within each invocation:

```text
Special/category-5 selection
→ Special written/recorded into shared state
→ five-tree guard
→ shared-eight guard
→ normal Common/category-0 selector OR guard fallback
→ new family generation OR cached-family assignment
```

Each processed biome receives at most one Common-family configuration through
this recovered per-biome Common assignment mechanism. Atmosphere, Everywhere,
and Special occurrences are separate and may coexist with it.

### Special/Common selector

`FUN_141580660`, with `FUN_14157C470`, is **PROVEN** for categories `5` and `0`:

```text
one MT19937 binary32 probability draw before enumeration
stored 0x238-byte RSGD order
category filter
cumulative Chance / 100
first roll < cumulative
no normalization
```

The up-front draw occurs with zero entries, one entry, or a single 100-percent entry. Special occurs before Common and is not a planet-wide pre-pass.

### Special insertion before guards

**PROVEN LIVE:** a selected Special is written and recorded into shared state before either Common guard. A new Special can fill slot eight and force the current biome into guard fallback. A duplicate Special does not increase the modeled unique-identity count.

Universal same-FormID behavior across every possible insertion site has not been directly traced. The cross-origin unique-FormID occupancy rule is a **STRONG, full-corpus-validated model**, while the shared count and guard at eight are proven.

## Common Family Generation and Cache

IRES `SNAM` rarity and Child Resources encode the family graph. For rarities `1..4`, candidate construction is stable-deduplicated `children(root) + children(current_structural_node)`, filtered to the requested rarity, with root-source candidates first.

`FUN_14157F120` is the **PROVEN LIVE** descendant helper. It draws inclusion and candidate selection, emits on inclusion, and advances structurally through the chosen candidate even when omitted. With zero candidates it consumes exactly one MT word, emits nothing, and leaves the structural node unchanged.

A newly selected Common root is emitted unconditionally. Its descendant result becomes an immutable planet-scope family configuration. Ordinary reuse is:

```text
normal Common weighted selector chooses root
→ cache hit
→ cached root + emitted descendants assigned to current biome
→ no descendant-generation RNG
```

This is distinct from guard fallback because ordinary reuse still performs the Common weighted selector.

## Common Guards

### Five-tree guard

**PROVEN LIVE for this generation path:** the guarded structure is the collection of already-generated/cached Common-family configurations.

Bara VII-d showed:

```text
0, 1, 1, 2, 2, 3, 4, 5
```

Normal cache reuse does not increment the count. At five:

```asm
1415DD0D3  cmp dword ptr [rsi],5
1415DD0D6  jae 1415DD255
```

The precise scope is five distinct generated/cached Common-family configurations. At the guard, normal Common selection is suppressed and fallback begins.

### Shared-eight guard

**PROVEN LIVE / STATIC:**

```asm
1415DD0DC  cmp dword ptr [r12],8
1415DD0E1  jae 1415DD255
```

At eight shared resource IDs, the normal Common selector is skipped before its usual RNG draw. The descendant helper likewise returns without consuming RNG when the shared count is at least eight.

**SUPERSEDED:** the shared-eight guard does not imply an empty biome or no Common-family assignment. It suppresses normal selection and enters fallback.

## Guard Fallback Assignment

**PROVEN LIVE:** both Common guards branch to fallback logic beginning near `0x1415DD255`. Fallback can assign an existing cached family configuration to the current biome without creating a new planet-wide identity or rerunning descendant generation.

### Candidate construction

`FUN_14154C710` is the **PROVEN LIVE** fallback candidate-construction helper.
Native list provenance differs from the optional direct source used by normal
selection: CK reads the resolved BIOM +0x728/+0x730 dependency list at
`0x1415DD273/281` before the call at `0x1415DD33C`. The following pseudocode
expresses candidate construction over that list; it does not prove that a
PNDT override replaces it:

```python
has_common_entries = False
preferred = []

for resource_entry in current_biome_generation_list:
    if resource_entry.resource.category != Common:
        continue
    has_common_entries = True
    for cached_family in generated_family_cache:
        if cached_family.root_form_id == resource_entry.resource.form_id:
            preferred.append(cached_family)
```

It applies no chance weighting.

### Decision rule and RNG

Jaffa VII-b proves:

```text
no Common roots in the scanned biome generation list
    → no Common family assignment

cached-family roots match scanned Common roots
    → choose from matching cached families

Common roots exist but none match
    → choose from all already-generated cached families
```

`FUN_14015B4A0`, through thunk `FUN_1401190CD` and `FUN_140924800`, performs the float32-scaled choice. A one-element pool consumes a probability draw. The selected cached root and previously emitted descendants are copied into the current biome's Common slots; the family is not regenerated.

Assignment provenance is:

```text
NEW_FAMILY
NORMAL_CACHE_REUSE
GUARD_MATCHED_FALLBACK
GUARD_GENERAL_FALLBACK
NO_COMMON_ASSIGNMENT
```

Family configuration origin and current biome assignment are separate. Preferred wording is:

> The planet-scope family configuration was first generated while processing biome X and was later assigned to biome Y.

## Capacity and Provenance Model

**PROVEN LIVE / STATIC:** the shared resource-ID state is guarded at count eight.

**STRONG / validated model:** occupancy is deduplicated by IRES FormID across modeled atmosphere, Everywhere, Special, Common-root, and descendant origins. Repeated occurrences retain provenance without consuming a second modeled slot. This is not claimed as a universal trace of every possible cross-origin collision.

Keep separate:

- planet-wide resource identity;
- resource occurrence provenance;
- family configuration cache;
- family configuration origin;
- current biome Common-family assignment.

## Validation Baseline

The current v1.0 reference model records:

```text
pre-07B: 1,281 / 1,444
07B:     1,426 / 1,444
08A:     1,441 / 1,444
08B:     1,442 / 1,444
08C+:    1,444 / 1,444

08D / 08D.1:
    planet-wide remains 1,444 / 1,444
    targeted pathological CK biome regressions exact

fresh holdout:
    10 / 10 exact CK + retail
    0 observed errors
```

The ten-body holdout is listed below; its channels must remain separate. It corroborates atmospheric output, CK biome-local terrestrial output, and retail final membership independently of address equivalence.

### Volii Alpha input boundary

Volii Alpha is absent from `PlanetResourceGeneration_v5.csv`; the independent atmosphere export contains Benzene and Water. The reproducer correctly reports known atmosphere while refusing to invent biome-local assignments.

This is a validated epistemic/input-boundary behavior, not a recovered engine rule and not evidence about Volii Alpha's actual terrestrial biome allocation. Missing PNDT/effective-RSGD input remains unknown or unavailable, not “no resources.”

## SurveyAggregator and Qualified Oracle

`SurveyAggregator` (RE ID `1016657`) and the historical `planet-all-resources.csv` snapshot remain valuable empirical/canonical validation evidence for the CK/RSGD-visible channel. The dataset is proven incomplete for atmosphere-derived final membership, does not expose biome identity in current use, and must never be used as generation logic. Its exact upstream semantic contract remains unresolved and is non-blocking for v1.0. The snapshot is no longer distributed from this research repository; maintained canonical data and tooling live in the sibling reproducer.

Historical qualified-dataset observations remain valid within that boundary:

- zero descendant-without-root cases across the recorded 1,549 body/family cases and 2,064 descendant occurrences;
- zero `FamilyCount > BiomeCount` cases across 1,436 analysed family-bearing bodies;
- 1,038 equal-count bodies, including 880 one-family/one-biome bodies.

These are planet-level constraints, not direct proof of biome co-location.

## Atmospheric Data Extraction

ATMO reflection data resolves inherited effective values. The dedicated xEdit atmospheric exporter recorded 335 planet-resource rows across 297 bodies, six resource types, no duplicate planet-resource rows, and at most two atmospheric resources per body.

The generic interpretation that a sole zero-count reflected `LIST` explicitly clears inherited Inorganic Resources remains **PROVISIONAL** and is retained in [the lead register](hypotheses.md).

## Superseded Primary Trail

The following low-level static work remains valid historical evidence:

```text
ResourceViewWidget::OnApplySeed
    ↓
FUN_1431bc320
    ↓ temporary TESContainer / FUN_140e0aab0
FUN_140e457b0
    ↓ generic leveled-list machinery
```

Its interpretation as the primary biome allocator is **SUPERSEDED / DEPRIORITISED** by live CK tracing of `FUN_1415DCFB0` and descendants. Do not delete its evidence or reconnect it to allocation without new live evidence.

## Provenance-Aware Validation

Validation must preserve origin channels:

```text
AtmosphericResources
EverywhereResources
SpecialResources
BiomeGeneratedResources
FinalPlanetaryResources
```

An atmospheric FormID must not mask failure of an RSGD path expected to produce the same identity. Deduplicate only at the final player-facing membership boundary while retaining occurrence and assignment provenance internally.



## Selector sources and native arithmetic

The [static selector bundle](experiments/evidence/special-common-selector/README.md)
contains the focused exports and repeatable read-only export command.
`FUN_141580660` receives RCX selector context, RDX caller-owned 16-byte result,
and R8B category. It draws before trying the optional direct source; if that
produces no two-pointer result, it visits resolved dependency sources from
`+0x728` in stored order, stopping at the first successful result. Exact C++
source types remain unnamed. Context fields are tabulated in the
[structure register](structure-register.md#creation-kit-reference).

The generation object has u32 entry count at `+0x118`, array pointer at
`+0x120`, and entry stride `0x238`. The resource category byte is `+0x2F8`.
At `0x14157C5AA` the scanner tests that byte against the requested category.
Instructions `0x14157C5B3–0x14157C5CA` derive the chance address and add
`float32(chance * 0.01f)`; `0x14157C5DE–0x14157C5E3` implements the strict
threshold comparison. Returns at `0x14157C5F7`, `0x14157C5FA` store resource and entry+8.
The caller reads the resource FormID at `+0x70`.

Chance locations `entry+0x24` (category 0) and `entry+0xEC` (category 5)
are **STRONG** correlations with xEdit Common/Special chance names; arithmetic
and offsets are **PROVEN STATIC**. The exact `0.01f` constant is loaded from
`0x148544E84` at `0x14157C4E1`. A total below 100 can leave no result;
excess weights retain stored order and receive no normalization.

`FUN_144D8C490` supplies the range at `0x141580699`; the selector calls the
MT-to-binary32 primitive at `0x1415806A8` and applies the range at
`0x1415806E4–0x1415806F4`. `FUN_140924800` itself generates the binary32 unit
value; its caller supplies the `0.99999f` range scaling. The primitive's loop
`0x140924870–0x1409249EF` runs once for binary32 precision,
`ceil(24/log2(2**32)) = 1`. The range maximum is exactly
`0.9999899864196777f`. Keep the primitive and caller scaling distinct even
when describing their composed probability conversion.

Prior Callisto live observation selected Helium-3 `000057F5` for category 5
then Iron `000057C7` for category 0 in CrateredNoLife09. Its ordered input is
Iron/Common30, Aluminum/Common70, Helium-3/Special100. **STRONG reconstructed
state**, rather than newly observed raw words: unsigned seed 2041483075, with
no single-biome shuffle draw, produces probabilities approximately 0.35974094
and 0.00357435, explaining that pair. The original supplied Callisto trace
was unavailable for independent per-instruction register extraction; the
static bundle does not replace it.

## Native orchestration and guard locators

The [pre-biome static bundle](experiments/evidence/pre-biome-resource-state/README.md)
preserves the exported orchestration excerpt, instructions and metadata.
The enclosing CK function's two direct wrappers call at `0x14157E8E4`
(`FUN_14157E850`) and `0x14158DC6E` (`FUN_14158DBE0`). Static references do not
identify which wrapper served the prior Galaxy View Apply observation;
the latter has no direct static caller in that database.

| Operation | CK instruction locator |
| --- | --- |
| Shuffle call | `0x14152CEBD` → `0x1401714A8` → `FUN_141560E90`; `0x141560F5A` → `0x14001D63D` → real bounded helper `FUN_141587240` |
| Shared uint32 array setup | `0x14152CEC2–0x14152CF00`; initialized once, retained across biome calls |
| Planet-keyed lookup/access | `0x14152CF17` → `FUN_1419FE120`, `0x14152CF28` → `FUN_141A46660` |
| Atmospheric FormID/load/append | `0x14152D034`, `0x14152D0D3`, store `0x14152D0E9`; direct-list duplicates checked before append |
| Everywhere call/test/write/append | `0x14152D1B5`, `0x141548AC9`, `0x141548ADA`, `0x141548AE7` |
| Family cache initialization | `0x14152D1D0`, after both prepopulation paths |
| Per-biome call/continuation | `0x14152D28F`, loop `0x14152D29B` |
| Special selector | `0x1415DD09E`, category 5 |
| First shared count check | `0x1415DD0A3`, `0x1415DD0A8`, count 8 |
| Family/Common guard | `0x1415DD0D3`, `0x1415DD0D6`, count 5, target `0x1415DD255` |
| Shared/Common guard | `0x1415DD0DC`, `0x1415DD0E1`, count 8, same fallback target |
| Normal Common selector | `0x1415DD0F2`, category 0 |

The lookup uses the current planet field `+0x134`; returned type byte
`+0x88 == 0xAD` is a static observation, not a recovered C++ type name.
`FUN_141A46660` returns `object+0x1D8`; the caller interprets it as a
count/pointer array of dependency-managed resource forms.
Before Everywhere processing the caller clears work fields `+0x50..+0x68`.
The helper takes the first category-6 match from its ordered nested records,
writes its FormID, appends and returns.

The Maal VIII final Iron-biome trace observed Iron bringing shared count to
eight. `FUN_14157F120` loaded the shared pointer from context `+0x20` at
`0x14157F14D`, compared at `0x14157F151`, and branched at `0x14157F154` to
`0x14157F371`: unchanged structural node, no RNG, no Alkanes emission.
The CK generation view had Iron, Nickel, Water, Uranium, Iridium, Vanadium
and Copper; retail survey additionally had Chlorine, supported by ATMO and
later directly traced before Everywhere. Earlier mismatch analysis found
atmospheric resources on 101/163 mismatch planets; that historical correlation
was supporting evidence, not itself the decisive insertion proof.

## Fresh holdout identities and channels

| Body | System |
| --- | --- |
| Vesta | Lunara |
| Niira | Narion |
| Eridani IV | Eridani |
| Cassiopeia IV-a | Eta Cassiopeia |
| Cassiopeia II-a | Eta Cassiopeia |
| Zosma V-a | Zosma |
| Eridani III-b | Eridani |
| Luyten's Rock | Luyten's Star |
| Bardeen V-d | Bardeen |
| Ka'zaal | Nirah |

All ten were fresh validation bodies after the fallback and Special-order
corrections: atmospheric output matched observed atmosphere, terrestrial biome
distributions matched CK, and final planetary membership matched retail scan.
The sample covers atmospheric overlap/descendants, Everywhere Water duplication,
one/two atmospheric resources and capacity/cache/fallback opportunities.
No unrecorded per-biome tables or per-body resource vectors are inferred.
Retail retained-slot agreement is a separate comparison with stricter
input-attestation limitations, described in [allocation validation](allocation-validation.md).

## Research ownership and unresolved boundaries

The research repository owns evidence, native locators and applicability;
the sibling reproducer owns the executable model and regressions. A settled
rule change requires a reproducible counterexample, classified research
evidence, reconciled baseline, implementation brief, reproducer change,
regression and renewed canonical/holdout validation. The
[sole lead register](hypotheses.md) owns current unresolved questions.
Non-blocking type names, unusual empty-cache guard reachability and upstream
oracle semantics do not justify reopening the validated algorithm.


## Pinned retail correspondence and native differences

These are **retail static** findings on Starfield.exe 1.16.244.0,
SHA-256 `7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28`,
preferred base `0x140000000`. They qualify corresponding native operations;
they do not upgrade the CK live observations to retail-live execution proof.
The [function register](function-register.md) supplies the compact function map.
The original SRR-002 focal listings were independently checked against PE bytes;
its broad discovery census had partial-decode and exception-range limitations,
so uniqueness/negative search conclusions are bounded to those decoded prefixes.

**Orchestration and inputs — PROVEN STATIC.** `FUN_140779760` obtains a
planet-keyed type-0xAD atmosphere form or fallback at `0x140779973`, walks
count/pointer fields +0xF8/+0x100 and duplicate-checks IDs before the store at
`0x140779AA6`. Its Everywhere pass is inlined at `0x140779B32`: a type-0xA0
BIOM supplies +0x308/+0x310, category 6 is tested at `0x140779B93`, and the
first nonzero match writes work+0x68 and inserts its ID at `0x140779BB8`,
without probability RNG. Per-biome call `0x140779C86` passes the work pointer,
MT state in RDX, separate family array in R8 and shared-ID array in R9.
The CK atmosphere and BIOM field layouts differ.

Retail reads the planet seed at +0x50 and initializes the same stack MT state
used later. Shuffle calls `0x1407798E0/0x1407798EB` feed pointer swaps;
rejection and unsigned remainder occur at `0x14077C8CE–0x14077C936`.
The full-width sibling branch and field-to-record seed provenance lack live
vector qualification. A **PROVEN STATIC** zero-planet-seed branch reseeds per
biome from its work field before generation; the recovered validated nonzero
RSCS scope must not be read as excluding that native zero-seed path.

**Per-biome sequence — PROVEN STATIC.** BIOM/optional direct RSGD type gates
are at `0x140777900/0x14077791A`. The selector receives categories 5 and 0 at
`0x140777954/0x1407779A4`. Between them a writable Special result enters
work+0x64 and shared state. Separate family/shared count guards at
`0x140777986/0x14077798F` converge on `0x140777AF8`. A newly generated family
appends a pointer to its five-ID work configuration on successful allocation
at `0x140777A88–0x140777A8B`; ordinary cache reuse copies five IDs.
The shared insert `FUN_1403c9970` checks existing uint32 IDs before append
and serves Everywhere, Special, Common roots and emitted descendants; the
atmosphere loop has its own duplicate check. These are distinct from family
configuration pointer storage.

**Selector — PROVEN STATIC, finite ordered scope.** Draw `0x140777E69`
precedes enumeration. A primary direct RSGD scan is inline; only if both
output pointers remain zero can the BIOM list retry call the outlined scanner
at `0x140777FAD`. Entries retain stride 0x238 and indexed chance
+0x24+category×0x28, but retail's resource category byte is +0x110. Binary32
0.01-scaled cumulative thresholds return `{form,entry+8}` when roll is strictly
less than cumulative for finite ordered values. Equality falls through at
`0x140777F3D/0x140778069`; the same carry branches accept unordered operands
if comparison completes. Nonfinite weights/chances were untested. Thus the
ordinary finite selector correspondence does not establish arbitrary nonfinite
or full override/null-case equivalence.

**Descendants — STRONG correspondence, PROVEN static draws.** The
count-eight branch `0x1407780E6` bypasses RNG. Otherwise an inclusion draw
precedes root and optional distinct-node child scans. A nonempty pool takes
a second draw and float32-scaled index; the selected structural node can be
returned without emission. Retail's child append loop
`0x140778533–0x1407785CD` filters rarity but has no visible per-entry duplicate
check. Overlapping lists may therefore preserve multiplicity if duplicate
pointers reach it; upstream uniqueness is unqualified. Do not silently promote
the CK/reference stable-deduplicated pool into a proven universal retail rule.
Nonfinite emission-chance behavior also remains untested.

**Fallback source — PROVEN STATIC.** At `0x140777B22` candidate construction
receives BIOM+0x308, while the optional direct RSGD resolved from work+0x4C
is unused at that site. This matches the CK BIOM-list walk at
`0x1415DD273/281` and fallback call `0x1415DD33C`; normal selection's override
precedence must not be substituted for fallback list provenance. The retail
helper flags category 0 at `0x14077C183–0x14077C191` and compares cached root
IDs at `0x14077C1B7`. Zero-lower-bound float-scaled choices at
`0x140777B48/0x140777B64` select the matching pool or whole cache when Common
exists and no match does. A nonnull selected pointer supplies five copied IDs,
without descendants. PNDT field provenance, repeated matches, empty-cache and
allocation-failure cases remain qualified. The validated v1 model's effective
input abstraction is not fresh proof about those untested override cases;
no reproducer algorithm change follows from this editorial reconciliation.

**Probability primitive — PROVEN STATIC.** `FUN_1402fbc20` has the 624-word
boundary, state advance/twist and equivalent pre-shift temper masks; its first
mask is state-resident. It converts uint32 and divides by binary32 2**32 on
the one-word path at `0x1402FBE25`. Retail callers separately supply the
0..0.99999 range at `0x14591F4C8`. A failed search for conventional literal
temper-mask pairs did not disprove MT identity. Unrelated callers and alternate
MT-looking functions are not allocation anchors.

Reproduce these bounded static claims with a lawful matching image and an
already analyzed matching Ghidra program, using the tracked exporter:

```text
analyzeHeadless <project-directory> Starfield -process Starfield.exe -readOnly -noanalysis -scriptPath ghidra/scripts -postScript ExportFunctionsByAddress.java <fresh-local-output> 140779760 140777870 140777E30 140777FF0 1407780B0 1407784D0 14077C0E0 1402FCEE0 1402FBC20
```

The command reads the analyzed program and writes external reports; it does
not modify the project. Native source listings and historical broad-scan
receipts remain privately held rather than distributed game-derived payloads.
The tracked export is a reproducible method, distinct from custody-backed
historical observations. Upstream dispatch candidates from SRR-002 were later
resolved by the [retail lifecycle evidence](retail-execution-lifecycle.md);
those former discovery questions are not duplicate active leads.
