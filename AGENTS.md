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

The v1.0 inorganic generation algorithm is recovered and independently validated within its defined scope:

```text
1,444 / 1,444 canonical planet-wide exact
all targeted pathological CK biome regressions exact
10 / 10 fresh CK + retail holdout exact
```

Start with `docs/v1-research-baseline.md`. Live x64dbg traces in the Creation Kit Galaxy View Apply path establish these primary anchors:

- `FUN_14152CBC0` — enclosing orchestration and atmosphere/Everywhere prepopulation;
- `FUN_141548920` — **PROVEN LIVE** Everywhere/category-6 pre-pass;
- `FUN_1415DCFB0` — **PROVEN LIVE** primary per-biome generator;
- `FUN_141580660` — **PROVEN** Special/Common weighted selector;
- `FUN_14157F120` — **PROVEN LIVE** descendant-generation helper;
- `FUN_14154C710` — **PROVEN LIVE** guard-fallback candidate construction;
- `FUN_14015B4A0` — **PROVEN LIVE** float-scaled fallback family selection.

The older Creation Kit trail through `ResourceViewWidget::OnApplySeed`, `FUN_1431bc320`, `FUN_140e457b0`, and generic leveled-list machinery is **SUPERSEDED / DEPRIORITISED AS PRIMARY ALLOCATION PATH**. Preserve its valid calling-convention, `TESContainer`, and leveled-list findings: it may remain legitimate CK/UI or downstream machinery. Do not assume it participates in biome allocation without new live evidence.

`SurveyAggregator` (RE ID `1016657`) and `data/planet-all-resources.csv` provide a valuable canonical validator for the CK/RSGD-visible channel used by the reproducer. The exact upstream semantic contract remains unresolved, and the dataset is proven incomplete for atmosphere-derived final membership. It is validation evidence, never generation logic.

The earlier Maal VIII atmosphere trace is complete: atmospheric Chlorine `000057D5` was observed entering shared resource-ID state before Everywhere and shuffled per-biome generation. Do not preserve that resolved trace as an active next investigation.

Current posture is to preserve evidence, investigate new falsifications or executable/version drift, and support downstream planner/data tooling. Do not silently reopen settled rules merely because a non-blocking semantic detail remains unknown.

## Protected v1.0 Baseline

Keep these generation concepts separate:

- planet-wide resource identity;
- family configuration cache;
- family configuration origin;
- biome-local Common-family assignment;
- atmosphere, Everywhere, and Special occurrence.

Do not merge the following RNG mechanisms:

1. biome-shuffle integer rejection/modulo;
2. MT19937-to-binary32 probability conversion;
3. Special/Common ordered cumulative selector;
4. descendant float32-scaled candidate index;
5. guard-fallback float32-scaled cached-family index.

Additional guardrails:

- do not treat Creation Kit addresses as retail `Starfield.exe` addresses;
- do not infer an empty result from missing PNDT/effective-RSGD input;
- do not use validation-oracle data as generation input;
- do not change the recovered algorithm without new evidence and a reproducible counterexample;
- preserve superseded evidence rather than deleting history.

The research repository owns evidence status, trace provenance, and native-function findings. The sibling `starfield-resource-reproducer` owns the executable reference model and regression suite. A future settled-rule change must reconcile both repositories:

```text
1. reproduce a counterexample
2. add or update research evidence
3. classify the evidence
4. reconcile the research baseline
5. issue an implementation brief
6. update the reproducer
7. add a regression
8. rerun canonical and holdout validation
```

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

**Preserve UTF-8 text encoding.** Do not introduce mojibake or replace valid Unicode punctuation or diagram characters with mis-decoded byte sequences. Before finalising documentation changes, inspect modified text for common mojibake patterns such as `Ã`, `Â`, `ÔÇ`, `â€`, `ÔÇö`, `ÔÇô`, or corrupted box-drawing and arrows. If the repository already uses valid Unicode em dashes, arrows, multiplication signs, or box-drawing characters, preserve them as valid UTF-8 rather than transliterating or re-encoding them.

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

### Diff export encoding

When producing a diff for external review, do not pipe `git diff` through PowerShell `Out-File`, `Set-Content`, or similar text commands. Use Git's native `--output=<path>` option so patch bytes are written directly without PowerShell transcoding.

```text
# Do not use:
git diff --cached | Out-File -Encoding utf8 "myDiff.diff"

# Use:
git diff --cached --output="myDiff.diff"
```

## Scope Discipline

The practical end goal is not merely to understand Starfield internals for their own sake. The reconstructed model should ultimately help determine which resources can be expected to co-occur at an outpost location without biome-boundary hunting.

Avoid spending effort on unrelated engine systems unless they become necessary to explain resource allocation.
