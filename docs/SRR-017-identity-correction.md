# SRR-017 native FormID identity correction

**Current contract.** The operator starts Starfield, holds the responsive
title card and explicitly requests extraction. The command reads an already
running compatible process; it never launches or closes the game. This
implementation task authorizes offline qualification only. See the
[run card](SRR-017-title-run-card.md) for the current invocation.

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

The census envelope remains 8,192 descriptors, 1,024 windows, depth 5,
8,388,608 map buckets, 8,192 reached map entries, 256 entries per chain,
80,000 pair events, 32 MiB requested and a 128 MiB journal. The 25 ms
minimum separation preserves fresh paired reads; it is not a deadline.
The portable document ceiling is 64 MiB. Executable hashing and backend
queries/reads are bounded and reported by the command's work manifest.
Existing native namespace ceilings remain unchanged.

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

The shared operator controller passed 20 owned-process controls on Python
3.14.3. The 3,210-row corpus and 4,096-row upper fixture exported and
replayed every one of 51,142 slot words, retaining 189 and 241 all-zero
rows respectively. Their rooted mixed populations were 3,600 and 5,120.
Independent field checks covered native/normalized keys and row metadata,
not only counts. A relative `DATA\` fixture also qualified.

Explicit PID, absent/multiple processes, incompatible executable, read
failure, cancellation before selection and during collection, native
namespace drift, paired input drift, invalid namespace, PNDT mismatch,
wrong BIOM/resource types, exhausted work, truncated replay, output
collision and an existing ordinary directory were exercised. Indeterminate
receipts replayed with the same refusal. Tripwires failed on old admission,
authorization, registry, save, preflight/exit and process-launch interfaces;
none was invoked. Every owned target remained alive until its fixture owner
quit it. The existing 20 native/source tests and 28 oracle tests passed.
No retail handle was opened.

| Qualified identity | SHA-256 |
| --- | --- |
| Execution source manifest | `20ad3d895a85dd8d79bca6ce3a8c4c0253b485d80999eaf08f6696303d74d204` |
| Work manifest | `63598b091189ecb3bfdf16b2519183bbff4763f748f1ccda131f721271eae4ef` |
| 20-control qualification result | `c314fbd297ffef0974d6d53881ca8321a074333129b5314fb2436465b36b06f1` |

Reproduce using the run card's offline commands with a new ordinary output
directory. `--identity` prints the exact byte-hashed execution dependency
manifest and work limits without opening a process. The manifest includes
historical helper modules because the reader reuses their API bindings;
this does not invoke their retired admission gates. Qualification builds
only disposable fixture binaries and writes rebuildable evidence.

The starting HEAD is `8321a3b`; the initial worktree already contained this
dossier's failed-attempt report and the supplied untracked correction
brief. The task patch excludes both pre-existing changes. The historical
attempt section below is preserved byte-for-byte.

The historical section below describes the superseded controller's actual
attempt. Its Steam registration failure is not a prerequisite or blocker
for the operator command above. Its recorded no-observation result is
unchanged.

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
challenge found no blocking scientific or operational-prerequisite defect.
The reviewer inspected the exact controller, native census changes, retained
reader/export dependencies and current run card. Retained requirements
establish compatible decoding, bounded work, native validity, coverage or
replay integrity; none requires credentials, external services, privileged
setup, save attestations or special custody infrastructure.

The reviewer independently reproduced both large exports using separately
written field/slot arithmetic and checked all 51,142 words and 430 zero
rows. A separate all-seven controller fixture preserved all seven distinct
nonzero lanes in ordinal order. Additional byte-fixture challenges covered
all plugin scales,
relative/missing physical paths, invalid/unmapped IDs, namespace conflicts,
wrong PNDT/BIOM/RSGD/resource types, resource vptrs, cyclic native chains,
short reads and exhausted namespace work. Nine independently resealed
receipt challenges refused changed binding/source/epoch/profile/work,
native read bytes, report contents and post-report events. Separate
same-controller runs retained indeterminate first-pass evidence on second
collection cancellation and refused invalid/absent PID, namespace drift
and exhausted work. Owned targets remained alive until fixture-owner Quit.

The reviewer checked all six task files against normalized manifest
`32c4006019e71a04ded6316e6146a9b6fb95354d76521c1adeb71d3f6e983fee`.
It hashes sorted UTF-8 lines of byte SHA-256, two spaces and relative path;
only this marked review body is excluded from the dossier hash.
The detailed independent report records methods, limitations and evidence
identities. These conclusions do not depend on access to private evidence.
The execution/work hashes above identify the qualified candidate. There is
no remaining mandatory infrastructure blocker. Live extraction awaits
maintainer acceptance/commit and an explicit current request after they
launch and hold the title card; this task performed no retail operation.
<!-- srr-017-identity-review:end -->
