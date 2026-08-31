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

Use these evidence labels consistently:

- **PROVEN** — directly established by live execution, direct data extraction, or equivalent decisive evidence.
- **STRONG** — multiple independent observations support the interpretation, but the exact mechanism has not yet been directly observed.
- **PROVISIONAL** — a working implementation or model fits current evidence, but an important structural detail remains unresolved.
- **COUNTERFACTUAL** — a prediction from a controlled hypothetical intervention, not yet observed.
- **SUPERSEDED** — an earlier interpretation retained for research history but displaced from the current model by later evidence.

When static Ghidra interpretation conflicts with later live x64dbg execution, the live observation governs the current model. Preserve the older static result as historical evidence rather than silently deleting it.

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

Live x64dbg traces in the Creation Kit Galaxy View Apply path establish these generation anchors:

- `FUN_1415DCFB0` — **PROVEN** primary per-biome generator in the live-traced CK generation path;
- `FUN_14157F120` — **PROVEN** descendant-generation helper in that path.

The older Creation Kit trail through `ResourceViewWidget::OnApplySeed`, `FUN_1431bc320`, `FUN_140e457b0`, and generic leveled-list machinery is **SUPERSEDED / DEPRIORITISED AS PRIMARY ALLOCATION PATH**. Preserve its valid calling-convention, `TESContainer`, and leveled-list findings: it may remain legitimate CK/UI or downstream machinery. Do not assume it participates in biome allocation without new live evidence.

`SurveyAggregator` (RE ID `1016657`) and `data/planet-all-resources.csv` provide a valuable empirical resource-set oracle/proxy that appears to correspond closely to the CK/biome-generation-visible channel. That correspondence is not a proven engine contract, and the exact upstream state exposed by `SurveyAggregator` remains unresolved. Current evidence proves that the dataset omits at least some atmosphere-derived inorganic resources, so it is not a complete final planetary-resource oracle.

The next Ghidra investigation, when explicitly authorised, is to start from `FUN_1415DCFB0`, identify its immediate outer caller/enclosing planet-generation loop, and trace atmosphere-derived resource pre-population of the shared planet-wide resource container before the first per-biome call. Do not begin that investigation as part of documentation reconciliation.

## Established Tooling Baseline

The first Ghidra tooling milestone was a script that exports analysis context for a selected function.

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

### Preserve text encoding

**Preserve UTF-8 text encoding.** Do not introduce mojibake or replace valid Unicode punctuation or diagram characters with mis-decoded byte sequences. Before finalising documentation changes, inspect modified text for common mojibake patterns such as `Ã`, `Â`, `ÔÇ`, `â€`, or corrupted box-drawing and arrows. If the repository already uses valid Unicode em dashes, arrows, multiplication signs, or box-drawing characters, preserve them as valid UTF-8 rather than transliterating or re-encoding them.

If a diff or export display appears mojibaked but the repository file itself is valid UTF-8, do not “fix” the source based only on the broken display. Verify the actual file bytes or decoded text first.

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
