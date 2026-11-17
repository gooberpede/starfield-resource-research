# SRR-014 — Allocation-bearing database operations

The retained resource IDs live in the inline payloads of the mixed edge
index at context +0x300. The native allocator borrows those payloads under
the same shared-mode protocol used by three verified copy readers. Edge
insertion, owner-range removal and context-wide clearing enter a ticketed
mutation protocol. The seven resource fields are cleared and filled in
separate stores inside each admitted planet callback. The shared-mode
join gives no transaction or completion signal for those fields.

All locators are preferred VAs for retail AMD64 `Starfield.exe` 1.16.244.0,
image base `0x140000000`, SHA-256
`7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28`.
Subtract the preferred base for an image-relative RVA. Names such as
“control,” “shared,” and “ticketed” describe behavior in the decoded
instructions. [Retail provenance](PROVENANCE.md) · [SRR-011 result lifecycle](SRR-011-planetary-allocation-execution-and-result-lifecycle.md) · [SRR-012 acquisition evidence](SRR-012-acquisition-evidence.md)

## Operation catalogue

| Operation, native locators and evidence status | Inputs and admission | Effects, ownership and use in the investigated path |
| --- | --- | --- |
| Owner, context and registry — **PRIOR ESTABLISHED**. `FUN_1423FF640`, `FUN_1424059F0`, `FUN_14231D000`, `FUN_142404EF0`. | Lazy global owner is `0x1482EE300`. Its constructor zeros owner +0x8B0 at `0x1423FE0E9`. The context is embedded at owner +0x2C0. | Constructor installs the native DB vptr `0x144D6A6C0` at `0x142405AD1–AD8`. Context +0x268 and +0x300 each begin with an empty tree header. Owner +0x8B0 receives the context at `0x1418993E3` (RVA `0x82EEBB0`). Registration uses descriptor receiver +0x100 and sets the u16 discriminator at `0x1461DFA4C` through `0x14231D7D9–D7F1`. Use the registry witness to interpret this word. |
| Queue attachment and service — **NEW STATIC FINDING**. `FUN_1428D8130`, `FUN_1428D87A0`, `FUN_1428D96C0`, `FUN_1428D8FE0`, `FUN_1428D89B0`. | After publication, attach DB to the owner +0x40 receiver at `0x1418993F1`. The new-registration arm stores receiver at context +0x30 at `0x1428D8211`. The startup branch then configures a callable at `0x141899408`, subject to the helper's u16 state gate at `0x1428D87AB–87D2`. | The command buffer is the attachment receiver +0x40, which is owner +0x80. The callable pointer used by submitters is receiver +0x238 (owner +0x278). Publication, attachment, callback configuration and callback execution are separate steps. See [command order](#command-order-and-visibility). |
| Author inputs and submit — **PRIOR ESTABLISHED** for the input fields and callback, **NEW STATIC FINDING** for command publication. `FUN_14076EC00`, `FUN_14233F2C0`, `FUN_140773180`, `FUN_140773BE0`. | Successful PPBD and ENAM-associated replacements get planet and BIOM keys from PNDT +0x28 and input payload +0x40. CSV admitted rows proceed with the row's BIOM at `0x14234102B–103A`. | Input builders zero all seven u32 fields before submitting at `0x14076F360`, `0x14076FCEA` and `0x14234103A`. Zero stores are `0x14076EEED–EEF6`, `0x14076F853–F862`, and `0x142340535–053F`. `FUN_14076E720` copies the 0x70-byte typed value into the command. The command owns the copy and captures the context pointer. Submission publishes queue bytes at `0x140773223–3239` or `0x140773C83–3C99`. |
| Inline edge construction — **PRIOR ESTABLISHED** for insertion and copy, **NEW STATIC FINDING** for equality and storage movement. `FUN_140777290 → FUN_140774E00 → FUN_1407766B0`. | Callback takes the ticketed guard at `0x140774E1C`. Context +0x300 is selected at `0x1407766D6`. Empty root goes to `FUN_140382700`, nonempty to `FUN_140383010 → FUN_140382800`. | Native insertion reserves 0x90 bytes and increments the mixed edge count before typed initialization, including first-root publication at `0x1403827E3`. It writes wrapper vptr and both key words, then constructs inline payload at edge +0x20 at `0x140776791–67A4`. The decoded same-key path goes through insertion and constructs another edge. Page repacking/split can move existing payloads. |
| Notifications and reverse index — **PRIOR ESTABLISHED** for the notification, **NEW STATIC FINDING** for the separate queued key operation. `FUN_142406B70 → FUN_1424069F0 / FUN_14240F5F0`. | Insertion status byte at returned iterator +0x20 controls notification. The notification reads edge key at `0x142406BA5–BAE2`. | The reverse-key path rearranges owner, target and discriminator into a pair at `0x142406A53–AA6` and addresses context +0x358. Its conditional command captures key and DB at `0x142406ACF–AEF`, later `FUN_142417100 → FUN_142413190` re-enters mutation guarding and operates on that reverse index with the captured key. The immediate callback loop passes a key copy at `0x142406BE2–BE8` and dispatches slot +0x10 at `0x14240F659`. Neither bounded body transfers resource IDs to another store. Concrete registered callback targets for a given runtime epoch are open. |
| Keyed copy lookup and miss — **PRIOR ESTABLISHED** for storage and consumers, **NEW STATIC FINDING** for caller guard scope. `FUN_140771F30 → FUN_1405F7A80 / FUN_14076E810`. | Owner key zero, absent range or no matching BIOM yields false at `0x140771F8B` or `0x140771FFD`. Key geometry is below. The primitive receives caller-provided output in R9. It tests payload +0x40 against the requested BIOM at `0x140771FB6`. | The first match triggers copy assignment at `0x14077200D` and returns true. Read success can copy zeroed authored fields, and the miss path has no generator call. Three verified slot consumers hold shared-mode scope around the lookup. Later work uses their local copies. |
| Enumeration and result writes — **PRIOR ESTABLISHED** for storage and slots, **NEW STATIC FINDING** for guard span. `FUN_140779610 → FUN_140779760 → FUN_14077BCE0`. | Adapter uses the published context and takes shared mode before calling the orchestrator. Collector accepts an eligible nonzero PNDT key and ranges over the matching entries. `FUN_140777870` resolves payload +0x40 BIOM (type byte `0xA0`) and nonzero +0x4C RSGD (type `0xAB`) via FormID lookup. | Collector appends inline pointers at `0x14077BE39` without a per-edge owning reference. Orchestrator clears seven u32s at `0x140779AF5–9B2E` and attempts the category-6 and per-biome generation passes. Productive selection writes to the same borrowed payload. Scratch release leaves the retained values in the tree. |
| Independent FormID map — **PRIOR ESTABLISHED**. `FUN_1405DE3B0 → FUN_1405ACAD0`. | Accepts a runtime FormID and uses its own hash chain and native map state. `0x1407778F0–7923` resolves and checks the component input types. | Records carry keys. A key range/copy hit alone does not establish BIOM or RSGD form validity. Verified consumer `FUN_14086A6D0` independently resolves copied resource IDs and checks type `0x9F` at `0x14086A7F7–A80C`. |
| Typed +0x268 factory insert/update — **PRIOR ESTABLISHED**. Vtable `0x144D5F5C8` +0x28/+0x30 → `FUN_142322520`. | Uses a distinct qword key with discriminator in the high u16, entity in the middle u32, and namespace in the low u16. Receives an existing typed source. | Creates a stored-component wrapper and copies at `0x142322633`, or assigns to the existing payload at `0x142322664`. Both copy all seven fields as ordinary members. This operation's existence is established. An allocator-edge source alias or startup use for a computed-result mirror remains open. The allocator's verified +0x268 lookup at `0x140779CD7` uses the independent `BiomeData` discriminator `0x1461E1D90`; the coverage update is at payload +0x44. |
| Owner-range erase — **PRIOR ESTABLISHED** for triggers, **NEW STATIC FINDING** for guard and cursor behavior. `FUN_140772EE0 → FUN_140776680 → FUN_140774970 → FUN_142409490`. | Takes ticketed mutation guard at `0x14077498C`. Focal caller passes owner, PerBiomeData type, and range fences from `0x140774997–0x1407749BF`. End of range or first out-of-range key ends the loop. | Saves each key, erases the entry at `0x142409682`, then signals change at `0x142409691`. It resumes from the eraser's returned cursor at `0x142409696–96A0`. In the multi-entry case `0x1422CEC32` calls virtual destructor slot +0 before moving directory descriptors at `0x1422CEC6D`. Edge destructor `FUN_140777810` tears down the typed value at `0x140777823`. ENAM at `0x14076F751` submits owner-wide removal before submitting replacement inputs. PNDT lifetime sites `0x14076E9EA` and `0x14076EB83` also submit it. |
| Clear, shutdown and deregistration — **PRIOR ESTABLISHED** for the three boundaries, **NEW STATIC FINDING** for native guard and queue-stop ordering. `FUN_1424063B0`, `FUN_1423FE320`, `FUN_1424058B0`. | Reset's signed arm and an independent TES destructor path call guarded context clear. Shutdown takes a different path through `0x141882F3D`. The registry remove takes the registered type word address. | Clear takes ticketed mutation admission at `0x1424063CE` and clears +0x268 and +0x300 at `0x1424063DB` and `0x14240640C`. It can leave the context published. Shutdown runs queue stop `FUN_1428D88B0`, destroys indexes and releases the control object's reference at `0x1423FE3A7`, then zeros published slot at `0x141882F4E`. Registration teardown `0x14231DAFB → FUN_1424058B0` clears registry fields and type word separately. |

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

For the standard PerBiomeData key, the inclusive ordered interval is
`[(K0, 0), (K0, 0x0000FFFFFFFFFFFF)]` where
`K0 = (u64(PNDT key) << 32) | 0x10000 | u16(discriminator)`.
Both insert helpers set the second key word to the zero-extended BIOM
ID. The accessor lower-bounds by the two key words via
`FUN_1403832A0` and `FUN_1403833E0`, then advances through records,
blocks and leaf links via `FUN_1403A4250` while under the inclusive
upper fence. End uses the null block and slot sentinel `0xFE0`
in the reader and collector. There is no iteration lease in the
four-word cursor itself. The collector computes
`block + u16[block + 4*slot + 0x12] + 0x20` at
`0x14077BDA5–BDB1`. [Exact index layout](SRR-012-acquisition-evidence.md#exact-mixed-index-model)

**NEW STATIC FINDING.** On an exact key, `0x14038304A–3066`
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

## Command order and visibility

**NEW STATIC FINDING.** The submitter copies the model inputs before
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

**OPEN/BLOCKED.** The positive ordering proves typed submission before
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

**NEW STATIC FINDING.** CSV's accepted-row branch at
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

**NEW STATIC FINDING.** The PNDT definition reader provides one concrete
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

**NEW STATIC FINDING.** Compare offsets from the refcounted control
object at context +0x238. Several helpers use control +0x10 as
their base. For example, helper +0x208 maps to control +0x218.

| Mode or transition | Native scope and limits |
| --- | --- |
| Per-thread shared admission | `FUN_142404230` gets the caller's thread record at `0x142404248`, increments local depth at `0x142404257`, and, on outer admission, adds 4 to shared state control +0x218. If the existing low phase bits require waiting, it loops at `0x1424042A3–2E6`. A nested admission skips the outer transition. |
| Writer and reader use the same shared mode | Adapter acquires at `0x1407796A6`, calls orchestrator at `0x1407796D2`, then unwinds read depth, completion-side counter at control +0x21C and control refcount at `0x1407796D8–9732`. Representative copy users have acquire/lookup/release sites `0x1407BAA5D / 7BAA7A / 7BAA8C`, `0x1407BD656 / 7BD677 / 7BD689`, and `0x14086A77B / 86A798 / 86A7AA`. `FUN_140771F30` itself contains no corresponding acquire. Shared holders can coexist at this level. |
| Ticketed mutation | `FUN_142404A80` retains the same control, takes a ticket using +0x228 and waits for serving +0x22C unless owner +0x240 matches the current caller. It sets owner and ticket word +0x23C at `0x142404B26–B33`. Insertion, erase, context clear and reverse-key application enter at `0x140774E1C`, `0x14077498C`, `0x1424063CE`, and `0x1424131AC`. Their outer exits reset owner and advance serving. |
| Page-token path | Many page accesses call `FUN_142404330`. It compares a per-page token at block −0x10 with control +0x23C. On a mismatch `FUN_142404090` checks writer ownership and handles phase/read counters before updating the page token. Its no-owner exit at `0x142404223` allows the shared-mode collector's call at `0x14077BDA0` to return without becoming the mutation owner. This admits a per-page synchronization operation. Token equality gives no witness for the separate allocator word stores. |

The operations below are conceptual transcriptions of the named paths.
Eligibility and allocator branch detail is in the primary dossier.

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
SRR-013 external collector borrows no native guard, and repeat agreement
still qualifies only the bracketed observations. Mixed count changes on
insert/erase, while allocation modifies values in place. Treating the
refcount, ticket, page token, input-queue status or registry word as a
result completion indicator would confuse distinct native transitions.

## Offline verification route

Use the tracked [PE decoder](../tools/srr011/inspect_pe.py) with Python
3.14 and Capstone 5.0.7. It hashes every input, checks AMD64 PE32+ and
preferred base, then reads bounded native windows. It prints to stdout.
Use a lawful executable matching the pin above.

```powershell
$image = '<path to the pinned Starfield.exe>'
python -B tools/srr011/inspect_pe.py $image functions 140773180 140773BE0 140774E00 1407766B0 140383010 140382700 140382800
python -B tools/srr011/inspect_pe.py $image window 1422CECC2 F0
python -B tools/srr011/inspect_pe.py $image data 144B3D258 10
python -B tools/srr011/inspect_pe.py $image functions 140779610 1407BA9B0 1407BD270 14086A6D0 142404A80 1424063B0
python -B tools/srr011/inspect_pe.py $image window 142404230 F8
python -B tools/srr011/inspect_pe.py $image window 142404090 19B
python -B tools/srr011/inspect_pe.py $image window 142404330 206
python -B tools/srr011/inspect_pe.py $image window 140771F30 F4
python -B tools/srr011/inspect_pe.py $image window 1418993BE 4F
python -B tools/srr011/inspect_pe.py $image window 141882F32 23
python -B tools/srr011/inspect_pe.py $image data 144DA7DB8 28
python -B tools/srr011/inspect_pe.py $image window 1428D96C0 95
python -B tools/srr011/inspect_pe.py $image functions 1428D8130 1428D8FE0 1428D8060 1428D7BD0 1428D8640
python -B tools/srr011/inspect_pe.py $image window 1428D87A0 108
python -B tools/srr011/inspect_pe.py $image window 1428D9560 E
python -B tools/srr011/inspect_pe.py $image window 1428D89B0 193
python -B tools/srr011/inspect_pe.py $image window 1422CE200 D6
python -B tools/srr011/inspect_pe.py $image window 14189753A 24
python -B tools/srr011/inspect_pe.py $image window 14189A687 21
python -B tools/srr011/inspect_pe.py $image window 141881A5A 12
python -B tools/srr011/inspect_pe.py $image functions 140472890 1407873D0 140799690 140799100
python -B tools/srr011/inspect_pe.py $image functions 1424069F0 142413190 14240F5F0 142322520 142340990
python -B tools/srr011/inspect_pe.py $image window 142340F79 160
python -B tools/srr011/inspect_pe.py $image window 141882004 19
python -B tools/srr011/inspect_pe.py $image window 140777860 10
python -B tools/srr011/inspect_pe.py $image window 14231D9A3 27
python -B tools/srr011/inspect_pe.py $image data 144D5F188 0D
python -B tools/srr011/inspect_pe.py $image scan 145FC00C8 145FC00D0 145FC00D8
python -B tools/srr011/inspect_pe.py $image scan 140773180 140773BE0 1407766B0 140774E00 140771F30 1424063B0 142409490 142322520
python -B tools/srr011/inspect_pe.py $image window 140770C98 25
python -B tools/srr011/inspect_pe.py $image functions 140773910 142346A60 1404775F0 1404768D0 1405DF5C0
python -B tools/srr011/inspect_pe.py $image data 144B3D7D8 8
```

The second scan tests branch/RIP candidates in file-backed .text
`[0x140001000, 0x143A3EF6C)` against 236,427 exception ranges and
searches exact qwords in file-backed sections. It produced 25 candidates
and 24 decoded references, plus two qwords for the +0x268 factory.
The out-of-range candidate at `0x140774A6A` is outside the selected
unwind ranges. The first scan produced six decoded direct references.
Computed references, arbitrary dynamic receiver registrations and runtime
producer timing fall outside that census. [Existing broader native lead controls](SRR-011-lifecycle-lead-register.md)

The tracked decoder generates the relevant disassembly from the pinned
offline image. This investigation read the image as data and left the
local Ghidra database untouched.
