# SRR-005 — Retail allocator live-observation preparation

Can an observer distinguish execution of the SRR-003
`StarField::ModuleState` → PNDT callback → planetary allocator path on
retail 1.16.244.0, including initialization before Save2 finishes loading?
This investigation prepares that experiment. Retail invocation remains
unobserved. The SRR-005 implementation brief defines the scope. The user-supplied brief was the sole untracked starting
path and remains outside the task patch.

## Pinned inputs

- Starting HEAD `41062476df24e981a8e7dfa1481f945218c4fc49`, tree
  `80a2cb81c29b621a2bf7ba3895939cb3244abe80`, with empty cached and tracked
  worktree diffs. Index SHA-256
  `271de2208302e4b09eaa73b5021d4f2006138565f1a9d9c52b8f3015c09f41b3`.
- Installed and analysis-copy `Starfield.exe`, 102,476,200 bytes, file and
  product version `1.16.244.0`, SHA-256
  `7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28`.
  Steam app `1716740` reports build `23518663`. The retained SRR-002 Ghidra
  report identifies `/Starfield.exe` with this import hash, preferred base
  `0x140000000`, language `x86:LE:64:default`, compiler ID `windows` and
  Ghidra 12.1.2 PUBLIC provenance. All present saved project files match the recorded import custody fingerprints.
  The fresh PE check is independent of the listing export. No Ghidra session
  was needed for SRR-005. [Provenance](PROVENANCE.md#current-retail-identity),
  [SRR-002](SRR-002-retail-static-reconnaissance.md),
  [SRR-003](SRR-003-retail-allocator-invocation-and-dispatch.md).
- PE machine AMD64, PE32+, image extent `0x89C2000`, dynamic-base bit set.
  Both vtable function-pointer slots have DIR64 relocations. Convert a
  preferred VA to RVA by subtracting `0x140000000`. Convert to live VA by
  adding the independently measured mapping base for that process. Code
  bytes and decoded targets must agree with the pinned PE after applicable
  relocation. Use the creation-event image handle for the backing-file
  hash and file identity, with the stopped process's mapped PE headers,
  machine, size and code windows as complementary checks. A disk file
  hash alone cannot authenticate in-memory instructions. All addresses
  in the experiment are retail. [Retail dispatch structures](structure-register.md#retail-dispatch).
- Project-authored sibling evidence was inspected in place. Reference
  handles revision `6a77579a184c64e0c080c8f3b7883c34bd17e24b`. Outpost
  research revision `d116bc63ff394b0156539161c8d1addfc902665a`. Exact files,
  hashes, executable and SFSE pins, and present save path are in the
  ignored input receipts. No sibling source or external dependency was
  incorporated into the tracked deliverables.

## Save2 qualification

The locally accessible original `Save2` hashes to HIST-0245
`1ac3d496e532b6286d983a1449946ba4fe34a34e66295c9d1d7da677772903d1`,
2,475,440 bytes, matching the historical capacity ledger and inventory.
The outpost `save-analysis/scripts/save_menu.py` 1.0.0 inspected the
first decoded stream and verified input custody. It reports Attila Kiraly,
level candidate 3, `Jemison - New Atlantis`, and 2h 5m of playtime.
Filename prefix identifies a manual slot. Original file mtime gives
14 August 2026, 4:34:32 pm Sydney under the reader's menu-time model.
A working copy's menu timestamp may follow its own filesystem mtime.
Record the working copy's projected label and use the other fields plus
its unique presence in the isolated namespace for selection. Later
Attila Kiraly Save25/Save39 are distinct files. Cao Tran Save52/HIST-0267
has a mature outpost network and is reserved for a separately selected
comparison.

The hash-bound historical player-location read resolves WRLD
`0001251B` (`NewAtlantis`). Proximity to the Lodge entrance is
maintainer-reported. Exact loaded position and tutorial/quest progression
are unknown. The two header version strings read `1.16.244.0`. Their
roles and the originating executable hash are unknown. The historical
presence matrix classifies this file as `NO_ACTIVE_OUTPOSTS_SUPPORTED`
within its bounded fingerprint. Its residual groups and engine authority
remain unresolved. The outside-to-inside Lodge crossing is an observable
same-character, low-intervention contrast. A fresh load could reuse
module state constructed before title, and the crossing could reuse
the same state or follow an unrelated path. A failed load, unavailable
door or untouched constructor leaves the target action inconclusive.

Sibling sources at the pinned outpost revision are
`docs/experiments/save-capacity-and-planetary-location.md`,
`save-capacity-location/capacity.csv` beside it,
`historical-save-inventory-triage.md` and
`historical-save-inventory/{inventory.json,presence-matrix.csv}`.
The frozen inventory recorded zero existing archives for HIST-0245 at
its measurement boundary. An independently verified backup for the
future run remains a gate. Save2 was only read here.

## Observer decision

| Method | What it can measure and why it ranks here |
| --- | --- |
| **Primary. Raw Win32 launch-under-debug, per-thread hardware execution stops** | Start the exact retail process under `DEBUG_ONLY_THIS_PROCESS`, with Steam already in its approved state. Process creation supplies the main image and initial thread before user-mode execution. Arm at that event and at every new-thread creation event before continuing it. Associate each event with the created process's handle and creation time. If the launch redirects to an unobserved helper or new PID, the startup experiment ends incomplete. A Steam launch followed by attach loses the pre-attach interval. Use simultaneous stable sites and no software patch, TF stepping or instruction emulation. Per-thread debug context, event delivery and resume still perturb scheduling. Source-level Win32 contracts and a local fixture justify developing this path. Retail launch compatibility, concurrent exception handling and failure recovery require qualification. [Win32 debugging events](https://learn.microsoft.com/en-us/windows/win32/debug/debugging-events). |
| **Fallback. Separately approved post-title hardware attach** | Use the same verifier and observation protocol at a stopped explicit attach barrier. Census existing threads reconciled with create/exit events and arm every new thread before continuation. Mark everything before complete readback as uncovered, including early construction and any previous load. Useful if a nominated post-title action produces a positive chain. A negative cannot decide whether the constructor ran earlier. Keep the session attached through normal target exit, as in the primary plan. Attachment and termination paths remain qualification gates. [DebugActiveProcess](https://learn.microsoft.com/en-us/windows/win32/api/debugapi/nf-debugapi-debugactiveprocess). |
| **SFSE/native early observer** | Installed SFSE advertises 0.2.21 for this retail build. The pinned sibling beacon example begins at `SFSEPlugin_Load` and creates a worker. The upstream startup code calls optional `SFSEPlugin_Preload` through the CRT `_initterm_e` path before normal global initialization and calls ordinary `SFSEPlugin_Load` later. A preload export is the earliest relevant plugin candidate. An observer would need a synchronous ready handshake there, evidence that SFSE startup hooks actually ran, and an independent trace placing preload ahead of the SRR-003 entry. Earlier loader/TLS work and handoff to a different process remain possible gaps. A worker snapshot/late message may see state after any sweep. A viable alternative would need a verified early loader phase and a synchronous, reentrancy-safe site capture installed before the constructor, with entry/exit continuity and safe lifetime across all threads. Hooks introduce code/control-flow, loader and exception side effects plus a deployment/cleanup surface. Its checkpoint and STOP journal ideas are adaptable. Startup timing and dispatch capture are unqualified. [SFSE startup code](https://github.com/ianpatt/sfse/blob/master/sfse/sfse.cpp), [plugin manager](https://github.com/ianpatt/sfse/blob/master/sfse/PluginManager.cpp), [0.2.21 release source](https://github.com/ianpatt/sfse/commit/48535cc). |
| **Software breakpoints via dbgeng/Pybag/x64dbg** | Can stop before a native instruction with a launch debugger and can inspect state after attach. Hot generic iterator hits would repeatedly patch/restore code and require thread-wide breakpoint and pending-step ownership. Reference handles reproduced post-detach `80000003` and `80000004` with exact byte restoration. The outpost transport had disposable successes and a separate disabled game path. One-shot software stops cannot gather both live frames across repeated dispatch while avoiding competing pending stops. Historical comparator only. |

The reference-handles `debugger/native/win32_hardware_observer.cpp` and
`debugger/native/README.md` provide an adaptable RF and event-ownership pattern.
`docs/experiments/live-starfield-observation-capability-recovery.md`
reports 20/20 multithreaded fixture trials and one bounded startup
smoke with two hits at a different site. Its successful smoke had zero
competing pending game hardware events. The saved report does not
qualify SRR-005's four simultaneous stops or post-title behavior. The
repository's subsequent post-title handle-lifecycle qualification failed.
Its `docs/experiments/debugger-multithreaded-breakpoint-lifecycle.md`
documents the restored-byte failure. The outpost
`debugger/exp0002a/native/{adapter.cpp,rf_core.h}` and `README.md`
record dynamic-new-thread retirement failure, a disabled live adapter
and a replacement fixture protocol that deliberately leaves later
threads unarmed. That protocol can miss the complete route. Its offline
evidence checks and survival split are adaptable. The sibling
`runtime/beacon-observer/{README.md,plugin.cpp}` supplies durable STOP
and partial evidence conventions. Outpost
`docs/experiments/beacon-observer/initial-live-session.md` records an
initial game startup with no SFSE/observer module and a retry with
verified READY at title. It establishes the need to check exact
launcher and module identity. It puts no bound on constructor coverage
before observer readiness. The reader can be reused as-is for
offline Save2 identification. Existing live capture binaries, recipes
and authority are excluded from this run card.

## Sites and causal join

Use four simultaneous execution locations on each covered thread.
These are design assignments to DR0–DR3. The fixture exercised two sites.

| RVA | Observation and qualification |
| --- | --- |
| `0x9518FD` | Module pointer comparison before the branch. Read the qword at base + `0x61E2288` and the compared RSI. Zero allows the construction route. Nonzero can bypass it. A later pointer snapshot cannot recover the earlier decision. |
| `0x5932EF` | Generic iterator's pre-call `call [rax+0x10]`. Capture RSP, RCX = R14 receiver, RAX = vptr, RDX = current nonnull form. Require `[RCX] == RAX == base+0x4B3D9E8` and `[RAX+0x10] == base+0x77C470`. The duplicate slot at +8 is insufficient. The iterator has pushed R14 and subtracted `0x30`, so `[RSP+0x38]` is its saved caller return. Accept `0x94E57C` (early; source `0x94E577`) and `0x94EF5C` (later; source `0x94EF57`). Count other iterator traffic as nonfocal controls. |
| `0x77C470` | Callback entry before `sub rsp,0x28`. Join to the most recent iterator candidate in the same physical frame, with callback RSP = iterator RSP−8, saved return `0x5932F2`, same receiver/vptr/slot and same RDX form. Recheck the sweep return at callback RSP+`0x40`. Record type byte at form +`0x2E` if safely readable. Treat a valid callback hit as invocation even if the form is rejected or type unavailable. |
| `0x779760` | Orchestrator entry before its prologue. Require `[RSP] = base+0x7796D7`, the return from direct call `0x7796D2`. Validate the entry's RCX as the address of the adapter's saved form pointer and RDX as the address of its saved context pointer. Match form and stack ancestry as specified below. |

For allocator-entry RSP `S`, the adapter's seven pushes and
`sub rsp,0x40` plus the direct call account for `0x80` bytes.
The callback's `sub rsp,0x28` and its direct call add `0x30`. Thus
`[S+0x80]` must be the callback-to-adapter return `base+0x77C487`,
`[S+0xB0]` must be the iterator resume `base+0x5932F2`, and
`[S+0xF0]` must be the same focal sweep return. Check
`[S+0x50]` for the inherited R14 saved by the adapter, matching the
iterator receiver, and check that RCX = `S+0x98`, RDX = `S+0x90`,
and `[RCX]` equals the callback's PNDT pointer. No dereference of the
context object is needed. The latest qualified callback record at
`S+0xB0` must be linked to its own latest iterator event at `S+0xB8`.
A newer conflicting frame observation supersedes the old one even when
the pointer or site repeats. Thread birth identity, process creation,
module and instrumentation epoch must agree. Reject ambiguous, duplicate
or out-of-order chains, including any intervening health/coverage gap
that could admit unseen frame reuse. Use checked stack bounds and
validate against the pinned prologue and unwind layout. Do not scan
memory for plausible return values. [Retail native predicates](SRR-003-retail-allocator-invocation-and-dispatch.md#native-path-and-predicates).

Form identity is the session-scoped object pointer and its validated
type. SRR-003 supplies no verified universal retail FormID offset for
this capture. A verified ID can be added in a later design with its
own provenance. Sample the qualified module qword and early-sweep flag
byte at base + `0x5EA6000` with the process stopped when readable.
Label those values as samples at the event. The saved source return
identifies which sweep ran. Only a stop at the flag comparison itself
could directly observe its controlling operand there. Null bucket
entries and empty buckets can bypass the generic call. A type mismatch
can stop at the callback. Empty biome work can still reach the planetary
orchestrator and bypass the per-biome call at `0x779C86`. Per-biome
arrival is outside the four-site measurement.

### Evidence record and handling

Use a versioned UTF-8 JSONL journal and a distinct final receipt with
the last durable sequence, record count and SHA-256 of the closed
journal. Each row carries run ID, monotonic sequence/QPC and UTC,
observation and operator phase, PID plus creation time, TID plus
thread creation time or event generation, and source of those identities.
Record target role, image hash/base/extent, file and mapped-image identity,
configuration digest, PE preferred base, site RVA and actual address.
Native rows carry exact register values and relevant checked reads,
with address, width, value or unavailable/error reason. Record
predicate gate, caller return and normalized RVA, receiver/vptr/slot,
form/type, guard and flag samples and whether they were operands or
snapshots. At downstream entry include the direct call, exact saved
returns, linked ingress sequence numbers, and the justification for
each join. Unknown identity or failed reads invalidate the claims that need
them. If a missing read could hide a focal invocation or prevent joining
an otherwise eligible event, mark that interval incomplete for the
affected outcome. Count a definite wrong vptr/source as a rejection.
Record an uncertain predicate as unknown. Event rows carry exception code/address/chance, debug status,
RF and ownership verdict, continue result, thread coverage changes,
writer and synchronization state. Keep process and per-window outcomes
independent of journal completeness.

- **STATICALLY_REACHABLE** is the retained static result before a live attempt.
- **OBSERVED_INVOKED** requires a durable joined iterator and callback
  event, even if the allocator pair is unavailable.
- **OBSERVED_REACHED_ALLOCATOR** requires the durable, same-invocation
  three-event chain through orchestrator entry.
- **NOT_OBSERVED** reports zero confirmed focal invocations in a named
  window with verified coverage, reconciled event counts and successful
  final flush. A qualified invocation without downstream evidence stays
  **OBSERVED_INVOKED**. The journal also reports allocator coverage or
  unresolved arrival independently. The broader causal or gameplay
  question can still be inconclusive.
- **INSTRUMENTATION_INCOMPLETE** marks an identity, coverage, correlation,
  writer or boundary gap for the affected window. Preserve earlier
  independently valid positive evidence with that limitation.
- **TARGET_FAILED** records an unexpected crash, fault, forced
  termination or loss of functional progress. Retain exit code or
  exception/progress evidence, whether evidence was durable, and observed
  or unknown observer contribution. Record this independently of the
  scientific status.

Process debug events serialize the stopped reads. Arm only free,
verified debug-register state. On each first-chance execution hit,
require known process/thread, enabled owned slot, matching RIP and
exception address, exact DR6 reason and no conflicting TF/debug cause.
Continue an owned hit with RF for one instruction and verified context
handling. No RIP rewrites, blanket handled exceptions or active rearm
cycles. Qualify the exact startup loader event from the pinned OS and
mapped ntdll. Pass unrelated first-chance exceptions through with
`DBG_EXCEPTION_NOT_HANDLED`; record unknown or second-chance events
and close the science window. At the loader stop, boundary checkpoints
and owned hits recheck slot configuration and thread inventory. Record
the loader stop separately from the arm timestamp and initial resume.
A successful setup readback is point-in-time evidence. Missing readback,
unexpected native modules or credible context changes that could
interrupt coverage invalidate a quiet window. Even a clean window
bounds only this debugged process and its qualified assumptions.
Debug registers and RF, process pauses and debugger presence are
observable interventions.

Use bounded in-memory pending frame tables and a fixed-capacity writer
queue. Fold nonfocal traffic into counters, including wrong vptr/slot
or return and read errors. Keep the first durably linked iterator
and callback pair per sweep and invocation phase, even if its form type
is rejected, unreadable, or the allocator pair is absent. Preserve
the first verified allocator chain per sweep and arrival phase with
its own precursor rows, all health transitions and audited batch counts.
Subsequent events still undergo ownership and continuation processing.
Maintain active frame tokens across ordinary phase markers, retaining
both source and arrival phases on a cross-boundary chain. Coverage
loss, thread exit or a newer observation of the same frame invalidates
the corresponding token. A STOP boundary closes eligibility for new
scientific observations. Reconcile attempted, accepted, sampled,
dropped, continued, flushed and uncommitted sequence ranges. Derive
queue size from disposable burst tests with a memory budget, and make
overflow an explicit incomplete boundary, never sampling success.
Batch writes outside the stopped-event path and acknowledge each
phase marker and STOP only after its evidence through a known sequence
has drained and flushed. Inspect the last verified prefix on failure.
Periodically check C: and D: space against the projected remaining
writes and the 40,000,000,000-byte floor. Stop acquisition on backpressure,
disk failure or coverage loss. Operator completion is based on named
transitions, with a separate emergency liveness watchdog selected in
the live approval for recovery. Neither elapsed time nor evidence
volume decides whether the engine invoked the path.

## Offline qualification

- Rechecked the five direct edges and post-call RVAs, iterator operand,
  prologues and adapter argument locations with Python 3.14.3 /
  Capstone 5.0.7 on the pinned PE and cross-checked the saved Ghidra image
  identity. Read the relocation directory and verified exact DIR64 slot
  entries. The code and derived locators remain local.
- Read the Save2 header with the pinned sibling scripts, compared the
  recorded digest and length, and preserved the input.
- The local synthetic correlation test passed six groups. It requires
  separate iterator, callback and allocator rows. Controls cover both
  sweeps, cross-phase correlation, missing precursor rows, duplicate,
  reordered and superseded frame observations, nested frames, PID/TID/
  creation/epoch/base mismatches, wrong form/receiver/slot/return,
  interrupted continuity and missing flush. It also exercises invocation
  with a rejected or unreadable type. It cannot validate live stack reads.
- Built and ran the isolated amd64 self-debug fixture on Windows build
  19045 using MSVC 14.51.36231 / Windows SDK 10.0.26100.0. At process
  creation and subsequent thread events its two slots passed readback.
  The initial thread and one explicit worker each hit both sites once,
  with RF continuation and verified normal child exit. A repeat placed
  the initial thread's first site in a process-attach TLS callback
  and its second in the child main routine. Both hits arrived in order. A loader-created
  thread also armed and had no target hits. The first build attempt
  rejected SDK switch syntax before compilation. The corrected invocation
  passed. No game path is accepted by the fixture. It has no detach
  workflow, process-wide drain test, retail launcher, or game data
  decoder. Its watchdog bounds only disposal of its own child.
- Remaining engineering gates are a four-site disposable controller
  with startup, simultaneous/multithread burst, loader/relaunch refusal,
  exact frame/receiver readback, zero-hit, coverage gap, STOP, writer
  failure, unrelated exception, crash and partial-recovery controls.
  Test owned and pending exception handling while retiring, and repeat
  through exact-process normal exit. Pin the actual source and binary
  after those tests. The fixture and schema qualify prerequisites for
  development. They provide no game-qualified observer binary.

The exact historical checks are custody-only and used the ignored
`check-sites.py <installed-PE> <SRR-002 identity.tsv>` and
`test-correlation.py` with Python `-B`, and `build-fixture.cmd` under
`.local-work/codex/SRR-005/`. The first reads disk PE and retained
metadata. The second uses synthetic records. The build writes its EXE/OBJ
beside its sources and executes that disposable program alone. Redirect
outputs in the same ignored task directory. These checks do not open or
write the Ghidra project. A public verification route is the
[SRR-003 procedure](SRR-003-retail-allocator-invocation-and-dispatch.md#reproduction-publication-and-next-experiment)
with a lawfully obtained matching PE. Current synthetic controls use
the [tracked SRR-006 fixture tooling](SRR-006-four-site-hardware-observer.md#reproduce-the-fixture-controls).
The privately retained, hash-identified Save2 is an optional input to a
separately approved Stage B. Launchability, engine execution and Save2's
live behavior remain held claims. Private paths, raw listings,
compiled fixtures and detailed receipts stay local.

## Proposed live run card

**Stage A, startup qualification.** Use a fresh process and an empty
test Saves namespace. Follow steps 1–3 and 5–7. The responsive title
marker closes the science window. Flush STOP and quit normally.
There is no working copy in this stage.

**Stage B, Save2 experiment.** With additional approval and Stage A's
verified launch, capture and retirement receipts, begin another fresh
process under the same pinned setup. Repeat steps 1–3, using the
verified Save2 working copy, then perform steps 4–7. Preserve startup
evidence in this process too. A qualified zero in Stage A need not
prevent Stage B. A coverage, process or custody failure does.

1. **Sign-off and exact configuration.** Freeze the tested four-site
   observer's source, compiler/SDK/OS and debugger binary hashes, schema,
   launch arguments, log location and tested recovery behavior in the
   new live brief. Target the pinned Steam build and executable above.
   Primary uses direct Win32 debugging, SFSE and observer plugin absent,
   with zero other native add-ons in the isolated retail test profile.
   Freeze the exact ESM/Creations order, data and config hashes, including
   autosave settings and test launch data. Compare recorded save/master
   requirements against that profile. Stop on mismatch or unexpected
   modules instead of substituting SFSE, attachments or updated
   executables. If direct startup under the approved Steam state requires
   handoff to another process, report incomplete and stop. A new plan may
   authorize the post-title fallback with its own scope.
2. **Protect storage before starting.** Close any existing instance.
   Inventory local active and Steam remote namespaces, cloud enabled
   state, sync status, file identities, lengths, hashes and timestamps.
   Verify originals and a separate backup accessible outside all active
   and sync paths, using independent reads and a restoration dry run
   into isolated storage. In Stage B hash Save2 source, backup and
   working copy separately. Use a clean Windows test profile or otherwise
   independently qualified configuration with a dedicated local Saves
   namespace. Verify it is empty for Stage A and contains only the
   verified working copy for Stage B. Disable Starfield Cloud for
   the test session under future authorization and validate isolation
   and no pending conflict before any launch. Keep original active
   directory and all protected saves outside the writable game namespace.
   Disable autosave/exit saves where the approved configuration supports
   it, and treat any unexpected output as working-namespace evidence.
   No game install file or original save is part of cleanup. See
   sibling `docs/SAVE_PROTECTION.md` at the pinned revision.
3. **Startup to title.** Mark run begin and arm before continuing the
   initial create-process event. Record each new thread's arm result.
   Have the operator verify responsive main menu without loading a
   save, then issue and confirm a title marker. Generic iterator hits
   with different receiver/source are natural discrimination controls.
   No such hit is required if the engineering controls already passed.
   A matched chain before title is a positive startup observation.
   A startup miss with process or coverage gaps remains incomplete.
4. **One primary load, one conditional contrast.** Mark and flush
   `LOAD_BEGIN` before choosing the unique Attila Kiraly level 3,
   Jemison – New Atlantis, 2h 5m candidate from the isolated namespace.
   Compare the local display timestamp/working-copy receipt when shown.
   No Continue shortcut, menu ordinal or alternate sample. Cancel and
   seal partial evidence on ambiguous row, missing-content prompt or
   unexpected data. Mark `PLAYER_CONTROL` when the loaded state is
   visibly responsive and location/quest context has been recorded.
   If outside the Lodge and its normal entrance is usable, mark
   `LODGE_BEGIN`, enter once using ordinary interaction, and mark
   `LODGE_END` after the responsive interior appears. Skip the
   contrast with a recorded reason if progression or position prevents
   it. No travel, reload or save is needed. Markers bound operator
   phases and do not themselves establish engine causation.
5. **Stop and retain.** STOP closes the scientific interval while
   the debug loop continues consuming and servicing owned events.
   Drain/flush the journal and record durable sequence, health and
   any excluded windows. For normal retirement keep the dedicated
   debug connection through user-initiated Quit to Desktop. After
   the science stop, the qualified policy may leave the stable
   slots owned through exit and count only retirement traffic.
   Account for thread exits, including the last thread at the
   exit-process event. Continue that event, then independently wait on a
   separately retained handle for the exact process and record its exit
   code. Windows releases its event-owned handles during this sequence. No in-session detach is needed. A
   surviving, responsive title and interior plus exit zero are process
   observations. A durable chain is scientific completion for its
   named window. Complete capture and zero hits still leave global
   execution and cache questions open.
6. **Emergency and crash.** Stop evidence acquisition on storage,
   coverage or control failure, mark partial where possible and
   keep servicing owned events. Retain the controller and exact
   process handle. Preserve unrelated exception disposition, last
   verified sequence, logs, exit status and available crash metadata
   in the local evidence root. If the game cannot quit, use only the
   preapproved, fixture-tested emergency path against that exact
   experimental process handle. Pin the controller-exit policy as
   part of that test. Win32 defaults to killing debuggees if the
   debugging thread exits. Turning that off implies implicit detach
   and would need its own qualification. Explicit permission is required for forced
   termination. While stopped on an unverified event, use the tested
   recovery and log the disposition before releasing it. Never abandon
   the session by killing the debugger or assume detach success clears
   pending events. No automatic restart, crash upload or Steam conflict
   resolution. Freeze the resulting save/cloud namespace until verified.
7. **After exit.** Rehash protected originals and backups, and the
   working input when Stage B used one. Compare
   inventories, protected installs, analysis evidence and configs to
   their starting values. Isolate any unexpected files. Operator
   verifies Steam remote inventory and prior Cloud setting after
   cleanup, then restores settings only if the protected originals
   are intact and there is no pending conflict. Retain logs locally,
   record permitted cleanup of experimental files, and escalate
   any discrepancy before enabling synchronization.

The first later live authorization should cover an isolated,
no-save startup-to-title trial only. It must name the pinned observer,
test profile, Cloud isolation, expected debug-register and exception
control operations, journal directory, normal exit and exact-child
emergency recovery. A subsequently approved Save2 phase additionally
requires permission for backup verification, a dedicated working
copy and save namespace, the one load and conditional Lodge crossing,
and cleanup. No prior sibling authorization carries over.

## Handoff

Ending HEAD and index bytes agree with the starting state. The only
tracked diff is the documentation index. This dossier and the supplied
brief are the only untracked paths outside ignored local work.
The protected-input receipt rechecks 56 exact file hashes, including
both executables, Save2, the retained Ghidra project and sibling
dependencies. The selective SFSE live-precedent receipt is separate.

Local work and verification are under `.local-work/codex/SRR-005/`.
The patch is `.local-work/diffs/SRR-005.diff`. The patch includes this
dossier and its index link. Check the end-state and replay receipt
for Git state, protected-input comparisons, UTF-8/link checks,
disk-space projections and isolated byte-for-byte patch replay.
The original brief is retained locally. Earlier review identities
remain in their original documents.

<!-- review-status:start -->
## Review status

**COMPLETE.** Independent internal challenge accepted AC1–AC7 for preparation
after rework on the three-event join, callback-only evidence,
startup coverage and the two authorization stages. The reviewer
independently checked the native stack arithmetic, PE and Save2
identity, fixture and synthetic evidence, protected-input receipts,
and the final patch replay. Retail launch, sustained four-site
coverage, process recovery and allocator execution on this build
remain open.

Reviewed substantive manifest SHA-256
`887010ae04a1f407a588f9215269db798a5e973b4d340eebd5b8a457fdfe1513`.
The manifest lists each file's SHA-256, two spaces, its
repository-relative path and LF, sorted by path. Only this marked review
block is excluded from the dossier digest. The local independent challenge
and final patch verification are under
`.local-work/independent-review/SRR-005/`.

<!-- review-status:end -->
