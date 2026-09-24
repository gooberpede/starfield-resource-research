# Public Release Readiness Audit

Audit date: 2026-09-24

Audited repository: `gooberpede/starfield-resource-research`

Audited branch and commit: `main` at `0408bf1`

Reachable commit history: 20 commits, including all local branches and remote-tracking refs

Verdict: **NOT READY**

## Executive Verdict

The repository is technically coherent and the credential/binary hygiene of the committed material is good. No credential, private key, proprietary executable, debugger dump, Ghidra project database, or deleted historical payload of those types was found in the current tree or reachable commit history.

It is nevertheless **not ready for public visibility**. Two content groups need an explicit owner and, where appropriate, legal review before publication:

1. approximately 4.24 MB of game-derived CSV data under `data/`; and
2. focused native-code evidence under `docs/experiments/evidence/`, including decompiler output, instruction listings, and executable-derived strings.

These are not declared unlawful. The audit cannot make that legal determination. They are release blockers because the repository does not document a redistribution basis or an explicit publication decision, and publishing the repository would publish the same material in Git history. If the material is approved, no rewrite is needed for these findings. If it is not approved, removing it only from `HEAD` would be insufficient; the affected history would need to be rewritten before visibility changes.

Finding counts:

| Severity | Count |
|---|---:|
| BLOCKER | 2 |
| SHOULD-FIX | 6 |
| OPTIONAL | 2 |
| NO-ACTION | 4 |

## Scope and Method

The audit covered the tracked tree, every object reachable through `git rev-list --objects --all`, the complete 20-commit history of `main`, the remote-tracking refs, and the local Codex base-tree ref. The latter is a tree object rather than a commit and contains the user-supplied audit brief; it is not part of `main` or `origin/main`.

Checks included:

- `git status`, ref inventory, commit log/stat inventory, and historical filename inventory;
- `git rev-list --objects --all` plus blob-size and origin inspection;
- current-tree and history scans for credentials, private-key material, credential-bearing URLs, cookies/session IDs, personal email, local paths, and common cloud-token formats;
- current-tree and history searches for executable, library, PDB, archive, dump, debugger trace, Ghidra project/database, database, backup, temporary, and log extensions;
- inspection of `data/`, `ghidra/`, `docs/experiments/`, `docs/implementation-briefs/`, the core evidence documents, and the sibling reproducer's current canonical-data documentation;
- README, evidence-label, documentation-navigation, hard-coded-path, Markdown-link, UTF-8/mojibake, build/run, and `.gitignore` review;
- `git diff --check` and a final status/diff review.

The secret scan was local and pattern-based; no external scanning service was used. Findings do not reproduce any credential-like value.

## Findings

| ID | Severity | Location | Area | Finding | Why it matters | Recommended remediation |
|---|---|---|---|---|---|---|
| PRR-001 | BLOCKER | BOTH | Game-derived data | `data/` contains three derived datasets totaling about 4.24 MB. Their technical purpose is inferable, but this repository does not document their extraction scripts, redistribution basis, or an explicit publication decision. Two are older than the sibling reproducer's canonical inputs; the validation-oracle file is duplicated byte-for-byte there. | These are bulk commercial-game record/runtime-derived data, not merely a few quoted facts. Public redistribution is a human/legal judgment, and duplication makes the necessity of distributing every file here unclear. | Decide and record whether each dataset may be published. If approved, add provenance, scope, historical/current status, and regeneration guidance. If any file is not approved, remove it and rewrite all affected reachable history before making the repository public. |
| PRR-002 | BLOCKER | BOTH | Native reverse-engineering evidence | `docs/experiments/evidence/` contains 63 focused evidence files (133,597 bytes), including 11 decompiler outputs (36,093 bytes/1,139 lines), 11 instruction listings (54,353 bytes/1,711 lines), and executable-derived string/data-reference exports. | The selection is focused and research-oriented, not a reconstructive binary dump, but some individual exports are substantial enough that public redistribution should be an explicit decision rather than an accidental consequence of changing visibility. | Obtain owner/legal approval for the selected excerpts and document why they are necessary, scoped, and transformative. If any are rejected, purge the affected blobs from history before publication. |
| PRR-003 | SHOULD-FIX | CURRENT-TREE | Licensing | There is no top-level `LICENSE` or content-specific licensing notice. | Publicly visible source without a license is not automatically open source and generally leaves reuse rights reserved. A license for original work also cannot grant rights the owner does not hold in third-party/game-derived material. | Choose—not during this audit—appropriate terms for original scripts, documentation/research prose, and any approved game-derived data/evidence. Use separate notices or exclusions if one license does not fit all groups. |
| PRR-004 | SHOULD-FIX | CURRENT-TREE | README/public presentation | The README explains the research result well but has no actual Markdown links, does not identify the datasets or evidence directories, lists an untracked/empty `tools/` path, omits `data/`, `docs/implementation-briefs/`, and checked-in evidence, and does not give a counterexample/reporting path. The sibling repository is named but not linked. There is no brief unofficial/unaffiliated disclaimer. | A new reader can understand the conclusion but cannot efficiently navigate, reproduce, assess provenance, or distinguish tracked history from current tooling. The layout shown on GitHub would be inaccurate because Git does not publish empty directories. | Correct the layout; link the baseline, facts, hypotheses, function register, Ghidra guide, evidence, and sibling reproducer; explain data/oracle boundaries; state version scope and counterexample handling; add a short conventional Starfield/Bethesda non-affiliation notice. |
| PRR-005 | SHOULD-FIX | BOTH | Reproducibility/versioning | Address-sensitive findings identify Creation Kit context but do not record an exact Creation Kit executable build/hash or a retail build mapping. Dataset timestamps are present, but the associated Starfield/Creation Kit/plugin versions are not collected in one reproducibility record. | Native addresses and extracted data can drift between game, Creation Kit, DLC, and tool versions. Third parties cannot confidently reproduce or compare results without exact build provenance. | Add a version/provenance document recording legally non-sensitive identifiers: CK version/build and executable hash, Starfield/plugin versions, Ghidra/xEdit/x64dbg versions, relevant extraction timestamps, and which evidence bundle each version produced. Do not redistribute binaries. |
| PRR-006 | SHOULD-FIX | BOTH | Local-path portability | Twenty-one current lines contain absolute paths. Most author-machine paths occur in active Ghidra/evidence run commands (`D:\Projects\...`, `D:\tools\...`, `D:\ReverseEngineering\...`); one historical brief also names the workspace. Other matches are Bethesda build paths preserved in executable-derived strings. No Windows user-profile username was exposed. | The active commands appear copyable but only work on the author's machine. The Bethesda paths are provenance evidence, whereas the `D:` paths are avoidable portability problems. | Replace active run-command paths with documented placeholders such as `<ghidra>`, `<repository>`, and `<project>`. Retain extracted Bethesda paths only if PRR-002 is approved, labeling them as executable-derived evidence. Historical task paths may remain if clearly framed. |
| PRR-007 | SHOULD-FIX | CURRENT-TREE | `.gitignore` | Existing rules successfully ignore local `.local-work/` traces, `scratch/` Ghidra projects, and generated `exports/`. They do not independently protect common `*.trace64`, `*.dmp`, x64dbg database/session, archive-transfer, Python-cache, editor, or OS artifacts. Actual ignored local trace and archive files demonstrate the workflow risk. | Moving or copying a trace/archive outside the currently ignored directories could make it easy to commit sensitive or proprietary runtime evidence accidentally during public development. | Add narrowly justified patterns for debugger traces/dumps and relevant x64dbg databases. Consider archive patterns because this repository already uses ZIP evidence transfers, but document how to force-add a deliberately reviewed archive. Add only cache/editor patterns actually used; avoid broad `*.db` rules that could hide legitimate source fixtures. |
| PRR-008 | SHOULD-FIX | CURRENT-TREE | Documentation navigation/history | Core current documents are mutually coherent, but there is no docs index separating the v1 baseline, settled facts, hypotheses, superseded experiments, evidence bundles, and 19 tracked implementation briefs. The briefs are valuable rationale but contain transient task instructions and can look current when read directly. | Public readers may follow superseded work or treat an old task specification as current project direction. | Add a concise `docs/README.md` or equivalent index. Mark implementation briefs as historical task specifications, not current authority, and point readers back to `v1-research-baseline.md`. Keep superseded evidence rather than deleting it. |
| PRR-009 | OPTIONAL | CURRENT-TREE | GitHub metadata | The remote URL and `main` default remote branch are locally verifiable. The brief states the repository is private. Description, homepage, topics, and archived state could not be verified from this environment because GitHub CLI/API access was unavailable. | Good metadata improves discovery after publication but does not affect repository safety. | Before publication, verify the repository is unarchived and use a concise description such as “Reverse-engineering evidence and research history for Starfield's runtime inorganic resource generation.” Consider `starfield`, `reverse-engineering`, `ghidra`, `xedit`, and `modding`; link the reproducer when both repos are accessible. |
| PRR-010 | OPTIONAL | CURRENT-TREE | Ghidra documentation | `ghidra/README.md` is about 64 KB and documents seven genuine read-only scripts. It is coherent and is not a concatenated proprietary decompiler dump, but its length and mixed per-script compatibility statements make first use harder. | This is usability and maintenance debt, not a release-safety problem. | After release, consider a short index plus per-script pages and a compatibility matrix. Preserve the exact live-test procedures and read-only guarantees. |
| PRR-011 | NO-ACTION | BOTH | Secrets/privacy/identity | No high-confidence credential, private-key, cloud-token, cookie/session, credential-bearing URL, unintended email address, phone/address data, private share, or user-profile path was found. Commit metadata is consistently `gooberpede` with a GitHub noreply address. | No credential rotation or privacy history rewrite is indicated by the audited material. | Re-run the same checks immediately before visibility changes. Do not publish ignored local artifacts. |
| PRR-012 | NO-ACTION | BOTH | Prohibited binaries/databases | No committed or historically reachable `.exe`, `.dll`, `.pdb`, `.gpr`, `.rep`, `.dmp`, `.trace64`, archive, binary dump, Ghidra database, or x64dbg session/database filename was found. No historical path has been deleted from `main`; the committed history consists of the same path set now present at `HEAD`. | The repository policy against proprietary binaries and analysis databases has been effective. | Preserve the policy and strengthened ignore protections. |
| PRR-013 | NO-ACTION | CURRENT-TREE | Scientific/evidence consistency | Sampling found the current baseline, facts, hypotheses, function register, and experiment notes consistently distinguish CK from retail, current from superseded, and oracle data from generation logic. The 1,444/1,444 and 10/10 claims are scoped. Intentional mojibake examples were distinguished from corruption; no unintended current-tree mojibake was found. | No evidence-classification correction is justified merely for release polish. | Preserve the current claims and evidence labels. Resolve future contradictions through the documented research workflow. |
| PRR-014 | NO-ACTION | CURRENT-TREE | Security/release semantics | This is a research repository without a network service. A boilerplate `SECURITY.md`, issue-template suite, formal GitHub Release, or software-style `v1.0` tag is not required for initial publication. | Boilerplate could imply a maintenance/security contract or confuse the research baseline with the reproducer's software version. | Publish from a reviewed commit without a formal release initially. Optionally add a clearly named research-baseline tag later if a stable citation point is useful. |

## Explicit Blocker List

1. **PRR-001:** approve or remove and purge the game-derived CSV datasets.
2. **PRR-002:** approve or remove and purge the selected decompiler/disassembly/string evidence.

No credential, personal-data, executable, debugger-dump, or Ghidra-database blocker was found.

## History Safety

Publication of the full reachable commit history **does not yet appear safe as-is** because PRR-001 and PRR-002 are present from their introduction commits onward. The result is conditional on a publication/redistribution decision, not on a discovered secret or prohibited binary.

The history is small and linear: 20 commits on `main`, with no historical filename absent from `HEAD`. The largest reachable blobs inspected were:

| Approximate blob size | Path/type | Assessment |
|---:|---|---|
| 3,270,063 bytes | `data/PlanetResourceGeneration_v5.csv` | Game/plugin-derived CSV; PRR-001 |
| 956,217 bytes | `data/planet-all-resources.csv` | Runtime-derived validation-oracle CSV; PRR-001 |
| 166,388 bytes | `ghidra/scripts/AnalyzeClassFieldProvenance.java` | Original source script |
| 124,931 bytes | `ghidra/scripts/ExportFunctionNeighbourhood.java` | Original source script |
| 110,374 bytes | earlier `ExportFunctionNeighbourhood.java` revision | Original source history |
| 109,847 bytes | earlier `AnalyzeClassFieldProvenance.java` revision | Original source history |
| about 64 KB each | revisions of `ghidra/README.md` | Original documentation |

No credential rotation is required on present evidence. If the two content groups are approved, their mere presence in earlier commits does not require rewriting. If either is rejected, use a history-rewriting tool, verify every ref and clone, then force-push only as a separately approved remediation operation.

## Proprietary and Copyright-Sensitive Material

### Checked and absent

- Starfield/Creation Kit executables and Bethesda DLLs/PDBs;
- imported Ghidra projects (`.gpr`/`.rep`) and analysis databases;
- committed memory/process dumps, x64dbg `.trace64` files, session databases, or raw binary dumps;
- committed archives containing those artifacts;
- very large string-table or whole-binary exports.

### Human/legal judgment still required

- the three CSVs under `data/`; and
- the 133,597-byte selected evidence corpus under `docs/experiments/evidence/`.

The evidence corpus is targeted and accompanied by analysis and provenance, which supports a research/transformative characterization, but this audit does not provide legal advice or decide fair use. The datasets are more bulk-like and need especially clear provenance and necessity.

Local ignored material includes x64dbg traces/ZIP transfers under `.local-work/`, generated export archives under `exports/`, and a Ghidra project/database under `scratch/`. These were verified as untracked and unreachable from commits. They must remain private unless individually reviewed and intentionally transformed into a publishable evidence excerpt.

## Data Directory Audit

| Dataset | Purpose and origin | State | Approximate size | Sibling relationship | Publication assessment |
|---|---|---|---:|---|---|
| `PlanetResourceGeneration_v5.csv` | xEdit-derived PNDT/BIOM/RSGD/IRES generation inputs, including stored order, chances, source plugins, and extraction timestamp | Historical research input; 7,920 data rows; timestamp `2026-08-30 11:40:41` | 3.28 MB working-tree size | Current reproducer uses `planet-resource-generation.csv`, a different hash/snapshot with the same schema and a later timestamp | Important to the recorded validation history, but not the current canonical distribution; document provenance/regeneration and obtain PRR-001 approval |
| `Starfield_IRES_Hierarchy.csv` | xEdit-derived IRES parent/child hierarchy | Historical research input; 56 data rows; older eight-column schema without source/timestamp provenance | 5.5 KB | Reproducer uses `ires-hierarchy.csv`, a different hash and newer 11-column provenance-aware schema | Low volume but still game-derived; retain only with PRR-001 approval and label as historical |
| `planet-all-resources.csv` | `SurveyAggregator`-derived planet-wide inorganic membership used as a validation oracle/proxy | Validation evidence, not generation input; 7,663 data rows; incomplete for atmosphere-derived final membership | 956 KB | Byte-identical copy exists in the reproducer | The README correctly limits its semantics, but duplication and redistribution still need PRR-001 review; users should regenerate/use maintained reproducer tooling rather than treat this repo as canonical data distribution |

The public README currently explains only the oracle limitation for `planet-all-resources.csv`. It does not explain why all three files remain here, their extraction procedures, which are historical, or where the maintained canonical inputs/export scripts now live.

## Ghidra and Debugger Audit

The seven Java scripts under `ghidra/scripts/` use Ghidra's public program/decompiler APIs and bundled Gson. Inspection found no hard-coded author paths, network activity, Ghidra transactions, symbol/type/comment mutation, or program-memory writes. They read the analyzed program and write UTF-8 files to a supplied or user-selected external directory. `ghidra/README.md` states those read/write boundaries and warns against choosing project storage.

Current run documentation does contain machine-specific absolute example paths (PRR-006), and per-script compatibility statements span Ghidra 10.x, 11.x, and a confirmed 12.1.2 compile without a single matrix (PRR-005/010). No CI is necessary solely for these environment-dependent Ghidra scripts, but a clean-room compile/live test against the documented supported version should be part of any future script release claim.

The committed experiment notes contain summarized x64dbg observations rather than raw trace/session files. Raw traces found locally are correctly ignored.

## Privacy and Secrets

No secrets or credentials were found in `HEAD`. No secrets or credentials were found in reachable Git history.

No unintended personal email, real-name path, phone/address data, machine name, private organization, personal cloud-storage path, or Windows user-profile name was found. The visible author identity is the chosen GitHub identity and noreply address. The `D:` paths disclose project/tool directory organization but not a personal username; they are portability findings, not privacy blockers. `E:\BuildAgent\...` strings are extracted Bethesda build-path evidence and fall under PRR-002 rather than author privacy.

## Licensing

No license is present.

Before publication the owner should make separate, conscious decisions for:

- original Java scripts and any other original code;
- original documentation and research prose; and
- third-party/game-derived CSV and native-code evidence.

A conventional software license may suit the scripts, while documentation may use the same license or a documentation/content license. Neither automatically resolves rights in Bethesda-derived material. The eventual README/license notice should make those boundaries explicit. This audit intentionally does not select a license.

## Documentation, Navigation, and Fresh-Reader Test

Within five minutes, a Starfield-modding reader can identify the research question, recovered result, confidence-label system, baseline document, CK-versus-retail boundary, and sibling-repository division. The strongest public-facing material is the scoped README status plus `docs/v1-research-baseline.md`.

The top likely points of confusion are:

1. the README contains paths as code text rather than links, so even the recommended starting document and sibling repo require manual navigation;
2. the layout omits `data/`, evidence bundles, and implementation briefs while listing an empty/untracked `tools/` directory;
3. dataset names and schemas look canonical here even though the reproducer owns newer canonical inputs and exporter scripts;
4. implementation briefs look like current instructions unless the reader already knows that they are historical task specifications;
5. exact game/Creation Kit build provenance is not centralized, limiting address-sensitive reproduction.

The evidence-label sample found no obvious current scientific contradiction. Superseded static trails are prominently marked and remain valuable research history. No broad rewriting or deletion is warranted.

Markdown-link inspection found no broken relative links or private `file:` links because the tracked Markdown currently contains no standard Markdown links at all. Critical internal and cross-repository links should be added as part of PRR-004.

## Reproducibility

The following evidence paths are reproducible in principle with legitimately obtained external inputs:

| Evidence path | External requirements | Current documentation quality |
|---|---|---|
| Ghidra static exports | Creation Kit/Starfield executable, Ghidra, completed analysis, repository scripts | Strong procedure/read-only documentation; exact target-build record and unified Ghidra support matrix missing |
| x64dbg live observations | Creation Kit, x64dbg, target build, breakpoints/addresses, scenario setup | Summaries and addresses preserved; raw traces are correctly private; exact build and repeatable setup are incomplete |
| xEdit data extraction | Starfield/plugin data, xEdit, exporter scripts | Semantics are documented in the sibling reproducer, but this repo neither contains nor directly links those exporters/provenance docs |
| Executable-model validation | Sibling reproducer plus its canonical datasets/tests | Ownership boundary is clear in prose; direct link and exact validation command/version are missing here |

Redistributing proprietary binaries is not required or recommended. Build hashes, version strings, tool versions, commands, and expected result summaries are sufficient publication-safe provenance.

## Third-Party Attribution and Affiliation

No copied third-party source snippet or external dependency requiring a new attribution was identified in the repository scripts. The scripts import Ghidra APIs and its bundled Gson as platform facilities. Ghidra, xEdit, and x64dbg are material tools and should be acknowledged with project links as practical provenance, whether or not a license obligation applies.

The project should add a short notice that Starfield and related marks/content belong to their respective owner and that this unofficial research project is not affiliated with or endorsed by Bethesda. Avoid a long legal disclaimer.

## AGENTS.md, Briefs, and Experiments

`AGENTS.md` is acceptable to publish as maintainer/AI-agent guidance. It contains no secret or personal path and accurately preserves the evidence/status discipline. The README need not foreground it, though a small contributor note may identify its role.

The 19 tracked implementation briefs contain useful historical rationale and no detected credential/private-conversation residue. They do contain transient task language and one workspace path. Keep them if desired, but index and frame them as non-authoritative historical specifications. The user-supplied release-audit brief was untracked before this audit and is not treated as committed repository history.

Experiment records consistently mark static-only, live, provisional, and superseded work. Referenced raw local traces are not public, which is acceptable, but exact target build and repeatable observation setup should be improved. The checked-in evidence bundles are the subject of PRR-002 rather than an automatic deletion recommendation.

## Public-Safe File Inventory

### Safe to publish as-is

- original Ghidra Java scripts, subject to the pending license choice;
- `AGENTS.md` and the core baseline/facts/hypotheses/function-register prose;
- experiment narrative notes and `exports/.gitkeep`;
- `.gitignore` in its present protective role, though PRR-007 should improve it.

### Safe but should be better documented

- `README.md`;
- `ghidra/README.md`;
- `docs/implementation-briefs/`;
- Ghidra/evidence run procedures that use local absolute paths.

### Requires human/legal review

- `data/*.csv`;
- `docs/experiments/evidence/**` native decompiler, instruction, and string/data-reference exports.

### Must not be public

No tracked or historically committed file was conclusively placed in this category. The following untracked/ignored local material must not be swept into a commit or release artifact without separate review:

- `.local-work/trace64/**` raw debugger traces and transfer archives;
- `scratch/StarfieldCKCaptureProject/**` Ghidra project/database content;
- generated `exports/**` archives and bulk decompiler exports.

## Suggested Remediation Sequence

1. Decide PRR-001 and PRR-002 with the repository owner and, where warranted, legal counsel. Record approval scope and provenance.
2. If any blocked content is rejected, write a separate history-rewrite plan, remove the material from all refs, verify a fresh clone, and rotate nothing unless a later secret finding requires it.
3. Choose and add licensing/notices with explicit treatment of code, prose, data, and game-derived evidence.
4. Add centralized build/tool/data provenance, including exact CK/game/plugin versions or hashes and extraction-to-evidence mappings.
5. Repair README navigation/layout, link the sibling repo, explain datasets/evidence/history, add counterexample guidance, and include a brief unofficial-project notice.
6. Add a docs index that frames implementation briefs and superseded experiments.
7. Replace active absolute-path examples and strengthen narrowly scoped ignore rules.
8. Review GitHub description/homepage/topics/archive/default-branch settings; reciprocally link the sibling repo when it is public.
9. Re-run the release checklist from a fresh clone immediately before changing visibility.

## Release Checklist

- [ ] PRR-001 game-derived datasets approved for publication, or removed from all reachable history.
- [ ] PRR-002 native-code evidence approved for publication, or removed from all reachable history.
- [ ] License/content notices added after an explicit owner decision.
- [ ] Exact CK/game/plugin/tool provenance recorded.
- [ ] README layout, navigation, data explanation, cross-link, counterexample path, and non-affiliation notice corrected.
- [ ] Historical briefs/experiments indexed and framed.
- [ ] Active local paths made portable and `.gitignore` strengthened.
- [ ] `git status` shows only intended release changes.
- [ ] High-confidence secret/privacy patterns re-scanned in `HEAD` and all refs without printing values.
- [ ] Historical filenames/extensions and largest blobs re-inventoried.
- [ ] Confirm no `.exe`, `.dll`, `.pdb`, `.gpr`, `.rep`, `.dmp`, `.trace64`, debugger database, archive, or imported analysis database is tracked or reachable.
- [ ] Verify Markdown links, UTF-8/mojibake scan, `git diff --check`, and a fresh clone.
- [ ] Verify GitHub description/homepage/topics/default branch/archived state and confirm visibility remains private until all blockers are closed.
- [ ] Do not create a tag or GitHub Release merely to publish the research repository.

## Audit Actions and Non-Actions

This audit created only this report. It did not modify research conclusions, evidence classifications, datasets, scripts, `.gitignore`, README, repository settings, visibility, Git history, tags, releases, commits, or remotes. No credential was rotated, and nothing was pushed.
