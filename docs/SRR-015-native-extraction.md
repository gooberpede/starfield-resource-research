# SRR-015 — Native census of retained allocation edges

**Feasible with named preconditions for a structurally qualified census of the
admitted +0x300 store.** The published context, mixed tree geometry, complete
record key and typed payload are recoverable through the existing read-only
approach. A population reader still needs an offline-qualified whole-tree
adapter and an independently prepared work envelope. Missing-component and
model-completeness claims additionally need an independent expected-key census
and the applicable oracle. SRR-013 established the acquisition path for four
rows in one epoch. It supplies regression controls and measured sample cost.
[Acquisition evidence](SRR-012-acquisition-evidence.md) ·
[Paired title result](SRR-013-retail-title-paired-structural-observation.md)

All preferred VAs here refer to the pinned retail AMD64 image
1.16.244.0, base `0x140000000`, SHA-256
`7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28`.
The runtime reader uses authenticated image-relative RVAs. The design and
fixtures in this document are proposed. The operation register distinguishes
observed checkpoint contents from static capability and conditional routes.
[Retail provenance](PROVENANCE.md#current-retail-identity)

## Population and identity

| Set | Definition | Evidence or qualification |
| --- | --- | --- |
| Mixed census | Every descriptor reached from the published context +0x300 root. | Deduplicate physical extents by structural ownership and reconcile the count with header +0x48. The mixed census supplies the search denominator. |
| Native target census | Every edge in that census whose standard key describes a registered `PerBiomeData` edge, with the matching wrapper, exact geometry and independently validated owner and target. | Test the key and wrapper in both directions. Retain attempted target rows that fail admission in the private refusal ledger. No preselected planet list filters the walk. |
| Expected component universe | Independently enumerated keys from a pinned winning-input profile, with explicit supported component-production rules, using the runtime remap for both PNDT and BIOM. | A predeclared baseline subset can be used. A population-wide expectation needs all admitted routes and an exclusion/unknown ledger. Keep source PNDT coverage, per-planet ordered PPBDs, ENAM replacement and CSV eligibility separate. |
| Value-oracle universe | Expected keys with a supported whole-planet generation input profile and qualified projection to the seven slots. | Always evaluate the complete modeled work set for a covered planet. Unsupported sibling biomes, duplicate targets and unexplained differing input order can invalidate predictions for that owner. |

PNDT FormID at +0x28 and allocation owner key at +0x54 coincide on the
authored path at `0x14076EC81–0x14076EC86`. The native sweep uses the
nonzero +0x54 key and requires the type-0xBA PNDT callback admission at
`0x14077C479`. Under this profile resolve the owner high u32 as a PNDT
runtime FormID and require its authoritative record's key to equal the owner.
An unmatched owner or a distinct runtime key encoding is an identity refusal
pending a qualified independent remap. A title-card edge need not already
have received a productive visit. Presence, generation eligibility and
nonzero output are separate observations.
[Authored key and form map](SRR-012-acquisition-evidence.md#independent-form-identity) ·
[Sweep gates](SRR-014-startup-allocation-component-database-lifecycle.md#sweep-and-productive-writes)

For discriminator `d`, the first word is
`K0 = (u64(owner) << 32) | 0x10000 | u16(d)`. Its native owner range
includes all keys from `(K0, 0)` through `(K0, 0x0000FFFFFFFFFFFF)`.
Require standard targets to have a nonzero zero-extended BIOM u32 in the
second word, matching the payload BIOM u32. The primary comparison key is
the pair of canonical PNDT and BIOM identities, each expressed as defining
plugin identity and local ID under an independently attested remap. Preserve
the winning source separately. Duplicate raw keys, duplicate canonical
pairs produced by remapping, repeated addresses under different claims and
alternative namespaces carrying the target discriminator or wrapper all
require explicit diagnostic treatment. Refuse a target-shaped row whose two
type tests disagree. Different typed keys are ordinary mixed entries even
when they share an owner or target numerical ID. Each mixed edge must expose
its key and wrapper prefix so it can qualify as an exclusion.
[Key bounds and construction](SRR-012-acquisition-evidence.md#exact-mixed-index-model)

For each present candidate, authenticate PNDT and BIOM, referenced optional
RSGD and every nonzero resource via the independent FormID map. Capture PNDT
seed, raw override and ordered BIOM RSGD list as input witnesses where
available. Native behavior resolves a missing or incompatible optional RSGD
to null. Preserve the unresolved or wrong-type raw word and mark the input
qualification separately. A reproducible resolution failure with exact,
terminated map traversal is an identity or input diagnostic, whereas a read
or chain failure cannot establish what the map contains. A typed candidate
with failed owner/BIOM/resource identity remains in the structural inventory,
but prevents a fully qualified target census. An all-zero row with valid
identity stays in the inventory. An absent row has no raw vector.
[Independent identity](SRR-012-acquisition-evidence.md#independent-form-identity) ·
[SRR-013 decoder](../tools/srr013/native.py)

## Whole-tree read contract

```text
Authenticated process epoch and image
    |-- published slot -> embedded DB -> +0x300 root and mixed count
    |      |-- root-order child walk -> leaf directories -> packed blocks
    |      |                 |             |                 |
    |      |                 +---- check neighbor links ----+
    |      |                             every descriptor -> key/wrapper
    |      |                                    admitted -> inline payload
    |      +-- registration receiver/descriptor checks the runtime type
    +-- independent FormID map -> PNDT, BIOM, optional RSGD and resources
                                    |
                                 identity join
                                    |
               full present-key census + independently authored expected keys
```

The diagram shows source and validation dependencies. It conveys no ordering
of startup callbacks, writes or load activity. The type registry is reached
independently from the image; the DB link represents applying its type witness
to the traversed tree.

| Base in private witness | Required data |
| --- | --- |
| Image base `M` | Read `M+0x82EEBB0` and require `M+0x82EE5C0`; DB vptr `M+0x4D6A6C0`. Discriminator at `M+0x61DFA4C`, independently verified through registry `M+0x82EEC20` and the live registration receiver. |
| Mixed header | Root qword +0 and mixed total qword +0x48. Both zero yields the structurally empty case after paired admission. |
| Internal node | u32 level and u32 separator count at +0/+4; 0x10-byte keys from +8, child qwords from +0xA88, count+1 children. Count at most 0xA8. |
| Level-zero leaf | u32 block count +4, next/previous +8/+0x10, 0x10-byte block minima from +0x18, block qwords from +0xA98. Require nonempty and at most 0xA8 entries. |
| Packed record block | u32 marker `0xFFFFFFFF`, u32 count +4; occupancy metadata +8, descriptor directory `+0x10` with u16 size/offset at stride 4, exclusive `+0xFE0` fence. A root can point directly to a packed block. |
| Standard typed edge | Size 0x90, wrapper vptr `M+0x4B3D258`, key pair at +0x10/+0x18, payload +0x20. Payload +0x40 BIOM, +0x44 coverage, +0x48 biome seed, +0x4C override, +0x50..+0x68 slots. |
| Independent form map | Slot `M+0x5E60EA0`; table and capacity at map+0x10/+0x18. Entries are 0x18 bytes, with u32 key +0, pointer +8, u32 next +0x10. |

[Native geometry and exact locators](SRR-012-acquisition-evidence.md#exact-mixed-index-model) ·
[Registry and publication](SRR-012-acquisition-evidence.md#published-context-and-identity)

```text
census(reader, independent_limits):
    identity = verify_epoch_image_and_checkpoint(reader)
    anchors = authenticate_publication_registry_root_and_form_map(identity)
    require(root_is_null == (mixed_count == 0))
    admit_count_within_independent_envelope(mixed_count)

    # FUN_1403832A0 defines ordered children and lower-bound semantics.
    # Enumerate every used child position even if no expected key selects it.
    for leaf in root_order_children(root):
        validate_level_counts_unique_extents_and_all_ancestor_fences(leaf)
        cross_check_previous_and_next_against_root_neighbors(leaf)
        for block in leaf_order_blocks(leaf):
            # Direct-block root acts as a one-block sequence.
            validate_directory_frontier_holes_and_all_record_spans(block)
            for descriptor in block_directory_order(block):
                key, vptr = read_exact_edge_prefix(descriptor)
                count_descriptor_once()
                verify_block_min_leaf_key_global_order_and_ancestor_fences(key)
                if standard_type_and_wrapper_agree_as_target(key, vptr):
                    collect_typed_payload_and_independent_identity(descriptor)
                else:
                    certify_mixed_exclusion_or_record_type_key_conflict(key, vptr)
    prove_root_end_leaf_chain_end_and_exact_mixed_count()
    cross_check_grouped_target_keys_and_owner_fences_against_native_order()
    recheck_structural_witnesses_and_close_epoch_anchors(identity, anchors)
    return witness

A = census(reader, limits)
B = census(reader, limits)    # fresh root and independent caches
require A and B cover the same graph, keys, identities and raw slot bytes
```

Use checked widened address arithmetic, exact reads and non-overlapping
claims for node/block pages and known map/form/registry allocations.
Claim before following a pointer and reject cycles, shared children and
cross-role aliasing. Every non-root child level decreases by exactly one.
Validate record minimum prefix length 0x20, directory/frontier bounds,
pairwise disjoint spans, block free-space credit and exact leaf-advertised
minima. Internal separators admit equality on either side as in the frozen
decoder's fence check. Demand global nondecreasing order including cross-page
adjacency. A duplicate target straddling a fence is still a duplicate. Check
both end links against root-derived edges. The sentinel null block with slot
`0xFE0` in `FUN_1403A4250` is a terminal cursor, never a record descriptor.
Root traversal and the neighbor walk must agree before accepting the terminal
fence. FormMap lookup separately uses FNV-1a-64 of the little-endian ID
masked by capacity minus one, and finishes evidence through the native
capacity sentinel even after a match. Bound cycles, reject a duplicate
queried key and validate object ID, type and, for resources, the pinned vptr.
Store the chain witnesses and distinguish cache reuse per pass from
independence across passes.
[Exact mixed index](SRR-012-acquisition-evidence.md#exact-mixed-index-model) ·
[Frozen checks](../tools/srr013/native.py) ·
[FormMap evidence](SRR-012-acquisition-evidence.md#independent-form-identity)

For a fixed admitted graph, every descriptor belongs to exactly one
root-backed record position. Enumerating every child position inductively
visits every leaf and every advertised block. Counts, unique extents and the
independent leaf chain catch omitted, repeated or redirected positions.
Inspecting each descriptor against the same key and wrapper predicates
establishes that no matching descriptor in the admitted graph was skipped.
Grouping the sorted census yields every owner range, with predecessor and
successor keys or root-backed ends. In particular, a lower-bound descent that
skips an earlier block because its separator is malformed cannot silently
exclude those descriptors. A valid rooted graph and count could be consistent
while a separate storage object, orphaned allocation or pending queue command
exists. Such objects are outside this checkpoint census.

A qualified missing component requires an expected key from the independent
expected set and a qualified full absence in that observed census. If
the oracle's expected-source contract is incomplete for the owner, publish
diagnostic set differences with the corresponding scope. A partial walk,
malformed fence, identity refusal, count disagreement or canceled walk never
produces a global absence verdict. Keep separate traversal, target identity
and value applicability statuses so a failed value prediction cannot erase
valid physical coverage.

## Read work and consistency

The frozen SRR-013 adapter supplies exact reads, epoch and mapped-image
verification, FormID and extent checks, journals and cancellation examples.
Its fixed sample limits, linear scan across claimed extents and sample request
list are unsuitable as population defaults. A future adapter should preserve
validation while using an ordered non-overlap index or offline sorted extents
with an incremental ownership check, checked queues and bounded coalesced
reads. Coalesce active record prefixes and typed witness spans where the
backend can prove complete bounded reads. Cache forms and visited chain
entries once per pass. A whole-tree adapter can reconstruct native behavior
without calling a game method. The native typed copy is valuable as a
member-order specification and fixture control, but returns the first BIOM
match and requires a caller-owned typed output value. Its guard and lifetime
dependencies require execution under the game's ABI, address space, TLS,
object and page protocols. The FormID wrapper even touches a native bitmap
and participates in independent map state. The external observation uses
query/read access and acquires none of those native guards.
[Exact form-map side effects](SRR-012-acquisition-evidence.md#independent-form-identity) ·
[Guard catalogue](SRR-014-database-evidence.md) ·
[Frozen reader](../tools/srr013/memory.py) ·
[Budget recovery](SRR-013-live-observation-budget-recovery.md)

Derive limits for each declared reader backend before acquisition. With
`E` the admitted mixed-count envelope, `D` the admitted root level,
`P` packed blocks, `L` leaf directories and `I` internal nodes, a
valid nonempty graph has `L <= P <= E` and `I + L <= (D+1)*L`.
Each node has at most 169 children, each populated block has at most
`floor((0xFE0-0x10)/(4+0x20)) = 112` descriptors. Take the smaller
proven bound where both geometry and the independent envelope apply.
If a direct packed root is used set `P=1, I=L=0`.
Count actual attempted reads and bytes, including failed reads, query
operations, revalidations, and output. For one pass a backend reading
each active node/block extent in one window budgets up to
`0xFE0*(I+L+P)` tree bytes and `I+L+P` tree reads. A backend that
reads prefixes individually must itemize directory windows and
up to `E` key/wrapper prefixes plus separate typed spans. Any chunk
introduced at a region boundary increases the declared request count.

Bound queried forms by the distinct owners, BIOMs, RSGDs and resource IDs
from the declared input profile and validated rows, including unexpected
identities within a separately preadmitted allowance. Before deduplication
`T` eligible candidates imply at most `10*T + sum(BIOM list counts)`
references (two identity forms, one optional override, seven outputs,
plus the ordered BIOM lists). Bound each list and each chain using an
independent corpus/fixture envelope plus actual validated table capacity.
The coarse identity cost is up to `20*Q*C` chain bytes for `Q`
lookups and chain cap `C`, plus typed-object and bounded list reads.
Dry-run the exact backend against malformed graphs and representative
large fixtures, including long collision chains and short reads.
Approve finite request, byte, node/record, chain, output and memory
ceilings against the resulting work estimate. An untrusted header cannot
raise the independent envelope. Scale the paired ceiling for end-anchor
and witness revalidation work, up to four full window plans when both
passes re-read all windows. Count reseals and optional retries separately.
Derive the timing estimate from measured request/throughput and hashing
costs on those fixtures, with cooperative cancellation checks before
each operation and during output. Timing is a planning measurement and a
protection envelope, independent of scientific absence. An admitted
held-title interval may end before the work budget is used.

Use two complete collections with fresh anchors, roots, extents and
form lookups each time. Re-read consumed structural/form windows and
closing anchors, compare raw slot vectors separately and retain the
bracketed time bounds. Compare ordered keys, payload/source identity,
traversal shape, map witnesses and exact slot bytes. A repack that only
moves addresses will fail this deliberately strict pair even if values agree.
Only a separately budgeted full retry can requalify transient failures.
Do not combine successful prefixes across attempts. Closing root equality
alone misses value writes and ABA. Paired equality also permits an
intervening mutation followed by restoration, repeat reads of a stable
intermediate zero state, and a combination of values that did not coexist
atomically. The approved claim is whole-graph paired structural observation
under this profile. It entails no transactional snapshot, continuous
lifetime, sweep completion or serialization.

## Evidence schema

Emit a private sealed UTF-8 JSONL stream and a versioned manifest. In the
private stream emit each pass in native key and structural visit order.
Use stable `pass, path, descriptor ordinal` to preserve duplicate and refused
rows. Record both u64 raw key words; store the exact 28 slot bytes and
their seven little-endian u32 words separately from normalized identities.
Keep private process epoch and image mapping, UTC start/end, request counters,
root/registry/type witnesses, structural path and source addresses, record
length, identity lookups, raw fields and hash-identified input policy.
Per-pass coverage fields include mixed header count, nodes/leaves/blocks,
visited descriptors, classified mixed exclusions, typed accepted, typed
refused, duplicate/alias counts, lower/upper/end fences and failure reason.
Include the approved bounds, consumed budgets, stop/checkpoint evidence,
reader and schema version, executable and input digests, payload digest per
pass and paired verdict. Record failures and preserve a protected prefix if
the final seal fails. Partial evidence exports carry an explicit incomplete
flag.

Generate a separate deterministic comparison JSONL keyed by canonical
planet and BIOM, sorted by normalized defining plugin then numeric local ID
for each key member. Normalize seven slots to canonical resource identities
or explicit zero. Preserve refused/absent/unsupported status without
substituting zero for unknown. Permit only a disclosed row projection or
aggregate when normalized IDs/source detail require withholding. Publish
counts, qualified checkpoint label, comparator policy and export SHA-256.
Omit process IDs, creation timestamps, machine paths, memory addresses,
raw bytes and unreviewed local plugin names. A random run label can link
sanitized artifacts without exposing process identity. Retain the private
run label mapping and raw-journal digests in private custody. Specify
canonical JSON (sorted members, UTF-8, single LF, fixed-width strings for
raw hex fields and no NaN) before computing file digests. Independent
comparison reads the normalized projection and committed oracle manifest.

## Offline fixture qualification plan

Reuse the [owned fixture and region reader](../tools/srr013/fixture.c),
[budget qualification](../tools/srr013/qualify_budget.py) and the
[structural harness](../tools/srr013/qualify_structural.py) for low-level
regression controls. Keep these sources frozen. A new population harness
must run the candidate whole-tree logic through a byte-backed reader with
scripted read-event mutations. Existing sample harnesses cannot qualify
the proposed enumeration.

| Fixture | Required result |
| --- | --- |
| Direct packed root, then deeper tree | Same typed rows after deterministic rebuild. Cover multiple owners, multi-biome groups spanning blocks/leaves, empty owners, known mixed entries and a valid unexpectedly indexed owner omitted from expected inputs. Prove census against fixture-builder descriptor truth and an independently sorted reference. |
| Empty published tree and unpublished context | Empty root/count yields a structurally empty census only under full admission. Null publication is a refusal. Missing expectations appear only after the qualified empty result. |
| Sparse rows and all zero | Assert all seven positions, including holes between emissions. Preserve all-zero row with valid identity and compare differently from missing row. Use the four SRR-013 samples as identity and slot regressions. |
| Duplicate raw/canonical pairs, alias and collisions | Duplicate across a separator, two edges sharing a BIOM legitimately across owners, one block or form pointer reused under different claims, conflicting vptr/discriminator, same runtime IDs remapped to colliding canonical keys and duplicate keys inside a legitimate hash collision chain. |
| Malformed coverage | Wrong mixed count, inaccessible or truncated row, oversized or overlapping descriptor, false minimum, violated separator, leaf skip/loop/wrong backlink, wrong level, premature null child, extra apparent leaf successor and root/count inconsistency. Never emit whole-population absence. |
| Owner or type failures | Independently missing PNDT, PNDT owner-key disagreement, edge/payload BIOM mismatch, valid RSGD type with wrong identity, wrong BGSResource type/vptr and unresolved namespace. Record causes without treating targets as benign mixed entries. |
| Timing and mutation | Insert/delete during first traversal, split/repack between passes, rewrite slots with header unchanged, reused address, same bytes restored before second read, pause in cleared output state. Reject observed churn and document that undetectable ABA or repeated intermediate values can still pass the pair. |
| Work and export | Near-cap valid multi-page graph, malformed operation amplification, cancellation between reads, attempt with failed seal, deterministic reordered output, and private-address leakage test. No unresolved row can silently shrink the denominator. |

## Capability and caller register

**S** denotes a verified static operation; **R** a statically joined route
under its stated predicates. The SRR-013 title observation verifies retained
contents and structure for four samples. This register has no native
invocation witness for those samples. A historical menu-return trace covers
reset ancestry only at the cited events.

| Operation | Upstream route, gate, effect and record | Evidence and extraction consequence |
| --- | --- | --- |
| Publication and registration | `FUN_1423FF640` lazy owner (TLS gate), constructor `FUN_1424059F0` at `0x1418993BE–0x1418993E3`, register `FUN_14231D000 → FUN_142404EF0` at `0x14231D7D9–D7F1`. Author, allocator, CSV and reset read the published slot. | S/R. External reader reads the witness and the independently registered descriptor. Neither initialization nor registration is required of the reader. |
| Navigation and writer enumeration | `FUN_1403832A0/1403833E0` lower-bound, `FUN_1424103E0` continuation and `FUN_1403A4250` advance. PNDT bucket iteration resolves visitor `FUN_14077C470` via vptr `0x144B3D9F8`; adapter `FUN_140779610 → FUN_140779760 → FUN_14077BCE0` borrows typed payloads from the admitted nonzero PNDT key range. Early path uses a gated CSV setting; late call at `0x14094EF57`. | S/R. Reconstruct traversal and prove whole graph separately. The collector writes scratch pointers and the orchestrator writes in place, so neither is a passive census operation. |
| Keyed lookup and typed copy | `FUN_140771F30 → FUN_1405F7A80`, first matching payload BIOM at `0x140771FB6`; assignment `FUN_14076E810` at `0x14077200D` into R9 caller storage. Representative direct caller sites `0x1407BAA7A/0x1407BD677/0x14086A798` operate on local copies. Miss returns false without a generator. | S/R. The seven copied fields specify what to decode. The first hit would hide a later duplicate. Representative readers acquire shared native mode outside this primitive. |
| Form lookup | `FUN_1405DE3B0 → FUN_1405ACAD0` reaches BIOM/optional-RSGD checks in `FUN_140777870`; `FUN_14086A6D0` independently checks resource form type `0x9F` after reading a copied word. | S/R. Byte-level reconstruction can reuse chain semantics. The native entry has bitmap and map-guard side effects. |
| Guard scope | Shared entry at `0x1407796A6` spans writer orchestrator; reader entries at `0x1407BAA5D/0x1407BD656/0x14086A77B`. Mutation admission via `FUN_142404A80` enters ticket state for insert, removal, clear and reverse key. The borrowed-pointer path also consults `FUN_142404330` page control. | S/R. Shared writer and shared readers can coexist. A page token, ticket, queue counter or root count is no slot-write generation. |
| Author and insert | PPBD submit `0x14076F360`, ENAM replacement submit `0x14076FCEA`, CSV submit `0x14234103A`. Queue captures authored zero-initialized payload and DB; callback +8 dispatch resolves to `FUN_140777290 → FUN_140774E00 → FUN_1407766B0`. Typed construction follows index insertion through `FUN_140382700` or `FUN_140383010 → FUN_140382800`. | S/R. Equal keys can allocate additional descriptors; first root/count publication can precede complete initialization; repack/split can move payloads. A9 leaves startup queue completion vs sweep order open. |
| Remove and compact | ENAM and PNDT lifetime sites `0x14076F751/0x14076E9EA/0x14076EB83` submit `FUN_140772EE0 → FUN_140776680 → FUN_140774970 → FUN_142409490`. Guarded owner/type range erase invokes edge destructor then notifies and repairs cursor. | S/R. Missing edge after a later checkpoint can reflect destruction, replacement or changed inputs. |
| Clear, reset, disposal | Signed reset arm at `0x141897167–0x14189716B` can clear through `0x141897552 → FUN_1424063B0`, then permits replay/module re-entry. TES destructor reaches clear at `0x140574286`. Shutdown calls `FUN_1423FE320` at `0x141882F42`, then zeros publication. Type teardown is independent via `FUN_14231DA10 → FUN_1424058B0`. | S/R. Selected menu-return reset and loader events were observed historically. The DB address can remain unchanged through clear/rebuild. Check registry and publication independently. |
| Edge notification and reverse key | Insert status controls `FUN_142406B70`; key read at `0x142406BA5–BAE2` feeds reverse-key +0x358 command through `FUN_1424069F0`, and a 16-byte key copy reaches context +0x38 subscriber dispatch `FUN_14240F5F0` at `0x142406BE8`. Concrete callback comes from slot +0x10 at `0x14240F659`. Range erase has its own post-erase notification at `0x142409691`. | S/R for native notification/key maintenance. Subscriber receiver-to-payload join remains open. |
| Possible transfer to +0x268 | Descriptor vtable `0x144D5F5C8` installed at descriptor receiver +0x100. Slots +0x28/+0x30 target `FUN_142322520` which copies or assigns a supplied typed source into +0x268 (`0x142322633/664`). The focal allocator's verified +0x268 path is a separate `BiomeData` discriminator and coverage update. | S for copy capability. No joined computed +0x300 source, matching target/destination or execution context. For this store census, +0x268 and +0x358 supply neither extra retained edges nor a substitute value source. |

[Result and reader lifecycle](SRR-011-planetary-allocation-execution-and-result-lifecycle.md#readers-and-reuse) ·
[Native operation catalogue](SRR-014-database-evidence.md#operation-catalogue) ·
[Startup paths and gates](SRR-014-startup-allocation-component-database-lifecycle.md#sweep-and-productive-writes)

## Focused offline B8 check

The pinned-image scan below reported 111 candidate byte positions and 111
distinct decoded references over 236,427 selected PE exception ranges. It
reported two exact `.rdata` qwords for `FUN_142322520` at
`0x144D5F5F0/0x144D5F5F8` and no decoded direct branch to that factory.
The `0x14231D19B–1A2` vtable reference installs the exact registered
receiver descriptor. The notifier continuation at `0x142406BD3–BE8`
uses DB +0x38 and copies only the edge key into its stack argument. The
nearby additional notifier caller `FUN_140777560` constructs a different
0x40-byte edge using wrapper `0x144B3D270` at `0x1407776E3–7753` and
copies 24 payload bytes. These checks sharpen the direct reference and
payload bounds. The general subscriber dispatch has many callers, and
the exact scan cannot resolve dynamically populated receivers, computed
dispatch or nonselected decode ranges. This is a bounded negative for a
direct factory branch. A concrete registered receiver, +0x300 computed
payload with matching canonical key, +0x268 destination and invocation
phase would establish the missing B8 join. Defer deeper subscriber ancestry
until evidence makes that join material to a question beyond this store.
[SRR-014 B8](SRR-014-lead-register.md#b8-coverage-and-history)

```powershell
# Use the hash-pinned retail PE as read-only data and Python with Capstone.
python -B tools/srr011/inspect_pe.py $srrExe scan 14240f5f0 142322520 144d5f5c8 142406b70
python -B tools/srr011/inspect_pe.py $srrExe functions 14240f5f0 140777560 142322520
python -B tools/srr011/inspect_pe.py $srrExe window 142406b86 71
python -B tools/srr011/inspect_pe.py $srrExe window 14231d18d 20
```

A9's checked direct and deferred attachment routes establish that each
collected edge was constructed before use on that route. They do not
establish that all winning authored commands were visible at sweep entry.
The adjacent unrelated drains in SRR-014 remain scoped exclusions.
Resolving startup ordering would require command/receiver identity joined
to an epoch's schedule and sweep. The proposed title census only measures
retained state. It neither closes the startup lead nor treats unmeasured
alternatives as competing explanations.
[A9 provenance](SRR-014-lead-register.md#srr-014--lead-register)
