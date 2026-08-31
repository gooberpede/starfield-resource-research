# Function Register

This register tracks native functions relevant to Starfield resource generation.

Names beginning with `FUN_` are Ghidra-generated identifiers unless otherwise stated.

Do not replace an original Ghidra name with a semantic alias unless evidence is strong. Proposed aliases should be recorded separately.

---

## FUN_1415DCFB0

**Name:** `FUN_1415DCFB0`

**Address:** `0x1415DCFB0`

**Proposed alias:** none

**Source context:** Creation Kit executable, live Galaxy View Apply path; executable diagnostics identify `BGSPlanetDataManager.cpp`

**Status:** **PROVEN primary per-biome generator in the live-traced CK generation path**

**Confidence:** high

### Observed behaviour

Live x64dbg traces tie this function to the Creation Kit Galaxy View Apply generation path. It handles at least Special category `5`, Common/root category `0`, family-cache interaction, descendant dispatch, and resource-count/family-count guards. The reconstructed behaviour agrees with known game/resource results; this entry does not claim that the address was independently traced in retail `Starfield.exe`.

It preserves stored `RSGDResourceIndex` order for category selection and uses unnormalized cumulative `Chance / 100`. Once a new Common family is selected, it unconditionally emits the root and dispatches descendant generation through rarity levels `1..4`.

### Proven limit checks

```text
0x1415DD0A3  cmp dword ptr [r12], 8
0x1415DD0A8  jae ...
0x1415DD0D3  cmp dword ptr [rsi], 5
0x1415DD0D6  jae ...
0x1415DD0DC  cmp dword ptr [r12], 8
0x1415DD0E1  jae ...
```

The `8` comparisons establish an eight-entry internal resource-container limit. The `5` comparison proves a `count >= 5` guard on the structure associated with generated/cached Common-family configurations. Its likely interpretation as a general five-family or five-generated-family-configuration limit remains **PROVISIONAL** because the structure's exact general role has not been independently established.

### Next analysis

Do not resume broad exploration from the older leveled-list trail. Identify this function's immediate outer caller/enclosing planet loop and inspect pre-population of the shared resource container before the first per-biome call, especially for Maal VIII atmospheric Chlorine.

---

## FUN_141580660

**Name:** `FUN_141580660`

**Address:** `0x141580660`

**Proposed alias:** none

**Source context:** Creation Kit executable, live Galaxy View Apply path

**Status:** **PROVEN category-generic Special/Common selector in the live-traced CK generation path**

**Confidence:** high

### Observed behaviour

`FUN_1415DCFB0` calls this function at `0x1415DD09E` with category `5`
(Special) and at `0x1415DD0F2` with category `0` (Common). It consumes one
MT19937 word before candidate enumeration, converts it through the binary32
`uint32 -> [0, 0.99999]` probability path, and delegates ordered entry scanning
to `FUN_14157C470`.

The helper filters on resource/IRES byte `+0x2F8`, reads the category-indexed
chance at RSGD entry `+0x24 + category*0x28`, accumulates `chance * 0.01f`
without normalization, and selects the first entry for which
`roll < cumulative`. The returned 16-byte pair is `{resource pointer,
entry+8}`. The selector uses the same code, RNG consumption, probability rule,
and return shape for categories `5` and `0`; it contains no Special-only or
Common-only branch.

The up-front draw occurs even with no qualifying entry, one qualifying entry,
or a single `100%` entry. Full static evidence is preserved in
`docs/experiments/special-common-selector-investigation.md`.

### Key addresses

```text
0x1415806A8  MT19937 binary32 draw via thunk to FUN_140924800
0x14158070C  scan optional direct generation-data source
0x14158080C  scan one fallback generation-data source
0x14157C5AA  compare resource/IRES +0x2F8 with requested category
0x14157C5BE  read entry +0x24 + category*0x28 chance
0x14157C5CA  update cumulative threshold
0x14157C5E3  branch when roll < cumulative
0x14157C5F7  store selected resource pointer
0x14157C5FA  store selected entry +0x08
```

### Open detail

The current Ghidra database does not name the exact C++ types of the selector
context's optional direct source and the source object containing the fallback
dependency array at `+0x728`. Their observed dataflow is established; semantic
type names should not be invented.

---

## FUN_14157F120

**Name:** `FUN_14157F120`

**Address:** `0x14157F120`

**Proposed alias:** none

**Source context:** Creation Kit executable, live Galaxy View Apply path

**Status:** **PROVEN descendant helper in the live-traced CK generation path**

**Confidence:** high

### Observed behaviour

For requested rarities `1..4`, it builds the stable-deduplicated candidate set from `children(root)` followed by `children(current_structural_node)`, rarity-filters it, draws inclusion and selection, emits on successful inclusion, and continues structurally through the chosen candidate even when omitted.

This behaviour was observed executing in the Creation Kit Galaxy View Apply path and agrees with reconstructed game/resource results. The address is not asserted here to have been independently traced in retail `Starfield.exe`.

With zero candidates it consumes exactly one MT word, emits nothing, and leaves the structural node unchanged.

### Proven resource-limit return

```text
0x14157F14D  mov rax,[rcx+20h]
0x14157F151  cmp dword ptr [rax],8
0x14157F154  jae 14157F371
```

If the internal resource count is at least `8`, the helper returns the current structural node without consuming RNG.

---

## FUN_14152CBC0

**Name:** `FUN_14152CBC0`

**Address:** `0x14152CBC0`

**Proposed alias:** none

**Source context:** Creation Kit, `BGSPlanetDataManager.cpp` diagnostics

**Status:** **PROVEN STATIC enclosing biome-generation orchestration function**

**Confidence:** high

### Observed behaviour

This is the sole direct caller of `FUN_1415DCFB0`, at `0x14152D28F`. It builds
and shuffles the biome work-object array, initializes a shared uint32 resource
FormID array, populates that array from a planet-keyed `+0x1D8` list and from
category-6 Everywhere entries, then calls `FUN_1415DCFB0` once per shuffled
biome without resetting the shared array.

At the generator call, `R9` is the shared resource-ID array and `R8` is the
separate generated/cached Common-family configuration array.

### Known relationships

```text
FUN_14157E850 / FUN_14158DBE0
    ↓
FUN_14152CBC0
    ├─ FUN_1419FE120 → FUN_141A46660 → shared FormID array
    ├─ FUN_141548920 → category-6 ID → shared FormID array
    └─ FUN_1415DCFB0 (repeated biome loop)
```

### Important addresses

```text
0x14152CEBD  shuffle helper call
0x14152CF17  planet-keyed typed-form lookup
0x14152CF28  +0x1D8 array accessor
0x14152D0E9  direct-list FormID store
0x14152D1B5  category-6 helper call
0x14152D28F  per-biome generator call
```

### Open question

Static xrefs do not identify which of the two thin immediate wrappers is the
previously observed Galaxy View Apply dispatch. `FUN_14158DBE0` has no direct
static callers and may be invoked indirectly.

---

## FUN_141548920

**Name:** `FUN_141548920`

**Address:** `0x141548920`

**Proposed alias:** none

**Source context:** Creation Kit pre-biome setup

**Status:** **PROVEN STATIC category-6 / Everywhere prepopulation helper**

**Confidence:** high

### Observed behaviour

The helper walks dependency-managed entries and their `0x238`-byte nested
records. It tests the resolved record's category byte at `+0x2F8` against `6`
at `0x141548AC9`. On the first match it copies form `+0x70` to the current
biome work object's `+0x68` field and appends the same uint32 FormID to the
shared resource array at `0x141548AE7`.

It is called only by `FUN_14152CBC0`, before that function starts the repeated
calls to `FUN_1415DCFB0`.

---

## FUN_1419FE120

**Name:** `FUN_1419FE120`

**Address:** `0x1419FE120`

**Proposed alias:** none

**Source context:** Creation Kit component-database lookup

**Status:** **PROVEN STATIC planet-keyed typed-form lookup; atmospheric role STRONG**

**Confidence:** high for mechanics; medium-high for ATMO interpretation

### Observed behaviour

Given a manager-like object and a uint32 planet key, this helper performs a
component-database lookup and returns either a resolved form whose type byte at
`+0x88` equals `0xAD`, or a fallback object. `FUN_14152CBC0` immediately passes
the result to `FUN_141A46660` and treats the returned field as the source of
pre-biome resource forms.

The current database does not name type `0xAD` as ATMO. The ATMO
interpretation is supported by the enclosing dataflow and explicit
“Atmosphere and Everywhere resources” diagnostic, but remains **STRONG** until
confirmed by live form identity.

---

## FUN_141A46660

**Name:** `FUN_141A46660`

**Address:** `0x141A46660`

**Proposed alias:** none

**Source context:** Creation Kit typed-form field accessor

**Status:** **PROVEN STATIC `+0x1D8` accessor; field semantics STRONG**

**Confidence:** high for offset/access; medium-high for atmospheric-resource-list interpretation

### Observed behaviour

This eight-byte leaf function returns `param_1 + 0x1D8`. Its thunk has exactly
one direct caller in the current database: `FUN_14152CBC0` at `0x14152CF28`.
That caller interprets the field as a dynamic array of dependency-managed form
pointers, resolves each entry, obtains its uint32 FormID from `form +0x70`,
deduplicates it, and appends it to the shared pre-biome resource array.

The exact field name and its ATMO semantic identity remain **STRONG**, not
PROVEN.

---

## ResourceViewWidget::OnApplySeed

**Name:** `ResourceViewWidget::OnApplySeed`  
**Address:** to be recorded from the current Ghidra project  
**Source context:** Creation Kit  
**Status:** **SUPERSEDED / DEPRIORITISED AS PRIMARY ALLOCATION PATH**; retained named CK/UI anchor

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

This remains a useful named CK/UI entry point, but it is not the current primary allocation anchor.

### Open questions

- What object owns the seed/resource-preview state?
- Which arguments carry PNDT, BIOM, RSGD, or RSCS-derived data?
- Does this path call shared game-runtime allocation logic or CK-specific preview logic?
- What state is populated before and after this function returns?

### Next analysis

No current analysis is planned on this path unless new live evidence connects it to `FUN_1415DCFB0` or the surrounding planet-generation loop. The earlier export objectives are preserved in the historical implementation briefs and experiment notes.

---

## FUN_1431bc320

**Name:** `FUN_1431bc320`  
**Address:** `0x1431BC320`  
**Proposed role:** resource seed / preview processing intermediary  
**Status:** **SUPERSEDED / DEPRIORITISED AS PRIMARY ALLOCATION PATH**; historical static-analysis target

**Confidence:** high in the recorded ABI/dataflow; low on its relation to biome allocation

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

This function lies downstream of the CK Apply Seed UI action and upstream of lower-level selection machinery. Live Galaxy View Apply tracing did not establish it as the primary biome allocator; it may remain legitimate CK/UI or downstream machinery.

### Why it matters

It is preserved because its low-level calling-convention and container findings are valid research history, not because it is the preferred current target.

### Questions to answer

- What arguments enter the function?
- Which arguments originate from the ResourceViewWidget or planet/resource configuration?
- Which fields/offsets are read from each object?
- Are BIOM or RSGD pointers referenced directly or indirectly?
- Is an RSCS-derived value created, transformed, or passed onward here?
- Which callees are resource-specific versus generic utility code?
- What values are passed to `FUN_140e457b0`?

### Next analysis

Revisit only if new live evidence connects it to the proven runtime generation path.

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
**Status:** **SUPERSEDED / DEPRIORITISED AS PRIMARY ALLOCATION PATH**; known generic-selection anchor

**Confidence:** medium

### Current interpretation

Prior Ghidra work traced this function into generic leveled-list evaluation machinery. The earlier interpretation of an RSCS-derived value as effective-level-like rather than a direct PRNG seed is **SUPERSEDED** by live proof of direct unsigned 32-bit RSCS seeding of MT19937.

### Known relationship

```text
FUN_1431bc320
    ↓
FUN_140e457b0
    ↓
generic leveled-list evaluator
```

The direct call in `FUN_1431bc320` is at `0x1431BC375` and targets the thunk at
`0x14013A471`, which resolves to `FUN_140e457b0`. Its Windows x64 arguments are:

```text
RCX = &temporary TESContainer at call-site RSP+0x20
RDX = &resolved-container output slot at call-site RSP+0xD0
R8  = *(ResourceViewWidget + 0x30)
R9W = low 16 bits of QSpinBox::value(*(ResourceViewWidget + 0x98))
```

`MOVZX R9D,AX` at `0x1431BC360` performs the narrowing; this caller applies no
further arithmetic transform. The resolver allocates a separate
`TESContainer`, stores it through RDX, copies ordinary entries, and resolves
`TESLevItem` entries through `FUN_140dddba0`. Immediately after return at
`0x1431BC37A`, RAX points to the output slot. Thus the temporary input is not
the post-resolution container.

The input layout used mechanically by the copy/resolver path is:

```text
container +0x40 : 32-bit entry count
container +0x44 : 32-bit capacity
container +0x48 : entry-array pointer
entry size      : 0x18
entry +0x00     : signed quantity/count
entry +0x08     : TESBoundObject/form pointer
entry +0x10     : metadata pointer
```

The resolver dynamically casts the form pointer from `TESBoundObject` to
`TESLevItem`; on success it passes `object+0x340` to `FUN_140dddba0`. These
facts do not establish any live form identity or resource-family topology.

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

No further work is currently planned on this path unless new live evidence connects it to biome allocation.

---

## SurveyAggregator

**Name:** `SurveyAggregator`  
**RE ID:** `1016657`  
**Runtime binding type:**

```cpp
using fn_aggregator_t = void (*)(void* buffer, std::uint32_t planet_id);
```

**Source context:** Starfield runtime  
**Status:** empirical resource-set observer/proxy; exact semantic contract unresolved

**Confidence:** high for observed output; low that it is allocation logic

### Current interpretation

Fills a fixed-size aggregation buffer for a planet.

Existing runtime tooling iterates populated spans and filters resource forms. Current atmospheric evidence proves that at least some atmosphere-derived inorganic resources are absent from its derived dataset.

### Established use

Used to create `data/planet-all-resources.csv`, whose provenance remains valuable for independent resource-set validation. The dataset appears to correspond closely to the CK/biome-generation-visible channel, but that is not a proven engine contract.

### Why it matters

It provides a large-scale empirical oracle/proxy useful for reconciling the CK/biome-generation-visible channel. Its exact semantics remain unresolved, and it must be reconciled separately from atmospheric extraction.

### Limitation

Current use exposes planet-wide membership without biome identity and omits at least some atmospheric resources. It must not be treated as a complete final inorganic oracle.

### Questions to answer

- Is resource allocation already complete before this function runs?
- What structures does it read?
- Is per-biome state available upstream?
- Can a related function expose final resource membership by biome?
- Is there a useful data structure connecting survey/resource state to BIOM records?

### Suggested priority

Secondary to the proven live-traced CK `FUN_1415DCFB0` / `FUN_14157F120` path.

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
