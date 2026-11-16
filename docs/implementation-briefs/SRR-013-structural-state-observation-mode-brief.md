# SRR-013 — Structural Allocation-State Observation Mode and Retail Qualification

**Implementation continuation for Codex · 16 November 2026**  
**Authority:** Offline source changes, owned disposable-process qualification, and independent review **only**. No retail Starfield launch, process opening, memory inspection, save operation, Git staging, commit, or push. Up to **two concurrent sub-agents** are approved.

## 1. Background and purpose

SRR-012 established a candidate read-only path from the pinned retail image to a published `BSComponentDB2::DB` context, its `+0x300` mixed component index, and inline `CTPerBiomeData` records with seven resource-ID slots. SRR-013 implemented and independently qualified the external reader on disposable Windows processes (49 cases). Its retail-readiness continuation qualified process/checkpoint admission on additional disposable tests (35 cases), but correctly withheld retail readiness because **the exact-tuple contract requires runtime verification of active plugins, winning records, and native fallback sources**. Installed `Starfield.esm` and offline predictions alone do not certify that stronger contract.

The immediate scientific question is narrower: **at a specified checkpoint, does the authenticated game's correctly identified `CTPerBiomeData` record contain nonzero resource-ID fields, or seven zero fields?** This does not require proving that the seven words equal the pinned reproducer's prediction. Do not treat hypothetical overrides as established facts about the user's installed base-game samples, but do not convert unverified effective inputs into verified inputs either.

**Objective:** Add an explicitly separate, lower-claim **structural-state mode**, preserving full native identity, read-only acquisition, and paired-consistency safeguards. Keep the existing exact-tuple measurement mode and its effective-input gate intact.

## 2. Required outcome contract

Use distinct structural classifications; never reuse the strict classifications as synonyms:

| Structural outcome | Necessary evidence | Permitted interpretation |
| --- | --- | --- |
| `STRUCTURALLY_POPULATED` | Authenticated process/mapping and published context; verified registration, owner, unique typed edge, matching PNDT/BIOM, seven complete and stable uint32 fields; at least one **independently validated nonzero resource FormID** | Selected retained output fields were populated at the sampled checkpoint; **not** exact reproducer agreement, complete allocator execution tracing, or persistence |
| `STRUCTURALLY_ZERO` | Same structural and acquisition checks, unique present sample, all seven words zero in the accepted pair | Selected fields were zero during the sampled observation; **not** proof of no earlier allocator execution, no allocation elsewhere, or eligible-but-unpopulated in the strict SRR-012 sense |
| `STATE_INDETERMINATE` | Any failed identity, context, type, provenance, coverage, readable-field, FormID-validation or consistency gate; missing/duplicate records; mixed unresolved nonzero values | Report exact reason and raw observations where safely permitted, without promoting an ambiguous sample |

A partially populated tuple may qualify **only** if all its nonzero words have sufficiently grounded identity/type validity; it need not equal any predicted tuple. A numerical nonzero alone is insufficient. Require a demonstrable, independent native FormID/type check (or a rigorously specified equivalent) rather than a whitelist derived only from the expected tuple. If this is not feasible with the current reader, report the specific blocker and propose a more narrowly labelled raw-state observation for separate approval; do **not** silently relax `STRUCTURALLY_POPULATED`.

Do not infer runtime eligibility from offline predicted inputs in structural mode. A structurally sound all-zero record is a **state report**, not `QUALIFIED_UNPOPULATED`. `component_absent`, null/unpublished context, registered-type absence, truncated tree, unverified winning form identity, unexpected mixed-type data or read denied remain indeterminate. Controls may also be zero. Preserve per-sample outcomes for the existing three Kreet biome keys and one Decaran VII-b control, plus their explicit logical identities. Keep sample predictions as **conditional reference annotations**, never a structural admission dependency.

A full sample-set claim must not exceed the actually validated records; no galaxy-wide negative. A populated title-card state would support pre-checkpoint allocation as the leading explanation under the established native writer, but is not a direct execution trace. Equal values or pointer addresses across checkpoints do not prove continuous object lifetime. Double reads do not guarantee atomicity and may agree during an intermediate clear or an ABA cycle.

## 3. Implementation boundaries

1. **Two named modes, explicit selection.** Strict mode retains `POPULATED_RESULT_OBSERVED`, `QUALIFIED_UNPOPULATED`, `STATE_INDETERMINATE`, exact prediction predicates, and verified effective-input requirements without semantic or test regressions. Structural mode has separate identifiers and receipt schema fields. No automatic fallback from a failed strict admission to structural claims; an operator must select the mode before acquisition.
2. **Preserve common acquisition gates.** Retain the authenticated process epoch, Steam/session attribution, mapped-image/profile identity, original publication pointer, embedded context/vptr, registered `PerBiomeData` descriptor, independent authoritative form identity, key bounds, mixed B-tree and packed-block traversal, full selected-range coverage, exact read rights/limits, repeated root collection, bracket checks, and evidence sealing/replay. Structural mode may bypass **only the exact effective-input/prediction applicability requirement**, not target or component identity checks. No generic PID target, debugger, target code execution, process writes, thread controls, elevation, or opportunistic privilege escalation.
3. **Explicitly distinguish gates.** The current retail controller refuses offline-only input evidence before opening a game handle. Implement the structural-mode admission route without treating an offline disk pin as runtime effective-input proof, while preserving the current retail identity, checkpoint and authorization controls. All live operations remain disabled in this task. If a security/identity prerequisite cannot be qualified offline, stop with an attributable refusal—not an implicit downgrade.
4. **One reusable inspector.** The exact same independently frozen implementation should accept operator-bound `title`, `menu`, or `settled-gameplay` checkpoint labels; these are externally reported phase metadata, not inferred from incidental target state. A future title-only run card is a proposal, **not authority** for any checkpoint.
5. **Evidence and privacy.** Record mode/version, source profile, verified structural/form evidence, all seven raw values, validation decisions, conditional model predictions, checkpoint token/epoch and timing, provenance, per-read counters, exact refusal reasons, pair comparison and completion seal. Keep runtime addresses, process identities, Steam/account details, raw memory or private records in ignored access-controlled evidence. Tracked outputs may contain sanitized scientific descriptions and public static addresses.
6. **Minimal scope.** Reuse the existing reader and native decoder. Do not implement a generic memory dumper, plugin loader, new instrumentation framework, broad FormID catalogue, automatic background monitoring, or a full effective-input witness. The goal is a reliable narrow state probe, not a workaround for every possible future input profile.

## 4. Disposable qualification and counterexamples

Use owned synthetic Windows processes only. Preserve and rerun **all 49 original + 35 retail-like** cases (or their current committed equivalent) on the final integrated implementation, then add focused tests for the new semantics. At minimum demonstrate:

- The *same* structurally valid nonzero observation with effective inputs unverified: structural populated if independent resource-ID/type checks pass, strict mode remains indeterminate.
- The same complete eligible-looking seven-zero observation: structural zero without claims of eligibility or historical non-execution; strict mode remains indeterminate without effective-input proof.
- Mixed nonzero values: valid FormIDs yield a structural state even when different from predicted output; invalid/unresolved FormID, wrong type, alias, or contradictory identity refuses. Show that predicted tuples are not being used as the only form-validity test.
- Missing context, unpublished pointer, wrong vptr, wrong registry, wrong planet/biome key, duplicate records, mixed-type decoys, incomplete range/leaf traversal, forged block minimum, and mismatched edge versus payload identity cannot yield a populated or zero structural result.
- Simulated slot clear, mutation/replacement, pair disagreement, ABA and stable intermediate clear retain the exact limitations and appropriate classifications; test control-zero and control-failure independence.
- Wrong process epoch, duplicate retail-shaped processes, wrong backing/mapped image, Steam/session mismatch, denied or query-only rights, impossible pre-birth or stale operator marker, expired read budget, corrupted or resealed contradictory receipts all refuse appropriately.
- Strict and structural receipt replay produces identical results from recorded bounded read responses and cannot change the selected mode after the fact. No target write/attach/suspend/remote-call privileges exist in the reviewed paths.

A reviewer must challenge at least one plausible **false populated** and one plausible **false zero** case, including the distinction between exact-tuple validation and genuine resource-ID identity. Preserve counterexample attempts and fixes in private receipts.

## 5. Workflow and completion criteria

Up to **two concurrent sub-agents** may work on independent code/tests and semantic review; the parent is responsible for integration and final scientific conclusions. Maintain a compact lead register for newly discovered implementation obstacles. A plausible in-scope lead must be resolved, disproved/exhausted, or concretely blocked with why and what evidence would unblock it; do not end merely because the first tests pass. Do not expand into broad plugin provenance research.

Deliver:

1. Narrow source changes and any necessary dedicated tests; an updated engineering dossier and **proposed** title-card run card specifying the structural-only result contract.
2. A side-by-side mode comparison that identifies which checks are common, which strict checks remain and precisely which input-related gate structural mode no longer needs.
3. Exact final test matrix, native acquisition and replay receipts, frozen source/binary identity where applicable, bounded refusal evidence, and reproducible commands.
4. Independent challenger review of scientific claim scope, identity and FormID validation, negative-state reliability, least-privilege access, test counterexamples, privacy and exact task-only forward/reverse patch replay.
5. A final handoff of either **`READY FOR SEPARATE RETAIL TITLE-CARD AUTHORIZATION`** (only if structural-mode retail admission is genuinely qualified except for checks necessarily performed against the live target) or **`STRUCTURAL RETAIL READINESS BLOCKED`** with a precise blocking predicate and required next evidence.

The reviewer must not perform any live retail operation. Do not rewrite the accepted SRR-012 and SRR-013 historical claims, overwrite private evidence, or reopen SRR-010. Any later live experiment requires a **separate written authorization** after review of the exact frozen implementation.

## 6. Later live-test boundary, not authorized here

The preferred first experiment remains **one responsive title-card observation**, without loading a save or travelling. Record independently the published context's existence, selected typed biome entries' existence and the validated seven-slot states. A future menu/gameplay checkpoint would require its own approved scope. **Save52 is necessary only if an eventual experiment actually requires travel to remote systems such as Decaran VII-b**; then preserve a verified copy in `.local-work/release-assets/` by the established Save2 method before travel. No save copy or game launch is authorized now.

**Git:** Leave all changes unstaged, uncommitted and unpushed for maintainer review.
