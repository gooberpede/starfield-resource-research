# Starfield Resource Research

This repository is the durable evidence and research-history record for reverse engineering Starfield's runtime inorganic resource-generation system. The central question is:

> How does Starfield transform planet, biome, resource-generation, atmosphere, and seed data into the final per-biome inorganic resource set at runtime?

The executable reference model lives in the sibling `starfield-resource-reproducer` repository. Start with `docs/v1-research-baseline.md` for the current evidence state.

## Status

**Core inorganic generation algorithm: recovered and independently validated within the v1.0 scope.**

```text
canonical planet-wide validation: 1,444 / 1,444 exact
mismatches:                         0
errors:                             0
targeted pathological CK regressions: exact
fresh CK + retail holdout:          10 / 10 exact
```

The holdout is an independent corroboration layer. Creation Kit addresses and control flow are proven for the live-traced CK Galaxy View Apply path; they are not asserted to be retail `Starfield.exe` addresses.

No known algorithmic hole remains within the current v1.0 scope. Future counterexamples, executable/version drift, and new evidence remain valid research targets.

## Recovered Model

```text
PNDT / BIOM / RSGD / IRES / ATMO
        ↓
nonzero unsigned RSCS seeds MT19937
        ↓
atmosphere prepopulation
        ↓
Everywhere/category-6 pre-pass
        ↓
PNDT-order biome construction
        ↓
deterministic biome shuffle
        ↓
per shuffled biome:
    Special/category-5 selector
        ↓
    Special shared-state insertion
        ↓
    five-tree guard
        ↓
    shared-eight guard
        ↓
    normal Common selector
        OR
    guard fallback family assignment
        ↓
    new family generation
        OR
    ordinary cached-family reuse
        OR
    guarded cached-family reuse
```

PNDT `Resource Generation` overrides `BIOM.RNAM` for that biome; the two RSGDs are not merged. Stored RSGD order is significant. Atmosphere, Everywhere, Special, Common roots, and emitted descendants share the guarded planet-wide resource-ID state. The validated model tracks unique FormID occupancy separately from provenance occurrences.

Keep these concepts distinct:

- planet-wide resource identity;
- family configuration cache and configuration origin;
- biome-local Common-family assignment;
- Everywhere, Special, and atmosphere occurrence.

The Common assignment mechanisms are `NEW_FAMILY`, `NORMAL_CACHE_REUSE`, `GUARD_MATCHED_FALLBACK`, `GUARD_GENERAL_FALLBACK`, and `NO_COMMON_ASSIGNMENT`.

## Native Anchors

The primary CK runtime anchors are:

```text
FUN_14152CBC0  enclosing orchestration and prepopulation
FUN_141548920  Everywhere/category-6 pre-pass
FUN_1415DCFB0  primary per-biome generator
FUN_141580660  Special/Common weighted selector
FUN_14157F120  descendant-generation helper
FUN_14154C710  guard-fallback candidate construction
FUN_14015B4A0  guard-fallback cached-family selection
FUN_140924800  MT19937 → binary32 probability conversion
```

The older static trail remains **SUPERSEDED / DEPRIORITISED AS PRIMARY ALLOCATION PATH**:

```text
ResourceViewWidget::OnApplySeed
    ↓
FUN_1431bc320
    ↓
FUN_140e457b0
    ↓
generic leveled-list machinery
```

Its calling-convention, `TESContainer`, and leveled-list findings remain valid historical evidence and may describe CK/UI or downstream machinery.

## Evidence and Oracle Boundaries

Evidence labels are **PROVEN**, **STRONG**, **PROVISIONAL**, **COUNTERFACTUAL**, and **SUPERSEDED**; see `AGENTS.md`.

`SurveyAggregator` (RE ID `1016657`) and `data/planet-all-resources.csv` are valuable validation evidence for the CK/RSGD-visible channel. The dataset is proven incomplete for atmosphere-derived final membership, and the exact upstream `SurveyAggregator` semantic contract remains unresolved. Oracle data must never become generation logic.

Missing PNDT/effective-RSGD input means biome-local generation is unknown or unavailable, not empty. Independently sourced atmosphere can still be reported. Volii Alpha is the negative control for this input-boundary rule, not evidence about its actual terrestrial biome allocation.

## Repository Contract

```text
starfield-resource-research
    owns evidence status, trace provenance, and native function findings

starfield-resource-reproducer
    owns the executable reference model and regression suite
```

A future settled-rule change must be reconciled across both repositories: reproduce the counterexample, preserve and classify the evidence here, update the research baseline, issue an implementation brief, update the reproducer and regressions, then rerun canonical and holdout validation.

## Current Research Posture

- preserve raw evidence and superseded interpretations;
- investigate new falsifications or executable/version drift;
- support downstream planner and data tooling;
- keep non-blocking questions clearly separated from recovered generation semantics.

Current non-blocking questions are summarized in `docs/v1-research-baseline.md` and `docs/hypotheses.md`.

## Repository Layout

```text
.
├─ AGENTS.md
├─ README.md
├─ docs/
│  ├─ v1-research-baseline.md
│  ├─ known-facts.md
│  ├─ hypotheses.md
│  ├─ function-register.md
│  └─ experiments/
├─ ghidra/scripts/
├─ exports/
└─ tools/
```

Do not commit proprietary Starfield binaries, extracted proprietary assets, or Ghidra project databases containing imported game binaries.
