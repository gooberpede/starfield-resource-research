# SRR-007 — Retail launch boundary and Stage A qualification

**Stage A blocked. The disposable attach candidate begins at a verified
attach barrier. Initial startup and pre-title module-state construction
remain outside its coverage. Retail allocator execution is NOT TESTED.**
An empty post-title window cannot rule out earlier invocation.

## Launch and coverage assessment

| Route | Gate | Evidence and missing capability |
| --- | --- | --- |
| Direct executable under `DEBUG_ONLY_THIS_PROCESS` | **PASS** for disposable creation. **UNKNOWN** for retail startup. | SRR-006 retains the launch handle and arms the initial thread before continuing the genuine creation event. The current creation controls observed the fixture's TLS guard. The maintainer reports that an ordinary direct Starfield launch is expected to fail. An actual direct game attempt was outside this assignment. |
| `steam://rungameid/1716740` as a launch request | **PASS** for identifying the local handler. **UNKNOWN** for the current retail launch lifecycle. | A read of the `steam` protocol registration resolves to `steam.exe -- "%1"`. The maintainer reports previous successful launches. A shell result can refer to a handler process or contain no process handle. It does not establish the game image, creation epoch or debug ownership. |
| Steam-mediated game creation under observer control | **FAIL** for the delivered integration. **UNKNOWN** for a future instrumented broker. | `DEBUG_PROCESS` follows the debugger's process tree. The observed registration does not show that the eventual game is created in that tree, especially when an existing client handles the URI. A PID discovered after URI dispatch supplies no pre-instruction barrier. A future candidate needs a controlled and authenticated creation event for the actual retail image, successful initial-thread readback and separately authorized launch testing. |
| Exact-process attach after title confirmation | **PASS** for the restricted disposable adapter. **UNKNOWN** for the retail title process and module set. | Windows supplies a synthetic creation event with null start address and the current thread and DLL inventory. The fixture executed its TLS guard before attachment. Its positive chains come from continued hardware events after the authenticated attach breakpoint. No successor is adopted. |

The live boundary follows the actual process handle and event origin.
Windows documents different process creation flags and the synthetic
attach inventory. Both event types can use the same debug event code.
[Process creation flags](https://learn.microsoft.com/en-us/windows/win32/procthread/process-creation-flags),
[DebugActiveProcess](https://learn.microsoft.com/en-us/windows/win32/api/debugapi/nf-debugapi-debugactiveprocess),
[Shell execution process handles](https://learn.microsoft.com/en-us/windows/win32/api/shellapi/ns-shellapi-shellexecuteinfow).

The local outpost prior art separates opening a process, durable session
setup and the actual attach API. Reference-handles prior art distinguishes
the internal loader breakpoint from the exported attach breakpoint and
documents a detach failure even with restored code. SRR-007 follows the
SRR-006 ownership model and keeps the pump attached through exact-process
exit. The sibling inputs were read at outpost research
`d116bc63ff394b0156539161c8d1addfc902665a` and reference handles
`6a77579a184c64e0c080c8f3b7883c34bd17e24b`. Their source hashes and
inspection paths are in the local input receipt.
[SRR-006 evidence and prior art](SRR-006-four-site-hardware-observer.md),
[SRR-003 dispatch](SRR-003-retail-allocator-invocation-and-dispatch.md).

## Integrated disposable method

`observer.exe --fixture-attach <scenario> <new-directory>` starts a copy of
itself without a debugger. The fixture runs one TLS guard and creates a
parked worker before signaling readiness. Only the PID and creation epoch
of the retained child handle can reach attachment. Preflight checks that
the child is alive, is free of a debugger and reports the nominated file
identity. At the stopped attach creation event the existing verifier
matches both process handles, the event file and its digest, mapped PE
headers, code bytes and relocated slot before writing any debug register.
The retail-role negative control reaches that same verifier and refuses
the disposable image before arming. The retail profile's positive mapping
controls read the lawful disk copy and operate on synthetic mappings.

At the pinned `ntdll!DbgBreakPoint`, compare the mapped image and code
window, exception ownership, inventory and hardware-slot readback. The
current OS reports Windows NT `10.0.19045.0`. The only content-pinned system
DLL in this controller is x64 `ntdll.dll`, file version `10.0.19041.4842`,
SHA-256 `36b1a62e4bf6bf7d68458fff6e8a33b39f6527ec6a46e55ecdd12cde83894c8d`.
The other permitted fixture DLLs use a System32 path and mapped-image
predicate. This fixture set does not qualify a retail module inventory.
The designated disposable System32 `version.dll` control invalidates the
affected window's continuity and permits a fresh chain after unload.
Other unqualified module identities quarantine capture while retaining
the event pump. An unexpected callback return is
classified by the existing predicates and the observer continues.
Ambiguity can degrade the affected coverage without discarding an
independent, authenticated later positive. The registers, addresses and
stack operands read remain within the four-site profile.
[Controller](../tools/srr006/observer.cpp),
[Correlation predicates](../tools/srr006/correlation.h),
[Per-window evidence](../tools/srr006/window_evidence.h).

The event journal identifies the run as image SHA-256, PID and creation
FILETIME. The fixture harness submits ASCII request files by atomic rename
inside the local run directory. Use a trusted directory with operator-only
write access for any future retail adaptation. The deterministic run ID is
a binding to that epoch, and directory access controls provide the writer
trust. Every accepted statement has a receipt sequence, QPC and UTC
FILETIME. Those values order receipts, not UI frames or instruction time.

| State | Receipt and required payload |
| --- | --- |
| STARTUP | `startup` records `covered:false` before attaching. `attach_barrier` opens the earliest candidate window after the continued break-in. |
| TITLE_CARD | `title.request` contains `<run> 1 TITLE_CARD 0` and LF. Wait for `PHASE_DURABLE <seq>` before advancing the fixture. |
| MAIN_MENU | `menu.request` contains `<run> 2 MAIN_MENU <title-seq>` and LF. The responsive-menu statement requires the durable title sequence. |
| STOP | `stop.request` contains `<run> 3 STOP 0` and LF. Admission closes even if menu confirmation never arrives. Before `STOP_DURABLE`, the writer flushes through that sequence and publishes `stop-prefix.json` with its exact byte count and SHA-256. |
| RETIRE | `retire.request` contains `<run> 4 RETIRE <stop-seq>` and LF. The pump continues owned events through exit. Retirement requires a separately durable acknowledgement. |
| EXIT | The continued exit event and independently retained handle must agree. A nonzero exit or an unconfirmed exit is an engineering outcome. |

A post-STOP crash leaves already authenticated, durable positive chains
usable. Absence conclusions require the particular window's verified
boundaries, continuity, resolved joins and durable prefix. The attach
receipt never issues a whole-run negative. A checkpoint is point-in-time
evidence. An intervening clear-and-restore of hardware slots can escape
it. A handoff recognized by the fixture marker invalidates its scope.
It does not establish generic Steam successor discovery.

## Reproduction and results

Use the x64 SDK `10.0.26100.0` and MSVC `19.51.36256.0` with the
[SRR-006 build and creation tests](SRR-006-four-site-hardware-observer.md#reproduce-the-fixture-controls).
From the repository root, use Python `3.14.3` and a fresh ignored directory
for the attach harness. Set `$srrObserver` to the freshly compiled
`observer.exe` and `$srrAttachOutput` to a new run directory.

```powershell
python -B tools/srr006/qualify_attach.py $srrObserver $srrAttachOutput
```

This executes the real fixture attach entry point, authenticates its output
with the existing journal and supervisor helpers and writes only disposable
files into the nominated directory. The build and tests read original tool
sources, the installed SDK and the lawful analysis copy for the mapping
control. They leave the Ghidra project untouched. The attach harness
refuses an external PID argument, a retail attach command and a Steam URI.
Both harnesses reserve 134,217,728 bytes per drive above the
40,000,000,000 caller-available byte floor. The writer repeats the check
before each batch. Fixture watchdogs and the 25 ms debug-event wait are
test and polling mechanisms. There is no scientific inactivity cutoff.

The prior Run 05 disposable executable SHA-256 is
`8fea600cad334458426514f298db76f72c5d99abd6ce38f356d14d277df8eb82`.
The four changed source hashes, including the harness, are in the
reviewed manifest. The unchanged MASM fixture, verifier, retail
manifest, correlation and window model are pinned with the other
build inputs in the local receipts. Run 05 passed all 15 attach
scenarios and all 25 creation scenarios. The three compiled controls
passed correlation, window evidence and profile mapping.

| Disposable control | Evidence |
| --- | --- |
| Attach baseline and busy | Initial creation replay starts at a null start address. The fixture had already executed one TLS guard, and the attach windows contain none of that startup execution. The barrier verified the pre-existing worker and armed later workers on their thread events. Baseline observed 10 guard, 144 iterator, 16 callback and eight allocator hits. Busy flushed 4,221 rows, with 4,096 nonfocal iterator arrivals and eight allocator arrivals. |
| Operator ordering | Wrong birth epoch, unbound legacy marker, premature menu and premature retire requests did not advance their respective phases. The operator harness delayed the valid title statement by at least 400 ms. Run 05's baseline, busy and crash runs kept qualified per-window coverage through STOP. |
| Anomaly and coverage | Direct wrong-return callback was nonfocal and a later full chain remained observable. The unreadable form control preserved invocation evidence and lacked allocator completeness. The controlled `version.dll` load and unload invalidated the title window's continuity, preserved a post-unload positive in that window and allowed a qualified menu window. Persistent slot loss is injected at checkpoint evaluation and prevents a complete negative. |
| Refusals and handoff | The retail role refused the disposable file identity before register writes. Context conflict and readback mismatch stimuli took the disposable recovery branch. The handoff fixture's known successor was never attached. Its receipt remains incomplete. |
| Storage and crash | The queue limit flushed all 60 accepted records but lost later rows. An injected partial write preserved 28 of 91 accepted rows and no durable STOP. The crash control retained all 43 records, reproduced the exact prefix bytes observed before the deliberate retirement fault and independently verified the sealed STOP prefix. It retained `OBSERVED_REACHED_ALLOCATOR` alongside nonzero exit. |
| Emergency | A run-bound emergency request terminated only the retained disposable process with `0x6006`. A restricted handle produced real access denial, with the process remaining available for cooperative Quit. Fixture-only timeouts bound supervision. |

The earlier busy test exposed a failed atomic watermark replacement
with a complete temporary watermark and surviving prior prefix. The
writer now retries sharing or access-denied replacement failures
briefly. The retry belongs to publication, and failures still close
admission if the watermark cannot be published. The evidence does not
identify the process that briefly held the destination. Failed attempts
and final journals remain under the local SRR-007 run directories.

## Continuation — patch identity, breakpoint attribution and recovery

The supplied SRR-007 patch SHA-256
`9bc6584596f863f32c76bfc39117a9101bbc28b9fae5d3e1127a67ddab9f5768`
matches the SRR-007 independent final receipt and the original Git-native
export. Independent replay against the starting Git contents reproduced
all six reviewed files byte-for-byte. The separately supplied SHA-256
`82200b45405319ce397206ca071ad00046ecf4486592631d926eb52c63e62725`
identifies the archived **SRR-006 round-two** patch, corroborated by the
SRR-006 round-two independent report. The discrepancy came from citing
the earlier investigation's patch hash. The prior SRR-007 patch and its
independent receipts are retained locally.

On the pinned Windows image the attach check requires the thread's
event-reported start at `ntdll+0xCCAF0` (`DbgUiRemoteBreakin`), the
first-chance exception and instruction pointer at `DbgBreakPoint`, and
the top-of-stack return to `ntdll+0xCCB3E` from a verified mapped call
site. The stopped census and context ownership checks still apply.
For a recovery request the candidate also needs a generation newer than
the request's observed thread generation. These predicates distinguish
the tested pre-existing thread's same-export breakpoint. They are
observational and cannot authenticate the origin of a separately created
thread matching the same start, return and event ordering.

The competitor fixture holds only the reported disposable break-in thread
long enough to deliver a real direct `DbgBreakPoint` on the pre-existing
thread. The exception was passed to its own handler, the genuine break-in
then opened the barrier, and the four sites subsequently recorded a
complete causal chain.

The `recover-*` cases use the same integrated attach entry point and
set kill-on-debugger-exit false before any arming. They require durable STOP
and RETIRE before accepting a run-bound recovery request. A matching
`DebugBreakProcess` exception stops the complete census. The observer
retains an extra suspension and a duplicate handle per thread, restores
only the exact debug registers it owns, and verifies restoration.
The observer continues the held event with its owned disposition and
rechecks the contexts while the extra suspensions still hold. An
exact-process detach follows only verified restoration; the observer
then releases its own suspensions. The harness retains the original
process handle through Quit. Existing and newly created fixture threads
execute guard sites after the attempt. The fixture checks whether
debugger attachment agrees with the outcome.

Refusal before restore, partial restoration, and an injected detach
failure keep the observer attached and continue servicing owned events
through cooperative exit. A transient wait failure and a failed first
continuation are covered with API-boundary stimuli. The non-killing
mode refuses a fixture termination request. Persistent inability to
continue an owned event or release a suspension leaves the controller
responsible for that event or handle. Recovery is unconfirmed while
retrying, and a hard pump loss while slots are armed remains outside
the tested recovery contract. This procedure does not establish a
guarantee of graceful exit. The separate deliberate fixture crash
continues to qualify the sealed pre-STOP evidence.

Continuation build SHA-256
`e79f5f3258585ea868c995fab541b325889deb86242841480ea567984d696ca1`.
The full attach suite covers the prior 15 scenarios and seven additional
controls. The ordered competitor is journal sequence 25, the real
break-in is 26, and the barrier is 27 in the principal run. The three
native detach successes include normal detach, one transient wait
failure and a failed first continuation with a successful retry.
The three attached recovery outcomes cover pre-write refusal, mixed
restore readback and a refused detach call. All six retained the
pre-STOP allocator chain and exited zero. The separate crash control
retained the sealed prefix and the nonzero native exception exit.
Build and journal receipts are in the private continuation directory.

## Proposed Stage A run card — blocked

1. Use Starfield `1.16.244.0`, Steam app `1716740` installed build
   `23518663`, executable SHA-256
   `7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28`
   and mapped profile
   `b7e7d773e0b9181ee88f48c0a65bff8ac60497e68e85851826c5b8acdf4b853f`.
   The exact reviewed candidate build below accepts disposable targets
   only. Before requesting Stage A, integrate a separately reviewed
   retail admission gate with the nominated path, retained handle,
   PID and birth, verified executable and module fingerprints, full
   arming readback, the qualified competing-breakpoint predicate and the
   selected non-killing recovery policy. Pin the exact binary,
   source manifest, Windows build, ntdll and approved title-time module
   map for that future revision.
2. With separate authority, the maintainer snapshots active saves,
   independent backups, game configuration and Steam sync state and
   qualifies an empty, isolated writable save location. The maintainer
   verifies SFSE absence and disables Steam Cloud and Steam and NVIDIA
   overlays for the isolated run. Both drives must meet the projected
   free-space floor. The maintainer owns settings, backups and restoration.
3. With explicit approval, launch via `steam://rungameid/1716740` and
   let the operator confirm the visible title card. Identify one exact
   live game image and epoch. Attach once via the reviewed gate while
   the operator waits at title. Require the authenticated barrier,
   durable title statement and valid coverage before advancing. The
   operator presses the key/button, confirms a responsive main menu and
   submits its marker. The controller does not manipulate the UI.
   Neither initial startup nor pre-title construction is observable
   on this route. No save load is part of the run.
4. The operator sends STOP and waits for a verified durable prefix.
   The controller records observations and completeness by window. It
   serves owned events during retirement and the operator uses Quit
   after the retirement acknowledgement. Confirm the continued EXIT
   event against the retained handle. Classify a post-STOP crash
   separately and preserve the verified pre-STOP prefix.
5. A future supervisor must expose last pump progress, held event
   ownership, queue and writer health and disk observations. Record a
   missed check and investigate. Sustained event progress or operator
   delay does not justify emergency action. After demonstrated control
   failure, preserve the durable prefix and seek maintainer direction.
   Retail forced termination has no approval. Any proposed exact-handle
   action needs separately bounded authorization and qualification.
   The disposable kill-on-exit default carries a target-termination
   risk on debugger loss and is unsuitable as an implicit retail policy.
   Use only the reviewed live adaptation of the disposable non-killing
   procedure. Report an abnormal exit separately from usable pre-STOP
   evidence. [Win32 kill-on-exit behavior](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-debugsetprocesskillonexit).
6. Confirm both exact PIDs have exited as appropriate, check isolated
   writes and backup/live save hashes, verify sync state before and
   after maintainer restoration, and restore only the explicitly logged
   settings and isolation changes. Retain the journal and manifest
   privately. Report process exit, protection verification and scientific
   outcome independently.

The smallest separate live survey is one maintainer-operated Steam URI
launch in the qualified isolated no-save environment, paused at the
visible title card. Authorize read-only inventory and process identity
collection for that launch only. Retain a query/synchronize handle,
record PID, creation FILETIME, architecture, full executable path,
on-disk file identity/version/SHA-256 and Windows build, and compare
against the pinned executable. Take two closely spaced module snapshots
while the operator remains at title. Record module bases, image extents,
backing paths and content hashes for the exact process. Recheck the
handle, epoch and module list at both boundaries. An inaccessible file,
unknown backing or inventory drift is an unresolved pin. Keep private
paths and raw receipts local. The operator advances only as needed to
use normal Quit, with the survey ending before advance. This survey uses
process query and module enumeration, without debugger attachment,
thread suspension, context writes or breakpoint placement. Check exit
and protection/restoration as in the run card. The inventory would
allow the retail admission build and a title-time approval policy to
be finalized and reviewed. A subsequent Stage A approval must name
that exact build, the Steam launch and attach sequence, read and debug
rights, output custody, operator actions and the chosen recovery
authority. Save2/HIST-0245, gameplay and Lodge crossing remain separate.
[SRR-005 preparation](SRR-005-live-observation-preparation.md).

## Custody and publication

Starting HEAD was `9886fd16b18b1c16fac6533d0a33c381202c4c65`, tree
`d08c406eba918e28535e55046180c1ef68de6ce5`, index SHA-256
`285b556fde4dc00297ead61459bf1a2bf41bb2f2e72d6c31bfe592b407002108`.
The supplied untracked brief was the only starting status entry.
Initial space was 75,570,974,720 caller-available bytes on C: and
69,648,470,016 on D:. Git used `2.53.0.windows.1`. The local start and
end receipts record exact status and protected dependency hashes.
No Steam or Starfield process was started or attached, and game
settings, saves, Steam sync and Ghidra were left alone.

For public fixture verification, start at the repository, build the
original MASM and C++ sources with the named SDK and compiler, and
run the fixture baseline and crash controls. The tests check a missed
pre-attach TLS site, causally linked post-barrier hits and byte
identity of the pre-crash durable prefix. Retail identity and mapping
controls require a lawfully obtained matching copy. Retail launch,
pre-title ordering, module inventory, actual invocation and lifecycle
remain held from publication as observed results. Private paths,
native payloads, executable binaries and reviewer rounds stay local.

<!-- review-status:start -->
## Independent review disposition

**BLOCKED for Stage A.** Independent internal challenger
`srr007_challenger` accepted the corrected disposable snapshot and the
blocked retail handoff. The original review reproduced capture suppression
after an unfamiliar module load and accepted the revised post-unload
positive, sealed STOP and crash evidence. Its manifest was
`a51639024e158efa2b32bfaa4f1767d7d4fb9bd1cc300ee065d61c12fadd49fc`.
The continuation independently reconciled both patch identities,
reran nine focused cases on the current build, checked the native
competing event, verified post-continuation register readback for
detach and confirmed crash tolerance. The final engineering controls
passed 22 attach scenarios, 25 creation scenarios and three compiled
controls. The blocker is the title-time retail module survey and the
final retail admission build, including the scoped recovery contract.
Initial startup remains a separate unknown.

Reviewed manifest SHA-256
`bc47d35e08b9dd8fbc31f83b348e71eaa0c2f94e4ca75c323ca63a98a850da88`.
The six sorted entries contain each file's SHA-256, two spaces, its
repository-relative path and LF. Only this marked block is excluded
from the dossier digest. Review evidence and receipts remain local.
<!-- review-status:end -->
