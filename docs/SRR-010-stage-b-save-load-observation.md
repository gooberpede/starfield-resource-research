# SRR-010 — Stage B save-load observation

## Final disposition

**CLOSED — INCONCLUSIVE; RESUMABLE.** Save2 allocator execution was
**neither demonstrated nor excluded**. All four authorized Stage B
loads with the four-site observer ended before confirmed player control
or scientific STOP. The attempts and evidence custody are complete.
The primary experiment remained incomplete, and all four load windows
retain `INSTRUMENTATION_INCOMPLETE`.

The four target exits returned `0x80000004` approximately 15–16 seconds
after the durable load marker, including time for the operator to select
Save2. None recorded an owned research-site hit, a focal invocation, a
correlated allocator arrival, or a corresponding delivered single-step
exception. The cause of these exits remains unknown.

The first observer, reduced load-period polling, census-only load
admission, and D5B-informed event-held sampling all reached the load
boundary. Each of their retail Save2 trials ended before player
control. Repeated incomplete loads left this phase with no qualifying
Save2 observation. A renewed investigation should first identify a
specific trigger and explain which part of its lifecycle would be
observable. See the [resumption gate](#resumption-gate).

### What the evidence supports

- [SRR-009](SRR-009-retail-debugger-admission-and-stage-a.md#finding)
  qualified `NOT_OBSERVED` for 84.281 seconds across two verified
  post-arming title and menu windows sealed at STOP 500. The earlier
  scoped Stage B pre-load findings stay with their original attempts.
- Control A is the maintainer's report of an ordinary, uninstrumented
  Save2 load to settled gameplay and normal Quit, without independently
  captured receipts.
- [Control B](#live-control-b--16-november-2026) reached operator-confirmed
  settled Save2 gameplay under debugger-only attachment and sealed its
  operational endpoint. The independent witness reported normal exit
  0. The missing terminal debugger event and receipt left the formal
  result `CONTROL_INCOMPLETE`. The observer was administratively closed
  after verified game exit. Control B had no allocator detection
  sensitivity.
- Disposable tests established four-site sensitivity and causal joins
  under their fixture conditions, including chains spanning phase
  markers and controlled STOP and failure paths. They did not establish
  that the retail allocator ran during Save2.

The histories below retain their original conditions, dispositions and
review blocks. Their run cards and approval proposals are historical.
The authorizations for the four attempts have been consumed.

## Resumption guide

### Measurement and decision trail

The question is whether the known planetary allocation path executes
while loading the existing Save2. The [scientific contract](#scientific-contract)
fixes DR0–DR3 respectively at `0x9518FD`, `0x5932EF`, `0x77C470`,
and `0x779760`. `OBSERVED_INVOKED` requires the validated focal
iterator-to-callback join. `OBSERVED_REACHED_ALLOCATOR` additionally
requires a correlated orchestrator arrival. A qualifying chain can
cross phase markers while its process, thread lifetime and causal
evidence remain valid. Scoped `NOT_OBSERVED` needs verified coverage
and the scientific STOP seal required by the reviewed protocol.
A plain site hit or a quiet interrupted load is insufficient.
`INSTRUMENTATION_INCOMPLETE` preserves those limits. None of the four
loads reached confirmed player control, post-load observation or the
optional Lodge crossing.

| Attempt | Method and result | Private run directory and manifest filename |
| --- | --- | --- |
| [First](#live-result--15-november-2026) | Initial four-site observer. Full load-entry sweep. Exit after 16.184 s | `stage-b-live-20261115T091730Z/phase2-evidence.sha256` |
| [Second](#second-live-attempt-with-the-recovery-observer--15-november-2026) | [Deferred load-period timer sweeps](#offline-observer-recovery). Full load-entry checkpoint retained. Exit after 16.067 s | `stage-b-recovery-live-02/attempt2-evidence.sha256` |
| [Third](#third-live-attempt-with-census-only-load_begin--15-november-2026) | [Census-only load entry](#instrumentation-strategy-after-the-two-save2-attempts) replaced the extra suspension and slot sweep. Exit after 15.349 s | `stage-b-strategy-live-03/attempt3-evidence.sha256` |
| [Fourth](#fourth-stage-b-attempt-with-the-d5b-recovery--16-november-2026) | [D5B-informed recovery](#scientific-status-and-d5b-recovery) used event-held periodic sampling, full operator checkpoints and expanded held-thread checks. Exit after 15.686 s | `stage-b-d5b-live-04/attempt4-evidence.sha256` |

Times are marker to native exit, including operator selection time.
Each linked record identifies its own challenger review, prefix digests,
exact exit and postflight. All four observers exited after publishing
terminal receipts and none required administrative termination. Normal
operator Quit and clean retirement were unexercised in those four
runs. Protection checks verified 98 Documents and 95 Steam remote
protected pairs, both designations and zero unclassified entries per
run. Control B recorded one incidental Documents exit-save
replacement, which remains documented separately.

### Source, builds and verification

Start with [SRR-003's static dispatch evidence](SRR-003-retail-allocator-invocation-and-dispatch.md),
[SRR-005's sites and predicates](SRR-005-live-observation-preparation.md),
[SRR-006's fixture build](SRR-006-four-site-hardware-observer.md#reproduce-the-fixture-controls),
[SRR-009 admission and evidence](SRR-009-retail-debugger-admission-and-stage-a.md)
and the [research workflow](research-workflow.md).

The [observer](../tools/srr006/observer.cpp), [correlation](../tools/srr006/correlation.h),
[window checks](../tools/srr006/window_evidence.h), [journal](../tools/srr006/journal.h),
[native fixture](../tools/srr006/fixture.cpp), and [assembly](../tools/srr006/fixture.asm)
are project source. See also the [phase marker publisher](../tools/srr006/stage_b_marker.py)
and [independent exit witness](../tools/srr008/watch_exit.py). The Stage B additions are in the reviewed patch stack
and some are absent from the starting Git HEAD. Replay the ordered stack
on the recorded baseline for a clean reproduction. The latest frozen
source and exact candidate are pinned by the
[D5B qualification](#offline-qualification-and-proposed-run-card).
The first, second and third observer identities are in the
[original qualification](#implementation-and-qualification),
[recovery review](#offline-observer-recovery), and
[strategy review](#instrumentation-strategy-after-the-two-save2-attempts).
The [Control B qualification](#control-b-debugger-only-qualification)
pins its separate debugger-only binary.

For a future **disposable** qualification, use the SRR-006 x64 native
recipe from an MSVC 14.51.36231 shell with Windows SDK 10.0.26100.0.
Assemble `fixture.asm` with `ml64`, then build `observer.cpp` and
`fixture.cpp` with the fixture object, `advapi32.lib`, `/O2 /EHsc
/std:c++20` and linker flags `/OPT:NOICF /Brepro`. The ignored
`d5b-recovery/final-build/build.cmd` under the SRR-010 custody root
records the exact qualified recipe. Use fresh output subdirectories
under an existing output root. The project scripts
[`qualify_stage_b.py`](../tools/srr006/qualify_stage_b.py),
[`qualify_stage_a.py`](../tools/srr006/qualify_stage_a.py),
[`qualify_d5b_admission.py`](../tools/srr006/qualify_d5b_admission.py),
and [`qualify_control_b.py`](../tools/srr006/qualify_control_b.py)
take the observer binary and output directory. The qualified environment
used Python 3.14.3 x64 with `-E -B`, matching native `ntdll.dll`, and
40,134,217,728 caller-available bytes on C: and D:. See the
[qualification prerequisites](#implementation-and-qualification).
[`compare_d5b.py`](../tools/srr006/compare_d5b.py) takes baseline and
candidate Stage B result directories. Matching retail executable data
is required for the separate retail profile check.

All live directories in the table are relative to the ignored
`.local-work/codex/SRR-010/` custody root. The Control B capture is
`control-b-live-01/`, indexed by `control-b-live-evidence.sha256`
and `steam-attribution-supplement.sha256`. The Stage B attempt sections
identify their individual digests and challenger reviews. The fourth
manifest SHA-256 is
`7e4a18c7c1d2c25c84f05e4092d6e92338aea5a82b5ff2da4b91f54e32614317`.
The Control B primary manifest SHA-256 is
`1794504690e29c180f1116ba4e6c2ab52349e9144d2da0c258d30e937a9b798b`.
The [SRR-009 proof](SRR-009-retail-debugger-admission-and-stage-a.md#evidence-and-verification)
identifies the STOP-500 seal and private `postflight-check.json`.
The [D5B comparator](#prior-art-and-scope) pins `pilot-evidence01.zip`
and its journal from the sibling project. Its Save52 and Build Mode
workload supplies prior art for event handling.

With authorized access, verify each evidence manifest's SHA-256
against the linked dossier, then rehash its listed files. Paths starting
with `.local-work/` in the newer manifests are repository-relative.
The earlier per-attempt manifests use paths relative to the manifest.
The [STOP verifier](../tools/srr006/verify_stage_b_stop.py) accepts a
capture directory, run token and STOP sequence for a run that actually
published a scientific seal. Retained terminal and phase prefixes for
the four aborted loads support replay of the evidence through their
watermarks. Those prefixes do not qualify as STOP seals. Private saves,
raw captures, proprietary images and retained observer binaries are
local artifacts. A clean applied source tree can reproduce the method
with lawful inputs. Historical live verification requires access to
the preserved records.

### Resumption gate

To reopen SRR-010, identify the new scientific question and the
observation window needed to answer it. Consult the preserved evidence
and the [scientific contract](#scientific-contract). Document any changes
to instrumentation and the coverage limitations of the proposed window.
Independently qualify and pin the candidate, then obtain fresh written
maintainer authorization before any live work.


<!-- srr-010-closure-review:start -->
### Independent closure review

**COMPLETE.** The independent internal challenger accepted
`CLOSED — INCONCLUSIVE; RESUMABLE` and found the documentation ready for a
separately approved commit with the reviewed SRR-010 patch stack.
The review checked historical scientific scope, retained evidence,
resumption links, qualification commands and task-only replay.

Reviewed substantive manifest SHA-256
`cb46fddb130920d333d6b4ec1758b28aa0a963437c44ecc6eada2f6b4d596906`.
Independent review SHA-256
`f09ddfa531c234e2e32e3c983490d893587c74621a0baea976bb424a5e584c08`
at `.local-work/independent-review/SRR-010/closure/review.md`.
Only this marked block and its following blank line are excluded from
the substantive dossier digest.
<!-- srr-010-closure-review:end -->

## Fourth Stage B attempt with the D5B recovery — 16 November 2026

**`INSTRUMENTATION_INCOMPLETE`.** The operator initiated the single
Save2 load. Starfield exited with `0x80000004` before responsive player
control, so the post-load and optional Lodge intervals were not
reached. The native debugger exit event, retained target handle and
independent exit witness all reported the same status. The only
delivered exception was the verified attach break-in. The run provides
no delivered single-step exception, faulting instruction or explanation
for the exit. Save-load resource allocation remains unresolved.

| Observation window | Boundaries and coverage | Focal invocation | Allocator arrival |
| --- | --- | --- | --- |
| Startup | Pre-arming, through sequence 430 | `INSTRUMENTATION_INCOMPLETE` | `INSTRUMENTATION_INCOMPLETE` |
| Post-arming title | 430–472, both endpoints verified with three event-held samples, without scientific STOP | `INSTRUMENTATION_INCOMPLETE` | `INSTRUMENTATION_INCOMPLETE` |
| Menu and Save2 selection | 472–505, full menu check followed by a census-only load boundary, with no delivered menu events | `INSTRUMENTATION_INCOMPLETE` | `INSTRUMENTATION_INCOMPLETE` |
| Load in progress | 505–607, verified load opening, interrupted before a full player-control endpoint | `INSTRUMENTATION_INCOMPLETE` | `INSTRUMENTATION_INCOMPLETE` |
| Post-load and Lodge | Unreached | — | — |

All four sites recorded zero owned hardware hits. No focal chain was
started, joined across phases, or left unresolved in the retained
journal. RF/DR6/TF continuation on an owned research hit was unexercised.
The load marker to native exit measured 15.686 seconds, including any
operator time before selection. Its native events were 92 thread exits
and the process exit. One event-held slot check occurred during this
interval. There were eight idle identity/mapping checks. A transient slot
displacement restored between sampled readbacks would remain undetectable.

### Admission, coverage and terminal evidence

The exact frozen observer
`e907b0f7db771db25c3721d726c6cf1f69d35d4e586f5e0f4e7969d9e0cdc5b0`
ran through the approved Stage B route. One Steam dispatch followed a
durable baseline in the ordinary medium-integrity account. A separate
read-only witness authenticated the exact target before attachment.
The non-killing policy, stopped admission and continued attach
break-in were verified.

All 92 initial and four later thread lifetimes read back the approved
DR0–DR3 assignment. Each arming readback verified execution-state
preservation, clean DR6 causes and clear TF and RF. The journal records
no failed arm, rollback or failed readback. The census-only
`LOAD_BEGIN` at 505 was durably acknowledged before the operator
selected the familiar Save2. The run recorded zero timer-driven
running-thread sweeps. Across armed phases, 63 idle checks verified
critical identity and mapping, with four event-held slot checks.

All 338 delivered native events were continued, including process exit
at 607. The observer completed the native event pump and published a
terminal receipt. The game exited before a normal Quit or retirement
request. The observer exited on its own without administrative closure.
The observer reported healthy instrumentation at the terminal receipt,
with no reported journal loss or writer failure. Scientific STOP was
not reached. The verified terminal prefix covers 609 rows and 426,530
bytes with SHA-256
`8cc812b1520a6e232766cb0b192cafca18d821b0c9adb1a0a35a152e6aa4d9a9`.
Its durable bytes and terminal receipt establish capture custody.

### Protection and custody

All 98 protected Documents saves and 95 protected Steam remote saves
matched their independent backups before and after the attempt. Both
designations matched. Both namespaces had zero unclassified entries
and identical transient inventories. No save was relocated or restored.
Steam Cloud and the per-game overlay remained disabled. Configured save
paths, build and critical pins matched. The appmanifest, Steam local
settings and `Plugins.txt` drift were recorded. C: and D: remained above
the caller-available floor plus reserve.

The raw journal, separate exit witness, operator records, exact Steam
attribution bytes, protected-save receipts and verified prefixes remain
in the access-controlled fourth-attempt evidence directory
`.local-work/codex/SRR-010/stage-b-d5b-live-04/private/`. The
`attempt4-evidence.sha256` manifest and `handoff/scientific-result.json`
record their hashes and conclusions. The three earlier Stage B
dispositions and both Control A and Control B remain as recorded below.


<!-- srr-010-stage-b-d5b-live-04-review:start -->
### Independent fourth-attempt review

**COMPLETE handoff review.** The independent internal challenger
accepted `INSTRUMENTATION_INCOMPLETE` for both scientific measures.
The challenger replayed the primary journal, phase and Steam attribution
records, exact target exit, observer closure and protected-save checks.
The missing player-control endpoint and scientific STOP preclude
qualified negative evidence. The cause of the exit remains unresolved.

Reviewed substantive manifest SHA-256
`ec7c964ac0a619aadb1698bcc9ae798ddffdd616740df84d3987ab13bf4a4ebd`.
Independent review SHA-256
`1c3d1874e961ab236288ae57519b52c8fcf4838003b4ae6f84acd24650207e90`
at `.local-work/independent-review/SRR-010/stage-b-d5b-live-04/review.md`.
Only this marked block and its following blank line are excluded from
the dossier digest in the fourth-attempt substantive manifest.
<!-- srr-010-stage-b-d5b-live-04-review:end -->

## Scientific status and D5B recovery

**Save2's allocator question remains unresolved.** All four Save2
attempts with the four-site observer ended during loading with
`0x80000004` and remain
`INSTRUMENTATION_INCOMPLETE`. SRR-009's qualified post-title negative
remains scoped to its 84.281-second observation. The maintainer reported
a successful ordinary load in Control A. Control B reached settled
gameplay with attachment present and all research slots unarmed. Its
operational seal and independently witnessed normal exit stand, and its
formal outcome remains `CONTROL_INCOMPLETE` because the terminal debugger
event and receipt were absent. The cause of all four exits remains
unresolved.

The D5B-informed observer used in the fourth attempt keeps the fixed
four SRR-005 sites on all admitted thread lifetimes. It preserves the
focal iterator, callback and allocator predicates and the joins across
operator boundaries. It adapts two mechanics from the live D5B precedent. Periodic slot reads
occur under delivered debug events throughout Stage B. Idle ticks verify
critical mapping and process ownership without taking running-thread
suspensions. The full operator phase checkpoints remain mandatory.
During a verified all-stop attach or new-thread event the observer sets
DR6 to a clean initial value on an already validated unowned context.
After arming and after RF continuation it verifies the x64 integer,
control, floating-point/SSE save area and MXCSR readbacks. The narrow
context write masks remain in place. If a Stage B arm cannot be
verified after the native register write, the observer tries to restore
the original debug registers while that exact thread is still held and
records the rollback readback. Such an arm refuses readiness and cannot
qualify a negative. The breakpoint resume path still
requires the exact owned slot and cause, TF clear, RF set, and actual
native continuation. Stage A and Control B retain their existing routes.

### Prior art and scope

The D5B build15 archive is
`starfield-outpost-research/.local-work/resource-combined-acquisition/pilot-evidence01.zip`
with SHA-256
`e3836d1e27c4cdc7e84c59ec8076b3fbeb52fae1c7025dea3acbd57110a618a4`.
The exact controller is the tracked
`research/resource-combined-acquisition/controller.cpp` blob
`714511e73eb65438129cd121af41d51a9a091be6` from
`9c0063de56961524c8f985a85e7db9b005426ced`. Build15's archived receipt
pins the controller executable to
`5b3a915b24928be1facf7f546ff3a3c283f76e1e7df615ef2b6fa91d39ecfa48`.
The receipt identifies the historical binary. Its bytes were unavailable
at the historical build path. The live member `raw/events.jsonl` hashes
to `19dd7b956eacd74f3c38a3179f56f5bce2115f45033337e1ed5d3f005cc2f79b`.
The local provenance receipt pins the build inputs and operator records
as well. The adaptation uses this project's sources and native Win32
APIs without a sibling checkout at build or runtime.

| Comparator | Attach, slots and thread lifetime | Delivered events and sampling | Workload, evidence and retirement |
| --- | --- | --- | --- |
| SRR-010 four-site incumbent, live and disposable | Authenticated post-title attach, non-killing policy, four fixed slots on initial and new threads | Exact single-step ownership, RF/DR6 checks and continuation. Delivered module and lifetime tracking. Timer-driven running reads remained outside the deferred menu/load interval | First three Stage B attempts ended during Save2 loading before player control. Disposable four-site joins and sealed sampled negatives verified. Exact exit and retirement separately assessed |
| SRR-010 Control B, live | Same exact retail attach, zero instrumentation slots or research context writes | Owned native attach break-in, continued native events and read-only phase inventories | Settled Save2 and sealed operational end, witness exit 0. Missing terminal native event and receipt, administrative observer-only closure |
| D5B build15, live and source-derived | Native attach and held initialization, 95 verified initial threads. Source installs slots on create events. The archived sample span exercises no newly created lifetime after initial arming | 15,119 captures, numbered ACKs and RF readbacks. No manual running-thread sweeps. Two held-event remaps changed the observed sites and cleared method-specific joins. The automatic switch row records DR6 only after remapping | Same retail build, different Save52 load and Build Mode workload. The later STOP drain ended in deliberate exit `0xc1d0`, under different kill/cleanup authority |
| Reference-handles smoke, live | Startup attach, one DR site, 146 verified TIDs | Two owned RF resumes, forwarded other events, pending-event retirement | Reached main menu. Load untested in smoke. Separate post-load release follow-up failed |
| EXP0002A, live and disposable | Post-title no-DR control and armed all-thread/single-owner alternatives | Owned RF handling demonstrated on disposable targets. No matching live request hit in the armed trials | Different New Save action. No-DR survived and both armed trials exited. Dump contexts do not identify the SRR-010 cause |

D5B shows sustained event-held instrumentation on the same executable.
Its sites, workload, synchronous acknowledgements, per-hit remapping
and kill-on-exit policy differ. The candidate keeps asynchronous durable
journaling, fixed slots and non-killing recovery. Additional periodic
running-thread samples are absent in the quiet title and post-load
periods. Only actual event-held checks and full operator endpoints
support slot continuity in those intervals. Existing gap and
cross-phase rules still apply. A quiet interval cannot exclude a
temporary displacement that appeared and resolved between samples.

### Offline qualification and proposed run card

The recovered binary SHA-256 is
`e907b0f7db771db25c3721d726c6cf1f69d35d4e586f5e0f4e7969d9e0cdc5b0`.
Comparative qualification reuses the same disposable Stage B program,
markers and stimuli with the pinned strategy observer
`a1b70b8ddb773aa488e15216cd763eda5503b5398f5131fc3d8e9841ec68d87e`.
`tools/srr006/compare_d5b.py BASELINE_RESULTS CANDIDATE_RESULTS` reads
the resulting journals and receipts from both roots, checks native
DR6/TF/RF continuation and per-lifetime arming, and compares the sealed
and terminal outcomes. In the busy load both observers captured 512
hits at each site across eight newly armed worker lifetimes. The
candidate verified the new execution-state readbacks. The quiet,
cross-phase, displaced-slot, unknown-module, abnormal-exit and sidecar
fault cases test the scopes of joined positives and sealed negatives.
The explicit Stage B admission fixtures omit the first arm or withhold
its verification after a native write. Both refuse readiness and
retain incomplete science, and the latter verifies rollback.

All 12 paired Stage B cases agreed on scientific dispositions,
seal availability, exit status and per-window outcomes. Across this
fixture schedule the incumbent made 76 periodic running-thread
sweeps and the candidate made zero. Nine Stage A and ten Control B
native regressions passed on the final binary. The compiled
correlation, window, retail-image data and admission diagnostics also
passed. A fresh MSVC 14.51.36231 x64, SDK 10.0.26100.0 `/Brepro` build
reproduced the final observer byte for byte.

The final build and raw qualification evidence are retained under
`.local-work/codex/SRR-010/d5b-recovery/`. Early overlapping fixture
runs recorded a marker-sharing error, a missing retirement row and a
busy supervisor timeout. Fresh representative repeats passed on the
same first binary. The failed runs and the first candidate are retained
with the final candidate evidence. The fourth live attempt exercised
the D5B-informed observer on retail Save2 and ended before player
control. See the fourth-attempt result above.

The following run card was prepared during offline qualification for
the fourth attempt.

For a separately authorized run, use the existing SRR-010 Stage B run
card with the reviewed recovery binary and verify its full hash before
execution. Confirm the Steam baseline, authenticate the independently
witnessed exact game process, and wait for `ATTACH_ARMED`. Keep every
menu, load, player-control and optional Lodge marker individually
acknowledged. The operator selects the familiar Save2 once after
`LOAD_BEGIN_DURABLE`. Preserve the existing complete STOP prefix
verification and capture-first outcome if the target exits unexpectedly.
Prefer normal Quit. Treat normal observer retirement and any authorized
observer-only closure after proven game exit as distinct results. The
write reserve, ordinary account, overlay and Cloud checks, populated
Saves directories and protected backup checks carry forward.

> Original authorization proposal for the fourth attempt. Approve one
> Steam launch using the exact independently reviewed D5B-informed
> candidate and frozen
> manifest, one operator-selected familiar Save2 load, and at most one
> conditional Lodge entrance. Permit normal Quit and observer-only
> closure solely after independently proven target exit and evidence
> verification. Any retry or change to sites, scientific predicates,
> debugger privileges or approved binary requires new authorization.


<!-- srr-010-d5b-review:start -->
### Independent D5B recovery review

**READY FOR STAGE B RE-AUTHORIZATION.** The independent internal
challenger accepted AC1–AC8 on the offline snapshot. The challenger
replayed D5B's exact primary capture and the historical SRR evidence,
verified the comparative tests and admission faults, reproduced the
binary and checked the task-only replay. The reviewed result preserves
four-site scientific sensitivity in disposable tests. Retail Save2
survival and the cause of the earlier exits remain unresolved.

Reviewed substantive manifest SHA-256
`6ad81e9cba0065a858c34d39096b55b3a8b814869a9987db540ab688320e212e`.
Independent review SHA-256
`b74649f3a653597fbbc7bd172af9c0fff2583d76e2ce17e4e10f9a8c8b71c3af`
at `.local-work/independent-review/SRR-010/d5b-recovery/review.md`.
Only this marked block and its following blank line are excluded from
the dossier digest in the substantive manifest.
<!-- srr-010-d5b-review:end -->

## Live Control B — 16 November 2026

**`CONTROL_INCOMPLETE`. Save2 reached settled, responsive gameplay with
the debugger-only observer attached.** The operator confirmed settled
gameplay, and the operational end was independently verified before
normal Quit. The separate exact-process witness recorded exit code
`0x00000000`. The observer continued to run without recording a native
`EXIT_PROCESS_DEBUG_EVENT` or publishing its terminal Control B receipt.
The reviewed contract requires reconciled native event service through
exit for `LOAD_SURVIVED_DEBUGGER_ONLY`.

The completed load establishes debugger-only compatibility through the
sealed endpoint for this run. Save2 selection and gameplay responsiveness
are operator observations. Control B has zero resource-allocation
detection sensitivity. The cause of the three previous Stage B exits
and the missing terminal native event both remain unresolved. The
historical Stage B dispositions and the maintainer-reported Control A
load remain as recorded below.

### Admission and operational evidence

One Steam URI dispatch followed a verified durable baseline in the
maintainer's ordinary medium-integrity session. Before the title marker,
a separate read-only witness bound to the exact retail process and file
identity. The exact approved Control B observer recorded the non-killing
policy, stopped admission, and continuation of its owned attach
break-in. The durable debugger-only barrier recorded zero research
context writes.

| Boundary | Durable sequence |
| --- | ---: |
| Debugger-only ready | 246 |
| Responsive main menu | 254 |
| Load acknowledged before selection | 255 |
| Operator-confirmed settled gameplay | 261 |
| Operational end | 262 |

The recorded load interval contained one thread exit and four debug-string
events, all continued successfully. The seal covered 250 continued native
events. The observer continued another 94 native events after the seal,
bringing the retained total to 344 of 344. The owned attach break-in was
the only captured exception. The retained journal contains zero research
arming, periodic register readbacks, hardware breakpoint hits or
resource-allocation records. The absent terminal receipt leaves its
final context-write counters unavailable.

The operational seal at sequence 262 covers 208,759 bytes with SHA-256
`622c382301509d6688e7f3fee1df029c0d7dd8c2c7549464d7f30ccd8ffa3ee1`.
The final durable journal prefix at sequence 356 covers 271,294 bytes
with SHA-256
`6343f0a48f4edb08963acf29e34b98b60a418d9fa71caa90c348ded2746e2388`.
Both were independently rehashed and preserved. After the witness
confirmed the game was signaled and the controller verified the exact
game was no longer active, the controller reauthenticated the orphaned
observer by PID, creation epoch and executable hash. It preserved the
evidence, closed only that observer under the authorized administrative
procedure, and verified its exit. Normal debugger retirement remains
unverified.

### Protection and custody

Before and after the run, 98 protected Documents saves and 95 protected
Steam remote saves matched their independent backups. Both designated
saves matched and both namespaces had zero unclassified entries. The
Documents transient inventory lost one policy-classified exit-save entry
and gained one. Those incidental changes were retained. Steam remote
transients were unchanged.

Steam Cloud and the per-game overlay stayed disabled. The configured
save path, Steam build and critical identity pins still matched.
Steam client and overlay file drift was recorded at admission.
Postflight recorded changes to the Steam appmanifest and local settings,
and an identity-only replacement of `Plugins.txt`. Both C: and D:
remained above 40,134,217,728 caller-available bytes.

The original journal, sealed and terminal prefixes, operator records,
independent exit witness and postflight are retained under the
access-controlled `.local-work/codex/SRR-010/control-b-live-01/private/`.
The evidence manifest and sanitized result receipt are in the enclosing
run directory and its `handoff/` child.


<!-- srr-010-control-b-live-review:start -->
### Independent live evidence review

**COMPLETE handoff review.** The independent internal challenger
accepted `CONTROL_INCOMPLETE`. The challenger reproduced the Steam
attribution hashes, both journal prefixes, each marker binding, exact
exit and observer-only closure, and the protected-save comparisons.
The settled gameplay observation stands through the operational seal.
Missing terminal debugger evidence limits the formal outcome and leaves
normal observer retirement unverified.

Reviewed substantive manifest SHA-256
`a15b73b7cfa797f1928b89a10881d1a329dc933ac7f0f7226909538e752be320`.
Independent review SHA-256
`9747a396f6f623f9530ff2db9518ba420bf4c87c0b21ca1e079a5766c9f0345e`
at `.local-work/independent-review/SRR-010/control-b-live-01/review.md`.
Only this marked block and its following blank line are excluded from
the dossier digest in the live substantive manifest.
<!-- srr-010-control-b-live-review:end -->

## Control B debugger-only qualification

### Results and interpretation

**Control A (maintainer report).** The maintainer launched Starfield without
the research debugger, loaded the familiar Save2, reached settled gameplay,
and exited normally. This is an operator-reported operational observation.
There is no independently captured exit or before/after save-protection
certificate for that run.

**Control B (offline engineering only).** Ten disposable Windows cases
passed on observer SHA-256
`2a448a789c69eca2400fb40bd5e4ef343d0ebead5963c1aae59974ff66bec640`.
A separately built observer matched that hash. No retail process was
launched, inspected, or attached to, and no Save2 load was performed in
this qualification. The three previous Stage B results remain
`INSTRUMENTATION_INCOMPLETE`. In all three Starfield exited with
`0x80000004` during loading, without a corresponding delivered debug
exception or established cause.

| Case | Disposable finding |
| --- | --- |
| Quiet and churn | Both survived through settled phase, sealed operational end and normal exit. The churn load included four worker lifetimes and four system DLL load/unload pairs. Genuine foreign first-chance single-step and breakpoint exceptions were delivered to the target's own handlers in both cases. |
| Competing debugger, wrong epoch, attach race | The existing debugger and wrong epoch refused before the attach API. The authentic disposable target in the attach race exited after eligibility, and native `DebugActiveProcess` failed. All three were incomplete, with a durable refusal. |
| Interrupted load | The target self-exited with `0x80000004` after the load boundary. The debugger continued its native exit event, and the retained handle and separate witness agreed on the exit code. No corresponding single-step event was delivered. The fixture result was `LOAD_FAILED_DEBUGGER_ONLY`. |
| Marker and operational end faults | Cross-mode, wrong-epoch and wrong-predecessor submissions were refused. A settled run without end and a failed end-sidecar publication remained incomplete. Exit 110 after a verified end preserved the sidecar and stayed incomplete. |

All ten exercised cases recorded zero research context writes, rejected
research context write attempts, and hardware hits. Control B routes all
non-attach exceptions through `DBG_EXCEPTION_NOT_HANDLED`, skips research
arming for pre-existing and new threads, and guards the observer's only
native context-write call. The attach checkpoint reads debug registers
only while Windows holds the initial debugger event. Later checks use
process, module and thread inventory without suspending running threads.
The readiness acknowledgement follows actual continuation of the native
attach break-in and a durable journal boundary. Control B preserves the
retail handle rights, ownership and mapping gates. Verified noncritical
Steam-component drift is recorded. Unclassified or incompatible module
changes can invalidate operational continuity.

The exact-binary regressions passed 12 Stage B, nine Stage A admission,
22 late-attach and 25 creation cases. They retained four-site correlated
positives, qualified quiet negatives, rejection paths, and STOP behavior.
Compiled correlation, window, retail-image data and admission diagnostics
also passed. The build used Visual Studio 18.9 x64, MSVC 14.51.36231,
Windows SDK 10.0.26100.0 and the established `/Brepro` build recipe.
Read-only protection receipts passed before and after disposable testing.
Both namespaces' 98 and 95 protected originals matched independent
backups, both designated saves matched, and there were zero unclassified
entries. Offline configuration checks found Steam Cloud and the per-game
overlay disabled. Session-specific checks remain part of live preflight.

| Capability | Four-site Stage B | Control B |
| --- | --- | --- |
| Native debugging, event service, exact target exit | Yes | Yes |
| Four hardware sites and focal/correlated allocator evidence | Yes | None |
| Qualified resource-allocation non-observation | Under the scientific coverage rules | None |
| Compatibility of this exact debugger-only Save2 run | Outside this control's scope | Assessed by a future separately approved retail run |

A successful Control B load would shift attention toward hardware
instrumentation or its associated handling as the variable that differs
from the prior sessions. It would establish compatibility only for that
exact run, with causation still open. A failed debugger-only load would
show that the four hardware sites were unnecessary for the failure to
occur in that session and direct attention to the common conditions.
Neither result identifies a faulting instruction or establishes which
condition caused the earlier exits.

### Proposed single-session authorization

> Authorize one retail Control B run using the independently reviewed
> manifest and the exact observer hash above on the pinned Starfield
> image `7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28`.
> Authorize one ordinary Steam launch, one operator-selected familiar
> Save2 load, settled gameplay confirmation, operational end and normal
> operator Quit. Authorize observer-only closure if the exact game has
> independently exited and evidence plus observer identity are verified.
> All UI actions stay with the maintainer. Authority excludes a second
> launch or load, movement or travel, Lodge contrast, intentional save
> creation, forced game exit, active detach and scientific Stage B.

### Run card for separate live approval

1. Under the approved ordinary medium-integrity interactive account and
   Steam session, verify the approved manifest, observer and retail
   image hashes, critical runtime and dependencies, Steam attribution,
   URI handler, absent existing Starfield, and absence of inherited
   `__COMPAT_LAYER`. Get the maintainer's NVIDIA overlay confirmation.
   Use the existing [retail admission checks](SRR-009-retail-debugger-admission-and-stage-a.md#draft-stage-a-run-card).
   Set `$session` to a fresh private directory with a trusted ACL and no
   reparse components, `$runDir` to its nonexistent `observer-run` child,
   `$observer` and `$retail` to the exact absolute executable paths,
   `$python` to the approved x64 interpreter, and `$cfg` to the approved
   private settings. Maintain 40,134,217,728 caller-available bytes on
   both C: and D: before material writes.

   ```powershell
   & $python -E -B tools/srr008/preflight.py protection --config $cfg --output "$session/pre-protection"
   & $python -E -B tools/srr008/preflight.py environment --config $cfg --output "$session/pre-environment"
   ```

   Require passing receipts with both designations, both independently
   backed namespaces, zero unclassified entries, the pinned build,
   disabled Cloud and per-game overlay and verified save-path settings.
   Record benign Steam and settings drift. Keep the existing populated
   Saves directories and backups in place.

2. Rehash the actual approved observer immediately before execution.
   Retain its PID, creation FILETIME, image, stdout and stderr.

   ```powershell
   $observerProcess = Start-Process -FilePath $observer -ArgumentList @(
       '--control-b', '--approved-control-b', ('"{0}"' -f $runDir)) -PassThru -WindowStyle Hidden `
       -RedirectStandardOutput "$session/observer.stdout.txt" -RedirectStandardError "$session/observer.stderr.txt"
   $observerBirth = $observerProcess.StartTime.ToFileTimeUtc()
   ```

   Wait for `BASELINE_DURABLE` and verify the journal's durable prefix
   contains the designated Steam baseline. Record dispatch intent, UTC,
   exact observer hash and URI result. Dispatch exactly once using
   `Start-Process 'steam://rungameid/1716740'`. Take `$run` from
   `TARGET_BOUND`. In a separate shell or process, start the witness.
   Verify its process identity and the bound receipt against the run
   token, retail path, image digest and creation FILETIME before
   continuing. Leave the witness running independently through exit.

   ```powershell
   & $python -E -B tools/srr008/watch_exit.py $run $retail $session
   ```

3. After the operator confirms the responsive title card and the witness
   binding is verified, submit the title statement in the controller.

   ```powershell
   & $python -E -B tools/srr006/stage_a_marker.py $runDir $run TITLE_CONFIRMED
   & $python -E -B tools/srr006/control_b.py verify $runDir $run ready $sequence
   ```

   For the verification command use the sequence from
   `DEBUGGER_ONLY_READY <sequence> <challenge>`. The verifier checks its
   exact durable sequence, prior attach admission, non-killing policy
   and continued loader break-in. On refusal, preserve the watermark
   and leave any attached observer servicing the exact process until
   normal exit. Before target binding, `cancel-before-target` remains
   available under the existing admission run card.

4. Run each marker command separately when its operator condition is
   met. Set `$prior` and `$challenge` from the immediately preceding
   acknowledgement. Require the corresponding durable acknowledgement
   and verify the boundary before advancing. Retain the operator's
   statement, marker inputs, response and verification output.

   | Operator point | Marker | Expected acknowledgement | Verify |
   | --- | --- | --- | --- |
   | Main menu responsive | `CONTROL_MENU_CONFIRMED` | `CONTROL_MENU_DURABLE` | `menu` |
   | Familiar Save2 ready for selection | `CONTROL_LOAD_BEGIN` | `CONTROL_LOAD_BEGIN_DURABLE` | `load` |
   | Operator confirms settled, responsive player control | `SETTLED_GAMEPLAY` | `SETTLED_GAMEPLAY_DURABLE` | `settled` |
   | Operator selects the end of observation | `CONTROL_END` | `CONTROL_END_DURABLE` | `end` |

   ```powershell
   & $python -E -B tools/srr006/control_b.py marker $runDir $run $marker $prior $challenge
   & $python -E -B tools/srr006/control_b.py verify $runDir $run $boundary $sequence
   ```

   The operator may activate Save2 once only after the verified load
   acknowledgement. Settled gameplay requires the operator's report
   of sustained responsive control. The operator chooses the endpoint,
   without a fixed inactivity or elapsed-time threshold. The end
   sequence must match the exact byte count and SHA-256 in
   `operational-end-prefix.json` before normal Quit. A missing seal
   leaves the last verified durable prefix as the evidence boundary.
   No scientific STOP or experimental site hits are expected.

5. Allow ordinary operator Quit. Compare the retained witness's exact
   PID, epoch and exit code with the native exit event, observer handle
   result, flushed journal and `control-receipt.json`. Verify the
   receipt's journal hash and final durable watermark. Phase codes are
   1 ready, 2 menu, 3 load, 4 settled and 5 operational end. A qualified
   survival requires a verified end, complete debugger service and
   reconciled normal exit. A qualified load failure requires a verified
   load boundary and reconciled nonzero exit during the load with valid
   service. Any disagreement, unconfirmed admission/phase, missing
   outcome evidence or unresolved service gap leaves the result
   `CONTROL_INCOMPLETE`. Report the target exit, operational seal,
   observer retirement and evidence integrity separately.

   For an orphaned observer after verified exact game exit, preserve
   evidence, reauthenticate observer PID, epoch and image, and use
   observer-only closure only if covered by the live authorization.
   Verify its exit and distinguish administrative closure from normal
   retirement. Preserve all exit evidence and avoid retrying any load
   or launch. Repeat both preflight commands with fresh
   `post-protection` and `post-environment` paths. Preserve and
   classify incidental game writes, including any new unclassified
   entries, without altering protected originals.

### Evidence custody

The offline evidence, exact binary, build logs, test receipts, patch
ancestry and substantive manifest are retained under
`.local-work/codex/SRR-010/control-b/`. That evidence includes the
earlier verifier failure, where an expected continuation field was
absent from the native event row. The final schema records actual
continuation in that row and passed independent replay and adverse
testing. Independent review and its primary challenge evidence are
retained under `.local-work/independent-review/SRR-010/control-b/`.
No raw journal, save, account record or proprietary binary is included
in the tracked patch.


<!-- srr-010-control-b-review:start -->
### Independent engineering review

**READY FOR CONTROL B LIVE APPROVAL.** The independent internal
challenger accepted CB-AC1 through CB-AC8 on the offline snapshot. The
challenger reconciled the primary native records, exercised adverse
cases against the exact candidate, rebuilt the binary, and verified
the task-only replay and historical evidence. Control B has zero
resource-allocation detection sensitivity. Retail Save2 compatibility
remains untested and requires separate authorization.

The reviewed substantive manifest SHA-256 is
`fd325ea518947f7981e7a77ed1c77f73f55807c716f319c9c62912f107fabc5c`.
The independent review at
`.local-work/independent-review/SRR-010/control-b/review.md` has SHA-256
`456521d800ffe5cb02d3a7bd5e06a299ec1e5fe088d62e052bad30093b0907d9`.
Only this marked block and its following blank line are excluded
from the dossier digest in the substantive manifest.
<!-- srr-010-control-b-review:end -->

## Third live attempt with census-only LOAD_BEGIN — 15 November 2026

The third authorized Save2 load ended **`INSTRUMENTATION_INCOMPLETE`**
for both focal invocation and allocator arrival. Starfield again exited
with `0x80000004` before confirmed player control. The retained
journal contains zero owned four-site hits, focal invocations, allocator
arrivals or unresolved cross-phase chains. No window in this attempt
qualified for `NOT_OBSERVED` under the strategy's scientific STOP rule.

| Window | Journal boundary | Duration | Four-site hits | Focal invocations | Allocator arrivals | Verdict for both claims |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Pre-arm startup | Before 430 | — | — | — | — | Uncovered |
| Post-arm title through responsive menu | [430, 466) | 33.833 s | 0 | 0 | 0 | `INSTRUMENTATION_INCOMPLETE`. Both boundaries verified, scientific STOP absent |
| Main menu and pre-load navigation | [466, 505) | 75.267 s | 0 | 0 | 0 | `INSTRUMENTATION_INCOMPLETE`. Census-only closing marker and no scientific STOP |
| Load marker through abnormal process exit | 505 to exit event 606 | 15.349 s | 0 recorded | 0 recorded | 0 recorded | `INSTRUMENTATION_INCOMPLETE`. Control endpoint and scientific STOP absent |
| Post-load and optional Lodge crossing | Unentered | — | — | — | — | Outside observed coverage |

Durations use the journal QPC boundaries. The marker-to-exit interval
includes operator time before the Save2 selection. The Lodge contrast
was omitted because the game exited before confirmed player control.

### Admission, exercised strategy and limits

The controller verified the approved strategy manifest and exact observer
binary immediately before execution. The installed retail image and
critical runtime pins matched. Steam ran under the same ordinary
medium-integrity account and session as the controller, and the operator
reconfirmed that the NVIDIA overlay was off. Baseline 2 was durable
before the one Steam URI dispatch. The retained Steam log tail, append
and attributed line match the recorded hashes and offset. The independent
witness bound to the authenticated target epoch before title confirmation.

Stopped admission and DR0–DR3 readbacks passed on 92 initial thread
generations. Four later threads had verified arming in the title window,
which included 17 successful running censuses, three event-held checks
and an incidental `WindowsCodecs.dll` load. The operator confirmed the
responsive main menu. The checkpoint at 466 read back slots and was
durably acknowledged. The operator identified the familiar Level 3
New Atlantis Save2 and waited for `LOAD_BEGIN_DURABLE` at 505 before
selecting it once. This establishes the operator's reported choice.

The quiet menu interval had 38 successful deferred idle checks and no
debug events. The `LOAD_BEGIN` record bound to the menu predecessor
with `checkpoint=1`, `thread_slot_readback=0` and
`opening_eligible=1`. It verified the inventory and critical identity
under the approved schedule. It did not sample running thread slots or
close a qualified menu negative. The load interval had seven deferred
idle checks (506–512) and one event-held slot check (513). Both intervals
had zero running-thread censuses. The load recorded 92 thread exits and
the process-exit event, with zero module transitions. The full
menu-to-player-control bracket never closed. The reduced-intervention
policy ran as intended and did not prevent the third observed load
failure. Sampled checks leave the documented inter-sample limit.

### Exact exit, evidence and postflight

The sole delivered exception was the owned attach breakpoint at 429.
The observer continued all 338 events, including
`EXIT_PROCESS_DEBUG_EVENT` at 606. Its exact-handle wait at 607 and the
separate witness agreed on exit value `0x80000004` (2147483652).
The journal contains no corresponding delivered single-step exception
or faulting instruction. The same exit value across all three attempts
establishes no shared cause.

The observer reported healthy instrumentation and a completed pump,
wrote a terminal receipt, and exited. Its retirement row at 608 records
`requested=0` and `clean=0`. The operator did not choose Quit, and
administrative closure was unnecessary. The authorization was consumed
by the single launch and load.

The complete operational prefix through **608** contains **421,089
bytes**, SHA-256
`6f274edc9a0446ff3e8a737203deb5e3f45dfb530ea8abed7977803b24fc9854`.
The last verified phase prefix through **505** contains **357,263
bytes**, SHA-256
`366ca704d7e87b5b45a6b2667d087cd899d4e502a6cf23bde1493956b2a2c21f`.
There was zero writer loss and no uncommitted tail. Neither retained
prefix is a scientific STOP seal. The first two attempts retain their
original accepted results below.

Fresh postflight verified 98 Documents and 95 Steam remote protected
pairs against independent backups, both designations and zero
unclassified or other entries. Both transient inventories matched
between snapshots. Steam Cloud and the per-game overlay remained off.
The app manifest and Steam local configuration digests changed while
their checked fields agreed. `Plugins.txt` changed file identity with
an identical digest. The monitored Steam executable and DLL hashes and
critical pins matched preflight. Both drives exceeded the space floor
with reserve.

The third capture is in
`.local-work/codex/SRR-010/stage-b-strategy-live-03/private/`.
Its parent contains the 36-entry `attempt3-evidence.sha256`, SHA-256
`5b7b5438841f4ac892113924e1aaeee71cbea07f8197004ccfb54d2f75e30c9e`.
It pins the complete journal, both verified prefixes, console and
operator records, Steam attribution inputs, independent witness,
preflight and postflight receipts, and the offline collection procedure.

<!-- srr010-attempt3-review:start -->
**COMPLETE for the authorized third attempt, evidence and postflight.**
The independent challenger accepted `INSTRUMENTATION_INCOMPLETE` for
both focal metrics and verified the census-only boundary, deferred
checks, exact exit, save protection and all three live evidence sets.
This attempt changed only the dossier relative to the approved strategy
stack.

The reviewed handoff manifest SHA-256 is
`e8a689e600e21af68656b5c62e73eb3dc44d637bfd16aca75724760a12bedf7b`.
Only this third-attempt review block is excluded from the dossier
entry. The independent report is
`.local-work/independent-review/SRR-010/strategy-live-03/review.md`,
SHA-256
`67b0c7487fdfbdce47a54623f6202bece11032acb6e53ba750e9031b18ec0996`.
The incremental task patch is
`.local-work/diffs/SRR-010-stage-b-strategy-live-03.diff` and applies
after the four reviewed historical patches.
<!-- srr010-attempt3-review:end -->

## Instrumentation strategy after the two Save2 attempts

Both retail loads remain **`INSTRUMENTATION_INCOMPLETE`**. Each ended
with `0x80000004` before confirmed player control, with no corresponding
delivered single-step exception or faulting instruction in the journal.
The two attempts' qualified pre-load negatives retain their original
scope. The new offline candidate keeps all four sites, defers idle
sweeps between the full main-menu and player-control checkpoints, and
removes the pre-load marker's running-thread suspension. It uses a read-only census at
`LOAD_BEGIN`. Disposable runs established positive detection and scoped
quiet qualification. Survival of retail Save2 loading remains unproved.

### Evidence and choice

| Prior evidence | What transfers to this design |
| --- | --- |
| SRR-009 | The four sites, post-title arming and STOP seal supported a bounded 84.281-second negative. The normal game exit and later observer-only closure were separate outcomes. No save load was covered. |
| Both SRR-010 live loads | Both passed a running-thread sweep at `LOAD_BEGIN` and then ended before player control. They recorded no native debug event during either menu/preload window, and no owned four-site exception during either load. The second deferred eight idle load readbacks and made one event-held check. The 16.184 s and 16.067 s marker-to-exit times include operator time. |
| Reference-handles native controls | Two owned startup DR0 hits were continued with RF and the game reached a responsive menu. A separate attached Kreet fast-travel run exited with the same process status. Neither establishes the SRR-010 failure mechanism. |
| EXP0002A | The live no-DR New Save control survived. The armed all-thread and single-owner New Save trials failed on a different workload. Their saved exception contexts provide partial evidence at the save-request site and do not identify an SRR-010 fault. |
| D5B build15 | The observer on the same retail build survived a different Save52 load through Build Mode, with 95 initial readbacks and 15,119 acknowledged, RF-verified resumes. Its register work occurred under delivered debug events. Sites, workload, arming order and authorized terminal disposal differed. |

The exact external source, commits, live streams and build identities
are described in [the recovery comparison](#evidence-for-the-change).
The strategy comparison reverified those primary pins, both archived
SRR-010 journals and exact-exit receipts, and the SRR-009 verifier.
The pre-implementation choice and rechecks are retained in
`.local-work/codex/SRR-010/strategy/`.

SRR-010 already uses native Win32 event delivery, arms later threads,
attributes owned execution breakpoints by thread and DR state, and
sets RF to continue at the original instruction. It retains its
stricter stopped admission, per-thread readbacks, critical mappings,
foreign-exception handling and non-killing policy. The remaining
transferable difference is D5B's lack of manual running-thread sweeps
immediately before the load. The strategy removes that required sweep
and any periodic one after the verified menu until player control.
That is a provisional timing intervention. The earlier reduced-idle
attempt exercised a smaller change and still failed.

Waiting for a natural all-stop event to acknowledge `LOAD_BEGIN` could
strand the operator on either observed silent menu. An explicit remote
break-in adds a new target intervention and identity checks. Changing
RF/DR6 servicing on delivered hits does not address the recorded
hit-free exit path. Removing the guard site would remove its samples
with no evidence of an operational benefit. Removing a correlation site
would also sacrifice an invocation or allocator claim. A thread subset
has no verified population basis. The candidate retains all four sites
on all admitted threads.

### Claim capability and qualification

| Capability | Qualification and observation boundary |
| --- | --- |
| Physical site detection | The busy disposable load had 512 owned hits at each of the four slots, eight new-thread readbacks and two incidental DLL load/unload pairs. The checks verify DR6, RF with TF clear and actual continuation. The retail executable and RVA windows are pinned separately. |
| `OBSERVED_INVOKED` | The busy load retained focal iterator-to-callback joins. The paused native chain test recorded its callback before `LOAD_BEGIN`. Generic hits alone remain outside this claim. |
| `OBSERVED_REACHED_ALLOCATOR` | Busy load captured orchestrator arrivals with the original ancestry predicates. The paused chain reached the allocator on the same thread and generation after `PLAYER_CONTROL` and both Lodge markers. The terminal crash before STOP preserved those durable positives. |
| Qualified `NOT_OBSERVED` | A quiet load qualified within a clean, fully checked menu-to-control bracket with a verified STOP. `LOAD_BEGIN` is census-only and cannot close the menu/preload window as a standalone negative. A real unknown-module transition in the preceding menu interval invalidated the later load opening even with a successful inventory marker, full control checkpoint and valid STOP. An unsealed Stage B receipt publishes no negative. |
| Cross-phase coverage | Markers preserve pending frames. The unresolved incoming-chain model rejects an aggregate quiet verdict. The native chain spanning the markers demonstrates the positive case. |
| Evidence integrity | Slot displacement invalidates the affected load coverage. A later coverage gap or abnormal exit leaves earlier durable positives assessable. Seal-sidecar failure preserves the operational watermark and cannot promote it to scientific STOP. Terminal event, same-handle witness and retirement outcomes remain separate. |

The full `MAIN_MENU_CONFIRMED` marker and `PLAYER_CONTROL` still
check thread slots and modules. Between them, idle ticks check exact
process and critical mapped-code identity and defer running context
readbacks. Held-event checks and new-thread arming continue. The
`LOAD_BEGIN` read-only census reconciles live thread IDs and retained
births against armed generations, reconciles modules, and verifies the
process and critical mappings. A successful marker records
`checkpoint=1` and `thread_slot_readback=0`. Its
`opening_eligible` field records whether the verified menu start and
coverage so far can support the enclosing bracket. A preceding gap or a
missing full control endpoint prevents a load negative. Incoming
unresolved chains still constrain the relevant coverage.

The sampled slot checks can miss a displacement restored between
samples. A quiet bracket can go unsampled for the full menu wait and
load if Windows delivers no events. Qualified quiet depends on the
documented sampled coverage, continued event service, the full enclosing
checkpoints and the verified STOP. The census-only marker itself
provides no slot sample.

Build with the pinned Phase 1 x64 toolchain and `/Brepro`. The Stage B
harness writes the new `preload-gap` and `chain-before-stop` native cases
alongside the earlier fixture cases. It uses only copies of its own
disposable binary. The existing research tooling and Ghidra have no
new runtime dependency.

```powershell
python -E -B tools/srr006/qualify_stage_b.py $observer "$out/strategy-stage-b"
```

All twelve Stage B cases and the 56 creation, late-attach and Stage A
regressions passed, along with the compiled correlation, window,
retail-profile and admission diagnostics controls. The five focused
strategy cases also passed under the ordinary medium-integrity
Windows account. No retail process was inspected or started.
Fresh protection receipts verified 98 Documents and 95 Steam remote
protected pairs, both designations, zero unclassified entries and
identical transient inventories. Both archived live evidence sets were
rehashed and the prior SRR-009 verification ran again.

### Proposed authorization and run card

Authorize one ordinary-account Steam dispatch of the pinned retail
executable, using the exact strategy observer and manifest in the
review block below. The scope would cover one operator-selected Save2
load, one optional practical Lodge entrance after player control, STOP,
normal operator Quit and exact observer-only closure after independently
verified target exit and evidence preservation. Keep the save namespace
populated and all in-game actions with the operator. There is no
automatic retry.

Apply the [reviewed run card](#reviewed-stage-b-run-card-and-authorization-proposal)
with the strategy binary. Verify fresh identity, process, environment,
free-space and save-protection receipts, and the separate exit witness.
Require durable verified arming and a successful full main-menu boundary.
Use the existing marker tool and predecessor/challenge to issue
`LOAD_BEGIN`. Before the operator selects Save2, verify both the
durable acknowledgement and its census-only fields described above.
Record a refused bracket as incomplete for a load negative. After the
operator reports responsive player control, verify the full boundary,
observe a useful post-load interval and coordinate the optional Lodge
markers only if practical. Verify scientific STOP before relying on a
quiet verdict. Preserve earlier durable positives and the operational
prefix if the process exits first. The original live authorizations
are consumed. This proposal requires new written approval.

<!-- srr010-strategy-review:start -->
**READY FOR STAGE B RE-AUTHORIZATION.** The independent challenger
accepted all eight criteria, verified the retained evidence and tested
the quiet-load counterexample through full player-control confirmation
and unsealed exit. No negative was published. The reviewer reproduced
the exact observer and verified isolated patch replay. Retail Save2
survival remains untested for this strategy.

The reviewed strategy manifest SHA-256 is
`4bf2ac306634aa638844349f71a75ff79068c36b989ba81401c60510c9c99682`.
Only this strategy review block is excluded from the dossier entry.
The proposed binary is
`.local-work/codex/SRR-010/strategy/build/observer.exe`, SHA-256
`a1b70b8ddb773aa488e15216cd763eda5503b5398f5131fc3d8e9841ec68d87e`.
The proposed retail image is Starfield 1.16.244.0, SHA-256
`7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28`.
The independent report is
`.local-work/independent-review/SRR-010/strategy/review.md`, SHA-256
`5ae6b9126c08f8ec74b0b28b3e40c1b7515afd783a221d23d58bdb672cc976e4`.
The incremental patch `.local-work/diffs/SRR-010-instrumentation-strategy.diff`
applies after the original Stage B, observer-recovery and second-attempt
patches. A live attempt requires separate written authorization.
<!-- srr010-strategy-review:end -->

## Second live attempt with the recovery observer — 15 November 2026

The authorized recovery attempt again ended **`INSTRUMENTATION_INCOMPLETE`**
for focal invocation and allocator arrival during the Save2 load. The
operator initiated the single permitted load through the ordinary menu.
Starfield exited with `0x80000004` before the operator regained control.
The observer recorded zero four-site hits, focal invocations, allocator
arrivals or unresolved cross-phase chains. The two closed pre-load
windows support qualified `NOT_OBSERVED` for both metrics.

| Window | Journal boundary | Duration | Owned four-site hits | Focal invocations | Allocator arrivals | Invocation and allocator verdicts |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Pre-arm startup | Before 427 | — | — | — | — | Uncovered |
| Post-arm title through responsive main menu | [427, 470) | 39.547 s | 0 | 0 | 0 | Qualified `NOT_OBSERVED` |
| Main menu and pre-load navigation | [470, 508) | 73.011 s | 0 | 0 | 0 | Qualified `NOT_OBSERVED` |
| Load marker through abnormal process exit | 508 to exit event 610 | 16.067 s | 0 recorded | 0 recorded | 0 recorded | `INSTRUMENTATION_INCOMPLETE` |
| Post-load and conditional Lodge crossing | Unentered | — | — | — | — | Outside observed coverage |

The durations are from the journal's QPC boundaries. The interrupted
interval includes operator time after `LOAD_BEGIN` and before selection.
The title window had 20 running censuses, four event-held readbacks and
five verified new-thread armings, along with an incidental
`WindowsCodecs.dll` load. The menu/preload window had 37 successful
running censuses and no debug events.

### Recovery policy exercised and outcome limits

The controller verified the approved recovery manifest, exact observer
binary, installed executable and critical runtime pins before execution.
The ordinary medium-integrity shell matched Steam's session, and the
operator reconfirmed the NVIDIA overlay was disabled. The observer
acknowledged Steam baseline 2 before the sole URI dispatch. The
independent exit witness bound to the exact target before title
confirmation. Stopped admission and all four hardware-slot readbacks
passed on 91 initial thread generations. The operator confirmed the
responsive title and menu, identified the familiar Level 3 New Atlantis
Save2 entry and waited for `LOAD_BEGIN_DURABLE` at 508 before selecting
it once. The operator's report identifies the UI choice.

During the load window, rows 509–516 recorded eight successful idle
process and critical-mapping checks with
`thread_readback_deferred: 1` and `census_attempted: 0`. Row 517 was
one successful event-held slot check. There were no timer-driven running
thread censuses, module transitions or delivered exception events in
this interval. The journal recorded 92 thread exits and the process
exit. The reduced cadence was exercised, and the load still failed to
reach player control in this run. The idle rows did not sample thread
registers. The missing arrival checkpoint and scientific STOP leave
both load metrics incomplete irrespective of the recorded zero hits.

The sole delivered exception in the whole run was the owned attach
breakpoint at 426. The observer continued all 338 events, including
`EXIT_PROCESS_DEBUG_EVENT` at 610. The same-handle wait at 611 and
independent witness agreed on `0x80000004` (2147483652) for the same
target epoch. As in the first attempt, this is the process exit value.
The journal contains no corresponding captured single-step exception or
faulting instruction. The cause remains unresolved.

### Evidence, retirement and preservation

The complete operational prefix contains **423,489 bytes** through
sequence **612**, SHA-256
`9239e3a5110f64b7ab3cb669f9c5dbd14a18bed5ed7dc351597d1241da3a1fda`.
The retained last verified phase prefix contains **359,040 bytes**
through sequence **508**, SHA-256
`d404b7f96859bd288c164f8c930ff3b7eee33983b8dcde5e2a4c1557ed5e9176`.
The terminal journal had no uncommitted tail or writer loss. There is
no scientific STOP sidecar. The observer reported healthy
instrumentation and a completed pump, wrote a terminal receipt and
exited. The retirement row at 612 records `requested=0` and
`clean=0`. The operator did not choose Quit, and administrative closure
was unnecessary. The Lodge contrast was omitted because the target
exited before player control. The second-attempt authority is consumed.

Fresh postflight verified 98 Documents and 95 Steam remote protected
pairs against independent backups, with both designations and zero
unclassified or other entries. Neither transient inventory showed an
addition, deletion or change between snapshots. Steam Cloud and the
per-game overlay remained off. The app manifest and Steam local
configuration digests changed while their checked fields agreed.
`Plugins.txt` changed file identity with an identical digest. The
monitored Steam backing files and critical pins matched their
preflight digests. Both drives remained above the free-space floor plus
reserve. The first attempt's evidence and accepted conclusions remain
as recorded below.

The capture is retained under
`.local-work/codex/SRR-010/stage-b-recovery-live-02/private/`.
Its parent contains `attempt2-evidence.sha256` with 36 entries and
SHA-256
`ac8eb2cd84458f02af24a09a6902e2832ef52f1fd7dc60ec9ae67743255f0487`.
It pins the raw journal, both retained prefixes, console and operator
records, Steam attribution inputs, independent exit witness, preflight
and postflight receipts, and the offline collection procedure.

<!-- srr010-attempt2-review:start -->
**COMPLETE for the authorized second attempt, evidence and postflight.**
The independent challenger verified both qualified pre-load negatives,
the incomplete load, the reduced-cadence journal records, exact
process exit and save preservation. The second attempt changed only
this dossier relative to the approved recovery stack.

The reviewed handoff manifest SHA-256 is
`46055ce61ebd9e31f121f03d90e0c3ea79e438cb710a6c53af59e134a10edd4a`.
Only this second-attempt review block is excluded from the dossier
entry. The independent report is
`.local-work/independent-review/SRR-010/recovery-live-02/review.md`,
SHA-256
`6d68e574bc98f20b1cfbf770719243b20d39be35e2cd78e6f6616520a6075e76`.
The task patch `.local-work/diffs/SRR-010-stage-b-recovery-live-02.diff`
applies after the original Stage B and observer-recovery patches.
<!-- srr010-attempt2-review:end -->

## Live result — 15 November 2026

The Save2 load and arrival outcome was **`INSTRUMENTATION_INCOMPLETE`**
for both focal invocation and allocator arrival. The game exited abnormally after the
operator initiated the Save2 load. Player control, post-load observation
and scientific STOP were never reached. The complete durable journal
contains zero four-site hits, focal invocations, allocator arrivals or
cross-phase joins. The two separately closed windows before the load
support qualified `NOT_OBSERVED` for both metrics.

| Window | Journal boundary | Duration | Owned four-site hits | Focal invocations | Allocator arrivals | Invocation and allocator verdicts |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Pre-arm startup | Before 427 | — | — | — | — | Uncovered |
| Post-arm title through responsive main menu | [427, 483) | 76.235 s | 0 | 0 | 0 | Qualified `NOT_OBSERVED` |
| Main menu and pre-load navigation | [483, 527) | 84.877 s | 0 | 0 | 0 | Qualified `NOT_OBSERVED` |
| Load marker through abnormal process exit | 527 to exit event 628 | 16.184 s | 0 recorded | 0 recorded | 0 recorded | `INSTRUMENTATION_INCOMPLETE` |
| Post-load and conditional Lodge crossing | Unentered | — | — | — | — | Outside observed coverage |

The durations use journal QPC at the two verified marker boundaries or,
for the interrupted window, the exit event. The last interval starts at
`LOAD_BEGIN`, before the operator selected the save. Its duration
includes operator time and does not measure engine load time. At exit,
the observer marked the open interval incomplete for both metrics.
Successful periodic readbacks during that interval cannot supply the
missing arrival boundary. The optional Lodge crossing was omitted because
the game exited before player control.

### Evidence, exit and preservation

The exact durable operational prefix through sequence **630** contains
**431,870 bytes** with SHA-256
`5906cd54edca3f1a9cc9114a8816a2cb90b5068191c144232bab102f94683f81`.
It matches the entire terminal journal. The last verified phase prefix
through `LOAD_BEGIN` at **527** contains **368,301 bytes** with SHA-256
`885b018fb9a5b9c576eed5949894e4162691f64f571f6eacdbe206e9fa205f86`.
These are operational and phase-boundary receipts. There is no scientific
STOP sidecar.

The `EXIT_PROCESS_DEBUG_EVENT` at 628 was continued successfully. The
observer's retained handle at 629 and the independent read-only witness
agreed on exit code `0x80000004` (2147483652) for the same process epoch.
Windows names that value `STATUS_SINGLE_STEP`. The only exception event
recorded in the journal was the owned attach breakpoint before arming.
The exit status identifies no recorded faulting instruction or scientific
site, and the cause of the exit remains unresolved.

The observer continued all 336 debugger events and recorded no continuation
errors, lost rows or writer failures. It reported healthy instrumentation
and a completed event pump. It wrote a terminal receipt and was confirmed
absent. At sequence 630, the observer recorded that retirement was unrequested
and lacked a clean retirement outcome. The operator did not choose normal
Quit, and administrative closure was unnecessary.

Postflight reverified all 98 Documents and 95 Steam remote protected
pairs against independent backups, both designations and zero unclassified
or other entries. The transient inventories reported zero added, changed
or removed entries. These inventories cover the checked namespaces and
do not attribute save behavior between snapshots. Cloud and the per-game
Steam overlay remained off. The app manifest and Steam local configuration
file digests changed while the checked app fields and overlay setting
agreed. `Plugins.txt` changed file identity with an identical digest.
The critical image, runtime and retained Save2 pins verified again. The
Steam binaries checked before and after the session matched their
respective preflight digests. Both drives exceeded the 40,134,217,728-byte
threshold including reserve.

### Authorized run and retained records

The written same-session authorization covered one Steam launch, one
operator-selected Save2 load and a conditional Lodge crossing using the
frozen Phase 1 candidate. The controller checked the approved executable,
manifest, patch and retail image before dispatch. The participating shell
matched Steam's ordinary medium-integrity account and session. The
operator confirmed NVIDIA overlay was disabled. The observer acknowledged
Steam baseline sequence 2 before the single URI dispatch. The captured
Steam process-log tail, title-time append and attributed tracking line
verify against the observer's recorded digests and offset.
Sequences 1 and 5 record origin-verified drift from the SRR-008
`steam.exe` and `gameoverlayrenderer64.dll` identities. The overlay
mapped before arming. Its presence establishes a loader observation.

The independent read-only witness bound to the exact target before
`TITLE_CONFIRMED`. Stopped admission and all four DR0–DR3 readbacks
passed on 91 initial thread generations. Four later post-arming thread
admissions also had verified readbacks. The title window had 40 successful
periodic checks and one incidental System32 `WindowsCodecs.dll` load.
The menu/preload window had 43 successful periodic checks. The
interrupted load interval recorded nine successful checks before exit,
91 thread exits and the exact process exit event. It had no hardware or
module-transition events.

The operator confirmed responsive title and main menu in sequence and
identified the familiar Level 3 Save2 entry for Jemison, New Atlantis.
Only after `LOAD_BEGIN_DURABLE` at 527 did the operator initiate the
single load. The operator reported that the game exited during the load.
The UI description identifies the operator's choice. The observation
does not establish the bytes consumed by the game. The authorization for
one Stage B session is consumed.

The capture is under private custody in
`.local-work/codex/SRR-010/stage-b-live-20261115T091730Z/private/`.
Its evidence manifest `phase2-evidence.sha256` is in the parent directory,
with SHA-256
`c9aeb6f9ff54de4e7ecd2033ecf8ac286574151b603d5ca37222bfbd08869f89`.
It pins the entire terminal journal, both retained prefixes, console
transcripts, marker and operator records, Steam attribution bytes,
independent witness, postflight receipts and local verification script.

<!-- srr010-phase2-review:start -->
**COMPLETE for the authorized Phase 2 attempt, evidence and postflight.**
The independent challenger verified both pre-load negatives, the
incomplete load, the terminal process outcome and protected-save
postflight. The exact approved observer was used. The final cumulative
patch preserves all Phase 1 tooling and changes only the dossier
relative to the Phase 1 handoff.

Reviewed handoff manifest SHA-256
`bd9174a072cf65937c94d0d8cac2f0f12fadbcac5a7d0e9ea0a9ca0025829bfb`.
Only this Phase 2 review block is excluded from the dossier entry. The
independent report is
`.local-work/independent-review/SRR-010/phase-2/review.md`, SHA-256
`470effbfc17234b49d64a87225fb6b32a7be6713bc4773a106600404bbac2f20`.
The cumulative task patch is `.local-work/diffs/SRR-010-stage-b-live.diff`.
<!-- srr010-phase2-review:end -->

## Offline observer recovery

The recovery candidate removes timer-driven thread suspensions while the
operator's Stage B load is in progress. Disposable tests exercised a quiet
load, a busy load with all four hardware sites and a real slot displacement
that prevented a qualified load verdict. Survival of retail Save2 loading
remains untested with this candidate. The first attempt's
`INSTRUMENTATION_INCOMPLETE` result and two qualified pre-load negatives
stand on their original approved binary and evidence.

### Evidence for the change

The retained SRR-010 journal has eight successful running thread censuses
and one successful event-held readback between `LOAD_BEGIN` 527 and
exit event 628. After `LOAD_BEGIN` it records 91 thread exits, the process
exit, zero module transitions and zero exceptions. The only delivered
exception in the run was the owned attach breakpoint at 426. There was
no hardware-hit RF operation or failed continuation in the load window.
The terminal process status and witness cannot distinguish an unobserved
event from other paths to the same exit value. The record establishes
no violated exception-handling contract or faulting instruction.

| Actual result and workload | Launch and attach | Threads and hardware | RF and single-step handling | Event service | Save or gameplay transition | Durability | Survival and limits |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Live failure** · SRR-010 original Stage B | Ordinary Steam, verified post-title attach | 91 initial and four later readbacks, four simultaneous sites, timer-driven running thread census | Exact owned-site/DR6 with RF and readback. No hardware exception delivered during load | 336 events continued, sole exception was the owned attach breakpoint | One Save2 selection, no player control | Operational 630, last verified phase 527, no scientific STOP | Abnormal exit `0x80000004`. Cause unresolved |
| **Live success** · reference-handles startup smoke | One Steam launch, direct native attach during startup | One DR0 site, 146 armed TIDs | Two native hits, RF, TF clear. Pending-event retirement scheme, no competing pending game event in this run | 314 continued events, eight naming exceptions passed through | Startup to responsive main menu | 1,406 retained raw rows and four delayed health checks | Main menu responded after detach. No save load exercised |
| **Live failure** · reference-handles release follow-up | Native attach after operator-reported Save2 load | Hardware release-observation sites, event-driven servicing | One delivered owned single-step failed the object filter and continued with RF. No selected release capture | Exit observed before retirement, exit continuation unconfirmed | Fast travel to Kreet | Retained 77,761-byte native journal | Exit `0x80000004`. An event-driven observer can still fail in another workload |
| **Live controls and failures** · outpost EXP0002A 0.1.2 and 0.1.3 | Native post-title attach, separate Save action trials | S1 ran with no DR sites and survived. All-thread 0.1.2 and single-owner S2 0.1.3 had DR0 armed | RF servicing qualified separately on a disposable hit. Neither live armed trial recorded a request hit | Retained native logs and two matching dump contexts at the save-request site | Ordinary **New Save** click, distinct from loading a save | Native journals, reviewed dump evidence and cleanup records | Both armed trials exited. The dump contexts do not assign a cause to SRR-010's exit |
| **Live success through load** · outpost D5B build15 | Ordinary Steam, native post-title attach to the same retail build | 95 initial readbacks, four DR sites per phase, two remaps, no timer-driven running thread suspension | Owned RF continuation and context readback, 15,119 verified resumes | Context work in held events, continued module and thread events, no EXCEPTION or LOSS rows | One operator-selected Save52 load, travel and Build Mode | Archived 45,645-row journal, framed captures and acknowledgements | Reached Build Mode while attached. Later deliberate disposal used different authority, site coverage and cleanup |

The exact source and primary records are pinned in ignored local custody
under `.local-work/codex/SRR-010/recovery/`. The reference-handles source
is from `6a77579a184c64e0c080c8f3b7883c34bd17e24b`. Its live smoke
journal SHA-256 is `fe9e2af5c8129e785a04eff4751e45ab94c59b3840dcfe1f853ed8857ba9e188`.
The outpost source is pinned at `d116bc63ff394b0156539161c8d1addfc902665a`,
with the exact archived 0.1.2 and 0.1.3 build inputs separately identified.
D5B's used controller matches Git blob `714511e73eb65438129cd121af41d51a9a091be6`.
The retained D5B archive includes the operator records, raw service
journal and build receipt. Its primary journal SHA-256 is
`19dd7b956eacd74f3c38a3179f56f5bce2115f45033337e1ed5d3f005cc2f79b`.
The two sibling Save-action dumps were preserved separately from their
journals. No comparable SRR-010 dump was used.

### Scoped method and limits

D5B is the closest positive evidence for a less intrusive event-service
schedule. The recovery borrows the scheduling choice only. During the
Stage B load phase, idle ticks still verify the exact process and critical
image mappings, with `thread_readback_deferred: 1`. They defer the
running thread and module censuses. Windows suspends the debuggee's
threads while delivering a debug event, which allows the existing
event-held slot checks to continue without acquiring extra suspensions.
The exact delivered module and thread events remain serviced. A running
thread's context cannot provide a valid substitute for the deferred
check. [Windows debugger loop](https://learn.microsoft.com/en-us/windows/win32/debug/writing-the-debugger-s-main-loop) ·
[GetThreadContext](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getthreadcontext).

`LOAD_BEGIN`, `PLAYER_CONTROL` and STOP still require the original full
thread and module checkpoints, which may briefly suspend running threads
at the explicit operator boundary. A deferred row provides no slot
verification. A transient slot change restored between event-held and
boundary checks can escape sampling. Quiet loads therefore have fewer
in-window context samples. A detected mismatch still leaves the affected
window incomplete. Missing `PLAYER_CONTROL` leaves load arrival unverified.
The four site RVAs, ownership and RF rules, correlation and pending-token
checks, critical identities, admission, scientific seal and recovery
authorities retain their original implementation. This change is a
**PROVISIONAL** way to reduce intervention during loading.

### Reproduction and proposed re-authorization

Build the observer with the Phase 1 toolchain and `/Brepro`. Run the
existing Stage B harness from the checkout root. Its two added cases are
`load-busy` and `load-slot-loss`. The first runs two waves of disposable
workers, loads and unloads a System32 module, and exercises all four sites
under competing thread activity. The second physically replaces DR3 on
the waiting disposable thread and tests that player-control qualification
fails while earlier closed windows remain assessable. The existing
`quiet` case checks that deferred ticks, event service and verified
endpoints permit a qualified zero. The fixture harness alone has a
watchdog, with a longer allowance for the busy case to drain its journal.
The harness writes fixture capture directories and receipts. The only
processes it creates or debugs are copies of its own disposable target.
Ghidra and the installed game remain outside those operations.

```powershell
python -E -B tools/srr006/qualify_stage_b.py $observer "$out/stage-b-recovery"
```

All ten Stage B cases, 56 creation, attach and admission regression
cases, and the compiled correlation, window, retail-profile and admission
diagnostic controls passed. The busy case recorded 2,048 owned hardware
events across the four sites, eight worker births and exits, and two
module load and unload pairs. It verified owned DR6, RF with TF clear,
successful continuation and a checked player-control boundary.

The three focused controls also passed under the ordinary medium-integrity
Windows account on Windows 10 build 19045.6466 with the pinned runtime.
In the first ordinary-account busy attempt the fixture supervisor's
18-second watchdog expired before it received `PLAYER_CONTROL_DURABLE`.
The terminal journal retained the accepted checkpoint and allocator
positives, with all events continued and zero row loss. That attempt
lacked the timely acknowledgement and scientific STOP required by the
test. The replay used the same observer binary and a longer fixture-only
watchdog. Both attempts are retained under the recovery directory.

Fresh before-and-after protection receipts agree on all 193 protected
save pairs, both designations and the transient inventories. The previous
SRR-009 and SRR-010 primary records and approved patches retain their
original hashes. No game process was launched or attached during
recovery qualification.

The proposed second attempt requires separate written approval of the
recovery manifest and executable in the review block below, the same
retail image, and exactly one new Steam dispatch and one normal Save2
selection. Recheck the protections, configured inputs, free space,
ordinary Steam account and independent read-only exit witness. Use the
[reviewed run card](#reviewed-stage-b-run-card-and-authorization-proposal)
with the approved recovery binary. Wait for verified `ATTACH_ARMED`
before navigating past the title card and for `LOAD_BEGIN_DURABLE`
before actually selecting Save2. Capture through operator-confirmed
`PLAYER_CONTROL` and a useful post-load interval. Allow the Lodge
contrast only if approved, practical and coordinated after player
control. The operator performs all game UI actions.

Verify scientific STOP separately from natural or abnormal game exit and
observer shutdown. If the process exits before STOP, retain the durable
operational prefixes and report the missing boundary. Normal operator
Quit follows an independently verified seal when possible. Any approved
administrative cleanup remains limited to the reauthenticated observer
after independent exact-target exit verification. No retry is included.

<!-- srr010-recovery-review:start -->
**READY FOR STAGE B RE-AUTHORIZATION.** The independent challenger
accepted all eight recovery criteria, including the adverse attempt to
qualify an interrupted load after successful deferred checks. The
reviewer verified the retained historical evidence, reproduced the
candidate binary from isolated source and replayed the incremental patch.
This disposition is for engineering readiness. Retail load survival
with the recovery candidate remains untested.

The reviewed recovery manifest SHA-256 is
`43d5c830a1ab87fd6776bd223b3846402a59da954a71793c2305ba168108b2c6`.
Only this recovery review block is excluded from the dossier entry.
The observer under `.local-work/codex/SRR-010/recovery/build/observer.exe`
has SHA-256
`43223b9c693fe38fd8d7d30f8e0b0a7b2bc78bcf5eb5d508ddfb7e3dd5d0725c`.
The report is `.local-work/independent-review/SRR-010/recovery/review.md`,
SHA-256
`c79dee9a733510b8b5d0d8ff97ed089d244406d3b33e4f5c4fdb6780dc1402fc`.
The incremental patch `.local-work/diffs/SRR-010-observer-recovery.diff`
applies after the preserved `.local-work/diffs/SRR-010-stage-b-live.diff`.
The proposed second attempt requires new written authorization.
<!-- srr010-recovery-review:end -->

## Phase 1 offline result and scope

All eight Stage B disposable cases passed on the candidate built from an
isolated patch replay. In the quiet case, the 8.600-second load window
produced qualified `NOT_OBSERVED` for both metrics at STOP 58. In the
cross-phase case, the invocation at sequence 44 joined to allocator
arrival at 48 across `PLAYER_CONTROL` at 45. A later module gap made
only the Lodge transition incomplete, and the scientific seal at
sequence 56 remained valid after the fixture crashed. When a separate
fixture blocked STOP sidecar publication, the observer withheld the
STOP acknowledgement and retained the earlier durable allocator positive.
All 9 Stage A admission, 22 late-attach and 25 creation regression cases
passed on the same binary. The compiled correlation, window, retail
profile and admission diagnostics controls and 10 synthetic preflight
tests also passed from the replay.

The offline candidate extends the four-site observer to bracket one
operator-selected Save2 load and the subsequent period of responsive
gameplay, with an optional Lodge entrance. Phase 1 used disposable
processes and read-only disk checks. The live session required separate
written approval of the reviewed snapshot.

[SRR-009](SRR-009-retail-debugger-admission-and-stage-a.md) established
bounded `NOT_OBSERVED` in two post-arm title and menu windows totaling
84.281 seconds. Its two earlier attempts ended with
`INSTRUMENTATION_INCOMPLETE` before attachment. The successful attempt
sealed the scientific prefix through sequence 500, independently verified
normal game exit, and had an administratively closed observer after exit.
Its bounds exclude pre-arm startup, save loading and gameplay.

## Scientific contract

The proposed observation uses the same authenticated retail 1.16.244.0
process epoch, image and native runtime checks, non-killing debugger policy,
and four hardware slots in DR0–DR3 order at RVAs `0x9518FD`, `0x5932EF`,
`0x77C470`, and `0x779760`. The access mask remains `0x00100410`
(`PROCESS_QUERY_INFORMATION | PROCESS_VM_READ | SYNCHRONIZE`). The
[native predicates](SRR-003-retail-allocator-invocation-and-dispatch.md#native-path-and-predicates),
[same-epoch, thread birth and frame join](SRR-005-live-observation-preparation.md#sites-and-causal-join),
and [module policy](SRR-009-retail-debugger-admission-and-stage-a.md#admission-and-scope-of-coverage)
govern acquisition.

| Window | Journal boundaries |
| --- | --- |
| Post-arm title and menu transition | `ATTACH_ARMED` → `MAIN_MENU_CONFIRMED` |
| Menu and preload navigation | `MAIN_MENU_CONFIRMED` → `LOAD_BEGIN` |
| Primary load and arrival | `LOAD_BEGIN` → `PLAYER_CONTROL` |
| Primary post-load observation | `PLAYER_CONTROL` → STOP, or `LODGE_BEGIN` if the operator elects the crossing |
| Optional Lodge transition | `LODGE_BEGIN` → `LODGE_END` |
| Optional responsive interior | `LODGE_END` → STOP |

The intervals use half-open journal sequence bounds in event pump order.
An event pending at a boundary can be recorded in the following interval.
The markers are operator reports. In particular, `PLAYER_CONTROL` marks
when the operator reported control of the character, and engine work may
continue afterward. A marker establishes no native hit or UI causation.
A validated native chain can span markers and keeps the sequence, process,
thread birth, frame and stack ancestry checks of the earlier observer.

Assign `OBSERVED_INVOKED` to the callback arrival window and
`OBSERVED_REACHED_ALLOCATOR` to the correlated allocator arrival window.
Each metric can independently have bounded `NOT_OBSERVED` where its
coverage is qualified, or `INSTRUMENTATION_INCOMPLETE` where a failed
boundary, uncertain chain or gap leaves it unresolved. A load or optional
Lodge transition interrupted by STOP lacks its intended arrival boundary.
A closed preload window can still be assessed when the load never starts.
Positive chains in the verified prefix remain assessable after local gaps
or later exit and retirement failures. Use the per-window verdicts for the
research question. The terminal receipt's run-level positive covers any
eligible post-arm window, and the four sites report invocation and allocator
arrival. They do not measure biome generation or output.

## Implementation and qualification

The observer accepts Stage B with `--stage-b --approved-stage-b`. Title,
STOP and retirement retain the existing request files and epoch binding.
Each post-arm phase requires the run token, sequence and one-use challenge
from the preceding durable acknowledgement. The observer consumes and
journals refusals of stale, misordered or wrong-epoch requests. A verified
phase opens the next window without clearing correlation tokens. STOP
publishes the labelled per-window verdicts in the hashed scientific
journal prefix, independently of a terminal debugger receipt. If the
STOP sidecar fails to publish, the operational watermark can include
the STOP row while its closing boundary remains scientifically
unverified. The observer issues no `STOP_DURABLE` in that case.

The [Stage B harness](../tools/srr006/qualify_stage_b.py) starts only
disposable children and writes new raw journals, subprocess transcripts,
per-case JSON results and exit witnesses. It exercises early title, menu
and load STOP and both optional Lodge paths. A quiet load covers refusals,
multiple periodic checks, thread birth and exit, and incidental module
changes. A delayed native chain crosses `PLAYER_CONTROL` and is followed
by a gap confined to the Lodge transition and a post-seal crash. A separate
fixture induces a STOP sidecar write failure after journal publication.
The event pump does not stop
on inactivity, elapsed time or hit count. Only fixture supervisors use
watchdogs.

Build with the [SRR-006 fixture commands](SRR-006-four-site-hardware-observer.md#reproduce-the-fixture-controls)
using x64 MSVC 14.51.36231 and SDK 10.0.26100.0. Add `/Brepro` on the
link line to match the freeze. Use Python 3.14.3 x64, matching native
System32 `ntdll.dll` and the lawfully obtained matching retail file for
the profile unit test. The retail file is read as data. Keep the
`__COMPAT_LAYER` environment unset. From the checkout root, set
`$observer` to the new binary and `$out` to an existing ignored test
parent with 40,134,217,728 caller-available bytes on both C: and D:.
Use new output names.

```powershell
python -E -B tools/srr006/qualify_stage_b.py $observer "$out/stage-b"
python -E -B tools/srr006/qualify_stage_a.py $observer "$out/stage-a"
python -E -B tools/srr006/qualify_attach.py $observer "$out/attach"
python -E -B tools/srr006/qualify.py $observer "$out/creation"
python -E -B tools/srr008/test_preflight.py
```

Also run the correlation, window, retail profile and admission diagnostics
executables from the fixture build. The admission diagnostics executable
accepts a new evidence directory as its argument. The phase publisher
writes a request file in the private run directory. The STOP verifier
reads the sidecar and exact journal prefix and prints JSON. The exit
witness opens a read-only handle, verifies image and process epoch, and
writes independent bound and exit receipts. These tools leave Ghidra
untouched.

Representative raw receipts are held locally under
`.local-work/codex/SRR-010/regression/stage-b/`. The quiet STOP SHA-256
is `e603b1c8c12ca1bdb29e3feef0831f7417f961626728dcd7830a9b7d60e1f479`
(40,939 bytes). The cross-phase STOP SHA-256 is
`aede59595782410570c2a7ceaf1a850e594a5efde1eca2353cb06d346e81cd10`
(44,407 bytes). The candidate observer SHA-256 is
`28c9b8d3c92f4e833b3bf588761bcaa3108d76f11d59a11c4935fb68ebbbbaed`.

## Custody

Starting HEAD `b976d43b6cb4fdb73d674ae92f1b11fd80bd71c6` and index SHA-256
`e7cf714c4e1b228b1a262ba7742bb03230bb918b819ae8e1979defceb9743d60`
were recorded with the initial worktree, which held the supplied untracked
brief. That brief is outside the task patch. The
[SRR-009 publication inventory](SRR-009-publication-verification.md)
identifies the prior capture and its method. The retained Stage A verifier
rechecked the successful sealed capture and original protection receipts.
The retail file and native Windows runtime match the
[Stage A pins](SRR-009-retail-debugger-admission-and-stage-a.md#inputs-and-applicability).

Phase 1 before and after receipts independently verified all 98 Documents
and 95 Steam remote protected pairs against their backup counterparts.
Both designations matched, transient records agreed, and there were zero
unclassified or other entries. Stored Cloud and overlay flags, shared
Steam settings and cache, app manifest and effective save-path checks
agreed. The complete Steam `localconfig.vdf` file identity and digest
changed while the parsed per-game overlay flag stayed off. C: and D:
remained above the floor including reserve.

Use the existing populated save directories. The private Save2 reference
has 2,475,440 bytes and SHA-256
`1ac3d496e532b6286d983a1449946ba4fe34a34e66295c9d1d7da677772903d1`.
Its role is retention and recovery. Save selection in Phase 2 is the
operator's ordinary menu choice, with a short visible identification
record. The claim is about the bound process during the observed interval.
Report ambiguous or unexpected choices and narrow the Save2-specific
interpretation accordingly. Logs, backups, private policy, executable
inputs and output binaries stay in local custody.

## Reviewed Stage B run card and authorization proposal

This is the historical Phase 1 proposal retained as the method record.

The proposed authorization covers **one** Steam dispatch, **one**
operator-selected Save2 load, STOP, normal Quit, read-only postflight,
and contingent exact-observer-only closure after verified target exit.
The operator must explicitly include a Lodge crossing in the same
authorization for that contrast. The maintainer may quote the reviewed
manifest and approved binary digest from the handoff when authorizing.

1. Use the same ordinary, non-elevated interactive account and session as
   Steam. Verify the candidate binary digest, native runtime, app and
   executable pins, URI handler, no pre-existing game process, Cloud and
   per-game Steam overlay off, and operator confirmation of NVIDIA overlay
   off. Use the [Stage A admission run card](SRR-009-retail-debugger-admission-and-stage-a.md#draft-stage-a-run-card)
   for environment and origin checks. Allow logged Steam-component drift
   with verified origin. Set `$session` to a fresh private evidence
   directory with a trusted ACL and no reparse components, `$runDir` to its
   as-yet nonexistent `observer-run` child, `$observer` to the frozen
   binary, `$python` to the pinned x64 interpreter, `$cfg` to the frozen
   private config and `$retail` to the exact installed executable path.
   Check both drives before material write stages as above.

   ```powershell
   & $python -E -B tools/srr008/preflight.py protection --config $cfg --output "$session/pre-protection"
   & $python -E -B tools/srr008/preflight.py environment --config $cfg --output "$session/pre-environment"
   ```

   Inspect receipts for `ok`, both namespaces' 98 and 95 independently
   backed protected pairs, both designations, zero unclassified and other
   entries, matched build, effective save path, Cloud, overlay and SFSE
   fields. A material discrepancy in input identity, protection or restore
   capability blocks dispatch. Leave the original saves, backups and
   relevant settings in place.
2. Run the reviewed observer with durable stdout and stderr retained.
   Record its exact PID, creation epoch and executable identity while alive.

   ```powershell
   $observerProcess = Start-Process -FilePath $observer -ArgumentList @(
       '--stage-b', '--approved-stage-b', ('"{0}"' -f $runDir)) -PassThru -WindowStyle Hidden `
       -RedirectStandardOutput "$session/observer.stdout.txt" -RedirectStandardError "$session/observer.stderr.txt"
   $observerBirth = $observerProcess.StartTime.ToFileTimeUtc()
   ```

   Once `BASELINE_DURABLE` is verified, record intended URI, UTC, observer
   hash and dispatch result. Dispatch once with
   `Start-Process 'steam://rungameid/1716740'` as approved. Keep the
   responsive title card open after the target appears.
   Set `$run` to the complete `TARGET_BOUND` token. Before title
   confirmation, run the exit witness from a separate shell and verify
   its bound receipt. It keeps its own read-only handle through exit.

   ```powershell
   & $python -E -B tools/srr008/watch_exit.py $run $retail $session
   & $python -E -B tools/srr006/stage_a_marker.py $runDir $run TITLE_CONFIRMED
   ```

   The second command runs in the controller shell after the operator
   confirms title responsiveness and `exit-witness-bound.json` exists.
   Require durable `ATTACH_ARMED <seq> <challenge>` and verify the
   stopped-admission and arming rows. Time before verified arming is
   uncovered.
3. The operator advances to the main menu and confirms responsiveness.
   Publish the first phase below using the sequence and challenge from
   `ATTACH_ARMED`. For each line, set `$prior` and `$challenge` to the
   values from the preceding durable acknowledgement. Wait for the
   respective acknowledgement and verify its checkpoint.

   ```powershell
   & $python -E -B tools/srr006/stage_b_marker.py $runDir $run MAIN_MENU_CONFIRMED $prior $challenge
   & $python -E -B tools/srr006/stage_b_marker.py $runDir $run LOAD_BEGIN $prior $challenge
   & $python -E -B tools/srr006/stage_b_marker.py $runDir $run PLAYER_CONTROL $prior $challenge
   ```

   Wait for `MENU_DURABLE`. The operator navigates to Save2 and records
   the visible character, level and location as available. Publish
   `LOAD_BEGIN` while awaiting the actual selection, then wait for
   `LOAD_BEGIN_DURABLE` before the operator selects and loads that save
   once. Wait for the operator to report a controllable character before
   issuing `PLAYER_CONTROL`. After `PLAYER_CONTROL_DURABLE`, continue
   observing for a coherent interval chosen by the operator.
4. If specifically authorized and practical, the operator may make one
   ordinary entrance into the Lodge from nearby. Publish `LODGE_BEGIN`
   with the player-control acknowledgement. Wait for `LODGE_BEGIN_DURABLE`
   before entering and acknowledge `LODGE_END` only after the interior
   is responsive. Wait for `LODGE_END_DURABLE`. Omit both markers when
   the crossing is skipped. Use the same publisher and predecessor
   arguments as in step 3.

   ```powershell
   & $python -E -B tools/srr006/stage_b_marker.py $runDir $run LODGE_BEGIN $prior $challenge
   & $python -E -B tools/srr006/stage_b_marker.py $runDir $run LODGE_END $prior $challenge
   ```
5. At the operator-selected end, issue STOP. Verify the seal against the
   acknowledged `$stopSequence` and retain the JSON report before
   requesting normal retirement.

   ```powershell
   & $python -E -B tools/srr006/stage_a_marker.py $runDir $run STOP
   & $python -E -B tools/srr006/verify_stage_b_stop.py $runDir $run $stopSequence > "$session/verified-stop.json"
   & $python -E -B tools/srr006/stage_a_marker.py $runDir $run QUIT_REQUESTED $stopSequence
   ```

   On the clean path, require verifier success and wait for
   `RETIRE_DURABLE` before normal operator Quit. If admission or a
   boundary is refused, capture the diagnostic and exact last verified
   prefix. A marker refusal cannot
   advance the phase. For an unsafe or unverified continuation, I/O
   failure or unresolved identity, keep evidence and follow the
   [existing recovery policy](research-workflow.md#live-observation-and-recovery).
   Record missing markers and affected coverage. After an unsealed STOP
   or an unconfirmed retirement request, preserve the last verified
   prefix and continue servicing events through normal operator Quit
   when safe. There is no repeat launch,
   reload or additional travel in this authorization proposal.
6. Verify the exact target's exit independently. Run protection and
   environment checks again using new `post-protection` and
   `post-environment` outputs, inspect the same fields, compare protected
   identities and settings, and record incidental save writes or autosave
   and exit-save behavior without restoring or removing files. Independently
   review the scientific and operational prefixes and their separate verdicts.
7. Normal debugger retirement requires its own evidence. If it is
   unconfirmed and the observer is orphaned, contingent administrative
   closure requires prior written scope for that action, independent
   exact-target exit evidence, reauthentication of the observer PID,
   creation epoch and approved executable on a retained handle, and
   preservation and verification of the scientific STOP and available
   operational prefixes. Terminate only that verified orphaned observer,
   document its administrative exit code, and reverify the prefixes.
   While the exact target is live or its exit uncertain, preserve the
   observer and escalate recovery. No forced game termination or
   unapproved detach is in scope.

## Phase 1 review and handoff

<!-- srr010-review:start -->
**READY FOR STAGE B APPROVAL.** Independent challenger `challenger`
accepted all eight Phase 1 criteria. The challenger exercised wrong-phase
and false-quiet cases, STOP corruption and publication failures,
same-frame continuity across the player-control boundary, and
exact-process exit and termination safeguards. The independently
replayed source rebuilt the exact candidate binary.

Reviewed manifest SHA-256
`8dd59033805f5d2a75c5460703bc8c6f0ae6361738945fd89599d630abcefce7`.
Only this marked block is excluded from the dossier entry. The independent
report is `.local-work/independent-review/SRR-010/review.md`, SHA-256
`9cd9a4d8ac41c0e86d7e209133638a3f979c3b1e719336ca39fe5e37e07bf54b`.
The final task-only patch is `.local-work/diffs/SRR-010.diff`. Retail
Stage B authority remains withheld pending written approval.
<!-- srr010-review:end -->
