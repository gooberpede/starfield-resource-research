# SRR-026 continuation — Claim-based release evidence selection and Save2/Save52 assessment

**Project:** `starfield-resource-research`  
**Proposed release:** `v1.0.0-sf1.16.244.0` (pinned `Starfield.exe` and `CreationKit.exe` version `1.16.244.0`)  
**Type:** Corrective, bounded continuation of SRR-026 release planning; not a new research investigation  
**Authority:** Offline inspection and documentation changes only. No uploads, commits, tags, release publication, save modification, deletion, or disclosure of private files.

## 1. Purpose and governing decision

Correct the SRR-026 preservation follow-up's overbroad premise that all unique artifacts in `.local-work/` must be kept in durable off-host storage. The intended release must let a technically competent researcher **understand, independently evaluate, and where feasible reproduce the findings**, using the repository, selected released evidence, the explicitly pinned public `starfield-resource-reproducer` companion and independently obtained lawful proprietary inputs.

An artifact's uniqueness is **not by itself** a reason to distribute or preserve it. Determine the *minimum sufficient evidentiary package* by tracing the principal published claims to their independent verification or reproduction routes. A historical observation need not be exactly replayable when its essential evidence and limitations are available. No release requirement to preserve the entire local project, Ghidra database, decompilation output, exploratory scratch, failed trials, or all 2,135 inventory hashes. Treat the previous large private custody catalog as an informative inventory, **not** a release gate or default distribution manifest.

**Explicit exception:** Treat the original **Save2 and Save52** files as strong candidates for inclusion *in full* as release assets, subject to individual clearance. They cannot usefully be trimmed into claim-specific save segments; Save2 is relied upon repeatedly in documented findings and gameplay observations, and Save52 represents extensive historical gameplay that is impractical to recreate. Do **not** substitute only the decoded SRR-022 datasets for the originals without examining this rationale. Nor should this become a precedent to release every historical save. The default proposal should be **both complete saves**, unless a specific identified privacy, rights, safety or integrity objection requires an explicit maintainer decision.

Keep the previous SRR-026 portability verification, companion carve-out, game/CK version pins, and proposed composite tag unchanged unless a direct contradiction is demonstrated.

## 2. Inputs and baseline

- Start from current working tree, record HEAD, index/worktree state, pre-existing changes and the exact earlier SRR-026 artifacts. **Do not overwrite or lose** pending SRR-026 release work. The original SRR-026 patch and preservation continuation may be uncommitted: treat the actual worktree as the baseline, separately accounting for each pre-existing change.
- Read `docs/release-candidate.md`, `docs/release-public-evidence.md`, `docs/release-workflows.md`, `docs/release-smoke-tests.md`, `docs/PROVENANCE.md`, `docs/allocation-validation.md`, `docs/component-database.md`, `docs/v1-research-baseline.md`, `docs/retail-execution-lifecycle.md`, `docs/research-workflow.md`, `docs/hypotheses.md` and relevant tool READMEs. Use the existing 2,135-hash local inventory and custody catalog as **discovery aids**; do not rebuild a comprehensive inventory merely to repeat it.
- Verify source identities and custody for Save2 and Save52 against the SRR-022 records, and for selected non-save evidence against its existing manifest. The actual local data and catalog are private inputs; don't incorporate their raw bytes into tracked files while preparing the plan.
- Work within the repository's established free-space, evidence-integrity, private scratch and review conventions. Do not infer a complete corpus from `.local-work/` alone where relevant existing evidence is already tracked or in declared external sources.

## 3. Workstream A — Claims → evidence → release decision

Create a **compact claim-to-evidence matrix** for the major public scientific conclusions, not every experimental subclaim. At minimum cover:

1. CK-derived inorganic generation algorithm and main branching/RNG rules;
2. canonical membership results and ten independent holdouts;
3. retail retained `CTPerBiomeData` census, seven-lane observations and the SRR-018 diagnostic comparison, **without promoting zero strict oracle admissions**;
4. component database and allocator lifecycle findings where they depend on specific observations rather than inspectable native code;
5. `PlayerKnowledge` state and SRR-022 Save2/Save52 serialization comparison;
6. survey UI / Kreet Neon and Volii Alpha observations, including original screenshots where necessary.

For each claim record: authoritative document and scope, existing evidence ID, verification route (**re-run code on lawful inputs**, **inspect already tracked evidence**, **inspect selected released historical observation**, or **qualified historical result with unobtainable original**), precise indispensable artifact(s), reproduction prerequisites, rights/privacy decision, and remaining limitation. Distinguish raw primary capture, selected meaningful derivative, reproducible output and disposable intermediates.

Evaluate candidates by this test: *Would absence of the artifact materially prevent an independent reader from reproducing the method, verifying the result, or fairly evaluating the evidence supporting the published claim?* Prefer smaller selected datasets/manifests over indiscriminate raw journals when sufficient. Do not require distribution of Ghidra-decompiled exports or entire Ghidra projects if version-pinned lawful inputs, native locators and the documented methods allow independent retrieval. Likewise do not make proprietary game/CK executables, BA2 archives or plugin payloads release assets. Record genuinely unrepeatable historical acquisition and provenance limitations rather than manufacturing a guarantee.

Use the result to classify a deliberately limited final asset set: (a) tracked-source-contained, (b) manually published supplemental evidence, (c) lawful external prerequisite, (d) cited historical evidence with acknowledged custody/availability limitation, (e) omitted as nonessential. **A nonessential private artifact is not a release blocker**, even if it cannot be recovered after local deletion. Do not represent GitHub as a guarantee of permanent backup.

## 4. Workstream B — Whole-save release candidates

Assess **Save2 and Save52 individually and in full**, retaining the exact original bytes, filenames, lengths, SHA-256 and existing custody provenance. Provide a proposed asset name/package format and integrity manifest, potentially bundling both in one clearly named ZIP or separately, with a rationale for discoverability, size, ease of individual retrieval and version attribution.

Perform a bounded, proportionate **pre-publication clearance review** without modifying the originals. Review what is actually embedded in these save files and accompanying metadata where reasonably inspectable, with attention to: player/character/profile names, identifiers, machine paths, account-linked names, mod/plugin lists, custom or user-created content, third-party content, personal text, hidden metadata and embedded data that a public recipient could recover. Clearly separate **demonstrated contents** from plausible but uninspected risks. Consult existing source/Steam metadata and save-decoder knowledge; a complete semantic decode of unrelated save units is **not** a prerequisite. Avoid exposing discovered personal identifiers or private information in tracked documentation or review summaries; describe concerns by category, private receipt and concrete action.

Review applicable sharing/redistribution considerations; distinguish Bethesda proprietary assets referenced by FormID from any proprietary payload actually embedded in the save. Do not assert clearance solely because files were created through gameplay. **No public distribution is approved by this brief.** For each save propose one of: `CANDIDATE_PENDING_MAINTAINER_CLEARANCE`, `REQUIRES_SPECIFIC_REMEDIATION_OR_CONSENT`, or `HOLD_WITH_REASON`. If clearance cannot responsibly be established offline, identify the exact decision or bounded additional check needed. Preserve both complete originals privately until the maintainer decides; never sanitize by overwriting or destructively transforming them. Any proposed redacted derivative would be a *separate* artifact and cannot be silently substituted for the whole save.

Link Save2 and Save52 to their exact SRR-022 and gameplay evidentiary roles. Their high scientific value and limited substitutability should weigh in the selection decision. If either is ultimately withheld, document honestly which historical results remain reproducible via method and which can only be evaluated through derivatives; do not demand deletion or rewriting of established scientific findings as a routine workaround.

## 5. Workstream C — Release manifest and recovery procedure

Update `docs/release-candidate.md` and `docs/release-public-evidence.md` to implement the corrected policy. Retain the previous 2,135-item private inventory only as optional historical/custody context, clearly **not** the list of required release files. Remove whole-corpus archival, private 9.83 GB object-store creation, off-host restore of all identified hashes, and "safe deletion of D: project" as mandatory release gates. A targeted off-host checksum verification remains appropriate **for assets actually chosen for release**, after publication is separately authorized.

Produce the proposed asset inventory with exact bytes/hash where an artifact is already built, or an explicitly labeled **planned/unbuilt** asset where it is not. Do not invent finished archives, upload URLs or measured checksums. For each asset give purpose, authoritative evidence consumer, source identity, expected contents, package regeneration steps where feasible, rights/privacy disposition and whether source-only archives already cover it. In particular revisit the prior **single 4,898-byte comparison ZIP** conclusion in light of the essential historical census, Save2/Save52 and screenshot evidence. An asset need not be maximally compressed; prioritize scientific sufficiency and inspectability.

Document a straightforward future publication check: verify package hashes, inspect contents against intended inclusion/exclusion and permissions, explicitly approve uploads, upload the selected assets, download/verify the published bytes independently and retain provenance. This check covers **selected release assets only**, not all working files. Keep `v1.0.0-sf1.16.244.0`, independently pinned `Starfield.exe`/`CreationKit.exe` 1.16.244.0 SHA-256, and the one declared `starfield-resource-reproducer` dependency. Retain pending SRR-027 documentation, SRR-028 archiving, final rights/source-tree review and maintainer publication approval as gates. Do not change release labels or Git tags.

## 6. Parallelism, documentation and constraints

Up to **three concurrent sub-agents** may be used: A, claim/evidence sufficiency; B, Save2/Save52 assessment; C, release manifest and publication procedure. The integrator reconciles their conclusions and commissions a **separate independent challenger after integration**. Reuse the existing private input manifests, custody reports and verification tools; avoid new archiving frameworks or broad exploratory code unless essential to a specific release decision.

Prefer editing the two release documents identified above. Other documentation may change only when necessary to resolve a concrete contradiction. Do not create another numbered research dossier, duplicate lead register, or independent rights-policy framework. The current scientific baseline and reproducer remain unchanged. No live game, debugger, save editing, new acquisition, public network access, new external storage, upload, Git commit/tag/push, publication, deletion or cleanup of unique evidence without separate authorization. Do not archive completed briefs in this task; defer to SRR-028.

Review rights/redistribution classifications conservatively, without conflating uncertain legal status with scientific non-reproducibility. Do not permit a blanket "publish nothing private" default to override claim-based selection; equally, do not publish any save or historical capture simply because it was useful.

## 7. Acceptance and handoff

The task is **COMPLETE** when:

1. A compact claim-to-evidence matrix covers all six claim groups, with defensible minimum-sufficient evidence selection and explicit reproduction limitations.
2. Both full saves receive distinct evidence-value and privacy/rights assessments, proposed package/asset identities, and clear **pending approval** dispositions; neither is silently excluded or published.
3. The release asset manifest is revised and distinguishes source-contained, public candidate, lawful external, historical-limited and omitted material. Any unbuilt packages or unresolved clearances are visibly labeled.
4. The previous whole-corpus preservation/deletion gate is removed as a **release acceptance requirement**, while selected-asset hash verification and publication approval remain.
5. Earlier SRR-026 portability/version work, prior local artifacts and historical scientific claims are protected.
6. A separate independent challenger checks the actual final diff, evidence selection, whole-save treatment, private-data leakage, patch integrity and original brief. Correct substantive findings and repeat review as needed.

Return the changed-path inventory, final task-only Git patch, private review receipt, verification summary and recommended commit message. Leave all changes **unstaged and uncommitted**. Do not claim release readiness or asset clearance where a specific review gate is still open. The maintainer will decide both individual save clearance and final publication.
