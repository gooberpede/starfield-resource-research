# Codex Brief — Research State Reconciliation Before Further Ghidra Work

Repository:

```text
gooberpede/starfield-resource-research
```

## Purpose

Bring the repository's durable research documentation up to date with the later live x64dbg findings and the newly established atmospheric-resource evidence.

This is a **documentation/research-state reconciliation task only**.

Do **not** begin a new Ghidra investigation yet.
Do **not** modify generation code in the separate reproducer repository.
Do **not** erase earlier Ghidra work merely because later evidence superseded some of its interpretations.

The goal is to leave `starfield-resource-research` in a state where a future Codex session can read the repository cold and correctly understand:

1. what is now proven;
2. what remains strong/provisional/open;
3. which older static-analysis trails were later deprioritised;
4. why those older trails should still be preserved as historical evidence;
5. what the next Ghidra question actually is.

After completing this brief, stop and report the diff. Do not commit or push unless explicitly instructed.

---

## 1. Evidence discipline

Update the documentation conventions so the following evidence labels are used consistently:

- **PROVEN** — directly established by live execution, direct data extraction, or equivalent decisive evidence.
- **STRONG** — multiple independent observations support the interpretation, but the exact mechanism has not yet been directly observed.
- **PROVISIONAL** — working implementation/model used because it fits current evidence, but an important structural detail remains unresolved.
- **COUNTERFACTUAL** — prediction from a controlled hypothetical intervention, not yet observed.
- **SUPERSEDED** — earlier interpretation retained for research history but no longer part of the current model because later evidence displaced it.

Add an explicit methodological rule:

> When static Ghidra interpretation conflicts with later live x64dbg execution, the live observation governs the current model. Preserve the older static result as historical evidence rather than silently deleting it.

Preserve the existing rule that Ghidra-generated names such as `FUN_...` must not be casually replaced with semantic names.

---

## 2. Correct the repository's current investigation direction

The repository currently over-emphasises the older Creation Kit / leveled-list trail:

```text
ResourceViewWidget::OnApplySeed
    ↓
FUN_1431bc320
    ↓
FUN_140e457b0
    ↓
generic leveled-list machinery
```

Later live x64dbg tracing established that this is **not the primary generation trail exercised by the tested Galaxy View Apply operation**.

Do not delete the old analysis. Instead:

- retain the careful calling-convention, TESContainer, and leveled-list findings;
- mark that trail as **SUPERSEDED / DEPRIORITISED AS PRIMARY ALLOCATION PATH**;
- explicitly state that it may still be legitimate CK/UI or downstream machinery;
- state that no future researcher should assume it participates in biome resource allocation without new live evidence.

The current primary runtime anchors are:

```text
FUN_1415DCFB0
FUN_14157F120
```

Add these to the current investigation direction and function register.

---

## 3. Current proven runtime model

### 3.1 PNDT / BIOM / RSGD

Established relationships:

```text
PNDT
 ├─ RSCS
 └─ ordered biome entries
        ↓
      BIOM
        ↓
      RSGD
```

PNDT can also provide a per-biome RSGD override.

**PROVEN precedence rule:**

```text
if PNDT biome Resource Generation != NULL:
    EffectiveRSGD = PNDT override
else:
    EffectiveRSGD = BIOM.RNAM
```

Do not describe PNDT and BIOM RSGDs as merged.

### 3.2 PRNG

**PROVEN**

For non-zero PNDT `RSCS`:

```text
RSCS
 ↓
MT19937 seeded directly with unsigned 32-bit RSCS
```

The same evolving MT19937 state is used for biome shuffle and subsequent resource-generation draws.

Biome list construction is in PNDT `BiomeIndex` order before shuffling for the tested live cases, with Kreet providing direct live proof.

Float conversion used in generation:

```python
raw_float = float32(raw_uint32)
unit_value = float32(raw_float * float32(1.0 / 2**32))
converted = float32(unit_value * float32(0.99999))
```

### 3.3 Two distinct bounded RNG mechanisms

Document these separately so future work does not incorrectly consolidate them.

#### Biome-shuffle bounded integer helper — PROVEN

Observed trace path:

```text
0x14152CEBD -> 0x1401714A8
0x1401714A8 -> 0x141560E90
0x141560F5A -> 0x14001D63D
0x14001D63D -> real helper 0x141587240
```

Equivalent logic:

```python
while True:
    raw = next_uint32()
    threshold = UINT32_MAX // upper_bound
    if raw // upper_bound < threshold:
        return raw % upper_bound
```

Rejected draws consume MT words.
Bound `1` consumes one MT word and returns `0`.

#### Descendant candidate selection — PROVEN

```text
raw uint32
→ float32(raw)
→ * float32(2**-32)
→ * float32(0.99999)
→ * float32(candidate_count)
→ truncate
```

For `candidate_count > 0`, exactly one MT word is consumed.

---

## 4. Per-biome generation

### 4.1 `FUN_1415DCFB0`

Add to `docs/function-register.md`.

**Address:** `0x1415DCFB0`

**Status: PROVEN primary per-biome generator**

Live traces tie this function to the real Creation Kit Galaxy View Apply resource-generation path. Relevant executable diagnostics identify it with `BGSPlanetDataManager.cpp`.

It handles at least:

- Special category (`5`);
- Common/root category (`0`);
- family-cache interaction;
- descendant-generation dispatch;
- resource-count / family-count limits.

### 4.2 Common/root selection

**PROVEN**

For the requested RSGD category:

- preserve stored `RSGDResourceIndex` order;
- use cumulative `Chance / 100`;
- first cumulative threshold exceeding the random value wins;
- do not normalize total weights.

### 4.3 Rarity/category enum

Current established mapping:

```text
0 Common
1 Uncommon
2 Rare
3 Exotic
4 Unique
5 Special
6 Everywhere
```

---

## 5. IRES resource graph and descendant generation

The resource-family graph is stored in IRES data:

```text
IRES
 ├─ SNAM - Rarity
 └─ Child Resources
```

This is no longer an unresolved “maybe leveled lists encode the family tree” question.

For each rarity level `1..4`, the runtime candidate builder uses:

```text
children(root)
+
children(current_structural_node)
```

then rarity-filters and stable-deduplicates candidates.

Root-source candidates appear before current-node-source candidates.

### 5.1 `FUN_14157F120`

Add to the function register.

**Address:** `0x14157F120`

**Status: PROVEN descendant helper**

When capacity permits:

1. build candidate set for requested rarity level;
2. draw inclusion probability;
3. draw candidate selection;
4. emit selected candidate if inclusion succeeds;
5. continue structurally through the chosen candidate even if it was omitted.

### 5.2 Zero-candidate behaviour

**PROVEN RNG consumption**

When there are zero candidates:

- exactly one MT word is consumed;
- no candidate is emitted;
- structural node remains unchanged.

Avoid asserting more semantic meaning than the trace establishes.

### 5.3 Root insertion

**PROVEN**

Once a new Common family is selected:

- the Common/root resource is emitted unconditionally;
- descendant generation proceeds through rarity levels `1..4`.

Move the older “root might merely be statistically unavoidable” wording to historical/superseded status.

### 5.4 Family cache

**PROVEN**

The first time a Common/root family is selected on a planet, descendants are generated and the family configuration is cached.

If another biome later selects the same root:

- the cached family result is reused;
- descendant helper calls are not repeated;
- descendant RNG is not consumed again.

---

## 6. Capacity / limit findings

Later Maal VIII traces recovered exact checks:

```text
0x1415DD0A3  cmp dword ptr [r12], 8
0x1415DD0A8  jae ...

0x1415DD0D3  cmp dword ptr [rsi], 5
0x1415DD0D6  jae ...

0x1415DD0DC  cmp dword ptr [r12], 8
0x1415DD0E1  jae ...
```

These establish the existence of:

- an internal resource-container limit of `8`;
- a generated Common-family-configuration limit of `5`.

The exact generic semantics of the five-family limit may still deserve caution, but the checks themselves are directly observed.

### 6.1 Descendant early return at resource limit

Dedicated Maal VIII trace:

```text
0x14157F14D  mov rax,[rcx+20h]
0x14157F151  cmp dword ptr [rax],8
0x14157F154  jae 14157F371
```

At the comparison:

```text
internal_resource_count = 8
```

**PROVEN:**

```text
if internal_resource_count >= 8:
    return current_structural_node
```

This early return consumes **no RNG**.

Do not describe this as merely “8 visible CK resources”.
Later atmospheric evidence shows the internal count can include resources absent from the CK Resource Generation tab / old plugin output.

---

## 7. Worked cases and full validation

Document that the reconstructed runtime model reproduced exact known results for multiple worked bodies:

```text
Oberon
Mimas
Decaran VII-b
Kreet
Algorab I
```

The standalone reproducer later reached:

```text
Validation population:       1,444
Exact matches:               1,281
Mismatches:                    163
Exact rate:                  88.71%
Errors:                         0
```

Those mismatches became the research guide rather than evidence that the core reconstructed algorithm was wrong wholesale.

---

## 8. Reinterpret `SurveyAggregator` / `planet-all-resources.csv`

This is a major correction.

The repository currently treats SurveyAggregator / its derived dataset as an authoritative complete final planetary-resource oracle.

Revise that.

`planet-all-resources.csv` remains valuable, but current evidence shows it omits at least some atmosphere-derived inorganic resources.

Treat it as an oracle for the CK/biome-generation-visible resource set unless/until a more exact semantic description is proven.

Do not allow atmosphere-derived resources to silently satisfy biome-generation mismatches.

Preserve provenance.

---

## 9. Atmospheric resource discovery

Add the newly established ATMO model.

### 9.1 Static data path

Planet records reference ATMO atmosphere records.

Effective atmosphere properties use Bethesda reflection data:

```text
root/default ATMO
    REFL = complete/base reflected object

child ATMO
    RFDP = reflection parent
    RDIF = local differences / overrides
```

The Creation Kit displays resolved inherited values.

### 9.2 Atmospheric inorganic resources

**PROVEN static examples**

#### Maal VIII

CK:

```text
ATMO_MaalVIII
  Atmosphere Type: AT_TYPE_NITROGEN
  Inorganic Resources:
    ResInorgCommonChlorine
```

The raw `RDIF` payload contains literal `AT_TYPE_NITROGEN` and little-endian:

```text
D5 57 00 00
→ 000057D5
→ Chlorine
```

#### Niira

CK effective atmospheric resources:

```text
Chlorine
Water
```

Serialized reflected `LIST` has count `2` followed by both IRES FormIDs.

#### Kreet

Atmospheric Helium-3 uses the same reflected list structure.

#### Vectera

No atmospheric resources; a zero-count `LIST` is present.

Treat generic “sole zero-count LIST = explicit Inorganic Resources clear” as **PROVISIONAL** until the reflected property identifier is fully decoded.

#### Water inheritance

Examples such as Titan and Maal IV inherit Water through ATMO parents.

Titan:

```text
AtmoDefaultDense
    Water
      ↓
AtmoOrangeBaseDense01
      ↓
ATMO_Titan
```

Root/default ATMO records store the base Water list under `REFL`, not `RDIF`.

---

## 10. Atmospheric extract

A dedicated xEdit exporter was developed:

```text
Starfield_ExportPlanetAtmosphericResources
```

Output grain:

```text
one row per planet × effective atmospheric resource
```

It resolves ATMO inheritance and preserves provenance.

Full-population extraction produced:

```text
335 planet × atmospheric-resource rows
297 distinct planets/moons with atmospheric resources
6 atmospheric resource types
0 duplicate planet × resource rows
maximum 2 atmospheric resources on one body
```

Observed resource counts:

```text
Water       260
Chlorine     32
Helium-3     16
Fluorine     11
Benzene       8
Alkanes       8
```

Do not invent a repository location for this script if it is not already present.

---

## 11. Maal VIII atmospheric-resource / capacity result

Creation Kit Resource Generation view shows Maal VIII:

```text
Iron
Nickel
Water
Uranium
Iridium
Vanadium
Copper
```

The in-game planetary survey reports eight resources and additionally includes:

```text
Chlorine
```

Maal VIII's ATMO explicitly assigns atmospheric Chlorine.

The old plugin/oracle omitted that Chlorine.

The final Iron-biome trace showed that after Iron insertion the internal resource count reached `8`, and the level-1 descendant helper returned immediately, preventing Alkanes and consuming no RNG.

Current **STRONG** interpretation:

```text
atmospheric Chlorine
    ↓
enters planet-wide resource state before/during biome generation
    ↓
occupies one of the same 8 internal resource slots
```

This explains the observed combination:

```text
7 resources in CK biome/resource view
8 resources in in-game survey
8 internal resources at descendant limit
```

Do not promote the exact atmospheric insertion function/order to PROVEN yet.

---

## 12. Population-level atmospheric evidence

Comparing the 163 reproducer mismatches against the atmospheric extract showed:

```text
101 / 163 mismatch planets
```

have at least one atmospheric inorganic resource.

A dense subset has atmosphere-only resources absent from both the old oracle and current reproducer, with counts strongly matching the Maal VIII capacity pattern.

Treat this as **STRONG** support that atmosphere-derived resources share the eight-entry planet-wide resource capacity.

---

## 13. Provenance-aware validation

Future work must not collapse resource origins too early.

The same IRES FormID can potentially be present through more than one mechanism.

Preserve channels such as:

```text
AtmosphericResources
BiomeGeneratedResources
EverywhereResources
SpecialResources
FinalPlanetaryResources
```

Do not allow:

```text
Chlorine from atmosphere
```

to mask a failure to generate:

```text
Chlorine from biome/RSGD
```

when the biome path should independently produce it.

Continue reconciling `planet-all-resources.csv` against the CK/biome-visible channel.

Reconcile the xEdit ATMO extract independently against the atmospheric channel.

Only final player-facing planetary membership should deduplicate origins by FormID.

---

## 14. Required document changes

Review and update at least:

```text
AGENTS.md
README.md
docs/known-facts.md
docs/hypotheses.md
docs/function-register.md
```

Strongly consider adding:

```text
docs/experiments/x64dbg-runtime-generation-findings.md
```

or a similarly clear durable evidence/history note.

It should preserve:

- decisive live x64dbg findings;
- exact addresses where supplied here;
- the two distinct bounded RNG mechanisms;
- 8-resource and 5-family checks;
- Maal VIII resource-limit trace;
- distinction between live evidence and older static hypotheses;
- atmospheric-resource evidence.

Do not fabricate trace filenames or addresses beyond those supplied in this brief.

---

## 15. Preserve history correctly

Do not rewrite the old Ghidra material so the repository appears to have always known the current answer.

Where an earlier interpretation was displaced:

- retain the historical finding;
- mark it **SUPERSEDED** or **DEPRIORITISED**;
- explain the later evidence that changed the interpretation;
- keep technically valid low-level findings even if the high-level inference was wrong.

For example, this may remain valid analysis:

```text
FUN_1431bc320
→ temporary TESContainer
→ FUN_140e0aab0
→ FUN_140e457b0
→ generic leveled-list machinery
```

What changed is the conclusion that it is the primary biome-resource allocation route.

---

## 16. Next research question — document only, do not execute

After reconciliation, clearly state the next Ghidra investigation:

> Starting from the proven per-biome generator `FUN_1415DCFB0`, identify its immediate outer caller / enclosing planet-generation loop and determine what occurs between entry to that planet-generation operation and the first per-biome call, with particular attention to pre-population of the shared planet-wide resource container by atmosphere-derived resources.

Target path:

```text
ATMO effective Inorganic Resources
        ↓
runtime insertion/loading path
        ↓
shared planet-wide resource container
        ↓
FUN_1415DCFB0 / FUN_14157F120 capacity checks
```

Maal VIII is the preferred live case because:

```text
ATMO_MaalVIII → Chlorine
```

and Chlorine appears in the in-game survey but not the CK biome Resource Generation view / old plugin output.

Do **not** begin this investigation under this brief.

---

## 17. Deliverables

At completion:

1. update the repository documentation described above;
2. preserve research history explicitly;
3. ensure no stale statement still presents the old leveled-list trail as the primary current algorithm path;
4. ensure no stale statement still says direct RSCS→MT19937 seeding is unresolved;
5. ensure no stale statement still treats SurveyAggregator / `planet-all-resources.csv` as a complete final inorganic oracle without qualification;
6. add/register `FUN_1415DCFB0` and `FUN_14157F120`;
7. document atmospheric resources and provenance-aware validation;
8. state the next Ghidra question without executing it;
9. run any repository-local markdown/docs checks that already exist;
10. stop and present:
   - changed files;
   - concise summary of what was corrected;
   - conflicts/ambiguities encountered;
   - `git diff`;
   - `git status`.

Do not commit.
Do not push.
Do not begin new reverse engineering.
