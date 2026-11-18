# SRR-012 — Native acquisition evidence

All VAs refer to retail AMD64 `Starfield.exe` 1.16.244.0, preferred base
`0x140000000`, SHA-256
`7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28`.
This report derives a bounded reader design from the committed SRR-011
baseline at `3e7f3f6b286d49eff5d09199ca547819c9b72b0c` and the matching
executable inspected as offline data. **PROVEN STATIC** below means the
instructions establish the relationship on the identified native path.
Availability and stability at retail checkpoints remain unmeasured.
[Retail provenance](PROVENANCE.md#current-retail-identity) ·
[SRR-011 result lifecycle](SRR-011-planetary-allocation-execution-and-result-lifecycle.md#result)

## Published context and identity

| Relationship | Exact evidence and constraint |
| --- | --- |
| Getter to process-global object | Both normal returns in `FUN_1423FF640` use the same image address `0x1482EE300` at `0x1423FF660` and `0x1423FF69F`. The TLS load and compare with `0x1482EE2C0` select the lazy initialization path. The known return object has an image-relative address across processes. |
| Object to published `BSComponentDB2::DB` | `0x1423FE0E9` initializes object +0x8B0 to zero. `0x1418993BE–0x1418993E3` gets the object, constructs a context at object +0x2C0 via `FUN_1424059F0` and publishes its address at object +0x8B0. Independently, the writer, authored PPBD loader, CSV input loader and reset read that slot at `0x140779676`, `0x14076F359`, `0x1423409BD` and `0x14189754B`. |
| Context identity and index | `0x142405AD1–0x142405AD8` installs the vptr at `0x144D6A6C0`. Its RTTI type name at `0x145CA7528` identifies `BSComponentDB2::DB`. Constructor runs at `0x142405E01–0x142405E63` and `0x142405E86–0x142405ECC` initialize the tree header at context +0x300. The writer collector and keyed reader independently add +0x300 at `0x14077BD31` and `0x1405F7AA5`. |
| Publication and disposal are separate operations | `0x141882F42–0x141882F4E` disposes the published context through `FUN_1423FE320` and then zeros the published pointer. `0x1423FE35D–0x1423FE364` destroys the +0x300 tree as part of that call. The SRR-011 reset path can clear indexed objects with the context itself still published. |

For the supported path, let `M` be the authenticated main-image mapping
base. Read the qword at `M + 0x82EEBB0` and require it to equal
`M + 0x82EE5C0`. Require its qword at +0 to equal
`M + 0x4D6A6C0`. The embedded index starts at `M + 0x82EE8C0` only
after those checks. A direct read of the index RVA alone would skip
publication checks and could report zeroed, initializing or disposed
storage. The known active context is selected by one authoritative slot.
An alternate value, null or conflicting identity is an indeterminate
measurement under this profile. Same address at two checkpoints is
expected even when an in-place reconstruction has occurred.

The runtime discriminator is the u16 at `M + 0x61DFA4C`, read afresh
with the context. `PerBiomeData` at `0x144D5F0A0` and the descriptor
at the registration receiver +0x100 are passed at
`0x14231D7D9–0x14231D7F1`. A stronger registry check is available.
`FUN_14240A270` returns the static registry at `M + 0x82EEC20`.
It has a u32 entry count at +0 and a qword entry table pointer at +8.
`FUN_142404EF0` initializes the word to `0xFFFF` at
`0x142404F4F`, writes the index at `0x142404FE4` or
`0x14240518D`, and stores the descriptor as the first qword of the
0x18-byte registry entry at `0x142404FCB` or `0x1424051CF`.
Require an in-bounds registered entry whose descriptor equals
`read_u64(M + 0x61FA160) + 0x100` with a valid nonnull registration
receiver. The constructor publishes that receiver at `0x14231D032`
and sets its vptr to `0x144D5FAC8` at `0x14231D06E`. Verify the
receiver vptr at the relocated address.
Deregistration clears the table entry and type word at
`0x142405923–0x142405927`. A zero word by itself is ambiguous.
Read these witnesses again around the selected edge reads.

## Exact mixed-index model

All scalar fields below are little-endian. The key is a pair of
unsigned 64-bit words compared lexicographically. The index contains
entries of multiple types. A key with a different discriminator or
owner may bound the target range but supplies no result for that range.

| Base | Layout | Native evidence |
| --- | --- | --- |
| Context +0x300 | Tree root pointer qword at +0. Total edge count qword at +0x48 counts mixed entries. A null root and zero count are compatible with an empty tree. | `0x1405F7AF0` and `0x1403832B4` load/test the root. `0x1403827DF` and `0x140382FE0` increment the entry count. |
| Tree node with nonzero level | u32 level at +0, u32 separator count at +4. At most 0xA8 separator keys, pair stride 0x10 starting at +8. Child pointers start at +0xA88, stride 8, with count+1 children. A level-zero child is a leaf directory. | `0x1403832C4–0x140383329` descends by an unsigned two-word lower bound. `0x140382D5F` and `0x140382E30–0x140382E79` bound and initialize the arrays. |
| Level-zero leaf directory | u32 block count at +4, at most 0xA8. Next and previous leaf pointers at +8 and +0x10. Pair of first keys at +0x18 + 0x10*i. Block pointer at +0xA98 + 8*i. | `FUN_140383570` lower-bounds the first keys. `0x140383372–0x1403833B5` joins the previous leaf and selected block. `0x1403A4264–0x1403A42C8` advances blocks and next leaf. |
| Record block | u32 marker `0xFFFFFFFF` at +0, u32 record count at +4. A single-block tree can point directly here. Descriptor array starts at +0x10, stride 4, with u16 record size followed by u16 record offset. Storage is relative to the block base and ends at exclusive +0xFE0. | `0x14038275B–0x14038276F`, `0x1403827B2–0x1403827E3` initialize and insert. `0x1403832C4–0x1403832C9` selects the direct-block case. `FUN_1403833E0` uses the descriptor's second word. |
| Inline edge | For this type, descriptor size `0x90`, wrapper vptr qword +0 equal to `M + 0x4B3D258`, key words +0x10 and +0x18, payload at +0x20. | `0x14077671E`, `0x14077673B` supply the size. `0x140776782–0x1407767A4` writes the wrapper, keys and copies the payload. RTTI name at `0x145A18D30` identifies the wrapper's `Edge<CTPerBiomeData>` specialization. |
| Payload | Reader compares BIOM u32 at +0x40. RSGD u32 is at +0x4C. Seven u32 result IDs are at +0x50 through +0x68 inclusive. From the edge these are +0x60, +0x6C and +0x70 through +0x88 respectively. | `0x140771FAA–0x140771FB9` resolves and compares payload BIOM. `0x1407778F0–0x140777923` reads and type-checks BIOM/RSGD. `0x140779AF5–0x140779B2E` clears the result fields. `0x14077200D` calls the copy helper. |

The lookup bounds are inclusive. Use
`K0 = (uint64(PNDT_key) << 32) | 0x10000 | uint16(discriminator)`
and the range `[(K0, 0), (K0, 0x0000FFFFFFFFFFFF)]`.
The collector constructs both bounds at `0x14077BD0A–0x14077BD63`.
`FUN_140772620` and `0x140771F71–0x140771F89` use the unsigned
upper comparison. In the PPBD creation path, the caller supplies the
PNDT FormID and payload BIOM ID at `0x14076F340–0x14076F360`.
`0x1407731A2–0x1407731BE` constructs the two words with the BIOM
zero-extended in the second. The CSV update path uses that same
construction through `0x14234102B–0x14234103A` and
`0x140773C02–0x140773C1E`. For the supported standard components,
verify the full second word equals the expected runtime BIOM FormID
and agrees with the independently stored payload BIOM. A different
encoding in a relevant edge is outside the qualified sample profile.
The native reader accepts the **first** payload BIOM match.
A scientific negative or a validated unique match requires covering
the **entire** bounded range and handling multiple matches explicitly.

For a bounded design, descend internal nodes through the first key
greater than or equal to the lower key, or the final child. In a leaf,
choose the exact first-key match or the predecessor block where
available, including the last block of the preceding leaf. Use the
native first-block case if there is no predecessor and the range
starts before all block keys. Lower-bound within the block and advance
through records and successor blocks until the first key above the
upper fence or the proven end of the root-backed traversal. The
lower-bound and continuation are implemented across
`FUN_1403832A0`, `FUN_1403833E0`, `FUN_1424103E0` and
`FUN_1403A4250`. The iterator's internal end markers `0xA8` and
`0xFE0` accompany null leaf/block pointers. They are neither
record offsets nor candidate row indices.

### Separator meaning and packed records

**PROVEN STATIC on the pinned retail image:** internal pivots fence routing
keys, including leaf-advertised **block minima**, rather than every record
inside those blocks. Comparisons are lexicographic on two unsigned u64
words. Equality takes the left internal child. The leaf then selects an
exact minimum or the predecessor block, including the previous leaf;
record lower-bound and cursor continuation finish the search.

The writer supplies the decisive distinction. In `FUN_1403835E0`, the
left-insertion split copies original leaf entries 84 onward to the right,
truncates the left, inserts the new left minimum, and promotes left key 84
at `+0x558`. The other branch promotes left key 83 at `+0x548`. Both are
the **last left block minimum**, not the last record key. Internal splits
promote existing routing pivots; they do not derive record maxima.

| Native locator | Established operation |
| --- | --- |
| `0x1403832EE–0x14038331E` | Unsigned two-word internal lower bound; equal pivot chooses its left child. |
| `0x140383339–0x14038339C` | Exact leaf minimum or predecessor; previous leaf when needed. |
| `0x14038340D–0x14038343C` | Unsigned lower bound within a packed block. |
| `0x142410439–0x14241049F`, `0x1403A4250–0x1403A42CF` | Cursor continuation through record/block ends and leaf links. |
| `0x140383D97–0x140383E2E`, `0x140383E64–0x140383F67` | Leaf split and promoted last-left-block minimum. |
| `0x140383776–0x140383898`, `0x140383A14–0x140383A5E` | Internal pivot promotion and repartitioning. |
| `0x140384499–0x1403844EF`, `0x140382E8D–0x140382EA1` | Parent key/right-child insertion and new-root installation. |

A final left block can therefore contain records greater than its ancestor
pivot. A query beyond that pivot can route right and select the preceding
leaf's final block. This is intentional navigation, not evidence of a
malformed tree. **SUPERSEDED:** the external reader's former assumption
that every descendant record must lie within all ancestor routing fences.
Apply those fences to pivots and block minima instead. Bound actual records
against the next block's minimum and global record order. The promoted
last-left minimum is a demonstrated static writer shape. **PROVEN on
disposable fixtures:** the external inclusive routing contract also admits
an interior pivot or equality with the next child's minimum while retaining
correct lookup/iteration. Those alternative pivot shapes are navigation-
derived fixture evidence, not observed retail writer states; exact pivot
equality is not imposed as an additional external-reader assumption.
[Current checked contract](SRR-016-native.md#separator-semantics)

Check the encountered levels, counts and sorted keys before following
children. Verify each visited leaf's advertised block minima against
its decoded records. Verify predecessor and successor links and
coverage fences against the root traversal. For any required block,
use checked pointer arithmetic, ensure that each descriptor lies in
the directory, and require that described spans are disjoint, start
past the directory and end by +0xFE0. Require room for both key words
before using a row as a fence. Enforce the exact size and vptr only on
the candidate type. Treat duplicate target keys, disagreement between
payload BIOM and edge target, unexplained order breaks, truncated or
unreadable reads, cycles and depth or byte budget exhaustion as
indeterminate. A stable empty range, including a structurally accepted
null root, can give the diagnostic sub-state component absent.
It yields no eligible payload inspection.

## Independent form identity

The edge key, registered type and wrapper prove where a record was
found. Validate authoritative forms through the separate FormID
lookup or an equivalently grounded identity witness before making
a checkpoint claim. Match against accepted input records and the
checkpoint's verified load order. `0x14076EC81–0x14076EC86` copies
PNDT FormID at +0x28 to its allocation key at +0x54 on the PPBD
path. `0x14077C479` requires type byte +0x2E equal to `0xBA`.
`0x140777900` and `0x14077791A` require BIOM and optional RSGD
type bytes `0xA0` and `0xAB`. For an independently resolved PNDT,
require the expected FormID, type, PNDT key and, when expected from
the sample manifest, seed at +0x50. An unresolved or mismatched form
is an identity failure. An optional zero RSGD field is handled by the
sample's validated effective-input rules.

The opened process can expose the same form map without calling
`FUN_1405DE3B0`. Its qword pointer is read from `M + 0x5E60EA0`
at `0x1405DE3BB` and `0x1405DE3D9`. Map +0x10 is the table
pointer and +0x18 is its qword capacity. Entries have 0x18-byte stride,
a u32 key at +0, qword form pointer at +8, and u32 next index at
+0x10. `FUN_1405ACAD0` derives the initial slot as FNV-1a-64 of
the four little-endian FormID bytes, masked with capacity−1. A starting
slot with next `0xFFFFFFFF` is empty. Otherwise the native lookup
compares the key and follows next indices until it matches or sees
the capacity sentinel. Bound table arithmetic, validate a nonzero
power-of-two capacity for this profile, and check every followed
index, stopping on cycles or unknown state. Validate the record ID
and type before use. Include map metadata, chains and relevant form
fields in both collections. This independent input identity path
contains no retained allocation slots.

The native wrapper does more than look up the hash chain. Its call at
`0x1405DE3D4` can update a per-FormID bitmap at `0x14036BCE9`. The
lookup path also enters native map state through +0x30 at
`0x1405DE3E0–0x1405DE3E4` and releases state using +0x34 at
`0x1405DE413`. The proposed external lookup reproduces only the table
lookup semantics and rejects missing or inconsistent witnesses.

## Acquisition and bounded lead dispositions

| Lead | Disposition | Evidence and remaining action |
| --- | --- | --- |
| Process-global owner versus TLS or context search | **Resolved, static.** | The two returns, constructor publication, actual writer reads and teardown converge on one module-relative publication slot. TLS controls lazy initialization. A displacement-based scan and examination of the getter callers with candidate +0x8B0 writes confirmed publication and shutdown and excluded the unrelated frame store at `0x14135F1EC`. The scan cannot rule out indirect aliases or unprofiled replacements. Unexpected publication state needs separate evidence and yields indeterminate here. |
| Mixed +0x300 tree, keyed copy reader and type word | **Resolved, static.** | Constructor, lookup, advance, insertion and teardown support the profile above. The reader copies result storage to caller memory on a hit and exits false on miss. Detached stack copies cannot establish a current retained object. Calling the reader requires in-process execution and is outside this phase. |
| Other context or module routes | **Exhausted for this profile.** | `[0x1461E2288]` guards a different module state published at `0x140951916`, then the module explicitly obtains the focal context from +0x8B0 at `0x140951ABB–0x140951AC0`. The +0x268 tree uses a distinct key and shape. SRR-011 identified component registry and coverage operations there without a generated-slot join. The map built under `FUN_1407BC3D0` and downstream reader copies are transient consumers. These routes provide cross-checks but no simpler persistent slot source. [SRR-011 readers and reuse](SRR-011-planetary-allocation-execution-and-result-lifecycle.md#readers-and-reuse) |
| Typed forms versus raw FormID sequences | **Resolved, static.** | The native form map gives a second rooted identity join. The PNDT sweep's counted bucket is another way to authenticate PNDT only, using data handler `[0x145FD9B28]` at `0x14094EF50` and `FUN_140593280`. It has no result pointer and does not cover RSGD. Prefer bounded FormID lookups to walking all bucket entries. |
| Ordinary external query/read, no debugger | **Resolved for API feasibility. Blocked for retail access.** | A 64-bit observer can obtain process identity, creation time, mapped main-image base and bounds, then read selected ranges via `ReadProcessMemory` with `PROCESS_VM_READ`. If using `VirtualQueryEx` request `PROCESS_QUERY_INFORMATION` too. Authenticate the backing image hash and compare mapped AMD64 PE metadata and selected relocation-independent instruction windows before applying RVAs. Reject failed or partial reads and unknown mappings. Reverify identity against the same process handle after each collection. Target DACL/access behavior and actual checkpoint availability remain blocked until a separate live approval. [Windows process rights](https://learn.microsoft.com/en-us/windows/win32/procthread/process-security-and-access-rights) · [ReadProcessMemory](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-readprocessmemory) · [VirtualQueryEx](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualqueryex) |
| UI or disk data, process snapshots | **Excluded as simpler acquisition.** | Authored inputs, the reproducer and prior CK/retail observations can qualify selected identities and results but supply no checkpoint-specific root/layout witness. SRR-011 has no byte-level Save2 stream mapping for these result slots. OS virtual-address metadata contains no page contents. A VA clone would collect cloneable pages far outside the sample and still require the same exact storage decoder and scope review. [SRR-011 persistence](SRR-011-planetary-allocation-execution-and-result-lifecycle.md#invalidation-and-persistence) · [Windows snapshot flags](https://learn.microsoft.com/en-us/windows/win32/api/processsnapshot/ne-processsnapshot-pss_capture_flags) |
| Native activity witness and snapshot consistency | **Blocked for atomicity and lifetime continuity.** | The native path borrows live inline pointers. Insert and teardown can publish intermediate shapes. Clearing and filling slots are separate stores, including stores that leave the root and count equal. No inspected field is a write generation covering publication, traversal and all seven writes. The proposed bounded repeated observations qualify sampled state only. Proving a transactionally coherent snapshot would need a verified writer-wide synchronization boundary or a separately authorized acquisition method. |

An external reader should query only bounded regions required for those
joins. Obtain complete reads, collect source pointers, counts, keys,
slot bytes and form witnesses twice independently, and recheck the
root/discriminator/process witnesses around each collection. Compare
the selected graph including its terminating fences and full target
range. Bound retries and report unstable or partial evidence. A stable
double read can still land inside a paused native clear or miss a
change followed by restoration. Record a bracketed observation window,
availability and treatment of suspected transition states. This method
holds no native lock or lifetime reference.

## Offline reproduction

Use the tracked [PE decoder](../tools/srr011/inspect_pe.py) with Python
and Capstone (5.0.7 was used here). Set the local path to a lawful
matching image. The tool verifies SHA-256, PE machine, PE32+ and
preferred base on each run. It reads binary bytes and prints decoded
local windows to stdout. No Ghidra database is opened or modified.

```powershell
$retailImage = '<path to the pinned Starfield.exe>'
python tools/srr011/inspect_pe.py $retailImage functions 1423ff640 1423fdf50 1424059f0 1423fe320
python tools/srr011/inspect_pe.py $retailImage window 1418993be 38
python tools/srr011/inspect_pe.py $retailImage window 141882f32 23
python tools/srr011/inspect_pe.py $retailImage functions 14240a270 142404ef0 1424058b0
python tools/srr011/inspect_pe.py $retailImage functions 14231d000 140779610 14077bce0
python tools/srr011/inspect_pe.py $retailImage functions 140382700 140382800 1403832a0 140383570 1403833e0
python tools/srr011/inspect_pe.py $retailImage functions 1424103e0 140772620 1405f7a80 140771f30
python tools/srr011/inspect_pe.py $retailImage functions 1403835e0 140384200 1403842b0 140384410
python tools/srr011/inspect_pe.py $retailImage window 1405f7b10 114
python tools/srr011/inspect_pe.py $retailImage window 140771f98 88
python tools/srr011/inspect_pe.py $retailImage window 1403a4250 80
python tools/srr011/inspect_pe.py $retailImage functions 1407766b0 140773180 140773be0
python tools/srr011/inspect_pe.py $retailImage data 145ca7528 18
python tools/srr011/inspect_pe.py $retailImage data 145a18d30 68
python tools/srr011/inspect_pe.py $retailImage functions 1405de3b0 1405acad0
python tools/srr011/inspect_pe.py $retailImage window 14036bc60 99
python tools/srr011/inspect_pe.py $retailImage window 1405de3c8 80
python tools/srr011/inspect_pe.py $retailImage window 1405acafc b8
python tools/srr011/inspect_pe.py $retailImage scan 1482ee300 1482eebb0 1482eeb98 142403850 144b3d258
```

Selected exception ranges can split a function. In those cases the
explicit `window` starts follow validated native instruction
boundaries. The RIP-reference scan corroborates direct references
within decoded exception ranges. For the additional owner-store
search, prefilter .text for the little-endian 32-bit displacement
`0x8B0`, decode candidate exception ranges and inspect memory
operands marked as writes in ranges with a decoded direct
`FUN_1423FF640` call. Confirm the base register's provenance before
treating the write as a context store. This identified the two relevant
stores and the unrelated frame write in the lead table.
