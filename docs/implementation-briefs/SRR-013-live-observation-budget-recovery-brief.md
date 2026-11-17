# SRR-013 — Live Observation Budget Recovery

**Codex implementation and independent-review brief · 16 November 2026**

## 1. Decision and scientific context

The single authorized retail title-card structural observation reached the authenticated `BSComponentDB2::DB` context, completed both selected PNDT index ranges, identified all four selected `CTPerBiomeData` records and independently validated every nonzero `BGSResource` FormID in its **first collection**. That collection's four seven-slot vectors also **descriptively matched** the predeclared SRR-012 sample-plan predictions. The second collection did not complete, so all four formal verdicts correctly remain `STATE_INDETERMINATE` (`observation_budget`); neither the paired structural verdicts nor the comparison controls qualified. Starfield exited normally, and the save protections passed. Preserve those original results and exact evidence unchanged.

The recorded failure was a wall-clock timeout at 5,000,920,400 ns, with only 1,092 calls and 20,032 requested bytes—well below the count and byte ceilings. An arbitrary disposable-test duration leaked into a retail measurement and prevented completion of an otherwise progressing acquisition. **Fix the policy, not the evidence.**

**Approved scope:** Offline engineering changes to the existing SRR-013 inspector, owned/disposable-process qualification, narrowly scoped documentation, frozen candidate, and independent review. **Not authorized:** retail Starfield launch or inspection, new live measurement, save operations, debugger attachment, privilege escalation, Git staging/commit/push, changes to earlier receipts, or changed scientific verdicts. Up to **two concurrent sub-agents** may be used; parent owns integration and final disposition.

## 2. Required technical change

Make the actual live observation depend on **bounded work, valid progress, valid identity and operator control**, not an arbitrary elapsed-time limit.

Inspect and reconcile **all** production-path time limits, at minimum:

- `tools/srr013/observe.py`: `WINDOW_NS = 5_000_000_000`, its absolute `RecordingReader` deadline, before/after-operation comparisons, and `LIMITS`/receipt/replay representations.
- `tools/srr013/native.py`: `MAX_SECONDS = 8`, the `Collection.deadline` check within `Collection.exact`.
- Any wrappers, retail controllers, checkpoint admission, token rules, or fixture harnesses that might impose an equivalent wall-clock expiry on a healthy paired collection.

Remove arbitrary **acquisition-duration** cutoffs from the live scientific path, including the per-collection eight-second limit. Do not just raise five seconds to another unexplained number or disable one timer while leaving another blocking the same work. Preserve meaningful *temporal ordering* predicates: marker issued after the authenticated process birth, marker and process epoch binding, operator-confirmed title state, start/end timestamps, chronological journal order and the genuine separation between independent collections. A long interval is diagnostic and may warrant operator cancellation or interpretation limits, but it must not by itself convert healthy finite progress into `observation_budget`.

Retain and clearly account for the existing finite safety budgets: maximum acquisition operations and requested bytes, native nodes/depth/entries/links/form chains, checked pointer/record bounds, no cycles, no nonprogress in traversal, and single authorized collection **pair**. Continue using fixed query/read-only handles; no target writes, thread control, debugger or remote code. Do not widen privileges on denied reads. Do not add automatic collection retries to chase a desired result. If either collection genuinely disagrees, preserve `inconsistent_pair` and do not select a later agreeing pair.

Provide a **specific termination path** for each of: complete pair, operator cancellation, target exit/identity loss, failed/incomplete read, invalid structure, traversal nonprogress, exhausted finite work budget, inconsistent pair, and journal/seal failure. Time spent should be recorded per collection and for the pair as a diagnostic. For a synchronous OS read that can block without returning, document the actual interruptibility limitation; do not invent a guarantee of immediate cancellation or build a substantial asynchronous execution framework without demonstrated need. Keep disposable-fixture watchdogs where useful, but clearly separate them from retail scientific policy and ensure they cannot be misdescribed as measurement limits.

## 3. Scientific invariants — do not relax

- Keep the SRR-012/013 **two full, independently rooted collections** and the required identity brackets, matching structural/typed-form/ownership evidence, full selected range traversal, and each sample's independently validated comparison control.
- Preserve `STRUCTURALLY_POPULATED`, `STRUCTURALLY_ZERO`, `STATE_INDETERMINATE` and the distinct strict exact-tuple mode. Effective-input requirements remain strict-mode-only; structural mode still validates FormIDs and object identities independently.
- Missing, malformed, aliased, duplicated, drifted or contradictory components **cannot** become qualified zeros or positives. Preserve the complete FormID-table-extent alias fix and prior counterexample regressions.
- Same values from two reads do not prove an atomic snapshot or uninterrupted object lifetime; a stable intermediate clear and ABA remain possible. Longer acquisition intervals must be documented honestly, not retrospectively converted into claims of allocator execution timing.
- A refusal or partial pair may retain validated first-collection evidence **descriptively**, but must not promote it to a structural verdict, an exact-tuple verdict, a comparison-control success or a galaxy-wide claim.
- One operator marker authorizes one observation at the stated checkpoint; no retry, second pair, extra checkpoint or second live attempt is implied.

If eliminating elapsed-time limits exposes a substantive nonprogress case not handled by existing finite budgets, add the smallest demonstrably necessary progress invariant, with an adversarial disposable test. Avoid speculative recovery systems, broad performance optimization, and unrelated native reverse engineering.

## 4. Offline qualification and challenge

Preserve and rerun the existing SRR-013 disposable regression suites, including all **145 external cases** from the structural-mode qualification, existing retail-like admission/authorization tests, and replay integrity controls, updating *only* tests whose old expected result depended explicitly on the unjustified time refusal. Record previous and revised expected outcomes separately, and never hide a genuine earlier failure.

Add or adapt real external disposable-process tests, not only classifier mocks, for:

1. **Slow, healthy paired collection:** both full collections finish and qualify even when the observation exceeds five seconds **and eight seconds**; use bounded fixture-controlled delays, with a separately scoped test-supervisor watchdog. No change to seven-slot interpretation.
2. **Finite safety limits:** acquisition call/byte caps and native tree/chain/node limits still refuse; these are real bounds, not new duration substitutes.
3. **Genuine nonprogress and malformed traversal:** detected via stable cursor/cycle/structure evidence, fail closed, without waiting indefinitely or misclassifying state.
4. **Cancellation and lifecycle changes:** cancellation between reads/collections, process disappearance or epoch/mapping drift; precise partial evidence and indeterminate reporting.
5. **Disagreement and temporal edge cases:** changed slots/owner between complete reads, ABA/stable-clear demonstrations, stale/prebirth/wrong-epoch markers; none gains a false verdict.
6. **Receipt replay:** both modes replay exact finished pairs and partially completed/refused pairs, with any revised limit schema/version explicit. Reject forged edits, invalid seals, changed modes and contradiction between declared limits and actual events. Prior captured receipts must remain interpretable and unaltered, including the actual five-second refusal.

The independent challenger must examine **all possible clock-based refusal paths** and construct at least one adversarial slow-but-progressing counterexample against the final candidate. Check that no fixture watchdog affects real observation. Rebuild/replay deterministically and retain comparative receipts and any failed preliminary tests. Do not require needless extra performance optimization or arbitrary test durations as a substitute for progress proof.

## 5. Documentation corrections and deliverables

Update the engineering dossier, relevant run card, measurement documentation and tests only as necessary. Add a concise, *descriptive* note to `docs/SRR-013-retail-title-structural-observation.md`:

- The first collection completed owner/registry, both planet ranges, four typed records and independent nonzero FormID validation.
- All **four full seven-word vectors** descriptively matched the predeclared SRR-012 conditional predictions (three Kreet biomes and the Decaran VII-b control), including zero positions. Cite the retained private replay and sample plan **without copying private runtime addresses or raw acquisition records into tracked documentation**.
- This comparison is **not** a qualified exact-tuple finding or a completed structural observation: second collection and closing identity checks were missing, and all final verdicts remain `STATE_INDETERMINATE`.
- State the actual 5.00092-second expiration, calls and bytes as the reason the pair was interrupted; preserve all evidence identity, historical review blocks and the independently accepted outcome.

In the revised future title-card run card, make the separation of **offline readiness** and **live authorization** unmistakable. It may recommend one further title-only run using the frozen revised source, but may **not** authorize a Steam dispatch, process handle opening, observation, extra phase, save load or travel. Preserve normal postflight, privacy and exact-custody requirements and the single-use approval gate. Save2/Save52 are irrelevant to a title-only observation; Save52 copy/travel remains a separate future gate if ever needed.

Expected handoff:

- Exact task-only patch and file inventory; unchanged committed baseline and unstaged index.
- Frozen source/execution identity, build/dependency identities, and independently reproduced disposable qualification.
- Clear original-versus-new timeout/control comparison and all retained prior outcomes.
- Independently reviewed final evidence and brief acceptance matrix, including the clock-path audit and progress/cancellation counterexamples.
- Updated dossier/run card and new live proposal, not a performed live run.

**Required disposition:** `READY FOR SEPARATE RETAIL TITLE-CARD RE-AUTHORIZATION` only if all invariants and test controls pass. Otherwise report `RECOVERY BLOCKED` with concrete unresolved predicates and remaining actionable leads. Follow the previously agreed **lead-exhaustion rule**: every relevant feasible issue discovered must be resolved, excluded with evidence or explicitly blocked; avoid unlimited general-purpose debugging. Two concurrent sub-agents maximum.

**Git:** Keep changes unstaged, uncommitted and unpushed. The maintainer will review the resulting diff and challenger report before any new live authorization.
