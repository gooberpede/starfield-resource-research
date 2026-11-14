# Documentation Index

The current baseline governs present conclusions. Experiment notes and
implementation briefs preserve the route to those conclusions, including
superseded interpretations, but are not substitutes for the baseline.

## Current Authoritative Baseline

- [v1 research baseline](v1-research-baseline.md) — current recovered model,
  validation scope, evidence boundaries, and open questions.
- [Known facts](known-facts.md) — established observations classified with the
  repository evidence vocabulary.
- [Hypotheses](hypotheses.md) — unresolved models and non-blocking questions.
- [Function register](function-register.md) — native anchors, addresses, and
  evidence status.
- [Provenance and applicability register](PROVENANCE.md#applicability-register) — executable identities,
  tool and data provenance, and the scope of each evidence class.

- [Glossary](glossary.md) — research terminology, record signatures and address domains.
- [Native structure register](structure-register.md) — build-qualified field and relationship evidence.

## Investigation Dossiers

- [SRR-001 executable identity and research foundations](SRR-001-executable-identity.md)
- [SRR-002 retail static reconnaissance](SRR-002-retail-static-reconnaissance.md)
- [SRR-003 retail allocator invocation and dispatch](SRR-003-retail-allocator-invocation-and-dispatch.md)
- [SRR-005 retail allocator live-observation preparation](SRR-005-live-observation-preparation.md)
- [SRR-006 four-site hardware observer](SRR-006-four-site-hardware-observer.md)
- [SRR-007 retail launch boundary and Stage A qualification](SRR-007-retail-launch-and-stage-a-qualification.md)
- [Research workflow](research-workflow.md)

## Experiments and Evidence

- [Experiment index](experiments/)
- [Focused evidence bundles](experiments/evidence/)

Experiment notes may contain hypotheses later marked **SUPERSEDED**. Focused
evidence bundles preserve selected supporting artifacts; they are deliberately
not complete executable or debugger captures.

## Historical Implementation Briefs

[Implementation briefs](implementation-briefs/) are preserved task
specifications and rationale from earlier work. They may contain transient
instructions, machine paths, or assumptions that are no longer current. Do
not treat them as project authority; return to the
[v1 research baseline](v1-research-baseline.md) for the current model.

## Tooling

- [Ghidra scripts and reproduction guide](../ghidra/README.md)
- [Executable reproducer, tests, canonical data, and extraction tooling](https://github.com/gooberpede/starfield-resource-reproducer)

The research repository owns evidence status, native-function findings,
provenance, and history. The sibling reproducer owns the executable reference
model, regression suite, and maintained production datasets/tooling.
