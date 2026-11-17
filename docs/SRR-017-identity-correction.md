# SRR-017 native FormID identity correction

**Current contract.** The maintainer withdrew physical ESM backing
provenance on 18 November 2026. Defining identity is the native loaded
plugin basename and local record ID decoded from an independently
validated runtime FormID. The corrected command preserves all rooted
coverage, native type, BGSResource vptr, pairing, replay and authorization
checks. The [proposed run card](SRR-017-title-run-card.md) remains
**NOT AUTHORIZED** pending a separate written single-use approval.

## Scope and starting state

The work started at research HEAD
`f4ba50cc046b43364cc001a8aea4baea09e87eb0`. The index was empty.
The sole pre-existing change was `.gitignore`, SHA-256
`e28b55c4ddd8649075b2ca5d971f0ef011c6eabe74755b6920ce2687623982b9`.
It is outside the task patch. Caller-available space was
87,669,133,312 bytes on C: and 63,823,982,592 bytes on D:.

The [previous readiness continuation](SRR-017-retail-readiness.md)
records the earlier physical-provenance requirement and blocked verdict.
That requirement and its resulting release blocker are **SUPERSEDED**.
Its native path observations remain historical static evidence. This
correction changes the acquisition contract using the existing recovered
namespace and FormID machinery. It adds no new native mechanism or
resource-generation rule.

## Corrected implementation

The exact proposed command drops the source-file profile argument.
Signed approval pins the execution source, work manifest, native identity
contract, selected operator/session, custody and preflight receipts. It
still consumes a flushed exclusive one-use claim before Steam/process
admission, validates the mapped game image and epoch, accepts one held
title marker and collects one pair. The executable and authorization
evidence retain their existing hashes and integrity checks.

```powershell
& $approvedPython -E -B -m tools.srr017.retail_title observe-title `
    $steamRoot $custody "$custody/authorization.json" `
    "$custody/authorization.json.sig"
```

The reader collects the full/medium/small native plugin arrays and
cross-checks each assigned slot with its TESFile flags/index/name and the
native registry. It no longer requests directory, provider, stream or
backing-file windows in the retail profile. A relative `DATA\` directory,
closed stream, missing local ESM or changed local ESM is outside the
identity gate.

`bind_native_namespace` converts that checked roster to an index. Each
runtime ID resolves through its native full, medium or small index,
preserving respectively 24, 16 or 12 local bits. It rejects unsupported
IDs, unassigned slots, duplicate names/assignments and conflicting
types. Its type claims consume the reader's existing FormID-map
stored-ID/type validation. Every nonzero resource still requires the
correct native BGSResource vptr. PNDT/BIOM key and payload checks remain
part of acquisition. The exported defining identity retains the observed
runtime ID, exact raw index words and all seven resource lanes.

The exporter joins the two checked native namespaces and emits their
deterministic digest. Winning-content and file-relative source record
fields remain null. Ordered native history, where readable, is diagnostic.
A missing, filtered, changed, contradictory or unreadable history alone
cannot invalidate a defining identity. Read/region failures confined to
history are retained as diagnostics. Work exhaustion, cancellation,
process exit, epoch change and evidence failures still stop acquisition.
Namespace and native-form read failures remain admission failures.

The old on-disk source helper is retained for historical offline analysis
and legacy fixture tests. The retail command and retail export use only
the new native index. Oracle inputs remain outside acquisition.
[Interchange](SRR-017-interchange.md) ·
[Native identity evidence](SRR-017-source-identity.md)

## Work envelope and preservation

The corrected flow uses the previously qualified finite paired envelope
of 8,192 descriptors, 1,024 windows, root level 5, 8,388,608 map buckets,
8,192 reached map entries, 256 entries per chain, 80,000 pair events,
32 MiB requested and a 128 MiB journal. Backend aggregate maxima remain
80,176 region queries, 80,040 process reads and 34,079,640 requested bytes.
There is no elapsed acquisition cutoff or automatic retry.

Native namespace and optional history remain under their original
individual ceilings and paired rereads. Removing ESM snapshots eliminates
all per-source file reads and source snapshot outputs from this command.
The 64 MiB portable-output cap, image hash limits and 512 MiB write
reserve on each drive remain conservative bounds. Both drives must retain
40,000,000,000 caller-available bytes after that reserve. The original
budget measurements remain in the
[capacity and admission dossier](SRR-017-title-admission.md).

The proposed run card preserves one ordinary Steam launch, the responsive
title checkpoint, a separate epoch-bound exit witness, operator normal
Quit and pre/post protection for 98 Documents plus 95 Steam remote
original/backup pairs and both designated saves. Cloud/overlays and
inherited compatibility settings retain their controls. These procedures
were exercised with synthetic receipts and owned processes. Real retail
launch, process access and save access were outside this work.

## Lead disposition and qualification

| Material lead | Performed check and result |
| --- | --- |
| Physical ESM/VFS provenance | Explicitly withdrawn by the maintainer. Removed directory/stream reads, source-file approval inputs, snapshots and digest/path matching from retail acquisition and replay. No further provider research was performed. |
| Defining native identity | Independent byte fixtures exercise nonzero full, medium and small namespaces, collision, unsupported IDs and conflicting types. The complete acquired rows require native-map and resource-vptr validation. |
| History as identity | Filtered and drifting history qualify with unresolved attribution. An independently unbacked history table qualifies only the verified native identity and records its read failure. Fatal process/work/evidence conditions retain their stopping behavior. |
| Completeness and replay | Complete direct, 3,210-target and 4,096-target datasets are checked through sealed receipt, replay, portable export and the unchanged SRR-016 observation parser, including all zero lanes. Namespace drift, invalid assignments, wrong PNDT/BIOM/resource type, wrong resource vptr, map region crossing, paired value drift, cancellation and truncation are refusal controls. |
| Authorization and preservation | The exact shared command continues to refuse absent/forged/stale approval, wrong scope/operator/source/custody and consumed attempts before another process admission. Independent exit and synthetic preservation checks reconcile separately from scientific qualification. |

The observable claim remains two agreeing, complete root-reachable
collections in the held epoch. Atomicity, uninterrupted lifetime,
intermediate mutation/ABA, other stores and queued work remain outside
that claim. Expected population and exact-value oracle qualification
follow separately.

## Verification and release

The exact shared controller passed 31 controls. Its owned service seam
opened only the test children. The direct, corpus and upper exports
preserved 4, 3,210 and 4,096 rows respectively, totaling 7,310 rows and
51,170 lane words. Each row's raw and canonical keys, native metadata
and seven lanes were asserted independently. Independent checked replay
regenerated byte-identical portable datasets and the unchanged SRR-016
observation parser consumed their projections.

The six native-identity unit tests and 14 existing source tests passed.
The unchanged oracle suite passed 28 tests. The rooted reader and
original owned admission regressions were also rerun with the corrected
source bytes. Historical retail observations retain their original scope.

| Retained qualification identity | SHA-256 |
| --- | --- |
| Reviewed execution manifest | `c33b26e68ce2a7b2746b7405f0de2684ae1c4d82a8e201b6aa28bef6a334f7bd` |
| Canonical work manifest | `4bf5dd930d6fa545fe5312ea9c7b62795d0f70666f483e0070a1bffc00f9d9ad` |
| 31-control shared-flow qualification | `9fa5809ea76f0b260cafd99df9530c902a8610fa927d09ca04f90d1c984e33a1` |
| Corpus portable export | `8eb7d3d52718e37e4a10647462732e0d09c226717bcb8e2f4e75bef3db395cf2` |
| Upper portable export | `e7fb793a410bca7943d87d5e7be09239f88e2fbab273fd0ad4b3d84c99d43fe1` |

Reproduce from the checkout using a fresh owned run name.

```powershell
python -E -B -m tools.srr017.qualify_retail_title $newRunName
python -E -B -m unittest -v tools.srr017.test_native_identity tools.srr017.test_source
python -E -B -m tools.srr016.qualify_oracle
python -E -B -m tools.srr017.retail_title execution-manifest
```

These commands write newly generated private fixture journals, claims,
signatures, synthetic protection/exit receipts and qualification summaries.
They leave the Ghidra project untouched. The proposed retail command
still requires separately enrolled maintainer trust and a fresh signed
single-use approval, normal operator launch/Quit and the prescribed
preservation receipts. Offline readiness supplies no live observation.

<!-- srr-017-identity-review:start -->
**READY_TO_REQUEST_SINGLE_LIVE_AUTHORIZATION.** The independent challenger
accepted the exact retail command, native namespace mapping, complete
paired acquisition, combined work limits, preservation procedure and
evidence replay under the corrected contract. This is an offline
readiness decision. A live observation still requires separate maintainer
approval and all operational gates on the proposed run card.

The challenger personally checked all 17 task files against reviewed
manifest SHA-256
`622750d41a071bc09ed349b04c87bd5d3f5e40bec45c12bd0ec5939df186db7c`.
Each line records the byte SHA-256, two spaces and the sorted
repository-relative path, terminated by LF. Only this marked body's
contents are excluded from its dossier hash.

Independent byte fixtures challenged full/medium/small namespace
assignments, missing namespaces, invalid IDs, native-map ID/type
disagreement, resource vptr and unreadable history. Checked replay
regenerated every raw and canonical key and all 51,170 words across
7,310 direct/corpus/upper rows. Relative DATA directories and absent or
changed ESM bytes qualified. Namespace drift, paired value drift,
incorrect native identity and work/evidence overruns retained refusals.
Resealed read tampering, wrong attempt digest and altered portable keys,
row counts and type witnesses were independently refused.

The substantive standalone Markdown review records separate judgments
for admission, identity export, combined budget, operational protection
and scientific boundaries. The challenger independently reconstructed
the committed baseline and verified the task patch in both directions
against every delivered byte. The pre-existing `.gitignore` change is
preserved and excluded. HEAD and the empty index remain at their
starting state. No real retail process or protected save was accessed.
<!-- srr-017-identity-review:end -->
