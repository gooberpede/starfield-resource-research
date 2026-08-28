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
- validate candidate algorithms against authoritative runtime observations;
- ultimately support a planner that can reason about likely resource co-location.

## Current Model

Known game data relationships include:

```text
PNDT
 ├─ planet-level data
 ├─ biome references
 └─ Resource Creation Seed (RSCS)

BIOM
 └─ references resource-generation data

RSGD
 └─ defines resource-generation possibility space
```

The exact runtime transformation from these inputs to final per-biome resource membership remains unresolved.

## Current Reverse-Engineering Anchors

The most promising Creation Kit trail found so far is:

```text
ResourceViewWidget::OnApplySeed
    ↓
FUN_1431bc320
    ↓
FUN_140e457b0
    ↓
generic leveled-list evaluation machinery
```

A separate runtime function, `SurveyAggregator` (RE ID `1016657`), can enumerate the final resources associated with a planet. It is useful as an authoritative observer of results, but it is not currently assumed to perform the biome allocation itself.

See `docs/function-register.md` for the working function register.

## Empirical Constraints

Independent extraction and analysis have established useful constraints on any candidate algorithm.

Examples include:

- every observed inorganic resource-family descendant occurs on a planet that also contains that family's root;
- across the authoritative analysed dataset, the number of represented resource families never exceeds the number of biomes on the same body;
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

## First Milestone

Build a Ghidra script that exports complete analysis context for one selected function without modifying the Ghidra program.

The first target should be `FUN_1431bc320`.

The export should include, at minimum:

- function address and name;
- decompiled pseudocode;
- callers;
- callees;
- referenced strings;
- referenced globals;
- useful constants.

Once this works reliably, extend it to recursively export a bounded call neighbourhood.

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
comparison against authoritative runtime observations
      ↓
counterexamples
      ↓
refined Ghidra investigation
```

The aim is to replace ad hoc manual exploration with repeatable evidence-producing experiments.

## Repository Policy

Do not commit proprietary Starfield binaries or Ghidra project databases containing imported game binaries.

Keep generated bulk exports out of Git unless they are deliberately selected as small, useful research evidence.
