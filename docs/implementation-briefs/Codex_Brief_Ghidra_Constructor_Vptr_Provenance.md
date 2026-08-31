# Codex Brief — Constructor-to-vptr Provenance for Virtual Call Resolution

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

The current neighbourhood exporter has now been live-tested with virtual-call analysis enabled against:

```text
FUN_1431bc320
0x1431BC320
CreationKit.exe
```

The analysis successfully detected the important indirect call and classified its shape as vtable-based.

The relevant result was:

```text
callSiteAddress: 1431BC350
status: unresolved-unknown-vtable
kind: vtable
vtableByteOffset: 80
vtableSlotIndex: 10
```

The evidence recorded was:

```text
Decompiler high p-code represents the call target as a LOAD at fixed offset 0x50.
```

The failure reason was:

```text
No unique vtable could be tied to the receiver from direct program data.
```

So the remaining problem is now very specific:

> The analyzer recognizes the virtual call and fixed slot, but cannot yet establish which vtable belongs to the receiver object.

The surrounding decompilation strongly suggests the receiver is initialized immediately beforehand by:

```c
thunk_FUN_140d7ce60(local_a8);
```

Earlier analysis of that constructor path indicated that it sets the receiver's vptr to:

```text
TESContainer::vftable
```

The purpose of this iteration is to teach the analyzer to recover that relationship from Ghidra's program/decompiler data.

---

# Goal

Enhance the existing virtual-call resolver so that it can trace a receiver backward through a simple constructor call and recover the vtable written by that constructor.

The immediate target is:

```text
FUN_1431bc320
```

and specifically this conceptual sequence:

```text
local_a8
    ↓ passed as first argument
FUN_140d7ce60
    ↓ constructor writes
TESContainer::vftable
    ↓ later receiver used in CALLIND
vtable + 0x50
    ↓
resolve slot 10
```

The intended outcome is to resolve the previously unresolved call at:

```text
0x1431BC350
```

to a concrete target function.

Do not expand scope beyond this simple constructor-vptr provenance case unless required to make the target work.

---

# Current Known Behaviour to Preserve

`ExportFunctionNeighbourhood.java` currently:

- exports the selected root;
- exports resolved direct internal callees;
- resolves thunk chains;
- detects `CALLIND`;
- recognizes a fixed-offset vtable-style load;
- calculates the vtable slot using program pointer size;
- reads candidate function pointers;
- maps pointers to Ghidra functions;
- writes `indirect-calls.json`;
- writes `indirectEdges` into `graph.json`;
- exports resolved virtual targets using the standard seven-file bundle;
- records unresolved calls without guessing;
- remains non-destructive.

Preserve these behaviours.

---

# Required Enhancement

Add focused backward provenance for the receiver of a vtable-style indirect call.

For a supported call such as:

```text
CALLIND [ [receiver] + constantOffset ]
```

the analyzer should attempt to determine whether the receiver was initialized by an earlier constructor-like call.

The supported pattern for this iteration is:

1. same high-level receiver varnode/object appears in the indirect call;
2. an earlier call in the same function receives that receiver as argument 0 / `this`;
3. that callee, after thunk resolution, contains a store equivalent to:

```text
receiver[0] = known_vtable_address
```

or the p-code equivalent;
4. the stored address resolves to a uniquely named vtable/vftable symbol;
5. that vtable can then be used to resolve the indirect slot.

Do not require semantic knowledge that the callee is "a constructor".

Infer the relationship from actual dataflow and the vptr store.

---

# Immediate Acceptance Target

The first live test remains:

```text
FUN_1431bc320
0x1431BC320
```

The analyzer should connect:

```text
receiver used at CALLIND 0x1431BC350
```

to the earlier initialization call corresponding to:

```text
FUN_140d7ce60
```

or its thunk.

It should then inspect the resolved implementation and recover:

```text
TESContainer::vftable
```

if that is what the current Ghidra analysis actually exposes.

Do not hard-code:

- `FUN_140d7ce60`;
- `TESContainer::vftable`;
- the vtable address;
- the resolved slot target.

The implementation should discover them from the analysed program.

---

# Receiver Identity / Provenance

This is the main challenge.

Prefer Ghidra high p-code / varnode identity over parsing decompiled C variable names.

Potential strategies may include:

- tracing the varnode used as the receiver input to the indirect call;
- walking defining p-code operations backward;
- accounting for `COPY`, `CAST`, `PTRSUB`, `PTRADD`, and similar simple wrappers;
- matching that normalized receiver against inputs to earlier `CALL` operations;
- determining which call argument corresponds to the receiver/`this`.

Keep normalization conservative.

Do not merge unrelated varnodes merely because they occupy the same stack location unless the evidence supports equivalence.

If identity cannot be established confidently, preserve the unresolved status.

---

# Constructor / Initializer Inspection

Once a candidate earlier call is found:

1. resolve any thunk chain;
2. decompile or inspect the implementation;
3. identify stores through its first argument / `this`;
4. look specifically for a store to offset zero of the receiver;
5. determine whether the stored value is a constant/program address;
6. resolve that address to a symbol/data location;
7. accept it as a vtable candidate only if the symbol naming/data evidence is sufficiently strong.

Preferred symbol-name evidence includes names containing:

```text
vftable
vtable
```

case-insensitively.

If multiple distinct vtable candidates are written, do not guess.

Record ambiguity.

---

# Important Inheritance Caveat

C++ constructors may write more than one vtable during base/derived construction.

Therefore:

- do not automatically use the first vtable store found;
- record all candidate vptr stores in execution/order context where practical;
- if exactly one relevant final/unique vtable can be established, use it;
- if multiple candidates remain ambiguous, leave the indirect call unresolved.

For the immediate target, the existing evidence suggests a simple enough case, but the implementation should not assume all constructors have one vtable write.

---

# Suggested Resolution Evidence

For a successful case, `indirect-calls.json` should record evidence conceptually like:

```json
{
  "status": "resolved-static-vtable",
  "kind": "vtable",
  "callSiteAddress": "1431BC350",
  "vtableByteOffset": 80,
  "vtableSlotIndex": 10,
  "vtableName": "TESContainer::vftable",
  "vtableAddress": "...",
  "provenance": {
    "method": "constructor-vptr-store",
    "initializerCallSite": "...",
    "initializerFunctionName": "FUN_140d7ce60",
    "initializerFunctionAddress": "140D7CE60",
    "receiverArgumentIndex": 0,
    "vptrStoreOffset": 0
  },
  "resolvedFunctionName": "FUN_...",
  "resolvedFunctionAddress": "..."
}
```

The exact schema may differ if a cleaner design fits the current implementation.

The important new information is:

- how the vtable was discovered;
- which earlier call established it;
- where the constructor/initializer implementation is;
- which vptr store was used.

---

# Failure Statuses

Add or retain clear statuses/reasons for cases such as:

```text
unresolved-no-initializer-call
unresolved-receiver-provenance
unresolved-no-vptr-store
unresolved-ambiguous-vptr-stores
unresolved-vtable-symbol
unresolved-no-function-at-slot
unsupported-pattern
```

Do not collapse all failures into `unresolved-unknown-vtable` if a more precise reason is available.

Precise failure output will help design the next iteration if needed.

---

# Vtable Slot Resolution

Once the vtable is recovered, preserve the current slot-resolution logic:

1. use `Program.getDefaultPointerSize()`;
2. calculate slot index from byte offset;
3. calculate the vtable entry address;
4. read the pointer using the program's endianness;
5. map it with `FunctionManager.getFunctionAt()`;
6. resolve any target thunk;
7. export the resulting internal function bundle;
8. deduplicate by resolved function entry address.

Do not change this logic unless live-test evidence shows a bug.

---

# Output

Continue using the current neighbourhood structure:

```text
exports/
└─ neighbourhoods/
   └─ FUN_1431bc320__1431BC320/
      ├─ graph.json
      ├─ manifest.json
      ├─ indirect-calls.json
      └─ functions/
```

If the target resolves, its full seven-file bundle should appear under `functions/`.

Do not create a separate export tree unless necessary.

---

# Diagnostic Output

Because this iteration depends heavily on Ghidra high-p-code shape, add enough diagnostic information to make a failed live test actionable.

For the relevant indirect call, record where practical:

- normalized receiver varnode identity;
- candidate earlier calls using that receiver;
- resolved initializer target;
- vptr store candidates found;
- stored address;
- symbol names associated with those addresses;
- reason each candidate was accepted/rejected.

This can be stored in structured JSON rather than console spam.

Do not dump enormous raw p-code unnecessarily.

The goal is useful diagnostics, not exhaustive IR export.

---

# Safety Requirements

The script must remain read-only with respect to the Ghidra program.

Do not:

- start transactions;
- rename symbols/functions;
- create labels;
- add comments;
- change signatures;
- apply types;
- alter memory;
- intentionally modify analysis state.

Writing export files is expected.

---

# Documentation

Update:

```text
ghidra/README.md
```

to explain:

- that the virtual resolver can now attempt constructor-to-vptr provenance;
- what limited pattern is supported;
- how ambiguous/multiple vtable stores are handled;
- how to interpret new failure statuses;
- the first live-test procedure.

Do not claim general C++ constructor recovery.

---

# Research Documentation

Do not add a semantic claim to `known-facts.md` merely because a vtable target resolves.

If the script successfully identifies a new concrete function behind the `0x50` virtual call, it is reasonable to update:

```text
docs/function-register.md
```

with only the directly supported relationship, for example:

```text
FUN_1431bc320
    ↓ virtual call through TESContainer::vftable + 0x50
FUN_xxxxxxxxx
```

Use cautious language for the function's interpretation.

Do not rename it in Ghidra.

---

# Explicit Non-Goals

Do not implement yet:

- full interprocedural SSA analysis;
- arbitrary alias analysis;
- full C++ constructor/destructor identification;
- class hierarchy reconstruction;
- multiple-inheritance vtable recovery;
- whole-program vtable enumeration;
- deep recursive neighbourhood export;
- automated semantic naming;
- runtime instrumentation;
- headless Ghidra;
- symbolic execution;
- resource-algorithm reconstruction itself.

This iteration is only about recovering the vtable from a simple earlier initializer/constructor call.

---

# Acceptance Criteria

A successful live test against:

```text
FUN_1431bc320
0x1431BC320
```

should ideally change the relevant indirect-call result from:

```text
status: unresolved-unknown-vtable
```

to something equivalent to:

```text
status: resolved-static-vtable
vtableName: TESContainer::vftable
vtableByteOffset: 80
vtableSlotIndex: 10
resolvedFunctionName: FUN_...
resolvedFunctionAddress: ...
```

The output should also identify the earlier initializer call and the vptr store used as evidence.

If resolution still fails, the enhanced diagnostics must make the next obstacle clear.

---

# Deliverables

When finished, report:

1. files modified;
2. whether any files were added;
3. how receiver identity is normalized/traced;
4. how earlier candidate initializer calls are found;
5. how initializer thunks are resolved;
6. how vptr stores are detected;
7. how multiple vtable stores are handled;
8. how vtable symbol confidence is determined;
9. any new failure statuses;
10. any changes to `indirect-calls.json` schema;
11. exact live-test instructions;
12. Ghidra API/high-p-code assumptions that still require live validation;
13. known limitations.

Do not proceed to broader provenance or deeper recursion until this case has been live-tested.
