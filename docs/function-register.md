# Function Register

This register tracks native functions relevant to Starfield resource generation.

Names beginning with `FUN_` are Ghidra-generated identifiers unless otherwise stated.

Do not replace an original Ghidra name with a semantic alias unless evidence is strong. Proposed aliases should be recorded separately.

---

## ResourceViewWidget::OnApplySeed

**Name:** `ResourceViewWidget::OnApplySeed`  
**Address:** to be recorded from the current Ghidra project  
**Source context:** Creation Kit  
**Status:** known named anchor  
**Confidence:** high

### Current interpretation

Entry point associated with applying a resource seed in the Creation Kit resource-preview UI.

### Known relationship

```text
ResourceViewWidget::OnApplySeed
    ↓
FUN_1431bc320
```

### Why it matters

This is currently the strongest named entry point into resource-seed processing.

### Open questions

- What object owns the seed/resource-preview state?
- Which arguments carry PNDT, BIOM, RSGD, or RSCS-derived data?
- Does this path call shared game-runtime allocation logic or CK-specific preview logic?
- What state is populated before and after this function returns?

### Next analysis

Export:
- decompilation;
- callers;
- callees;
- referenced globals;
- referenced strings;
- structure offsets;
- argument flow into `FUN_1431bc320`.

---

## FUN_1431bc320

**Name:** `FUN_1431bc320`  
**Address:** `0x1431BC320`  
**Proposed role:** resource seed / preview processing intermediary  
**Status:** primary current target  
**Confidence:** medium that it is close to target logic; low on exact semantics

### Known relationship

```text
ResourceViewWidget::OnApplySeed
    ↓
FUN_1431bc320
    ↓
FUN_140e457b0
```

### Current interpretation

This function lies directly downstream of the Creation Kit Apply Seed action and upstream of lower-level selection machinery.

Its exact semantic role remains unresolved.

### Why it matters

This is the preferred first target for automated Ghidra context export.

### Questions to answer

- What arguments enter the function?
- Which arguments originate from the ResourceViewWidget or planet/resource configuration?
- Which fields/offsets are read from each object?
- Are BIOM or RSGD pointers referenced directly or indirectly?
- Is an RSCS-derived value created, transformed, or passed onward here?
- Which callees are resource-specific versus generic utility code?
- What values are passed to `FUN_140e457b0`?

### Next analysis

First tooling milestone:

```text
export complete one-function analysis context for FUN_1431bc320
```

Then inspect its immediate call neighbourhood.

---

## FUN_140e457b0

**Name:** `FUN_140e457b0`  
**Address:** `0x140E457B0`  
**Proposed role:** lower-level selection / leveled-list evaluation path  
**Status:** known investigative anchor  
**Confidence:** medium

### Current interpretation

Prior Ghidra work traced this function into generic leveled-list evaluation machinery.

An RSCS-derived or seed-derived value appeared to behave more like an effective level/input than an obvious conventional PRNG seed.

### Known relationship

```text
FUN_1431bc320
    ↓
FUN_140e457b0
    ↓
generic leveled-list evaluator
```

### Important caution

Reaching leveled-list machinery does not establish that this function itself assigns resource families to biomes.

It may instead be a generic selector used by a higher-level resource-specific algorithm.

### Questions to answer

- What exact leveled list or data structure is supplied?
- Where was that list selected?
- What is the semantic meaning of the effective-level/selector argument?
- Does the function choose a family, a family member, a branch, or some downstream placement item?
- Which resource-specific callers invoke it?

### Next analysis

Use the automated exporter to:
- enumerate all callers;
- identify caller clusters;
- inspect constant/offset patterns;
- locate resource-specific callers distinct from generic leveled-list use.

---

## SurveyAggregator

**Name:** `SurveyAggregator`  
**RE ID:** `1016657`  
**Runtime binding type:**

```cpp
using fn_aggregator_t = void (*)(void* buffer, std::uint32_t planet_id);
```

**Source context:** Starfield runtime  
**Status:** authoritative runtime observer  
**Confidence:** high for observed output; low that it is allocation logic

### Current interpretation

Fills a fixed-size aggregation buffer for a planet.

Existing runtime tooling iterates the populated spans and filters resource forms to recover authoritative final planet-wide resources.

### Established use

Used to create the canonical runtime-derived planet/resource dataset.

### Why it matters

It provides a large-scale oracle against which candidate reconstructed algorithms can be tested.

### Limitation

Current use exposes planet-wide final resource membership but not biome identity.

### Questions to answer

- Is resource allocation already complete before this function runs?
- What structures does it read?
- Is per-biome state available upstream?
- Can a related function expose final resource membership by biome?
- Is there a useful data structure connecting survey/resource state to BIOM records?

### Suggested priority

Secondary to the Creation Kit Apply Seed trail for now.

Return to this path when:
- validating candidate algorithms;
- searching for runtime per-biome result structures;
- or identifying where final allocations are consumed.

---

## Generic Leveled-List Evaluator

**Name:** exact function/address to be recorded  
**Status:** downstream dependency  
**Confidence:** high that generic list-selection machinery is involved somewhere in the observed path

### Current interpretation

Generic engine logic reached from `FUN_140e457b0`.

### Important caution

This is likely infrastructure rather than the complete resource-allocation algorithm.

### Questions to answer

- What list definition is passed by resource-specific code?
- Is the selector input derived from RSCS?
- Is family structure represented through nested lists?
- Which higher-level function chooses the relevant list for a BIOM/RSGD context?

---

## LL_ResourceSurfaceFlora_* consumers

**Type:** leveled-list/data family rather than one function  
**Status:** investigated and deprioritised

### Current interpretation

These lists appear to be downstream surface-placement machinery.

Observed behaviour includes conditions based on body resource availability and rarity weighting.

### Conclusion

They are not currently considered the primary source of planet/biome resource allocation.

### Revisit only if

Static analysis shows that family/member selection feeds directly into these lists in a way not previously understood.

---

# Candidate Register Template

## FUN_xxxxxxxxx

**Name:** `FUN_xxxxxxxxx`  
**Address:** `0x...`  
**Proposed alias:** none  
**Source context:** Starfield runtime / Creation Kit / unknown  
**Status:** candidate  
**Confidence:** low / medium / high

### Observed behaviour

Record only what is directly supported by decompilation, xrefs, runtime testing, or dataflow.

### Known relationships

```text
caller
  ↓
this function
  ↓
callee
```

### Current interpretation

State the best working interpretation and clearly mark uncertainty.

### Evidence

- caller/callee relationship:
- referenced string:
- global access:
- structure offset:
- runtime observation:

### Questions

- ...

### Next analysis

- ...
