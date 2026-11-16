# SRR-012 — Retained planetary allocation state observation feasibility

**FEASIBLE WITH CONDITIONS.** Static analysis on the pinned retail image
connects an ASLR-adjusted image slot to the context used by the allocator,
the context's keyed index and the inline biome payload. The same context
construction path publishes an independently checkable embedded object
address and vtable. A small read-only design can target three Kreet biomes
and a contrasting Decaran VII-b biome. The remaining conditions are
disposable qualification of the exact reader and effective-data profile,
then separate authorization to measure one live checkpoint. Runtime
mapping access, actual context readiness, read stability and result
presence at title, menu and Save2 remain unmeasured.

## Findings and limits

| Source | Finding |
| --- | --- |
| New offline acquisition evidence | `FUN_1423FF640` returns the same image object at preferred VA `0x1482EE300` through either arm. Startup initializes its embedded context at +0x2C0 and publishes it through +0x8B0. The allocator loads that slot, and shutdown destroys the published context before zeroing the slot. The supported runtime route starts at module base + RVA `0x82EEBB0`. The context pointer is corroborated by the expected relocated embedded address and vptr. Index block, key and record decoding are documented with native locators. [Acquisition evidence](SRR-012-acquisition-evidence.md) |
| New sample screening | The selected logical keys and seven-slot expectations distinguish ordinary and override BIOMs, sparse Common descendant roles, Everywhere and Special. The sample avoids the observed retail/model differences in BIOM fallback and Everywhere handling. Expected tuples are conditional model predictions, screened against retail static paths. [Sample plan](SRR-012-sample-plan.md) |
| New decision qualification | A fabricated fixture exercises the outcome gates, including eligible all-zero with a valid zero control, missing or duplicate targets, wrong identity, unsupported slot vectors, epoch and index drift, and partial/control failures. It exercises only decision logic. [Reproduction](#reproduction) |
| Inherited result and timing limits | SRR-011 established the retained writer and no-generation lookup miss, not the actual invocation at startup or during Save2. The four SRR-010 Stage B attempts ended before confirmed player control or scientific STOP. SRR-010 remains closed, inconclusive and resumable. No rule in the validated v1 generation baseline changes. [SRR-011](SRR-011-planetary-allocation-execution-and-result-lifecycle.md) · [SRR-010](SRR-010-stage-b-save-load-observation.md#final-disposition) · [v1 baseline](v1-research-baseline.md) |

The [measurement contract](SRR-012-measurement-contract.md) specifies all
three checkpoint markers, exact outcome boundaries, identity-aligned
comparison, paired collection and private custody. A completed populated
tuple shows retained state at the sampled checkpoint. In a fresh process at
the title card it supports the inference of earlier allocator execution
given the established producer evidence. A later populated tuple after a
qualified zero establishes a difference between the sampled values for those identities.
The writer can clear previously populated data and typed copies can preserve
output, so zero tuples and transitions cannot retrospectively time an
invocation. The [lead and evidence matrix](SRR-012-lead-register.md)
records the remaining discriminators.

## Acquisition choice and next gate

Use an external 64-bit reader with `PROCESS_QUERY_INFORMATION |
PROCESS_VM_READ | SYNCHRONIZE`. The prior [read-side admission
logic](../tools/srr006/retail_profile.h) and [diagnostics](../tools/srr006/admission_diagnostics.h)
show region checks, exact reads and epoch handling. The existing code
contains debugger-specific operations and supplies source examples only.
On the same handle, ordinary query and read access should suffice for
mapped-image checks and bounded structural reads, subject to actual access,
origin and data-profile checks. No write, suspension, thread, debug or
native invocation rights are needed in the proposed method. A denied or
unverifiable read yields an attributable indeterminate outcome.

The simpler direct image-slot lookup replaces replaying the native
TLS-guarded accessor or following the allocator stack. Directly reading
the fixed embedded address without checking publication is insufficient
during construction or teardown. Invoking the native copy-out reader
would require execution in the target, including correct owner, thread
and output-object semantics. The reader's ordinary no-generation miss
does not make it an external read-only operation. Any later decision to
consider it would need separate authority. A save-file check, CK scan,
canonical oracle or public scanner can corroborate source or output
semantics. None of the inspected evidence provides the same responsive-phase
owner/edge/result tuple. A previously saved trace could substitute only if
it already captured that checkpoint, process identity, full coverage and
all seven slots under the contract.

1. **Implementation and disposable qualification.** Approve only a narrow
   inspector and tests on fabricated trees and an owned disposable
   process. Test nested and single-block paths, corrupted descriptors and
   bounds, duplicate or absent keys, wrong image/epoch/region, partial
   reads, concurrent mutation and custody failures. Freeze the supported
   structural and data profile and budgets. Cross-check the selected
   effective inputs against the installed lawful game data offline. Use
   fixture mutation to demonstrate refusal and document what equal reads
   cannot discriminate.
2. **One live checkpoint.** After review of the qualified inspector,
   authorize at most one operator-marked checkpoint for the pinned
   environment and measurement contract. The responsive title card is a
   useful first gate because positive evidence there constrains startup
   and requires no Save2 load. Compare against other checkpoints only after
   their own authorization and measured phase evidence.

## Baseline and custody

Starting HEAD `3e7f3f6b286d49eff5d09199ca547819c9b72b0c`, tree
`b538761e4b548025b51798729d1a6cca547af507`. The supplied untracked
implementation brief was present at entry, SHA-256
`5b4b0d7a69abf8d354ce6e62b6b147b7b740ff90b1b3b6bbfa7e9d3db4c1e280`.
The evidence baseline uses committed blobs. Selected identities follow,
with a wider inventory retained in the local start receipt.

| Committed source | Git blob |
| --- | --- |
| [SRR-002](SRR-002-retail-static-reconnaissance.md) / [SRR-003](SRR-003-retail-allocator-invocation-and-dispatch.md) | `ad6879a86d608e9b11f31d6137c5dbd76e10662c` / `3bf0a6eeb696e1db1a7a6071adf11fa5fc1b2d51` |
| [SRR-005](SRR-005-live-observation-preparation.md) / [SRR-006](SRR-006-four-site-hardware-observer.md) | `072fd045a2f0d96d5e9c315cd62072f9dadd6d71` / `ef7f797fb3cb16c62058bc33b71c2371c1f1669d` |
| [SRR-009](SRR-009-retail-debugger-admission-and-stage-a.md) / [SRR-010](SRR-010-stage-b-save-load-observation.md) | `33209d6fd1b9d793a53f5352991810f964114b66` / `9d9c2e7df9b26963a160d2158af6a12015237835` |
| [SRR-011 dossier](SRR-011-planetary-allocation-execution-and-result-lifecycle.md) / [lead register](SRR-011-lifecycle-lead-register.md) | `40fb312663085e0545ba99ba8bea7e97f105ebec` / `207319a80787c975de92c421d4653d5859233922` |
| [Function register](function-register.md) / [structure register](structure-register.md) | `585229ba1aa7194d48aa45df59cee425b5ae8521` / `b22220c27efa505312113f170d0a20ff7c7b5086` |

The installed and analysis copies of `Starfield.exe` both measured
102,476,200 bytes, file/product version `1.16.244.0` and SHA-256
`7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28`.
Native locators use preferred base `0x140000000`. The baseline
[provenance](PROVENANCE.md#current-retail-identity) records Steam installed
build 23518663. The existing saved Ghidra 12.1.2 PUBLIC retail project
`Starfield` contains `/Starfield.exe`, file ID
`c0a816bc892993545618675600`, with the prior matching import hash. Its
`db.2.gbf` SHA-256 is
`9465cc9944d35acb75440471b0841fece52cc142341c269a5129a575791ded44`.
The other preexisting project names were `StarfieldCK` and
`CompletePlanetSurveyDll`. They represent different image domains and
were excluded from this retail chain. No project import or analysis
mutation is required. Offline output came from the PE decode on
Python 3.14.3 / Capstone 5.0.7 and the pinned accepted sources.

## Reproduction

Reverify version/SHA-256 using the [retail identity
procedure](PROVENANCE.md#current-retail-identity). Use the matching PE
strictly as a data file. From the research repository with Python and
Capstone already available, pass the actual interpreter and pinned
executable paths. The [native evidence](SRR-012-acquisition-evidence.md)
provides further windows and the [sample plan](SRR-012-sample-plan.md)
gives the independent model reproduction.

```powershell
$srrPython = '<path to Python with Capstone>'
$srrExe = '<path to matching offline Starfield.exe>'
& $srrPython -B tools/srr011/inspect_pe.py $srrExe window 1423FF640 6B
& $srrPython -B tools/srr011/inspect_pe.py $srrExe window 1418993C6 34
& $srrPython -B tools/srr011/inspect_pe.py $srrExe window 140771F30 E8
& $srrPython -B tools/srr012/check_contract.py
```

The first commands read the PE and print native windows to stdout. The
fixture builds fabricated observations in memory, runs four test methods
with adversarial subcases and emits terminal test results. It takes no
input paths, opens no process and writes no capture. These commands make
no Ghidra project changes. The fixture supplies no independent evidence
about NT process access, memory layout correctness, retail latency or
runtime stability.

The reproducible method uses the committed source, a lawfully obtained
matching PE and the accepted, pinned sample inputs. Publication review
in this phase is limited to the proposed changes. Detailed native
listings, Ghidra files, historical captures, evidence receipts and
runtime-bearing data remain in local custody.

<!-- review-status:start -->
## Review status

**COMPLETE for the offline feasibility scope.** The independent internal
challenger accepted AC1–AC8 on the frozen substantive snapshot. Review
clarified the zero-control rule, the structural equality gate, the mapping
identity limit and the matching of authored and native edge order.
The challenger re-decoded the native ownership and traversal,
rechecked the selected authored records and replayed the sample projection,
decision fixture and task patch. Runtime availability, atomicity and
the actual state at all three checkpoints remain unverified.

Reviewed manifest SHA-256
`4d46e17c199600824b55d1346157e7028ace811dd3ad6a9442925c0c4b4e584c`.
It records file SHA-256, two spaces and the repository-relative path
with LF in sorted path order. Only this marked review block is excluded
from the dossier digest. The exact task patch is
`.local-work/diffs/SRR-012.diff`. Manifest, hash and endpoint replay
receipts are under `.local-work/codex/SRR-012/`. The independent
review and replay receipts are under
`.local-work/independent-review/SRR-012/`. The pre-existing brief
is unchanged and excluded from the patch.
<!-- review-status:end -->
