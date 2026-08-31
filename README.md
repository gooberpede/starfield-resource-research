# Starfield Resource Research

This repository contains tooling and research notes for reverse engineering Starfield's runtime inorganic resource-generation system.

The central question is:

> How does Starfield determine exactly which inorganic resources are available in each biome?

The final resource set is not stored directly as a simple planet/biome/resource table in `Starfield.esm`. Instead, the game combines planet, biome, resource-generation, and seed data at runtime.

This project is intended to make that process reproducible and analysable without relying on a manual cycle of opening functions in Ghidra, copying decompiled code into chat, and choosing the next function by hand.

## Goals

The project aims to:

- automate extraction of useful analysis context from Ghidra;
- build a durable register of relevant Starfield functions and addresses;
- distinguish confirmed observations from working hypotheses;
- trace the runtime path that assigns inorganic resource families and family members to biomes;
- validate candidate algorithms against provenance-qualified runtime observations;
- ultimately support a planner that can reason about likely resource co-location.

## Current Model

Evidence labels used throughout the repository are **PROVEN**, **STRONG**, **PROVISIONAL**, **COUNTERFACTUAL**, and **SUPERSEDED**. See `AGENTS.md` for their definitions.

The proven data path and override precedence are:

```text
PNDT
 ├─ RSCS
 └─ ordered biome entries
        ↓
      BIOM
        ↓
      RSGD
```

For each biome, a non-null PNDT Resource Generation override replaces `BIOM.RNAM`; the two RSGDs are not merged. Non-zero `RSCS` directly seeds unsigned 32-bit MT19937. The same evolving state drives the biome shuffle and later generation draws.

In the live-traced Creation Kit Galaxy View Apply path, `FUN_1415DCFB0` is the proven primary per-biome generator and `FUN_14157F120` is its proven descendant helper. IRES records provide rarity and child-resource graph data. Common roots are inserted unconditionally, descendant choices traverse this graph, and a planet-level family cache prevents repeated descendant generation for a reused root. The reconstructed behaviour agrees with known game/resource results; these addresses are not presented as independently traced retail `Starfield.exe` addresses.

The traced path has a proven eight-entry internal resource-container limit and a proven `count >= 5` guard on a structure associated with generated/cached Common-family configurations. Interpreting the latter as a general five-family or five-generated-family-configuration limit remains provisional. Atmospheric resources are strongly supported as sharing the eight-entry planet-wide capacity, although their exact insertion function and order remain unresolved.

## Current Reverse-Engineering Anchors

The current primary runtime anchors are:

```text
FUN_1415DCFB0  primary per-biome generator
FUN_14157F120  descendant helper
```

The older static trail is retained as **SUPERSEDED / DEPRIORITISED AS PRIMARY ALLOCATION PATH**:

```text
ResourceViewWidget::OnApplySeed
    ↓
FUN_1431bc320
    ↓
FUN_140e457b0
    ↓
generic leveled-list evaluation machinery
```

Its low-level `TESContainer`, calling-convention, and leveled-list findings remain valid historical evidence and may describe legitimate CK/UI or downstream machinery. Live Galaxy View Apply tracing did not exercise it as the primary allocation trail.

`SurveyAggregator` (RE ID `1016657`) and `data/planet-all-resources.csv` remain useful empirical proxies for reconciling the CK/biome-generation-visible channel, but that correspondence is not a proven semantic contract. The exact upstream state exposed by `SurveyAggregator` remains unresolved. The dataset is not a complete final inorganic-resource oracle: atmosphere-derived resources can be absent.

See `docs/function-register.md` for the working function register.

## Empirical Constraints

Independent extraction and analysis have established useful constraints on any candidate algorithm.

Examples include:

- every observed inorganic resource-family descendant occurs on a planet that also contains that family's root;
- across the qualified SurveyAggregator-derived proxy dataset, the number of represented resource families never exceeds the number of biomes on the same body;
- many bodies have exactly as many represented resource families as biomes.

These observations strongly motivate investigation of a biome/family allocation step, but they do not by themselves prove one fixed family per biome.

See:
- `docs/known-facts.md`
- `docs/hypotheses.md`

## Repository Layout

```text
.
├─ AGENTS.md
├─ README.md
├─ docs/
│  ├─ known-facts.md
│  ├─ hypotheses.md
│  └─ function-register.md
├─ ghidra/
│  └─ scripts/
├─ exports/
└─ tools/
```

Suggested use:

- `docs/` — durable research notes and evidence summaries;
- `ghidra/scripts/` — Ghidra extraction and analysis scripts;
- `exports/` — generated analysis output;
- `tools/` — supporting parsers, comparators, graph tools, and validation utilities.

## Next Investigation (Not Yet Executed)

Starting from proven generator `FUN_1415DCFB0`, identify its immediate outer caller or enclosing planet-generation loop. Determine what happens between operation entry and the first per-biome call, focusing on the path from effective ATMO Inorganic Resources into the shared planet-wide resource container. Maal VIII is the preferred live case because atmospheric Chlorine appears in its in-game survey but not in the CK biome Resource Generation view or old plugin output.

Keep origin channels distinct during validation: `AtmosphericResources`, `BiomeGeneratedResources`, `EverywhereResources`, `SpecialResources`, and `FinalPlanetaryResources`. Deduplicate FormIDs only for final player-facing membership.

## Research Method

The intended loop is:

```text
Ghidra analysis
      ↓
candidate interpretation
      ↓
candidate algorithm/model
      ↓
implementation or prediction
      ↓
comparison against provenance-qualified runtime observations
      ↓
counterexamples
      ↓
refined Ghidra investigation
```

The aim is to replace ad hoc manual exploration with repeatable evidence-producing experiments.

## Repository Policy

Do not commit proprietary Starfield binaries or Ghidra project databases containing imported game binaries.

Keep generated bulk exports out of Git unless they are deliberately selected as small, useful research evidence.
