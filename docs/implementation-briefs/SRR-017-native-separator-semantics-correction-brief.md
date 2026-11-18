# SRR-017 — Native tree separator semantics correction

**Type:** Focused offline implementation and audit brief  
**Status:** Authorized for offline analysis, correction and disposable qualification only. **No live Starfield operation is authorized.**  
**Target:** Pinned retail `Starfield.exe` 1.16.244.0, SHA-256 `7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28`.

## 1. Objective and decisive counterexample

Correct the rooted-index separator interpretation used by the whole-store reader, **only after establishing the native rule**. The operator-initiated title-card attempt on **18 November 2026** stopped at `index_fence`, after traversing 1,202 of the 18,314 declared mixed descriptors (37 exclusions and 1,165 raw typed targets). It retained 8,155 raw resource-slot words but **no qualified population or normalized extract**. Acquisition limits were not exhausted. Its sealed evidence independently reproduces the refusal; no second collection completed.

The failure occurred in a 14-descriptor packed block at root-derived traversal path `[0, 83]`. Its level-one ancestor has five separator keys, and the relevant ancestor child is index 0. The ancestor separator equals the **first key of the packed block**, while later keys in that block exceed that separator. The inherited check in `tools/srr013/native.py`, `Collection.check_fences`, assumes every descendant key of child 0 must be no greater than the separator. This assumption is contradicted by the captured bytes, but **the precise replacement rule is not yet proven**.

Primary offline inputs are the retained operator receipt and independent review, including the uploaded capture bundle `srr017-extract-20261118T041728Z-58f816c0.zip` and the associated review. Preserve their original hashes and historical `ACQUISITION_INDETERMINATE` classification. Do not turn the 1,165 partial typed rows into a qualified dataset.

## 2. Required investigation

1. **Reproduce the precise failure offline.** Replay the retained sealed receipt under the unchanged reader and reconstruct the root/leaf/block path, raw separator values, the block's fourteen ordered keys, and the exact failing comparison. Account explicitly for key representation (two unsigned words), boundary inclusivity and the distinction among internal-node pivots, leaf block minima and records within packed blocks. Use existing private custody rather than publishing addresses or receipt bytes.
2. **Recover native navigation semantics.** Inspect the pinned native lookup, lower-bound, iterator and cursor implementations already located in SRR-012 through SRR-016 (including `FUN_1403832A0`, `FUN_1403833E0`, `FUN_1424103E0` and `FUN_1403A4250`, as relevant). Determine what internal separators and leaf keys represent and which constraints are actually guaranteed at each level. Trace relevant comparisons and edge cases rather than assuming an ordinary B-tree model. Distinguish proven static semantics, fixture evidence and inference.
3. **Implement the narrow correct fix.** Repair checks in `tools/srr016/census.py` and/or the shared `tools/srr013/native.py` only where the recovered rule requires it. Preserve global ordered traversal, block-minimum agreement, leaf links, parent/child ownership, counts, fences where valid, extent checks, native FormID/type validation, paired agreement and checked replay. **Do not simply disable `check_fences`, suppress `index_fence`, or allow one anomalous path by special case.** Assess whether the changed shared primitive affects SRR-013 selected-key lookups and historical qualification.
4. **Preserve scientific scope.** The retained real-game receipt is a diagnostic counterexample, not proof of a complete tree or successful allocation. A later live acquisition must still fully traverse and reconcile the declared root-reachable population, and complete both collections before qualification.

## 3. Qualification and independent challenge

- Build native-shaped disposable cases for the **observed valid boundary geometry**, including internal separators equal to an interior/final packed-block minimum while that block contains greater record keys. Test direct root, multiple leaves, several internal levels and cross-node boundaries.
- Provide negative controls for truly misplaced child/block minima, descending or duplicate records, overlapping neighboring ranges, incorrect separator ordering or routing, invalid leaf links and counts, aliasing, and relevant exact-boundary off-by-one cases. Demonstrate that a false-positive fence has been eliminated **without accepting genuinely invalid trees or hiding missing records**.
- Replay the retained original receipt unchanged. It must reproduce the historical refusal with the frozen old reader; the corrected reader should pass the former separator condition **only if justified by the native semantics**. If the receipt is insufficient to reach a complete qualified observation, retain the appropriate incomplete verdict; don't invent missing read events or a second collection.
- Rerun the affected SRR-013/SRR-016/SRR-017 disposable regression suites, including the population-scale operator extraction, normalized exports, seven-slot conservation, interruption and tampered-receipt refusals. Preserve the existing finite work-based resource limits; introduce no new elapsed-time or administrative gate.
- Obtain an **independent substantive challenge**, up to **two concurrent sub-agents**, testing the inferred native rule and attempting to falsify the fix with independently constructed byte examples. Retain evidence-grounded lead exhaustion: resolve actual relevant counterexamples and explain any genuine remaining block, but do not investigate unsupported alternatives merely because they are conceivable.

## 4. Documentation and operational boundaries

Update **existing** authoritative technical documentation and the applicable tests/reader. Prefer corrections to the current database/extraction explanation over another dossier, lead register or diary. Record the revised native separator contract with concise pseudocode or a diagram, exact native locators, the retail counterexample and its interpretation. Keep the historical failed-run outcome unchanged. Do not reference private `.local-work/` artifacts as dependencies in tracked documentation; substantive independent-review findings should be summarized in the existing dossier. Store the full review under `.local-work/independent-review/` (singular).

No live process access, Steam launch, save-file access, debugger attachment, memory writes, new authorization/preflight infrastructure, auto-retry, staging, commit or push is authorized. Do not modify the reproducer or redefine the expected oracle to make the capture appear valid.

## 5. Handoff and completion

Return a task-only `.diff`/`.patch`, concise source-linked explanation of the corrected separator semantics, disposable-test outcomes, exact old-receipt replay result, frozen execution/work identities, and a substantive independent review. Explicitly state whether the operator-initiated extractor is **ready for a separately requested live attempt** or what concrete native/implementation issue remains. Leave all changes unstaged, uncommitted and unpushed for maintainer review.
