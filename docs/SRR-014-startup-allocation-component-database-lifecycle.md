# SRR-014 — Startup allocation and component database lifecycle

**STARTUP LIFECYCLE PARTIALLY RESOLVED — BOUNDED BLOCKS DOCUMENTED.** The
pinned retail image constructs the embedded component database and publishes
its address before the guarded galaxy type-registration call on the inspected
application startup route. File loading can submit zero-initialized
`PerBiomeData` edges. The generation visitor then synchronously borrows
the edges it finds and clears and conditionally fills their resource slots
in place. A normal return from the later PNDT iterator orders that invocation's
completed visitor calls. The iterator can return with no eligible work.
Its return does not identify a populated galaxy or a durable readiness state.
The same database address can survive the signed reset's clearing and replay.

SRR-013 directly measured four populated components at the responsive title card
before save selection. The pair describes those components and that window.
It does not identify the writing invocation, its timestamp or how many times it
ran. The original five-second attempt remains `STATE_INDETERMINATE`.
[Paired title observation](SRR-013-retail-title-paired-structural-observation.md) ·
[Original title attempt](SRR-013-retail-title-structural-observation.md)

| Evidence class | What the evidence supports |
| --- | --- |
| PRIOR ESTABLISHED | Retail construction and PNDT dispatch; conditional reset/replay; authored and CSV zero initialization; indexed payload writes, readers and clear; publication slot and the two stores. [SRR-003](SRR-003-retail-allocator-invocation-and-dispatch.md) · [SRR-011](SRR-011-planetary-allocation-execution-and-result-lifecycle.md) · [SRR-012](SRR-012-acquisition-evidence.md) |
| NEW STATIC FINDING | Publication and the guarded registration call share a normal startup continuation. The early sweep flag is the current value of the default-false `bImportCSVBiomeData:Data` setting. Database commands and readers participate in native synchronization with different modes. The late iterator return provides a local control-flow boundary because its resolved visitor calls the adapter inline and always returns continue on normal completion. [Startup evidence](SRR-014-startup-evidence.md) · [Database evidence](SRR-014-database-evidence.md) · [Sweep and productive writes](#sweep-and-productive-writes) |
| HISTORICAL RUNTIME OBSERVATION | Same-build startup loader frames, selected menu-return reset/replay and four paired populated title-card samples. The sibling observations locate upstream work. The title pair locates retained state. [Historical sources](#provenance-and-reproduction) |
| STATIC INFERENCE | The guarded startup sweep is the leading explanation for the sampled pre-save output. Other traversals or rewrites within the process window are not excluded by the pair. |
| OPEN/BLOCKED | Exact startup invocation and write provenance for the samples, startup flag value, cross-thread publication/ready-state contract, and ordinary save-load or cross-process behavior. [Lead register](SRR-014-lead-register.md) |

## Startup and reset ordering

The arrows show normal native continuation or the explicitly named dispatch.
The relation between the marked events [A] and [B] is unverified. The
[startup evidence](SRR-014-startup-evidence.md) supplies the worker and
application entry paths, source predicates and guard identities. The
[database evidence](SRR-014-database-evidence.md) supplies the submission and
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
predicate. [SRR-011 invocation and callback predicates](SRR-011-planetary-allocation-execution-and-result-lifecycle.md#invocation)

## Ownership and access

```text
Image owner at VA 0x1482EE300
  +0x8B0 published pointer ---+
  +0x2C0 embedded DB <--------+
           +0x30 queue-host link -> typed commands -> native callbacks
           +0x238 synchronization/control object
           +0x268 separate component index
           +0x358 reverse-key index reached by key-change handling
           +0x300 mixed edge index -> block descriptor -> typed edge
                                       +0x10 planet/type + target key
                                       +0x20 inline CTPerBiomeData
                                               +0x40 BIOM, +0x4C RSGD
                                               +0x50..+0x68 result words
                                  collector borrows ^      |
                                  writer clears/fills      v
                             matching reader -> caller-owned copy

  Targeted removal destroys selected payloads and can move entries.
  Context clear destroys/releases index contents. Embedded address can persist.
  Owner shutdown disposes context and clears published pointer.
  Galaxy-module teardown has a separate type-registration disposal route.
```

The collector stores the inline address computed at
`0x14077BDA5–0x14077BDB1` at `0x14077BE39`, so the work array owns
its pointer storage while the DB owns the records. The writer and checked
copy consumers enter through `FUN_142404230`. Insert, removal and clear use
the ticket path through `FUN_142404A80`. These guards qualify the examined
native callers. The write and copy callers use the shared-mode path, so guard
participation alone cannot establish mutually exclusive access to the seven
words. External inspection acquires no native guard. The [operation catalogue](SRR-014-database-evidence.md)
records identity, inputs, entry points, admission, effects and call-site scope.

| Operation | Preconditions and transition | Evidence |
| --- | --- | --- |
| Insert authored edge | Accepted PPBD or other admitted input supplies typed keys and a zeroed seven-word payload. Service executes the captured command and copies into the index. A duplicate-key search result alone is insufficient to infer replacement in the edge insertion primitive. | **PRIOR ESTABLISHED** initialization and command role. **NEW STATIC FINDING** guard and insertion behavior. [Database evidence](SRR-014-database-evidence.md) |
| Replay or import | The ENAM route can submit range removal before submitting new zero-initialized edges. The inspected CSV submission uses the same append callback as authored creation. Its reachability and possible presence ahead of the later sweep do not establish replacement or effective configuration in the observed title epoch. | **PRIOR ESTABLISHED** input and removal paths. **NEW STATIC FINDING** equal-key insertion behavior and setting attribution. [Database evidence](SRR-014-database-evidence.md) |
| Populate in place | A nonzero PNDT key and a collected payload admit a clear. BIOM and downstream selection tests govern stores. Every completed visitor can leave zero or nonzero slots. | **PRIOR ESTABLISHED** [SRR-011 result](SRR-011-planetary-allocation-execution-and-result-lifecycle.md#result); branch-level join below. |
| Lookup and copy | Zero planet key, missing range or missing matching BIOM returns false. Match copies the payload, including all seven words, to caller storage. A separately qualified consumer validates resource IDs by native FormID resolution and type. | **PRIOR ESTABLISHED** `0x140771F8B/0x140771FFD/0x14077200D`, `0x14079BC52/0x14079BC63`. [Readers](SRR-011-planetary-allocation-execution-and-result-lifecycle.md#readers-and-reuse) |
| Remove or clear | Removal erases the selected key range and notifies after the erase. Signed reset clears +0x268 and +0x300 before Starfield module teardown, with a reverse-key clear gated by its +0x10 header word. The examined shutdown disposes the published context before Starfield teardown and galaxy type deregistration. | **PRIOR ESTABLISHED** erase and focal clear. **NEW STATIC FINDING** reverse-key operation and joined shutdown order. `0x142409682/0x142409691`, `0x1424063DB/0x14240640C/0x142406418–0x142406430`, `0x141882F4E/0x141882FA8/0x141882FE9`. [Database evidence](SRR-014-database-evidence.md) · [Startup evidence](SRR-014-startup-evidence.md#return-reset-and-disposal) |

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
| PNDT admission | Callback requires the form type `0xBA`. The +0x54 key supplies the indexed range; a zero key or no collected work bypasses the per-biome loop. A zero seed changes reseeding at `0x140779C33–0x140779C6F`. [SRR-011 result](SRR-011-planetary-allocation-execution-and-result-lifecycle.md#result) |
| First payload pass | Both clear branches at `0x140779B00–0x140779B2E` zero the 28-byte field span. The clear occurs before BIOM resolution, so failure to resolve type `0xA0` can leave zeroed slots. The category-6 scan can write resource FormID to +0x68 at `0x140779B9F`; subsequent loop decisions test the actual written value. |
| Second payload pass | Nonempty work reaches `0x140779C86`. At `0x1407778F0–0x14077792B` +0x40 must resolve as BIOM, while a missing or incompatible +0x4C resolves to a null optional RSGD pointer. `FUN_140777E30` attempts the optional list and can fall through to the BIOM list when both selection pointers are zero. |
| Conditional results | Special needs the selected pair and shared count below eight before +0x64 is written at `0x140777971`. The Common path may write a new root at `0x1407779FC` with conditional descendant writes, copy a cached family at `0x140777AD1–0x140777AEA`, or explicitly zero +0x50 at `0x140777AEF`. The guarded branch can copy an eligible configuration at `0x140777B7E–0x140777B96`. [SRR-002 mapping](SRR-002-retail-static-reconnaissance.md#retail-mapping-on-the-pinned-image) |
| After the loops | The +0x268 lookup at `0x140779CD7` uses a different discriminator and gates coverage adjustments including payload +0x44. The follow-up at `0x14094EF5C` starts with a visitor that collects BIOM identities and can schedule jobs. The distinct final PNDT sweep at `0x14094EFBD` uses vptr `0x144B3D9C8`. Neither is needed for the focal Common/Special/Everywhere stores to precede the late visitor return. [SRR-011 readers and reuse](SRR-011-planetary-allocation-execution-and-result-lifecycle.md#readers-and-reuse) |

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

## Future observation boundaries

| Rank and native boundary | What would count | Accessibility, method and limits |
| --- | --- | --- |
| 1. Identity-joined per-biome Common root store at `0x1407779FC` during the late visitor | A nonzero EAX stored to `[RDI+0x50]` with RDI joined to an indexed target such as Kreet Mountains and `0x14094EF57` in the causal ancestry would identify that writing invocation. A complete negative only excludes the new-root path at this site in the covered scope. Reuse, guard fallback, Special and Everywhere have other sites. Early writes reach the same site from a different callsite. | Highest causal specificity. It requires authorized pre-title event capture with caller and payload identity. SRR-013's read-only sample cannot identify an instruction. A narrow event can reduce observer load, but handling can perturb early execution and must be qualified separately. Missing coverage or unreliable attribution makes a negative inconclusive. |
| 2. Return to `0x14094EF5C` from the late PNDT iterator, with an identity-qualified retained sample | A correctly attributed return establishes normal completion of the admitted visitor calls for that instance. A sample at the boundary can establish selected retained contents. Even nonzero contents do not alone attribute the writing instruction or distinguish output inherited from a prior visit. | One control-flow boundary per late sweep and less event volume than counting all inner stores. Requires authorized early control-flow observation plus a qualified sample if retained state is part of the question. A read-only title collection alone cannot establish this return. No return in a fully covered run may indicate bypass, a different path or abnormal exit, so entry and coverage witnesses matter. |

Both proposals require separate written authority for live activity.

## Provenance and reproduction

The input was retail `Starfield.exe`, file and product version `1.16.244.0`,
102,476,200 bytes, SHA-256
`7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28`.
All instruction locators are preferred VAs for image base `0x140000000`.
For example, publication slot VA `0x1482EEBB0` maps to main-image RVA
`0x82EEBB0`. The scenario was offline byte decoding on 2026-11-17 UTC.
No plugin/load-order input participated in the decode. The historical
observations retain their own scenario and data qualifications.
[Retail provenance](PROVENANCE.md#current-retail-identity) ·
[SRR-012 measurement contract](SRR-012-measurement-contract.md) ·
[Sample plan](SRR-012-sample-plan.md)

The starting HEAD was `fabf7dc9f2a8aa020d2ec8906d7df74cc725dcc7`, with
index SHA-256 `c4c4d061a69924e1eb45f8ff06bb3365196043290c3e41d365d37ec0604c4e5d`.
The supplied brief was the sole initial untracked file. Its SHA-256 is
`b1708de6b53032fc0fa5b32a161209c5d85fb4fcc59a86264b405fc3fbb0e0e1`.
It is preserved as a maintainer input outside the task delta.

Python 3.14.3 and Capstone 5.0.7 ran the existing tracked PE decoder. It
checks the image hash, AMD64 PE32+ format and preferred base before decoding
file-backed bytes. It reads the PE and prints to stdout. It neither loads the
executable as a program nor opens the Ghidra project. To reproduce the local
completion relation, pair the installed slot pointer with the iterator's
indirect call, resolve the visitor's always-continue normal return, then
follow the adapter call and the return address at the late callsite.

```powershell
$image = '<lawfully obtained matching Starfield.exe>'
python -B tools/srr011/inspect_pe.py $image data 144b3d9e8 18
python -B tools/srr011/inspect_pe.py $image functions 140593280 14077c470
python -B tools/srr011/inspect_pe.py $image window 140779610 14b
python -B tools/srr011/inspect_pe.py $image window 14094ef57 70
python -B tools/srr011/inspect_pe.py $image functions 140779760 140777870 140777e30 1407780b0
```

The startup and database evidence notes give their own replay commands.
Native bytes, raw decode receipts, private historical captures and local
Ghidra assets stay out of the patch. The verification route for static
claims is the tracked decoder plus a lawful matching executable. The
historical observations are custody-backed. Any release or redistribution
decision remains with the maintainer.

The local `handoff/sweep-replay.txt` receipt in SRR-014 custody preserves the
iterator, visitor, adapter, loader continuation and focal writer decodes
for review. Its SHA-256 is
`1e611e94da083113565973b9c3304062092bd2357d4a8f21cea6c6c70fbcef64`.
The sibling `handoff/drain-candidates.txt` receipt records the bounded
direct-reference census and receiver windows for nearby queue-drain calls.
Its SHA-256 is
`940a65c0faa6d0bdcf2a92806ef570517c8480c5cf4ff64d01e42b0a47b47d9b`.

The pinned sibling Git objects were available locally. The startup report
identifies the same SHA-256 and return VAs `0x141883DCE`, `0x141894C93`
and `0x14187FA14`. The menu-return report identifies the same SHA-256 and
calls at `0x141897535` and `0x141897B19`. Those records attribute the
upstream observations to separate scenarios. The SRR-013 sealed evidence
and inspector stay in their original custody.
[Sibling startup report](https://github.com/gooberpede/starfield-reference-handles/blob/7be6624893ef8a1abfdbbef7b50ed35e90b8f970/docs/experiments/pack-in-storage-reference-startup-construction.md) ·
[Sibling menu-return report](https://github.com/gooberpede/starfield-reference-handles/blob/5dd46ff91d24761d9b67f4a25a07419c1e87bc0c/docs/experiments/subtype-3-menu-return-teardown-reconstruction.md) ·
[SRR-013 inspector](SRR-013-read-only-allocation-state-inspector.md)

<!-- srr-014-review:start -->
**COMPLETE — independent internal challenge against AC1–AC8.** The
`challenger` reviewer reproduced the native locators against the pinned PE,
checked the historical claims and tested the diagrams, pseudocode, queue
and write boundaries against bypass, empty-work and alternate receiver
cases. Review prompted explicit registration-bypass and conditional
reverse-index clear branches, and lead dispositions for queue ordering,
callback effects and saved-slot persistence.

Reviewed substantive manifest SHA-256
`b6b1a61f0d71736b92eb93020888f3f5b18a7d5a4083eea4cb15289d02f9706e`.
The manifest records raw file SHA-256, two spaces, repository-relative
path and LF in sorted order for ten documentation paths. Only this
marked block is omitted from the dossier's manifest bytes.

The task patch passed independent forward and reverse replay against the
starting Git blobs with byte-for-byte comparison and an unchanged working
index. The original untracked brief was checked separately. Ending HEAD
and index SHA-256 matched their starting identities. The review cleared the offline
handoff. The scientific limits in the lead register still apply.
<!-- srr-014-review:end -->
<!-- srr-014-doc-corrections-review:start -->

## Documentation correction review

**COMPLETE — independent documentation check.** The `doccheck` reviewer
checked the startup ordering, the object-memory predicate, the B8 coverage
and history, and the Starfield spelling against the existing evidence.
The correction preserves the **PARTIALLY RESOLVED** scientific disposition
and the original independent review above. No new native investigation
or live observation was performed.

The reviewed three-file manifest SHA-256 is
`edcfdea104774f66e2577496cc60a6a490a67ae20e126d6bbeefc3106b145639`.
It records raw file SHA-256, two spaces, repository-relative path and LF
in sorted order, omitting only this correction review block from the
dossier's bytes. The correction-only patch replays and reverses byte-for-byte
against the captured pre-correction worktree. The prior SRR-014 patch,
HEAD and Git index retain their starting identities.

<!-- srr-014-doc-corrections-review:end -->
