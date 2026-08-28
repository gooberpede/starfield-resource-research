# Ghidra tooling

This directory currently provides two read-only exporters:

- `ExportSelectedFunctionContext.java` exports one selected function.
- `ExportFunctionNeighbourhood.java` exports the selected root function plus the resolved implementations of its direct internal callees. Its traversal depth is fixed at 1. It also performs focused recovery of simple vtable-based indirect calls in the root.

Both scripts read the current Ghidra analysis database and write plain files beneath a user-selected export root. Neither script starts a transaction or modifies the open program.

## ExportSelectedFunctionContext.java

`ExportSelectedFunctionContext.java` is a read-only Ghidra Java script that exports analysis context for the function containing the CodeBrowser cursor. It does not start a transaction and does not modify the program, symbols, types, labels, comments, or function names.

The script exports only the selected function and its direct relationships. It does not recursively traverse the call tree.

### Compatibility and assumptions

- Written as a Java `GhidraScript` for Ghidra 11.x.
- Uses Ghidra's bundled Gson library for JSON output; no separate script dependency is required.
- Expected to work on recent Ghidra 10.x releases that expose the same public scripting and decompiler APIs, but those versions have not been tested.
- The program should have completed normal Ghidra analysis. Results depend on the functions, references, strings, and data already defined in the current program.
- The Decompiler component must be available. Decompilation is limited to 60 seconds.
- The chosen export root must be a normal filesystem directory outside the Ghidra project storage. The repository's `exports` directory is the intended choice.

### Installation

Either add this repository's `ghidra/scripts` directory as a Ghidra script directory:

1. Open Ghidra's **Script Manager** with **Window > Script Manager**.
2. Open **Manage Script Directories** from the Script Manager toolbar.
3. Add the absolute path to this repository's `ghidra/scripts` directory.
4. Refresh the Script Manager if `ExportSelectedFunctionContext.java` does not appear immediately.

Alternatively, copy `ExportSelectedFunctionContext.java` into any script directory already configured in Ghidra. Keeping the repository directory configured directly makes future updates immediately available.

### Usage

1. Open the analysed Starfield or Creation Kit program in CodeBrowser.
2. Navigate to the target function and place the cursor anywhere inside its body. The script uses the function containing the current cursor address; it does not use the current selection or highlighted text.
3. In **Script Manager**, find `ExportSelectedFunctionContext.java` under **Starfield Research** and run it.
4. When prompted for an export root, choose this repository's `exports` directory (not the Ghidra project directory).
5. Review the Ghidra console for the final absolute output path or an error message.

If the cursor is not inside a defined function, the script reports an error and writes nothing. It also rejects an export root located inside the current Ghidra project's storage directory. If decompilation fails or times out, the script still exports the remaining context, records the failure in `metadata.json`, and writes a failure comment to `decompiled.c`.

### Running against FUN_1431bc320

1. In CodeBrowser, press **G** (**Go To**).
2. Enter `1431BC320` (or `0x1431BC320`, depending on the accepted address syntax for the loaded program) and go to that address.
3. Confirm the Listing shows `FUN_1431bc320` and leave the cursor at the entry point or anywhere in its function body.
4. Run `ExportSelectedFunctionContext.java` from Script Manager.
5. Choose `<repository>/exports` as the export root.

The expected output is:

```text
exports/functions/FUN_1431bc320/
    metadata.json
    decompiled.c
    callers.json
    callees.json
    strings.json
    globals.json
    constants.json
```

Existing files with these names in the target function directory are replaced on a subsequent export. Generated exports are ignored by Git by default.

### Output notes

- `metadata.json` records program identifiers, cursor address, function name, entry address, signature, and decompiler status.
- `decompiled.c` contains Ghidra's pseudocode, or a diagnostic comment if decompilation failed.
- `callers.json` and `callees.json` contain direct function relationships reported by Ghidra.
- `strings.json` contains defined string data referenced by instructions in the function, plus the referring instruction addresses.
- `globals.json` contains data references to memory addresses outside the selected function body. Defined symbol and data-type names are included when available.
- `constants.json` contains scalar operands found in the function's instructions, including signed decimal and unsigned hexadecimal forms. This deliberately preserves offsets and masks as well as obvious numeric literals; later tooling can filter them without losing evidence.

All JSON files are UTF-8 and deterministic by address where applicable. The script reads the current analysis database and writes only to the selected export directory.

## ExportFunctionNeighbourhood.java

`ExportFunctionNeighbourhood.java` reduces the manual work needed to inspect one function and its immediate implementation neighbourhood. It exports:

- depth 0: the function containing the CodeBrowser cursor;
- depth 1: each distinct, exportable internal implementation reached by a direct call from the root.
- resolved virtual target: each distinct internal function recovered from a supported static vtable call in the root.

It does not export callees of the depth-1 functions. Their direct caller and callee summaries are still included in each function bundle, just as they are for the single-function exporter.

### Installation and usage

If this repository's `ghidra/scripts` directory is already configured in Script Manager, refresh the manager and `ExportFunctionNeighbourhood.java` should appear under **Starfield Research**. Otherwise, follow the script-directory installation steps above or copy the new script into a configured Ghidra script directory.

To run it:

1. Open the analysed program in CodeBrowser and allow normal analysis to complete.
2. Put the cursor anywhere inside the root function. For the first planned live test, go to `1431BC320` and confirm that the containing function is `FUN_1431bc320`.
3. Run `ExportFunctionNeighbourhood.java` from Script Manager.
4. Choose the repository's `exports` directory as the export root. Do not choose a directory inside Ghidra project storage.
5. Review the console and the generated `manifest.json` for any per-function export failures.

The script reports an error and writes nothing if the cursor is not inside a defined function. A decompilation failure does not stop the other context files from being generated. Failure to export one function bundle is recorded in the manifest and does not stop the remaining bundles.

### Focused virtual-call resolution

The neighbourhood exporter inspects the root function's decompiler high p-code for `CALLIND` operations. It supports the deliberately limited case where the target has the form:

```text
load(load(receiver) + constant byte offset)
```

For that pattern, it attempts to tie the receiver to one uniquely identifiable vtable. It accepts either a vtable address propagated directly into the decompiler expression or the following limited initializer pattern:

1. normalize the receiver through `COPY`, `CAST`, integer extension, and constant `PTRSUB`, `PTRADD`, or `INT_ADD` wrappers;
2. find an earlier direct `CALL` in the same high function whose argument 0 has the same normalized identity;
3. resolve the called function's Ghidra-defined thunk chain;
4. decompile the resolved implementation and obtain its high-p-code parameter 0;
5. require a `STORE` through that parameter at byte offset zero;
6. require the stored value to resolve to a program address with exactly one symbol name containing `vftable` or `vtable`, case-insensitively.

This is dataflow evidence only: the script does not require the callee to be named or typed as a constructor. Matching uses structural constant-offset expressions and high-variable object identity within each decompilation, not decompiled C variable names or storage reuse alone. The serialized identity strings are diagnostics rather than the equality test. Matching is deliberately conservative and confined to argument 0.

Every relevant `STORE` in a matched initializer is recorded in execution-address context with its destination identity, offset, stored address, symbol names, and acceptance or rejection reason. Repeated stores of the same vtable address are retained as provenance but collapse to one vtable candidate. If stores yield more than one distinct accepted vtable address, the result is `unresolved-ambiguous-vptr-stores`; the script does not assume that the first or last constructor store is the final dynamic type.

Once one vtable is identified, the script:

1. adds the fixed byte offset to the vtable symbol address;
2. calculates the slot index when the offset is aligned to `Program.getDefaultPointerSize()`;
3. reads exactly that many bytes from program memory using the program's endianness;
4. maps the resulting address with `FunctionManager.getFunctionAt()`;
5. follows any Ghidra-defined thunk chain using the same bounded logic as direct calls;
6. exports the resolved internal implementation's normal seven-file context bundle.

This is not a general-purpose C++ devirtualizer. It does not perform whole-program points-to analysis, class-hierarchy recovery, symbolic execution, or speculative target enumeration. If receiver matching is absent or ambiguous, the call remains unresolved.

Every computed call instruction in the root is retained in `indirect-calls.json`. Schema version 2 adds `receiverIdentity`, `initializerCandidates`, and `provenance` to the existing call record. `initializerCandidates` contains the earlier matching call, thunk-resolution result, resolved implementation, normalized parameter-0 identity, inspected vptr stores, symbol evidence, and rejection reasons. A successful constructor-derived result uses `resolutionBasis: constructor-vptr-store`; its `provenance` array identifies the earlier call, directly called function, resolved implementation, argument index, and offset-zero store. Unsupported or failed cases include a `failureReason`. Status values currently include:

```text
resolved-static-vtable
unresolved-receiver-provenance
unresolved-no-initializer-call
unresolved-no-vptr-store
unresolved-ambiguous-vptr-stores
unresolved-vtable-symbol
unresolved-nonconstant-offset
unresolved-no-function-at-slot
unsupported-pattern
```

`graph.json` preserves its existing direct `edges` array and adds a separate `indirectEdges` array. Resolved targets are deduplicated with direct targets by function entry address, so a function bundle is written at most once per run.

### Thunk handling

For every direct callee, the script records the function referenced by the root's call instruction. If that function is a Ghidra thunk, the script follows `Function.getThunkedFunction(false)` one hop at a time until it reaches a non-thunk implementation. It retains the original thunk name/address, grouped call-site addresses, resolution status, hop count, and resolved name/address in `graph.json`.

Thunk traversal tracks visited entry addresses and has a 100-hop safety limit. An unresolved or cyclic chain is recorded on its graph edge without aborting the neighbourhood export. External targets remain in the graph but do not receive full context bundles.

Resolved implementations are keyed by function entry address. If several thunks or direct callees resolve to the same implementation, the graph preserves every original edge while the implementation bundle is exported once.

### Output structure

Directory names use:

```text
<sanitised-function-name>__<sanitised-uppercase-entry-address>
```

Each character outside `A-Z`, `a-z`, `0-9`, `.`, `_`, and `-` is replaced with `_`. Including the address avoids collisions between functions with the same name.

For `FUN_1431bc320`, the output has this shape:

```text
exports/
└─ neighbourhoods/
   └─ FUN_1431bc320__1431BC320/
      ├─ graph.json
      ├─ manifest.json
      ├─ indirect-calls.json
      └─ functions/
         ├─ FUN_1431bc320__1431BC320/
         │  ├─ metadata.json
         │  ├─ decompiled.c
         │  ├─ callers.json
         │  ├─ callees.json
         │  ├─ strings.json
         │  ├─ globals.json
         │  └─ constants.json
         └─ FUN_140e457b0__140E457B0/
            └─ ...same seven context files...
```

`manifest.json` identifies the root, fixed depth, program, timestamp, successful bundle count, indirect-call counts and analysis status, and any per-function failures. `graph.json` contains the root and one edge per distinct direct callee; each edge preserves the directly called function and the resolved implementation separately.

For the first virtual-call live test against `FUN_1431bc320`:

1. Go to `1431BC320` in the analysed `CreationKit.exe` program and confirm the cursor is inside `FUN_1431bc320`.
2. Confirm normal analysis is complete and that Ghidra exposes the expected `TESContainer::vftable` symbol.
3. Run `ExportFunctionNeighbourhood.java` and choose the repository's `exports` directory.
4. Open `exports/neighbourhoods/FUN_1431bc320__1431BC320/indirect-calls.json`.
5. Locate the computed call whose `vtableByteOffset` is `80`; verify that `vtableSlotIndex` is `10` for the 8-byte pointer-size program.
6. Verify that `receiverIdentity` is populated and that an `initializerCandidates` entry at the preceding initialization call identifies the called thunk and its resolved implementation corresponding to `FUN_140d7ce60`.
7. In that candidate, verify an accepted `vptrStores` entry at offset `0`, with a stored address whose `symbolNames` includes `TESContainer::vftable`.
8. Verify that the indirect-call record names `TESContainer::vftable`, reports `resolved-static-vtable`, uses `resolutionBasis: constructor-vptr-store`, and identifies both the slot pointer and resolved function.
9. Verify that `provenance` records the initializer call site, direct and resolved initializer functions, argument index `0`, vptr store address, and store offset `0`.
10. Confirm that `functions/<resolved-name>__<resolved-address>/` contains the seven standard context files and that `graph.json` contains the matching `indirectEdges` entry.
11. Review the Ghidra undo/history state if desired; the script starts no transaction and intentionally changes no program state.

If the call remains unresolved, use its precise status and `initializerCandidates` diagnostics to distinguish receiver matching, thunk resolution, parameter-0 recovery, offset-zero store recovery, constant-address recovery, vtable-symbol confidence, and slot lookup failures. Do not update the function register with a virtual target until this live output directly supports it.

Files with the same names are replaced when the same neighbourhood is exported again. The script does not delete old function directories, so a bundle from an earlier run can remain if analysis changes and that function is no longer a direct callee. Use the current manifest and graph as the authoritative membership list for a run.

### Compatibility and known limitations

- The script is written against Ghidra 11.x public program-model and decompiler APIs. The direct depth-1 export has been live-tested; the new virtual-call pass still requires the live test above.
- Direct callees come from Ghidra's `Function.getCalledFunctions` results and therefore depend on call references and defined functions in the current analysis database.
- Thunk resolution depends on Ghidra having marked the forwarding function as a thunk and assigned its thunk target.
- Only simple fixed-offset vtable dispatch is eligible for indirect resolution. All other computed calls are retained as unresolved records rather than being guessed or dropped.
- External/imported functions are represented in relationship metadata but are not decompiled or given context bundles.
- Depth is fixed at 1; there is no recursive or transitive call-tree crawl.
- The constructor-to-vptr path assumes the decompiler exposes the caller receiver and argument 0 in equivalent supported forms, exposes the resolved initializer's parameter 0 in `LocalSymbolMap`, and represents the vptr assignment as a high-p-code `STORE` whose destination is parameter 0 plus constant zero.
- Constant vtable recovery assumes the stored value remains a constant/address varnode (possibly under the supported wrappers) and that the exact address has one unambiguous symbol name containing `vftable` or `vtable`.
- The exporter does not follow aliases through memory, PHI/`MULTIEQUAL`, nonconstant pointer arithmetic, helper calls inside the initializer, base-to-derived adjustments, multiple inheritance, or nested constructor chains. It does not infer which of several distinct vptr stores is final.
- The exporter uses decompiler high p-code only for this focused pattern. It does not export raw p-code, build a general SSA/dataflow framework, infer semantic names, or reconstruct structures or class hierarchies.
- The export is not atomic. Cancellation or an I/O failure can leave a partially written neighbourhood; the final manifest is written only after function processing completes.

Like the single-function exporter, this script is non-destructive with respect to Ghidra: it starts no transaction and does not rename symbols, change signatures, create labels or comments, apply types, modify memory, or intentionally change analysis state.
