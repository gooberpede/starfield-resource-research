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
The version qualification does not identify a historical live-trace session.

## Creation Kit live evidence

The [x64dbg findings](v1-research-baseline.md) use
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
current pin also qualifies [retail static correspondence](v1-research-baseline.md#pinned-retail-correspondence-and-native-differences).
The existing Ghidra 12.1.2 PUBLIC program recorded the same import SHA-256,
base `0x140000000`, language `x86:LE:64:default` and compiler ID `windows`.
An independent PE decode corroborated the instruction locations and critical
operands in the focal listing. The historical scan builds remain unknown.

## Locations interface input

The installed `Data/Starfield - Interface.ba2` inspected on 19 November 2026
is a 135,450,443-byte BTDX v2 GNRL archive, SHA-256
`dab6aeebb7e54282818e9a1957e80baef22ae992c6363cbe910f92b8adf3e702`.
This input qualifies the [Locations presentation findings](component-database.md#how-locations-gets-its-resource-counter).
Co-installation with the pinned retail executable does not establish the
assets selected in any supplied screenshot.

| Archive member under `interface/` | Zero-based directory index | SHA-256 of complete compressed SWF member |
| --- | ---: | --- |
| `locationspage.swf` | 135 | `3977612bf4f8285ac6dfed149a8ce01c23ac8ccc5e8c1673be40434978c4998d` |
| `locationspage_lrg.swf` | 136 | `79faa3c6c342935b42a278dde791ed49098f32073b3cdcc93890ce2072372038` |
| `planetinfocard.swf` | 175 | `fdd8731f2445b67f4e0c0a4e6e394cca6aed13a24fdc90e90e64028b3f7636fd` |
| `planetinfocard_lrg.swf` | 176 | `955a87392ba4c43c1ef6ba89c222583a0f2048b2ced376722cbd706376b124b4` |

**Reproducible method.** From a lawful matching archive, use the following
Python 3 standard-library check with the archive path as its sole argument.
It reads four indexed entries, checks the counter loop in both page layouts
and prints member identities. It writes no files.

```python
import hashlib, struct, sys, zlib

with open(sys.argv[1], "rb") as archive:
    assert hashlib.file_digest(archive, "sha256").hexdigest() == (
        "dab6aeebb7e54282818e9a1957e80baef22ae992c6363cbe910f92b8adf3e702"
    )
    for index, method in [(135, 0x27CC0), (136, 0x27E94), (175, None), (176, None)]:
        archive.seek(32 + 36 * index)
        offset, packed, size = struct.unpack_from("<QII", archive.read(36), 16)
        assert packed == 0
        archive.seek(offset)
        member = archive.read(size)
        print(index, hashlib.sha256(member).hexdigest())
        if method is not None:
            body = zlib.decompress(member[8:])[method:][:225]
            # AVM2 iftrue skips the increment of integer local 4.
            assert body[0x53] == 0x11 and body[0x57:0x59] == bytes([0xC2, 4])
            assert 0x57 + int.from_bytes(body[0x54:0x57], "little", signed=True) == 0x59
```

To verify the semantics, inspect the SWF DoABC tag (82), resolve AVM2
multinames against its constant pool and follow these ABC method indexes in
either Locations member. `1257` subscribes the provider, `1262 → 1285`
passes event data to the card, `1039 → 1233` dispatches the projected data,
and `1234` calls its superclass `1031`. In 1031 the instruction at method
offset +0x50 reads `bDisabled` and +0x57 increments x. The formatting path
at +0x86…+0xA7 reads x and the saved array length. Method 910 selects the
icon color, timeline frame, rarity and tag. In the PlanetInfoCard members
the corresponding icon method is 512. The two authored icon states can
also be checked in DefineSprite 18 (standard) or 16 (large) by following
the labeled frames and depth-1 color transform. No game process, UI dump
or save is an input to this check.

## Scanner and starmap interface inputs

The same hash-verified BTDX archive supplies four more uncompressed archive
entries, each containing a compressed SWF. The member hash covers the
complete SWF as stored in the archive. The evidence concerns these shipped
layouts. The effective UI and load order in the captures remain unknown.

| Member under `interface/` | Index | SHA-256 |
| --- | ---: | --- |
| `galaxystarmapmenu.swf` | 79 | `d7c2a2c437e1342b88a744cb331e7e4aefeccd46e5ba13f2f6987a39e2764559` |
| `galaxystarmapmenu_lrg.swf` | 80 | `ad56e480fadd237cb6b357b87c1a938994a46b46a3a14948a90cd306669118bb` |
| `monoclemenu.swf` | 162 | `1d7867d12e65356aaebffe73e74e186e9f6fd94e700c9423c0c0d4d7d5a2df2d` |
| `monoclemenu_lrg.swf` | 163 | `7ece68d18f44604a145475266cbe2947c4f70956e4e9f5efc3067aaaddcaca53` |

**Reproducible method.** In the [archive check above](#locations-interface-input)
use the entries `[(79, 0x38E06), (80, 0x381EC), (162, None), (163, None)]`
to verify all four identities and the orbital counter increment in both
layouts. For a direct wheel check, inflate member[8:] and inspect its 245-byte
slot setter at offset 0x2A723 (162) or 0x2A58E (163). In both layouts the
conditional branch at setter+0x9C selects the row-color path at +0xA8 when
disabled is false. For the named methods, read the DoABC tag, match method-body
indexes to class traits and resolve property operands in the ABC multiname
pool. Index pairs below refer to standard/large layouts.

| Movie | What to follow in the ABC |
| --- | --- |
| Monocle | Survey update 966/972, offsets +0x320…+0x332, assembles the two resource scalars with a slash. Known-resource update 967/973 passes arrays to 742/748 and slot setter 740/746. Inspect the disabled test and frame at +0x4F and RGB selection at +0x99…+0xBB in the setter. SHOW RESOURCES 941/947 calls the arc animation. Pick update 959/965 handles the selected tile. |
| GalaxyStarmapMenu | Subscribe 1338/1288 → callback 1337/1287 → Planet.SetBodyInfo 1389/1402 → BodyDataInfo.SetBodyInfo 1438 in both. System view subscribes in 1648 and calls its card in 1647. Method 1437 initializes up to eight icons. Method 1450 counts them and handles empty arrays. Method 866 projects each resource icon. The imported PlanetInfoCard supplies eight authored positions and the Known/Unknown timeline detailed above. A separate callback 1336/1286 leads to hover nameplate update 1342/1292. |

For native verification run the [pinned PE decoder](component-database.md#offline-reproduction)
from the repository root with the same lawful executable as `$image`.
The commands read disk bytes and print bounded disassembly.

```powershell
python -B tools/srr011/inspect_pe.py $image functions 141599EC0 141597A50 1407B7D60 1407BB5B0 14159A0B0
python -B tools/srr011/inspect_pe.py $image window 1415996DA 48
python -B tools/srr011/inspect_pe.py $image window 14159B439 38
python -B tools/srr011/inspect_pe.py $image window 141681680 70
python -B tools/srr011/inspect_pe.py $image window 141685AD2 70
python -B tools/srr011/inspect_pe.py $image window 141685D1B 7E
python -B tools/srr011/inspect_pe.py $image functions 14168FC50 141698650 141685E30 14168A8D0 14168AE30
python -B tools/srr011/inspect_pe.py $image window 1416E8572 72
python -B tools/srr011/inspect_pe.py $image functions 1416ED390 1416E87C0
```

## Save2 screenshot evidence

**Custody-backed historical observations.** All 15 gameplay captures began
from Save2 according to the maintainer. Each retained original was copied
from Steam and compared byte-for-byte with its scratch counterpart. Fourteen
also match the JPEGs and supplied manifest in the handoff ZIP (SHA-256
`4ecd292c8fa6cffdb20f61f4ff8232665c6a20417f5a43b4182bfeee0a12ce29`).
S21-01 is the additional original corresponding to scratch alias
`1716740_173.jpg`. The CK About screenshot has separate provenance above.
The private custody manifest (SHA-256
`98ee59595ab0e15c21246188101e50e6ebc1ae6edb7903be5ee26f23abd19874`)
records filenames, sizes, capture metadata and limits. A second reader
verified the original, scratch, retained and archive bytes. Redistribution
is the maintainer's decision.

Steam creation records establish the order below. The groups 01, 02–04,
05–09 and 10–15 belong to four different Steam timelines. Within each
multi-frame group the timeline offsets also increase. The reported scan
action between 13 and 14 comes from the maintainer. The sequence measures
display states, with no input log, executable fingerprint or memory read
for those particular frames. Percentages refer to the displayed survey
percentage unless qualified.

| Evidence ID | Displayed observation | SHA-256 of original JPEG |
| --- | --- | --- |
| S21-01 | Sumati, Starmap, seven muted symbol tiles and SCAN prompt. 0/7, survey 17%. | `ab172d19d644ef84937ecb9bc81e490562ba0116c265232b3790a21417a4f3f0` |
| S21-02 | Kreet, Locations, five resource-colored and three muted tiles. 4/8, survey 60%. | `5cc2d3559d55ca5c0af84e4ccd3e9d0663060414789c5a50124a0170cf811c12` |
| S21-03 | Vectera, Locations, five colored tiles. 0/5, survey 80%. | `4ba7eb186874ca0f75d9e49a7b251091ad907582e9879ac843289d4e0bcc23bd` |
| S21-04 | Sumati, Locations, RESOURCES UNKNOWN with no resource rows. UNKNOWN, survey 17%. | `182957c9b9a7d18676d0cd83cbedfc6e4679834c99af9770e0b597f493a03f1b` |
| S21-05 | Kreet, Scanner, green-outlined target at 9 m, single large Pb/Lead wedge, SHOW RESOURCES prompt. 4/8, survey 61%. | `85c9a13af7e0ef5b779704d36f69291fe7ed31eaa6e210f1eab257b2d9629cfd` |
| S21-06 | Kreet, Scanner, same Pb target; expanded resource wheel above large Pb wedge. 4/8, survey 61%. | `478b6cd7565cc488b0afe7a743828ba3ec8fde5af5e7c2a0aef25c77ab404bc5` |
| S21-07 | Volii Alpha, Starmap, Neon settlement marker; two muted tiles H2O and C6Hn. 0/2, survey 31%. | `0690298d7ae65c974274ef7c8afeee722bddbac1be1c57e87c0ffac4264c88a9` |
| S21-08 | Volii Alpha, Ordinary handheld scanner, cockpit looking toward Neon. 2/2, survey 88%, fauna 0/2. | `89a957ba4fe1d63dbef4685ff358e40da66f41f8d6e6af1fad184016fc29dafd` |
| S21-09 | Volii Alpha, Ordinary handheld scanner, exterior landing pad below ship, NEON banner. 2/2, survey 88%, fauna 0/2. | `d3cd6e043104474936ab6d852ad82987a80348167e027371c7402ad325612623` |
| S21-10 | Kreet, Starmap, body selected; 8 square tiles in left panel. 4/8, survey 60%. | `f5a607daa3c1b9ef54b2380f698c62069cde3b6d45a9cfcd1ab728d2382bb2aa` |
| S21-11 | Kreet, Starmap, same left inventory, travel data Jemison to Kreet, Frozen Volcanic, LAND prompt. 4/8, survey 60%; destination Frozen Volcanic 0%. | `7a8f98aabb594291bd8fa04f917c12230789af8d41560527a67afe0f0fe6c7d9` |
| S21-12 | Kreet, Landing Area handheld scanner, cyan terrain beyond reticle, no named target or wheel. 4/8, survey 61%. | `39c53b3998b5e67541965795780cd98a713c35dcbdefa4c5cdf44433fa3328cc` |
| S21-13 | Kreet, Locations, eight named rows; muted Ne tile with three diamonds. 4/8, survey 60%. | `afa0faaa5c0a3983c1aae95b83c920781b72754c884f2b0178b0107a56d06990` |
| S21-14 | Kreet, Landing Area scanner, expanded wheel; small cyan Ne tile and separate large cyan Ne/Neon wedge, reticle over cyan terrain. 5/8, survey 63%. | `d08e77ae602e6bf98430713e86be554f9d2bc92b98ecb82ca233aa382241e20b` |
| S21-15 | Kreet, Locations, eight named rows; muted Ne tile still has three diamonds. 5/8, survey 63%. | `58e838822fe93a030c304a148b8ee428fb4674725a2c8de464c737277c19738a` |

## Applicability register

| Evidence or claim | Executable/build reference | Claim type | Qualification and limit |
| --- | --- | --- | --- |
| [Pre-biome static bundle](experiments/evidence/pre-biome-resource-state/) | CK static fingerprint above | Native control flow, addresses and offsets | Applies to the focused export and excerpt scope. Historical data/plugin versions are unknown. Later live evidence governs conflicts. |
| [Special/Common static bundle](experiments/evidence/special-common-selector/) | Same CK static fingerprint | Native selector control flow, addresses and constants | Applies to the focused export. Historical data/plugin versions are unknown. |
| [CK Galaxy View Apply traces](v1-research-baseline.md) and [function register](function-register.md) | CK address space, live build and hash unknown | Observed native control flow, addresses, offsets and state ordering during Apply | Scenario-specific runtime observations. Data/plugin versions are unknown. Broader object lifecycles and retail addresses require separate evidence. |
| [Historical ten-body holdout](v1-research-baseline.md) | CK and retail builds/hashes unknown | Output semantics | CK biome assignments and retail final planet-wide scan membership, 10/10 exact. Run date and data/plugin versions unknown. Native equivalence and retail lifecycle remain open. |
| [Canonical 1,444-body validation](v1-research-baseline.md#validation-baseline) | Reproducer source-data snapshot, upstream retail capture build unknown | Output semantics | Exact on the CK/RSGD-visible planet-wide validation channel. Run date and base-game/plugin/DLC versions unknown. Atmosphere-derived final membership and native equivalence are outside the oracle's coverage. |
| Current retail identity above | Steam `1716740`, observed build `23518663` | Executable identity | Applies to the measured local file. No data/plugin identity was needed for this observation. |
| [Retail mapping](v1-research-baseline.md#pinned-retail-correspondence-and-native-differences) | Pinned retail executable and matching saved Ghidra program above | Bounded static native control flow, addresses and offsets | The native correspondence is static. Output agreement is demonstrated within validation scope; joined retail write timing and full effective-input attestation remain open. |
| [SRR-003 retail static dispatch](retail-execution-lifecycle.md) | Same pin, reverified 2026-11-13 UTC against the installed and analysis copies and saved Ghidra program | Resolved native callback dispatch and conditional PNDT enumeration | Ghidra 12.1.2 PUBLIC and Capstone 5.0.7. Static `StarField::ModuleState` construction path. Runtime flag values, named gameplay association and invocation frequency are unobserved. |
| [SRR-009 Stage A](allocation-validation.md) | Same pinned retail image, Steam build `23518663` | Custody-backed qualified non-observation | Two verified post-title windows totaling 84.281 seconds, zero hits at the four sites. Coverage excludes startup before arming, loading and gameplay. |

The [SRR-011 allocation lifecycle dossier](retail-execution-lifecycle.md)
reverified the same pin against both retail copies. Its native route
uses Capstone 5.0.7 on Python 3.14.3. Same-build sibling observations
qualify earlier startup and menu-return frames. Direct retail allocation
timing and saved-slot persistence remain open.

Retail title-state read feasibility and defining namespace identity were later
demonstrated by SRR-013 and SRR-017. The [validation subject](allocation-validation.md)
retains the four selected vectors, complete 3,211-row rooted pair, source/work
pins, original receipt/output hashes and historical incomplete attempts.
These observations do not attest winning inputs, allocator timing or save
persistence. SRR-018's 22,470 shared-lane agreement corroborates the model
diagnostically; strict effective-input admission remains zero.

The [SRR-014 startup and database dossier](component-database.md)
applies to the pinned retail image reverified on 2026-11-17 UTC. It uses
the tracked PE decoder with Python 3.14.3 and Capstone 5.0.7 for offline
control-flow, queue, insert and synchronization evidence. The normal late
iterator return orders its synchronous visits. Whether any given visit
produced the historically observed title-card slots remains unresolved.
The lifecycle subject identifies the pinned sibling records used for upstream
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

## Verification routes and retention

**Reproducible method:** tracked Ghidra scripts and [offline PE tools](../tools/README.md)
operate on a lawfully obtained pinned executable or existing matching analysis.
Tracked qualifiers use disposable fixtures; oracle/comparison methods use the
four inputs at reproducer commit `a8ff1c788bca415f571f06769ab3e712fa674f75`.
Build pins constrain applicability and are not redistributable payloads.

**Custody-backed historical observation:** original live journals, saves,
policies, identities and related receipts are private. Their durable content
identities are recorded in [validation](allocation-validation.md). Fresh
fixture qualification cannot recreate the history of a past execution.
The SRR-017 original-evidence ZIP and compact derivative remain private;
the compact CSV reproduces comparison arithmetic only. Original receipt
replay needs its exact source pin; get historical source from its recorded
Git revision without bypassing the replayer's source check. Historical
SRR-013 evidence was inaccessible to the SRR-016 review account; that phase
did not replay it and relied on the earlier qualified custody record.

**Unresolved applicability:** CK live trace-specific identity, historical
scan builds, effective winning data/substitution closure and joined retail
write timing remain qualified unknowns. No current claim assumes CK/retail
instruction identity. Inspection/use authority and attribution are distinct
from clearance to redistribute images, native bytes or derived payloads.
See [rights notices](../THIRD_PARTY_NOTICES.md); no new release is authorized.
