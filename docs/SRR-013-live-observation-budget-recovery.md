# SRR-013 live observation budget recovery

The original [retail title-card attempt](SRR-013-retail-title-structural-observation.md)
remains four `STATE_INDETERMINATE` results. Its first collection completed
both ranges, verified all four components and observed seven-word vectors
that matched the [conditional sample predictions](SRR-012-sample-plan.md#fixed-samples-and-controls).
The wall-clock deadline interrupted the second collection after
5.000920400 seconds. The receipt recorded 1,092 calls and 20,032 requested
bytes, both below their limits. The recovery qualifies changes offline using
owned disposable processes. The [future run card](SRR-013-structural-title-run-card.md)
requires separate written authorization.

## Clock paths and finite work

| Path | Recovered policy |
| --- | --- |
| Reader used to impose a five-second absolute deadline before and after calls | Both deadline checks are removed. The pair can make up to 8,192 acquisition operations and request at most 2 MiB. A work-limit refusal records the operation that was refused without dispatching it. |
| Native `Collection.exact` used to apply an eight-second deadline | Native bounds cover reads and requested bytes per collection, eight internal levels, 128 nodes, 512 entries, 256 FormID links per lookup and 32 BIOM RSGD pointers. Pointer arithmetic, tree progress, visited-chain checks and typed object ownership remain in force. |
| Wall/monotonic marker and target birth checks | An operator marker must be fresh and chronological when accepted at intake, before any acquisition. Subsequent capture uses the recorded intake and monotonic order. No recheck ages the marker during acquisition. The marker remains bound to the process creation epoch, label, mode and single-use token. Steam launch ordering and phase confirmation remain required. |
| Paired collections | The 25 ms separation remains. The journal records monotonic boundaries for both collection attempts and the pair. Actual elapsed times are diagnostic. There is one independently rooted pair and no retry. |
| Disposable fixture and test runner | Communication, retirement and test-supervisor watchdogs apply to test helpers. They are outside retail acquisition. |

Both collections still verify process identity, mapped image, context and
form identity, selected range coverage, typed payloads and all seven words.
The established comparison-control rules and full FormID-table alias checks
remain in force. Structural mode and strict exact-tuple mode retain separate
outcomes. Strict observation still requires effective-input evidence.

## Termination and evidence

| Event | Handling |
| --- | --- |
| Complete agreeing pair | Classify jointly qualified samples and their controls using the selected mode. |
| Operator cancellation | The title command handles Ctrl+C cooperatively. Stop at a returning read or identity boundary or across the gap and seal `operator_cancelled` with available partial evidence. A synchronous Windows call can delay the next boundary. The implementation cannot interrupt it or guarantee prompt cleanup while it remains blocked. |
| Process exit, loss of identity, failed or incomplete read | Refuse the affected scope. A failed pair-level check produces indeterminate outcomes while preserving completed evidence. |
| Invalid structure or nonprogress | Existing checked bounds, visited-node evidence and FormID chain checks refuse the scope. No fallback traversal. |
| Exhausted finite work | Refuse the pair with the operation or byte cause or the native traversal reason. |
| Disagreement | Seal `inconsistent_pair` and the observed evidence. One observation cannot choose another pair. |
| Journal open, write, seal or publication failure | Stop with a specific journal error. Retain any `.partial` file as incomplete evidence. The completed receipt is published only after a flushed seal. Replay refuses a pending file. |

Version 4 receipts encode the work limits and chronological collection
boundaries. Replay derives the decisions from the recorded operations and
rechecks declared limits, counters, mode and seal. Versions 1–3 retain their
historical rules for replaying the original outcomes. Old timeout receipts
stay indeterminate. No earlier receipt has been rewritten.

Longer successful pairs still sample separate moments. They can agree during
an intermediate clear or miss an ABA cycle. First-collection observations in
a refused pair remain descriptive. They confer no paired result, successful
control verdict, execution timing or wider planetary claim.

## Qualification and custody

Run the offline suite from the repository root with AMD64 CPython and the
local MSVC x64 toolchain. The tools build owned fixtures, obtain bounded
read-only responses and write receipts under ignored `.local-work/`.
They leave Starfield, saves and the Ghidra project untouched.

```powershell
python -B tools/srr013/qualify_budget.py budget-qualification
python -B tools/srr013/structural_title.py source-identity
```

| Qualification control | Owner run |
| --- | --- |
| Prior regression cases | All 49 original, 35 retail-shaped and 61 explicit-mode cases passed with the single intentional change to the expired-duration expectation. The previous recorded outcomes and receipts remain intact. |
| Same slow-progress case before and after | The historical `budget-expired` case expected four `observation_budget` refusals. In recovery, three bounded fixture pauses made the first collection take 8.753 seconds and the pair take 8.804 seconds. All four observations were `STRUCTURALLY_POPULATED`. The output and comparison predicates were unchanged. |
| Finite work and malformed traversal | Eleven new external controls exercised pre-dispatch operation and byte refusal, depth/entry/chain limits, cyclic traversal, cancellation before a second collection or during a read, target exit and delayed admission after marker intake. Test-only lower call and byte caps exercised the live dispatch and replay accounting without changing the released values. |
| Pair and marker invariants | The retained suite refused disagreement, mapped-image drift, malformed ranges, FormID-table aliases and stale, prebirth or wrong-epoch markers. It preserved the stable-clear and ABA controls. |
| Receipt integrity | The retained suite replayed both modes and refused invalid seals or changed modes. New resealed controls contradicted dispatched work and refusal counters. A simulated flush failure at seal time retained an unreplayable pending journal. |
| Prior evidence | 243 owned historical receipts replayed with their original decisions and 10 historical negative controls still refused. The actual private retail v3 journal was replayed read-only with original hash `82ab34550fca287e54155f28a9cf6e628587d5eb3bc212ac7289af7d512392dd`; all four indeterminate results and the historical counters matched. |

The disposable fixture PE SHA-256 is
`975e3242c792823e7b7bc68e09effaa93b0e47f9fe12f6fc9e860750058950d0`.
The handoff records the exact toolchain, reviewed execution source, patch
and receipt digests. The new frozen candidate has no retail receipt.

The code and documentation delta starts from `595960b`, with a clean index
and the supplied untracked recovery brief. The brief is outside the task
patch. Follow the [research workflow](research-workflow.md) and retain raw
addresses, process identities, and acquisition data privately. The
[lead register](SRR-013-lead-register.md) records the dispositions.

<!-- review-status:start -->
**READY FOR SEPARATE RETAIL TITLE-CARD RE-AUTHORIZATION.** Independent
offline review is **COMPLETE**. The challenger rebuilt the fixture and
repeated all 145 regression cases and 11 new external controls. In a
separate adversarial owned-process test, the first collection took 9.380
seconds and the pair took 9.432 seconds. All four structural outcomes
qualified and replay reproduced the result. A resealed receipt with a
zero collection gap was rejected. The reviewer checked the clock paths,
cancellation and evidence boundaries, and verified exact forward and
reverse replay of the 16-file task patch.

Reviewed source manifest SHA-256
`0c9436e6da3763df6ced3eb21b8300e9951649c2fdb3e6197d18831a6b7c74bc`.
The manifest hashes delivered files in sorted path order and excludes
only this marked block. The execution-source identity is
`69d8623f734c19fabed2674d2ea97ff4779505fe1ee22ff8fb4a1b2f66500cd6`.
Independent review and receipts remain under
`.local-work/independent-review/SRR-013-budget/`. This disposition applies
to offline readiness. Any later live observation requires new written
authorization and remains subject to its actual runtime predicates.
<!-- review-status:end -->
