# Function Register

See the [native structure register](structure-register.md) for selected fields
and relationships used by the retail functions below.

This register tracks native functions relevant to Starfield resource generation.

See the [applicability register](PROVENANCE.md#applicability-register) for
build qualifications on CK native evidence and historical retail output checks.

Names beginning with `FUN_` are Ghidra-generated identifiers unless otherwise stated.

Do not replace an original Ghidra name with a semantic alias unless evidence is strong. Proposed aliases should be recorded separately.

## Retail Starfield.exe 1.16.244.0

These preferred VAs apply to the [pinned retail image](PROVENANCE.md#current-retail-identity).
RVA is VA minus `0x140000000`. The [SRR-002 mapping](SRR-002-retail-static-reconnaissance.md#retail-mapping-on-the-pinned-image)
records instruction anchors, differences and supporting helpers.

| Retail Ghidra entry | CK VA or region | Bounded correspondence |
| --- | --- | --- |
| `FUN_140779760` | `0x14152CBC0`, with `0x141548920` role inlined | **STATICALLY ESTABLISHED / PROVEN** prepopulation and shuffled biome loop. |
| `FUN_140777870` | `0x1415DCFB0` | **STATICALLY ESTABLISHED / PROVEN** per-biome allocation and guard dispatch. |
| `FUN_140777e30`, `FUN_140777ff0` | `0x141580660`, `0x14157C470` | **STATICALLY ESTABLISHED / PROVEN** category-generic selector and entry scan. |
| `FUN_1407780b0`, `FUN_1407784d0` | `0x14157F120` region | **STRONG CORRESPONDENCE / STRONG** descendant generation. Candidate multiplicity remains open. |
| `FUN_14077c0e0`, `FUN_1402fcee0` | `0x14154C710`, `0x14015B4A0` | **STATICALLY ESTABLISHED / PROVEN** guarded fallback construction and float-scaled selection. |
| `FUN_1402fbc20` | `0x140924800` | **STATICALLY ESTABLISHED / PROVEN** MT-to-binary32 primitive. |
| `FUN_14077c6e0`, `FUN_14077c4d0` | Shuffle call at `0x14152CEBD` | **STRONG CORRESPONDENCE / STRONG** integer shuffle helpers. |

[SRR-003](SRR-003-retail-allocator-invocation-and-dispatch.md#native-path-and-predicates)
qualifies these retail upstream entries:

| Retail Ghidra entry | Bounded native role |
| --- | --- |
| `FUN_1409518b0`, `FUN_14094e3d0` | **PROVEN STATIC** module-pointer-guarded `StarField::ModuleState` construction and callback setup. A byte gates an early sweep. The common tail contains a later sweep using the same callback. |
| `FUN_140593280`, `FUN_14077c470` | **PROVEN STATIC** type-bucket iterator and resolved PNDT callback. The call at `0x1405932EF` uses slot +`0x10`. The callback's type-gated direct call is at `0x14077C482`. |
| `FUN_140779610` | **PROVEN STATIC** form/context adapter. The direct call to `FUN_140779760` is at `0x1407796D2`. |

[SRR-011](SRR-011-planetary-allocation-execution-and-result-lifecycle.md)
extends the pinned retail graph.

| Retail entry | Bounded native role |
| --- | --- |
| `FUN_141893ee0`, `FUN_141896280`, `FUN_140951c80` | **PROVEN STATIC** initial-loader continuation and signed-mode reset/replay path. Teardown can clear the module guard. `PerformGameReset` is diagnostic-derived terminology. |
| `FUN_141840e60`, `FUN_14183df10`, `FUN_141896020` | **PROVEN STATIC** load-order callback bodies and mode dispatch. Their mode-0x84 path can dispatch reset via state 1. |
| `FUN_14076ec00`, `FUN_140773180`, `FUN_14077bce0`, `FUN_1407766b0`, `FUN_142322520` | **PROVEN STATIC** PNDT definition reader and queued component creation, collector of existing CTPerBiomeData edges, typed edge insertion and separate typed component insertion/replacement. |
| `FUN_142412830`, `FUN_142406B70`, `FUN_14240F5F0` | **PROVEN STATIC** DB +0x38 notification subobject initialization, edge-key notification and indirect callback dispatch. A same-key computed-result transfer to +0x268 remains unresolved. [SRR-015 bounded follow-up](SRR-015-lead-register.md#b8-bounded-follow-up) |
| `FUN_140771f30`, `FUN_14076e720`, `FUN_14076e810` | **PROVEN STATIC** keyed component lookup with output assignment on hit, typed copy and typed assignment. The seven generated IDs are copied. |
| `FUN_1407ba9b0`, `FUN_1407bd270`, `FUN_14086a6d0` | **PROVEN STATIC** consumers of the looked-up generated slots on accepted branches. |
| `FUN_140774970`, `FUN_142409490`, `FUN_1424063b0` | **PROVEN STATIC** scoped edge-range removal and broader context index clear. |
| `FUN_14231da10`, `FUN_1424058b0` | **PROVEN STATIC** PerBiomeData type-registry disposal from native `BSGalaxy::ModuleState` teardown. |

[SRR-012](SRR-012-acquisition-evidence.md) resolves these retail acquisition
and traversal anchors.

| Retail entry | Bounded native role |
| --- | --- |
| `FUN_1423ff640`, `FUN_1424059f0` | **PROVEN STATIC** lazy accessor returning a fixed image object on both arms and initializer for its embedded context. Publication at `0x1418993E3` supplies the context consumed by the allocator at `0x140779676`. |
| `FUN_1405f7a80`, `FUN_1403832a0`, `FUN_1403833e0`, `FUN_1424103e0`, `FUN_1403a4250` | **PROVEN STATIC** planet/type range construction, unsigned two-word lower-bound, leaf exact/predecessor selection and record/block/leaf continuation on the +0x300 index. Ancestor pivots bound routing minima, not all packed records. |
| `FUN_1403835e0`, `FUN_140384200`, `FUN_1403842b0`, `FUN_140384410` | **PROVEN STATIC** leaf split promotes the final left block minimum; internal promotion, truncation and parent insertion preserve routing pivots. Exact instruction locators and scope: [separator contract](SRR-012-acquisition-evidence.md#separator-meaning-and-packed-records). |
| `FUN_1405de3b0` | **PROVEN STATIC** FormID lookup sourced from an image-relative locator for the form map. The map contents and per-form addresses require fresh resolution in a later observation. |

[SRR-017 FormID map capacity evidence](SRR-017-title-admission.md)
qualifies the allocation and growth path on the same pinned image.

| Retail entry | Bounded native role |
| --- | --- |
| `FUN_1405DD4C0`, `FUN_1405DEA80` | **PROVEN STATIC** atomic first-owner construction gate, initial authoritative map allocation with capacity floor `0x40000` and publication. |
| `FUN_1405E2B30`, `FUN_1405E2C30`, `FUN_1405E3020` | **PROVEN STATIC** insertion through the helper and large-table doubling when the free count is exhausted. |
| `FUN_1405DEDC0` | **PROVEN STATIC** teardown of the authoritative map. |

[SRR-013 structural observation](SRR-013-structural-state-observation.md#native-resource-identity)
qualifies the independent resource type check on the same retail image.

| Retail entry | Bounded native role |
| --- | --- |
| `FUN_1409e7440`, `FUN_1409e9b40`, `FUN_1409e9bc0` | **PROVEN STATIC** `BGSResource` construction, factory type return `0x9F`, and factory call to the constructor. The constructor installs the primary vptr and record type byte. |
| `FUN_1407bc3d0`, `FUN_14079b520` | **PROVEN STATIC** retained-slot staging and consumer path that resolves resource IDs by the native FormID getter and checks type `0x9F`. |

[SRR-014](SRR-014-startup-allocation-component-database-lifecycle.md)
qualifies the startup and DB execution roles on the same retail image.

| Retail entry | Bounded native role |
| --- | --- |
| `FUN_141898870`, `FUN_141881660`, `FUN_14231D000` | **PROVEN STATIC** startup continuation from publication at `0x1418993E3` to the guarded galaxy module construction and `PerBiomeData` registration at `0x14231D7F1`. |
| `FUN_14008C050`, `FUN_140305FD0` | **PROVEN STATIC** initializer route for boolean `bImportCSVBiomeData:Data`, whose value at `0x145EA6000` gates the early sweep/CSV branch. |
| `FUN_1428D8130`, `FUN_1428D87A0`, `FUN_1428D8FE0` | **PROVEN STATIC** published DB attachment, queue callable installation, and service scheduling with direct and deferred branches. Individual submission completion is separate. |
| `FUN_142404230`, `FUN_142404A80` | **PROVEN STATIC** shared-mode participant entry around the planet adapter and representative copy readers, and distinct ticket admission for inspected insert, removal and clear paths. |
| `FUN_1424069F0`, `FUN_142413190` | **PROVEN STATIC** reverse-key command preparation and guarded application to the +0x358 index. The inspected path carries the key. |
| `FUN_140773910`, `FUN_142346A60`, `FUN_1405DF5C0` | **PROVEN STATIC** PNDT proxy submission and the primary PNDT vtable +0x1A0 flag setter. Their join to the final CSV hook requires a hit on that PNDT proxy. |

[SRR-017](SRR-017-source-identity.md) distinguishes the loaded plugin namespace,
typed FormID lookup and per-form source history in the pinned retail image.

| Retail entry | Bounded native role |
| --- | --- |
| `FUN_140598430`, `FUN_14200A5A0`, `FUN_1405B78C0` | **PROVEN STATIC** name-registry lookup, registered GetFormFromFile wrapper and full/medium/small local-ID formatting. The wrapper calls the separate native FormID map. |
| `FUN_1405994A0`, `FUN_14059FCF0` | **PROVEN STATIC** guarded initial namespace assignment, including a deferred-file branch, and three compiled slot assignments. |
| `FUN_14058E350` | **PROVEN STATIC** diagnostic lookup of source-file vectors for found FormIDs and full/small/medium compiled slots on its missed-form branch. |
| `FUN_1405E0D50`, `FUN_1405E3980`, `FUN_1405DC730` | **PROVEN STATIC** guarded source-vector update, index interning and ordered append of a previously unlisted source. The caller can filter prior contributors before appending. |
| `FUN_1405972B0`, `FUN_140597A70`, `FUN_1405B9750` | **PROVEN STATIC** initial scan and packed-source construction. One startup branch supplies the relative `DATA\\` directory to the packed-file constructor. |
| `FUN_1405B5BE0`, `FUN_1405B9950`, `FUN_1428E4230` | **PROVEN STATIC** packed-file open wrapper, pathname composition and distinct direct or virtual provider route, followed by the typed file constructor. |
| `FUN_1427D8950`, `FUN_1427D7FA0`, `FUN_1405BA840` | **PROVEN STATIC** relative-path virtual provider delegation, ordered provider search stopping on success, and packed-file close that clears the open stream pointer. |

The CK entries below retain their original build and evidence scope.

---

## FUN_1415DCFB0

**Name:** `FUN_1415DCFB0`

**Address:** `0x1415DCFB0`

**Proposed alias:** none

**Source context:** Creation Kit executable, live Galaxy View Apply path; executable diagnostics identify `BGSPlanetDataManager.cpp`

**Status:** **PROVEN primary per-biome generator in the live-traced CK generation path**

**Confidence:** high

### Observed behaviour

Live x64dbg traces tie this function to the Creation Kit Galaxy View Apply generation path. It handles Special category `5`, Common/root category `0`, family-cache interaction, descendant dispatch, Common guards, and guarded fallback assignment. The reconstructed behaviour agrees with CK and retail outputs; this entry does not claim that the address was independently traced in retail `Starfield.exe`.

It preserves stored `RSGDResourceIndex` order for category selection and uses unnormalized cumulative `Chance / 100`. Once a new Common family is selected, it unconditionally emits the root and dispatches descendant generation through rarity levels `1..4`.

**PROVEN LIVE ordering:**

```text
Special selector
→ Special written/recorded into shared state
→ five-tree guard
→ shared-eight guard
→ normal Common selector OR fallback near 0x1415DD255
```

A new Special can fill slot eight and force fallback for the current biome. A duplicate Special does not increment the validated unique-identity occupancy model.

### Proven limit checks

```text
0x1415DD0A3  cmp dword ptr [r12], 8
0x1415DD0A8  jae ...
0x1415DD0D3  cmp dword ptr [rsi], 5
0x1415DD0D6  jae ...
0x1415DD0DC  cmp dword ptr [r12], 8
0x1415DD0E1  jae ...
```

The `8` comparisons establish the shared resource-state guard. Bara VII-d live progression `0, 1, 1, 2, 2, 3, 4, 5` proves that the `5` guard applies to five distinct generated/cached Common-family configurations in this generation path; normal cache reuse does not increment it.

Both Common guards suppress the normal category-0 selector and branch to fallback near `0x1415DD255`. The earlier interpretation that the shared-eight branch necessarily leaves the biome without a Common family is **SUPERSEDED**.

### Common assignment paths

```text
normal selector → new root:
    generate and cache family

normal selector → cached root:
    ordinary cache reuse; no descendant RNG

five-tree/shared-eight guard:
    FUN_14154C710 candidate construction
    → FUN_14015B4A0 cached-family choice when a pool exists
    → copy existing configuration; no descendant regeneration
```

Current assignment provenance is `NEW_FAMILY`, `NORMAL_CACHE_REUSE`, `GUARD_MATCHED_FALLBACK`, `GUARD_GENERAL_FALLBACK`, or `NO_COMMON_ASSIGNMENT`.

### Current posture

No settled generation hole remains within v1.0 scope. Revisit this function for new falsifications, version drift, or evidence that contradicts the recovered control flow.

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

## FUN_14154C710

**Name:** `FUN_14154C710`

**Address:** `0x14154C710`

**Proposed alias:** none

**Source context:** Creation Kit guard-fallback path

**Status:** **PROVEN LIVE fallback candidate-construction helper**

**Confidence:** high

### Observed behaviour

The helper scans the current effective RSGD in stored order. It considers only category-0/Common resources, records whether any Common entries exist, and compares each Common root FormID with roots in the already-generated family cache. Matching cached configurations form a preferred pool. It applies no chance weighting.

### Decision context

```text
no Common roots
    → NO_COMMON_ASSIGNMENT
matching cached roots
    → preferred matching pool
Common roots but no matches
    → all cached families
```

Jaffa VII-b provides the decisive live decision-rule observations. Selection from the resulting pool is performed separately by `FUN_14015B4A0`.

---

## FUN_14015B4A0

**Name:** `FUN_14015B4A0`

**Address:** `0x14015B4A0`

**Proposed alias:** none

**Source context:** Creation Kit guard-fallback path

**Status:** **PROVEN LIVE float-scaled fallback family selector**

**Confidence:** high

### Observed behaviour

For lower bound zero and candidate count `N`, selection is:

```python
index = trunc(float32(probability * float32(N)))
```

It obtains `probability` through `FUN_1401190CD → FUN_140924800`. A one-element pool still consumes one probability draw. This semantic mechanism is distinct from the biome-shuffle integer rejection/modulo helper even though it shares arithmetic with descendant candidate indexing.

---

## FUN_1401190CD

**Name:** `FUN_1401190CD`

**Address:** `0x1401190CD`

**Proposed alias:** none

**Source context:** Creation Kit

**Status:** **PROVEN thunk to FUN_140924800**

**Confidence:** high

### Observed behaviour

The thunk jumps to `FUN_140924800` and supplies the recovered MT19937-to-binary32 probability primitive to guard-fallback selection.

---

## FUN_140924800

**Name:** `FUN_140924800`

**Address:** `0x140924800`

**Proposed alias:** none

**Source context:** Creation Kit PRNG machinery

**Status:** **PROVEN MT19937 binary32 probability conversion**

**Confidence:** high

### Observed behaviour

```text
raw uint32
→ float32(raw)
→ × float32(2**-32)
→ × float32(0.99999)
→ binary32 probability
```

Proven callers include the Special/Common selector path through its thunk and the guard-fallback selector through `FUN_1401190CD`. Descendant and fallback bounded choices use the resulting probability in separate semantic contexts; this function is not the biome-shuffle integer helper.

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

**Status:** **PROVEN STATIC enclosing orchestration; PROVEN LIVE atmosphere-before-Everywhere-before-biomes semantics**

**Confidence:** high

### Observed behaviour

This is the sole direct caller of `FUN_1415DCFB0`, at `0x14152D28F`. It builds
and shuffles the biome work-object array, initializes a shared uint32 resource
FormID array, populates that array from a planet-keyed `+0x1D8` list and from
category-6 Everywhere entries, then calls `FUN_1415DCFB0` once per shuffled
biome without resetting the shared array.

Maal VIII live tracing proves that the first source carries effective atmospheric Chlorine `000057D5` into shared state before Everywhere and the first per-biome call. This upgrades the enclosing atmospheric prepopulation order from strong static interpretation to proven live semantics while preserving the static evidence boundary on unnamed engine types/fields.

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

**Status:** **PROVEN LIVE category-6 / Everywhere prepopulation helper**

**Confidence:** high

### Observed behaviour

The helper walks effective generation entries and their `0x238`-byte nested
records in stored order. It tests the resolved record's category byte at
`+0x2F8` against `6` at `0x141548AC9`. On a match it copies form `+0x70`
to the current biome work object's `+0x68` field and appends the same uint32
FormID to the shared resource array at `0x141548AE7`.

It is called only by `FUN_14152CBC0`, before that function starts the repeated
calls to `FUN_1415DCFB0`.

Fermi VIII-b `OceanDefaultRes` proves live that this path does not consult DNAM Everywhere chance, consumes no RNG, and is not ordinary weighted selection.

---

## FUN_1419FE120

**Name:** `FUN_1419FE120`

**Address:** `0x1419FE120`

**Proposed alias:** none

**Source context:** Creation Kit component-database lookup

**Status:** **PROVEN STATIC planet-keyed typed-form lookup in the PROVEN LIVE atmospheric prepopulation path**

**Confidence:** high for mechanics and enclosing atmospheric role; medium for exact type identity

### Observed behaviour

Given a manager-like object and a uint32 planet key, this helper performs a
component-database lookup and returns either a resolved form whose type byte at
`+0x88` equals `0xAD`, or a fallback object. `FUN_14152CBC0` immediately passes
the result to `FUN_141A46660` and treats the returned field as the source of
pre-biome resource forms.

The current database does not name type `0xAD` as ATMO, so no semantic C++
type name is assigned. Separately, Maal VIII live tracing proves the enclosing
path's effective atmospheric-resource role and concrete Chlorine identity.

---

## FUN_141A46660

**Name:** `FUN_141A46660`

**Address:** `0x141A46660`

**Proposed alias:** none

**Source context:** Creation Kit typed-form field accessor

**Status:** **PROVEN STATIC `+0x1D8` accessor in the PROVEN LIVE atmospheric prepopulation path**

**Confidence:** high for offset/access and enclosing atmospheric role; medium for exact field identity

### Observed behaviour

This eight-byte leaf function returns `param_1 + 0x1D8`. Its thunk has exactly
one direct caller in the current database: `FUN_14152CBC0` at `0x14152CF28`.
That caller interprets the field as a dynamic array of dependency-managed form
pointers, resolves each entry, obtains its uint32 FormID from `form +0x70`,
deduplicates it, and appends it to the shared pre-biome resource array.

The exact C++ field name remains unknown and must not be invented. The enclosing
path's atmospheric-resource semantics are independently **PROVEN LIVE**.

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

Used to create the historical `planet-all-resources.csv` snapshot, whose provenance remains valuable for independent resource-set validation. The snapshot is no longer distributed from this research repository. It appears to correspond closely to the CK/biome-generation-visible channel, but that is not a proven engine contract.

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
