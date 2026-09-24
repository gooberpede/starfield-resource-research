# Public-Release Remediation Brief — `starfield-resource-research`

## Purpose

Implement the approved public-release remediation for:

```text
gooberpede/starfield-resource-research
```

following:

```text
docs/audits/PUBLIC-RELEASE-READINESS.md
```

The audit verdict was `NOT READY`, with 2 BLOCKER, 6 SHOULD-FIX, and 2 OPTIONAL findings.

The owner has now made these decisions:

1. **PRR-002 native reverse-engineering evidence is approved for publication in principle**, with one scope-tightening change:
   - retain the focused evidence corpus;
   - trim the full-function `FUN_14152CBC0` decompilation and instruction listing to the portions actually needed to substantiate the relevant research findings;
   - preserve the rest of the selected Ghidra evidence unless another concrete issue is discovered.

2. **PRR-001 CSV datasets should be removed from the current tree if they are not actually required by this repository**, for repository hygiene rather than because they are considered impermissible to publish.
   - Do not rewrite Git history merely because the files were formerly present.
   - First verify there is no active dependency on those files.

3. **License preference: GPL-3.0-or-later** for original project material, with a clear third-party/game-derived-content boundary.
   - Do not claim that the GPL licenses material the owner does not own.
   - Apply licensing language carefully to original scripts, documentation, and research prose.
   - Game-derived excerpts/data must be separately framed as third-party-derived evidence/content.

This is an implementation/remediation task.

Do **not** make the repository public yet.
Do **not** rewrite history.
Do **not** create a tag or GitHub Release.
Do **not** commit or push unless explicitly asked.

---

## 1. Remediation goals

Bring the repository to a state suitable for a final public-release recheck.

Close or materially resolve:

```text
PRR-001
PRR-002
PRR-003
PRR-004
PRR-005
PRR-006
PRR-007
PRR-008
```

The OPTIONAL findings may be deferred.

Do not reopen settled scientific findings or generation semantics.

---

## 2. Preserve research integrity

Preserve the evidence vocabulary:

```text
PROVEN
STRONG
PROVISIONAL
COUNTERFACTUAL
SUPERSEDED
```

Preserve superseded evidence where historically meaningful.

Do not simplify or delete research material merely because it may be unfamiliar to a public reader. Prefer framing and indexing.

---

## 3. Verify whether `data/` files are still used

Search the current repository for references to:

```text
data/PlanetResourceGeneration_v5.csv
data/Starfield_IRES_Hierarchy.csv
data/planet-all-resources.csv
```

and to the filename-only forms.

Classify each reference as:

```text
active runtime/tool dependency
active documentation dependency
historical documentation reference
validation-history reference
stale reference
```

Do not infer “unused” solely from lack of direct code imports.

Report the dependency result for each file.

---

## 4. Remove redundant CSVs from HEAD if dependency-safe

If no current runtime/tool requirement exists, remove:

```text
data/PlanetResourceGeneration_v5.csv
data/Starfield_IRES_Hierarchy.csv
data/planet-all-resources.csv
```

from the current tree.

Do **not** rewrite history or purge historical commits.

Reason:

> Maintained canonical inputs and extraction tooling now belong in the sibling reproducer; these are historical/redundant research artifacts and are not needed in the current research tree.

If any file is genuinely required, stop and report that dependency instead of deleting it blindly.

If `data/` becomes empty, remove the empty directory rather than preserving it with `.gitkeep`.

Historical text may still refer to the datasets where that is necessary to describe past validation.

---

## 5. Update documentation after CSV removal

If the CSVs are removed:

- remove wording that implies `data/` is the current canonical source;
- preserve historical references explaining past validation;
- point current readers to the sibling reproducer for maintained canonical datasets and xEdit exporters;
- do not rewrite history as though the files were never used.

---

## 6. PRR-002: preserve the focused evidence corpus

Retain the selected evidence under:

```text
docs/experiments/evidence/
```

except for the agreed scope tightening around `FUN_14152CBC0`.

The publication decision is:

> Focused Ghidra-derived evidence is intentionally retained because it makes the reverse-engineering claims inspectable and falsifiable.

Do not broadly delete:

```text
decompiled.c
instructions.txt
callers.json
callees.json
metadata.json
data-references.json
constants.json
manifest.json
```

from the evidence corpus.

Do not collapse the evidence into prose-only summaries.

---

## 7. Trim `FUN_14152CBC0` full-function evidence

Current files:

```text
docs/experiments/evidence/pre-biome-resource-state/FUN_14152cbc0-decompiled.c
docs/experiments/evidence/pre-biome-resource-state/FUN_14152cbc0-instructions.txt
```

contain the complete enclosing orchestration function, including logic beyond what is needed for the resource-state investigation.

Replace them with **bounded, contiguous, provenance-preserving excerpts** containing only the regions needed to establish:

```text
atmosphere/pre-existing shared resource-state population
Everywhere/category-6 pre-pass
ordering before shuffled/per-biome generation
transition into per-biome processing
calls into FUN_1415DCFB0
```

Avoid unrelated later logic, including large sections devoted only to:

```text
biome percentage normalization
unrelated error handling
post-generation bookkeeping
cleanup/destruction
```

unless small surrounding context is necessary for intelligibility.

Preferred filenames:

```text
FUN_14152cbc0-decompiled-excerpt.c
FUN_14152cbc0-instructions-excerpt.txt
```

Delete the old full-function files from HEAD after verifying the excerpts.

Do not rewrite history.

The excerpts must preserve:

```text
original function address/name
relevant instruction addresses
contiguous ordering
enough context to correlate decompiler and instruction views
```

Do not manually rewrite raw evidence into “cleaned-up” pseudocode and label it as exporter output.

---

## 8. Update the pre-biome evidence README

Update:

```text
docs/experiments/evidence/pre-biome-resource-state/README.md
```

to state that:

- the evidence set is intentionally bounded;
- `FUN_14152CBC0` is represented by selected excerpts rather than a complete function dump;
- the excerpts preserve the exact regions needed for the documented findings;
- the complete executable/decompiler output is not distributed;
- source executable identity and Ghidra provenance remain recorded.

Also replace machine-specific active reproduction paths as described below.

---

## 9. Add a third-party / reverse-engineering evidence notice

Add a concise top-level notice, preferably:

```text
THIRD_PARTY_NOTICES.md
```

It should explain that:

- Starfield, Creation Kit, Bethesda, and related marks/content belong to their respective rights holders;
- this is an unofficial research/modding project and is not affiliated with or endorsed by Bethesda/ZeniMax;
- the repository contains limited, targeted reverse-engineering evidence derived from legitimately obtained software;
- such material is retained only to document specific technical findings and support reproducibility;
- the repository does not distribute Starfield/Creation Kit executables, DLLs, Ghidra project databases, raw debugger traces, memory dumps, or bulk binary reconstruction material;
- users must obtain the game and tools through legitimate channels;
- the project license applies only to material for which the repository owner holds the relevant rights and does not purport to relicense proprietary third-party content.

Keep this concise and factual.

Do not claim fair use or legal immunity as a settled fact.

---

## 10. Add GPL-3.0-or-later licensing

Add a top-level:

```text
LICENSE
```

using the official GNU GPL version 3 text.

Use `GPL-3.0-or-later` as the project license identifier.

Add a concise README/notices statement such as:

```text
Original project code and documentation are licensed under GPL-3.0-or-later,
except where otherwise noted.
```

Explicitly distinguish:

```text
original project material
third-party/game-derived evidence
trademarks/names
```

Do not imply the GPL grants rights in Bethesda/ZeniMax material.

Do not add GPL headers to derived decompiler/disassembly evidence.

For clearly original Java/Ghidra scripts, SPDX headers are optional. If added consistently, use:

```text
SPDX-License-Identifier: GPL-3.0-or-later
```

---

## 11. README public-facing remediation

Update root `README.md` while preserving the strong technical summary.

Add real Markdown links to:

```text
docs/v1-research-baseline.md
docs/known-facts.md
docs/hypotheses.md
docs/function-register.md
ghidra/README.md
docs/experiments/
docs/experiments/evidence/
docs/implementation-briefs/
https://github.com/gooberpede/starfield-resource-reproducer
THIRD_PARTY_NOTICES.md
LICENSE
```

Correct the repository-layout section to match the tracked tree.

Remove references to nonexistent or empty/untracked paths such as `tools/` unless they genuinely exist after remediation.

If `data/` is removed, do not list it as a current directory.

Add a concise section explaining where current canonical data and executable model live: the sibling reproducer.

---

## 12. Counterexample/correction guidance

Add a concise public path for reporting contradictions.

For example:

> If you find a planet/build/scenario that contradicts the recovered model, open an issue with the Starfield/Creation Kit version, relevant body, reproduction steps, and observed result.

Do not require a formal `CONTRIBUTING.md` unless it provides real value.

Make clear that new evidence should be reconciled through the existing evidence-status workflow rather than silently overwriting research history.

---

## 13. Add centralized provenance/version documentation

Create a durable document, preferably:

```text
docs/PROVENANCE.md
```

Record, where known:

```text
CreationKit.exe identity
Creation Kit version/build
CreationKit.exe hash(es)
Starfield game version/build used for retail checks
plugin/DLC versions relevant to the canonical dataset
Ghidra version(s)
xEdit version(s)
x64dbg version(s)
important extraction dates/timestamps
which evidence bundles correspond to which executable build
which validation runs correspond to which source-data snapshot
```

Do not invent missing version data.

If exact values are unknown, state:

```text
unknown / not recorded
```

Preserve existing executable hashes and timestamps where available.

Do not redistribute binaries.

---

## 14. Preserve CK-versus-retail distinction

README and provenance documentation must continue to make clear:

```text
Creation Kit addresses/control flow
    ≠
retail Starfield.exe addresses
```

Do not generalize CK addresses to retail.

Retail holdout validation must be framed as validation evidence, not direct retail address mapping.

---

## 15. Replace active author-machine paths

Search current tracked text for active examples such as:

```text
D:\ProjectsD:	oolsD:\ReverseEngineering```

Replace active copy-paste commands with placeholders or portable variables, e.g.:

```text
<ghidra-install>
<repository>
<ghidra-project-dir>
<output-directory>
```

Historical implementation briefs may retain old workspace paths if clearly framed as historical task specifications.

Do **not** remove executable-derived Bethesda build paths such as:

```text
E:\BuildAgent\...
```

when they are part of retained evidence. Label them as executable-derived strings where useful.

---

## 16. Strengthen `.gitignore`

Add narrowly justified patterns for workflow artifacts that should not be accidentally published.

At minimum consider:

```text
*.trace64
*.dmp
```

and common x64dbg database/session artifacts actually used by the workflow.

Also consider:

```text
*.zip
*.7z
*.rar
```

because the audit found local evidence-transfer archives.

If archives are broadly ignored, document that a deliberately reviewed archive must be force-added explicitly.

Do not add overbroad rules such as `*.db` without confirming they will not hide legitimate project files.

Preserve existing binary/Ghidra-project exclusions.

---

## 17. Add documentation index

Create:

```text
docs/README.md
```

that clearly separates:

```text
CURRENT AUTHORITATIVE BASELINE
    v1-research-baseline.md
    known-facts.md
    hypotheses.md
    function-register.md

EXPERIMENTS / EVIDENCE
    experiment records
    focused evidence bundles

HISTORICAL IMPLEMENTATION BRIEFS
    non-authoritative task specifications preserved for rationale/history

TOOLING
    ghidra/README.md
```

Make clear that implementation briefs are historical specifications, not current authority.

Do not delete them merely because they are procedural.

---

## 18. Experiments/evidence framing

Add a concise index/README under `docs/experiments/` if one does not already exist and if it improves navigation.

It should state:

- experiment notes may contain superseded hypotheses;
- the current baseline governs current conclusions;
- evidence bundles preserve selected supporting artifacts;
- raw debugger traces remain local/private unless deliberately reviewed and transformed.

Do not duplicate the full baseline document.

---

## 19. Ghidra documentation portability

Update `ghidra/README.md` only as needed to:

- remove active machine-specific paths;
- link to centralized provenance/version documentation;
- preserve script read-only guarantees;
- preserve actual tested Ghidra-version statements;
- avoid implying universal compatibility.

Do not perform the optional large restructuring of the 64 KB Ghidra README in this remediation.

---

## 20. Sibling-repository linkage

Add a real link to:

```text
https://github.com/gooberpede/starfield-resource-reproducer
```

with the ownership boundary:

```text
research repo:
    evidence status, native-function findings, provenance, history

reproducer repo:
    executable reference model, tests, canonical production data/tooling
```

Do not modify the sibling repository in this brief.

---

## 21. Update audit status without rewriting history

Update:

```text
docs/audits/PUBLIC-RELEASE-READINESS.md
```

with a clearly dated remediation-status section or appendix.

Do not rewrite the original findings or retroactively change the original `NOT READY` verdict.

Record statuses such as:

```text
RESOLVED
RESOLVED BY OWNER DECISION
RESOLVED BY REMEDIATION
DEFERRED OPTIONAL
```

Recommended treatment:

```text
PRR-001
    resolved by removing redundant CSVs from HEAD after dependency verification;
    historical presence intentionally retained

PRR-002
    resolved by explicit publication approval + targeted FUN_14152CBC0 scope trim
    + third-party evidence notice

PRR-003
    resolved with GPL-3.0-or-later + rights-boundary notice

PRR-004..008
    resolved by docs/provenance/path/ignore remediation

PRR-009..010
    optional/deferred unless naturally addressed
```

---

## 22. Recheck evidence after trimming

After replacing the `FUN_14152CBC0` full files:

- confirm the excerpts still support the documented claims;
- verify referenced addresses remain correct;
- confirm evidence README filenames match actual files;
- ensure no current docs still refer to deleted filenames unless explicitly historical.

Do not weaken the research record until claims become unsupported.

---

## 23. Recheck CSV dependencies after deletion

After removing the CSVs, confirm:

```text
no script fails because of missing research-repo data files
no current README instruction expects them
no active evidence workflow depends on them
```

Historical text may still mention them.

Where appropriate, replace active references with links to maintained reproducer equivalents.

---

## 24. Licensing boundary model

The repository should end with a clear model:

```text
GPL-3.0-or-later
    applies to original project code and documentation unless otherwise noted

Third-party/game-derived material
    remains subject to the rights of its respective owners
    and is not relicensed by this repository
```

Do not add a separate Creative Commons license unless explicitly requested later.

---

## 25. Non-affiliation statement

Add a short statement, preferably in README and/or `THIRD_PARTY_NOTICES.md`, along the lines of:

```text
This is an unofficial community research project and is not affiliated with,
endorsed by, or sponsored by Bethesda Softworks or ZeniMax Media.
```

Keep it concise.

---

## 26. Git-history policy

For this remediation:

```text
NO HISTORY REWRITE
```

The owner has chosen to retain historical presence of:

- the old CSVs;
- previous full-function evidence exports.

Do not use:

```text
git filter-repo
BFG Repo-Cleaner
force-push
orphan-branch recreation
squash-to-new-root
```

---

## 27. No visibility change

Do not:

```text
make repository public
change visibility
create a GitHub Release
create a tag
change GitHub topics/settings
```

The repository remains private until the final re-audit is reviewed.

---

## 28. Verification — safety

Re-run:

```text
secret-pattern scan on HEAD
secret-pattern scan on reachable history
prohibited binary/artifact scan on HEAD
prohibited binary/artifact scan on reachable history
absolute local-path scan
large-blob inventory
tracked extension inventory
```

Confirm no remediation introduced:

```text
credentials
raw traces
archives
Ghidra databases
executables
memory dumps
```

---

## 29. Verification — docs and encoding

Run:

```text
Markdown internal-link check
UTF-8/mojibake scan
git diff --check
```

Verify:

- no broken relative links;
- no private/local file URLs;
- no stale filenames after evidence/CSV changes;
- no malformed Unicode;
- no whitespace corruption.

---

## 30. Fresh-clone/public-reader check

From a fresh clone or equivalent clean checkout:

- confirm README navigation works;
- confirm no current instruction requires missing local files;
- confirm Ghidra instructions are portable enough to adapt;
- confirm provenance docs are discoverable;
- confirm sibling-reproducer linkage is clear;
- confirm no ignored local artifacts are present.

Do not require the repo to be self-contained without Starfield/Creation Kit.

---

## 31. Scientific-integrity check

Confirm remediation did not change the recovered model.

At minimum preserve:

```text
1,444 / 1,444 canonical validation scope
10 / 10 holdout scope
CK-versus-retail distinction
oracle limitations
evidence-label system
superseded-path framing
```

---

## 32. Final release-readiness recheck

After remediation, rerun the release checklist and create either:

```text
docs/audits/PUBLIC-RELEASE-READINESS-RECHECK.md
```

or a clearly separated recheck section in the existing audit.

Preferred result:

```text
READY
```

or:

```text
READY AFTER MINOR FIXES
```

with zero unresolved BLOCKER findings.

Do not make the repository public automatically.

---

## 33. Expected changed files

Likely changes include:

```text
LICENSE
THIRD_PARTY_NOTICES.md
README.md
.gitignore

docs/README.md
docs/PROVENANCE.md
docs/audits/PUBLIC-RELEASE-READINESS.md
docs/experiments/... README/index files
ghidra/README.md

docs/experiments/evidence/pre-biome-resource-state/
    FUN_14152cbc0-decompiled-excerpt.c
    FUN_14152cbc0-instructions-excerpt.txt
    README.md
```

Likely deletions from HEAD if dependency-safe:

```text
data/PlanetResourceGeneration_v5.csv
data/Starfield_IRES_Hierarchy.csv
data/planet-all-resources.csv
```

Likely replaced/deleted from HEAD:

```text
FUN_14152cbc0-decompiled.c
FUN_14152cbc0-instructions.txt
```

Avoid redundant documents.

---

## 34. Deliverable report

Report:

1. files changed;
2. whether each CSV was confirmed unused before deletion;
3. CSV files removed from HEAD;
4. confirmation no history rewrite was performed;
5. exact `FUN_14152CBC0` excerpt boundaries retained;
6. confirmation excerpts still support intended claims;
7. other evidence files retained unchanged or justified exceptions;
8. license added and exact identifier used;
9. third-party/evidence notice summary;
10. provenance/version document contents and unknown values;
11. README/navigation changes;
12. docs index/history framing changes;
13. absolute-path replacements;
14. `.gitignore` additions;
15. sibling-repository link changes;
16. updated audit finding statuses;
17. secret/binary/history re-scan result;
18. Markdown-link result;
19. UTF-8/mojibake result;
20. `git diff --check` result;
21. fresh-clone/public-reader result;
22. final re-audit verdict;
23. confirmation visibility remained private;
24. confirmation no tag/release/commit/push was performed unless explicitly requested.

Do not commit or push.

---

## Acceptance criteria

The remediation is complete when:

1. the three CSVs are removed from HEAD after verified non-use, or explicitly retained with a documented dependency;
2. the full `FUN_14152CBC0` decompilation/instruction dump is replaced with bounded evidence excerpts;
3. the remaining PRR-002 evidence corpus remains intact and clearly framed;
4. GPL-3.0-or-later is added for original project material;
5. third-party/game-derived content is explicitly excluded from implied relicensing;
6. README navigation/layout is public-ready;
7. provenance/version information is centralized as far as existing evidence allows;
8. active author-machine paths are removed from current public instructions;
9. `.gitignore` is strengthened for trace/dump/session/archive risks;
10. implementation briefs and experiments are clearly indexed;
11. sibling-repository linkage is explicit;
12. the original audit is preserved with remediation status appended rather than rewritten;
13. public-safety scans pass;
14. Markdown links and UTF-8 checks pass;
15. final re-audit has zero unresolved release blockers;
16. repository visibility remains private.

Suggested commit message after review:

```text
chore: prepare research repo for public release
```
