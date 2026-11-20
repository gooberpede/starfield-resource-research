# Research library

Read the subject needed for the question, then use the reference registers
for exact native locators. Each subject qualifies its executable, evidence
domain and tested scope.

| Subject | Use it for |
| --- | --- |
| [Generation baseline](v1-research-baseline.md) | Recovered mechanism, RNG, inputs, cache/guards and occurrence distinctions |
| [Retail execution lifecycle](retail-execution-lifecycle.md) | Startup, dispatch, scheduling, input visibility, reset and visit timing |
| [Component database](component-database.md) | Indexed allocations, typed commands, PlayerKnowledge in saves, and resource counters and colors in Locations, the orbital map and the scanner |
| [Allocation validation](allocation-validation.md) | CK/retail results, negative observations, complete census, oracle and custody |
| [Current questions](hypotheses.md) | Sole active lead register |

Reference: [provenance](PROVENANCE.md), [functions](function-register.md),
[structures](structure-register.md), [glossary](glossary.md).

Methods: [research workflow](research-workflow.md), [Ghidra](../ghidra/README.md),
[tool catalog](../tools/README.md), [current extraction](../tools/srr017/README.md),
[interchange](../tools/srr017/interchange.md),
[environment tools](../tools/srr008/README.md).

Retained [native evidence](experiments/evidence/README.md) consists of static
exports, not live traces. Completed [implementation briefs](implementation-briefs/README.md)
are indexed separately from the [readiness assessment and historical audits](audits/README.md).
Use the subjects above for scientific authority. Full retired prose remains in Git.

For the proposed repository release, see the [candidate manifest and draft
notes](release-candidate.md), [workflow dependencies](release-workflows.md)
and [clean-export test results](release-smoke-tests.md).

## Documentation sufficiency review

**COMPLETE.** An independent internal challenger verified the nine public reader routes and the documentation repairs against the retained evidence. Historical build attribution, effective-input attestation and visit timing retain their existing limits. This review covers documentation sufficiency for the proposed release.

The five-file manifest SHA-256 is `9b9dfa3435381ebca7a7ea649b0231ffe576e97280561f0d8e768edb774aa250`. Hash the substantive bytes of this index, allocation validation, component database, glossary and generation baseline. Sort by repository-relative path and hash UTF-8 lines of lowercase file SHA-256, two spaces, path and LF. Exclude this section from its heading through EOF.
