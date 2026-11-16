# SRR-011 — Planetary Resource Allocation Execution and Result Lifecycle

**Implementation / research brief for Codex**  
**Authorization:** Offline investigation only. **Up to two concurrent sub-agents.** No live retail execution, changes to game files, Git staging, commits or pushes.  
**Scientific disposition on entry:** Execution timing, allocation-result ownership, reuse, and persistence are **unresolved**. SRR-010 is **CLOSED — INCONCLUSIVE; RESUMABLE**, not evidence against allocation during save loading.

## 1. Objective

Determine, as far as the available native and documentary evidence permits, **under what conditions Starfield invokes the known planetary/biome resource-allocation machinery, what representation it produces, where that result goes, and how the result is owned, consumed, reused, invalidated, disposed of, or persisted**. Identify the actual code-level relationships that could distinguish startup, save-load, on-demand/first-access, and repeated allocation. These paths may coexist. Do **not** force an exclusive choice or infer execution frequency from static reachability alone.

Treat **invocation lifecycle** and **result lifecycle** as coequal objectives. Investigate both *upstream* of the allocator (callers, registrations, dispatch, guards, request triggers) and *downstream* (out parameters, returned objects, writes, ownership, readers, retained state, cache-like lookup/miss paths, teardown, potential serialization). Follow whichever evidence-bearing direction is most productive; do not assume one direction must finish first.

An **inconclusive conclusion is allowed; an unexplained decision to stop pursuing plausible, actionable leads is not**. This is a research task, not a request to construct new runtime instrumentation.

## 2. Authoritative baseline and initial leads

Read the actual committed records before investigating; do not substitute this brief for their native predicates or exact evidence:

- `docs/SRR-003-retail-allocator-invocation-and-dispatch.md` — established static dispatch/registration findings and unresolved upstream chains.
- `docs/SRR-005-live-observation-preparation.md` — verified scientific sites, receiver, stack/frame and causal-join requirements.
- `docs/SRR-006-four-site-hardware-observer.md` — observer sensitivity and disposable controls, for context only.
- `docs/SRR-009-retail-debugger-admission-and-stage-a.md` — scoped post-title/menu non-observation; **not** startup coverage.
- `docs/SRR-010-stage-b-save-load-observation.md` — closed, incomplete Save2 tests, Control A/B contrast, resumption details and primary evidence scope.
- `docs/research-workflow.md` and relevant earlier SRR-001/002/004 records, including provenance and public/private evidence distinctions.

Known retail image: `Starfield.exe` **1.16.244.0**, SHA-256 `7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28`, preferred base `0x140000000`. Initial anchors include planet orchestrator `FUN_140779760` (RVA `0x779760`), per-biome allocator `FUN_140777870`, direct related edge `FUN_140779610`, and callback/wrapper `FUN_14077C470` (RVA `0x77C470`). SRR-003 identified possible function-pointer references near preferred VAs `0x144B3D9F0`, `0x144B3D9F8`, `0x1485F1500`. **These are starting leads, not proof of when the game executes them.** Reconfirm identities against native instructions and the recorded build; treat addresses from Creation Kit or other builds separately.

The known PNDT/BIOM/RSGD/RSCS input chain and independently validated reproducer identify **what the algorithm computes**, not necessarily **where the game stores its results or when it recomputes them**. Distinguish static planetary inputs, selected derived resource allocations, and presentation/world-generation data. Likewise, established early reference-handle initialization is not, by itself, evidence of early resource allocation.

## 3. Investigation requirements

### A. Incoming paths and trigger conditions

1. Enumerate and validate relevant **direct calls, indirect calls, virtual dispatch, callback registrations, table references, and construction/initialization links** that can reach the known allocator/orchestrator. Check code versus mere data references; resolve receiver identity, table provenance and guards whenever possible.
2. Trace evidence-bearing chains outward to meaningful ownership or demand boundaries: process/module state initialization, game/menu setup, save deserialization, planet record access, starmap/scan/landing access, cell/world loading, or other actual subsystem. These are **hypotheses**, not mandated destinations.
3. For each candidate route, establish the strongest defensible statement about **reachability, prerequisite state, conditional branches, frequency and trigger**. Separate *can be called* from *was observed called*. Do not infer initialization from a constructor-like symbol or on-demand behavior from a UI association without the relevant control-flow link.
4. Reuse and reconcile SRR-003's existing dispatch evidence. Where a lead contradicts previous interpretations, preserve both the original evidence and the new counterargument; do not silently rewrite history.

### B. Output representation, ownership and consumers

1. Identify the allocation result's **actual in-memory representation**, at the granularity supported by evidence: local buffers, out parameters, member fields, return values, heap objects, arrays/maps, planet/biome keys, etc. Confirm whether a candidate object holds computed allocations or merely PNDT/BIOM/RSGD/RSCS inputs.
2. Trace writes and handoffs from production to owning objects or consumers. Identify readers and request-side access patterns wherever plausible. Inspect relevant allocation, initialization, reference counting, copies/moves, teardown and lifetime boundaries.
3. Investigate cache-like structures **as causal mechanisms**, not names: keyed lookup; hit/miss branches; conditional generation; insertion/replacement; subsequent retrieval; invalidation/clearing; epoch/world/planet/biome scope; and possible save serialization/deserialization. Establish only relationships actually supported by instructions and data flow.
4. Distinguish **retained object**, **computed-result cache**, **precomputed content**, **load-time deserialization**, and **independent recalculation**. Absence of a found cache is not proof no cache exists. If a result representation cannot be pinned down, explicitly document competing candidates and what discriminates them.
5. Follow relevant consumers only as far as necessary to characterize whether and how they use allocation results. Do not expand into general terrain, outpost placement, full starmap rendering or whole-save reverse engineering without a separately justified decision.

### C. Lifecycle hypotheses and discriminating evidence

Assess, without assuming mutual exclusivity:

- Process/module/game startup generation.
- Save-load generation or restoration.
- On-demand, first-access or event-triggered generation (planet selection, scan, landing, area/surface load, or another supported trigger).
- Process-local or object-local retention/reuse, with potential miss-driven regeneration.
- Persistent/save-serialized or shipped/precomputed allocations.

For each: cite direct native evidence, counterexamples, missing links, supported scope, and what would discriminate it from alternatives. Treat **generated versus consumed** resource data as different operations. Static analysis can identify necessary conditions and call paths but generally cannot establish actual runtime frequency by itself.

## 4. Lead-exhaustion rule — mandatory

Maintain a **living lead register** throughout the investigation. Every plausible, relevant, actionable lead arising from caller tracing, result tracing, existing SRR records or cross-agent discoveries must have: stable ID; source/function/address; why it plausibly matters; proposed next examination; evidence and confidence; cross-references; owner; and a final disposition.

A lead may close only as:

- **RESOLVED:** followed far enough to establish a scoped lifecycle relationship or to discriminate the relevant possibilities, with reproducible evidence and remaining limits.
- **EXHAUSTED / DISPROVED:** specific attempted analyses, verified dead end, disproving evidence or documented irrelevance establish why further investigation of *this lead* is not warranted.
- **BLOCKED:** an actual impediment (missing data, irreducible indirect target, inadequate tool/source coverage, access restriction, etc.) prevents meaningful further progress. Identify the precise blocked step, attempted alternatives, evidence required to unblock it and likely remedy. **Difficulty, ambiguity after one look, or a promising initial conclusion do not constitute a block.**

**Do not return the final handoff while plausible in-scope leads remain actionable.** Finding a persuasive startup path does not justify leaving cache or on-demand leads untouched; discovering a result object does not justify abandoning invocation ancestry. No arbitrary function-count, call-depth, clock-time or token-budget stopping threshold. However, the scope does **not** require traversing every speculative engine call path: relevance must be justified by a concrete trace, data-flow relationship or credible prior evidence. If pursuing a lead would necessarily entail a materially different large subsystem, characterize its connection and propose a justified scope decision; do not call it exhausted merely because it is inconvenient.

The parent agent must perform a **final lead-disposition audit**: every lead is resolved, exhausted/disproved or specifically blocked; contradictions are reconciled or explicitly documented; no actionable in-scope lead remains outstanding. Independent review must challenge this audit, not just the final hypothesis table.

## 5. Parallel-agent arrangement

Authorize **at most two concurrently active Codex sub-agents**, coordinated by the parent agent; finished sub-agents may be replaced without exceeding the cap. Initial allocation:

- **Sub-agent A:** upstream callers, registration, dispatch, initialization and demand triggers.
- **Sub-agent B:** allocator outputs, object ownership, consumers, cache/reuse, lifetime and serialization leads.

This is a practical division, not an evidence boundary. Both agents must share native identities, provenance and new leads; the parent maintains a **single lead register and evidence matrix**, avoids duplicated long-running investigations and actively reconciles cross-chain results. Reassign agents as leads evolve. The parent remains accountable for the final scientific statements and the independent-review handoff. Agent count does not relax the stopping rule or justify speculative claims.

## 6. Method, safety and custody

- **Offline only.** Use existing committed source, retained reports, lawful matching retail executable as **read-only data**, existing Ghidra project as **read-only / no-analysis**, static disassembly/decompilation, and small disposable analysis scripts or tests as appropriate. Confirm the exact program/build and starting repository state before work.
- Do **not** launch or attach to retail Starfield; create hardware breakpoints; run an SFSE plugin; inject code; patch game/executable/save files; mutate the Ghidra project or its database; or authorize a live experiment. No runtime profiler against the actual game.
- If the Ghidra project is insufficient, record the specific gap and attempt non-mutating alternatives. Do not quietly reanalyze, relabel or save project state. Preserve original source and evidence, without copying private journals or proprietary executable bytes into tracked artifacts.
- Use ignored `.local-work/codex/SRR-011/` for primary scratch/receipts and `.local-work/independent-review/SRR-011/` for challenger records. Keep task-only patch at `.local-work/diffs/SRR-011.diff`. Observe existing free-space protection floor and identity/provenance rules; avoid unrelated file changes.
- No staging, commits, pushes, release or publication actions. Document relevant restrictions and external source dependencies. Do not introduce a new broad instrumentation framework or alter SRR-010's closed scientific disposition.

## 7. Deliverables

1. **Results-first SRR-011 research dossier** under `docs/` with a concise executive conclusion; exact applicability/build; known and unresolved lifecycle claims; a traceable **upstream/downstream call/data-flow map**; cache/result ownership analysis; hypothesis/evidence/counterexample matrix; and explicit epistemic limits.
2. **Durable lead register**, sufficient to audit each plausible in-scope avenue and its resolution/exhaustion/blocker. Use a readable Markdown table and, if warranted, a structured companion file for the larger register. Avoid burying the lead inventory solely in private scratch.
3. **Source-backed native evidence**, with exact function addresses/offsets, dispatch/receiver identities, branch or data-flow observations, instruction evidence, provenance and cross-references. Provide a compact diagram only where it clarifies actually verified relationships. For negative searches record the search universe, predicates and tool limits.
4. **Reproducible verification** for substantive evidence where practical: read-only scripts/checks, explicit inputs and expected outcomes, recorded results and counterexample tests. Do not needlessly reproduce established prior work. State which conclusions depend on existing Ghidra analysis or lawfully obtained executable bytes versus independently reconstructible tracked material.
5. **Next-investigation decision** with no more than **two** prioritized potential dynamic experiments, only if useful, stating for each the predicted discriminating observation, necessary instrument, limits, relative cost and what a quiet result could *not* prove. Recommendations are not live authorizations; a static result requiring no live follow-up is also acceptable.
6. **Independent challenger review** of native evidence, hypothesis distinctions, lead-exhaustion gate, contradictions, reproducibility, private-data separation, and complete task-only diff. Return a results-first review, final diff, identity/verification receipts and uncommitted handoff.

## 8. Acceptance criteria

- **AC1 — Baseline integrity:** Correct retail image and research provenance; SRR-010 closure and SRR-009 scoped result remain unchanged; read-only/ignored evidence boundaries respected.
- **AC2 — Invocation lifecycle:** All discovered plausible upstream routes receive validated edges and guards or a concrete exhausted/blocked disposition; no data reference masquerades as a proven execution path.
- **AC3 — Result lifecycle:** Output representation and ownership are pursued as first-class targets; writers, readers, reuse, disposal and possible persistence are investigated to evidence-supported limits, without confusing inputs with derived outputs.
- **AC4 — Hypothesis discipline:** Startup/save-load/on-demand/cache/persistence alternatives and coexistence are assessed with affirmative evidence, counterevidence, unresolved links and precise distinction between static reachability and actual execution.
- **AC5 — Lead exhaustion:** The final register is comprehensive for plausible in-scope discoveries, each disposition defensible, blockers actionable, and the parent/challenger audits find no omitted actionable lead.
- **AC6 — Two-agent coordination:** At most two concurrent sub-agents; cross-agent findings and contradictions integrated under one accountable parent report.
- **AC7 — Reproducibility and scope:** Important native assertions supported by reproducible evidence, negative searches bounded, no unauthorized live process work, no Ghidra mutation, and no proprietary/private artifacts in tracked diff.
- **AC8 — Review and delivery:** Independent challenger tests the strongest claims and unresolved-lead counterexamples, verifies source/diff and unchanged baseline, and reports any limitation; all changes remain unstaged/uncommitted/unpushed.

**Permitted final scientific disposition:** `SUPPORTED LIFECYCLE MODEL`, `PARTIALLY RESOLVED`, or `INCONCLUSIVE / BLOCKED` **only after** the mandatory lead-exhaustion audit. Do not label an inconclusive investigation complete because a promising path has been identified or because the analysis has become lengthy. If blocked, state exactly what would unblock further research.

**Handoff gate:** Deliver the independently challenged dossier, evidence, lead register, reproduction instructions, final task-only patch and recommendation for maintainer review. **No live retail test or Git commit is authorized by this brief.**
