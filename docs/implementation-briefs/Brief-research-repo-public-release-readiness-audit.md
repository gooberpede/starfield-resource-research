# Release-Readiness Audit Brief — `starfield-resource-research`

## Purpose

Audit:

```text
gooberpede/starfield-resource-research
```

for safe public release on GitHub.

This is an **audit-only** exercise unless an extremely small, non-controversial correction is necessary to complete the audit. Do not perform a broad cleanup, rewrite history, change repository visibility, create a release, tag a version, or push changes.

The immediate question is:

> Is the repository safe, understandable, legally/reputationally sensible, and technically coherent enough to make public in its current form? If not, what must be changed first?

The repository is currently private.

The sibling executable model is:

```text
gooberpede/starfield-resource-reproducer
```

The research repository owns evidence status, trace provenance, reverse-engineering findings, historical experiments, and native-function analysis. The reproducer owns the executable reference model and regression suite.

The diagnostic CLI work discussed for the reproducer is **deferred until after public release** and is out of scope here.

## 1. Audit posture

Treat this as a **forensic public-release audit**, not ordinary documentation polish.

A repository that has been private can contain material that is harmless privately but inappropriate once the complete Git history becomes public.

Audit both:

1. the current `main` tree; and
2. the repository's reachable Git history.

Do not assume that deleting a sensitive file from HEAD makes it safe to publish.

Classify every finding as:

```text
BLOCKER
SHOULD-FIX
OPTIONAL
NO-ACTION
```

Definitions:

```text
BLOCKER
    Must be resolved before repository visibility changes to public.

SHOULD-FIX
    Public release is possible without it, but the issue materially harms
    clarity, reproducibility, professionalism, maintainability, or user trust.

OPTIONAL
    Useful polish that can safely happen after release.

NO-ACTION
    Reviewed concern; current state is acceptable.
```

Also distinguish:

```text
CURRENT-TREE
HISTORY
BOTH
```

for where a finding exists.

Do not silently modify evidence classifications or research conclusions as part of release cleanup.

## 2. Current repository context to preserve

The current root contains at least:

```text
.gitignore
AGENTS.md
README.md
data/
docs/
exports/
ghidra/
```

Current public-facing intent is already reasonably clear:

- durable evidence and research-history record;
- reverse engineering of Starfield's runtime inorganic resource-generation system;
- current v1.0 model validated 1,444 / 1,444 canonical planet-wide;
- sibling reproducer owns executable model;
- evidence labels:
  `PROVEN`, `STRONG`, `PROVISIONAL`, `COUNTERFACTUAL`, `SUPERSEDED`;
- Creation Kit addresses/control flow must not be presented as retail `Starfield.exe` addresses;
- proprietary binaries/assets and imported Ghidra databases must not be committed.

Preserve these boundaries.

Do not simplify the repository by deleting legitimate superseded evidence merely because it may confuse a casual reader. Prefer clearer framing/navigation.

## 3. First priority: secrets, credentials, personal information, and local-environment leakage

Audit the **entire reachable history**, not only HEAD, for:

```text
API keys
access tokens
GitHub tokens
OAuth credentials
passwords
cookies
session identifiers
private URLs with embedded credentials
private repository tokens
cloud credentials
SSH/private keys
email addresses not intended for publication
personal phone/address data
usernames where they identify private/local accounts
Windows user-profile paths
machine names
private network paths
local absolute paths
```

Search for patterns including, but not limited to:

```text
ghp_
github_pat_
Bearer
Authorization:
token=
password
passwd
secret
api_key
apikey
client_secret
BEGIN PRIVATE KEY
BEGIN OPENSSH PRIVATE KEY
C:\Users\
D:\Users\
\\server\
localhost paths containing personal usernames
```

Do not report secrets by reproducing their full values in the audit.

If a credential-like value is found:

- report file/path/commit and type;
- redact the value;
- classify severity;
- state whether history rewriting and credential rotation are required.

A genuine credential in reachable history is a **BLOCKER** even if it has already been deleted from HEAD.

## 4. Proprietary/copyright-sensitive material audit

This repository concerns reverse engineering a commercial game, so perform a careful content audit.

The repository policy already prohibits:

```text
Starfield.exe
Bethesda DLLs
PDBs
extracted proprietary game assets
Ghidra project databases containing imported game binaries
other redistributable game binaries
```

Verify that these are absent from both HEAD and history.

Also inspect for potentially problematic **large verbatim derived material**, including:

```text
full binary dumps
large disassemblies
very large decompiler exports
large verbatim string tables
bulk extracted game records beyond what is reasonably necessary
raw proprietary asset content
memory dumps
process dumps
trace files containing substantial executable bytes
```

Do not assume that plain text is automatically safe just because it is not a binary.

For each category, distinguish:

```text
small factual/transformative research excerpt
small machine-readable metadata
large verbatim/reconstructive dump
```

Flag large verbatim material for human/legal review rather than making unsupported legal conclusions.

Do not delete or rewrite anything during the audit.

## 5. Ghidra-specific public-safety audit

Inspect:

```text
ghidra/
ghidra/scripts/
ghidra/README.md
```

and relevant history.

Verify that the repository contains only:

```text
scripts
documentation
small derived metadata
research notes
```

and does **not** contain:

```text
.gpr files
.rep directories
Ghidra project databases
imported executable databases
binary caches
analysis databases containing game binaries
temporary decompiler databases
```

Check whether the current `.gitignore` exclusions are sufficient for ordinary future use.

Audit Ghidra scripts for:

```text
hard-coded local absolute paths
user-profile paths
machine-specific Ghidra installation paths
private working directories
assumptions that only work on the author's machine
```

Classify hard-coded paths according to whether they are merely examples/documentation or active runtime assumptions.

## 6. x64dbg / trace / reverse-engineering artifact audit

Search current tree and history for debugger artifacts such as:

```text
.trace64
.dmp
memory dumps
register dumps
raw execution traces
breakpoint-state files
session files
```

Determine whether any committed trace material contains:

- proprietary executable bytes;
- sensitive local paths;
- excessive raw process data;
- material better kept private/local.

Small textual observations and manually summarized trace evidence are expected and acceptable unless another issue applies.

## 7. Data-directory audit

Inspect every file under:

```text
data/
```

Current known tracked datasets include:

```text
PlanetResourceGeneration_v5.csv
Starfield_IRES_Hierarchy.csv
planet-all-resources.csv
```

For each dataset, document:

```text
purpose
origin/extraction method
whether it is raw or derived
whether it is still current or historical
whether it is required by the public research record
approximate size
whether equivalent/current data now lives in the reproducer
whether redistribution presents any concern
```

Pay particular attention to the fact that the research repo still appears to use historical filenames while the reproducer has newer canonical filenames.

Do **not** rename or refresh datasets merely for neatness during this audit.

Determine whether the public README/docs adequately explain:

- why these datasets are present;
- which are historical research inputs/validation evidence;
- which are incomplete or superseded;
- that `planet-all-resources.csv` is a validation oracle and not generation logic;
- whether users should regenerate data themselves using the reproducer/xEdit tooling instead of treating this repo as the canonical data distribution.

If a dataset is unnecessary for the public research record and materially increases redistribution risk, classify that explicitly.

## 8. Full repository-history audit

Because making the repository public exposes history, inspect reachable commits for files that are no longer present.

At minimum audit historical filenames/extensions matching:

```text
*.exe
*.dll
*.pdb
*.gpr
*.rep
*.dmp
*.zip
*.7z
*.rar
*.trace64
*.bin
*.dat
*.db
*.sqlite
*.bak
*.tmp
*.log
```

Also identify unusually large historical blobs.

Produce a short list of the largest blobs in reachable history and inspect their types/origins.

A proprietary executable or sensitive dump in history is a **BLOCKER** even when absent from HEAD.

If history rewriting would be required, do not perform it in this audit. State the required remediation separately.

## 9. `.gitignore` audit

Review `.gitignore` against likely research workflow.

Current exclusions include Ghidra projects, binaries, generated exports, scratch/temp material, and `.local-work/`.

Check whether it should additionally protect against common accidental commits such as:

```text
*.dmp
*.trace64
*.zip / archives used for local evidence transfer
Ghidra user/cache files
x64dbg session/database files
Python caches if applicable
OS/editor artifacts
```

Do not recommend broad patterns that could hide legitimate source files.

Any proposed ignore additions should be justified by an actual workflow risk.

## 10. README public-facing audit

Review `README.md` as the first page a stranger will see.

Assess whether it clearly answers:

```text
What is this?
What problem was being investigated?
What was recovered?
How strong is the evidence?
What is the relationship to the reproducer?
Where should a new reader start?
What is in scope and out of scope?
What game/tool versions matter?
What is Creation Kit evidence versus retail evidence?
What should a user do if they find a counterexample?
```

Check whether the prominent:

```text
1,444 / 1,444 exact
10 / 10 holdout exact
```

claims are framed with sufficient scope and provenance.

Do not weaken well-supported claims merely to sound cautious.

Do ensure the README avoids implying:

- universal correctness across all future Starfield versions;
- retail-address equivalence where only CK addresses are known;
- atmosphere completeness where the oracle is known incomplete;
- that reverse-engineered function names are official Bethesda symbols.

## 11. Repository-layout accuracy

The README currently includes a repository-layout section.

Verify it against the actual tree.

Flag:

```text
listed paths that do not exist
important directories omitted
historical references that are now misleading
```

For example, if README documents `tools/` but no `tools/` directory exists, classify and recommend correction.

This is likely `SHOULD-FIX`, not a release blocker.

## 12. Documentation navigation audit

Inspect:

```text
docs/v1-research-baseline.md
docs/known-facts.md
docs/hypotheses.md
docs/function-register.md
docs/experiments/
docs/implementation-briefs/
ghidra/README.md
```

Assess whether a public reader can distinguish:

```text
current baseline
settled facts
open hypotheses
superseded investigations
historical experiment records
implementation/project-management artifacts
```

Identify documents that are:

```text
stale
contradictory
orphaned
misleading without context
too internally procedural for public value
```

Do not automatically delete internal-looking documents. Historical process can be valuable in a research repository.

Recommend better indexing or framing where sufficient.

## 13. Evidence-label consistency audit

Sample the repository for use of:

```text
PROVEN
STRONG
PROVISIONAL
COUNTERFACTUAL
SUPERSEDED
```

Check for obvious cases where:

- an old hypothesis is stated as fact in one document;
- a superseded interpretation remains presented as current;
- a Creation Kit finding is accidentally generalized to retail;
- a validation result is described without its population/scope;
- a known limitation has disappeared from a later summary.

This is a consistency audit, not an invitation to reopen settled reverse-engineering questions.

If a potential scientific/research contradiction appears, report it for review rather than "fixing" it without evidence.

## 14. Hard-coded path and machine-specific instruction audit

Search all tracked text for local-machine assumptions such as:

```text
D:\Projects\
D:\tools\
C:\Users\
AppData
specific Ghidra install paths
specific x64dbg install paths
private scratch directories
.local-work absolute equivalents
```

Distinguish:

```text
historical evidence/procedure that legitimately records a path
vs
current public instruction that incorrectly assumes the author's machine
```

Historical experiment notes do not necessarily need sanitizing if no personal/sensitive information is exposed.

Current setup/run instructions should be portable.

## 15. Public identity/privacy audit

Check commit-visible/public text for accidental personal identifiers beyond the chosen GitHub identity.

Do not flag the GitHub username itself.

Do flag unintended exposure such as:

```text
real-name paths
email addresses not meant for publication
home-directory usernames
machine names
private organization names
personal cloud-storage paths
```

Also inspect Git commit author metadata across history and report whether it exposes names/emails that the repository owner should consciously approve before making the repo public.

Do not rewrite author history during this audit.

## 16. License audit

Determine whether the repository currently has a license.

If no license exists, classify this as at least **SHOULD-FIX** before public release.

Do **not** choose a license on the user's behalf.

Report the practical consequence:

> Publicly visible source without a license is not automatically open-source and generally leaves reuse rights reserved.

Separate licensing questions for:

```text
original scripts/code
original documentation/research prose
third-party or game-derived data
```

If one license may not appropriately cover all content, call that out.

Do not make unsupported legal determinations about Bethesda data.

## 17. Third-party attribution audit

Search for dependencies, copied snippets, external algorithms, forum findings, xEdit/Ghidra examples, or third-party data sources that merit attribution.

Check whether public documentation should acknowledge:

```text
Bethesda / Starfield
Ghidra
xEdit
x64dbg
other researchers/sites/tools if materially relied upon
```

Do not add attribution merely because a tool was used; distinguish customary acknowledgments from actual licensing obligations.

## 18. Trademark / affiliation framing

Check whether README/public metadata makes clear that the project is unofficial and unaffiliated with Bethesda where appropriate.

Do not over-lawyer the README.

A short conventional disclaimer may be sufficient if currently absent.

## 19. Security/disclosure posture

This project is reverse engineering a game, not exposing a network service.

Assess whether `SECURITY.md` would provide meaningful value.

Do not recommend boilerplate security files unless there is a real maintenance benefit.

Likewise, do not require issue templates, codes of conduct, or governance files purely for appearance.

## 20. AGENTS.md public-release audit

`AGENTS.md` is currently substantial and useful for Codex/project continuity.

Assess whether publishing it:

- leaks sensitive/private workflow details;
- contains machine-local paths;
- creates confusion for ordinary readers;
- is acceptable as a contributor/AI-agent instruction document.

Do not remove it merely because it is agent-oriented.

If retained, consider whether README should simply ignore it or briefly identify it as project-maintainer guidance.

## 21. Implementation-brief audit

Inspect:

```text
docs/implementation-briefs/
```

Determine:

- whether briefs contain private conversation residue;
- absolute local paths;
- transient instructions that no longer make sense publicly;
- secrets/tokens;
- references to unavailable private artifacts;
- valuable historical rationale.

Do not remove them automatically.

Classify whether they should:

```text
remain as research history
be moved/archived
be excluded before release
```

with reasons.

## 22. Experiment-record audit

Inspect `docs/experiments/`.

For each category of experiment record, look for:

```text
unredacted local paths
raw debugger dumps
transient hypotheses presented without current status
missing provenance
references to files that will not be public
```

A historical experiment may remain wrong or superseded if clearly classified.

Public release should not flatten research history into a falsely tidy narrative.

## 23. Ghidra README size/content audit

`ghidra/README.md` is comparatively large.

Review whether it is:

- genuine documentation/research history;
- a concatenation of large proprietary decompiler output;
- excessively verbose but safe;
- better split/indexed;
- internally coherent with the current v1 baseline.

Do not rewrite it during the audit.

Flag any large verbatim decompilation excerpts separately under proprietary/copyright-sensitive review.

## 24. GitHub repository metadata audit

Review current GitHub-level metadata where accessible:

```text
repository description
homepage
topics
visibility
default branch
archived state
```

Recommend a concise public description and useful topics if absent.

Do not change visibility.
Do not modify repository settings in this audit.

Suggested topic categories might include:

```text
starfield
reverse-engineering
ghidra
xedit
modding
```

but do not apply them automatically.

## 25. Release/version semantics

This research repository is not necessarily a packaged software product.

Assess whether public release should use:

```text
no formal GitHub Release initially
a v1.0 research-baseline tag
a GitHub Release corresponding to the v1.0 recovered model
```

Do not create tags/releases in the audit.

Recommend the simplest option that accurately communicates the state of the research.

Distinguish the research-baseline version from the sibling reproducer's software/package version.

## 26. Cross-repository linkage

Check that the research repo clearly links to:

```text
gooberpede/starfield-resource-reproducer
```

and correctly describes the ownership boundary.

For eventual public release, the sibling reproducer should reciprocally link back.

Do not make reproducer changes in this audit.

Report any cross-link text that will become broken/confusing if one repository becomes public before the other.

## 27. Fresh-reader audit

Approach the repository as someone who knows Starfield modding but has never seen this project.

Determine whether, within approximately five minutes, they can identify:

```text
the research question
the current conclusion
the confidence/evidence system
the best starting document
the distinction between research repo and reproducer
how to reproduce or inspect evidence
what remains unresolved
```

List the top 3–5 points of likely confusion.

This is a usability/publication test, not a request to dumb down the technical material.

## 28. Reproducibility audit

Determine which research results can actually be reproduced by a third party from the public repository plus legitimately obtained external tools/game files.

For major evidence paths, identify required external dependencies such as:

```text
Starfield installation
Creation Kit
Ghidra
xEdit
x64dbg
specific exported CSVs
specific executable/game versions
```

Check whether version requirements are adequately recorded.

If exact executable/Creation Kit build identification is missing for address-sensitive findings, flag it.

Do not require redistributing proprietary binaries to make the research "self-contained."

## 29. Build/run tooling audit

The research repo is not the executable reproducer, but inspect scripts under `ghidra/scripts/` and any other tooling directories for:

```text
syntax/runtime obviousness
documented prerequisites
portable invocation
read/write behavior
destructive behavior
hard-coded paths
output locations
```

No need to add CI solely for research scripts unless it provides real value.

## 30. Public-safe file inventory

Produce a concise inventory grouping tracked content into:

```text
SAFE TO PUBLISH AS-IS
SAFE BUT SHOULD BE BETTER DOCUMENTED
REQUIRES HUMAN/LEGAL REVIEW
MUST NOT BE PUBLIC
```

Do this at useful directory/file-group grain rather than listing every trivial Markdown file individually.

## 31. Required audit commands/checks

Use appropriate local/Git tooling.

At minimum include:

```text
git status
git log --all --stat / equivalent history inventory
git rev-list --objects --all
large-blob inspection
tracked extension inventory
secret-pattern scan across current tree
secret-pattern/history scan where practical
absolute-path scan
binary/archive/debugger-artifact scan
UTF-8/mojibake scan
git diff --check
```

Do not use an external secret-scanning service.

## 32. Mojibake / encoding audit

Preserve UTF-8 discipline.

Scan public-facing and historical/current research text for common mojibake patterns such as:

```text
Ã
Â
â€
ÔÇ
```

Distinguish actual repository corruption from terminal/rendering corruption.

Do not "fix" valid Unicode punctuation or box-drawing characters.

## 33. Documentation/link audit

Check Markdown links and paths for:

```text
broken relative links
links to private/local files
D:\... links
references to removed documents
references to private ChatGPT artifacts
references to unavailable local exports
```

External URLs need not all be live-tested exhaustively, but obvious critical links should be checked.

## 34. No visibility change

Do **not**:

```text
make repository public
change GitHub visibility
create GitHub release
create tag
rewrite history
force-push
delete branches
rotate credentials
```

The audit should tell the user what needs to happen before those actions.

## 35. No broad cleanup during audit

Do not conflate:

```text
finding
remediation
implementation
```

Desired sequence:

```text
audit
→ review findings with user
→ write remediation brief
→ Codex implements approved fixes
→ review diff
→ rerun release-readiness checks
→ only then make public
```

## 36. Deliverable

Create a durable audit document, preferably:

```text
docs/audits/PUBLIC-RELEASE-READINESS.md
```

If `docs/audits/` does not exist, creating it is acceptable.

The audit should contain:

### Executive verdict

One of:

```text
READY
READY AFTER MINOR FIXES
NOT READY
```

### Findings table

For each finding include:

```text
ID
Severity
Location (CURRENT-TREE / HISTORY / BOTH)
Area
Finding
Why it matters
Recommended remediation
```

### Explicit blocker list

If none:

```text
No release blockers found.
```

### History-safety section

Explicitly state whether publication of full reachable history appears safe.

### Proprietary-material section

Explicitly state what was checked and what remains a human/legal judgment.

### Privacy/secrets section

Explicitly state whether credentials or unintended personal data were found.

### Licensing section

State current license status and what decision is still required.

### Public-reader section

Top confusion/usability findings.

### Suggested remediation sequence

Order fixes to minimize churn.

### Release checklist

A short checklist to rerun immediately before changing visibility.

## 37. Deliverable report back to user

Report:

1. audit verdict;
2. number of BLOCKER findings;
3. number of SHOULD-FIX findings;
4. number of OPTIONAL findings;
5. whether secrets/credentials were found in HEAD;
6. whether secrets/credentials were found in reachable history;
7. whether prohibited binaries/Ghidra databases were found in HEAD;
8. whether prohibited binaries/Ghidra databases were found in reachable history;
9. whether large/sensitive derived reverse-engineering artifacts need human/legal review;
10. license status;
11. privacy/local-path findings;
12. README/navigation findings;
13. whether Git history is safe to publish as-is;
14. top remediation actions in order;
15. files created/changed by the audit;
16. confirmation repository visibility was not changed;
17. confirmation no history rewrite, tag, release, commit, or push was performed unless explicitly requested.

Do not commit or push.

## 38. Special attention points already visible at HEAD

Without prejudging the audit outcome, pay explicit attention to these currently visible facts:

- repository is private;
- `README.md` already states the proprietary-binary prohibition;
- `.gitignore` excludes `*.exe`, `*.dll`, `*.pdb`, Ghidra projects, generated exports, scratch/temp, and `.local-work/`;
- `exports/` currently contains only `.gitkeep`;
- `data/` contains sizeable derived CSV material;
- `ghidra/README.md` is large and deserves a copyright/provenance-content review;
- README repository-layout text should be checked against the actual current tree;
- no top-level `LICENSE` is currently apparent from the root inventory.

These are **audit prompts**, not predetermined findings.

## Acceptance criteria

The audit is complete when:

1. both current tree and reachable history have been assessed;
2. secrets/privacy exposure has been checked;
3. proprietary binaries and sensitive reverse-engineering artifacts have been checked;
4. large historical blobs have been inventoried;
5. data provenance/publication suitability has been assessed;
6. README/navigation/public-reader usability has been assessed;
7. evidence-status consistency has been sampled;
8. machine-local paths and private references have been scanned;
9. license status has been explicitly reported;
10. GitHub metadata/public-presentation issues have been assessed;
11. a durable audit document exists;
12. every finding has severity and remediation;
13. the audit gives a clear READY / READY AFTER MINOR FIXES / NOT READY verdict;
14. no visibility change, history rewrite, release, tag, commit, or push was performed.

Suggested eventual audit commit message after review, if the audit document itself is retained:

```text
docs: audit research repo for public release
```
