# SRR-016 — Whole-Store Allocation Census and Oracle Comparison Implementation

**Implementation brief for Codex**  
**Authority:** offline implementation, disposable-process qualification, documentation, and independent challenge only. **No live retail Starfield launch/process acquisition, save access, debugger attachment, injection, elevated privileges, staging, commit, or push.**  
**Starting point:** committed and synchronized SRR-015 (`FEASIBLE WITH NAMED PRECONDITIONS`), and the existing SRR-012/013 acquisition and SRR-014 native-lifecycle evidence.  
**Concurrency:** at most **two concurrent sub-agents**, with parent-agent reconciliation and a separate independent challenge.  
**End state:** maintainer-reviewable implementation and evidence sufficient to decide whether to authorize **one** separately scoped retail title-card **structural census**. An exact population-wide match is **not** a prerequisite for authorizing a qualified structural observation.

## 1. Scientific purpose and evidence discipline

Implement a reproducible, external **read-only census of every structurally reachable allocation-bearing `CTPerBiomeData` edge** in the authenticated published `BSComponentDB2::DB` `+0x300` mixed index. Independently develop (a) an expected component/key ledger and (b) a qualified seven-slot native-write oracle based on the pinned sibling reproducer, then compare qualified observations to applicable expectations without confusing the three propositions:

1. **Observed-store coverage:** every descriptor reachable from the admitted root was visited and classified.
2. **Expected-population coverage:** independently supported component keys agree with the observed target-key set, within an expressly admitted input scope.
3. **Value agreement:** observed seven-slot values agree with a qualified retail-compatible oracle for that owner and input scope.

A conclusion about (1) must not be made conditional on (2) or (3); conversely, (1) does not establish (2) or (3). A complete rooted-tree traversal does **not** establish absence of pending commands, orphaned storage, data outside `+0x300`, or an atomic snapshot. Two agreeing observations do **not** prove uninterrupted state or absence of ABA.

**Lead discipline:** investigate evidence-grounded leads and the upstream callers/conditions of relevant native capabilities. Distinguish native capability, identified caller, admitted path, actual invocation, and observed effect. Exhaust actionable leads inside scope or give a precise, supported disposition. Do not manufacture alternate mechanisms merely because they cannot be logically ruled out. Deferred save-file survey/discovery-state research remains on the backlog, **not** a dependency or justification for this work. Do not cite hypothetical mods as motivation.

## 2. Evidence and frozen foundations

Before changes, inventory the repository HEAD/index/worktree, SRR-015 deliverables, and current sibling reproducer state. Preserve pre-existing unrelated work and the supplied brief. Record exact source identities, tool versions and input digests; do **not** silently update the executable, reproducer, game corpus or evidence baseline.

Read and honor, at minimum:

- `docs/SRR-015-retained-allocation-extraction-feasibility.md`, `docs/SRR-015-native-extraction.md`, `docs/SRR-015-oracle-comparison.md`, `docs/SRR-015-lead-register.md`;
- SRR-012 native acquisition/identity evidence and SRR-013 read-only inspector, structural qualification, budget recovery, and successful title-card observation;
- SRR-014 startup/database-operation catalogue and lead register, especially A9 and B8;
- the pinned sibling `starfield-resource-reproducer` production interface, tests, and maintained inputs.

The known pinned retail executable is `Starfield.exe` **1.16.244.0**, SHA-256 `7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28`. The SRR-015 sibling-reproducer reference is commit `a8ff1c788bca415f571f06769ab3e712fa674f75` (package 1.0.0); check applicability rather than assuming a local HEAD is identical. Preserve the established SRR-013 four title-card outcomes and sealed historical evidence unchanged.

The SRR-015 baseline reports **3,210 modeled biome rows across 1,444 bodies**, with **332 additional directory bodies without terrestrial predictions**. Those numbers describe the model's inputs, **not an automatically authoritative expected retail component census**.

## 3. Parallel workstreams and integration contract

Use up to two parallel sub-agents, one for each workstream; avoid simultaneous edits to shared files and fixtures. Parent owns reconciliation, cross-repository contracts, overall validation and the final handoff. Each workstream must produce independently inspectable outputs, meaningful negative tests, and a claim/evidence/limitation register.

### Workstream A — Native full-store census and paired acquisition

Build on the existing SRR-013 read-only process-memory adapter and native decoder, rather than introducing a new access technique. Reuse the native `+0x300` tree topology, descriptor geometry, ordered key semantics, registered type witnesses, edge wrappers, BIOM/PNDT identities, independent FormID mapping, source/epoch checks, and existing replay/qualification machinery.

**Traversal contract**

- Start from the authenticated published DB context and its mixed-index root; **do not** use a predeclared planet/biome list to limit traversal.
- Account for **every reachable mixed descriptor**, including non-target types, and reconcile traversal against the admitted tree's structural counts, root/leaf boundaries, ordering and native topology. Preserve mixed and target denominators separately.
- For candidate `PerBiomeData`, validate key words, registered discriminator, wrapper/vptr, ownership, target BIOM identity, typed input references when required, and every nonzero resource FormID through the independent native map. Preserve the exact seven raw u32 words and raw native key pair, including valid all-zero tuples.
- Detect/refuse: malformed nodes, holes/blocks, invalid separators/fences, unvisited ranges, cycles, duplicate identities, collisions/aliases, contradictory remaps, type mismatches, unreadable or changing memory, unresolved maps, partially traversed trees, and capacity/work exhaustion. Preserve diagnostic attempted-target rows in **private** evidence without silently accepting or skipping them.
- Independently reconstruct the normalized key set and sorted representation from raw traversal. A **structurally empty** tree can be admitted as empty after complete identity and paired checks; it cannot silently become a complete expected population.
- Keep **two independently rooted and bracketed collections**, the reviewed inter-collection separation, epoch/process/image/Steam admission, change detection, cooperative cancellation, and checked receipt/replay. Define a consistent pair verdict for whole-store structure and values, with exact reasons for refusal or mismatch; do not conflate this with a transactionally atomic view.
- No debugger, process writes, remote call execution, suspension, privilege change, game UI automation, or native in-process function invocation. Investigate/reuse **native semantics**, not native calls, where external read-only constraints prevent calling the game's implementation.

**Population-scale budgets:** derive finite read/byte/node/depth/chain/layout and output limits from independently generated **whole-tree** fixture envelopes, native layout constraints and measured request counts. Avoid arbitrary elapsed-time deadlines. Preserve finite work limits, target-identity validity, operator cancellation and fail-closed handling. If bounds are insufficient, report the bound and evidence rather than automatically retrying or raising the live limit. Fixture watchdogs are permitted solely for offline test safety.

**Deliverable:** deterministic, versioned export for all admitted target records plus separately retained mixed-census accounting, acquisition/identity brackets, failure ledger, and replay-readable manifest. Keep address-bearing/raw process data private; provide a sanitized, reproducible normalized export or report with clear provenance and hashes. Separate reader qualification from comparison decisions.

### Workstream B — Independent expected-key ledger, native-slot oracle, comparator

Develop offline prediction and comparison against the **independently sourced** data in the pinned sibling reproducer. Treat these as separate layers.

**Expected-component ledger**

- Enumerate and normalize candidate PNDT-owner/BIOM keys from authoritative winning inputs and the native component-production rules, including authored PPBD ordering, runtime/source FormID remapping, relevant ENAM removal/replacement, and admissible CSV paths if any.
- Categorize every scope as `EXPECTED`, `EXCLUDED` or `UNKNOWN` with source, reason, identities and coverage. Preserve the distinction between a body in the directory, a modelled generation row, an inserted component, and a component eligible for productive allocation.
- Explicitly characterize effective input/load-order uncertainty; do not silently declare canonical source inputs to be retail-effective. Permit **conditional** ledgers and scoped subsets, but never label them complete for the full retail database without provenance.

**Seven-slot native-write projection**

- Expose generation state needed to predict **actual native seven-slot stores**, not merely accepted occurrences or selected resources. Preserve the current validated production semantics and 1,444/1,444 canonical and 10/10 fresh-holdout scope.
- Address the **three known Special-selection-at-count-eight cases**: a modeled selection is not an admitted native store. Correctly gate the native Special output slot using the proven writer predicate and before-store shared count. Include explicit negative regressions.
- Review the SRR-015 documented retail/model differences, including Everywhere selection, shuffle/order, floating-point draw semantics, descendant candidate multiplicity, RSGD/BIOM override and input/remap applicability. Do not silently normalize unknown differences. Qualify **whole owners**, not just independently selected biome rows when earlier processing can alter shared state/RNG.
- Verify four SRR-012/013 Kreet/Decaran control tuples, including seven slot positions, under clearly declared conditional input assumptions. Do not upgrade their historical structural outcomes to strict exact-tuple verdicts.
- Keep oracle **frozen independently of any observed retail dump**. No fitting, retroactive expected-set adjustment, or reading captured values to construct oracle rows.

**Comparator**

- Consume versioned, normalized extraction and frozen oracle/ledger manifests; perform deterministic identity joins and field-by-field comparisons.
- Distinguish at minimum: `MATCH`, `MISSING_EXPECTED`, `UNEXPECTED_OBSERVED`, `SLOT_MISMATCH`, `OBSERVED_ALL_ZERO`, `DUPLICATE_IDENTITY`, `NO_APPLICABLE_PREDICTION`, `RETAIL_APPLICABILITY_UNRESOLVED`, `INPUT_PROVENANCE_MISMATCH`, and `ACQUISITION_INDETERMINATE`, with structural vs oracle/population decisions reported on **separate axes**. Differentiate zero slots within a legitimate tuple from a wholly zero tuple.
- Treat no-overlap, unknown universe, partial traversal, unqualified owner inputs, digest/version drift, or unresolved remap as **not** a population-wide complete match. Report transparent denominators (observed mixed, admitted targets, expected, excluded, unknown, comparable and mismatched).
- If changes to `starfield-resource-reproducer` are necessary, keep them narrow, preserve its CLI/output/schema by default, and provide a **separate reviewable patch** for that repository. Do not stage, commit or push either repository. Changes must retain all existing production tests and validations.

**Deliverable:** versioned ledger/oracle schemas, independent offline fixtures and an end-to-end comparator capable of explaining partial applicability without suppressing a qualified structural census.

## 4. Shared schema and integration checkpoints

Before significant parallel coding, agree a small **interchange contract** between agents: source/retail identities; raw and canonical PNDT/BIOM key pairs; exact slot byte/word order; typed FormID witness status; owner/biome scope; admission status; observed vs expected provenance; digest and schema versions; error/refusal categories; stability and comparison classifications. Set this contract in a tracked, reviewable artifact, then let workstreams advance independently. Keep normalized outputs deterministic and suitable for offline replay; timestamps/volatile evidence belong in separate provenance fields.

Parent must integrate both without forcing comparator success to govern native extractor correctness. **At the handoff, report independent readiness dispositions** for (i) whole-store acquisition, (ii) expected-population closure, (iii) native-slot oracle applicability, and (iv) combined comparison. Any unfinished layer remains expressly incomplete with its own next evidence requirement.

## 5. Mandatory disposable qualification and independent challenge

Build real **whole-tree fixtures**, not merely larger versions of SRR-013's four sample keys. Cover at least:

- Empty tree; packed single block; multi-block/multi-level trees; mixed non-target entries; many owners; multiple biome entries per owner; owned records spanning leaf/upper separators; legitimately unexpected owner; synthetic 3,210-row-scale and higher/denser shapes where practical.
- Independent fixture-builder descriptor truth and separately computed sorted reference identity; demonstrate all nodes/edges are visited once, counts and fences reconcile, and expected missing/extra/zero cases remain distinguishable.
- Duplicates across separators; same BIOM under different owners; raw-to-canonical key collisions; cyclic or malformed trees; mismatched types/vptrs; duplicate or aliased FormID tables; invalid or decoy FormID-chain entries; short reads and request-limit failures.
- Mid-traversal insert/delete, splits/repacking, slot rewrites with unchanged tree headers, address reuse, observed disagreement, ABA returning to original bytes, and stable intermediate cleared slots. Refuse detectable instability and explicitly document undetectable cases.
- Ledger unknown/excluded keys, conditional inputs, incomplete owner coverage, three Special-at-eight cases, mismatched raw slot order, zero-overlap, oracle input/version drift, one-field and many-field mismatches, and attempted oracle leakage from observations.
- Existing SRR-013 structural/budget regressions and historical journal replays **unchanged**, including the initial incomplete title attempt and successful paired title attempt. If private replay receipts are unavailable, state exactly which controls were not performed rather than asserting success.

Use independent implementations/fixtures to challenge the traversal completeness and oracle comparator. The independent reviewer must test **semantic correctness** of the code and the documents' diagrams, tables and pseudocode, and challenge positive *and* negative outcomes. Run tests serially where reusable fixture process names or native resources can collide; no parallel test overlap without isolation. Record commands, versions, identities, counts, passes/failures and scope of actual execution. Do not paper over failures with changed acceptance criteria.

## 6. Documentation and lead-exhaustion requirements

Maintain durable documentation of:

- full-tree traversal and identity algorithms, with native-anchored pseudocode and topology/ownership diagrams;
- schema and population coverage contract, with explicit assumptions and failure dispositions;
- the model-to-native-slot projection, especially ordering and write-admission predicates;
- native capability/caller matrix (capability → direct caller → upstream operation → guard → observed/not observed), and scoped dispositions of actionable leads;
- test matrix, reproducible offline instructions, independent challenge, and next-authorization prerequisites.

Use native evidence rather than invented names/guarantees. Do not reopen SRR-014 A9 or B8 without a concrete new caller or discrepancy material to this implementation; preserve them as scoped unresolved leads otherwise. Preserve the historical evidence and avoid asserting allocation timing, save persistence, queue quiescence, atomic snapshots or other-store absence from a successful `+0x300` census.

**Independent review custody:** `.local-work/independent-reviews/` (ignored/private), **not** a new committed `docs/*-independent-challenge.md`. Put only a concise review-status summary and appropriate evidence/custody references in tracked docs. Keep raw captures, private addresses, executable-derived private dumps, and temporary receipts under ignored `.local-work/` paths. Name the hashes of any separately furnished review/patch artifacts.

## 7. Authorization and stopping conditions

This brief **does not authorize the proposed title-card measurement**. It authorizes offline work on tracked project files, pinned authorized source datasets and **owned disposable test processes only**. No live game, no save handling, no Steam launch, no debugger development or live installation, no elevated access. The protected retail environment and 193 save pairs must not be accessed or modified in this phase.

Stop when: the agreed features are implemented and independently qualified, or a concrete, reported dependency blocks a layer after justified lead exhaustion. A qualified full-store reader may be accepted while the ledger or oracle remains conditional; do not extend scope indefinitely to force global completeness. **Do not automatically run more experiments or alter source after freezing review artifacts**; submit any material issue with evidence and a proposed follow-up.

## 8. Handoff and acceptance gates

Return:

1. An exact **task-only** patch (and a separately reviewable sibling reproducer patch if any), source/path inventory, HEAD/index/worktree status and SHA-256 identities; leave all changes **unstaged, uncommitted and unpushed**.
2. Durable technical dossier with executable pseudocode-equivalent explanation, native links, diagrams, population/slot schema, per-layer readiness and explicit blockers.
3. Fixture suites, test commands and counts, independent comparison outputs and unchanged SRR-013 replay results where available.
4. An independent challenge in `.local-work/independent-reviews/`, with findings and byte-for-byte forward/reverse patch replay; original brief must remain outside the task patch unless separately authorized.
5. A **proposed** one-session title-card structural census run card specifying exact tested source identity, checkpoint, collection/work bounds, ownership/custody, operator actions, preservation checks, scientific classifications and termination rules. Mark it **NOT AUTHORIZED** pending maintainer approval. Do not implicitly authorize additional checkpoints or oracle-dependent live reads.

**Minimum acceptance for structural-census readiness:** proven fixture-level root-to-fence coverage and no-skip census, all target identity checks, bounded cooperative paired read, independent replay, negative tests, and an independently reviewed run card. Population ledger and oracle may retain explicitly conditional statuses. **Strict population/oracle agreement is a separate milestone** and cannot be manufactured by constraining the observed inventory to the predicted one.
