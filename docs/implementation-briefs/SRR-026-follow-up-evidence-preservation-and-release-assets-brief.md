# SRR-026 follow-up — Durable evidence preservation and release assets

**Project:** `D:\Projects\starfield-resource-research` (`gooberpede/starfield-resource-research`)  
**Task type:** Bounded correction to SRR-026 release planning; **not** a new scientific investigation or release authorization  
**Proposed release:** `v1.0.0-sf1.16.244.0` — retail `Starfield.exe` and `CreationKit.exe` both pinned at `1.16.244.0`  
**Status:** Implementation brief; all changes require review before commit

## 1. Why this follow-up is necessary

SRR-026 established the proposed composite version, the separately pinned and publicly obtainable `starfield-resource-reproducer` exception, and clean-checkout portability. Those conclusions stand. Its **source-only release / zero manual uploads** assumption is withdrawn: it does not provide durable custody of unique evidence held in `.local-work/` or elsewhere on the local D: drive. That material may be deleted to recover disk space, and GitHub may ultimately be the only accessible record.

**Objective:** Plan complete, verified, long-term preservation of scientifically significant research artifacts, distinguish public release assets from material requiring private custody, and update the release candidate accordingly. **The intended end state is that deletion of the local project, including `.local-work/`, does not destroy unique research evidence.** Merely documenting a local filename, digest, or a proposed upload is not proof of durable preservation.

**Do not** revisit the generation algorithm, replay SRR-026's established portability work except to validate changed instructions, change the reproducer carve-out, or alter the proposed tag.

## 2. Inventory and custody reconciliation

Inventory the **actual existing files**, not only files already labeled `release-assets`. Examine at least:

- `.local-work/release-assets/`, including SRR-017/018 native capture archives and compact exports, SRR-021 original Save2 screenshots/manifest, and SRR-022 original Save2/Save52 saves;
- selected unique material under `.local-work/codex/`, `.local-work/independent-review/`, `.local-work/diffs/` and historical experiment/output locations, where scientific claims depend on original observations or receipts;
- tracked evidence bundles and historical archives, to distinguish already Git-preserved bytes from untracked originals;
- other **known, evidence-specific locations** referenced by `docs/PROVENANCE.md`, `docs/allocation-validation.md`, `docs/retail-execution-lifecycle.md`, `docs/component-database.md`, and tool READMEs. Search referenced roots and provenance records, not the entire drive indiscriminately.

For every candidate retained artifact, record the **actual observed path**, origin, bytes, SHA-256, format, relevant investigation/claim or consumer, sensitivity/rights status, whether Git already retains the exact content, and whether another verified durable copy exists. Preserve original bytes and evidence IDs. Deduplicate by content without losing aliases, provenance or capture ordering. Identify absent/referenced-but-not-found material explicitly: **do not claim custody based on old manifests alone**. Reconcile prior hashes and retained manifests rather than overwriting them. Where source-versus-copy equality is asserted, actually verify it.

Classify each item as: **(A)** unique essential primary evidence, **(B)** valuable historical record or audit receipt, **(C)** deterministically rebuildable output with a verified reproduction route, **(D)** tracked/otherwise durably preserved exact content, or **(E)** disposable duplicate/scratch. Classification must include a rationale and a dependency check: a supposedly rebuildable item is not rebuildable if it needs an unretained historical state. Do not delete anything as part of classification.

## 3. Publication and private-preservation distinction

Evaluate each candidate independently; do not treat the name `.local-work` as a reason to exclude it from release, nor presume that preservation need implies redistribution permission.

For each proposed public package, state the rights basis and any outstanding clearance for embedded Bethesda-derived data, binary excerpts, screenshots, save files, player-specific data, third-party material or private configuration. A repository license does not grant rights to proprietary game content. Inspect for credentials, account identifiers and unnecessary personal metadata. **Do not invent authorization or silently redact original evidence.** If a public derivative is justified, preserve its relationship to the unmodified primary original; distinguish what it can and cannot verify.

Assign every **unique retained** artifact exactly one disposition:

1. **Already durable in Git:** exact content and commit/path identified, with inclusion in the proposed source release verified;
2. **Proposed public GitHub release asset:** identified package, included members, hashes, size and clearance status, with actual upload pending explicit approval;
3. **Requires separate durable private preservation:** contents cannot appropriately be public; define an actionable, verifiable private storage destination and procedure, but **do not claim it exists or is backed up until independently confirmed**;
4. **Rebuildable / not needed to retain:** demonstrate a reproducible route whose source inputs themselves have durable dispositions;
5. **Hold / unresolved:** missing, rights-unclear, unsized, or no adequate destination. Name the exact blocker and prevent declaring preservation complete.

Save2, Save52, Steam screenshots and raw native acquisition material must be assessed specifically, not excluded wholesale. Do not publish proprietary executables, BA2 archives, plugin payloads, unapproved saves or other material merely to satisfy a preservation target.

## 4. Proposed immutable release packages

Propose a **small, coherent set of immutable evidence packages** where justified; preserve existing acquisition boundaries rather than indiscriminately bundling all `.local-work`. For each package specify: stable artifact name including research/game version where useful; content purpose; member inventory and logical paths; original per-file SHA-256; archive SHA-256 and size once built; source/custody chain; public/private designation; rights holds; and research claims depending on it.

Prefer packaging and hashing from unchanged source bytes, with a machine-readable manifest and readable index. If archives are built in this task, ensure reproducible member listing, lossless extraction and hash verification; avoid unexplained transformations. Archive assembly **does not authorize upload**. Preserve the original sources and any existing acquisition ZIPs. Distinguish generated source archives from manual evidence assets: **zero manual assets is no longer a predetermined outcome**.

Assess GitHub release size/file constraints and the feasibility of each proposed asset using current documented limits or actual tool-visible constraints. If a package is too large, propose splitting or a separate durable destination rather than omitting its contents. No Git LFS or new external storage service should become a requirement without explicit maintainer approval.

## 5. Publication and disaster-recovery procedure

Update the proposed release candidate and relevant workflow documentation to explain:

- which scientific claims are reproducible from public source and lawful versioned external inputs, and which depend on custody-backed observations;
- which evidence packages should accompany `v1.0.0-sf1.16.244.0`, what remains privately retained or on hold, and what users may independently inspect;
- the **future** authorized upload sequence: calculate final hashes, upload each approved asset, retrieve it independently, verify bytes/member hashes, and reconcile the final release manifest;
- an explicit **deletion-readiness gate**: every irreplaceable artifact must have a verified surviving durable copy, including private artifacts, with a second independent backup recommended for especially irreplaceable data. A pending upload, local archive or mere SHA-256 record does **not** satisfy this gate.

Keep repository documentation portable: machine-specific paths may be described as historical origins but not as required entrypoints. Maintain the companion reproducer at the exact pinned commit `a8ff1c788bca415f571f06769ab3e712fa674f75` and the existing executable/provenance qualifications. Do not overstate older live-session build attribution.

## 6. Execution boundaries and workflow

- **Up to three concurrent sub-agents:** (A) evidence/custody inventory; (B) rights/privacy and release-package design; (C) independent dependency/rebuildability and disaster-recovery validation. Parent integrates findings; commission a **separate independent challenger** afterward, following `docs/research-workflow.md`.
- Offline and read-only research inspection. Bounded local manifest/package creation and documentation edits are permitted, subject to the project's existing free-space rule and protected-input verification. **No file deletions, Git history rewrites, cleanup of existing private material, game runs, debugger attachment, save changes, external upload, GitHub release, tag, commit or push.** Read-only external lookup of GitHub limits/licensing facts is permissible where needed; do not fetch unrelated private sources.
- Honor pre-existing HEAD/index/worktree state and preserve the existing SRR-026 changes. Keep any new private manifests, trial archives, receipts and inventories under existing ignored `.local-work/` conventions. Do not add unreviewed large evidence archives to Git.
- Modify existing `docs/release-candidate.md`, `docs/release-workflows.md`, `docs/release-smoke-tests.md`, `docs/PROVENANCE.md` or other authoritative documents **only where necessary**. A concise, durable *release evidence inventory/asset plan* may be added if it is genuinely needed; avoid duplicating historical scientific narratives or creating an additional lead register.
- Produce task-only diff and changed-path inventory; record checksums, exact holds and end status; keep changes **unstaged and uncommitted**. Independent challenger checks claims against actual source bytes, member inventories, cross-document links, privacy/rights judgments, and byte-exact patch replay against starting content. Do not describe an independently untested upload as verified.

## 7. Acceptance criteria and handoff

The follow-up is COMPLETE only if:

1. The evidence-specific inventory accounts for known scientifically significant **tracked and untracked** assets, resolves or explicitly flags absent source files, and verifies actual bytes and identities for material on hand.
2. Every unique retained asset has a justified preservation and distribution disposition, including Save2, Save52, screenshot originals and native captures; no loss-prone local-only custody is silently counted as durable.
3. The proposed release asset packages have explicit content, provenance, verification instructions and rights/privacy gates; public release and private backup remain separate.
4. The revised release manifest withdraws the source-only/zero-manual-upload presumption, preserves the composite version and reproducer exception, and states the post-upload retrieval and deletion-readiness gates.
5. The original SRR-026 portability conclusions and reproducible commands remain valid, or any necessary change is specifically retested. No unauthorized upload, publication, deletion or commit occurs.
6. An independent challenger has reviewed the final substantive snapshot, and the task-only diff replays byte-for-byte with a verified ending index/worktree state.

**A complete preservation *plan* is not equivalent to completed remote preservation.** If public redistribution clearance, private durable destination or uploads are still pending, mark those as explicit **publication/preservation holds** while the bounded planning task itself may be COMPLETE. The maintainer decides which assets to publish and separately authorizes uploads, private archival transfers and any deletion of local sources.

**Suggested commit message (only after maintainer review):** `docs(release): plan durable evidence assets and preservation gates`
