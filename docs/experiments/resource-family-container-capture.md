# Resource-family container capture

> **SUPERSEDED / DEPRIORITISED AS PRIMARY ALLOCATION PATH:** This note preserves a valid static experiment and its `TESContainer`/leveled-list evidence. Later live tracing of the Creation Kit Galaxy View Apply operation established `FUN_1415DCFB0` and `FUN_14157F120` as the primary generation path exercised by that operation, and IRES data as the family graph. Do not treat the proposed live capture below as the current next investigation.

## Objective

Test whether the Creation Kit resource-preview path represents inorganic
resource families as ordinary `TESContainer` entries plus nested `TESLevItem`
structures, and whether RSGD family choice occurs before or inside leveled-list
resolution.

The required live stages are:

```text
source at *(ResourceViewWidget+0xA0)+0x20
    -> copied temporary TESContainer
    -> separately allocated resolved TESContainer
```

This pass produced the reusable static capture contract. It did not produce a
live family case: static Ghidra has no CK heap or QSpinBox state, and no Creation
Kit case was available to observe.

## Setup and method

`ExportResourceResolutionEvidence.java` was run against the analysed
`CreationKit.exe` project. The GUI held the original project lock, so the
project was copied under ignored `scratch/` and processed with:

```text
-process CreationKit.exe -readOnly -noanalysis
```

The original project was not modified. The exporter starts no transaction and
does not rename functions, create labels/comments, change signatures, apply
types, write memory, or alter analysis state. It writes plain files under
`exports/resource-resolution/<case-name>/`.

The verified generated run is:

```text
exports/resource-resolution/static-template/
```

## Mechanically supported capture points

Runtime addresses are the live `CreationKit.exe` module base plus the RVA.

| Stage | Static address | RVA | State to capture |
|---|---:|---:|---|
| source, before copy | `0x1431BC350` | `0x31BC350` | R8 source; RCX temporary destination |
| pre-resolution / selector | `0x1431BC375` | `0x31BC375` | RCX input; RDX output slot; R8 context; R9W selector |
| post-resolution | `0x1431BC37A` | `0x31BC37A` | dereference saved resolver-entry RDX output slot |

The resolver call targets thunk `0x14013A471`, resolving to
`FUN_140e457b0` at `0x140E457B0`.

## Selector evidence

The caller loads `ResourceViewWidget+0x98`, calls `QSpinBox::value`, then runs:

```asm
1431BC360  MOVZX R9D,AX
```

The fourth resolver parameter is therefore the unsigned low 16 bits of the
QSpinBox integer, passed in R9W. This caller performs no further arithmetic
transform. The exact value for a particular preview is runtime state and was
not captured; `selector.json` records `null` rather than inventing it.

## Container behavior and layout

The temporary input layout is mechanically supported as:

```text
container +0x40 : uint32 entry count
container +0x44 : uint32 capacity
container +0x48 : entry-array pointer

entry size      : 0x18
entry +0x00     : int32 quantity/count
entry +0x04     : unidentified/padding
entry +0x08     : TESBoundObject/form pointer
entry +0x10     : metadata pointer
```

`FUN_140e457b0` allocates a new `TESContainer`, stores its pointer through RDX,
and iterates the temporary input. An entry that does not dynamically cast from
`TESBoundObject` to `TESLevItem` is copied to the new container. A leveled entry
is evaluated through `FUN_140dddba0` using `object+0x340`, the 16-bit selector,
and input quantity; results are appended to the new container.

This corrects a consequential capture assumption: resolution does not mutate
the temporary input into the post state. The post state is a separate container
reached through the output slot.

## Runtime limitation and smallest practical instrumentation plan

Static Ghidra cannot reveal live source entries, identify live leveled objects,
walk their children, or establish that terminal forms are `IRES`. The smallest
practical next run is an observation-only native debugger session:

1. Open a known CK planet/biome and choose a Resource Seed that selects a
   documented family.
2. Set breakpoints at the three exported RVAs using the live module base.
3. At the copy call, save R8 and enumerate source `+0x40/+0x48` in 0x18-byte
   records before executing the copy.
4. At resolver entry, enumerate RCX, save RDX as the output-slot address, and
   record R9W exactly.
5. At the return breakpoint, dereference the saved output slot and enumerate
   the resolved container before `FUN_140f5fac0` consumes it.
6. For each form proven to be `TESLevItem`, walk entries to depth 8, stopping on
   cycles, repeated addresses, null forms, unsupported types, or the limit.
7. Resolve FormID, EditorID, and form type only with mechanically verified CK
   fields/helpers. Do not guess offsets or call unverified engine helpers.
8. Populate the generated stage, diff, tree, leaf, correlation, and topology
   artifacts from that single coherent run.

This plan requires breakpoints and memory reads only. It does not patch code,
game data, seed logic, or live objects.

## Selected cases and evidence status

No live case was captured in this pass.

| Requested test | Result |
|---|---|
| Nickel linear family | insufficient evidence — runtime case not run |
| Lead/Copper branching family | insufficient evidence — runtime case not run |
| source contents | not captured |
| temporary pre-resolution contents | not captured |
| exact selector | not captured; ABI/provenance established |
| post-resolution contents | not captured |
| recursive `TESLevItem` structure | not captured |
| terminal IRES leaves | not captured |
| source-vs-temporary diff | not captured |
| pre-vs-post diff | not captured |
| RSGD correlation | not captured |

Generated empty entry arrays are explicitly placeholders and are not evidence
of empty containers.

## Hypothesis and model classification

Static evidence proves only that the generic resolver can accept ordinary
and/or leveled entries, preserve ordinary entries in a new output, and
materialize leveled results into that output. It does not prove that the
resource preview supplies both kinds, that leaves are `IRES`, or that nesting
encodes a family.

Therefore:

- family-tree-as-leveled-list: structurally plausible, not live-tested;
- root-invariant mechanism: insufficient evidence;
- Model 1, Model 2, and Model 3: insufficient evidence;
- linear and branching topology: insufficient evidence.

The hypothesis is neither strengthened nor rejected by live evidence. It is
narrowed to a precise test with corrected input/output object identities.

## Historical recommended next target (superseded)

Run one Nickel-selected CK preview with the three breakpoints and capture raw
source, temporary input, selector, and returned output. Use that run first to
reconcile the `TESLevItem` child layout and form identity fields/helpers. This
is the shortest route to deciding whether the root lies structurally outside
the randomized portion before adding a branching-family case.

The current next question instead begins at `FUN_1415DCFB0` and traces its enclosing planet-generation loop for atmospheric pre-population of the shared resource container.
