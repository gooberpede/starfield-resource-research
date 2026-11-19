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
RVA is VA minus `0x140000000`. The [retail correspondence](v1-research-baseline.md#pinned-retail-correspondence-and-native-differences)
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

[SRR-003](retail-execution-lifecycle.md)
qualifies these retail upstream entries:

| Retail Ghidra entry | Bounded native role |
| --- | --- |
| `FUN_1409518b0`, `FUN_14094e3d0` | **PROVEN STATIC** module-pointer-guarded `StarField::ModuleState` construction and callback setup. A byte gates an early sweep. The common tail contains a later sweep using the same callback. |
| `FUN_140593280`, `FUN_14077c470` | **PROVEN STATIC** type-bucket iterator and resolved PNDT callback. The call at `0x1405932EF` uses slot +`0x10`. The callback's type-gated direct call is at `0x14077C482`. |
| `FUN_140779610` | **PROVEN STATIC** form/context adapter. The direct call to `FUN_140779760` is at `0x1407796D2`. |

[SRR-011](retail-execution-lifecycle.md)
extends the pinned retail graph.

| Retail entry | Bounded native role |
| --- | --- |
| `FUN_141893ee0`, `FUN_141896280`, `FUN_140951c80` | **PROVEN STATIC** initial-loader continuation and signed-mode reset/replay path. Teardown can clear the module guard. `PerformGameReset` is diagnostic-derived terminology. |
| `FUN_141840e60`, `FUN_14183df10`, `FUN_141896020` | **PROVEN STATIC** load-order callback bodies and mode dispatch. Their mode-0x84 path can dispatch reset via state 1. |
| `FUN_14076ec00`, `FUN_140773180`, `FUN_14077bce0`, `FUN_1407766b0`, `FUN_142322520` | **PROVEN STATIC** PNDT definition reader and queued component creation, collector of existing CTPerBiomeData edges, typed edge insertion and separate typed component insertion/replacement. |
| `FUN_142412830`, `FUN_142406B70`, `FUN_14240F5F0` | **PROVEN STATIC** DB +0x38 notification subobject initialization, edge-key notification and indirect callback dispatch. A same-key computed-result transfer to +0x268 remains unresolved. [SRR-015 bounded follow-up](component-database.md) |
| `FUN_140771f30`, `FUN_14076e720`, `FUN_14076e810` | **PROVEN STATIC** keyed component lookup with output assignment on hit, typed copy and typed assignment. The seven generated IDs are copied. |
| `FUN_1407ba9b0`, `FUN_1407bd270`, `FUN_14086a6d0` | **PROVEN STATIC** consumers of the looked-up generated slots on accepted branches. |
| `FUN_140774970`, `FUN_142409490`, `FUN_1424063b0` | **PROVEN STATIC** scoped edge-range removal and broader context index clear. |
| `FUN_14231da10`, `FUN_1424058b0` | **PROVEN STATIC** PerBiomeData type-registry disposal from native `BSGalaxy::ModuleState` teardown. |

[SRR-012](component-database.md) resolves these retail acquisition
and traversal anchors.

| Retail entry | Bounded native role |
| --- | --- |
| `FUN_1423ff640`, `FUN_1424059f0` | **PROVEN STATIC** lazy accessor returning a fixed image object on both arms and initializer for its embedded context. Publication at `0x1418993E3` supplies the context consumed by the allocator at `0x140779676`. |
| `FUN_1405f7a80`, `FUN_1403832a0`, `FUN_1403833e0`, `FUN_1424103e0`, `FUN_1403a4250` | **PROVEN STATIC** planet/type range construction, unsigned two-word lower-bound, leaf exact/predecessor selection and record/block/leaf continuation on the +0x300 index. Ancestor pivots bound routing minima, not all packed records. |
| `FUN_1403835e0`, `FUN_140384200`, `FUN_1403842b0`, `FUN_140384410` | **PROVEN STATIC** leaf split promotes the final left block minimum; internal promotion, truncation and parent insertion preserve routing pivots. Exact instruction locators and scope: [separator contract](component-database.md). |
| `FUN_1405de3b0` | **PROVEN STATIC** FormID lookup sourced from an image-relative locator for the form map. SRR-017 resolved the map and typed per-form identities at its paired title checkpoint; a new epoch still requires fresh resolution. |

[SRR-017 FormID map capacity evidence](component-database.md)
qualifies the allocation and growth path on the same pinned image.

| Retail entry | Bounded native role |
| --- | --- |
| `FUN_1405DD4C0`, `FUN_1405DEA80` | **PROVEN STATIC** atomic first-owner construction gate, initial authoritative map allocation with capacity floor `0x40000` and publication. |
| `FUN_1405E2B30`, `FUN_1405E2C30`, `FUN_1405E3020` | **PROVEN STATIC** insertion through the helper and large-table doubling when the free count is exhausted. |
| `FUN_1405DEDC0` | **PROVEN STATIC** teardown of the authoritative map. |

[SRR-013 structural observation](component-database.md)
qualifies the independent resource type check on the same retail image.

| Retail entry | Bounded native role |
| --- | --- |
| `FUN_1409e7440`, `FUN_1409e9b40`, `FUN_1409e9bc0` | **PROVEN STATIC** `BGSResource` construction, factory type return `0x9F`, and factory call to the constructor. The constructor installs the primary vptr and record type byte. |
| `FUN_1407bc3d0`, `FUN_14079b520` | **PROVEN STATIC** retained-slot staging and consumer path that resolves resource IDs by the native FormID getter and checks type `0x9F`. |

[SRR-014](retail-execution-lifecycle.md)
qualifies the startup and DB execution roles on the same retail image.

| Retail entry | Bounded native role |
| --- | --- |
| `FUN_141898870`, `FUN_141881660`, `FUN_14231D000` | **PROVEN STATIC** startup continuation from publication at `0x1418993E3` to the guarded galaxy module construction and `PerBiomeData` registration at `0x14231D7F1`. |
| `FUN_14008C050`, `FUN_140305FD0` | **PROVEN STATIC** initializer route for boolean `bImportCSVBiomeData:Data`, whose value at `0x145EA6000` gates the early sweep/CSV branch. |
| `FUN_1428D8130`, `FUN_1428D87A0`, `FUN_1428D8FE0` | **PROVEN STATIC** published DB attachment, queue callable installation, and service scheduling with direct and deferred branches. Individual submission completion is separate. |
| `FUN_142404230`, `FUN_142404A80` | **PROVEN STATIC** shared-mode participant entry around the planet adapter and representative copy readers, and distinct ticket admission for inspected insert, removal and clear paths. |
| `FUN_1424069F0`, `FUN_142413190` | **PROVEN STATIC** reverse-key command preparation and guarded application to the +0x358 index. The inspected path carries the key. |
| `FUN_140773910`, `FUN_142346A60`, `FUN_1405DF5C0` | **PROVEN STATIC** PNDT proxy submission and the primary PNDT vtable +0x1A0 flag setter. Their join to the final CSV hook requires a hit on that PNDT proxy. |

[SRR-017](component-database.md) distinguishes the loaded plugin namespace,
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

### Retail survey and Locations locators

| Function | Established retail-static operation |
| --- | --- |
| `FUN_1407B65D0`, `FUN_1407BA290` | Query the body knowledge mask or effective scan level. Named-query call sites at `0x140BF8077` and `0x140BE2CC0`. |
| `FUN_1407B75B0 → FUN_1407B77D0` | Body/ID/delta path to the stored PlayerKnowledge item table. |
| `FUN_1417D6520 → FUN_1417D67D0 / FUN_1417D7540` | Populate caller snapshot, then compute progress. `FUN_1417D8D40` and `FUN_1417D6960` traverse membership. `FUN_1417D7EB0` supplies knowledge-dependent counts. |
| `FUN_1416D0EF0 → FUN_1416D1510` | Gate, assemble and group body resource rows. `FUN_1416B6310 → FUN_1416B6180` transfers them to named UI fields. |
| `FUN_1417D8560`, `FUN_1417D67D0` | Normalize each pointer span, then subtract shared pointers from atmosphere. |
| `FUN_141360090`, `FUN_141369B80 → FUN_14136DC40 → FUN_14135FCC0` | Move Locations detail, enqueue callback, resolve owner and bind selected rows. |
| `FUN_1415A01D0`, `FUN_141597330` | Update and register the scanner’s two scalar wrappers. Locations has its own row-counting consumer. |
| `FUN_141599EC0 → FUN_141597A50 / FUN_14159A0B0` | Rebuild the Monocle wheel. The first helper checks terrestrial discovery through `FUN_1407B7D60` and an absent-slot-ID fallback. The second sets disabled and chooses the destination array. |
| `FUN_141599DE0 → FUN_1415ABD00`, `FUN_14159AE80` | Queue wheel refresh after resource scan. Separately, the picked-resource provider calls the discovery helper and supplies its own target color. |
| `FUN_14159ED90 → FUN_1417D52B0` | Conditional scene-effect path with a discovery-dependent candidate. Later branches can change the submitted index. |
| `FUN_141685AB0 → FUN_1416CF0F0`, `FUN_141698650 → FUN_141685E30` | Construct and queue selected orbital body detail, then bind its resource rows to the body-inspect model through `FUN_1416B6310`. |
| `FUN_14168A8D0`, `FUN_14168AE30` | Build and bind the positional map hover row with independent disabled/show-color values. |
| `FUN_1416ED390 → FUN_1416E87C0` | System-view body-card callback and common binder, paired with its own selected-body provider. |
| `FUN_141411190 → FUN_142337790`, `FUN_141413570 → FUN_142337A50` | Global write/read pair for keyed PlayerKnowledge. Mask bit 3 gates item records. |
| `FUN_140868B30 → FUN_14086A530 → FUN_14086A6D0` | Select from candidate forms built using copied biome slots. |

For predicates, qualified endpoints and offline verification see the
[relationship matrix](component-database.md#resource-membership-player-knowledge-and-the-locations-page).

## Creation Kit generation locators

CK executable scope and static/live identity qualifications are in
[provenance](PROVENANCE.md). Original `FUN_` identifiers below are retained;
behavioral descriptions are aliases, not confirmed engine symbols. The
[generation baseline](v1-research-baseline.md) explains the coherent mechanism,
arithmetic, native branch locators and validation limits.

| Original entry/address | Evidence and bounded role |
| --- | --- |
| `FUN_1415DCFB0` / `0x1415DCFB0` | **PROVEN LIVE** primary per-biome generator in Galaxy View Apply; `BGSPlanetDataManager.cpp` diagnostics. Special → shared insertion → family/shared guards → Common selector or fallback. |
| `FUN_141580660` / `0x141580660` | **PROVEN STATIC**, with prior live category-5/category-0 calls: category-generic selector. Draw `0x1415806A8`; direct-source scan `0x14158070C`, fallback scan `0x14158080C`. |
| `FUN_14157C470` / `0x14157C470` | **PROVEN STATIC** ordered scanner: category test `0x14157C5AA`, chance `0x14157C5BE`, cumulative `0x14157C5CA`, threshold `0x14157C5E3`, returned resource/entry+8 `0x14157C5F7/5FA`. |
| `FUN_144D8C490` / `0x144D8C490` | **PROVEN STATIC** range source used by selector at `0x141580699`; range [0, 0.99999f]. Static export retains generated spelling `FUN_144d8c490`. |
| `FUN_14154C710` / `0x14154C710` | **PROVEN LIVE** fallback candidate construction, no chance weighting. Jaffa VII-b distinguishes no Common roots, preferred matching cached roots and general cached-family pool. |
| `FUN_14015B4A0` / `0x14015B4A0` | **PROVEN LIVE** float32-scaled cached-family index; one-element pool consumes one draw. |
| `FUN_1401190CD` / `0x1401190CD` | **PROVEN** thunk to `FUN_140924800`. |
| `FUN_140924800` / `0x140924800` | **PROVEN STATIC** MT19937-to-binary32 unit primitive; caller range scaling supplies 0.99999f. Distinct from integer shuffle. |
| `FUN_14157F120` / `0x14157F120` | **PROVEN LIVE** descendant helper. Count-eight early return at `0x14157F14D/151/154` → `0x14157F371`, no RNG. |
| `FUN_14152CBC0` / `0x14152CBC0` | **PROVEN STATIC** enclosing orchestrator, sole direct per-biome caller at `0x14152D28F`; **PROVEN LIVE** atmosphere → Everywhere → per-biome allocation ordering. |
| `FUN_141548920` / `0x141548920` | **PROVEN LIVE** Everywhere prepopulation, Fermi VIII-b OceanDefaultRes: no DNAM chance or RNG. Category test `0x141548AC9`, output `0x141548ADA`, shared append `0x141548AE7`. |
| `FUN_1419FE120` / `0x1419FE120` | **PROVEN STATIC** planet-keyed DB lookup, returned type byte +0x88 == 0xAD or fallback. Exact type name unresolved; enclosing atmospheric role independently **PROVEN LIVE**. |
| `FUN_141A46660` / `0x141A46660` | **PROVEN STATIC** eight-byte leaf returning input+0x1D8; single direct accessor call at `0x14152CF28`. Exact field name unresolved. |
| `FUN_14157E850`, `FUN_14158DBE0` | **PROVEN STATIC** thin enclosing wrappers, calls at `0x14157E8E4` and `0x14158DC6E`. Which served prior live UI dispatch is unresolved; second has no direct static caller. |
| `FUN_141560E90`, `FUN_141587240` | CK shuffle helper and real rejection/modulo helper. Trace chain includes `0x1401714A8`, `0x141560F5A`, `0x14001D63D`; baseline retains the full chain. |

## Historical CK preview and container operations

The interpretation of this route as primary biome allocation is
**SUPERSEDED / DEPRIORITISED**. Its static ABI, generic copy and resolver
findings remain valid; no live family/container capture occurred.

`ResourceViewWidget::OnApplySeed` is the named CK/UI entry (address not
recorded), forwarding to `FUN_1431bc320` at `0x1431BC320`. At
`0x1431BC350`, temporary TESContainer vptr dispatch uses slot +0x50/index 10:
vtable `0x1487399C8`, entry `0x148739A18`, thunk `0x1400904FD`, implementation
`FUN_140e0aab0` at `0x140E0AAB0`. These are **PROVEN STATIC** resolved targets,
not a live execution trace. Both listing and high p-code show exactly three
`__fastcall` parameters with analysis-derived signature and no custom storage:

```text
RCX = temporary TESContainer at call-site RSP+0x20 (normalized stack -0xA8)
RDX = *(ResourceViewWidget+0x30)
R8  = *(ResourceViewWidget+0xA0)+0x20
```

R9 is caller-saved residue, not an argument; no stack arguments are stored.
The first 0x20 stack bytes are Windows shadow space. `CALLIND` input zero is
the target and inputs 1..3 are these arguments. R8 has one pointer load followed
by addition, without another dereference. Entry preservation in the callee is
RCX→RBP, RDX→R14, R8→RDI. At `0x140E0AAD7–0x140E0AADD`, it loads the adjusted
source vptr and calls slot +0x30, compares with identity from
`thunk_FUN_140f0e590`, and returns without copying on mismatch.
On equality, `thunk_FUN_140e4bc10(destination,context)` prepares the destination;
source +0x40/+0x48 supply count/array state. It grows/initializes destination
0x18-byte entries and copies through
`thunk_FUN_140e03ee0(destination_entry,context,source_entry)`.
`CopyComponent` is a **STRONG proposed alias**, not an engine symbol.

Class-scoped QTreeWidget::clear compatibility does not prove the concrete
object is Qt's stock QTreeWidget. Its adjusted +0x20 polymorphic component may
arise through secondary inheritance or containment; that remains unresolved.
Representative other component slot-10 functions also have three parameters,
which supports the generic operation shape, not a native method name.
Zero direct callers are expected for vtable-thunk dispatch. Ten bounded +0x50
indirect candidates were collected; only this call has proven receiver/vtable
provenance, so the others are not established callers.

`FUN_140e457b0` at `0x140E457B0` is the generic resolver. Call `0x1431BC375`
via thunk `0x14013A471` receives RCX temporary container, RDX output-slot
address at RSP+0xD0, R8 widget+0x30 context and R9W the low 16 bits of
QSpinBox::value from widget+0x98. `MOVZX R9D,AX` at `0x1431BC360` is the
only caller transform. A separate allocated TESContainer is stored through
RDX; post-return `0x1431BC37A` uses that output slot. Ordinary entries copy;
TESBoundObject→TESLevItem dynamic-cast successes resolve via
`FUN_140dddba0` using object+0x340, selector and quantity. The output is later
consumed by `FUN_140f5fac0`. The temporary input is not the post-resolution
container. No live IRES leaves, family topology or selector value were measured;
empty exported templates are not evidence of empty runtime containers.
The former RSCS-as-effective-level allocator theory is superseded by direct
nonzero unsigned RSCS→MT19937 proof.

Repeatable read-only static methods are
`ExportCallSignatureEvidence.java`, `ExportResourceResolutionEvidence.java`
and `ExportFunctionNeighbourhood.java`; see [Ghidra tooling](../ghidra/README.md).
The historical exports used `-readOnly -noanalysis` on an unlocked scratch
copy, no transactions or program changes. The respective output schemas are
call-signatures and resource-resolution; generated runs are reproducible
exports, not custody-backed live observations.

`LL_ResourceSurfaceFlora_*` lists were investigated and deprioritised:
observed resource-availability conditions and rarity weighting support a
surface-placement role, without establishing primary biome allocation.

## SurveyAggregator

RE ID **1016657**, historical runtime binding
`void (*)(void* buffer, std::uint32_t planet_id)`, fills a fixed-size aggregation
buffer whose populated spans are filtered for resource forms. It supplied the
historical planet-all-resources.csv validation snapshot, now maintained only
in the sibling reproducer. Observed planet membership has high confidence;
the historical build and upstream filter remain unresolved.
For **this retail pin**, Address Library v22's matching versionlib (format 5,
data format 0, SHA-256 `299ea1b4da35b42e9bf1b8ed94fa980694a4dcbebfc7693201619c4c08fa49d8`)
maps this ID to RVA `0x17D6520` (little-endian u32 at file offset
`96 + 4 × 1016657`). The [pinned native graph](component-database.md#resource-membership-player-knowledge-and-the-locations-page)
explains two separate membership spans and the knowledge-dependent summary.
Attribution of the historical CSV to a particular span/filter and build is
still open. Historical extraction exposes no biome identity and demonstrably omits some atmospheric
resources. It is an empirical CK/RSGD-visible-channel proxy, never generation
logic or a complete final membership oracle. See
[baseline](v1-research-baseline.md#surveyaggregator-and-qualified-oracle) and
[the current lead register](hypotheses.md).
