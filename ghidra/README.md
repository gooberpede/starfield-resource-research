# Ghidra tooling

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
