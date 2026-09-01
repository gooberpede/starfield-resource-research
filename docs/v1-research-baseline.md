# v1 Research Baseline

## Purpose and Scope

This is the first orientation document for the recovered v1.0 inorganic-resource-generation model. It summarizes settled evidence without duplicating every experiment.

The scope covers PNDT/BIOM/effective-RSGD inputs, IRES hierarchy, effective inorganic atmosphere, nonzero RSCS MT19937 state, biome shuffle, Everywhere, Special, Common families and descendants, family caching, Common guards and fallback, biome-local assignment provenance, and planet-wide membership.

It does not cover organics, flora/fauna spawning, extractor placement, vein geometry, arbitrary mods, future executable/data versions, or proof that Creation Kit addresses equal retail `Starfield.exe` addresses.

## Proven Algorithm

```text
PNDT / BIOM / RSGD / IRES / ATMO
        ↓
nonzero unsigned RSCS seeds MT19937
        ↓
atmosphere prepopulation into shared resource-ID state
        ↓
Everywhere/category-6 pre-pass without RNG
        ↓
PNDT-order biome construction
        ↓
deterministic biome shuffle
        ↓
per shuffled biome:
    Special/category-5 ordered weighted selector
        ↓
    immediate Special shared-state insertion
        ↓
    five-distinct-cached-Common-family guard
        ↓
    shared-eight-resource guard
        ↓
    normal Common/category-0 selector
        OR
    guarded cached-family fallback
        ↓
    NEW_FAMILY
        OR NORMAL_CACHE_REUSE
        OR GUARD_MATCHED_FALLBACK
        OR GUARD_GENERAL_FALLBACK
        OR NO_COMMON_ASSIGNMENT
```

PNDT per-biome Resource Generation overrides `BIOM.RNAM`; the sources are not merged. Special and Common selection each draw before enumerating stored RSGD entries, filter by category, accumulate unnormalized `Chance / 100`, and take the first `roll < cumulative` entry.

A new Common family configuration is generated once and cached at planet scope. Normal selector cache hits reuse it without descendant RNG. When either Common guard fires, fallback near `0x1415DD255` prefers cached roots matching Common roots in the current effective RSGD, otherwise chooses among all cached families; no Common roots means no Common assignment. Fallback selection consumes a float32-scaled probability draw even for one candidate.

Keep planet-wide resource identity, family configuration origin, current biome assignment, and atmosphere/Everywhere/Special occurrence distinct.

## Native Function Anchors

| Function | Evidence status and role |
|---|---|
| `FUN_14152CBC0` | PROVEN STATIC enclosing orchestration; PROVEN LIVE atmosphere → Everywhere → biome order |
| `FUN_141548920` | PROVEN LIVE Everywhere/category-6 prepopulation helper |
| `FUN_1415DCFB0` | PROVEN LIVE primary per-biome generator |
| `FUN_141580660` / `FUN_14157C470` | PROVEN Special/Common weighted selector and ordered scanner |
| `FUN_14157F120` | PROVEN LIVE descendant helper |
| `FUN_14154C710` | PROVEN LIVE guard-fallback candidate construction |
| `FUN_14015B4A0` | PROVEN LIVE float-scaled fallback family selector |
| `FUN_1401190CD` | PROVEN thunk to `FUN_140924800` |
| `FUN_140924800` | PROVEN MT19937-to-binary32 probability conversion |

These addresses belong to the investigated Creation Kit executable. Retail output is an independent corroboration layer, not an address-equivalence proof.

## Evidence Stack

The durable evidence stack is:

1. live x64dbg observations in the CK Galaxy View Apply path;
2. focused read-only Ghidra control-flow and dataflow exports;
3. authoritative xEdit PNDT/BIOM/RSGD/IRES/ATMO extraction;
4. targeted CK biome regression observations;
5. full canonical planet-wide validation;
6. fresh CK biome plus retail planetary-scan holdout validation.

When static interpretation conflicts with live observation, live execution governs the current model and the older static interpretation remains preserved as historical evidence.

The validated shared-occupancy model deduplicates unique IRES FormIDs across modeled origins while retaining every provenance occurrence. The shared count and guard at eight are proven; universal duplicate-slot behavior across every possible insertion site has not been directly traced and remains a strong full-corpus-validated model boundary.

## Validation Baseline

```text
canonical planet-wide: 1,444 / 1,444 exact
mismatches:            0
errors:                0
targeted CK regressions: exact
fresh holdout:         10 / 10 exact CK + retail
```

Historical progression:

```text
pre-07B  1,281 / 1,444
07B      1,426 / 1,444
08A      1,441 / 1,444
08B      1,442 / 1,444
08C+     1,444 / 1,444
08D/D.1  planet-wide unchanged; pathological biome assignments exact
```

The fresh holdout is recorded in `docs/experiments/v1-holdout-validation.md`.

## Input and Oracle Boundaries

`planet-all-resources.csv` is a canonical validator for the CK/RSGD-visible channel used by the reproducer. It is proven incomplete for atmosphere-derived final membership, its upstream `SurveyAggregator` semantic contract is unresolved, and it must never be consulted during generation.

Missing PNDT/biome/effective-RSGD input means biome-local generation is unknown or unsupported, not empty. Volii Alpha is absent from the generation corpus while independent atmosphere data provides Benzene and Water; reporting those known atmospheric resources without fabricating terrestrial biome assignments validates the model's input boundary. It is not evidence about Volii Alpha's actual terrestrial allocation or a recovered native engine rule.

## Non-Blocking Open Questions

- exact upstream semantic contract exposed by `SurveyAggregator`;
- generic interpretation of a zero-count ATMO reflected `LIST` clear;
- retail `Starfield.exe` native-address equivalence and version mapping;
- **OPEN, apparently unreachable:** guard plus Common entries plus an empty global family cache.

None blocks v1.0.

## Major Superseded Interpretations

- The `ResourceViewWidget::OnApplySeed → FUN_1431bc320 → FUN_140e457b0` trail is not the primary allocator in the tested Galaxy View Apply path. Its valid static findings remain preserved.
- Atmosphere sharing the guarded state and its insertion order are no longer hypotheses; Maal VIII live tracing proved them.
- Everywhere does not use DNAM chance or ordinary weighted selection.
- The five-tree structure is no longer merely provisional; in this path it is the collection of five distinct generated/cached Common-family configurations.
- Shared-eight fallback does not necessarily mean an empty biome Common result.
- SurveyAggregator output is not a complete final resource oracle.

## Cross-Repository Contract

```text
starfield-resource-research
    owns evidence status, trace provenance, native function findings,
    superseded interpretations, and the research baseline

starfield-resource-reproducer
    owns the executable reference model, diagnostics, and regression suite
```

Future settled-rule changes must proceed in order:

1. reproduce a counterexample;
2. add or update research evidence;
3. classify evidence;
4. reconcile this baseline;
5. issue an implementation brief;
6. update the reproducer;
7. add regression coverage;
8. rerun canonical and holdout validation.

Do not independently “fix” one repository while leaving the other with contradictory settled semantics.

## Current Posture

The core inorganic algorithm is recovered and independently validated within v1.0 scope. Current work should preserve evidence, investigate genuine falsifications or executable/version drift, and support downstream planner/data tooling. No claim is made that future discovery is impossible.
