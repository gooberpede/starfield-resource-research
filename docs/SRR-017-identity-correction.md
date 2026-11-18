# SRR-017 native FormID identity correction

**Current contract.** The operator starts Starfield, holds the responsive
title card and explicitly requests extraction. The command reads an already
running compatible process; it never launches or closes the game. This
implementation task authorizes offline qualification only. See the
[run card](SRR-017-title-run-card.md) for the current invocation.

**Latest live result:** the operator observation was incomplete because the
published 18,314-descriptor store exceeded the reviewed 8,192 ceiling. No
allocation rows were acquired; see the actual-observation section below.

## Scope and implementation

The command is `python -E -B -m tools.srr017.extract --output DIRECTORY`.
It selects the unique compatible Starfield executable, or the operator's
`--pid` when multiple compatible processes exist, and reports the selection.
It authenticates the executable/layout and creation epoch through the
existing query/read-only interface. It obtains one pair of independently
rooted full-store collections and checks the sealed receipt before export.
No launch, Quit or automatic acquisition retry occurs.

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

The exact operator controller passed 29 owned-process controls on Python
3.14.3, including complete paired native acquisition, normalization, export
and checked replay substantially above the 18,314 retail declaration.
Every target's keys, metadata and seven words were independently asserted.

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
| Execution source manifest | `062ec189671de1e37e55294083de8da186701ee8ec166b73a9fa91752b0386ae` |
| Work manifest | `490060e6deafda06b4383a3de300c68fa1adaf71691830ba3a5cfb4d0aa20b60` |
| 29-control qualification result | `c5cdf1f6498a176cdbff2e9cbdb371cef69f6427d47e5448759275fb348a5138` |

Reproduce using the run card's offline commands with a new ordinary output
directory. `--identity` prints the exact byte-hashed execution dependencies
and work limits without opening a process. Qualification builds disposable
fixtures and writes rebuildable evidence; it never opens Starfield. The
starting HEAD was `90ff8d62043dabc9b36703d91e70f43ce5534444`, with the actual
incomplete-observation report already modified in the worktree. The task
patch excludes that pre-existing report change.

The actual observations below retain their original disposition and scope.
The former 8,192-descriptor refusal describes the previous implementation;
it is not a condition of the new operator command.

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
challenge accepted the capacity correction and the necessity audit. No
unresolved blocker remains within the qualified work envelope. Scientific
identity, count reconciliation, malformed-structure refusals, pairing,
cancellation and evidence integrity remain mandatory.

The reviewer independently checked every large-fixture target and all
516,096 slot words against separate arithmetic, including metadata,
normalized identities and 4,338 all-zero rows, and checked byte-identical
export replay. Separate byte fixtures qualified all 4,605 native plugin
slots and 8,701 registry files, plus 600 ordered RSGD pointers across two
chunks. Wrong RSGD types/pointer identities, namespace exhaustion,
cancellation and resealed receipt edits refused. Tree-depth and cached
chain controls directly exercised the remaining stack/computation bounds.

One material review finding identified the remaining plugin-registry
count ceiling as redundant and its claimed native implementation extent
as unsupported. The active ceiling was removed; the 8,701-file test
exceeds the previous 8,192 bound and still validates under actual read/byte
budgets. Native slot-space invariants, registry cycle and alias checks
remain. No replacement prerequisite was introduced.

The reviewer checked the eleven-file manifest
`8bba2da64fc2393883f9b17bd7585173f9e2c034849fd433fc2df1dedd7550f8`.
It hashes sorted lines of byte SHA-256, two spaces and relative path,
terminated by LF; only this marked review body is excluded from the
dossier hash. The historical refused attempt is unchanged. The later
incomplete observation retains its original result and explicit old
source/work identities. No retail operation occurred during correction.
The detailed independent report records the substantive methods and
resolved finding; these conclusions need no private-file dependency.
<!-- srr-017-identity-review:end -->
