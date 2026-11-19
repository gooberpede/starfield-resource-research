# Component database

Retail `BSComponentDB2::DB` retains resource IDs in indexed
`BSGalaxy::CTPerBiomeData` payloads. Generation borrows them and writes in
place; a separate keyed reader returns a caller-owned copy. The mixed +0x300
store, single-key +0x268 store, reverse-key +0x358 store, type registry and
independent FormID map have different identities and contracts. Presence,
nonzero output, eligibility and allocation completion are separate questions.

Unless marked as fixture or live observation, native claims below are
**PROVEN STATIC** on retail AMD64 `Starfield.exe` 1.16.244.0, preferred base
`0x140000000`, SHA-256
`7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28`.
Subtract the base from VAs for RVAs; relocate against authenticated image
base `M`. These are retail locators, not CK addresses. Behavioral labels
are research aliases. [Provenance](PROVENANCE.md) pins evidence domains;
[execution lifecycle](retail-execution-lifecycle.md) explains startup/reset,
and [allocation validation](allocation-validation.md) records title samples
and strict applicability limits.

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
[Complete rooted traversal](#complete-rooted-traversal)

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

## Operation catalogue

| Operation, native locators and evidence status | Inputs and admission | Effects, ownership and use in the investigated path |
| --- | --- | --- |
| Owner, context and registry — **PROVEN STATIC**. `FUN_1423FF640`, `FUN_1424059F0`, `FUN_14231D000`, `FUN_142404EF0`. | Lazy global owner is `0x1482EE300`. Its constructor zeros owner +0x8B0 at `0x1423FE0E9`. The context is embedded at owner +0x2C0. | Constructor installs the native DB vptr `0x144D6A6C0` at `0x142405AD1–AD8`. Context +0x268 and +0x300 each begin with an empty tree header. Owner +0x8B0 receives the context at `0x1418993E3` (RVA `0x82EEBB0`). Registration uses descriptor receiver +0x100 and sets the u16 discriminator at `0x1461DFA4C` through `0x14231D7D9–D7F1`. Use the registry witness to interpret this word. |
| Queue attachment and service — **PROVEN STATIC**. `FUN_1428D8130`, `FUN_1428D87A0`, `FUN_1428D96C0`, `FUN_1428D8FE0`, `FUN_1428D89B0`. | After publication, attach DB to the owner +0x40 receiver at `0x1418993F1`. The new-registration arm stores receiver at context +0x30 at `0x1428D8211`. The startup branch then configures a callable at `0x141899408`, subject to the helper's u16 state gate at `0x1428D87AB–87D2`. | The command buffer is the attachment receiver +0x40, which is owner +0x80. The callable pointer used by submitters is receiver +0x238 (owner +0x278). Publication, attachment, callback configuration and callback execution are separate steps. See [command order](#command-order-and-visibility). |
| Author inputs and submit — **PROVEN STATIC** for the input fields and callback, **PROVEN STATIC** for command publication. `FUN_14076EC00`, `FUN_14233F2C0`, `FUN_140773180`, `FUN_140773BE0`. | Successful PPBD and ENAM-associated replacements get planet and BIOM keys from PNDT +0x28 and input payload +0x40. CSV admitted rows proceed with the row's BIOM at `0x14234102B–103A`. | Input builders zero all seven u32 fields before submitting at `0x14076F360`, `0x14076FCEA` and `0x14234103A`. Zero stores are `0x14076EEED–EEF6`, `0x14076F853–F862`, and `0x142340535–053F`. `FUN_14076E720` copies the 0x70-byte typed value into the command. The command owns the copy and captures the context pointer. Submission publishes queue bytes at `0x140773223–3239` or `0x140773C83–3C99`. |
| Inline edge construction — **PROVEN STATIC** for insertion and copy, **PROVEN STATIC** for equality and storage movement. `FUN_140777290 → FUN_140774E00 → FUN_1407766B0`. | Callback takes the ticketed guard at `0x140774E1C`. Context +0x300 is selected at `0x1407766D6`. Empty root goes to `FUN_140382700`, nonempty to `FUN_140383010 → FUN_140382800`. | Native insertion reserves 0x90 bytes and increments the mixed edge count before typed initialization, including first-root publication at `0x1403827E3`. It writes wrapper vptr and both key words, then constructs inline payload at edge +0x20 at `0x140776791–67A4`. The decoded same-key path goes through insertion and constructs another edge. Page repacking/split can move existing payloads. |
| Notifications and reverse index — **PROVEN STATIC** for the notification, **PROVEN STATIC** for the separate queued key operation. `FUN_142406B70 → FUN_1424069F0 / FUN_14240F5F0`. | Insertion status byte at returned iterator +0x20 controls notification. The notification reads edge key at `0x142406BA5–BAE2`. | The reverse-key path rearranges owner, target and discriminator into a pair at `0x142406A53–AA6` and addresses context +0x358. Its conditional command captures key and DB at `0x142406ACF–AEF`, later `FUN_142417100 → FUN_142413190` re-enters mutation guarding and operates on that reverse index with the captured key. The immediate callback loop passes a key copy at `0x142406BE2–BE8` and dispatches slot +0x10 at `0x14240F659`. Neither bounded body transfers resource IDs to another store. Concrete registered callback targets for a given runtime epoch are open. |
| Keyed copy lookup and miss — **PROVEN STATIC** for storage and consumers, **PROVEN STATIC** for caller guard scope. `FUN_140771F30 → FUN_1405F7A80 / FUN_14076E810`. | Owner key zero, absent range or no matching BIOM yields false at `0x140771F8B` or `0x140771FFD`. Key geometry is below. The primitive receives caller-provided output in R9. It tests payload +0x40 against the requested BIOM at `0x140771FB6`. | The first match triggers copy assignment at `0x14077200D` and returns true. Read success can copy zeroed authored fields, and the miss path has no generator call. Three verified slot consumers hold shared-mode scope around the lookup. Later work uses their local copies. |
| Enumeration and result writes — **PROVEN STATIC** for storage and slots, **PROVEN STATIC** for guard span. `FUN_140779610 → FUN_140779760 → FUN_14077BCE0`. | Adapter uses the published context and takes shared mode before calling the orchestrator. Collector accepts an eligible nonzero PNDT key and ranges over the matching entries. `FUN_140777870` resolves payload +0x40 BIOM (type byte `0xA0`) and nonzero +0x4C RSGD (type `0xAB`) via FormID lookup. | Collector appends inline pointers at `0x14077BE39` without a per-edge owning reference. Orchestrator clears seven u32s at `0x140779AF5–9B2E` and attempts the category-6 and per-biome generation passes. Productive selection writes to the same borrowed payload. Scratch release leaves the retained values in the tree. |
| Independent FormID map — **PROVEN STATIC**. `FUN_1405DE3B0 → FUN_1405ACAD0`. | Accepts a runtime FormID and uses its own hash chain and native map state. `0x1407778F0–7923` resolves and checks the component input types. | Records carry keys. A key range/copy hit alone does not establish BIOM or RSGD form validity. Verified consumer `FUN_14086A6D0` independently resolves copied resource IDs and checks type `0x9F` at `0x14086A7F7–A80C`. |
| Typed +0x268 factory insert/update — **PROVEN STATIC**. Vtable `0x144D5F5C8` +0x28/+0x30 → `FUN_142322520`. | Uses a distinct qword key with discriminator in the high u16, entity in the middle u32, and namespace in the low u16. Receives an existing typed source. | Creates a stored-component wrapper and copies at `0x142322633`, or assigns to the existing payload at `0x142322664`. Both copy all seven fields as ordinary members. This operation's existence is established. An allocator-edge source alias or startup use for a computed-result mirror remains open. The allocator's verified +0x268 lookup at `0x140779CD7` uses the independent `BiomeData` discriminator `0x1461E1D90`; the coverage update is at payload +0x44. |
| Owner-range erase — **PROVEN STATIC** for triggers, **PROVEN STATIC** for guard and cursor behavior. `FUN_140772EE0 → FUN_140776680 → FUN_140774970 → FUN_142409490`. | Takes ticketed mutation guard at `0x14077498C`. Focal caller passes owner, PerBiomeData type, and range fences from `0x140774997–0x1407749BF`. End of range or first out-of-range key ends the loop. | Saves each key, erases the entry at `0x142409682`, then signals change at `0x142409691`. It resumes from the eraser's returned cursor at `0x142409696–96A0`. In the multi-entry case `0x1422CEC32` calls virtual destructor slot +0 before moving directory descriptors at `0x1422CEC6D`. Edge destructor `FUN_140777810` tears down the typed value at `0x140777823`. ENAM at `0x14076F751` submits owner-wide removal before submitting replacement inputs. PNDT lifetime sites `0x14076E9EA` and `0x14076EB83` also submit it. |
| Clear, shutdown and deregistration — **PROVEN STATIC** for the three boundaries, **PROVEN STATIC** for native guard and queue-stop ordering. `FUN_1424063B0`, `FUN_1423FE320`, `FUN_1424058B0`. | Reset's signed arm and an independent TES destructor path call guarded context clear. Shutdown takes a different path through `0x141882F3D`. The registry remove takes the registered type word address. | Clear takes ticketed mutation admission at `0x1424063CE` and clears +0x268 and +0x300 at `0x1424063DB` and `0x14240640C`. It can leave the context published. Shutdown runs queue stop `FUN_1428D88B0`, destroys indexes and releases the control object's reference at `0x1423FE3A7`, then zeros published slot at `0x141882F4E`. Registration teardown `0x14231DAFB → FUN_1424058B0` clears registry fields and type word separately. |

### Ownership and cursor lifetime

Read the relationships from the published slot outward. The dashed arrow
denotes a borrowed pointer or read.

```text
Process-global owner 0x1482EE300
  +0x8B0 published pointer -> embedded BSComponentDB2::DB at owner +0x2C0
     +0x30  ->  owner +0x40 queue attachment (commands capture DB + value/key)
     +0x238 ->  refcounted database control
     +0x268 ->  single-key component tree (separate typed values)
     +0x300 ->  mixed edge tree -> record block -> inline 0x90-byte edge
        edge +0x10/+0x18 key; edge +0x20 inline CTPerBiomeData
          payload +0x40 BIOM, +0x44 coverage, +0x48 seed, +0x4C RSGD
          payload +0x50..+0x68 seven u32 outputs
          ^-- collector's borrowed pointer -- allocation clears/writes here
          ^-- keyed reader -- copies value to caller-owned buffer
     +0x358 ->  separate reverse-key index

Insertion allowing page replacement can move live records.
Owner erase destroys matching inline values and advances a repaired cursor.
Context clear destroys index contents with the context address still available.
Shutdown stops queue service, destroys DB, then clears the published slot.
Registration has its own type-word and descriptor lifetime.
```

**PROVEN STATIC.** On an exact key, `0x14038304A–3066`
returns relation zero after the lower-bound comparison. The
typed inserter passes the relation into `FUN_140382800` with
no hit exit at `0x140776719–6734`. The path with room shifts
descriptors, reserves a new one at `0x140382894–28B0`, and
increments the mixed count at `0x140382FE0`. Repack and split
call `FUN_1422CEC90` at `0x14038295E` and `FUN_1422CEDB0`
at `0x140382B7D` and use the edge's virtual copy at slot +8
(`0x144B3D260 → FUN_1407777E0`; call at `0x1422CED31`
on the repack path). The old block's records are destroyed before the
block is recycled at `0x140382974–29A0` or
`0x140382F6E–2FA0`. The same logical key can therefore retain
an existing value at a new address after another insertion.
Native first-match lookup and the SRR-013 inspector's rejection of
ambiguous keys serve different purposes. Neither this path nor the
title samples establish whether duplicates occur during ordinary startup.

## Slot storage and copied consumers

Common occupies payload +0x50..+0x60 (five u32s), Special +0x64,
Everywhere +0x68. `FUN_14076E720` and `FUN_14076E810` copy all seven
fields at `0x14076E7D9–0x14076E7F2` and `0x14076E86A–0x14076E886`.
The work-pointer list, Common-family pointers and shared resource-ID array
are call-local scratch. Family pointers alias Common slots inside work
payloads; scratch cleanup leaves indexed payloads retained. A separate
retained planet-wide vector of the shared IDs is unestablished.

`FUN_140771F30` looks up the same +0x300 planet range through
`FUN_1405F7A80` at `0x140771F4F`. It scans for a matching BIOM key
at `0x140771FB6`. On a hit it calls `FUN_14076E810` at
`0x14077200D` to assign the component to caller-provided storage
and returns true. A zero planet key, missing range or unmatched BIOM
returns false at `0x140771F8B` or `0x140771FFD`. This is reuse of
stored data by lookup. The reader has no conditional generation on its
miss branch, and the batch writer clears and recomputes the fields without
testing for a retained result.

The hit path of `FUN_1407BA9B0` reads a selected slot at
`0x1407BAAF2` and uses a nonzero value in setting a caller byte at
`0x1407BAB12`. `FUN_1407BD270` tests all seven slots from index 6
to 0 at `0x1407BD701` while filtering its reference entries.
`FUN_14086A6D0` reads the slot range from its copy and resolves
selected IDs with `FUN_1405DE3B0`. These joins follow the actual stack
outputs passed in R9. In two inspected calls in `FUN_1413072A0` and
`FUN_141307BC0`, apparent matching positive RBP offsets instead
belong to a different frame region than the component passed in R9.
Those instructions do not establish a slot reader.

The [sibling input-provenance study][inputs] identified a temporary
root-to-array map under `FUN_1407BC300 → FUN_1407BC3D0`. This path
collects derived relationships from the same planet edge range
through `0x1407BC40D → FUN_1405F7A80`. The loop at
`0x1407BC480–0x1407BC666` stages the nonzero values from all
six slots following the Common root. A nonzero root selects the
map entry for a swap at `0x1407BC669–0x1407BC6FA`. The caller
`FUN_14079B520` supplies its temporary map at `0x14079B920` and
resolves IDs from it at `0x14079BC52–0x14079BC67`. This derives
per-request relationships from the stored slots.

The sweep immediately following each generation sweep is a useful control.
`FUN_14077B1D0` enters `FUN_14077A700`, which dispatches receiver
`0x144B3DA08` to `FUN_14077C450` via the same iterator. Its helper
`FUN_14077D090` walks the same per-planet range but collects payload
+0x40 at `0x14077D165–0x14077D174`. The caller resolves each collected
ID as a type-0xA0 BIOM at `0x14077A9D0–0x14077A9ED`. The later
job installation at `0x14077AFFA–0x14077B027` passes BIOM metadata
and a key using `word[0x1461E1DAC]`. The installed callback reaches
`FUN_14077D400` through `FUN_14077D800` and `FUN_14077D1C0`.
This path starts with BIOM identities. The separate final PNDT sweep
through `FUN_14077C4A0` branches at `0x14077C4A9` to `FUN_140778600`.
Its range query at `0x14077870C → 0x14077B92C` opens a different
edge discriminator `0x1461E1D9C` and copies 24 bytes per matched entry
at `0x14077BA3F–0x14077BA4D`.

## Command order and visibility

**PROVEN STATIC.** The submitter copies the model inputs before
exchanging the queue segment's +0x10 position and adding committed byte
count at segment +0xC. The typed command's +8 slot holds
`0x140777290` and the +0x98 qword is its DB receiver. Submission
checks and can invoke slot +0x10 of the attachment's notifier twice
(e.g. `0x14077323F–326B`). Each check permits a null notifier.

Construction zeros the owner's attachment +0x238 notifier at
`0x1428D871E`, and the configured path builds a callable whose vtable
`0x144DA7DB8` slot +0x10 is `0x1428D9600`. This tail-calls
`FUN_1428D96C0`, which sets/tests state bits around owner +0x296
at `0x1428D96CC–972A`. The callable gets the separate scheduler's
+0x40 receiver through `FUN_1428D1870` and dispatches
`FUN_1428D8FE0` at `0x1428D974A`. A matching scheduler
TLS record (its +0x88 equals that receiver) with mode dword +0xE0
equal to 1 can reach the direct call at `0x1428D926D`.
The other admitted path builds a scheduler command whose callback
`FUN_1428D9560` reaches the same service routine
`FUN_1428D89B0` later. Both paths service the captured original owner,
passing owner +0x40 to `FUN_1428D8060` at `0x1428D8A3E–8A49`.
Its bounded and draining variants acquire receiver-local state and use
`FUN_1422CE200` to consume available queue entries. The draining
variant calls each returned command's +8 slot at `0x1428D7C1B` until
the cursor yields no command. A null pop can also occur at its current
segment/cursor limit (`0x1422CE284–2CC`). This is queue service state.

**UNRESOLVED.** The positive ordering proves typed submission before
that command's callback/store and file-loader return before normal
module entry. The two routes alone do not join every selected PPBD,
ENAM or CSV command's return to its focal sweep. For the concrete
join candidates examined:

- `FUN_140472890`, reached near initial loader return and after reset
  re-entry, drains the independent image queue at `0x145E82940`
  (`0x1404728A3`, `0x1404728DE`). The direct drain therefore has
  a different queue identity from the authored command buffer.
- Before the later sweep, `0x14094EECC → FUN_1407873D0` uses shared
  mode at `0x140787417` and typed lookups with discriminators at
  `0x1461DD80C` and `0x1461DD830`. The adjacent PNDT callback
  with vptr `0x144B3EC50` selects slot +0x10
  (`FUN_140799490`) at `0x14094EEFD` through the type iterator.
  Its worker uses `FUN_140799690 → FUN_140799100 → FUN_140772030`,
  which opens the `0x1461E1D9C` range at `0x14077203D`.
- Reset's `0x14189753A–7541` services a separate queue attachment at
  reset receiver +0x200. State 1 reloads that receiver from
  `[0x145E71710]` at `0x14187FB94`; the direct mode route loads
  the same global at `0x14189603D`. The receiver comes from a
  separate 0x500-byte allocation constructed by `FUN_141881660` at
  `0x14189A69E` and published at `0x14189A6A8`. Its constructor
  selects receiver +0x200 at `0x141881776` and installs a
  different attachment at `0x141881A5A–A67`. The focal DB's
  attachment instead starts at image owner `0x1482EE300` +0x40.

These negatives cover the inspected direct operations and selected
virtual entry. The scheduler's thread/phase values, current queued
commands and any additional indirect rendezvous remain unobserved.
A qualified phase/timing join from original attachment and typed
command identity to the sweep would distinguish immediate execution,
resumed deferred work and pending work. For a collected record,
typed payload construction precedes the collector's use of that
payload. The per-edge relation supplies no finish time for the
insertion notification or the rest of the queue.

**PROVEN STATIC.** CSV's accepted-row branch at
`0x142341026–103F` submits the same insert callback as PPBD. The
separate ENAM owner-range erase has a direct call at `0x14076F751`.
The CSV submission helper has no corresponding edge erase in its
decoded body. Catalogued coverage lookups use `BiomeData` rather than
PerBiomeData. The only decoded direct stores to CSV callback globals
`0x145FC00C8/D0/D8` in the bounded scan are startup writes at
`0x141882006–201B`. That setup zeros the first two validation
hooks and assigns the last to `FUN_140777860`. The last callback
tail-dispatches receiver +0x1A0 if its argument is nonnull. This
argument comes from a second +0x268 lookup at `0x142340F79–FDC`
with `ProxyFormPtr` discriminator `0x1461DD81C` (registration
`0x14231D9AD–D9C5`, name at `0x144D5F188`). The hook runs after
buffer submission or disposal and receives neither edge cursor nor
output-slot arguments at `0x142341095–10C3`. Arbitrary computed
global writes remain unqualified.
The observed CSV insertion route supports providing new zeroed
inputs. Evidence of an actual replacement of an already indexed
edge would require a separate erase, assignment or callback join
with the same key.

**PROVEN STATIC.** The PNDT definition reader provides one concrete
proxy origin. At `0x14076EC33` it saves the form receiver in R12 and
at `0x140770C98–0x140770CB8` submits that pointer under its +0x54
planet key. `FUN_140773910` forwards the pointer and key at
`0x14077397F–0x14077398B`. The proxy helper captures the pointer at
`0x142346ABF` and the packed `ProxyFormPtr` key at `0x142346AC3`.
Command `FUN_1404775F0` calls the guarded apply routine
`FUN_1404768D0`, which stores the pointer in the +0x268 component at
`0x1404769B7` on insertion or `0x1404769D8` on assignment.
If that PNDT is the CSV lookup hit, its primary vtable
`0x144B3D638` slot +0x1A0 resolves to `FUN_1405DF5C0`.
The hook's DL = 1 at `0x1423410BE` then sets bit mask 2 in the
form's +0x20 flags at `0x1405DF636`. The method returns directly after
TLS cleanup. This conditional PNDT join supplies a specific alternate
effect for the hook. The runtime proxy population and effects of other
virtual targets remain open.

## Native synchronization and state transitions

**PROVEN STATIC.** Compare offsets from the refcounted control
object at context +0x238. Several helpers use control +0x10 as
their base. For example, helper +0x208 maps to control +0x218.

| Mode or transition | Native scope and limits |
| --- | --- |
| Per-thread shared admission | `FUN_142404230` gets the caller's thread record at `0x142404248`, increments local depth at `0x142404257`, and, on outer admission, adds 4 to shared state control +0x218. If the existing low phase bits require waiting, it loops at `0x1424042A3–2E6`. A nested admission skips the outer transition. |
| Writer and reader use the same shared mode | Adapter acquires at `0x1407796A6`, calls orchestrator at `0x1407796D2`, then unwinds read depth, completion-side counter at control +0x21C and control refcount at `0x1407796D8–9732`. Representative copy users have acquire/lookup/release sites `0x1407BAA5D / 7BAA7A / 7BAA8C`, `0x1407BD656 / 7BD677 / 7BD689`, and `0x14086A77B / 86A798 / 86A7AA`. `FUN_140771F30` itself contains no corresponding acquire. Shared holders can coexist at this level. |
| Ticketed mutation | `FUN_142404A80` retains the same control, takes a ticket using +0x228 and waits for serving +0x22C unless owner +0x240 matches the current caller. It sets owner and ticket word +0x23C at `0x142404B26–B33`. Insertion, erase, context clear and reverse-key application enter at `0x140774E1C`, `0x14077498C`, `0x1424063CE`, and `0x1424131AC`. Their outer exits reset owner and advance serving. |
| Page-token path | Many page accesses call `FUN_142404330`. It compares a per-page token at block −0x10 with control +0x23C. On a mismatch `FUN_142404090` checks writer ownership and handles phase/read counters before updating the page token. Its no-owner exit at `0x142404223` allows the shared-mode collector's call at `0x14077BDA0` to return without becoming the mutation owner. This admits a per-page synchronization operation. Token equality gives no witness for the separate allocator word stores. |

The operations below are conceptual transcriptions of the named paths.
Eligibility and allocator branch detail is in the [generation baseline](v1-research-baseline.md).

```text
submit_authored_row(planet_id, row):
    # Successful PPBD, ENAM-associated replacement or admitted CSV row
    zero_u32(row + 0x50 .. row + 0x68)    # input builder locators in catalogue
    command = copy_input_and_capture_db(planet_id, row)
    publish_command(command)             # 140773223..239 or 140773C83..C99
    if notify_callable_is_present():
        signal_service()                 # state gates admit inline or deferred service

run_insert_command(db, key, row):
    enter_ticketed_mode(db)
    cursor = insert_descriptor(db.index_300, key, 0x90)  # 140776719..741
    construct_wrapper_key_and_payload(cursor, key, row)  # 140776791..7A4
    notify_key_if_inserted(cursor)                      # 1407767C1
    exit_ticketed_mode(db)

write_one_planet(db, planet_key):
    enter_shared_mode(db)                    # 1407796A6
    work = collect_matching_inline_payloads(planet_key)
    clear_seven_slots_and_try_everywhere(work)  # 140779AF5..B2E, then selection
    for payload in the admitted work order:
        if input_resolution_and_selection_admit_writes(payload):
            write_selected_fields_in_place(payload)
    release_work_and_exit_shared_mode(db)    # 1407796D8 onward in adapter

read_one_biome(db, planet_key, biome_id, out):
    # Three traced callers enter/exit shared mode around this primitive.
    if planet_key == 0:
        return false
    for edge in the inclusive ordered planet/type range:
        if edge.payload.biome_id == biome_id:
            assign_payload(out, edge.payload)  # 14077200D
            return true
    return false

erase_biome_range(db, owner_and_type_fences):
    enter_ticketed_mode(db)
    cursor = lower_bound(owner_and_type_fences.first)
    while cursor.exists() and cursor.key <= owner_and_type_fences.last:
        key = cursor.key
        cursor = destroy_and_erase(cursor)   # 142409682, returns continuation
        report_key_change(key)               # 142409691
    exit_ticketed_mode(db)

clear_db_contents(db):
    enter_ticketed_mode(db)
    clear_focal_indexes_268_and_300(db)       # 1424063DB, 640C
    if qword[db + 0x358 + 0x10] != 0:        # 142406418..641C
        clear_reverse_key_index(db)          # 142406424, zero header through 6430
    ...                                     # additional context state
    exit_ticketed_mode(db)
```

The native decoder does not establish engine-wide scheduling between
every reader and writer. The scoped shared-mode evidence rules out treating
that admission as an exclusive transaction for the seven fields. The
external collector borrows no native guard, and repeat agreement
still qualifies only the bracketed observations. Mixed count changes on
insert/erase, while allocation modifies values in place. Treating the
refcount, ticket, page token, input-queue status or registry word as a
result completion indicator would confuse distinct native transitions.

## Key-change notifications and separate-store capability

On the pinned retail PE, `0x142406BD3` forms DB +0x38 and
`0x142406BDC–BE8` supplies the two key qwords in caller stack storage
to `FUN_14240F5F0`. The dispatcher reads its collection at receiver
+0x80 (`0x14240F602`), the per-entry callable at +0x28
(`0x14240F64A`), and invokes its vtable slot +0x10 at
`0x14240F659`. The DB constructor reaches `FUN_142412830` at
`0x142405A1C` with DB +0x38. This initializer installs
`0x144D6A540` and zeros the collection +0x80 at `0x142412894`.
The image vtable's +0x10 entry (`FUN_1407B3280`) clears storage
associated with receiver +8 when its +0x18 is populated. It is an
operation of the containing object. The runtime subscriber call at
`0x14240F659` instead obtains its vtable from the loaded callable.

The exact-target scan for `142406B70 14240F5F0` returned 110 decoded
references from 110 candidates in 236,427 selected exception ranges.
This includes both edge-insert calls at `0x1407767C1` and
`0x140777784`. The alternate nearby path at `0x140775D3F–D54`
also uses DB +0x38 and supplies a 16-byte key. The constructor scan
returned one decoded direct reference to `0x142412830`, at
`0x142405A1C`. The exact vtable scan flags `0x142412834` outside
the selected unwind ranges. Bounded window decoding recovers the
instruction beginning at `0x142412832`.

These checks cover direct rel32 and supported RIP-relative candidates in
file-backed .text and exact qword hits, plus the explicit windows. They
leave computed subscriber registration, concrete callback receivers and
indirect calls open. The separate +0x268 factory can copy all seven
fields from its typed source. A key-only callback, reverse-key command,
and the factory capability supply no same-key source-to-destination
join on their own. See the [cross-store lead](hypotheses.md).

## Save and lifetime boundaries

The copy path establishes in-memory reuse, not serialization. A lookup miss
returns false without generation. The writer clears slots without a retained-
result skip; no lookup-hit suppression link is demonstrated. Page movement,
removal and context clear invalidate borrowed storage; type deregistration
has its own metadata lifetime. An unchanged published address does not prove
that its payloads survived reset.

The primary PNDT vtable at `0x144B3D638` binds +0xD0/+0xD8 to
`FUN_1405DF980` and `FUN_1405DFA40`. The decoded direct save/changeform
handlers use identity and flag operations. Their optional PNDT
slot +0x230 getter resolves to a null-returning function. The
[sibling Save52 save-unit audit][saves] independently identified a different
discriminator in Global Unit 6. The clear prefix at `0x14182E2F2` and
first typed reader at `0x1424B5DCE` use `0x1461DD824`.
The function installed at vtable `0x144CAE268` slot +0x10 accesses
a context ID through the erased callback, as can be checked at
`0x14182F590`. These positive receiver and field distinctions
bound the evidence against a direct stored slot image in the
inspected routes. A complete save streaming or arbitrary external
callback search was outside the eligible native slice.


[inputs]: https://github.com/gooberpede/starfield-outpost-research/blob/e29b7507def041e25884e87222deea32b30d964d/docs/experiments/resource-retained-population/d5ad-input-provenance.md
[saves]: https://github.com/gooberpede/starfield-outpost-research/blob/b0b7f1b1c8bfb8d62658e0c3ca279d4f305eab5a/docs/experiments/resource-retained-population/d5ar-saved-components-proof.md

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

The BGSResource factory `0x1409E9B40` returns type `0x9F`; create
`0x1409E9BC0` calls constructor `0x1409E7440`, installing primary vptr
`0x144B6F0B0` at `0x1409E74E6` and type byte `0x9F` at `0x1409E75D9`.
Independent consumer checks are `0x14079BC52/0x14079BC63` and root sites
`0x14079B94A/0x14079B963`. Every nonzero lane needs one independently
rooted matching stored ID/type/vptr and a nonoverlapping object extent.
Claim the entire known FormID-table extent against aliasing even though
only required chains are read: unread buckets may contain convincing
object-shaped decoys. A zero vector still requires native owner/BIOM identity.

## FormID map capacity

The lookup slot at `0x145E60EA0` is independent of the retained component
tree. A decoded RIP-reference scan found 667 references, including the two
decoded direct stores below. It did not establish a global absence of
indirect aliases. AMD64 PE hash authentication precedes disassembly.

| Lead | Native evidence | Disposition |
| --- | --- | --- |
| Initial capacity | `FUN_1405DD4C0` gates first-owner initialization with the prior value from `lock xadd` at `0x1405DD567–0x1405DD573`. The call enters `FUN_1405DEA80`. The null-slot guard at `0x1405DEBA9` skips existing publication. The doubling loop reaches `0x40000` at `0x1405DEC0C`, saves capacity at object `+0x18` at `0x1405DEC16`, allocates `capacity × 0x18` bytes and publishes at `0x1405DEC9B`. | **PROVEN STATIC.** A newly allocated table begins at 262,144 entries. The 16,384 SRR-016 limit cannot admit that initialization. |
| Growth | The form construction path calls `FUN_1405E2B30` at `0x1405DD6EF`. The ID-changing path calls the same routine at `0x1405E1CE6`. Its insertion helper `FUN_1405E2C30` takes the growth branch when free entries at `+0x20` reach zero. Capacity doubles for large tables at `0x1405E2D7B`. `FUN_1405E3020` publishes the replacement table and capacity at `0x1405E308B` and `0x1405E3092`. The PE scan found one decoded direct caller of the resize function, at `0x1405E2D81`. | **PROVEN STATIC.** The initial capacity can grow. The inspected growth decision supplies no title-specific maximum. |
| Teardown | `FUN_1405DD800` calls `FUN_1405DEDC0` at `0x1405DD9C9`. The callee handles table cleanup then clears the root pointer at `0x1405DEE67`. | **PROVEN STATIC.** Pointer and extents belong inside each collection's revalidation. |
| Main-source population scale | Independent bounded traversal of each installed ESM's 24-byte record and group headers counted 3,829,247 physical records and 101,341 groups for `Starfield.esm`, and 1,029,529 physical records and 17,747 groups for `ShatteredSpace.esm`. Each contained one zero-ID TES4 header. Each file's remaining FormID words were distinct within that file. | **PROVEN disk counts.** The sum is 4,858,774 nonzero physical records before collapsing any cross-file overrides. It gives a scale for the doubling sequence under this two-file input. It leaves loaded extras, dynamically added forms, alternate form stores and actual title occupancy unresolved. |

The reader claims the table extent using the observed capacity with checked
arithmetic. It hashes each requested FormID into that extent and walks only
its validated chain.
The 8,388,608 bucket ceiling bounds a 192 MiB address claim. Acquisition
requests individual 20-byte occupied entries and the corresponding
validated form fields. This separation makes the capacity extension
independent of the aggregate read budget. The [census topology and native
identity rules](component-database.md) and the [independent FormID lookup
evidence](component-database.md) still
govern.

Static reproduction uses [the pinned PE decoder](../tools/srr011/inspect_pe.py)
with Capstone 5.0.7 and `$srrExe` set to the exact matching executable.

```powershell
python -E -B tools/srr011/inspect_pe.py $srrExe scan 145E60EA0 1405DEA80 1405DEDC0 1405E3020
python -E -B tools/srr011/inspect_pe.py $srrExe window 1405DEBA1 101
python -E -B tools/srr011/inspect_pe.py $srrExe functions 1405DD4C0 1405E18A0 1405E2B30 1405E2C30 1405E3020 1405DEDC0
```

For the physical record counts, start at each pinned source file's byte
zero and use its byte length as the outer closing fence. The SHA-256 pins
are `1dabed00c3f4282dd3bb54d2e9601e40b577d8742d078b7ccef203adbfef0da7`
for `Starfield.esm` and
`f8b9333000aba2a4a8a417cb74a11ede6f5b824d27db1918fd1c1f7b64385a43`
for `ShatteredSpace.esm`. Decode each header as `<4s5I`. For `GRUP`,
validate `start + 24 <= start + size <=
containing_end`, push that end and descend immediately after the header.
Otherwise validate `start + 24 + size <= containing_end`, increment the
record count, add the fourth unpacked field to the distinct FormID set if
nonzero and seek to the payload end. Pop fences on equality and refuse
overrun or a nesting depth beyond 32. This procedure skips payloads and
reads installed ESMs as files. It uses no save, installed process or
effective load-order assertion.

## Loaded namespace and defining identity

The current identity contract joins independently native-validated runtime
FormIDs to the paired loaded-plugin namespace: plugin basename plus local
record ID. Full/medium/small records retain 24/16/12 local bits. It requires
neither an open ESM nor a physical source manifest. Invalid or unassigned
slots, ambiguous names, conflicting assignments or native types refuse.
A relative `DATA\` directory or retired stream does not affect defining
identity. Winning content and optional source-history attribution remain
separate; they do not override a verified namespace and record type.

| Pinned retail site | Evidence |
| --- | --- |
| 0x140573774..0x14057378D | The null global leads to FUN_140592890 and data-handler pointer publication at image+0x5FD9B28. |
| 0x142011503..0x14201152B, FUN_14200A5A0 | Papyrus registration names the wrapper GetFormFromFile. It reads the data-handler global, calls FUN_140598430, rejects unmatched or unassigned files (TESFile+0x218=FF), rewrites the FormID, and tail-calls the independent FormID lookup FUN_1405DE3B0. |
| FUN_140598430 | Walks the embedded singly linked node at data handler +0x1570. Each node holds the TESFile pointer at +0 and successor at +8. The native name operand is TESFile +0x38. |
| FUN_1405994A0, FUN_14059FCF0 | The traversal at 0x140599680 assigns files with native flag bit 2 set. Bit 3 defers one file via data handler +0x1568. Assignment sites are 0x1405996AE and 0x14059975B. Reset and startup callers are 0x141897B19 and 0x141883DC9. The three array writers are FUN_14058D880, FUN_14058D8D0 and FUN_14058D930. |
| FUN_1405B78C0 | TESFile flags at +0x1B8 select full, medium (bit 10) or small (bit 8). The routine keeps 24, 16 or 12 local bits and uses +0x218 for the high byte, +0x219 for the medium index and +0x21A for the small index. Bit 9 takes a distinct update-file path through +0x1D8. |
| 0x14058E577..0x14058E64C | On the FormID diagnostic's absent-result path, the high byte chooses full, FD medium, FE small or FF runtime-created. Full uses data handler +0x1580/+0x1588, small +0x1590/+0x1598, medium +0x15A0/+0x15A8. Each accessor checks index against the count and the array result against null before reading the file name. Native writers read capacity at header +4. |
| 0x14058E453..0x14058E508 | The diagnostic's successful lookup path reads a u16 source index from TESForm +0x30 with FFFF sentinel. The table count is at image+0x5E881E8 and pointer at image+0x5E881F0. Indexed bucket +0 points to TESFile pointers, +8 holds u32 length. The diagnostic prints source names in order. |
| FUN_1405E0D50, FUN_1405E3980, FUN_1405DC730 | The writer canonicalizes through TESFile +0x18 and can filter non-master history before supplying TESForm +0x30 at 0x1405E0EB6. It then interns the list and stores its index. The append path preserves prior order and adds the supplied file unless already present. Matching and append are at 0x1405DC7A3..0x1405DC7D7 and 0x1405DC851..0x1405DC883. The loader region FUN_14059E000 calls the writer at 0x14059E280. |

The arrays establish the runtime slot for the defining plugin. The ordered
source vector independently describes native file attribution for a resolved
form. The writer can filter prior non-master contributors. Registration's
deferred branch and the vector filter prevent treating either list as
universal proof of winning bytes.

CommonLibSF Address Library 1.16.244.0 ID `825890` resolves to service
slot `0x145912E10`, with registered vptr at `0x14395A8DB`, rather than the
loaded collection. The independent native getter and constructor identify
the loader data-handler global. A runtime prefix does not universally equal
the on-disk high byte. [Upstream identifier](https://github.com/Starfield-Reverse-Engineering/CommonLibSF/blob/main/include/RE/IDs.h)

### Optional physical backing and source attribution

Physical ESM backing provenance is **SUPERSEDED as an extraction gate**.
These native locators retain static value for source-applicability research.
Relative `DATA\` plus a matching installation basename/hash does not prove
which VFS provider supplied earlier bytes. Closed streams are ordinary
native behavior. Registry order and the last diagnostic source are not
universal winner witnesses because registration can defer files and history
can filter contributors.

| Pinned instruction or typed location | Evidence |
| --- | --- |
| `0x140573968..0x14057396F`, `0x140597319..0x140597350`, `0x1405973FA`, `0x140597C86` | Startup submits the handler to `FUN_1405972B0`. The first scan builds `DATA\\` and can construct a packed source with that relative directory. The later scan at `0x140597971` supplies a separate directory from the `%sdata/` formatter. |
| `0x144B29B80` and `0x1405B694C..0x1405B6966` | RTTI identifies the packed file vtable. Header load dispatches slot `+0x18` if the file fails the already-open check. Its destination `0x1405B5BE0` passes directory `+0x268` and basename `+0x38` to `FUN_1405B9950`. |
| `0x1405B99D8..0x1405B9A0B`, `0x1405B9F52..0x1405B9F7F` | The open routine retains both 260-byte buffers, joins them, and distinguishes the direct path by a leading slash or a colon. The observer admits an ordinary absolute local drive pathname, excluding ambiguous roots and Windows device paths. |
| `0x1405B9FB2..0x1405B9FD3`, `FUN_1427D8950`, `FUN_1427D7FA0` | Relative opens use `LocationTree` (`0x144D9C578`) with the object at image `+0x61FAB68`. The wrapper delegates at `+0x30`. `GlobalLocations` (`0x144D9C498`) iterates ordered location nodes at object `+0x28`. Each node's first qword links the successor and its next qword supplies the provider. Dispatch stops on the first zero result. |
| `0x1427D95DD..0x1427D9692`, `FUN_1427F6810`, `0x1427FB1A0` | The default setup installs multiple location holders. The loose-file provider (`0x144D9D0B8`) returns its selected prefix from the object at `+0x10`. The object graph has candidate roots and ordering, with no per-plugin record of which provider succeeded at startup. |
| `0x1405BA022..0x1405BA053`, `0x1405BA126..0x1405BA13C`, `0x1428E4340..0x1428E4360` | A successful provider can contribute the effective backing prefix before the packed file constructs a `BSFile`. The live pointer is at packed file `+0x378` and its typed vtable is `0x144DA7FB8`. The constructor copies the resulting filename to `BSFile +0x6C`. The caller tests open state `+0x4C` at `0x1405BA1EE`. |
| `0x140597C98`, `0x1405B6890`, `0x1405BA859..0x1405BA86D` | The registry walk can retire the packed stream through the file close virtual method. The native close disposes of the open-file object and clears `+0x378`. The populated directory field can survive that close. |


### Independent disk controls

These are bounded disk-header observations and counterfactual remap controls,
not witnesses of historical effective winning inputs.

| File | SHA-256 | PNDT / BIOM / RSGD / IRES |
| --- | --- | ---: |
| Starfield.esm | 1dabed00c3f4282dd3bb54d2e9601e40b577d8742d078b7ccef203adbfef0da7 | 1,765 / 431 / 32 / 332 |
| ShatteredSpace.esm | f8b9333000aba2a4a8a417cb74a11ede6f5b824d27db1918fd1c1f7b64385a43 | 11 / 3 / 0 / 0 |

The base file has no MAST. The DLC's sole MAST is Starfield.esm.
The base records include runtime-observed Kreet PNDT 0003F59F,
BIOM 000D9BAC and IRES 000057EA. A typed disk example for RSGD is
000083D8. The four previously observed SRR-013 sample prefixes agree with
the base file-local prefix 00. DLC PNDT 01000801 and BIOM 01012244
define shatteredspace.esm:000801 and shatteredspace.esm:012244. Their
retail runtime prefix was unobserved in that earlier disk-only phase.
The later SRR-017 pair measured runtime `01000801` and `01012244` under
the paired defining namespace. The separate `0x11` example below remains
counterfactual. [Observation scope](allocation-validation.md)

The 39 installed Data candidates include full IRES 01033E3F in
sfbgs00d.esm, base PNDT overrides, and medium definitions FD002810 in
sfbgs003.esm, FD006D06 in sfbgs00b.esm, FD0113AB in sfta03.esm and
FD0196AB in sfta06.esm. Both SFTA files list one medium MAST before their
own records. A counterfactual topological sort over all inspected files
using lexically sorted filenames on each pass admitted 2,586 canonical
definitions across the four signatures. Its assigned full slot 5 made
05000801 the DLC PNDT runtime word. The disk word would select
BlueprintShips-Starfield.esm in that counterfactual. Disk counts describe
source coverage. [Independent file-relative format experiments](https://github.com/Ortham/esplugin/issues/42)

The 39-file typed-header manifest canonical SHA-256 was
`b08681ada86d1fbda7e3b801f93dd01d420b5e062adaaa674036fc2fba5f5cef`.
The independently scanned base/DLC files held 1,457,098,709 and 501,394,621
bytes; two-file typed-manifest hash
`a17f7176b9090fb728efbfc37cc105397378904cdce2d38ef5f848434e5d7777`.
A **COUNTERFACTUAL** DLC full slot `0x11` resolves `11000801` and `11012244`
to `shatteredspace.esm:000801` and `shatteredspace.esm:012244`, preserving
the disk words `01000801/01012244`. These controls demonstrate remapping;
they do not attest that slot in retail.

## Complete rooted traversal

```text
authenticated AMD64 process epoch and source
    published context → mixed header +0x300
                             ├─ null root and zero count
                             ├─ direct packed block
                             └─ branch levels → leaf directories
                                                    │   ↔ previous / next leaf
                                                    └─ ordered packed blocks
                                                        └─ descriptor positions
                                                          └─ prefix + inline payload
    type registration → target discriminator and wrapper check ─────┘
    independent native FormID map → PNDT, BIOM, RSGD, resource witnesses
    independent ID manifest → canonical PNDT/BIOM pair and seven lanes
```

The arrows represent navigation and validation dependencies. They carry no
claim about startup order or the writer's execution. Each target's inline
payload lies in its packed block. The looked-up forms are separate allocations.
Extent claims cover the complete tree windows, context, registration metadata,
FormID table, consumed form extents and BIOM pointer lists. No block, leaf
or branch window can occupy a second root-derived position.

```text
read authenticated publication, registry, mixed header and FormID map
require root/count consistency and admit the independent limits
if root is a packed block, visit it as the entire tree
otherwise walk every used root-derived child position in ascending order:
    require level decrement and separator order
    require routing pivots/block minima within inclusive ancestor bounds
    at a leaf, cross-check both directions of the root-derived leaf adjacency
    for every block position, validate layout and exact advertised minimum
at every block:
    validate descriptor directory/frontier and disjoint occupied spans
    reconcile free holes with occupancy credit
    visit each record in directory order and require increasing global keys
    test registered discriminator and exact wrapper in both directions
    classify a non-target prefix or validate the entire typed target
require null terminal leaf link and exact mixed/target/exclusion counts
independently reconstruct canonical ordering from privately retained raw keys
re-read consumed windows and anchors, then close process/image bracket
```

The geometry comes from the pinned retail lower bound
`FUN_1403832A0`, block selection `FUN_1403833E0`, cursor continuation
`FUN_1424103E0` and record advance `FUN_1403A4250`. The external traversal
enumerates every child instead of calling the keyed reader. On a finite
admitted graph, every edge has a single root-derived descriptor position.
At each node the child array bounds this induction. Leaf links and header
count provide independent reconciliation. The cursor's terminal +0xFE0
denotes an exclusive block boundary. No descriptor or payload starts there.
[Exact mixed-index model](#exact-mixed-index-model)

The corrected routing contract above is also applied by the whole-store
reader. Every node pivot and block minimum satisfies inclusive ancestor
bounds; every actual record satisfies strict global order, including
cross-page adjacency. The final record in a block need not be below an
ancestor pivot. Fixture interior pivots and endpoint equalities test the
external navigation contract; only the promoted-last-left-minimum writer
shape is established statically. Selected-key range completeness and
whole-store census completeness are different qualifications.

A typed target requires both discriminator and wrapper agreement, exact
0x90-byte extent, owner high-u32 mapped to PNDT, and the second key u64
matching the nonzero payload BIOM u32. A disagreeing or blank prefix stops
the walk; other mixed entries get exclusion classification without an
invented semantic type. Free holes contribute occupancy credit and no
descriptor positions. Every root-derived position is unique; cycles,
shared children, descriptor overlap, corrupted minima or count mismatch
refuse. Optional RSGD failure is distinct from unreadable map/chain state.
The external chain checker continues through termination, validating decoy
headers, duplicate keys, aliases and successor bounds; merely finding a
first matching form is insufficient for its scientific identity contract.

Two fresh complete collections independently authenticate publication,
registry, roots, native FormID/namespace witnesses and typed inputs. Each
rechecks consumed windows and closes its process/image epoch bracket.
Graph and input digests are separate from exact seven-lane agreement.
If graphs agree and lanes differ, graph coverage can qualify while values
remain indeterminate. Every refusal preserves its readable diagnostic
prefix and attempted target; successful prefixes from separate attempts
are never combined. Rooted absence concerns only the admitted graph,
not pending commands, orphans, other stores or all-galaxy eligibility.

Endpoint agreement permits ABA, stable intermediate clears and non-atomic
publisher behavior. The external observer acquires no native guard or
lifetime reference. No inspected counter, token or registry field spans
publication, tree mutation and all seven allocator stores as a write
generation. Native copy calls require game ABI/TLS/object/page state and
are not a simpler external read-only export. Current finite bounds and
operator commands are in [the extraction guide](../tools/srr017/README.md).
Historical selected-reader and census qualification stays labeled in the
[tool catalogue](../tools/README.md).

## Offline reproduction

Use CPython 3.14.3 x64 and Capstone 5.0.7 with a lawful matching PE.
The tracked decoder verifies image identity, reads disk bytes and prints
bounded disassembly; it does not open a process or modify Ghidra.

```powershell
$image = '<path to the pinned Starfield.exe>'
python -B tools/srr011/inspect_pe.py $image functions 1423FF640 1424059F0 14231D000 142404EF0 1424058B0
python -B tools/srr011/inspect_pe.py $image functions 1403832A0 1403833E0 1403835E0 140384200 140384410 1424103E0
python -B tools/srr011/inspect_pe.py $image window 1403A4250 80
python -B tools/srr011/inspect_pe.py $image functions 140773180 140773BE0 140774E00 1407766B0 140383010 140382800 142409490
python -B tools/srr011/inspect_pe.py $image functions 142404230 142404A80 142404090 142404330 1424063B0 142322520
python -B tools/srr011/inspect_pe.py $image functions 1428D96C0 1428D8FE0 1428D8060 1428D7BD0 1428D89B0 1422CE200
python -B tools/srr011/inspect_pe.py $image functions 1405DE3B0 1405ACAD0 1405DEA80 1405E2C30 1405E3020 1405DEDC0
python -B tools/srr011/inspect_pe.py $image functions 1409E7440 1409E9B40 1409E9BC0
python -B tools/srr011/inspect_pe.py $image window 142406B70 8B
python -B tools/srr011/inspect_pe.py $image functions 14240F5F0 142412830 1407B3280
python -B -m tools.srr017.probe_namespace $image
python -B -m tools.srr017.source --manifest $newPrivateManifest @plugins
python -E -B -m unittest -v tools.srr017.test_native_identity
python -B -m unittest -v tools.srr017.test_source
```

For the source-header command, set `@plugins` to explicit lawful `.esm`,
`.esp` and `.esl` paths and `$newPrivateManifest` to a fresh private output.
It hashes each file and scans PNDT/BIOM/RSGD/IRES headers, writing a manifest
of filename, digest, size, flags, ordered MAST names and typed headers.
`probe_namespace` checks the pinned PE and prints native windows, callers
and RTTI without writing source data. Unit controls construct independent
synthetic namespaces/headers; they do not attest retail effective inputs.

Native scans use the bounded [decoder scope](retail-execution-lifecycle.md#static-search-and-reproduction),
which cannot exclude arbitrary computed references. The +0x8B0 owner-store
search checked write operands in exception ranges containing a direct
`FUN_1423FF640` call; it identified publication/disposal and excluded unrelated
frame store `0x14135F1EC`. Notification direct scans found 110 decoded
references for `142406B70/14240F5F0`; constructor scan found `0x142405A1C`.
These are scoped counts, not universal subscriber enumeration. Evidence
for a specific computed mirror needs a concrete subscriber and same-key
source/destination slot join. This uncertainty remains in the
[sole lead register](hypotheses.md).
