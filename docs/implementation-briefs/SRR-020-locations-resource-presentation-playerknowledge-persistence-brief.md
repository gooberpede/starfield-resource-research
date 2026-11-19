# SRR-020 — Locations Resource Presentation and PlayerKnowledge Persistence

**Implementation brief for Codex · 19 November 2026**  
**Repository:** `starfield-resource-research`  
**Disposition:** Authorized offline static investigation; findings require independent challenge and maintainer review before commit.

## 1. Objective

Resolve, as far as static evidence permits, the native relationship among (a) the resource current/maximum counts calculated for a celestial body, (b) the per-resource fields supplied to the **Locations** interface, and (c) the player's persistent survey knowledge. In particular, determine whether native code can account for the user-observed **Kreet `Resources (4/8)`** beside five apparently brighter resource names, **without assuming that brightness signifies survey credit**.

The primary objective is **counter and presentation reconciliation**. Bounded secondary objectives are the handling of atmospheric-only/overlapping resource identities and **`BSGalaxy::PlayerKnowledge` serialization/restoration**. The outcome may be a demonstrable native binding, a narrowed boundary in external UI presentation, or a qualified negative. No live testing is authorized.

This is **SRR-020** as an investigation identifier, **not** authorization to create `docs/SRR-020-*.md` or another dossier.

## 2. Starting evidence and essential qualifications

Use the current committed research repository, especially:

- `docs/component-database.md` — **Resource membership, player knowledge and the Locations page**; current native relationship matrix and reproducible static decoding instructions.
- `docs/function-register.md` and `docs/structure-register.md` — retail-qualified native locators, layouts and operations.
- `docs/retail-execution-lifecycle.md`, `docs/PROVENANCE.md`, `docs/allocation-validation.md`, and `docs/hypotheses.md` — executable identities, evidence classification and existing open leads.
- `tools/README.md` and the repository's established static-inspection tooling. Consult sibling reproducer data only for independently supported resource membership, never as proof of gameplay knowledge or rendering.

**Retail target:** `Starfield.exe` **1.16.244.0**, preferred image base `0x140000000`, SHA-256 `7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28`. Treat addresses as retail VAs unless explicitly stated otherwise. The Creation Kit generation model is a distinct evidence domain; do not promote CK findings into retail instruction facts.

Relevant established retail-static anchors (verify before extending):

| Relationship | Existing locator / fact |
| --- | --- |
| Build normalized body resource snapshot | `FUN_1417D6520`; `FUN_1417D8D40`, `FUN_1417D6960` and downstream membership walks. Snapshot atmospheric span at +`0x1D0`, biome-derived span at +`0x1E8`. |
| Overlap normalization | `0x1417D6868–0x1417D6923`: removes identities overlapping biome-derived resources **from the atmospheric span**. Verify direction, identity equality, multiplicity and downstream consequences rather than infer them from summary prose. |
| Compute resource counts | `FUN_1417D7EB0`; visited bit credits the remaining atmosphere span; nonnull biome-derived resource receives credit for positive item knowledge byte +`0x21`. Current and maximum written at snapshot +`0xC4` / +`0xC8` (`0x1417D7887–0x1417D78DA`). |
| Body-scoped knowledge | `BSGalaxy::PlayerKnowledge` stored through DB+`0x268`, with visit mask, scan level and FormID-keyed item progress. `FUN_1407B65D0`, `FUN_1407BA290`, `FUN_1407B75B0 → FUN_1407B77D0`. |
| Locations rows | `FUN_1416D0EF0 → FUN_1416D1510`; row groups, labels, symbols, rarity, `bDisabled`, `bShowColor` and packed color. `FUN_1416B6310 → FUN_1416B6180` binds named row fields; Locations detail created through `0x14135F108` and `FUN_1416CF0F0`. |
| UI names / alternate counter | `LocationsBodyInfoData`, `ResourcesA`, `iScanLevel`, `bPlayerVisited`, `fSurveyPercent` known; scanner schema `uResourcesCurrent/Max` at `0x1415973A0/73B7` is **not established as the Locations `x/y` binding**. |
| Persistence candidate only | `PlayerKnowledge` factory vtable `0x144D5F2C8`, +`0x28/+0x30` → `FUN_14231FC90` → `FUN_142322A80`; known DB lookup and **in-memory copy** do not prove a save-stream write or restore. |

The observed Kreet screenshot, Vectera `0/5` with listed names, and Sumati `UNKNOWN` are **user-supplied UI observations**, with unknown prior actions/skill/settings. The screenshots do **not** prove a five-versus-four bug. The smaller diamond symbols are not discovery markers. Distinguish *resource present*, *known*, *credited*, *disclosed*, *colored*, and *rendered*.

## 3. Workstreams and division of labor

Allow **up to three concurrently active sub-agents**, not three mandatory workers. The parent agent owns scope control, cross-workstream integration, final evidence grades and handoff. A **separate independent challenger** reviews the substantive consolidated result; it is not a fourth parallel investigation. Coordinate file edits through the parent to avoid conflicting changes.

### A — Counter source, propagation and UI binding (primary)

1. Trace snapshot resource current/maximum at +`0xC4/+0xC8` forward through the body detail, Locations data providers, widget/native bindings and any formatting or arithmetic until reaching the nearest demonstrable `Resources (x/y)` producer/consumer. Work backward from named Locations counter fields, UI-bound method/asset names and the known scanner `uResourcesCurrent/Max` **independently**; reconcile only when an actual edge exists.
2. Preserve the distinction between the computed body count, intermediate copied/recalculated values, scanner UI count and **Locations** text. Identify whether counts are unique resource identities, original slot occurrences or normalized spans; confirm zero/null handling, widths and any saturation or signedness relevant to Kreet.
3. If the final string rendering is in UI assets or an external presentation layer not available in the existing lawful/static inputs, pinpoint the last proven native schema/field and the missing binding. Do not invent the bridge or require a new UI asset dump as a prerequisite.
4. Produce a concise native evidence chain with exact addresses, field offsets, argument/data origins, branch conditions, call/dispatch type and confidence for each link. Distinguish proven static reachability from observed execution.

### B — Resource row rendering and atmosphere/terrestrial overlap (primary support)

1. Trace the producer-to-consumer semantics of `bDisabled`, `bShowColor`, `rarity`, packed RGB, row order/grouping and disclosure gate; separately identify what the native code proves versus what only a final UI renderer could determine. Pay special attention to how the scan-level threshold and classes 5/6 affect `bShowColor`.
2. Re-examine the normalization at `0x1417D6868–0x1417D6923` against primary instructions and establish which span wins on an equal resource identity, whether duplicate occurrences are collapsed, and how **both** the resource count and row builder treat the normalized spans. Avoid replacing a proved algorithm with inferred UI semantics.
3. Use **Volii Alpha** as a conceptual atmosphere-only control: the SRR-017 retail record is all-seven-zero; the independently modeled atmospheric set contains Benzene and Water. Evaluate only consequences legitimately derived from the proven static predicates; do not claim a live observed `2/2` or even a specific displayed count.
4. Use **Kreet** as a potential mixed-origin test **only if the actual data establishes overlap**. Verify (or explicitly leave unresolved) the premise that Helium-3 belongs to both atmosphere and biome-derived resources in the applicable Kreet dataset. Form separate predictions for the normalized counter and row flags; do not rely on brighter names as surveyed.
5. Where suitable, create small **synthetic/offline deterministic fixtures** testing atmospheric-only, terrestrial-only and duplicate identity cases, but label them model/fixture deductions and do not mistake them for live game evidence.

### C — PlayerKnowledge persistence and restoration (secondary, bounded)

1. Start with the established `BSGalaxy::PlayerKnowledge` type registration, DB+`0x268` lookup, factory, copies and mutation paths. Identify a concrete stored-state owner, fields, and plausible serialization dispatch boundaries.
2. Seek **attributable save-stream write and corresponding restore/read** of body identity, visit bit, scan level and per-resource entries; identify transformation or versioning, if established. A type registration, factory copy, generic archive method, command submission or snapshot equality is **not** enough. Require a data-flow connection to a writer/reader acting on the same payload.
3. Inspect only evidence-grounded adjacent serializer/restore calls; avoid a broad search through the entire save subsystem. If the chain stops at a virtual or opaque boundary, record receiver identity, vtable slot, known inputs and smallest discriminating follow-up.
4. Keep serialization of the **seven biome allocation words** distinct from serialization of **player-specific knowledge**; neither proves the other. No Save2/Save52 reading, parsing, loading or editing is authorized in SRR-020.

## 4. Future gameplay test design — planning only

Produce a **small ranked experiment matrix**, derived from actual static findings, without performing any test. Use the user-identified saves and scenarios as potential fixtures, not proven records:

- **Save2**: restricted player knowledge (Vectera, Kreet and Jemison), and Volii Alpha is reachable. Suitable for controlled first-visit and resource-survey transitions.
- **Volii Alpha**: atmospheric-only Benzene/Water, supported by the all-zero terrestrial component. Candidate controls: no orbital scan, orbital scan, landing while aboard, disembark. Observe first visible counter separately from `UNKNOWN`; preserve no-action/matched branches.
- **Kreet**: `4/8` screenshot and perceived five bright names. Test counter, per-row status and scan level separately. Any Helium-3 cross-origin premise must first be validated from data.
- **Save52**: richer comparative survey knowledge, potentially useful later for save persistence and completed surveys; do not presume matching history, plugins or configuration with Save2.

For each proposed test, state the prediction under distinct hypotheses, the necessary controls and what observation would genuinely discriminate. Distinguish raw resource count, presentation, survey percentage and final counter text. **No future experiment is authorized by this brief.**

## 5. Boundaries and lead-exhaustion rule

**Allowed:** offline/read-only static inspection of the pinned retail executable, existing Ghidra project/exports, documented source and data; temporary read-only analysis helpers; narrowly scoped synthetic fixtures; documentation updates and independent review.

**Not allowed:** starting/attaching to Starfield, live tracing/debugging, opening or parsing Save2/Save52 or any save, modifying the executable/Ghidra project, editing the validated reproducer, new broad save-format reverse engineering, source installation requiring new privileges/services, speculative mod/product motivation, new SRR dossier, or unrelated DB/startup lifecycle expansion. Preserve the current committed baseline and protected local evidence. Follow existing repository workflow and safety rules without adding gratuitous gates.

Follow each concrete evidence-backed lead until (a) a qualified link is established, (b) a contrary boundary is demonstrated, or (c) the remaining available routes provide no discriminating evidence. Record the precise last proven edge and next useful evidence. **Do not invent arbitrary call-count/time quotas, and do not follow unbounded references merely because they exist.** Secondary serialization work must not displace counter/presentation objectives.

Treat native-static proof, fixture inference, existing title-card observation, user gameplay description and future experimental prediction as separate evidence classes. Neither the fully validated generation model nor the completed retail census establishes survey UI behaviour. Report unknowns as unknowns.

## 6. Deliverables and documentation

Update **existing authoritative subject documents only**, where findings warrant:

- `docs/component-database.md`: integrated snapshot→knowledge→presentation/persistence chains, with precise native locators, guards and limits.
- `docs/function-register.md` and `docs/structure-register.md`: reusable verified retail addresses, field offsets and semantic qualifications; avoid duplicating narratives.
- `docs/hypotheses.md`: refine `SURVEY-UI` and create **at most necessary evidence-grounded** independent persistence/overlap leads; keep one register. Include the concise future experiment matrix or a link to an existing subject location.
- `docs/PROVENANCE.md` **only if** new executable/data/tool identity or evidence-applicability information materially requires it. Do not rewrite settled generation evidence or unrelated files.

Keep full work logs, temporary decoded traces, fixture outputs, lead sheets and independent review under `.local-work/codex/SRR-020/` and `.local-work/independent-review/SRR-020/` (or repository-standard equivalent). Task-only diff under `.local-work/diffs/`. No tracked audit diary, new SRR-numbered document, separate lead register, or automatic archival of the new implementation brief. Do not publish private acquisition assets.

The final handoff must provide: starting and ending HEAD/index/worktree status; changed-path inventory; each workstream's principal evidence chains and decisive unresolved boundaries; classification of the Kreet hypothesis; the smallest future test matrix; repeatable offline verification commands; separate independent challenger disposition; and the task-only patch. **Do not stage, commit, push or tag.**

## 7. Acceptance and independent challenge

The independent challenger must examine the **original native evidence**, not only agent conclusions, and try to falsify the strongest claims. Specifically challenge:

1. **Counter:** Does an actual Locations-specific native binding exist? Could the evidence instead belong to scanner UI, body-survey percentage, a different widget or a stale/copy value?
2. **Overlap:** Is the atmospheric subtraction direction and duplicate treatment proved? Is Kreet cross-origin Helium-3 actually supported? Does a row's apparent brightness necessarily reflect its disabled/show-color flags?
3. **Knowledge:** Are bit/level/item-byte semantics correctly qualified and body-keyed? Could a cited getter/memory copy be mistaken for a persistent write?
4. **Serialization:** Does each claimed persistence route reach an attributable write/read of PlayerKnowledge contents, rather than merely sharing generic component machinery?
5. **Evidence:** Are all retail claims pinned to the right image/addresses, without borrowing CK live or hypothetical gameplay certainty? Are negative and incomplete paths represented honestly?
6. **Repository:** Do current source/tool references work, are all links and native locators credible, and can the task-only patch apply/reverse byte-exactly against the recorded starting state without erasing unrelated changes?

Return **COMPLETE** only if the required static workstreams and evidence tests are substantively covered, including explicitly documented and justified unresolved boundaries. Otherwise **REWORK** or **BLOCKED**, with precise gaps. Static analysis need not establish a final rendered pixel treatment or save-stream writer to pass, but must not claim either without adequate evidence.

**Scientific success:** a demonstrably closer explanation of the Locations `x/y` and per-resource appearance, or a precisely delimited interface boundary explaining what is still missing; an evidence-grounded account of atmospheric normalization; and a bounded, non-speculative PlayerKnowledge persistence assessment. The investigation should make later Volii Alpha/Kreet and Save2/Save52 tests materially more discriminating, not automatically launch them.
