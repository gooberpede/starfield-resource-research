# SRR-013 structural allocation-state observation

This continuation adds a separately selected structural observation mode for
three Kreet biomes and the Decaran VII-b control. It measures retained
`CTPerBiomeData` fields for those identities within one accepted paired
window. The [retail title run card](SRR-013-structural-title-run-card.md) is
**NOT AUTHORIZED**. This investigation used owned Windows fixtures and the
pinned retail executable as an offline data file.

The [budget recovery](SRR-013-live-observation-budget-recovery.md) qualifies
a later acquisition policy. The original tests and review below describe
the candidate frozen for the first title-card attempt.

The existing [strict continuation](SRR-013-retail-readiness-continuation.md)
and its effective-input blocker remain in force for strict measurements.
The [SRR-012 acquisition](SRR-012-acquisition-evidence.md), [strict measurement
contract](SRR-012-measurement-contract.md), and [sample plan](SRR-012-sample-plan.md)
provide the layout, identities, sample/control relationships and predictions.
[SRR-011](SRR-011-planetary-allocation-execution-and-result-lifecycle.md#result)
establishes the retained writer, clears and copy paths. SRR-010 remains closed
and inconclusive. See the [lead register](SRR-013-lead-register.md) for the
remaining runtime predicates.

## Measurement modes

| Gate | Strict | Structural |
| --- | --- | --- |
| Common process and acquisition | Verified Steam/session and process epoch, pinned disk/mapped image, marker, published owner, registry, typed component, ordered range coverage, seven complete fields, control and equal bounded pair. | Same checks. The control can be structurally zero or populated. Its failure affects the samples that depend on it. |
| Authoritative form identity | PNDT key and seed, typed BIOM and pinned RSGD list and override, plus effective inputs for exact comparison. | PNDT key and typed PNDT/BIOM. The actual BIOM RSGD pointer list and nonzero override must resolve independently. Observed seed and actual RSGD identities are retained without comparison to pinned inputs. Every nonzero output word must independently resolve as `BGSResource`. |
| Applicability | Requires admitted effective load order, winning inputs, and relevant native source agreement. | Bypasses the effective-input/prediction applicability requirement. Offline predictions are conditional references. Native identity and structural checks still apply. |
| Positive and zero | `POPULATED_RESULT_OBSERVED` or `QUALIFIED_UNPOPULATED` under the exact contract. | `STRUCTURALLY_POPULATED` with independently validated nonzero resource IDs, or `STRUCTURALLY_ZERO` with seven zero fields in the verified component. |
| Refusal | `STATE_INDETERMINATE` with exact cause and readable observations. | `STATE_INDETERMINATE` with exact cause, readable observations and validated witness prefix. A mixed tuple containing an unresolved word refuses. |

The mode is selected at token issuance and copied into the operator marker,
sealed header, ordered acquisition events and report. Replay uses that
selection and checks an independently expected mode when supplied. Legacy
strict receipts retain their schema and decode semantics. Receipt seals
provide consistency checks under private custody. They do not authenticate
an author or a wholly substituted receipt.

## Native resource identity

The applicable image remains Starfield `1.16.244.0`, SHA-256
`7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28`.
The `BGSResource` factory returns runtime record type `0x9F` at
`0x1409E9B40`. Its create method at `0x1409E9BC0` calls the constructor
at `0x1409E7440`, which writes primary vptr `0x144B6F0B0` at `0x1409E74E6`
and writes `0x9F` to object `+0x2E` at `0x1409E75D9`. Independently, the
result consumer in `FUN_14079B520` resolves staged IDs through
`FUN_1405DE3B0` at `0x14079BC52` and tests type `0x9F` at `0x14079BC63`.
It performs the same check on the focal root at `0x14079B94A` and
`0x14079B963`. `FUN_1407BC3D0` stages the nonzero retained slots and
provides the Common-root selection consumed on this path.

For each observed nonzero slot, the external reader independently follows
the bounded authoritative FormID chain rooted at image RVA `0x5E60EA0`.
It requires one reachable match, a nonoverlapping object, matching header
FormID, type `0x9F`, and the exact relocated primary vptr in the admitted
image. It retains FormID, address, type and vptr as structural witnesses
and rereads the selected address-bearing evidence. An independent overlap
challenge required reserving the bytes of the entire known FormID table
even though the reader touches only the selected chains. Table storage can
contain a convincing object-shaped decoy in unread buckets. A present zero
tuple still needs independently rooted PNDT and BIOM identity.

To reproduce the instruction checks, give the existing hash-enforcing
offline decoder a lawful pinned executable. It prints bounded disassembly
and leaves the Ghidra project untouched.

```powershell
python -B tools/srr011/inspect_pe.py $pinnedRetailExe functions 1409E7440 1409E9B40 1409E9BC0
python -B tools/srr011/inspect_pe.py $pinnedRetailExe window 14079BC50 19
```

## Scientific scope and later admission

`STRUCTURALLY_ZERO` reports seven zero fields in an identified sample at the
checkpoint. The result carries no eligibility or population claim elsewhere.
A valid populated title-card result would support pre-checkpoint allocation
as the leading explanation given the established writer. The paired reads
do not show execution timing, continuous object lifetime, allocator idleness,
or save serialization. A stable intermediate clear or an ABA cycle can
produce agreeing pairs.

The future title-only entry point uses the previously qualified query/read
adapter and the same paired native decoder. It requires single-use private
custody, a record bound to the separately approved title scope and source
identity, and the operator's explicit responsive-title declaration for the
admitted process epoch. It performs no launch, save load or game-control
action. Actual Steam attribution, unchanged mapping, read rights,
publication and individually eligible structural witnesses are conditional
requirements of that live epoch. A failed predicate gives refusal.

## Reproduction and custody

AMD64 CPython and the local x64 Visual Studio toolchain suffice for the
disposable suite. It rebuilds its owned fixture, reruns both previous
matrices and adds structural, cross-mode, authorization and replay controls.
It reads only owned processes and writes private local evidence. The
source-identity command is offline. The journal replay uses recorded replies
without opening a process. These tools leave Ghidra untouched.

```powershell
python -B tools/srr013/qualify_structural.py structural-qualification
python -B tools/srr013/structural_title.py source-identity
```

| Qualification group | Result |
| --- | --- |
| Historical and retail-shaped strict matrices | 49 original and 35 continuation external tests passed. Separately, all 90 retained prior sealed strict receipts replayed with their original results. |
| Structural, dual-mode and refusal cases | 61 explicit-mode external observations passed. The same owned process and seven words produced strict indeterminate and structural populated or zero when effective inputs were unverified. A divergent independently resolvable resource ID qualified, while mixed unresolved words and wrong type, vptr, ID, alias and duplicate evidence refused. |
| Zero and coverage counterexamples | Unpublished context, wrong owner and registration, absent/duplicate or wrong BIOM, forged minimum, malformed tree and short reads refused. Object-shaped resource and BIOM records embedded in unread map buckets produced false populated and zero outcomes before rework and refused after the reserved extent check. |
| Time, model and control | Stable intermediate clear, ABA, a valid zero control and failed-control dependency reproduced. Between-read mutation, mid-read insertion, image drift, stale/prebirth marker and the expired acquisition budget refused. Changed seed and actual typed RSGD selection were accepted in structural mode without qualifying predictions. |
| Replay and authorization | Four invalid receipt challenges refused, including both resealed mode reversals. Scope, source digest, canonical custody and duplicate authorization controls refused offline, and the generic controller refused a retail request before admission. |

The owned fixture PE SHA-256 is
`bfbba9405d7777410ab3a6a119326b53dfb8a02878960621a4fcb9a6ad198496`.
The frozen handoff records the execution-source identity, the complete
case summary and the compiler, linker and Python identities. For an explicit
offline replay, call `observe.replay(receipt, expected_mode="structural")`
with the reviewed sources. The ordinary legacy replay command also reads
mode-bound receipts and uses their declared mode.

The work starts from `ecaf2d6a80a70aa408d3007878695b14dc443b3d` plus the
previously reviewed unstaged retail-readiness continuation. The exact
structural patch is relative to the captured starting worktree. It excludes
both supplied briefs and pre-existing changes. Raw identities, private Steam
evidence, addresses and read bytes remain in ignored local custody.
Builds, qualifications, review evidence and patch checks use the
[research workflow](research-workflow.md).

<!-- review-status:start -->
**READY FOR SEPARATE RETAIL TITLE-CARD AUTHORIZATION** in structural mode.
Independent offline and disposable review is **COMPLETE** after rework.
The reviewer independently reproduced the false populated and false zero
map-alias cases, verified their refusals on the final candidate, rebuilt the
fixture and repeated all 145 external cases. The review also verified mode
replay, least-privilege access, the one-use custody association, the proposed
run card and byte-exact forward and reverse replay of the 17-file task patch.
Live-only admission and separate written permission remain pending. The
strict effective-input blocker is unchanged.

Reviewed source manifest SHA-256
`5d79bed1f318e8a3fd120f03aaa8442c22ad929c19cca3c3e20c1eeb9a1a2b68`.
The manifest hashes delivered files in sorted path order and excludes this
marked block. The executable inspector source identity for the run card is
`f03a3ee256d19e6e56227a0abdaa5568e067a23befbbc65cb8751c14bf0b214d`.
<!-- review-status:end -->
