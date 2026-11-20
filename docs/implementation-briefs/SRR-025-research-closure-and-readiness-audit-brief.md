# SRR-025 — Research Closure and Readiness Assessment

**Type:** Evidence and readiness audit (not a new reverse-engineering implementation)  
**Repository:** `D:\Projects\starfield-resource-research`  
**Decision owner:** Maintainer  
**Execution:** Offline, read-only except for approved documentation/audit receipts; no live game, debugger, SFSE observer, save modification, new data acquisition, or reproducer changes.

## Purpose and governing standard

Determine whether the inorganic resource-generation research programme is ready to become a **stable, reusable foundation for future work**, not whether every open lead has been eliminated.

**Agreed readiness definition:** The research is ready when its recovered mechanisms are sufficiently validated, reproducible and documented to support future work *within their stated scope*, without requiring the remaining historical runtime uncertainties to be resolved.

Test this definition rather than presume either closure or continuation. Distinguish **scientific confidence**, **reproduction/public verification route**, **applicable executable/data version**, and **operational readiness**. Closure of the active programme does not mean universal validity, proof of CK/retail instruction equivalence, deletion of open questions, or permanent retirement of the repository.

## Starting context and critical qualifications

Use the current authoritative subjects, not historical briefs as competing sources: `docs/v1-research-baseline.md`, `docs/allocation-validation.md`, `docs/retail-execution-lifecycle.md`, `docs/component-database.md`, `docs/PROVENANCE.md`, `docs/hypotheses.md` (the sole lead register), `docs/function-register.md`, `docs/structure-register.md`, `docs/research-workflow.md`, relevant tool READMEs and `THIRD_PARTY_NOTICES.md`. Verify current HEAD and working-tree status before work; preserve all pre-existing changes. Consult retained primary evidence and private custody records only as needed to audit a specific claim. Keep historical review snapshots distinguished from present content.

Known bounded results to test, not elevate by wording: recovered v1.0 CK generation mechanisms; 1,444/1,444 canonical planet memberships and 10/10 fresh holdouts; 3,211 native PNDT/BIOM component pairs across 1,445 bodies; 22,470 shared retail seven-slot diagnostic matches; **zero strict native-oracle admitted rows** because effective loaded inputs/ordered operations lack sufficient independent attestation. Retail pinned executable is Starfield 1.16.244.0. Survey/UI, PlayerKnowledge and save serialization have later evidence from SRR-019 through SRR-024, with precise historical execution timing still unresolved. Never infer a deposit's outpost-scale placement from a biome membership. Do not conflate native retained state, modeled expectations, serialized state, and historical gameplay displays.

## Required assessment

### A. Scientific claims and scope

Produce a concise **claim-level readiness matrix** covering at minimum:

1. Generation algorithm and input resolution (PNDT, BIOM, effective RSGD, IRES, atmosphere, RSCS/MT19937, ordered selection, fallback, cache and guard mechanics).
2. Canonical/holdout validation, retail component population and per-biome seven-slot agreement; explicitly report the strict-oracle admission boundary and its significance.
3. Retail database structures, allocation persistence/availability and startup lifecycle: distinguish static reachable paths from actual writer attribution and typed-command readiness.
4. PlayerKnowledge query/mutation, visited status, resource survey credit, three interface presentations, and Save2/Save52 serialization/comparison; distinguish decoded saves, predicted restored state and screenshot history.
5. Explicit **exclusions**: organics, terrain vein/deposit geometry, outpost-scale co-location and extractor placement, unsupported builds or arbitrary plugin load orders, and any other material unsupported application.

For each significant claim, give its **supported statement**, evidence type and identifier/locator, applicability, reproducible verification route, uncertainty and whether that uncertainty blocks the agreed readiness standard. Challenge overstatements and understatements alike; do not replace proven empirical agreement with an unjustified requirement for complete historical certainty.

### B. Entire current lead register

Inventory **every row currently in `docs/hypotheses.md`**, using the exact stable IDs and latest statuses, including `ORACLE-INPUTS`, `SRR014-A8`, `SRR014-A9`, `SRR011-U05b`, `SRR011-D07b`, `SRR014-B8`, `SRR011-U04`, `H1`, `SurveyAggregator` and `SURVEY-UI` if they remain present. Do not assume that this pre-brief list is exhaustive if HEAD differs.

Recommend one clear disposition per lead: **resolved/close**, **open but not a closure blocker**, **deferred pending a concrete trigger**, or **closure blocker requiring specific corrective work**. Supply a one-sentence rationale, minimum evidence needed to reopen, and whether a further **offline** investigation has a specific promising path. Distinguish the two startup leads, and keep the outstanding post-scan Kreet orbital-card case separate from Volii Alpha visit-bit timing under `SURVEY-UI` if necessary. Do not delete useful unresolved questions or create a second register. `H1` may be a compact future offline investigation, but its mere existence is not automatically a closure blocker.

### C. Reproducibility, stewardship and reuse

Audit, by checking actual methods and documentation rather than simply listing files:

- Tracked generation/reproduction, native inspection, screenshot custody and save-decoder workflows; sample at least one important end-to-end verification route from a clean-checkout perspective using declared lawful inputs. State what was **actually rerun**, what was only inspected and what requires private historical evidence.
- Version/build/plugin/load-order boundaries; source identity and hashes; distinction between CK live evidence, CK static evidence, retail static evidence, native title-card captures, historical screenshots and serialized saves.
- Custody and privacy of `.local-work/release-assets/` (including Save2, Save52, screenshot originals and earlier allocation captures), links from tracked documents to evidence identifiers, and non-redistribution of proprietary/private materials.
- Whether a downstream developer can understand and use supported resource-generation outputs without adopting the entire reverse-engineering toolchain. Flag only concrete usability obstacles, not speculative product features.
- Unsupported new dependencies, broken links, untracked prerequisites, stale instructions, and any relevant publication/third-party rights cautions.

The prior documentation consolidation was deliberate. **Do not undertake another broad rewrite**, add a new dossier, invent a release process, or convert private evidence into tracked payloads. Correct an identified material factual/documentation defect in its authoritative subject; otherwise report it as a recommendation.

### D. Closure decision and post-closure policy

Deliver a reasoned choice among:

1. **READY — close active research**, retain qualified leads and version boundaries;
2. **READY AFTER TARGETED CORRECTIONS**, identifying a finite, justified set of blockers;
3. **NOT READY — continue specific investigation**, specifying exactly which assertion/use case cannot yet be supported.

For every proposed blocker, show which readiness criterion it fails, its concrete downstream impact, the minimum safe corrective action, and whether it requires offline analysis or separately authorized runtime evidence. Do not treat absence of strict native-oracle admissions or a historical first-write witness as automatically blocking without demonstrating that they are required for the intended bounded use.

Include a concise **reopen policy**: reproducible falsification, relevant retail/CK or plugin version change, newly available primary evidence, or a concrete downstream requirement. Optional live observers for allocator startup (`SRR014-A8/A9`) and visit timing (`SURVEY-UI`) should be evaluated by what finding they would change, not by whether they are technically feasible. **No observer implementation or execution in this audit.**

## Work allocation and independent challenge

Allow **up to three concurrent sub-agents**, chosen by the integrator (not mandatory):

- **A — Scientific validity:** evidence hierarchy, model/validation claims, strict-oracle boundary and scope exclusions.
- **B — Native lifecycle and lead disposition:** startup, knowledge/visit behaviour, complete current lead register and observation necessity.
- **C — Reproducibility, custody and reuse:** toolchain, verification routes, evidence protection, build applicability and documentation usability.

The integrator reconciles contradictory assessments and produces a single decision. After integration, use a **separate independent challenger**, not one of A/B/C, with the original brief, source evidence, proposed audit disposition and actual task patch. Challenge the strongest closure claim, one possible counterexample, the strict-oracle qualifier, all lead dispositions and clean-checkout reproducibility. Follow `docs/research-workflow.md` and `AGENTS.md` for receipts, immutable-source protections, free-space checks before material writes, task-only diff, review manifest and uncommitted handoff.

## Deliverables

- **One concise durable closure/readiness audit record** in the repository's existing audit location/conventions. This is the decision record, **not** a new numbered scientific dossier or second lead register. Include the claim matrix, complete lead-disposition table, verified reuse/provenance findings, blockers if any, final recommendation and independent review outcome.
- **Minimal updates** to existing authoritative subjects and the sole `docs/hypotheses.md` register only for verified corrections or explicitly approved disposition changes. Avoid rewriting the baseline or validation record simply to summarize them.
- Private verification/check receipts and independent review under `.local-work/codex/SRR-025/` and `.local-work/independent-review/SRR-025/`; task-only Git diff in `.local-work/diffs/`; changed-path inventory and final HEAD/index/status. Do not stage, commit or push.

## Acceptance criteria

SRR-025 is complete when (1) the readiness definition is applied explicitly; (2) all major scientific areas receive bounded evidence-based readiness judgments; (3) **every current lead** receives a justified disposition without being silently discarded; (4) reproducibility, custody, applicability and future reuse are critically tested, with checks and their limits recorded; (5) the final closure/conditional/not-ready decision is actionable and not dependent on optional live experiments unless a concrete blocker requires one; and (6) a distinct independent challenger verifies the substantive assessment and delivered task-only patch.

**Stop conditions:** Do not expand into new reverse engineering merely to clear an open lead. If the audit finds a potentially false central conclusion, inspect only the necessary existing evidence to characterize it; document a precise corrective investigation if a substantive new experiment would be needed. Report `COMPLETE`, `REWORK` or `BLOCKED` according to the existing workflow. The maintainer, not Codex, decides whether to declare the programme closed or authorize further work.
