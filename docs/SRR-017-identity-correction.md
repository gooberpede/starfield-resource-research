# SRR-017 native FormID identity correction

**Current contract.** The operator starts Starfield, holds the responsive
title card and explicitly requests extraction. The command reads an already
running compatible process; it never launches or closes the game. This
implementation task authorizes offline qualification only. See the
[run card](SRR-017-title-run-card.md) for the current invocation.

**Latest live result: FINISHED — QUALIFIED.** Two complete title-card
collections reconciled all 18,314 mixed descriptors and agreed on 3,211
identity-resolved Planet → Biome rows and all seven resource slots. The
prior incomplete observations below retain their original classifications.

## Scope and implementation

The command is `python -E -B -m tools.srr017.extract --output DIRECTORY`.
It selects the unique compatible Starfield executable, or the operator's
`--pid` when multiple compatible processes exist, and reports the selection.
It authenticates the executable/layout and creation epoch through the
existing query/read-only interface. It obtains one pair of independently
rooted full-store collections and checks the sealed receipt before export.
No launch, Quit or automatic acquisition retry occurs.

**PROVEN STATIC:** the pinned native writer promotes a left leaf's final
block minimum; lookup can route right and select a previous-leaf block.
The corrected census therefore applies ancestor fences to routing pivots
and block minima, not later records in a packed block. It still checks
strict global record order, advertised minima, node routing, links and
counts. The shared selected-key reader additionally checks the actual next
block minimum across root-derived leaf boundaries. The former record-maximum
fence is **SUPERSEDED**, rather than suppressed on one anomalous path.
[Native rule and exact locators](SRR-012-acquisition-evidence.md#separator-meaning-and-packed-records) ·
[Checked separator contract](SRR-016-native.md#separator-semantics)

The full/medium/small loaded-plugin namespace is checked against TESFile
flags, indices, names and the native registry. PNDT, BIOM, RSGD and resource
IDs retain their native map, stored-ID, type and resource-vptr validation.
Invalid or conflicting assignments, duplicate identities, incorrect types,
incomplete coverage and inconsistent observations refuse qualification.
Every qualified Planet/Biome row retains native and normalized identities
and all seven resource slots, including zero slots and all-zero rows.

Defining-record identity is distinct from winning-content attribution.
Physical ESM paths, provider witnesses, handles and hashes are outside the
acquisition requirements. A relative `DATA\` directory is valid. Optional
source history is diagnostic; unreadable or contradictory history alone
cannot invalidate defining identity. Exhausted work, cancellation, process
exit, changed epoch and evidence failures stop acquisition. Oracle data is
not read during acquisition.

## Operational prerequisites and work

| Remaining condition | Purpose |
| --- | --- |
| Operator-held title card and explicit current request | Defines the intended checkpoint; the tool cannot prove UI state. |
| Compatible executable/layout and stable process epoch | Makes fixed-address interpretation applicable to the selected process. |
| Query/read access and readable native structures | Obtains evidence without target writes. Ordinary access failure is reported. |
| Published DB, rooted census, native identity/type checks and agreeing pair | Establishes the admitted store's coverage, identity and values. |
| Finite read, tree, namespace and output limits; cooperative cancellation | Bounds work and evidence size without an elapsed acquisition deadline. |
| Writable ordinary output filenames and checked sealed replay | Retains evidence and reproduces the scientific decisions. No special directory or one-use credential is required. |

Operator receipt v2 has no independent descriptor-count, tree-window,
reached-map-entry, map-capacity, BIOM-RSGD-count or plugin-registry-count
ceiling. The published
count never sizes an allocation: bounded blocks are read, each descriptor
is validated, and the complete traversal must reconcile with that count.
Strict order/fences, unique ownership/extents, leaf links, native FormID
map/type/vptr checks, consumed-window rereads and paired agreement remain.
The map's native power-of-two capacity and pointer extent still validate.
RSGD pointer lists are read in 512-pointer chunks, each member is checked
through the native map, and repeated checked lists share their collection
witness. A large declared count cannot cause a bulk allocation.

| Retained work bound | Purpose |
| --- | --- |
| 4,000,000 pair operations; 512 MiB requested memory | Bounds actual reads and retained memory witnesses, independently of declared population. |
| 1 GiB raw journal; 512 MiB per portable output | Bounds retained evidence and export size; the former 128/64 MiB caps were insufficient for large qualified populations. |
| Tree depth 64 | Protects the recursive reader's stack while child levels, ownership and fences independently validate structure. |
| 65,536 entries per FormID chain | Bounds per-lookup cached-chain computation, which may perform no fresh reads; cycles and conflicting IDs remain invalid. |
| 4,605 compiled plugin slots; 32,768 reads / 16 MiB per namespace | Covers the full native full/medium/small index space. Registry growth is bounded by actual reads/bytes and cycle/alias checks, without an independent file-count ceiling. |

Backend query/read caps are derived from the pair-operation/byte budgets
plus the existing eight image-identity brackets; executable hashing and
process enumeration retain their separate finite bounds. Optional history
limits remain diagnostic and cannot block defining identity. There is no
independent target-row ceiling or elapsed deadline. The 25 ms minimum
separation remains a gap between fresh collections, not a deadline.
Historical receipt profiles retain their original limits and must replay
with their pinned source version; new operator v2 receipts use the current
source and explicit work manifest. No alternative safety infrastructure
or new admission condition is introduced.

Steam registry, parent/session/log attribution, authorization records,
claims, signatures, preflight/postflight, saves, overlays/Cloud, disk floors,
exit witnesses and administrative infrastructure are not consulted by this
command. Older admission/run instructions are superseded for new captures.
No alternative infrastructure replaces them. Output write errors are
ordinary failures. Useful raw/partial evidence is retained where possible.
The Ghidra project and game/save files are not modified.

The claim is two agreeing complete collections of the admitted rooted store
in one epoch. It establishes neither atomicity nor intervening mutation
absence, completed allocator execution, all-galaxy coverage, or oracle
agreement. A partial or identity-unresolved result is never qualified.
[Interchange](SRR-017-interchange.md) ·
[Native identity evidence](SRR-017-source-identity.md)

## Qualification and independent review

The corrected operator controller passed 46 owned-process controls on
Python 3.14.3. Native-shaped direct/root-leaf/two-leaf/multilevel/cross-node
cases include pivots equal to final left block minima while later records
exceed them. Synthetic pivot gaps and right-minimum equality also qualify
as navigation-compatible fixture geometry; they are not claimed as observed
retail writer states.
Misplaced pivots/minima, descending/duplicate/overlapping records, wrong
separator order, links, counts and aliases still refuse. Complete paired
acquisition, normalization, export and replay were repeated at population
scale using the native promoted-minimum geometry. Every target's keys,
metadata and seven words were independently asserted.

| Mixed descriptors | Qualified target rows | Slot words | All-zero rows | Tree windows / reached map entries per pass |
| ---: | ---: | ---: | ---: | ---: |
| 32,768 | 24,576 | 172,032 | 1,446 | 3,007 / 2,130 |
| 65,536 | 49,152 | 344,064 | 2,892 | 6,008 / 12,371 |

The larger case used 205,452 pair operations, 99,467,384 requested bytes,
a 349,431,403-byte journal and 184,963,882-byte portable dataset. The
operation/read/journal/output bounds have respectively about 19/5.4/3.1/2.9
times that measured use. These are measured capacities, not an inference
of retail population or proof that every possible graph fits finite work.
Both large datasets exceed the old portable-output limit; the larger also
exceeds the old tree-window and reached-map thresholds.

A positive 513-reference BIOM list crosses the 512-pointer chunk boundary.
All seven nonzero lanes and all-zero rows survive export. Invalid native
types/keys/namespaces, changed paired inputs, malformed count/span/cycle,
pre-acquisition and mid-collection cancellation, event and byte exhaustion,
absent/multiple/explicit PID, wrong executable, truncation and ordinary
output errors retain their specific refusals. A `UINT64_MAX` declared count
walks the actual six-record graph and fails count reconciliation without
allocating from that declaration. Optional history exhaustion does not
block native defining identity. Old operational-interface tripwires remain
active. The existing 20 native/source tests and 28 oracle tests passed.
No retail handle was opened and all owned targets retired normally.

| Qualified identity | SHA-256 |
| --- | --- |
| Execution source manifest | `4c958ae9cd557c5e952bfa0c20b48b7fb80e9f344eac2c7f523c219cdafb26f3` |
| Work manifest | `490060e6deafda06b4383a3de300c68fa1adaf71691830ba3a5cfb4d0aa20b60` |
| 46-control qualification result | `28ce33ba9ccd177ad9b6a5de06fa60325585e8db2d434416954b140545dcd75d` |

Affected regressions also passed: SRR-013 strict 51 controls, structural
63 new observations plus four replay challenges (including the strict and
prior retail-like owned baselines); SRR-016 whole census 73 owned controls,
eight tamper controls and one remap refusal; SRR-017 export eight positive
and nine negative controls. The existing 20 native/source and 28 oracle
tests passed. No work limit, oracle, reproducer or operational gate changed.
The fresh pinned static export manifest SHA-256 is
`244cdfebc8a421c7576bdb76af29b46b985bad0c35ebe8d1995322981611c121`;
it pins function/window text and machine-byte hashes, recovered with the
tracked PE inspection tool and existing Capstone 5.0.7.

Frozen old execution source
`062ec189671de1e37e55294083de8da186701ee8ec166b73a9fa91752b0386ae`
from `8a963710` reproduces the original receipt's exact `index_fence` and
byte-identical indeterminate export. Work identity remains
`490060e6deafda06b4383a3de300c68fa1adaf71691830ba3a5cfb4d0aa20b60`.
The current public replayer refuses that receipt's old source pin. An
explicitly diagnostic checked prefix consumes the original 4,251 operations,
passes the former `[0, 83]` boundary, then requires a read at operation 4,252
where the retained stream instead ends the failed collection. No read or
second collection is fabricated; historical raw targets remain unqualified.

Reproduce using the run card's offline commands with a new ordinary output
directory. `--identity` prints the exact byte-hashed execution dependencies
and work limits without opening a process. Qualification builds disposable
fixtures and writes rebuildable evidence; it never opens Starfield. The
starting HEAD was `8a963710ce297dd97ef56d8840cf6ed2f8544656`, with the actual
incomplete-observation report already modified in the worktree. The task
patch excludes that pre-existing report change.

The actual observations below retain their original disposition and scope.
The former 8,192-descriptor refusal describes the previous implementation;
it is not a condition of the new operator command.

## Qualified operator observation at 16:13 AEDT on 18 November 2026

**PROVEN — FINISHED / QUALIFIED.** The operator explicitly requested one
extraction after normally launching to the responsive title card. The
command began at 05:13:33 UTC (16:13:33 AEDT), selected PID 52272 and used
clean committed checkout `bd993bebc1376c3a019bc61bc7bd5e16221f6a6c`.
The pinned retail executable, reviewed execution source
`4c958ae9cd557c5e952bfa0c20b48b7fb80e9f344eac2c7f523c219cdafb26f3`
and unchanged work
`490060e6deafda06b4383a3de300c68fa1adaf71691830ba3a5cfb4d0aa20b60`
matched. There was one observation pair and no retry or implementation change.

Each collection declared and visited 18,314 mixed descriptors: 3,211 typed
targets plus 15,103 certified mixed exclusions. Both have verified coverage,
572 tree windows (565 blocks, six leaves and one internal node), and 2,870
reached native FormID-map entries. There were zero mixed/target refusals,
zero unresolved source fields and no acquisition failure. Rooted graph,
typed inputs, slot values, complete form witnesses and namespace identity
all agree. Both collections have opening and closing process identities
and consumed-window revalidation; these do not imply atomicity.

The 3,211 unique edges cover 1,445 normalized PNDT identities (1,437
`starfield.esm`, eight `shatteredspace.esm`), 428 BIOM identities (425/three
respectively), and 45 distinct IRES identities. There are 3,192 rows with a
base-game defining PNDT and 19 with a Shattered Space defining PNDT. All
7,445 nonzero resource occurrences resolve to native `starfield.esm` IRES
records with the required type/vptr. Raw runtime IDs, normalized defining
plugin/local IDs, seeds, RSGD references and all seven slot words survive.
The equal native namespace has 38 assigned plugins: eight full, nine medium
and 21 small; its normalized digest is
`64724895b5a71ebe4ff60305d4cf0bde2d93e18699b5c66ed5705143db77803a`.
This is defining identity, not physical-file or winning-content attribution.

| Slot | Nonzero words | Explicit zero words |
| --- | ---: | ---: |
| Common | 2,985 | 226 |
| Uncommon | 1,425 | 1,786 |
| Rare | 730 | 2,481 |
| Exotic | 364 | 2,847 |
| Unique | 8 | 3,203 |
| Special | 472 | 2,739 |
| Everywhere | 1,461 | 1,750 |
| Total | 7,445 | 15,032 |

All 22,477 words are retained. One all-zero row is explicitly present:
`starfield.esm:05E3A5` → `starfield.esm:120C76`. Its native forms resolve
and its observed BIOM has zero RSGD references; the seven zero words are
observed payload values, not an inferred empty allocation. No generation,
eligibility or comparison conclusion is inferred from that row.

The sealed pair used 44,748 operations and 9,787,692 requested bytes;
backend totals including image authentication were 44,769 process reads,
44,854 region queries and 9,795,947 bytes. Evidence and normalized exports
remain private. All output hashes reconcile; checked offline replay
regenerates byte-identical dataset and comparator projection.

| Evidence | SHA-256 |
| --- | --- |
| Sealed receipt | `3a48b04479bf88a8821a704a77d684cd6941585c075323ce53c0d6a14a1efea3` |
| Qualified normalized dataset | `15711109761112c3ce3b2f5bf2a03966ccdb26a277ea7ec0961f0147b16eedb4` |
| Comparator projection | `496ccd835e2e3de062aa07f812f15f406097c8f8948610a3f7952d6b08ae7c16` |
| Source/work and output manifest | `3441ccf092bef63ed7c9046a21ae99bb343e303443f85b1064d8215b2e971357` |

The command exited successfully and the operator was immediately told they
could Quit normally. No further game access occurred. Process exit and save
preservation are not independently measured by this operator workflow.
The result is complete for the admitted rooted store at this title-card
checkpoint. It establishes neither all-galaxy completeness nor atomicity,
intermediate mutation absence, completed allocator execution or oracle
agreement. No oracle or reproducer comparison was performed.

**Independent disposition: QUALIFIED_COMPLETE_ROOTED_STORE_PAIR.** The
reviewer independently reconstructed all 572 native pages and 18,314
positions in each collection, checked routing minima/fences, leaf links,
strict global order and exact counts, and classified all target/exclusion
prefixes. Independent FNV native-map traversal checked 2,870 reached entries
and 1,950 typed PNDT/BIOM/RSGD/IRES identities per collection. Every raw and
normalized row, metadata field and seven resource words was checked against
retained bytes. All plugin assignments and paired axes agree. Dataset and
comparator projection regenerated byte-for-byte, and all hashes/source/work
identities reconciled. Review was entirely offline with live entry points
replaced by failing tripwires; no oracle comparison or broader completion
claim was made. The standalone substantive review SHA-256 is
`ef5a93a1e538fe517466a44fd5212e37b85a8bb5a9859ebe680abac04a83851e`.

## Operator title-card observation at 15:17 AEDT on 18 November 2026

**INCOMPLETE — ACQUISITION_INDETERMINATE.** The operator explicitly
requested one attempt at the responsive title card. At 04:17:28 UTC
(15:17:28 AEDT), the unchanged reviewed operator-v2 command selected
Starfield PID 34104. Checkout `8a963710ce297dd97ef56d8840cf6ed2f8544656`
was clean; its execution identity was
`062ec189671de1e37e55294083de8da186701ee8ec166b73a9fa91752b0386ae`,
its work identity was
`490060e6deafda06b4383a3de300c68fa1adaf71691830ba3a5cfb4d0aa20b60`,
and the executable matched the pinned retail hash.

The collection declared 18,314 mixed descriptors and traversed 1,202:
37 mixed exclusions and 1,165 native-typed target records. It then refused
`index_fence: keys cross a root-derived separator`. Resource limits were
not exhausted. This records the reader's fence comparison; it does not
establish whether the discrepancy reflects a decoder assumption, changed
memory or a native structure issue. No check was bypassed or changed.

The retained raw targets contain 512 distinct runtime PNDT IDs, 302 distinct
runtime BIOM IDs and all 8,155 slot words, including 5,480 zero lanes and
no all-zero target row in this partial subset. Those counts describe only
unqualified diagnostic records. Complete coverage and closing witnesses
were not reached; native namespace acquisition and the second collection
did not begin. No normalized identity or qualified export is established.
The empty qualified row list is not an empty population. Downstream
`source_binding_incomplete`/namespace source issues reflect the absent
namespace collection, not demonstrated invalid loaded-plugin identities.

The sealed receipt contains 4,251 acquisition events and 396,207 requested
bytes. Backend totals including image checks were 4,260 process reads,
4,294 region queries and 399,509 bytes. Output hashes reconcile, and checked
offline replay reproduces the exact refusal and byte-identical diagnostic
export. Retained evidence identities:

| Evidence | SHA-256 |
| --- | --- |
| Sealed receipt | `2d43d7aa323cde6c2b5b7743864fbd0d3b160c2823a8da69d0ee30d0b9471508` |
| Indeterminate dataset | `e794d7e34b6505c7bc375cd08853e326c2a8bef4f0d562c1f0986a4bb5516614` |
| Source/work and output manifest | `3670b465acaa45d1f72bf0319e9d4b82a94d1a95172a1dbc99f37f8bb01f3500` |

The operator was told immediately that they could Quit normally. There was
no retry, limit enlargement, code change or further live access. Quit and
save preservation were not independently measured under this workflow.
No atomicity, allocator completion, complete population or oracle agreement
is claimed. The concrete unresolved observation is the fence refusal;
any implementation diagnosis/correction requires separate offline work,
and another live attempt requires an explicit operator request.

Independent offline review verified all evidence hashes, the exact fourteen
execution files and work identity, receipt seal and byte-identical replay.
An offline trace isolated the predicate in `check_fences`: a 14-descriptor
packed block at path `[0, 83]` exceeded its inherited level-1 parent's
child-0 upper fence. The block's first key equals that fence; later keys
exceed it. No lower fence applies there. This establishes the reader's
specific failed comparison, not native corruption or its cause. The walk
had reached 86 windows and 1,335 native map entries, within all budgets.
The reviewer confirmed every partial count and the absence of closing
identity, namespace and paired agreement; the only supported disposition
is an incomplete diagnostic observation. The standalone review SHA-256 is
`468f053d8005cd1704c7be242b198fd8a18029a67bc675ab97c57d3a9417f2b0`.

## Operator title-card observation on 18 November 2026

**INCOMPLETE — ACQUISITION_INDETERMINATE.** One operator-requested
extraction at 2026-11-18 03:29:38 UTC used committed checkout
`90ff8d62043dabc9b36703d91e70f43ce5534444` and execution identity
`20ad3d895a85dd8d79bca6ce3a8c4c0253b485d80999eaf08f6696303d74d204`,
work identity
`63598b091189ecb3bfdf16b2519183bbff4763f748f1ccda131f721271eae4ef`. The selected compatible Starfield 1.16.244.0 process was
PID 74148 with the pinned executable hash. The command opened only the
query/read interface; it did not launch or close Starfield.

**PROVEN (opening publication, not a completed census):** the retained
registered index header declares 18,314 mixed descriptors. The unchanged
8,192-descriptor work ceiling therefore refused at the predicate
`self.total <= self.limits["entries"]` in `WholeCollection.collect`, after
publication and FormID-map anchors and before rooted traversal. The exact
failure is `traversal_budget: mixed descriptor cap exceeded`. This is a
concrete capacity mismatch in the qualified envelope, not an ESM identity,
Steam or authorization failure.

No descriptor was traversed, no target was attempted or verified and no
Planet/Biome identity or resource lane was acquired. One incomplete
collection is retained; no second collection began. Neither the complete
population nor any zero-valued allocation count is established. The
export's empty qualified row list does not mean the game has no allocations.
No collection agreement, complete coverage, allocator completion, atomicity
or oracle agreement is claimed.

The sealed receipt contains 13 recorded operations and 94 requested bytes;
backend totals, including executable identity checks, were 22 process reads,
56 region queries and 3,396 requested bytes. All output hashes reconcile.
Checked offline replay reproduces the same refusal and byte-identical
indeterminate dataset. The retained identities are:

| Evidence | SHA-256 |
| --- | --- |
| Raw sealed receipt | `1f9ecbd8da5ac8195912f4da946a97998042e947cc229ca985d3b54291388b23` |
| Indeterminate dataset | `8991a02eb1937034e211a0c90376216b64222376763fbd29aa6f83b042b0dce0` |
| Result | `d112933c45d0910d92a984f96beb612283272f538e03e9e5a4ff4db25288677c` |
| Source/work and output manifest | `b346ffe7690ec8f4e02ecaf1e5a706f900f643b09453988d52b48dc79c8c2fc0` |

The operator was immediately told the terminal result and that they could
Quit normally. No automatic retry, limit enlargement, relaunch or further
live access occurred. Operator Quit and protected-save state are not
independently measured under this procedure. Evidence remains private;
source code and work limits are unchanged. Any capacity correction needs
offline qualification and review before a separately requested later
extraction. The current envelope cannot deliver a complete observation of
this declared store.

Independent offline review verified the source/work identity, every output
hash, receipt seal, exact replay and byte-identical indeterminate export.
It independently decoded the declared count and confirmed that the refusal
precedes rooted traversal. `source_binding_incomplete` is a downstream
consequence of absent acquisition, not evidence of invalid native identity.
The review accepts the incomplete classification only; it establishes no
complete population, game exit or save preservation. Its substantive
conclusion is that the reviewed envelope is insufficient for this observed
store declaration. Earlier fixture qualification established bounded
behavior, not that the retail population would fit the descriptor ceiling.
The independent report SHA-256 is
`348f3db37144ff8b946bf542ba9c9f81376ea33d8be43bec5b290042a3b43152`.

## Authorized retail attempt on 18 November 2026

**ADMISSION_REFUSED — NO_OBSERVATION.** One separately authorized
invocation used committed candidate `8321a3b`, approved execution digest
`dde03db307559f0d954d7787acfbc74432f252e8c3987dbf06f690386cc17d00`
and work digest
`4bf5dd930d6fa545fe5312ea9c7b62795d0f70666f483e0070a1bffc00f9d9ad`.
The installed retail executable matched the pinned 1.16.244.0 hash.
The working tree and index were clean before preparation.

The one-use claim was durably consumed. The command then returned
`steam_install_unverified: Steam installation registry witness unavailable`
with observer exit status 1. A read-only post-failure diagnosis of
`HKEY_CURRENT_USER\Software\Valve\Steam`, value `SteamPath`,
returned `FileNotFoundError`, Windows error 2, in the executing account.
The retained attempt's exact byte SHA-256 matches the independent console
value
`c694c2d331349b3ec89658f2b4fdbe29ac332716710865d109314f670c54bf6e`.

Source ordering and the retained console show that this failure precedes
Steam process selection/open, log-baseline retention and the operator
launch prompt. The operator had confirmed the intended existing Steam
account and disabled NVIDIA overlay, but was never asked to launch.
There was no authenticated game epoch, title marker, target-bound
receipt, native memory journal or partial journal. There was no second
invocation, launch or observation. The approved implementation and work
limits were preserved.

| Scientific or operational axis | Actual result |
| --- | --- |
| Native descriptors and Planet/Biome/resource population | Unmeasured. No allocation rows or slot words were acquired. |
| All-zero targets, zero lanes, coverage and absence | Unmeasured. An empty dataset is not inferred. |
| Collection agreement | No collection began. |
| Acquisition and export qualification | No qualified extraction or normalized dataset. The attempt's native receipt hash is null. |
| Evidence integrity | Written approval, consumed claim, reviewed manifest, console and failure attempt retained privately. The attempt hash independently reconciled. There is no native seal to replay. |
| Protected saves | Preflight and postflight passed all 98 Documents and 95 Steam remote original/backup pairs, both designated saves, and no unclassified or other entries. Protected and transient inventories reconciled exactly. |
| Environment and space | Executable/build, disabled Steam Cloud/overlay and save-path checks passed before and after. Both drives exceeded the required available-space floor plus reserve. |
| Game retirement | No admitted target. Closeout reports protection `UNCHANGED`, `EXIT_UNVERIFIED` and null epoch because no game exit witness was bound. It establishes no game exit code. |

The independent reviewer inspected the actual approval, claim, console,
attempt and protection/environment receipts. Offline revalidation of
the written authorization and exact source/work bindings passed. The
reviewer verified the failure's position before process admission and
all pre/post reconciliation fields, including transient inventories.
The substantive standalone review classifies the result as refused
admission with preservation passed and scientific measurements unavailable.
The original offline qualification retains its scope.

This authorization is consumed. The concrete runtime blocker is the
unavailable Steam registration witness in the observer account. Any
later launch or observation needs separate maintainer authorization.

<!-- srr-017-identity-review:start -->
**READY_FOR_SEPARATELY_AUTHORIZED_OPERATOR_EXTRACTION.** Independent
challenge accepted the narrow separator correction with no unresolved native
or implementation blocker. This is offline readiness, not a new retail
observation or authorization.

The reviewer personally rechecked the pinned lookup, split, truncation,
insertion and cursor bytes: internal equality routes left, leaf lookup can
choose a previous-leaf block, and a leaf split promotes its last left block
minimum rather than record maximum. Independent byte examples covered seven
valid geometries, including unsigned qword boundaries, and nine malformed
geometries. Seventy-five selected-key queries and 21 malformed selected
routing/overlap/link cases challenged the shared primitive. The documented
pivot-gap/equality admission examples are explicitly fixture/navigation
evidence, separate from the proven static native writer shape.

The reviewer independently checked all 73,728 large-fixture targets and
516,096 slot words, including normalized identities, metadata and 4,338
all-zero rows; replay regenerated byte-identical exports. Six independently
resealed evidence attacks refused. Source/work identity, compiled fixture
provenance and all seventeen pinned static exports reconciled.

Frozen old source independently reproduces the exact historical refusal
and indeterminate export. The corrected raw prefix passes the former block
then needs uncaptured operation 4,252. No source pin is bypassed in the
public replayer; no read, closure or second collection was invented. The
retained retail result remains `ACQUISITION_INDETERMINATE`.

The fourteen-file review manifest is
`469486653aa8683a9a387f2b22684cca319bdeb11c0492c326e6e4fbae7c2dda`.
It hashes sorted UTF-8 lines of byte SHA-256, two spaces and relative path,
terminated by LF; only this marked review body is excluded from the dossier
hash. Tracked conclusions are self-contained and require no private review
files. No scientific check, work limit or operator prerequisite was removed
except the contradicted record-maximum application of routing fences;
minima/pivot fences, genuine record boundaries and complete paired coverage
remain mandatory. No live operation occurred during this correction.
<!-- srr-017-identity-review:end -->
