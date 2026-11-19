# Retail execution lifecycle

The pinned retail executable has a **PROVEN STATIC** construction-time route
from PNDT traversal to in-place allocation writes. Database publication,
queued input submission, normal visitor completion and productive allocation
are separate events. Retained populated title-card components are **PROVEN
LIVE** observations of state; they do not identify the generating visit or
its time. Creation Kit Galaxy View Apply traces establish the CK mechanism
in the [generation baseline](v1-research-baseline.md); CK addresses are not
retail addresses, and output agreement does not prove instruction-level identity.

All preferred VAs on this page refer to AMD64 retail `Starfield.exe`
1.16.244.0, base `0x140000000`, SHA-256
`7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28`.
Subtract the base for an RVA. Semantic names in pseudocode are research
aliases. Build identity and evidence routes are in [provenance](PROVENANCE.md).
Storage, commands and synchronization are explained in the
[component database](component-database.md); [validation](allocation-validation.md)
records exact live samples and custody identities.

## Startup and reset ordering

The arrows show normal native continuation or the explicitly named dispatch.
The relation between the marked events [A] and [B] is unverified. The
[startup setting and dispatch evidence](#startup-setting-and-csv-input) supplies the worker and
application entry paths, source predicates and guard identities. The
[database evidence](component-database.md) supplies the submission and
execution boundaries.

```text
Startup and reset control flow
  -> construct embedded DB (+0x268, +0x300) -> publish at owner +0x8B0
  -> queue-host attachment
       +-> galaxy state object memory allocated and galaxy guard zero
       |     -> construct galaxy module -> register PerBiomeData
       +-> object memory allocation failed or galaxy guard nonzero
             -> bypass registration
  -> both normal continuations lead toward application dispatch (inline or queued)
       +-> optional direct loader call, if admitted
       +-> state-0 worker, if admitted, calls the same file/group loader
  File/group loader:
       +-> can submit PPBD/ENAM commands [S]
       +-> on normal return, continue to Starfield module entry [M]

  Load-order/other dispatch -> reset if signed mode < 0 -> clear indexes
    -> tear down Starfield module and clear its guard -> replay file groups
       +-> can submit PPBD/ENAM commands during replay [S]
       +-> on normal return, re-enter Starfield module [M]

  [M] Starfield module entry
       +-> guard nonzero: bypass construction
       +-> guard zero: construct
            -> if CSV import flag is set: early PNDT sweep -> follow-up
               -> CSV loader can submit accepted rows [S]
            -> on normal continuation of either flag path:
               [A] enter later PNDT allocation sweep
                -> for each admitted PNDT, visitor calls allocator synchronously
                   -> collect indexed edges -> clear slots / try Everywhere
                   -> per-biome allocator calls -> conditional ID stores
                -> after iteration returns, run follow-up

Component command flow
  [S] Submit command: publish queued command bytes
       -> if notifier and scheduler admit service:
            +-> direct: call service in the notification path
            +-> deferred: schedule a callback that calls the same service
       -> if service dequeues this command: execute its typed callback
            -> insert and construct the indexed edge
            -> on normal callback return, this insertion command completes [B]

  [B] command completion vs. [A] later sweep entry: UNVERIFIED for the
      queued insertions as a group. No queue-wide completion join is established.

  Separate readers can copy any matching visible edge. Their order relative
  to any particular sweep is caller-dependent.
  Observed at title: four retained outputs. Exact generating visit unknown.
```

The startup allocation check concerns memory for the native galaxy state
object. The loader and CSV arrows show where commands can be submitted.
Whether every command finished before loader return or the later sweep
began is unresolved. The collector can borrow only an edge already indexed
when it reaches that edge. The two follow-up visitor types have separate roles.

```text
application_setup_on_inspected_path():
    ctx = initialize_embedded_db()                 # 0x1418993BE–0x1418993DE
    owner.published = ctx                          # 0x1418993E3
    attach_queue_host(ctx)                         # 0x1418993F1
    if galaxy_state_object_allocation_succeeded(): # 0x500-byte request at 0x14189A687
        if qword[0x1461FA160] == 0:               # 0x141882092–0x14188209A
            construct_galaxy_module_and_register() # 0x1418820A3; 0x14231D7F1
    ...                                            # app command inline or queued

application_command():
    if configured_true(0x14591AC00) or (           # nonnull pointer to nonzero byte
       configured_true(0x14591AC20) and
       configured_true(0x14591AC40) and
       configured_true(0x14591AC60)):
        initial_loader_on_normal_continuation()    # callsite 0x14189ABB4
    ...
    if byte[0x145E71718] == 0 and saved_virtual_AL:  # AL from call at 0x14189AB43
        schedule_state_0()                          # state 0 calls the same loader

initial_loader_on_normal_continuation():
    load_file_groups()                             # 0x141894C8E, return 0x141894C93
    ...                                            # three intervening calls
    enter_starfield_module()                       # 0x141894CC3

enter_starfield_module():
    if qword[0x1461E2288] == 0:                     # 0x140951904
        publish_module_and_enter_constructor()     # 0x1409519BE
        if byte[0x145EA6000] != 0:                 # 0x14094E542–0x14094E549
            visit_PNDT_bucket(generate_visitor)    # 0x14094E577
            run_BIOM_follow_up()                   # 0x14094E57C
            try_biome_CSV_loader()                 # 0x14094E608
        ...                                        # normal continuation of either arm
        visit_PNDT_bucket(generate_visitor)        # 0x14094EF57
        run_BIOM_follow_up()                       # 0x14094EF5C
        ...                                        # separate receiver at 0x14094EFBD
    continue_module_entry()                        # 0x140951A3C

generate_visitor(form):
    if form != null and form.type_at_0x2E == 0xBA:  # 0x14077C474–0x14077C47D
        generate_for_planet_under_db_guard(form)  # 0x14077C482 -> 0x1407796D2
    return 1                                     # 0x14077C487, continue iteration

reset(receiver):
    if signed_byte[receiver + 0x2E] < 0:           # 0x141897167–0x14189716B
        ...                                       # admitted reset work
        clear_published_context_indexes()          # 0x141897552
        teardown_starfield_module()               # 0x141897557; guard clear 0x140951CDD
        ...                                       # same signed branch
        replay_file_groups()                       # 0x141897B19
        enter_starfield_module()                  # 0x141897B59
    ...                                           # reset continuation
```

The direct loader branch and the worker scheduling condition are separate.
If both reach module entry, a still-populated Starfield module guard
bypasses a second construction. The reset route may come from mode
`0x84` wait/drain and state-1 dispatch
or direct dispatch for `0x85/0x86`. The two identified load-order callbacks
admit their `0x84` calls on `DL == 0` and zero pending +0xC1C.
Nonzero pending +0xC1C instead stages +0xC10 = `0x20` and mode `1` or
`0x82`; the pending handler can later set `0x84`. Mode and receiver can be
reread before reset. These edges establish possible re-entry under the signed
predicate. [load-mode predicates](#application-dispatch-and-load-mode-predicates)

## Dispatch identity

| Reference | Native classification |
| --- | --- |
| `0x144B3D9F0` | Absolute pointer at vtable `0x144B3D9E8 + 0x08` to `FUN_14077c470`. The observed iterator uses the other slot. |
| `0x144B3D9F8` | Absolute pointer at vtable `0x144B3D9E8 + 0x10` to the same function. At vtable minus eight, the MSVC complete object locator `0x144FD4B68` resolves the concrete local function implementation and the `ILocalFunction<BSContainer::ForEachResult, TESForm*>` base, both at object offset zero. |
| `0x1485F1500` | PE exception-directory entry with begin RVA `0x77C470`, exclusive end RVA `0x77C491`, and unwind-info RVA `0x541CC78`. The neighboring `0x1485F1398` and `0x1485F13A4` entries describe the adapter and orchestrator. These references describe unwind metadata. |

The iterator computes the type bucket as owner + `(uint8(DL)+5)*0x18`
(+0x11E8 for PNDT type `0xBA`). It reads count at bucket +8 and array at
+0x10, skips nulls, and calls `[receiver.vptr+0x10]` at `0x1405932EF`.
The adapter `FUN_140779610` saves TLS state, sets it to `0x82`, obtains
`FUN_1423FF640()` result +0x8B0, prepares access and directly calls
`FUN_140779760` at `0x1407796D2`. Cleanup restores TLS after return.
The callback always returns 1 on normal continuation, including rejection.

## Sweep and productive writes

In `FUN_140593280` the bucket count at +0x08 and the array at +0x10 define
the traversal. The iterator admits the bucket at `0x1405932B4` and releases
its reader count at `0x14059330F`. The null and callback-result branches
are `0x1405932E4–0x1405932F6`. The installed vtable entry
`[0x144B3D9F8]` resolves to `FUN_14077C470`. The visitor calls the adapter
and then sets EAX to 1 even when it skips the adapter. Thus the generic
stop-on-zero branch is not an early exit for this receiver on normal
continuation. The adapter calls `FUN_140779760` directly and releases its DB
control participation on return. There is no handoff between these direct
calls and the focal slot stores.

| Point | Gate and effect |
| --- | --- |
| PNDT admission | Callback requires the form type `0xBA`. The +0x54 key supplies the indexed range; a zero key or no collected work bypasses the per-biome loop. A zero seed changes reseeding at `0x140779C33–0x140779C6F`. [storage](component-database.md#slot-storage-and-copied-consumers) |
| First payload pass | Both clear branches at `0x140779B00–0x140779B2E` zero the 28-byte field span. The clear occurs before BIOM resolution, so failure to resolve type `0xA0` can leave zeroed slots. The category-6 scan can write resource FormID to +0x68 at `0x140779B9F`; subsequent loop decisions test the actual written value. |
| Second payload pass | Nonempty work reaches `0x140779C86`. At `0x1407778F0–0x14077792B` +0x40 must resolve as BIOM, while a missing or incompatible +0x4C resolves to a null optional RSGD pointer. `FUN_140777E30` attempts the optional list and can fall through to the BIOM list when both selection pointers are zero. |
| Conditional results | Special needs the selected pair and shared count below eight before +0x64 is written at `0x140777971`. The Common path may write a new root at `0x1407779FC` with conditional descendant writes, copy a cached family at `0x140777AD1–0x140777AEA`, or explicitly zero +0x50 at `0x140777AEF`. The guarded branch can copy an eligible configuration at `0x140777B7E–0x140777B96`. [native mapping](function-register.md) |
| After the loops | The +0x268 lookup at `0x140779CD7` uses a different discriminator and gates coverage adjustments including payload +0x44. The follow-up at `0x14094EF5C` starts with a visitor that collects BIOM identities and can schedule jobs. The distinct final PNDT sweep at `0x14094EFBD` uses vptr `0x144B3D9C8`. Neither is needed for the focal Common/Special/Everywhere stores to precede the late visitor return. [copied consumers](component-database.md#slot-storage-and-copied-consumers) |

One local happens-before relation is decisive: every completed focal store
reached in a late visit precedes that visitor's return, which precedes
the return to `0x14094EF5C` on the same invocation. The early sweep has
the equivalent local return at `0x14094E57C`, before its follow-up and CSV
call. A return with an empty bucket, no matching edges or no successful
selection is equally consistent with the instructions. DB publication, the
tree count, the readiness latch written before the wait, and the post-loader
worker signal have no successful-write predicate in the inspected paths.
The worker signal can order normal upstream continuation without requiring
module construction or nonempty work. Byte `[0x145E614D9]` is set before
initial module entry at `0x141894CBD`. The signed reset path instead clears it
at `0x1418975FF` and sets it after re-entry at `0x141897C01`. A set byte
cannot distinguish those orders.

## Startup setting and CSV input

**PROVEN STATIC.** The early comparison at `0x14094E542` reads
the current value of the native default-false `bImportCSVBiomeData:Data`
setting. The earlier exact-reference search found only the comparison because
the writers use a computed field address.
The evidence resolves the initialization and one configuration writer for
this build. The effective value at the historical title checkpoint is open.

| Join | Native evidence |
| --- | --- |
| Name and default | Initializer `FUN_14008C050` loads `R8D=0`, the name string at `0x144B65898` and the setting address `0x145EA5FF8` before calling `FUN_140305FD0` at `0x14008C065`. The latter writes the name to +0x18, clears the value dword and sets the value byte at `0x140305FEF–0x140305FF6`, then copies the initialized value to +0x10. The consumed byte is `0x145EA5FF8 + 8`. An exact qword reference to the initializer occurs at `0x143A566C8`. |
| Membership in the INI collection | `FUN_1403061C0` returns a singleton whose vptr is installed as `0x144AFB330` at `0x140306213`. Its RTTI locator at `0x144F678E0` resolves to `INISettingCollection` (type-name VA `0x1459BB140`). The call at `0x140306062` uses the collection's slot +8, `FUN_140308070`, which adds the setting pointer to the list at collection +0x118 when its name is absent. |
| Load and dispatch | Startup calls `FUN_140C80E60` with this collection at `0x141898D05`, `0x141898DBF` and `0x141898E05`. The latter path uses `StarfieldCustom.ini` at `0x144CB3518`. The callee sets its path, then calls collection slot +0x30. The resolved method `FUN_1428CD970` establishes +0x110 and returns true. The +0x58 method `FUN_140307FA0` iterates the +0x118 setting list and calls its collection slot +0x28 with each nonnull setting. That slot resolves to `FUN_1428CDBE0`. |
| Configured write | The reader parses the name and section from setting +0x18. `FUN_1428CD500` maps the initial `b` via byte table `0x1428CD58C` and jump table `0x1428CD56C` to type 0. The reader's table at `0x1428CE004` sends 0 to `0x1428CDF83`. It passes section, key, current boolean default and path to the integer profile reader at `0x1428CDF9B`, normalizes nonzero and writes setting +8 at `0x1428CDFA8`. These startup load calls precede construction at `0x1418993DE`. |
| Neighbor controls | The preceding guard at `0x14094E4C1` reads `bImportCSVStarData:Data` (initializer `0x14008C020`, object `0x145EA5FD8` +8). The guard at `0x14094E4EC` reads `bImportCSVCelestialBodyData:Data` (`0x14008C190`, object `0x145EA6128` +8). Their calls at `0x14094E4DA`, `0x14094E50A` and `0x14094E531` precede the early-sweep decision. They are distinct inputs and are not substitutes for inspecting the biome CSV branch. |

**PROVEN STATIC.** For nonzero `bImportCSVBiomeData:Data`, the
constructor calls the early PNDT iterator at `0x14094E577`, its BIOM
follow-up at `0x14094E57C` and the biome CSV parser at `0x14094E608`,
in that order. The parser's file source is a setting object with default
`Space\BiomeData.csv` (string `0x144D609C8`, pointer at `0x145920A88`). The file acceptance branch requires a nonnull
stream and its bit 0x08 at `0x14233F34D–0x14233F361`. Accepted buffered
rows start with zero at +0x50..+0x68 (`0x142340535–0x14234053F`).
Both flush sites call `FUN_142340990` and reach
`FUN_142340AB0`, which checks the separate +0x268 record type
`0x1461E1D90` before the row submission path at `0x14234103A`.
That site copies the row into a typed command via `FUN_140773BE0`.
The CSV loader may return without a submitted row. The later iterator at
`0x14094EF57` is on the common normal continuation of both flag paths.
[input operations](component-database.md#operation-catalogue)

**PROVEN STATIC.** The common-tail call at `0x14094EECC` consumes
the published DB. Within `FUN_1407873D0` the search at
`0x14078742A–0x140787468` uses +0x268 and discriminator
`0x1461DD80C`. The subsequent write at `0x140787559` is to that
edge's +0x20, populated from a type-0x75 form's +0x28 or zero. This
provides a positive control for nearby DB activity on a different record.
The follow-up directly after each allocation visit similarly gathers BIOM
identity and can install jobs with a separate discriminator. Neither
call provides an allocation-result count. CSV submission, command service,
and the later collector's successful fetch are distinct boundaries.
An indexed payload seen by a collector has been inserted by the time of that
lookup. These paths alone leave global queue quiescence and complete
visibility of every accepted row before the later sweep open.
[Database command and guards](component-database.md) ·
[follow-up consumers](component-database.md#slot-storage-and-copied-consumers)

## Application dispatch and load-mode predicates

The two load-order callbacks return early on callback argument
`DL == 0xFF`. Their mode-0x84 arms require `DL == 0` and
zero pending-load byte +0xC1C, tested at `0x141840E82` and
`0x14183DF4F`. Nonzero +0xC1C instead sets pending state +0xC10
to `0x20` and writes control mode `1` or `0x82`. A separate
pending-load handler, `FUN_141852410`, tests that state at
`0x141852E61`, writes mode `0x84` at `0x141852E80` and
calls the dispatcher at `0x141852E84` on the admitted path.

The application startup driver supplies a second verified ancestry.
`0x14365D891` calls `FUN_1418814C0`, with continuations through
`0x14188155B`, `0x14189A80C` and `0x1418A257E` to
`FUN_1418A37C0`. This driver reaches `FUN_14189A970` inline at
`0x1418A3A34` or through installed command vptr `0x144CB2AD0`,
slot +8, at `0x1418A3C70`. The path to `0x14189ABB4` calls the
same initial loader under the optional byte guard through
`0x14591AC00` or the three byte guards through `0x14591AC20/40/60`.
The PE entry in `.bind` uses an unresolved computed transfer.

The [sibling load-readiness map][load] identifies a first-transition wait
before the ordinary manual-load arm. `FUN_1418501B0` tests pending
+0x50 against mask `0x40D4` at `0x141850226`. The wait route through
`0x141850266` enters `FUN_141898210`, which checks the latch at `0x14189821E`.
The unset-latch branch calls `FUN_14187FBD0` at `0x141898237`.
When a worker control exists it waits on the same handle field
signaled by state 0 at `0x14187FB52`, after initial loading returns.
The set-latch branch skips this wait. The manual-load branch tests
mask `0x4` at `0x1418507AB` and calls into load handling at
`0x1418507CF`. Within the nonzero mask arm, the alternate at
`0x14185022D–0x141850252` requires dword `[0x145F42700] == 2`,
byte `[0x145F42720] != 0`, a non-null pointer in `[0x145E60E98]`
and nonzero byte at that pointer +0x13FE30. All four passing writes
mode `0x86` at `0x14185025B` and leaves the direct path. This
supplies a conditional ordering relationship between startup and load
admission.

The application loop also schedules reset processing.
`FUN_14189D520` exits this region for nonzero +0x28 at
`0x14189D80B`. The arm for +0x2E and byte `[0x145E71718]`
both nonzero at `0x14189D815` and `0x14189D81F` enters the
wait/counter block before scheduling.
It passes callback `0x141884330` at `0x14189D96D`.
`FUN_1418A2D60` can call it inline at `0x1418A2FDC`, or queue
vptr `0x144CB2BE8` slot +8, whose method calls the captured pointer
at `0x1418A3FB5`. The captured thunk jumps to `FUN_141896020`.
Another command path at `0x14189DC08` requires nonzero byte
`[0x145E6D67A]` at `0x14189DBB9`, uses thunk `0x141884340`
and eventually writes mode `0x85` at `0x1417C6B86` before entering
the dispatch helper. Those edges establish mode handling independent of
the two load-order callback bodies.

The registered `CreateViewEvent` receiver supplies a demand-side
control. Module-state construction registers its +0x10 subobject at
`0x1409519B6`. Table `0x144B66650` slot +8 binds `FUN_14094F010`,
which gates on event +0x20 equal to 2. Its resolved visitor is
`FUN_142396D80` through vtable `0x144D64438` slot +0x10. This is
a scene-object walk with nested virtual receivers. The verified
functions contain no direct edge to the focal dispatcher.

## Reset, readiness and disposal

| Evidence class | Candidate boundary | Defensible ordering |
| --- | --- | --- |
| PROVEN STATIC | Latches at `0x145E7B57C` and `0x145E758AF` | The former is written to 1 at `0x14189932A`, before DB construction. The latter is written to 1 at `0x14189947E`, after context attachment and a separate type registration (`0x1461DD824`), but before `PerBiomeData` registration and guarded loader dispatch. Shutdown writes zero to the latter at `0x141882F6F` after context disposal. The positive stores are too early to mark allocation completion on this path. |
| PROVEN STATIC | Byte at `0x145E614D9` | The initial loader exchanges byte 1 at `0x141894CBD`, before the Starfield module call. Signed reset exchanges zero at `0x1418975FF` before replay and writes 1 at `0x141897C01` after re-entry. Its different placement across initial and reset legs and the module-guard bypass preclude a common productive-write completion interpretation. |
| PROVEN STATIC | Worker event and first-transition latch | State 0 calls SetEvent at `0x14187FB52` after initial loader return and intervening work. State 1 signals at `0x14187FBA4` after the reset call returns. `FUN_141898210` sets its own latch at `0x141898230` **before** entering `FUN_14187FBD0`. If worker control exists, the latter loops on a zero-timeout WaitForSingleObject at `0x14187FBF6` against control +8. The first-transition gate can order a qualifying request after worker progress. An event can signal after a guard bypass, an empty sweep, or via state 1 after a reset that skips replay. [manual-load admission](#application-dispatch-and-load-mode-predicates) |
| PROVEN STATIC | Reset and repeat construction | Signed-negative receiver mode at `0x141897167–0x14189716B` admits data-handler reset, then the index clear at `0x141897552` using the already-published context, distinct module teardown at `0x141897557`, loader replay at `0x141897B19`, and module re-entry at `0x141897B59`. The Starfield teardown uses `FUN_1409501A0` on the nonnull path and clears the Starfield guard at `0x14095028E` and `0x140951CDD`. Its known destructor removes a receiver at galaxy module +0x38. Type deregistration has a separate call. |
| PROVEN STATIC | Shutdown order for the separate lifetimes | In `FUN_141882BB0`, `0x141882F32–0x141882F4E` detaches the owner, disposes the DB and zeros the publication slot. The same body later calls the Starfield teardown at `0x141882FA8`, checks the galaxy module pointer at `0x141882FD8` and invokes slot +0 at `0x141882FE9` before zeroing its pointer at `0x141882FEB`. The galaxy vtable `0x144D5FAC8` resolves slot +0 to `FUN_14231DDA0 → FUN_14231DA10`, which deregisters `PerBiomeData` at `0x14231DAFB–0x14231DB02`. This order applies to that shutdown continuation. The reset clear and Starfield destructor examined above leave the publication slot and registration in place through the shown operations. |
| HISTORICAL RUNTIME OBSERVATION | Earlier startup and menu-return captures | The locally verified startup report has return sites `0x141883DCE / 0x141894C93 / 0x14187FA14` in its startup loader stack. The separately pinned menu-return report directly witnessed `0x141897535` (data-handler reset) and `0x141897B19` (loader replay). Both use the pinned executable hash. These observations locate their sampled upstream work. The SRR-013 title sample measures retained output later in its own process. [Startup report][startup] · [Menu-return report][menu] · [Title samples](allocation-validation.md) |

The same-build load-order callbacks, pending handler and application
service commands can reach reset conditional on the mode and receiver
read at dispatch. The signed reset path does not establish that an ordinary
Save2 load enters it. The known visual-demand receiver was previously
followed through its scene visit without a resolved edge to the allocator.
Exact flag execution, complete insertion visibility, title-epoch writes and
repeat counts need corresponding observations in a qualified epoch.
[observed scope](#observed-scope-and-unresolved-execution)

## Observed scope and unresolved execution

SRR-009's qualified `STOP500` interval establishes only **NOT_OBSERVED**
at the four armed sites during **84.281 seconds** of post-arm title/menu
coverage. It starts after arming and cannot exclude earlier startup allocation.
All **four** SRR-010 Save2 attempts are **INSTRUMENTATION_INCOMPLETE**:
they exited `0x80000004` approximately 15–16 seconds after the load marker,
before confirmed player control or scientific STOP. The cause is unknown;
execution was neither demonstrated nor excluded. Control A is a maintainer
report of an uninstrumented settled load without an independent receipt.
Control B reported settled gameplay under debugger-only attachment and has
an independently witnessed exit zero, but no allocator sensitivity and no
terminal event/receipt: its formal result remains **CONTROL_INCOMPLETE**.

SRR-013's initial pair timed out with four `STATE_INDETERMINATE` results.
Its later qualified pair measured four `STRUCTURALLY_POPULATED` components
at responsive title before save selection. SRR-017 subsequently established
a complete paired census of the admitted rooted store, with 3,211 typed
rows. These observations resolve retained-state accessibility; none joins
an individual slot write to startup, an ordinary Save2 load or a specific
queue completion. Exact vectors, receipts and comparison limits are in
[allocation validation](allocation-validation.md).

A normal late iterator return at `0x14094EF5C` orders completed synchronous
visitor calls and any focal stores reached in that invocation. It can also
follow an empty bucket or unsuccessful selection. A payload-qualified store
at `0x1407779FC` causally joined to `0x14094EF57` would identify a new Common
root write in that invocation; it would not cover cached-family reuse,
guard fallback, Special or Everywhere, which have different sites. An early
sweep can reach the same store. A retained sample alone identifies no
instruction. Open timing, queue, lifetime and persistence questions belong
only in [the research lead register](hypotheses.md).

## Static search and reproduction

The reproducible route reads a lawfully obtained matching executable as
file data. The tracked [PE decoder](../tools/srr011/inspect_pe.py) checks
SHA-256, AMD64 PE32+ and preferred base, then prints bounded decodes to
stdout. It neither starts Starfield nor opens or modifies Ghidra. The
qualified environment is CPython 3.14.3 x64 and Capstone 5.0.7.

```powershell
$image = '<path to the pinned Starfield.exe>'
python -B tools/srr011/inspect_pe.py $image functions 141898870 141881660 14231D000 14189A970 14187FEA0 14187F9D0
python -B tools/srr011/inspect_pe.py $image functions 141893EE0 141896280 141882BB0 1409518B0 14094E3D0 140593280 14077C470 140779610
python -B tools/srr011/inspect_pe.py $image data 144B3D9F0 10
python -B tools/srr011/inspect_pe.py $image data 1485F1500 C
python -B tools/srr011/inspect_pe.py $image functions 14008C050 140305FD0 1403061C0 140308070 140C80E60 140307FA0
python -B tools/srr011/inspect_pe.py $image window 1428CDBE0 430
python -B tools/srr011/inspect_pe.py $image functions 14233F2C0 142340990 142340AB0 1407873D0
python -B tools/srr011/inspect_pe.py $image scan 140779760 140777870 140779610 14077C470 144B3D9E8 140778600 14077D090 14077B1D0 14077A700 14077B910 145EA6000 1461DFA4C
```

For unwind metadata, read the three little-endian u32 RVAs at exception
entry `0x1485F1500`: begin `0x77C470`, exclusive end `0x77C491`, unwind
`0x541CC78`. Decode the begin VA and direct adapter call independently.
Vtable RTTI uses the preceding complete-object-locator pointer; the type
descriptor RVA is locator +0x0C, decorated name at descriptor +0x10.
The five original dispatch exports' 1,089 instruction starts agreed with
independent Capstone decodes. Existing matching Ghidra analysis can be
queried read-only with the [explicit-address exporter](../ghidra/README.md).

The decoder's reference census covers file-backed `.text`
`[0x140001000, 0x143A3EF6C)` and 236,427 selected exception ranges,
checking decoded rel32 branches, supported RIP-relative operands and exact
qwords in file-backed sections. It does not exclude computed references,
unknown indirect targets, short branches or unrecognized decodes. Exception
ranges can split a function; use checked `window` starts across those splits.
The original dispatch census found the two direct constructor callers and
the two receiver-vtable loads. Neighbor sweeps are distinct receivers:
`0x14094EEFD → FUN_140799490`, `0x14094EF26 → FUN_140AC7860`, and
`0x14094EFBD → FUN_14077C4A0 → FUN_140778600`. They do not establish
additional calls to the focal allocator merely by sharing a bucket.

Historical same-build upstream evidence is separately pinned:
[startup loader report][startup] blob
`b5e88cb244f303fe08088f5f65d9fae543f5e0a9`, and
[menu-return reset report][menu] blob
`6799d994d4cc2730909c55e2f708032f9798b1f0`.
These are custody-backed historical associations; the lawful-PE walk
independently reproduces the static edges. Save52's scoped
[load-readiness map][load] supplies the qualified manual-load context.
No retained CK static evidence bundle is a retail live trace.

[startup]: https://github.com/gooberpede/starfield-reference-handles/blob/7be6624893ef8a1abfdbbef7b50ed35e90b8f970/docs/experiments/pack-in-storage-reference-startup-construction.md
[menu]: https://github.com/gooberpede/starfield-reference-handles/blob/5dd46ff91d24761d9b67f4a25a07419c1e87bc0c/docs/experiments/subtype-3-menu-return-teardown-reconstruction.md
[load]: https://github.com/gooberpede/starfield-outpost-research/blob/dec9f4de5816f8e7c8f694b064d3298f8a6afad2/docs/experiments/resource-retained-population/d5ae-eligibility-readiness-map.md
