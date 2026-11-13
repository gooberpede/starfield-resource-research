# Research Workflow

Use one principal dossier under `docs/` per bounded investigation and link it
from the [documentation index](README.md). Freeze the objective, scope, and
acceptance criteria in the brief. Record the starting HEAD, index and worktree
state, including pre-existing changes. In the dossier record the baseline,
method, observations, interpretation, limitations, evidence, verification and
review disposition. Link to the baseline and evidence in place. Preserve
historical reports and qualify them in the navigation and provenance layer.

Use [provenance](PROVENANCE.md) for executable identities and claim
applicability. Capture executable product version and SHA-256, tool version,
scenario, UTC time, applicable plugin load order and versions, and the
resulting evidence or validation run. Record how each field was obtained and
what evidence could resolve each unknown. Verify the retail executable
baseline before retail native research begins.

## Local work and content verification

- Use `.local-work/codex/<investigation>/` for task inputs and check receipts,
  `.local-work/independent-review/<investigation>/` for review rounds, and
  `.local-work/diffs/` for the review patch. Confirm all are ignored and
  untracked. Preserve pre-existing local material.
- Retain selected evidence with a content identity, source, scientific purpose
  and named consumer. Record promotion when warranted. Scratch files and review
  copies have no protected status by default.
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

## Independent review and handoff

Give one independent challenger at a time the original brief and criteria,
starting state, actual diff and inventory, and access to relevant primary
records and checks. The challenger tests each criterion and the strongest
conclusion against a plausible counterexample. Keep detailed round records
local and durable scientific corrections or material objections in the
dossier or evidence record.

Use COMPLETE when every mandatory criterion passes on the substantive
snapshot. For REWORK, fix the gaps and return the revised snapshot for review.
Use BLOCKED for an unmet mandatory condition that cannot be resolved within
available authority or resources. Record attempted checks and the minimum
action needed to resume. Self-review cannot satisfy this gate.

Record the disposition, reviewer role, material limits and reviewed commit or
deterministic SHA-256 manifest in the dossier. For an uncommitted handoff
exclude only the dossier's review-status block from its own manifest and have
the reviewer verify the populated block and covered content. Renew review
after substantive changes. Describe the review as an internal challenge
against the brief and ground scientific confidence in the evidence.

Record ending HEAD, index and status. Produce a task-only patch with Git's
native output as specified in [AGENTS.md](../AGENTS.md#diff-export-encoding).
Include new task files and the completed review block. Check and apply the
patch against the starting content in an isolated context, then compare the
result byte-for-byte against the delivered files. Account for pre-existing
changes separately.
