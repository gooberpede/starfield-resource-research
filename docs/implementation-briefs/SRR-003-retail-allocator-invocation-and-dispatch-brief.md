# SRR-003 — Retail allocator invocation and dispatch

## Assignment and controlling question

Investigate the **upstream invocation mechanism** of the planetary/biome inorganic-resource allocator mapped by SRR-002 in the pinned retail `Starfield.exe`. Work in `starfield-resource-research`, using its existing research workflow and evidence classifications.

**Controlling question (Q1):** *What native invocation mechanisms and statically supportable demand conditions lead to the established planet-level resource allocator in the pinned retail executable?*

The requested outcome is a defensible account of how the allocator can be reached and under what code-level conditions, **not** a claim that ordinary gameplay has been observed exercising that path. Establishing actual execution frequency, cache lifetime, invalidation, persistence, or gameplay reachability is not required and must not be inferred from static code alone. Keep the inquiry at planet/biome allocation level, not landing-site deposits or raster geometry.

The SRR-002 dossier is the starting evidence, **not an instruction to assume its provisional upstream mapping is correct**. Preserve its settled static findings and test alternative readings. Maintain one principal `docs/SRR-003-retail-allocator-invocation-and-dispatch.md` dossier; update existing function, hypothesis, known-fact, provenance and navigation records only where warranted.

## Baselines, authority, and initial checks

1. Read the controlling brief, `AGENTS.md`, `docs/research-workflow.md`, `docs/PROVENANCE.md`, `docs/SRR-002-retail-static-reconnaissance.md`, the relevant function register, known facts/hypotheses, and the original CK static/live evidence necessary for comparison. Inspect relevant maintainer-owned tools and findings in `starfield-outpost-research` if a specific investigative need arises; reuse in place when practical, and do not copy or redesign them reflexively. The sibling reproducer is semantic reference material, not a native-code oracle.
2. Record starting HEAD, index/worktree status, pre-existing files/edits, toolchain and Ghidra project identity. Confirm that the **exact analyzed program and source executable** correspond to the SRR-001/SRR-002 retail pin: `Starfield.exe` **1.16.244.0**, SHA-256 `7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28`, preferred image base `0x140000000` (Steam build `23518663` is the observed installation record, not a substitute for the file hash). Treat CK addresses and historical retail output tests as separate evidence domains.
3. Default to the existing Ghidra project **read-only / no-analysis**, preserving its project/database content and associated protected primary inputs. Check relevant hashes before and after, with task-scoped dependency verification rather than a growing historical scratch inventory. If analysis state is absent, inconsistent or insufficient, report the precise gap; do not silently import, reanalyze, relabel, patch or modify the Ghidra database. New local scripts, if genuinely needed, must document their scope, inputs, outputs, limitations and read/write effects.
4. Preserve unrelated project and local files. Use `.local-work/codex/SRR-003/` for task receipts and scratch, `.local-work/independent-review/SRR-003/` for challenge rounds, and `.local-work/diffs/SRR-003.diff` for the task-only handoff. These are ignored working locations, not automatically indispensable evidence. Before material writes, enforce the existing **40,000,000,000-byte caller-available free-space floor on both C: and D:** after projected growth; recheck during sustained writes. Do not add a fixed `.local-work` size cap.

## Research direction — leads, not prescribed conclusions

SRR-002 established a statically supported planet-level orchestrator at `FUN_140779760` and per-biome allocator at `FUN_140777870`. It identified direct edges involving `FUN_140779610` and provisional upstream wrapper `FUN_14077C470`; the wrapper has data references at preferred VAs **`0x144B3D9F0`**, **`0x144B3D9F8`** and **`0x1485F1500`**. These are useful first leads, **not** established gameplay dispatch or an obligatory route to a positive result.

Investigate the ownership and semantics of these references and, as evidence warrants, trace the relevant caller, receiver, registration, indirect-call, dispatch-table, initialization, service-demand or other upstream relationships. Where a proposed chain depends on a virtual method or callback, establish the actual receiver/table and callsite linkage rather than matching address-shaped values alone. Consider false positives: pointer-to-function data may represent registration, metadata, bookkeeping, unreachable paths or a different invocation context. Verify decisive control-flow edges against native instructions, using independent PE decoding or other suitably independent checks where useful; distinguish direct calls, indirect calls, jumps, data references and inferred control-flow links.

Codex is **not restricted to these three references or a forwards/backwards search order**. Follow alternative leads if they offer greater information gain. If a caching or initialization condition is essential to explain why an invocation occurs, establish only the relevant predicate and dependencies; defer ownership across epochs, cache eviction/reuse, save/load, and full lifecycle behavior. Record bounded negative searches with exact predicates, scanned ranges, coverage, tool caps and partial-decode qualifications. An unproductive starting lead must not be treated as a negative answer to Q1.

For every proposed invocation route, report: caller or registration source, resolved target, receiver or input identity where supportable, guards/demand conditions and their exact code evidence, reachable alternatives, and the **strongest justified claim**. Separate:

- statically established potential or conditional invocation;
- an inferred association with a named game operation or consumer;
- **observed** ordinary gameplay invocation (out of scope and not proven here).

Do not assume that the existence of the core allocation machinery establishes its use by any particular UI, planet scan, outpost system or gameplay event.

## Research products and publication boundary

The principal dossier should contain the controlling question and result, pinned evidence identity, methods and limits, an inspectable upstream graph or compact edge table (mark inferred edges), demand-condition analysis, rejected hypotheses/negative controls, unresolved alternatives, and the next discriminating experiment. Explain exactly which parts of Q1 are answered and which would require live verification. If a genuine static barrier prevents Q1, retain the useful partial graph and an actionable, minimally scoped follow-up proposal without relabeling partial findings as completion.

Update `docs/function-register.md`, `docs/known-facts.md`, `docs/hypotheses.md`, `docs/PROVENANCE.md` and `docs/README.md` proportionately. Preserve historical CK records, v1 algorithm semantics and the reproducer unchanged. Raw PE excerpts, full disassemblies/decompilations, Ghidra databases, proprietary payloads and local captures remain unpublished. Publish only appropriate project-authored interpretations, bounded locators, methods and qualified claims; record each candidate claim's build, evidence and lawful public verification route or hold. Maintainer-owned sibling scripts need no third-party permission request, but tool origin and exact version/commit still matter for scientific reproducibility.

## Completion and independent challenger

Use the existing **one-active-sub-agent** rule. Before submitting COMPLETE, task Codex must send an independent challenger the **original Q1 and acceptance criteria**, starting state, exact changed files and patch, primary static evidence and negative controls, and any claims about exhaustiveness or gameplay association. The challenger must actively attempt to falsify the strongest invocation interpretation, test alternative ownership/receiver/dispatch explanations, check instructions against claimed edges, and assess whether Q1—not merely the first three leads—has been answered.

- **COMPLETE:** The original static-scope Q1 has a defensible positive answer satisfying every applicable acceptance criterion, with static demand conditions and qualifications made explicit; or a separately agreed bounded negative question is decisively answered. Finding that the three named data references are irrelevant is **not**, by itself, COMPLETE for Q1.
- **REWORK:** An answer is premature, a material authorized static lead or alternative remains unexamined, a key edge/predicate is unsupported, or a mandatory verification is missing. Codex continues within the same assignment and resubmits the corrected evidence; no fresh brief is necessary for ordinary rework.
- **BLOCKED:** A specifically evidenced essential barrier remains after reasonable authorized alternatives are pursued (for example, an essential live-only distinction or inaccessible qualified analysis input). Report attempted methods, retained partial findings, exact unmet criteria, and the smallest permission, input or follow-up necessary. An unfavorable result, limited time, or polished dossier alone does not constitute BLOCKED.

The reviewer writes detailed challenge rounds only under `.local-work/independent-review/SRR-003/`. The tracked dossier carries the final disposition, reviewer role, substantive snapshot identity (commit or deterministic SHA-256 manifest), important limitations and any material scientific objections. For an uncommitted dossier, exclude only its marked review-status block from its own manifest; have the challenger verify the populated block and final patch. Scientific corrections belong in durable research content, not solely in disposable review notes. Internal review does not amount to independent retail runtime replication.

## Acceptance criteria

| ID | Required demonstration |
| --- | --- |
| **AC1 — Scope and provenance** | Exact retail and analyzed-image identities are pinned; starting/ending Git and scoped protected-input checks are recorded; CK and retail evidence domains are not conflated; unrelated assets remain unchanged. |
| **AC2 — Investigative sufficiency** | The three SRR-002 reference leads are classified with evidence or a documented access limitation. The investigation pursues available alternative upstream static routes as warranted by Q1, rather than stopping at a convenient lead. Search coverage/caps/negative results are reproducible and correctly qualified. |
| **AC3 — Native path and conditions** | A proposed upstream dispatch chain has verified call/registration/receiver edges and explicit code-level triggering or demand predicates, with alternatives addressed. Where any essential link cannot be settled, label it clearly and do not claim an established chain. An unresolved Q1 must be returned as REWORK or evidenced BLOCKED, not COMPLETE. |
| **AC4 — Scientific discipline** | The dossier clearly separates observed static instructions, inferred mechanism, consumer association and unobserved gameplay execution. Cache/lifecycle, effective data resolution, descendant multiplicity and model equivalence are not silently declared resolved. The strongest claim survives a plausible counterexample test. |
| **AC5 — Durable and lawful report** | One coherent dossier plus only justified register/index updates; valid UTF-8 and links; traceable build-qualified evidence and reproducible verification route or hold; no proprietary payloads, speculative release claims or gratuitous supporting reports. |
| **AC6 — Operational handoff** | Task-scoped dependency hashes, Ghidra read-only/no-analysis preservation, both-drive free-space checks, ending Git/index status and a Git-native task-only `.diff` are recorded. Patch `--check`, isolated replay against starting Git objects and byte-exact comparison cover all deliverable files, including the completed review block. |
| **AC7 — Independent challenge** | A separate challenger tests Q1 and every criterion against original evidence and serious alternative explanations, issues COMPLETE/REWORK/BLOCKED appropriately, and verifies any corrections and the final reviewed snapshot; the dossier records the disposition while full rounds stay local. |

## Explicit non-goals and handoff

No game launch, runtime tracing, debugger attach, breakpoints, hooks, injected SFSE plugin, Ghidra state mutation, executable patching, installed-file edits, save access/modification, or new release/tag/publication. No exhaustive cache lifecycle, full algorithm equivalence, descendant candidate-multiplicity resolution, outpost geometry investigation, or changes to the sibling reproducer. No stage/commit/push unless separately instructed.

Return the dossier, changed-file inventory, patch path, local verification and independent-review paths, criterion-by-criterion disposition, strongest supported invocation result, remaining uncertainties, and the **specific next experiment**. If a live trace would be decisive, propose a bounded future test with target address/condition and observation needed, **without executing it**.
