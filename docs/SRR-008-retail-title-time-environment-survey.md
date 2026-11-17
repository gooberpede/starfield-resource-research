# SRR-008 — Retail title-time environment survey

**Current status — COMPLETE for the bounded interactive-account title-time survey.**
The two earlier BLOCKED attempts and their independent reviews are preserved
below as historical evidence.

**Scientific disposition — BLOCKED before launch.** The survey asks whether
two inventories at the visible title card can identify the native module
environment of one authenticated Steam-launched Starfield process well
enough to prepare a separately reviewed debugger-admission profile. The
installed executable passed its identity check. An effective empty, isolated
save namespace could not be demonstrated. The brief authorized one Steam
URI launch conditional on
those checks. No launch was attempted.

## Preflight evidence

| Item | Observation and limit |
| --- | --- |
| Installed executable | File and product versions `1.16.244.0`. Two matching SHA-256 reads around the preflight metadata check give `7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28`, matching [SRR-001](SRR-001-executable-identity.md). This identifies the installed file. |
| Steam | The app manifest reports app `1716740`, build `23518663`, install directory `Starfield` and state flags `4`. The registered URI handler is `steam.exe -- "%1"`. No `Starfield.exe` PID was returned by the preflight and closing process queries. Process identity and mapping remain unobserved. |
| Steam overlay and Cloud | The single on-disk profile with a local configuration has `OverlayAppEnable=0` and `cloudenabled=0` in its respective app-specific records for `1716740`. The stored settings corroborate the maintainer's report. Effective runtime behavior was unobserved. The Cloud cache hash is diagnostic. |
| NVIDIA overlay | Disabled globally according to the maintainer. The process-name check returned no matching helper. Residual NVIDIA Overlay files exist and the effective global switch was not independently verified. |
| SFSE | `sfse_loader.exe` was absent at the game root. The installation and Documents plugin folders each held residual notices and a Vortex marker, with no immediate plugin DLL observed. Documents also held an SFSE log directory. These are disk observations. Runtime loader, proxy and module behavior remain unknown. |
| Save protection | The standard Documents save directory holds 271 .sfs files. No sLocalSavePath entry was found in the three checked Documents INIs. The scoped backup comparison below found byte matches, and the effective isolated writable route remains unverified. |
| Disk and host | Windows `10.0.19045.0`. Initial caller-available bytes were 75,686,686,720 on C: and 69,522,694,144 on D:. Before receipts and patch work, both remained above the 40,000,000,000-byte floor after reserving 134,217,728 bytes per drive for local writes, replay and review. |

Read-only operations covered process-name queries, registry and file metadata,
configuration lookups, directory inventories and scoped hashes. Game files,
settings, saves, backups, desktop and Ghidra received no write or control
operations. The sibling policy classified 98 Documents saves as protected and 173 as
transient. All 98 matched copies with distinct file identities in the
historical backup directory on D: by byte length and SHA-256. Both research
designations also matched their policy pins. The Steam remote Saves subtree
contained 95 protected and 159 transient saves under the same policy. All
95 protected remote saves matched distinct backup files by basename, length
and hash. No transient save bytes were needed for the final comparison. The
historical backup manifest expected by the earlier tool was unavailable.
Archive-wide preservation, restoration readiness and separation from a
future test/sync route remain unverified. The local save-check and designation
receipts record the exact pairs, identities and policy pins.
No debugger or observer ran against Starfield.

## Offline inventory qualification

The original Python prototype adapted the Tool Help enumeration
pattern from the outpost environment reader. The
[tracked inventory fixture](../tools/srr008/README.md#disposable-module-inventory)
runs on a disposable x64 CPython child with the documented Windows inputs.

The controller retains a handle with
`PROCESS_QUERY_LIMITED_INFORMATION | SYNCHRONIZE` (`0x101000`). It checks
liveness, PID, creation FILETIME, image path and architecture before each
inventory, after enumerating modules and after disk reads. It uses
`TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32` (`0x18`), allows three attempts for
`ERROR_BAD_LENGTH` and caps enumeration at 2,048 entries. It records module
base, image extent and reported path, and attempts to resolve a local path
and record its volume/file ID, size, timestamp, PE identity and SHA-256.
Per-file hashing is capped at 512 MiB. It checks file metadata and path identity
around each disk read. Schema 1 records UTC boundary times, enumeration and
read errors, snapshot differences and the fixture exit code. It writes a
fresh, flushed local JSON report. The CLI accepts only a fixture output
path. Its process rights exclude VM reads and thread operations.
[Tool Help snapshot documentation](https://learn.microsoft.com/en-us/windows/win32/api/tlhelp32/nf-tlhelp32-createtoolhelp32snapshot).
[Windows process access rights](https://learn.microsoft.com/en-us/windows/win32/procthread/process-security-and-access-rights).

Both disposable snapshots enumerated 15 modules for the same retained epoch,
with no reported enumeration, file or PE errors and no differences. The
main image's backing-file identity and disk hash matched its independently
read fixture pin, and the image extent matched the disk PE. The deliberately
wrong FILETIME was refused before module enumeration. Closing fixture stdin
produced a signaled handle and exit code zero. These checks qualify the
tested inventory primitives on the fixture. The prototype has no live
operator, Steam launch, retail binding or retail sealing path.

The hashes identify files read through the reported paths. A file replacement
between module mapping and inspection could yield different on-disk bytes
even when the file is stable throughout the read. Tool Help covers the
reported loader list, has visibility limits and can race loader changes.
Both samples are finite and can miss a module loaded and removed between
samples. Neither file hashes nor a stable inventory establish the mapped
bytes or authorize future debugger attachment.

## Retail disposition and next bounded action

| Finding | Status |
| --- | --- |
| Actual Steam process identity | Unobserved. No game PID, retained handle, creation epoch, architecture or mapped image was acquired. |
| Retail module completeness and drift | Zero retail snapshots. Module differences and critical image identities are unknown. |
| Environment qualification | Blocked on the effective isolated save location and independently verified protection of current originals and backups. |
| Operator phase | No visible title confirmation or UTC receipt. |
| Scientific seal and game exit | No retail evidence seal or exit observation. |
| Instrumentation health | Fixture inventory and cooperative exit passed. Retail acquisition was not exercised. |

The smallest next prerequisite is a maintainer-established empty writable
save namespace for the intended Steam session, with the effective route
demonstrated and the verified backup copies confirmed outside that route and
any writable sync namespace. Then qualify the
operator-gated retail controller and obtain separate live authorization
for a later attempt.

For a future SRR-007 admission revision, bind the exact retail build and
process epoch to the mapped main image and approve module identities by
resolved backing-file and PE fingerprints. Treat unidentified or changing
modules as findings and hold any admission claim that depends on an
unresolved critical identity. The next bounded integration is an offline
admission-profile verifier with controls for changed critical identities,
legitimate drift and epoch mismatch, once an actual retail profile is
available. The present fixture list cannot supply that profile. Startup
coverage, allocator invocation and Stage A remain open.
[SRR-007 admission boundary](SRR-007-retail-launch-and-stage-a-qualification.md#proposed-stage-a-run-card--blocked).

## Custody and publication

Starting and closing HEAD `5bb6bd0ff7f8fd0b8c4234ab12a7fda152a8cf30`,
tree `821e22ff6eb955f2f4db90a1c84206f446069523` and index SHA-256
`53c84d930f7ac5905c90bf954f5f877e395252b01c7c0a285b0ebc5caa66dc39`
match. The supplied brief was the sole starting untracked path and is
excluded from the task patch. The tracked index document and new dossier
are the only task paths. The local preflight, save comparison and closing receipts identify
the scoped documentation, policy, executable, configuration and fixture
dependencies. The tool SHA-256 is
`7cbdbfad27d10faa1cc0d3fb4113f3ee910b65da9ee8f5af363a942d768415f4`
and the schema 1 fixture receipt SHA-256 is
`9cbb91c6a51a1fc041c3804773249ada9cfe78dc6b0f28e61f1a0eeffbf83924`.
The local replay uses the starting Git blob and verifies both delivered
files byte-for-byte.

The installed-file identity is eligible as a scoped claim. From the public
repository, follow [SRR-001 and provenance](PROVENANCE.md#current-retail-identity)
on a lawfully obtained copy and compare versions, two SHA-256 reads and the
local Steam app manifest. This route was exercised against the local install.
The no-launch disposition and exact historical fixture result are
custody-backed. The tracked fixture is the current rerun route. Host-specific paths,
configuration and save records stay local. Retail process/module claims,
effective runtime settings, startup coverage and allocator results remain
held for lack of retail observations.

<!-- review-status:start -->
## Independent review disposition

**BLOCKED before launch.** Independent internal challenger
`srr008_challenger` checked AC1–AC6 against the primary receipts, independently
reran the fixture, and requested correction of the Steam remote save
classification root. The corrected comparison and both Documents
designations were verified. The installed-file pin, disposable checks and
task-only byte replay support this partial handoff. The missing effective
isolation route leaves retail process identity, title and module inventory
unobserved.

Reviewed substantive manifest SHA-256
`236acd4780ed59c8c0a364ac339abf8cde72185789879cd26c3e0b9abddafaba`.
The two sorted entries contain each file's SHA-256, two spaces, its
repository-relative path and LF. Only this marked review block is excluded
from the dossier digest.
<!-- review-status:end -->

## Amended preflight and Steam dispatch — 14 November 2026

**Current disposition — BLOCKED after one Steam URI invocation.** The amended
save preflight passed. The URI handler reported success, and no Starfield
process could be authenticated. The survey has zero retail inventories.

The maintainer prospectively removed the empty and isolated save namespace
requirement for SRR-008. Ordinary Documents and Steam remote saves could
remain in place. The amendment required current protected-save and backup
verification, Cloud confirmation, a postflight comparison, and retention
of any unexpected changes. The original blocked preflight above and its
independent review are historical. No save, backup, game file, setting,
Steam sync configuration or Ghidra project was changed by Codex. No save
load or creation was requested or performed by Codex.

### Amended preflight

The controller checked the pinned installed executable, the Steam app/build
metadata, and the absence of an existing Starfield process. The on-disk Steam
app record still showed Cloud disabled and the per-game overlay off.
NVIDIA overlay state remained maintainer-reported, with no matching helper
seen by the process-name check. The SFSE loader remained absent and the
earlier disk inventory of residual files remained applicable. No retail
runtime module inference follows from those checks.

Both namespace roots and their ancestors passed reparse checks. Documents
had 98 protected and 173 transient entries. Steam remote Saves had 95
protected and 159 transient entries. Each protected entry matched a distinct
backup file by size and SHA-256, and both Documents research designations
matched their exact policy pins. The backup was on D: outside both ordinary
save paths. The historical manifest was unavailable. The amendment accepted
the scoped current comparison. Transient entries were recorded by name,
file ID, length and modification time. Both drives met the 40,000,000,000-byte
floor after a 134,217,728-byte reservation per drive.

### Acquisition and observed boundary

The schema 2 controller reuses the schema 1 read-only inventory core. It
requires the installed image pin and same-session Steam client, invokes the
URI once with `ShellExecuteW`, and looks for a candidate process with
the nominated native AMD64 image, PID and creation FILETIME. It retains the
`0x101000` query/synchronize handle and checks the epoch and image path
across both Tool Help snapshots. Operator confirmation would be bound to
that epoch and logged in UTC when received, with no claim about the exact
engine transition. A complete prefix is flushed and SHA-256 sealed before
observing exit on the retained handle. The fixture ran the controller's
collection path with two inventories, a valid seal and cooperative exit.
A second fixture supplied the wrong epoch and produced zero inventories,
an incomplete seal and cooperative exit. Fixture controls did not exercise
Steam dispatch or retail access. The prototype records parent PID and
parent process name when available. It permits collection when the parent
differs from Steam, and its marker parser accepts the fixture source value.
A future retail controller needs a trusted retail-only marker and independent
Steam attribution before accepting the inventories as retail evidence.

At `05:21:08.635946 UTC`, `ShellExecuteW` returned `42` after the single
`steam://rungameid/1716740` invocation. That value records shell dispatch.
The read-only process queries yielded no Starfield candidate, and the checked
Steam game-process and console logs had modification times before dispatch.
The logs and process polls do not exclude an unobserved short-lived process. The maintainer
reported **“No visible launch activity.”** The UTC close-decision receipt
records when Codex acted on the report. With that observation and the
process/log checks, Codex stopped only its local inventory controller.
The decision used no elapsed-time cutoff. No second invocation was made.

The caller used a separate, non-elevated Windows sandbox account at medium
integrity, in the same Windows session as Steam. The exact account and
integrity SID are in the private access receipt. The account boundary is a
plausible explanation for failure to hand off to the active Steam client.
The evidence does not establish the cause. A separate WMI process-owner
check returned access denied. The actual Steam application acceptance,
retail process identity, mapping, title-card phase, module coverage,
instrumentation health in retail, and game exit remain unobserved.

The retained launch-attempt journal prefix has three flushed records,
1,634 bytes and SHA-256
`7287f42117549b8a9237d1cd5d29da35338d3474561097bfce8c5e09cf73ff62`.
There is no retail scientific seal. A shell success code alone cannot
support a launch, startup coverage or a debugger-admission claim.

### Postflight, custody and handoff

The postflight reran the protected byte and backup checks after closing the
launch attempt. All 193 pairs and both designation checks agreed with
preflight. Transient names and checked metadata, scoped game and
configuration hashes, Steam settings and the diagnostic Cloud cache hash
also agreed. The postflight observed no additions, removals or changes in
those checks. This was a post-attempt comparison because no game exit was
observed. Both drives remained above the reserved floor.

The amended run's controller source SHA-256 is
`b34162ac780ae79a653002c800ce1fad83b43446b95cb7f6dc8374bc632a96d3`.
The revised task-only patch included the index link and this dossier against the same
starting Git objects. HEAD and the actual index retained their original
identities. The maintainer-supplied brief was excluded from the patch.

Publication eligibility is limited to the installed-file claim and a
sanitized account of the blocked attempt. The preflight files, precise
account and save identifiers, raw module schemas and host diagnostics stay
local. The next bounded action is to review a Steam URI launch from the
maintainer's ordinary interactive Windows context under fresh one-attempt
authorization, with independent Steam attribution and a trusted retail-only title marker
bound to the exact process epoch. Stage A debugger admission remains a separate review and experiment.

<!-- amended-review-status:start -->
### Amended independent review

**BLOCKED after one Steam URI invocation.** Independent internal challenger
`srr008_challenger` checked AC1–AC6, independently replayed the patch and
reran both disposable controls. The challenger verified the three-record
launch prefix, the access-level limitation and the scoped pre/post save and
backup results. Review clarified the process-attribution, marker and log
limits. The absent authenticated game process leaves AC2–AC4's live
evidence unmet. AC5 and AC6 pass for the partial handoff.

Reviewed substantive manifest SHA-256
`f760d44d0a4b0a3887765f568219c26bd3911450195442f2dc59ef921394d637`.
Only this amended review block is excluded from the dossier digest. The
original review block is included as historical evidence.
<!-- amended-review-status:end -->

## Current protection and environment checks

The [tracked offline tools](../tools/srr008/README.md) read explicit
effective roots, a pinned policy and independent backups. The historical
`interactive/check-saves.py`, `interactive/environment.ps1` and
`interactive/survey.py` are custody-only. The two 146-module retail
snapshots are custody-backed historical observations. A fresh full
title-time survey would require separate authority and live inputs.

## Interactive-account survey — 14 November 2026

**Scientific disposition — COMPLETE, scoped to two title-time snapshots of
one authenticated Steam-launched process.** The maintainer authorized one
additional URI invocation under their ordinary interactive Windows account.
The earlier sandbox-account attempt and both prior reviews are historical.
The separate account remains a plausible cause of the earlier handoff
failure. The successful attempt used a different account and establishes
no causal diagnosis of the earlier failure.

### Execution and protection

The supported Codex command runner outside the sandbox used the same
Windows account and session as the Steam client, at medium integrity
without an administrator token. A read-only identity probe verified this
before the controller and again at invocation. Earlier outpost and
reference-handle records informed the search for an existing execution
mechanism. This run used no credentials, elevation, desktop automation,
debugger or save loading.

The non-destructive save checks again matched 98 protected Documents
entries and 95 protected Steam remote entries to independent backup files
by length and SHA-256. Both research designations matched their policy
pins. The 173 and 159 transient entries were checked by name and metadata.
The executable matched the SRR-001 version and SHA-256. The checked Steam
settings recorded Cloud disabled and per-game overlay off. NVIDIA overlay
state was maintainer-reported and the SFSE loader was absent on disk.
At dispatch C: and D: had 75,697,217,536 and 69,520,261,120 caller-available
bytes, respectively. Both cleared the 40,000,000,000-byte floor after the
134,217,728-byte per-drive reservation.

### Actual observations

| Boundary | Observation |
| --- | --- |
| Shell dispatch | One `steam://rungameid/1716740` invocation. `ShellExecuteW` returned `42` at 05:45:39.219099 UTC. |
| Process creation and attribution | Native AMD64 Starfield PID `23012`, creation FILETIME `134391087409492948`, acquired at 05:45:41.494904 UTC. The process record named the same Steam client as parent. One new app `1716740` tracking record appended to the fingerprinted Steam log matched the exact PID and executable path. |
| Operator phase | Maintainer reported arrival at the visible title card. The controller recorded the epoch- and nonce-bound chat marker at 05:46:39.606924 UTC. The immediate chat statement confirmed arrival. The protocol label was `TITLE_CARD_RESPONSIVE`. The maintainer separately confirmed responsiveness after seal and exit. These are operator observations with receipt clocks. |
| Snapshot 1 | Tool Help enumeration at 05:46:39.631992 UTC. 146 modules, with no enumeration, file or PE read errors. |
| Snapshot 2 | Tool Help enumeration at 05:46:41.180741 UTC. 146 modules, with no enumeration, file or PE read errors. |
| Scientific seal | Sequence 10, 151,281 bytes, sealed at 05:46:42.726069 UTC. SHA-256 `f6b5674c9c3159b27e8a442a61d82190b081e78e995ace7340a040e3366d9848`. |
| Game exit | Same retained handle signaled at 05:47:06.538354 UTC with exit code `0`. Maintainer reported Quit from the main menu. Exit occurred after the scientific seal. |

The collector requested `0x101010` for the target, adding
`PROCESS_VM_READ` to limited query and synchronization for bounded reads
of the mapped main-image DOS, COFF and optional headers. It requested
`0x101000` for the Steam client. The x64 Python 3.14.3 controller and
inventory core requested no thread handles. Their disposable controls
reproduced successful acquisition and sealing, and refusal of a mismatched
title-marker epoch. The archived interactive controller and its exact
disposable cases are custody-only. The [tracked inventory fixture](../tools/srr008/README.md#disposable-module-inventory)
repeats read-only inventory and the wrong-epoch control.

The live journal records the actual source and
dependency hashes. The interactive controller SHA-256 is
`7447908960f69d44f5ebf17bed0d487854b83cfa5f231ff4a5d0bd82d25a2af6`.

Both samples used the same retained epoch and main image at
`0x7FF755E20000` with extent `0x89C2000`. The mapped header fields matched
the pinned disk PE, including AMD64 machine, PE32+ magic, nine sections,
timestamp, image extent and checksum. For each enumerated module the
journal records its base, extent, path, file identity, SHA-256 and disk
PE fields. The snapshot comparison found zero one-sided or changed
records. Backing-file hashes identify the files read through the reported
paths. Mapped header agreement covers those header fields. Executable
pages and other mapped bytes were outside this comparison.

The 146 records comprise 128 Windows-path, 10 game-install-path, four
other Steam-path and four other-path entries. The backing `ntdll.dll` hash
matches the SRR-007 pin. Steam's `gameoverlayrenderer64.dll` appeared in both
inventories despite the stored per-game overlay setting. Presence establishes
a loaded module in these samples. Overlay UI activation and the reason it
loaded were unobserved. NVIDIA telemetry modules were recorded separately.
The sampled list showed no SFSE-named image. Tool Help samples describe
the reported loader list at two points and can miss intervening loads,
manual mappings or other loader-invisible images. The experiment leaves
startup coverage, universal module membership, allocator invocation and
later debugger safety unresolved.

### Postflight and admission handoff

The postflight found no changes in the 193 checked protected pairs, the
two designation checks, transient namespace metadata, the pinned
executable, relevant INIs or load-order files. Steam Cloud, overlay records
and the Cloud cache hash agreed. The Steam app manifest's full-file hash
changed during the run. The checked app ID, build, install directory and
state fields agreed, and the retail executable hash remained pinned.
Both drives stayed above the reserved floor. No restoration was performed.

The next bounded engineering action is an offline SRR-007 admission
profile for this executable and captured environment. Pin the main image
and critical system/Steam dependencies by approved backing-file and PE
identity and require fresh mapped checks at admission. Review the observed
overlay renderer explicitly. Exercise controls for missing critical
identity, a changed hash, legitimate optional module drift and epoch
mismatch. Unknown modules may remain recorded while claims that depend on
an unresolved critical identity stay held. Any live debugger test requires
its own authorization.

The installed-file and bounded run summary are eligible for scoped
publication. A public reproduction starts with the SRR-001 file checks
on a lawfully obtained copy. A new authorized run can reproduce the
observational method using a Steam PID/path record, Windows process identity
and Tool Help snapshots. The original run is a custody-backed historical
observation. Exact raw records, full inventories, account details, save
comparisons and operator records remain private. The task-only patch
excluded the user-supplied brief.

<!-- interactive-review-status:start -->
### Interactive-account independent review

**COMPLETE for the scoped title-time survey.** Independent internal challenger
`srr008_challenger` verified AC1–AC6, including the one Steam dispatch,
PID and creation epoch, mapped-image and backing-file evidence, both
146-record snapshots, title and exit receipt order, seal and preservation
checks. The challenger reran the disposable controls and checked the
task-only patch against the starting Git objects. Review clarified the
retrospective responsiveness confirmation and the public verification limit.

Reviewed substantive manifest SHA-256
`b96c6026d712b1288741c47c732739f20d30a4aa6c473e9595557fb8cea756ec`.
Only this review block is excluded from the dossier digest. Both prior
review blocks remain included as historical evidence.
<!-- interactive-review-status:end -->
