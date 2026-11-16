# SRR-010 — Stage B Observer Recovery and Prior-Art Reconciliation

**Assignment:** Offline implementation continuation to the existing SRR-010 investigation  
**Disposition sought:** `READY FOR STAGE B RE-AUTHORIZATION`, or a specific `REWORK`/`BLOCKED` explanation  
**Authority:** No new retail launch, save load, debugger attachment, game operation, or commit is authorized by this brief.

## Objective and operating principle

**Primary question:** What is the shortest evidence-supported route to an observer capable of surviving a normal Save2 load and collecting trustworthy four-site resource-allocation observations through return to player control?

Prioritize a **working scientific instrument** over a definitive causal explanation of the prior abnormal exit. The first SRR-010 Stage B session ended during the operator-selected load with Starfield exit code `0x80000004` (`STATUS_SINGLE_STEP`). No owned four-site hits, focal invocations or allocator arrivals were recorded; the load and arrival remain `INSTRUMENTATION_INCOMPLETE`. The preceding post-arming title and menu/pre-load windows are separately qualified `NOT_OBSERVED`. The observer serviced the recorded event pump and exited, and protected save pre/post checks passed. These conclusions and the original evidence are frozen historical facts. **An exit status alone does not prove a delivered single-step exception or establish its cause.**

Codex may use a demonstrated working approach from sibling research even if it leaves the previous failure unexplained. Do not require comprehensive failure attribution as an acceptance criterion. Conversely, a successful startup smoke or disposable fixture must not be presented as proof of safety across save loading.

## Authoritative inputs and preservation

1. Start from the current, uncommitted SRR-010 worktree and dossier; record HEAD, index, status, brief and task-only diff identity. Read the complete SRR-010 Phase 1 implementation, its eight Stage B disposable cases, 56 regression cases, the authorized Stage B transcript, primary journal, exit/STOP-witness records, postflight evidence and independent Phase 2 review. Preserve these byte-for-byte as historic input.
2. Consult committed SRR-009 results-first finding and the relevant SRR-005 native site/causal-join specification. The existing observer is the starting point, not an invitation to construct a new general-purpose debugger.
3. Compare exact versioned source **and retained live evidence**, not only summaries, from:
   - `starfield-reference-handles`: `debugger/native/win32_hardware_observer.cpp`, `starfield_hardware_smoke.cpp`, `run_starfield_smoke.py`, and `docs/experiments/live-starfield-observation-capability-recovery.md`, including hardware/RF, pending-event and cleanup controls.
   - `starfield-outpost-research`: `debugger/exp0002a/native/adapter.cpp`, its native/fixture and review records; `docs/experiments/SOR-EXP-0002A-native-save-thread-mapping.md`; relevant live S1/S2, post-title and save-action evidence.
   - Other focused historical evidence only when an explicit mechanism warrants it. Keep software-breakpoint, startup-smoke, no-DR, one-thread, and four-site experiments distinct.
4. Pin consulted repository commits/source blobs, relevant observer versions, Windows/debugger contexts, and primary evidence identities. Do not assume a sibling `.local-work/` path survives or use inaccessible raw captures as if reviewed. Mark inaccessible evidence and scope claims accordingly.
5. Protect all original Starfield saves, backups, retained Save2 reference, SRR-009 STOP evidence, SRR-010 primary evidence, Ghidra state, settings and ignored historical work. Preserve the existing disk-space floor: **40,000,000,000 caller-available bytes on each of C: and D:** after projected writes and appropriate reserve, with rechecks at material write boundaries.

## Work package A — Focused comparative diagnosis

Perform a **bounded** read-only reconstruction of the SRR-010 load-exit boundary. Examine the final debugger events, reported exception types/dispositions, thread arrivals/exits, owned DR slots, DR6/RF/TF handling, continuation results, module transitions, operator marker ordering and the exact witness/process-exit evidence. Identify any specific mismatch against established debugger contracts. Do not infer an unlogged exception, a faulting instruction, a corrupt save or a definite observer-caused crash.

Create a compact comparison matrix with columns for: actual live result and workload, process/debugger launch/attach arrangement, thread and hardware-breakpoint management, RF/single-step semantics, event-service behavior, save or gameplay transition exercised, evidence durability, target survival and known limits. Separate **demonstrated live success**, **live failure**, **disposable qualification** and **proposed mechanism**.

The analysis should answer only what is useful to selecting an implementation. **Stop pursuing cause attribution** once (a) a testable corrective mechanism is found, or (b) a credible previously working design can be adapted and qualified without explaining the old exit. Do not expand into an open-ended `0x80000004` forensic investigation.

## Work package B — Select and implement a pragmatic recovery candidate

Favor the smallest coherent change that improves confidence in surviving the load transition. The choice may be a targeted correction to current Win32 event/exception/thread handling or reuse of a proven mechanism. Preserve the existing native debugger and its successful retail admission wherever practical. Do **not** transplant a previous project's entire lifecycle, timeout policy, software-breakpoint strategy or recovery machinery merely because one of its experiments succeeded.

**Non-negotiable scientific contract:**

- Retain the four approved SRR-005 site RVAs, their mapped-code verification, per-thread DR0–DR3 ownership/readbacks, and precise focal iterator/callback/orchestrator joins. No invented FormID or inferred engine callbacks.
- Preserve sequence/epoch/thread-generation identity, cross-phase pending frames, hit-versus-invocation distinction, bounded window qualification, truthful `NOT_OBSERVED` and `INSTRUMENTATION_INCOMPLETE` results, and earlier durable positives through later failures.
- Keep fail-closed critical image/ntdll and existing-debugger checks, origin-verified Steam-component drift policy, predicate-level admission refusals, and normal user-operated Save2 selection.
- Maintain exact durable scientific STOP versus operational-prefix separation, stdout/stderr, independent exit witness, protected-save checks, and the post-game-exit observer-only administrative closure policy.
- Do not add arbitrary live inactivity timeouts, event quotas, gameplay automation, extra game loads, intentional save writes, forced game termination, or a requirement to isolate/duplicate the game-visible Save2.

**Pragmatic freedom:** Codex may change the implementation of native exception handling, hardware register servicing, thread population management, relevant event scheduling or retirement **if comparative evidence and tests justify it**. Broad process access rights are acceptable when required for reliable functioning, but new capabilities must not silently expand allowed operations. Account for actual effects on the live target and capture reliability rather than optimizing permissions or elegance for its own sake.

If the preferred solution would be a substantial debugger-backend replacement, major new injection/hooking approach, or change of the scientific observation contract, **do not implement it automatically**. Deliver a tightly specified option, evidence for choosing it, expected additional risk, and a maintainer decision gate. Otherwise implement the bounded fix now; do not stop at a report or require another brief for an ordinary localized correction.

## Work package C — Offline qualification and falsification

Build an exact, versioned observer candidate and qualify it with disposable children. Prefer **focused discriminating controls** over a gratuitous full redesign or endless fixture expansion. Include, as relevant to the selected change:

- Four-site initial and later-thread arming, valid and foreign DR state, owned hardware execution hits, RF/TF/DR6 semantics, exception dispositions, and continuation under busy multithreaded activity.
- A controlled **load-like** transition involving thread churn, module traffic and sustained event activity; demonstrate that the changed path genuinely executes, not just that a mock returns success. Label any model's limits relative to Starfield's real Save2 load.
- Cross-phase iterator/callback/allocator joins, unresolved incoming chains, quiet windows, event loss, STOP and sidecar publication failure, and an abnormal target exit after or before scientific seal.
- Safe normal retirement, exit-event/independent-witness reconciliation and the existing post-exit observer-only administrative closure; avoid retesting unrelated components without a clear reason.
- At least one adversarial test directly tied to the prior-art hypothesis or the hypothesized defect. Confirm that scientific results cannot be falsely upgraded by an incomplete window.

Run the existing relevant regression suites wherever shared code is touched. Maintain evidence for every failing disposable attempt rather than hiding failures behind subsequent passing reruns. Assess whether results on a sandbox child are transferable to the ordinary interactive account; if a discrepancy matters, qualify the narrow control in the **offline disposable** host context, not by probing the live game.

An independent challenger, separate from the integrator, must inspect the actual diff, raw fixture observations and proposed positive claims, seek at least one plausible counterexample, check preserved historical inputs and dependencies, and verify the candidate patch by isolated Git replay. Reviewer activities remain offline. `READY FOR STAGE B RE-AUTHORIZATION` means engineering readiness, **not** proven survival of retail save loading.

## Stage B operating plan and authorization boundary

Keep the **primary** scientific action unchanged: one normal operator-selected Save2 load, performed only after post-title attachment, verified four-site arming and durable `LOAD_BEGIN`. Observe through player-control return and a useful post-load interval. The Lodge crossing remains an **optional, low-cost conditional contrast**, not a requirement and not justification for changing the observer substantially. All GUI actions belong to the maintainer.

Produce a short proposed run card tied to the frozen candidate. It should retain the SRR-010 operational safeguards and explicitly distinguish:

1. Scientific readiness and `ATTACH_ARMED` from game/menu readiness.
2. Durable `LOAD_BEGIN` from the player's actual Save2 selection.
3. The load window from post-load activity and the optional Lodge transition.
4. Scientific STOP from natural/abnormal game exit and observer shutdown.
5. Observer-only administrative closure after independently verified **exact target exit** from any control over a live attached game.

**No additional live Starfield launch, load, Lodge crossing, retail debugger attachment or game operation is authorized by this continuation.** The prior Stage B authorization was consumed. A proposed second attempt requires a separate written approval specifying exact manifest and binary identities, allowed actions and recovery terms.

## Durable deliverables and acceptance criteria

Keep **one principal SRR-010 dossier**, with a results-first presentation. Do not turn it into an instrumentation diary. Preserve the earlier authorized Stage B outcome and its limitation; append a concise recovery rationale, evidence and changed method. Retain detailed exploratory traces and reviewer rounds under ignored local evidence; update tracked registers or workflow documents only where a substantive reusable finding genuinely warrants it. Do not commit, push, tag, release or move private evidence into Git.

An independent reviewer must assess these eight criteria:

1. **Preservation:** existing SRR-009/010 scientific results, manifests, protected saves and backups, Ghidra state and initial worktree baseline unchanged outside explicitly reviewed task files.
2. **Prior art:** specific demonstrated successes/failures and operating contexts compared at source and live-evidence level; limitations and unavailable primary material clearly labeled.
3. **Pragmatic selection:** a concrete credible recovery route is selected for implementation; definitive crash attribution is not required and unsupported claims are rejected.
4. **Scientific invariants:** four-site observation, causal links, cross-phase qualifications, actual exceptional outcomes, and durable evidence remain trustworthy after the adaptation.
5. **Operational safety:** retained Steam/retail identity, non-killing debugger policy, protected-save constraints, truthful retirement and limited post-exit administrative closure; no new unauthorized target operations.
6. **Qualification:** focused adverse tests and proportionate regressions passed; retained failures, environment differences and transfer limits reported accurately.
7. **Reproducibility/custody:** tracked reusable source and declared lawful inputs, exact build and dependency pins, private evidence custody, free-space and publication requirements met; original records remain distinguishable.
8. **Independent handoff:** challenger verdict, SHA-256 substantive manifest, pinned candidate executable, task-only Git-native patch, isolated byte-exact replay, starting/ending Git HEAD/index/status and an actionable proposed Stage B authorization supplied.

**Success:** `READY FOR STAGE B RE-AUTHORIZATION` if an implemented, independently qualified candidate satisfies these criteria. If a credible fix demands a material architecture change or cannot be qualified offline, return a precise `BLOCKED`/decision proposal, not a speculative declaration of readiness. No requirement exists to identify the definitive cause of `0x80000004`.

**Final boundary:** Stop after the independently reviewed offline handoff, with all changes **unstaged, uncommitted and unpushed**. The maintainer will separately review and authorize any live experiment.
