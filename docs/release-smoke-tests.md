# Release portability checks

On 20 November 2026 a fresh Windows export passed the canonical generation, consumer export, synthetic comparison, save decoder, executable and interface-archive checks below. A subsequent fetch of the exact public companion commit passed the full qualifier and oracle freeze. The earlier ZIP-only run exercises the missing-Git-metadata refusal.

## Clean setup

On a network-enabled host with Git, choose a new directory `$model` outside the research checkout. Set the per-checkout line-ending policy before populating the worktree. The historical oracle gates the **raw CRLF bytes** of four CSVs. The standalone disk check also verifies their normalized Git blob identities.

```powershell
$pin = 'a8ff1c788bca415f571f06769ab3e712fa674f75'
git init --quiet $model
if ($LASTEXITCODE) { throw 'Disposable checkout initialization failed' }
git -C $model config core.autocrlf true
if ($LASTEXITCODE) { throw 'Line-ending configuration failed' }
git -C $model -c credential.helper= fetch --no-tags --depth=1 https://github.com/gooberpede/starfield-resource-reproducer.git $pin
if ($LASTEXITCODE) { throw 'Pinned companion fetch failed' }
git -C $model checkout --detach $pin
if ($LASTEXITCODE) { throw 'Pinned checkout failed' }
if ((git -C $model rev-parse HEAD) -cne $pin) { throw 'Wrong model revision' }
if (git -C $model status --porcelain --untracked-files=all) { throw 'Dirty model checkout' }
$env:SRR016_REPRODUCER = (Resolve-Path $model).Path
```

For generation, use a dedicated Python 3.12+ environment. The model is pure Python and the data directory must remain beside its source. For the four canonical tests supply pytest 8.x in the environment. The example uses the selected environment's `python`, adds only the absolute pinned source path for the duration of the commands, then restores the caller's settings. Supply an absolute, fresh `$product` CSV path outside either checkout. Keep the current directory outside unrelated projects. Use a separate AMD64 Python 3.14 environment in the research root for the research commands in the [workflow inventory](release-workflows.md).

```powershell
$oldPath = $env:PYTHONPATH
$oldPlugins = $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD
try {
    $env:PYTHONPATH = (Resolve-Path (Join-Path $model src)).Path
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
    python -B -s -S (Join-Path $model reproduce.py) --output $product --manifest
    if ($LASTEXITCODE) { throw 'Production export failed' }
    python -B -s -m pytest -p no:cacheprovider -q (Join-Path $model tests/test_full_validation.py)
    if ($LASTEXITCODE) { throw 'Canonical validation failed' }
} finally {
    $env:PYTHONPATH = $oldPath
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = $oldPlugins
}
```

For final Git-backed verification, run from the clean research checkout with the above `SRR016_REPRODUCER` value and a new `$freeze` directory outside both trees.

```powershell
python -E -S -B -m tools.srr016.qualify_oracle -q
if ($LASTEXITCODE) { throw 'Full qualifier failed' }
python -E -S -B -m tools.srr016.oracle $env:SRR016_REPRODUCER $freeze
if ($LASTEXITCODE) { throw 'Oracle freeze failed' }
```

## Executed checks

Windows 10.0.19045 AMD64, PowerShell 7.6.9, Git 2.53.0.windows.1 and CPython 3.14.3. The PE decoder loaded Capstone module 5.0.7 (installed distribution metadata 5.0.9). The canonical test used pytest 8.4.2 with third-party plugin autoload disabled. Research started from `git archive --format=zip --output=research.zip d37d56e4b843e14e98ca6a87d04eaabfc67f562c`, with `core.autocrlf=true`, 190 files, SHA-256 `4713e80d768d2e13bf8b94794f1c474b0fe80d9ed82ff8a0ada76fb4ed8c805d`. The qualifier change was then applied to this export and checked separately.

For the initial offline run the companion input was the prior SRR-025 Git export, unpacked independently into a new temporary directory. Its archive comment named the full pin above, its CRCs passed, and its 84 files came from ZIP SHA-256 `3e7b66483a954a40ec7d725ce6aa9e084b02038276df82468c2baa65d1887a2c`. All four raw production CSV digests matched the pins in [oracle.py](../tools/srr016/oracle.py). The validation-only CSV SHA-256 was `eecde53f2258f918e37650a4ba583720583ffb6153b2132db8e2fd29d3e76a97`. The twelve LF-normalized `src/` files reproduced the earlier freeze's source digest `adc6bdead0c4647aca92ac36ea3ac9e8078fbe0341a529818ddff67fc51acd99` (SHA-256 of sorted compact JSON mapping each relative path to file SHA-256). The ZIP lacks commit objects. These checks verified the offline inputs against earlier pins.

The exports contained no private inputs or adjacent sibling checkout. Each interpreter used a fresh `venv --without-pip` outside both exports with `-E -s -B`. Local environment path files exposed already installed libraries, bypassing the workstation's global editable-package path. Only the model interpreter exposed the unpacked `src` directory. Import probes showed that the research interpreter could not resolve the model and that the model interpreter resolved it inside the independent export. Module invocations ran at the research export root. Standalone scripts, model tests and model export ran from a separate caller directory with absolute paths. All 84 companion files compared equal before and after.

| Command or input | Exit | Result |
| --- | ---: | --- |
| `-m pytest -p no:cacheprovider -q <model>/tests/test_full_validation.py` | 0 | Four tests passed, including two identical 1,444/1,444 planet-wide generations with zero mismatches or errors. |
| `<model>/reproduce.py --output <out>/resources.csv --manifest` | 0 | 7,780 rows, including 7,445 biome and 335 atmosphere occurrences. CSV SHA-256 `e6a0b278cec2fe9113e309e19cbaf5a022f494131b7668fc8fec5e3458ca332b`. Manifest SHA-256 `8eb50ca6694fc62af21fc4ba3d39ce42b8c8eda4e7bd969235b028bd5a44bb27`. Both include the export timestamp. |
| `tools/srr012/check_contract.py` and `-m tools.srr018.qualify -q` | 0 each | Four decision-gate and ten synthetic comparator tests passed. |
| `-m unittest -q tools.srr016.qualify_oracle.ComparisonFixtures tools.srr016.qualify_oracle.AuthorAndProjectionFixtures` | 0 | 26 comparison and projection tests passed before and after the qualifier patch. |
| `-m tools.srr017.extract --identity` and `-m unittest tools.srr017.test_source tools.srr017.test_native_identity -q` | 0 each | Printed the source/work identity without opening a process. Work SHA-256 `490060e6deafda06b4383a3de300c68fa1adaf71691830ba3a5cfb4d0aa20b60`. Twenty source/identity tests passed. |
| `-m unittest discover -s tools/srr022 -q` | 0 | All fourteen synthetic save-comparison/decoder tests passed. |
| `tools/srr013/retail_inputs.py <Data/Starfield.esm> <model>` | 0 | All six pinned Git blob identities matched. Returned `runtime_effective_inputs_unverified` for the 1,457,098,709-byte master, SHA-256 `1dabed00c3f4282dd3bb54d2e9601e40b577d8742d078b7ccef203adbfef0da7`. |
| `tools/srr011/inspect_pe.py <Starfield.exe> window 14077200D 30` | 0 | Passed the executable SHA gate, decoded the call at 0x14077200D to 0x14076E810. Stdout SHA-256 `c938c5d48a6c9bb646402b2958c903fdaf11f1b98461cda1f89a9a09d705b10f`. |
| [Locations and orbital index checks](PROVENANCE.md#locations-interface-input) with the installed interface BA2 | 0 each | Passed archive identity and counter-loop assertions for both layouts in both checks. All eight member digests matched the tables. |
| Candidate `-m tools.srr016.qualify_oracle -q`, first with the path unset, then with the non-Git ZIP export supplied | 1 each, expected | Unset path reported the required environment variable. Export refused at Git HEAD verification. These failure cases and the 26 passing tests exercised the patched qualifier. |

The PE, BA2 and ESM SHA-256 measurements agreed before and after. PE and BA2 identities are in [provenance](PROVENANCE.md). The private run receipt records the exact paths, arguments, input digests, exits and both output stream hashes (receipt SHA-256 `7c4d69f0b8f6d98193a7f3eb8452a8ba83e40d3f84adbbb9f7da48aa21791175`). The candidate qualifier receipt is `3b1ba681ac17dbecf128896f1b14ba882578ef509ca7668244024302e1919c26`.

## Independent public fetch and oracle freeze

With maintainer authorization, Git fetched only the named commit at depth one from the public repository over HTTPS into a new disposable repository. Credential helpers and terminal prompts were disabled for the fetch. The detached HEAD matched the pin and its tree was `543c7fd546388ee972bb9d9ab77e5500a1765977`. Git reported a clean checkout before and after testing.

From the isolated research export with the candidate qualifier, both Git-backed commands above exited 0. All **28 qualifier tests** passed. The freeze produced 3,191 joinable ledger rows, 19 unresolved candidate identities and **four conditional oracle rows**. The canonical JSON digest of the oracle was `bfd0c22c531d7c461fd005838d3c23787aae5edb39de8745b16f243c47b6db0c`. The written `freeze.json` had SHA-256 `83e6cd04ae8e548f6a2a7438c918bc576b4eaa17eb5aaca4583754fd5b47825d`. These model controls leave the historical strict native-oracle admission at 0/3,211.

An import probe resolved the package inside the fetched checkout. All four canonical tests passed again, and the production export again produced 7,445 biome and 335 atmosphere rows. The public-fetch run receipt records commands, inputs, output hashes and exits, SHA-256 `039daf29562ec5c0ecc736783037b86bd3a3e3c2446cceef1675199dc98ae405`.

Private capture replay, historical arithmetic, saves, screenshots, live acquisition, owned native fixture compilation and Ghidra reanalysis were outside this run. The existing [SRR-025 results](audits/research-closure-and-readiness.md#reproduction-and-custody) retain their original evidence conditions.
