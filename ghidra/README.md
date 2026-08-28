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
2. when that stronger normalization does not establish a receiver, conservatively correlate argument 0 as `&stack[X]` with target-side vptr storage at exactly `stack[X]`;
3. find an earlier direct `CALL` in the same high function whose argument 0 has the recovered receiver identity;
4. resolve the called function's Ghidra-defined thunk chain;
5. decompile the resolved implementation and obtain its high-p-code parameter 0;
6. require a `STORE` through that parameter at byte offset zero;
7. require the stored value to resolve to a program address with exactly one symbol name containing `vftable` or `vtable`, case-insensitively.

The stack-object rule uses `resolutionBasis: stack-object-address-vptr-match`. It requires argument 0 to reduce through the existing bounded stack-address provenance logic to one stack offset, requires the target vptr source to expose one stack-backed storage object, requires both sizes to equal the program pointer size, and requires exact offset equality. Thus `&stack[-0xA8]` may match vptr contents stored at `stack[-0xA8]`; it does not match nearby offsets. The rule does not use variable names, infer from storage reuse alone, or implement general alias analysis. Existing direct/high-variable normalization has precedence. If both supported methods produce conflicting receiver expressions, the result is ambiguous and constructor provenance is not guessed.

This is dataflow evidence only: the script does not require the callee to be named or typed as a constructor. Matching uses structural constant-offset expressions and high-variable object identity within each decompilation, not decompiled C variable names or storage reuse alone. The serialized identity strings are diagnostics rather than the equality test. Matching is deliberately conservative and confined to argument 0.

Every relevant `STORE` in a matched initializer is recorded with its instruction address, destination identity, receiver offset, stored address, symbol names, and acceptance or rejection reason. Accepted stores also record their high-p-code basic-block start/index, order within that block, and outgoing block addresses. Repeated stores of the same vtable address are retained as provenance but collapse to one vtable-address candidate.

C++ constructors commonly install a base-class vptr before base/member initialization and then replace it with the derived-class vptr. When an initializer contains more than one distinct accepted vtable, the exporter performs a bounded high-p-code CFG proof rather than treating decompiler or source display order as execution order. It propagates the identity of the last accepted same-offset store from the initializer entry block through `PcodeBlockBasic` outgoing edges. Within a block, `PcodeBlockBasic.getIterator()` supplies operation order. A candidate is selected only when every reachable normal high-p-code `RETURN` has that exact store as its final accepted write, every accepted candidate is reachable, and no reachable terminal block or indirect branch makes control flow unclear. Earlier candidates are then recorded as superseded by the selected store.

The rule is deliberately conservative. A return with no accepted store, differing final stores on different return paths, an unassignable/unreachable store, an indirect branch, a non-basic-block edge, or a terminal block without `RETURN` preserves ambiguity with a specific failure status. The implementation does not infer class hierarchy, compare class-name specificity, or apply a global “last write wins” heuristic. Exception and unwind flow is not modeled; only normal decompiler `RETURN` operations are considered in this supported case.

Once one vtable is identified, the script:

1. adds the fixed byte offset to the vtable symbol address;
2. calculates the slot index when the offset is aligned to `Program.getDefaultPointerSize()`;
3. reads exactly that many bytes from program memory using the program's endianness;
4. maps the resulting address with `FunctionManager.getFunctionAt()`;
5. follows any Ghidra-defined thunk chain using the same bounded logic as direct calls;
6. exports the resolved internal implementation's normal seven-file context bundle.

This is not a general-purpose C++ devirtualizer. It does not perform whole-program points-to analysis, class-hierarchy recovery, symbolic execution, or speculative target enumeration. If receiver matching is absent or ambiguous, the call remains unresolved.

Every computed call instruction in the root is retained in `indirect-calls.json`. Schema version 4 adds final-vptr CFG selection evidence to the version-3 receiver, initializer, and provenance fields. For a stack-object match, `receiverResolution` records `status: resolved-stack-object`, `resolutionBasis: stack-object-address-vptr-match`, argument index, argument and target stack offsets, sizes, equality, target defining-opcode/address metadata, evidence, and any failure reason. `initializerCandidates` contains the earlier matching call, thunk-resolution result, resolved implementation, normalized parameter-0 identity, inspected vptr stores, symbol evidence, rejection reasons, and per-initializer `vptrSelection` when multiple distinct vtables require analysis. The call-level `vptrSelection` retains candidate count, receiver offset, normal return addresses, selected store/vtable, superseded stores, evidence, and failure reason. A successful selection uses `status: resolved-final-store` and `resolutionBasis: ordered-final-vptr-store`. A successful constructor-derived call still uses top-level `resolutionBasis: constructor-vptr-store`; its `provenance` array identifies the earlier call, directly called function, resolved implementation, argument index, and selected offset-zero store. `graph.json` schema version 2 adds `vptrSelectionBasis` to virtual edges without changing direct edges. Unsupported or failed cases include a `failureReason`. Status values currently include:

```text
resolved-static-vtable
unresolved-receiver-provenance
unresolved-no-initializer-call
unresolved-no-vptr-store
unresolved-ambiguous-vptr-stores
unresolved-branching-vptr-final-state
unresolved-no-unique-final-vptr
unresolved-vptr-control-flow
unresolved-vtable-symbol
unresolved-nonconstant-offset
unresolved-no-function-at-slot
unsupported-pattern
```

### Focused high-p-code diagnostics

The neighbourhood exporter also writes `pcode-diagnostics.json` to explain indirect calls whose status is `unresolved-receiver-provenance` and to preserve the evidence for calls that use the stack-object receiver rule. This remains a focused diagnostic, not a general dump of every p-code operation in the function. Other successful or differently unresolved indirect calls do not receive a diagnostic entry; the file is still written with an empty `calls` array when nothing qualifies so each run has a predictable output shape.

For each included call, the JSON records:

- the `CALLIND` operation, opcode, sequence number, instruction address, output, and indexed inputs;
- the indirect target varnode and a recursive tree of its defining operations;
- every defining operation's opcode, sequence metadata, parent function, output, input count, and indexed inputs;
- varnode size, address space, offset, address, storage flags, constant value, high-variable metadata, representative storage, and datatype where available;
- every `CALLIND` argument, using `argumentIndex` for the call argument and `pcodeInputIndex` for its original p-code input position, together with its own recursive definition tree;
- conservative stack-address provenance for each argument, including a signed stack offset, readable stack location, confidence label, resolution basis, and derivation chain when the expression reduces to a stack pointer plus constant offsets through supported wrappers;
- stack-backed storage nodes found in the call-target definition tree, including their path, size, defining operation, and whether they occur on the base side of a constant-offset addition;
- focused `INDIRECT` metadata for target stack-storage nodes defined by a call side effect, including the operation inputs, sequence address, associated instruction, and same-storage check;
- `receiverStorageCorrelation`, which compares argument 0's resolved stack-address offset with the target expression's stack-storage offsets and reports `matched-stack-object` only when the offsets agree;
- comparisons between call argument 0 (the likely C++ `this` argument) and each nonconstant varnode encountered in the target tree: exact varnode, high-variable object identity, storage, and defining-operation equality.

The diagnostic follows Ghidra's high-p-code `CALLIND` convention: input 0 is the indirect target and inputs 1 through N are call arguments. Thus `argumentIndex: 0` corresponds to `pcodeInputIndex: 1`. This convention is also recorded in each diagnostic call object.

Definition traversal has a maximum depth of 8. The target and each argument use independent visited sets, so a node seen in one tree does not prematurely stop another tree. Traversal stops at constants, null varnodes, inputs without definitions, the depth bound, and previously visited varnodes or defining operations within that tree. Repeated nodes receive stable IDs within that one call diagnostic, and stopped branches contain a `stopReason`. The IDs are diagnostic identities scoped to one exported call; high-variable names or storage equality alone are not treated as proof of semantic equivalence.

Stack-address provenance is deliberately narrower than alias analysis. It recognizes the configured stack-pointer register plus constant `INT_ADD`, `PTRSUB`, or constant-index `PTRADD` arithmetic, with `COPY`, `CAST`, and integer-extension wrappers. Status is `resolved-stack-address`, `unresolved-stack-address`, or `unsupported-stack-address-pattern`. Stack offsets are emitted as signed decimal values, signed hexadecimal strings such as `-0xA8`, and readable labels such as `stack[-0xA8]`. A stack-space varnode in the target tree is treated as stored contents, not as proof that an argument is its address.

`receiverStorageCorrelation` preserves the detailed evidence for the address/storage relationship—argument 0 is the address of a stack object while the target expression reads contents from the same stack offset. It does not compare the argument value to the vptr value. When stronger receiver normalization is unavailable, the resolver now applies the same conservative exact-offset relationship to establish the receiver and then reuses the existing initializer/constructor provenance path. An `INDIRECT` definition remains supporting side-effect evidence only; it is not proof that an earlier call is a constructor.

For the current diagnostic target, navigate to `FUN_1431bc320` at `1431BC320`, run the exporter, and open:

```text
exports/neighbourhoods/FUN_1431bc320__1431BC320/pcode-diagnostics.json
```

Locate `CALLIND` at `1431BC350`. Inspect `callTarget.definitionTree` for the fixed `0x50` addition and the stack-backed vptr source. Then inspect `arguments[0].definitionTree`, `arguments[0].stackAddressProvenance`, `callTarget.stackStorageNodes`, and `receiverStorageCorrelation`. The expected receiver result in `indirect-calls.json` is `receiverResolution.status: resolved-stack-object`, `resolutionBasis: stack-object-address-vptr-match`, equal argument and target offsets of `-168`, and `sameStackObject: true`. The call should then progress into initializer/vptr provenance rather than fail at `unresolved-receiver-provenance`.

For the ordered-final-store live test, use the same root and inspect `CALLIND` at `1431BC350`. The minimum acceptable result is either a unique `vptrSelection` or one of the more precise CFG failure statuses above instead of the former undifferentiated multiple-store ambiguity. If `FUN_140d7ce60` has the expected linear high-p-code CFG, the best-case result is `vptrSelection.status: resolved-final-store`, `resolutionBasis: ordered-final-vptr-store`, selected store `140D7CE87`, and selected vtable `TESContainer::vftable`; the call should then resolve slot byte offset `80` (index `10`) and export the resolved internal target's seven-file bundle. These names and addresses are live-test expectations only and are not hard-coded in the script.

`graph.json` preserves its existing direct `edges` array and uses a separate `indirectEdges` array. Each virtual edge preserves the call-site address, receiver-resolution basis, vtable name/address, byte offset, slot index, and resolved target fields. Resolved targets are deduplicated with direct targets by function entry address, so a function bundle is written at most once per run.

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
      ├─ pcode-diagnostics.json
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

For the targeted high-p-code diagnostic live test against `FUN_1431bc320`:

1. Go to `1431BC320` in the analysed `CreationKit.exe` program and confirm the cursor is inside `FUN_1431bc320`.
2. Confirm normal analysis is complete. Do not create or rename symbols for the test.
3. Run `ExportFunctionNeighbourhood.java` and choose the repository's `exports` directory.
4. Open `exports/neighbourhoods/FUN_1431bc320__1431BC320/indirect-calls.json` and locate `CALLIND` at `1431BC350`; verify that it remains identifiable as a vtable call with `vtableByteOffset: 80` and `vtableSlotIndex: 10` for the 8-byte pointer-size program.
5. Inspect `receiverResolution`; the expected basis is `stack-object-address-vptr-match`, with argument and target offsets both `-168`, pointer-compatible sizes, and `sameStackObject: true`.
6. Verify that `callOperation.inputs[0]` is the target and that `arguments[0]` has `pcodeInputIndex: 1`.
7. Inspect `callTarget.definitionTree` and confirm it exposes the target `LOAD`, the fixed `0x50` arithmetic, the inner pointer/vtable load, and all input varnodes with sequence and storage metadata.
8. Confirm every item in `arguments` now has a bounded `definitionTree`. For `arguments[0]`, inspect `stackAddressProvenance`; the expected useful result is `status: resolved-stack-address`, `stackOffset: -168`, and `stackLocation: stack[-0xA8]`.
9. Inspect `callTarget.stackStorageNodes` for a node with `stackOffset: -168`, `beforeConstantOffsetAddition: true`, and the path leading to it. If its defining opcode is `INDIRECT`, verify the nested metadata preserves the sequence/associated instruction near `1431BC331` and reports whether its output uses the same stack storage.
10. Inspect `receiverStorageCorrelation`; the expected success indicators are `status: matched-stack-object`, equal argument and target offsets, and `sameStackObject: true`. Review `receiverComparisons` separately as the older value-identity diagnostics; they may remain false because the object address and stored vptr are different values.
11. Confirm `pcode-diagnostics.json` has schema version 2, `manifest.json` reports `pcodeDiagnosticCount: 1`, and the normal direct-call bundles, `indirect-calls.json`, and graph outputs remain present.
12. Confirm the call no longer has top-level status `unresolved-receiver-provenance`. For the known two-store initializer, the minimum acceptable next result is `resolved-final-store` or a precise CFG status such as `unresolved-branching-vptr-final-state`, `unresolved-no-unique-final-vptr`, or `unresolved-vptr-control-flow`. The best case is top-level `resolved-static-vtable`, a populated virtual edge in `graph.json`, and a seven-file bundle for the resolved target.
13. Review the Ghidra undo/history state if desired; the script starts no transaction and intentionally changes no program state.

If the call remains unresolved, use its precise status and `initializerCandidates` diagnostics to distinguish receiver matching, thunk resolution, parameter-0 recovery, offset-zero store recovery, constant-address recovery, vtable-symbol confidence, and slot lookup failures. Do not update the function register with a virtual target until this live output directly supports it.

Files with the same names are replaced when the same neighbourhood is exported again. The script does not delete old function directories, so a bundle from an earlier run can remain if analysis changes and that function is no longer a direct callee. Use the current manifest and graph as the authoritative membership list for a run.

### Compatibility and known limitations

- The script is written against Ghidra 11.x public program-model and decompiler APIs. The direct depth-1 and earlier virtual-call detection paths have been live-tested. Indirect-call schema version 4, including ordered final-vptr selection for the exact `1431BC350` stack-object receiver path, requires the live test above.
- Direct callees come from Ghidra's `Function.getCalledFunctions` results and therefore depend on call references and defined functions in the current analysis database.
- Thunk resolution depends on Ghidra having marked the forwarding function as a thunk and assigned its thunk target.
- Only simple fixed-offset vtable dispatch is eligible for indirect resolution. All other computed calls are retained as unresolved records rather than being guessed or dropped.
- External/imported functions are represented in relationship metadata but are not decompiled or given context bundles.
- Depth is fixed at 1; there is no recursive or transitive call-tree crawl.
- The constructor-to-vptr path assumes the decompiler either exposes the caller receiver and argument 0 in equivalent supported forms or exposes the exact supported `&stack[X]`/vptr-at-`stack[X]` relationship. It also assumes the resolved initializer's parameter 0 is present in `LocalSymbolMap` and the vptr assignment is a high-p-code `STORE` whose destination is parameter 0 plus constant zero.
- Constant vtable recovery assumes the stored value remains a constant/address varnode (possibly under the supported wrappers) and that the exact address has one unambiguous symbol name containing `vftable` or `vtable`.
- The stack-object receiver rule is not arbitrary stack reconstruction: it accepts one stack address, one stack-backed vptr source, exact offset equality, and pointer-compatible sizes only. The exporter does not follow aliases through memory, PHI/`MULTIEQUAL`, nonconstant pointer arithmetic, helper calls inside the initializer, base-to-derived adjustments, multiple inheritance, or nested constructor chains. It does not infer which of several distinct vptr stores is final.
- The exporter uses decompiler high p-code only for focused virtual-call analysis and unresolved-receiver diagnostics. Stack provenance does not follow memory aliases, `MULTIEQUAL`, nonconstant pointer arithmetic, or unsupported defining operations. Target storage collection reports stack-backed nodes exposed within the same depth-8 tree and may include several nodes or paths. It does not dump every p-code operation, build a general SSA/dataflow framework, infer semantic names, or reconstruct structures or class hierarchies. Diagnostic object IDs are stable only within one exported call, and metadata availability depends on the decompiler's high-p-code objects.
- The export is not atomic. Cancellation or an I/O failure can leave a partially written neighbourhood; the final manifest is written only after function processing completes.

Like the single-function exporter, this script is non-destructive with respect to Ghidra: it starts no transaction and does not rename symbols, change signatures, create labels or comments, apply types, modify memory, or intentionally change analysis state.
