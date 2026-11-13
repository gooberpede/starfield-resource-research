# SRR-005 — Retail allocator live-observation preparation

**Assignment type:** bounded, offline-first research and instrumentation preparation. **No live Starfield execution or deployment is authorized by this brief.**

## Controlling question

What observation method and controlled experiment can reliably distinguish execution of the SRR-003 `StarField::ModuleState` → PNDT callback → planetary allocator path in retail Starfield **1.16.244.0**, including events that might occur before a save finishes loading, while preserving the installation, analysis state, saves, and usable evidence?

**Required outcome:** a technically justified method selection, a qualified observation design and a reviewable, separately authorizable live run card. Where proportionate, implement and test *offline/disposable* tooling that makes the proposed method executable under a later authorization. Do not assert live coverage, successful capture, or deployment readiness from offline tests alone. This assignment prepares an experiment; it does **not** answer whether the path executes in retail gameplay.

## Starting evidence and required reading

Work in `starfield-resource-research`. Read its `AGENTS.md`, `docs/research-workflow.md`, `docs/PROVENANCE.md`, `docs/SRR-002-retail-static-reconnaissance.md`, `docs/SRR-003-retail-allocator-invocation-and-dispatch.md`, `docs/function-register.md`, `docs/structure-register.md`, `docs/glossary.md`, and this brief. Inspect the relevant code/evidence before choosing an observer. Capture starting HEAD, index, status, and exact task dependencies. Preserve all existing work; do not modify the sibling projects.

The currently pinned retail image is `Starfield.exe` 1.16.244.0, SHA-256 `7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28` (Steam build `23518663` observed locally). Establish actual file/Ghidra identity and RVA→loaded-VA assumptions independently for any proposed live method. **Do not borrow CK addresses or infer execution from static reachability.**

SRR-003 supplies *candidate* observation anchors, not compulsory sites: iterator indirect call **RVA `0x5932EF`**, callback vtable **preferred VA `0x144B3D9E8`** (image base `0x140000000`), relevant saved return RVAs **`0x94E57C` and `0x94EF5C`**, callback/adapter chain through `FUN_14077C470` and `FUN_140779610`, and downstream direct call **RVA `0x7796D2`** into planet-level orchestrator `FUN_140779760`. Verify instruction sites, receiver/slot conditions, return address meanings, module base, and thread context before proposing captures. The module-state pointer bypass, early-sweep flag, PNDT type `0xBA` filter, null forms, and nonempty biome work-list condition are possible reasons for a downstream event not occurring.

### Prior art — inspect selectively before inventing machinery

Read and compare relevant *maintainer-owned* methods and recorded results, without automatically copying or activating them:

- `starfield-reference-handles/docs/experiments/debugger-multithreaded-breakpoint-lifecycle.md` and `debugger/native/README.md` (software-breakpoint/detach failure evidence; hardware-breakpoint approaches and qualifications).
- `starfield-outpost-research/debugger/exp0002a/README.md` and focused hardware/debugger qualification records (multithread failure and capture limitations).
- `starfield-outpost-research/runtime/beacon-observer/README.md` and any directly relevant SFSE observer implementation/qualification (startup timing, retained evidence, observer-side effects and coverage).
- `starfield-outpost-research/docs/SAVE_PROTECTION.md` and the relevant early-save/source-identity records.

Record which existing components are usable as-is, adaptable, unsuitable, disabled, or only historical. Explain the decision based on the **SRR-003 dispatch target**, not general preference. These are all maintainer-owned assets: no new third-party reuse permission is required for project-authored content. Still record precise source paths/revisions, distinguish external dependencies, and do not inherit a sibling project's live authorization or its unresolved failures.

## Save candidate and identity qualification

The **preferred primary sample is Save2 / `HIST-0245`** from outpost research, with historical SHA-256:

`1ac3d496e532b6286d983a1449946ba4fe34a34e66295c9d1d7da677772903d1`

The outpost record `docs/experiments/save-capacity-and-planetary-location.md` links its saved player to WRLD `0001251B` (`NewAtlantis`) and identifies the near-Lodge-doors condition as **maintainer-reported**, not independently measured. `docs/experiments/historical-save-inventory-triage.md` classifies its bounded inventory as supporting **no active outposts**, not proving an entirely pristine state. Historical header version strings read `1.16.244.0 / 1.16.244.0`; these do not by themselves prove originating executable identity. The exact Save2 character/menu identity, tutorial progression, and present-day source-file availability must be checked, not assumed. Do not conflate Save2 with later Attila Kiraly Save25/Save39 or with Cao Tran Save52.

For preparation:

1. Locate the exact source or approved preserved copy *read-only* where accessible, validate SHA-256 and size, assess save-header/menu identity from existing lawful tools and records, and identify a usable selection procedure without relying on menu ordinal. If unavailable, record the narrow missing input and design a conditional operator check; do **not** fabricate a PASS.
2. Specify protected original, independently verified backup, working-copy strategy, save namespace and Steam Cloud safeguards. **Do not load, overwrite, copy into active Saves, delete, rename, restore, or alter the original under this brief.** A later live brief must explicitly authorize any such operations.
3. Evaluate whether a player outside the Lodge provides a suitable observable transition. A single load may not trigger the allocator if initialization already occurred or cached state persists; the plan must allow an inconclusive observation rather than turn it into a negative scientific result.
4. Retain **Save52 / `HIST-0267`** solely as a possible later comparison, not a required sample or alternative to use automatically. Its large mature outpost network and different lifecycle make it an inferior primary control for this question.

The operator should not be asked to recreate a save or repeat facts that can be checked from approved records. Any remaining user-only identity/menu confirmation belongs in the later run card.

## Method assessment and preparation

Evaluate at least the credible options for **pre-load/initialization observation** and **post-load observation**, including a hardware-breakpoint debugger path and an appropriately early SFSE/native observer path; evaluate software breakpoints as a known-risk comparator rather than a default. Other methods are welcome if justified. Compare:

- earliest achievable observation point relative to process launch, module-state construction, SFSE loading and Save2 load;
- all-thread versus selected-thread coverage, new-thread behavior, race windows, callback multiplicity, and false negatives;
- ability to identify the correct loaded image and callsite/receiver/form instance, and correlate ingress to downstream allocator arrival *within the same causal invocation*;
- intervention, pause/step, thread-control and target-exit hazards, including documented software breakpoint / detach failures; SFSE load/hook side effects and potential late attachment;
- observational footprint, finite capture boundaries, logging durability, partial failure reporting, stop/retirement, and recovery;
- exact dependencies, build/configuration needs, offline testability, and permission or operator gates.

Choose a **primary** approach and an explicit fallback or alternative. A reviewer must be able to see why each rejected option is inferior. Do not presume a successful debugger attach, a safe detach, an SFSE callback timing guarantee or reliable capture merely because previous projects produced useful results.

Design an observation record sufficient to distinguish **NOT_OBSERVED / INSTRUMENTATION_INCOMPLETE / STATICALLY_REACHABLE / OBSERVED_INVOKED / OBSERVED_REACHED_ALLOCATOR / TARGET_FAILED** as applicable, with unambiguous semantics. Include loaded module base and hash, relative and absolute site, process/thread IDs, process creation and observation epochs, receiver/vptr/slot evidence, form identity/type where safely obtainable, source callsite or saved return address, upstream flag and module-pointer state where safely obtainable, downstream call identity, instrumentation health and exact capture/flush status. Do not dereference speculative pointers or use unverified layouts merely to fill a report.

**Avoid arbitrary elapsed-time or evidence-size cutoffs used as a substitute for scientific completion.** Use finite, justified operations, bounded buffers and explicit STOP/capture boundaries to prevent runaway writing; if a deadline, sample quota or retention limit is essential for safety, justify it as an operational bound and distinguish it from the scientific question. Partial evidence must remain classifiable. The design should expose when observer setup may have missed early events.

**Offline work permitted:** inspect source and retained static evidence; author a bounded design, schemas, dry-run controls and a prospective run card; create or adapt tools in the resource repository when demonstrably necessary; compile and test on a disposable synthetic target or offline fixtures if safe and within scope; verify program-input identities without attaching to or launching Starfield. Explicitly distinguish any compiled prototype from a deployed/game-qualified observer. Do not mutate the existing Ghidra program or installed tool configuration. Avoid broad framework development and redundant reporting.

**Not authorized:** starting or loading Starfield, launching or attaching a debugger to it, arming any game breakpoint, loading SFSE plugins into the game, placing an observer DLL in the live plugin directory, memory reads/writes against the live game, modifying saves/game files/Steam Cloud, creating new saves, external uploads, commits, pushes or releases. The later live experiment requires a new brief and maintainer approval of the exact operational plan.

## Durable deliverables

Use **one principal dossier**: `docs/SRR-005-live-observation-preparation.md`, linked from `docs/README.md`. It should contain the controlling question and explicit preparation-only disposition; pinned inputs; Save2 qualification; a concise compared-method decision; target and observation schema; offline/disposable test results with negatives; readiness gates; unresolved risks; and a **specific next live run card** (an appendix/section within the dossier by default, or one separate file only if operator usability materially requires it). Identify which operations are later authorization requests, not approvals.

Update `docs/PROVENANCE.md`, function/structure registers, glossary or standing workflow **only where substantive new information warrants it**. Use existing conventions for a diagram or pseudocode only if they make the selected observer's data flow or timing substantially clearer. No new live scientific facts should be entered in `known-facts.md` from offline qualification. Keep compilation outputs, private installation identifiers, screenshots, raw native excerpts, save copies, manifests and detailed reviews in ignored `.local-work/codex/SRR-005/`, `.local-work/independent-review/SRR-005/` and `.local-work/diffs/` as appropriate. Publish neither proprietary payloads nor a mechanism for distributing or reconstructing them.

The live run card must state: exact build/tool/plugin/source pins and operator-selected save; before/after protection and backup checks; instrumentation setup relative to process startup; a baseline/control and target action(s); observable success/failure/inconclusive criteria; expected evidence and synchronization/flush; emergency stop; game crash handling; normal retirement/cleanup and Steam Cloud verification; and the smallest permissioned action needed to begin. Distinguish capture completeness, process survival and scientific completion. **Do not claim that the run card is approved or that the method is game-qualified.**

## Independent challenger and completion gate

Use **one independent reviewer sub-agent at a time**, separately from the implementing agent. Supply the original brief, exact starting state, method candidates and prior-art sources, protected-input receipts, save qualification, all proposed artifacts, offline test evidence and actual patch. The reviewer must actively challenge:

- whether the chosen method can be active **before** the relevant initialization event, and whether any negative observation would be interpretable;
- whether a claimed same-invocation downstream hit actually correlates process/thread/receiver/form rather than merely two nearby events;
- software/hardware breakpoint and SFSE risks, thread coverage, exception retirement and instrumentation-caused crashes;
- whether Save2 really matches the pinned file and documented location/character assumptions, and whether originals and backups are protected;
- whether a prototype or dry-run has been mislabeled game-ready, or scientific completion claimed from engineering preparation;
- whether the final run card names every necessary future permission and preserves the pinned runtime/static evidence boundaries.

For **REWORK**, Codex corrects remediable gaps under the *same* assignment and resubmits to a fresh independent challenge pass. **COMPLETE** means preparation criteria pass; it never means live dispatch was observed. **BLOCKED** requires a specific essential missing input/authority or exhausted permitted method, with attempted checks and minimum next action; stopping at the first difficult tool or absent source is not automatically BLOCKED. Preserve scientific objections in the dossier; detailed review rounds remain local. Record final disposition and SHA-256 reviewed manifest without replacing SRR-001–004 review identities.

## Acceptance criteria

| ID | Mandatory result |
| --- | --- |
| **AC1 — Scope and baseline** | Starting/ending Git state and task-scoped protected hashes are recorded. Starfield executable and static-address domain are pinned; no game, save, Ghidra project or sibling project is modified or launched; protected inputs are rechecked. |
| **AC2 — Save qualification** | Save2/HIST-0245 evidence is checked against existing records and, where available, actual bytes; exact unknowns are preserved. Backup, active-save and cloud precautions are concrete. Save52 remains optional only. |
| **AC3 — Prior art and method decision** | Relevant prior-art successes and failures have been critically assessed. At least one primary method and a reasoned fallback/alternative are selected against startup timing, thread coverage, safety, and evidence needs. |
| **AC4 — Observation design** | Exact target anchors and qualifications, observable record/schema, causal correlation, coverage gaps, failure states and bounded capture/retirement are specified. Negative observation is not mistaken for absence. |
| **AC5 — Preparation tests and authorization boundary** | Available offline/disposable controls are executed or a specific tested prerequisite is documented; outputs/results/limits are recorded. A separately authorizable run card is complete. No game execution, instrumentation deployment or save manipulation occurs. |
| **AC6 — Documentation and handoff** | One indexed dossier plus necessary minimal updates; valid UTF-8/links; no publication-unsafe material; both C: and D: projected available space stay at least **40,000,000,000 bytes** during material writes; a Git-native task-only patch independently checks and replays byte-for-byte. |
| **AC7 — Independent scientific and engineering challenge** | A separate challenger verifies the original criteria against primary evidence, tests counterexamples and readiness claims, requires REWORK for material gaps, and verifies final review block, deterministic manifest and patch. |

Return: disposition; selected method and explicit rationale; Save2 identification and unresolved qualifiers; offline test results; dossier/run-card path; task patch; local independent-review and verification receipt locations; and the precise scope of authorization sought next. Do not stage, commit or push.

## Non-goals

Do not establish observed retail invocation, cache lifecycle, planetary resource membership, descendant multiplicity, or CK–retail dynamic equivalence in SRR-005. Do not retrofit or repair disabled sibling live tooling, reorganize evidence archives, mass-hash unrelated `.local-work/`, or make a public release. The later experiment may change methods if its own approved evidence and safety analysis justify doing so.
