# SRR-019 — Resource Consumers and Player Survey-State Boundaries

**Implementation brief · 19 November 2026**  
**Repository:** `starfield-resource-research`  
**Work type:** Bounded, offline retail-native static investigation  
**Approval:** This brief authorizes the investigation and proportionate documentation/tooling changes below, **not** live game access, debugger attachment, save manipulation, reproduction-model changes, staging, committing, pushing, or publication.

## 1. Purpose and research question

The resource-generation model and the retail title-card retained allocation have been extensively validated. SRR-019 investigates a different boundary:

> How does retail Starfield transform available planetary resource information into player-specific discovery/survey state and the resource information displayed by the game?

**Primary priority:** Locate, qualify, or meaningfully bound the *player-specific survey-state owner(s), representations, readers, and mutation paths*. Mapping every consumer of the retained resource database is **not** the objective. Work from both sides: downstream from proven resource-data readers and upstream from defensible survey/UI entry points. Do not presume those paths meet, or that discovery state resides in `BSComponentDB2::DB`.

This task is **static reconnaissance and relationship mapping**, not complete survey-system reverse engineering or proof of the game's observed gameplay semantics.

## 2. Starting evidence and observation prompts

Begin with the current committed, consolidated documents, particularly:

- `docs/component-database.md` — retained `BSGalaxy::CTPerBiomeData`, indexed component reads, native identity, known consumers and operation boundaries;
- `docs/retail-execution-lifecycle.md` — relevant startup/lifecycle context;
- `docs/function-register.md`, `docs/structure-register.md`, `docs/PROVENANCE.md` — locators and evidence-domain/build qualifications;
- `docs/allocation-validation.md` and `docs/hypotheses.md` — observation limits and active leads;
- existing Ghidra tooling/documentation and read-only static evidence where warranted.

**Executable:** the established pinned retail `Starfield.exe` **1.16.244.0**, SHA-256 `7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28`. Confirm the applicable image/analysis identity from existing evidence before reporting executable-relative addresses. Keep **Creation Kit static**, **Creation Kit live**, **retail static**, **retail live**, and **cross-executable inference** explicitly distinct. CK mechanisms are reference context, not proof of a retail survey-state pathway.

Treat the following as **user gameplay observations/hypotheses to explain or test**, not established native mechanisms:

| Body | Screenshot observation | Candidate interpretation requiring verification |
| --- | --- | --- |
| Sumati | Resource list `UNKNOWN`, body survey 17% | Planet not yet scanned or visited; planetary visibility may gate list presentation |
| Vectera | Five resource names displayed, `RESOURCES (0/5)`, body survey 80% | Body visited during introduction, but individual resources not formally surveyed |
| Kreet | Eight resource names displayed, `RESOURCES (4/8)`, body survey 60%; apparent discrepancy between counter and brighter entries | List disclosure, per-resource appearance, and survey count may depend on different predicates; **do not assume** brightness equals surveyed state or declare a UI bug |

Reported gameplay rules needing confirmation: orbital scan **or** landing may expose a body's resources; explicit handheld scan **or** harvesting may discover individual terrestrial resources; atmospheric resources may be automatically marked known on arrival, with **landing versus disembarking unresolved**. The small rarity diamonds are separate visual data; do not treat them as discovery badges without contrary native evidence. Scanning-skill gating may affect orbital presentation, resource knowledge, or both; distinguish if the evidence permits.

The reproducer's atmospheric input/model describes **resource membership and origin**; it is **not** an established oracle for player survey knowledge or arrival triggers.

## 3. Investigation workstreams

At most **two concurrent sub-agents**; the parent coordinates evidence, settles overlap, and writes the final synthesis. Agents may pursue complementary routes, not duplicate broad scans.

### A. Retained resource data → downstream consumers

1. Recover the smallest useful set of **proven native** resource-data readers, returned-copy and borrowed-payload contracts, and any established planet-wide/atmospheric resource aggregation path. Preserve exact native type/owner, address domain, direction and evidence grade.
2. Follow concrete callers, data movement, or registration edges toward gameplay and presentation. Distinguish resource **existence/membership**, biome allocation, atmospheric membership, and any player-state interpretation. Show actual joins or explicit limits of reachability; never infer survey ownership from a resource FormID alone.
3. Stop following a consumer branch when it becomes unrelated, leaves the evidenced graph, or offers no discriminating question. A credible dead end is a valid result.

### B. Gameplay survey/UI → upstream owners and producers

1. Identify defensible static entry points or providers associated with planet scan/visit, handheld scan confirmation, resource harvesting, survey completion, and resource database UI. Search by grounded strings, native RTTI, references, call sites, or prior verified locators; **strings and suggestive names are leads, not proof**.
2. Look for concrete state owners and operations capable of distinguishing, where supported: body discovered; body scanned; resource membership; individual resource surveyed; resource name revealed; and survey progress. **Do not predefine six flags, tables, or bits.** Record actual representation, keys, actor/player ownership, readers, writes and predicates before semantic naming.
3. Trace the UI **list contents/order**, **per-resource visual treatment**, and **numerator/denominator** as separate outputs. Establish shared or distinct source predicates only where qualified. Examine the Kreet `4/8` question as an unexplained relationship, not an assumed defect.
4. Explicitly investigate atmospheric-resource survey handling and the landing/disembark/orbit distinctions, but do not assert an event trigger unless the native path supports it. Identify the smallest discriminating gameplay test when static analysis is insufficient.
5. **Conditional serialization reconnaissance:** only if a credible player-specific state owner emerges, inspect directly connected persistence/save/load methods or registration. Distinguish demonstrable serialization from generic save-system proximity. Do not perform an unrestricted serializer or save-format sweep.

### Cross-stream reconciliation

The parent agent maintains a compact **relationship/evidence matrix** covering: source → operation → state owner/consumer → UI/trigger if reached, with native locators and proof grade; otherwise label the missing edge and a concrete way to test it. Do not collapse an absence of demonstrated connection into a proven absence of connection.

## 4. Evidence and method requirements

- **Offline only.** No launching/attaching to Starfield, no debugger/live trace, no gameplay or save tests, no operating on private save files, no Ghidra project mutation without separately approved scope. Existing read-only decompilation, disassembly, RTTI/string/reference inspection, and narrowly scoped static helper scripts are permitted.
- Establish native claims using instruction-level evidence (register/data flow, call semantics, branches, writes and consumers), with precise addresses, build pin, qualification and counterexamples/uncertainty. Treat a decompiler alias, class-like label, matching FormID, or isolated reference as insufficient for a claimed causal join.
- Avoid turning CK evidence or reproducer-generated output into retail-live behaviour. Preserve the existing resource-generation algorithm, retail allocation findings, and strict-oracle applicability limits. **Do not modify** `starfield-resource-reproducer`.
- Reuse existing tooling where possible. Temporary scripts and intermediate outputs stay under ignored `.local-work/`. A new **tracked** helper requires an independently useful, repeatable task and documented provenance; otherwise do not enlarge the maintained tool surface.
- Work within a bounded set of evidence-grounded leads. Before pursuing a branch, record the starting locator, the proposed connection and what observation would distinguish success from a dead end. Close it on demonstrated relationship, contradicting boundary, or exhaustion of *identified* meaningful references. **No arbitrary function counts, time cutoffs, or speculative recursive xref exploration.**
- Do not require broad environment, rights, authorization, release, or security infrastructure unrelated to this offline analysis. Follow existing project workflow only where applicable. Maintain starting worktree state, preserve unrelated changes, and do not stage/commit/push.

## 5. Deliverables and documentation

Provide a concise final research synthesis, with:

1. **Established native relationships:** a directional graph/table of supported resource data, discovery state and presentation connections, with retail locators and evidence categories.
2. **Player-specific survey-state candidates:** for each, whether it is proven, candidate-only, contradicted, or unlocated; actual storage/key/owner if identifiable; reads, writes and event associations. Name what was *not* found without claiming proof of absence.
3. **UI and atmosphere findings:** separately report list disclosure, visual styling, `x/y` arithmetic, skill gating and atmospheric discovery triggers; clearly differentiate verified mechanisms from screenshot/gameplay hypotheses.
4. **Persistence boundary:** evidence-grounded direct associations, or a concise account of why static inquiry cannot yet attribute a serializer.
5. **Next observational design:** the smallest worthwhile controlled gameplay tests, including starting conditions, single action, screen/state measurements and alternatives each test discriminates. Account for orbit scan, land, disembark, terrestrial scan, harvest and atmospheric behaviour where relevant; do **not** perform them in this task.
6. **Unresolved leads and stopping rationale:** few concrete follow-ups with evidence locators and what additional evidence is needed; no speculative roadmap.

Update existing authoritative files only as warranted: `docs/component-database.md`, `docs/retail-execution-lifecycle.md`, `docs/hypotheses.md`, `docs/function-register.md`, `docs/structure-register.md`, `docs/PROVENANCE.md`, and appropriate existing validation/tool docs. **Do not automatically create `docs/SRR-019-*.md`, a new subject document, an additional lead register, a progress diary, or a tracked audit.** Only introduce a new current subject file if the result genuinely cannot fit the existing structure; justify it before creation. Keep detailed working notes, independent reviews and patch under the established ignored `.local-work/` locations (singular `.local-work/independent-review/`). No hypothetical-mod motivation or future product design belongs in current research docs.

## 6. Independent review and acceptance

Use an independent challenger, supplied the original brief, change inventory, exact patch, principal primary native locators and core contrary cases. Challenge **scientific inference**, not merely successful tool execution. In particular verify:

- CK-specific findings and retail static/live evidence do not become interchangeable;
- every asserted database → player-state → UI edge has actual qualified evidence;
- UI counter/list/style semantics are not inferred solely from screenshots;
- orbital/landing/disembark and atmospheric behaviour remain hypotheses unless traced;
- candidate persistence structures are not promoted to proven serialization;
- previous generation/retail allocation findings and native locators are preserved;
- documents remain navigable, present one authoritative lead register, and do not acquire speculative mod requirements;
- any added tooling/tests are relevant, reproducible and offline; no unrelated repo edits.

An outcome is acceptable without a complete survey-state or serialization recovery **if** the evidence-backed boundary map is useful, the strongest candidate routes have been examined to their meaningful ends, and the remaining unknowns are expressed as concrete discriminating observations. Report `COMPLETE`, `REWORK`, or `BLOCKED` with grounded reasons, not an invented implementation quota. Provide a task-only diff and changed-path inventory for maintainer review. **Do not stage, commit, push, tag, publish, or request live game access under this brief.**
