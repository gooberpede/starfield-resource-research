# SRR-013 — Retail-Readiness Continuation: Admission, Effective Inputs and Checkpoint Binding

**Implementation brief for Codex · 16 November 2026**  
**Authority:** offline engineering and disposable qualification only. **No live Starfield launch, attachment, process handle, memory read, Save2/Save52 operation, Git staging, commit or push.**  
**Expected outcome:** independently reviewed, frozen candidate **READY FOR SEPARATE RETAIL TITLE-CARD AUTHORIZATION**, *only if* all required gates can actually be qualified. Otherwise return a precisely scoped readiness blocker; do not mislabel a fixture-only build as retail-ready.

## 1. Starting point and objective

SRR-012 established a feasible but conditional state measurement; SRR-013 implemented its native decoder, classification and read-only external acquisition against an **owned disposable AMD64 process**. The accepted implementation passed 49 external tests and independent review. The existing `tools/srr013/memory.py` `open_owned(...)` admits only the `srr013-fixture.exe` launched by a controlled `subprocess.Popen`; `contract.py` currently promotes exact tuples only for `DISPOSABLE_INPUTS`. Neither currently constitutes a retail admission mechanism.

**Objective:** adapt this exact narrow toolchain to admit the pinned retail Starfield image, authenticate one operator-declared checkpoint, and establish the applicability of the four predefined sample predictions using defensible effective-input evidence. Reuse the existing bounded native reader and scientific classification contract. Deliver an executable, reviewable **proposal** for the first **title-card-only** observation, *not* a live observation in this task.

Read first and cite in your durable report: `docs/SRR-012-retained-planetary-allocation-state-observation-feasibility.md`, `docs/SRR-012-acquisition-evidence.md`, `docs/SRR-012-measurement-contract.md`, `docs/SRR-012-sample-plan.md`, `docs/SRR-013-read-only-allocation-state-inspector.md`, `docs/SRR-013-proposed-title-run-card.md`, `docs/SRR-013-lead-register.md`, the relevant SRR-011 result-lifecycle evidence, and the research workflow. Compare current committed source and task identities; do not assume the historical patch baseline is still HEAD.

The four fixed samples are Kreet Frozen, Mountains and Volcanic and Decaran VII-b Cratered. They are **memory lookup keys**, not travel destinations. The initial title-card observation needs neither Save2 nor Save52.

## 2. Hard boundaries

- Do **not** launch, open, read, suspend, debug, inject into, call functions in, or otherwise interact with the **retail Starfield process** during this continuation. The retail EXE may be read offline as lawful data for identity and layout verification.
- A future adapter must request only the reviewed **`PROCESS_QUERY_INFORMATION | PROCESS_VM_READ`** process handle (and separately justified non-invasive metadata access where required); no write, debug, thread-context, suspend, remote-thread, elevated or auto-retry privileges. No arbitrary-PID / generic process-inspection utility.
- Preserve `native.py`'s established bounded tree and FormID decoder and `observe.py`'s two-collection journal/replay logic unless an actual incompatibility supported by evidence requires a reviewed, testable correction. Preserve the three SRR-012 verdicts: `POPULATED_RESULT_OBSERVED`, `QUALIFIED_UNPOPULATED`, `STATE_INDETERMINATE`.
- Never turn an absent, unreadable, structurally ambiguous or unexpectedly valued component into a qualified zero. The scientific sample/control relationship remains authoritative, including a valid all-zero comparison control.
- No broad process-memory scanning or dumps; read only the known image, identity, owning context, typed index, selected payloads and independently necessary witnesses. Retain sensitive PID/epoch/path/address/raw-byte evidence in ignored private custody; keep tracked documents sanitized.
- Do not change SRR-010's closed inconclusive disposition or imply that title-card resource state directly proves the instant or frequency of allocator execution.

## 3. Workstream A — Retail process and image admission

Implement a **retail-specific, fail-closed adapter** separate from `open_owned` (or a shared internal primitive with explicit profile-specific outer admission). It must not accept an arbitrary supplied PID as sufficient identity.

1. **Pinned applicability.** Retain Starfield `1.16.244.0` SHA-256 `7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28`. Verify actual executable file identity, mapped main-image base/extent, expected pointer/address RVAs, image-backed memory regions and selected mapped PE/header/code windows. Handle the loader's legitimate relocation of OptionalHeader.ImageBase as in SRR-013; do not waive unrelated mismatches. Reuse SRR-012's published context pointer `M + 0x82EEBB0`, expected embedded context `M + 0x82EE5C0`, owner/type registration, +0x300 index and rooted FormID map checks. Do not substitute an address-pattern hunt.
2. **Target attribution.** Design an operator-coordinated selection/binding method that authenticates a unique process instance by verified Steam launch provenance (or another independently evidenced equivalent), path/image identity, PID **and creation epoch**, correct session/account, and absence of conflicting instances. A PID alone, process name alone, or unverified human assertion is insufficient. Keep acquisition read-only and non-elevated. Work out how the existing Steam witness/attribution patterns can be reused *without* requiring a debugger or a new Steam launch in this phase.
3. **Admission and rechecks.** Authenticate immediately before every observation, bracket both retained collections with exact process/image identity, and fail closed on exit, PID reuse, mapped drift, unreadable region, disallowed access, ambiguous Steam provenance, altered owner or changed tree. Preserve a short, precise diagnostic for refusal. No automatic rights escalation, no fallback to debugger attachment, no unapproved process manipulation.
4. **Offline qualification.** Extend controlled synthetic targets to mimic the **retail admission contract** (including expected file/mapping layout), rather than simply disabling fixture identity checks. Use independently generated/checked records and adversarial wrong-image, wrong-owner, wrong-epoch, duplicate-process, stale marker, wrong-session, mismatch and access-denial cases. Clearly differentiate a *simulated* Steam provenance or retail profile from an actually authenticated Starfield process. Rebuild reproducibly and retain source/build identities.

If some authentication requires facts obtainable only during an authorized retail session, implement a verifiable *pending-runtime* gate and identify exactly what future evidence must satisfy it. Do not claim it has already passed.

## 4. Workstream B — Effective-input and scientific admission

The existing `DISPOSABLE_INPUTS` must **never** be passed or relabelled as a retail attestation. Establish the narrowest credible independent evidence required to apply the SRR-012 four-sample expected tuples to the user's installed game.

- Specify and verify the relevant **effective load order and overrides**, source-master identity, PNDT keys/seeds, BIOM ownership/list and any RNAM/PPBD override, RSGD, IRES and ATMO dependencies, and any previously identified differences between native/reproducer inputs. Reuse verified SRR-012 source and sibling evidence; don't repeat already-settled resource-algorithm research.
- Distinguish **offline disk-derived expectations**, **actual effective runtime data**, and **selected observed output words**. Show provenance and what can versus cannot be established without the live process. If a plugin override or uncertain load order can change expected results, refuse exact tuple admission unless resolved through a reliable bounded verification route.
- Keep exact expected-tuple comparison separate from structural validity. Clearly document whether a structurally valid nonzero result could be described provisionally without asserting equality to the predicted tuple; **do not silently broaden the existing three official classification verdicts** or label a prediction-unverified result as `POPULATED_RESULT_OBSERVED`. Any proposed scientific semantics change requires explicit maintainer review.
- Qualify the all-zero path independently of whether the comparison control is populated; an eligible stable seven-zero payload is scoped to its component and checkpoint only, not to allocator inactivity or never having executed. Require consistent paired evidence and disclose ABA/intermediate-clear limits.
- Prove refusal for unknown/contradictory effective inputs, mismatched override, absent/duplicate FormID, unsupported native fallback, corrupt seven-word tuple, and an apparently correct tuple paired with invalid provenance. Use the existing classifier/replay for deterministic results.

If runtime-effective inputs cannot be adequately attested from the permitted evidence, return **a specific blocked gate** and the least intrusive future discriminator. Do not fake successful qualification to reach the live stage.

## 5. Workstream C — Operator checkpoint and receipt protocol

Support **one observation request per separately authorized window**, with an explicit operator declaration `title`, `menu`, or `settled-gameplay` accepted by the **same frozen binary**. Build and qualify all three label paths offline, but propose only **responsive title card** for the first live run.

Bind the operator confirmation to the **exact process epoch**, a unique attempt token, a wall-clock timestamp and monotonic interval; verify the checkpoint precedes acquisition. The inspector must not infer phase from incidental game data. Treat the operator's observation as a report, not native proof of UI state. Avoid arbitrary gameplay time quotas. Enforce a bounded acquisition duration for snapshot validity, not an imposed game-session timeout.

Keep one bounded paired collection (existing 25 ms gap, five-second acquisition deadline and structural byte/record/depth/chain limits unless independently justified otherwise). Preserve full failure causality, identity brackets, precise `STATE_INDETERMINATE` outcomes, selected raw words, SHA-256-sealed journal and deterministic replay. Require an explicit new operator marker for a *separately authorized* additional observation after any invalidated window; no silent retry. Private receipts must allow independent checking without publishing account identifiers, saved-game data or raw unrelated memory.

Write a short future run card covering: authorized ordinary-account Steam title-card session; protective environment and save checks proportionate to the absence of gameplay/save loading; disabled Cloud/overlays where retained protocol requires them; exact process and image attribution; operator responsive-title confirmation; one read-only acquisition; seal/replay; normal operator-controlled Quit; independent verification and postflight. No travel, Save2 load, Save52 load or repeat observation is authorized by this engineering brief.

**Save52 contingency:** If a *later separately authorized* experiment needs actual travel to Kreet or Decaran VII-b, use Save52, not Save2. Before such live use, seek separate authority to copy and verify Save52 under `.local-work/release-assets/`, with the same protected-original/backup/retained-copy discipline used for Save2. Do not copy or touch Save52 in this continuation; title/menu state checks do not require visiting sampled planets.

## 6. Disposable adversarial matrix and lead-exhaustion

Use real external reads against **owned disposable native Windows processes** for successful cases and adverse cases; include both the native structural decoder and the full retail-like admission/controller path. At minimum test:

1. Admitted populated, admitted eligible zero and mixed/indeterminate tuples with the exact sample-control dependencies; wrong effective input blocks positive *and* qualified zero.
2. Unique correct process versus stale PID/epoch, multiple plausible instances, wrong executable hash, wrong Steam/session attribution and wrong mapped backing; rights-denied and query-only handles; no escalation.
3. Registry and FormID decoys, malformed tree and packed directories (including the prior **forged block minimum** counterexample), partial coverage, duplicates and wrong owner; zero must never follow failed coverage.
4. Paired stable reads, between-read mutation, mid-read insertion, stable intermediate clear, ABA and end-of-window identity drift; retain the known limitations of double collection.
5. Operator marker token/epoch/ordering mismatch, stale or duplicate markers, title/menu/gameplay labels on one binary, failed or partial journal, seal tampering and independent replay refusal.
6. A reproducible proof of **zero target-write/debug/suspend capabilities**, and negative tests showing the adapter refuses any unqualified retail-like profile or impossible source attestation.

Preserve the 49 SRR-013 disposable regression cases and add proportionate focused controls; do not substitute fake record feeds for the actual external acquisition path. Independent reviewer must construct at least one plausible counterexample and verify any rework on the final candidate.

Retain the **lead-exhaustion rule**: pursue every credible, actionable lead relevant to the *retail-admission and effective-input contract* to resolved, exhausted or specifically blocked; explain the exact block and needed discriminator. Avoid open-ended engine reverse engineering or debugger work. Up to **two concurrent Codex sub-agents** are authorized; the parent integrates findings and maintains one lead register and evidence set.

## 7. Deliverables and acceptance criteria

Deliver tracked, sanitized documentation, a narrowly scoped reader/adapter change, tests and a proposed title-card run card. Retain build products and raw receipts in ignored local custody.

- **RA-01 — Scope and preservation:** SRR-012/013 scientific semantics, samples, reviewer history and existing regression fixtures preserved; no live game, saves, debugger or Ghidra modifications; no staging/commit/push.
- **RA-02 — Retail identity:** Authenticated, unique process/epoch and pinned mapped image admission implemented and falsifiable in disposable trials, with any retail-only witness requirements clearly pending.
- **RA-03 — Effective inputs:** Exact provenance-based retail-input applicability contract, independent verification/refusals and no synthetic-profile substitution; unsupported real-world conditions explicitly blocked.
- **RA-04 — Native measurement:** Existing decoder and paired-read constraints exercised end-to-end through new admission. Wrong structures, missing/duplicate records and short reads fail closed.
- **RA-05 — Operator binding:** All three labels work on one candidate; valid, stale, wrong-epoch and duplicated markers behave as specified; only title is proposed live.
- **RA-06 — No intervention:** Verified read/query-only capabilities, no debugger/thread-context/target writes/elevation, bounded private evidence and deterministic sealed replay.
- **RA-07 — Qualification and lead audit:** Existing and new real-process disposable cases pass, historical fixes retained, all material leads disposed or specifically blocked; exact reproducible frozen implementation and hashes.
- **RA-08 — Independent handoff:** Independent challenge of scientific false positives/zeros, identity attribution, effective inputs, race cases, privacy and actual patch; byte-exact forward/reverse replay and a clear permission boundary.

The dossier must prominently differentiate **fully offline-qualified gates**, **conditional runtime gates**, and **unresolved blocks**. The final readiness label is:

- **`READY FOR RETAIL TITLE-CARD AUTHORIZATION`** only if the code can be operated under a separately authorized session *without further unreviewed source changes*, and all remaining checks are explicit runtime admission checks with established verification mechanisms; or
- **`RETAIL READINESS BLOCKED — <specific reason>`** if an indispensable identity, effective-input or acquisition requirement is still unsupported by a qualified method.

The next live session, if later approved, is one read-only observation at the responsive title card, with separately reviewed exact code/source identities, process rights, private custody and operator instructions. **This brief grants no such approval.**

**Commit policy:** Leave all source and documents **unstaged, uncommitted and unpushed** for maintainer review. Return the final task-only patch, frozen source/build manifest, qualification receipts, independent review and disposition. Do not interpret the fixture-only qualification as proof of any actual retail resource-state observation.
