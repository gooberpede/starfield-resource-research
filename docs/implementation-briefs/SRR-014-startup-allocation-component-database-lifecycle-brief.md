# SRR-014 — Startup Allocation and Component Database Lifecycle

**Codex research implementation brief · 17 November 2026**  
**Authority:** Offline native research and documentation only  
**Initial disposition:** OPEN — INVESTIGATION AUTHORIZED  
**Parallelism:** At most **two concurrent Codex sub-agents**, coordinated by the parent  
**Git:** Leave all changes unstaged, uncommitted and unpushed; return the task-only diff for maintainer review

## 1. Context and purpose

SRR-013 has now obtained **two agreeing, independently reviewed read-only collections** at the responsive retail Starfield title card, before any save was selected. Four retained `CTPerBiomeData` samples—three Kreet biomes and one Decaran VII-b control—were `STRUCTURALLY_POPULATED`; all seven-slot vectors matched the conditional SRR-012 predictions. This is **direct evidence of populated retained state at the title checkpoint**, not a direct trace of when the allocator ran. The original five-second-limited attempt remains historically `STATE_INDETERMINATE`.

SRR-011 statically connected startup and qualifying reset paths to the known allocation machinery and identified its in-place writes into context-owned `CTPerBiomeData` records. SRR-012 traced the process-global object, published `BSComponentDB2::DB` pointer, the `+0x300` mixed component index and native lookup/traversal. **Database construction, pointer publication, component creation, allocation-result population, and completion must not be treated as equivalent events.** The database may be published before all relevant records are created or populated, and clearing/repopulation may occur without the embedded context's address changing.

**Central SRR-014 question:** What is the best-supported ordering and control flow by which the startup machinery creates, publishes, populates, exposes, and eventually resets or disposes allocation-bearing component records, and what native database operations govern those records?

This investigation should identify **one or two narrow, credible observation boundaries** for possible *future* dynamic research, but must not presuppose that execution breakpoints, the existing SRR-010 observer, or any particular instrumentation technique are the answer.

## 2. Primary workstreams

### A. Startup construction, scheduling and result population

Reconstruct, using actual native control/data flow:

1. The relevant startup loader and module-state construction entry paths, guards, alternatives, ordering and return edges; reconcile with SRR-003 and SRR-011 instead of re-discovering them.
2. Creation and initialization of the process-global owner and embedded `BSComponentDB2::DB` context; the publication slot's zero/nonnull transitions; registration of `PerBiomeData`; creation of the `+0x268` and `+0x300` indexes.
3. Creation/insertion of `CTPerBiomeData` payloads from PPBD/PNDT/BIOM/RSGD paths and any actually supported CSV/replacement-input routes. Identify precisely which slots are initialized to zero and when.
4. Scheduling and admission of the planetary allocation sweep, collection of existing biome payload pointers, clearing/replacement of output slots, and subsequent readers/consumers. Distinguish entering a sweep, encountering an eligible planet/biome, and actually writing selected resource IDs.
5. Whether these operations are synchronous, callback-driven, queued, deferred, or conditional. Establish explicit happens-before relationships where proved, and mark other orderings unknown.
6. Any *verified* completion, readiness, publication, count, generation or reset condition that could act as an observation boundary. Do **not** label a generic database-initialized flag as allocation-complete without an actual data/control-flow join to the writes.
7. Reset/re-entry, module-guard clearing, load-order callback paths, clearing, reconstruction and disposal where they inform startup ordering or repeated allocation within a process. Do not infer ordinary Save2 execution from mere reset reachability.

### B. Native database operations and allocation-bearing component lifecycle

Investigate the methods relevant to these records, including shared mechanisms necessary to interpret their behaviour:

- **Identity/ownership:** process-global owner, context lifetime, registration/discriminator, planet/biome key, inline edge payload and borrowed pointers.
- **Lookup:** keyed search, miss behaviour, copy-out, FormID validation and independently identified consumers.
- **Creation/insertion:** initial payload construction, native command/edge insertion, duplicate/replacement behaviour and publication visibility.
- **Mutation/update:** in-place writes, copying, replacement, notifications/callbacks, any actual synchronization or consistency contract.
- **Enumeration:** range scans, iterators, ordering, extent/termination, interaction with concurrent changes and borrowed object lifetimes.
- **Removal/clear/reset:** targeted edge removal, context-wide clear, teardown, registration removal, pointer disposal and reinsertion/reconstruction.
- **Lifetime and access:** how callers retain or borrow references, what invalidates them, and whether any established native operation signals a batch or allocation completion.

Build a **database operation catalogue** with native function(s), identity/inputs, preconditions, side effects, consumers/callers, ownership implications, relevant startup phase and evidence. Explicitly distinguish a method's existence from demonstrated use on the investigated startup path.

The scope is **allocation-bearing components and the shared DB mechanisms required to explain them**. Do not reverse engineer the entire `BSComponentDB2` subsystem, unrelated game systems, general save formats, or the entire starmap.

## 3. Required starting evidence and reuse

Start with the committed project records and original native locators, especially:

- `docs/SRR-003-retail-allocator-invocation-and-dispatch.md` — known module-entry/allocator predicates and prior findings.
- `docs/SRR-011-planetary-allocation-execution-and-result-lifecycle.md` and `docs/SRR-011-lifecycle-lead-register.md` — startup/reset ancestry, output aliases, readers, teardown and open qualifications.
- `docs/SRR-012-acquisition-evidence.md`, `docs/SRR-012-measurement-contract.md`, `docs/SRR-012-sample-plan.md` — published context, registration, key/index mechanics, record layout, identity checks.
- `docs/SRR-013-retail-title-paired-structural-observation.md` and SRR-013 inspector documentation — qualified title-card findings and observation limitations.
- `docs/function-register.md`, `docs/structure-register.md`, `docs/known-facts.md`, `docs/hypotheses.md`, `docs/PROVENANCE.md`, `docs/research-workflow.md`.
- Relevant historical startup and menu-return evidence from `starfield-reference-handles` **only where pinned, available and independently attributable**.

Known retail build for applicability: **Starfield.exe 1.16.244.0**, SHA-256 `7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28`. Treat its bytes as lawfully obtained **offline input**, not a redistributable artifact. Reuse existing Ghidra analysis and static scripts where practical. Do not modify the Ghidra database; save additional independent static artifacts in local ignored custody as needed.

Illustrative **existing leads**, not conclusions or an exhaustive task list:

- Process-global getter `FUN_1423FF640`; object at preferred VA `0x1482EE300`.
- Construction at `0x1418993BE–0x1418993E3`, embedded context object `+0x2C0`, publication via owner `+0x8B0` (runtime main-image RVA `0x82EEBB0`).
- `BSComponentDB2::DB` context index `+0x300`, type registration and alternate `+0x268` store.
- Result collector around `0x14077BD2E–0x14077BE39`; allocator/orchestrator near `0x140779760`; established seven-word result fields `CTPerBiomeData +0x50..+0x68`.
- Authored component insertion/copy paths near `0x14076F360`, `0x140774E00`, `0x1407766B0`; keyed copy reader `FUN_140771F30` / copy near `0x14077200D`.
- Startup loader return and module-entry path, signed reset/file-replay path, index/context clearing and owner teardown detailed in SRR-011/012.

Validate function identities and semantics against the committed records before using any of these as a new claim. Distinguish absolute preferred VAs from RVAs.

## 4. Evidence and reasoning standards

1. **Re-use and novelty:** For each material claim mark `PRIOR ESTABLISHED`, `NEW STATIC FINDING`, `HISTORICAL RUNTIME OBSERVATION`, `STATIC INFERENCE`, or `OPEN/BLOCKED`. Do not repackage earlier SRR findings as discoveries.
2. **Concrete native grounding:** Include the module/build identity, function/callsite or memory field, actual instruction/decompilation evidence and causal relationship supporting each assertion. Record indirect or virtual dispatch qualification, guard predicates, type identity and address transformations when material.
3. **Ordering versus possibility:** A statically reachable call is not an observed execution. A published context is not proof of populated resources. A zero-initialization is not evidence of later allocation. A matching title-card tuple is direct state evidence but not a trace of the writing instruction or exact timestamp.
4. **Concurrency:** Establish synchronization, callbacks, queueing, pointer publication and data visibility only where native evidence permits. Do not infer atomic publication or continuous lifetime from a stable embedded address or from two agreeing snapshots.
5. **Negative evidence:** Bound all searched references, function sets, indirect-call candidates and type/consumer populations. Incomplete static call-graph discovery cannot justify global absence claims.
6. **Cache terminology:** Differentiate preallocated component records, retaining written resource slots, copied lookup results, conditional bypass of allocation, and cache invalidation. Prove any proposed skip-on-hit or completion mechanism; do not assume it exists.
7. **Competing explanations:** Test credible alternate ordering or paths actually supported by native data; avoid speculative mechanisms unsupported by the identified code. Record contradictions and unresolved dependencies.

## 5. Mandatory explanatory representations

**The dossier must communicate a usable mechanism, not just a collection of addresses.** Narrative claims about control flow, ownership or lifetime must be accompanied by suitable **source-linked pseudocode, diagrams and/or tables** wherever those representations make the mechanism clearer. At minimum deliver:

1. **Startup ordering diagram:** Construction, pointer publication, type registration, component insertion, allocation sweep/writes, readers and title-card observation as supported; show guards, loops, reset edges, deferred work and *unknown ordering* honestly. Do not draw a linear chain where native evidence shows only partial ordering.
2. **Guarded startup/reset pseudocode:** Include actual relevant predicates, possible early/later sweep branches, module-guard and reset transitions, and eligibility before writing slots. This is a conceptual transcription, never a fabricated literal source listing.
3. **Native database-operation table:** As specified in §2B, with direct locators and verified effects.
4. **Ownership and lifetime diagram:** Process-global owner, publication slot, embedded context, `+0x300` tree, typed inline edge/payload, collector borrowed pointers, writers/readers, and removal/teardown boundaries.
5. **Insertion/write/read/clear pseudocode or state-transition tables:** Show representative relevant operations, including their preconditions, failure/miss behaviour and where output slots change. Clarify which steps already had evidence before SRR-014.
6. **Observation-boundary comparison:** Rank at most two specific boundaries by causal relevance, startup accessibility, feasibility, interference risk, required instrumentation, and what a positive/negative result could actually establish. A proposed boundary must be backed by identified native events or state fields, not merely a plausible label.

Use Markdown tables and Mermaid or legible fenced monospaced diagrams. Retain underlying native notes/references and include the rendered or textual form in the dossier itself. Independent review must challenge the **semantic fidelity** of pseudocode and diagrams, not just syntax/rendering.

## 6. Lead exhaustion and parallel work

**Up to two concurrent sub-agents** are authorized. Suggested initial split:

- **Agent A:** startup path, construction/publication, scheduling, guards and completion candidates.
- **Agent B:** database operations, component insertion/update/lookup/clear, ownership and lifetime.

The parent owns integration, source identity, cross-agent synchronization, contradiction resolution, unified lead register and final evidence. Reassign work as needed; never exceed two concurrently active sub-agents. Preserve coherent findings when either sub-agent finishes.

**Mandatory lead-exhaustion rule:** Do not hand off while a plausible **actionable, in-scope** lead remains uninvestigated. Every lead must be classified as:

- `RESOLVED` — sufficiently characterized with supported conclusion and limits;
- `EXHAUSTED/EXCLUDED` — inspected and bounded, with evidence explaining irrelevance, lack of support or a dead end; or
- `BLOCKED` — concrete obstruction preventing the next relevant step, with attempted approaches, missing input/access/tool/capability and a proportionate route to unblock it.

Finding one credible startup boundary or an attractive database method does **not** end the investigation. Audit both workstreams and cross-links before claiming completion. Difficulty, ambiguity or additional static steps alone are not a valid block; conversely, speculative unrelated call-graph branches are not obligatory. A partial scientific conclusion is acceptable only when all credible in-scope actionable leads have dispositions.

Avoid arbitrary function-count, call-depth, wall-clock or research-duration quotas. Use actual technical constraints and proportional scope control instead.

## 7. Deliverables

Provide tracked, sanitized outputs consistent with the repository's documentation layout:

- **Primary SRR-014 technical dossier** with executive answer, novelty table, diagrams/pseudocode, full startup ordering, DB-operation catalogue, evidence links, qualified hypotheses and limitations.
- **Unified lead register** with disposition, evidence, attempts, cross-agent handoff and any precise block.
- **Source/register updates** to existing `function-register.md`, `structure-register.md`, `known-facts.md`, `hypotheses.md`, `PROVENANCE.md`, navigation/index only where the new evidence warrants them.
- **Native evidence and reproducibility notes**, distinguishing source committed to repo from private lawful binaries, local Ghidra assets and derived captures. A small offline helper may be added only if genuinely required; document and qualify it.
- **At most two ranked future observation opportunities**, each identifying exactly what it would measure, how it could fail scientifically, and whether existing read-only acquisition suffices. Neither proposal grants live authority.
- **Independent challenger review** of native claims, lead exhaustion, cross-agent reconciliation, pseudocode/diagram accuracy, source-to-claim provenance, scope/privacy, reproducibility and exact patch replay.
- **Final handoff** identifying changed files, scientific disposition, open questions, review and exact identities, followed by an unstaged, uncommitted, unpushed task-only `.diff` for maintainer assessment.

## 8. Acceptance criteria

- **AC1 — Prior work and title result:** Historical SRR-003/011/012/013 claims remain correctly scoped. The paired title-card state observation is preserved without upgrading it to a direct runtime allocator trace.
- **AC2 — Construction and publication:** Native evidence supports the owner/context creation, registration, publication and disposal ordering actually claimed; partial/ambiguous order is visible.
- **AC3 — Allocation startup path:** Relevant guards, per-planet eligibility, component insertion and allocation-write ordering are traced sufficiently to distinguish construction, sweep entry and productive writes; no static path is promoted into an observed runtime event.
- **AC4 — Database mechanics:** Relevant lookup, insert, modify, enumerate, remove, clear and ownership paths are examined and indexed with evidence and explicit demonstrated-versus-possible startup use.
- **AC5 — Completion and synchronization:** Proposed completion or scheduling markers are checked against native writes; unsupported flags or synchronization are rejected or visibly qualified.
- **AC6 — Lead exhaustion:** All credible actionable leads across both workstreams are resolved, boundedly excluded or precisely blocked; contradictory findings reconciled.
- **AC7 — Explanatory quality:** Required pseudocode, diagrams and tables faithfully communicate relevant native predicates, ownership, ordering, state transitions, unknowns and evidence locators; reviewed for semantics.
- **AC8 — Evidence, custody and replay:** Independent challenger substantiates the substantive claims against retained/native materials, verifies privacy/legal boundaries and exact patch replay, and confirms no unauthorized retail operations or Git mutations.

Return a disposition such as `STARTUP LIFECYCLE PARTIALLY RESOLVED — BOUNDED BLOCKS DOCUMENTED` if appropriate. Do not present unproven execution timing as established, or treat unresolved questions as implementation failures merely because static evidence has a limit.

## 9. Explicit exclusions and authorization boundary

**Authorized:** Offline inspection of lawfully obtained pinned binaries as data, previously analyzed Ghidra material in read-only form, committed research records, offline scripts/fixtures necessary to validate an actual static claim, and independent review.

**Not authorized:** Starting, attaching to, inspecting or modifying a live retail Starfield process; startup instrumentation; process-memory snapshots; debugger development; breakpoints; gameplay, scanning, travelling, Save2/Save52 operations or copies; modification of Ghidra databases; broad unrelated engine reverse engineering; publication; staging, commit or push.

No future observation design authorizes its execution. The parent must return for **separate written maintainer approval** of any live activity or materially expanded scope. Preserve the existing committed source and private historical evidence unchanged.
