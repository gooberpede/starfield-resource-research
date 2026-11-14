# SRR-006 — Four-site hardware observer

**Retail allocator execution — NOT TESTED.**

The disposable controller demonstrates four simultaneous execution
breakpoints and the SRR-005 causal join on its synthetic executable.
The compiled retail profile is wired into the creation-event arming gate.
The entry point launches its own disposable executable only. The
review block governs whether to request Stage A.
[SRR-005 preparation](SRR-005-live-observation-preparation.md),
[SRR-003 dispatch evidence](SRR-003-retail-allocator-invocation-and-dispatch.md).

## Inputs and custody

- Both installed and analysis copies were measured at 102,476,200 bytes,
  file and product version `1.16.244.0`, SHA-256
  `7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28`.
  Steam app 1716740 reports build `23518663`. The build number identifies
  the Steam installation record. The binary hash identifies the PE.
- Ghidra 12.1.2 PUBLIC came from the retained SRR-002 import receipt,
  reporting preferred image base `0x140000000`, `x86:LE:64:default` and
  compiler ID `windows`. The offline check used Python 3.14.3 and Capstone
  5.0.7. It rechecked the indirect slot, four upstream direct edges, the
  separate per-biome edge, stack relationships, PE extent `0x89C2000` and
  two DIR64 entries. No Ghidra database or original save was opened.
  [Provenance](PROVENANCE.md#current-retail-identity).
- The fixtures used Windows NT `10.0.19045.0`, system ntdll file version
  `10.0.19041.4842`, x64 MSVC `19.51.36256.0` and SDK `10.0.26100.0`.
  The observer requires the qualified system ntdll image hash and checks
  its mapping and breakpoint window.
- Reference handles `6a77579a184c64e0c080c8f3b7883c34bd17e24b` supplied
  the DR6/RF ownership pattern and the restored-code detach counterexample.
  Outpost research `d116bc63ff394b0156539161c8d1addfc902665a` supplied
  event-owned handle lifetime, generation checks, and separation of STOP
  and durable acknowledgement. Its later-thread exclusion and prior
  live recovery faults motivated creation-time arming and exact-handle
  exit. Beacon startup records motivate an independent launcher/module
  gate. The implementation uses original source. Sibling evidence
  paths and hashes are in the local input receipt.
- Starting HEAD `fb1693dd83094c72d5c1300f567674aa0fc385e0`, tree
  `e59f2557dabf1653529c8aab278f69fa371eb4c1`, index SHA-256
  `aeca62fcf026172172bb43a42d334932e498c3b5eeebba29699fa15ff4775cb2`.
  Cached and tracked diffs were empty. The supplied SRR-006 brief was
  untracked at entry and stays outside the patch. The pre/post receipts
  record index bytes, HEAD and exact status. The task used no retail
  process, save, SFSE deployment or installed setting changes.

## Controller and evidence

The executable launches only its own disposable child with
`DEBUG_ONLY_THIS_PROCESS`. It matches the creation-event process handle
and birth against the separately retained launch handle, compares image file
IDs, mapped PE headers, code bytes and relocated callback slot, then reads,
arms and verifies DR0–DR3 before continuing the initial thread. Subsequent
thread creation events use the same checks and a fresh generation. Event-owned
handles are left to Windows on exit. The debugger retains its separate handle
through process exit and compares the signaled handle's exit code with the
continued exit event. [Win32 debug events](https://learn.microsoft.com/en-us/windows/win32/api/debugapi/nf-debugapi-waitfordebugevent).

An immutable profile role selects both the retail site layout and the
compiled manifest at the creation gate. The manifest contains derived
locators and SHA-256s, with profile SHA-256
`b7e7d773e0b9181ee88f48c0a65bff8ac60497e68e85851826c5b8acdf4b853f`.
The same stopped-process adapter used by the disposable pump checks both
process handles against the retained PID and creation time, matches the
creation-event backing handle against the nominated read-only handle,
hashes the event file, and checks file identity and stamps across hashing.
Hashing the 102 MB retail backing handle is a one-time synchronous
pre-arm prerequisite while the initial event is held. The recurring
event path sends journal writes to a separate worker.
The adapter then checks the mapped PE headers, executable code windows,
unwind data windows and the two DIR64 pointers. Reads require the same
`MEM_IMAGE` allocation and appropriate page rights. The mapped header
may contain the observed rebased value in OptionalHeader.ImageBase. The
verifier validates that field and normalizes it to its preferred value
before hashing the header. All remaining bytes in the checked ranges
must agree. An unrelocated slot at a rebased address refuses arming.
A positive retail mapping check is synthetic and a native disposable
creation exercises the adapter with its own known image. The same
event pump rejects the disposable child when given the retail role,
before any DR write.

Hardware exceptions require first chance, known thread, exact slot enables
and addresses, matching RIP and exception address, the sole corresponding
DR6 cause and clear TF. The observer clears its cause, sets RF and verifies
readback before continuation. Windows may normalize EFLAGS reserved bit 1.
Context checks still require the requested RF and preserved RIP/RSP. A
separately authenticated initial loader breakpoint has its own disposition.
Other exceptions pass through. Slot state, brief additional suspends during
thread census, debug-event stops and RF all affect the process or scheduling.

| Retail RVA | Checked relationship |
| --- | --- |
| `0x9518FD` | Record RSI and the qword at base + `0x61E2288` at the comparison. |
| `0x5932EF` | RCX = R14, RAX and [RCX] = base + `0x4B3D9E8`, [RAX+0x10] = callback, nonnull RDX, and [RSP+0x38] = early `0x94E57C` or later `0x94EF5C` relative return. |
| `0x77C470` | Callback RSP = iterator RSP−8, exact return `0x5932F2`, same receiver, form, vptr and slot, and same sweep return at RSP+0x40. Form+0x2E is optional for invocation. |
| `0x779760` | With entry RSP S, check returns at [S], [S+0x80], [S+0xB0], [S+0xF0], saved R14 at [S+0x50], RCX = S+0x98 and RDX = S+0x90, saved form and type 0xBA. Consume the same-generation callback token once. |

Return values in the table are RVAs unless stated as register or stack
expressions. Read errors carry a width, address and Win32 error. Flag and
module samples away from the guard are event-time snapshots. A form
pointer is session scoped. The observer never derives a FormID from it.
Missing required reads and ambiguous joins close eligibility. Earlier
durable positives survive a later gap. The synthetic fixture uses the same
code for correlation with a separate layout.

The single-producer journal hands records to a writer with a ring of 8,192
rows and at most 4,096 field bytes per row. The record payload ceiling is
approximately 33.8 MB before allocation overhead. The busy control
records the observed queue high-water mark. The writer checks both
drives before each batch of up to 128 rows and confirms the contiguous
prefix with `FlushFileBuffers`. Overflow disables further acceptance.
The final receipt distinguishes accepted, flushed and uncommitted ranges
and authenticates the closed journal, including any partial tail. Phase
and STOP acknowledgements require the marker's sequence to be flushed,
with a separate acknowledgement for each named phase. After each journal
flush the writer publishes `durable-prefix.json` via a flushed temporary
file and replacement. It records the prefix sequence, byte count and
SHA-256 of that prefix. A retained watermark can establish that prefix
after a tested process interruption. Output after the watermark, a
missing watermark, and I/O or power failures beyond the observed test
contract leave durability uncertain.

Each receipt window names its verified boundaries and separates journal
completeness, invocation coverage and allocator coverage, including the
last sequence needed to resolve cross-window joins. A verified callback
or allocator result belongs to its site's arrival window and identifies
its precursor windows and sequences. The arrival window orders debug-event
delivery against marker consumption. An event queued by the OS before a
marker can arrive after it. The receipt does not timestamp instruction
execution or the actual UI frame. A missing callback or unresolved
typed allocator can carry uncertainty across boundaries. A missing form
type preserves invocation evidence and reduces allocator completeness.
A later gap does not erase an earlier independent positive. STOP leaves
the event pump active and ends scientific eligibility.

## Disposable qualification

The tracked [controller](../tools/srr006/observer.cpp),
[fixture](../tools/srr006/fixture.asm) and
[qualification harness](../tools/srr006/qualify.py) reproduce these controls
on the pinned Windows environment.

Run12 passed all 17 original fixture assertions plus the compiled correlation unit
and offline mapping controls. Fixture executable SHA-256
`f9e69d1cc42512909df5302e12f875793bd318f5f21f31a7f7acb26b104e7bee`.
The busy run continued 4,179 events and flushed 4,204 records with
high-water 3,038. The burst STOP continued another 3,850 hardware
events from at least nine generations. The overflow run flushed 32 of
32 accepted rows out of 4,204 attempts. The interrupted write confirmed
6 durable rows out of 303 accepted, with an incomplete row in the tail.
No fixture watchdog fired. Exact receipts and earlier failures are under
`.local-work/codex/SRR-006/`.

Run18 reran all 17 original controls and passed seven additional
scenarios on fixture SHA-256
`67f686f07672051e5aef9b1abe95413b66063f7e2a59457772d22b369747e797`.
The correlation, window and stopped-profile C++ controls passed in the
same build. The stopped-profile fixture mapped at `0x7FF62E250000`
with preferred base `0x140000000`. The busy run reconciled 4,179
events and flushed 4,204 rows, with queue high-water 3,808. The burst
case continued 3,850 hits after STOP. Wait and continue failure each
produced independent exact-child exit code `0x6006`. The denied
request followed by quit exited zero. The combined failure and abrupt
observer termination each produced exact-child exit `0xC0000354` in
the supervisor. The abrupt run retained 20 durable rows and 252
unverified tail bytes. Run16's first integrated fixture arming refused
an incomplete header profile. The repair pins the complete disk header
and tests the OS-mapped header normalization in Run18.

Run21 passed all 25 scenarios and the three compiled controls on
fixture SHA-256
`0702e0c1e75a7046891726ea3e6bccb792aefb9b07834b8eeb955fcd939b6549`.
The busy run flushed all 4,204 records again and reached a queue
high-water mark of 3,806. The unexpected-module fixture continued
all 19 events, recorded both module boundaries, flushed 28 rows and
exited normally with incomplete scientific coverage. The abrupt
run again recovered 20 durable rows and rejected all 252 tail bytes.
Round 3 preserved a native counterexample from the prior snapshot.
Run19 also preserved the first fail-closed result for an expected
system DLL loaded after STOP.

| Control | Evidence and result |
| --- | --- |
| Baseline and busy | Early TLS hit on initial thread, worker creation before fixture code, four slots on each thread, 10 guard hits including one after STOP, 16 callbacks and eight allocator entries. Busy adds 4,096 rejected generic iterator hits. A handled unrelated exception reaches the fixture handler. |
| Quiet and delayed | Covered quiet fixture with zero hits. Delayed case waits for separate phase and STOP inputs. No inactivity threshold exists in the event pump. |
| Callback-only and unreadable type | Durable `OBSERVED_INVOKED` with no allocator arrival. A native read failure on form+0x2E preserved the invocation and the resulting exception closed coverage. |
| Correlation negatives | Synthetic actual-code tests cover duplicate arrival/callback, lost callback, a competing wrong-return callback, cross-thread join, thread generation reset, missing sweep return and explicit gap. Numeric TID reuse was modeled. The integrated cross-window fixture splits iterator, callback and allocator across three named windows. |
| Initial conflict and arming readback | Injected conflict and mismatched readback take the exact-child recovery branch. Faults are injected at the decision boundary. They do not represent a real competing debugger. |
| Queue and storage | Slow writer and 32-row ring cause explicit overflow. Interrupted row write retains a flushed prefix and a partial tail. Both fixtures exit zero after continuing owned events. |
| Exception and pump faults | Foreign single-step passes through and invalidates coverage. A synthetic transient continuation failure recovers the held creation event. Persistent wait failure and a continuation failure whose fallback also fails leave debugger retirement unconfirmed. A separately retained process handle confirms the exact child's exit in both tests. |
| Failed emergency request | A restricted exact-child handle produces real access denial. With a healthy pump, the child remains alive until a cooperative quit. Combined with a persistent wait fault, the debugger cannot verify exit. The independent supervisor confirms the child exited after the debugger ended under the fixture's kill-on-exit policy. |
| Abrupt observer termination | A fixture-only supervisor retains the exact child handle, waits for a durable phase acknowledgement and an intentionally incomplete journal row, and terminates the disposable observer. The supervisor confirms child exit. The final receipt is absent, and retained evidence ends at the separately hashed prefix. |
| Pinned profile | Pinned disk inputs regenerate the same manifest. Native disposable creation qualifies event-handle identity and readback at an observed ASLR base. Synthetic retail controls check both bases, header normalization, wrong image, moved window bytes, unreadable code and an unrelocated callback slot. The pump refuses the retail profile on a non-retail child before arming. |
| Unexpected native module | The fixture loads and unloads genuine System32 `version.dll` outside its declared test profile. The active window closes to further science and the child still quits normally. Loads and unloads record base and module name. An approved retail profile would require its own expected module set. |
| STOP and exit | STOP closes scientific eligibility. Normal exit and exact-child emergency exercise continued EXIT_PROCESS and a wait on the retained handle. The burst scenario places STOP during competing worker hit traffic. |
| Startup ownership | The probe rejects an attach request and Steam URI before opening a target. A disposable direct child hands off to an instrumentally unobserved successor. The fixture marks that successor explicitly, so this does not qualify generic retail handoff discovery. |

The initial runs failed with a propagated hardware exception. Startup
reconnaissance located the actual internal `ntdll+0xD0860` breakpoint
for the pinned OS image and identified EFLAGS normalization. Run03
established the corrected loader and RF paths. The first independent
challenge then reproduced a quiet false negative and iterator token
displacement. The controller now audits slots and inventory at phase and
STOP and rejects displacement. Native clear experiments immediately after a
loader stop showed point-in-time loss and later slot readback intact.
Persistent slot loss is injected at the checkpoint decision boundary.
Point-in-time audits cannot exclude an undetected clear-and-restore between
checks. Fault stimuli for persistent Win32 event-pump failures are at the
API decision boundary. They do not induce an OS fault. The dedicated
emergency-denied case exercises the real failing API using limited rights.
Fixture kill-on-exit and supervisor results establish exact-child exit for
these controls. A stopped observer cannot keep pumping events or guarantee
cooperative target survival. That is a separate Stage A recovery decision.

## Reproduce the fixture controls

From the repository root, check caller-available C: and D: with
`[IO.DriveInfo]::new('C').AvailableFreeSpace` and the D: equivalent.
Reserve 134,217,728 bytes per drive and require at least 40,000,000,000
bytes after that reservation. Create an ignored local build directory
under `.local-work/codex/SRR-006/`. From an x64 MSVC prompt, with that
directory as cwd and `SRR006_SOURCE` set to the absolute source path:

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

The harness copies the just-built binary into a fresh fixture run directory.
It writes journals, receipts and marker files only under that directory.
Its finite fixture watchdog requests exact-child recovery after 35 seconds
without scenario completion and reports unconfirmed recovery at 55 seconds.
The controller's 25 ms event wait only polls for control input. The
`stop-burst` event count is an explicit fixture stimulus. Durable marker
and exit receipts determine whether the controls worked. After the
fixture exits, retain or remove only the named disposable build/run
directory as desired. The code does not modify Ghidra. For an offline PE
check, run `python -B pin_pe.py <lawful-analysis-copy> --self-test` and
write the resulting hashes to local evidence if needed.

## Proposed Stage A no-save run card

1. Complete integration and independent offline qualification. Obtain
   separate authorization for direct launch of the pinned retail path,
   its exact creation-event debugger connection and four register stops.
   Pin observer/configuration, OS/ntdll, executable and expected module
   set. Verify the observed loaded base, independent backing-file
   identity and mapped windows before arming. Abort coverage on identity
   mismatch or unobserved process handoff.
2. Before launch establish the isolated save namespace and independently
   hash and verify originals and backups. Verify Steam Cloud disabled,
   Steam and NVIDIA overlays off and SFSE absent. Use a local ignored
   evidence destination and the two-drive floor. Keep Save2 outside the
   Stage A namespace. The Steam URI is a game launcher with unqualified
   debug creation ownership. A post-title attach requires a separate
   method approval and begins coverage only after its stopped census
   and verified arming. Such attach cannot decide startup silence.
3. Follow **startup → responsive title card → user presses a key →
   responsive main menu → STOP/flush → user chooses Quit to Desktop →
   qualified process exit**. The user confirms each named transition and
   performs GUI actions. Screenshots are optional and independent of the
   Steam overlay. Operator markers bound an interval. Exact engine UI
   transition frames are outside their resolution.
4. Track scientific progress, instrumentation health and exact-process
   health separately. Elapsed time and inactivity do not trigger STOP,
   failure or termination. On evidenced unsafe instrumentation, close
   acquisition and preserve durable evidence. Continue qualified debugger
   service through orderly exit. Name the later-approved exact-handle
   emergency trigger, recovery authority, controller exit policy and
   evidence handling in the approval. Retail termination and detach
   remain separate authority.
5. After the same handle signals, recheck evidence, originals, backups,
   install and configuration. Preserve the isolated namespace and keep
   Cloud disabled pending verified postflight and user decision. Loading
   Save2 and crossing into the Lodge require separate Stage B approval.

### Retail boundaries

Any start without an exact matching creation event has no startup
coverage. The disposable handoff marker verifies refusal of an explicitly
identified successor. The observer cannot identify an arbitrary successor
started indirectly by Steam from the original child's debug events.
Any eventual Stage A title/menu acknowledgement therefore needs to be
bound to the verified process, and ambiguity closes coverage. A creation
stop whose relocated pointers are not ready cannot be treated as verified
pre-TLS startup. A revised startup strategy would require separate review.
The direct retail launcher and a post-title attach remain separate
approval boundaries. Actual retail startup, liveness, coverage and
allocator execution remain untested.

<!-- review-status:start -->
## Review status

**Engineering disposition — READY FOR LIVE APPROVAL. Independent review —
COMPLETE for offline qualification.** Rounds 1–3 preserved the quiet-window,
frame-displacement and unexpected-module counterexamples. Round 4 accepted
AC1–AC7 on substantive manifest SHA-256
`4af4b36f3989c22f2c1d077837bcda5aa1fffde240b6e8ae966bc9e9e9e779c3`.
The independent rebuild passed all 25 fixtures and three compiled controls,
and the challenger verified the protected inputs and task-only byte replay.
Detailed rounds remain under `.local-work/independent-review/SRR-006/`.
This disposition supports requesting the separately approved no-save
Stage A run card with a pinned launch and module profile, operator-bound
checkpoints, and explicit emergency and debugger-exit authority. Retail
startup, liveness, coverage and allocator execution remain untested.
<!-- review-status:end -->
