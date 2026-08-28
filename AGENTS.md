# AGENTS.md

## Project Purpose

This repository supports reverse engineering of Starfield's runtime inorganic resource-generation system, with particular focus on how the game determines which inorganic resources are available in each biome.

The primary research question is:

> How does Starfield transform planet, biome, resource-generation, and seed data into the final per-biome inorganic resource set at runtime?

The project uses Ghidra for static analysis, small scripts for repeatable extraction, Git for research history, and Codex for implementation and analysis support.

## Working Principles

### Separate facts from hypotheses

Do not treat an inference, working theory, or pattern as an established fact.

- Confirmed observations belong in `docs/known-facts.md`.
- Unproven explanations and models belong in `docs/hypotheses.md`.
- If evidence changes, update the relevant file rather than silently rewriting history.

When reporting a conclusion, state whether it is directly observed, strongly supported, tentative, or speculative.

### Preserve evidence

Prefer outputs that can be reproduced from Ghidra or game data.

When a script or analysis produces a finding:
- record the source function/address where practical;
- preserve relevant decompiled output or machine-readable metadata;
- document the command or procedure used;
- avoid conclusions that depend only on transient GUI state.

### Do not rename functions casually

Unknown Ghidra functions such as `FUN_1431bc320` must retain their original generated names unless there is strong evidence for a more descriptive name.

If proposing a semantic name:
- keep the original address/name in the function register;
- explain the evidence;
- distinguish a proposed alias from a confirmed engine symbol.

### Prefer small, verifiable steps

Do not attempt to reverse engineer the entire resource-generation system in one pass.

Prefer narrowly scoped tasks such as:
- export one function and its immediate context;
- identify callers and callees;
- enumerate referenced globals;
- trace one argument through a call chain;
- find accesses to a specific structure offset;
- compare one hypothesis against known runtime observations.

Each step should produce an inspectable result before expanding the scope.

### Keep Ghidra scripts non-destructive by default

Analysis scripts should not modify the Ghidra program unless explicitly requested.

Default scripts should:
- read analysis state;
- export metadata;
- export decompilation;
- enumerate references;
- create external report files.

If a script does alter symbols, types, comments, labels, or function names, that behavior must be explicit and documented.

### Favor machine-readable exports

Where possible, export analysis results as JSON, CSV, text, or other plain formats that can be searched by Codex, diffed in Git, processed by scripts, and compared across experiments.

Generated bulk exports may remain untracked if they are large or noisy.

### Do not commit proprietary game binaries

Do not commit:
- `Starfield.exe`;
- Bethesda DLLs;
- extracted proprietary game assets;
- Ghidra project databases containing imported binaries;
- other redistributable game binaries.

The repository should contain scripts, notes, schemas, derived metadata, and small research outputs only.

## Current Investigation Direction

The most promising static-analysis trail begins with the Creation Kit resource preview path:

- `ResourceViewWidget::OnApplySeed`
- `FUN_1431bc320`
- `FUN_140e457b0`

Previous work suggests this path eventually reaches generic leveled-list evaluation machinery.

A separate runtime anchor is:

- `SurveyAggregator`
- RE ID `1016657`

`SurveyAggregator` provides authoritative planet-wide final resource observations, but it is not currently believed to be the allocation algorithm itself.

## First Tooling Milestone

The first Ghidra tooling milestone is a script that exports analysis context for a selected function.

At minimum, export:

- function name;
- function address;
- decompiled pseudocode;
- callers;
- callees;
- referenced strings;
- referenced globals;
- useful scalar constants;
- referenced types/structures where available.

A suitable output layout is:

```text
exports/functions/<function-name-or-address>/
    metadata.json
    decompiled.c
    callers.json
    callees.json
    strings.json
    globals.json
    constants.json
```

The design should be easy to extend later to recursive neighbourhood export.

## Documentation Expectations

When adding or changing analysis tooling:

1. Explain what the tool does.
2. Explain how to run it.
3. State what it reads and writes.
4. State whether it modifies the Ghidra project.
5. Include a small example where practical.

When making a research claim:
1. update `docs/function-register.md` if a specific function is involved;
2. update `docs/known-facts.md` only when the result is established;
3. otherwise update `docs/hypotheses.md` or an experiment note.

## Scope Discipline

The practical end goal is not merely to understand Starfield internals for their own sake. The reconstructed model should ultimately help determine which resources can be expected to co-occur at an outpost location without biome-boundary hunting.

Avoid spending effort on unrelated engine systems unless they become necessary to explain resource allocation.
