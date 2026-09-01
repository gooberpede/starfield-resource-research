# Brief R09 — Reconcile research repository to the v1.0 reproducer baseline

## Status

Research-state reconciliation brief for:

`gooberpede/starfield-resource-research`

This brief should be performed after, or in direct coordination with, Brief 09A in `starfield-resource-reproducer`.

Its purpose is to make both repositories describe the **same recovered algorithm and evidence state** so that Codex can move between them without inheriting obsolete hypotheses, stale “next investigation” instructions, or contradictory evidence labels.

This is primarily a research/documentation reconciliation task. Preserve raw experiments and historical evidence.

Do not commit or push unless explicitly asked.

## Governing principle

The research repository remains the durable record of:

```text
what was observed
how it was observed
which interpretations were superseded
which native functions were recovered
which questions remain genuinely open
```

The reproducer repository is the reference implementation.

After reconciliation:

```text
starfield-resource-research
    = authoritative evidence/history state

starfield-resource-reproducer
    = authoritative implementation of the recovered v1.0 model
```

They must agree on all settled generation semantics.

## Milestone to record

The recovered inorganic-resource-generation model has now passed:

```text
1,444 / 1,444 canonical planet-wide validation
0 mismatches
0 errors

all targeted pathological CK biome regressions

10 / 10 fresh holdout bodies:
    exact atmospheric resources
    exact CK biome-local terrestrial resources
    exact retail planetary-scan resource sets
```

The ten fresh holdout bodies were:

```text
Vesta — Lunara
Niira — Narion
Eridani IV — Eridani
Cassiopeia IV-a — Eta Cassiopeia
Cassiopeia II-a — Eta Cassiopeia
Zosma V-a — Zosma
Eridani III-b — Eridani
Luyten's Rock — Luyten's Star
Bardeen V-d — Bardeen
Ka'zaal — Nirah
```

This validation was performed after the guarded biome-family fallback and Special-before-guards corrections.

Describe it as an independent corroboration layer, not as proof that Creation Kit addresses equal retail `Starfield.exe` addresses.

## Settled high-level model

Update README and durable research docs to reflect:

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

Maintain separate concepts:

```text
planet-wide resource identity
family configuration cache
family configuration origin
biome-local Common-family assignment
Everywhere occurrence
Special occurrence
atmosphere occurrence
```

## Evidence labels

Retain:

```text
PROVEN
STRONG
PROVISIONAL
COUNTERFACTUAL
SUPERSEDED
```

Several older active hypotheses are now resolved and must be moved, upgraded, or marked superseded.

## Atmosphere prepopulation

The current README/hypotheses still describe exact atmospheric insertion/order as unresolved or merely STRONG.

That is stale.

### PROVEN LIVE

In the CK Galaxy View Apply generation path:

```text
effective atmospheric resource IDs
    ↓
shared planet-wide resource-ID state
    ↓
Everywhere pre-pass
    ↓
shuffled per-biome generator
```

Maal VIII live tracing observed atmospheric Chlorine `000057D5` entering shared state before main generation.

Atmosphere therefore shares the same eight-unique-FormID state used by Everywhere, Special, Common, and descendants.

Remove any active “next investigation: trace Maal VIII atmospheric Chlorine” instruction. Preserve the old plan only as historical context where useful.

Reconcile:

```text
README.md
docs/known-facts.md
docs/hypotheses.md
docs/function-register.md
relevant experiment notes/indexes
```

## Everywhere/category 6

Record as settled:

### PROVEN LIVE

`FUN_141548920`:

- scans effective generation entries;
- checks IRES/category `6`;
- does not consult DNAM Everywhere chance;
- consumes no RNG;
- writes biome/work `+0x68`;
- appends the FormID into shared state;
- runs before shuffled per-biome generation.

Fermi VIII-b OceanDefaultRes is the decisive live case.

Supersede any earlier hypothesis that Everywhere uses a chance field or ordinary weighted selection.

## Special/Common selector

Retain as PROVEN:

`FUN_141580660` with helper `FUN_14157C470`.

For categories 5 and 0:

```text
one MT19937 binary32 probability draw
stored 0x238-byte RSGD order
category filter
cumulative Chance/100
first roll < cumulative
no normalization
```

The draw occurs before enumeration.

Special occurs before Common.

Special is not a planet-wide pre-pass.

## Special insertion ordering

Add the 08D.1 evidence explicitly.

### PROVEN LIVE

Within the per-biome generator:

```text
Special selection
→ Special written/recorded into shared state
→ five-tree guard
→ shared-eight guard
→ normal Common selector or fallback
```

A new Special can fill slot eight and cause the current biome to skip the normal Common selector.

A duplicate Special does not increment the unique count.

## Five-tree guard

The research docs currently describe the `count >= 5` interpretation as PROVISIONAL.

Reconcile that with the later Bara/Jaffa work.

### PROVEN LIVE for this generation path

The guarded structure is the collection of already-generated/cached Common-family configurations used by the per-biome generator.

Observed progression on Bara VII-d:

```text
0, 1, 1, 2, 2, 3, 4, 5
```

Normal cache reuse does not increment it.

At 5:

```asm
1415DD0D3 cmp dword ptr [rsi],5
1415DD0D6 jae 1415DD255
```

Normal Common selection is suppressed and control enters the recovered fallback block.

Use precise wording:

> five distinct generated/cached Common-family configurations

Do not generalize beyond the proven generation path into unrelated engine structures.

## Shared-eight guard

Record as:

### PROVEN LIVE / STATIC

At eight unique resource FormIDs:

```asm
1415DD0DC cmp dword ptr [r12],8
1415DD0E1 jae 1415DD255
```

The normal Common selector is skipped before its usual RNG draw.

However, the guard does **not** necessarily mean no Common family is assigned to the biome.

Any old wording equivalent to:

```text
shared8 guard → empty biome / no Common family
```

must be marked **SUPERSEDED**.

## Guard fallback assignment

This is the major missing research-state reconciliation.

Add a durable section to `known-facts.md` and appropriate function-register entries.

### PROVEN LIVE

Both five-tree and shared-eight guards branch to fallback logic beginning near:

`0x1415DD255`

The fallback can assign an already-generated family configuration to the current biome.

### `FUN_14154C710`

Record as a **PROVEN LIVE fallback candidate-construction helper**.

Observed semantics:

```python
has_common_entries = False
preferred = []

for resource_entry in current_effective_rsgd:
    if resource_entry.resource.category != Common:
        continue

    has_common_entries = True

    for cached_family in generated_family_cache:
        if cached_family.root_form_id == resource_entry.resource.form_id:
            preferred.append(cached_family)
```

No chance weighting in this helper.

### Decision rule — PROVEN LIVE on Jaffa VII-b

```text
no Common roots in EffectiveRSGD
    → no Common family assignment

cached-family roots match current RSGD Common roots
    → choose from matching cached families

Common roots exist but none match
    → choose from all already-generated cached families
```

The selected cached configuration is copied into the current biome's Common slots.

No descendant regeneration.

No new planet-wide identity.

### Assignment provenance terminology

Use, or explicitly map to, these domain concepts:

```text
NEW_FAMILY
NORMAL_CACHE_REUSE
GUARD_MATCHED_FALLBACK
GUARD_GENERAL_FALLBACK
NO_COMMON_ASSIGNMENT
```

## Guard fallback RNG

Add `FUN_14015B4A0` and thunk `FUN_1401190CD` to the function register if absent.

### PROVEN LIVE

```text
FUN_14015B4A0
    ↓
FUN_1401190CD
    ↓ jmp
FUN_140924800
```

Fallback therefore uses the already-recovered MT19937 → binary32 probability helper.

For lower bound 0 and candidate count N:

```python
index = trunc(float32(probability * float32(N)))
```

A one-element pool still consumes the probability draw.

Do not merge this semantic mechanism with the biome-shuffle integer helper.

## Ordinary family-cache reuse

Retain and strengthen the distinction.

### PROVEN LIVE

```text
normal Common weighted selector chooses root
→ cache hit
→ cached root + emitted descendants copied into current biome
→ no descendant-generation RNG
```

This is distinct from guard fallback, where normal Common weighted selection never happens.

## Family-origin provenance

Add the conceptual distinction:

```text
family configuration origin
vs
current biome assignment
```

Preferred research wording:

> The planet-scope family configuration was first generated while processing biome X and was later assigned to biome Y.

Avoid stronger wording such as “biome Y copied resources from biome X” except as clearly labelled shorthand.

## PRNG mechanism register

Make sure durable docs distinguish:

```text
1. biome shuffle integer rejection/modulo
2. MT19937 → binary32 probability conversion
3. Special/Common weighted selector
4. descendant float32-scaled candidate index
5. guard-fallback float32-scaled cached-family index
```

Keep mechanisms distinct even where arithmetic is shared.

## Validation-state reconciliation

`known-facts.md` still presents the old:

```text
1,281 / 1,444
88.71%
```

as current reproducer status.

That must become historical.

Where useful, record the progression:

```text
pre-07B: 1281 / 1444
07B:     1426 / 1444
08A:     1441 / 1444
08B:     1442 / 1444
08C+:    1444 / 1444

08D / 08D.1:
    planet-wide remains 1444 / 1444
    pathological CK biome regressions exact

fresh holdout:
    10 / 10 exact CK + retail
```

Use only values already supported by project evidence.

## Fresh validation experiment note

Create:

`docs/experiments/v1-holdout-validation.md`

Record:

### Purpose

Independent validation after the algorithm was considered complete.

### Sample

The ten fresh bodies listed above.

### Selection intent

Representative of previously troublesome dimensions:

- atmosphere/terrestrial overlap;
- Water/Everywhere duplication;
- atmospheric descendant-family members;
- single- versus multi-resource atmosphere;
- capacity/cache/fallback opportunities.

### Result

For all ten:

```text
reproducer atmospheric resources == observed atmosphere
reproducer biome distributions == Creation Kit
reproducer planet-wide set == retail planetary scan
```

Overall:

```text
10 / 10 exact
0 observed errors
```

Do not invent detailed per-biome tables unless separately supplied or already tracked.

## Volii Alpha negative control

Record this as an input-boundary finding.

```text
Volii Alpha absent from PlanetResourceGeneration_v5.csv
available atmosphere export:
    Benzene
    Water
```

The reproducer correctly refuses to invent biome-local assignments.

Research conclusion:

Independent atmospheric occurrence knowledge does not imply biome-generation knowledge.

Missing PNDT/effective-RSGD input must remain unknown/unavailable, not silently converted to “no resources”.

This is **not** evidence about Volii Alpha's actual terrestrial biome allocation.

## SurveyAggregator / `planet-all-resources.csv`

Retain careful scope:

- valuable empirical/canonical validator for the CK/RSGD-visible channel used by the reproducer;
- proven incomplete for atmosphere-derived final membership;
- exact internal SurveyAggregator semantic contract remains unresolved.

Do not restart SurveyAggregator reverse engineering merely because the exact semantic contract remains open. It is not blocking v1.0.

Move it to a non-blocking open-questions section.

## `hypotheses.md` cleanup

Required actions:

### H1 — atmosphere shares eight-entry capacity

Move to **PROVEN** / `known-facts.md`.

Remove from active hypotheses.

### H4 — five-family check semantics

Move the recovered five-distinct-cached-Common-family interpretation into `known-facts.md` with precise scope.

Remove the old active provisional form.

### Open Runtime Question — Maal VIII atmosphere trace

Mark completed/superseded and remove as next investigation.

### H2 — zero-count reflected LIST explicitly clears atmosphere

May remain **PROVISIONAL** if still unresolved.

### H3 — one ordinary resource family per biome

Reassess wording.

The recovered runtime directly models one Common-family assignment per biome invocation, but:

- Everywhere/Special/atmosphere coexist;
- guard fallback may assign a family whose root is not in that biome's effective RSGD.

Rewrite or retire H3 so it cannot mislead planner work.

A narrower candidate statement is:

> Each processed biome receives at most one Common-family configuration through the recovered per-biome Common assignment mechanism.

Only label PROVEN if the recovered control flow directly supports the exact wording chosen.

## Function-register reconciliation

Update at minimum:

### `FUN_1415DCFB0`

Add:

- Special-before-guards ordering;
- five-tree semantic role;
- shared-eight guard;
- post-guard fallback block;
- ordinary cache reuse versus guard fallback;
- relevant fallback calls.

Remove stale atmosphere “next analysis” text.

### `FUN_14152CBC0`

Upgrade atmosphere prepopulation semantics where live evidence now proves it.

Preserve static-vs-live evidence distinctions.

### `FUN_141548920`

Upgrade to PROVEN LIVE where supported.

### `FUN_14154C710`

Add:

```text
address: 0x14154C710
status: PROVEN LIVE fallback candidate-construction helper
```

Describe Common-root matching semantics.

### `FUN_14015B4A0`

Add:

```text
status: PROVEN LIVE float-scaled fallback family selector
```

Describe bounded arithmetic and draw consumption.

### `FUN_1401190CD`

Add/note:

```text
PROVEN thunk to FUN_140924800
```

### `FUN_140924800`

Ensure it records the shared binary32 probability conversion and the proven call relationships.

Do not invent semantic C++ names.

## README reconciliation

Replace the stale “Next Investigation” focused on atmosphere insertion with a current posture.

Suggested framing:

```text
Core inorganic generation algorithm:
    recovered and independently validated

Current research posture:
    preserve evidence
    investigate new falsifications or executable/version drift
    support downstream planner/data tooling
```

Do not claim no future discovery is possible.

Do state that no known algorithmic hole remains within the current v1.0 scope.

## Research completion/baseline document

Create:

`docs/v1-research-baseline.md`

This should be the first orientation document for Codex and summarize:

- scope;
- proven algorithm;
- native function anchors;
- evidence stack;
- current validation;
- known non-blocking open questions;
- major superseded interpretations;
- relationship to `starfield-resource-reproducer`.

Do not duplicate every experiment.

## Cross-repository contract

Document explicitly:

```text
starfield-resource-research
    owns evidence status, trace provenance, native function findings

starfield-resource-reproducer
    owns executable reference model and regression suite
```

Future settled-rule changes should follow:

```text
1. reproduce a counterexample
2. add/update research evidence
3. classify evidence
4. reconcile research baseline
5. issue implementation brief
6. update reproducer
7. add regression
8. rerun canonical + holdout validation
```

Codex must not independently “fix” one repository while leaving the other with contradictory semantics.

## Remaining non-blocking OPEN questions

Retain only genuine open items, likely including:

```text
exact semantic contract exposed by SurveyAggregator
generic interpretation of zero-count ATMO reflected LIST clearing
retail Starfield.exe native-address equivalence/version mapping
defensive theoretically unreachable:
    guard + Common entries + empty global family cache
```

These do not block v1.0.

Do not preserve resolved algorithm questions as active merely for historical caution.

## Historical evidence preservation

Do not delete old experiments or superseded paths because their interpretation changed.

Instead:

- mark interpretations **SUPERSEDED**;
- retain raw trace/static findings;
- point readers to newer decisive evidence.

The old:

```text
ResourceViewWidget::OnApplySeed
→ FUN_1431bc320
→ FUN_140e457b0
```

trail remains valid historical static work but is not the primary allocator.

## AGENTS.md reconciliation

Update agent instructions so both repositories enforce the same baseline:

1. preserve evidence labels;
2. do not silently reopen settled rules;
3. do not merge distinct RNG mechanisms;
4. do not treat CK addresses as retail addresses;
5. do not infer from missing input;
6. do not use validation oracle data as generation logic;
7. do not change the algorithm without new evidence;
8. reconcile both repositories after any future rule change;
9. preserve superseded evidence rather than deleting history;
10. retain UTF-8/mojibake safeguards.

## Verification

Run repository-appropriate checks:

```text
mojibake/UTF-8 guard if present
tests/tool checks if present
git diff --check
```

Cross-check updated factual claims against preserved trace/experiment material and current v1.0 reproducer semantics.

Do not add unsupported per-body detail.

## Deliverable

Report:

1. changed research files;
2. hypotheses moved to PROVEN/SUPERSEDED;
3. function-register entries added/updated;
4. stale next-investigation instructions removed;
5. new `v1-research-baseline.md`;
6. new holdout-validation experiment note;
7. remaining genuinely OPEN questions;
8. cross-repository contract added;
9. repository checks;
10. no commit/push unless explicitly requested.

Suggested commit message after review:

```text
docs: reconcile research state to v1 reproducer
```
