# SRR-001 — Executable identity and research foundations

## Objective and baseline

Qualify the historical CK research, record the designated installed retail
executable, and establish the [research workflow](research-workflow.md).
The [v1 baseline](v1-research-baseline.md) governs the recovered algorithm.
This investigation used read-only identity checks and existing research
records. Retail native control flow, addresses, offsets, and lifecycle are
open research questions.

The checkout started at `a23e1c337bc369232d6ce463552a53617bb918e2`
with an empty index diff and no tracked worktree changes. The supplied
implementation brief was already untracked. It remains a preserved input
outside the task patch.

## Method and observations

Read the historical [static bundles](PROVENANCE.md#creation-kit-static-evidence),
[live notes](experiments/x64dbg-runtime-generation-findings.md),
[holdout](experiments/v1-holdout-validation.md), and
[function register](function-register.md) with the v1 baseline. Checked
relevant project records and Git history for build associations. Measured the
designated Steam files using version metadata, file hashes, and app manifest
fields as described in [provenance](PROVENANCE.md). Neither executable was
launched or analyzed.

| Check | Outcome | Evidence needed for a stronger claim |
| --- | --- | --- |
| Historical CK static fingerprint | Both focused bundles record the same MD5. The installed CK candidate matches it and reports file/product `1.16.244.0`. Its new SHA-256 pins the measured candidate. | A historical installation record for the original Steam build. The candidate match supports executable version attribution. |
| Historical CK live | The recorded CK address-space association stands. No trace-specific executable hash, version, or data/plugin identity was found. | A trace-session capture or a build record tied to that session. |
| Historical CK and retail holdout | The historical report records 10/10 output matches. Neither executable nor the data/plugin builds are identified by those runs. | Run-linked executable and data provenance. Native claims require separate native evidence. |
| Canonical validation | The 1,444-body result applies to the recorded corpus and CK/RSGD-visible channel. Historical executable and data/plugin build details remain unresolved. | Run-linked capture records and data manifest. |
| Installed retail | File/product version `1.16.244.0` and SHA-256 observed, with Steam app `1716740` build `23518663` recorded separately. | Future retail work must establish native claims on its own measured input. |

The [applicability register](PROVENANCE.md#applicability-register) gives the
limits of each evidence class. The About image was retained in its supplied
local location as an input to the SRR-001 dossier and review, solely to verify
the [displayed text](PROVENANCE.md#creation-kit-static-evidence). The receipt
pins its SHA-256. The screenshot stays local and unpublished. The brief,
screenshot, executable bytes, Steam manifests and review records stay outside
the patch.
No scratch copy was promoted to public evidence.

## Release scope

The [third-party notices](../THIRD_PARTY_NOTICES.md#srr-001-sources-and-permissions)
record inspection authority, credit and redistribution limits. This table
assesses candidate claims for a future release decision.

| Candidate claim and build scope | Essential evidence and verification route | Rights and hold |
| --- | --- | --- |
| CK static direct call at `0x14152D28F` from `FUN_14152CBC0` to `FUN_1415DCFB0` on the fingerprinted CK | [Pre-biome bundle](experiments/evidence/pre-biome-resource-state/), with the walk below. A lawful matching CK copy and the bundle's versioned Ghidra recipe are an optional reproduction route. | Existing focused material has the rights boundary in the notices. Hold new executable-derived excerpts pending specific clearance. |
| CK live Apply behavior on the recorded CK address space | [Live findings](experiments/x64dbg-runtime-generation-findings.md) document the observations. The underlying trace and trace-specific identity are essential for independent build-specific verification. | Hold build-specific or full-trace claims pending trace evidence and clearance. |
| 10/10 historical CK/retail output agreement | [Holdout report](experiments/v1-holdout-validation.md) documents the sample and aggregate result. Run-linked identities and raw observations would be needed to replay the original comparison. | Hold exact historical replay and any native or lifecycle inference. |
| 1,444-body canonical model agreement | [Reproducer v1.0.0 validation baseline](https://github.com/gooberpede/starfield-resource-reproducer/blob/v1.0.0/docs/V1-VALIDATION-BASELINE.md) and the versioned corpus and runner. This route can test the model against that corpus. | The companion notices govern game-derived data. Hold historical build attribution and republication of game-derived inputs pending specific authority. |
| Observed local retail file identity | Hash and version commands in [provenance](PROVENANCE.md#current-retail-identity) on a lawfully obtained copy of the named build. If that build is unavailable, comparison waits for a matching copy. | Publishable scope is project-authored metadata and method, subject to maintainer decision. Hold executable and manifest redistribution. |

### CK evidence walk

At research revision `a23e1c337bc369232d6ce463552a53617bb918e2`,
start at the [pre-biome bundle README](experiments/evidence/pre-biome-resource-state/README.md)
for its recorded MD5 and excerpt scope. In
[orchestrator metadata](experiments/evidence/pre-biome-resource-state/FUN_14152cbc0-metadata.json)
check the same MD5 and the caller entry. In
[generator callers](experiments/evidence/pre-biome-resource-state/FUN_1415dcfb0-callers.json)
check `callSite`, `referenceType` and caller entry. The
[instruction excerpt](experiments/evidence/pre-biome-resource-state/FUN_14152cbc0-instructions-excerpt.txt)
shows `14152d28f  CALL 0x1415dcfb0`. The two exports support that direct
edge within the fingerprinted static evidence. The walk uses repository
objects and makes no claim about how often the call executes. All four
sources were retrieved from the public GitHub repository at the pinned
revision and their blob IDs matched the local Git objects. The public
reproducer baseline was also retrieved at tag `v1.0.0`.

## Verification

The local receipt records starting and ending repository state, protected
inputs, repeated content hashes, preserved evidence comparison, UTF-8 and
link checks, the task file inventory, and patch replay. The receipts and
review copies are administrative working records. The historical evidence
and project release versions remain governed by the sources linked above.

Caller-available space measured at 04:51:55 UTC on 2026-11-13 was
87,674,273,792 bytes on C: and 69,837,811,712 bytes on D:. The dry run
allows both drives at exactly 40,000,000,000 bytes after projected writes,
refuses a one-byte shortfall on either drive, and refuses an unavailable
reading on either drive. The work consisted of read-only checks and small
documentation and handoff files.

<!-- review-status:start -->
## Review status

**COMPLETE.** An independent challenger reviewed this snapshot in an internal
challenge against SRR-001 and AC1–AC7. The follow-up review confirmed that the
incidental About text is excluded from version qualification and that the
screenshot stays local. Scientific confidence rests on the evidence and limits
documented above.

Reviewed manifest SHA-256
`5cb36cb291a8f491e96f973ab0ca6d17ed53051d3b7b4da25ac2709863560fc3`.
The deterministic manifest covers the nine task paths in sorted order. Each
line contains the file SHA-256, two spaces, the repository-relative path,
and LF. The dossier hash excludes this entire review-status block, including
its marker lines. The challenger verified the populated block and final
patch against the covered content.

Material limits remain the unpinned live and historical output builds,
historical data/plugin unknowns, and the release holds above. Retail native
equivalence and lifecycle remain open.
<!-- review-status:end -->
