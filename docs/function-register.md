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
    ├─ resolved TESContainer virtual slot +0x50 / index 10 → FUN_140e0aab0
    └─ FUN_140e457b0
```

Live `ExportFunctionNeighbourhood.java` output resolves the computed call at
`0x1431BC350` through `TESContainer::vftable` slot byte offset `0x50` (index
10), via `thunk_FUN_140e0aab0` at `0x1400904FD`, to `FUN_140e0aab0`.

Machine code and high p-code now establish the three actual arguments as:

```text
RCX = &temporary TESContainer at caller stack offset -0xA8
RDX = *(ResourceViewWidget + 0x30)
R8  = *(ResourceViewWidget + 0xA0) + 0x20
```

There is no fourth or stack argument. `R9` is not defined as an argument at the
call; its physical value is caller-saved residue after the preceding constructor
call. High-p-code `CALLIND` input 0 is the target and inputs 1, 2, and 3 map to
the three values above.

The `+0x20` operation is literal pointer adjustment after the single load from
`ResourceViewWidget + 0xA0`; no hidden extra dereference occurs at the call
site. The callee immediately dereferences the adjusted pointer as a polymorphic
object and invokes its vtable slot `+0x30`. This strongly supports that the
concrete QTreeWidget-compatible object has a component-compatible subobject at `+0x20`.
It does not place that subobject in Qt's plain `QTreeWidget` layout or identify
the concrete multiple-inheritance/containment declaration.

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

## FUN_140e0aab0

**Name:** `FUN_140e0aab0`

**Address:** `0x140E0AAB0`

**Proposed role:** generic `TESContainer` source-to-destination component copy operation

**Status:** confirmed resolved virtual target; semantics tentative

**Confidence:** high for the call edge and source/destination dataflow; medium for a semantic `CopyComponent` name

### Established relationship

```text
FUN_1431bc320 computed call at 0x1431BC350
    ↓ TESContainer::vftable slot +0x50 / index 10
FUN_140e0aab0
```

The source-like argument supplied by `FUN_1431bc320` is derived from:

```text
*(param_1 + 0xA0) + 0x20
```

### Confirmed ABI and first-use facts

`FUN_140e0aab0` has three analyzed `__fastcall` parameters stored in `RCX`,
`RDX`, and `R8`. At entry it preserves them as destination, context/owner, and
source candidates respectively. It first uses the `R8` value by loading its
vptr and calling virtual slot `+0x30`, compares the returned identity against
the identity value used by this TESContainer routine, and returns without copying on a
mismatch. On a match it:

- prepares the `RCX` destination with the `RDX` value;
- reads source count/capacity at source `+0x40`;
- reads the source element pointer at source `+0x48`;
- grows and writes the destination array at destination `+0x40/+0x48`;
- copies 0x18-byte source elements through a helper that also receives `RDX`.

This is strong source-to-destination component-copy behavior. The exact engine
method name remains unknown.

### Important caution

The resolved receiver is a temporary `TESContainer`. The callee's vptr dispatch,
identity gate, and subsequent source-field reads establish that the adjusted
`+0x20` value is a compatible polymorphic component subobject, not an opaque
address. Current evidence does not determine whether the concrete
QTreeWidget-compatible type obtains that subobject through multiple inheritance
or containment, nor does it justify calling the enclosing UI object itself a
`TESContainer`.

### Next analysis

- identify the concrete QTreeWidget-compatible class stored at
  `ResourceViewWidget + 0xA0` and recover its `+0x20` subobject layout;
- avoid semantic renaming until that class/layout identity is established.

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
