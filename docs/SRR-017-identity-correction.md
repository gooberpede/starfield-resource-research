# SRR-017 native FormID identity correction

**Current contract.** The maintainer withdrew physical ESM backing
provenance on 18 November 2026. Defining identity is the native loaded
plugin basename and local record ID decoded from an independently
validated runtime FormID. The corrected command preserves all rooted
coverage, native type, BGSResource vptr, pairing, replay and authorization
checks. The [proposed run card](SRR-017-title-run-card.md) remains
**NOT AUTHORIZED** pending a separate written single-use approval.

## Scope

The current candidate is based on committed native-identity correction
`37e85698e0cdeb9e970ee8df9d82096e057e09cd`. The correction retains native
FormID identity, complete paired traversal, resource slots and evidence
replay. Written approval follows the already qualified SRR-013 mechanism.
Physical ESM provenance remains outside acquisition.

## Corrected implementation

The exact command uses a written maintainer approval record, following
SRR-013. It binds execution source, work limits, title-only scope and
canonical custody. Native operator/session identity and exact preflight
receipt hashes are retained automatically in the one-use claim. It
still consumes a flushed exclusive one-use claim before Steam/process
admission, validates the mapped game image and epoch, accepts one held
title marker and collects one pair. The executable and authorization
evidence retain their existing hashes and integrity checks.

```powershell
& $approvedPython -E -B -m tools.srr017.retail_title observe-title `
    $steamRoot $custody "$custody/authorization.json"
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

## Operational prerequisite audit

Every mandatory condition in the retail command, inherited admission,
preflight and run card was reviewed for its purpose and proportionality.

| Category | Retained conditions and justification |
| --- | --- |
| Scientific validity | Pinned executable/layout and execution-source/work identity; authenticated mapped image and creation epoch; native namespace, FormID, type and resource-vptr checks; rooted counts/fences/extents; two fresh complete collections with the 25 ms gap; typed/value agreement and exact replay. Each establishes identity, coverage or repeatability of the claimed dataset. |
| Game, save and evidence protection | Ordinary same-user medium-integrity query/read access, Steam parent/session/log checks, no inherited compatibility flags, held title checkpoint, disabled Cloud/overlays, 98/95 independent backup pairs and both designated saves, unexplained-entry reconciliation, separate exact-epoch exit witness, normal operator Quit, sealed receipts, canonical private custody and flushed one-use claims. These protect the process, protected files and attributable evidence. |
| Ordinary preparation | Qualified local x64 Python with -E/-B and no optimization; current private config/policy and backups; fresh custody; written approval reference; operator launch/title/Quit and retained console digests. Operator SID/session and preflight hashes are recorded automatically. |
| Finite work and capacity | Reviewed tree/map/chain/read/output ceilings, cooperative cancellation, image and input-byte limits, 40 GB available-space floor after the 512 MiB projected write reserve. These derive from fixture geometry and measured cost, stop before excess work or evidence loss, and permit no automatic retry. The title marker's 30-second intake recency checks the immediately confirmed phase and places no deadline on acquisition. |

Removed requirements are SSH signing and enrollment infrastructure,
manual operator/SID/session enrollment, a hexadecimal approval ID,
canonical formatting for the handwritten JSON, fixed approval/preflight
expiry, and absence of installed SFSE loader/plugin files. The latter
remain inventory diagnostics. A normal Steam-launched authenticated
process supplies the runtime evidence. No replacement infrastructure is
required. New infrastructure needs explicit maintainer approval under
the [standing workflow rule](research-workflow.md#live-observation-and-recovery).

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

The six native-identity tests and unchanged 28-test oracle suite passed.
The 11 synthetic preflight tests include installation of an unused SFSE
loader/DLL while environment qualification remains valid. The shared
controller also accepts that inventory. Historical retail observations
retain their original scope.

| Retained qualification identity | SHA-256 |
| --- | --- |
| Reviewed execution manifest | `dde03db307559f0d954d7787acfbc74432f252e8c3987dbf06f690386cc17d00` |
| Canonical work manifest | `4bf5dd930d6fa545fe5312ea9c7b62795d0f70666f483e0070a1bffc00f9d9ad` |
| 31-control shared-flow qualification | `57959f42841f3b0a2b640e9dee3ca8716518780165b24d5dfeac1746fed40fb3` |
| Corpus portable export | `9beb42e3aded330261a46bb5860343a2088de1fccc519aba7e3e9e30b2515f8a` |
| Upper portable export | `3753caab1233b3f844e64ca37514d26066cb3d1a3937be9e3bff026ca2df249c` |

Reproduce from the checkout using a fresh owned run name.

```powershell
python -E -B -m tools.srr017.qualify_retail_title $newRunName
python -E -B -m unittest -v tools.srr017.test_native_identity tools.srr017.test_source
python -E -B -m tools.srr016.qualify_oracle
python -E -B -m tools.srr017.retail_title execution-manifest
```

These commands write private fixture journals, claims, synthetic
protection/exit receipts and qualification summaries.
They leave the Ghidra project untouched. The proposed retail command
requires fresh written single-use maintainer approval, normal operator
launch/Quit and the prescribed preservation receipts. Offline readiness supplies no live observation.

<!-- srr-017-identity-review:start -->
**READY_TO_REQUEST_SINGLE_LIVE_AUTHORIZATION.** The independent reviewer
accepted the written SRR-013-style approval binding and the exact
three-argument retail command. The review challenged the necessity and
proportionality of every mandatory prerequisite in the command,
admission path, preflight and run card. Remaining conditions establish
scientific validity, protect the game/saves/evidence, or prepare the
already qualified workflow. No additional infrastructure or credentials
are required.

The reviewer personally checked all 11 task files against manifest SHA-256
`f0b3e363bb7dce273bd1b9d5af2a1238d0ee44544601b7702d2b6f1c59e68f05`.
It lists sorted byte hashes and repository-relative paths separated by
two spaces, terminated by LF. Only this marked body's contents are
excluded from its dossier hash. An independent reconstruction of the
committed baseline verified task-patch forward and reverse application
against every delivered byte.

Nine independently constructed plain-approval controls accepted readable
JSON and refused incorrect source/work/scope/custody, blank approval
reference, duplicate members and obsolete trust fields. An exclusive claim
preceded process admission and refused reuse. The actual production CLI
refused absent approval on disposable input. Full checked replay
regenerated 7,310 rows and all 51,170 words. Native identity/type/vptr,
namespace, pairing, cancellation and finite-work refusals remained intact.
Wrong attempt hashes, changed marker epochs, edited portable datasets and
resealed native-read tampering were independently refused.

The substantive standalone Markdown report records these checks and
the operational audit. The scientific reader, native identity and
FormID validation code are unchanged. HEAD and the empty index remain
at the starting commit. All qualification used owned processes and
synthetic preservation receipts. A live extraction requires a fresh
separate written approval and the current preservation procedure.
<!-- srr-017-identity-review:end -->
