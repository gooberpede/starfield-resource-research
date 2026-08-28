# Ghidra tooling

This directory currently provides two read-only exporters:

- `ExportSelectedFunctionContext.java` exports one selected function.
- `ExportFunctionNeighbourhood.java` exports the selected root function plus the resolved implementations of its direct internal callees. Its traversal depth is fixed at 1.

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

`manifest.json` identifies the root, fixed depth, program, timestamp, successful bundle count, and any per-function failures. `graph.json` contains the root and one edge per distinct direct callee; each edge preserves the directly called function and the resolved implementation separately.

Files with the same names are replaced when the same neighbourhood is exported again. The script does not delete old function directories, so a bundle from an earlier run can remain if analysis changes and that function is no longer a direct callee. Use the current manifest and graph as the authoritative membership list for a run.

### Compatibility and known limitations

- The script is written against the same Ghidra 11.x APIs as the tested single-function exporter. The neighbourhood exporter itself has not yet been live-tested in Ghidra.
- Direct callees come from Ghidra's `Function.getCalledFunctions` results and therefore depend on call references and defined functions in the current analysis database.
- Thunk resolution depends on Ghidra having marked the forwarding function as a thunk and assigned its thunk target.
- Indirect calls, unresolved call targets, and virtual dispatch recovery are out of scope and will not appear as resolved graph edges.
- External/imported functions are represented in relationship metadata but are not decompiled or given context bundles.
- Depth is fixed at 1; there is no recursive or transitive call-tree crawl.
- The exporter does not generate control-flow graphs, p-code, decompiler ASTs, dataflow, inferred semantic names, reconstructed structures, or vtable analysis.
- The export is not atomic. Cancellation or an I/O failure can leave a partially written neighbourhood; the final manifest is written only after function processing completes.

Like the single-function exporter, this script is non-destructive with respect to Ghidra: it starts no transaction and does not rename symbols, change signatures, create labels or comments, apply types, modify memory, or intentionally change analysis state.
