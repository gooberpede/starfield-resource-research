# Research Provenance

Executable identities, tool versions, and data provenance apply only to the
evidence identified below. Project model version v1.0 is a separate identifier.

## Creation Kit static evidence

The [pre-biome bundle](experiments/evidence/pre-biome-resource-state/) and
[Special/Common bundle](experiments/evidence/special-common-selector/) record
`CreationKit.exe`, MD5 `0215f03ec24922dfd4015dcdc5317dc4`, image base
`0x140000000`, and focused exports from 2026-08-31 UTC using Ghidra 12.1.2 PUBLIC.
See the per-file metadata and the [selector manifest](experiments/evidence/special-common-selector/manifest.json)
for export times. The MD5 is the historical fingerprint.

On 2026-11-13 at 04:51:54 UTC, the installed Steam CK candidate (239,885,664
bytes) reported file and product versions `1.16.244.0`. Its MD5 matched the
historical fingerprint. Reading version metadata and MD5 between two matching
SHA-256 reads of the same file links those values to the measured bytes. The
candidate SHA-256, newly measured, is
`ed54e4906bc13b0fbc43ec7624fec4af2389a9a1e12b2789d73c5617f5a14020`.
The match supports attributing version `1.16.244.0` to the fingerprinted
exports. The local Steam CK app manifest (app `2722710`) reported installed
build `23516818`. That is a current installation record. The distribution
build of the historical import is unknown.

The maintainer-supplied CK About capture displays version `1.16.244.0`
with the incidental text `Data: 582`. The capture time and process identity
are unrecorded. Executable identification and version qualification rely on
the MD5 match and file metadata above. The data field is excluded from both.
See the [SRR-001 dossier](SRR-001-executable-identity.md) for custody.

## Creation Kit live evidence

The [x64dbg findings](experiments/x64dbg-runtime-generation-findings.md) use
the same CK address space. Trace-specific executable version, hash, debugger
version, and data/plugin versions are unrecorded. Version attribution requires
trace-specific executable metadata or a fingerprint tied to the trace
session. Live observations retain their evidence grades and govern when they
conflict with the earlier static interpretation.

## Current retail identity

| Field | Observed local value |
| --- | --- |
| Executable | `Starfield.exe` (102,476,200 bytes) |
| File version | `1.16.244.0` |
| Product version | `1.16.244.0` |
| SHA-256 | `7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28` |
| Distribution record | Steam app `1716740`, installed build `23518663` |
| Observed at | 2026-11-13 04:51:55 UTC |

In Steam, use Starfield's **Browse local files** location to identify the
designated installation. Two levels above that installation directory, the Steam library `steamapps` directory
contains `appmanifest_1716740.acf` (retail) and `appmanifest_2722710.acf` (CK).
Read only `appid`, `installdir`, `StateFlags`, and `buildid`. Both local
manifests reported `installdir=Starfield` and `StateFlags=4`. The manifest
identifies the installed app build. The executable hash identifies the file
bytes independently of Steam's record.

From the installation directory in PowerShell, run the following for each
filename. Repeat the SHA-256 after the metadata and, for CK only, the MD5 to
check content stability. The SRR-001 measurements used absolute file paths
under the designated install and verified both manifest hashes around the
reads. Executables were read without launching them.

```powershell
$exe = '.\Starfield.exe' # Use .\CreationKit.exe for the CK check.
Get-FileHash -LiteralPath $exe -Algorithm SHA256
(Get-Item -LiteralPath $exe).VersionInfo | Select-Object FileVersion, ProductVersion
# CK only
Get-FileHash -LiteralPath '.\CreationKit.exe' -Algorithm MD5
Get-FileHash -LiteralPath $exe -Algorithm SHA256
```

The historical retail planetary-scan executable version, build and hash are
unknown. A record tied to those scan sessions is needed to resolve them. The
current file observation provides a starting pin for future native research.

## Applicability register

| Evidence or claim | Executable/build reference | Claim type | Qualification and limit |
| --- | --- | --- | --- |
| [Pre-biome static bundle](experiments/evidence/pre-biome-resource-state/) | CK static fingerprint above | Native control flow, addresses and offsets | Applies to the focused export and excerpt scope. Historical data/plugin versions are unknown. Later live evidence governs conflicts. |
| [Special/Common static bundle](experiments/evidence/special-common-selector/) | Same CK static fingerprint | Native selector control flow, addresses and constants | Applies to the focused export. Historical data/plugin versions are unknown. |
| [CK Galaxy View Apply traces](experiments/x64dbg-runtime-generation-findings.md) and [function register](function-register.md) | CK address space, live build and hash unknown | Observed native control flow, addresses, offsets and state ordering during Apply | Scenario-specific runtime observations. Data/plugin versions are unknown. Broader object lifecycles and retail addresses require separate evidence. |
| [Historical ten-body holdout](experiments/v1-holdout-validation.md) | CK and retail builds/hashes unknown | Output semantics | CK biome assignments and retail final planet-wide scan membership, 10/10 exact. Run date and data/plugin versions unknown. Native equivalence and retail lifecycle remain open. |
| [Canonical 1,444-body validation](v1-research-baseline.md#validation-baseline) | Reproducer source-data snapshot, upstream retail capture build unknown | Output semantics | Exact on the CK/RSGD-visible planet-wide validation channel. Run date and base-game/plugin/DLC versions unknown. Atmosphere-derived final membership and native equivalence are outside the oracle's coverage. |
| Current retail identity above | Steam `1716740`, observed build `23518663` | Executable identity | Applies to the measured local file. No data/plugin identity was needed for this observation. Retail native control flow, addresses, offsets, and lifecycle remain open. |

The historical PNDT/BIOM/RSGD/IRES extraction timestamp is
`2026-08-30 11:40:41`. The xEdit version is unknown. The 2026-09-24
public-release remediation removed the older research-tree CSV snapshots from
the current tree after confirming no active script or workflow depended on them.
Maintained canonical data, model, tests, and xEdit extraction tooling live in
the [reproducer](https://github.com/gooberpede/starfield-resource-reproducer).
The historical `planet-all-resources.csv` was a `SurveyAggregator` validation
oracle/proxy, incomplete for atmosphere-derived final membership. The
historical `PlanetResourceGeneration_v5.csv` and `Starfield_IRES_Hierarchy.csv`
predated the maintained reproducer inputs. See the
[research workflow](research-workflow.md) for future captures.
