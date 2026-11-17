# SRR-010 — Stage B Save-Load and Conditional Lodge-Transition Observation

**Implementation brief for Codex — Phase 1 only**  
**Disposition sought:** `READY FOR STAGE B APPROVAL`  
**Live authorization:** **WITHHELD.** This brief authorizes offline engineering, documentation, disposable-target qualification and independent review. It does **not** authorize launching or attaching to retail Starfield, loading a save, traversing the Lodge, or operating the live debugger. A short written authorization of the exact reviewed candidate, in the same Codex session, will be issued only after maintainer review. Stage B is a new investigation, not an extension of SRR-009's completed live authority.

## 1. Purpose and scientific contract

**Controlling question:** During a normal operator-selected load of the existing Save2/HIST-0245 game, and the immediately ensuing return to responsive gameplay, does retail Starfield execute the four-site PNDT/resource-allocation invocation path identified by SRR-003/005? Optionally, does one ordinary entrance into the Lodge produce an additional observation?

Use the **successful SRR-009 post-title attach and four-hardware-breakpoint observer** as the engineering baseline. Stage A produced qualified `NOT_OBSERVED` during two post-arm title/menu windows totaling **84.281 seconds**; it said nothing about startup or loading a save. Stage B deliberately places **the save-load action after verified attachment and arming**, so that the action of interest is inside a qualified observation window. Do not conflate post-load observations with startup coverage or assert that a phase marker proves an engine call was caused by a UI action.

Preserve the four approved Starfield.exe RVA assignments in DR0–DR3 order: `0x9518FD`, `0x5932EF`, `0x77C470`, `0x779760`, with the existing native predicate, provenance, thread, frame, correlation, instrumentation-health and evidence-sealing rules. A generic breakpoint hit is not automatically a focal invocation. Retain the distinct conclusions `OBSERVED_INVOKED`, `OBSERVED_REACHED_ALLOCATOR`, bounded qualified `NOT_OBSERVED`, and `INSTRUMENTATION_INCOMPLETE`; report invocation and allocator-arrival coverage independently. Positive evidence sealed before a later fault remains assessable. Do not add per-biome generation/output claims that the existing four sites cannot establish.

The **primary experiment is the Save2 load and arrival**. The **Lodge crossing is only a conditional, low-effort contrast**, not a separate mandatory objective. The primary experiment is complete without a Lodge crossing if the relevant window can be observed and sealed.

## 2. Read before implementation; baseline and custody

Consult the committed repository's `AGENTS.md`, `docs/research-workflow.md`, `docs/SRR-003-retail-allocator-invocation-and-dispatch.md`, `docs/SRR-005-live-observation-preparation.md`, `docs/SRR-006-four-site-hardware-observer.md`, `docs/SRR-007-retail-launch-and-stage-a-qualification.md`, `docs/SRR-008-retail-title-time-environment-survey.md`, and **results-first** `docs/SRR-009-retail-debugger-admission-and-stage-a.md`, together with the tracked `tools/srr006/` observer and `tools/srr008/` offline preflight helpers. Read the relevant Stage A primary evidence/receipts as needed from existing local custody, not as justification to repeat the experiment. Preserve the exact SRR-009 capture result, both earlier incomplete attempts, and the administrative observer closure.

Record starting HEAD, index, worktree, relevant source/toolchain and protected-input identities. Do not overwrite SRR-009 journals or local release assets. Use fresh, ignored task, fixture and independent-review directories (for example `.local-work/codex/SRR-010/`, `.local-work/independent-review/SRR-010/`, `.local-work/diffs/`). Observe the existing caller-available **40,000,000,000 bytes on each of C: and D:** floor, including the established 134,217,728-byte per-drive experimental reserve where applicable. Do not add arbitrary `.local-work/` size caps.

## 3. Save handling: deliberately simple and non-destructive

The maintainer will **load the same Save2 ordinarily selected in prior research, from the existing in-game load menu**. Leave the current Documents and Steam remote save directories populated and in place. **Do not introduce a new game-visible save namespace, rearrange saves, duplicate Save2 into the active load list, delete/rename saves, or develop an elaborate save-selection authenticator.** The privately retained Save2 copy is a protected reference/recovery asset, **not** a mandatory game-load input. Its established identity is **2,475,440 bytes**, SHA-256 `1ac3d496e532b6286d983a1449946ba4fe34a34e66295c9d1d7da677772903d1`.

Keep existing proportionate protection: use the newly tracked self-contained `tools/srr008/` methods and private configuration to verify the protected population and independent backups before/after, including the established 98 Documents and 95 Steam remote pairs, designations and unclassified entries, plus Cloud status and relevant settings. Check actual receipt fields, not process exit alone. Do not require saves to be absent, and do not manipulate original/backup specimens to manufacture isolation. Record incidental game-created/changed saves and autosave/exit-save behavior as observations; do not silently remove or restore files. Avoid unnecessary settings changes solely to suppress possible writes. Any material risk to protected data, identity, or restore capability is a real preflight blocker; mere existence of other saves is not.

A brief operator identification of the Save2 choice (e.g. character, level and visible location) suffices for phase annotation. The research claim is about **what the instrumented process did during the observed load**, not forensic proof that particular file bytes were consumed. If the UI shows an ambiguous selection or an unexpected save, record what was actually chosen and qualify the intended Save2-specific claim; do not silently substitute another save or claim identity beyond the available evidence. Never load a save during Phase 1.

## 4. Observation protocol and phase boundaries

Design the smallest extension of the already qualified SRR-009 marker/window mechanism. Keep one attached observer and one authenticated process epoch, with event coverage maintained continuously after arming. Suggested operator sequence for the eventual **separately approved** live session:

1. Start the same ordinary, non-elevated interactive-user Steam-launch procedure and existing read-only/protection preflight. Start observer and seal Steam baseline; one permitted Steam URI dispatch, subject to future authorization. Operator confirms responsive title card. Attach and pass unchanged process/image, ntdll, module-origin, thread, DR ownership, non-killing and debugger-break-in gates. Wait for the **durable verified `ATTACH_ARMED`** acknowledgment before further UI actions. Pre-arm time is explicitly uncovered.
2. Operator advances to main menu and confirms responsiveness. Record a menu-ready boundary so that time spent navigating menus can be distinguished from load activity; this need not produce a negative claim unless its coverage is qualified.
3. Operator prepares to select Save2; Codex emits/acknowledges **`LOAD_BEGIN` before the actual selection**. The operator selects and loads Save2 **once** using ordinary UI. Continue serving all debugger events and recording the four sites through loading screens and world initialization. Do not impose a deadline merely because loading takes longer than expected. Avoid a “Continue” shortcut that might bypass intended human selection if not the explicitly chosen action.
4. Once the character is controllable in the loaded world, the operator confirms **`PLAYER_CONTROL`**. This is a reported UI/experience boundary, not an engine completion signal. Continue observing during a sensible operator-selected post-load period; do **not** automatically STOP on first control or assume background work is finished.
5. **Optional only if practical:** if the character is already near the Lodge, the entrance is ordinarily usable, and the operator wishes to proceed, use `LODGE_BEGIN` before entering and `LODGE_END` after a responsive interior appears. One ordinary crossing, no travel/repositioning quest, reload, or extra save. If supporting these markers requires significant changes to the observer's scientific core, **drop the contrast from SRR-010** and state why; do not block the primary Save2 test.
6. At the operator-selected coherent stopping point, issue **STOP**, durably seal/verify the scientific prefix and classify each eligible window. Request retirement, obtain normal operator-controlled Quit and independently verify exact-process exit; run postflight and independent evidence review. Do not permit another game launch or reload automatically after a refusal, crash, negative or incomplete result.

**Windows:** Distinguish at minimum (a) menu/preload from (b) `LOAD_BEGIN → PLAYER_CONTROL` and (c) `PLAYER_CONTROL → STOP`; if the Lodge option is exercised, distinguish its pre-entry and transition/arrival interval. Permit valid causal joins across phase markers while preserving actual sequence order and thread/frame identity. A marker/phase cannot create a hit. If an expected marker cannot be durably bound, report the precise coverage limitation. Scientific evidence and observer health, target outcome, retirement and cleanup are separate verdicts.

Favor a **minimal marker-protocol change** over adding timer-based automatic phases, GUI automation, instrumentation sites or arbitrary native callbacks. No extra tracing should be required simply to prove which Save2 bytes were loaded. The observer must tolerate ordinary menu time, long loads and delayed worker activity, subject to genuine resource, identity and coverage failures.

## 5. Recovery and postflight: retain the workable policy

Keep the proven capture-first discipline and strict arming/continuation checks. Do not revive the older SRR-005 direct-startup debugger or empty-save-namespace approach. Normal target Quit and event-pump servicing remain preferred; **normal observer retirement is not a prerequisite for accepting a verified scientific STOP**.

The **Phase 2 authorization proposal** should explicitly include proportionate observer-only administrative closure **after** (1) independent evidence that the exact target process has exited, (2) reauthentication of observer PID **and creation epoch** and approved executable identity, and (3) preservation/verification of scientific STOP and available operational prefixes. It may terminate **only the verified orphaned observer**, recording the exit as administrative rather than normal debugger retirement. No observer killing while it still controls a live target, no forced game termination and no unapproved detach. A cleanup attempt must not rewrite scientific data. This simplifies the eventual postflight without prematurely authorizing a live process operation in Phase 1.

For any actual unsafe instrumentation, blocked I/O, failed continuation or process uncertainty, preserve valid evidence and escalate according to the existing research workflow. Do not treat an unexpected yet safely observable result as a reason to abort. No arbitrary elapsed-time/inactivity/hit-count cap for the scientific live window.

## 6. Phase 1 implementation and offline qualification

Implement **only** what Stage B requires on top of the committed SRR-009 baseline, principally additional operator phase markers and bounded per-window qualification. Reuse its retail process rights (`PROCESS_QUERY_INFORMATION | PROCESS_VM_READ | SYNCHRONIZE`), Steam drift policy, image/runtime pins, four DR0–DR3 sites, native event handling, refusal diagnostics, journal watermark, STOP, and non-killing policy. If changes are unnecessary for a planned optional contrast, don't make them.

Use disposable processes/fixtures only. Prove, with focused adversarial controls and existing relevant regression suites:

- a menu marker cannot preempt `ATTACH_ARMED`; `LOAD_BEGIN` cannot be accepted before verified arming/menu or without a proper prior marker; invalid/duplicate/wrong-epoch/out-of-order markers refuse without false coverage;
- continuous coverage through simulated long save-load intervals, thread births/exits, incidental module changes and delayed work; no event/count/time-based scientific cutoff;
- correct window boundaries and a positive allocator chain crossing a phase marker; a legitimate qualified zero; a gap invalidating only affected negatives while preserving earlier valid positive evidence;
- optional Lodge phase admission/omission and STOP behavior, without falsely making Lodge mandatory;
- journal write faults and refusal/STOP watermark correctness, including capture-first value after later crash or retirement failure;
- safeguards and unrelated observer behavior preserved, including competing debug-register ownership, Steam-module origin/drift and exact process identity.

Run enough of the existing observer fixture matrix to qualify any touched shared code; prefer relevant regression coverage over repeating broad unrelated tests by ritual. If core changes warrant the full suite, run it. Do not attach to a retail Starfield or Steam process, send game/UI controls, load Save2 or modify the actual save namespace as a qualification shortcut. Keep local test inputs synthetic or disposable.

## 7. Documentation and independent review

Create **one principal results-first** `docs/SRR-010-...md` dossier, link it from `docs/README.md`, and use existing glossary/structure registers only for materially reusable discoveries. Before Stage B, state the intended scientific contract, exact phase coverage, known SRR-009 limitations, local input custody and approved-versus-withheld authority. Do not narrate every engineering iteration before the results, and do not anticipate future Stage B observations as facts.

Where helpful, provide a concise run card with exact observer/marker commands, user/agent division of responsibility, contingency behavior, protected-save checks, evidence directory and normal/administrative retirement distinctions. Ensure clean-checkout build/test instructions require only tracked source and declared lawful inputs; keep private paths, actual saves, raw debugger journals, secrets and copyrighted game binaries out of Git and the final patch. Respect the existing GPL provenance and publication rules.

Engage an **independent challenger** with the original brief, prior-art contracts, actual candidate and raw offline test evidence. The challenger must attempt adverse tests of wrong-phase acceptance, fabricated quiet windows, token continuity across phase boundaries, unsafe observer termination and hidden local dependencies. If REWORK, correct and resubmit; do not treat self-review as the final gate. Preserve detailed reviews/receipts locally; put the disposition and reviewed manifest into the dossier.

## 8. Two-phase authorization gate, acceptance criteria and handoff

Phase 1 must end **before any live run**, at `READY FOR STAGE B APPROVAL`, with the exact source, binary, configuration, tested run card and independent review frozen. Leave all work unstaged, uncommitted and unpushed. Supply a task-only Git-native diff (including new files, excluding private material), a deterministic manifest, representative fixture receipts and the independent review. Verify byte-for-byte isolated patch replay. The maintainer will review that handoff and then, if satisfied, issue a **short Stage B authorization in the same Codex session** for exactly one live Steam launch and one Save2 load, with the optional Lodge transition as specifically approved. Do not construe the implementation brief as that authorization.

The challenger should assess these eight acceptance criteria independently:

1. **Scope and preservation:** committed SRR-009 scientific results, source and evidence are preserved; no game/save/live-debug actions in Phase 1; protected inputs and disk floors checked proportionately.
2. **Scientific continuity:** unchanged four-site predicate/causal-join contract; phase markers do not create causation or manufacture qualified zero; correct event/window boundaries.
3. **Primary load protocol:** one operator-selected normal Save2 load after verified arming, with a credible `LOAD_BEGIN → PLAYER_CONTROL → post-load STOP` window and no unnecessary file-forensic or namespace retooling.
4. **Optional contrast:** Lodge crossing, if implemented, is truly conditional and lightweight; its omission cannot fail the primary observation.
5. **Safety and cleanup:** original admission and non-killing safeguards preserved; evidence sealed independently of retirement; proposed exact-observer-only administrative closure strictly after independently verified target exit.
6. **Offline qualification:** focused adverse and relevant regression cases pass; retained evidence supports positive, negative, incomplete, failure and seal outcomes; no unreviewed live execution.
7. **Reproducibility and custody:** tracked source and lawful declared inputs suffice for offline qualification; private Save2/reference, originals/backups and raw captures stay out of Git; new dependency references and archive links resolve.
8. **Independent and final handoff:** separate challenger passes substantive snapshot; reviewed manifest and complete patch replay verified; final worktree/index and pre-existing changes reconciled; deliver exact Stage B run card and authorization proposal without committing.

**Explicitly out of scope:** startup-before-title instrumentation, SFSE deployment, software breakpoint substitution, loading additional saves, repeated load experiments, arbitrary travel, game automation, changes to Starfield or saves, forced termination of a live game, Stage C or follow-on hypotheses. Stage B's actual findings and any subsequent research direction remain for a separate postflight scientific review.
