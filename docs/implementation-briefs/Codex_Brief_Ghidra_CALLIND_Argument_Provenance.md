# Codex Brief — CALLIND Argument Provenance and Stack-Object Correlation

## Context

This repository supports reverse engineering of Starfield's runtime inorganic resource-generation system.

Before making changes, read:

- `AGENTS.md`
- `README.md`
- `docs/known-facts.md`
- `docs/hypotheses.md`
- `docs/function-register.md`
- `ghidra/README.md`
- `ghidra/scripts/ExportSelectedFunctionContext.java`
- `ghidra/scripts/ExportFunctionNeighbourhood.java`

The current neighbourhood exporter has been live-tested against:

```text
FUN_1431bc320
0x1431BC320
CreationKit.exe
```

The relevant indirect call is:

```text
CALLIND at 0x1431BC350
```

The latest high-p-code diagnostics successfully exposed the target-expression shape.

The decompiler renders the call approximately as:

```c
(**(code **)(local_a8[0] + 0x50))
    (local_a8,
     *(undefined8 *)(param_1 + 0x30),
     *(longlong *)(param_1 + 0xa0) + 0x20);
```

The p-code diagnostics show that the virtual-call target is built from something equivalent to:

```text
LOAD
  ↓
CAST
  ↓
INT_ADD
   ├─ stack[-0xA8]
   └─ constant 0x50
```

The `stack[-0xA8]` value is believed to correspond to:

```text
local_a8[0]
```

that is, the vptr stored at the beginning of the local object.

The first actual call argument (`this`) is represented separately as:

```text
unique:0x9D00
```

The current diagnostics only record metadata for that argument, not its full defining-expression tree.

All existing comparisons between the first argument and nodes in the call-target tree were false:

```text
sameVarnode: false
sameHighVariable: false
sameStorage: false
sameDefiningOp: false
```

This is now expected, because the two values are semantically different:

```text
local_a8      = address of object
local_a8[0]   = contents of object's first field / vptr
```

The next task is to determine whether Ghidra's p-code can prove that the first argument is the address of the same stack object whose first slot supplies the vptr.

---

# Goal

Extend the existing targeted p-code diagnostics so that each `CALLIND` argument also includes a bounded recursive definition tree.

Then add a focused comparison that attempts to correlate:

```text
CALLIND first argument
```

with:

```text
stack storage used as the base/vptr source inside the call-target expression
```

The immediate research question is:

> Does the first call argument ultimately resolve to the address of stack object `stack[-0xA8]`, while the virtual target expression reads the contents of that same stack object?

This task is diagnostic.

Do not yet change the receiver-resolution behavior or constructor-provenance logic.

---

# Required Change 1 — Argument Definition Trees

For each `CALLIND` argument, especially argument 0 (`pcodeInputIndex: 1`), export:

- varnode metadata;
- defining p-code operation;
- recursively defined inputs;
- constants;
- address-space information;
- sequence/instruction addresses;
- high-variable information where available.

Reuse the existing bounded p-code tree walker if practical.

Use the same conservative depth limit:

```text
8
```

and the same cycle/visited protections.

Suggested output:

```json
{
  "arguments": [
    {
      "index": 0,
      "pcodeInputIndex": 1,
      "varnode": { "...": "..." },
      "definitionTree": {
        "...": "..."
      }
    }
  ]
}
```

Do not emit only metadata for arguments anymore.

---

# Required Change 2 — Stack-Object Address Provenance

Add a focused diagnostic that tries to identify whether an argument definition represents the address of a stack location.

Supported simple patterns may include:

```text
stack pointer + constant offset
```

or equivalent forms involving simple wrappers such as:

- `COPY`
- `CAST`
- `PTRSUB`
- `PTRADD`
- `INT_ADD`
- constant offset arithmetic

Do not implement full alias analysis.

The desired diagnostic output should identify something like:

```text
argument 0
  -> address of stack[-0xA8]
```

if the p-code supports that conclusion.

Record:

- base address space;
- stack offset;
- derivation chain;
- confidence/resolution basis.

Suggested status values:

```text
resolved-stack-address
unresolved-stack-address
unsupported-stack-address-pattern
```

---

# Required Change 3 — Correlate Argument Address with Target Storage

The call-target diagnostics already expose a stack-backed value used in the target-expression tree.

Add a comparison between:

```text
argument 0 stack-address provenance
```

and:

```text
stack storage used by the target expression
```

The key comparison is whether both refer to the same stack offset.

Conceptually:

```text
argument 0
    = &stack[-0xA8]

target base/vptr source
    = stack[-0xA8]
```

If so, record a relationship such as:

```json
{
  "receiverStorageCorrelation": {
    "status": "matched-stack-object",
    "argumentIndex": 0,
    "argumentStackOffset": -168,
    "targetStorageStackOffset": -168,
    "sameStackObject": true,
    "evidence": [
      "argument resolves to address of stack[-0xA8]",
      "call target reads value stored at stack[-0xA8]"
    ]
  }
}
```

Use whatever schema fits cleanly.

Do not yet feed this result into the actual receiver resolver.

This iteration should prove the relationship first.

---

# Important Distinction

Do not compare:

```text
argument value == vptr value
```

They are not expected to be equal.

The intended relationship is:

```text
argument value == address of object
target base == contents stored at object address
```

That distinction is the whole purpose of this diagnostic step.

---

# Target-Expression Storage Extraction

If not already exposed clearly, add a small diagnostic helper that identifies stack-backed storage nodes inside the call-target definition tree.

For each relevant stack-backed node, record:

- address space;
- stack offset;
- size;
- defining op;
- whether it appears before the constant vtable offset addition;
- path within the definition tree.

The immediate expected storage is:

```text
stack[-0xA8]
```

Do not hard-code that offset.

Discover it from p-code.

---

# INDIRECT / Call-Side-Effect Clue

The latest diagnostics also showed that the stack-backed vptr value is defined by an `INDIRECT` p-code op associated with the earlier call area near:

```text
0x1431BC331
```

Preserve this information.

If practical, record:

- `INDIRECT` op sequence address;
- source/input varnodes;
- associated instruction/call site;
- whether it refers to the same stack storage.

Do not attempt to infer constructor semantics from `INDIRECT` yet.

This is useful evidence for the later provenance step.

---

# Output

Continue using:

```text
pcode-diagnostics.json
```

inside:

```text
exports/
└─ neighbourhoods/
   └─ FUN_1431bc320__1431BC320/
```

Do not create another large diagnostic file unless necessary.

Increment the diagnostic schema version if the current file uses one.

---

# Existing Behaviour to Preserve

Do not regress:

- direct-call export;
- thunk resolution;
- depth-1 neighbourhood export;
- virtual-call detection;
- fixed-offset vtable recognition;
- vtable slot calculation;
- constructor-vptr provenance logic;
- `indirect-calls.json`;
- `graph.json`;
- existing p-code diagnostics;
- non-destructive behavior.

Do not change the current receiver-resolution outcome yet.

It is acceptable and expected for:

```text
0x1431BC350
```

to remain:

```text
unresolved-receiver-provenance
```

after this task.

---

# Safety Requirements

The script must remain read-only.

Do not:

- begin transactions;
- rename symbols/functions;
- create labels;
- add comments;
- apply types;
- change signatures;
- modify memory;
- intentionally alter analysis state.

Only write export files.

---

# Documentation

Update:

```text
ghidra/README.md
```

to explain:

- CALLIND arguments now include definition trees;
- stack-address provenance diagnostics;
- receiver-storage correlation;
- that this remains diagnostic and does not yet alter resolution behavior;
- the live-test target at `0x1431BC350`.

---

# Live Acceptance Test

Run the exporter with the cursor inside:

```text
FUN_1431bc320
0x1431BC320
```

Inspect the diagnostic entry for:

```text
CALLIND @ 0x1431BC350
```

A highly useful successful result would show:

```text
argument 0
  -> address of stack[-0xA8]
```

and:

```text
target expression
  -> reads stack[-0xA8]
```

with:

```text
sameStackObject: true
```

or equivalent evidence.

Success does not require the virtual call to resolve.

Success means:

> The diagnostics mechanically establish whether the first call argument is the address of the same stack object whose first field supplies the vptr.

---

# Explicit Non-Goals

Do not implement yet:

- new receiver-normalization rules;
- automatic receiver/vptr correlation in the resolver;
- full alias analysis;
- `MULTIEQUAL` tracing;
- symbolic execution;
- class hierarchy reconstruction;
- multiple inheritance handling;
- deeper call-tree recursion;
- broader indirect-call analysis.

This iteration only gathers the missing argument-provenance evidence.

---

# Deliverables

When finished, report:

1. files modified;
2. whether files were added;
3. how argument definition trees are represented;
4. how stack-address provenance is detected;
5. how stack offsets are represented;
6. how target-expression stack storage is identified;
7. how receiver-storage correlation is represented;
8. whether `INDIRECT` metadata was expanded;
9. diagnostic schema changes;
10. exact live-test instructions;
11. expected success indicators;
12. remaining limitations.

Do not implement receiver-resolution changes until this diagnostic output has been live-tested and reviewed.
