# SRR-017 — Retail Readiness Completion Continuation

**Codex implementation, qualification and independent-audit brief — OFFLINE ONLY**  
**Status:** SRR-017 owned-fixture implementation accepted; retail-ready milestone **not yet achieved**. No live authorization is granted.

## 1. Purpose and starting evidence

Complete the *existing, uncommitted* SRR-017 implementation so that the maintainer can assess a single, frozen candidate for **one separately authorized retail Starfield title-card extraction**. Do not initiate that extraction under this brief.

The eventual live deliverable is a **complete, usable, identity-resolved Planet (PNDT) → Biome (BIOM) → seven resource-slot dataset** from all qualifying `CTPerBiomeData` edges root-reachable in the authenticated, published `BSComponentDB2::DB +0x300` index. Include all-zero rows and zero slots. Preserve the exact raw runtime IDs and fields as well as the ESM-derived identities so that the dataset can later be compared offline against the reproducer **without another live run merely to obtain omitted identity or allocation fields**. This is **not** a count-only or runtime-ID-only census. The initial live run does **not** need to prove oracle equality or total expected population from authored inputs; those conclusions have their own later evidence requirements.

Preserve the accepted SRR-016 baseline and the substantive results of the current SRR-017 uncommitted patch. Work from the actual current worktree, tracking its original HEAD, index, uncommitted files and source hashes. Consult `docs/SRR-016-*`, `docs/SRR-017-*`, `docs/SRR-013-structural-title-run-card.md`, `docs/SRR-013-retail-title-paired-structural-observation.md`, `docs/research-workflow.md`, and the pre-existing SRR-017 brief. Confirm exact current filenames and source identities rather than assuming historic snapshots remain current.

**Previous independent-review limitation:** The prior `final-challenge.json` is a *summary receipt*, not a standalone independent review. It reports `OWNED_QUALIFICATION_ACCEPTED_RETAIL_REQUEST_BLOCKED`, 20 checked files, seven legacy counterexamples, three paired namespace cases, exact u64 roundtrip, and blocker categories of (i) exact retail invocation, (ii) epoch-bound effective loaded paths and digests, and (iii) qualified total retail work envelope. It records no retail access and manifest SHA-256 `01fb54136f21e907a3dd760cabee5da10fcf66789954c87fbc2dc41bd0c61a8f`. Do **not** portray that receipt or a dossier review-status paragraph as a complete standalone independent challenge. Retain its historical verdict; generate a proper final report for this continuation.

Pinned retail target: `Starfield.exe` **1.16.244.0**, SHA-256 `7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28`. The relevant ESMs are principally `Starfield.esm` and `ShatteredSpace.esm`; the native fields already studied contain FormIDs, not evidence of some alternative pointer or reference-handle encoding.

## 2. Required scope and work allocation

At most **two concurrent sub-agents**, with parent reconciliation and an independent challenger. Suggested parallel division:

- **A — Retail command/admission and combined acquisition:** Build the exact retail-facing command, one-use approval gate, Steam/title epoch binding, freeze and replay mechanics, finite population-scale work limits, cancellation, failure handling, and normal closeout protocol. Test exclusively with owned disposable processes and simulated retail admissions.
- **B — Effective loaded-plugin identity and usable export:** Prove the simplest sufficient per-epoch runtime FormID → defining ESM/local record ID correspondence, independently check full/medium/small namespace cases where genuinely applicable, separate source identity from override/provenance attribution, and challenge the complete normalized export against independent fixtures.

Integrate the two paths and subject the **final combined source** to an independent review. Retain evidence-grounded lead exhaustion: for each material native or engineering lead, document caller/guard or other direct evidence, attempted tests/searches, conclusion and a specifically explained blocker if unresolved. Do not pursue unsupported alternatives solely because they are logically possible. No broad unrelated research.

## 3. Close the three retail-readiness blockers

### A. Implement the **exact** retail-facing command

The current `tools/srr017/title.py` and `tools/srr017/export.py` have deliberate `OWNED_DISPOSABLE` restrictions. Retain their safety purpose, but supply and qualify the **actual reviewed retail execution path** and source profile that a later written authorization could invoke. This is an implementation requirement, not permission to run it.

- Reuse the SRR-013 Steam/process admission, mapped-image/creation-epoch verification, responsive title-card confirmation, private receipt sealing, independently witnessed process retirement and preflight/postflight procedures. Reuse SRR-016 full rooted traversal, native type/FormID validation, paired reads and source-independent export. Avoid a new debugger or generic game harness.
- Require a **separate real maintainer written authorization** bound to the frozen command/source hash, unique private canonical custody directory, prescribed title-only scope and single-use claim; simulated approval is allowed only for disposable tests. A valid source hash, local configuration, or this brief alone must never unlock real retail access.
- The precise invocation, arguments, source manifest, approved work envelope, permission/identity checks and fail-closed refusals must be executable in the owned profile. Verify denial without authorization **before** any retail process handle or observation is attempted. The proposed run card must identify the exact command, not a placeholder.
- No save load, main-menu action, travel, runtime injection, process write, debugger attachment, thread suspension, elevation or automatic retry. Operator performs game UI interactions and normal Quit **only in a later separately authorized run**.

### B. Establish adequate **epoch-bound ESM identity evidence**

Start with the evidenced expectation that PNDT, BIOM, RSGD and resource FormIDs correspond to their source records in `Starfield.esm` and `ShatteredSpace.esm` (and any actually relevant additional loaded plugin). Validate the native full/medium/small index assignments only to the degree those namespaces occur in the inspected set. Never treat a pointer address or Bethesda `REFR` form as an alternative identity without affirmative evidence.

- Independently identify the loaded native plugin namespace, source names/paths, file identities and applicable hashed on-disk ESM bytes. Establish the relationship between that native loaded-file table **in the authenticated epoch** and the files used to normalize IDs. Check native loaded names/index and independently known PNDT/BIOM/resource records from both ESMs where applicable, including nonzero plugin indices. Preserve both raw runtime FormIDs and defining-plugin/local-ID identities.
- Investigate the **least complicated sufficient** process-to-file evidence: native loaded-path/namespace witness plus pinned file digests and appropriate pre/post stability checks may suffice. Do not impose a more intrusive live file-handle-to-content attestation unless a *specific* unresolved ambiguity actually requires it. If the simple proof is insufficient, demonstrate the counterexample and define the minimal extra witness.
- **Separate identity from winning-record provenance.** The ability to identify a record's defining plugin/local ID must not be rejected just because a filtered or incomplete source-history vector fails to establish every override contributor. Investigate `owned_source_vector_disagreement` and equivalent guards in `tools/srr017/export.py`; test missing, filtered, incomplete and contradictory vectors. Retain genuine identity/namespace conflicts as qualification failures, and record unresolved effective override/winning-content attribution **separately**. Avoid silently weakening a check that actually catches misidentified forms.
- If meaningful canonical identity remains unresolved, retain the complete raw evidence and explicitly report the defect. **Do not** propose authorizing a merely count-only or unjoinable export as fulfillment of this task.

### C. Qualify **combined** retail-scale work bounds

Calculate one auditable finite work envelope for the complete **two-collection** retail-facing path: Steam and image admission, native plugin namespace and file identity, tree windows/depth/blocks/descriptors, native FormID-map capacity/chain traversal, typed PNDT/BIOM/RSGD/resource checks, witness rereads, identity brackets, export, receipt/seal and final closeout. Reconcile backend query/read/byte caps with higher-level work caps, evidence file limits, available C:/D: reserves and measured SRR-016/SRR-017 owned fixtures. Reflect the native FormID-map starting capacity `0x40000` and growth, rather than incorrectly reusing its earlier 16,384-entry fixture cap.

- Use realistic measured work and justified margin; demonstrate oversized, sparse-map, region-boundary, chain/pathology, missing-plugin and output-limit refusals on owned processes.
- **No arbitrary wall-clock acquisition deadline.** Preserve finite per-operation/work bounds, cooperative cancellation, explicit reason codes and truthful partial evidence if a bound is reached. A failed/incomplete first or second collection must not trigger a replacement pair, budget increase or fresh launch automatically.
- Verify pairwise graph, typed-input and exact seven-word agreement independently; a seven-zero target is a real present record. The observable claim remains a qualified pair of root-reachable contents at the held checkpoint—not atomicity, absence of mutation/ABA, all queued work finished, or a full-galaxy oracle match.

## 4. Mandatory offline qualification

Run the existing SRR-013/SRR-016/SRR-017 disposable tests and the unchanged sibling reproducer checks where available. Do not silently replace or alter their historical results. Recheck the population-scale fixtures (**3,210** and **4,096** typed targets) and preserve every row, seven slots, zeros, raw IDs and normalized source identity through sealed journal → replay → final Planet/Biome/Resource export → SRR-016 comparator input. A complete export must be derivable from captured evidence, not fabricated from the reproducer prediction.

Add independent counterexamples for the newly combined retail path: unapproved retail command refusal, forged/stale/single-use approval, ambiguous Steam epoch, executable/mapped-image drift, namespace index collision or reassignment, swapped/changed ESM bytes, correct defining identity but filtered source-history vector, true contradictory origin identity, missing relevant plugin, cross-region native map reads, volume-budget exhaustion, evidence truncation, process exit and cancellation. Test admission and preservation flow against owned mocks/fixtures only. **No retail test process, no live game, no saves.** Historical retail journals that are inaccessible must remain historical and may not be falsely reported as replayed.

## 5. Standalone independent review — mandatory

Create a substantive **separate Markdown review report** at:

`.local-work/independent-review/SRR-017-retail-readiness/challenge.md`

Use this **singular** `independent-review` directory, not `independent-reviews`. The report must exist as its own file even though the substantive findings are also summarized in the tracked SRR-017 dossier. A compact JSON verdict, test count, checklist with no reasoning, or dossier paragraph is **not** an adequate substitute.

The challenger must independently inspect the **final combined source and exact proposed retail command**, attempt to falsify identity attribution, source-history rules, work limits and authorization barriers, construct or run at least some independently prepared counterexamples, verify source/tests/manifest identities and task-only patch forward/reverse replay, and report:

1. Scope, exact reviewed files/hashes, methods and evidence personally examined;
2. Counterexamples attempted (including failed challenges), observations, any defects and corrections with retests;
3. Separate judgments for **retail source/admission readiness**, **identity-resolved export**, **combined budget**, **operational safety/preservation**, and **scientific result boundaries**;
4. Explicit residual risks and precisely justified remaining blockers (if any), with a final `READY_TO_REQUEST_SINGLE_LIVE_AUTHORIZATION` or `BLOCKED` disposition.

Include a short self-contained review-status summary in the tracked dossier **without linking to or relying on** the private review artifact. Other tracked documents must likewise be portable, with no dependency/link to pre-existing `.local-work/` files. Working paths may be documented for generating fresh scratch outputs or describing custody policy only.

## 6. Deliverables and completion gate

Provide the reviewed task-only implementation patch, file inventory, source and execution manifests, hashes, owned qualification receipts/results, documented namespace/identity proof, budget derivation, sealed-export round-trip proof, updated dossier and **one exact proposed retail run card explicitly marked `NOT AUTHORIZED`**. Preserve historical evidence classifications. The run card must specify one Steam launch, one confirmed responsive title checkpoint, one read-only pair, normal Quit, independent exit witness, protection of the **98 Documents + 95 Steam remote** original/backup save pairs and two designated saves, disabled Cloud/overlays and relevant environment controls, required disk reserves, source/custody binding, no travel/save loading, failure stops and postflight.

Report a final two-state release decision: `READY_TO_REQUEST_SINGLE_LIVE_AUTHORIZATION` only if the actual retail command, epoch-bound identity resolution and combined work envelope are *all* independently qualified offline; otherwise `BLOCKED`, with concrete missing evidence and no suggestion that owned-only testing is a retail observation. **Do not downgrade the objective to a structural-only census.** The oracle's complete expected-population and exact-value qualification can follow the live extraction, but the output must contain the identities and fields necessary for that comparison.

**Hard boundary:** This continuation authorizes offline static inspection, code changes, disposable/owned fixture process tests and independent review only. It authorizes **no** retail launch, game process access, live measurement, save-file access, debugger operation, staging, commit, push or publication. Finish with the candidate and review for maintainer judgment. All modifications remain **unstaged, uncommitted and unpushed** until separately approved.
