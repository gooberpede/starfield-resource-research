# Hypotheses and Open Models

This file contains interpretations not directly established by decisive evidence. Labels follow `AGENTS.md`.

## H1 — Atmospheric resources share the eight-entry capacity

**STRONG**

Current interpretation:

```text
effective ATMO inorganic resources
    ↓
planet-wide resource state before/during biome generation
    ↓
same eight-entry internal container checked by FUN_1415DCFB0/FUN_14157F120
```

Maal VIII provides the clearest evidence: ATMO supplies Chlorine; the CK biome view has seven resources; the in-game survey has those seven plus Chlorine; and the final Iron-biome trace reaches internal count `8`, causing the proven no-RNG descendant early return and preventing Alkanes.

Population comparison independently supports the interpretation: `101 / 163` reproducer-mismatch planets have at least one atmospheric inorganic resource. A dense subset has atmosphere-only resources missing from both the old oracle and current reproducer, with counts matching the Maal VIII capacity pattern.

The exact atmospheric insertion/loading function and ordering remain unresolved and must not be called proven.

## H2 — Zero-count reflected LIST explicitly clears atmospheric resources

**PROVISIONAL**

Vectera has no atmospheric resources and a zero-count `LIST`. Treating a sole zero-count list as an explicit Inorganic Resources clear fits current evidence, but the reflected property identifier has not been fully decoded.

## H3 — One ordinary resource family per biome

**STRONG** as a planner model, not proven as a universal engine rule.

In the qualified SurveyAggregator-derived proxy dataset, `FamilyCount <= BiomeCount` had zero violations across 1,436 analysed bodies, including 880 one-family/one-biome bodies. The dataset appears to correspond closely to the CK/biome-visible channel, but its exact semantic contract remains unresolved. Aggregate planet-level counts cannot prove exact biome membership.

Practical heuristic: required resources from different ordinary inorganic families should not be assumed co-located in one normal biome. This remains a planning heuristic, not proof of a global one-family-per-biome mapping.

## H4 — Five-family check semantics

**PROVISIONAL**

The `count >= 5` guard in `FUN_1415DCFB0` is directly observed in the live-traced CK generation path and therefore **PROVEN**. Its interpretation as a general five-family or five-generated-family-configuration limit fits the trace, but remains **PROVISIONAL** because the structure's exact general role has not been independently established.

## Open Runtime Question

The next Ghidra investigation is documented but intentionally not executed:

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

Maal VIII is the preferred live case because `ATMO_MaalVIII → Chlorine`, while Chlorine appears in the in-game survey but not the CK biome Resource Generation view or old plugin output.

## Superseded Interpretations

### Creation Kit leveled-list trail as primary allocation path

**SUPERSEDED / DEPRIORITISED AS PRIMARY ALLOCATION PATH**

Earlier work proposed that `ResourceViewWidget::OnApplySeed → FUN_1431bc320 → FUN_140e457b0 → generic leveled-list machinery` contained or closely approached the target biome allocator. Live traces of the Creation Kit Galaxy View Apply operation instead establish `FUN_1415DCFB0` and `FUN_14157F120` as the primary generation path exercised by that operation.

The old trail's calling-convention, `TESContainer`, mixed ordinary/`TESLevItem`, and generic resolver findings remain technically valid. It may still be CK/UI or downstream machinery. New live evidence would be required before reconnecting it to biome allocation.

### Direct RSCS seeding unresolved

**SUPERSEDED**

Earlier static work could not identify a simple `RSCS → global PRNG reseed` pattern and speculated about an effective-level selector. Live tracing now proves that non-zero unsigned 32-bit RSCS directly seeds MT19937 and that its evolving state drives shuffle and generation.

### Root insertion mechanism unresolved

**SUPERSEDED**

The earlier alternative that family roots might merely be statistically unavoidable has been displaced. Live tracing proves unconditional Common/root emission when a new family is selected.

### Leveled lists may encode the resource-family graph

**SUPERSEDED**

The resource graph is established in IRES `SNAM` rarity and Child Resources data. The generic leveled-list resolver's mixed-entry capability remains a valid static fact, but it no longer explains the current family graph.

### SurveyAggregator as complete final oracle

**SUPERSEDED**

The old oracle omits at least some atmosphere-derived inorganic resources. It remains a useful empirical proxy for reconciling the CK/biome-generation-visible channel, but the correspondence is **STRONG / PROVISIONAL** rather than a proven engine contract. The exact upstream state exposed by `SurveyAggregator` remains open.
