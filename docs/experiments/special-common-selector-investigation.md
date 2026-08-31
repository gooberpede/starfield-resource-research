# Special/Common Selector Investigation

## Objective

This static-only investigation asks how Creation Kit `FUN_141580660` at
`0x141580660` selects category `5` (Special) and category `0` (Common) for
`FUN_1415DCFB0`. The Ghidra project was opened read-only with analysis disabled.
No new x64dbg trace, reproducer change, xEdit export, or Ghidra database change
was performed.

The focused export and reproduction command are preserved under
`docs/experiments/evidence/special-common-selector/`.

## Prior live evidence

**PROVEN LIVE (Creation Kit Galaxy View Apply):** Callisto's single
`CrateredNoLife09` biome made both calls through the same selector:

```text
category 5 -> 000057F5 Helium-3
category 0 -> 000057C7 Iron
```

The Special result entered the shared planet-wide resource-ID array before the
Common call. These live results are prior evidence; this experiment did not
repeat them. The brief's `/mnt/data/callisto-category-5-call.trace64` was not
present at an accessible Windows or repository path, so no new per-instruction
register extraction from that trace is claimed.

## Static function map

```text
FUN_1415DCFB0
    | 0x1415DD09E, category 5
    | 0x1415DD0F2, category 0
    v
FUN_141580660
    |-- 0x141580699 -> FUN_144D8C490: range [0.0, 0.99999]
    |-- 0x1415806A8 -> FUN_140924800: one MT19937 binary32 draw
    `-- 0x14158070C / 0x14158080C -> FUN_14157C470
            ordered entry scan, category filter, cumulative chance, return
```

`FUN_141580660` first tries the optional direct generation-data pointer in its
context. If that does not produce a two-pointer result, it walks the dependency
array at the resolved source object's `+0x728` in stored order and applies the
same helper to each resolved generation-data object. The scan stops at the first
non-null two-pointer result.

## Parameter and data-structure findings

The Windows x64 signature recovered by Ghidra is:

```text
RCX / param_1  selector context
RDX / param_2  caller-owned 16-byte result { resource, entry+8 }
R8B / param_3  requested category byte
```

`FUN_1415DCFB0` constructs the selector context at `0x1415DD07A`–
`0x1415DD08F`:

| Context offset | Best-supported meaning | Evidence |
|---|---|---|
| `+0x00` | MT19937 state pointer | passed as `RCX` to `FUN_140924800` at `0x1415806A8` |
| `+0x08` | current biome work/result object | receives category-indexed FormID and roll telemetry through `FUN_14157C470` |
| `+0x10` | pointer to optional direct generation-data pointer | dereferenced and tried first at `0x1415806FA`–`0x14158070C` |
| `+0x18` | pointer to resolved source object with dependency array at `+0x728` | fallback count/data loads at `0x141580737`–`0x14158074C` |

The exact C++ types of the two source members are not present in the current
Ghidra database. Their observed dataflow is therefore stated instead of
inventing types. In the established higher-level model these objects supply the
effective RSGD entries for the biome.

`FUN_14157C470` treats each generation object as:

```text
+0x118  uint32 entry_count
+0x120  pointer to ordered entry array

entry stride: 0x238 bytes
entry +0x00: dependency-managed IRES/resource pointer
entry +0x24 + category*0x28: category-specific float chance
```

The helper returns a pair:

```text
result[0] = selected resource/IRES pointer
result[1] = selected entry + 0x08
```

The caller uses `result[0] + 0x70` as the selected 32-bit FormID.

## Category filtering

**PROVEN STATIC:** `FUN_14157C470` loads the requested byte at `0x14157C494`,
loads the entry's resource pointer at `0x14157C5A3`, and compares:

```text
0x14157C5AA  CMP byte ptr [RDX + 0x2F8], BPL
0x14157C5B1  JNZ 0x14157C5E5
```

`RDX` is the resolved resource/IRES object and `BPL` is the zero-extended
requested category. Thus category membership is read directly from resource
offset `+0x2F8`. Under the already established mapping, `5` is Special and `0`
is Common.

Stored order is preserved. Entries advance by `0x238` at `0x14157C5E5`, and
the helper returns immediately after the first threshold win.

## Probability and selection

For a matching entry, `FUN_14157C470` computes:

```text
chance_address = entry + 0x24 + category * 0x28
cumulative += float32(chance * 0.01f)
selected if roll < cumulative
```

Exact instructions:

```text
0x14157C5B3–0x14157C5BE  derive category*0x28 and chance address
0x14157C5BE–0x14157C5CA  chance * 0.01f and cumulative addition
0x14157C5DE–0x14157C5E3  compare roll with cumulative; branch on roll < cumulative
0x14157C5F7               store selected resource pointer
0x14157C5FA               store selected entry + 0x08
0x14157C611–0x14157C625  copy and return the 16-byte result
```

The exact binary32 `0.01f` is loaded at `0x14157C4E1` from `0x148544E84`.
The chance offsets relevant here are:

```text
category 0: entry + 0x24  (BiomeCommonChance correlation)
category 5: entry + 0xEC  (BiomeSpecialChance correlation)
```

**STRONG:** the semantic column names are established by the xEdit layout and
Callisto data correlation: Iron has Common `30`, Aluminum Common `70`, and
Helium-3 Special `100`. Static code proves the indexed offsets and arithmetic;
the current Ghidra types do not name those fields.

Weights are cumulative and are not normalized. Therefore multiple qualifying
entries retain stored RSGD order, and the first cumulative threshold greater
than the roll wins. A total below `100` can return no result. A total above
`100` makes later excess weight unreachable once cumulative first exceeds the
maximum roll; the code performs no normalization or total-weight pre-pass.

## RNG consumption

**PROVEN STATIC:** `FUN_141580660` obtains its roll before checking any source
or entry:

```text
0x141580699  obtain [0.0f, 0.99999f] range
0x1415806A8  call MT19937 float helper through thunk -> FUN_140924800
0x1415806E4–0x1415806F4  roll = raw_unit * (max-min) + min
```

`FUN_140924800` computes one binary32 generator word divided by `2^32` for this
call. Its precision calculation is `ceil(24 / log2(2^32)) = 1`, so the loop at
`0x140924870`–`0x1409249EF` executes once. The selector then multiplies that
binary32 unit value by the exact range maximum `0.9999899864196777f`.

Equivalent selector conversion:

```text
raw uint32
-> float32(raw)
-> * float32(2^-32)
-> * float32(0.99999)
```

This is the existing Starfield binary32 probability path, without a candidate
count multiplication. It consumes exactly one raw MT19937 word per selector
call:

- even when no entry has the requested category;
- even with one eligible entry;
- even when that entry's chance is `100`;
- equally for category `5` and category `0`.

No additional RNG call occurs during enumeration or selection.

## Category 5 versus category 0

| Question | Result |
|---|---|
| Same code path | Yes |
| Same candidate enumeration | Yes |
| Same probability logic | Yes |
| Same RNG consumption | Yes: one raw word before enumeration |
| Same return shape | Yes: `{resource pointer, entry+8}` |
| Special-only behavior | None in this selector |
| Common-only behavior | None in this selector |

The requested byte selects both the `IRES +0x2F8` equality value and the
chance field at `entry +0x24 + category*0x28`. All later differences occur in
`FUN_1415DCFB0`, which handles the returned Special and Common resources
differently.

## Callisto reconciliation

The extracted Callisto RSGD rows are, in order:

```text
0  Iron      category 0  Common chance 30
1  Aluminum  category 0  Common chance 70
2  Helium-3  category 5  Special chance 100
```

For category `5`, Iron and Aluminum fail the category comparison. Helium-3
adds `1.0` to the cumulative threshold, so every selector roll in
`[0, 0.99999]` selects Helium-3. The `100` case still consumed the selector's
up-front MT word.

For category `0`, Iron contributes the first threshold `0.30` and Aluminum
extends it to `1.00`. The prior live result of Iron therefore proves that the
Common roll was below `0.30`; it does not indicate a hard-coded Iron choice.
Using Callisto's unsigned seed `2041483075` and the statically recovered
binary32 conversion reconstructs selector probabilities approximately
`0.35974094` for Special and `0.00357435` for Common when no single-biome
shuffle draw occurs, which predicts the observed Helium-3 then Iron pair.
This numeric state reconstruction is **STRONG**, not a newly extracted live
register observation.

## Evidence summary

### PROVEN

- **PROVEN STATIC:** requested category is compared with resource/IRES byte
  `+0x2F8` at `0x14157C5AA`.
- **PROVEN STATIC:** ordered `0x238`-byte entries use chance offset
  `0x24 + category*0x28`, scale by `0.01f`, and accumulate without
  normalization.
- **PROVEN STATIC:** the first entry satisfying `roll < cumulative` is returned
  as `{resource pointer, entry+8}`.
- **PROVEN STATIC:** one MT19937 word is converted through the binary32
  probability path before enumeration on every selector call.
- **PROVEN STATIC:** category `5` and `0` have no selector-specific branch other
  than category comparison and indexed chance field.
- **PROVEN LIVE (prior):** Callisto returned Helium-3 for category `5` and Iron
  for category `0` in Creation Kit Galaxy View Apply.

### STRONG

- Entry `+0x24` and `+0xEC` correspond respectively to the xEdit-exported
  `BiomeCommonChance` and `BiomeSpecialChance` fields.
- The reconstructed Callisto selector values explain the live pair exactly.

### PROVISIONAL

- The exact C++ names/types of the selector context's optional direct source
  and `+0x728` fallback source remain unavailable in the current Ghidra type
  information. Their dataflow and entry layout are established.

### OPEN

- The supplied `.trace64` was unavailable in the accessible workspace, so the
  exact Callisto raw MT words and the live `entry +0x24/+0xEC` memory reads were
  not independently re-extracted in this task.

## Recommended next experiment

No multi-candidate Special experiment is required to recover the rule: static
code proves ordered cumulative selection. The smallest useful optional live
confirmation is an automated trace of one category-5 RSGD with two Special
entries and non-trivial weights, recording `RBP`, `[RDX+0x2F8]`, the chance
load at `0x14157C5BE`, cumulative value at `0x14157C5CA`, and branch at
`0x14157C5E3`. This would validate field naming and live values, not discover a
missing selector branch.
