# SRR-010 — Control B: Debugger-Only Save2 Load Qualification

**Implementation and independent-review brief for Codex**  
**Status:** Offline preparation only — **no retail launch, attach, or save load authorized**  
**Repository** `starfield-resource-research`

**Investigation:** Continue SRR-010; do not create SRR-011 merely for this operational control.

## 1. Purpose and decision to be tested

Three separately authorized SRR-010 sessions successfully attached the native four-site observer but ended during the operator-selected Save2 load with Starfield exit status `0x80000004` (`STATUS_SINGLE_STEP`), before player control. Their load/arrival outcomes remain `INSTRUMENTATION_INCOMPLETE`; the logs did **not** contain a corresponding delivered single-step exception or faulting instruction. Reducing running-thread monitoring did not prevent the repeated exits. Preserve all three attempts and their evidence exactly.

The maintainer subsequently performed **Control A**, an ordinary Starfield launch **without the research debugger**: they manually loaded the familiar Save2, reached settled gameplay, and exited normally. This is a **maintainer-reported operational control**, not an independently instrumented observation or a before/after save-integrity certificate. Do not retrofit evidentiary claims it cannot support or request a repeat solely to add paperwork.

**Control B question:** Can the same pinned retail Starfield build complete the same ordinary Save2 load and reach settled gameplay **while attached to our native Win32 debugger, but with no hardware execution breakpoints armed**?

Control B is a **discriminating operational control**; it has **zero resource-allocation detection sensitivity by design**. It must never produce `OBSERVED_INVOKED`, `OBSERVED_REACHED_ALLOCATOR`, or a resource-allocation `NOT_OBSERVED` verdict. Its outcomes are instead: `LOAD_SURVIVED_DEBUGGER_ONLY`, `LOAD_FAILED_DEBUGGER_ONLY`, or `CONTROL_INCOMPLETE` with specific stage/coverage and target-exit detail. Even success establishes compatibility only for that exact run, not that four-site debugging is safe. Do not claim `0x80000004` causation from the exit code alone.

**Primary deliverable:** a small, separately selectable, independently qualified debugger-only control and a precise run card, frozen for **a later, separate one-session live authorization**. This assignment must **stop before retail execution**.

## 2. Sources and boundaries

The original assignment started from the then-uncommitted SRR-010 source
and the private records of the three live attempts. The tracked
[Stage B dossier](../SRR-010-stage-b-save-load-observation.md) now records
their evidence identities, findings, reviews and limitations. Background
includes `AGENTS.md`, the [research workflow](../research-workflow.md),
[SRR-009](../SRR-009-retail-debugger-admission-and-stage-a.md) and the
SRR-005/006/007/008 research and fixture contracts.

Specifically inspect the existing `tools/srr006/observer.cpp`, relevant headers and fixture harnesses; `tools/srr006/stage_b_marker.py`; and `tools/srr008/watch_exit.py` and read-only protection tools. Consult sibling reference-handle/outpost source only if useful for the debugger-without-DR precedent, and keep earlier live results differentiated from disposable results.

The current approved Stage B observer uses the four Starfield RVAs `0x9518FD`, `0x5932EF`, `0x77C470`, `0x779760`. **Control B must install none of them**. Retain the four-site scientific implementation **unchanged and available** for any future separately authorized scientific trial; do not trade away its detection sensitivity to make Control B succeed.

## 3. Smallest safe implementation

Add a clearly named, fixed **debugger-only control mode** to the existing native observer, or a minimal adapter sharing its established attach/event-pump code. Prefer the less invasive of these based on actual source. It must be unmistakably distinct from `--stage-b` and must default to refusing live use without the established explicit human approval gate. Avoid an arbitrary-PID/general-purpose debugger CLI and do not repurpose a fixture mode to operate retail.

**Required native behavior:**

- Retain the **same retail authentication**: designated interactive account and Steam session, pinned Starfield executable/path and process creation epoch, independent Steam attribution, critical mapped code/runtime and module-origin checks, prior debugger-ownership check, reviewed handle rights (`PROCESS_QUERY_INFORMATION | PROCESS_VM_READ | SYNCHRONIZE`), and meaningful diagnostic refusal/watermark reporting. Noncritical Steam updates remain recorded drift, not automatic rejection.
- Use `DebugActiveProcess` only after the above gates, then apply and verify the reviewed **non-killing debugger policy**. Attribute the debugger-owned initial break-in using the existing qualified method and **service/continue native debug events correctly**. Unrelated first-chance exceptions must retain their existing dispositions; do not globally swallow exceptions, emulate instructions, change RIP, or invent a success when the target dies.
- **Never write DR0–DR3, DR6/DR7, TF or RF for a research breakpoint in Control B.** No hardware execution slots, no INT3 research breakpoints, no thread-wide arming, no breakpoint-hit/correlation path and no surrogate hooks. Reading already available context for diagnosis is optional and must not lead to writes or a false ownership claim. The OS-generated debugger attach break-in is expected and is **not** a research breakpoint. Make the absence of research breakpoint installation/writes visible and testable, not a console assertion only.
- Preserve reasonable event-loop observation of process/thread/module events, continuation successes/errors, target identity, health, operator phases, exact-process exit and journal integrity. Prefer existing journal/marker functions, but **do not require `ATTACH_ARMED`, four-slot readbacks, or a scientific STOP** to execute this no-DR control. Introduce unambiguous `DEBUGGER_ONLY_READY` and load/control phase acknowledgments as needed; these denote debugger connection and operating readiness, **not** scientific hardware coverage.
- Choose a deliberately quiet operational footprint: no extra running-thread suspension sweeps for science, no user-driven debugger breaks to create artificial phase events, no timer-driven interruption merely to obtain a marker. Phase markers should be durable and bound to the exact process/run epoch without fabricating native execution evidence. Keep any genuine safety checks needed for debugger service.
- Keep the independent exit witness in its **separate process/shell**, bound before the operator loads Save2, without blocking the main control flow. Preserve stdout and stderr, refusal watermarks and exact-process exit status. A subsequent abnormal exit must be reported separately from observer completion.
- Normal operator-controlled Quit is preferred after settled gameplay. The eventual approval proposal may include **observer-only** administrative termination **after** independently verified target exit, retained evidence and exact observer PID/creation epoch/image reauthentication. No game termination, unapproved active detach, forced remote break or automatic relaunch.

Avoid broad refactoring of shared four-site code. If making a shared change, prove that unchanged `--stage-a` / `--stage-b` paths and their scientific predicates remain equivalent. The inability to obtain a focal resource observation is **intentional for Control B only**.

## 4. Proposed operator procedure (for later approval, not authorized here)

One ordinary Steam launch under the maintainer's non-elevated interactive Windows account. The maintainer performs all UI actions. Normal populated Saves directories remain in place; they select the **same familiar Save2** as before. Do not create a second game-visible copy, require an empty namespace or add forensic save-selection infrastructure.

1. Fresh, scoped and non-destructive preflight: pinned binaries and control build; Cloud and per-game Steam overlay disabled; operator reconfirms NVIDIA overlay state; no inherited `__COMPAT_LAYER`; no existing Starfield instance; exact account/session; fresh private output directory; protected original/backup comparison, designations, unclassified entries; both drives retain at least **40,000,000,000 caller-available bytes plus the established reserve**. Do not interpret benign Steam configuration/hash drift as a blocker when the material settings and critical identities are unchanged.
2. Start the reviewed **Control B** service, obtain durable Steam baseline, and then one separately approved Steam URI dispatch. Authenticate exact Starfield epoch. Operator confirms responsive title. Attach, attribute the initial debugger break-in, verify non-killing mode and debugger-pump readiness **without arming breakpoints**. Publish `DEBUGGER_ONLY_READY` with an independently verifiable journal boundary.
3. Operator advances to responsive main menu; publish an acknowledged menu marker. Publish a durable `LOAD_BEGIN` **before** instructing the operator to select the familiar Save2. These markers must be synchronized individually; never run the sequence speculatively as a batch.
4. Operator loads Save2 once. If player control returns, they confirm **settled, responsive gameplay** and the observer records an acknowledged `PLAYER_CONTROL` / `SETTLED_GAMEPLAY` phase (use the smallest defensible protocol). No Lodge crossing is required or authorized for this control; no additional movement, travel, reload or save. Let the operator choose a sensible observation endpoint; no arbitrary scientific inactivity deadline.
5. Capture a durable **operational** end marker/receipt. Operator uses normal Quit; the separately retained witness confirms process identity and exit. Observe debugger exit handling and retire/close the observer as qualified. Compare protected saves/backups and settings postflight. Distinguish game exit, observer exit, cleanup and evidence completeness.

If save loading fails, preserve the observed last phase and exact native exit code; don't automatically conclude that the debugger caused it or that Save2 is faulty. If debugger admission fails, report that as `CONTROL_INCOMPLETE`, not a failed load. A user-reported successful load with a dead event pump is also incomplete unless the control has independently verified its attachment/event-service obligations. No retry implied.

## 5. Disposable qualification and falsification

Use genuine disposable child processes and the established Windows toolchain. Add **focused Control B fixtures**, rather than duplicating the full research observer or building a general crash diagnostic framework. Cover at minimum:

1. A successful debugger-only attach, verified initial break-in, explicit non-killing mode, native event service, a synthetic load/settled phase, normal exit, and durable control receipt; assert **zero research DR writes, zero research breakpoints and zero eligible scientific verdicts**.
2. Same workflow with a target that creates/exits threads and loads modules during the simulated load. Assert event-service completeness, no special breakpoint machinery, continued liveness, and exact epoch handling.
3. An already-debugged target, wrong executable/epoch or otherwise invalid authentication and an actual attach failure; assert attributable refusal, no accidental attach/arming, and a trusted evidence boundary.
4. An abrupt target exit during the simulated load, including a modeled exit code `0x80000004`; preserve the exit without inventing a delivered exception or claiming causal attribution.
5. Journal/marker refusal, wrong phase/predecessor and write/STOP-equivalent operational seal failure; no falsely successful `LOAD_SURVIVED_DEBUGGER_ONLY` result.
6. The no-DR mode must not break the ordinary four-site fixture contract: run relevant **SRR-010 Stage B and SRR-009 regression** suites, extending them only as actual shared changes warrant. Verify four-site positives and quiet-coverage qualification remain intact on their own modes.

Test both native event servicing and the independent witness using disposable processes. Preserve failed controls as evidence rather than hiding them through repeated attempts. Fixture-only deadlines may bound broken tests; **do not transfer them to live scientific waits**. Avoid relying solely on synthetic mocked API returns for success claims.

## 6. Evidence, reporting and review

Keep SRR-010's **results-first** principal dossier. Record Control A as operator-reported, uninstrumented and without postflight protection certification. Record Control B Phase 1 as **offline qualification only**. Preserve all three historical Stage B incomplete attempts, their evidence, reviewer conclusions and previous patch chronology. An offline success must **not** be described as successful retail Save2 loading.

Provide a concise capability matrix showing what the previous four-site observer measures versus Control B's **operational-only** discrimination. Explicitly identify what a future successful or failed Control B would and would not establish. Note that a successful debugger-only load would point toward hardware instrumentation or its associated handling as a variable, without proving it caused earlier failures; a failed debugger-only load would implicate an earlier common factor but not isolate its cause.

Apply the repository's provenance, dependency, privacy, publication and custody workflow. Avoid proprietary binaries, raw saved games, personal account details and actual debug journals in the patch. Keep private raw evidence under ignored `.local-work/codex/SRR-010/` and independent review under `.local-work/independent-review/SRR-010/`. Do not alter Steam, saves, Ghidra, or other project repositories in Phase 1.

Use an **independent challenger** with the original brief, live history, exact proposed implementation/diff and primary disposable records. The challenger should deliberately attempt to falsify: no-DR enforcement, absence of research conclusions, debugger-event correctness across load, identity/epoch gating, reliable exit observation, evidence durability, and preservation of the four-site mode. Rework adverse cases until the declared criteria pass, or report a real blocker; do not paper over a failure with documentation.

## 7. Acceptance criteria and handoff

- **CB-AC1:** Prior results, artifacts, protected sources, and three historical failed load observations preserved; Control A characterized no more strongly than the operator report supports.
- **CB-AC2:** Explicit, gated debugger-only retail design with **zero research DR writes/breakpoint arming**, accurate ready/phase/exit protocol and no accidental scientific negative/positive conclusions.
- **CB-AC3:** Verified native debugger ownership, thread/module event continuation and non-killing operating policy on disposable targets, including adverse exit handling.
- **CB-AC4:** Familiar one-save, one-session operator run card, no save reorganization or Lodge contrast, proportionate pre/post protection and separate exit witness.
- **CB-AC5:** Existing four-site observer scientific sensitivity, mapping/identity requirements, causal joins, seals and regression behavior preserved.
- **CB-AC6:** Focused native tests, fault/negative controls and proportional regression passed with raw evidence and declared limitations.
- **CB-AC7:** Dependency/privacy/publication checks, exact binary/source pins, reproducible build, clear result/operational reporting, task-only patch and correct UTF-8.
- **CB-AC8:** Independent challenger accepts the substantive snapshot; final deterministic manifest and complete Git-native patch replay match all supplied files byte-for-byte.

**At the engineering gate, stop** and return: the exact frozen Control B binary and full SHA-256, substantive manifest, qualification receipts, independent review, the updated SRR-010 dossier with a **short proposed single-session authorization**, and a complete task-only diff against the actual starting Git/worktree state. Describe the marker and launcher commands precisely. If new worktree material derives from existing uncommitted SRR-010 paths, retain cumulative chronology and avoid dropping unstaged additions. Leave files **unstaged, uncommitted and unpushed**.

**Required final disposition:** `READY FOR CONTROL B LIVE APPROVAL` if all criteria pass, otherwise `REWORK` or `BLOCKED` with the exact unresolved condition. **No game launch, retail process probe, live debugger attachment, Save2 load, or Lodge crossing is authorized by this brief.** A subsequent maintainer authorization may approve **one** live Control B run. Scientific Stage B retrial authority remains withheld.
