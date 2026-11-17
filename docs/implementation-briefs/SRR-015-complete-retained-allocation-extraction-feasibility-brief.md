# SRR-015 — Complete Retained Allocation Extraction and Oracle Comparison
## Offline feasibility, native-reuse assessment, and experiment design

**Recipient:** Codex, `starfield-resource-research`  
**Disposition:** IMPLEMENTATION BRIEF — OFFLINE INVESTIGATION ONLY  
**Target:** Pinned retail `Starfield.exe` 1.16.244.0; retain the existing executable and source identity requirements from the repository  
**Git:** No staging, committing, pushing, or publishing without maintainer review

## 1. Scientific question

Determine whether we can obtain a **qualified, population-wide extraction** of retained `BSGalaxy::CTPerBiomeData` inorganic-resource allocations from a live retail process and compare it with an **independently generated, grain-compatible reproducer reference**, initially at the responsive title card. Design the extraction and comparison before requesting any live test.

The scientific goal is to establish, at a named checkpoint and process epoch:

1. **Coverage:** Which expected planet/biome allocation-bearing components exist in the inspected database?
2. **Values:** Which of the seven retained resource-ID fields are present, zero, or different from independent predictions?
3. **Completeness:** Does the qualified extracted population agree with the applicable oracle, and what is the precise scope of any such agreement?

A complete qualifying title-card match would establish completeness **of the modeled and enumerated population in the inspected store at that checkpoint**. It would **not by itself** establish the generating invocation, all planet types, strict effective-input attestation, persistent/atomic lifetime, or save-file serialization.

This work is motivated by understanding the game. **Do not justify it using prospective mods, planner requirements, or hypothetical products.**

## 2. Established starting evidence — reuse, do not rediscover

Read and reconcile the current committed material, at minimum:

- `docs/v1-research-baseline.md`, `docs/known-facts.md`, `docs/hypotheses.md`, `docs/PROVENANCE.md`.
- SRR-011 result storage, native readers, and invalidation paths; SRR-012 embedded context, mixed-index topology, typed edge identification, and sample plan.
- SRR-013 inspector, structural qualification, budget recovery, paired retail title-card observation, and their independently reviewed disposable counterexamples.
- SRR-014 startup ordering, native operation catalogue, and lead register (especially A9 and B8).
- Maintained sibling repository `gooberpede/starfield-resource-reproducer`, its production inputs, manifest, output formats, coverage model, and test evidence. Follow its current committed interface rather than assuming the former `planet-all-resources.csv` snapshot is a complete oracle.

Preserve the established distinction between the CK generation model and its independently verified retail output; between **planet-wide** agreement (1,444/1,444 canonical, 10/10 holdouts) and **per-biome seven-slot** agreement; and between a modeled prediction and an effective-input-attested retail fact.

## 3. Workstream A — complete native population extraction

Investigate how to enumerate the full, relevant `CTPerBiomeData` population using the verified published `BSComponentDB2::DB`, the context `+0x300` mixed index, native key/range conventions, registered type discriminator, independent FormID map, and resource/biome type checks. The four SRR-013 samples become regression controls, **not** the acquisition boundary.

**Prefer reuse of native game machinery where it materially helps.** Identify the native iterator, typed lookup, copy, range traversal, identity and guard operations already recovered. For each, distinguish:

- What it supplies as a **static specification** for an external reader;
- What can be reused in offline tests or reconstructed from known layouts;
- What would require **executing code inside the retail process**, acquiring native synchronization, injecting code, or attaching a debugger—and is therefore **not authorized** in this phase.

Do not casually replace the successful external read-only inspector with a new in-process integration. An external process cannot simply invoke native game methods safely; explain the trust, lifecycle and authorization boundary. Evaluate native enumeration/typed-copy semantics against direct external traversal, including the risk that live copy functions are not callable from outside the process.

Define an extraction model with:

- Full index-range coverage, root/leaf/end-fence and mixed-entry checks; duplicate/alias/owner/type detection; identity and native FormID validation; handling of absent, malformed and zero-field records.
- Explicit planet and biome key association and a **defined expected population universe**. Do not equate `+0x300` mixed index size, number of planetary bodies, number of PNDT biomes, and eligible allocation-bearing components without proof.
- Raw retained seven-word vectors in native slot order, plus independently resolved FormIDs and source-identification metadata. Preserve originals separately from normalized export.
- A practical export specification (e.g., JSONL plus manifest, or a reasoned alternative) with deterministic ordering, schema version, source provenance, checkpoint/process identity, coverage counts, refusals, and digests. Keep sensitive runtime addresses and process identifiers in private evidence; define a sanitized comparison output.
- Paired or otherwise justified consistency observations with independently rooted traversals and bounded structural work. Distinguish complete traversal from an atomic snapshot: agreement cannot exclude intervening ABA, stable intermediate zero states or concurrent mutation. Do **not** impose arbitrary five-/eight-second deadlines; derive acquisition limits from population and actual read work, with cooperative cancellation.

Show precisely how a traversal could establish that **no relevant record was skipped** under the admitted structural evidence, and state what it cannot prove under concurrent mutation. Specify deterministic fixture-driven tests for multi-planet/multi-biome ranges, mixed entries, duplicate keys, alias collisions, split/repack, insertion/removal during acquisition, zeroes, unmatched owners and malformed coverage. Reuse the existing SRR-013 fixtures and adapters where feasible.

## 4. Workstream B — independent reproducer oracle and comparison

Inspect the sibling reproducer's **current** public interfaces, internal biome-level representation, data provenance and tests. Determine whether it can already produce deterministic one-row-per-planet/biome **seven-slot** expectations, or whether it supplies occurrence/family provenance that must be mapped carefully into the native seven-slot format. Establish the mapping in detail; do not invent equivalences between planet-wide membership and biome-local fields.

Specify a reproducible, independent comparison that **does not derive expected values from the retail dump**. Classify at least:

- expected and observed component with exact seven-slot agreement;
- expected component absent from an otherwise qualified complete extraction;
- present component with seven zero slots;
- present component with valid nonzero fields but differing slot values;
- unexpected observed component or duplicate identity;
- unsupported/unresolved prediction or input-provenance mismatch;
- incomplete/invalid extraction (separate from genuine missing components).

Indicate required inputs and provenance (winning base-game records, overrides/mods, load order, source corpus, runtime FormID mapping, and inclusion/exclusion rules). **Structural identity**, **conditional reproducer match**, and **strict effective-input attestation** are different verdicts. Define explicit scopes for any `COMPLETE_MATCH`, `PARTIAL_MATCH`, or `INDETERMINATE` label, avoiding a universal completeness claim from an incomplete oracle.

Assess the minimum viable oracle-export extension if required. Propose it with tests and example rows, but **do not modify the sibling repository** without separate authorization. If a non-retail, disposable adapter/prototype materially settles feasibility, it may be developed within the allowed research-repository task scope, with independent tests and evidence, not as production-ready live tooling.

## 5. Native capability-and-usage tracing — evidence-grounded only

Maintain a concise **capability-and-caller register** for native methods pertinent to extractor validity and interpretation: index iteration, keyed lookup, typed copy, insertion, clear, removal, reset, notification, and possible result transfer. For a relevant operation, attempt to identify:

1. Native effect and target structure;
2. Direct upstream callers, including identifiable virtual/callback dispatch;
3. Upstream engine context and gating predicates;
4. Which source/destination records are actually involved;
5. Whether the evidence establishes callable capability, a possible execution route, or an observed invocation.

Trace actionable callers when the answer could change the extraction model, population eligibility or data-consistency interpretation. Record longer-term leads separately rather than expanding this task into a general database reverse engineering project.

**Hypothesis discipline:** Do not promote an unexcluded possibility to a competing explanation. Open a lead when native evidence, a real observation/discrepancy, or a material ambiguity supports it. Lead exhaustion applies to **credible, scoped evidence-grounded leads**, not every conceivable reset, mirror, serializer or alternate store. A bounded negative search is not proof of universal absence; document its exact search domain and indirect-call limitations. For SRR-014 B8, distinguish verified notification/copy operations from the unproven same-key mirror join.

## 6. Later checkpoints and separate save-state research

Design checkpoint comparison so that a later authorized title/main-menu/settled-save comparison could distinguish population coverage and values **without assuming** that differences demonstrate regeneration rather than changes in input/context/record identity. **Do not perform any such retail observation now.** Prior live authorizations are consumed.

Add a **deferred research item** (not a dependency or current workstream) covering **what saves actually contain**, how the game represents a planet's underlying resource allocations versus the player character's discovery/survey knowledge, the native callers/serializers that persist or restore such state, and how to distinguish serialization of allocation IDs from deterministic regeneration. Do not claim that either storage arrangement is known. No save reading, modifying, loading or copying is authorized by this brief.

## 7. Deliverables

Produce committed-path **drafts only** (unstaged) as appropriate to the repository's documentation layout:

1. **Feasibility verdict** — `FEASIBLE`, `FEASIBLE WITH NAMED PRECONDITIONS`, or `BLOCKED`, each tied to concrete native and oracle evidence.
2. **Native extraction design** — enumerated target universe, traversal/copy choices, qualified completeness rules, state-consistency limitations, work-derived acquisition budgets, schema and privacy boundary.
3. **Oracle mapping and comparison contract** — per-biome seven-slot mapping, inclusion rules, sample tuples, fixtures and falsifiable classifications, with independent oracle provenance.
4. **Capability/caller register** — functions, native locators, callers, scope of invocation evidence, and remaining actionable leads.
5. **Evidence-linked lead register** — resolved, exhausted, blocked (specific missing evidence), deferred, and unexamined/out-of-scope distinguished accurately.
6. **Future experiment proposal** — a **single**, separately authorizable title-card observation design only if feasibility is established. It must specify expected work, protective controls, stop criteria, evidence, comparison and independent review; **do not create or consume live authorization**.
7. **Independent challenger report and task-only diff** — assess native/production oracle correspondence, coverage proof, unsupported assumptions, false-positive completeness, privacy and source changes. Reproduce any offline tests from tracked commands.

Because this task reconstructs traversal and data mapping, **prose must be supplemented with source-linked pseudocode, diagrams and tabulated field/operation mappings where useful**. Diagrams must not imply unproven temporal or completeness joins. Include explicit counterexamples and at least one worked Kreet/Decaran sample crossing native fields to oracle fields; do not copy the retail observed tuple into the expected side as its source.

## 8. Work organization and non-negotiable boundaries

- **At most two concurrent sub-agents.** Suggested split: native extraction/completeness versus reproducer oracle/comparison. Parent reconciles shared key semantics, evidence and final scientific claims.
- Apply **lead exhaustion** to all relevant credible leads; every important lead must be resolved, specifically blocked, or explicitly deferred with a scope/evidence justification. No unexplained `BLOCKED` labels.
- Offline only. No retail launch/process access, debugger attachment, breakpoints, injections, memory writes, save operations, Ghidra database mutations, privilege escalation or changes to protective save directories.
- Read-only inspection of the existing pinned executable and tracked documents is permitted; controlled external-process fixtures and reproducible offline PE decoding are permitted under existing project practices.
- Preserve frozen SRR-013 sources, evidence and all historical dispositions. Do not silently upgrade SRR-013's structural result to strict exact-tuple qualification.
- Do not edit the reproducer repository, deploy a live extractor, run a title-card observation, stage, commit, push or publish.
- Finish with a summary of findings, exact changed paths, test commands/results, independent challenge, honest unresolved gaps, and proposed **next authorization boundary**. Stop for maintainer review.

## Success criterion

SRR-015 succeeds if it yields a **credible and testable design for complete retained allocation extraction and independent per-biome comparison**, or a specific, demonstrated reason why it cannot currently be qualified. It does **not** need to prove actual title-card completeness during this offline phase.
