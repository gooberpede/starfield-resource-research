# SRR-017 operator title-card extraction

Implementation and offline qualification do not authorize live access. After
accepting and committing the candidate, the maintainer launches Starfield
normally, holds at the responsive title card before menu/save navigation,
and explicitly tells Codex to extract in the current conversation.

## Run once against the already running process

From the reviewed repository checkout, run:

```powershell
python -E -B -m tools.srr017.extract --output .local-work/srr017-title-extraction
```

The command prints the selected process name, PID and executable path. It
selects the unique compatible `Starfield.exe`. If several compatible
processes exist, specify the operator's intended PID:

```powershell
python -E -B -m tools.srr017.extract --output .local-work/srr017-title-extraction --pid 12345
```

The output directory is an ordinary supplied or automatically created
location. Omitting `--output` creates a unique directory below `.local-work`.
Existing unrelated files are allowed; output filenames are not overwritten.
Keep address-bearing raw evidence private. No approval file, one-use claim,
Steam registry, save inventory, environment attestation or exit witness is
required. The command never launches or closes Starfield.

The compatible layout is Starfield 1.16.244.0, executable SHA-256
`7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28`.
The selected image/layout and process epoch must remain valid. Native
FormIDs, loaded-plugin namespace, types, rooted coverage and both fresh
collections must agree. Every qualified row includes all seven resource
slots and explicit zeroes. Physical ESM provenance and oracle comparison
are not acquisition gates.

Hold the title card until the command reports a terminal result. Ctrl+C
requests cooperative cancellation and retains diagnostic evidence where
possible. Work has finite read/tree/memory/output limits and no elapsed
acquisition deadline. Failure does not cause an automatic retry, relaunch
or budget increase. An operator may explicitly request a later attempt.

The operator v2 reader has no separate descriptor/population ceiling. It
retains native count reconciliation, structure and identity checks, with
finite limits of 4,000,000 pair operations, 512 MiB requested memory,
1 GiB journal and 512 MiB per portable output. Tree depth 64 protects the
reader stack; long cached FormID chains remain bounded. See the dossier
for the combined limit audit and large-population qualification. These
are resource limits, not a prediction of the retail population.

## Read the result and Quit

- **FINISHED**: the whole admitted rooted store and normalized export are
  qualified, and checked replay passed.
- **INCOMPLETE**: retained evidence did not qualify a complete export;
  inspect the specific failure and partial collections.
- **FAILED**: selection, access, output or another technical failure
  prevented completion. A partial journal may remain diagnostically useful.

Tell the operator the terminal result, selected PID and output directory.
They may then Quit normally. Do not claim atomicity, completed allocator
execution, all-galaxy coverage or oracle agreement.

`receipt.jsonl` holds the sealed raw reads; `dataset.json` holds the
normalized seven-slot dataset; a qualified `observation.json` projects it
for later comparison. `result.json` states status/failure and work usage;
`manifest.json` records source/work identities and output hashes. An
unfinished `.partial` journal cannot be qualified or replayed as complete.
Preserve the whole output directory. Normal filesystem errors are reported
without additional setup gates.

## Offline identity, replay and qualification

These operations do not open a game process:

```powershell
python -E -B -m tools.srr017.extract --identity
python -E -B -m tools.srr017.extract --replay .local-work/srr017-title-extraction/receipt.jsonl
python -E -B -m tools.srr017.qualify_extract .local-work/srr017-owned-qualification
```

The qualification controller starts and retires only its own disposable
fixtures; the extraction command itself never starts or retires a target.
The [existing dossier](SRR-017-identity-correction.md) records reviewed
source/work identities, tests and independent review conclusions. Its
historical refused Steam-admission attempt remains a no-observation result;
the earlier admission procedure is superseded for new extraction.
