# SRR-009 — Publication Readiness and Durable Workflow Remediation

**Implementation brief for Codex**  
**Disposition:** Authorized, **offline repository and local-asset remediation only**  
**Repository:** `gooberpede/starfield-resource-research`  
**Starting point:** Existing uncommitted SRR-009 implementation, three Stage A attempts, qualified third-attempt `NOT_OBSERVED`, and independently reviewed administrative observer closure. **Do not commit or reset this work.**  
**Controlling question:** Can the published research claims and documented procedures be supported from versioned project sources, explicitly declared lawful external inputs, and accurately classified historical evidence, without hidden reliance on disposable `.local-work/` files or a sibling project checkout?

## 1. Authority, priorities and boundaries

This task implements the agreed publication-readiness audit findings and future-proofing rules **before the maintainer commits SRR-009**. Prioritize completing the practical remediation; do not broaden it into historical re-research or a repository reorganization.

1. Preserve the established science: **the four-site observer recorded qualified `NOT_OBSERVED` for focal entry and allocator arrival during two verified post-title windows totaling 84.281 seconds**. This does **not** cover startup before arming, game loading, or gameplay. The first two Stage A attempts were instrumentation-incomplete. In the third, Starfield exited normally; ordinary debugger retirement was unconfirmed, and the exact stranded observer was subsequently administratively terminated after the target's exit. Retain all primary observations, seals, original history and qualifications.
2. Work offline. **No Starfield or Steam launch, debugger attachment, process probing/control, save loading, Stage B, Ghidra mutation, new gameplay testing, forced process termination, or game configuration edits.** Read-only inspection of existing files, local copying of the explicitly authorized Save2 asset, offline build/test and fixture execution on disposable children are permitted within existing tool and safety rules. Do not alter or deploy runtime instrumentation.
3. Do not change `tools/srr006/` observer behavior or the established four observation sites in this task. If a real issue is uncovered, document it as a separate proposed follow-up rather than silently repairing the scientific instrument.
4. Do not modify originals, backups, or already-sealed evidence under any project. Existing `.local-work/` and independent-review material must not be deleted, reorganized or overwritten. The normal working-area conventions, protected-input hashing, UTF-8 checks, native Git patch export and free-space requirements of `AGENTS.md` and `docs/research-workflow.md` still apply. **Both C: and D: must retain at least 40,000,000,000 caller-available bytes after projected writes**, with appropriate headroom for temporary copies.
5. Leave work **unstaged, uncommitted and unpushed**. Release packaging, release tags, public release publication, and publication of Save2 require separate maintainer decisions.

## 2. Required authoritative inputs

Inspect the actual repository state, source and records rather than relying on this brief's summary:

- `AGENTS.md`, `docs/research-workflow.md`, `docs/README.md`, `docs/PROVENANCE.md`, `THIRD_PARTY_NOTICES.md`, `.gitignore`, `.gitattributes`, and the existing implementation-brief and audit archive conventions.
- SRR-001 through SRR-009 dossiers, with special attention to the current SRR-009 dossier, the SRR-008 survey and documented reproduction commands, the SRR-006/007/009 observer build/test chain, and the older SRR-002/003/005 local scripts.
- The completed **SRR-009 read-only publication audit** (`publication-audit/report.md`, `challenger.md`, start/end receipts and manifest) and the current SRR-009 scientific and observer-closure independent reviews and evidence pins.
- SRR-008 local helpers (notably `interactive/check-saves.py`, `interactive/environment.ps1`, `interactive/survey.py`, and any helpers they import or invoke), and their dependencies on `starfield-outpost-research`, particularly `save_policy.py`, `save_policy.json`, `environment.py`, `docs/SAVE_PROTECTION.md`, and the actual local private backup/policy data.
- The established **Save2/HIST-0245** identity: historical recorded byte length **2,475,440**, SHA-256 **`1ac3d496e532b6286d983a1449946ba4fe34a34e66295c9d1d7da677772903d1`**. These are expected identity checks, **not permission to substitute a similarly named file**. Verify the actual provenance and content before copying.

Record the exact starting HEAD, index and working-tree state and make the accumulated SRR-009 task-file set an explicit protected baseline. A task-only final diff must faithfully include the accumulated uncommitted SRR-009 files as applicable, not only the newly remediated files. Preserve current branch and working material.

## 3. Dependency inventory and proportionate remediation

Assess substantive public claims and documented procedures across **SRR-001–SRR-009**. Trace actual calls, imports, configuration reads, reference paths, file requirements and documented commands from tracked material into `.local-work/`, local system tools, sibling repositories, and private evidence. Do **not** bulk-inventory every scratch artifact or copy entire working directories.

For each material dependency record: owning procedure/claim, source and path, version/content identity, role (**versioned reusable source**, **lawful external prerequisite**, **generated/rebuildable output**, **private input/configuration**, or **custody-only historical evidence**), whether present in a clean checkout, rights/privacy status, required action and reviewer-verifiable result.

**Promotion rule:** Promote reusable source or schemas needed for current repeatable methods into tracked paths. Preserve provenance, avoid duplicated obsolete alternatives, and add concise invocation and read/write documentation with non-private examples. One-off historical scanners may instead remain custody-only if no present claim or prescribed reproduction route requires them. Where a historical recipe cannot run from a clean checkout, repair it or mark it explicitly historical/custody-only and provide the current supported alternative when one exists. Do not relabel a method “reproducible” without testing its declared inputs.

Apply this assessment explicitly to:

- SRR-008 survey and inventory methods, the two protection/environment helpers and the SRR-009 run card's reuse of them;
- SRR-002/003 static exports, local scanners, and any sibling Ghidra script references;
- SRR-005 site/correlation test tooling and private Save2 menu records;
- SRR-006/007/009 tracked observer/build/qualification sources versus private native inputs and archived test receipts;
- SRR-001/004 figures and editorial render tools where actual reproduction is claimed;
- documentation links, implementation briefs, evidence archives, version provenance and third-party notices.

## 4. Self-contained save and environment tooling — REQUIRED

**Maintainer decision: copy the smallest coherent reusable implementation into this repository. Do not use `starfield-outpost-research` as an ongoing runtime/build dependency.** A shared package extraction is also out of scope.

1. Inspect the existing helper call graph and select the required save-policy logic, schemas, fixtures and environment/inventory checks. Place reviewed copies under suitable tracked project tooling paths (choose a cohesive layout and document it). Preserve semantics and test against known SRR-008/009 receipts without writing to live saves. Remove mandatory imports, path assumptions and execution references to the sibling repository from the supported workflow.
2. **Separate code from personal state.** No personal save directory names, account IDs, backup inventories, actual saves, credentials, active Steam log extracts, absolute machine paths or private protection JSON should enter tracked source. Use parameters or an explicitly ignored, documented local configuration. Validate effective roots, expected policy version and backup availability at invocation. A clean checkout should be able to run self-contained synthetic tests without private inputs; live protection comparisons still require the maintainer's private data.
3. Reconcile outputs and behavior with the existing read-only checker, including pair-by-pair length/SHA-256 comparisons, protected designations, unclassified entries and failure classification. Report any differences; **do not weaken protection checks** merely to achieve the same outcome. Provide a way to choose a fresh output directory so historical SRR-008 evidence cannot be overwritten. Keep `-E -B` Python isolation where applicable; report a false success if a subprocess exits 0 while the success fields fail.
4. Review and record licensing/provenance for the copied material. The publication audit identified sibling save-policy code marked **GPL-3.0-or-later**; check actual file notices and compatibility with this repository, preserve any required copyright/license notices, and update `THIRD_PARTY_NOTICES.md` as appropriate. Distinguish rights in *reusable source* from rights in personal configurations or third-party/game data. If any required code cannot properly be incorporated, stop that portion and report the exact blocker rather than silently adding an external dependency.
5. Preserve the old SRR-008/009 helper versions and receipts as history. Supported current instructions should point to the newly tracked, self-contained commands. Historical exact-command reproduction should be labeled custody-only when it depends on private state.

## 5. Preserve Save2 as a private local release asset — REQUIRED

The maintainer authorizes a **non-destructive copy** of the verified Save2/HIST-0245 original into:

`.local-work/release-assets/save2/`

- Locate the actual protected source through established save provenance; confirm its original identity (including expected size and SHA-256) and that it is the intended Save2, not an incidental autosave or a renamed substitute. If several candidates exist or identity differs, do not guess: report and hold that copy operation.
- Record source provenance and a pre-copy identity receipt. Copy the bytes without altering, moving, deleting or reclassifying the original; confirm source and destination identity and full SHA-256 after the copy. Use collision-safe create-new semantics and refuse to overwrite an existing asset without separate approval. Leave sources and backups in place.
- Retain an adjacent **private manifest** (e.g. `manifest.json`) with SHA-256, size, source evidence/identity, copy time, copy verification and intended Stage B research role. Avoid public/private identifying metadata in tracked summaries.
- Ensure `release-assets/` stays ignored, is excluded from the task diff and any automatically assembled public release, and is **not** treated as approved for redistribution. This copy is local retention against possible later cleanup of the outpost project's `.local-work/`. Verify capacity on C: and D: before material writes.
- A short public note may state that a privately retained, hash-identified research save is an optional Stage B input. **No Save2 loading, testing, conversion or save modification is authorized.**

## 6. Research findings and dossier presentation

Make the current SRR-009 dossier **results-first**: a reader must encounter the central scientific result before the lengthy debugger-development history. Prefer a compact opening **Finding / Observation boundaries / Applicability and limitations / Evidence and verification / Method and dependency requirements / Historical engineering record** structure. Reorder or create navigation/summary sections as needed, rather than expanding the already long chronological narrative.

The controlling scientific statement is **no observed entry into the four monitored resource-generation path sites in the qualified 84.281-second post-title interval**, with 95 verified initially armed thread generations, four verified subsequent thread arrivals, and two bounded windows. The verified STOP-500 prefix is **353,147 bytes**, SHA-256 **`f4cd672725622db9c3e0d8a74bc5b4c3bb1c7bd1469ddd3b89017a8b33d80967`**. No finding about pre-arm startup, Save2 load or later gameplay follows. Cite the original exact run, build and evidence custody for this result.

Preserve, but subordinate, the two earlier `INSTRUMENTATION_INCOMPLETE` admission attempts, their diagnostics, the independently witnessed normal Starfield exit, unconfirmed normal debugger retirement and later exact-observer administrative termination. Do not rewrite reviewed historical records to remove failure modes or invent a normal retirement. Preserve earlier review blocks, their exact identities and their immutable evidence. Avoid turning the top-level dossier, root README or authoritative baseline into a diary; implementation history belongs in a concise provenance/engineering section or appendix and may be linked rather than repeated.

Use **three *verification-route* categories**, separate from the project's existing epistemic labels (`PROVEN`, `STRONG`, `PROVISIONAL`, `COUNTERFACTUAL`, `SUPERSEDED`):

- **Reproducible method** — tracked source and declared lawful inputs permit another researcher to rerun the method; does not promise byte-identical output.
- **Custody-backed historical observation** — exact historical evidence is retained and hash-identified but may not be publicly redistributed or reproducible byte-for-byte.
- **Provisional/unresolved claim** — evidence is insufficient for that specific statement; state what is missing and what would settle it.

The categories can coexist for one investigation. Do not confuse a reproducible procedure with a reproduced historical observation, or the review disposition `COMPLETE` with proof of all scientific hypotheses. Update navigation and applicability registers only where necessary for truthful current claims.

## 7. Archives, links, privacy and publication rights

- Preserve the existing implementation-brief and audit archive conventions. Resolve the broken SRR-009 brief link: incorporate a rights- and privacy-reviewed brief under the established tracked/archive convention **or** provide an honest stable tracked summary/custody reference where exact publication is inappropriate. Do not fabricate a link or silently imply an untracked document is present in a clone.
- Validate repository-relative links, archive entry references and explicitly documented local commands. Check the relevant archived Markdown/JSON payloads, not just ZIP filenames/extensions, for personal paths, sensitive data, proprietary excerpts and permission limitations. Repair only relevant issues; retain informative generic/example paths.
- Inspect rights and attribution for any source transplanted from the outpost project and for SRR-008 survey adaptations. The repository's GPL license does not relicense Bethesda binaries, private saves, external proprietary data or third-party material. Update notices for the actual incorporated code.
- Do not add actual Save2, protected save inventories, raw Steam logs, executable/DLL bytes, game assets, dumps, full private title inventories, personal configuration, credentials or Ghidra databases to Git or to a public archive. Any rights-uncertain artifact stays local or gets an explicit publication hold.
- Correct claim/navigation precision where the audit identified it (e.g. established bounded retail *static mapping* versus unresolved *live invocation*) without reopening settled scientific work.

## 8. Durable workflow rules — REQUIRED

Update `docs/research-workflow.md` as the **authoritative** policy; add at most a short pointer in `AGENTS.md` where useful. Rules should be clear and proportionate, not a new full audit bureaucracy:

1. **Source/output classification:** distinguish reusable tracked methods, lawful versioned external inputs, generated outputs and private/custody records whenever a research tool is introduced.
2. **Promotion trigger:** an exploratory `.local-work/` helper that becomes necessary for a documented *current repeatable procedure* must be tracked or explicitly declared as a versioned, obtainable external dependency; never silently require ignored scratch files.
3. **Private state separation:** reusable source is parameterized; private save paths, protection policies, source secrets and other machine-specific inputs are local and ignored.
4. **Verification routes:** label reproducible methods, custody-backed historical observations and provisional claims accurately and independently of epistemic confidence.
5. **Proportionate independent publication/dependency check:** reviewers check new imports, commands, files, archive/link targets, third-party permissions and clean-checkout viability for the task's actual scope; not every editorial change needs a full historical sweep.
6. **Attributable live-gate refusal:** a safety/admission gate that can prevent a scientific experiment should retain a durable, specific failure reason and an explicit indication when durability itself fails. Do not require impossible logging guarantees; preserve a trusted earlier prefix.
7. **Separate scientific and operational outcomes:** evidence validity, observation coverage, target survival, debugger retirement and cleanup are independently assessed. An abnormal cleanup does not erase an already sealed scientific result.
8. **Observer-only administrative closure:** once the exact target has demonstrably exited, its identity and evidence are verified, and authority is granted, an orphaned observer can be terminated administratively without requiring an extensive fresh fixture program; do not infer this grants authority to terminate an observer while it still controls a live target.
9. **Results-first durable research writing:** lead with established findings, scope and limitations. Preserve operational history as supporting provenance instead of letting it dominate the scientific account.

Keep the existing 40 GB per-drive floor, source pinning, original-evidence preservation, independent review, and exact Git patch workflow intact. Do not add contradictory policies in multiple documents.

## 9. Clean-checkout and offline acceptance verification

Use a **fresh isolated checkout or reconstructed tracked snapshot**, without accidentally borrowing ignored working-directory files, to verify current supported offline procedures. Record precisely which external lawful inputs and tool versions were supplied. Test representative paths end-to-end, including:

- Build and disposable qualification instructions for the tracked observer, subject to available lawful PE/Windows SDK/toolchain inputs; no retail attachment.
- The newly promoted self-contained save-policy/environment tooling against **synthetic**, non-private saves/configuration, including correct success and deliberate mismatch, missing configuration, wrong namespace and refusing output overwrite.
- An SRR-008 inventory/survey *offline* fixture route where supported, or an accurate documented dependency and custody limitation if that exact route cannot be reproduced.
- A targeted audit of SRR-002/003/005 documented commands and references: either show source availability and a lawful reproduction method, or accurately classify the historical procedure as custody-only and link the current substitute.
- Documentation-relative links and archive references, code provenance, Git ignored paths and the absence of accidental private/proprietary payloads in the candidate patch or tracked archives.

Do not demand byte identity of a newly built binary containing a timestamp, a historical retail journal or the historical independent reviews. An unsupported current command, missing undeclared dependency, missing tracked source required for the method, inaccurate present-tense reproducibility claim, or leaking private release asset is a **REWORK** issue. An explicitly scoped custody-only historical observation is not.

Run any affected tests and document skipped controls with exact prerequisites and impact. Any test requiring a live game, unapproved debugger operation, private save load or third-party redistribution must stay unrun and expressly labeled.

## 10. Independent challenge, acceptance criteria and handoff

Assign a fresh independent reviewer access to this brief, original publication audit, starting/current diff, tracked sources, clean-checkout evidence, private dependency identities *without requiring their publication*, and local Save2 copy receipts. The reviewer must test plausible counterexamples, including an undeclared sibling-repository import, a hardcoded old evidence path, a falsely passing save checker, a broken archive link, mislabeled historical reproducibility, or Save2 accidentally entering the Git patch. No live Steam/game/debugger action is permitted in review.

**Mandatory acceptance criteria:**

- **AC1 — Preservation/authority:** No live experiment or instrumentation change. SRR-009 scientific STOP and historical evidence unchanged; protected originals/backups unchanged, starting Git state reconciled and disk floor observed.
- **AC2 — Self-containment:** Current supported SRR-008/009 protection/environment method and selected reusable survey methods have tracked source, synthetic tests and documented configuration; no required dependency on sibling checkout or ignored code. Copyright/provenance reviewed.
- **AC3 — Private Save2 retention:** Correct Save2 located and content-verified, independently copied to ignored `.local-work/release-assets/save2/`, both identities rechecked, provenance recorded, no public inclusion or modification to original. If identity/source cannot be verified, explicitly report **BLOCKED for AC3** rather than copying an arbitrary save or claiming completion.
- **AC4 — Claim integrity and presentation:** SRR-009 begins with the qualified zero result, its exact scope and evidence; failure and cleanup history is preserved but subordinate. SRR-001–009 verification-route and applicability statements are accurate without inflating conclusions.
- **AC5 — Publication and rights:** Brief/archive/link repairs; relevant third-party source notices and license conditions; no private/proprietary payload or unapproved Save2 distribution.
- **AC6 — Durable workflow:** All agreed rules are incorporated concisely into the authoritative workflow and referenced appropriately, without redundant bureaucracy or conflict.
- **AC7 — Clean-checkout validation:** Documented current offline procedures work with declared inputs; explicit custody-only exceptions; recorded negative controls; no accidental reliance on `.local-work/` or sibling source.
- **AC8 — Independent challenge and exact handoff:** Fresh challenger evaluates AC1–AC7 and strongest contrary cases; final manifest/review block, protected identities and Git-native task-only patch are byte-verified against a clean replay; no staging/commit/push.

Use **COMPLETE / REWORK / BLOCKED** per `docs/research-workflow.md`. If one subtask genuinely cannot be completed safely (such as verifying Save2 provenance), preserve successful work, report precise failed criterion and minimum decision needed, and do not fabricate overall COMPLETE. Correct issues and return to the independent reviewer until criteria pass or a genuine blocker remains.

**Return to maintainer:** short findings-first summary; updated files and dependency inventory; local Save2 verification receipt *without private data in the public diff*; clean-checkout commands/results and limitations; privacy/license disposition; final consolidated task-only diff; independently reviewed manifest and report; explicit **READY FOR MAINTAINER COMMIT REVIEW** only when all mandatory criteria pass. Do **not** commit, push, tag, publish a release, or begin Stage B.
