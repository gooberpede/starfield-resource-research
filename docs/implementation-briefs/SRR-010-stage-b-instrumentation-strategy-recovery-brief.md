# SRR-010 — Stage B instrumentation-strategy recovery

**Implementation brief for Codex · Offline continuation · 15 November 2026**

**Disposition at entry:** The two authorized retail Save2 loads are complete historical observations. Both ended before player control with process exit `0x80000004` and **`INSTRUMENTATION_INCOMPLETE`** for the load. The second attempt genuinely deferred running-thread censuses during loading, yet failed in the same broad way. No causal explanation of the exits is established. **Neither attempt authorizes another launch.** Keep SRR-010 open, with all changes unstaged and uncommitted.

## 1. Controlling question and priorities

**What is the smallest evidence-supported change to instrumentation or debug-event service that offers a credible prospect of observing a *completed* Save2 load while retaining scientifically meaningful detection and qualification of the retail resource-allocation path?**

The deliverable is a **working candidate for review**, not a definitive forensic diagnosis. Prefer demonstrated, relevant live prior art and a focused correction or adaptation over another broad debugger investigation. Stop spending time on attribution when a viable, testable route emerges. However, **stability alone is not success**: an observer that cannot detect or discriminate the machinery we seek has not met the objective.

Distinguish three separate standards:

1. **Engineering:** reproduces the relevant debugger and instrumentation behavior in adverse disposable tests.
2. **Scientific sensitivity:** can positively establish focal invocation and allocator arrival under the agreed predicates, preserve cross-phase joins and durable positives, and identify when a quiet interval is *not* qualified.
3. **Retail applicability:** survival and capture during the actual Save2 load, which remains unproved until separately authorized live observation.

Do not claim the third standard from the first two. No obligation to explain the original `0x80000004` exits definitively.

## 2. Starting evidence, constraints and prior art

The original assignment started from the uncommitted Phase 1 observer,
both independently reviewed live attempts and the offline recovery
continuation. The second live attempt's dossier patch followed the
original Stage B and recovery patches, with 12 task-file identities in
the accumulated handoff. The [Stage B dossier](../SRR-010-stage-b-save-load-observation.md)
records the historical evidence identities and verification limits.

The original comparison called for the following primary evidence:

- **SRR-010, attempts 1 and 2:** the native event/prefix records, readbacks, thread birth/exit service, exception dispositions, load marker-to-exit window, and exact target exit (`0x80000004`). Both have qualified pre-load negatives but incomplete save-load evidence; the second has eight deferred idle checks and one event-held check during load. The load-marker-to-exit interval includes operator time and is **not** a measured save-load execution duration. Neither has a corresponding delivered single-step exception or faulting instruction.
- **`starfield-reference-handles`:** the successful native Win32 startup hardware smoke and any separately retained game-transition attempt. A startup smoke is not proof of save-load stability. Compare exact source, event ownership, RF/TF/DR6 rules, thread population and survival.
- **`starfield-outpost-research`:** EXP0002A live no-DR and armed-save controls, including unsuccessful ones; and especially the successful **D5B** live Save52-load/Build-Mode observer, its actual source revision, raw native journal and independent qualification. The reported D5B success includes 15,119 acknowledged/RF-verified resumes but involved different observed sites, load and workload. Identify transferable **mechanisms**, not assumed equivalence.
- **SRR-009:** a valid 84.281-second four-site post-title negative, successful STOP seal, normal target exit and subsequent observer-only administrative closure. This establishes instrumentation viability in the earlier window, not during save loading.

Pin each inspected external commit, source/blob and relevant raw-evidence identity. Separate demonstrated live behavior, disposable evidence, hypothesis and unresolved differences. Keep comparative findings concise in the existing **results-first SRR-010 dossier**; put verbose comparison and trial receipts in ignored local evidence. Do not create a sprawling new research-document hierarchy.

## 3. Select the least disruptive viable strategy

Compare **no more than a small, evidence-driven shortlist** before implementation, including:

- **Event-service adaptation** from a successful relevant live observer (especially D5B): e.g. debugging-event ownership, delivery/continuation, thread lifecycle, RF/DR state and scheduling during loading. Explicitly identify code paths that SRR-010 already shares and those that differ.
- **A narrower breakpoint footprint during loading**, *only if* the remaining observation can still answer a valuable bounded question and the reduction has a credible operational advantage. Consider which sites/threads are essential for detecting the focal path, not arbitrary reductions in monitoring cost.
- **Other small changes** only when a concrete comparison or targeted test supports them. Do not invent a large backend replacement or switch to software breakpoints, SFSE hooks or an entirely new instrument merely to try something different.

Prefer preserving the existing **four simultaneous SRR-005 sites** (`0x9518FD`, `0x5932EF`, `0x77C470`, `0x779760`), original mapped-code and per-thread identity checks, and the native correlation contract. A footprint reduction must be justified against the explicit scientific matrix below and must never be presented as equivalent four-site coverage.

Before committing to a design, write a brief choice record within the dossier or private investigation notes: candidate mechanism, positive prior-art evidence, expected benefit, scientific loss (if any), failure/counterexample, and reason for selection. **If no credible useful candidate emerges, return `BLOCKED / NO VIABLE SENSITIVITY-PRESERVING CHANGE` rather than weakening instrumentation to manufacture progress.** For a major architectural replacement, stop at a reviewed proposal and obtain maintainer approval before implementation.

## 4. Non-negotiable scientific sensitivity contract

For the proposed instrument, explicitly construct and test a claim-capability matrix:

| Claim / capability | Required evidence or explicit limitation |
| --- | --- |
| Detect entry to the resource machinery | An eligible physical execution at a relevant pinned site must remain observable on all threads claimed covered; demonstrate with a positive test, not just a quiet load. |
| `OBSERVED_INVOKED` | Preserve a durable, qualified focal iterator-to-callback join, or explicitly label the claim **unavailable** if a proposed narrower design cannot establish it. |
| `OBSERVED_REACHED_ALLOCATOR` | Preserve the actual orchestrator entry and verified same-invocation ancestry, or explicitly label the claim **unavailable**. Mere raw address hits cannot replace correlation. |
| `NOT_OBSERVED` | Permit only for a bounded interval with demonstrably sufficient coverage **for the named claim**, valid boundaries, reconciled event service, appropriate thread/register checks, and a verified scientific STOP. No hit in an uncovered or incomplete interval is not a negative. |
| Cross-phase execution | Preserve valid pending frames and joins through `LOAD_BEGIN`, `PLAYER_CONTROL` and optional Lodge boundaries; carry unresolved earlier chains into aggregate qualification. |
| Evidence integrity | Preserve raw native records, sequence/epoch, RF/DR6 ownership, continuation, durable positives and STOP-prefix/sidecar validation; fail closed for incomplete instrumentation or lost evidence. |

Challenge at least one **realistic positive on every remaining asserted detection path**, including under concurrent thread activity during a simulated load, and one false-quiet counterexample. If a suggested reduced-site approach cannot preserve both focal invocation and allocator-arrival claims, flag that as a **material scientific scope change** and do **not** silently select it. Submit it for approval rather than implementing or using it as an equivalent Stage B observer.

Sampled register checks have an explicit temporal limitation. Avoid making unsupported universal coverage claims; preserve the distinction between event-driven/endpoint checking and continuous thread-state observation.

## 5. Implementation boundaries and offline qualification

Make the **smallest coherent changes** to the existing tracked SRR-010 observer, marker protocol, fixtures, run card and tests needed by the selected mechanism. Avoid ancillary cleanup or a general refactor. Preserve the exact retail identity, Steam origin/drift rules, existing-debugger and foreign-DR safety checks, non-killing policy, operator UI authority, protected-save preflight, and 40,000,000,000 caller-available-byte C:/D: floor plus reserve.

Test changed mechanisms against **disposable targets only**. The qualification must meaningfully exercise:

- Busy multi-threaded load with hardware hits, new-thread births/exits, competing debug events and module transitions; recorded owned DR state, RF/TF disposition, successful continuation and durable focal/allocator positives.
- Quiet load with sufficient checks to support a precisely **qualified** zero (or an incomplete verdict where the proposed narrower observer cannot justify zero).
- Cross-marker callback/allocator join and unresolved-chain negative control.
- Actual breakpoint-slot displacement or a comparable credible coverage breach; affected window becomes incomplete without erasing an earlier valid positive.
- Target crash/early exit, journal/STOP-sidecar failure, and observable separation of science, game exit and observer retirement.
- Relevant existing SRR-006/009/010 regression suites, re-running broader suites when shared behavior changes. Fixture watchdogs may be tailored to fixture workloads but must not become live scientific deadlines.

Build and pin the *actual* chosen executable with reproducible source/toolchain identities. Record failures and partial fixture runs; a later green run does not erase them. The independent challenger must inspect primary evidence and attempt adversarial counterexamples, particularly **false negatives caused by reduced instrumentation** or missed exception/thread ownership. A passing disposable suite does not authorize retail use.

## 6. Proposed Stage B run card and operational simplicity

Prepare an updated **proposed** run card for later maintainer review, retaining the existing one-session objective: ordinary interactive-account Steam launch; verified post-title attach and arm; `LOAD_BEGIN_DURABLE` before the maintainer selects the familiar Save2; continue through confirmed player control and a meaningful post-load interval; optional one-step Lodge crossing only if practical and not demanding significant retooling. The save directories stay populated; do not relocate Save2 or impose another elaborate selection contract.

Prioritize the *capture*, not perfection of cleanup. STOP and scientific evidence sealing precede normal Quit where possible. Retain the independent exact-process exit witness. After confirmed target exit and evidence preservation, an exactly reauthenticated orphan observer may be administratively terminated under the separately approved run policy. This does not authorize killing a live game or detaching an active debugger arbitrarily.

The candidate run card must state the true observation coverage and any relaxed assumption. Do not pre-authorize a second save load, alternative sample, new game launch or unexpected intervention. Preserve the two failed save-load attempts as history subordinate to the still-open scientific question.

## 7. Review gate, deliverables and authority

Return:

1. **Existing SRR-010 dossier updated**, led by current established findings and their limits, with a concise prior-art comparison, selected approach, claim-capability matrix, changed method and proposed exact Stage B run card. Keep earlier histories intact but subordinate.
2. **Frozen reviewed source/binary and manifests**, task-only Git-native patch with all new files and exact inputs/outputs; preserve initial HEAD/index/worktree and earlier evidence identities.
3. **Offline qualification report**, selected native fixture journals and verified seals, adverse-case results, evidence/custody and publication-dependency checks; private native logs remain in `.local-work/`.
4. **Independent challenger verdict** assessing the eight acceptance criteria below, the scientific sensitivity contract, and isolated byte-for-byte patch replay. Correct any REWORK before returning.
5. **A short, exact live authorization proposal** for the maintainer if ready; identify implementation hashes, required scope, altered scientific capabilities, and unresolved risks.

**Acceptance criteria:** AC1 historical preservation and authority; AC2 accurate primary-evidence prior-art comparison; AC3 pragmatic, justified choice without open-ended attribution; AC4 maintained scientific sensitivity and honest claim scope; AC5 targeted implementation with unchanged critical safety/identity controls; AC6 adverse disposable tests and retained failures; AC7 source/dependency/provenance and clean isolated reproduction; AC8 independent challenge, frozen handoff and byte-for-byte patch replay.

**Permitted now:** repository edits within this continuation, local offline analysis, builds and own disposable fixture processes, independent offline challenge.

**Not permitted:** live Steam/Starfield launch or process probing, actual game debugger attachment, Save2 loading, in-game UI automation, gameplay/Lodge crossing, new proprietary distribution, Ghidra mutation, forced termination of any live game, commit, push or release. No spontaneous expansion to a new backend. Retain the existing project and original research evidence.

**Stop at `READY FOR STAGE B RE-AUTHORIZATION`** only when the candidate is independently reviewed and retains scientifically useful sensitivity. Otherwise return a qualified `BLOCKED` or reviewed major-change proposal. Another live Stage B attempt requires a **new explicit written authorization** against the exact candidate. Leave changes unstaged, uncommitted and unpushed.
