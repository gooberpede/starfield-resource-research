# Research Workflow

Maintain the small subject library listed in the [documentation index](README.md).
Put generation, retail lifecycle, database and validation findings in their
authoritative subject; keep unresolved current questions only in
[hypotheses](hypotheses.md). Freeze the objective, scope and acceptance criteria
for bounded work in its brief. Record the starting HEAD, index/worktree and
pre-existing changes in private task receipts. Transfer durable observations,
methods, qualifications and evidence identities into the appropriate subject,
without creating a numbered dossier, duplicate register or consolidation diary.
Preserve superseded mechanisms with concise qualifications; Git retains full
historical discussion. Archive completed briefs only under an explicit task,
after verifying byte preservation and transfer of unique scientific content.

Use [provenance](PROVENANCE.md) for executable identities and claim
applicability. Capture executable product version and SHA-256, tool version,
scenario, UTC time, applicable plugin load order and versions, and the
resulting evidence or validation run. Record how each field was obtained and
what evidence could resolve each unknown. Verify the retail executable
baseline before retail native research begins.

## Local work and content verification

Tracked documentation must be self-contained. Cite tracked methods,
declared lawful inputs and durable evidence identities. Describe the
substantive findings, review disposition and limits in the authoritative subject.
Treat prior review manifests as identities of their historical snapshots.
Private scratch areas can hold new outputs and custody records.

- Use `.local-work/codex/<investigation>/` for task inputs and check receipts,
  `.local-work/independent-review/<investigation>/` for review rounds, and
  `.local-work/diffs/` for the review patch. Confirm all are ignored and
  untracked. Preserve pre-existing local material.
- Retain selected evidence with a content identity, source, scientific purpose
  and named consumer. Classify the method's files as reusable tracked
  source, versioned lawful external input, rebuildable output or private
  custody material. Track an exploratory helper once a current documented
  repeatable procedure requires it, or name its versioned, obtainable
  external replacement and verify that route. Parameterize machine-specific
  roots and keep private policies, settings and credentials in ignored
  local state. Scratch files and review copies have no protected status by
  default.
- Identify the protected primary inputs and retained outputs the task consumes.
  Pin content with SHA-256 or Git objects, using an existing MD5 for historical
  reconciliation. Verify before use or at the relevant measurement boundary
  and recheck after work. Compare preserved tracked paths with the starting
  state. Equal content passes despite incidental timestamp changes. If metadata
  is an experimental condition, record and check it explicitly. For
  intentionally mutable inputs, specify the starting identity and expected
  transition in the brief. Keep checks scoped to the task and its dependencies.

## Free space

Before any material write, measure caller-available bytes on both C: and D:
with `[IO.DriveInfo]::new('C').AvailableFreeSpace` and the corresponding D:
query. On each drive subtract projected writes, temporary copies, and output
growth. Proceed only if both projections are at least 40,000,000,000 bytes
and both readings are available. For sustained writes, recheck during
execution and before every material write stage, with enough margin to stop
before crossing the floor. If either drive would fall below it or a reading
is unavailable, refuse or stop the operation, preserve inputs and useful
partial output, and record the affected drive and next safe step. Lightweight
documentation and read-only identity checks may continue. This floor applies
to available space on the drives. There is no fixed size cap on `.local-work/`.

## Pseudocode, diagrams and structure records

- Keep optional pseudocode in its authoritative subject. Use original prose and research
  aliases to express control or data semantics. Cite native locators for
  branches, ordering, exits, effects and fallbacks, and mark unknowns. Use
  the reproducer only as a qualified comparison where retail evidence leaves
  a gap.
- Use Mermaid when a control-flow, data-flow or structure relationship
  diagram improves on the surrounding prose or table. Label direct calls,
  predicates, indirect dispatch and unresolved links in text or a legend.
  Identify static reachability and observed execution explicitly.
- Validate Mermaid syntax, render the diagram and visually inspect the
  result with a documented available method. If rendering is unavailable,
  record the limitation and perform the available syntax and structural
  checks. Dependency installation or external validation requires separate
  approval.
- Record reusable fields in the [structure register](structure-register.md)
  with a build pin, base and offset unit, access width and operation,
  evidence locator, confidence and unknowns. Identify proposed aliases and
  keep layout observations distinct from ownership and lifetime hypotheses.
  Add reusable terms to the [glossary](glossary.md) when they resolve an
  ambiguity. Link to existing evidence and keep review metadata distinct.

## Live observation and recovery

Justify each mandatory operational prerequisite by scientific validity,
game/save protection or evidence integrity. Reuse previously qualified
mechanisms. New privileged setup, credentials, external services or other
infrastructure require explicit maintainer approval before they become
mandatory. A chosen precaution alone does not establish a requirement.

An admission or safety gate that can stop acquisition should retain an
attributable predicate and cause at a verifiable durable boundary. If
durability fails, report that failure and retain the earlier trusted
prefix. Assess scientific evidence, coverage, target exit, debugger
retirement and cleanup separately. An abnormal cleanup can coexist with a
valid earlier seal.

With explicit authority, an orphaned observer may be administratively
closed after independently confirming the exact target has exited and
verifying the observer identity and evidence. Use a proportionate
procedure. Record the actual exit status and distinguish it from normal
retirement. A live target requires its own authorization and recovery
plan.

## Publication

For each candidate claim, record build applicability, essential evidence,
public verification route, and holds. Start the route from the public
repository and named versioned public dependencies or lawfully obtained
inputs. Walk at least one relevant claim using those sources. Hold an affected
claim if an essential source is missing or an identity needed for the claim
is unresolved. Record inspection/use authority separately from redistribution
clearance and credit known substantive contributions in the
[third-party notices](../THIRD_PARTY_NOTICES.md). Hold material with unclear
rights or privacy exposure. Apply any research exception only to its specific
material and purpose. Exclude unauthorized third-party content, proprietary
payloads and means to reconstruct proprietary material. Leave release
numbering, tagging and publication to the maintainer.

Label the verification route separately from epistemic confidence:
**Reproducible method** means tracked source and declared lawful inputs
can rerun the method. **Custody-backed historical observation** means
retained, hash-identified evidence supports a particular past result.
**Provisional/unresolved claim** identifies the missing evidence and what
could resolve it. These routes can coexist in one subject.

## Independent review and handoff

Give one independent challenger at a time the original brief and criteria,
starting state, actual diff and inventory, and access to relevant primary
records and checks. The challenger tests each criterion and the strongest
conclusion against a plausible counterexample. Scope publication checks to
the change. Inspect new imports, commands, prerequisites, clean-checkout
viability, links and archive entries, privacy and third-party rights where
they affect the task. Keep detailed round records
local and durable scientific corrections or material objections in the
dossier or evidence record.

Use COMPLETE when every mandatory criterion passes on the substantive
snapshot. For REWORK, fix the gaps and return the revised snapshot for review.
Use BLOCKED for an unmet mandatory condition that cannot be resolved within
available authority or resources. Record attempted checks and the minimum
action needed to resume. Self-review cannot satisfy this gate.

Record the disposition, reviewer role, material limits and reviewed commit or
deterministic SHA-256 manifest in the authoritative subject. For an uncommitted handoff
exclude only the subject's review-status block from its own manifest and have
the reviewer verify the populated block and covered content. Renew review
after substantive changes. Describe the review as an internal challenge
against the brief and ground scientific confidence in the evidence.

Record ending HEAD, index and status. Produce a task-only patch with Git's
native output as specified in [AGENTS.md](../AGENTS.md#diff-export-encoding).
Include new task files and the completed review disposition. Check and apply the
patch against the starting content in an isolated context, then compare the
result byte-for-byte against the delivered files. Account for pre-existing
changes separately.
