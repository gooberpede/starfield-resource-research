# Glossary

- [Allocation and provenance](#allocation-and-provenance)
- [Records and runtime collections](#records-and-runtime-collections)
- [Dispatch and evidence](#dispatch-and-evidence)
- [Executables, addresses and random state](#executables-addresses-and-random-state)

## Allocation and provenance

| Term | Meaning in this research |
| --- | --- |
| Planetary and biome resource allocation | The planetary pass and biome-local decisions that establish inorganic resource identities and assignments. Landing-site deposit generation concerns where deposits appear on the terrain within a landing area. A biome assignment alone does not locate an outpost-scale deposit. |
| Resource identity and occurrence | Identity is keyed by the IRES FormID. An occurrence is a research term for an instance with a specific origin, such as atmosphere, Everywhere, Special, a Common root or a descendant. One identity can have several occurrences. See the [capacity and provenance model](v1-research-baseline.md#capacity-and-provenance-model). |
| Common family, configuration and assignment | A Common family is rooted at a category-0 IRES and can have descendants. A configuration records the chosen root and descendant IDs. Its origin is the generation event that produced it. An assignment is a biome's use of that configuration, whether newly generated or reused. The family cache holds configurations for reuse, while the shared ID state tracks resource identities. See the [Common family cache](v1-research-baseline.md#common-family-generation-and-cache). |
| Five-tree guard and shared-eight guard | Research aliases for the count checks that route Common processing to fallback. “Tree” here means a cached Common-family configuration. The other check counts entries in shared resource-ID state. See the [Common guards](v1-research-baseline.md#common-guards) and the [retail mapping](component-database.md). |
| Special and Everywhere | Project labels for IRES categories 5 and 6, respectively. The Everywhere pass prepopulates before per-biome allocation. Special selection precedes the Common guards in the per-biome pass. See the [category mapping](v1-research-baseline.md#input-resolution-and-biome-order). |
| Primary allocation path and validation oracle | The old `ResourceViewWidget::OnApplySeed` / leveled-list trail is superseded as the primary allocation path. The historical SurveyAggregator snapshot is an empirical oracle for the CK/RSGD-visible planet-wide output channel with limited coverage. See [superseded trail](v1-research-baseline.md#superseded-primary-trail) and [qualified oracle](v1-research-baseline.md#surveyaggregator-and-qualified-oracle). |

## Records and runtime collections

PNDT, BIOM, RSGD, IRES and ATMO are record signatures. The descriptions below
explain their roles. The exact native class name is given where the retail
mapping establishes one.

| Term | Role |
| --- | --- |
| PNDT and RSCS | PNDT is the planet record signature. RSCS is the PNDT field tag for the seed used by the recovered CK/reference model. The retail `+0x50` seed read is established separately from its field-to-record provenance. |
| BIOM | Biome record signature. Retail RTTI identifies `BGSBiome`. |
| RSGD and effective RSGD | Resource-generation record signature. Retail RTTI identifies `BGSResourceGenerationData`. Effective RSGD describes the selected generation data in the recovered CK model. A non-null PNDT biome override takes precedence over the BIOM default. See [input resolution](v1-research-baseline.md#input-resolution-and-biome-order). |
| IRES and FormID | IRES identifies an inorganic resource record and supplies category/rarity and child-resource data. A FormID is the numeric identifier for a form, such as the 32-bit IRES ID used for resource identity. |
| ATMO | Atmosphere record signature. Retail RTTI identifies `BGSAtmosphere`. The research tracks the inorganic resource contribution from effective atmosphere data. |
| Form record and form bucket | A form record is a typed game-data record, with a corresponding in-memory form in the dispatch example. “Form bucket” describes the runtime type-indexed collection enumerated by the iterator. The PNDT bucket holds pointers and the callback independently checks each accepted form's type byte. |

See the [retail mapping](component-database.md)
and the [dispatch predicates](retail-execution-lifecycle.md).

## Dispatch and evidence

| Term | Meaning |
| --- | --- |
| Direct call, indirect call and dispatch | A direct call instruction encodes its destination. An indirect call obtains its destination from a register or memory. Dispatch is the act of selecting and invoking a target, such as the iterator calling the function pointer it reads from a virtual slot. |
| Callback receiver, vptr and virtual slot | The receiver is the object supplied as the callback's object argument. Its vptr points to a virtual function table (vtable). A virtual slot is a table entry at a byte displacement from that vptr. In SRR-003, “callback receiver” is descriptive and `stl::local_function_detail::ILocalFunction` names the native interface identified through RTTI. |
| TLS | Thread-local storage, data associated with the current thread. The SRR-003 adapter sets and restores a TLS field around the orchestrator call. |
| Static reachability and observed execution | Static reachability describes edges and paths supported by the instructions under their predicates. Observed execution means a trace or equivalent evidence captured those operations in a particular executable and scenario. A resolved static target may still lack a known gameplay caller or any retail runtime observation. |
| `FUN_<address>` | A Ghidra-generated name. Descriptions such as “planetary orchestrator” and “guard fallback” are research aliases. See the [function register](function-register.md) and [structure register](structure-register.md). |

## Executables, addresses and random state

| Term | Meaning |
| --- | --- |
| CK and retail | CK means Creation Kit (`CreationKit.exe`). Retail refers to the shipped game (`Starfield.exe`). Each executable has its own build identity, code addresses and layouts. See [provenance](PROVENANCE.md). |
| PE and RTTI | PE is Portable Executable, the Windows image format. RTTI is run-time type information, used here to associate vtables and object offsets with native types. |
| Preferred VA, RVA and runtime VA | A VA is a virtual address. An RVA is a relative virtual address measured from the image base. Preferred VA equals preferred image base plus RVA. Runtime VA equals the actual loaded module base plus RVA for the matching image. |
| RNG, PRNG and MT19937 | RNG refers to random-number generation or a random-number generator. MT19937 is the Mersenne Twister pseudorandom generator (PRNG) whose state the allocator advances. Integer shuffle draws, binary32 probability conversion, cumulative selection and the two float-scaled index uses have distinct roles. See the [PRNG mechanism register](v1-research-baseline.md#prng-mechanism-register). |
