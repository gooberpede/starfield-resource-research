# SRR-012 retained allocation measurement contract

This is an offline specification for a separately authorized inspector.
Use the [dossier](SRR-012-retained-planetary-allocation-state-observation-feasibility.md)
for the verdict and the [native acquisition evidence](SRR-012-acquisition-evidence.md)
and [sample plan](SRR-012-sample-plan.md) for build-specific decoding and
sample admission. An observation has one outcome per sample and checkpoint.

## Admission and checkpoint

Bind all reads to the operator-selected 64-bit retail process using one
handle, PID and creation time. Verify the designated executable path and
file identity, account/session and independent Steam attribution under the
[prior admission model](SRR-009-retail-debugger-admission-and-stage-a.md).
Verify the pinned on-disk SHA-256 and mapped main-image identity, including
image extent, rebased headers and focused code windows for the root accessor,
reader, key comparison and writer, with relocation handling for any affected
window. Verify that module-relative roots and expected image pointers fall
in the authenticated mapping. Record data files, load order, overrides and
sample-input pin independently of executable identity. A relevant patch,
unsupported override, unknown mapping or identity failure blocks classification.
Reuse the prior evidence conventions and the pure read-side checks, including
epoch validation and region/type/extent checks. The prior debug-event file
handle is unavailable in this design. Re-establish mapping-to-file identity
from the read-only module census and the mapped path/file identity, bracketing
inspection with the same pinned file handle and mapped checks. Treat unresolved
path aliases, file replacement, inconclusive module attribution or material
mapping drift as admission failures. Disk identity and focused mapped checks
qualify the declared profile. They leave unchecked mapped pages and any
undetected preexisting backing-file substitution outside the evidence.

Use one explicit operator marker after each of the following responsive
states has been demonstrated. Hold the phase without another menu action or
load while collecting. Record marker and collection times with a monotonic
clock and a UTC anchor. Discard the interval if the operator reports or
another observation establishes loss of phase.

| Checkpoint | Required operator evidence |
| --- | --- |
| Responsive title card | Title card visible and demonstrably responsive, still before advancing to the main menu. |
| Responsive main menu | Main menu displayed and navigation responsive, before issuing the selected load. |
| Settled Save2 gameplay | Operator-selected Save2 request in the same process epoch, followed by completed loading, a responsive world and confirmed player control. Record load and settle markers. A hang, crash, aborted request, different save or exit invalidates this checkpoint. |

The three comparisons require the same authenticated build and applicable
effective inputs and logical sample keys. A new process, changed load order
or a new/replaced context must be reported. Across separate process epochs
one may compare values descriptively. They cannot bound a transition within
one process. A loader failure before player control gives no Save2 state
measurement. Historical Stage B run cards are spent.

## Bounded collection

Use the authenticated module base and resolve the owner root afresh for each
collection. Check the context anchors and registered type word, then walk the
native +0x300 range for each sampled planet up to its native upper bound or
the genuine end. Require the published pointer to equal the supported
embedded context and verify the expected context vptr. Require the type
word to resolve to the live PerBiomeData descriptor in the verified registry
and reject the unregistered sentinel. An in-range record must have the
matching edge type and stable inline payload. Apply identical identity checks
to controls and targets. Keep all candidate edges in traversal order for
audit and reject duplicate eligible matches even when the engine copy-out
would simply choose the first. Both the edge identity and inline BIOM must
agree. Resolve just the target PNDT and BIOM IDs and any relevant nonzero
RSGD FormID through the independently rooted form map. Require compatible
native record types and the PNDT +0x54 key to match the range owner.
Validate observed inputs against the pinned effective profile. Read all seven
output fields from the same component. A missing component inside a
successfully traversed range is recorded as `component_absent` and remains
indeterminate.

An exact read checks overflow, address/width alignment where warranted,
commit state, access protection, returned byte count and page/region bounds
for each requested range. Follow only demonstrated reachable pointers and
bounded lengths. Verify native ordering, traversal termination and local
descriptor/occupancy invariants before using any payload. Reject invalid
slot locators, cycles, nonprogress, impossible counts or pointer aliases,
tree-root or type drift, contradictory identities and cap exhaustion.
Derive the traversal cap from the supported fixture/data profile and enforce
an independent time, node and byte budget. A cap hit is incomplete traversal.

Bracket each independent collection with process liveness/identity, root,
discriminator and tree anchors. Recheck the touched descriptors as needed
for structural consistency. Repeat the complete selected collection from
the root, including misses and range termination, in the same marker window.
Compare process/mapping epoch, owner, registry and typed-form identity,
relevant path and range records, raw/decoded keys, eligibility inputs
and all seven raw slots. Require equality of the relevant address-bearing
structural evidence for the accepted pair. Within a pair, owner or edge
replacement or a change from empty to populated is a conflict even if the end values match
another epoch. Record any failed attempt. An initial implementation should
qualify a bounded policy of at most three pairs, with one short nonzero gap
between collections and an overall checkpoint budget. Freeze the actual
time/read caps during disposable qualification. A clean retry after a
transient read failure can supply a fresh pair within the same phase. An
observed change of owner, target identity, slot contents or index state
invalidates the marked window. Require a fresh operator marker to attempt a
new window. Repeated identical values do not rule out ABA, complete
writer cycles between reads or a writer stalled between clears and writes.
This is an evidence-supported observation interval with no atomic-snapshot
or allocator-idleness guarantee.

Conceptual observation procedure, with native layout in the
[acquisition evidence](SRR-012-acquisition-evidence.md):

```text
authenticate the process, mapped profile and inputs
require a responsive checkpoint marker for the same process epoch
collect the selected full ranges twice, resolving the owner each time
require a consistent pair and a structurally validated comparison control
for each target, require a unique edge and matching eligible payload
if the tuple meets the admitted populated-slot predicate, report populated
else if the tuple meets the admitted all-zero predicate, report qualified unpopulated
else report indeterminate with reason and observed sub-state
```

## Outcome and comparison

| Outcome | Operational rule and scope |
| --- | --- |
| `POPULATED_RESULT_OBSERVED` | All gates passed. The seven-slot tuple for the identified eligible sample satisfies the predeclared populated predicate in the sample plan. List the actual nonzero slots and qualified optional zeros. Require a complete admitted tuple. A plausible isolated value, unexpected family member, or conflicting tuple is insufficient. |
| `QUALIFIED_UNPOPULATED` | All gates passed. A unique, present, eligible payload with a predeclared nonempty expected tuple has all seven slots zero in both complete collections. The separate control may meet its populated predicate or be all zero. The result is scoped to the target identities and the sampled interval. Both fresh insertion and the allocator's intermediate clear can yield those bytes. Do not infer that allocation never ran, was idle, or is absent elsewhere. |
| `STATE_INDETERMINATE` | Any gate failed, or the value pattern lacks an admitted interpretation. Record the exact cause and useful observed sub-state, such as `context_absent`, `context_ambiguous`, `component_absent`, `ineligible`, `read_incomplete`, `potential_partial_output`, `inconsistent_pair`, `mapping_unverified` or `input_drift`. A typed hit or all-zero bytes alone are insufficient. |

For every Kreet sample use Decaran VII-b as comparison control. For
Decaran VII-b use Kreet's frozen biome. Validate the control directly on
its own keys and eligibility and require its tuple to be either admitted
populated or all zero. Its output can therefore also be zero at an
earlier checkpoint. Qualify each target
separately. A checkpoint summary lists coverage and
counts by outcome. A sample-set negative requires every predeclared
eligible target to qualify and the comparison control to pass. The control
cannot stand in for incomplete target coverage. This sample admits no
galaxy-wide negative. That would require a separately established eligible
population, complete coverage and a qualified observation window for the
larger traversal.

Join observations by effective data profile and logical PNDT/BIOM pair,
with RSGD as an admission and comparison qualifier. Record same/different
epoch and owner/edge identity separately from slot equality. Changed addresses
show that the observations used different storage locations. Record suspected
replacement and any direct lifetime evidence separately. Equal addresses
cannot establish continuous lifetime. A qualified zero followed by admitted
population establishes later state after the earlier sampled zeros. It
bounds a difference between sampled values, with possible additional
transitions within or between the windows. The established copy/reconstruction paths prevent
inferring the allocator ran within that interval from state alone.
A populated title sample supports earlier allocation in the process as the
leading explanation under the established producer evidence. A positive
result is direct evidence of retained state by the checkpoint. It supplies
neither a direct execution trace nor a serialization or persistence finding.

## Evidence record and custody

| Field group | Minimum fields |
| --- | --- |
| Profile and timing | Schema/tool version, build and mapped-check profile ID, effective data and sample-plan IDs, phase marker and its evidence, UTC anchor and monotonic start/end, process epoch and collection ordinal. |
| Acquisition | Module identity and base, root RVA and resolved owner, context anchor data and type word, range bounds, touched path/descriptor evidence and deterministic digest, termination, read budgets and observed costs. |
| Identity and data | Logical PNDT/BIOM, optional effective and observed RSGD, matching evidence, edge and payload identities, all seven raw uint32 slots plus decoded role and resource identity, eligibility evidence and expected tuple version. |
| Decision | Validation results and precise failure predicates, per-read errors and short counts, bracket and pair checks, restarts and counters, outcome, observed sub-state, comparison and scoped qualifications. Missing fields are explicit. |

Keep detailed records, raw address-bearing bytes and operator evidence under
private custody. Use an append-only ordered record with a completion marker,
then hash the bounded evidence and retain the verified prefix if sealing
fails. No scientific negative comes from an unsealed or incomplete interval.
Tracked summaries may contain build pins, static VAs/RVAs, confirmed public
record identities, sanitized counts and explicitly cleared derived results.
Exclude PID/creation time, usernames, machine and Steam/account IDs, host
filesystem file IDs, private save names/paths/hashes, local load-order details with privacy
implications, runtime virtual addresses, pointer words, raw pages, dumps
and screenshots from tracked/public output. Keep the minimum private fields
needed to reproduce an attribution and record any redaction.
