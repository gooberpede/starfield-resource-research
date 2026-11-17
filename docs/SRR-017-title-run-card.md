# Proposed SRR-017 retail title-card extraction

**NOT AUTHORIZED.** This is the prospective operational procedure for one
separately authorized title-card observation. It gives the exact retail
entry point and the independent checks required to assess that candidate.
Use it only after the release decision and a new maintainer authorization.
SRR-013 approvals and disposable signatures confer no retail authority.

## Exact invocation and one-use custody

From the reviewed checkout, set absolute local paths for the reviewed
64-bit Python executable, the Steam root, and an existing restricted
custody directory below the checkout's private work root. The two
approval files and source profile have the fixed basenames shown here.

```powershell
& $approvedPython -E -B -m tools.srr017.retail_title execution-manifest
& $approvedPython -E -B -m tools.srr017.retail_title observe-title `
    $steamRoot $custody "$custody/authorization.json" `
    "$custody/authorization.json.sig" "$custody/source-files.json"
```

The first command is offline and prints the canonical execution manifest
digest, exact runtime SHA-256, arguments, source byte hashes, executable
pin and combined work manifest. The retail command checks these values
again from the execution checkout. Preserve the source and Python bytes
on this checkout through replay. The owned equivalent uses a private
test seam and the same controller, acquisition, replay and export rules.

```powershell
& $approvedPython -E -B -m tools.srr017.qualify_retail_title $uniqueRunName
```

The real signer is a separately enrolled maintainer. On the observation
host, the existing trusted deployment must provide exactly one
`srr017-maintainer namespaces="srr017-retail-title" ssh-ed25519` public
key record in `C:\Program Files\SRR017\allowed_signers`. The deployment
owner must authenticate the enrolled public key out of band. The
ordinary observation token must lack write and replacement access to
the trust anchor and verifier. The observer never enrolls a key, changes
ACLs or elevates. The command uses the system OpenSSH verifier at
`C:\Windows\System32\OpenSSH\ssh-keygen.exe`. If the trust anchor or
unprivileged verifier requirement is unavailable, the command refuses
before game admission. Provisioning is separate from both the approved
operator run and the owned qualification.

The maintainer approves the one launch, operator, restricted custody and
bounds by signing exact UTF-8 JSON bytes in the `srr017-retail-title`
SSHSIG namespace. Use sorted JSON keys, compact separators, ASCII escapes
and one final LF. The schema has these fields.

| Fields | Bound value |
| --- | --- |
| `schema`, `scope`, `purpose` | `srr017-title-authorization-v1`, `srr017-retail-title`, `one-responsive-title-readonly-pair` |
| `approval_id` | New unique 32-character lowercase hex ID |
| `operator_sid`, `steam_session` | Approved Windows user SID and interactive session number |
| `steam_root`, `custody` | Canonical Steam and custody paths |
| `source_sha256`, `work_sha256` | Canonical SHA-256 of the command manifest and its `work` member, without final LF |
| `input_sha256` | Byte SHA-256 of canonical `source-files.json` |
| `trust_sha256`, `verifier_sha256` | Exact approved allowlist and OS SSH verifier byte SHA-256 |
| `retail_sha256` | `7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28` for Starfield.exe 1.16.244.0 |
| `pre_environment_sha256`, `pre_protection_sha256` | Exact SHA-256 of the two preflight receipt byte files |
| `issued_utc_ns`, `expires_utc_ns` | Signed Unix nanosecond interval no longer than 24 hours, checked at claim and marker admission |

The maintainer retains their signing key independently of the observer
and uses the following command on the reviewed approval JSON. Transfer
the original JSON bytes and detached signature to the agreed directory.

```powershell
& $approvedSshKeygen -Y sign -f $maintainerPrivateKey -n srr017-retail-title $approval
```

The source profile uses schema `srr017-source-files-v1` and a `files`
array of per-plugin objects with `plugin`, `path`, `bytes` and
`sha256`. The files cover the intended effective roster, including the
two principal ESMs and any applicable installed plugins. Native loaded
paths and slot namespaces supply the independent epoch check. Use only
paths and digests verified for the proposed invocation. The expected
population and the reproducer do not enter the command.

The strict approval and preflight checks precede any Steam baseline or
game process open. After verification, the tool creates and durably
flushes one exclusive `retail-authorization.used` file in the approved
custody. Keep the claim with the original custody. Its existence bars
every retry, including failed admission. Distinct signed custody and
fresh review are required for any later attempt. An expiry is an
admission boundary. The acquisition itself has finite work caps and
cooperative cancellation without a duration deadline.

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
   hashes each original and backup. Give the maintainer the two exact
   preflight receipt hashes for the approval. The observer consumes
   these receipts without opening any save files.

```powershell
& $approvedPython -E -B tools/srr008/preflight.py environment --config $config --output "$custody/pre-environment"
& $approvedPython -E -B tools/srr008/preflight.py protection --config $config --output "$custody/pre-protection"
```

3. Invoke the exact signed command. Wait for the displayed authenticated
   baseline prompt. The operator performs one normal Steam launch and
   holds the responsive title card. Type `launched` only at that
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

2. Hold the title scene through both collections and source closeout.
   Collect from each fresh published root and registry, check consumed
   witnesses and the process epoch, wait at least 25 ms, and repeat.
   Keep exact counts, all seven words and present all-zero targets.
   Native epoch-bound loaded paths and slot assignments resolve
   defining identities against the prelaunch and post-pair file
   snapshots. An override attribution remains a separate question.
3. Stop if there is cancellation, phase or identity drift, unsupported
   loaded paths, malformed data, or work/evidence exhaustion. Ctrl+C
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
addresses, source paths, process epoch tokens, logs, signed lease
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
