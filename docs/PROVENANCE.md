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
current pin also qualifies [SRR-002](SRR-002-retail-static-reconnaissance.md).
The existing Ghidra 12.1.2 PUBLIC program recorded the same import SHA-256,
base `0x140000000`, language `x86:LE:64:default` and compiler ID `windows`.
An independent PE decode corroborated the instruction locations and critical
operands in the focal listing. The historical scan builds remain unknown.

## Applicability register

| Evidence or claim | Executable/build reference | Claim type | Qualification and limit |
| --- | --- | --- | --- |
| [Pre-biome static bundle](experiments/evidence/pre-biome-resource-state/) | CK static fingerprint above | Native control flow, addresses and offsets | Applies to the focused export and excerpt scope. Historical data/plugin versions are unknown. Later live evidence governs conflicts. |
| [Special/Common static bundle](experiments/evidence/special-common-selector/) | Same CK static fingerprint | Native selector control flow, addresses and constants | Applies to the focused export. Historical data/plugin versions are unknown. |
| [CK Galaxy View Apply traces](experiments/x64dbg-runtime-generation-findings.md) and [function register](function-register.md) | CK address space, live build and hash unknown | Observed native control flow, addresses, offsets and state ordering during Apply | Scenario-specific runtime observations. Data/plugin versions are unknown. Broader object lifecycles and retail addresses require separate evidence. |
| [Historical ten-body holdout](experiments/v1-holdout-validation.md) | CK and retail builds/hashes unknown | Output semantics | CK biome assignments and retail final planet-wide scan membership, 10/10 exact. Run date and data/plugin versions unknown. Native equivalence and retail lifecycle remain open. |
| [Canonical 1,444-body validation](v1-research-baseline.md#validation-baseline) | Reproducer source-data snapshot, upstream retail capture build unknown | Output semantics | Exact on the CK/RSGD-visible planet-wide validation channel. Run date and base-game/plugin/DLC versions unknown. Atmosphere-derived final membership and native equivalence are outside the oracle's coverage. |
| Current retail identity above | Steam `1716740`, observed build `23518663` | Executable identity | Applies to the measured local file. No data/plugin identity was needed for this observation. |
| [SRR-002 retail mapping](SRR-002-retail-static-reconnaissance.md#retail-mapping-on-the-pinned-image) | Pinned retail executable and matching saved Ghidra program above | Bounded static native control flow, addresses and offsets | The dossier grades each pairing and bounds the search. Retail execution, output equivalence and lifecycle remain open. |
| [SRR-003 retail static dispatch](SRR-003-retail-allocator-invocation-and-dispatch.md) | Same pin, reverified 2026-11-13 UTC against the installed and analysis copies and saved Ghidra program | Resolved native callback dispatch and conditional PNDT enumeration | Ghidra 12.1.2 PUBLIC and Capstone 5.0.7. Static `StarField::ModuleState` construction path. Runtime flag values, named gameplay association and invocation frequency are unobserved. |
| [SRR-009 Stage A](SRR-009-retail-debugger-admission-and-stage-a.md#finding) | Same pinned retail image, Steam build `23518663` | Custody-backed qualified non-observation | Two verified post-title windows totaling 84.281 seconds, zero hits at the four sites. Coverage excludes startup before arming, loading and gameplay. |

The [SRR-011 allocation lifecycle dossier](SRR-011-planetary-allocation-execution-and-result-lifecycle.md)
reverified the same pin against both retail copies. Its native route
uses Capstone 5.0.7 on Python 3.14.3. Same-build sibling observations
qualify earlier startup and menu-return frames. Direct retail allocation
timing and saved-slot persistence remain open.

The [SRR-012 feasibility dossier](SRR-012-retained-planetary-allocation-state-observation-feasibility.md)
reverified the same two PE files and checked the existing retail Ghidra
project's file identity and custody. The new owner and index observations
are static on that pin. Sample tuples are conditional predictions from
versioned data and model inputs. The disposable decision fixture uses
fabricated inputs. Retail checkpoint state and ordinary process-read
feasibility remain untested.

The [SRR-014 startup and database dossier](SRR-014-startup-allocation-component-database-lifecycle.md)
applies to the pinned retail image reverified on 2026-11-17 UTC. It uses
the tracked PE decoder with Python 3.14.3 and Capstone 5.0.7 for offline
control-flow, queue, insert and synchronization evidence. The normal late
iterator return orders its synchronous visits. Whether any given visit
produced the historically observed title-card slots remains unresolved.
The dossier identifies the pinned sibling records used for upstream
runtime attribution and the lawful-input route for independently checking
its static claims.

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
