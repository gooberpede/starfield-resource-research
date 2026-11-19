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

## Resource membership, player knowledge and the Locations page

**PROVEN, retail static** on the [pinned 1.16.244.0 image](PROVENANCE.md#current-retail-identity).
Addresses are preferred-image VAs. This graph describes reachable instructions.
The title-card measurements establish populated allocation edges. The supplied
Locations captures establish displayed values in a different, unidentified
gameplay epoch. Neither observation measures these instructions executing.

| Source → operation | Destination and decisive observation |
| --- | --- |
| Copied biome result → resource selection | `FUN_14086A6D0` passes a stack destination at `0x14086A78B–A798`, resolves nonzero copied IDs, checks type 0x9F and appends form pointers. Via `FUN_14086A530`, `FUN_140868B30` filters candidates, selects one and reads form+0xF0 at `0x140868E8A–E98`. This branch ends at selection. A different installed reader at `0x1409518D8` supplies an ID and a byte to the packed-value consumer at `0x14234C9C3–CA63`. Neither branch identifies a Locations row. |
| Borrowed +0x300 biome edge and separate atmosphere modifier → body snapshot | `FUN_1417D6520` records the body ID at +0x1C8 and calls population and summarization at `0x1417D67B2/7BA`. `FUN_1417D8D40` resolves the body's atmosphere modifier (type 0xAD or fallback) and enumerates typed biome edges. Inside the edge callback, `0x1417D6BC5–6C2E` appends the modifier's pointer list to snapshot+0x1D0. The nested body range reads edge+0x70…+0x88 and resolves collected IDs into +0x1E8 at `0x1417D7455–7499`. Both operations depend on reaching the outer callback. `0x1417D6868–6923` normalizes the spans and removes overlap from +0x1D0. An unresolved or wrong-type slot ID can yield a null pointer. |
| Named body queries → stored `BSGalaxy::PlayerKnowledge` | Registration at `0x14231D9D4–D9EC` binds the type word. The stored-component lookup uses DB+0x268 with key `(type << 48) \| (bodyID << 16)` in 64-bit arithmetic. GetPlanetVisited passes bit 1 to `FUN_1407B65D0`. IsCelestialBodyScanned tests `FUN_1407BA290(body) != -1`. A miss returns −1, bit 0 forces level 4, otherwise the result is the stored signed level. At `0x141A373D1–3D9` and `0x142108A6F–A77` the callers request bit 1 set through `FUN_1407B6710` (bit operations at `0x1407B6CB0/B6`). The first caller is a PlayerCharacter virtual method (vtable slot +0x860, entry at `0x144CBCCA8` → `FUN_141A37140`). Their timing relative to landing and disembarking is unverified. No actor ID appears in this key. Body-list inclusion has a further predicate/bypass check at `0x141360BD5–BE5`. |
| Scanner/gather path → body and item → knowledge mutation | Reason 7 (HandScannerResourceScanned) at `0x1415996DA–9708` passes a nonzero form ID and a global receiver to `FUN_1407B75B0`. After outer/nested type checks and a type-0x9F item check, the reason-6 (ItemGathered) call at `0x1407B8467–8476` reaches the same helper. It resolves body context and submits a body/ID/delta operation. On a lookup hit `FUN_1407B77D0` updates or inserts an item and derives another capped byte via `FUN_1423464E0/142346630`. This qualifies a mutation route, with no guarantee that every scan or harvest reaches it. |
| Body visit bit and item progress → resource count | `FUN_1417D7EB0` tests the same component. Bit 1 credits the **entire remaining atmospheric span**. Each nonnull +0x1E8 form credits one when lookup by form+0x28 finds an entry with byte +0x21 above zero (`0x1417D8049–80C5`). `0x1417D7887–78DA` writes the zero-extended byte accumulator to snapshot+0xC4 and the sum of both span lengths to +0xC8. Length includes slots that fail the numerator test. Atmospheric credit here requires no per-item mutation. Overall survey fraction at +0x1CC has separate cross-category arithmetic at `0x1417D7E67–7E95`. |
| Snapshot and knowledge → selected body's resource rows | Locations constructs the body detail at `0x14135F108` (snapshot nested at +0x188), then calls `FUN_1416CF0F0`. Its tail call supplies the equality of two resolved keys (`0x1416CF169–F1AB`). `0x1416D04E0–0527` passes that flag to the row builder and moves the resulting vector into detail+0x168. `FUN_1416D0EF0` requires a knowledge lookup hit and either effective scan level != −1 or the supplied flag. Missing knowledge yields empty native rows even with the flag. This bounds disclosure at the producer. The page handles the resulting empty array below. The gameplay action that first opens the native gate remains untraced. |
| Two spans → separately computed row fields → named Locations provider | `0x1416D1083–111A` walks detail+0x358 and +0x370 (snapshot+0x1D0 and +0x1E8). The former supplies the visit result, the latter the item-byte predicate. `FUN_1416D1510` gates on insertion by FormID, builds name and symbol, packs three color channels, inverts the knowledge argument for row+0x25, and computes +0x26 from scan state and form+0x110. It groups 0x28-byte records by that form byte. `0x1416D14A0–14CA` inserts seven groups in index order, using the output beginning for groups 5 and 6 and the end for earlier groups. This is native ordering before rendering. |
| Native row → UI field contract | `LocationsBodyInfoData` is registered at `0x14135DE6C–DE81`. The body binder names `ResourcesA`, `iScanLevel`, `bPlayerVisited` and `fSurveyPercent` (`FUN_14135D570`). `0x14135FD0D` calls the common binder. Its resize path and indexed setter at `0x1416B6A24/6A7D` connect to the row schema via `0x1413685BA/85CA` and `0x14136B661/6970C`. `FUN_1416B6180` sets name, symbol, packed color, rarity, disabled, show-color and tagged fields in the order named at `0x14136CFE6–D074`. Thus `bDisabled` and `bShowColor` have different inputs. The latter compares resource class with a scan-level-derived threshold, with explicit special classes 5/6 (`0x1416D1967–19BD`). Neither field identifies final pixel brightness by itself. |

### How Locations gets its resource counter

**PROVEN, static on the pinned executable and interface archive.** The scanner
uses the snapshot scalars. Locations computes its fraction from the selected
body’s resource rows. The paths agree under ordinary conditions, but their
identity rules, widths and disclosure limits differ.

| Stage | Operation and evidence |
| --- | --- |
| Normalize membership | At `0x1417D686B/6873`, each span passes through `FUN_1417D8560`. It sorts qword pointer values, compacts equal neighbors and erases the surviving null (`0x1417D85A7–8646`). The cross-span loop compares pointers at `0x1417D68A0/68E0`, writes survivors to atmosphere at `0x1417D68EE` and updates its end at `0x1417D691C`. A shared pointer survives once in the biome span and requires positive item progress for credit. Failed resolutions and repeated slots do not inflate the normal maximum. |
| Count | On a knowledge hit, `0x1417D8049–80C5` adds visited atmospheric entries and increments for each positive terrestrial item. Current accumulates in an unsigned byte without saturation, then zero-extends. Maximum sums normalized pointer counts in 32 bits. Eight resources cannot wrap the byte. |
| Scanner | `FUN_14159FEB0` installs a snapshot pointer at `0x14159FF6A`. `FUN_1415A01D0` obtains the Monocle menu model through virtual +0x58. At `0x1415A0506–0591` it reads +0xC4/+0xC8, updates changed dwords in wrappers +0xE0/+0x100 and dispatches virtual +0x48. `FUN_141597330` registers these as `uResourcesCurrent/Max`. |
| Locations transport | Detail construction directly calls the snapshot builder at `0x1416CD560`. `0x14135F35B–F366` moves the projected detail. `0x141360436/0x14136043E` copies a block covering both counts to detail+0x24C/+0x250, while the row vector travels at +0x168. `FUN_141369B80` queues callback `FUN_14136DC40` and the moved packet. On owner resolution the callback calls `FUN_14135FCC0`, whose virtual +0x58 lookup and direct bind at `0x14135FD0D` supply the display model. |
| Locations schema | The 34-field enumerator `FUN_14135D570` names paired flora, fauna and trait counts. Its resource field at `0x14135D818` is `ResourcesA`. The array resize and indexed row setters above supply its contents. The survey meter separately receives `fSurveyPercent` from detail+0x24, originating at snapshot+0x1CC. |

The row helper inserts by **u32 FormID** (form+0x28, `0x1416D153A–1555`),
atmosphere first. Distinct pointers carrying the same FormID would survive
pointer normalization but compete for a single row. Row order by class is
6, 5, 0, 1, 2, 3, 4. The packed RGB comes from the form triplet at +0xE0 or
a class fallback when all three converted low bytes are zero
(`0x1409E7890–78FB`, packing at `0x1416D1907–194A`). An effective level
of −1 clears `bShowColor` even if the key-equality override discloses the list.
Otherwise classes 5 and 6 always qualify, and other classes qualify at or
below the threshold. Stored levels 0…4 map to themselves, unexpected stored
values default to threshold zero, and mask bit 0 forces level 4
(`0x1416D1967–19BD`, table `0x1416D1C30`). The independent `bDisabled`
is the inverse of the visit or positive-item predicate appropriate to that row.

**PROVEN, interface bytecode.** Both [pinned Locations layouts](PROVENANCE.md#locations-interface-input)
subscribe `LocationsPage.onBodyInfoUpdate` to `LocationsBodyInfoData`.
The callback passes event data to the body card. Its `AlmanacBodyDataInfo.SetBodyInfo`
passes `ResourcesA` and `iScanLevel` to `UpdateResourceInfo`. The override calls
the base `BodyDataInfo.UpdateResourceInfo`. Its actual counter rules are:

- With a nonempty array, **y** is its full length. **x** starts at zero. For
  each available icon position with a nonnull row, `SetResource` runs and
  `!row.bDisabled` increments x. The method formats `(x/y)` and calls
  `GlobalFunc.SetText` on `ResourcesAmount_mc.text_tf`. Each shipped layout
  defines eight row slots, and initialization stops at the first missing icon
  or the limit of eight. A ninth supplied row would affect y only.
- With an empty array, scan level ≥ `SL_MINIMAL` (0) selects `$NONE`;
  a lower level selects `$UNKNOWN`. This distinguishes a hidden list from
  a displayed zero numerator. A missing amount clip skips the text write.
- `PlanetInfoResourceIcon.SetResource` uses `bShowColor` to choose the
  background color transform (packed `uColor` or `0x394253`), `bDisabled`
  to select the icon’s **Unknown/Known** timeline frame, `uRarity + 1` to
  select its rarity frame, and `bTagged` for tag visibility. In the imported
  PlanetInfoCard symbol the Unknown background placement has zero alpha
  multiplier and Known restores the default transform. These are authored
  frame states; the applied transform, compositing and screenshot pixels are
  separate observations. The full name is a **sibling text field**: the
  Almanac override sets it from the icon’s stored `sName` for each visible
  parent. Its name assignment has no disabled/color branch. Counting apparently
  bright full names cannot recover x.

For an open gate, one canonical form pointer per FormID, all rows fitting the
card and consistent knowledge across reads, both routes count the same credited
resources. This explains agreement without a scalar-to-text binding. Another
method in the same movie, `GetInorganicsText`, mentions inorganic scalar
fields. The selected Almanac override above calls `UpdateResourceInfo`
for this label. The [matched cases and proposed tests](hypotheses.md#locations-and-survey-observations)
separate this asset behavior from claims about a particular capture.

The `ScanningPowerLevelAV` default object is named at `0x14005215F`.
`FUN_14168AF80` reads its resolved pointer, obtains a float via the receiver
at [0x145F43230]+0x70, truncates and clamps the result to 0…4 (null gives 0).
Only an increase over the effective level reaches `FUN_1407BA3A0` and the
hit-path payload+4 write at `0x1407BA8C6–A8CE`. The StarMap BodyInspectState vtable at `0x144C941C0` points at
`FUN_141680910` in slot +0x10, which calls this path at `0x141680A7C`.
The named StarMapMenu_ScanPlanet binding at `0x1416BFCAE–FCE9` alone does
not identify the dispatch into that slot. The actor-value path supplies a stored level
used in presentation. The chain from a particular perk rank or orbital input
to an individual resource write remains unresolved.

### Resource displays across interfaces

**PROVEN, retail static and installed UI bytecode.** The three interfaces
start from the body resource snapshot. They diverge where they choose a body,
build display rows and decide what earns color. All VAs below belong to the
[pinned retail executable](PROVENANCE.md#current-retail-identity). The
[movie identities and method indexes](PROVENANCE.md#scanner-and-starmap-interface-inputs)
qualify the UI findings independently of the gameplay captures.

| Display | Which items, and in what order? | What supplies x/y? | Appearance, target and missing state |
| --- | --- | --- | --- |
| Locations body card | Selected body's normalized spans. Knowledge lookup must succeed and either effective level differs from −1 or the two resolved body keys compare equal. FormID deduplication admits atmosphere first. Groups appear in class order 6, 5, 0, 1, 2, 3, 4. | Non-disabled nonnull rows within the eight icon positions / full supplied array length. Atmospheric rows use visit bit 1, terrestrial rows use positive item progress. | Level/class selects color eligibility. Disabled selects the icon frame. Full names use sibling text fields. Empty rows display UNKNOWN below level 0, otherwise NONE. No scanner target is an input to this counter. |
| Handheld survey line and expanded resource wheel | Current snapshot. Wheel walks normalized biome pointers first, atmosphere second, skipping nulls. Five native arrays group rows by class, preserving insertion order within each. No second FormID deduplication in this append path. | Survey line formats the two snapshot scalars regardless of how many wheel slots are occupied. Bit 1 credits residual atmosphere, terrestrial credit requires positive item progress. | Wheel uses its own disabled predicate below. The SHOW RESOURCES control displays the resource arc. Picked-object data drives the large target tile separately. Missing wheel positions do not produce a card-style UNKNOWN counter. |
| Orbital/starmap body card | Body-inspect selection goes through the same detail builder, knowledge gate, FormID deduplication, class groups and row binder as Locations. The equality override depends on the keys resolved for this selection. | Its own movie counts non-disabled rows in up to eight slots / supplied array length. Its survey meter reads the separate aggregate fraction. | Same level/class color, disabled frame, rarity and tag rules as Locations. Empty rows select NONE/UNKNOWN by effective level. Map hover data has its own one-row nameplate. Selecting a landing site provides no evidence of a new survey credit. |

**Handheld wheel.** `FUN_141599EC0` rebuilds the known-resource arrays from
snapshot+0x1E8 and +0x1D0. For an atmospheric entry it supplies true at
`0x14159A00C`, even though the scalar numerator needs the visit bit. For a
terrestrial entry `FUN_141597A50` first queries the current body and FormID
through `FUN_1407B7D60`. A successful item lookup returns the byte at
+0x21 (`0x1407B7E52`). Missing body context, component or item returns zero.
If the result is zero, `FUN_1407BB5B0` and its callback collect nonzero
resource IDs from the body's seven biome slots. At `0x141597B43–B46`
equality with the **end** of that search grants known status to a FormID
*absent* from the list. An empty list can therefore make a row known.
The scalar numerator has no such exception. An atmospheric/terrestrial
pointer overlap survives on the terrestrial side of normalization and takes
that side's test.

`FUN_14159A0B0` inverts known into the Monocle row's disabled flag at
`0x14159A1E5`. Its class switch (`0x14159A328`) sends classes 0, 5 and 6
to Common, 1…4 to their respective arrays, and skips classes above 6.
`FUN_1415A6D20` appends the row. The source RGB uses the form triplet or
class fallback through `FUN_1409E7890`. The wheel UI uses disabled to
select **both** Unknown/Known and muted `0x394253`/row RGB. It assigns
symbol and name independently. The UI has 7 Common, 7 Uncommon, 6 Rare,
5 Exotic and 5 Unique positions. Its five Special references reuse positions
from the first three arrays. The native path above fills five arrays.
A colored tile can thus coexist with zero scalar credit. Counting colored
wheel positions is an unreliable substitute for the survey fraction.

Three Monocle subscriptions distinguish these presentations. `MonocleMenuData` formats
`uResourcesCurrent/Max` on the ordinary survey line. An explicitly false
`bShowPlanetInfo` hides the panel and skips that text update. `MonocleKnownResourcesData`
updates the arc. SHOW RESOURCES opens that arc when hidden, and an update can
request that it open. On the static reason-7 resource-scan path the call at
`0x141599708` submits the knowledge mutation. `0x141599714` requests the
wheel update with a true flag and `0x14159971C` requests snapshot refresh.
The queued callback reaches the wheel builder on owner resolution
(`0x1415ABD1A`), passing the flag exposed as `bShowArcOnUpdate`.

`MonoclePickRefData` updates the right-hand target tile. In the resource
branch `FUN_14159AE80` calls the same discovery predicate at `0x14159B439`
and sets `bIsDiscovered` separately from the intrinsic/fallback `uColor`
(`0x14159B31B–B385`). When the form or pick type changes, the HUD uses
that RGB for the target tile. Scarcity selects its rarity frame. Discovery
participates in the scan/SHOW RESOURCES prompt. A separate scene path in
`FUN_14159ED90` tests the same discovery helper at `0x14159F54E` and can
select effects 4/5. Later branches can replace the selection before dispatch
at `0x14159F654`. This bounds the highlighting evidence at an effect choice.
The mapping to a particular terrain pixel in a capture remains unresolved.

**Orbital card.** The selection at `0x141681686–6E3` takes input+0x6F0,
stores it at state+0xC90 and passes it to `FUN_141685AB0`. Calls at
`0x141685AD9/0x141685B3A` construct the detail and pass it to
`FUN_1416CF0F0`. The detail key at +0x184 participates in the resolved-key
comparison at `0x1416CF174–19B`. On the queued path `0x141685D57` supplies
callback `FUN_141698650`, which calls `FUN_141685E30` on owner resolution.
State+0x6B0 holds the registered `StarmapInspectBodyInfoProvider` object.
Its embedded +0x20 model interface supplies virtual +0x58 at the bind site
(`0x14168FC7F–FCFB`, `0x141685E45–E72`). The resulting
`FUN_1416B6310` bind and the movie's `PlanetData_mc.SetBodyInfo` callback
join the row fields to the orbital card. The card hides and skips its
update for a zero body ID or `BT_SATELLITE`. In the separate hover path,
`FUN_14168A8D0` starts the disabled/show-color bytes at 1/1 and clears
disabled on a populated positional lookup (`0x14168AABC`). The bind at
`0x14168AF0D` supplies one row. The `StarMapMenuPlanetInspectData`
subscriber uses `bShowResourceName` and `HoveredResourceA[0]` for its
nameplate. A colored hover icon can therefore appear without item credit.

System view has its own body-card subscription. At `0x1416E8572–857F`
state+0xA14 supplies the body key. The call at `0x1416E85E0` projects its
rows. Callback `FUN_1416ED390` reaches `FUN_1416E87C0`, which binds
through state+0x238 at `0x1416E8802`. The enclosing provider at state+0x218
is registered as `StarmapSystemBodyInfoProvider` at `0x1416E3FAF–3FC4`.
The movie subscribes a second callback for `SystemPlanetInfoCard_mc` and
uses the same resource renderer. The two routes establish the displayed
card rules without identifying a historical frame's active callback.

**PROVEN, user-observed displays.** In the [Save2 corpus](PROVENANCE.md#save2-screenshot-evidence),
Kreet's two orbital cards (S21-10/11) both show 4/8. The latter includes a
landing target. S21-12 shows the ordinary scanner at 4/8. S21-13 shows
Locations at 4/8. After the maintainer-reported Neon scan, S21-14 shows
5/8, a cyan Ne wheel tile and a separate cyan Neon target tile. S21-15
shows Locations at 5/8 with the Neon background still muted. The earlier
wheel S21-06 showed Ne muted and He-3, Pb, Fe and Ag colored. These two
wheel captures belong to different Steam timelines. The post-scan orbital
counter and Neon tile are unobserved.

**STRONG interpretation.** Kreet's measured biome slots include Neon
(`000057E9`), so the absent-ID exception would fail for this resource under
matched inputs. An explicit scanner mutation that raises its item byte from
zero to positive would enable and color its wheel tile and increment the
two observed counters. Locations can still supply muted RGB for an Exotic
resource below threshold 3. This gives a native and UI mechanism for the
observed divergence. The frames do not measure the byte, the scan level,
or the execution of that branch. For Volii Alpha the landed-aboard reading
already includes both resources. The [control and remaining tests](hypotheses.md#locations-and-survey-observations)
bound the interval and distinguish body visit credit from per-item writes.

### PlayerKnowledge in the global save and load paths

**PROVEN, retail static.** The body-keyed stored wrapper contains the u64 key
at +0x10 and the PlayerKnowledge payload at +0x20. The registration, factory
and PNDT paths identify the object in memory. At factory vtable
`0x144D5F2C8` both +0x28 and +0x30 lead via `FUN_14231FC90` to
`FUN_142322A80`, which copies an indirect memory source at `0x142322B96`.
The PNDT MNAM/NNAM paths (`0x140770B77/0x140770BBD`) read plugin subrecords,
initialize level −1 and enqueue typed data. Neither copy identifies the
player’s save. A separate, paired global-data route does.

| Operation | Body, type and field evidence |
| --- | --- |
| Write | SaveGlobalData unit 6 dispatch (`0x141825881–0x141825927` in the unit dispatcher, then `0x141822732`) reaches `FUN_141411190`. It selects the PlayerKnowledge type in DB+0x268. At `0x141411343–138B` it passes the key’s body ID through the ID writer, writes the low u16 and passes that same wrapper’s payload to `FUN_142337790`. Through archive context+0xB0, virtual +0x28, it writes the u32 mask (including visit bit 1), u16 format value 3 and i32 stored scan level at `0x1423377B9/77D2/77E8`. |
| Conditional item records | Mask bit 3 gates the item section at `0x14233783D–7845`. It writes a u64 occupied-entry count, walks occupied 0x30-byte entries and sends the item FormID through the ID callback. It writes the +0x21 credit byte then +0x20 at `0x1423378CC–78F8`. The mutation path at `0x1407B78AD` calls `FUN_1423464E0`, which caps positive progress at 255 and sets payload mask bit 3 at `0x142346614`. Additional nested data follows. This ordering matters when comparing stored progress with the displayed numerator. |
| Read | LoadGlobalData unit 6 selects its callback at `0x1418243F5–0x141824449` and `0x141823172–3191`. The paired load path at `0x14182E43E` reaches `FUN_141413570` via `0x14140D814`. Its ID reader and raw u16 read supply the body and low word, then `0x14141362E–164A` rebuilds the typed key. `0x141413756` calls `FUN_142337A50` on the destination payload. Archive virtual +0x20 restores mask, version and level at `0x142337A81/7AA3/7AB6`. Bit 3 gates the item block here too. `0x142337E60–7EB8` reads the item ID and +0x21, and reads +0x20 for version ≥2. `0x1423380C5–812C` repopulates the item table. WriteUtil (`FUN_14186BD40`) maps/encodes IDs and writes the encoded value in the unit’s four-byte mode. ReadUtil (`FUN_14186BC80`) obtains a buffered or stream ID and translates it via `FUN_1418599A0`. The per-item nested ID list is read from version 1 and a trailing block from version 3. |

This pair establishes a fieldwise save/load route on the pinned executable.
The subsequent offline comparison below identifies its serialized population.
The action that dirtied a component and persistence of the seven biome
allocation words remain separate questions.

#### PlayerKnowledge in Save2 and Save52

**PROVEN · SERIALIZED.** Both preserved saves contain the entire version-3
population. All ranges below are half-open. Unit offsets address the inflated
SFS. Record and field offsets in the [decoder output](../tools/srr022/README.md)
address the unit payload. The BCPS chunk index links both coordinate systems
to physical compressed spans. [Save identities](PROVENANCE.md#save2-and-save52-binary-evidence)
identify the historical inputs.

| Measurement | Save2 | Save52 |
| --- | ---: | ---: |
| Unit 6 in inflated SFS | [0x3EA8D, 0x576A0) | [0x11F1F6, 0x1624FC) |
| PlayerKnowledge count through last record, unit-relative | [24269, 52471) | [42687, 109971) |
| Components, all version 3 and low key zero | 985 | 1,379 |
| Visited bit set | 3 | 40 |
| Item section present / omitted | 2 / 983 | 37 / 1,342 |
| Item entries, all positive +0x21 | 27 | 906 |
| Auxiliary IDs / nested item IDs / 12-byte trailer entries | 0 / 2 / 18 | 54 / 715 / 1,051 |
| Bodies joinable from save alone | 956 | 1,209 |
| Additional bodies conditional on installed TES4 header flags | 18 | 19 |
| Save-scoped dynamic body IDs | 11 | 151 |

The first global table closes at its next directory boundary after 17 units.
The unit-6 dispatcher and the sizes of 17 preceding component tables lead
to the PlayerKnowledge count. The following writer at `0x141822749` emits
a u32 count and ten bytes per entry. The two next tables contain 1,821 and
1,982 entries and end at unit offsets 70,685 and 129,795 respectively. No
signature search or assumed planet count determines the population.

**Comparison.** With the qualified full-plugin mappings, 970 body keys occur
in both saves. Of these, 604 have equal compared fields and 366 differ. Four
joinable bodies occur only in Save2 and 258 only in Save52. The 11 and 151
dynamic bodies remain in their respective inventories with no cross-save
match asserted. Of the conditional joins, 17 are equal, one differs, and one
additional body occurs only in Save52. Using the saves alone yields 587 equal,
365 changed, four only in Save2 and 257 only in Save52.

Among shared keys, 221 masks, 33 stored levels, 17 auxiliary ID sequences and
239 trailer sequences differ. The item-section bit differs on 28. These counts
overlap. All 933 item identities resolve in the saved base-plugin namespace.
No body/item pair appears in both saves. All 27 Save2 entries and all 906
Save52 entries are one-sided, including entries on one-sided bodies. Neither
save contains a zero progress byte or a present-but-empty item section.
The item table includes IDs outside a body's inorganic resource list.

**RECONSTRUCTION_PREDICTED.** On a successful load into fresh destinations,
the reader builds the DB+0x268 typed body/low-word key, restores the mask
and stored level, and fills the auxiliary vector with translated IDs. When
bit 3 is set it indexes each 0x30-byte item slot by translated FormID and
restores the two bytes and nested vector. A translated-key collision can
discard a later insertion. The loader skips all-zero trailer tuples. No
such tuples occur here. The ordinary level query returns 4 when bit 0 is
set. Plugin availability and runtime redirects at a particular load epoch
remain unobserved.

**Independent gameplay and membership check.** At the separately pinned
reproducer revision in [provenance](PROVENANCE.md), join its planetary
directory and inorganic membership by FormID, then consult its atmosphere
list separately. Save2 Kreet has mask `8000003E`, stored level 0 and 20
positive item entries. Three match its seven canonical terrestrial candidates
(Iron, Lead, Silver). The visit bit and atmospheric Helium-3 account for a
fourth credit under the documented survey calculation. Neon has no saved
entry. This agrees with the earlier 4/8 screenshots and distinguishes the
later 5/8 observation. Vectera has seven items with zero matches to its five
canonical inorganics, consistent with S21-03's 0/5. Sumati and Volii Alpha
both omit the item section and have clear visit bits. S21-07 through S21-09
show Volii Alpha at 0/2 and later 2/2 across different displays. Those
captures began from Save2 and include subsequent gameplay. Neither save
provides a controlled before/after action test.

<!-- SRR-022 review -->
**SRR-022 internal challenge: COMPLETE.** A separate reviewer decoded both
original saves independently, compared every component and item by identity
and byte offset, checked the native framing and ID branches, and challenged
the refusal cases, source custody, screenshot hashes and task-only patch.
The 14-path manifest SHA-256 is
`1abaee16964e1b8ca732401ffc81cd275032d3628a1da59efc89c94c0c02cf9e`.
It hashes UTF-8 lines of lowercase file SHA-256, two spaces, repository path
and LF in lexical order, excluding this block and its following blank line.
Dynamic cross-save identities and actual runtime/display state remain
unobserved. Full-plugin joins retain the TES4-header condition above.
<!-- /SRR-022 review -->


**Reproducible method.** Use the tracked decoder in [offline reproduction](#offline-reproduction)
with `functions 1417D6520 1417D6960 1417D7540 1416D0EF0 1416D1510 1416B6180 14136CFD0`.
Use `window 1417D7F0D 22D` for the knowledge-count loop and
`window 1416B69B8 10A` for the row bind across exception-range boundaries.
Use `data 144D5F178 F` and `window 14231D9D4 1D` to verify the registration.
Run on a lawfully obtained matching disk image. These commands write disassembly
to stdout. Game state, load order and save contents are outside this static method.

For the normalization, scanner, queued detail, typed writer and restore,
run these additional bounded reads from the repository root:

```powershell
python -B tools/srr011/inspect_pe.py $image window 1417D8560 F1
python -B tools/srr011/inspect_pe.py $image window 141360436 11
python -B tools/srr011/inspect_pe.py $image window 1415A0506 8E
python -B tools/srr011/inspect_pe.py $image functions 14135D570 141411190 141413570
python -B tools/srr011/inspect_pe.py $image window 142337790 170
python -B tools/srr011/inspect_pe.py $image window 142337DB2 136
python -B tools/srr011/inspect_pe.py $image window 1423380C5 68
```

<!-- SRR-021 review -->
**SRR-021 internal challenge — COMPLETE.** An independent reviewer checked
the retail executable, both scanner and map layouts, Steam capture chronology,
original and handoff identities, and the task patch. The absent-ID exception
limits a simple wheel-color/credit equivalence. Both orbital Kreet captures
precede the reported scan, and Volii Alpha bounds the visible increase to
the orbit-to-landed-aboard interval. Capture-epoch configuration, actual
knowledge writes and exact scene effects remain unmeasured. Covered
five-subject SHA-256 manifest
`b0d813879aa35a5638db91f7794f2855791631a8d529b55e8b3df376df7ca3dd`.
The manifest hashes UTF-8 lines of lowercase file SHA-256, two spaces,
repository path and LF in lexical order, excluding this block and its
following blank line.
<!-- /SRR-021 review -->

<!-- SRR-020 review -->
**SRR-020 internal challenge — COMPLETE.** A separate reviewer challenged the
counter binding, pointer normalization, Kreet control, UI bytecode and typed
save/load paths against the source inputs. Gameplay timing and the screenshot
epoch remain unresolved. The reviewed five-subject SHA-256 manifest is
`265316a3698002b22edb75bf67c3e6ea02c39b619e6263cc904530ca24632dd4`.
It hashes UTF-8 lines of lowercase file SHA-256, two spaces, repository path
and LF in lexical order. The manifest excludes this block and its following
blank line.
<!-- /SRR-020 review -->

<!-- SRR-019 review -->
**SRR-019 internal challenge — COMPLETE.** An independent reviewer checked
the pinned native relationships, contrary cases and proposed observations.
The orbital-scan design records the first visible numerator because UNKNOWN
supplies no prior value. The rendered counter binding, arrival event and
save-stream attribution remain open. Reviewed content manifest SHA-256
`95a2adc57084b0b3fa5f2e4e2acd7f0b28cd8e2414e2f1388dee42e4103fcc58`
covers the four changed subjects in lexical path order (UTF-8 lines of
lowercase file SHA-256, two spaces, repository path and LF), excluding this
delimited block and its following blank line.
<!-- /SRR-019 review -->

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
