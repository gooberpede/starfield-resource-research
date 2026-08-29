# Ghidra Call-Signature Reconciliation: `FUN_1431bc320` → `FUN_140e0aab0`

## Scope and execution

Target:

```text
caller:    FUN_1431bc320 @ 0x1431BC320
call site: 0x1431BC350
callee:    FUN_140e0aab0 @ 0x140E0AAB0
```

Evidence was exported from the existing analyzed `CreationKit.exe` Ghidra
project with `ExportCallSignatureEvidence.java`. The live GUI project was
locked, so a scratch copy was made under the ignored `scratch/` directory and
opened headless with `-readOnly -noanalysis`. The original project was not
modified. The exporter starts no transaction and performs no program writes.

Generated evidence is under:

```text
exports/call-signatures/FUN_1431bc320__1431BC320__call_1431BC350/
```

## Call-site disassembly

The decisive machine instructions are:

```asm
1431BC329  MOV  RBX,RCX
1431BC32C  LEA  RCX,[RSP+0x20]
1431BC331  CALL  0x1400ED0F9             ; TESContainer initializer thunk
1431BC337  MOV  R8,qword ptr [RBX+0xA0]
1431BC33E  MOV  RAX,qword ptr [RSP+0x20] ; temporary vptr
1431BC343  ADD  R8,0x20
1431BC347  MOV  RDX,qword ptr [RBX+0x30]
1431BC34B  LEA  RCX,[RSP+0x20]
1431BC350  CALL qword ptr [RAX+0x50]
```

The temporary begins at call-site `RSP+0x20`, which Ghidra normalizes to
caller stack offset `-0xA8`. The first 0x20 bytes at the call-site stack
pointer are Windows x64 shadow space, not additional arguments.

## Exact ABI mapping

| Callee parameter | Call-site storage | Exact value | Defining instructions |
|---|---|---|---|
| parameter 0 | RCX | address of temporary TESContainer at `RSP+0x20` | `LEA RCX,[RSP+0x20]` |
| parameter 1 | RDX | `*(ResourceViewWidget+0x30)` | `MOV RDX,[RBX+0x30]`, with `RBX` saved from incoming `RCX` |
| parameter 2 | R8 | `*(ResourceViewWidget+0xA0)+0x20` | `MOV R8,[RBX+0xA0]`; `ADD R8,0x20` |
| no parameter | R9 | indeterminate caller-saved residue | no defining write after the initializer call |
| stack arguments | — | none | high p-code has three actual arguments; machine code makes no stack-argument stores |

At the machine level R9 necessarily contains some bit pattern, but it is not an
argument to this call and cannot be reconstructed statically after the
preceding call, which is permitted to clobber it.

## High-p-code mapping

The high-p-code operation at `0x1431BC350` is `CALLIND` with four inputs.
Under Ghidra's rule, input 0 is the target and inputs 1..3 are actual arguments:

```text
input 0 target:
  LOAD(CAST(INT_ADD(INDIRECT(stack[-0xA8]), 0x50)))

input 1 / argument 0 / RCX:
  PTRSUB(stack-pointer, -0xA8)

input 2 / argument 1 / RDX:
  LOAD(CAST(INT_ADD(param_1, 0x30)))

input 3 / argument 2 / R8:
  INT_ADD(LOAD(CAST(INT_ADD(param_1, 0xA0))), 0x20)
```

There is no hidden load between the `+0xA0` field load and the `+0x20`
adjustment.

## Callee signature and parameter storage

Ghidra's listing signature and decompiler high parameters agree:

```c
void FUN_140e0aab0(longlong param_1, longlong param_2, longlong *param_3)
```

Calling convention is `__fastcall`; custom storage is disabled; the analyzed
signature source is `ANALYSIS`.

| Parameter | Listing storage | High storage | Entry preservation |
|---|---|---|---|
| param_1 | `RCX:8` | `RCX:8` | `MOV RBP,RCX` |
| param_2 | `RDX:8` | `RDX:8` | `MOV R14,RDX` |
| param_3 | `R8:8` | `R8:8` | `MOV RDI,R8` |

## First-use dataflow

### Parameter 2 / R8 / adjusted source candidate

This parameter is used first and is not opaque:

```asm
140E0AAC6  MOV  RDI,R8
140E0AAD7  MOV  R9,[RDI]       ; load vptr from adjusted +0x20 address
140E0AADA  MOV  RCX,RDI
140E0AADD  CALL qword ptr [R9+0x30]
```

The returned value is compared against identity data obtained from
`thunk_FUN_140f0e590`. The adjusted pointer is retained only on equality;
otherwise the function returns without copying.

On a match, the callee reads:

```text
source + 0x40: count/capacity-like 32-bit field
source + 0x48: element-array pointer
element size:  0x18 bytes
```

It iterates those elements and supplies each to `thunk_FUN_140e03ee0`.

### Parameter 0 / RCX / destination

After the source type/identity gate succeeds, the first semantic use is:

```c
thunk_FUN_140e4bc10(param_1, param_2);
```

The function then treats `param_1+0x40` and `param_1+0x48` as the
destination array state, grows it if required, initializes new 0x18-byte
records, and appends/copies source records.

### Parameter 1 / RDX / context or owner

Its first semantic use is the second argument to
`thunk_FUN_140e4bc10(destination, param_2)`. It is later passed as the middle
argument to the per-element copy helper:

```c
thunk_FUN_140e03ee0(destination_element, param_2, source_element);
```

The exact semantic type of this value is not established; `context/owner` is
descriptive dataflow terminology only.

## TESContainer slot 10

Mechanically:

```text
TESContainer::vftable              0x1487399C8
slot 10 / byte offset +0x50        0x148739A18
raw entry                          thunk_FUN_140e0aab0 @ 0x1400904FD
resolved implementation           FUN_140e0aab0 @ 0x140E0AAB0
```

Representative slot-10 entries for `TESFullName`, `BGSPropertySheet`,
`TESModel`, `BGSPreviewTransform`, `BGSDestructibleObjectForm`,
`TESDescription`, `TESSpellList`, and `BGSSkinForm` mostly resolve to
three-parameter functions. This strongly supports a common component virtual
operation shape. It does not establish the engine's original method name.

Ghidra reports zero direct calling functions for `FUN_140e0aab0`, as expected
for dispatch through a vtable thunk. Ten bounded `+0x50` indirect-call
candidates were collected from functions that also call the TESContainer
initializer. Only the target call has independently proven receiver/vtable
provenance; the others are preserved as comparison leads and are not treated
as callers of this callee.

## Reconciliation of `QTreeWidget + 0x20`

The value is literally:

```text
load pointer from ResourceViewWidget + 0xA0
add 0x20 to that pointer
pass the adjusted address in R8
```

The callee immediately loads a vptr from the adjusted address, invokes virtual
slot `+0x30` on it, applies an identity gate, and then dereferences fields
`+0x40/+0x48`. Therefore it is not merely opaque context and it is not a
decompiler argument-order artifact.

Independent class-scoped evidence that the enclosing pointer is accepted by
`QTreeWidget::clear` establishes QTreeWidget compatibility, not that the
concrete object is exactly Qt's stock `QTreeWidget`. The best-supported model
is a concrete QTreeWidget-compatible CK UI class with a secondary or contained
component-compatible subobject at `+0x20`. Multiple inheritance and
containment remain unresolved alternatives. No evidence places a
`TESContainer` inside Qt's generic QTreeWidget class definition.

## Mechanically proven

- The call target is TESContainer vtable slot 10 via a thunk to
  `FUN_140e0aab0`.
- Exactly three actual arguments are present: RCX, RDX, and R8.
- R9 is not an argument and there are no stack arguments.
- R8 is exactly `*(ResourceViewWidget+0xA0)+0x20`.
- No hidden dereference occurs during that call-site adjustment.
- `FUN_140e0aab0` has three analyzed parameters stored in RCX/RDX/R8.
- The callee dereferences R8 as a vptr-bearing object and calls its slot
  `+0x30`.
- After an identity comparison, it reads source `+0x40/+0x48` and writes a
  destination array at corresponding destination offsets using 0x18-byte
  elements.

## Strong interpretation

`FUN_140e0aab0` implements a generic TESContainer component copy operation:
RCX is the destination TESContainer, RDX is copy context/owner state, and R8 is
a type-checked source component. The concrete QTreeWidget-compatible UI object
stored at `ResourceViewWidget+0xA0` exposes that source component at adjusted
address `+0x20`.

`CopyComponent` remains a proposed semantic alias, not a confirmed engine
symbol.

## Withdrawn / superseded interpretation

Withdraw:

> The value is just an opaque address into a plain QTreeWidget and therefore
> invalidates the TESContainer source-copy interpretation.

Also withdraw the overstrong inverse claim:

> Qt's stock QTreeWidget itself embeds a TESContainer at offset +0x20.

The earlier source-component interpretation survives, but only when stated as
an adjusted component-compatible subobject of the concrete QTreeWidget-compatible
object.

## Remaining uncertainty

The only uncertainty affecting the next step is the concrete identity and C++
layout of the object stored at `ResourceViewWidget+0xA0`: specifically whether
its `+0x20` component arises through secondary inheritance or containment.

## Branch B — Earlier interpretation substantially right

The corrected model is:

```text
ResourceViewWidget + 0xA0
    -> concrete QTreeWidget-compatible CK object
    -> adjusted +0x20 component-compatible source
    -> type/identity gate in FUN_140e0aab0
    -> copy source +0x40/+0x48 records
       into temporary TESContainer destination +0x40/+0x48
```

One next target: identify the constructor/RTTI of the concrete object assigned
to `ResourceViewWidget+0xA0` and recover only its primary vptr and `+0x20`
subobject vptr/layout.

