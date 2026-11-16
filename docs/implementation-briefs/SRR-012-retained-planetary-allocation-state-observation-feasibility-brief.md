# SRR-012 — Retained Planetary Allocation State Observation Feasibility

**Type:** Codex research / feasibility implementation brief  
**Authorization:** Offline investigation and documentation only  
**Scientific status at entry:** SRR-011 partially resolved; SRR-010 closed — inconclusive, resumable  
**Concurrency:** Up to **two concurrent sub-agents**, coordinated by the parent agent  
**Commit authority:** None. Leave work unstaged, uncommitted and unpushed.

## 1. Purpose and scientific question

SRR-011 established a native route by which planetary resource allocation writes into retained, context-owned `BSGalaxy::CTPerBiomeData` payloads. It identified a keyed reader that can retrieve and copy a matching payload without generating on a miss, as well as relevant context and component lifecycle operations. It **did not** establish when ordinary retail execution populates the allocation fields. Four live SRR-010 Stage B Save2 loads ended before their required observation endpoint, so they neither demonstrated nor excluded allocation during Save2 loading.

SRR-012 shall determine **whether a reliable, minimally intrusive measurement can establish the presence or qualified absence of populated inorganic allocation results at defined game checkpoints**: (1) responsive title card, (2) responsive main menu, and (3) settled gameplay following an operator-selected Save2 load. This phase designs and qualifies the *measurement*, but **does not take those retail measurements**.

The aim is to narrow the execution interval using retained **result state**, rather than attempting to observe every allocator invocation. An identified, valid populated result is positive evidence that result state exists by that checkpoint. Given the recovered allocator writer and the absence of an established alternative producer, allocator execution earlier in that process is the leading explanation; distinguish that inference from direct observation of execution. Do not introduce unsupported alternative producers to dilute the inference. Conversely, neither an inaccessible context nor an ineligible/legitimately empty component is evidence of no allocation.

## 2. Authoritative inputs and reuse

Begin with the **committed** current repository state and record HEAD, relevant source/blob identities, image/build applicability, and the available preexisting Ghidra project identities. Prefer accepted research over rediscovery:

- `docs/SRR-011-planetary-allocation-execution-and-result-lifecycle.md`, `docs/SRR-011-lifecycle-lead-register.md`, updated structure/function registers and provenance: context-owned index at `+0x300`, indexed edge/payload arrangement, `CTPerBiomeData` fields, allocator writer, keyed copy-out reader and lifecycle limits. Read the exact native predicates and layout from the committed sources; **do not substitute illustrative pseudocode for a native field definition**.
- SRR-002/SRR-003 and the validated reproducer/dictionary evidence: legitimate resource selections, identity, eligibility, rarity and biome relationships; PNDT/BIOM/RSGD/RSCS input versus *derived output* distinction.
- SRR-005/SRR-006/SRR-009/SRR-010: process identity, data-read and evidence/custody safeguards, earlier scientific verdicts and documented live instrumentation interference. Treat historical Stage B run cards as **spent**, not permission to launch.
- Existing tool, Ghidra and native evidence already available. Use the matching lawfully held `Starfield.exe` image as **offline data**, if required, and identify its version/hash; do not assume a memory address remains stable across releases.

Any discrepancy with earlier layout, call path, key or output interpretation must be recorded and reconciled, not silently corrected. Maintain traceability to actual native addresses, disassembly/decompilation, saved evidence and function identities.

## 3. Mandatory investigation tracks

### A. Live-object discovery and identity (initial sub-agent A)

Find and verify a practical **read-only acquisition route** from an authenticated process and matching game image to the correct live owning context, its `+0x300` index, selected edge records and `CTPerBiomeData` payloads. Establish:

1. Pointer root(s), acquisition dependencies, ownership and how the relevant context is selected if multiple instances may exist.
2. Index structure, key construction and comparison, edge versus payload offsets, linked/inlined storage, count and traversal invariants, and how to avoid false positives or dangling/partial objects.
3. Which pointers/identifiers are reliable across title, menu and Save2 gameplay, and which are **per-process / per-context** and must be resolved afresh at each checkpoint.
4. What constitutes authoritative planet and BIOM identification (and optional RSGD where applicable), rather than recognizing a sequence of plausible FormIDs in arbitrary memory.
5. Feasibility of using ordinary query/read-only process rights without debugger attachment or hardware breakpoints. Account for ASLR, runtime mapping identity, allocation/teardown and concurrent mutation. Consider a simpler, better-grounded read-only route if evidence supports one.
6. How to detect an absent root, invalid root, multiple ambiguous roots, traversal failure and an internally inconsistent read **without reporting a scientific absence**.

Trace credible alternative ownership/index routes where the evidence warrants; do not assume the first pointer chain is unique or stable.

### B. Measurement validity and sample selection (initial sub-agent B)

Select a **small but discriminating set** of known eligible planet/biome components grounded in the accepted resource dictionary/reproducer and native evidence. Determine:

1. Which components are eligible for the relevant allocator writes; expected nonzero/zero/optional slot behaviour; whether the seven fields and their semantics differ across biome categories or special cases.
2. A minimal positive target with a well-established, nontrivial expected result, multiple eligible biome components when useful, and a contrasting identity/control to detect incorrect key or layout interpretation. Name actual planet/BIOM identities **only when confirmed from accepted inputs**.
3. How to validate the output slots against accepted allocation rules without assuming every eligible component must have seven nonzero IDs. Distinguish input/default values and intermediate cleared state from completed derived selections.
4. Which comparisons across title, menu and gameplay require stable logical identity rather than stable virtual address, and how to report object replacement, copied equal values and differing output.
5. How to qualify *absence* conservatively: a valid identified context, complete target index traversal, verified eligible sample coverage, structurally valid reads, known slot semantics and sufficient consistency. If the small sample cannot support a global negative, narrow the conclusion to the sampled components or propose the minimum additional coverage needed.
6. How a read-only multi-field/multi-node snapshot could race with native modification; specify proportionate read-retry/invariant or double-collection checks and explicit `INDETERMINATE` classification for inconsistent data. Do not assume `ReadProcessMemory` makes an atomic snapshot.

Track the expected confidence and inferential scope of each sample. Avoid selecting cases solely because they are easy to locate.

### Parent integration

The parent agent must reconcile the two tracks into **one verified measurement contract**: root and traversal, sample keys/eligibility, expected slot interpretation, consistency checks, output schema and evidence requirements. Investigate contradictions between the tracks rather than simply concatenating reports. Sub-agents may exchange leads or be reassigned; **no more than two may run concurrently**.

## 4. Required measurement contract

Define three mutually exclusive **state-measurement outcomes**, separate from SRR-010 execution-observation verdicts:

- **`POPULATED_RESULT_OBSERVED`** — authenticated target; verified owning context and matching eligible component; structurally valid, consistent read; populated output fields meeting explicit validity tests. State exactly which planet/BIOM keys, slots and checkpoint this covers.
- **`QUALIFIED_UNPOPULATED`** — the relevant context and selected eligible components were located and fully/consistently inspected, with absent/unpopulated derived results under a stated, validated eligibility and coverage contract. Scope the claim to the tested identities; do not extrapolate automatically to the whole galaxy or entire startup phase.
- **`STATE_INDETERMINATE`** — object/root missing or ambiguous, component ineligible, partial traversal, unknown slot semantics, inconsistent/unstable reads, unverifiable module identity or other coverage limitation. Report the exact reason.

Document any useful sub-states (context not present, component absent from an otherwise valid index, present/empty, present/partially populated, present/validated) without inflating them into separate scientific claims. A component not yet constructed is not equivalent to a validated, eligible component with unpopulated output slots.

Define an **identity-aligned comparison** across title → menu → settled Save2. A later populated result after a prior qualified absence narrows the interval in which the state appeared; it does **not**, by itself, prove the allocator ran in that interval rather than a known copy/reconstruction path. A populated title-card result supports the allocator-before-title inference under the currently established producer evidence. Equal resource values at two checkpoints do not establish identical object lifetime or cross-process persistence.

Specify the minimum output record fields (logical planet/biome identity; context and process epoch; acquisition/root provenance; component/edge identity; seven raw slots and decoded meaning; eligibility/validity outcomes; per-read consistency; checkpoint; outcome and qualifications). State which private identifiers and raw memory values are excluded from tracked/public deliverables.

## 5. Feasibility and acquisition design

Compare at least the preferred **external read-only process inspection, without debugger attachment** against any demonstrably simpler, non-mutating alternative discovered in research. Do not call into game functions, alter memory, suspend game threads, arm DR registers or require SFSE merely for convenience. If any mechanism would require such operations, describe the trade-off and **escalate for a separate decision**; it is not authorized here.

Produce a minimal design, not a general-purpose memory dumper: documented pointer resolution and index traversal, small selected sample, structural/identity checks, bounded retries, failed-read reporting, and private capture/audit evidence. Establish what can be verified in **disposable synthetic memory/structures** or using read-only offline fixtures; do not claim that synthetic success proves live retail access or stability.

Specify separately what the next two approvals would cover, *if justified*: (i) implementation and disposable qualification of a narrow inspector, and (ii) one authorized live checkpoint observation. Neither approval is granted by this brief.

## 6. Lead-exhaustion requirement

This is **lead-exhaustive within the defined feasibility question**, not a fixed function-count or time-boxed reconnaissance. Codex must maintain a durable lead register covering incoming roots, ownership paths, index/reader behaviour, sample eligibility, consistency and alternative non-mutating acquisition routes.

Every credible **actionable** lead within scope must reach one of:

1. **Resolved** — verified to a clear, bounded result with supporting evidence;
2. **Exhausted / excluded** — investigated with a defensible reason it no longer answers the measurement question;
3. **Blocked** — a precise obstruction is identified (missing source/data/authority/tool capability or a genuine ambiguity not resolvable with currently available offline evidence), with attempted work and the specific evidence/action required to unblock it.

Finding one feasible pointer chain or one positive sample is **not** sufficient to stop while other credible competing paths or coverage concerns remain. Difficulty, ambiguity at first inspection, or agent completion alone are not valid block reasons. Conversely, do not pursue speculative general engine branches lacking a credible connection to the measurement. Review and reconcile all lead dispositions before handoff. If feasibility fails, deliver an exact reasoned failure and viable alternatives rather than manufacturing a working design.

## 7. Scope and authorization boundaries

**Authorized:** read-only static analysis of existing source and lawful executable data; Ghidra inspection without database modification; analysis of retained research; disposable synthetic tests and offline validation scripts if proportionate; research documentation and independent review.

**Not authorized:** retail Starfield launch or attachment; reading a live retail process; debugger or hardware-breakpoint work; writes to game or save state; invasive OS hooks; modifying the Ghidra database; broad starmap/terrain/save-format reverse engineering; building or running a live retail memory inspector; publication, staging, committing or pushing.

Preserve the current SRR-011 and SRR-010 dispositions. No hypothetical serialization or alternative output producer should be promoted without concrete evidence. If an existing source materially contradicts the known writer, investigate and document it rather than disregarding it.

## 8. Deliverables

Provide tracked, durable and reviewable artifacts consistent with repository conventions:

1. **SRR-012 feasibility dossier** — results-first summary; explicit new versus inherited findings; verified object-discovery chain and memory layout; measurement interpretation; acquisition options and limitations; feasibility verdict (`READY FOR INSPECTOR IMPLEMENTATION DESIGN`, `FEASIBLE WITH CONDITIONS`, or `BLOCKED / NOT DEMONSTRATED`); recommended next gate.
2. **Measurement contract** — precise identity, eligibility, slot validation, checkpoint and consistency rules; outcome semantics; minimal evidence schema; pseudocode and small diagrams where they make the root-to-result relationship clearer.
3. **Lead register and evidence matrix** — native addresses, verified sources, counterexamples, provenance, lead statuses and specific blocks. Record evidence of **absence of capability** narrowly; a limited static search is not proof no alternative path exists.
4. **Minimal sample plan** — selected concrete identities and rationale, or an explicit blocked reason if selection cannot yet be made reliably.
5. **Reproduction instructions** — offline input identities, safe read-only checks, disposable verification steps and known limitations.
6. **Independent challenger review** — test scientific inference, sample validity, false-positive and false-negative risks, object ownership, acquisition feasibility, lead-exhaustion completeness, privacy and exact diff/custody. Incorporate any required corrections before final handoff.

Prefer links to existing accepted documents over duplicating large amounts of earlier disassembly. Use accurate conceptual pseudocode/diagrams when helpful, always with native evidence locators and no fabricated executable control flow.

## 9. Acceptance criteria

- **SRR12-AC1:** Historical contracts and project state preserved; no unsupported revision of SRR-010 or SRR-011 conclusions.
- **SRR12-AC2:** Credible root-to-context-to-index-to-component lookup is shown with exact native support, or the specific unresolved link is evidenced as blocked.
- **SRR12-AC3:** Candidate sample identities, allocation eligibility and slot semantics are evidence-grounded; no assumed seven-nonzero rule or pattern-only memory identification.
- **SRR12-AC4:** Positive, qualified-unpopulated and indeterminate outcomes are operationally distinguishable; negatives are properly scoped and failures cannot be misclassified as absence.
- **SRR12-AC5:** Read-only acquisition, concurrency/consistency, phase identity and context-lifetime limitations are honestly analyzed, with a minimal justified proposed method.
- **SRR12-AC6:** All credible in-scope actionable leads have resolved, excluded or specifically blocked dispositions; parent independently audits and reconciles the two sub-agent streams.
- **SRR12-AC7:** No retail operations, debugger modifications, Ghidra DB changes, unauthorized sensitive artifacts, staging, commits or pushes; durable sources and references intact.
- **SRR12-AC8:** Independent review challenges native and scientific claims; task-only patch applies and reverses byte-for-byte from the recorded baseline, all links and tracked changes verified.

## 10. Handoff

Return: summary of **genuinely new** SRR-012 findings; feasibility disposition; proposed minimum measurement and explicit limits; actionable/blocker register; dossier/contract/qualification artifacts; exact task-only diff and frozen hashes; independent review and replay receipts; unchanged HEAD/index and unstaged worktree inventory. Do not propose a live authorization as already granted.

**Stop at the reviewed offline handoff. No retail inspection, live test or commit is authorized.**
