# Special/Common selector evidence

This directory preserves the read-only Creation Kit Ghidra evidence used by
`docs/experiments/special-common-selector-investigation.md`.

## Source

```text
program:    CreationKit.exe
MD5:        0215f03ec24922dfd4015dcdc5317dc4
image base: 0x140000000
```

The export was produced from the existing analysed project with analysis
disabled and the project opened read-only:

```powershell
<ghidra-install>\support\analyzeHeadless.bat `
  <ghidra-project-dir> StarfieldCK `
  -process CreationKit.exe -readOnly -noanalysis `
  -scriptPath <repository>\ghidra\scripts `
  -postScript ExportFunctionsByAddress.java `
  <output-directory> `
  141580660 14157C470 140924800 144D8C490
```

`ExportFunctionsByAddress.java` reads the Ghidra analysis database and writes
external text/JSON files only. It does not start a transaction or modify the
Ghidra project.

## Contents

- `FUN_141580660__141580660/` — requested selector, including decompilation,
  instructions, metadata, callers, callees, and data references.
- `FUN_14157c470__14157c470/` — ordered category filter and cumulative chance
  helper.
- `FUN_140924800__140924800/` — MT19937-to-binary32 probability helper.
- `FUN_144d8c490__144d8c490/` — selector range provider.
- `constants.json` — exact relevant binary32 constants extracted from the
  analyzed executable's mapped PE sections.
- `manifest.json` — run-level export manifest.

The constants were checked read-only against the executable's PE section
mapping. No proprietary binary content is copied here beyond the small scalar
values needed to reproduce the analysis.

See the [central provenance record](../../../PROVENANCE.md) for the recorded
Ghidra version, executable identity, and known version gaps.
