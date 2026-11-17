# SRR-013 read-only allocation state inspector

This investigation implements the [SRR-012 measurement contract](SRR-012-measurement-contract.md)
for an owned disposable AMD64 Windows child. The four fixed samples exercise
retained `CTPerBiomeData` storage. The phase labels are operator metadata.
Retail state at title, menu and settled gameplay remains unmeasured.

The frozen disposable candidate passed 49 external cases with full receipt
replay. The [proposed title run card](SRR-013-proposed-title-run-card.md)
is **NOT AUTHORIZED**. The adapter admits the owned fixture only. Retail
requires separately reviewed process and input admission and written authority.

## Acquisition

The qualifier builds one C fixture from tracked source and launches it with
an explicit scenario. The adapter binds a fresh `PROCESS_QUERY_INFORMATION |
PROCESS_VM_READ` handle to the launched process epoch. It checks the pinned
file and mapped main image, including the path, extent and focused PE
checks, before following any layout RVA. The adapter has no PID option.
The production read path queries the memory region and requires an exact
byte count. Qualification includes a deliberately reduced-rights probe.

The decoder follows the published context at `M + 0x82EEBB0`, requires the
embedded owner and expected vptr, then checks the live registered descriptor
and reads the native `+0x300` index. It descends the unsigned two-word key
tree, validates directory minima and packed descriptors, and follows
root-backed successor leaves through the upper fence or validated end. In an
encountered leaf it checks all advertised block minima against the packed
first keys. It decodes complete descriptors and record keys for blocks used
to establish range coverage. This leaves unvisited subtrees and unrelated
record payloads outside the evidence.
The [native acquisition evidence](SRR-012-acquisition-evidence.md) gives
the field widths, locators and build applicability. The decoder requires
the pinned order and cardinality of the full selected ranges. It resolves
each selected PNDT, BIOM and relevant RSGD through the independently rooted
FormID hash table and checks the PNDT key and seed, BIOM list and override.

The collector repeats the selection from the root and compares address-bearing
structure, typed forms and all seven words. It brackets each collection with
process/image identity and rechecks structural reads. One pair uses a 25 ms
gap and a five-second deadline with independent read, byte, depth, node,
record and chain bounds. Limit violations mean incomplete coverage. The
classifier requires the sample and its designated control to pass. It keeps
the observations separate from the [pinned predictions](SRR-012-sample-plan.md).
Prediction applicability is restricted to the admitted disposable input
profile. Retail load order, data and effective-input admission are separate
requirements.

The window budgets 8,192 acquisition calls and 2 MiB of requested layout
bytes. Counts include the four process identity brackets as calls. Each
successful bracket independently uses four fixed-size mapped header/code
reads, in addition to its bounded query checks. Native limits include 8
internal levels, 128 visited nodes, 512 inspected record entries and 256
links per FormID chain. One observation attempts one pair. An observed
disagreement invalidates the window.

**Two agreeing reads do not rule out intervening writes, storage reuse or
ABA. Both reads can also coincide with a stable intermediate clear.** These
observations cannot establish allocator execution, timing, persistence or
save serialization. A zero verdict is scoped to one eligible sampled
component and its marked window.

## Reproduction and custody

Run from the repository root using AMD64 Python 3.14 and local Visual Studio
Build Tools for x64 C. The qualifier reads tracked fixture and reader source,
builds and runs the disposable child and writes sealed receipts under ignored
`.local-work/codex/SRR-013/`. The decoder and replay leave the Ghidra project
untouched. A receipt contains disposable epoch and address-bearing evidence.
Keep receipts and compiled outputs local.

```powershell
$srrRun = "qualification-$([guid]::NewGuid().ToString('N'))"
python -B tools/srr013/qualify.py run $srrRun
python -B tools/srr013/qualify.py replay ".local-work/codex/SRR-013/$srrRun/populated.jsonl"
```

Replay checks the completion seal, then runs the same decoder and classifier
against the exact ordered, bounded read replies. An admission refusal receipt
preserves the refusal and replays the resulting indeterminate decisions.

## Disposable qualification

| Coverage | Result |
| --- | --- |
| Direct packed block, multi-block leaf, levels one and two, predecessor, packed hole and exact root end | Both collections matched the independent ordered three-plus-one BIOM enumeration and the four expected tuples. |
| Eligible all-zero, mixed, ineligible-zero and unknown effective inputs | Correct verdict per sample. Mixed yielded two populated, one qualified zero and one unexpected tuple. Unknown inputs preserved all four conditional observations. |
| Absent, duplicate, wrong owner/type/registry, map collision/cycle, readable replacement forms and malformed structures | Affected samples failed closed. Unaffected samples with complete shared coverage and a valid control retained their verdicts. |
| Successor-leaf duplicate and forged trailing block minimum | The first exposed both Frozen edges. The independent challenge initially hid a duplicate behind a false advertised minimum. The regression now rejects the leaf with `block_minimum`. |
| Traversal bound, changed mapped PE header, wrong process epoch and missing rights | Deterministic refusal. The excessive tree reached a native traversal budget. The adapter did not retry with additional privileges. |
| Payload clear, index insertion/removal and insertion during collection | Changes between collections produced `inconsistent_pair`. Mid-collection insertion produced `structural_change`. |
| Free writer, ABA and stable intermediate clear | The free-running writer gave disagreeing evidence in one run and agreeing nominal evidence in another. The scheduled ABA cycle reproduced agreement and the stable clear qualified all four zero samples. |

An early disposable build refused genuine mappings because Windows rebased
the mapped PE `ImageBase` field. The reader now matches that field against the
independently acquired module base when rebased and checks the remaining
header and focused code bytes. The mapped-timestamp counterexample still
fails admission. A reviewer also checked the deadline at the final identity
call and reproduced the refusal with a controlled clock after rework.

The exact fixture PE SHA-256 is
`edac25b21ad832b69015bf3d73e6f19f8c6e148d77d58b27a6200204c6c1c105`.
The reader is Python source. The run used AMD64 CPython 3.14.3, MSVC
14.51.36231 and Windows SDK 10.0.26100.0. The qualifier generates a
build manifest, per-case receipts and hash summary for the new run.
The patch excluded diagnostic evidence, proprietary images, real game
memory and save files.

## Review and authorization

The [lead register](SRR-013-lead-register.md) records the engineering and
retail applicability gates. No retail process or save was accessed. The
starting HEAD and synced tracking tip were both `4dcb5e0`, the index was
clean, and the supplied brief was already untracked. The delivery patch
excludes that pre-existing brief. The index, HEAD and protected baseline
documents remain intact.

<!-- review-status:start -->
**COMPLETE for disposable AC1–AC8 after rework. READY FOR RETAIL
STATE-OBSERVATION AUTHORIZATION.** The disposition refers to consideration
of a separate authorization. The current fixture adapter only admits the
disposable executable. A live protocol needs the separately reviewed retail
admission and effective-input gates before any measurement.

The independent internal challenger rebuilt the exact fixture, repeated all
49 external scenarios and replayed the sealed receipts. The review covered
the malformed-minimum counterexample, deadline refusal, the proposed run
card and an exact 11-file patch replay against `4dcb5e0`.

Reviewed source manifest SHA-256
`d7bd83899be4a8c44b76058d83f16b26f0e3032d5dec67cf4db5fcab3f4e078d`.
The manifest hashes each delivered file in sorted path order with only this
marked review block excluded.
<!-- review-status:end -->
