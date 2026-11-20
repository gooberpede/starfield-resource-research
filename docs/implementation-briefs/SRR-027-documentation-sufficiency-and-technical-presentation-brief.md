# SRR-027 — Documentation Sufficiency and Technical Presentation

**Project:** `starfield-resource-research`  
**Task type:** bounded release-readiness documentation review and necessary remediation  
**Proposed release:** `v1.0.0-sf1.16.244.0` (proposal only; do not tag or publish)  
**Execution:** offline/read-only scientific inputs; up to **three concurrent sub-agents**, followed by a **separate independent challenger**  
**Disposition:** implementation brief; all edits unstaged and uncommitted for maintainer review

## 1. Objective and standard

Make the existing research understandable, navigable and technically usable by an **experienced technical reader starting from the public repository**, without access to historical conversations, the authors' local directories or exploratory scratch records. The reader may be familiar with programming, Bethesda modding and/or reverse engineering, but should not be assumed to know project-specific nomenclature, the SRR chronology or every native component layout. Do **not** turn this into a beginner's tutorial for Ghidra, Python or the Creation Engine.

This is a **sufficiency exercise, not an expansion quota**. Prefer confirming that an existing explanation is adequate to adding text. Make focused improvements only where a concrete reader task exposes ambiguity, an unsupported leap, a missing relationship or a navigation failure. Preserve the research closure decision and scientific qualifications established through SRR-025.

**Primary acceptance standard:** From the released repository alone (plus explicitly declared lawful inputs and the pinned public `starfield-resource-reproducer` exception), a reader can locate, understand and follow the principal recovered mechanisms, validation evidence, reproduction methods and limitations.

## 2. Baseline and boundaries

Read `AGENTS.md`, `docs/research-workflow.md`, `docs/README.md`, `README.md`, and the release documentation before making changes. Record starting HEAD, index status, worktree changes and untracked files. Preserve any pre-existing SRR-026 work and the supplied SRR-027 brief. Use the current authoritative subjects, in particular:

- `docs/v1-research-baseline.md` — algorithm, effective inputs, RNG, families, cache, guards and fallback.
- `docs/allocation-validation.md` — validation channels, native census, strict-oracle boundary and historical evidence.
- `docs/retail-execution-lifecycle.md` — retail startup, scheduling, input-readiness and visited-bit execution boundaries.
- `docs/component-database.md` — typed stores, keys, commands, resource snapshots, `PlayerKnowledge`, save/load and interface rules.
- `docs/function-register.md`, `docs/structure-register.md`, `docs/glossary.md`, `docs/PROVENANCE.md`, `docs/hypotheses.md` — locators, terminology, evidence scope and outstanding questions.
- `docs/release-workflows.md`, `docs/release-smoke-tests.md`, `docs/release-candidate.md`, `docs/release-public-evidence.md` — portability and release-reader entry points, as applicable.

The latest verified static pins are **Starfield.exe and CreationKit.exe `1.16.244.0`**, with distinct SHA-256 values in `docs/PROVENANCE.md`. Some historical CK live traces or retail captures lack trace-specific build attribution; do not erase this caveat. The reproducer is the **sole expressly permitted external companion project**, referenced by its pinned public commit, not by an implicit sibling checkout.

No new native research, gameplay, save modification, debugger attachment, SFSE implementation, reproducer modifications or reinterpretation of scientific findings is authorized. A demonstrable documentation defect may be corrected within the evidence already held; if it would require new investigation or materially alter a scientific conclusion, describe the issue and hold that change for separate approval. Do not create numbered research dossiers, parallel lead registers or a new documentation architecture. **SRR-028, not SRR-027, owns archival housekeeping.**

## 3. Reader-task assessment before editing

First perform an independent reader-oriented gap assessment, starting at `README.md` and `docs/README.md`. For each question below, record the actual navigation route, relevant passage/diagram or executable method, and a concise **PASS / REPAIR / LIMITED BY EVIDENCE** disposition. Do not accept a route that requires knowing a historical SRR number, local `D:\Projects\...` path or private scratch filename to find essential context.

| Reader question | Expected authoritative route |
| --- | --- |
| How do PNDT, BIOM, effective RSGD, RSCS, IRES and atmosphere lead to planet/biome inorganic membership? | Generation baseline; input resolution, order and suitable flow explanation |
| What are the distinct RNG uses, Special/Everywhere processing, Common family cache, five-tree/shared-eight guards and fallback? | Baseline algorithm, existing pseudocode and native locators |
| What is an identity versus an occurrence, and how do model outputs relate to seven retained native slots? | Baseline, database and validation; no grain conflation |
| Where and how does retail store per-biome allocations? | Component database, relevant structure/function registers |
| How are typed mutations submitted, serviced and made visible to allocator consumers? | Lifecycle and database; scheduling versus completion distinguished |
| What is `PlayerKnowledge`, how is it keyed/serialized, and how is survey credit calculated? | Database, registers and provenance; saved data versus inferred loaded state |
| Why do Locations, orbital map and scanner wheel counters/colors differ? | Three-interface comparison and knowledge predicates |
| What can an independent researcher rerun, with which exact versioned lawful inputs and tools? | Validation, release workflows, provenance, pinned companion |
| What is established versus unqualified, historically observed, deferred or outside scope? | Validation, provenance, lead register and release statement |

Where a passage is already sufficient, leave it unchanged and record the basis for that judgment. A successful read-through is a deliverable in itself; do not merely count edits, headings or diagrams.

## 4. Selective technical improvements

### A. Generation and validation

Assess whether the generation baseline has a coherent, followable explanation of the *enclosing* flow and its principal branches: effective input resolution, biome order/shuffle, atmospheric and Everywhere contributions, Special, Common-family creation/reuse, guard fallback and resource occurrence handling. Add or revise **only necessary** diagrams or pseudocode, located in the authoritative subject. Each nontrivial algorithm must identify whether it is explanatory pseudocode or an instruction-grounded rule; associate branch/order claims with existing native evidence. Do not accidentally collapse distinct RNG primitives or infer exact retail instruction equivalence from output agreement.

Preserve the measured validation distinctions: **1,444/1,444** canonical memberships, **10/10** fresh holdouts, **22,470** diagnostic ordered-slot matches across **3,210** common keys, and **0/3,211** strictly admitted native-oracle rows due to missing independent effective-input attestation. Do not misrepresent the all-zero Volii Alpha record as a valid modeled comparison, or imply that biome membership locates an outpost-scale deposit.

### B. Retail database and PlayerKnowledge

Assess whether a reader can understand the relationship between the indexed component stores (`CTPerBiomeData`, `PlayerKnowledge`), typed command submission, asynchronous service, snapshot construction, resource normalization and presentation. Consider a **single precise data-flow diagram** if existing prose is difficult to follow. Similarly, assess the need for compact illustrative pseudocode for resource-credit calculation, `PlayerKnowledge` lookup/update, or the three interface-specific predicates.

Distinguish body-wide visit credit from item progress; the two save GlobalData records from runtime in-memory structures; requested, completed and visible writes; and Locations/orbital scan-level color eligibility from wheel discovery/color behavior. The radial wheel's absent-biome-ID exception remains a bounded native predicate, **not** a claim that arbitrary off-planet resources appear in the wheel. Retain static-versus-live timing caveats and evidence-backed consumer relationships.

### C. Glossary, navigation and new-reader usability

Check `docs/glossary.md` for material gaps added by SRR-019–024. Candidate terms include `BSComponentDB2::DB`, `CTPerBiomeData`, `PlayerKnowledge`, typed component, per-body snapshot, effective scan level, visited bit, item progress, survey credit, knowledge/disclosure predicate, native oracle versus diagnostic agreement, strict admission, and serialized versus reconstructed versus displayed state. Add only terms that genuinely clarify terminology; link to their authoritative definitions. Do not catalog function names or replicate whole technical sections.

Verify navigation from the root README to the correct research subjects, version/provenance, reproduction workflow and limits. Fix broken or misleading links, missing entry-point cues and ambiguous ownership. Current authoritative sources must remain visually and textually distinct from historical briefs/audits and private evidence. Avoid repeated introductory material across subjects.

## 5. Diagrams, pseudocode and documentation quality

Use **Mermaid only where it adds explanatory value**. Suitable candidates are the generation pipeline, Common-family cache/guards, typed database operation lifecycle, PlayerKnowledge/survey-data flow and save/load. Do not mandate a number of diagrams or introduce decorative illustrations. Distinguish direct control-flow from inferred association; label queue boundaries, optional branches, source versus derived data, and any unresolved connections. Preserve distinct CK versus retail address domains and specific build pins.

Follow `docs/research-workflow.md` for Mermaid: check syntax, render and inspect the result using an already available method; if rendering cannot be performed without new installation, record the limitation and complete the available checks rather than treating a new dependency as mandatory. Check pseudocode syntax/semantics where executable snippets exist; no unapproved dependency installation or native/game execution.

Documentation changes should be small, evidence-preserving, readable and accurate. Do not make a broad text reflow, churn mature sections, or add redundant sections merely for symmetry.

## 6. Coordination and review

Up to **three concurrent sub-agents**, if productive:

- **A — generation and validation:** test reader paths and repair essential algorithm/diagram/pseudocode gaps in the baseline and validation subjects.
- **B — native storage and knowledge:** test reader paths and repair essential database, lifecycle, PlayerKnowledge and interface explanation gaps.
- **C — independent reader and terminology:** assess navigation, glossary, version/limitations discoverability, and test a reader's path to reproducible procedures.

Partition edits to avoid collisions. The parent/integrator should reconcile repeated terminology and ensure no duplicate explanation or new evidence claim is introduced. After integration, appoint **one separate independent challenger**, not an author of the substantive changes, to inspect the original brief, actual diff, source-backed claims, diagrams, navigation routes and documentation acceptance tests. The challenger must actively attempt to falsify overstatements and locate reader dead ends. Follow the existing COMPLETE / REWORK / BLOCKED gate and content-manifest workflow.

## 7. Deliverables and acceptance criteria

1. A concise **reader-task coverage receipt**, private under `.local-work/codex/SRR-027/`, recording the path and disposition for each §3 question, evidence for each repair, and accepted areas left unchanged. Keep the authoritative documentation self-contained; private receipts are review aids, not missing dependencies.
2. Only warranted edits to the existing authoritative documentation, glossary and navigation. Do not create an additional SRR-027 scientific dossier or change release asset decisions.
3. A check of local Markdown links/anchors and relevant examples; Markdown files remain UTF-8. Verify any new Mermaid graphs as specified, including rendered inspection or an explicit limitation. Preserve build/evidence grades and existing locators.
4. Independent challenger disposition and substantive review block/manifest according to workflow, including a counterexample check for scientific overstatement and reader-route usability.
5. Task-only `git diff` exported under `.local-work/diffs/`; include new task files if any, replay it against starting content in isolation and compare all delivered files byte-for-byte. Report starting/ending HEAD, index status and pre-existing changes. **Nothing staged, committed, pushed, tagged or published.**

**Scientific guardrails:** SRR-025's bounded closure remains accepted. No change may inflate the diagnostic native census into a strictly admitted oracle, equate CK and retail execution without direct evidence, erase historical provenance limits, or treat physical vein placement as established. Unresolved `ORACLE-INPUTS`, A8/A9 and visit timing remain properly qualified.

**Success condition:** The named reader tasks can be answered from a clean repository and declared lawful/pinned inputs, with transparent evidence limits. Quality is measured by correctness and sufficiency, **not volume of edits**. If the existing material already passes a task, record PASS without editing it.
