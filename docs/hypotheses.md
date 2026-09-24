# Hypotheses and Open Models

This file contains only interpretations not directly settled by decisive evidence. Labels follow `AGENTS.md`. Resolved rules are in `known-facts.md`; displaced interpretations remain below as research history.

## H1 — Zero-count reflected LIST explicitly clears atmosphere

**PROVISIONAL**

Vectera has no atmospheric resources and a zero-count reflected `LIST`. Treating a sole zero-count list as an explicit Inorganic Resources clear fits current evidence, but the generic property identifier and override semantics have not been fully decoded.

This question does not block v1.0 because the authoritative effective-atmosphere export already resolves the current corpus.

## H2 — Planner co-location shorthand

**PROVISIONAL as planner guidance; not an engine rule**

The recovered per-biome mechanism assigns at most one Common-family configuration during each processed biome invocation. This exact control-flow statement is **PROVEN** and belongs in `known-facts.md`.

It must not be shortened to “one resource family per biome” without qualification:

- atmosphere, Everywhere, and Special occurrences can coexist with Common resources;
- guard fallback can assign a family whose root is absent from that biome's effective RSGD;
- qualified planet-level `FamilyCount <= BiomeCount` evidence does not itself prove physical co-location.

A planner may conservatively avoid assuming that resources from different Common families co-occur in one normal biome, but that remains derived guidance rather than a universal allocation rule.

## Genuine Non-Blocking Open Questions

### SurveyAggregator semantic contract

The exact upstream state represented by `SurveyAggregator` and the historical `planet-all-resources.csv` snapshot remains unresolved. The dataset is a useful canonical validator for the CK/RSGD-visible channel and is proven incomplete for atmosphere-derived final membership. The snapshot is no longer distributed from this research repository; maintained canonical data lives in the sibling reproducer. Reversing its exact contract is not required for v1.0.

### Retail address/version mapping

Creation Kit addresses and control flow are proven for the live-traced CK Galaxy View Apply path. Equivalent retail `Starfield.exe` addresses and version mappings have not been independently established.

### Defensive empty-cache fallback state

**OPEN, apparently unreachable:** if a Common guard were entered with Common entries present but no generated family configurations available, current evidence does not define the engine's behavior. Recovered control flow appears to prevent this during normal execution, so it does not block v1.0.

## Resolved and Superseded Interpretations

### Atmosphere sharing the eight-entry state

**SUPERSEDED AS A HYPOTHESIS → PROVEN LIVE**

Maal VIII live tracing observed atmospheric Chlorine `000057D5` entering shared planet-wide resource-ID state before Everywhere and shuffled per-biome generation. The old proposed trace is complete and is not a current next investigation.

### Five-family check semantics

**SUPERSEDED AS PROVISIONAL → PROVEN LIVE FOR THIS GENERATION PATH**

Bara VII-d progression `0, 1, 1, 2, 2, 3, 4, 5` and the branch at five establish that the guarded structure contains five distinct generated/cached Common-family configurations. Normal cache reuse does not increment it.

### Shared-eight means no biome Common family

**SUPERSEDED**

The guard suppresses the normal Common selector but enters fallback near `0x1415DD255`, which can assign an existing family configuration.

### Everywhere uses chance or ordinary weighted selection

**SUPERSEDED**

`FUN_141548920` performs a pre-biome category-6 scan without consulting DNAM Everywhere chance or consuming RNG.

### Creation Kit leveled-list trail as primary allocation path

**SUPERSEDED / DEPRIORITISED AS PRIMARY ALLOCATION PATH**

The earlier `ResourceViewWidget::OnApplySeed → FUN_1431bc320 → FUN_140e457b0` trail retains valid calling-convention, `TESContainer`, and generic resolver evidence. Live Galaxy View Apply tracing instead establishes `FUN_1415DCFB0` as the primary per-biome generator in that operation.

### Direct RSCS seeding unresolved

**SUPERSEDED**

Live tracing proves that nonzero unsigned 32-bit RSCS directly seeds MT19937 and that the evolving state drives shuffle and generation.

### Root insertion mechanism unresolved

**SUPERSEDED**

A newly selected Common root is emitted unconditionally before descendant processing.

### Leveled lists encode the resource-family graph

**SUPERSEDED**

IRES rarity and Child Resources directly encode the recovered inorganic family graph.

### SurveyAggregator as complete final oracle

**SUPERSEDED**

The derived dataset omits at least some atmosphere-derived inorganic resources and cannot be treated as a complete final planetary-resource oracle.
