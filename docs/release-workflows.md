# Release workflow dependencies

Start in the **research checkout root** for the `tools` commands. A checkout
can live at any path. PowerShell variables in the examples stand for explicit
local input/output paths. A new private output directory can live outside
either checkout. For module invocations, `python -E -B -m …` uses the selected
interpreter, ignores inherited Python environment settings and suppresses
bytecode writes. The research Python baseline is AMD64 CPython 3.14 on
Windows. Each row below names additional dependencies. See the
[separate companion checkout and smoke results](release-smoke-tests.md).

For byte-pinned research reader sources, use the recorded reader revision
with LF source bytes (Git clone option `--config core.autocrlf=false`).
Compare the per-file reader manifest with the seal before interpreting replay
results. The companion's four frozen CSV digests cover CRLF worktree bytes.
Use its separate checkout procedure with `--config core.autocrlf=true`
before checkout. These per-clone settings leave global Git configuration
unchanged. For standard-library-only checks use `-E -S -B` to disable site
initialization and its `.pth` files as well. Tests requiring pytest or Capstone
need the declared package in their selected environment.

| Workflow | Required inputs and dependencies | Output and qualification boundary |
| --- | --- | --- |
| Generation, occurrence export and canonical regression | Public companion Git revision `a8ff1c788bca415f571f06769ab3e712fa674f75`, its Python 3.12 source package under `src`, `reproduce.py`, and its four `data/` files: `planet-resource-generation.csv`, `ires-hierarchy.csv`, `planet-atmospheric-resources.csv`, `planet-directory.csv`. Only the regression adds pytest, `tests/test_full_validation.py` and `planet-all-resources.csv`. Use the source checkout with data. | Consumer CSV, optional generation manifest or test verdict. Use [the test and setup commands](release-smoke-tests.md#clean-setup). No game, captured rows or other project supplies generation inputs. |
| Conditional native-slot oracle and comparison | Git on PATH, the same clean companion Git checkout and four production CSVs. `tools/srr016/oracle.py` checks HEAD, clean status and raw CSV hashes before importing the companion package. Its qualifier requires the explicit `SRR016_REPRODUCER` path. Tracked `ledger.py` contains the sample/control definitions. The separate comparison reads the observation and frozen ledger/oracle/receipt JSON plus an independently retained canonical receipt digest. | New ledger/oracle/freeze JSON and stdout report. The two synthetic comparison/projection test classes require only the research tree. The four pinned corpus controls require the companion. See [commands](../tools/README.md#offline-oracle-and-comparison) and [schemas](../tools/srr017/interchange.md). |
| Disk-source identity and fabricated decision gates | `tools/srr013/retail_inputs.py` imports adjacent `contract.py`. Supply the lawful pinned `Data/Starfield.esm` and separate companion checkout. In addition to the four CSVs it checks the pinned `generation.py` and `tests/test_worked_case_validation.py` blobs, inventories nearby plugin filenames and checks for loose `Space/BiomeData.csv`. `tools/srr012/check_contract.py` needs only the standard library. | Stdout digest/gate receipt or synthetic test verdict. The disk check authenticates sources only. Direct rederivation of the fields in the two control bodies has a separate hold below. |
| Current title-card extraction, source identity, replay and owned qualification | AMD64 Windows and Python, tracked `tools/srr017`, `srr016` and `srr013` modules. `extract --identity` reports its source/work manifest offline. Live mode requires a separately authorized, already running, hash-matched retail process at the title card. Replay requires a sealed journal and byte-matched reader sources. Owned qualification adds the tracked C fixture, `cmd.exe`, Visual Studio Installer's `vswhere.exe` under `ProgramFiles(x86)`, `vcvars64.bat`, MSVC x64 compiler/linker and Windows SDK. | Receipt, dataset, observation, result and manifest under the supplied output. The `.local-work` default creates **new** output. It consumes no pre-existing custody files, Steam settings or source manifest. Owned qualification starts disposable children and writes its own build and test results. [Operator and offline commands](../tools/srr017/README.md) |
| Historical population arithmetic and private preservation | `tools/srr018/compare.py` needs the research Git checkout, Git, the clean companion Git checkout above and either five hash-identified originals (`receipt.jsonl`, `dataset.json`, `observation.json`, `result.json`, `manifest.json`) or the pinned compact CSV with its adjacent `.manifest.json`. `preserve.py` needs the five originals and matching research source bytes, and checks free space on both C: and D:. `qualify.py` uses synthetic rows only. | Comparison writes JSON reports. Preservation writes a private ZIP, CSV and manifests. Use a fresh destination. Originals are needed for replay. The reported 22,470 agreements are diagnostic and strict admission is 0/3,211. [Inputs and commands](../tools/README.md#offline-oracle-and-comparison) |
| Native executable inspection and Ghidra export | PowerShell identifies the lawfully acquired CK or retail executable by version and hash. `tools/srr011/inspect_pe.py` takes the pinned retail PE and requires Capstone 5.0.7. The seven Java scripts need Ghidra (historically 12.1.2 PUBLIC), its compatible JDK, bundled Gson, program-model and decompiler APIs, and a matching analyzed program. Give the script its requested address/cursor/field and output root. | PE check prints the bounded window to stdout. Ghidra reads the analyzed program and writes external reports. Function recovery depends on the supplied analysis state. [PE identity and example](PROVENANCE.md#current-retail-identity) · [Ghidra scripts and output schemas](../ghidra/README.md) |
| Interface archive checks | The Python standard-library snippet and member-index tables in provenance, plus the caller's lawful, hash-matched `Starfield - Interface.ba2`. No Steam-root discovery, separately downloaded movies or private screenshots are needed. | Stdout member digests and bounded bytecode checks for the supplied archive. Correlation with a historical display requires separate custody evidence. [Locations](PROVENANCE.md#locations-interface-input) · [Scanner and starmap](PROVENANCE.md#scanner-and-starmap-interface-inputs) |
| Serialized PlayerKnowledge comparison | `tools.srr022.compare` uses the tracked container, section, record and identity modules with standard-library zlib. Supply two lawful SFS specimens matching the documented profile. Optionally give an explicit plugin directory for header-qualified identities. Synthetic unittest discovery supplies its own small fixtures. | JSON comparison on stdout, including side-specific unresolved keys. Specific Save2/Save52 counts require the exact originals and matching headers for the header-qualified result. [Profile and commands](../tools/srr022/README.md) |

## Historical dependencies and held routes

The outpost ESM reader used for the independent Kreet/Decaran check decoded
record bodies. The tracked SRR-017 source scanner inventories record headers.
Fresh direct ESM field rederivation is **held** pending a maintainer decision
on ownership and a tested, self-contained reader or an implementation in the
pinned companion. This limits that individual verification route. The
historical corroboration and corpus-vector checks have separate provenance.
[Field controls](allocation-validation.md#independent-base-field-controls)

The SRR-006/009/010 debugger, SRR-008 protection/configuration and module
inventory, SRR-013 selected-key and SRR-016 whole-store acquisition
controllers, SRR-015 exploratory oracle audit, and SRR-017 file-backed
source/title profiles remain historical source. Their Steam paths, C:/D:
checks, private policies, approvals, old source pins, x64 build setups and
test outputs apply to their own records. Reused SRR-013/016 modules are still
required by the current extractor. Earlier Ghidra CK/UI investigations and
outpost references in the subjects identify prior analyses. No release
workflow imports the outpost checkout. Historical acquisition, debugger and
source-profile commands and their dependencies remain in the
[tool catalog](../tools/README.md) and [environment tool notes](../tools/srr008/README.md).
