# Codex Brief — Ghidra Virtual/Indirect Call Resolution

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

The current depth-1 neighbourhood exporter has been live-tested successfully in Ghidra against:

```text
FUN_1431bc320
0x1431BC320
CreationKit.exe
```

It exported the root function and its resolvable direct internal callees.

That run revealed an important blind spot: a potentially significant indirect virtual call is present in the decompilation but absent from the call graph because Ghidra does not represent it as a direct callee.

The relevant pattern is approximately:

```c
thunk_FUN_140d7ce60(local_a8);

(**(code **)(local_a8[0] + 0x50))
    (local_a8,
     *(undefined8 *)(param_1 + 0x30),
     *(longlong *)(param_1 + 0xa0) + 0x20);
```

The constructor path for `local_a8` appears to establish:

```text
local_a8 -> TESContainer
TESContainer constructor -> TESContainer::vftable
```

The indirect call then dispatches through:

```text
TESContainer::vftable + 0x50
```

This call occurs before the later generic leveled-list processing path and is therefore a high-priority target for reverse engineering.

---

# Goal

Add a focused Ghidra analysis capability that can identify and export simple vtable-based indirect calls where the target can be resolved statically from known program data.

The immediate research target is:

```text
FUN_1431bc320
```

and specifically the indirect call through:

```text
TESContainer::vftable + 0x50
```

The intended outcome is to answer:

> Which concrete function occupies the vtable slot used by this call, and what is its analysis context?

Do not attempt to implement a general-purpose C++ devirtualizer.

This iteration should solve the simple, statically recoverable case first.

---

# Preferred Implementation Direction

Extend the existing tooling with a new script or focused helper capability.

A suitable script name would be:

```text
AnalyzeVirtualCalls.java
```

or:

```text
ExportResolvedIndirectCalls.java
```

Alternatively, if there is a clean way to extend `ExportFunctionNeighbourhood.java` without making it difficult to understand or test, that is acceptable.

Prefer small, inspectable code over architectural complexity.

---

# Required Behaviour

For the function containing the current cursor:

1. identify call instructions and/or decompiler call sites that are not already represented as normal direct callees;
2. identify simple vtable-dispatch patterns where:
   - the receiver object has a statically identifiable vtable;
   - the call target is loaded from a fixed vtable offset;
3. resolve the target function from the vtable slot where possible;
4. record the evidence used to resolve it;
5. export the resolved target's normal function-context bundle;
6. preserve unresolved indirect calls rather than silently dropping them.

The first acceptance target is the call in `FUN_1431bc320` using vtable offset `0x50`.

---

# Scope: What Counts as a Supported Case

This iteration only needs to support straightforward cases such as:

```text
known object/vtable
    +
constant vtable offset
    =
concrete function pointer
```

Examples of acceptable evidence include:

- constructor sets the object vptr to a known vtable symbol;
- Ghidra already identifies the vtable as `TESContainer::vftable`;
- the decompiler uses a fixed offset such as `+ 0x50`;
- the vtable entry at that offset points to a defined internal function.

Do not attempt to solve cases that require:

- whole-program points-to analysis;
- dynamic class hierarchy reconstruction;
- speculative type inference across complex control flow;
- symbolic execution;
- runtime instrumentation;
- speculative resolution of function pointers with multiple possible targets.

Unsupported cases should be recorded clearly as unresolved.

---

# Immediate Target

The first target is:

```text
FUN_1431bc320
0x1431BC320
```

The analysis should attempt to resolve the indirect call conceptually represented as:

```c
(**(code **)(local_a8[0] + 0x50))(...)
```

The expected class/vtable context is believed to involve:

```text
TESContainer::vftable
```

Do not hard-code the resolved target address or function name.

It is acceptable to use the known vtable symbol as evidence if Ghidra already exposes it.

The script must discover the actual function pointer stored at the relevant vtable slot from the analysed program.

---

# Vtable Slot Interpretation

On x64, function pointers are normally 8 bytes.

Therefore a byte offset of:

```text
0x50
```

corresponds conceptually to slot index:

```text
0x50 / 8 = 10
```

Record both when practical:

```text
vtableByteOffset: 0x50
vtableSlotIndex: 10
```

Do not assume every future platform or structure uses this layout without checking the current program's pointer size.

Prefer calculating the slot index using the program pointer size.

---

# Required Output

Add machine-readable output for indirect/virtual call analysis.

Suggested structure within the existing neighbourhood export:

```text
exports/
└─ neighbourhoods/
   └─ FUN_1431bc320__1431BC320/
      ├─ graph.json
      ├─ manifest.json
      ├─ indirect-calls.json
      └─ functions/
         ├─ FUN_1431bc320__1431BC320/
         ├─ <resolved-direct-callee>__<address>/
         └─ <resolved-virtual-target>__<address>/
```

If a separate script/output directory is cleaner, that is acceptable, but document it clearly.

---

# indirect-calls.json

Create a machine-readable file describing every relevant indirect call discovered in the selected root function.

A possible schema:

```json
{
  "rootFunction": {
    "name": "FUN_1431bc320",
    "address": "1431BC320"
  },
  "indirectCalls": [
    {
      "callSiteAddress": "1431BC...",
      "status": "resolved",
      "kind": "vtable",
      "receiverExpression": "local_a8",
      "vtableName": "TESContainer::vftable",
      "vtableAddress": "...",
      "vtableByteOffset": 80,
      "vtableSlotIndex": 10,
      "targetPointerAddress": "...",
      "resolvedFunctionName": "FUN_...",
      "resolvedFunctionAddress": "...",
      "evidence": [
        "receiver constructed by function ...",
        "constructor sets vptr to TESContainer::vftable",
        "call dereferences vtable at fixed offset 0x50"
      ]
    }
  ]
}
```

The exact schema may differ if a better design is available.

The important requirements are:

- call-site identity;
- resolution status;
- type of indirect call;
- vtable identity if known;
- byte offset;
- slot index;
- resolved function identity;
- evidence or resolution method;
- failure reason for unresolved cases.

Do not invent semantic names for the resolved function.

---

# Graph Integration

If practical, extend `graph.json` so resolved virtual calls are represented as edges.

Example conceptual edge:

```json
{
  "callerName": "FUN_1431bc320",
  "callerAddress": "1431BC320",
  "callSiteAddress": "1431BC...",
  "edgeKind": "virtual",
  "vtableName": "TESContainer::vftable",
  "vtableByteOffset": 80,
  "resolvedName": "FUN_...",
  "resolvedAddress": "...",
  "resolvedInternal": true
}
```

Do not break the existing direct-call schema if compatibility can be preserved.

A separate `indirectEdges` array is acceptable if cleaner.

---

# Resolved Target Export

If an indirect target is resolved to an internal function:

- export the same seven-file context bundle used by the existing exporter:

```text
metadata.json
decompiled.c
callers.json
callees.json
strings.json
globals.json
constants.json
```

- deduplicate it by function entry address;
- do not export the same function twice if it is already present as a direct callee;
- record in metadata or graph that it was reached through a virtual/indirect edge.

---

# Evidence and Confidence

Do not treat every guessed indirect target as fact.

For each resolution, record a confidence or resolution basis.

Suggested statuses:

```text
resolved-static-vtable
unresolved-unknown-vtable
unresolved-nonconstant-offset
unresolved-multiple-candidates
unresolved-no-function-at-slot
unsupported-pattern
```

If confidence is not effectively deterministic, do not claim a definitive target.

For the supported simple case, resolution should ideally be based on direct program data rather than heuristics.

---

# Implementation Options

Use whichever Ghidra APIs are most appropriate and stable.

Potential sources of evidence may include:

- function instructions;
- references;
- data definitions at vtable addresses;
- symbols;
- pointer-size-aware memory reads;
- decompiler output;
- p-code only if needed for the simple case.

Prefer existing Ghidra program model data over parsing decompiled C text.

Avoid brittle regex-based interpretation of decompiler text if possible.

If decompiler information is used, document where and why.

---

# Important Research Guardrail

The goal of this task is not to prove that the resolved virtual function is the resource-family allocator.

The goal is only:

> identify the concrete function behind the indirect call and export enough context to inspect it.

Do not update `known-facts.md` with a semantic interpretation of the resolved function unless the evidence truly supports it.

If useful, update `docs/function-register.md` only with:

- the new function address/name;
- the fact that it is reached through the specified virtual call;
- a cautious current interpretation;
- open questions.

Do not rename the function in Ghidra.

---

# Error Handling

The script should continue gracefully if:

- no function is selected;
- no indirect calls are found;
- the receiver type/vtable cannot be determined;
- the vtable symbol exists but the slot cannot be read;
- the slot points outside mapped memory;
- the pointer is null;
- no Ghidra function exists at the pointed-to address;
- decompilation of the resolved target fails.

An unresolved call should still appear in `indirect-calls.json`.

One failure must not abort unrelated analysis.

---

# Safety Requirements

The script must remain read-only with respect to the Ghidra program.

Do not:

- start transactions;
- rename functions;
- create labels;
- modify symbols;
- add comments;
- apply data types;
- alter memory;
- change signatures;
- modify analysis state intentionally.

Output files may be written to the chosen export directory.

---

# Documentation

Update:

```text
ghidra/README.md
```

to document:

- what the indirect/virtual-call analyzer does;
- the limited supported case;
- how to run it;
- where output is written;
- what `indirect-calls.json` contains;
- how resolved targets are exported;
- that unresolved indirect calls are expected and retained;
- that this is not a general-purpose devirtualizer.

---

# Acceptance Criteria

A successful live run against:

```text
FUN_1431bc320
0x1431BC320
```

should:

1. identify the indirect call through fixed offset `0x50`;
2. associate it with `TESContainer::vftable` if the Ghidra evidence supports that association;
3. calculate the corresponding slot using the current program pointer size;
4. read the function pointer stored in that slot;
5. resolve it to a Ghidra function if one exists;
6. record the relationship in `indirect-calls.json`;
7. export the resolved target's full context bundle;
8. leave the Ghidra program unchanged.

If the call cannot be resolved, the output must clearly explain why.

---

# Explicit Non-Goals

Do not implement yet:

- depth-2 or deeper recursive neighbourhood export;
- arbitrary virtual dispatch recovery;
- class hierarchy reconstruction;
- indirect-call target enumeration across the whole program;
- vtable scanning for every class;
- dynamic instrumentation;
- runtime hooks;
- symbolic execution;
- SSA/dataflow framework;
- automated function renaming;
- automatic resource-algorithm inference;
- headless Ghidra orchestration.

This iteration should remain tightly focused on the simple virtual call immediately visible in `FUN_1431bc320`.

---

# Deliverables

When finished, report:

1. files added;
2. files modified;
3. whether existing exporter code was refactored;
4. how the vtable is identified;
5. how the vtable slot is read;
6. how pointer size is handled;
7. how the resolved target is mapped to a Ghidra function;
8. how unresolved cases are represented;
9. how duplicate function bundles are avoided;
10. exact live-test instructions for `FUN_1431bc320`;
11. any API assumptions that still require live validation in Ghidra;
12. any limitations or edge cases discovered during implementation.

Do not proceed to broader indirect-call analysis until this version has been live-tested successfully.
