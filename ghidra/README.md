# Ghidra tooling

This directory currently provides seven read-only exporters/analyzers:

- `ExportSelectedFunctionContext.java` exports one selected function.
- `ExportFunctionNeighbourhood.java` exports the selected root function plus the resolved implementations of its direct internal callees. Its traversal depth is fixed at 1. It also performs focused recovery of simple vtable-based indirect calls in the root.
- `ExportCallSignatureEvidence.java` exports focused machine-code and high-p-code call-signature evidence.
- `ExportResourceResolutionEvidence.java` exports focused resource-resolution path evidence.
- `AnalyzeFieldProvenance.java` traces a selected parameter/member offset, ranks same-offset read/write candidates, performs bounded written-value and nested-offset analysis, and exports the strongest candidate functions.
- `AnalyzeClassFieldProvenance.java` discovers a bounded method family for one named class and searches only strong/medium class members for a selected `this`-relative field.
- `ExportFunctionsByAddress.java` exports explicitly addressed functions with exact call sites and is suitable for GUI or headless investigations.

All seven scripts read the current Ghidra analysis database and write plain files beneath a user-selected export root. None starts a transaction or modifies the open program.

## ExportFunctionsByAddress.java

`ExportFunctionsByAddress.java` is a read-only, address-led exporter intended for
small reproducible investigations. It writes one directory per requested
function containing `metadata.json`, `decompiled.c`, `instructions.txt`,
`callers.json`, `callees.json`, and `data-references.json`, plus a run-level
`manifest.json`. Caller and callee records retain exact call-site addresses.

The script takes an output directory followed by one or more addresses. For
example, from the Ghidra installation directory on Windows:

```powershell
support\analyzeHeadless.bat <ghidra-project-dir> StarfieldCK `
  -process CreationKit.exe -readOnly -noanalysis `
  -scriptPath <repository>\ghidra\scripts `
  -postScript ExportFunctionsByAddress.java `
    <output-directory> `
    1415DCFB0 14157F120
```

It reads only the open Ghidra program and writes only the requested filesystem
export. It does not start a transaction or modify symbols, types, comments,
labels, function names, or any other Ghidra project state. Keep the traversal
set small: the script exports exactly the supplied addresses and does not
recursively expand the call graph.

Exact executable and tested-tool provenance for the checked-in evidence is
recorded in [docs/PROVENANCE.md](../docs/PROVENANCE.md). Compatibility notes
below describe the assumptions of each script; they are not a universal
compatibility guarantee.

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

`receiverStorageCorrelation` preserves the detailed evidence for the address/storage relationship-argument 0 is the address of a stack object while the target expression reads contents from the same stack offset. It does not compare the argument value to the vptr value. When stronger receiver normalization is unavailable, the resolver now applies the same conservative exact-offset relationship to establish the receiver and then reuses the existing initializer/constructor provenance path. An `INDIRECT` definition remains supporting side-effect evidence only; it is not proof that an earlier call is a constructor.

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

## ExportCallSignatureEvidence.java

`ExportCallSignatureEvidence.java` is a focused, read-only exporter for reconciling
the indirect call at `FUN_1431bc320` address `0x1431BC350` with resolved target
`FUN_140e0aab0`. It exports the call-site disassembly and low p-code, the complete
high-p-code `CALLIND` inputs and bounded definition trees, Windows x64 argument
mapping, callee entry/signature/parameter storage, bounded first uses of every
callee parameter, direct-caller results, candidate calls from other users of the
same TESContainer initializer, and representative component-vtable slot-10 data.

The default GUI run prompts only for an export root. Headless use accepts:

```text
ExportCallSignatureEvidence.java <export-root> [caller] [call-site] [callee] [window-start] [window-end]
```

All addresses are hexadecimal. Defaults are:

```text
caller       1431BC320
call-site    1431BC350
callee       140E0AAB0
window-start 1431BC320
window-end   1431BC370
```

Example headless invocation against an existing project copy:

```text
analyzeHeadless <project-directory> <project-name> \
  -process CreationKit.exe -readOnly -noanalysis \
  -scriptPath <repository>/ghidra/scripts \
  -postScript ExportCallSignatureEvidence.java <repository>/exports
```

Output is written beneath:

```text
exports/call-signatures/FUN_1431bc320__1431BC320__call_1431BC350/
```

The script reads the current program's listing, symbols, references, function
signatures, decompiler high p-code, and instruction low p-code. It writes only
plain evidence files under the selected export root. It starts no transaction
and does not rename symbols, apply types, change signatures, create labels or
comments, modify memory, or intentionally alter analysis state. Candidate
same-initializer/slot calls remain comparison leads unless receiver/vtable
provenance independently attributes them to `TESContainer`.

## ExportResourceResolutionEvidence.java

`ExportResourceResolutionEvidence.java` is the focused, read-only setup exporter
for the pre-/post-resolution family-container experiment. Static Ghidra does not
contain Creation Kit heap objects, so the script exports an exact runtime
capture contract rather than presenting static memory as a live observation.
It records the copy, resolver-entry, and resolver-return addresses and RVAs;
caller/resolver code; the supported container layout; selector provenance; and
explicitly marked empty runtime-stage templates.

Headless arguments are:

```text
ExportResourceResolutionEvidence.java \
  <export-root> [case-name] [caller] [copy-call] [resolver] [max-depth] \
  [expected-BIOM] [expected-RSGD] [expected-family]
```

Defaults are caller `1431BC320`, copy call `1431BC350`, resolver `140E457B0`,
and maximum recursive depth 8. Example:

```text
analyzeHeadless <scratch-project-directory> StarfieldCK \
  -process CreationKit.exe -readOnly -noanalysis \
  -scriptPath <repository>/ghidra/scripts \
  -postScript ExportResourceResolutionEvidence.java \
  <repository>/exports nickel-linear 1431BC320 1431BC350 140E457B0 8 \
  FrozenNoLife09 FrozenBarrenDefaultRes03 Nickel
```

Output is written to `exports/resource-resolution/<case-name>/`. On the
currently analysed CK build the script resolves the resolver call at
`0x1431BC375` and its return instruction at `0x1431BC37A`. Runtime consumers
must use the exported RVAs plus the live module base.

The stage files begin with `captureStatus: not-captured`; empty entry arrays are
placeholders, not evidence. The script starts no transaction and does not
rename, type, comment, patch, or otherwise modify the Ghidra program.

## AnalyzeFieldProvenance.java

`AnalyzeFieldProvenance.java` is a focused, read-only field-provenance exporter. It is intended for questions such as “where is the pointer later read from parameter 0 plus `0xA0` installed, and how is a nested `+0x20` expression used?” It does not assign semantic names or claim that equal offsets imply equal C++ types.

The script accepts three analysis inputs:

- base parameter index (default `0`);
- field byte offset in decimal or hexadecimal (default `0xA0`);
- optional nested byte offset (default `0x20`; blank disables nested tracing).

It first decompiles the function containing the cursor and identifies `LOAD` operations whose pointer expression structurally reduces to the selected parameter plus the exact field offset. Identity is based on high-p-code varnodes/high variables and supported constant pointer arithmetic, not decompiled variable names. For each root load it records the instruction/sequence address, p-code operation, base and result varnodes, available datatype/high-variable metadata, and a bounded downstream-use chain. Calls in that chain include the p-code argument index and a direct callee when one is defined.

The whole-program candidate pass uses instruction scalars only as a performance prefilter. A candidate is emitted only when high p-code then proves a `LOAD` or `STORE` address of the form parameter 0 plus the exact selected offset. This avoids treating every unrelated `0xA0` constant as a class match.

Candidate relevance is ranked as follows:

- 60 points when the function's full symbol or namespace contains `ResourceViewWidget`;
- 40 points when it is the selected root or a direct caller/callee of the root;
- 30 points for at least one direct write to the selected field;
- 10 points for the required parameter-0 structural match.

Scores of 70 or more are `high`, 40–69 are `medium`, and lower scores are `low`. The score is evidence prioritisation, not proof that all candidates share one object type. Each candidate includes the reasons for its score and whether it is already in known ResourceViewWidget context.

Writes are distinguished directly from reads by high-p-code `STORE` versus `LOAD`. Null constants are retained as `clear`; call returns and constant addresses are classified as likely `initialization`; parameter or fixed-field copies are `assignment`; unsupported forms remain `unknown`. Written-value provenance is bounded to eight operations and supports:

- direct constants or program addresses, with symbols when available;
- function parameters;
- direct or indirect call return values, plus same-function calls that consume that value before the field store as bounded initializer candidates;
- loads from a fixed offset of parameter 0;
- explicit unresolved status for `MULTIEQUAL`, unsupported operations, missing definitions, and the depth limit.

This is diagnostic classification, not constructor or ownership proof.

Each ranked candidate also records its full symbol name, direct callers, direct callees, and referenced strings. Strong candidate functions receive the normal seven-file bundle for fuller inspection.

When a nested offset is supplied, the root trace follows uses of the loaded field value through copies, casts, fixed pointer arithmetic, and loads. It marks the exact nested-offset expression and downstream operations derived from it, including call arguments. Candidate writers that copy a function parameter into the field are also checked for same-function accesses at that parameter plus the nested offset. The script does not search a heap graph or infer aliases across arbitrary calls.

### Usage and live test

1. Open the analysed `CreationKit.exe` program in CodeBrowser and allow normal analysis to complete.
2. Go to `1431BC320`, confirm the cursor is inside `FUN_1431bc320`, and run `AnalyzeFieldProvenance.java` from Script Manager.
3. Enter base parameter index `0`, field offset `0xA0`, and nested offset `0x20`.
4. Choose the repository's `exports` directory. Do not choose Ghidra project storage.
5. Open `exports/field-provenance/FUN_1431bc320__1431BC320__field_A0/root-access.json` and confirm an exact field load is identified.
6. Inspect its downstream uses for the `loaded + 0x20` expression and the call argument that consumes it.
7. Review `candidate-writes.json` before `candidate-accesses.json`; high-confidence writer/initializer candidates should appear first. If no writer can be tied confidently, the files preserve that outcome rather than guessing.
8. Inspect `provenance.json` and the bounded candidate bundles under `functions/`.
9. Confirm the Ghidra undo/history state is unchanged; the script starts no transaction and intentionally changes no analysis state.

The minimum successful result is an exact root access, exported same-field candidates, and either a ranked writer/initializer or explicit evidence that no writer could be tied confidently. The best case identifies the installed object's initializer/type evidence, structurally explains the nested `+0x20` component, and exposes resource-specific upstream data. Those best-case interpretations must come from live evidence; they are not encoded in the script.

### Output structure

```text
exports/
└─ field-provenance/
   └─ FUN_1431bc320__1431BC320__field_A0/
      ├─ manifest.json
      ├─ root-access.json
      ├─ candidate-accesses.json
      ├─ candidate-writes.json
      ├─ provenance.json
      └─ functions/
         └─ <candidate-name>__<address>/
            ├─ metadata.json
            ├─ decompiled.c
            ├─ callers.json
            ├─ callees.json
            ├─ strings.json
            ├─ globals.json
            └─ constants.json
```

Candidate bundles are deduplicated by function entry and limited to the strongest ten writer functions, or the strongest ten access functions when no writer exists. Files with the same names are replaced on a repeat run; unrelated old candidate directories are not deleted. Treat the current manifest and candidate arrays as authoritative membership for that run.

### Known limitations

- The script uses public decompiler/program-model APIs, compiles against Ghidra 12.1.2, and requires completed normal analysis.
- Instruction-scalar prefiltering can miss a compiler form that does not retain the requested byte offset as a scalar operand.
- Same-field candidates require a parameter-0 expression but do not prove a shared class. Symbol/namespace and direct call-family context improve ranking only.
- The bounded trace supports simple wrappers, fixed pointer arithmetic, loads, call returns, parameters, and constants. It does not implement arbitrary alias analysis, heap recovery, symbolic execution, class reconstruction, or recursive call tracing.
- Nested-component evidence is structural. Passing `object + 0x20` to a known method is evidence, but is not by itself enough to assign a type.
- Decompiler high-variable metadata depends on the current analysis database. Decompiled names are exported only as diagnostics and are never used as identity proof.
- Whole-program decompilation can take time on a large program, though the scalar prefilter avoids decompiling functions without the selected offset.
- Export is not atomic; cancellation or an I/O failure can leave partial files. The final manifest is written last.

Like the other exporters, this script only reads Ghidra analysis state and writes external files. It starts no transaction and does not rename symbols/functions, create labels/comments, change signatures/types, or modify memory.

## AnalyzeClassFieldProvenance.java

`AnalyzeClassFieldProvenance.java` is the focused follow-up to the whole-program offset scan. It answers a narrower question: which functions have independent evidence tying them to a named class, and which of those functions access one exact `this`-relative field? Offset reuse, nearby addresses, generic Qt relationships, and raw caller proximity do not establish class membership.

The initial target and defaults are:

```text
class name: ResourceViewWidget
field offset: 0xA0
nested offset: 0x20
exact root anchor: ResourceViewWidget::OnApplySeed
```

The class name, field offset, and optional nested offset are prompted at run time. The exact root-anchor suffix is deliberately fixed to `::OnApplySeed` for this focused iteration. If the exact full symbol does not resolve, the export records `anchor-unresolved`; it never substitutes a similarly named symbol.

### Anchor discovery and confidence

The script scans the current symbol table for symbols containing the supplied class text and separates:

- exact class-qualified functions;
- vtable/vftable candidates;
- RTTI-related candidates;
- the exact `ResourceViewWidget::OnApplySeed` method anchor;
- functions structurally confirmed to write a discovered class vtable through parameter 0 at any recoverable constant offset.

Every candidate method has one of three confidence levels:

- `strong`: exact class-qualified symbol, direct vtable slot, confirmed class-vtable writer, or a Ghidra-defined thunk/implementation relationship to one of those;
- `medium`: a bounded outbound call from a strong anchor or receiver-family helper has high-p-code evidence that the unchanged parameter-0 receiver flows as callee argument 0;
- `weak`: supporting context only. Weak evidence never establishes membership and weak candidates are not searched for the field.

This model intentionally excludes the previous global rule that treated structural parameter-0 `+0xA0` matches as possible class evidence.

### Vtable enumeration

For each symbol whose full name contains both the exact class text and `vtable` or `vftable`, the script reads pointer-sized entries beginning at the symbol address. It records the slot index, byte offset, slot address, raw pointer, directly defined function, thunk hop count, and resolved implementation.

Walking stops at the first null, unreadable, overflowed, or non-function slot, or after 256 slots. The bound and stop reason are exported. Each matching named vtable is walked independently. Slots record internal/external status, thunk resolution, and duplicate resolved implementations. The script does not continue through arbitrary adjacent data or infer multiple-inheritance semantics.

### Vtable xrefs and structural vptr stores

For every discovered vtable, `vtable-xrefs.json` records all Ghidra references and classifies them as `direct data reference`, `LOAD/use`, `STORE source`, `constant/address materialization`, `vptr-store`, or `other`. Code references include their containing function, instruction, Ghidra reference type, matching high-p-code operations, whether the vtable reaches a memory store, the destination expression, and receiver evidence.

A `vptr-store` requires high-p-code evidence that the stored vtable value reaches a destination reducible to:

```text
parameter 0 + constant offset
```

Both zero and nonzero offsets are retained. Stores to a nonzero offset can support a secondary-subobject hypothesis, but the script does not assign a base-class identity or reconstruct an inheritance layout.

The stored value does not need to expose the vtable address directly at the `STORE`. Before classification, the analyzer resolves the value backward through at most eight non-branching high-p-code definitions. Supported forms are `COPY`, `CAST`, `INT_ZEXT`, `INT_SEXT`, constant-form `PTRSUB`, constant-form `PTRADD`, and `INT_ADD` with one constant operand, including the common address-materialization form in which a zero base is combined with the vtable address. The final value must resolve uniquely to one discovered concrete class vtable and the STORE input must match the program pointer size.

Resolution stops explicitly at `MULTIEQUAL`, `LOAD`, call returns, nonconstant arithmetic, missing or unsupported definitions, cycles, or the depth bound. This is bounded value propagation, not alias analysis or symbolic execution. Each accepted store retains the original xref address plus a separate `storeAddress`, `valueResolutionBasis`, `valueDefinitionPath`, and resolved STORE operation.

### Constructor/destructor candidates

References to each concrete class-vtable address are used as a prefilter. A function becomes a strong vtable-writer candidate only when high p-code proves:

```text
STORE ResourceViewWidget vtable address -> parameter 0 + constant offset
```

`lifecycle-candidates.json` records all class-vptr stores in operation order, their receiver offsets, surrounding class-vptr stores, callers, callees, return behavior, receiver-relative store count, and allocation context. It also reports `primaryVptrOffset` when offset zero is observed and collects every observed nonzero offset in `secondaryVptrOffsets`; those fields describe stores, not exact base-class identity. Classification is conservative: deallocation or teardown structure combined with vptr evidence can produce `destructor-like`; allocation context plus a non-late vptr store, or receiver return plus additional member stores, can produce `constructor-like`; otherwise a structural installer is `lifecycle-helper` or `unknown`. Neither a name hint nor store position is sufficient by itself, and no classification is presented as recovered C++ type information.

### Receiver-preserving method family

Starting from exact class symbols, internal vtable functions, thunk targets, and structural lifecycle candidates, the script follows outbound direct calls for at most two hops. A callee enters with `medium` confidence only when the caller passes its structurally unchanged parameter-0 receiver as callee argument 0 and the callee is internal code. `receiver-family.json` records the source function, call site, depth, receiver argument index, and the explicit caveat that this is receiver-family provenance rather than proof of literal C++ membership.

`FUN_1431bc320` is independently recorded in `class-anchors.json`, including function-pointer references when available. It joins the class family only if the same bounded receiver-preserving rules connect it; otherwise the negative connection is preserved. This provides bounded callback evidence without general Qt meta-object reconstruction.

### Class-scoped field matching and provenance

Only strong and medium method candidates are decompiled for field analysis. A read or write is accepted only when high-p-code pointer arithmetic reduces structurally to:

```text
parameter 0 + exact requested field offset
```

`LOAD` and `STORE` are reported separately. Writes are conservatively classified as:

- `clear/null` for a direct zero constant;
- `initialization` for a direct call return;
- `assignment` for a function parameter;
- `copy` for a load expression;
- `unknown` otherwise.

The bounded written-value trace has a maximum depth of eight. It supports constants/program addresses and symbols, function parameters, direct or indirect call returns, fixed-offset loads, and simple constant address arithmetic. Allocator/factory-looking names are emitted only as name-based hints. `MULTIEQUAL`, cycles, unsupported operations, and the depth limit are explicit unresolved states; the script does not choose branches or perform alias analysis.

For a read from the selected field, downstream high-p-code uses are followed through simple wrappers, loads, and fixed pointer arithmetic to identify the requested nested offset. For a write sourced directly from another function parameter, same-function loads/stores at that parameter plus the nested offset are also recorded. Calls consuming the derived component include argument indices and direct callee metadata where available. This is structural evidence only and does not force the nested component to be `TESContainer` or any other type.

### Member-object usage and constructor callbacks

The same run now performs a focused second stage for the object loaded from the selected field. Each structural `LOAD [parameter 0 + offset]` in the strong/medium class family and constructor callback family gets a bounded use tree in `member-A0-object-usage.json`. The record retains the load address, output varnode, HighVariable, decompiler datatype, null checks, arithmetic, call argument positions and adjustments, field reads/writes through the loaded object, direct/thunk-resolved callees, and recoverable indirect vtable slot metadata. Use expansion stops at depth eight, cycles, merged values, and non-alias-producing operations.

For every structurally `constructor-like` lifecycle function, the analyzer examines call arguments for internal function addresses that occur after a proven ResourceViewWidget receiver/context argument. These conservative candidates are written to `callback-bindings.json`, including the registration call, source-object varnode, connection API when direct, raw and thunk-resolved callback, receiver/context positions and adjustments, and bounded symbol/string context. This rule is designed to separate a signal function pointer occurring before the receiver from a slot/callback function pointer occurring after it; opaque metadata-table and load-derived callbacks are not decoded.

Each resolved internal callback seeds an independent callback family. `callback-family.json` follows direct internal calls for at most two hops and admits a helper only when callback parameter 0 is passed unchanged as callee argument 0. `callback-A0-accesses.json` then distinguishes:

- pointer assignment and pointer clear/null at `this+0xA0`;
- a read of the pointer;
- calls on or with the loaded object;
- field reads and writes through the loaded object;
- uses of the requested nested offset.

The receiver rule is deliberately conservative and exported as evidence. It does not prove that every callback ABI exposes ResourceViewWidget as parameter 0.

### Object mutation, type evidence, and `obj+0x20`

`object-mutations.json` treats a `STORE` through the loaded object as a mutation. A call receiving the object is recorded separately as an `unknown mutation candidate`, because high p-code alone does not establish constness or side effects. This keeps pointer assignment distinct from mutation of the already-referenced object.

`object-plus20-usage.json` selects operations whose address, call receiver, argument adjustment, or recovered indirect-dispatch receiver is structurally `obj+0x20`. It reports reads, writes, direct or indirect calls, vptr loads and slot offsets where recoverable, but does not assign a type to the embedded component.

`type-evidence.json` scores evidence independently of the decompiler guess. A HighVariable datatype such as `QTreeWidget *` is weak. A resolved API/constructor/destructor containing the concrete Qt type is strong; a compatible `QAbstractItemView`, `QWidget`, or `QObject` API is medium and supports only the base relationship. The script never applies the proposed type. `resource-signals.json` scans the focused functions and one internal call edge for BIOM, RSGD, PNDT, RSCS, TESLevItem, TESContainer, resource text, and the two registered resource-path functions. A generic TESContainer match is explicitly not sufficient by itself.

### Output structure

For the default target, the output is:

```text
exports/
└─ class-provenance/
   └─ ResourceViewWidget/
      ├─ manifest.json
      ├─ class-anchors.json
      ├─ vtable-xrefs.json
      ├─ lifecycle-candidates.json
      ├─ class-methods.json
      ├─ receiver-family.json
      ├─ field-A0-accesses.json
      ├─ field-A0-writes.json
      ├─ provenance.json
      ├─ member-A0-object-usage.json
      ├─ callback-bindings.json
      ├─ callback-family.json
      ├─ callback-A0-accesses.json
      ├─ object-mutations.json
      ├─ object-plus20-usage.json
      ├─ type-evidence.json
      ├─ resource-signals.json
      └─ functions/
         └─ <function-name>__<entry-address>/
            ├─ metadata.json
            ├─ decompiled.c
            ├─ callers.json
            ├─ callees.json
            ├─ strings.json
            ├─ globals.json
            └─ constants.json
```

`class-anchors.json` preserves all matching symbols, concrete vtable candidates and bounded slots, RTTI candidates, exact method-anchor status, the independent `FUN_1431bc320` status, and lifecycle summaries. `vtable-xrefs.json` contains per-vtable xrefs and explicit negative results. `lifecycle-candidates.json` contains structural stores and conservative role classifications. `class-methods.json` contains confidence and membership evidence; `receiver-family.json` isolates bounded nonvirtual helpers. The access file contains only strong/medium candidates. The writes file explicitly contains `negativeResult: no-class-scoped-writer-found` when appropriate. `provenance.json` collects detailed written-value traces. Every new focused report likewise preserves an explicit negative result rather than silently omitting an empty discovery.

Every internal function that directly references a discovered concrete class-vtable address is exported first. The ordinary class-family selection is capped at 30 functions. Focused member-object readers, constructor callbacks, callback-family functions, internal loaded-object callees, and the structurally rediscovered acceptance target `FUN_1431ef760` plus its resolved internal thunk target are then forced and deduplicated, so the actual total can exceed 30. `manifest.json` records both the configured ordinary cap and actual total. External/inherited Qt functions are not exported. Their call metadata remains in the JSON reports.

### Exact live test

1. Open the normally analysed `CreationKit.exe` program in CodeBrowser.
2. Go to `ResourceViewWidget::OnApplySeed` if its exact symbol is available. Otherwise go to `FUN_1431bc320` at `1431BC320`, which is the known direct downstream context; the script still requires and separately verifies the exact named anchor.
3. Run `AnalyzeClassFieldProvenance.java` from Script Manager.
4. Enter `ResourceViewWidget`, `0xA0`, and `0x20` at the three prompts.
5. Choose the repository's `exports` directory. Do not choose Ghidra project storage.
6. Inspect `exports/class-provenance/ResourceViewWidget/class-anchors.json`. Confirm that the discovered anchors include `0x148B7CFB0` and `0x148B7D170`, then review their slot counts, stop reasons, internal/external flags, thunks, and duplicates.
7. Inspect `vtable-xrefs.json`; record the xref and structural-vptr-store count for each vtable. A zero count must appear as an explicit negative result.
8. Confirm `FUN_1431e7d20` has recovered stores for the two concrete vtables at receiver offsets `0x0` and `0x10`. Verify that each record retains its xref address, resolved store address, and value-definition path.
9. Inspect `lifecycle-candidates.json`; verify every classification against its vptr-store order, receiver offsets, callers, callees, allocation evidence, and limitations. `FUN_1431e7d20` is expected to become destructor-like from structural teardown evidence, but this result is not hard-coded. Treat offset `0x10` only as secondary-subobject evidence.
10. Confirm both direct internal xref functions, `FUN_1431e7d20` and `FUN_1431e29f0`, are listed in the manifest's forced-xref export fields and have function bundles.
11. Inspect `class-methods.json` and `receiver-family.json`; confirm that searched functions are `strong` or `medium`, receiver helpers have depth at most 2, and `FUN_1431bc320` is either structurally connected or explicitly preserved as unconnected.
12. Inspect `field-A0-writes.json` before `field-A0-accesses.json`, then review `provenance.json`. The `+0xA0` matcher is unchanged; a negative result remains valid.
13. Inspect `member-A0-object-usage.json`. Locate the structurally rediscovered `FUN_1431ef760` entry, verify each load address/HighVariable/datatype, and follow the depth-bounded uses. Confirm `manifest.json.memberUsageAcceptance` reports whether the known acceptance name was rediscovered without using it for discovery. Confirm its function bundle and any internal thunk target bundle exist.
14. Inspect `callback-bindings.json`. Verify the constructor is `FUN_1431e29f0` from lifecycle evidence, then check source-object, receiver/context, connection call, raw callback, resolved callback, and evidence. Confirm the observed callback family around `thunk_FUN_1431f10b0`, `thunk_FUN_1431f0fe0`, and any text-change callback is either rediscovered structurally or absent with an explicit negative result; those names are not discovery seeds.
15. Inspect `callback-family.json`; verify depth never exceeds 2 and every helper has unchanged receiver evidence. Then inspect `callback-A0-accesses.json`, explicitly separating pointer assignment/clear from loaded-object calls and field mutations.
16. Inspect `object-mutations.json`. Treat stores as observed mutations and calls only as candidates. Inspect `object-plus20-usage.json` for `obj+0x20` reads/writes/calls, receiver adjustments, vptr loads, and recovered slots.
17. Inspect `type-evidence.json`. Do not promote `QTreeWidget *` beyond weak unless an independent concrete Qt API, constructor/destructor, RTTI, or vtable relationship is present. Inspect `resource-signals.json` and validate every resource-related match against its referenced symbol/string/callee; one generic TESContainer match is insufficient.
18. Confirm `manifest.json` reports schema version 3, `readOnly: true`, the 256-slot vtable limit, receiver/callback depth 2, the 30-function configured cap plus documented forced-export exceptions, report counts, and explicit negative results where applicable.
19. Confirm the Ghidra undo/history state is unchanged. The script starts no transaction and intentionally changes no analysis state.

The minimum successful live outcome for this iteration is: `FUN_1431ef760` is structurally rediscovered and exported with a recorded `+0xA0` use tree; constructor-wired internal callbacks are enumerated; callback-family expansion completes to depth two; callback-family `+0xA0` accesses are reported; concrete type evidence is separated from the weak Ghidra datatype; and `obj+0x20` use is recorded when observed. The best case is independent identification of the member-object type, a constructor callback that mutates or populates it, structural identification of the `+0x20` component, and a multi-signal path into resource-specific container/list generation.

### Known limitations

- The script targets Ghidra's public program-model and decompiler APIs and depends on completed analysis, current symbols, references, defined functions, and high p-code.
- A concrete vtable cannot be inferred when it is unnamed; RTTI is recorded as supporting evidence but is not fully reconstructed.
- The vtable walk assumes the named address is the first method slot and stops conservatively at the first invalid region.
- Receiver-flow expansion is outbound-only and bounded to depth two; it is not recursive class reconstruction.
- Constructor callback extraction sees only function-pointer arguments that reduce to defined internal addresses and follow a proven receiver/context argument. It does not decode arbitrary Qt metadata or heap-allocated functors.
- Callback-family expansion assumes parameter 0 carries ResourceViewWidget and deliberately rejects adjusted, merged, indirect, or otherwise ambiguous receiver flow.
- Object use trees follow wrappers and constant pointer arithmetic only. Calls are mutation candidates unless a write is independently recovered.
- Indirect vtable recovery can report a slot and receiver adjustment without identifying the concrete runtime vtable/type.
- Resource-signal scanning is name/string/type based and bounded to one internal call edge; it is a prioritization aid rather than semantic proof.
- Vtable reference prefiltering can miss a compiler/decompiler form whose reference is absent from the current database.
- Allocation, cleanup, and deallocation names are diagnostic inputs to conservative lifecycle classification; ownership and exact C++ semantics remain unresolved.
- Nested analysis is bounded and same-function only. It does not traverse a heap graph or arbitrary aliases across calls.
- Export is not atomic; cancellation or an I/O failure can leave partial files, while the manifest is written last.

Like the other exporters, this script only reads Ghidra analysis state and writes external files. It starts no transaction and does not rename symbols/functions, create labels/comments, change signatures/types, apply types, or modify memory.
