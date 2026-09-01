# x64dbg Runtime Generation Findings

## Purpose and evidence boundary

This note preserves decisive live x64dbg findings that displaced parts of the earlier Ghidra interpretation. Addresses below are recorded only where supplied by the underlying traces. Static results that remain technically valid are preserved, even where their former high-level interpretation is **SUPERSEDED**.

When static interpretation and later live execution conflict, live execution governs the current model.

## Primary live path

- `FUN_1415DCFB0` (`0x1415DCFB0`) — **PROVEN** primary per-biome generator exercised by the live-traced Creation Kit Galaxy View Apply operation; diagnostics identify `BGSPlanetDataManager.cpp`.
- `FUN_14157F120` (`0x14157F120`) — **PROVEN** descendant helper in that CK path.

The reconstructed behaviour agrees with known game/resource results. These addresses are not presented as independently traced retail `Starfield.exe` addresses.

The older `ResourceViewWidget::OnApplySeed → FUN_1431bc320 → FUN_140e457b0 → generic leveled-list machinery` route is **SUPERSEDED / DEPRIORITISED AS PRIMARY ALLOCATION PATH**. Its `TESContainer`, ABI, and resolver findings remain legitimate CK/UI or downstream evidence.

## Seed, shuffle, and generation

For non-zero PNDT `RSCS`, live execution proves direct unsigned 32-bit seeding of MT19937. The same evolving state is used for biome shuffle and later generation draws. Tested biome lists are constructed in PNDT `BiomeIndex` order before shuffle; Kreet directly proves this ordering.

The shuffle's rejection-based bounded integer trace is:

```text
0x14152CEBD -> 0x1401714A8
0x1401714A8 -> 0x141560E90
0x141560F5A -> 0x14001D63D
0x14001D63D -> real helper 0x141587240
```

Rejected values consume MT words, and bound `1` consumes one word while returning `0`.

Descendant selection uses a distinct float32 path:

```text
raw uint32 → float32 → * float32(2**-32) → * float32(0.99999)
           → * float32(candidate_count) → truncate
```

For a non-empty candidate set this consumes exactly one MT word. These mechanisms must not be consolidated into one bounded-RNG abstraction.

## Per-biome and descendant behaviour

Common/root selection preserves stored `RSGDResourceIndex` order and chooses the first unnormalized cumulative `Chance / 100` threshold exceeding the random value.

IRES rarity (`SNAM`) and Child Resources encode the family graph. At rarity levels `1..4`, descendants are drawn from stable-deduplicated `children(root) + children(current_structural_node)`, with root-source candidates first. A newly selected Common root is inserted unconditionally. Reused roots obtain their cached family configuration without more descendant calls or RNG.

With zero candidates, the descendant helper consumes exactly one MT word, emits nothing, and leaves the structural node unchanged.

## Capacity checks

The observed per-biome checks are:

```text
0x1415DD0A3  cmp dword ptr [r12], 8
0x1415DD0A8  jae ...
0x1415DD0D3  cmp dword ptr [rsi], 5
0x1415DD0D6  jae ...
0x1415DD0DC  cmp dword ptr [r12], 8
0x1415DD0E1  jae ...
```

The `8` comparisons prove the shared resource-state guard. Later Bara VII-d
live work established that the `5` comparison guards the collection of five
distinct generated/cached Common-family configurations in this generation path;
ordinary cache reuse does not increment it.

The descendant early return is:

```text
0x14157F14D  mov rax,[rcx+20h]
0x14157F151  cmp dword ptr [rax],8
0x14157F154  jae 14157F371
```

At the dedicated Maal VIII observation, the internal count was `8`. The helper returned the current structural node and consumed no RNG.

## Maal VIII and atmosphere

The CK biome Resource Generation view has seven entries: Iron, Nickel, Water, Uranium, Iridium, Vanadium, and Copper. The in-game survey additionally has Chlorine. ATMO data explicitly assigns Chlorine, while the old plugin/oracle omits it.

In the final Iron-biome trace, Iron insertion brought the internal count to `8`; the rarity-1 descendant call returned immediately, preventing Alkanes without consuming RNG. This directly proves the limit behaviour.

**Later PROVEN LIVE reconciliation:** a focused Maal VIII trace observed
atmospheric Chlorine `000057D5` entering the same shared planet-wide
resource-ID state before Everywhere and the shuffled per-biome generator.

The population comparison provides independent support: `101 / 163` mismatch planets have atmospheric inorganic resources.

## Validation and provenance

At the time of this experiment, the reconstructed model exactly reproduced
Oberon, Mimas, Decaran VII-b, Kreet, and Algorab I. The then-current validation
was 1,281 exact matches from 1,444 bodies (88.71%), with 163 mismatches and no
errors.

**HISTORICAL:** subsequent atmosphere, Everywhere, five-tree, shared-eight,
fallback, and Special-order corrections reached 1,444 / 1,444 exact with zero
mismatches and zero errors. Targeted CK biome regressions and the fresh ten-body
CK/retail holdout are also exact.

Resource origins must remain separate during validation. Atmospheric membership cannot silently satisfy an expected biome/RSGD result. Continue validating `planet-all-resources.csv` independently as an empirical proxy for the CK/biome-visible channel, while recognizing that this correspondence is not a proven semantic contract, and validate the ATMO extract independently against the atmospheric channel. Deduplicate FormIDs only when constructing final player-facing membership.

## Historical next question (completed)

Starting at `FUN_1415DCFB0`, identify the enclosing planet-generation caller/loop and trace activity before the first per-biome call, especially effective ATMO resource insertion into the shared resource container. Maal VIII atmospheric Chlorine is the preferred live case.

This investigation was later completed. `FUN_14152CBC0` is the enclosing
orchestrator, and Maal VIII atmospheric Chlorine was observed in shared state
before Everywhere and the first per-biome call. It is not an active next task.
