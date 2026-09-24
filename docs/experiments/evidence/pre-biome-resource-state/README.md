# Pre-biome resource-state static evidence

This directory preserves the focused Ghidra evidence used by
the [pre-biome resource-state investigation](../../pre-biome-resource-state-investigation.md).

## Source

```text
Program:    CreationKit.exe
MD5:        0215f03ec24922dfd4015dcdc5317dc4
Image base: 0x140000000
Ghidra:     12.1.2 PUBLIC
Exported:   2026-08-31 UTC
```

The Ghidra project was opened with `-readOnly -noanalysis`. The exporter did
not start a transaction or change symbols, types, labels, comments, function
names, or other project state.

## Reproduction

From the Ghidra installation directory, use the repository script with a small
explicit address set:

```powershell
<ghidra-install>\support\analyzeHeadless.bat <ghidra-project-dir> StarfieldCK `
  -process CreationKit.exe -readOnly -noanalysis `
  -scriptPath <repository>\ghidra\scripts `
  -postScript ExportFunctionsByAddress.java <output-directory> `
    1415DCFB0 14152CBC0 141548920 1419FE120 141A46660 14157E850 14158DBE0
```

Each prefix names the original Ghidra function. `metadata.json` records the
program identity and analyzed signature; `decompiled.c` and `instructions.txt`
normally preserve pseudocode and disassembly; `callers.json` and `callees.json`
preserve exact direct call sites. The files are raw exporter output except for
being copied from the ignored `exports/` working area into this tracked
evidence directory and the explicitly documented `FUN_14152CBC0` excerpting
below.

The selected set is intentionally bounded. It includes the proven generator,
its sole direct caller, the two pre-biome helpers, the `+0x1D8` accessor, and
the orchestration function's two immediate wrappers. It is not a recursive
call-graph export.

## `FUN_14152CBC0` excerpt scope

The enclosing orchestration function is intentionally represented by selected
contiguous excerpts rather than a complete function dump:

- `FUN_14152cbc0-decompiled-excerpt.c` retains exporter lines 1–277, from the
  original function declaration through the end of the loop calling
  `FUN_1415DCFB0`.
- `FUN_14152cbc0-instructions-excerpt.txt` retains the contiguous address range
  `0x14152CBC0`–`0x14152D2A1`.

Together these exact exporter regions preserve the pre-existing/atmosphere
shared-state population, biome construction and shuffle setup,
Everywhere/category-6 pre-pass, ordering before per-biome generation, and calls
into `FUN_1415DCFB0`. The later biome-percentage normalization, unrelated error
handling, post-generation bookkeeping, and cleanup/destruction regions are not
distributed. The complete executable and complete decompiler output are not
distributed.

The original name/address, relevant instruction addresses, contiguous ordering,
source executable identity, and Ghidra provenance remain recorded. See the
[central provenance record](../../../PROVENANCE.md).
