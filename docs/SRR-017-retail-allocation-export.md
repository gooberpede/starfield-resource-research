# SRR-017 retained allocation export and retail readiness

This dossier records the original owned qualification. The
[retail readiness continuation](SRR-017-retail-readiness.md) records the
subsequent command, source-binding scope and current release decision.

**BLOCKED for a retail authorization request.** The offline candidate
produces a complete identity-resolved dataset for owned fixtures through
the rooted +0x300 reader, checked receipt replay and a typed source join.
The pinned retail executable implements three loaded plugin index domains
and a FormID map that grows beyond the SRR-016 fixture cap. The owned
title profile acquires and replays namespace and typed-form provenance
in the same pair. The retail candidate still needs effective loading
attestation, reviewed total limits, and an exact retail invocation.
No Starfield launch, live process access, title observation or save access
occurred in this phase.

[Proposed run card](SRR-017-title-run-card.md) ·
[Interchange v1](SRR-017-interchange.md) ·
[Source ID evidence](SRR-017-source-identity.md) ·
[Owned admission and limits](SRR-017-title-admission.md) ·
[SRR-016 baseline](SRR-016-whole-store-census.md)

## Starting state and boundaries

| Item | Identity |
| --- | --- |
| Research HEAD and branch | `70238677b1b404b6b0b9b78e6d79a3ba92f64064` on `main`, empty index |
| Pre-existing worktree input | Untracked SRR-017 brief, SHA-256 `e900ba442964ec8182f0135a9d0e106e0d9d708aff49067367d97ede54d7e986` |
| Sibling | Clean at `a8ff1c788bca415f571f06769ab3e712fa674f75`, package 1.0.0 |
| Installed image | On-disk version 1.16.244.0 and SHA-256 `7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28` |
| Test runtime | AMD64 Windows, CPython 3.14.3 SHA-256 `cce21c0e8710e304273e98ac4b2b0f5aceb639acbcd2343cbaa5c4e81619c45b` |
| Available space at entry | C: 88,235,999,232 bytes and D: 68,336,984,064 bytes, each above the 40 GB floor after projected disposable writes |

The only scientific population is the root-reachable mixed allocation
store observed at the checkpoint. The registration witness discriminates
every target regardless of its owner. The reader derives PNDT and BIOM
identities from the native key and typed form lookups, and rechecks
publication, visited extents and authoritative form witnesses. The output
preserves zero lanes and zero rows, and separately records count and
pair disagreement with original bytes in private custody. Equality is
endpoint evidence and permits intervening mutation, including ABA.
[Native contracts](SRR-015-native-extraction.md) ·
[Historical title-card evidence](SRR-013-retail-title-paired-structural-observation.md)

The source join is a post-acquisition step. It partitions runtime IDs
using the witnessed scale/index and looks up the local ID in the typed
file inventory. The existing SRR-016 oracle and conditional expected
population are consumers. Neither is a filter, a source of resource
values, or authority for the effective plugin population. No reproducer
change was needed. [Interchange](SRR-017-interchange.md) ·
[Existing oracle applicability](SRR-016-oracle.md)

## Material leads and disposition

| Lead | Work and evidence | Result or next required check |
| --- | --- | --- |
| Source namespace | Followed Papyrus file/ID lookup registration, native mask formatter and inverse diagnostic, and independently scanned pinned ESM record headers. | Native full/medium/small slot decoding is established. The owned pair captures and replays the compiled namespace and per-form source vectors. The effective loaded retail paths and file hashes still need an admissible witness. [Source identity](SRR-017-source-identity.md) |
| Source winner and relevant extra plugins | Checked stock masters and target-bearing extra plugins offline. Examined native metadata for file provenance. | An installed file cannot establish that it was loaded or that it won an override. The source dossier describes the precedence evidence and supported/refused cases. [Source identity](SRR-017-source-identity.md) |
| FormID table capacity | Followed the first construction guard, map initializer, insertion/growth callers and teardown. Exercised a large sparse table and refusal using an owned AMD64 process. | Initial retail capacity is 0x40000 and the growth path doubles it. Extent claims and actual entry reads are independently bounded. A retail envelope still needs a defended allowance for effective inputs and the integrated namespace/retail identity call costs. [Owned admission](SRR-017-title-admission.md) |
| Complete useful output | Exercised direct, multilevel, empty, full-lane and unexpectedly present owner cases. Replayed both full passes and tested an independently authored source inventory with a missing resource record. | Every accepted fixture row carries canonical identity and seven words. Missing identity retains the raw row and withholds qualification. A corrupt mixed prefix and a refused target have separate counts. [Interchange](SRR-017-interchange.md) |
| Comparator portability | Projected and parsed every qualified key and slot through the unchanged SRR-016 observation parser. Challenged projected row deletion and mismatched runtime witnesses. | Count conservation and typed witness checks refuse those edits. Effective-input and full oracle coverage remain later comparison questions. [Interchange](SRR-017-interchange.md) |
| Protection and exit | Reused the tracked protection checker's synthetic suite. Ran the independent query/synchronize exit witness on an owned child with exact creation token. | Retail protection remains an operator gate under separate approval. The inspected run card specifies both namespaces, all pair/designation checks, pre/post reconciliation and normal Quit. [Run card](SRR-017-title-run-card.md) |

## Verification

The tests use synthetic native processes and scratch outputs. Use disjoint
fresh run names under private custody. The first command builds the native
fixture and produces sealed census journals. The second separately tests
owned title admission, one-use claims and the larger map geometry. The
third replays both suites, builds an independently authored typed header
fixture, checks every field against the reference and produces both forms
of portable JSON. The commands leave Ghidra untouched.

```powershell
python -E -B -m tools.srr016.qualify_census $censusRun
python -E -B -m tools.srr017.qualify_title owned-title $titleRun
python -E -B -m tools.srr017.qualify_export $censusOutput $newExportOutput --owned-admission $titleOutput
python -E -B -m tools.srr016.qualify_oracle -v
python -E -B tools/srr008/test_preflight.py
```

The census tool prints the outcomes and writes its journals to the named
ignored run directory. Set `$censusOutput` and `$titleOutput` to the newly
produced named run directories. The updated census exercised 60 native
controls, eight tamper controls and one remap preflight refusal. The new
cases include a window crossing adjacent readable regions with different
protection, cancellation of the second collection with a complete first
pass retained, and a direct-root row with all seven fields populated.
The oracle's 28 tests and the protection checker's 10 synthetic tests
passed. Run the historical disposable
[SRR-013 inspector](SRR-013-read-only-allocation-state-inspector.md),
[retail admission simulator](SRR-013-retail-readiness-continuation.md),
[structural simulator](SRR-013-structural-state-observation.md) and
[budget simulator](SRR-013-live-observation-budget-recovery.md) from a clean
checkout with fresh names. All four completed here. Historical retail
journals were unnecessary. The sibling passed all 183 tests, including the
canonical 1,444/1,444 exact assertion. Its validation-only output checked
7,780 rows, including 7,445 BIOME and 335 ATMOSPHERE. The previous 10/10
holdout remains historical. [Sibling rerun workflow](SRR-016-oracle.md#comparator-and-offline-verification)

| Owned case | Mixed | Qualified rows | Exact checked lane words | All-zero rows | All-seven rows |
| --- | ---: | ---: | ---: | ---: | ---: |
| Empty rooted store | 0 | 0 | 0 | 0 | 0 |
| Direct root | 6 | 4 | 28 | 1 | 0 |
| Direct root with all lanes | 6 | 4 | 28 | 1 | 1 |
| Corpus multilevel | 3,600 | 3,210 | 22,470 | 189 | 0 |
| Upper multilevel | 5,120 | 4,096 | 28,672 | 241 | 0 |

The independent checks compare each raw key, canonical PNDT/BIOM and
resource ID, native ordinal and role, typed input and payload metadata.
The exceptional owner contributes its ordinary observed row. With a
missing source ID, a disagreement or an incomplete second pass, the
export retains diagnostic rows and supplies an indeterminate comparator
projection. The original receipt remains the replay authority.
The combined owned title profile also checked the namespace and
per-form vectors for every typed reference in the direct, corpus and
upper cases. It refused changed namespace identity, an invalid native
slot tag and a contradictory offline source index while preserving
the available raw rows.

| Retained qualification evidence | SHA-256 |
| --- | --- |
| Combined owned title qualification summary | `74fcec91433323658c99a974b2d97ccf8e6c59b350687a9f5eb4c4cd9c05ea47` |
| Per-field export and projection summary | `9f0321ccc0280376c1295c90a3d4cbfd7b1423c213ab51f352f3a4f272dc9362` |
| Unchanged SRR-016 comparator output for the combined owned corpus | `37a751a3bed63078a0141120b69a76e0dd471b3ce90d2e03a81d2c13c4f009a9` |

The unchanged SRR-016 comparator accepted the owned corpus projection
with 3,600 mixed descriptors, 3,210 admitted targets and 189 all-zero
rows. Regenerating its independent freeze reproduced the existing
ledger and oracle digests. The comparator reported
`RETAIL_APPLICABILITY_UNRESOLVED` for effective inputs and
`INDETERMINATE` for population and values.
[Comparator command and independent receipt pin](SRR-016-oracle.md#comparator-and-offline-verification)

## Authorization decision

| Decision | Required evidence |
| --- | --- |
| **READY TO REQUEST LIVE AUTHORIZATION** | One final command and manifest set passes the owned equivalents of Steam attribution, title marker, capture and exit. A bounded epoch-bound native witness covers defining identity for all needed FormIDs and participates in both collections and sealed replay. Reviewed work limits cover effective-source, OS admission, whole-tree, reachable map, evidence and closeout costs. The run card binds the approved preservation procedure and custody. |
| **BLOCKED (current)** | The owned command pairs and seals the namespace, source vectors and rooted reads. An exact retail invocation with a verified method to join loaded paths to file digests is still missing. The total backend envelope for the effective profile needs qualification. Supply that invocation and rerun its exact disposable equivalent before requesting a launch. |

The current patch is suitable for maintainer review and owned
reproduction. It does not change the allocation algorithm or prior
retail observation records. Keep executables, native evidence,
protection receipts and independent review files private. A retail
command, a second attempt or a changed work envelope would need a
separately reviewed single-use authorization.

Execution manifests are hashes of the actual checkout bytes. Reverify
them in the intended execution checkout because line-ending conversion
can change those bytes.

The first useful retail dataset requires defining plugin and local ID,
the typed native fields and observed source vectors. A retail path must
label unresolved winning bytes where precedence remains uncertain. The
comparison can settle applicable winners and model inputs offline using
the retained evidence.

<!-- srr-017-review:start -->
**Owned qualification accepted. Retail authorization request BLOCKED.**
An independent internal challenger verified 20 final source and
documentation files against manifest SHA-256
`01fb54136f21e907a3dd760cabee5da10fcf66789954c87fbc2dc41bd0c61a8f`.
Each manifest line records the file SHA-256, two spaces and the
repository-relative path, sorted by path and terminated by LF. Only the
body of this marked block is excluded from the dossier's file hash.

The challenger inspected the final code and run card, reproduced seven
byte-level, identity and adapter controls, and checked the combined owned
process seal, namespace drift and invalid slot tag against independently
authored ESM bytes. The adapter preserved a composite raw key above 2^53.
The source challenge independently verified 16 direct-case native
source vectors, both passes of each namespace refusal, and rejection of
resealed read or report tampering. The final independent review receipt
SHA-256 is `e63c1a5db1504ead82f5e3699e3136fd71b60998f73f4a67629750ff68dfd202`.

The ending executable and two principal ESM byte hashes matched their
pins. Research HEAD and the empty index remained at their starting
state. The pre-existing untracked implementation brief was preserved
verbatim and excluded from the task-only patch. The sibling stayed clean
at its starting commit. Raw journals and review artifacts remain private.
<!-- srr-017-review:end -->
