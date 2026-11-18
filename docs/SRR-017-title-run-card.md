# Proposed SRR-017 retail title-card extraction

**NOT AUTHORIZED.** This is the prospective operational procedure for one
separately authorized title-card observation. It gives the exact retail
entry point and the independent checks required to assess that candidate.
Use it only after the release decision and a new maintainer authorization.
Earlier run approvals confer no authority for a new attempt.

## Exact invocation and one-use custody

Use the reviewed checkout, qualified x64 Python executable and an existing
restricted private custody directory below the checkout's `.local-work` root.
Verify the execution/work digests printed by the offline command against
the maintainer-reviewed candidate.

```powershell
& $approvedPython -E -B -m tools.srr017.retail_title execution-manifest
& $approvedPython -E -B -m tools.srr017.retail_title observe-title `
    $steamRoot $custody "$custody/authorization.json"
```

The separate written maintainer approval authorizes one responsive title
checkpoint and one read-only pair. Record its reference in an ordinary
UTF-8 JSON file at `$custody/authorization.json`. The six fields are below.
Whitespace and key ordering may follow the operator's normal JSON editor.
Duplicate members refuse. Hashes identify exact execution sources and
work limits, using the command's canonical manifest digest.

| Field | Required value |
| --- | --- |
| `schema` | `srr017-title-authorization-v2` |
| `scope` | `srr017-retail-title` |
| `source_sha256` | Reviewed execution manifest digest |
| `work_sha256` | Canonical digest of that manifest's `work` member |
| `custody` | Canonical absolute path of this private run directory |
| `approval_reference` | Nonempty reference to the separately issued written maintainer approval |

The observer checks that record, current execution sources and preflight
receipts, authenticates its ordinary operator/session, and durably creates
one exclusive `retail-authorization.used` claim before any Steam baseline
or game process admission. An existing claim bars reuse after success or
failure. The record is the SRR-013 approval binding adapted to the complete
SRR-017 reader. The command does not infer approval from a passing test.

Use freshly generated preflight receipts for the intended run. The claim
retains their exact hashes and the native operator/session identity. A
fixed approval expiry is unnecessary for this one-use mechanism. The
immediately confirmed title marker retains its existing intake recency
check. Acquisition has finite work caps and cooperative cancellation.

Native loaded-plugin assignments and the authoritative native FormID map
resolve defining identities. Physical ESM provenance and winning-content
attribution are outside acquisition. Installed SFSE files remain an
on-disk inventory diagnostic. The operator launches normally through Steam
and the reader authenticates that exact process and mapped executable.

The owned qualification command exercises the same controller with
synthetic protection evidence and owned test processes.

```powershell
& $approvedPython -E -B -m tools.srr017.qualify_retail_title $uniqueRunName
```

## Before launch

1. Under separate scope for future preparation, check the installed
   image, intended Steam account, disabled Steam Cloud, disabled Steam
   and NVIDIA overlays, absence of an inherited `__COMPAT_LAYER` and
   ordinary medium integrity. Leave Starfield closed. Keep both C: and
   D: at 40,000,000,000 caller-available bytes after the 512 MiB combined
   reserve. The controller independently checks the reserve before claim
   and after acquisition.
2. Prepare exact current configuration and policy for the protected
   inventories. Execute the existing preflight procedures under the
   future operational authorization. Check exactly 98 Documents and 95
   Steam remote original/backup pairs, both designations and zero
   unclassified or other entries. The predecessor checker independently
   hashes each original and backup. Retain both preflight receipts in
   custody. The claim binds their exact byte hashes. The observer consumes
   these receipts without opening any save files.

```powershell
& $approvedPython -E -B tools/srr008/preflight.py environment --config $config --output "$custody/pre-environment"
& $approvedPython -E -B tools/srr008/preflight.py protection --config $config --output "$custody/pre-protection"
```

3. Invoke the reviewed command with the written approval record. Wait for
   the authenticated baseline prompt. Perform one normal Steam launch and
   hold the responsive title card. Type `launched` only at that
   checkpoint. The controller checks the unique selected process, its
   Steam parent, application log, creation FILETIME, mapped executable,
   user SID and access rights.

## Pair and independent exit

1. At the printed PID/creation/image token, start the existing independent
   exit witness in a separate shell. Use the exact printed image and
   token. The witness opens only query-limited and synchronize rights.
   Verify it retained `exit-witness-bound.json` for the printed epoch
   and image. Only then confirm the responsive held checkpoint by
   typing `title` into the waiting observer.

   ```powershell
   & $approvedPython -E -B tools/srr008/watch_exit.py $epochToken $approvedImage $custody
   ```

2. Hold the title scene through both collections and epoch closeout.
   Collect from each fresh published root and registry, check consumed
   witnesses and the process epoch, wait at least 25 ms, and repeat.
   Keep exact counts, all seven words and present all-zero targets.
   Native epoch-bound slot assignments resolve defining identities.
   Preserve observed runtime IDs, typed input metadata, all seven slots
   and canonical plugin/local IDs. Winning content stays unresolved.
3. Stop if there is cancellation, phase or identity drift, unsupported
   namespace conflicts, malformed data, or work/evidence exhaustion. Ctrl+C
   requests cooperative cancellation when the current operation returns.
   A failed attempt never triggers a replacement pair, larger limits,
   or fresh launch. Keep any sealed refusal or incomplete private prefix.
4. After the observer closes its handle, the operator Quits normally.
   Independently retain the console-printed attempt and sealed receipt
   SHA-256 values. Retain the independent report for the same PID and
   creation FILETIME, signaled state and exit code 0. Record abnormal or
   unverified exit separately. The operator performs the game UI actions.
   The approved sequence stays at the title card, with no save selection
   or travel.

## Postflight and replay

```powershell
& $approvedPython -E -B tools/srr008/preflight.py environment --config $config --output "$custody/post-environment"
& $approvedPython -E -B tools/srr008/preflight.py protection --config $config --output "$custody/post-protection"
& $approvedPython -E -B -m tools.srr017.retail_title verify-closeout $custody --attempt-sha256 $attemptSha
& $approvedPython -E -B -m tools.srr017.export "$custody/title.jsonl" `
    --retail --receipt-sha256 $receiptSha --attempt-sha256 $attemptSha
```

Verify the same original/backup byte identities, both designations and
zero unexplained differences, including transient inventories, after
normal Quit. Reconcile Steam Cloud and overlays, source, application
and protection controls as in preflight. Protection and retirement have
their own verdict independent of scientific qualification. Keep raw
addresses, source paths, process epoch tokens, logs, written approval
records and protection manifests in restricted custody. Export only
after checked replay and the separate custody review.

A qualified pair supports agreement at the two observed endpoints and
coverage of the qualifying root-reachable contents. Intermediate
mutation, atomicity, writer invocation, queued work, orphaned state
and other stores remain outside that claim. Population and value-oracle
comparison can follow offline.

[Prior paired title result](SRR-013-retail-title-paired-structural-observation.md) ·
[Protection configuration](../tools/srr008/README.md) ·
[Research workflow](research-workflow.md)
