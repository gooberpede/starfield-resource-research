# SRR-024 — PlayerKnowledge Visit-Bit Lifecycle

**Implementation / research brief for Codex**  
**Project:** `starfield-resource-research`  
**Mode:** Offline, read-only native investigation; documentation changes only  
**Status:** Proposed; implement only this authorized scope  
**Parallelism:** Up to **three concurrent sub-agents**, followed by a **separate independent challenger** after integration

## Objective

Determine as precisely as offline evidence permits **when, under which conditions, and for which celestial-body identity** retail Starfield sets **bit 1 (visited)** in `BSGalaxy::PlayerKnowledge`. Distinguish a first `0 → 1` transition from an idempotent set, pre-existing or initialized state, and save restoration. Reconcile the resulting model with the established atmospheric-resource credit consumer and existing Save2 evidence. Where actual execution timing cannot be proven statically, produce **specific, falsifiable alternatives and minimal observation points**, not an asserted historical timeline.

This is a focused lifecycle investigation, not another general survey of the resource allocator or Starfield exploration system.

## Authoritative context and pinned evidence

Use the existing consolidated research documents as the authoritative starting point, principally:

- `docs/component-database.md` — `PlayerKnowledge` representation and operations, resource snapshot and survey credit, three display paths, saved-state findings.
- `docs/function-register.md`, `docs/structure-register.md` — native locators and established field contracts.
- `docs/hypotheses.md` — sole authoritative lead register, especially `SURVEY-UI`.
- `docs/retail-execution-lifecycle.md`, `docs/PROVENANCE.md` — native qualification and evidence identities.
- `tools/srr022/` — read-only Save2/Save52 decoder; existing private comparison/evidence, if needed.
- Private SRR-021 original screenshot corpus, notably Volii Alpha `S21-07`, `S21-08`, `S21-09` and their manifest.

**Retail executable:** `Starfield.exe` version **1.16.244.0**, SHA-256 `7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28`, preferred image base `0x140000000`. Verify executable identity before accepting native addresses. Use the project's existing offline disassembly tooling; do not rely on inferred symbol names as proof of semantics.

Previously established **starting points, not conclusions about event timing**:

| Locator | Previously established role |
| --- | --- |
| `FUN_1407B6710`, `0x1407B6CB0/B6` | Body-keyed knowledge-mask update / bit operations |
| `0x141A373D1–3D9` | Caller requests bit 1; contained in `FUN_141A37140`, reached via a `PlayerCharacter` virtual slot `+0x860` (vtable `0x144CBCCA8`) |
| `0x142108A6F–A77` | Second known request to set bit 1 |
| `FUN_1407B65D0` | Knowledge-mask read; named `GetPlanetVisited` query path |
| `FUN_1407BA290` | Effective body scan-level query; distinguish from visit state |
| `FUN_1417D7EB0` | Visit bit credits the **remaining atmospheric resource span** in resource survey snapshot |
| `BSComponentDB2::DB +0x268` | Body-keyed `PlayerKnowledge` component store, separate from retained per-biome data in `+0x300` |

The existing Save2 Volii Alpha sequence shows orbital **`0/2`, 31%** before landing; after landing **while still aboard**, the scanner shows **`2/2`, 88%**; after disembarking, still **`2/2`, 88%**. These screenshots establish *when the credit was visible*, not the native write instruction or its exact trigger. The comparison crosses a landing and a UI change. All SRR-021 screenshots derive from Save2 as a starting save; later actions are **not** part of the archived original Save2 state. SRR-022 recovered serialized knowledge, but serialized state does not identify the action that wrote it.

## Workstreams

### A — Visit-bit setter and caller ancestry

1. Re-verify both known setter call sites, argument and body-ID provenance, mask manipulation, return/dispatch semantics and any intervening typed commands or deferred operations.
2. Trace callers upward through actual direct and indirect/virtual dispatch until the trigger conditions can be described or a defensible unresolved boundary is reached. Identify distinct caller contexts; do **not** merge them merely because both reach the same setter.
3. Test evidence-grounded alternatives: additional setter paths; repeated requests; skipped writes; possible clear/reset; first creation versus update of an existing component. Investigate other paths only when anchored in a concrete xref, dispatcher, mutation helper or observed contradictory state.
4. Identify what the known paths can prove about the **target body**, especially whether it is the selected starmap body, orbital destination, current planet, landing target or another resolved object.

### B — Travel/arrival and knowledge-component lifecycle

1. From the relevant callers, trace travel, orbital arrival, scan-from-orbit, landing request/completion, active-world/player transition and disembarkation **only as necessary to identify the visited-bit trigger**. Treat these as candidate events, not predefined answers.
2. Distinguish component lookup, initialization, creation, scan-level change, visited-bit change and restoration from save. Verify whether a missing component can be created by the mutation path and whether that changes ordering or observability.
3. Account for synchronous versus deferred execution and publication. If a trigger schedules work, a trigger call, queued command execution, successful component update and subsequent UI refresh are different events.
4. Determine the narrowest **statically supported** event boundary. Do not infer chronological timing from lexical code proximity, function names, menu labels or a single call graph edge.

### C — Cross-evidence reconciliation and rival models

1. Independently verify pivotal native predicates and alternative dispatch paths with the pinned executable. Challenge assumptions about body identity, first-write detection, visit versus scan flags, and conditional paths.
2. Reconcile each supported interpretation with `FUN_1417D7EB0` and the established atmospheric-only Volii Alpha membership (Benzene and Water, no terrestrial slots). Explain the minimum conditions for `0/2 → 2/2` without asserting unobserved state changes.
3. Consult existing SRR-021 originals/manifest and SRR-022 private decoded output as independent controls where useful. Verify their evidence identities; **do not** treat the screenshot sequence as an uninterrupted native trace or the archived Save2 as containing the later landing transition.
4. Document competing explanations that remain viable, and observations that would falsify each. Do not perform new gameplay or generate new save states.

The parent agent integrates the three workstreams and adjudicates contradictions. Agent C is an analytical cross-check, **not a substitute** for the required post-integration independent challenger.

## Required execution model and evidence standards

Produce a compact, source-linked model that distinguishes:

- **Who** can request the visited bit (confirmed call chain, branch conditions, event association).
- **Which body** is targeted (how the body ID is computed/resolved, not merely a guessed planet name).
- **What state** is required before the request (component existence, initial mask, saved state, scan state).
- **When a transition is committed** (request, command processing, store mutation, observer-visible update).
- **Whether a call can repeat**, is idempotent, clears state or can be bypassed.
- **Why atmospheric survey credit follows** and which independent conditions affect the displayed numerator.

Grade every pivotal assertion as static control-flow fact, conditional inference, or unresolved runtime/historical observation. Identify candidate travel events explicitly as proven, excluded, or still possible; do not elevate a feasible path into proof that it executed in Save2. Where static evidence leaves a branch/input/scheduling ambiguity, give the precise discriminating condition and the *minimum useful* live observation (native location, body ID, mask before/after, call ancestry, scheduling/return boundary, and relevant UI checkpoint). A live-observer **specification** may be included in the existing lifecycle document only if warranted; no observer implementation is authorized.

**Important negative-control requirement:** Show that the observed `0/2 → 2/2` is not automatically evidence that the bit first changed exactly at landing completion; alternative mechanisms (prior state, view/refresh timing, different data source, initialization) must be considered where grounded. Conversely, do not invent speculative explanations without a supporting mechanism.

## Scope exclusions and safeguards

- **Offline/read-only only.** No running or attaching to Starfield/Creation Kit, debugging, SFSE plugins, injected hooks, live observers, or save edits.
- No changes to `starfield-resource-reproducer`, resource-generation algorithms, strict native-oracle admission or allocation validation.
- Do not expand into a general survey of map markers, quest discovery, exploration, ship travel or arbitrary PlayerKnowledge fields absent a concrete native link to visited bit 1.
- Do not build a broad tracing framework, new evidence system, standalone numbered dossier or second hypotheses register.
- Preserve original save files, gameplay screenshots and other primary evidence unmodified and private. If any new primary asset is actually used in a tracked claim, verify and register its custody under the existing private release-assets conventions before publication.
- No arbitrary function-count ceiling; expand only through evidence-grounded leads, and stop when an unresolved runtime boundary is precisely specified.

## Durable deliverables

1. **Primary technical account:** Amend `docs/component-database.md` with established setter/lookup/creation relationships and the conditional visit-bit lifecycle. Use `docs/retail-execution-lifecycle.md` for a concrete event-sequence model and observation boundary if warranted; avoid duplicative narratives.
2. **Lead register:** Update the single `SURVEY-UI` row in `docs/hypotheses.md` with what was resolved, what remains open and the discriminating evidence. Preserve the separate post-scan orbital-Neon presentation question as unresolved unless SRR-024 actually supplies evidence.
3. **Registries/provenance:** Amend `docs/function-register.md`, `docs/structure-register.md` and `docs/PROVENANCE.md` **only if justified** by new findings or evidence identities.
4. **Private evidence:** Retain bounded disassembly windows, source locators, alternative-model checks and any other working receipts under existing `.local-work/` directories. Avoid tracking private save data or screenshot binaries.
5. **Independent challenge:** After integration, use a separate challenger to verify the pivotal disassembly/control flow, body-ID attribution, competing event interpretations, screenshot/save qualification and final edited artifacts. Resolve and rerun review after substantive corrections.
6. **Handoff:** Provide a task-only patch/diff, changed-path inventory, review receipt, evidence qualifications, clear A/B/C disposition and the smallest next live observation **if required**. Leave all changes **unstaged and uncommitted**; do not push.

## Acceptance criterion

**Recover and independently challenge the native lifecycle of `PlayerKnowledge` visited bit 1, including setter invocation, body identity, component creation/lookup and its relationship to travel and arrival. Identify the earliest event boundary supported by offline evidence, distinguish first transitions from repeated writes and restored state, and specify precise minimal runtime observation(s) only for remaining execution-dependent uncertainties.**

A rigorous partial resolution with explicit falsifiers is acceptable. A list of plausible event names or unqualified claims that the bit changes on landing is not.
