# Codex Brief — Ghidra Neighbourhood Export, Depth 1

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

The existing script `ExportSelectedFunctionContext.java` has now been tested successfully inside Ghidra against:

```text
FUN_1431bc320
0x1431BC320
CreationKit.exe
```

It successfully exported:

```text
metadata.json
decompiled.c
callers.json
callees.json
strings.json
globals.json
constants.json
```

The live test confirmed that this first-generation exporter works.

The next goal is to reduce the amount of manual navigation required in Ghidra.

---

# What We Are Trying to Achieve

At present, the script can export one selected function.

We now want one Ghidra run to export:

1. the selected root function; and
2. all of its direct internal callees;
3. with simple thunks resolved to their real implementation functions.

This is intentionally only a **depth-1 neighbourhood**.

Do not recursively crawl an entire call tree yet.

The purpose of this iteration is to let us inspect one function and its immediate implementation neighbourhood without manually visiting and exporting every callee in Ghidra.

---

# Why Thunk Resolution Matters

Ghidra may show a callee such as:

```text
thunk_FUN_140e457b0
```

at a small thunk address, while the actual implementation we care about is:

```text
FUN_140e457b0
0x140E457B0
```

A thunk is typically a tiny forwarding function, often little more than a jump to another function.

For reverse engineering, the forwarding stub is usually much less interesting than the underlying implementation.

The exporter should therefore preserve both facts:

```text
call site -> thunk -> resolved implementation
```

but export the full analysis context of the resolved implementation.

Do not silently discard the thunk relationship.

---

# Required Behaviour

Implement a new non-destructive Ghidra script under:

```text
ghidra/scripts/
```

A suitable filename would be:

```text
ExportFunctionNeighbourhood.java
```

or another clear name.

The existing single-function exporter should remain available unless there is a strong implementation reason to refactor shared code.

If practical, factor reusable export logic into helper methods or a shared helper class rather than duplicating large blocks of code.

Do not over-engineer the design.

---

# Target Selection

The root target should be selected using the same basic interaction pattern as the current exporter:

- use the function containing the current cursor location;
- fail clearly if the cursor is not inside a function.

The first target for live testing will again be:

```text
FUN_1431bc320
0x1431BC320
```

---

# Depth Rule

Export:

```text
depth 0 = selected root function
depth 1 = direct internal callees of the root function
```

Do not export callees of depth-1 functions in this iteration.

Do not recurse beyond depth 1.

Do not export the same resolved implementation twice if multiple call sites or thunks point to it.

---

# Internal Versus External Functions

The script should distinguish between functions implemented inside the currently analysed program and external/imported functions.

Examples of external/library functions may include Qt functions such as:

```text
QSpinBox::value
```

For this iteration:

- include external/library callees in relationship metadata;
- do not attempt to export full decompilation/context bundles for external functions unless Ghidra considers them normal internal functions with usable bodies.

The priority is the internal Starfield/Creation Kit implementation neighbourhood.

---

# Thunk Resolution Requirements

For each direct callee of the root:

1. determine whether the callee is a thunk;
2. if it is a thunk, resolve it to the ultimate non-thunk target where practical;
3. record:
   - original callee name;
   - original callee address;
   - whether it is a thunk;
   - resolved function name;
   - resolved function address;
4. export the full function context for the resolved implementation if it is internal and exportable.

If a thunk cannot be resolved safely:

- record that fact;
- preserve the original callee metadata;
- do not fail the entire export.

Avoid infinite loops or cyclic thunk resolution.

---

# Full Context Bundle

For every exported function — root and resolved internal depth-1 callees — generate the same context currently produced by `ExportSelectedFunctionContext.java`.

At minimum:

```text
metadata.json
decompiled.c
callers.json
callees.json
strings.json
globals.json
constants.json
```

Preserve the current useful behaviour:

- non-destructive;
- no Ghidra transactions;
- no symbol renaming;
- no comments added;
- no type changes;
- no program modification;
- continue exporting other evidence if decompilation fails.

---

# Output Layout

Use a neighbourhood-level directory.

Suggested structure:

```text
exports/
└─ neighbourhoods/
   └─ FUN_1431bc320__1431BC320/
      ├─ graph.json
      ├─ manifest.json
      └─ functions/
         ├─ FUN_1431bc320__1431BC320/
         │  ├─ metadata.json
         │  ├─ decompiled.c
         │  ├─ callers.json
         │  ├─ callees.json
         │  ├─ strings.json
         │  ├─ globals.json
         │  └─ constants.json
         │
         ├─ FUN_140e457b0__140E457B0/
         │  └─ ...
         │
         └─ ...
```

Including the address in directory names is preferred because function names may not always be unique.

If Windows filename restrictions require sanitisation, document the sanitisation rule.

---

# manifest.json

Add a simple manifest describing the export.

Suggested fields:

```json
{
  "rootFunctionName": "FUN_1431bc320",
  "rootFunctionAddress": "1431BC320",
  "depth": 1,
  "exportedFunctionCount": 5,
  "generatedAt": "...",
  "programName": "CreationKit.exe"
}
```

Use whichever timestamp format is convenient and deterministic enough for the purpose.

Do not invent semantic interpretations of functions in the manifest.

---

# graph.json

Create one compact machine-readable graph describing the immediate call relationships.

Each edge should preserve both the directly referenced callee and any resolved implementation.

A possible schema:

```json
{
  "root": {
    "name": "FUN_1431bc320",
    "address": "1431BC320"
  },
  "edges": [
    {
      "callerName": "FUN_1431bc320",
      "callerAddress": "1431BC320",
      "calleeName": "thunk_FUN_140e457b0",
      "calleeAddress": "14013A471",
      "isThunk": true,
      "resolvedName": "FUN_140e457b0",
      "resolvedAddress": "140E457B0",
      "resolvedInternal": true
    }
  ]
}
```

The exact schema may differ if you have a better design, but preserve these concepts.

Do not infer or add semantic labels such as:

```text
"resource allocator"
"family selector"
"seed processor"
```

unless such names already exist in Ghidra.

This phase is extraction, not interpretation.

---

# Duplicate Handling

If multiple edges resolve to the same implementation function:

```text
thunk A -> FUN_X
thunk B -> FUN_X
```

export `FUN_X` only once.

The graph should still retain both original edges.

Use function entry address as the preferred identity key.

---

# Error Handling

The script should fail gracefully.

Examples:

## No selected function

Show a clear message and stop.

## Decompilation failure

Still export:

- metadata;
- callers;
- callees;
- strings;
- globals;
- constants where possible.

Record decompilation failure in metadata.

## One callee cannot be exported

Do not abort the whole neighbourhood.

Record the failure in the manifest or graph and continue with the remaining functions.

## Thunk resolution failure

Preserve the original callee and mark resolution as unsuccessful.

---

# Safety Requirements

This script must be read-only with respect to the Ghidra program.

Do not:

- begin a transaction;
- rename symbols;
- change function signatures;
- create labels;
- create comments;
- apply types;
- modify memory;
- modify analysis state intentionally.

Writing output files to the user-selected export directory is expected.

Retain the current protection against accidentally exporting into Ghidra project storage if that protection remains reliable.

---

# Documentation

Update:

```text
ghidra/README.md
```

to explain:

1. the difference between the single-function exporter and neighbourhood exporter;
2. how to run the new script;
3. that depth is currently fixed at 1;
4. how thunk resolution works at a high level;
5. the output directory structure;
6. that the script is non-destructive;
7. known limitations.

Do not replace useful existing instructions for the original exporter.

---

# Scope Exclusions

Do not implement these yet:

- arbitrary recursive depth;
- transitive call-tree crawling;
- control-flow graphs;
- p-code export;
- decompiler AST export;
- dataflow analysis;
- automatic semantic function naming;
- structure reconstruction;
- vtable analysis;
- indirect-call recovery;
- function similarity analysis;
- automated hypothesis testing;
- direct invocation of headless Ghidra;
- integration with Starfield runtime DLL tooling.

These may become future milestones.

Keep this iteration focused.

---

# Acceptance Test

The first live test will be performed in Ghidra with the cursor inside:

```text
FUN_1431bc320
0x1431BC320
```

A successful result should produce:

- a neighbourhood manifest;
- a graph of direct calls;
- a full context bundle for `FUN_1431bc320`;
- full context bundles for each resolvable internal direct callee;
- simple thunk relationships preserved and resolved;
- no modification to the Ghidra program.

Based on the previous single-function export, likely direct callees include functions corresponding to:

```text
thunk_FUN_140d7ce60
thunk_FUN_140e457b0
thunk_FUN_140d97800
thunk_FUN_140f5fac0
QSpinBox::value
```

Do not hard-code this list.

Discover it from Ghidra.

---

# Deliverables

When finished, report:

1. files added;
2. files modified;
3. whether existing exporter code was refactored;
4. how thunk resolution is implemented;
5. how duplicate resolved functions are avoided;
6. how to install/run the new script;
7. the exact output structure;
8. any Ghidra API assumptions that could not be live-tested;
9. any limitations or risks that should be checked during the first live run.

Do not proceed to deeper recursive export until this version has been live-tested successfully.
