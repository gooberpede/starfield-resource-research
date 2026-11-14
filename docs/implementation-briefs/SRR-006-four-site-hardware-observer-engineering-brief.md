# SRR-006 — Four-site hardware observer engineering and offline qualification

## Assignment and controlling question

In `starfield-resource-research`, implement and independently qualify a **four-site, per-thread Win32 hardware-breakpoint observation controller** for the pinned retail allocator-dispatch path documented in SRR-003 and SRR-005. Answer:

> Can the proposed controller preserve and correlate the four native observation sites, correctly cover initial and newly created threads, handle competing debugger events and failures, and retire safely **on disposable targets**, sufficiently to justify requesting a separate, limited Starfield Stage A live authorization?

The scientific question of whether Starfield actually invokes the allocator **remains open**. This assignment is offline engineering, not an authorization to launch Starfield, attach to it, load a save, deploy SFSE, or execute a live retail experiment. Return `READY FOR LIVE APPROVAL` only as a **qualified engineering recommendation**, never as proof of retail safety, startup coverage, or allocator execution.

Read `AGENTS.md`, `docs/research-workflow.md`, `docs/PROVENANCE.md`, `docs/SRR-002-retail-static-reconnaissance.md`, `docs/SRR-003-retail-allocator-invocation-and-dispatch.md`, `docs/SRR-005-live-observation-preparation.md`, its original brief, and the relevant glossary and structure register. Check the current checkout before acting; do not assume HEAD or working-tree cleanliness. Examine the specific maintainer-owned reference-handles and outpost-research Win32 debugger, hardware breakpoint, SFSE, startup and failure records identified by SRR-005. Reuse or adapt prior art selectively; do not copy entire frameworks or import their historical live authorization. Treat preserved failures as engineering constraints, not as an invitation to rerun them.

## 1. Protected baseline, authority and workspace

- Pin the **actual** installed and analysis-copy `Starfield.exe` to SHA-256 `7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28`, file/product version `1.16.244.0`, and distinguish Steam build `23518663` from byte identity. The image base in static analysis is `0x140000000`; actual runtime addresses require the observed loaded module base. Record the actual Ghidra/toolchain/OS and prior-art revisions used. Do not infer that the pinned retail executable will run successfully under the proposed debugger.
- Scope pre/post identity checks to **actual task dependencies**: relevant executables, source, manifests, test fixtures, original saves if read, and any Ghidra database files accessed. Do not inventory or hash unrelated historical `.local-work/` trees. Preserve all existing tracked files and local material; record starting and ending HEAD, index and status, including unrelated pre-existing changes.
- Put working copies and disposable test outputs in `.local-work/codex/SRR-006/`, detailed independent challenge in `.local-work/independent-review/SRR-006/`, and a Git-native review patch in `.local-work/diffs/SRR-006.diff`. A reusable, project-authored controller and its small tests may be tracked once reviewed; bulky logs, binaries, dumps, original saves and full native excerpts remain ignored and unpublished.
- Before material writes, and during sustained writing, verify **caller-available free space on both C: and D:** after projected growth is at least **40,000,000,000 bytes on each**. Missing readings or inadequate headroom stop the affected write safely. No maximum `.local-work/` size is imposed. No unapproved installation, external download, source modification to sibling repositories, configuration change, game execution, staging, commit or push.

## 2. Controller contract and observation model

Implement a narrowly scoped, configuration-pinned controller consistent with the four-site plan in SRR-005, without hard-coding a claim about actual game invocation. The proposed site RVAs are:

| RVA | Purpose |
| --- | --- |
| `0x9518FD` | Module-pointer guard sample |
| `0x5932EF` | Iterator pre-call, receiver/vtable/source-return discrimination |
| `0x77C470` | PNDT callback entry |
| `0x779760` | Planet-level orchestrator entry |

Preserve SRR-005's checked register/stack relationships, receiver at `image base + 0x4B3D9E8`, indirect slot `+0x10`, early/later saved sweep return RVAs `0x94E57C` and `0x94EF5C`, form-type read limitations, direct-call return and frame-ancestry checks. Source material is authoritative over this summary. Validate each relevant code window and mapping identity against the pinned source before any eventual retail arming. Do not substitute an unrelated executable or guessed symbol during a future game attempt.

Controller design must address:

1. **Launch and identity:** Own the disposable child through `CREATE_PROCESS_DEBUG_EVENT`; identify its exact process/creation epoch, loaded image and initial thread before ordinary user-mode continuation. Handle `CREATE_THREAD_DEBUG_EVENT` before continuing a new thread, reconcile exits, and detect unobserved process handoff rather than silently following a Steam URI or attaching late. The ability to launch Starfield through `steam://rungameid/1716740` is **not** proof that the debugger owns the game's creation event. Assess the primary direct launch and separately proposed post-title attach boundaries without running Starfield.
2. **All four slots simultaneously:** Safely reserve DR0–DR3 on each covered thread and verify `DR7`/address readback and original register state. Refuse conflicts or unverified ownership; do not overwrite other agents' debug state. Check the exact debug-event ownership, RIP/exception address, DR6, TF/RF and unrelated exceptions. Continue only qualified owned hits, preserving original instruction bytes and without general software breakpoints, generic stepping or RIP rewrites. Record context manipulation and the residual observer effect. Confirm how debug state is cleared/retired at each supported boundary.
3. **Causal evidence:** Implement SRR-005's versioned JSONL and final receipt, durable sequence numbers, process/thread birth identity, site RVAs and loaded-base validation, checked reads, caller-return and frame correlation. Retain first qualifying iterator→callback evidence even without allocator arrival. Reject frame reuse, cross-thread/process joins, ambiguous reads and gaps; classify `OBSERVED_INVOKED`, `OBSERVED_REACHED_ALLOCATOR`, scoped `NOT_OBSERVED`, `INSTRUMENTATION_INCOMPLETE` and `TARGET_FAILED` conservatively. Preserve the difference between an observer hit and a game-semantic conclusion.
4. **Concurrency and evidence integrity:** Simulate busy generic iterator traffic, multiple threads, interleaved stops, duplicate/ambiguous frames, new threads and exits, queue pressure, storage errors, and interruption. Bound memory and writer queues by an evidenced budget; on overflow, mark the affected interval incomplete instead of silently dropping records. Ensure events can be handled without blocking the stopped thread on lengthy filesystem work. Report attempted, accepted, rejected, flushed and lost/uncommitted ranges.
5. **STOP, retirement and recovery:** STOP closes eligibility for new scientific observations, **not** the event pump. Drain and flush, keep servicing owned debugger events, and qualify a clean normal-child-exit sequence and wait on the *same* process handle. Never simply kill the debugger, detach on an unsafe pending exception, or assume that restored bytes prove thread state is clean. Exercise an exact-child emergency path on disposable targets; retail force-termination, detach or recovery requires separately approved authority. Distinguish target survival, instrumentation health, completeness of durable evidence and scientific outcome.

Do not silently widen the four-site plan or add a fifth debugger stop. A discovered need to change sites, observer technique, or game startup method is a proposal for review, not automatic scope expansion.

## 3. Time, progress and operator contract — mandatory

**Elapsed time alone is not a failure, STOP condition, or reason to terminate the observer or game.** Hardware breakpoints and high-frequency events may slow a multithreaded target considerably. Long intervals without native hits, title/menu transitions, or operator responses may reflect ongoing work. Do **not** impose arbitrary session deadlines, fixed event-count quotas, short inactivity timeouts, or automatic termination just because the game appears slow.

Separate the following explicitly:

- **Scientific progress:** Has a decisive qualifying event or declared phase transition occurred? No events is not evidence of non-execution unless coverage is demonstrated.
- **Instrumentation health:** Are the debug-event pump, writer, thread coverage, owned slots, process identity and durable records in a known good state? Log heartbeat/progress observations if useful without turning them into scientific events.
- **Target health:** Is the precise experimental child still alive? A long wait or apparently stalled UI is **not** proof of a crashed target. Actual process exit, unrecoverable debugger fault, verified corruption/coverage loss or other evidenced unsafe condition is different.
- **Operator action:** At title card, the user must press a key/button to reach the main menu. Codex may start the game via the separately approved launcher in a later live assignment, but must ask the user to perform UI actions; no automated desktop clicks/key presses or screenshot requirement. Wait for explicit operator phase confirmation. Operator-confirmed timestamps bound an interval but do not prove the exact engine UI transition frame.

For **disposable engineering fixtures only**, finite predetermined scenarios, explicit STOP, and separately documented *safety watchdogs* for hung test children are appropriate; they must have defensible triggers, not be falsely described as scientific completion criteria. The prospective live run card should use named transitions and explicit operator STOP/consent, plus an exceptional liveness/recovery policy requiring later approval. Safety failures, disk-space failures, lost debugger ownership or queue corruption stop the affected operation regardless of how long it has run. Do not weaken safeguards to avoid waiting.

## 4. Offline qualification, including adversarial controls

Do not launch/attach to Starfield, enter its GUI, load Save2 or change installed SFSE/Steam/NVIDIA/Cloud settings. Use synthetic records and disposable multithreaded Windows executables only. Run tests against the **actual final four-site controller**, not only SRR-005's earlier two-site fixture. In the engineering dossier report exactly which conditions were exercised, which remain untested, and why a control is representative.

At minimum, verify: initial process/thread arming before an early TLS callback; newly created workers before first execution; four simultaneous sites on all eligible threads; concurrent hits and unowned exceptions; DR ownership conflict and readback failure; event and thread identity rollover; stack/return/callback-only and full allocator-chain synthetic cases; zero-hit covered window versus gap; missing/unreadable operands; queue overflow and interrupted writes; phased STOP with outstanding events; normal process exit and exact-child emergency recovery; startup/Steam handoff refusal and post-title attach coverage limitations; retained evidence after abrupt failure. Probe nonfatal delayed progress and operator-marker delays without triggering a premature failure. A test that ends under an approved fixture watchdog must not be represented as a scientific negative result.

A failure in a mandatory engineering control is **REWORK** while authorized repair and retesting remain available. Preserve failure evidence; do not merely re-label or exempt it. An actual missing prerequisite or evidenced safety/authority barrier is **BLOCKED** with a precise minimum next action. A bounded negative finding about one startup technique does not by itself complete the controlling controller-qualification question.

## 5. Stage A run card — proposal only

Update the SRR-005 proposed run card or include an explicitly linked revision in a single SRR-006 dossier. **Do not execute it.** Keep Stage A a separate approval covering only an isolated **no-save** retail session, with subsequent Save2 loading and Lodge crossing under another authorization.

The proposed operator sequence must acknowledge **startup → responsive title card → user presses key → responsive main menu → STOP/flush → user-initiated Quit to Desktop → qualified process exit**. Do not treat title card and main menu as the same state. Identify the planned direct-launch method and the distinct `steam://rungameid/1716740` ownership risk; the URI is a proven game starter, not a proven launch-under-debugger mechanism. The main-menu fallback is a *new approved method* with loss of pre-attach coverage, not a silent switch within a session.

For a future approved run, specify an isolated save namespace, independently verified originals/backups, no save loaded in Stage A, pinned executable and configuration/module identity, Steam and NVIDIA overlays off, Steam Cloud disabled and verified, SFSE absent, local evidence destination, phase-marker confirmations, normal exit and separately approved exact-process emergency intervention. User performs any actual GUI actions. Screenshots are optional and must not depend on the Steam overlay. Distinguish tested engineering readiness from untested retail startup/liveness. The plan must avoid automatically restoring Cloud or changing active saves before postflight checks.

## 6. Durable deliverables and review

Prefer **one principal dossier** `docs/SRR-006-four-site-hardware-observer.md` (or equally clear name), indexed from `docs/README.md`, containing method selection/reuse, implementation contract, test matrix with failures, evidence provenance, explicit go/no-go conditions, run-card revision, limitations and next approval request. Place reusable reviewed controller source and minimal fixtures/tests in a sensibly named tracked directory if needed. Document compile/run and clean-up operations for **disposable fixtures only**. Update `docs/PROVENANCE.md`, function/structure registers and glossary only if newly necessary to remove an actual ambiguity; don't create separate prose reports by default. Raw native output, binaries, crash material, unlicensed game assets and operator/private paths stay local. Publication independence must not depend on preserving `.local-work/`.

Use the standing independent challenger sub-agent **after implementation and testing**, one active at a time. Give it the controlling question, original brief, actual code/diff, test commands/results, primary evidence and counterexamples. The reviewer must try to falsify thread coverage, exception ownership, four-slot correctness, writer durability, frame correlation, STOP/exit behavior and the no-timeout rule; do not accept a superficial test-summary endorsement. `REWORK` returns Codex to the **same** assignment with corrections and renewed challenge. `COMPLETE` requires every AC below to pass on the final substantive snapshot. `BLOCKED` requires a genuine documented barrier and minimum requested action. A completed engineering review does not authorize Starfield execution. Keep detailed review rounds in `.local-work/independent-review/SRR-006/`, and a compact, immutable review disposition in the dossier per the established manifest-exclusion procedure.

### Acceptance criteria

| ID | Mandatory evidence |
| --- | --- |
| **AC1 — Scope and protection** | Pinned build/source/tool identities; documented starting and ending HEAD/index/status; scoped input hashes; original saves, existing Ghidra projects and sibling work unchanged; no retail process, SFSE deployment or installed setting change. |
| **AC2 — Implementation and reuse** | Reviewable four-site controller with justified selective reuse of sibling prior art; exact site/receiver/frame contract; four DR slots per covered thread; explicit launch, handoff and late-attach boundaries. |
| **AC3 — Event ownership and causal truth** | Fixture-backed thread creation/exit coverage, conflict/unknown exception handling, RF/context and resume integrity, strict three-event joins and callback-only preservation; incomplete or ambiguous coverage cannot produce false negative or false-positive claims. |
| **AC4 — Health, latency and recovery** | Demonstrated STOP/drain/flush, normal exit, partial/failure and exact-child recovery in disposable targets; busy/delayed/no-event/operator-marker controls show **no arbitrary inactivity or elapsed-time termination**; real health/safety failures still stop safely. |
| **AC5 — Four-site qualification** | Final-controller disposable tests run with all four sites concurrently, multi-thread/TLS/new-worker and adversarial controls; actual results and residual retail untested conditions disclosed; engineering failures corrected or reported BLOCKED. |
| **AC6 — Documentation and handoff** | One coherent dossier and revised Stage A no-save proposal covering title-card/main-menu operator progression, Cloud/overlay isolation, no direct UI automation, distinct approval gates, UTF-8/link checks and Git-native task-only patch replay; 40 GB projected disk-space guards verified. |
| **AC7 — Independent challenge** | Separate reviewer independently checks all AC1–AC6 and material counterexamples, verifies final content/patch and preserved limits; accepts COMPLETE only on the final reviewed snapshot or returns REWORK/BLOCKED with evidence. |

Return the engineering disposition (`READY FOR LIVE APPROVAL`, `REWORK`, or `BLOCKED`) separately from scientific findings (`allocator execution: NOT TESTED`), the reviewer disposition, actual test coverage, deliverable paths, task-only patch and exact future authorization required. Do not stage, commit, push or initiate any live operation.

## Non-goals

Live Starfield startup/attach/observation, Steam/overlay/Cloud changes, Save2 load, Lodge crossing, game native code patching, SFSE installation/deployment, algorithmic-equivalence work, cache lifecycle, and broad instrumentation frameworks. Do not turn engineering success into an engine-behavior claim. No additional mandatory report for each fixture/test/review iteration.
