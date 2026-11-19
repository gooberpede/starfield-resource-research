# Analysis tools

Run Python commands from the research checkout using AMD64 Python 3.14
(historically 3.14.3). Replace `python` with your installed interpreter if
needed. Commands below use tracked source and explicitly supplied lawful
inputs. Output paths must be fresh; keep raw address-bearing evidence private.
None of these tools modifies a Ghidra project. Tool-specific process effects
are described below. Research/live access needs its own explicit instruction.

## Current operation

[SRR-017 extraction](srr017/README.md) is the current operator command for an
already running compatible title-card process. It reads the rooted native
store, typed forms and paired plugin namespace with query/read access, writes
sealed evidence plus portable outputs and never launches/closes the game.
Its [interchange contract](srr017/interchange.md) also defines the legacy
SRR-016 comparison envelopes. Physical source provenance and strict oracle
admission remain separate from native acquisition.

## Offline oracle and comparison

Requires the clean reproducer at
`a8ff1c788bca415f571f06769ab3e712fa674f75` and its four maintained CSV inputs
listed in [validation](../docs/allocation-validation.md). The freeze pins
source/corpus hashes and writes ledger.json, oracle.json and freeze.json.
Freeze independently **before** reading observed values and retain the
canonical receipt digest independently. `$srrReproducer`, `$srrOut`,
`$srrObservation` and `$srrFrozenReceiptSha256` below are caller-supplied paths
and the independently retained digest, not pre-existing private dependencies.

The oracle qualifier defaults to a sibling directory named
`starfield-resource-reproducer`. For a checkout elsewhere, set
`$env:SRR016_REPRODUCER = $srrReproducer` before qualification. Its tests
read the pinned checkout without modifying it.

```powershell
python -B -m tools.srr016.qualify_oracle -q
python -B -m tools.srr016.oracle $srrReproducer $srrOut
python -B -m tools.srr016.compare $srrObservation `
  (Join-Path $srrOut ledger.json) (Join-Path $srrOut oracle.json) `
  (Join-Path $srrOut freeze.json) --receipt-sha256 $srrFrozenReceiptSha256
python -B -m tools.srr018.compare <reproducer-root> <original-capture-directory> <new-output-directory>
python -B -m tools.srr018.compare <reproducer-root> <compact.csv> <new-output-directory> --compact
python -B -m tools.srr018.preserve --source <original-capture-directory> --output <private-assets-directory>
python -B -m tools.srr018.qualify -q
```

The comparison reads the prepared originals or compact CSV and pinned inputs,
writing deterministic JSON coverage/applicability/key/slot/planet reports.
Preservation reads the five original acquisition files, verifies identities and
writes a private ZIP, compact CSV and manifests. These commands open no game
process, modify neither reproducer nor inputs, and change no Ghidra state.
The repository does not distribute the historical capture/CSV. You can run
synthetic qualifiers without them; exact historical arithmetic requires the
hash-identified evidence in lawful custody. Compact arithmetic does not replay
native acquisition. Qualification results must keep fixture evidence separate.

The standalone base-input check reads a lawful master and pinned sibling,
prints disk identities/gate disposition and writes nothing:

```powershell
python -B tools/srr013/retail_inputs.py <Starfield.esm> <reproducer-root>
python -B tools/srr012/check_contract.py
```

To independently rederive base fields, use the
[versioned ESM reader](https://github.com/gooberpede/starfield-outpost-research/blob/d116bc63ff394b0156539161c8d1addfc902665a/save-analysis/scripts/inspect_outpost_definitions.py),
blob `391dd8fb007b8ed8ceff48fce2f6ba97a61bd618`, in its own checkout.
With that script directory on `PYTHONPATH`, import `esm_records` from
`inspect_outpost_definitions` and call
`esm_records(esm_path, {b"PNDT", b"BIOM", b"RSGD"}, repeated=True)`.
Hash the lawful base master before and after; require
`1dabed00c3f4282dd3bb54d2e9601e40b577d8742d078b7ccef203adbfef0da7`.
Filter to Kreet/Decaran and their selected BIOM/RSGD IDs in
[validation](../docs/allocation-validation.md#independent-base-field-controls).
Compare PNDT RSCS seeds, ordered PPBD prefixes decoded as `<IfII`
(BIOM ID, coverage, per-biome seed, override ID), each BIOM's ordered
four-byte RNAM references and referenced typed RSGD records. Retain field
verification only, without raw proprietary records. This independently
corroborates base definitions, not the running process's winning inputs.
The self-contained oracle qualifier above separately verifies the four
conditional control vectors using the explicitly supplied pinned reproducer.

`tools.srr016.ledger.CONTROL_SOURCE` retains the historical string
`SRR-012-sample-plan.md#offline-reproduction` as an evidence identity, not a
current filesystem dependency. Its scientific content now lives in
[validation](../docs/allocation-validation.md).

## Offline native inspection

The tracked `tools/srr011/inspect_pe.py` reads a lawfully obtained PE, prints
address-qualified instruction/data windows using Capstone 5.0.7 and does not
write the image. Use its `--help` for exact subcommands; subject-specific
native reproduction examples are in [lifecycle](../docs/retail-execution-lifecycle.md)
and [database](../docs/component-database.md). Ghidra's seven read-only
exporters and output schemas are documented [separately](../ghidra/README.md).

## Historical selected-key readers and whole-store census

SRR-013 selected four keys; SRR-016 generalized to the rooted mixed store.
They remain for reproducing old fixtures/receipts, not current retail admission.
Use local x64 Visual Studio Build Tools and Python. Qualifiers build, start,
read and retire **only their own disposable child**, writing receipts/build
manifests to new ignored output names. Run process-name tests serially.

```powershell
$srrRun = "qualification-$([guid]::NewGuid().ToString('N'))"
python -B tools/srr013/qualify.py run $srrRun
python -B tools/srr013/qualify.py replay ".local-work/codex/SRR-013/$srrRun/populated.jsonl"
python -B tools/srr013/qualify_budget.py $srrRun
```

Replay checks the seal, exact bounded event order and pinned source, then
re-executes native decoding/classification without opening a process. Old
source pins require their recorded revision. Structural mode can qualify
native presence/resources without the strict effective-input gate. Strict
mode retains conditional tuples when input admission fails and does not
promote them to exact or qualified zero results.

Historical challenges cover false block minima, duplicates in successor
leaves, whole-map alias decoys, typed extent/namespace collisions, PE rebasing,
deadline crossing, value mutation, cancellation and malformed seals.
Map extents are reserved before target decoding. The mapped ImageBase is
checked against the independently obtained module base after rebasing;
remaining PE/code fields must still match. Pair agreement permits ABA or a
stable intermediate clear; no atomic snapshot or lifetime guarantee follows.
The budget-recovery implementation stops cooperatively at returning read
boundaries, retains partial evidence and uses finite work bounds without
claiming hard pre-emption of a blocked OS read. New operator extraction has
no elapsed acquisition deadline. The record-maximum fence assumption is
superseded by native block-minimum routing semantics.

## Historical four-site hardware observer

SRR-006/009/010 source is retained under `srr006/`. It uses native Windows
debug attachment, DR0–DR3 and thread-context writes; it is not a passive
query/read-only observer. `DebugSetProcessKillOnExit(FALSE)` and verified
cleanup are part of its non-killing protocol, not evidence of normal retirement.
No historical run card grants present authority. Current operator extraction
has no Steam/SSH/preflight/one-use approval-file requirement.

Four retail RVAs are `9518FD`, `5932EF`, `77C470`, `779760` in slot order.
A focal invocation requires same epoch/thread lifetime/frame, focal sweep
return, vptr/slot and form/stack predicates at the iterator→callback join.
Allocator arrival needs the accepted PNDT/adapter predicates as well. A plain
site hit is insufficient. Phase markers do not break a still-valid causal
join. `NOT_OBSERVED` requires verified coverage and scientific STOP seal;
interrupted coverage remains `INSTRUMENTATION_INCOMPLETE`. Startup before
arming and productive per-biome stores lie outside this contract.

For disposable rebuilds, use MSVC 14.51.36231 x64 and SDK 10.0.26100.0.
Set `SRR006_SOURCE` to the absolute `tools/srr006` directory and work in a
fresh ignored build directory. Check caller-available C:/D: space per the
[workflow](../docs/research-workflow.md#free-space). The original fixture
recipe is:

```bat
ml64 /nologo /c /Fo frames.obj "%SRR006_SOURCE%\fixture.asm"
cl /nologo /W4 /O2 /EHsc /std:c++20 "%SRR006_SOURCE%\observer.cpp" "%SRR006_SOURCE%\fixture.cpp" frames.obj advapi32.lib /link /OUT:observer.exe /OPT:NOICF
cl /nologo /W4 /O2 /EHsc /std:c++20 "%SRR006_SOURCE%\correlation_test.cpp"
correlation_test.exe
cl /nologo /W4 /O2 /EHsc /std:c++20 "%SRR006_SOURCE%\windows_test.cpp"
windows_test.exe
cl /nologo /W4 /O2 /EHsc /std:c++20 "%SRR006_SOURCE%\retail_profile_test.cpp" advapi32.lib
retail_profile_test.exe "<lawful-analysis-copy>"
python -B "%SRR006_SOURCE%\qualify.py" observer.exe fresh-run
```


Use `/Brepro` additionally when reproducing later deterministic Stage B
binaries; disable ICF with `/OPT:NOICF`. The harness copies the built binary,
writes journals/receipts/markers to the fresh run, and starts only its fixture.
Its watchdog requests exact-child recovery at 35 seconds without completion
and reports unconfirmed recovery at 55 seconds; the 25 ms event wait polls
control input, not a coverage claim.

`qualify_stage_a.py`, `qualify_stage_b.py`, `qualify_d5b_admission.py` and
`qualify_control_b.py` each accept `<observer.exe> <new-output-directory>`.
`compare_d5b.py` accepts baseline and candidate result directories.
`stage_b_marker.py --help` documents durable phase publication;
`verify_stage_b_stop.py` takes capture directory, run token and STOP sequence
only for a run that actually published a scientific seal. D5B sampling works
under delivered held events, avoiding manual running-thread sweeps; debugger-only
Control B installs zero research instrumentation and cannot detect allocation.
Late attach/creation admission, module origin/critical windows, epoch identity,
thread readbacks, STOP prefix and target exit are separate predicates. Owned
attach break-in must be distinguished from unrelated first-chance exceptions;
RF continuation/readback applies to owned research hits. An unknown module
arrival clears affected causal continuity. No incidental Steam component hash
is a universal immutable dependency.

`pin_pe.py <lawful-analysis-copy> --self-test` reads the pinned retail image,
checks call/vtable/unwind/relocation windows and compares the generated header
with tracked `retail_manifest.h`; stdout contains derived hashes/metadata.
It does not write source or game bytes. Native `retail_profile_test.exe`
needs the lawful matching image. [Environment checks](srr008/README.md) have
their own synthetic and private input modes; they are historical observer
support, not current extraction prerequisites.

## Historical file-backed source profile

This superseded acquisition profile remains useful for offline source
comparison and old receipts. It is not a current operator extraction gate.
`python -B -m tools.srr017.source --manifest <new-private-manifest> <plugin-paths...>`
hashes explicitly named lawful ESM/ESP/ESL files and scans top-level
PNDT/BIOM/RSGD/IRES headers; it writes a typed manifest and prints counts/hash.
`python -B -m tools.srr017.probe_namespace <pinned-retail-PE>` verifies the
PE pin and prints decoded namespace/history/VFS locators with Capstone.

`SourceIndex(manifest, namespace)` serves historical owned ordered-winner
tests. The namespace schema is `srr017-namespace-v1`, with `authority` and
ordered `plugins` entries (`index`, `kind`, `plugin`). Bind authority and epoch
independently; reject ambiguous/unsupported/deleted or contradictory records.
`bind_source_files(native_namespace, snapshot)` instead resolves definition
from slot, local master domain and typed signature, leaving winning content
unresolved; source-history contradictions stay diagnostic.

The `srr017-source-files-v1` profile supplies `files` entries with plugin,
absolute path, bytes and SHA-256. `snapshot_source_files` verifies stable
regular-file identity, canonical path and digest, then scans typed headers.
Limits are 256 files, 4 GiB total input, 4,096 groups/file and one million
typed records. Cancellation is checked between at most 1 MiB hash reads.
Duplicate file identities, missing loaded files and path/hash discrepancies
refuse. Snapshot paths/stamps remain private. Portable outputs expose only
basenames, hashes and evidence classes. These bounds describe this historical
profile, not the current operator population/work limits.

Historical owned-title fixtures observed 6/4, 3,600/3,210 and 5,120/4,096
mixed/typed rows, with 16/350/424 source vectors respectively. Namespace
mutation refused despite equal raw rows; invalid slot tags preserved raw
coverage without a normalized source join. Fixture PE SHA-256
`96109beeb4accb823b2b8fe7cc82d6e37be223f80398d7edb02074be934d3ecd`,
qualification report `74fcec91433323658c99a974b2d97ccf8e6c59b350687a9f5eb4c4cd9c05ea47`.
Rebuild using `python -B -m tools.srr017.qualify_title owned-title <new-run-name>`;
it starts only its disposable fixture. Source/native-identity tests use
`python -E -B -m unittest tools.srr017.test_source tools.srr017.test_native_identity`.
No synthetic namespace or disk counterfactual is a retail winning-content
attestation. Current definition-only identity is documented in
[database](../docs/component-database.md).
