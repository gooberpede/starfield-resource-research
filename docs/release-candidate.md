# Proposed first research release

**Provisional.** SRR-025 recommended closing research within the tested scope. The maintainer still owns release numbering, approval of the exact source tree and publication. The inventory below starts from research commit `d37d56e4b843e14e98ca6a87d04eaabfc67f562c` (190 tracked files). The release commit will be selected after review.

## Draft release notes

<!-- release-notes-begin -->
**Starfield resource research v1.0.0 (Starfield and Creation Kit 1.16.244.0)**

Proposed tag `v1.0.0-sf1.16.244.0`. This proposed release documents the recovered **v1.0 generation model** for per-biome inorganic resource membership. Two installed executable identities qualify the build-specific findings.

| Executable | File and product version | SHA-256 |
| --- | --- | --- |
| Starfield.exe | 1.16.244.0 | `7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28` |
| CreationKit.exe | 1.16.244.0 | `ed54e4906bc13b0fbc43ec7624fec4af2389a9a1e12b2789d73c5617f5a14020` |

The historical canonical comparison matched 1,444/1,444 CK/RSGD-visible planet memberships. The targeted pathological CK biome cases and ten fresh CK/retail holdouts matched in their measured channels. Retail comparison found 22,470 diagnostic slot agreements across 3,210 shared keys. **0/3,211 rows qualified for strict native-oracle admission.** A biome match identifies a region to search. Deposit geometry and co-location within an outpost radius remain unknown.

The fingerprints qualify the corresponding static analyses. Historical CK live sessions, retail screenshots and holdout scans lack session-specific executable fingerprints. Native instruction equivalence and applicability to other builds remain unestablished. The [companion model, inputs and tests](https://github.com/gooberpede/starfield-resource-reproducer/tree/a8ff1c788bca415f571f06769ab3e712fa674f75) are pinned to `a8ff1c788bca415f571f06769ab3e712fa674f75`. Readers can use the research source tree directly. Proposed supplements cover the comparison result, seven-slot census, selected survey displays and the two complete saves used for the serialized-state comparison. Availability depends on clearance of each specific attachment. Verification involving game files requires separately obtained lawful matching inputs.
<!-- release-notes-end -->

## Version and source contract

The identities in the notes are the manifest's two executable input pins. On 20 November 2026 at 02:41 UTC, read-only SHA-256 checks bracketing the version reads agreed for both installed files. Retail measured 102,476,200 bytes and CK measured 239,885,664 bytes. CK MD5 `0215f03ec24922dfd4015dcdc5317dc4` connects the static exports to the measured CK. The installed interface archive has its own input pin. Historical build and load-order qualifications are recorded per claim in [provenance](PROVENANCE.md).

The release number tracks changes to the research and its distribution. The shared suffix records the two verified matching versions. A Bethesda update leaves the historical release applicable to its original scope. Supporting changed bytes requires revalidation and a new composite tag. If the verified versions diverge, include both, for example `v1.1.0-sf1.17.100.0-ck1.17.90.0`.

## Candidate asset manifest

Select an attachment when its absence would materially limit a reader's ability to evaluate or reproduce a published result. **Five supplemental assets are proposed, all pending approval.** None is included in the generated source archives. The [claim matrix, member identities and individual save assessments](release-public-evidence.md) give the basis for each decision.

| Proposed manual asset | Reader and purpose | Current bytes and decision |
| --- | --- | --- |
| `retail-allocation-comparison-v1.0.0-sf1.16.244.0.zip` | Inspect the original diagnostic outcome, strict admission and input digests. | Built, 4,898 bytes. SHA-256 `7e2b377d4c2b8ec133298f809f606c178d058f8f5c95242b2e52ca107bee6d7f`. Approve the bounded report and selected identifiers. |
| `retail-biome-slots-v1.0.0-sf1.16.244.0.zip` | Independently count the 3,211 observed keys and compare their seven lanes with the pinned model using the compact comparator. | **Planned, unbuilt.** Exact CSV and a newly prepared path-free comparison manifest. Requires clearance for the complete normalized table of Bethesda-derived identifiers. |
| `survey-display-evidence-v1.0.0-sf1.16.244.0.zip` | Inspect selected Volii Alpha and Kreet display states and their recorded order. | **Planned, unbuilt.** Nine unmodified JPEGs and a public index. Clear the selected imagery, visible details and embedded metadata. |
| `save2-srr022-v1.0.0-sf1.16.244.0.sfs` | Reinspect the serialized baseline for the Save2 observations and one side of the PlayerKnowledge comparison. | Existing full SFS, 2,475,440 bytes. SHA-256 `1ac3d496e532b6286d983a1449946ba4fe34a34e66295c9d1d7da677772903d1`. Individual consent and rights decision pending. |
| `save52-srr022-v1.0.0-sf1.16.244.0.sfs` | Independently inspect the later, extensively played state and repeat the comparison across complete saves. | Existing full SFS, 16,411,136 bytes. SHA-256 `6b4a10084c7e752c31fd2de121a00850aaa2bf1decd700b437d7dccfcdbc82e8`. Separate consent and rights decision pending. |

**Source-contained.** The research subjects, provenance, registers, focused CK evidence, tools, schemas and tests travel with the approved Git tree. Preserve LICENSE and THIRD_PARTY_NOTICES.md. Review its inherited executable-derived excerpts and both nested historical archives as part of that tree. The pinned companion revision owns the model, production CSVs and validation oracle.

**Lawful external inputs.** Native checks use the matching retail PE, CK, interface BA2 or plugin headers required for the particular claim. Obtain them independently. The pinned public reproducer remains the sole cross-project execution dependency.

**Limited historical evidence.** The written ten-body holdout, historical CK trace observations and title/load timing measurements retain their original scope. The selected derivatives let researchers inspect output agreement. Raw private journals remain necessary only for an exact replay of the original acquisition.

**Omitted.** Whole Ghidra databases, bulk decompilations, observer memory, source-path manifests, Steam account records, exploratory outputs, failed-trial directories, other saves and the private backup packages add no required release capability. The earlier 2,135-hash inventory remains a private discovery aid. Custody decisions about those files are independent of release approval.

The checkout also contains repository housekeeping (`.gitignore`, `exports/.gitkeep`). A packaging dry run at the starting commit using Git 2.53.0.windows.1 and the ZIP options below produced 190 files in 1,032,467 bytes, SHA-256 `f0302d68d9bef2002efb3776c99f27ea88d5f2ac1ac199c6aa2279991ee1e5b8`. Python's `ZipFile.testzip()` passed on the archive and both nested ZIPs. That digest identifies the starting snapshot only. The source downloads inherit the selected commit, including tracked historical material. Leaving a file off the attachment list cannot remove it from that commit. If any tracked item lacks clearance, hold publication until its disposition is resolved in the reviewed candidate. See [third-party notices](../THIRD_PARTY_NOTICES.md) and the [publication rules](research-workflow.md#publication).

## Release decision and remaining work

SRR-026 pins the release inputs, removes implicit sibling discovery from
oracle qualification and identifies which methods a clean research checkout
can run. The [dependency inventory](release-workflows.md) covers each supported
workflow. The [smoke receipts](release-smoke-tests.md) distinguish new runs
from prior custody-backed results.

| Status | Owner | Action or limit |
| --- | --- | --- |
| Release gate · exact source tree and rights | Maintainer | Review the bounded CK excerpts, attributed code and nested archive members at the actual release commit. Resolve any hold before approving that tree. |
| Release gate · documentation and history | SRR-027 and SRR-028 maintainers | Assess technical documentation and navigation in SRR-027. Reconcile historical briefs and audits in SRR-028, preserving unique evidence. Review any resulting change in the final candidate. |
| Release gate · independent acquisition and packaging | Final candidate verifier | Obtain both exact Git checkouts independently. Verify the companion HEAD, run the pinned oracle controls with the specified checkout byte policy, rerun the canonical regression and inspect the source archive made from the approved research commit. Record commit, tree, checksum and exits. |
| Release gate · publication | Maintainer | Approve the research version, tag, final notes and rights disposition after candidate verification. |
| Held individual method | Research tooling maintainer | Assign ownership and qualify a self-contained reader before advertising fresh Kreet/Decaran base-field rederivation. The historical comparison and the conditional corpus controls retain their separate evidence scopes. |
| Nonblocking operator limits | Operator | Live title-card collection needs a separately authorized session and matching installation. The private preservation command also assumes the documented C: and D: space checks. Neither is needed to consume the research model. |

## Final verification and later authorized publication

The maintainer must approve one full research commit after SRR-027, SRR-028 and final candidate checks. In a clean detached checkout at that approved commit, PowerShell users can reproduce a local source ZIP for review. Supply `$approvedCommit` as the approved full object ID and `$reviewDir` as a fresh, existing directory outside the checkout. Inspect the Git list, ZIP members and nested archives for held material. The local ZIP hash identifies those local bytes only. Retain the receipt privately.

```powershell
$tag = 'v1.0.0-sf1.16.244.0'
$title = 'Starfield resource research v1.0.0 (Starfield and Creation Kit 1.16.244.0)'
if ((git rev-parse --verify HEAD) -cne $approvedCommit) { throw 'Unexpected research commit' }
if (git status --porcelain) { throw 'Use a clean candidate checkout' }
git rev-parse 'HEAD^{tree}'
git ls-tree -r --full-tree HEAD
$zip = Join-Path $reviewDir "$tag-source.zip"
git -c core.autocrlf=false archive --format=zip "--prefix=starfield-resource-research-$tag/" "--output=$zip" HEAD
if ($LASTEXITCODE) { throw 'Source archive failed' }
Get-FileHash -Algorithm SHA256 -LiteralPath $zip
tar -tf $zip
if ($LASTEXITCODE) { throw 'Archive inspection failed' }
```

For publication, the maintainer first records the approved subset in a release manifest with one row per attachment: public filename, measured byte length, SHA-256, purpose, clearance decision and exact permitted members. For each planned ZIP, assemble only its listed members, inspect them after extraction, and measure the finished archive. For each SFS, compare the complete payload with the specimen hash and use its neutral public filename. The private custody ZIPs contain additional material and are excluded. Record withheld candidates and their verification limits in the final notes.

1. Review that manifest, the exact research commit, the release notes and individual rights decisions. Supply `$repo`, `$tag`, `$title`, `$approvedCommit` and `$noteFile` for this release. Obtain explicit authorization for the tag and publication.
2. From the verified checkout, create the approved annotated tag with `git tag -a $tag $approvedCommit -m $title`, push that tag with `git push origin "refs/tags/$tag"` after verifying the remote, and create a draft with `gh release create $tag --repo $repo --verify-tag --draft --title $title --notes-file $noteFile`. Stop on a failed command.
3. For **each individually approved file**, check the exact name, byte length, SHA-256 and contents against the manifest. Upload that file with `gh release upload $tag $approvedFile --repo $repo`. Check the draft's entire attachment list against the approved subset, including any withheld saves. Publish the approved draft with `gh release edit $tag --repo $repo --draft=false`.
4. An independent reviewer downloads each published attachment into an empty directory with `gh release download $tag --repo $repo --pattern $approvedName --dir $freshDirectory`. Verify the names, file lengths and hashes against the pre-upload manifest and each ZIP member against its approved list. Record the release and asset IDs, tag, commit, retrieval date and verification results. Check GitHub's generated source archive against the approved tree separately. A mismatch keeps that asset's verification open.

This check covers the selected public assets. The 2,135-item catalog, off-host restoration of the local project and deletion of working files are outside release acceptance. GitHub distribution supplies a retrieval route at the time it is checked. Future host availability remains outside this verification.

## Original SRR-026 independent review

**COMPLETE** — The independent internal challenger verified the revised eight-file patch and the separately fetched, clean companion commit. All 28 qualifier tests passed in the challenge run, and all three freeze files matched the public-fetch receipt byte for byte. This resolves the earlier acquisition hold. Maintainer rights approval, SRR-027, SRR-028 and verification of the final release commit remain open. Research starting HEAD `d37d56e4b843e14e98ca6a87d04eaabfc67f562c`. Substantive file manifest SHA-256 `c921876f0105cbaf64536aacf607323264973cf2ffb4ac9f7bf3e33388d48c9b`. The manifest hashes sorted UTF-8 lines of lowercase file SHA-256, two spaces, repository-relative path and LF. Only this final section, starting at its heading, is excluded.

## Earlier preservation review (historical snapshot)

**COMPLETE** — The independent challenger verified the preservation plan, public package bytes and historical comparison scope, checked private collections and Git evidence, and replayed the two-file patch against the original working state. Publication clearance and independently restored surviving evidence remain open. The reviewed two-file SHA-256 manifest is `2bd2928208c33d887efa4a7b8438306cadf8ad2194ea1001920ce2108aeeb1bc`, using the original SRR-026 line format and excluding this follow-up review section. The baseline includes the uncommitted SRR-026 candidate at the start of the follow-up.

## Evidence selection review

**COMPLETE** — The independent review verified the six claim groups, the individual full-save assessments, the selected screenshot and comparison inputs, and byte-exact patch replay against the starting worktree. Asset clearance and publication remain pending. The reviewed two-file SHA-256 manifest is `3f8227af93c1148608053e12a25558a5e0f394f53935648c15b74982bb6fd016`, using the original SRR-026 line format and excluding this selection review section. The baseline includes the uncommitted preservation follow-up.
