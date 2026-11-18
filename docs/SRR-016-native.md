# SRR-016 whole-store reader

**PROVEN on the owned disposable profile.** The complete rooted traversal
reconciles the mixed header, physical descriptor positions and typed target
denominator for the qualified fixture layouts. A paired result includes
separate graph and seven-slot decisions. The current retail operator entry
point and separately requested live boundary are in the
[SRR-017 run card](SRR-017-title-run-card.md). The original SRR-016 entry
point remains an owned-process qualification and offline replay interface.

## Reachability and identity

```text
authenticated AMD64 process epoch and source
    published context → mixed header +0x300
                             ├─ null root and zero count
                             ├─ direct packed block
                             └─ branch levels → leaf directories
                                                    │   ↔ previous / next leaf
                                                    └─ ordered packed blocks
                                                        └─ descriptor positions
                                                          └─ prefix + inline payload
    type registration → target discriminator and wrapper check ─────┘
    independent native FormID map → PNDT, BIOM, RSGD, resource witnesses
    independent ID manifest → canonical PNDT/BIOM pair and seven lanes
```

The arrows represent navigation and validation dependencies. They carry no
claim about startup order or the writer's execution. Each target's inline
payload lies in its packed block. The looked-up forms are separate allocations.
Extent claims cover the complete tree windows, context, registration metadata,
FormID table, consumed form extents and BIOM pointer lists. No block, leaf
or branch window can occupy a second root-derived position.

```text
read authenticated publication, registry, mixed header and FormID map
require root/count consistency and admit the independent limits
if root is a packed block, visit it as the entire tree
otherwise walk every used root-derived child position in ascending order:
    require level decrement and separator order
    require routing pivots/block minima within inclusive ancestor bounds
    at a leaf, cross-check both directions of the root-derived leaf adjacency
    for every block position, validate layout and exact advertised minimum
at every block:
    validate descriptor directory/frontier and disjoint occupied spans
    reconcile free holes with occupancy credit
    visit each record in directory order and require increasing global keys
    test registered discriminator and exact wrapper in both directions
    classify a non-target prefix or validate the entire typed target
require null terminal leaf link and exact mixed/target/exclusion counts
independently reconstruct canonical ordering from privately retained raw keys
re-read consumed windows and anchors, then close process/image bracket
```

The geometry comes from the pinned retail lower bound
`FUN_1403832A0`, block selection `FUN_1403833E0`, cursor continuation
`FUN_1424103E0` and record advance `FUN_1403A4250`. The external traversal
enumerates every child instead of calling the keyed reader. On a finite
admitted graph, every edge has a single root-derived descriptor position.
At each node the child array bounds this induction. Leaf links and header
count provide independent reconciliation. The cursor's terminal +0xFE0
denotes an exclusive block boundary. No descriptor or payload starts there.
[Native topology](SRR-012-acquisition-evidence.md#exact-mixed-index-model) ·
[Census derivation](SRR-015-native-extraction.md#whole-tree-read-contract)

## Separator semantics

**PROVEN STATIC:** keys are unsigned `(u64 word0, u64 word1)` pairs ordered
lexicographically. Internal lower-bound chooses the first pivot `>= query`,
with equality on the left. Leaf keys advertise packed-block minima; exact
match selects that block, otherwise lookup can choose a predecessor in the
same or previous leaf. The record cursor continues through blocks and leaves.
`FUN_1403835E0` promotes the final left block minimum during a leaf split;
that block's subsequent records may exceed the pivot. See the
[exact native locators](SRR-012-acquisition-evidence.md#separator-meaning-and-packed-records).

```text
for each ancestor (pivots S, child i):
    lower = S[i-1] if i > 0 else -infinity
    upper = S[i]   if i < len(S) else +infinity
    require lower <= each routing pivot / block minimum <= upper
for each packed block in complete root order:
    require first_record_key == advertised_block_minimum
    require every record key > the previously visited record key
    # Its last record need not be <= an ancestor pivot.
require complete count reconciliation, leaf links, consumed-window stability
require independent second collection and identity/value/coverage agreement
```

The census still checks every node's pivots and every packed minimum against
all ancestor fences; it has not disabled `index_fence`. Its global strict
record ordering rejects overlap/duplicates across blocks, leaves and internal
subtrees. **PROVEN on disposable fixtures:** inclusive routing bounds permit
both endpoint equalities and a pivot between the last left-subtree block
minimum and first right-subtree block minimum. This is a navigation-derived
external admission contract, not a claim that the native writer was observed
producing every such pivot. Exact equality to a child's extremum is not
imposed as an additional reader assumption.

The shared SRR-013 selected-key reader applies the same minimum-only fence,
then bounds a block's final record by the **actual next block minimum**,
including a next leaf derived from the root rather than trusted links alone.
It preserves its nondecreasing boundary check and duplicate-component
classification. Predecessor coverage checks, root-backed neighbors, native
record/type checks and selected-range coverage remain. Selected-key
qualification is distinct from whole-store completeness.

The retail diagnostic counterexample has a 14-record block at path `[0, 83]`:
its first key equals the level-one child-0 upper pivot; later keys exceed it.
That boundary is native-supported. Its receipt still ends after only 1,202
mixed descriptors and 1,165 raw targets, before closure, namespace resolution
or the second collection. Frozen source `8a963710` reproduces `index_fence`.
The corrected checked prefix passes that block but needs an uncaptured read
at operation 4,252. Current strict replay refuses its old source identity.
No altered seal, fabricated read or retrospective qualification is allowed.
The historical observation remains `ACQUISITION_INDETERMINATE`.

The decoder compares the wrapper to `image+0x4B3D258` and the low u32
of key word 0 to `0x10000 | discriminator`. The owner is the high u32 of
that key. The second u64 must equal the nonzero inline BIOM u32. Agreeing
target signals require a 0x90-byte record. Disagreeing signals stop the
walk and preserve the attempted target. A blank mixed prefix also stops the
walk. Other mixed types are classified as exclusions by the readable key
and wrapper signals. They receive no semantic type assignment. A valid free
hole contributes to occupancy credit, with zero descriptor positions.

The independently rooted FormID join uses the little-endian FNV-1a hash
and capacity sentinel from `FUN_1405ACAD0`. Each lookup checks the complete
chain through termination. It validates traversed decoy headers and refuses
duplicate keys, object aliases, cycles, invalid successors and invalid table
references. The witness covers consumed chain entries. The live map may
contain unrelated entries beyond those chains. Every target requires a
type-0xBA PNDT whose +0x54 key agrees, a type-0xA0 BIOM and its ordered
type-0xAB RSGD pointer witnesses. A completed optional override lookup with
no form or with an incompatible type is recorded as null resolution and
an applicability limitation. Every nonzero lane resolves independently as
type 0x9F with the BGSResource vptr. The raw lane order is seven little-endian
u32 words at edge +0x70..+0x88. A fully zero vector remains present.
[Independent form identity](SRR-012-acquisition-evidence.md#independent-form-identity) ·
[Typed targets](SRR-015-native-extraction.md#population-and-identity)

Canonical IDs come from the independently supplied, one-to-one remap.
Each typed row is normalized in native slot order and then sorted on
canonical owner and target. A second reconstruction starts from the raw
descriptor keys. A missing namespace can leave the independently typed
runtime census complete and prevents a normalized release. Evidence
for retail FormID-to-plugin remapping remains a prerequisite for the
canonical profile.

## Pairing, refusal and limits

The fixture runner uses SRR-013's least-rights Windows reader, ownership,
mapped-image/epoch check, simulated Steam attribution and one-use title
marker. It starts the two collections from fresh publication, graph and
form witnesses. It rechecks each read window and closes the identity
bracket in each pass. Separation between the closed first bracket and
opening second bracket is at least 25 ms. Tree shape and payload fields
other than the seven slots contribute to the graph digest. PNDT, BIOM and
RSGD input paths have a separate digest covering the input chains and
selected form fields. Exact raw lanes and the complete reread digest
follow these graph and input checks. A pair with the same graph and
typed inputs and differing raw lanes yields a qualified graph result
and an indeterminate allocation-value acquisition. An exhausted limit,
unreadable range, conflicting identity, changed witness or failed bracket
cannot produce a qualified normalized export.

Private diagnostics include attempted targets, descriptor positions,
prefixes, typed references, a complete or failed witness, bracket details
and raw slot bytes. They remain under ignored `.local-work/`. The journal
keeps pending bytes if durability fails. Checked replay verifies source and
remap identities, canonical event encoding, requested operations, timings,
gap, counters, report and seal. A pre-admission Windows refusal is an
attestation recorded during acquisition, with no process-read trace to
reproduce. The seal verifies internal agreement and integrity against
the retained hash; it supplies no external signature.

The independently generated corpus-shaped fixture uses 24 records per
block and seven blocks per leaf, with branch fanout four. Its 3,600 mixed
rows require 150 packed blocks, 22 leaves and 9 branch nodes. The upper
fixture uses 13 records per block and the same leaf sizing. Its 5,120
mixed rows require 394 blocks, 57 leaves and 21 branch nodes. The private
fixture's 512-window budget leaves margin over this 472-window layout
while guarding against unexpectedly sparse or malformed graphs. The
maximum root level of 4 is achieved by the upper fixture. Native geometry
limits a packed block to 112 minimum-sized records and an internal node
to 169 children. Shape and per-stage caps apply independently.

The owned-profile work limits are 5,120 mixed records, 512 tree windows,
root level 4, map capacity 16,384, 4,096 distinct visited map entries,
256 entries per lookup chain, 32 BIOM RSGD references per list, and
8,192 independent remap entries. The node window width is 4,064 bytes.
The two collections and complete rechecks use at most four window plans,
or 8,323,072 tree bytes at the window ceiling. Each distinct map occupant
can add a 20-byte entry and a 7-byte object header per plan. Additional
known-width form reads, ledgers, anchors and rechecks consume the common
40,000-event and 16 MiB pair ceilings. The receipt cap is 64 MiB,
including hex expansion, operation overhead and private rows. Each cap is
a refusal boundary. Simultaneously reaching every subordinate limit need
not fit the shared budget.

The owned runner meters `VirtualQueryEx` and `ReadProcessMemory`
attempts before dispatch. Caps include admission and up to four bracket
identity calls. Each identity permits up to four mapped windows with
two query operations per window and twelve fixed RVA checks. The resulting
backend maxima are 40,100 region queries, 40,020 process reads and
17,105,376 requested process bytes. Reader-level operations and replay
report counters are tracked separately. Operator cancellation is polled
at read boundaries and in cached traversal, chain and projection work.
Synchronous OS calls and bounded report serialization can delay retirement.
There is no elapsed-time acquisition deadline.

| Fixture | Mixed / targets | Tree windows | Pair events / requested bytes | Backend queries / reads / requested bytes | Journal bytes |
| --- | ---: | ---: | ---: | ---: | ---: |
| Direct packed | 6 / 4 | 1 | 304 / 19,300 | 400 / 320 / 24,900 | 96,194 |
| Corpus-shaped | 3,600 / 3,210 | 181 | 5,096 / 2,992,780 | 5,192 / 5,112 / 2,998,380 | 14,877,496 |
| Upper | 5,120 / 4,096 | 472 | 7,148 / 7,733,636 | 7,244 / 7,164 / 7,739,236 | 27,043,656 |

The measured upper pair took 0.82 seconds on this host, including the
gap. Timing describes the fixture and carries no validity threshold.
Reads wider than one readable VirtualQueryEx region refuse under this
backend. A retail region-boundary or capacity discrepancy requires separate
qualification. None of these measurements supplies a retail population,
performance or FormID-map capacity guarantee.

## Reproduction, controls and limits of interpretation

```powershell
$srrRun = "native-$([guid]::NewGuid().ToString('N'))"
python -B -m tools.srr016.qualify_census $srrRun
python -B -m tools.srr016.qualify_census --replay ".local-work/codex/SRR-016/$srrRun/direct.jsonl"
```

Use a fresh first-command run name. Qualification uses 64-bit Windows,
Python 3.14.3, MSVC x64 toolset 14.51.36231 and Windows SDK 10.0.26100.0.
It reads the synthetic C source and the owned process, stages no repository
paths, and writes fixture binaries, simulated log writes, private receipts,
summary and normalized disposable exports to the named ignored directory.
Replay reads the named sealed receipt and emits sanitized observation JSON
to standard output. Neither command opens or changes a Ghidra project.

All 57 owned-process controls passed and reproduced exactly by checked
replay. The 12 positive and scope controls included empty, direct, valid
holes, multilevel mixed, corpus-shaped and upper layouts, valid decoys and
a long chain, known-null optional override, stable clears, ABA and an
unresolved remap. The separately constructed C descriptor truth and
Python sorted key/slot reference agreed with both full passes. A legitimate
exceptional owner appears independently of any comparator ledger. The
negative controls include malformed fences, minima, blocks and links;
separator duplicates; shared children; prefix and typed identity failures;
map corruption and aliasing; short and unreadable reads; mid-read insert,
delete, repack, address reuse and slot rewrite; paired value or graph
disagreement, combined PNDT seed and raw-slot drift, cancellation in cached
work, and finite work exhaustion including a lowered BIOM list cap.
Eight resealed or pending receipt challenges and one separate contradictory
remap preflight control passed.

Stable clears and the inter-pair ABA control intentionally qualify at the
boundaries. Paired equality can coexist with a stable intermediate value,
intervening mutation or non-atomic publisher behavior. Rooted coverage
supports absence within the enumerated graph only. Pending queue work,
orphans and other stores remain outside the observation.

| Artifact | SHA-256 |
| --- | --- |
| Reader source manifest | `c813eb4bff937c475b07debb907aa45a22ecd55c78f6fc0931476f8975b803bd` |
| Fixture source | `f5d745634028c586491424712ba3173f5683876fa066a6cb896485796d724665` |
| Fixture PE | `b22098cfb84453c24c899240b06ca3b48536cae4b556ee6c6bffa9e1acd93c16` |
| `qualification.json` | `5ce7041faf589f1d3fb46de615ac577f3299e12d8af09af4152c8dcac64a13b1` |
| `direct-observation.json` | `14545df99af8ff479e866b6679969cadf66c978b930cb08ad06dfb561be8d598` |
| `corpus-observation.json` | `ed3045e3bcb943ca77a95a7e28ad56f38f5cc1727705dd89ccca64ba0051712d` |
| `upper-observation.json` | `bf609cd82029fcab22a2bb404ff67f1a2c8372cdf35c46115595d27abbf8451e` |

The table identifies the recorded fixture outputs. The tracked commands
produce a new summary, receipts and normalized exports. Per-attempt
receipts carry process epoch addresses and remain private. The [main dossier](SRR-016-whole-store-census.md) records cross-layer
readiness, legacy replay and review.
