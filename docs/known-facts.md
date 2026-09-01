# Known Facts

This file contains **PROVEN** observations established by live execution, direct extraction, authoritative static data, or equivalent decisive evidence. **STRONG** and **PROVISIONAL** interpretations belong in `hypotheses.md`. Displaced interpretations are retained as **SUPERSEDED**.

Creation Kit addresses below apply to the live-traced CK Galaxy View Apply path. Retail validation corroborates outputs independently; it does not prove that CK addresses equal retail `Starfield.exe` addresses.

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

The **PROVEN** effective-RSGD rule is:

```text
if PNDT biome Resource Generation != NULL:
    EffectiveRSGD = PNDT override
else:
    EffectiveRSGD = BIOM.RNAM
```

The sources are not merged. Biome work objects are constructed in PNDT `BiomeIndex` order before shuffling; Kreet provides direct live proof. Stored `RSGDResourceIndex` order is semantically significant.

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

The settled order is:

```text
effective atmospheric resource IDs
    ↓
shared planet-wide resource-ID state
    ↓
Everywhere/category-6 pre-pass
    ↓
PNDT-order biome construction and deterministic shuffle
    ↓
repeated per-biome FUN_1415DCFB0 calls
```

### Atmosphere prepopulation

**PROVEN LIVE:** effective inorganic atmospheric resources enter the shared planet-wide resource-ID state before Everywhere processing and shuffled per-biome generation. Maal VIII tracing observed atmospheric Chlorine `000057D5` entering that state before main generation.

Atmosphere therefore participates in the same guarded shared state used by Everywhere, Special, Common, and emitted descendants. Atmospheric insertion consumes no generation RNG.

Static analysis locates the enclosing path through a planet-keyed type-`0xAD` form, `FUN_1419FE120`, the `+0x1D8` accessor `FUN_141A46660`, and FormIDs loaded from resolved entries at `form +0x70`. Exact engine type and field names should not be invented from the current Ghidra database.

### Everywhere/category 6

**PROVEN LIVE:** `FUN_141548920` scans effective generation entries in stored order, checks IRES category `6`, writes the selected FormID to biome/work offset `+0x68`, appends it to shared state, and runs before shuffled per-biome generation.

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

`FUN_14154C710` is the **PROVEN LIVE** fallback candidate-construction helper:

```python
has_common_entries = False
preferred = []

for resource_entry in current_effective_rsgd:
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
no Common roots in EffectiveRSGD
    → no Common family assignment

cached-family roots match current RSGD Common roots
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

The ten-body holdout is recorded in `docs/experiments/v1-holdout-validation.md`. It corroborates atmospheric output, CK biome-local terrestrial output, and retail final membership independently of address equivalence.

### Volii Alpha input boundary

Volii Alpha is absent from `PlanetResourceGeneration_v5.csv`; the independent atmosphere export contains Benzene and Water. The reproducer correctly reports known atmosphere while refusing to invent biome-local assignments.

This is a validated epistemic/input-boundary behavior, not a recovered engine rule and not evidence about Volii Alpha's actual terrestrial biome allocation. Missing PNDT/effective-RSGD input remains unknown or unavailable, not “no resources.”

## SurveyAggregator and Qualified Oracle

`SurveyAggregator` (RE ID `1016657`) and `data/planet-all-resources.csv` remain valuable empirical/canonical validation evidence for the CK/RSGD-visible channel. The dataset is proven incomplete for atmosphere-derived final membership, does not expose biome identity in current use, and must never be used as generation logic. Its exact upstream semantic contract remains unresolved and is non-blocking for v1.0.

Historical qualified-dataset observations remain valid within that boundary:

- zero descendant-without-root cases across the recorded 1,549 body/family cases and 2,064 descendant occurrences;
- zero `FamilyCount > BiomeCount` cases across 1,436 analysed family-bearing bodies;
- 1,038 equal-count bodies, including 880 one-family/one-biome bodies.

These are planet-level constraints, not direct proof of biome co-location.

## Atmospheric Data Extraction

ATMO reflection data resolves inherited effective values. The dedicated xEdit atmospheric exporter recorded 335 planet-resource rows across 297 bodies, six resource types, no duplicate planet-resource rows, and at most two atmospheric resources per body.

The generic interpretation that a sole zero-count reflected `LIST` explicitly clears inherited Inorganic Resources remains **PROVISIONAL** and is retained in `hypotheses.md`.

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
