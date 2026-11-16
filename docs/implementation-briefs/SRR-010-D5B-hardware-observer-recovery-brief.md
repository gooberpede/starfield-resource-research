# SRR-010 — D5B-Guided Hardware-Breakpoint Observer Recovery

**Codex offline implementation continuation | Maintainer brief | 16 November 2026**

**Required handoff:** `READY FOR STAGE B RE-AUTHORIZATION` only after independently reviewed qualification; otherwise `REWORK` or a precisely evidenced `BLOCKED`/design-decision handoff. **No live Starfield/Steam launch, attach, Save2 load, commit, stage or push is authorized by this brief.** Continue the existing SRR-010 investigation; do not create SRR-011 for this work.

## 1. Controlling objective and decision policy

Deliver the most credible **working four-site, all-thread hardware-breakpoint observer for a retail Save2 load**, guided primarily by actual successful D5B live instrumentation in `starfield-outpost-research`. Prioritize successful operation and scientifically useful sensitivity over definitive forensic attribution of prior `0x80000004` exits. A valid, demonstrably better mechanism may be adopted while the cause of those exits remains unresolved.

Do **not** achieve apparent stability by quietly removing the observations needed for the research. Preserve the current focal-invocation and allocator-arrival criteria and their causal joins, or stop for explicit maintainer review of any proposed change to the scientific contract. The independent challenger must be able to distinguish *stability*, *sensitivity*, and *qualified coverage* rather than treating them as interchangeable.

### Settled evidence that this work must preserve

- SRR-009: a qualified 84.281-second post-title **`NOT_OBSERVED`** result with all four sites armed; the game exited normally. Preserve its STOP-500 seal and subsequent administrative observer closure.
- SRR-010: **three** four-site Save2 loads ended before player control with target exit `0x80000004`, no delivered corresponding exception in the recorded journals, and primary load outcome **`INSTRUMENTATION_INCOMPLETE`**. Reduced running-thread polling, then reduced menu/load-period suspensions, did not permit completion. None establishes the crash's cause.
- **Control A:** maintainer-reported ordinary, uninstrumented Save2 load to settled gameplay and normal Quit; not a native audited capture.
- **Control B:** the native debugger-only observer attached, Save2 reached operator-confirmed settled gameplay, and an operational endpoint was durably sealed. Exact-process witness observed normal exit 0. Formal **`CONTROL_INCOMPLETE`** remains correct because native debugger retirement lacked the terminal event/receipt; do not relabel it. Control B has **zero resource-allocation sensitivity**. This is strong positive operational evidence that debugger presence/event servicing alone is compatible with the load under the tested conditions.
- Save2/HIST-0245 remains preserved privately; no new game-visible working save, save relocation or elaborate selection check is required. Protected original and backup content must remain undisturbed.

Keep an **outcome-first** SRR-010 dossier. Preserve immutable historic bytes, dispositions, reviews and experimental limitations; do not make the reader traverse the debugging chronology to discover the current scientific status.

## 2. Reconcile the actual working D5B implementation, not merely its narrative

Inspect relevant **tracked source, exact revision/build identities, control code and primary retained evidence** in `gooberpede/starfield-outpost-research` for D5B's native observer, including the successful Save52-load / Build Mode sequence. The prior reviewed SRR-010 recovery record identifies D5B's 95 initially verified threads, **15,119 captured/acknowledged/RF-verified resumes**, and its different sites and workload. Establish its exact code paths and evidence scope; distinguish the successful live span from later lifecycle/retirement issues.

Use the sibling project's `research/resource-retained-population/` source and `docs/experiments/resource-retained-population/` records as discovery starting points; **locate and pin the actual D5B build-15 sources and live artifacts rather than presuming any similarly named current file is identical**. Keep necessary borrowed code under this project's own tracked tree with versioned provenance and rights notices where appropriate, so no new hidden runtime sibling-checkout dependency is introduced.

For direct comparison, inspect current SRR-010 native observer and Control B mode, plus the working `starfield-reference-handles` smoke and relevant outpost EXP0002A negative controls. Produce a concise matrix for:

1. Process/debugger attachment and event-loop ownership;
2. Initial and new-thread DR0–DR3 setup, thread lifetime and context writes;
3. Actual exceptions, breakpoint ownership, DR6, TF, RF and `ContinueDebugEvent` disposition;
4. Event-held versus running-thread suspension/readback/census, and module transitions;
5. Load-transition behavior, event pressure, evidence queues and STOP/prefix preservation;
6. Cleanup/exit behavior, separating post-science retirement faults from failures during the load itself.

Record which comparisons are **observed in live game**, **disposable-qualified**, **source-derived**, or **unresolved**. A D5B success does not prove that its mechanisms will work at SRR-010's sites or with Save2. Avoid a broad catalogue of hypothetical Windows faults or re-investigation of every old experiment.

## 3. Choose and implement a credible recovery

**Primary candidate:** a D5B-informed event-service / breakpoint-lifecycle adaptation that retains **four sites on every eligible thread**, with the SRR-010 identities, phase protocol, exact predicates, causal correlation, journals, seals, and eligibility qualifications.

Codex may change native debugger implementation mechanics more substantially than in previous scheduling-only continuations when justified by observed prior art. Prefer a coherent, testable adaptation over successive speculative polling changes. Do not import D5B's gameplay-specific addresses, target behavior, identity assumptions, or unqualified cleanup. Don't broaden access rights or introduce game writes merely because the other tool had them.

**Secondary comparison/fallback:** a smaller breakpoint footprint *only* if the primary approach is unconvincing or materially blocked. Compare first with disposable controls, not a live exploratory session. Record precisely what a reduced instrument could positively detect and what it could *not* establish. A lone unjoined allocator hit may be retained as a site arrival, **not** promoted to the existing `OBSERVED_REACHED_ALLOCATOR` causal verdict. Selected-thread coverage is disfavored unless a defensible independent selection rule identifies all relevant threads; an unarmed thread population generally precludes a qualified negative.

**Maintainer decision boundary:** If a scientifically useful solution requires changing the established verdict definitions, removing required causal sites, abandoning all-thread coverage or redefining qualified `NOT_OBSERVED`, **do not silently implement or ship it**. Return a compact design trade-off with exact lost/retained claims and evidence, requesting approval before that scientific-contract change. If the strongest safe design is not yet supported by adequate prior art, report that limit rather than claiming success from fixture survival.

No definitive proof of the previous exit mechanism is an acceptance criterion. Bounded analysis of relevant exit/event records may inform an implementation choice; stop once a justified, testable route is available.

## 4. Mandatory scientific and operational invariants

Unless separately approved, retain:

- Retail executable identity, process birth/epoch, Steam attribution, critical mapped-image and runtime checks, SFSE exclusions, and origin-verified Steam drift admission.
- The four SRR-005 sites, in existing DR0–DR3 mapping, and existing validated focal iterator → callback → allocator evidence predicates. Maintain callback and downstream frame joins across `LOAD_BEGIN`, `PLAYER_CONTROL` and optional Lodge markers when the native records permit; gaps must invalidate only the affected claims.
- Per-thread register ownership, correct trap attribution, DR6/TF/RF handling, exception forwarding, and correct continuation of debug events. No blanket exception swallowing or fabricated ownership.
- Actual initial/new-thread arming coverage, thread-exit reconciliation, relevant module handling and explicit, defensible limits on **quiet-window** confidence. A positive captured at a covered site must remain assessable even if another interval fails.
- Phase ordering and individual durable acknowledgements: authenticated debugger/arming → responsive menu → `LOAD_BEGIN_DURABLE` **before** operator selects the ordinary Save2 → `PLAYER_CONTROL` where observed → optionally one Lodge crossing if practical → scientific STOP. No speculative marker batch.
- Durable JSONL journal and verifiable STOP sidecar (sequence, byte count, SHA-256); distinguish trusted partial prefixes from complete scientific seals. Report instrumentation, scientific outcome, target survival, observer retirement and data protection separately.
- Normal Steam launch under the maintainer's ordinary interactive user, **human UI actions**, populated saves and non-destructive backup comparisons; private data stays local. Preserve Steam overlay/Cloud state checks, `__COMPAT_LAYER` handling and C:/D: 40,000,000,000 caller-available-byte floor plus write reserve.
- Capture-first evidence and non-killing observer recovery. An observer left alive **after independently proven target exit** can be administratively closed under the established exact-process/evidence rules only when **separately authorized for the future live run**. Do not invent authority to terminate a running game or detach while it is alive.

Do not impose arbitrary live inactivity, duration, or hit-count cutoffs. Fixture-only watchdogs are distinct from live science bounds.

## 5. Targeted offline qualification

Build a small **comparative** fixture program and evidence set under ignored SRR-010 work roots. Use the reviewed incumbent binary as baseline and compare the recovered candidate on the **same stimulus**: concurrent thread churn, all four known execution sites, burst/hot-site hits, thread creation/exit, DLL transitions, relevant phase markers, and abnormal exit/retirement. Demonstrate not just process survival but scientific sensitivity and integrity.

Mandatory adverse/positive cases:

1. Busy four-site run with real owned hits and correct DR6, TF, RF, native event continuation, initial/new-thread coverage and **fully joined** iterator/callback/allocator positives.
2. Positive joining across `LOAD_BEGIN`/`PLAYER_CONTROL` and preservation of that positive through later STOP failure or abnormal exit.
3. Quiet, fully observed load with evidence supporting only the qualified negatives that the sampled-coverage contract genuinely permits; include unarmed, missed-readback, unknown-module and displaced-slot counterexamples that cannot become false zero.
4. Competing/foreign breakpoint or single-step event delivered without misattribution or destructive swallowing; another debugger ownership refused where necessary.
5. Writer loss / sidecar-publication fault with last trusted prefix intact and no false `STOP_DURABLE` or terminal science verdict.
6. Abnormal target exit and post-seal debugger retirement anomaly independently classified; a scientific positive can survive operational failure.
7. Original Stage A/Stage B regressions and Control B debugger-only invariants, proportionately rerun where shared code changes affect them. The new candidate must not impair the successful debugger-only operational control.

Make native, independently checked event/slot readbacks the basis of claims; do not rely merely on fixture self-reported verdict labels. Preserve failed qualification attempts. Keep the prior successful four-site observer available as a pinned baseline, not overwritten.

If there is a comparative **failure to demonstrate scientific detection**, label `REWORK` or return for scientific-design approval. An observer that simply runs quietly is not ready.

## 6. Documentation, review and exact handoff

Maintain **one current SRR-010 dossier** with a short leading statement of the scientific status (save-load allocator question still unresolved), method and scope; append only a concise recovery comparison and justified candidate decision. Keep raw comparative traces, historic replay copies and review rounds in ignored local evidence. Correct any research/dependency references affected by actual changes. Do not republish private saves, game bytes, debugger traces or licensed third-party material.

Obtain a separate **independent challenger** supplied the original briefs, prior live primary evidence/controls, actual diff, prior-art sources and new raw qualification data. Have the challenger test the strongest alternative explanation and explicitly assess:

- D5B source/evidence applicability and provenance, not analogy by label;
- Full four-site/all-thread sensitivity, cross-phase causal joins and honest negative-coverage qualification;
- Correct exception disposition, hardware ownership, event continuation, process stability and safe operational boundaries;
- Preservation of SRR-009, three incomplete Stage B attempts and debugger-only Control B;
- Exact offline reproducibility, clean tracked-source dependency surface, privacy/licensing, Git status/index and patch byte replay.

Use the repository's deterministic manifest / delimited review-block convention; record exact compiled binary SHA-256, source and toolchain pins, and any behavioral divergence from the previous candidate. Build the final **task-only Git-native diff** inclusive of new tracked files, apply/reverse-check in an isolated LF-correct baseline, compare bytes against delivered files and confirm no accidental staging. Do not commit or push.

Final handoff: (a) outcome-first dossier; (b) one selected recovered observer **or a decision-ready alternative** with an explicit sensitivity map; (c) bounded run card and separate proposed one-attempt Stage B authorization; (d) qualification results and hash-manifested primary evidence; (e) independent review; (f) final task-only patch. **Stop before any retail Steam launch/attachment/save load.**

### Acceptance criteria (AC1–AC8)

- **AC1 — Historical preservation:** SRR-009 and all SRR-010 attempts and Control A/B claims are unaltered, their exact evidence identities and classifications verified; protected inputs preserved and free-space contract satisfied.
- **AC2 — Real prior-art reconciliation:** pinned D5B source/live evidence, applicable event-handling differences and limitations documented; competing mechanisms compared; no unsupported cause attribution.
- **AC3 — Pragmatic recovery choice:** candidate choice justified by demonstrated mechanism and comparative evidence, not by a speculative crash explanation; fallback/report-for-approval if primary is materially unsuitable.
- **AC4 — Scientific sensitivity:** retained four-site, all-thread detection and exact invocation/allocator joins, or explicit maintainer-facing scientific-contract change request. Uncovered or corrupted zero-result claims fail closed.
- **AC5 — Safe capture mechanics:** native debugging/exception/ownership/continuation, phase boundaries, durability, capture-first and recovery behavior work under adverse disposable controls without new unauthorized live capabilities.
- **AC6 — Comparative qualification:** controlled baseline-vs-candidate results, positive and adverse raw evidence, relevant existing regressions, and no overclaim of retail success.
- **AC7 — Reproducible/publication-safe deliverables:** tracked source or declared lawful inputs, verifiable builds, private evidence excluded, documentation results-first, clean links and provenance.
- **AC8 — Independent review and handoff:** challenger attempts falsification, resolves substantive REWORK, verifies manifests, exact patch replay and unchanged uncommitted Git baseline.

**Completion:** `READY FOR STAGE B RE-AUTHORIZATION` only if the independently qualified recovered observer preserves the original scientific sensitivity and has a credible operational basis. Offline success never authorizes live execution. If scientific-trade-off approval or a larger redesign is needed, present that decision explicitly and stop.
