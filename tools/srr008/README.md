# SRR-008/009 offline protection, environment and inventory tools

These tools use the Python standard library. Use x64 Windows with C: and D:
available and x64 CPython 3.14.3 for the qualified route. At least
40,000,000,000 caller-available bytes must remain per drive after the
134,217,728-byte reserve. All commands run from the repository root. Use
an existing ignored output parent and new output names. No command in this
directory launches a game, opens Ghidra or changes game files, saves,
backup files or settings.

## Synthetic protection and environment checks

```powershell
python -E -B tools/srr008/test_preflight.py
```

The test source defines the complete synthetic configuration and policy,
constructs small temporary files, and verifies the resulting success and
failure fields. It uses no installed game, real settings, saves, backup
inventory or sibling source. The temporary test directory is deleted.

## Private configurations and read-only checks

Keep the configuration, private policy, outputs and any manually retained
evidence under an ignored, access-controlled location such as
`.local-work/codex/<investigation>/`. Keep saves and backups in place.
The checker accepts explicit effective Documents and Steam roots. Confirm
the chosen Steam account and effective save roots independently. Pin the
exact private policy bytes and retail executable SHA-256 from the relevant
research baseline.

The JSON config uses the following fields. The synthetic setup in
[`test_preflight.py`](test_preflight.py) is a complete worked example.

| Fields | Meaning |
| --- | --- |
| `schema`, `native_build` | `srr-save-environment/1` and the qualified save-name grammar build `1.16.244.0`. |
| `documents_root`, `documents_save_directory` | Absolute local Documents game directory and one child directory name. The default `Saves` applies in the absence of an explicit INI setting. |
| `steam_root`, `steam_profile` | Absolute local Steam root and its selected numeric `userdata` child. The remote namespace is app `1716740/remote/Saves` under that profile. |
| `backup_root`, `policy`, `policy_sha256` | Absolute paths to the independent flat backup and private policy file, plus its lowercase SHA-256. |
| `expected_protected_counts` | Positive expected counts keyed by `documents` and `remote`, established independently for the intended namespace. |
| `expected_game_sha256`, `expected_steam_build` | The lowercase executable SHA-256 and the Steam build ID as a string. |
| `additional_configuration` | Array of absolute paths to separately selected config files such as load-order records. May be empty. |
| `documents_data_target` | Absolute, independently verified target when the Documents `Data` directory is deliberately junctioned for the SFSE check. Use JSON `null` for a normal directory. Save, policy and backup readers reject links and reparses. |

The private policy schema is `sor-save-protection/1`. Supply
`native_build`, nonempty `designated` and a `classified` object that
may be empty. The keys are save basenames.
Each designation supplies `bytes`, `sha256` and an `evidence` string.
Each explicit classification supplies an `evidence` string and `kind`
from `MANUAL`, `AUTO`, `EXIT` and `QUICK`. Keep the original private policy
pin when reusing it. Set `$srrConfig` to a configuration you create
using the schema above and the tracked synthetic example. Create the ignored
output parent before running these commands.

```powershell
$local = '.local-work/codex/example'
python -E -B tools/srr008/preflight.py protection --config $srrConfig --output "$local/pre-protection"
python -E -B tools/srr008/preflight.py environment --config $srrConfig --output "$local/pre-environment"
```

Protection hashes each protected original and independent backup, rejects
same-file aliases, checks all explicit designations in Documents, and
records transient metadata. Unknown names, non-save files, count changes
or missing and mismatched pairs fail the check. Environment reads the
installed executable, app manifest, stored per-game overlay/cloud values,
cloud cache hash, selected INIs and SFSE paths. It records current on-disk
settings. The interactive session, launcher association, absence of
running processes and NVIDIA overlay require separate live-run gates.

Use a fresh output directory for each mode and each before/after check.
An exit of 0 requires `ok: true` in the receipt. Also inspect namespace
success, every protected pair, all designations, the unclassified and
other entries, and the relevant environment fields. Treat an exit of 0
with failed or missing receipt fields as a failed check. An evaluated
failure returns 1 and writes a report. Invalid inputs, unsafe paths,
unavailable space or an existing output return 2. Inputs and receipts
include private information and belong outside Git.

Compared with the historical SRR-008/009 checker, the promotion retains
the filename classification, size/hash comparison, distinct file identity,
and designation checks. It adds a pinned explicit config, expected counts
and nonzero failure exits. It rejects unclassified and other entries
directly. The environment method separates the on-disk checks from the
historical live process and account observations. Exact historical
interactive commands and reports remain in private custody.

## Disposable module inventory

Installed SFSE loaders and plugin files remain environment-inventory
diagnostics. Their presence does not establish use by the authenticated
Steam process and does not fail the environment receipt.

Create the ignored output parent first. The receipt path is a new output.

```powershell
python -E -B tools/srr008/inventory.py .local-work/codex/example/module-fixture.json
```

The inventory fixture starts its own disposable x64 CPython child, verifies
its identity and performs two read-only Tool Help module snapshots. It
checks the backing executable and rejects a wrong creation epoch. The
child exits cooperatively. It writes one new receipt and reads no retail
process. The original retail controller and its captures remain in
historical custody.

The policy classifier and inventory pattern provenance are given in the
[third-party notices](../../THIRD_PARTY_NOTICES.md) and
[dependency inventory](../../docs/PROVENANCE.md).
