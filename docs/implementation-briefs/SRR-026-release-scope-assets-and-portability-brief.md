# SRR-026 — Release Scope, Assets and Portability

**Project:** `starfield-resource-research`  
**Type:** Implementation and release-readiness investigation (not release authorization)  
**Proposed first release:** `v1.0.0-sf1.16.244.0`  
**Status on issue:** Proposed; no Git tag, GitHub Release, version declaration or publication is authorized until independently reviewed and approved by the maintainer.

## Purpose and decision framework

Prepare the research repository for a self-contained, reproducible, version-pinned public release **within the boundaries confirmed by SRR-025**. Establish exactly which source, documents, tools, and optional derived artifacts belong to the release, and remove avoidable dependencies on the maintainer's local environment. The **sole explicit cross-project carve-out** is the public `starfield-resource-reproducer` repository, referenced at an immutable commit or independently obtainable tagged release; do not duplicate its maintained model/data merely to achieve nominal independence.

Keep this work distinct from the planned follow-ups: **SRR-027** assesses glossary, diagrams, pseudocode and navigation; **SRR-028** archives completed briefs and historical audits. SRR-026 may flag issues for those tasks, but must not preemptively perform either broad documentation rewriting or archive housekeeping.

## Pinned release identity

Confirm the current `docs/PROVENANCE.md` entries and any installed files used for verification before recording the version contract. The present evidence identifies:

| Role | File/product version | SHA-256 |
| --- | --- | --- |
| Retail game — `Starfield.exe` | `1.16.244.0` | `7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28` |
| Creation Kit — `CreationKit.exe` | `1.16.244.0` | `ed54e4906bc13b0fbc43ec7624fec4af2389a9a1e12b2789d73c5617f5a14020` |

**Proposed tag:** `v1.0.0-sf1.16.244.0` (research semver plus game version). The same suffix suffices for this release because the *verified* CK and retail file versions match. Do not assume future CK/game alignment: if later verified versions differ, explicitly identify each in the future composite release identifier (e.g. `v1.1.0-sf1.17.100.0-ck1.17.90.0`). Increment the research version according to research/release change scope, not automatically according to a Bethesda update.

Make the pinned **game and CK versions**, identities and applicability visible in the root README, proposed release notes and manifest, with `docs/PROVENANCE.md` as the detailed authority. Distinguish verified executable identity from historical CK live sessions, retail screenshots and scans without trace-specific fingerprints; do **not** retroactively claim that those sessions ran on the pinned build. Distinguish the **v1.0 generation model** from the proposed **v1.0.0 repository release**. An update to Bethesda software does not change the historical validity of the tagged release or automatically extend it to new bytes; a later supported version needs revalidation and a new composite tag.

## Workstreams

### A. Release surface, asset inventory and version contract

1. Inventory candidate distributable artifacts in the **tracked repository**: authoritative subjects, provenance, glossary, current offline tools, relevant manifests, tests and public-safe evidence, and any legitimately redistributable summary/derived data. Identify redundant or historical-only tools without silently deleting them.
2. For each proposed GitHub release asset, record its exact origin/build command, named consumer, content hash once built, dependencies, source/licensing/redistribution status, and whether it is **required**, **optional** or **excluded**. Distinguish assets accompanying a release from the GitHub-generated source archives and from private scientific custody records.
3. Explicitly exclude by default: Bethesda executables/archives and third-party proprietary payloads; saves (including Save2/Save52); personal gameplay screenshots; raw private captures, observer journals, private `.local-work/` material, and other unreviewed assets. Evidence may support a tracked conclusion without itself being redistributable. Do not put private data or a recipe to reconstruct restricted assets in a public distribution.
4. Propose a *minimal*, justified asset set. Do not create a large bundle by default or publish a raw 3,211-row native capture merely because it exists. Any derived dataset proposed for publication requires a separate rights/provenance assessment; hold it if its clearance is uncertain.
5. Produce a prospective release name, concise draft release notes and manifest. Record the exact pinned companion reproducer commit/tag used for any validation; do not invent an upstream release or use a mutable branch reference as the release contract. Leave release number, Git tag and asset upload for maintainer approval.

### B. Independence and clean-checkout portability

1. Enumerate **supported, current** workflows from README/tool catalog and the SRR-025 readiness audit. Identify every needed executable, import, Python package, schema, configuration, CSV, environment variable and ancillary script; distinguish current operator methods from historical experiments and private acquisition receipts.
2. Trace any dependencies on absolute machine paths (`D:\\Projects\\…`, `C:\\…`), `.local-work/`, user-specific Steam directories, local sibling checkouts, undocumented environment setup, cached outputs or files from other projects (especially the outpost project). Historical evidence may cite its original path as provenance; a **current procedure** must not silently depend on that path.
3. **Allowed exception:** the distinct public `starfield-resource-reproducer` project, obtained from an explicitly pinned, accessible revision via a documented clean-checkout procedure. This exception does not authorize accessing the maintainer's sibling checkout or silently importing unversioned working files. Prefer the model and data from the designated reproducer without copying their sources into this repository.
4. A user may need to acquire matching proprietary game/CK binaries and installed UI archives **lawfully** for certain verification tasks. Declare these as external, user-supplied, identity-checked prerequisites. They are not distributable assets or local-repo dependencies. Workflows which do not need them should not require them.
5. Repair concrete portability problems **within this repository** when bounded and uncontroversial (relative imports, parameterized input paths, checked-in small public schemas/scripts, explicit dependencies, reproducible commands, path-independent defaults). Preserve established evidence semantics. If fixing a problem requires moving ownership between repositories, copying substantive reproducer source/data, changing the public scientific claim, large tooling refactoring or a new external service, record the issue and proposed decision instead of doing it unilaterally.
6. Test representative supported workflows from a **fresh clone/export in a new independent location**, without `PYTHONPATH`/working-directory accidents, access to `.local-work/`, unrelated repositories, or an already-present sibling checkout. Obtain the pinned reproducer *separately* for workflows that require it. Require actual smoke-test receipts (commands, environment, exact inputs, hashes, exits, outputs). Distinguish a clean checkout's public reproducibility from historical custody-backed observations not re-creatable without private input. If rights or resources prohibit acquisition of a lawful proprietary input, test independently what can be tested and identify precisely what is unexercised; never substitute a private input unnoticed.
7. Verify workflows on supported Windows/PowerShell where applicable; ensure Python usage and dependencies are explicit and reasonably platform-independent when they claim to be. Do not add platform claims without testing.

### C. Release readiness and handoff

1. Check README, `docs/README.md`, `docs/PROVENANCE.md`, `THIRD_PARTY_NOTICES.md`, `LICENSE`, tooling entrypoints and existing publication rules for internally consistent version, rights and dependency statements. Do not dilute the `0/3,211` strictly admitted native-oracle bound or the `22,470` diagnostic slot agreements. No claim of exact CK/retail instruction equivalence, game-build universality, or outpost-scale deposit placement.
2. Produce a compact release-asset/portability report and list **release blockers versus nonblocking limitations**, with an owner and precise remedy for each. Include a candidate release manifest and reproducible artifact-generation/checksum commands. Avoid introducing a new numbered scientific dossier or duplicate lead register; use existing release/readiness/audit conventions or a small specifically scoped release-planning record where needed.
3. Explicitly distinguish completed SRR-026 remediations from work deferred to SRR-027 (technical documentation sufficiency), SRR-028 (archive housekeeping) and final release-candidate verification. The final release verdict remains **provisional** pending those tasks.

## Execution limits and project conventions

- Confirm starting HEAD, index/worktree, installed source identities and pre-existing untracked material. Read `AGENTS.md`, `docs/research-workflow.md`, SRR-025 audit and existing tool documentation before changes. Use the existing `.local-work/codex/SRR-026/`, `.local-work/diffs/` and independent-review conventions; do not modify previous task receipts.
- **Up to three concurrent sub-agents** may examine (A) version/assets/rights, (B) portability/dependencies, and (C) independent clean-checkout verification/alternative failure modes. Integrate centrally, then engage a **separate independent challenger** after integration. The reviewer must test the strongest portability and release claims, not merely check formatting.
- Respect the workflow's C: and D: available-space safeguards before material writes; do not fetch or install new dependencies, obtain credentials, use paid services or change global workstation configuration without explicit authority. Test with already available lawful files where possible; identify unavailable external prerequisites explicitly.
- Offline and read-only with respect to Starfield, CK, Ghidra projects, save files, private primary evidence and the companion reproducer. No live gameplay, debugger, instrumentation or modifications to game inputs. Work only in this repository and disposable clean-checkout/test directories; do not edit the companion repo.
- Preserve provenance and scientific claims. Do not modify the generation algorithm, regenerate native evidence as if it were a historical observation, create new research leads or reopen SRR-025 closure merely to remove documentation imperfections.
- **No tag creation, GitHub release creation, public distribution, commit, push or staging.** Provide the exact proposed commands for later authorized publication, but do not execute publication actions.

## Acceptance criteria

SRR-026 is complete when:

1. The release/version contract explicitly names both verified executable versions/hashes, the proposed composite tag and the historical-evidence caveats, with a future divergent-CK-version rule.
2. Every proposed downloadable release asset has a justifiable audience, source/build/reproduction method and rights disposition; private or proprietary inputs are excluded unless separately cleared. The manifest is concrete enough for final packaging, not an assertion that publication has occurred.
3. All **current supported workflows** are inventoried for dependencies and local-only assumptions. The one pinned reproducer carve-out is explicit; no other implicit project dependency is accepted. Bounded defects have been fixed or reported with specific release-blocker status.
4. Representative reproducibility and portability checks have been executed from an isolated clean checkout with a separately obtained pinned reproducer where required. Actual run receipts and honest gaps are recorded; the audit does not claim that privately held evidence is reconstructible from the public repository.
5. Documentation changes are limited to relevant release/version/portability surfaces. SRR-027/028 work is not preempted. Existing version, validation, provenance and rights boundaries are retained.
6. Independent challenger verifies the task-only Git patch against initial HEAD, checks its substantive claims/receipts and gives COMPLETE, REWORK or BLOCKED with limitations. All edits remain unstaged and uncommitted for maintainer review.

## Handoff

Return: proposed release tag/title; release asset manifest and rights/hold classifications; exact reproducer pin and clean-setup procedure; inventory of portable workflows and tested results; changes by path; blockers/deferrals to SRR-027, SRR-028 or final verification; final independent-review receipt; task-only diff with byte-exact replay; ending HEAD/index/status; proposed commit message. Do not claim that `v1.0.0-sf1.16.244.0` exists until the maintainer authorizes creation.
