# SRR-017 title admission and work envelope

The [native FormID identity correction](SRR-017-identity-correction.md)
supersedes physical ESM provenance release gates. The native work envelope
and original fixture measurements below retain their historical scope.

**PROVEN on owned AMD64 fixtures.** The single-use controller completed
two full collections with an authoritative synthetic FormID table capacity
of 8,388,608. Both collections agreed on every rooted descriptor and every
target's seven words. The controller verified the designated image and
process epoch, used the existing query/read-only backend, and retained a
separate query-and-wait witness for cooperative fixture exit. Both passes
also captured the fixture's native namespace and ordered form-source
witnesses. **Retail
remains blocked.** The tested extent covers a plausible table size for the
two principal source files. Runtime namespace authentication, effective
source completeness and a retail work bound remain release conditions.
[Proposed run card](SRR-017-title-run-card.md)

## FormID map capacity

The lookup slot at `0x145E60EA0` is independent of the retained component
tree. A decoded RIP-reference scan found 667 references, including the two
decoded direct stores below. It did not establish a global absence of
indirect aliases. AMD64 PE hash authentication precedes disassembly.

| Lead | Native evidence | Disposition |
| --- | --- | --- |
| Initial capacity | `FUN_1405DD4C0` gates first-owner initialization with the prior value from `lock xadd` at `0x1405DD567–0x1405DD573`. The call enters `FUN_1405DEA80`. The null-slot guard at `0x1405DEBA9` skips existing publication. The doubling loop reaches `0x40000` at `0x1405DEC0C`, saves capacity at object `+0x18` at `0x1405DEC16`, allocates `capacity × 0x18` bytes and publishes at `0x1405DEC9B`. | **PROVEN STATIC.** A newly allocated table begins at 262,144 entries. The 16,384 SRR-016 limit cannot admit that initialization. |
| Growth | The form construction path calls `FUN_1405E2B30` at `0x1405DD6EF`. The ID-changing path calls the same routine at `0x1405E1CE6`. Its insertion helper `FUN_1405E2C30` takes the growth branch when free entries at `+0x20` reach zero. Capacity doubles for large tables at `0x1405E2D7B`. `FUN_1405E3020` publishes the replacement table and capacity at `0x1405E308B` and `0x1405E3092`. The PE scan found one decoded direct caller of the resize function, at `0x1405E2D81`. | **PROVEN STATIC.** The initial capacity can grow. The inspected growth decision supplies no title-specific maximum. |
| Teardown | `FUN_1405DD800` calls `FUN_1405DEDC0` at `0x1405DD9C9`. The callee handles table cleanup then clears the root pointer at `0x1405DEE67`. | **PROVEN STATIC.** Pointer and extents belong inside each collection's revalidation. |
| Main-source population scale | Independent bounded traversal of each installed ESM's 24-byte record and group headers counted 3,829,247 physical records and 101,341 groups for `Starfield.esm`, and 1,029,529 physical records and 17,747 groups for `ShatteredSpace.esm`. Each contained one zero-ID TES4 header. Each file's remaining FormID words were distinct within that file. | **PROVEN disk counts.** The sum is 4,858,774 nonzero physical records before collapsing any cross-file overrides. It gives a scale for the doubling sequence under this two-file input. It leaves loaded extras, dynamically added forms, alternate form stores and actual title occupancy unresolved. |

The reader claims the table extent using the observed capacity with checked
arithmetic. It hashes each requested FormID into that extent and walks only
its validated chain.
The 8,388,608 bucket ceiling bounds a 192 MiB address claim. Acquisition
requests individual 20-byte occupied entries and the corresponding
validated form fields. This separation makes the capacity extension
independent of the aggregate read budget. The [census topology and native
identity rules](SRR-016-native.md) and the [independent FormID lookup
evidence](SRR-012-acquisition-evidence.md#independent-form-identity) still
govern.

Static reproduction uses [the pinned PE decoder](../tools/srr011/inspect_pe.py)
with Capstone 5.0.7 and `$srrExe` set to the exact matching executable.

```powershell
python -E -B tools/srr011/inspect_pe.py $srrExe scan 145E60EA0 1405DEA80 1405DEDC0 1405E3020
python -E -B tools/srr011/inspect_pe.py $srrExe window 1405DEBA1 101
python -E -B tools/srr011/inspect_pe.py $srrExe functions 1405DD4C0 1405E18A0 1405E2B30 1405E2C30 1405E3020 1405DEDC0
```

For the physical record counts, start at each pinned source file's byte
zero and use its byte length as the outer closing fence. The SHA-256 pins
are `1dabed00c3f4282dd3bb54d2e9601e40b577d8742d078b7ccef203adbfef0da7`
for `Starfield.esm` and
`f8b9333000aba2a4a8a417cb74a11ede6f5b824d27db1918fd1c1f7b64385a43`
for `ShatteredSpace.esm`. Decode each header as `<4s5I`. For `GRUP`,
validate `start + 24 <= start + size <=
containing_end`, push that end and descend immediately after the header.
Otherwise validate `start + 24 + size <= containing_end`, increment the
record count, add the fourth unpacked field to the distinct FormID set if
nonzero and seek to the payload end. Pop fences on equality and refuse
overrun or a nesting depth beyond 32. This procedure skips payloads and
reads installed ESMs as files. It uses no save, installed process or
effective load-order assertion.

## Owned one-use qualification

```powershell
$srrOwnedRoot = '.local-work/codex/SRR-017'
$srrRun = "highmap-$([guid]::NewGuid().ToString('N'))"
python -E -B -m tools.srr017.qualify_title source-manifest
python -E -B -m tools.srr017.qualify_title owned-title $srrRun
python -E -B -m tools.srr017.qualify_title replay-owned "$srrOwnedRoot/$srrRun/direct/title.jsonl"
```

Both entry points need Windows x64 CPython. The owned capture also needs
MSVC x64 and the Windows SDK. It compiles the
tracked C fixture, allocates its synthetic tree and map, and opens only the
owned fixture after checking its image, simulated Steam log and creation
epoch. The source manifest separately pins execution dependencies. Each
fixture-only authorization binds source digest, exact limits, fixture PE
and remap digest, and canonical run directory. An exclusive claim is
flushed before taking a launch baseline. The unchanged SRR-016 marker
protocol consumes a separate token before acquiring one pair. Exit
verification runs the existing [independent watcher](../tools/srr008/watch_exit.py)
on the exact owned PID and creation FILETIME. The observer closes its
read handle before cooperative retirement. Reuse of a passing or failed
claim is refused before another owned launch. The commands write private
build files, simulated tracking logs, summaries, claims and journals and
leave Ghidra unchanged.

The original SRR-016 default stays at 16,384 buckets. Extended owned
receipts record the current reader source identity. Checked replay admits
the one frozen SRR-016 source identity under its original limits and
re-executes the recorded parser operations. A direct historical disposable
receipt passed checked replay. Historical retail SRR-013 journals were
outside this check.

| Fixture | Mixed / target | Pair events / requested bytes | Backend queries / reads / bytes | FormID entry reads / highest bucket | Private journal bytes |
| --- | ---: | ---: | ---: | ---: | ---: |
| Direct root | 6 / 4 | 400 / 21,876 | 496 / 416 / 27,476 | 64 / 8,144,517 | 110,598 |
| Corpus shaped | 3,600 / 3,210 | 6,528 / 2,998,028 | 6,624 / 6,544 / 3,003,628 | 1,400 / 8,372,476 | 15,010,140 |
| Upper | 5,120 / 4,096 | 8,876 / 7,739,476 | 8,972 / 8,892 / 7,745,076 | 1,696 / 8,372,476 | 27,202,495 |

The controls asserted the separately constructed raw keys and slot words
in both passes. The traces contained six table metadata checks and bounded
entry reads within the larger extent. Namespace drift between passes and
a malformed slot both preserved raw graph agreement and withheld a
normalized result. A lowered entry count and a lowered capacity ceiling
each refused deterministically. Cancellation retired the attempt before
collection. The journal ceiling case left 17,607 pending
bytes, an already consumed authorization and no published receipt. Six
wrong authorization fields and one modified replay claim refused. The
separate owned exit witness recorded signaled status and exit code zero.
The existing [synthetic preflight controls](../tools/srr008/test_preflight.py)
passed 10/10 without any access to protected Starfield save namespaces.

| Reproduced artifact | SHA-256 |
| --- | --- |
| Owned execution source manifest (canonical JSON digest) | `167ac0480ec392c1dbc00291836380a359569f5a7226c1b6d4401b8cb96b8c32` |
| Owned work manifest (canonical JSON digest) | `4a5dd9676ffdd21c638c99770687b2e7a2eaa2272fa1e5bab3b47680524165a5` |
| Fixture PE (MSVC 14.51.36231 and SDK 10.0.26100.0) | `96109beeb4accb823b2b8fe7cc82d6e37be223f80398d7edb02074be934d3ecd` |
| Qualification receipt | `74fcec91433323658c99a974b2d97ccf8e6c59b350687a9f5eb4c4cd9c05ea47` |

## Retail release gaps

These are the release gaps at the original owned qualification. The
[continuation](SRR-017-retail-readiness.md) records the integrated
candidate, updated limits and current status.

The demonstrated caps are 5,120 mixed records, 512 windows, root level
4, 8,388,608 table buckets, 4,096 visited map entries, 256 chain entries,
32 BIOM RSGDs per list, 8,192 remap entries, 40,000 pair events, 16 MiB
in requested pair bytes and a 64 MiB private journal. At the measured
upper case, the tree used 472 windows. The native window width is 4,064
bytes, so four complete read plans at the window cap request 8,323,072
tree bytes. A consumed FormID entry plus its header can request 27 bytes
per plan. The exact combined budget includes form fields, opening and
closing anchors, private replay evidence and separate output. At the
owned caps, the backend allows up to 40,100 region queries, 40,020 memory
reads and 17,105,376 requested bytes. An exhausted bound stops the attempt
and preserves the diagnostic state or unpublished prefix.

The pinned retail image profile checks five mapped windows including the
PE header and four instruction windows. It also checks twelve fixed RVA
regions. The constructor, explicit marker-binding identity and four pair
brackets would therefore add at most 132 region queries, 30 process reads
and 393,906 requested bytes to the pair budget. A retail candidate must
account additionally for independently authenticated namespace lookups,
image file hashing and Steam attribution. The existing backend bounds a
process census at 32,768 entries, a Steam log tail at 4,096 bytes, an
append at 1 MiB and the module buffer at 1,024 entries per identity.
These are per-operation bounds. The future command must fix the maximum
identity and namespace operations, plus its closeout and output limits.

The implemented owned bounds contain both measured tree shapes and a
large FormID table extent. There is no affirmative static bound that all
retail mixed descriptors or consumed FormID-chain entries fit those caps.
The blocked retail lead can proceed with a reviewed bound for the effective
source set and a pair of epoch-bound runtime namespace witnesses. A runtime
overrun would leave the attempt indeterminate and require separately
approved changed limits. The implemented command performs no live
admission and cannot emit a retail-qualified dataset.
