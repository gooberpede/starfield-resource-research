# SRR-009 — Retail four-site Stage A observation

## Finding

**Qualified `NOT_OBSERVED`.** On retail Starfield 1.16.244.0, the four-site
observer recorded zero site hits, focal invocations or correlated allocator
arrivals in two verified post-title windows totaling **84.281 seconds**.
Initial arming verified 95 thread generations. Four subsequently arrived
threads also had verified register readbacks in the observation windows.

| Qualified window | Durable journal interval | Duration |
| --- | --- | ---: |
| Post-arming title through the transition to the main menu | [439, 483) | 52.253 s |
| Responsive main menu through scientific STOP | [483, 500) | 32.029 s |

### Applicability and limitations

Coverage starts at verified post-title arming. The result leaves pre-arm
startup, save loading, gameplay, and other builds or execution paths
unresolved. The first two attempts ended with
`INSTRUMENTATION_INCOMPLETE` before debugger attachment. In the third,
the game exited normally. Normal debugger retirement remained unconfirmed,
and the exact observer was later administratively terminated after
verified game exit.

### Evidence and verification

**Custody-backed historical observation.** The
[third attempt](#third-stage-a-attempt--15-november-2026) was sealed at
sequence 500, **353,147 bytes**, SHA-256
`f4cd672725622db9c3e0d8a74bc5b4c3bb1c7bd1469ddd3b89017a8b33d80967`.
The access-recovery observer SHA-256 is
`dac1d88aea5b23e9725567b00426bfc3faa940a362e46521d59f15d10d64da88`.
The primary and handoff manifests, independent review and [closure
receipts](#administrative-observer-closure--15-november-2026) identify the
original run. Raw observations and private protection receipts stay in local
custody. The [dependency inventory](SRR-009-publication-verification.md)
lists the evidence and verification routes.

### Method and dependency requirements

**Reproducible method.** The [tracked observer and disposable fixture
instructions](SRR-006-four-site-hardware-observer.md#reproduce-the-fixture-controls)
use the declared Windows toolchain and lawful matching executable inputs.
The [tracked protection, environment and inventory checks](../tools/srr008/README.md)
run offline on synthetic inputs. Actual protection comparisons also
require the maintainer's private policy, saves and independent backups.
See the [historical Stage A brief summary](implementation-briefs/README.md#srr-009-stage-a)
for authorization and custody. Live runs require separate authority.

## Historical engineering record

Phase 1 qualified a disposable candidate. This record preserves the scope,
configuration and independently reviewed engineering and operational history
through all three retail attempts.

## Inputs and applicability

The starting Git HEAD was `1fd0b0d33c1212721a483ac0078a89fbc9f9a3c7`.
The index-entry hash was `9727b8da3557d1719027fc1b6c07cf889db04346`.
The supplied SRR-009 brief was the only initial untracked path. The task patch
excluded it. Build and capture receipts have private custody.

| Pin | Value |
| --- | --- |
| Installed and offline analysis image | Retail `Starfield.exe`, file and product version `1.16.244.0`, SHA-256 `7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28`, preferred base `0x140000000` |
| Steam installation and launch | App `1716740`, build `23518663`, state 4, installation directory `Starfield`, URI `steam://rungameid/1716740` |
| Runtime used for breakpoint attribution | Native Windows build 19045, System32 `ntdll.dll` SHA-256 `36b1a62e4bf6bf7d68458fff6e8a33b39f6527ec6a46e55ecdd12cde83894c8d` |
| Retail image profile | `b7e7d773e0b9181ee88f48c0a65bff8ac60497e68e85851826c5b8acdf4b853f`, thirteen mapped windows and two ASLR-adjusted pointer slots |
| Toolchain | MSVC `14.51.36231` x64, Windows SDK `10.0.26100.0`, Python `3.14.3` x64, Git `2.53.0.windows.1` |

The [SRR-003 static predicates](SRR-003-retail-allocator-invocation-and-dispatch.md#native-path-and-predicates)
and [SRR-005 causal join](SRR-005-live-observation-preparation.md#sites-and-causal-join)
govern the four sites `0x9518FD`, `0x5932EF`, `0x77C470`, and `0x779760`, in
DR0–DR3 order. The iterator, callback and allocator join uses the same process
epoch, thread birth and frame, the focal sweep return, vptr/slot and form
identity, and checked native stack ancestry. A callback can establish invocation
even if the form type was rejected or unavailable. The allocator requires the
accepted PNDT type and the additional adapter predicates. The sites can establish
allocator arrival. Per-biome allocation output and pre-title execution are
outside their observation contract.

## Admission and scope of coverage

The [SRR-008 interactive survey](SRR-008-retail-title-time-environment-survey.md#interactive-account-survey--14-november-2026)
recorded two identical 146-entry inventories in one exact epoch. The original
151,281-byte prefix through sequence 10 verifies against SHA-256
`f6b5674c9c3159b27e8a442a61d82190b081e78e995ace7340a040e3366d9848`.
The Stage A policy adopts the following distinctions.

| Class | Evidence and behavior |
| --- | --- |
| Critical | Main image backing path, event file identity, full SHA-256, mapped PE and exact code/unwind windows and relocated slots. Native `ntdll.dll` uses the pinned System32 path/file and verified executable mapping at the actual base, including `DbgBreakPoint` `0xA10D0` and the `DbgUiRemoteBreakin` path from `0xCCAF0` through the call at `0xCCB39`. |
| Expected Steam | The names and mapped directories of `steam_api64.dll` in the game directory, and `steamclient64.dll`, `tier0_s64.dll` and `vstdlib_s64.dll` in the Steam root fit ordinary Steam integration. Their mapped code is outside the proof. The optional overlay renderer and `steam_api64.dll` follow the drifting rule in the next row. Overlay presence while per-game overlay is disabled was observed twice with the SRR-008 build; UI activation was unobserved. |
| Incidental | Direct System32 loader entries outside the breakpoint mechanism are recorded. NVIDIA graphics, NGX, and telemetry paths and the Defender module were incidental to the survey. Entries outside the runtime's explicit origin checks are recorded as unknown even when historically expected. |
| Drifting Steam component | Steam executables and libraries are independently updated software, not immutable dependencies of this research. `gameoverlayrenderer64.dll` mapped from the pinned Steam root, or `steam_api64.dll` from the pinned game directory, whose verified backing file no longer matches its recorded SRR-008 hash (`688cc70e58cd8d1f31345fdf93ba1b9ab08c77c38df847bd2b0ae2145a437a2f` and `1db3fd414039d3e5815a5721925dd2e0a3a9f2549603c6cab7c49b84966a1af3`) is admitted as drifting: the observed hash, size, file identity and version strings are journaled with both identities preserved (`steam_component_drift` summary plus module fields), never one hash silently replacing the other. Present before arming, drift is reported and admissible; it does not refuse admission or qualify the science. The same identity recording applies to the `steam.exe` client at `steam_baseline`, whose drift never refuses. |
| Unknown / incompatible | A valid unknown image is logged and can coexist with acquisition. Its post-arm arrival or departure conservatively invalidates affected continuity and clears frame tokens; the same applies to a drifting Steam component arriving or unloading during observation, which qualifies the affected window while earlier durable positives remain assessable. Reused module bases without an observed unload, unload of the pinned runtime, incompatible mappings, SFSE-named images, an overlay-named image whose backing file or origin cannot be verified (lookalike), and critical-image drift invalidate acquisition. |

The module evidence is a loader/debug-event view. An event file handle, where
available, improves backing-file attribution. ASLR changes bases without
changing backing-file identity. Reads of mapped windows verify only those
ranges. The observer cannot inventory manual mappings, exclude transient
changes between checks, or infer that mapped incidental code equals its disk
bytes. Review drift by its mechanism and effect on the active interval.

The controller first retains the exact Steam client and one later-born,
same-account and same-session native AMD64 target. It corroborates the target
with its direct parent and exactly one new full app/PID/path tracking line in
the checked tail of Steam's log. The controller does not dispatch a URI. Record
the human or approved dispatch separately. Neither the log nor the relation
to the Steam client independently identifies the URI. A rotated/truncated log,
ambiguous targets or a changed process epoch refuses acquisition. The target
handle is retained through exit and a successor is never adopted.

The manifest's attach window is the first window that may support a zero.
The stopped barrier requires the retained epoch, image and runtime checks,
module and exact thread census, all initial debug registers unowned, and
readback of each armed slot. Attachment itself is accepted when the
first-chance trap has the pinned address/bytes, RIP, DR6/flags, fresh
break-in thread start and native stack return from the pinned call. A genuine
competing exception on another thread remains the target's exception.
The observations cannot cryptographically attribute a separately created
thread that duplicates the device, stack, and timing of the break-in.

New thread events, per-hit DR ownership/RF/DR6, and idle/held readbacks apply
after arming. The held poll verifies already tracked live thread contexts
without comparing the OS list to potentially pending birth/exit events. Idle
and phase/STOP checks attempt the full census. A qualified zero applies only
to the bounded, observed epoch with a complete journal and verified
boundaries. These checks sample execution state. Unknown module transitions,
foreign exceptions that could unwind a frame, ambiguous joins, active event
pump failure, or missed readbacks qualify the affected scientific result.
An earlier durable positive can remain assessable independently.

## Draft Stage A run card

**Approval gate.** Use the binary and source manifest identified by separate
written authorization and verify their approved SHA-256 digests. The review
blocks below identify historical candidates. Run the observer and log under the same
ordinary interactive account and session as the designated Steam instance.
Verify the protected preflight before running the command. Retain an open
operator console and a separate shell for markers. Allow ordinary long
pauses. There is no experimental inactivity cutoff.

1. Compare the approved binary hash, pinned file versions and digests, app
   installation fields, Steam URI handler, interactive account and session, and
   relevant settings. Cloud and per-game Steam overlay must be off. Obtain
   operator confirmation that NVIDIA overlay is off. Check SFSE loader and
   native plugin deployment in the install and effective Documents paths.
   Leave inert Vortex markers alone. Inspect the effective INIs, save
   namespace, load order and backups as in SRR-008. There should be no existing
   Starfield process at baseline. The operator and marker shells must not
   define `__COMPAT_LAYER` or another inherited AppCompat layer: a layer maps
   `apphelp.dll` into the observed process, which is outside the fixture
   allowlist and therefore quarantined as unexpected. The offline
   qualification below records that shell case.
   A Steam client self-update since SRR-008 is expected drift, not a blocker:
   preflight verifies the overlay's origin and file identity, records its
   current hash and version against the SRR-008 pin, and proceeds whether the
   pin matches or drift is reported. Only an overlay-named image whose origin
   cannot be verified (lookalike) refuses admission.
   Preserve populated Saves directories.
2. Check available space on C: and D: before every material write stage,
   including the run directory, with a 134,217,728-byte reservation per drive
   above the 40,000,000,000-byte floor. The journal writer rechecks every
   write batch. Use a fresh, private, ordinary directory under
   `.local-work/codex/SRR-009/` with a trusted parent ACL and no reparse
   components. Launch the reviewed observer only after written authorization.

   ```powershell
   & $observer --stage-a --approved-stage-a $runDirectory
   ```

   The second flag selects the retail route. Written approval is a human
   gate. The observer has no game-launch code, no arbitrary-PID command, and
   no credentials or privilege changes. Once it displays `BASELINE_DURABLE`,
   record dispatch intent, UTC, URI and dispatch result locally. Invoke the
   authorized Steam URI once under the same interactive account.
3. Wait for `TARGET_BOUND`. Leave the title card on screen. When the operator
   confirms it is responsive, store the full token as `$run` and issue
   the title statement with the pinned Python executable. That statement
   authorizes the observer's next transition within the approved session.

   ```powershell
   & $python -B tools/srr006/stage_a_marker.py $runDirectory $run TITLE_CONFIRMED
   ```

   Wait for `ATTACH_ARMED <sequence>`, which follows journal flush and
   readback. Check `stopped_admission` and all `arm_readback` rows. Startup
   and title time before this barrier are uncovered. On refusal, retain all
   evidence and keep any attached pump servicing events through normal exit.
4. The operator advances to the main menu and confirms responsiveness. Use
   the acknowledged barrier sequence for `$armSequence`. Wait for
   `MENU_DURABLE` and check the `operator_menu` checkpoint. Marker times are
   times of reported states.

   ```powershell
   & $python -B tools/srr006/stage_a_marker.py $runDirectory $run MAIN_MENU_CONFIRMED $armSequence
   ```

5. At the operator's coherent stopping point publish STOP. Acknowledge only
   after `STOP_DURABLE <sequence>` and independent verification of the exact
   byte prefix in `stop-prefix.json`. An integrity failure or unconfirmed
   marker ends the affected acquisition. Preserve the particular durable
   watermark and any compatible partial positives. After the seal, request
   retirement, wait for `RETIRE_DURABLE`, and Quit using the normal game UI.

   ```powershell
   & $python -B tools/srr006/stage_a_marker.py $runDirectory $run STOP
   & $python -B tools/srr006/stage_a_marker.py $runDirectory $run QUIT_REQUESTED $stopSequence
   ```

   The observer continues serving owned traps and waits for the exact exit
   event and original process handle. If capture cannot acknowledge STOP,
   preserve the available watermark and have the operator quit normally
   when safe, recording the missing marker. Do not close the debugger console
   while it owns an active attachment.
6. Check the STOP sequence, byte length and SHA-256 over exactly that many
   journal bytes. Verify consecutive sequence IDs, process epoch, successful
   continuation, breakpoint ownership and the causal chain. Record the
   scientific outcome, observer health, target exit, and environment
   protection separately. If normal retirement fails after a verified
   prefix, preserve the prefix and classify the later failure independently.
   Compare app build fields, executable/runtime, relevant INIs and effective
   plugin state, the original save and backup content and namespace, and
   Steam Cloud state/cache against preflight. Retain logs and receipts locally.

| Event | Operator action |
| --- | --- |
| Launch fails or process identity is ambiguous | Preserve the dispatch receipt. Before title, place the regular file `cancel-before-target` in the private run directory if the observer is still waiting. No alternative launch or successor attachment. |
| Title report arrives after advance, exit or a different process | Withhold the title marker. If the same original process exits while waiting, retain its handle outcome. A late marker on the same still-responsive title can only start later coverage. |
| Modules differ | Record names and effective origin. Continue for permitted differences as specified by the policy. If the critical checks fail, cease scientific acquisition and use the same normal-quit path. |
| Early process exit or crash | Retain exit event, same-handle status, and any verified prefix. An open or failed window is incomplete. A valid earlier chain through the original STOP seal remains assessable after a later crash. |
| Loss of pump, unconfirmed continuation/suspension release or kill-on-exit setup failure | Keep the owning pump and console alive. Preserve output and escalate with exact current state. Normal STOP and Quit remain the planned actions. Do not request a second attachment. |

The non-killing policy is requested immediately after the debug connection,
before any context writes. Windows requires a connection before changing
the policy. A failed call leaves the default potentially destructive while
the pump tracks the same target for normal exit. A hard observer or OS failure
can abandon the connection or leave debugger-owned DR slots installed. Neither
the kill-policy toggle nor the retry path guarantees survival. The pump retries
continuation of the same held event/disposition for 250 ms. Persistent failures
remain explicitly unresolved and the owning pump keeps trying without an
automatic kill. Suspension release retries only the observer's own exact
handle obligation.

The existing [SRR-007 fixture recovery](SRR-007-retail-launch-and-stage-a-qualification.md#continuation--patch-identity-breakpoint-attribution-and-recovery)
qualifies an emergency proposal consisting of an exact-process break,
stopped census, restoration/readback of owned registers under retained
balanced suspensions, and detach only after verified restoration. Retail
has no recovery marker for this operation. A later authorization would
need to approve reviewed implementation and exact intervention terms.
Any forced exit or debugger teardown likewise needs separate authority.
[Windows kill-on-exit API](https://learn.microsoft.com/windows/win32/api/winbase/nf-winbase-debugsetprocesskillonexit).

## Reproduction, protection and publication

Use the pinned x64 compiler and the [SRR-006 build commands](SRR-006-four-site-hardware-observer.md#reproduce-the-fixture-controls)
with a fresh local build directory and the lawful analysis copy. Run the
existing creation and attach harnesses and the new focused controls.

```powershell
& $python -B tools/srr006/qualify_stage_a.py $observer $newFixtureEvidenceDirectory
```

The fixtures read the reviewed binary, lawful PE and System32 test inputs.
They write only to their designated local evidence directories. They modify
no Ghidra project. The staged fixture cases cover a real optional image load
and unload, a real competing breakpoint with a premature menu marker, and
quiet/delayed control. The Steam drift controls simulate an updated client
layout in the run directory: an origin-verified overlay whose hash differs
from the SRR-008 pin and is present before arming
(`admission-overlay-drift`, admitted with a recorded
`steam_component_drift` row and a full scientific positive), the same
drifting overlay arriving mid-observation (`admission-drift-arrival`, the
earlier durable positive survives and the affected window is qualified), and
a same-named overlay loaded from outside the pinned origin
(`admission-overlay-lookalike`, classified incompatible at its load event
with no arm attempts; in retail the same classification refuses during the
pre-attach census). Injected results model critical identity drift, replaced
DR3 at readback, and failed first continuation after an already durable-path
invocation. The existing suites cover target crashes, STOP during busy work,
journal short write/overflow, process handoff, missing slots, adverse causal
frames, and recovery refusal or partial restoration. Keep API-boundary
injections distinct from OS load events, exceptions and exits. Run the suites
from a shell without an inherited AppCompat layer: with `__COMPAT_LAYER`
defined, the loader maps `apphelp.dll` into the disposable child and the
unknown-module policy failed the first fixture scenario. One
qualification attempt on the rework also failed when the stopped census
rejected the fixture child's main thread with every other pre-arm check
green; the observer correctly refused arming rather than share the thread.
A diagnostic build attributed the rejection to foreign debug-register state
on that thread (occupied slots, trap flag, DR6 hits) — the preserved journal
records the refusal, not the register dump. The transient interference was
not reproducible afterwards. Standalone child probes read clean. Stage A preflight's unowned-register check is
the same guard at retail.

The historical run used the local SRR-008 `interactive/check-saves.py`
and a routing-only copy of `interactive/environment.ps1`. Their exact
commands and inputs are custody-only. The supported offline procedure uses
the [tracked checks](../tools/srr008/README.md) with `-E -B`, a pinned
private policy and separate fresh output directories for each pre/post
check. Inspect the success fields, all pairs, designations and unclassified
entries. Retain both namespaces and independent backups in place.
Protection and environment receipts are private.

Public verification starts with the [retail pin procedure](PROVENANCE.md#current-retail-identity)
and the build and fixture commands above. The retail profile test compares
lawful file windows at preferred and rebased addresses and checks correct and
incorrect relocated slots. The survey's original process inventory, Steam
tracking records, account and save paths and proprietary code/process bytes
remain local. Phase 1 established fixture results. The later retail
observations are recorded below.

<!-- srr009-review:start -->
## Independent review

**READY FOR STAGE A APPROVAL** — round-2 independent challenge,
2026-11-15. The challenger was a separate agent session that did not author the
candidate; it re-ran the three qualification suites itself against the frozen
binary (creation 25/25, attach 22/22, stage 6/6), re-derived the binary
timestamp-only equivalence, reproduced the preserved AppCompat-layer refusal,
verified the STOP seals and allocator chains on its own journals, attempted
eight falsifications without success, and confirmed every P1-AC1–P1-AC7
criterion. The table identifies that historical review and candidate.

| Identity | Value |
| --- | --- |
| Round-2 review | SHA-256 `ded77f8830cbe680f0ae41dc64e13a5dccfccf7b0bb3790274013b606b18184b` |
| Reviewed task-file set | manifest v1 SHA-256 `f777e9eb9f08e4927061aab337e9287dfcaa53180b17bda417315b08fa8c7931` (adding this review block was the sole change in the original handoff) |
| Challenger-verified binary | `34b3e0acb7cf053c0f7d93e4daf9b8c4e8a16b19b6a8c6a6693135197c916019` |
| Integrator rebuild | `399b60c6318fbcc0a71907004b5a1213136beb21bfcb010a5c405308bc762fee` (identical except the wall-clock PE TimeDateStamp) |

The round-2 handoff identified its candidate by closing manifest v2 and
the task patch. Stage A still required separate written authorization.

**Scope deviation on record (maintainer direction, 2026-11-15).** During the
round-2 review the challenger exercised the freeze binary's
`--stage-a --approved-stage-a` admission path once against the live
interactive session: it authenticated the single Steam client, wrote
`steam_baseline`, printed `BASELINE_DURABLE`, launched and attached to
nothing (no Starfield process existed), and exited through the documented
`cancel-before-target` control with an `admission_refused` receipt. The
maintainer has recorded this as a deviation from the Phase 1 offline
boundary. Its factual results are retained unchanged as evidence; it is not
a precedent. All subsequent review rounds operate strictly within the
offline boundary.

**Round 3 — rework review, 2026-11-15: READY FOR STAGE A APPROVAL.** After
the maintainer's Steam-component drift directive, a fresh challenger agent
reviewed the revised candidate without authoring it and operated entirely
within the offline boundary. It re-ran all three suites itself (creation
25/25, attach 22/22, stage 9/9), verified each directive requirement in
source and receipts — strict rejection retained for the main image, the
ntdll attach runtime, SFSE-named images and origin-unverifiable overlay
lookalikes; origin-verified drift journaled with both identities and never
substituted; drifting arrivals qualifying coverage without terminating; no
global Windows state touched; the `__COMPAT_LAYER` control and preserved
failures intact; the round-2 scope deviation accurately recorded — and its
five falsification attempts all failed. Two non-blocking wording notes from
that review are incorporated above.

| Identity | Value |
| --- | --- |
| Round-3 review | SHA-256 `da26307915ba44fac72f61efddfa3ad605df76d4a3ec507b170d942fda146140` |
| Revised observer binary | SHA-256 `8962a74a230086c179f807c54de40aed5708f6e7cfaf5a75e8d103237eda6144` |
| Prior history preserved | round-2 review `ded77f88…`, manifests v1/v2, freeze binary `399b60c6…`, compat-layer and foreign-DR evidence — all unchanged |

The round-3 handoff identified its candidate by closing manifest v3 and
the task patch. Stage A still required separate written authorization.
<!-- srr009-review:end -->

## Stage A attempt — 15 November 2026

**Scientific outcome — `INSTRUMENTATION_INCOMPLETE`.** The maintainer
authorized one attempt against the round-3 frozen manifest
`51e9609458c40a01208f24cc8a2d395519276de2fceba190c2ee5af0f8257faa`
and the binary identified above. The adapter bound the Steam-launched
process and accepted the operator's responsive-title confirmation. The
aggregate pre-attach check returned false. The observer never called
`DebugActiveProcess`, armed any thread, or opened a scientific window.
Neither startup nor time at title or menu provides a qualified zero.

| Boundary (UTC) | Evidence |
| --- | --- |
| 01:48:37 | Ordinary non-elevated interactive account, same Windows session as the designated Steam instance, clean participating shell, and no existing Starfield process. The observer's Steam baseline flushed through sequence 2. |
| 01:49:37 | One `steam://rungameid/1716740` dispatch from the approved account, recorded with separate intent and shell return receipts. The observer bound the later-born native AMD64 retail epoch at sequence 3. |
| 01:50:32 | Operator confirmed the title was visible and responsive. Sequence 4 records the received marker and exact Steam append hash. The bounded retained log tail and append match the baseline and title digests. |
| 01:50:32 | Sequence 5 records `attach_refused`, `preflight:0`, `winerror:0`. The source assigns error zero on ineligibility and short-circuits the attach call. The recorded fields do not identify which preflight predicate failed. No overlay-lookalike event, stopped census, foreign debug-register observation, or arming readback was captured. |
| 01:52:04 | The operator reported normal Quit from the main menu. A separate read-only exit witness opened a query/synchronize handle before Quit, verified the exact PID, creation FILETIME, native architecture and image path against the bound process, and retained its own handle through exit code 0. The original observer handle had already closed. |

The observer recorded `steam.exe` drift alongside the SRR-008 pin
(`c97eb13c…` and `1e17d08c…` respectively), then proceeded through
process binding and title attribution. The attempt did not establish the
effective mapped overlay identity or explain the preflight refusal. The
compatibility-layer and foreign-DR incidents documented above are fixture
history. The retail refusal cannot be attributed to either.

The refusal journal is five consecutive records and 3,543 bytes. The
whole-journal SHA-256, final receipt, and durable sequence-5 watermark agree
at `2f548f0c3d17d92c620ea628751be640b9f5b577d0246d8f8c4a68b8393e5656`.
This is a durable refusal record. There was no `ATTACH_ARMED`, qualified
menu marker, scientific STOP, or `stop-prefix.json`. The observer reported
zero received debug events, no writer loss and an unopened pump. There
were no debugger recovery operations or forced intervention.

Fresh preflight and postflight verified the effective Documents and Steam
remote save roots with the pinned checker, isolated Python environment and
unchanged policy. All 98 Documents and 95 remote protected originals
matched their independent backups by length and SHA-256 before and after.
Both designations passed, no unclassified entries were present, and the
173 and 159 transient namespace records agreed. The populated saves
stayed in place. Cloud and per-game overlay stored settings and Cloud
cache digest agreed. NVIDIA overlay was operator-confirmed disabled.
The Steam app manifest's full file hash changed, with the checked app,
build, install directory and state fields equal. Executable and scoped
configuration hashes agreed, and both drives stayed above the floor
with the fixed reservation at the measured boundaries.

The game-bound capture used a restricted directory before launch.
The environment helper was adapted only to route output into the
new local run. Its source and adapted hashes are recorded with the
receipts. The two environment receipt ACLs were explicitly restricted
after collection. No frozen source or configuration changed. The
historical Phase 1 manifest, patch and reviews retain their identities.

The historical postflight manifest identifies the primary and preservation
receipts by SHA-256. The private capture contains the launch, title, refusal and
exit records and the bounded Steam log input. These contain operational
paths and process details and stay local. A follow-up would require
separate authorization. Before proposing another attempt, qualify
predicate-level refusal logging offline while preserving the admission
gate and the frozen candidate's historical record.

<!-- srr009-stage-a-review:start -->
### Stage A independent handoff

**BLOCKED at pre-attach admission.** Independent challenger
`srr009_challenger` verified the primary refusal journal, Steam attribution
and operator statements, the separately retained exact-process exit witness,
and scoped postflight preservation. P2-AC2 and the STOP prerequisite of
P2-AC3 remain blocked. The recorded scientific disposition is
`INSTRUMENTATION_INCOMPLETE`. This handoff documents the single authorized
attempt.

Reviewed substantive manifest SHA-256
`44ea2b85e4d95d1d158297726981bd60c2bfee667a27f609a508276042bc7247`.
Only this Stage A review block is excluded from the dossier digest.
The independent review has SHA-256 `9300a9345e93b8892db6c5de3e0a2bd020cf36c47363f2305df2d376c997f4e9`.
<!-- srr009-stage-a-review:end -->

## Offline admission diagnostics continuation — 15 November 2026

The first authorized attempt above remains **INSTRUMENTATION_INCOMPLETE**.
Its five-row journal identified the failing pre-attach phase and did not
record a leaf predicate. Diagnostics collected by this continuation cannot
retroactively resolve that refusal. The round-3 manifest and binary, first
attempt patch and evidence, and both historical review blocks remain preserved.

The continuation records the first failing predicate in the existing
short-circuit order. An `attach_refused` journal row with
`diagnostic_schema:1` carries the following fields.

| Field | Meaning |
| --- | --- |
| `stage` | `preflight` for a failed preflight check, `eligibility` for a later failed gate after successful preflight, or `debug_attach` for an actual `DebugActiveProcess` failure. |
| `predicate`, `detail` | Leaf decision and context such as target backing file, Steam process epoch, main-image mapping, overlay origin or the native attach mapping. |
| `operation`, `winerror` | Failing API and its immediately captured error when applicable. Pure comparisons have null error fields. |
| `expected`, `observed`, `rva` | Relevant safe measurements where available. Module-relative offsets identify mapping windows or relocated targets. Unexpected pointers outside the image are suppressed. Paths, SIDs, file IDs and instruction bytes are omitted from refusal metadata. |
| `preflight`, `attach_attempted` | Whether preflight passed and whether the attach API was actually reached. |

Module enumeration distinguishes creation, first entry and abnormal
iteration failure from a normal end with a required module absent. A
late iteration error still fails even if both required names were seen.
Digest and mapping details are reported from existing reads, including
errors from memory-query, read and hash operations. The patch adds no
target introspection or separate image scan to diagnose a refusal.
The original identity, mapping, eligibility and arming policy still applies.
Origin-verified Steam drift remains admissible and origin-unverifiable
overlays still fail.

A refusal requests a flush and waits for its exact sequence to appear in
the durable-prefix watermark. This wait can continue after the target exits.
It holds no debug connection or stopped event. If the row or watermark cannot
be committed, the console emits `ATTACH_REFUSAL_NOT_DURABLE` with the
diagnostic. The prior verified prefix remains the evidence boundary.
A refusal prefix does not qualify as a scientific STOP seal. Keep the
console output alongside `events.jsonl` and `durable-prefix.json`.

### Offline qualification and reproduction

The rebuilt observer SHA-256 is
`c52319bceb305e0da4eb6be7e51154388b54f985f8931b3b84650e8e3a7752c3`.
Its build uses the same pinned x64 MSVC/SDK, clean shell and lawful
offline PE inputs described above. Compile the additional focused test
in the same x64 build directory, with `SRR006_SOURCE` set as in the
[existing build instructions](SRR-006-four-site-hardware-observer.md#reproduce-the-fixture-controls).

```bat
cl /nologo /W4 /O2 /EHsc /std:c++20 "%SRR006_SOURCE%\admission_diagnostics_test.cpp" advapi32.lib
admission_diagnostics_test.exe focused > focused.console.txt 2>&1
```

From the repository root, use the pinned Python and point the verifier to
the resulting fresh fixture folder and console transcript.

```powershell
& $python -E -B tools/srr006/qualify_admission_diagnostics.py $focused $focusedConsole
```

The test program reads its own identity and two disposable output files,
checks a synthetic mapped image, and injects enumerator results and an attach
API failure. Rejected cases assert that the following eligibility or attach
callback cannot run where it is unauthorized. It never attaches to a target.
Both it and the verifier use local files only and do not open or modify
Ghidra. The broader observer suites separately exercise real disposable
debugger events, drift admission, competing breakpoints, STOP and recovery.

The verified focused record has 11 refusal rows and 2,978 bytes at
SHA-256 `2f777826ae5379621642846b60a5d709824f5ebfa2bb4dc00bf90383c3ff3dde`.
Controls distinguish real PID/epoch and file-identity comparisons, changed
synthetic mapped bytes, first/late enumeration failures, absent main and
critical modules, wrong backing path, an eligibility rejection, and a
modeled attach API rejection. An injected short write left a verified
64-row prefix and 125 untrusted trailing bytes. The same console fallback
used in production emitted the refusal with a durability warning.

The final binary passed all 25 creation, 22 attach and nine staged
disposable cases. The preceding concurrent qualification stopped its
attach suite at `reject-retail-profile` when the harness acquired the
child witness after the handle had signaled. The final sequential suite completed the same refusal control and the full
matrix. Success remains scoped to offline source, disk and fixture evidence.

### Proposed second attempt

Seek separate written authorization for one attempt using the exact
diagnostic build and reviewed handoff identity below. Preserve the existing
run card, operator actions, account and protection gates, four hardware
sites, and normal Quit boundary. The only operating addition is to retain
observer stderr and verify either the refusal's durable watermark or the
explicit loss notice. A failed predicate still closes admission, including
when writing fails. Publish no scientific result from an unarmed interval.
This proposal grants no live authority.

<!-- srr009-diagnostics-review:start -->
**READY FOR STAGE A RE-AUTHORIZATION.** Independent challenger
`srr009_challenger` accepted the offline diagnostic continuation after
checking the admission order, predicate and error attribution, refusal
durability and failure fallback, fixture regressions, preservation and
isolated patch replay. The Stage A historical disposition is unchanged.

The reviewed manifest SHA-256 is
`42611a1f006044b1698b99cb7083f8ee3b6fd046630af2be228f30345df1b388`.
It excludes only this new review block from the dossier digest. The independent review has SHA-256 `0ab49ca34bb99e0233c3f7a98aa56dc1cfa1d0bf9ea99a3813f62a6278800f5d`.
The revised build still requires separate written authority before
another live launch or debugger attachment.
<!-- srr009-diagnostics-review:end -->

## Second Stage A attempt — 15 November 2026

**Phase 2 blocked at pre-attach admission. Scientific outcome — `INSTRUMENTATION_INCOMPLETE`.**
The maintainer separately authorized one additional launch using the
reviewed diagnostics manifest and observer identified above. The full
observer SHA-256 was verified before starting it and again immediately
before the Steam dispatch. The first attempt's failing predicate remains
unknown.

| Boundary (UTC) | Evidence |
| --- | --- |
| 03:43:53 | The observer recorded the Steam process epoch under the ordinary non-elevated interactive account and acknowledged the durable baseline. It recorded admissible `steam.exe` backing-file drift against the SRR-008 SHA-256. |
| 03:44:23 | One dispatch of `steam://rungameid/1716740` under that account and session. Separate intent and shell-return receipts were retained. |
| 03:44:25 | The observer bound the later-born native AMD64 retail process at sequence 3. The retained Steam log segment matches the recorded 4,096-byte baseline tail and 466-byte append. One exact app/PID/full-image tracking line matches the separate line and offset recorded at title. |
| 03:45:02 | A separate read-only witness verified the bound PID, creation FILETIME, native architecture and image path, and acquired a query/synchronize handle. |
| 03:45:17 | The maintainer confirmed the title was visible and responsive. The observer recorded the epoch-bound title marker at sequence 4. Sequence 5 recorded a preflight refusal at `target_debugger_query`. |
| 03:45:45 | After the maintainer reported normal Quit from the main menu, the independent witness's retained handle signaled exit code 0 for the same epoch. The observer did not own the exit witness handle. |

The sequence-5 row records `operation:"CheckRemoteDebuggerPresent"`,
`winerror:5` (`ERROR_ACCESS_DENIED`), `preflight:0`, and
`attach_attempted:0`. The query failed, leaving debugger presence
undetermined. In the reviewed source, failure returns before the remaining
preflight checks and before the debugger attach call. The requested handle
rights in that source were `PROCESS_QUERY_LIMITED_INFORMATION |
PROCESS_VM_READ | SYNCHRONIZE`. The record establishes the failed
operation but does not resolve the underlying access-control decision.
The actual retail attach permissions and later mapped-image, runtime,
module, and thread checks remain unevaluated for this epoch. The outcome
says nothing about why the first attempt failed. [Windows debugger-query contract](https://learn.microsoft.com/windows/win32/api/debugapi/nf-debugapi-checkremotedebuggerpresent)
and [Win32 error definitions](https://learn.microsoft.com/windows/win32/debug/system-error-codes--0-499-).

The refusal journal has five consecutive records and 3,740 bytes.
Its whole-journal hash and durable watermark agree at
`5388a3492917025b3b65928ffdd5911d443685c1cb5535917bfd348abdce18ff`.
Both observer transcripts were retained. Stderr is empty. The observer
received no debug events, acknowledged no arming, and produced no scientific
STOP seal. The maintainer's later visit to the menu served normal Quit.
No scientific menu marker was issued, and there is no qualified startup,
title, or menu interval. Allocator invocation and arrival remain
unobserved within an incomplete instrument state. No debugger recovery
or forced intervention was used.

The fresh checks found all 98 Documents and 95 Steam-remote protected
originals matched their independent backups by length and SHA-256 before
and after. Both designations passed, no unclassified entries appeared,
and the 173 and 159 transient namespace records agreed. Cloud settings and
cache digest, per-game overlay setting, executable and checked configuration
agreed. The full Steam app manifest changed while its checked app ID, build,
state and install directory agreed. Both drives cleared the floor and reserve
at the measured boundaries. The scope is the recorded configuration and
save namespaces. Both game attempts and all earlier qualification snapshots
remain separate.

The historical postflight manifest identifies the primary receipts,
console logs, bounded Steam log and exit witness by SHA-256. These
records have private custody.
The approved implementation and qualification snapshot stayed frozen.
This attempt ended at refusal and normal exit. It grants no authority for
another launch, a changed process access mask, or Stage B.

<!-- srr009-stage-a-second-review:start -->
### Second-attempt independent handoff

**BLOCKED at the debugger-query predicate in pre-attach admission.**
Independent challenger `srr009_challenger` verified the exact
observer identity, epoch and Steam attribution, refusal watermark,
separately witnessed normal exit, and scoped preservation. P2-AC2 and
the scientific STOP prerequisite of P2-AC3 remain blocked. The
scientific result is `INSTRUMENTATION_INCOMPLETE`.

Reviewed substantive manifest SHA-256
`4b2e56f696e2dcb4bc949d458d6725745bc8a894a3faa7b6e25adc5645c68d8c`.
Only this marked review block is excluded from the dossier digest.
The independent review has SHA-256 `4a5adf277bf6c99227d4417479b0c969bf0274bfbb78358deaa0d3982d864dfe`.
<!-- srr009-stage-a-second-review:end -->

## Offline retail debugger access recovery — 15 November 2026

Both Stage A attempts remain **INSTRUMENTATION_INCOMPLETE**. The
second attempt proved that `CheckRemoteDebuggerPresent` failed with
`ERROR_ACCESS_DENIED` on the retained handle before any attach call.
The first attempt's failed predicate remains unknown.

### Successful and failed prior art

| Source and recorded boundary | Handle, execution context and lifecycle |
| --- | --- |
| `gooberpede/starfield-reference-handles@6a77579a184c64e0c080c8f3b7883c34bd17e24b`, `debugger/native/starfield_hardware_smoke.cpp`, `run_starfield_smoke.py`, and `docs/experiments/live-starfield-observation-capability-recovery.md` | The runner checked the game pin, refused an existing Starfield process, dispatched Steam, checked one PID/path and started the native client as an ordinary subprocess of its own execution context. The client requested `PROCESS_ALL_ACCESS`, verified the fixed executable path and called `DebugActiveProcess` directly, with no separate debugger-presence query. It set non-killing mode, attributed the native break-in, installed DR0 per thread, checked owned traps and used RF. The pinned retail startup smoke recorded two hits, 146 armed threads and normal retirement/detach with delayed health and operator-confirmed menu responsiveness. That one-site startup run used timing and retirement procedures specific to its workload. The runner did not request elevation or adjust privileges. Its retained run record does not identify the Windows token's integrity or elevation. |
| `gooberpede/starfield-outpost-research@d116bc63ff394b0156539161c8d1addfc902665a`, `debugger/exp0002a/native/adapter.cpp`, its 0.1.3 build-02 source snapshot, `docs/experiments/SOR-EXP-0002A-native-save-thread-mapping.md` and the 0.1.2/0.1.3 audits | The native adapter requested full query, VM read, synchronize and terminate rights (`0x100411`). It checked debugger presence, executable/module identity and its mapped site before attaching by PID. It disabled kill-on-exit. Its 0.1.3 S1 live control attached and retired without installing DR0. The 0.1.2 host run reached ARMED with 92 threads after the same executable's sandboxed run failed at module snapshot. The 0.1.3 S2 live run armed one existing thread and later entered recovery after target exit without a durable request capture. The raw attach/arming evidence establishes access through those boundaries. The scientific save traces and their recovery outcomes remain unsuccessful. The native adapter has no token adjustment or impersonation path. Approved host execution in the native audit establishes a runner-context difference, without a measured Windows elevation or integrity token. The separately documented elevated x64dbg attempt belongs to an older tool path and brings no authority into SRR-009. |

The local `access-recovery/prior-art.json` receipt pins the inspected
sources and audit entries. The reproduced smoke raw digest is
`fe9e2af5c8129e785a04eff4751e45ab94c59b3840dcfe1f853ed8857ba9e188`.
The outpost S1 and S2 native records match their audit digests
`2155f65faf61ed42d83dac05c5f36636dbc34a78ba061f4d5698fa2285ab5b82`
and `e204aa3deffb99ce0f81f48e81c0961638d1b0584a4a362209e3d407347299d9`.
No code or cleanup mechanism was imported.

### Revised retained handle and qualification

The single retail target handle now requests
`PROCESS_QUERY_INFORMATION | PROCESS_VM_READ | SYNCHRONIZE`
(`0x00100410`). Windows also grants limited query with full query.
This keeps the successful native adapter's query/read/wait basis and
preserves the ownership check. The Steam client handle, exact candidate
and epoch checks, interactive account and session checks, module and
mapping gates, and attach call remain in place. The retained target
handle adds no terminate or target-write rights. The observer still
uses the OS debug event and thread handles for its existing debugger
operations. [Windows process access rights](https://learn.microsoft.com/windows/win32/procthread/process-security-and-access-rights).

The observer records the requested mask at binding. An unsuccessful
`OpenProcess` captures the actual error immediately and records it as
`target_open` before binding or debugger admission. It uses the same
durable refusal watermark and stderr fallback as other admission errors.
The successful-open path still performs the debugger-presence query.
The four-site register checks, qualified windows, correlations, Steam
drift policy, STOP seal, and normal-exit and recovery boundaries are
unchanged.

The observer SHA-256 is
`dac1d88aea5b23e9725567b00426bfc3faa940a362e46521d59f15d10d64da88`.
The focused and revised-handle staged controls used the same ordinary interactive account,
with a medium-integrity, non-elevated token and no inherited AppCompat
layer. The qualification used the [existing build and harness instructions](SRR-006-four-site-hardware-observer.md#reproduce-the-fixture-controls)
and the [focused diagnostics procedure](#offline-qualification-and-reproduction)
above. The new controls read their own or disposable process state.
They write local fixture output only and do not modify Ghidra.

On the same disposable process epoch, the original requested mask
`0x00101010` returned error 5 from the debugger query, while the revised
mask queried successfully. A separately debugged disposable child using
the revised handle was rejected as already owned, with no API error.
An invalid-PID `OpenProcess` control recorded error 87 at target-open.
The staged `admission-fixture` case acquired the same access mask as the
retail path before running the existing four-site disposable observer.
The focused verifier checked 13 durable refusals, including the real
query denial and handle-open failure. The injected short write retained
its prior 64-row prefix and reported the incomplete final row via stderr.
These results isolate the old mask's symptom on this Windows host and
qualify the revised access path on disposable targets. The revised-handle
stage fixture passed four-site arming, allocator correlation, a durable STOP
and exact-process exit 0. Retail admission remains untested with this build.

The broader runs preserve two adverse results from the ordinary-account
runner. In legacy attach `busy`, the fixture's existing watchdog intervened
after the valid sequence-4209 STOP seal and before retirement. The fixture
receipt records no writer failure or lost row. In staged
`admission-competitor`, the unrelated competing breakpoint was passed
through and the genuine break-in arrived. The stopped thread census
failed with the other pre-arm checks green and arming was refused.
That test did not reopen the target with the revised access mask. Its exact
census-failure cause was unrecorded. Neither failed fixture is a retail
observation, and both records are retained alongside the successful
controls.

The ordinary-account creation suite completed 25/25. The same built binary
completed the full 22-case legacy attach and nine-case staged suites on
the sandbox disposable runner, including the competitor, STOP, drift and
recovery controls. Those passes supplement the revised-handle test on the
ordinary account and leave the two ordinary-account adverse outcomes intact.

### Proposed next Stage A authorization

If separately authorized, use the exact reviewed manifest and observer
below for one Steam launch under the maintainer's ordinary interactive
Windows account in the same Steam session, at medium integrity and
without elevation or privilege adjustment. Verify that context and the
binary hash before launch. Approve the revised target handle request
`0x00100410` and the original operator-driven four-site run card,
including protection checks, both observer transcripts, refusal
watermark, and exact-process exit verification. A denied open, debugger
query or later safety check closes this attempt; retain its evidence.
Any elevated run would require a distinct authority and reviewed design.
This proposal grants no live authority.

<!-- srr009-access-recovery-review:start -->
**READY FOR STAGE A RE-AUTHORIZATION.** Independent challenger
`srr009_challenger` accepted the offline access recovery. The challenger
verified the successful prior-art boundaries, the revised access mask
and unchanged observer operations, raw qualification evidence including
the ordinary-account adverse controls, preservation and patch replay.
Both historical attempts remain `INSTRUMENTATION_INCOMPLETE`.

Reviewed manifest SHA-256
`7b7d59ccedafa2229d3fc08dbe5f4bc6cfea6de64eb3fa3321d5512ccdd15ce7`.
Only this marked block is excluded from the dossier digest.
The independent review has SHA-256 `9aac904a2465c04e154a6545b1246e451dacbe25df8c54a0fe5688c3199a5ccf`.
Retail attachment remains untested with this candidate and requires separate
written authority.
<!-- srr009-access-recovery-review:end -->


## Third Stage A attempt — 15 November 2026

The maintainer authorized one further Steam launch using the independently
reviewed access-recovery build above. This attempt used the ordinary
non-elevated, medium-integrity Windows account in Steam's interactive
session. The launch record pins the observer binary immediately before
dispatch; the observer bound the authenticated retail 1.16.244.0 process
using the approved request of `0x00100410`. The first and second attempts
remain historical `INSTRUMENTATION_INCOMPLETE` results. The first attempt's
failed predicate remains unknown.

### Admission and acquisition

| UTC | Durable evidence |
| --- | --- |
| 04:58:43 | Steam baseline acknowledged at sequence 2 before the single launch at 04:59:33. The target epoch was bound at sequence 3. |
| 05:00:25 | The operator confirmed the responsive title card at sequence 4. Non-killing policy was confirmed at sequence 6. Stopped admission at sequence 247 passed the process, critical mapping, module census, thread census and pre-arm checks. The recorded owned attach break-in was continued at sequence 438, followed by `ATTACH_ARMED` at 439. |
| 05:01:17 | The operator confirmed the responsive main menu. The observer passed the checkpoint and acknowledged it at sequence 483. |
| 05:01:50 | Operator-authorized STOP passed its checkpoint at sequence 500. The exact STOP prefix was verified before the request to Quit. |
| 05:02:15 | Sequence 501 acknowledged the retirement request to observe the exact process through exit. The operator then selected Quit. |
| 05:02:36 | A separate retained read-only handle to the same process epoch signaled with exit code 0. |

The stopped, pre-barrier readbacks verified 95 thread generations at the four DR0–DR3
addresses documented in [SRR-005](SRR-005-live-observation-preparation.md#sites-and-causal-join).
All four later thread admissions within the observation windows had
verified register readbacks. The two windows contained 44 successful
periodic checkpoints, including 42 census checks and two held-slot checks.
The raw journal retains the owned
break-in event and the stopped-admission checks. The observer's
runtime break-in attribution also used stack inputs that are absent
from the journal.

Origin-verified Steam client and overlay DLL drift from SRR-008 was
recorded at sequences 1 and 5, including observed and historical
SHA-256 values. The overlay mapped before arming. The only module
transition in the qualified windows was incidental System32
`WindowsCodecs.dll` at sequence 455. The Steam Cloud and per-game overlay
settings were disabled, and the operator reconfirmed the NVIDIA overlay
was disabled.

### Scientific result

| Qualified window | Sequence interval | Duration | Periodic checks | New thread readbacks | Owned site hits | Focal invocations | Allocator arrivals |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Post-arming title and transition to the menu | [439, 483) | 52.253 s | 28 | 4 | 0 | 0 | 0 |
| Responsive main menu to STOP | [483, 500) | 32.029 s | 16 | 0 | 0 | 0 | 0 |

**Qualified `NOT_OBSERVED`** applies to the focal invocation and correlated
allocator arrival in both windows. The verdict is derived from the sealed
journal. The STOP prefix has 500 consecutive records, 353,147 bytes and
SHA-256 `f4cd672725622db9c3e0d8a74bc5b4c3bb1c7bd1469ddd3b89017a8b33d80967`.
Coverage begins at verified post-title arming. Startup before that
barrier, save loading and gameplay are outside this result.

### Exit, debugger retirement and preservation

The independent witness bound the exact admitted PID and creation epoch
before title confirmation and observed its normal exit with code 0. The
observer acknowledged the retirement request and continued events after the
seal. The latest verified operational prefix at the evidence boundary was
sequence 601, 415,855 bytes, SHA-256
`06e600452257113d68f5c53b69778847f3c4dce9304f8200037a44c3026a4be8`.
It ends after successful continuation of an `EXIT_THREAD_DEBUG_EVENT`.
At 05:06:36 UTC the original observer PID and epoch were still present
and no Starfield process was present. The observer journal contained no
`EXIT_PROCESS_DEBUG_EVENT`, observer-handle exit result, terminal retirement
outcome or final receipt. Debugger retirement therefore remains
**incomplete at the evidence boundary**, with cause undetermined. The
owning observer was left available and no active detach, forced termination
or repeat launch was performed.

Fresh postflight verified 98 Documents and 95 Steam remote protected
saves byte-for-byte against their independent backups. Both designations
matched, transient namespace records agreed and the unclassified count was
zero. Steam Cloud and the per-game overlay settings, relevant save-path
configuration, and monitored runtime dependencies agreed across the checks.
The Steam app manifest's full hash changed while the recorded app ID,
build, state and install directory agreed. Caller-available space after the
run was 82,916,966,400 bytes on C: and 69,249,986,560 bytes on D:. Both
measurements exceeded the 40,134,217,728-byte threshold including reserve.

The saved operator actions, original observer transcripts, exact immutable
copies of both verified prefixes, process exit witness and protection
receipts were indexed by a postflight manifest in private custody.
The historical verifier used the pinned Python interpreter with `-E -B`
and read the sealed journal and protection snapshots. The independent
review below records the replay and preservation outcomes.

<!-- srr009-stage-a-third-review:start -->
The independent challenger confirmed qualified `NOT_OBSERVED` in both
sealed windows, exact-target exit 0 and postflight preservation.
The observer retirement chain remains incomplete at the evidence boundary.
The challenger verified the retained evidence and replayed the
13-file task-only candidate.

The substantive handoff manifest SHA-256 is
`b3fc0d693e7cfcf0392718776ee6981ee67ae5e837971a2a1392142b98ec9049`.
Only this marked block is excluded from its dossier digest.
The independent review has SHA-256 `21cf2883e44f923f4abee0d1152bcd94a07c9be17b511c098c8e84919318f8df`.
<!-- srr009-stage-a-third-review:end -->


### Administrative observer closure — 15 November 2026

Read-only reconciliation at 05:24:25 UTC confirmed that the original
observer still ran and that the capture ended at sequence 601. The
maintainer then authorized termination of that exact observer only.

At 05:32:19 UTC, the closure used `TerminateProcess` on a retained
handle to observer PID 44908 after matching its creation time
(`04:58:42.6226413 UTC`) and approved executable SHA-256. The exact
Starfield process, PID 31380, was absent from active process
enumeration. Its separately retained exit evidence and a fresh
read-only query of the signaled process object both confirmed code 0.
The observer handle signaled after termination and returned exit code 1,
the requested administrative status.

**Administrative closure completed.** Normal debugger retirement
remains unconfirmed. The original capture had no journal extension,
terminal receipt, or other file change. The STOP-500 and operational
prefix-601 hashes were reverified, and the sealed scientific result
remains qualified `NOT_OBSERVED`. No game launch, debugger attachment,
detach, or further game operation took place.

The intent, exit and evidence-reconciliation receipts have private
custody. The exit receipt SHA-256 is
`4060e577f979b80e8058f1b2a0722634b2fe3124d2e3fda459c4518b81ba8319`.

<!-- srr009-publication-remediation:start -->
**COMPLETE for publication-readiness remediation.** The fresh independent
challenger accepted preservation, self-containment, private Save2 retention,
claim scope, publication rights, workflow and clean-checkout verification.
The observer and original Stage A evidence retain their prior identities.
The reproducible offline methods and custody-backed observations are
listed in the [dependency inventory](SRR-009-publication-verification.md).

Reviewed manifest SHA-256
`3b8c2163309517ae53df90ca5a3b0738faf9378881e5566826be3675d2bcbb21`.
Only this marked block is excluded from its dossier digest.
The independent review has SHA-256 `9bbc1f3a8fe2b3fd47d7204db47a1c2b930245318374367e8bc0c668aab32bb8`.
<!-- srr009-publication-remediation:end -->
