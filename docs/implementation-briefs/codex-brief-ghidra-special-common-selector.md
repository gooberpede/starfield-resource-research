# Codex Brief — Static Ghidra Inspection of `FUN_141580660` (Special/Common Selector)

Repository:

```text
gooberpede/starfield-resource-research
D:\Projects\starfield-resource-research
```

## Purpose

Perform a **focused static Ghidra investigation** of:

```text
FUN_141580660
0x141580660
```

This function is now live-observed in the Creation Kit Galaxy View Apply path as the selector called by `FUN_1415DCFB0` for both:

```text
category 5 → Special
category 0 → Common
```

The immediate goal is to explain, statically and precisely, how the selector:

1. filters RSGD/resource-generation candidates by requested category;
2. applies the relevant per-category chance/weight data;
3. consumes RNG, if any;
4. chooses among multiple qualifying resources, if supported by the code;
5. returns the selected resource object / related generation data;
6. behaves differently, if at all, for category `5` versus category `0`.

This is a **static Ghidra task only**. Do not perform new x64dbg tracing under this brief.

---

# 1. Evidence already established — do not reopen

Treat the following as current research state.

## 1.1 Caller and live path

`FUN_1415DCFB0` at:

```text
0x1415DCFB0
```

is **PROVEN in live Creation Kit Galaxy View Apply execution** to be the per-biome resource generator.

Its sole direct static caller is:

```text
FUN_14152CBC0
0x14152CBC0
```

at:

```text
0x14152D28F
```

The enclosing orchestration function:

- prepopulates the shared planet-wide resource-ID array with atmosphere-derived resources;
- performs a complete per-biome category-6 / Everywhere pre-pass;
- only then begins shuffled per-biome calls to `FUN_1415DCFB0`.

Do not revisit the old leveled-list trail as a primary generation path.

---

## 1.2 Special and Common calls in `FUN_1415DCFB0`

Static decompilation and live Callisto tracing agree that `FUN_1415DCFB0` calls:

```text
FUN_141580660(..., category=5)
```

first, then later:

```text
FUN_141580660(..., category=0)
```

The category-5 result is handled as the biome's Special resource.

The category-0 result is handled as the biome's Common/root resource.

The caller is already known to be category-driven rather than hard-coded to particular FormIDs.

---

## 1.3 Callisto control case

Live test planet:

```text
Callisto
single biome: CrateredNoLife09
resources: Iron + Helium-3
```

Observed live:

```text
Special call:
    FUN_141580660(..., 5)
    → 000057F5 Helium-3

Common call:
    FUN_141580660(..., 0)
    → 000057C7 Iron
```

Before the Special insertion:

```text
shared planet resource count = 0
```

After Helium-3 insertion:

```text
shared planet resource count = 1
```

Then Iron is selected and appended.

Therefore:

**PROVEN live:** biome-derived Special resources enter the same shared planet-wide resource-ID array used for the eight-resource capacity checks.

---

## 1.4 Everywhere is architecturally distinct

Do not conflate category 5 and category 6.

Current architecture:

```text
FUN_14152CBC0
    |
    |-- atmosphere prepopulation
    |
    |-- category 6 / Everywhere pre-pass over all biomes
    |
    `-- shuffled biome loop
           |
           `-- FUN_1415DCFB0
                  |
                  |-- category 5 / Special selector
                  |
                  |-- category 0 / Common selector
                  |
                  `-- descendants 1..4
```

Maal VIII live tracing already showed the category-6 helper is generic and tests:

```text
resource.category == 6
```

rather than testing specifically for Water.

This brief concerns category 5 / category 0 selector behavior only.

---

# 2. Live trace available for comparison

The latest Callisto trace is:

```text
/mnt/data/callisto-category-5-call.trace64
```

It contains complete live executions of `FUN_141580660` for:

```text
category 5 → Helium-3
category 0 → Iron
```

The two executions appear to follow the same broad internal instruction path.

Use this trace as **live comparative evidence** if useful, but do not perform new runtime experiments.

If Codex cannot directly parse `.trace64`, do not build a large parser unless genuinely necessary. Static Ghidra analysis is primary for this brief.

---

# 3. Required reading

Before analysis, read the current repository guidance and relevant evidence.

At minimum:

```text
AGENTS.md
README.md

docs/known-facts.md
docs/hypotheses.md
docs/function-register.md

docs/experiments/pre-biome-resource-state-investigation.md
docs/experiments/x64dbg-runtime-generation-findings.md
```

Also inspect the preserved evidence bundle under:

```text
docs/experiments/evidence/pre-biome-resource-state/
```

especially:

```text
FUN_1415dcfb0-decompiled.c
FUN_1415dcfb0-instructions.txt
FUN_1415dcfb0-callees.json
```

Do not assume repository documentation is current where it explicitly marks claims as historical, superseded, provisional, or open.

---

# 4. Primary static question

The central question is:

> **What exactly does `FUN_141580660` do when asked for category 5 or category 0, and what data/RNG determines which resource it returns?**

Recover the smallest accurate semantic model.

A successful result should ideally explain code equivalent in spirit to:

```text
input:
    biome/RSGD generation context
    PRNG state
    requested category

enumerate generation records
filter to requested category
evaluate category-specific chance/weight
possibly consume RNG
select one candidate
return selected resource / generation record
```

Do **not** assume this pseudocode is correct. Derive the actual behavior from the code.

---

# 5. Required analysis tasks

## 5.1 Export full function evidence

Export a focused context bundle for:

```text
FUN_141580660
0x141580660
```

At minimum preserve:

```text
decompiled C
instructions
metadata
callers
callees
```

Use the existing repository Ghidra export workflow/scripts where practical.

Suggested evidence location:

```text
docs/experiments/evidence/special-common-selector/
```

Suggested filenames:

```text
FUN_141580660-decompiled.c
FUN_141580660-instructions.txt
FUN_141580660-metadata.json
FUN_141580660-callers.json
FUN_141580660-callees.json
```

Do not rename the Ghidra function.

Do not modify the Ghidra project unless absolutely necessary.

Prefer read-only analysis.

---

## 5.2 Recover parameters

Determine the best-supported meaning of each parameter.

Especially identify:

```text
- source biome/RSGD/resource-generation structure
- MT19937 / RNG state input
- requested category
- output container / temporary result structure if any
```

If a parameter's exact semantic type cannot be proven, describe its observed dataflow rather than inventing a type.

---

## 5.3 Locate category filtering

Find the exact instruction(s) and data field used to decide whether a resource entry belongs to the requested category.

We expect the category ultimately corresponds to the established IRES rarity/category byte:

```text
0 Common
1 Uncommon
2 Rare
3 Exotic
4 Unique
5 Special
6 Everywhere
```

But do not simply assert that `FUN_141580660` reads `IRES +0x2F8` unless the static dataflow actually proves it.

Identify:

```text
address
source object
offset/field
comparison instruction
requested-category value source
```

---

## 5.4 Determine how RSGD generation records participate

Trace the function back to the data representing the RSGD/resource-generation entry.

Identify, if possible:

```text
resource identity / IRES
category
BiomeCommonChance
BiomeSpecialChance
other generation probabilities used here
record ordering
nested record stride / structure
```

The existing xEdit dataset includes fields such as:

```text
BiomeCommonChance
BiomeUncommonChance
BiomeRareChance
BiomeExoticChance
BiomeUniqueChance
BiomeSpecialChance
BiomeEverywhereChance
```

Determine which of those, if any, this selector actually consumes for category 5 and category 0.

Do not assume column names map one-to-one to fields without evidence.

---

# 6. RNG investigation — high priority

Determine whether `FUN_141580660` consumes random numbers.

If it does, identify:

```text
- exact RNG helper(s)
- exact call site(s)
- number of raw MT19937 draws
- conversion used
- whether category 5 and category 0 use the same RNG mechanism
- whether a 100% Special chance still consumes RNG
- whether a single eligible candidate still consumes RNG
```

This matters because exact RNG consumption affects every subsequent generation decision.

Do not conflate this selector with the two already proven bounded RNG mechanisms:

### biome shuffle bounded integer helper

```text
rejection-based uint32 bounded selection
```

### descendant candidate selection

```text
uint32
→ float32
→ * 2^-32
→ * 0.99999
→ * candidate_count
→ truncate
```

If `FUN_141580660` uses a third mechanism, document it separately.

If it uses the existing Starfield float path, prove the call/dataflow rather than assuming.

---

# 7. Special chance semantics

Callisto is especially useful because its Helium-3 entry is expected to have:

```text
BiomeSpecialChance = 100
```

Determine whether the selector:

```text
A. always returns a category-5 candidate if one exists;
B. performs a chance roll even at 100%;
C. treats the RSGD chance as a weight among Special candidates;
D. uses some other threshold/cumulative mechanism;
E. delegates probability logic to another helper.
```

Do not promote any answer beyond the evidence.

If a chance field exists but is bypassed when only one candidate exists, document that.

If the function always consumes an RNG draw even when the result is deterministic, this is especially important.

---

# 8. Multiple candidates

Determine the selector's behavior if more than one resource qualifies for the requested category.

Questions:

```text
- Are candidates accumulated?
- Is stored RSGD order preserved?
- Are chances cumulative?
- Are weights normalized?
- Is the first passing candidate returned?
- Is one candidate uniformly selected?
- Can selection fail and return nothing?
```

If the function contains logic that cannot be fully resolved without a multi-Special test case, identify the exact unresolved branch and stop.

Do not invent a multi-candidate rule from the Common selector behavior unless the same code proves it.

---

# 9. Compare category 5 and category 0

This is the key comparative output.

Determine whether:

```text
category 5 and category 0
```

are truly handled identically apart from:

```text
requested category
category-specific probability field
```

or whether Special has additional branches.

Explicitly report:

```text
same code path:
    yes/no/mostly

same candidate enumeration:
    yes/no

same probability logic:
    yes/no

same RNG consumption:
    yes/no

same return shape:
    yes/no

Special-only behavior:
    <if any>

Common-only behavior:
    <if any>
```

---

# 10. Correlate with the Callisto trace

Use the live trace to anchor static interpretation where possible.

The static explanation should account for:

```text
category 5 call → 000057F5 Helium-3
category 0 call → 000057C7 Iron
```

Do not use final output agreement alone as proof of mechanism.

Prefer evidence of:

```text
specific entry examined
category matched
chance/weight read
RNG result
selected resource pointer
FormID returned
```

If the current trace does not preserve enough state for one of those steps, label it unresolved.

---

# 11. Static call graph scope

Follow only helpers directly necessary to understand `FUN_141580660`.

Good reasons to inspect a helper:

```text
- resource entry enumeration
- category lookup
- chance/weight retrieval
- RNG generation/conversion
- candidate selection
- return/result construction
```

Do not recursively expand the wider Creation Kit call graph.

Stop once the selector's semantics are sufficiently explained.

---

# 12. Evidence labels

Use the project vocabulary consistently:

```text
PROVEN
STRONG
PROVISIONAL
COUNTERFACTUAL
SUPERSEDED
```

Examples:

```text
PROVEN STATIC:
FUN_141580660 compares requested category against field X at offset Y.

PROVEN LIVE:
Callisto category-5 call returned Helium-3.

STRONG:
Field Z likely corresponds to BiomeSpecialChance because...

PROVISIONAL:
A multi-candidate Special case may use cumulative weights, but no live case
has yet exercised multiple category-5 entries.
```

Do not collapse static and live evidence into one unlabeled claim.

---

# 13. Documentation deliverable

Add a focused experiment note, suggested:

```text
docs/experiments/special-common-selector-investigation.md
```

It should contain:

```text
1. Objective
2. Prior live evidence
3. Static function map
4. Parameter/data-structure findings
5. Category filtering
6. Probability/chance handling
7. RNG consumption
8. Category 5 vs category 0 comparison
9. Callisto reconciliation
10. Proven / Strong / Provisional / Open
11. Recommended next experiment, if any
```

Update:

```text
docs/function-register.md
```

for `FUN_141580660`.

Update:

```text
docs/known-facts.md
docs/hypotheses.md
```

only where the new evidence genuinely changes durable research state.

Do not rewrite unrelated documentation.

---

# 14. Important precision rules

## 14.1 Creation Kit context

The functions in this investigation are proven live in:

```text
CreationKit.exe
Galaxy View Apply path
```

Do not casually call them proven retail `Starfield.exe` functions.

If using the word "runtime", make the CK execution context explicit.

---

## 14.2 Do not overstate developer intent

It is reasonable to discuss a category-generic architecture if the code supports it.

But distinguish:

```text
PROVEN:
the selector uses category values generically

from

INFERENCE:
Bethesda intended mod authors to create arbitrary new Everywhere/Special resources
```

The latter is design interpretation, not an engine fact unless tool/editor evidence supports it.

---

## 14.3 Preserve provenance

Do not collapse:

```text
AtmosphericResources
EverywhereResources
SpecialResources
BiomeGeneratedResources
```

into a single mechanism merely because all may eventually enter the same shared resource-ID array.

---

# 15. Explicit non-goals

Do **not** under this brief:

- perform new x64dbg tracing;
- modify the standalone reproducer;
- modify xEdit exporters;
- reverse-engineer ATMO reflection further;
- revisit the old leveled-list trail;
- implement Special handling in production code;
- change validation behavior;
- create synthetic plugin records;
- test custom IRES categories in CK;
- explore all categories 1–4;
- bulk-rename Ghidra functions;
- recursively export large call graphs;
- commit;
- push.

---

# 16. Stop conditions

Stop static analysis when either:

### Successful stop

You can explain, with evidence:

```text
FUN_141580660
    → candidate source
    → category filtering
    → relevant chance/weight logic
    → RNG consumption
    → selected resource
    → returned result
```

for Callisto's:

```text
category 5 → Helium-3
category 0 → Iron
```

### Useful unresolved stop

You identify a specific branch that cannot be resolved statically, for example:

```text
multiple category-5 candidates require a live control
```

or:

```text
chance < 100 requires a live case
```

In that case, stop and recommend the **smallest deterministic automated trace** needed.

Do not broaden the investigation to compensate.

---

# 17. Final deliverables

At completion, provide:

1. concise conclusion;
2. parameter interpretation;
3. exact category-filtering addresses;
4. exact probability/chance-related addresses;
5. exact RNG helper/call addresses, if any;
6. exact selection/return addresses;
7. category-5 vs category-0 comparison;
8. explanation of the Callisto live result;
9. evidence-labelled findings:
   - PROVEN
   - STRONG
   - PROVISIONAL
   - OPEN
10. any next live experiment required;
11. files added/changed;
12. `git diff`;
13. `git status --short`.

Do not commit.

Do not push.

---

# 18. Research question to keep front and centre

The investigation should answer this, not drift into generic reverse engineering:

> **When `FUN_1415DCFB0` asks `FUN_141580660` for category 5 or category 0, how does that function use the RSGD/IRES data and MT19937 state to choose the resource it returns?**

The Callisto live trace gives us the perfect paired control:

```text
same planet
same biome
same RSGD context
same selector function

category 5 → Helium-3
category 0 → Iron
```

Use that contrast aggressively.
