# Codex Brief — Forensic Call-Signature Reconciliation for `FUN_1431bc320` → `FUN_140e0aab0`

## Context

Before changing anything, read the repo guidance and current research/tooling docs, especially:

- `AGENTS.md`
- `README.md`
- `docs/known-facts.md`
- `docs/hypotheses.md`
- `docs/function-register.md`
- `ghidra/README.md`
- `ghidra/scripts/ExportFunctionNeighbourhood.java`
- `ghidra/scripts/AnalyzeClassFieldProvenance.java`

We need to close one specific contradiction before proceeding.

Mechanically established:

```text
FUN_1431bc320
CALLIND @ 0x1431BC350
    ↓
TESContainer::vftable + 0x50
slot 10
    ↓
FUN_140e0aab0
```

Also strongly established from live class-scoped evidence:

```text
*(ResourceViewWidget + 0xA0)
```

is a `QTreeWidget *` or compatible object. `FUN_1431ef760` calls `QTreeWidget::clear` on the members at `+0x88`, `+0xA0`, and `+0xB8`.

Yet `FUN_1431bc320` decompiles approximately as:

```c
(**(code **)(local_a8[0] + 0x50))(
    local_a8,
    *(undefined8 *)(param_1 + 0x30),
    *(longlong *)(param_1 + 0xA0) + 0x20
);
```

Earlier we interpreted `FUN_140e0aab0` as TESContainer copy/component machinery and the third apparent argument as a source component. That interpretation is now suspect because `*(param_1 + 0xA0)` is a QTreeWidget pointer.

## Objective

Produce a forensic reconciliation of this call.

Answer:

1. What exact machine-level values are passed in RCX, RDX, R8, R9, and any stack arguments at `0x1431BC350`?
2. How do those values map to `FUN_140e0aab0`'s incoming parameters under the Windows x64 ABI?
3. How does `FUN_140e0aab0` first use each incoming argument?
4. What exactly happens to the value `QTreeWidget + 0x20`?
5. Which parts of the earlier “TESContainer copy/source component” interpretation survive?
6. Which parts must be withdrawn?

This is a high-yield forensic task, not another general analyzer-extension task.

## Required evidence

### A. Call-site machine code

Export/disassemble a tight window around:

```text
0x1431BC350
```

Suggested range:

```text
0x1431BC320..0x1431BC370
```

Capture enough instructions to show temporary-object setup, argument setup, target-vtable load, indirect call, and immediate post-call handling.

Record instruction addresses, mnemonics, operands, register writes, and stack reads/writes.

### B. Windows x64 ABI mapping

At the exact call site, reconstruct:

```text
RCX
RDX
R8
R9
```

plus any stack arguments.

For each, record:

- defining instruction(s)
- high-p-code varnode if available
- source expression
- Ghidra datatype
- confidence

Do not trust decompiled C parameter order until it matches machine code.

### C. High p-code for CALLIND

Export the full high-p-code representation of the call:

- target varnode
- all inputs
- input indices
- storage
- high variables
- datatypes
- bounded definition trees

Preserve the rule:

```text
CALLIND input 0 = target
inputs 1..N = actual arguments
```

### D. Low p-code if useful

Export low p-code for the immediate call-site range if it helps reconcile machine registers with high-p-code/decompiler output.

### E. `FUN_140e0aab0` entry signature

For `FUN_140e0aab0` export:

- entry disassembly
- high p-code
- decompiled C
- calling convention
- parameter count
- parameter storage
- datatypes
- first use of every incoming argument

Map each callee parameter explicitly back to:

```text
RCX / RDX / R8 / R9 / stack
```

### F. First-use dataflow

For every incoming argument, trace bounded first-use behavior:

- dereference offsets
- comparisons
- calls
- RTTI casts
- loop use
- writes
- destination/source behavior

Do not infer semantic type from decompiler parameter names alone.

### G. Re-check TESContainer slot 10 semantics

Re-examine:

```text
TESContainer::vftable + 0x50
slot 10
```

Determine separately:

```text
mechanically proven
strong interpretation
speculative
```

Do not automatically call it `CopyComponent`.

Useful evidence may include:

- other callers of `FUN_140e0aab0`
- other virtual calls through the same slot
- a small comparison with the equivalent slot of other `BaseFormComponent`-derived classes

Do not expand into general class reconstruction.

### H. Reconcile `QTreeWidget + 0x20`

Determine whether:

```text
*(param_1 + 0xA0) + 0x20
```

is literally an interior pointer into the QTreeWidget object.

Check:

1. Is there a hidden dereference that the decompiler simplified away?
2. Is it used only as an opaque address?
3. Does `FUN_140e0aab0` dereference it?
4. At what offsets?
5. Could it be an adjusted `this` pointer to a Qt base/subobject?
6. Is there vptr/RTTI/base-layout evidence at that offset?

Do not assume `+0x20` is an embedded TESContainer.

### I. Compare other callers

Inspect up to 10 representative internal callers of `FUN_140e0aab0`.

For each, record argument shapes and especially the argument corresponding to the `QTreeWidget +0x20` value in our target call.

Question:

> Does that argument consistently behave like a BaseFormComponent pointer, adjusted subobject pointer, opaque context, or something else?

This comparison may be decisive.

## Focused exporter

If current exports are insufficient, add ONE small raw-evidence script, preferably:

```text
ExportCallSignatureEvidence.java
```

Suggested outputs:

```text
callsite-disassembly.txt
callsite-high-pcode.json
callsite-low-pcode.json
abi-arguments.json
callee-entry-disassembly.txt
callee-parameters.json
callee-first-use.json
other-callers.json
slot-comparison.json
reconciliation.md
manifest.json
```

Keep it evidence-oriented. Do not build another broad semantic framework.

## Execution strategy

If practical, run this via Ghidra headless against the existing analysed project.

However:

- do not let headless setup consume the task;
- do not restructure the repo;
- one manual GUI run is acceptable if needed.

The research answer is the priority.

## Required conclusion format

After gathering evidence, report:

### Mechanically proven

Concrete ABI/p-code facts only.

### Strong interpretation

Best-supported semantic model.

### Withdrawn / superseded interpretation

Explicitly identify any earlier interpretation that should no longer be used, especially:

```text
"QTreeWidget + 0x20 is a TESContainer source component"
```

if unsupported.

### Remaining uncertainty

Only unresolved points that affect the next research step.

## Decision

End with exactly one of:

### Branch A — Earlier interpretation substantially wrong
Give the corrected call/dataflow model and one next target.

### Branch B — Earlier interpretation substantially right
Explain exactly how `QTreeWidget + 0x20` is valid and one next target.

### Branch C — Still insufficient
Specify exactly one further experiment needed.

Do not recommend another broad analyzer.

## Documentation

After live evidence:

- update `docs/function-register.md` with directly supported call/signature facts;
- update `docs/hypotheses.md` if an earlier interpretation is disproven or superseded;
- do not promote speculative semantics into `docs/known-facts.md`.

Do not rename Ghidra symbols.

## Safety

All Ghidra work remains read-only.

Do not:

- start transactions
- rename symbols/functions
- add labels/comments
- change signatures/types
- modify memory
- intentionally alter analysis state

Only export files.

## Explicit non-goals

Do not spend this task on:

- more `ResourceViewWidget +0xA0` scanning
- callback extraction
- deeper class reconstruction
- Qt meta-object reconstruction
- general alias analysis
- full headless automation architecture
- resource-algorithm reconstruction itself

The task is only:

```text
CALLIND 0x1431BC350
    ↓
exact ABI / p-code mapping
    ↓
FUN_140e0aab0 parameter usage
    ↓
reconcile QTreeWidget +0x20
    ↓
close this branch
```

## Acceptance target

Primary target:

```text
caller: FUN_1431bc320
call site: 0x1431BC350
callee: FUN_140e0aab0
```

Minimum success:

1. exact RCX/RDX/R8/R9 mapping;
2. exact callee parameter/storage mapping;
3. explicit account of the `QTreeWidget +0x20` value;
4. explicit status of the old CopyComponent/source-component interpretation.

Best case:

> A fully reconciled call signature and corrected semantic model that closes the `ResourceViewWidget +0xA0` branch and gives one clear next reverse-engineering target.

## Deliverables

Report:

1. files modified
2. files added
3. whether a focused exporter was added
4. whether headless execution was attempted/succeeded
5. call-site disassembly findings
6. RCX/RDX/R8/R9 mapping
7. high-p-code mapping
8. callee parameter/storage mapping
9. first-use behavior for every argument
10. other-caller comparison
11. slot-10 comparison if performed
12. exact status/meaning of `QTreeWidget +0x20`
13. mechanically proven facts
14. withdrawn/superseded interpretation
15. corrected call/dataflow model
16. one recommended next research target
