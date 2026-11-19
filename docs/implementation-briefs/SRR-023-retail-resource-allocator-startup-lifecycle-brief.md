# SRR-023 — Retail Resource Allocator Startup Lifecycle

**Implementation brief for Codex**  
**Project:** `D:\Projects\starfield-resource-research` (`gooberpede/starfield-resource-research`)  
**Mode:** Offline, read-only native investigation and documentation  
**Status:** Authorized for implementation; changes subject to subsequent review

## Objective

Reconstruct and independently challenge the retail resource allocator's **startup invocation, typed-input readiness, and retained-write lifecycle** as far as offline evidence permits. Keep these questions separate:

- **SRR014-A8:** Which startup invocation(s), if any, produce the retained `BSGalaxy::CTPerBiomeData` contents, and when/how often? In particular, determine the supported call/identity relationship to the retained write at `0x1407779FC`.
- **SRR014-A9:** At the relevant startup sweep, which typed input commands have completed and become available? Determine the precise scheduling and completion contract around host `+0x40`, including direct versus deferred paths and outstanding-work handling.

Deliver a **falsifiable execution model**: an ordered, evidence-graded account of relevant states, callbacks, guards, and writes, with explicit alternative explanations and the smallest discriminating observation for any remaining runtime-dependent ambiguity. Do not equate plausible static callability with proof of execution in the historical retail title epoch.

## Baseline and research constraints

Start from the **current committed authoritative documentation** and the existing repository tooling, especially:

- `docs/retail-execution-lifecycle.md` (principal destination for results)
- `docs/component-database.md`, `docs/function-register.md`, `docs/structure-register.md`
- `docs/hypotheses.md` (the *single* authoritative lead register)
- `docs/PROVENANCE.md`, `docs/research-workflow.md`, `docs/allocation-validation.md`

Retain the independently established scope of previous results: SRR-017's title-state collection, SRR-018's exact **diagnostic** agreement across 22,470 matched seven-slot lanes, and the distinction between observed retained rows and a strictly qualified oracle. Do not reinterpret those agreements as identifying their generating invocation or proving complete effective input readiness. The strict `ORACLE-INPUTS` lead may be informed by SRR-023 but is **not** an acceptance target.

Use the pinned **retail** `Starfield.exe` version `1.16.244.0`, SHA-256:

`7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28`

Preferred image base: `0x140000000`. Verify the local input identity before trusting any native addresses. Do not conflate this image with `CreationKit.exe`; identify all evidence by executable and provenance. Existing documented function locators are *starting points*, not proof of a particular execution sequence.

**Out of scope:** launching/attaching to Starfield or Creation Kit; live observation or instrumentation; editing saves or game files; modifying the resource reproducer or its validated output; re-running a galaxy-wide generation comparison; constructing an exhaustive strict-oracle input ledger; speculative or untargeted review of other component types; implementation of any live observer. No arbitrary function-count or time budget should replace an evidence-based stop condition.

## Workstreams and concurrency

Codex may use **up to three concurrent sub-agents**, as appropriate. Integrate their findings before commissioning a **separate independent challenger**; the challenger is not one of the three concurrent investigators.

### A — Allocator invocation and retained-write attribution

Trace the bounded startup path and calls/guards leading toward allocation, late sweep, and the retained `CTPerBiomeData` write at `0x1407779FC`. Establish, where the static image permits:

- The relevant entry points, direct/indirect callers, dispatch objects, queue callbacks, owner/body/biome identity propagation and invocation conditions.
- Whether the implementation **permits** multiple invocations, bypass, reset, reuse, initialization of existing state, or regeneration; distinguish these from demonstrated startup execution.
- The key and target identity at the write and any earlier/later store operations that could alter the retained result.
- Whether the previously identified late return around `0x14094EF5C` can be connected to a specific write, and which link still requires an execution-qualified witness.

Do not assume a single sweep or that one candidate store accounts for every retained row. A negative finding at one specific store must not be generalized to all possible writers.

### B — Typed-input scheduling, publication and completion

Investigate the existing command submission and scheduling evidence, concentrating on host `+0x40` and the conditions at sweep entry:

- The command producer → submission → direct/deferred execution → publication/read path, including relevant receivers, queue/service identity and command ownership.
- How outstanding work is counted or signaled; whether the sweep waits, drains, tests readiness, or may operate on partial inputs.
- Which operations actually synchronize with the sweep, versus nearby resets, drains or completion callbacks on **different** receivers.
- The exact static predicates needed to say a particular typed input was visible at sweep entry, and the conditions that cannot be settled without observing a run.

Do not infer command readiness from agreement between modeled and retained resource allocations.

### C — Independent lifecycle reconciliation

Build an independent control-flow account and challenge both analyses. Seek concrete counterpaths: different invocation ancestry, deferred command completion, repeated sweeps, missing owner/biome identity, or alternate writes. Classify each claim as **proven retail static**, **strongly inferred**, **runtime-conditional**, or **unresolved**. Prioritize disagreements that materially affect the A8/A9 conclusions rather than broad adjacent exploration.

## Required investigation method

1. **Baseline:** Record starting HEAD and clean/dirty working-tree status; inspect the current lead text and existing native evidence before adding new claims. Check executable hash and base assumption.
2. **Bounded static traces:** For each consequential connection, retain the concrete caller/callee or indirect-dispatch proof, argument/receiver/identity flow, branch condition, and source address. Distinguish direct calls, likely dispatches and unjoined callbacks. Use the repository's existing offline disassembly workflow; do not introduce a new analysis framework unless essential.
3. **Cross-check:** Reconcile both workstreams into an ordered sequence with alternative routes. Explicitly state what would be different if input publication occurred after sweep entry, or if retained rows came from another invocation.
4. **Decision:** If static analysis resolves a question, document exactly why. If it cannot, state the **single missing join or epoch-sensitive fact** for each remaining branch and an observational discriminator sufficiently specific to guide a later observer.
5. **Challenge:** Have a separate reviewer test the important native interpretations, counterexamples, alternative lifecycles, evidence labels and final diff. Resolve substantiated objections before reporting completion.

Avoid circular proof: observed `CTPerBiomeData` contents must not be used to manufacture the effective input operation order, and a title-card database snapshot must not be labeled a witnessed allocator return.

## Deliverables

### 1. Authoritative research updates

Update `docs/retail-execution-lifecycle.md` as the main durable technical account. Update `docs/hypotheses.md` **in place** for A8/A9 disposition and any precise remaining test. Amend `docs/component-database.md`, `docs/function-register.md`, `docs/structure-register.md` and `docs/PROVENANCE.md` **only if** new evidence makes an amendment useful. Do not create a numbered research dossier, a new lead register, or broad duplicated narrative.

The lifecycle account should make the following immediately auditable:

- **Sequence:** stage, entry/guard, receiver/owner identity, resulting state and next transition.
- **A8:** known candidate invocation(s), write path, identity continuity, and the boundary between proven control flow and unobserved historical execution.
- **A9:** direct/deferred typed command routes, readiness/ordering contracts, and any missing sweep-entry completion witness.
- **Alternatives:** a small table of concrete rival explanations and what would falsify each.
- **Disposition:** resolved, partly resolved or observation-required for each lead separately; implications for `ORACLE-INPUTS` without trying to close that lead.

### 2. Private evidence and independent review

Retain bounded disassembly captures, working notes, counterexamples and reviewer receipt under existing `.local-work/codex/` and `.local-work/independent-review/` conventions. Preserve any useful byte/offset verification and trace commands. Do not put large generated native listings into tracked documentation.

### 3. Conditional live-observer specification — not implementation

Only if an A8/A9 ambiguity genuinely depends on execution, document the *minimal* hypothetical observer: exact event/function boundary, receiver/key/body identity fields, sequencing/epoch signals, expected positive/negative observations, and guards against false attribution. Place this within the existing lifecycle/lead documentation or private notes, whichever best avoids duplication. **No plugin, debugger script, injected hook, or game run is authorized.**

### 4. Tests and closure report

Run applicable existing checks for any edited tooling or documents. If no tool changes are needed, do not add artificial tests. Include a task-only diff, precise changed-path inventory, starting/ending HEAD and working-tree state, independent reviewer findings and any remaining limitations. Leave changes **unstaged, uncommitted and unpushed**. The user will review the diff before committing.

## Acceptance criteria

SRR-023 is ready for review when:

1. A8 and A9 have **distinct**, concrete and independently challenged static accounts rather than a single undifferentiated startup story.
2. Each proposed invocation, command-completion dependency and retained write is supported by addresses, branch/receiver evidence and correctly qualified identity flow.
3. Repeated/conditional execution and alternative routes are tested where motivated by code, without claiming exhaustiveness where none is established.
4. The lifecycle report separates what the binary **can do** from what the historical startup **did**; no claim silently upgrades diagnostic agreement to strict native oracle proof.
5. Any surviving uncertainty is reduced to an actionable, minimal observation rather than a vague request for future tracing.
6. The documentation uses the established authoritative files and privacy conventions; no game/save/reproducer changes or live instrumentation have occurred.
7. A separate independent challenger has checked and signed off the important findings and final patch, with objections addressed or expressly retained.

**Success does not require proving historical execution offline.** A rigorously bounded, falsifiable model with a clearly justified runtime-only boundary is an acceptable scientific result.
