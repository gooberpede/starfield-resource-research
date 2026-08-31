# Codex Brief — Capture Pre-Resolution Resource-Family Container Structure

## Context

This repository supports reverse engineering of Starfield's runtime inorganic resource-generation system.

Before changing anything, read:
- `AGENTS.md`
- `README.md`
- `docs/known-facts.md`
- `docs/hypotheses.md`
- `docs/function-register.md`
- `docs/experiments/ghidra-call-signature-reconciliation.md`
- `ghidra/README.md`
- `ghidra/scripts/ExportCallSignatureEvidence.java`
- `ghidra/scripts/ExportFunctionNeighbourhood.java`
- `ghidra/scripts/AnalyzeClassFieldProvenance.java`

Recent forensic work established this high-confidence path:

```text
ResourceViewWidget + 0xA0
    -> QTreeWidget-compatible concrete CK object

that object + 0x20
    -> component-compatible adjusted subobject

FUN_1431bc320
    -> copies that source component through
       TESContainer::vftable + 0x50
       -> FUN_140e0aab0

temporary TESContainer
    -> passed to FUN_140e457b0

FUN_140e457b0
    -> generic TESContainer / TESLevItem processing
    -> copies ordinary entries
    -> resolves leveled entries
```

The copy/source-component interpretation is substantially correct.

We now want to test a more important hypothesis:

> Resource-family structure may be represented directly, or materialized transparently, as ordinary TESContainer entries plus nested TESLevItem structures, with the seed-derived selector determining what descendants resolve.

## Known data model

A BIOM record links an RSGD record.

An RSGD defines the resource candidates for the biome, including weighted resource-family choices and non-family resources such as Water or Helium-3.

Example:

```text
BIOM: FrozenNoLife09
RSGD: FrozenBarrenDefaultRes03

Water   100%
Nickel   60%
Lead     40%
```

Current interpretation:

```text
Water is unconditional.
Nickel vs Lead is a weighted alternative:
one family is selected.
```

Empirical invariant from the canonical runtime dataset:

> If any descendant member of a resource family occurs, the root member of that family also occurs.

Examples:

```text
Cobalt never without Nickel
Silver never without Lead
```

A plausible representation is therefore:

```text
ordinary entry:
    family root

leveled/nested structure:
    optional descendants / branch selection
```

This is a hypothesis to test, not a fact to assume.

## Objective

Capture and compare the resource structure at three stages:

```text
source component at CK/UI backing object + 0x20
            ↓ FUN_140e0aab0 copy
temporary TESContainer before FUN_140e457b0
            ↓ FUN_140e457b0
resolved TESContainer after processing
```

At the same time, capture the selector/level value passed into `FUN_140e457b0`.

The experiment should answer:

1. What exact entries are in the source component?
2. What exact entries are in the temporary TESContainer before resolution?
3. Which entries are ordinary forms vs `TESLevItem`?
4. What do nested `TESLevItem` structures contain?
5. Do they ultimately reference IRES records?
6. Does their topology resemble known resource-family topology?
7. Is the family root structurally outside the leveled/randomized portion?
8. What exact selector value is passed to `FUN_140e457b0`?
9. What changes between pre-resolution and post-resolution?
10. Is the source component already fully constructed before the copy?

The priority is evidence capture, not broad semantic inference.

## Working method

Prefer one reusable evidence-capture tool rather than several one-off analyzers.

If practical, implement a focused script such as:

```text
ExportResourceResolutionEvidence.java
```

It should be usable repeatedly against different planets/biomes/family cases without code changes.

Do not add another large general framework to `AnalyzeClassFieldProvenance.java` unless there is a compelling reason.

## Required capture point 1 — Source component

At the `FUN_1431bc320` call to `FUN_140e0aab0`, capture the source argument:

```text
R8 = *(ResourceViewWidget + 0xA0) + 0x20
```

Enumerate the source component's entry storage using the structure inferred from `FUN_140e0aab0`.

The reconciliation showed source array state at approximately:

```text
source + 0x40
source + 0x48
```

Use actual live evidence rather than assuming offsets if reanalysis differs.

For every entry, record:
- index
- raw entry address
- entry size
- referenced form pointer
- FormID
- form type
- EditorID if available
- display/name string if available
- quantity/count/metadata
- whether ordinary or leveled
- any additional entry fields

Do not mutate or type the live program.

## Required capture point 2 — Temporary TESContainer before resolution

Identify the temporary TESContainer created in `FUN_1431bc320`.

After the copy from `FUN_140e0aab0` completes, but before `FUN_140e457b0`, enumerate its contents.

Record the same fields as for the source component.

Then compare source vs temporary:

```text
same entry count?
same form pointers?
same metadata?
same order?
any transformation?
```

Produce an explicit diff.

## Required capture point 3 — Resolver selector

At the call to `FUN_140e457b0`, capture every argument under the actual ABI/p-code mapping.

Identify specifically the `ushort` / level / selector argument previously derived from the Resource Seed control.

Record:
- original displayed/input Resource Seed value if recoverable
- intermediate transforms
- final value passed to resolver
- width/signedness
- register/stack location
- exact call site

If only the final selector is recoverable, record that fact without inventing the upstream transformation.

## Required capture point 4 — Post-resolution container

After `FUN_140e457b0` returns, enumerate the resulting container/list state before it is consumed/displayed.

Record:
- entries remaining
- newly materialized entries
- removed/replaced leveled entries
- final IRES forms
- ordering
- counts/metadata

Produce a pre-resolution vs post-resolution diff.

## Recursive TESLevItem inspection

For every entry whose form is a `TESLevItem` / leveled-list object, recursively inspect its entries to bounded depth.

Suggested maximum depth:

```text
8
```

Stop on:
- cycles
- repeated object addresses
- null forms
- unsupported object type
- depth limit

For each leveled node, record:
- FormID
- EditorID
- RTTI/form type
- list flags
- chance-none or equivalent if present
- number of entries
- each child:
  - level
  - count
  - weight/chance if represented
  - form pointer
  - FormID
  - EditorID
  - form type
- nested leveled-list children
- terminal IRES children

Do not infer semantic family relationships unless the structure actually supports them.

## IRES resolution

For terminal resource forms, record:

```text
FormID
EditorID
form type
```

Confirm whether the terminal form is actually `IRES` rather than assuming all leaf forms are resources.

If the static Ghidra type system does not expose a convenient form-type API, use existing Bethesda form-type fields/helpers already present in the program/scripts.

## Comparison experiment

The tooling should support at least two contrasting family shapes without code changes.

### Case A — Linear family

Prefer Nickel, whose known family structure is:

```text
Nickel
  -> Cobalt
      -> Platinum
          -> Palladium
```

Use a planet/biome where the CK currently resolves to the Nickel family.

### Case B — Branching family

Prefer Lead or Copper, because their known family topology branches.

For example:

```text
Lead
├─ Tungsten -> Titanium -> Dysprosium
└─ Silver -> Mercury
```

Use a known planet/biome where that family is actually selected.

If identifying suitable live cases automatically is expensive, support manual selection/input and document the exact procedure.

Do not spend large effort building automatic planet discovery.

## Family-topology test

For each captured family case, answer:

```text
Does the nested TESLevItem/TESContainer topology
match or substantially reflect
the known resource-family topology?
```

Classify result as:
- strong match
- partial match
- no match
- insufficient evidence

Use explicit structural reasons.

## Root-invariant test

Specifically test whether the family root is represented differently from descendants.

Useful evidence would include:

```text
root = ordinary TESContainer entry
descendants = TESLevItem-resolved entries
```

or:

```text
root is itself inside leveled structure but selected by
some invariant rule
```

Do not assume the expected result.

The experiment should help explain the empirical rule:

> descendant never occurs without family root.

## RSGD correlation

For the selected biome/case, record the known:

```text
BIOM
RSGD
RSGD candidate entries / percentages
```

If convenient, obtain these from existing exported/static data rather than implementing a new RSGD parser in Ghidra.

The purpose is to compare:

```text
RSGD candidate families
vs
captured container family
```

Critical question:

> Has family selection already happened before the captured source component is built?

For example, with:

```text
Water 100
Nickel 60
Lead 40
```

does the captured container contain:

```text
Water + Nickel family only
```

or:

```text
Water + both Nickel and Lead candidate structures
```

## Important branching question

Explicitly determine which model fits the evidence:

### Model 1 — RSGD family choice happens before TESLevItem resolution

```text
RSGD
  ↓ weighted family selection
selected Nickel family
  ↓
container contains Nickel-family structure
  ↓
FUN_140e457b0 selects descendants
```

### Model 2 — RSGD alternatives themselves are represented in leveled structure

```text
RSGD
  ↓
container contains Water + Nickel alternative + Lead alternative
  ↓
FUN_140e457b0 selects family and descendants
```

### Model 3 — Other / mixed

Describe directly from evidence.

Do not assume Model 1.

## Static vs dynamic evidence

If headless Ghidra against the analysed project can only inspect static code/data and cannot observe runtime container contents, say so clearly.

In that case, determine the best available next approach among:
1. static reconstruction of the source component's backing data
2. CK debugger/runtime instrumentation
3. targeted patch/logging hook
4. existing CK object memory export
5. another minimally invasive method

Do not pretend static analysis can inspect runtime heap state if it cannot.

If runtime observation is required, produce the smallest practical instrumentation plan.

## Headless execution

Use the read-only scratch-copy method established in the previous experiment when applicable:

```text
scratch project copy
-readOnly
-noanalysis
```

Do not modify the original Ghidra project.

If the experiment requires live CK runtime state, distinguish that clearly from what headless Ghidra can provide.

## Output

Suggested experiment directory:

```text
exports/
└─ resource-resolution/
   └─ <case-name>/
      ├─ context.json
      ├─ source-container.json
      ├─ pre-resolution-container.json
      ├─ selector.json
      ├─ post-resolution-container.json
      ├─ source-vs-pre-diff.json
      ├─ pre-vs-post-diff.json
      ├─ leveled-tree.json
      ├─ ires-leaves.json
      ├─ rsgd-correlation.json
      ├─ family-topology-analysis.md
      └─ manifest.json
```

If runtime capture requires a different artifact shape, keep equivalent information.

## Reusability

The resulting tooling should be parameterized enough to run the same experiment for multiple cases.

Prefer parameters such as:

```text
case name
caller / resolver call site
optional expected BIOM
optional expected RSGD
optional known selected family
```

Do not hard-code Nickel, Lead, Archimedes III, or one call-site outcome into the core logic.

Known addresses may be used as default acceptance targets.

## Documentation

Add a durable experiment report under:

```text
docs/experiments/
```

Suggested filename:

```text
resource-family-container-capture.md
```

Document:
- objective
- setup
- capture method
- static/runtime limitations
- selected cases
- evidence
- family-topology comparison
- model selection
- remaining uncertainty

Update `docs/function-register.md` only with new mechanically supported function/dataflow facts.

Update `docs/hypotheses.md` if the family-tree-as-leveled-list hypothesis is strengthened, narrowed, or rejected.

Do not add speculative claims to `docs/known-facts.md`.

## Safety requirements

All Ghidra work must remain read-only.

Do not:
- begin transactions
- rename functions
- create labels
- add comments
- change signatures
- apply types
- modify memory
- alter analysis state

If runtime CK instrumentation is needed:
- prefer observation/logging only
- avoid behavior changes
- document exactly what is hooked/read
- do not patch game data or seed logic

## Explicit non-goals

Do not spend this task on:
- identifying the exact concrete subclass at `ResourceViewWidget+0xA0`
- Qt inheritance reconstruction
- more callback graph analysis
- global field provenance
- full RSGD reverse engineering
- deriving the final seed algorithm
- planner implementation

The task is:

```text
capture family representation
        ↓
inspect ordinary vs leveled entries
        ↓
capture selector
        ↓
compare pre/post resolution
        ↓
test resource-family-tree hypothesis
```

## Minimum success

A successful task must determine, for at least one known family case:

1. whether the pre-resolution structure contains ordinary entries, TESLevItem entries, or both
2. whether terminal leaves include IRES forms
3. whether the family root has a structurally distinct role
4. whether RSGD family choice has already happened before `FUN_140e457b0`
5. the exact selector value passed to `FUN_140e457b0`
6. what changes across resolution
7. whether runtime capture is required for anything not statically recoverable

## Best-case success

For both a linear and branching family:

```text
RSGD
  ↓
captured family representation
  ↓
ordinary root + nested TESLevItem topology
  ↓
selector
  ↓
resolved IRES set
```

with the nested structure substantially matching the known family topology.

That would strongly support the hypothesis that resource-family relationships are represented transparently through generic container/leveled-list data structures.

## Deliverables

When finished, report:

1. files modified
2. files added
3. tooling added
4. whether static or runtime capture was used
5. whether headless Ghidra was used
6. selected test case(s)
7. source-component contents
8. temporary pre-resolution contents
9. selector value
10. post-resolution contents
11. TESLevItem recursive structure
12. terminal IRES leaves
13. source-vs-temp differences
14. pre-vs-post differences
15. RSGD correlation
16. whether family choice occurs before or inside leveled resolution
17. root-invariant evidence
18. linear-family topology result
19. branching-family topology result if completed
20. whether the family-tree hypothesis is strengthened, narrowed, or rejected
21. one recommended next research target

The goal is to answer a major resource-algorithm question with one reusable experiment, not merely add another analyzer feature.
