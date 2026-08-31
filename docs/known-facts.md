# Known Facts

This file contains **PROVEN** observations established by live execution, direct extraction, or equivalent decisive evidence. Interpretations that remain **STRONG** or **PROVISIONAL** belong in `hypotheses.md`. Historical interpretations displaced by later evidence are retained as **SUPERSEDED**.

## PNDT, BIOM, and RSGD

The established data relationship is:

```text
PNDT
 ├─ RSCS
 └─ ordered biome entries
        ↓
      BIOM
        ↓
      RSGD
```

PNDT may specify a per-biome RSGD override. The **PROVEN** precedence rule is:

```text
if PNDT biome Resource Generation != NULL:
    EffectiveRSGD = PNDT override
else:
    EffectiveRSGD = BIOM.RNAM
```

PNDT and BIOM RSGDs are not merged. For tested live cases, biome-list construction follows PNDT `BiomeIndex` order before shuffling; Kreet provides direct live proof.

## PRNG

For non-zero PNDT `RSCS`, unsigned 32-bit `RSCS` directly seeds MT19937. The same evolving MT19937 state drives the biome shuffle and subsequent resource-generation draws.

Generation converts a raw word to a float as follows:

```python
raw_float = float32(raw_uint32)
unit_value = float32(raw_float * float32(1.0 / 2**32))
converted = float32(unit_value * float32(0.99999))
```

### Biome-shuffle bounded integer helper

The **PROVEN** trace path is:

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

Rejected draws consume MT words. Bound `1` consumes one word and returns `0`.

### Descendant candidate selection

This is a separate **PROVEN** bounded mechanism:

```text
raw uint32
→ float32(raw)
→ * float32(2**-32)
→ * float32(0.99999)
→ * float32(candidate_count)
→ truncate
```

For `candidate_count > 0`, it consumes exactly one MT word.

## Live Creation Kit Generation Path

Live traces of the Creation Kit Galaxy View Apply operation establish `FUN_1415DCFB0` as the primary per-biome generator exercised by that operation. It handles at least Special category `5`, Common/root category `0`, family-cache interaction, descendant dispatch, and resource/family limits. The reconstructed behaviour agrees with known game/resource results; the supplied addresses are not asserted here to have been independently traced in retail `Starfield.exe`.

### Static enclosing orchestration

Read-only Ghidra analysis establishes `FUN_14152CBC0` at `0x14152CBC0` as the
sole direct caller and the enclosing orchestration function. It initializes a
shared dynamic array of 32-bit resource FormIDs, performs two pre-biome
population passes, and then iterates the shuffled biome work objects. The call
to `FUN_1415DCFB0` is at `0x14152D28F`.

At that call, argument 4 (`R9`) is the shared resource-ID array. It is the same
object whose count `FUN_1415DCFB0` compares against `8`; the temporary context
passed onward lets `FUN_14157F120` recover it through offset `+0x20`.

One prepopulation pass uses `FUN_141548920` at `0x141548920`. It finds category
`6` (Everywhere) entries, writes the selected FormID to biome offset `+0x68`,
and appends the same ID to the shared array. The other pass obtains a
planet-keyed type-`0xAD` form through `FUN_1419FE120`, accesses an array at that
form's `+0x1D8` through `FUN_141A46660`, resolves its entries, deduplicates
their `form +0x70` IDs, and appends them to the same shared array. Its exact
ATMO semantic identity is **STRONG**, not yet PROVEN, and is documented in
`hypotheses.md`.

The generator's diagnostic at `0x1415DD453` explicitly states that
“Atmosphere and Everywhere resources” can fill all available slots. Full
static evidence and the bounded live-trace window are preserved in
`docs/experiments/pre-biome-resource-state-investigation.md`.

The established rarity/category mapping is:

```text
0 Common
1 Uncommon
2 Rare
3 Exotic
4 Unique
5 Special
6 Everywhere
```

### Common/root selection

For the requested RSGD category, stored `RSGDResourceIndex` order is preserved. Selection uses cumulative `Chance / 100`; the first cumulative threshold exceeding the random value wins. Total weights are not normalized.

### Category-5 / category-0 selector

Read-only static analysis of Creation Kit `FUN_141580660` and its focused
helpers establishes the selector mechanism used by `FUN_1415DCFB0` for both
Special category `5` and Common category `0`:

```text
draw one MT19937 binary32 probability in [0, 0.99999]
walk ordered 0x238-byte RSGD entries
require resource/IRES +0x2F8 == requested category
cumulative += (entry +0x24 + category*0x28 chance) * 0.01
return first entry where roll < cumulative
```

The draw occurs before enumeration, so each selector call consumes exactly one
raw MT word even if the category has no entries, has one entry, or has a single
`100%` entry. Categories `5` and `0` use the same selector path, probability
logic, RNG consumption, and `{resource pointer, entry+8}` result shape; there
is no Special-only branch inside `FUN_141580660`.

Callisto provides paired **PROVEN live** CK evidence: category `5` returned
Helium-3 `000057F5`, then category `0` returned Iron `000057C7`. Its extracted
RSGD rows give Helium-3 Special chance `100`, Iron Common chance `30`, and
Aluminum Common chance `70`, consistent with the statically proven ordered
cumulative mechanism. Exact addresses and evidence boundaries are recorded in
`docs/experiments/special-common-selector-investigation.md`.

### IRES graph and descendants

The resource-family graph is stored in IRES data:

```text
IRES
 ├─ SNAM - Rarity
 └─ Child Resources
```

For rarity levels `1..4`, the candidate builder combines `children(root)` followed by `children(current_structural_node)`, rarity-filters the result, and stable-deduplicates it. Root-source candidates precede current-node-source candidates.

`FUN_14157F120` is the **PROVEN** descendant helper in that live-traced CK path. When capacity permits it builds the requested rarity candidates, draws inclusion probability, draws candidate selection, emits the candidate on inclusion, and continues structurally through the chosen candidate even when omitted.

With zero candidates, exactly one MT word is consumed, nothing is emitted, and the structural node is unchanged. This states only what the trace establishes.

After a new Common family is selected, its root is emitted unconditionally and descendant generation proceeds through rarities `1..4`.

The first selection of a Common/root family on a planet generates and caches its family configuration. Later biomes selecting the same root reuse the cache: the descendant helper is not called again and consumes no descendant RNG.

## Capacity Limits

Maal VIII live traces establish these checks:

```text
0x1415DD0A3  cmp dword ptr [r12], 8
0x1415DD0A8  jae ...
0x1415DD0D3  cmp dword ptr [rsi], 5
0x1415DD0D6  jae ...
0x1415DD0DC  cmp dword ptr [r12], 8
0x1415DD0E1  jae ...
```

The `8` comparisons prove an internal resource-container limit of `8`. The `5` comparison proves that the generation path contains a `count >= 5` guard on the structure associated with generated/cached Common-family configurations. The most likely interpretation is a five-family or five-generated-family-configuration limit, but that broader semantic interpretation remains **PROVISIONAL** because the structure's exact general role has not been independently established.

The descendant helper's early return is:

```text
0x14157F14D  mov rax,[rcx+20h]
0x14157F151  cmp dword ptr [rax],8
0x14157F154  jae 14157F371
```

At the observed comparison, `internal_resource_count = 8`. Thus:

```text
if internal_resource_count >= 8:
    return current_structural_node
```

The early return consumes no RNG. The internal count must not be described as merely eight visible CK resources.

## Worked Cases and Validation

The reconstructed runtime model reproduced exact known results for Oberon, Mimas, Decaran VII-b, Kreet, and Algorab I.

Standalone reproducer validation reached:

```text
Validation population:       1,444
Exact matches:               1,281
Mismatches:                    163
Exact rate:                  88.71%
Errors:                         0
```

The mismatches became research guides rather than wholesale disproof of the core algorithm.

## SurveyAggregator and the Old Oracle

`SurveyAggregator` (RE ID `1016657`) and derived `data/planet-all-resources.csv` remain valuable, provenance-preserved empirical observations. Current evidence proves that the dataset omits at least some atmosphere-derived inorganic resources, so it is not an authoritative complete final planetary-resource oracle and does not expose biome identity in current use. It appears to correspond closely to the CK/biome-generation-visible resource set, but that correspondence is **STRONG / PROVISIONAL**, not a proven engine contract; the exact upstream state exposed by `SurveyAggregator` remains open.

Earlier aggregate family and biome results derived from this dataset remain useful when treating it as a qualified proxy, including the observed root invariant and `FamilyCount <= BiomeCount` constraint. They must not be generalized silently to all resource origins.

### Preserved empirical constraints from the qualified dataset

The ordinary family model used in that analysis was:

| Root | Other modelled members |
|---|---|
| Aluminum | Beryllium, Neodymium, Europium, Indicite |
| Nickel | Cobalt, Platinum, Palladium, Tasine |
| Lead | Tungsten, Titanium, Dysprosium, Silver, Mercury |
| Uranium | Iridium, Vanadium, Plutonium, Vytinium |
| Copper | Fluorine, Tetrafluorides, IonicLiquids, Gold, Antimony |
| Chlorine | Chlorosilanes, Lithium, Caesium, Xenon, Aldumite |
| Iron | Alkanes, Tantalum, Ytterbium, Rothicite |
| Argon | Benzene, CarboxylicAcids, Neon, Veryl |

Water and Helium3 were treated as standalone resources for the family-count analysis. IRES data now directly establishes the resource graph rather than leaving this only as an aggregate model.

Across 1,549 body/family cases and 2,064 descendant occurrences, the qualified dataset had zero cases where a descendant was present without its root. Intermediate members were not mandatory: deeper members could occur while intermediate members were skipped.

The PNDT-to-BIOM xEdit export contained 3,192 biome rows and reproduced all six known Montara Luna biomes and composition percentages. Joining it to the qualified resource dataset produced zero `FamilyCount > BiomeCount` violations across 1,436 analysed family-bearing bodies; 1,038 had equal counts, including 880 one-family/one-biome bodies. These are planet-level empirical constraints, not direct proof of per-biome co-location.

Treating Indicite or Vytinium as separate standalone families introduced count violations on Katydid III and Decaran VII-b respectively, supporting their placement within the Aluminum and Uranium graphs.

## Atmospheric Resources

Planet records reference ATMO atmosphere records. Bethesda reflection data resolves effective values as:

```text
root/default ATMO: REFL = complete/base reflected object
child ATMO:        RFDP = reflection parent
                   RDIF = local differences/overrides
```

The Creation Kit displays the resolved inherited values.

**PROVEN static examples:**

- Maal VIII's effective ATMO is nitrogen and explicitly contains Chlorine. Its raw `RDIF` includes literal `AT_TYPE_NITROGEN` and `D5 57 00 00`, the little-endian FormID `000057D5` for Chlorine.
- Niira's effective atmospheric list contains Chlorine and Water; its serialized reflected `LIST` count is `2`, followed by both IRES FormIDs.
- Kreet's atmospheric Helium-3 uses the same reflected list structure.
- Vectera has no atmospheric resources and contains a zero-count `LIST`.
- Titan and Maal IV demonstrate inherited Water. Titan inherits through `AtmoDefaultDense → AtmoOrangeBaseDense01 → ATMO_Titan`; the root/default Water list is in `REFL`, not `RDIF`.

The generic interpretation that a sole zero-count `LIST` explicitly clears Inorganic Resources remains **PROVISIONAL** pending full property-identifier decoding.

### Atmospheric extract

The dedicated xEdit exporter `Starfield_ExportPlanetAtmosphericResources` resolves ATMO inheritance and emits one row per planet × effective atmospheric resource while preserving provenance. No repository location is asserted here.

Full-population extraction produced:

```text
335 planet × atmospheric-resource rows
297 distinct planets/moons with atmospheric resources
6 atmospheric resource types
0 duplicate planet × resource rows
maximum 2 atmospheric resources on one body
```

| Resource | Rows |
|---|---:|
| Water | 260 |
| Chlorine | 32 |
| Helium-3 | 16 |
| Fluorine | 11 |
| Benzene | 8 |
| Alkanes | 8 |

### Maal VIII capacity observation

The CK Resource Generation view shows Iron, Nickel, Water, Uranium, Iridium, Vanadium, and Copper. The in-game survey adds Chlorine, and Maal VIII's ATMO explicitly assigns that Chlorine. The old oracle omitted it.

In the final Iron-biome trace, Iron insertion brought the internal count to `8`; the level-1 descendant helper returned immediately, preventing Alkanes and consuming no RNG. The exact atmospheric insertion function/order is not yet proven; the shared-capacity interpretation is recorded as **STRONG** in `hypotheses.md`.

## Superseded Static Trail

The following low-level analysis remains valid historical evidence:

```text
ResourceViewWidget::OnApplySeed
    ↓
FUN_1431bc320
    ↓ temporary TESContainer / FUN_140e0aab0
FUN_140e457b0
    ↓
generic leveled-list machinery
```

Its interpretation as the primary biome-resource allocation route is **SUPERSEDED / DEPRIORITISED**. Later live x64dbg tracing of the Creation Kit Galaxy View Apply operation establishes `FUN_1415DCFB0` and `FUN_14157F120` as the primary path exercised by that operation. The older path may still be legitimate CK/UI or downstream machinery; no researcher should assume it participates in biome allocation without new live evidence.

## Provenance-Aware Validation Rule

Validation must preserve resource origins rather than collapse them early:

```text
AtmosphericResources
BiomeGeneratedResources
EverywhereResources
SpecialResources
FinalPlanetaryResources
```

An atmospheric FormID must not mask failure of a biome/RSGD path expected to produce the same FormID. Continue reconciling `planet-all-resources.csv` independently as an empirical proxy for the CK/biome-visible channel, without treating that correspondence as a proven contract, and reconcile the xEdit ATMO extract independently against the atmospheric channel. Deduplicate origins only for final player-facing membership.
