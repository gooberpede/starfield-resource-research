// Export bounded, read-only provenance evidence for a selected object's member field.
// @category Starfield Research
// @keybinding
// @menupath
// @toolbar

import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.IdentityHashMap;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.TreeSet;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileOptions;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.pcode.HighFunction;
import ghidra.program.model.pcode.HighParam;
import ghidra.program.model.pcode.HighVariable;
import ghidra.program.model.pcode.LocalSymbolMap;
import ghidra.program.model.pcode.PcodeOp;
import ghidra.program.model.pcode.Varnode;
import ghidra.program.model.scalar.Scalar;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.Symbol;
import ghidra.util.exception.CancelledException;

public class AnalyzeFieldProvenance extends GhidraScript {

    private static final int DECOMPILE_TIMEOUT_SECONDS = 60;
    private static final int MAX_TRACE_DEPTH = 8;
    private static final int MAX_EXPORTED_FUNCTIONS = 10;
    private static final Gson JSON = new GsonBuilder()
        .setPrettyPrinting().disableHtmlEscaping().serializeNulls().create();

    private DecompInterface decompiler;

    @Override
    public void run() throws Exception {
        if (currentProgram == null || currentAddress == null) {
            printerr("Open a program and place the cursor inside the root function.");
            return;
        }
        Function root = currentProgram.getFunctionManager().getFunctionContaining(currentAddress);
        if (root == null) {
            printerr("The cursor is not inside a defined function: " + currentAddress);
            return;
        }

        int baseParameterIndex = parseNonNegativeInt(askString(
            "Base parameter index", "Parameter index (0 is the usual C++ this parameter)", "0"));
        long fieldOffset = parseOffset(askString(
            "Field byte offset", "Field offset in decimal or hexadecimal", "0xA0"));
        String nestedText = askString(
            "Nested byte offset", "Optional nested offset; leave blank to disable", "0x20").trim();
        Long nestedOffset = nestedText.isEmpty() ? null : parseOffset(nestedText);

        File chosenRoot = askDirectory(
            "Choose export root (for example, the repository's exports directory)", "Export");
        Path exportRoot = chosenRoot.toPath().toAbsolutePath().normalize();
        if (isInsideGhidraProjectStorage(exportRoot)) {
            printerr("The export root must be outside the Ghidra project storage: " + exportRoot);
            return;
        }

        Path output = exportRoot.resolve("field-provenance").resolve(
            safeName(root) + "__field_" + unsignedHex(fieldOffset).substring(2));
        Files.createDirectories(output.resolve("functions"));
        Instant generatedAt = Instant.now();

        decompiler = new DecompInterface();
        try {
            DecompileOptions options = new DecompileOptions();
            options.grabFromProgram(currentProgram);
            decompiler.setOptions(options);
            if (!decompiler.openProgram(currentProgram)) {
                printerr("Decompiler could not open the current program: " + decompiler.getLastMessage());
                return;
            }

            Decompilation rootDecompilation = decompile(root);
            RootResult rootResult = analyzeRoot(
                root, rootDecompilation, baseParameterIndex, fieldOffset, nestedOffset);
            Set<String> rootContext = collectRootContext(root);
            List<AccessCandidate> candidates = scanProgram(
                root, rootContext, fieldOffset, nestedOffset);
            Collections.sort(candidates, AccessCandidate.ORDER);

            List<AccessCandidate> writes = new ArrayList<>();
            List<Map<String, Object>> provenance = new ArrayList<>();
            for (AccessCandidate candidate : candidates) {
                if (candidate.hasWrite()) {
                    writes.add(candidate);
                    for (Map<String, Object> record : candidate.provenanceRecords) {
                        Map<String, Object> enriched = new LinkedHashMap<>(record);
                        enriched.put("relevanceScore", candidate.score);
                        enriched.put("confidence", candidate.confidence);
                        enriched.put("knownResourceViewWidgetContext", candidate.knownResourceViewWidgetContext);
                        enriched.put("receiverEvidence", candidate.receiverEvidence);
                        enriched.put("callers", candidate.callers);
                        enriched.put("callees", candidate.callees);
                        enriched.put("referencedStrings", candidate.referencedStrings);
                        provenance.add(enriched);
                    }
                }
            }

            List<Function> exported = exportCandidates(
                writes.isEmpty() ? candidates : writes,
                output.resolve("functions"), generatedAt);

            write(output.resolve("root-access.json"), json(rootResult.toMap(
                root, baseParameterIndex, fieldOffset, nestedOffset)));
            write(output.resolve("candidate-accesses.json"), json(candidateDocument(
                "All structurally matched parameter-0 field accesses, ranked by ResourceViewWidget/context evidence.",
                candidates)));
            write(output.resolve("candidate-writes.json"), json(writeDocument(provenance)));
            write(output.resolve("provenance.json"), json(provenanceDocument(provenance)));
            write(output.resolve("manifest.json"), json(manifest(
                root, baseParameterIndex, fieldOffset, nestedOffset, generatedAt,
                rootResult, candidates, writes, exported)));

            println("Exported field provenance for " + root.getName() + " to " + output);
            if (!rootResult.found) {
                printerr("The exact root field load was not identified; review root-access.json diagnostics.");
            }
            if (writes.isEmpty()) {
                printerr("No candidate write could be tied confidently; ranked reads remain in candidate-accesses.json.");
            }
        }
        finally {
            if (decompiler != null) {
                decompiler.dispose();
            }
        }
    }

    private RootResult analyzeRoot(Function root, Decompilation decompilation,
            int parameterIndex, long fieldOffset, Long nestedOffset) throws CancelledException {
        RootResult result = new RootResult();
        if (!decompilation.completed || decompilation.highFunction == null) {
            result.error = decompilation.error;
            return result;
        }
        HighParam parameter = getHighParamSafely(decompilation.highFunction, parameterIndex);
        if (parameter == null) {
            result.error = "Requested base parameter " + parameterIndex +
                " is unavailable; decompiler LocalSymbolMap contains " +
                getHighParamCount(decompilation.highFunction) + " parameters.";
            return result;
        }
        if (parameter.getRepresentative() == null) {
            result.error = "Decompiler high p-code exposed no representative for parameter " + parameterIndex + ".";
            return result;
        }
        result.baseParameter = varnode(parameter.getRepresentative());

        Iterator<? extends PcodeOp> operations = decompilation.highFunction.getPcodeOps();
        while (operations.hasNext()) {
            monitor.checkCancelled();
            PcodeOp operation = operations.next();
            if (operation.getOpcode() != PcodeOp.LOAD || operation.getNumInputs() < 2) {
                continue;
            }
            Long offset = offsetFromBase(operation.getInput(1), parameter.getRepresentative(), 0);
            if (offset == null || offset.longValue() != fieldOffset) {
                continue;
            }
            result.found = true;
            Map<String, Object> access = operationRecord(operation, "read", fieldOffset);
            access.put("fieldLoadExpression", "parameter[" + parameterIndex + "] + " + unsignedHex(fieldOffset));
            access.put("baseVarnode", varnode(parameter.getRepresentative()));
            access.put("loadResultVarnode", varnode(operation.getOutput()));
            access.put("nestedExpression", nestedOffset == null
                ? null
                : "loaded-field-value + " + unsignedHex(nestedOffset));
            access.put("downstreamUses", traceUses(operation.getOutput(), nestedOffset));
            result.accesses.add(access);
        }
        if (!result.found) {
            result.error = "No LOAD pointer expression reduced to the selected parameter plus the exact field offset.";
        }
        return result;
    }

    private List<AccessCandidate> scanProgram(Function root, Set<String> rootContext,
            long fieldOffset, Long nestedOffset) throws Exception {
        List<AccessCandidate> result = new ArrayList<>();
        FunctionIterator functions = currentProgram.getFunctionManager().getFunctions(true);
        int inspected = 0;
        int skippedWithoutParameterZero = 0;
        while (functions.hasNext()) {
            monitor.checkCancelled();
            Function function = functions.next();
            if (function.isExternal() || function.getBody() == null || function.getBody().isEmpty() ||
                    !hasInstructionScalar(function, fieldOffset)) {
                continue;
            }
            inspected++;
            monitor.setMessage("Field provenance: decompiling candidate " + inspected + " (" + function.getName() + ")");
            Decompilation decompilation = decompile(function);
            if (!decompilation.completed || decompilation.highFunction == null) {
                continue;
            }
            HighParam receiver = getHighParamSafely(decompilation.highFunction, 0);
            if (receiver == null) {
                skippedWithoutParameterZero++;
                continue;
            }
            if (receiver.getRepresentative() == null) {
                continue;
            }
            AccessCandidate candidate = inspectFunction(
                function, decompilation.highFunction, receiver.getRepresentative(), fieldOffset, nestedOffset);
            if (!candidate.accesses.isEmpty()) {
                rank(candidate, root, rootContext);
                enrichCandidateContext(candidate);
                result.add(candidate);
            }
        }
        println("High-p-code inspected " + inspected + " functions containing scalar " + unsignedHex(fieldOffset) + ".");
        println("Skipped " + skippedWithoutParameterZero +
            " scalar-prefilter candidates without decompiler parameter 0.");
        return result;
    }

    private AccessCandidate inspectFunction(Function function, HighFunction highFunction,
            Varnode receiver, long fieldOffset, Long nestedOffset) throws CancelledException {
        AccessCandidate candidate = new AccessCandidate(function);
        Iterator<? extends PcodeOp> operations = highFunction.getPcodeOps();
        while (operations.hasNext()) {
            monitor.checkCancelled();
            PcodeOp operation = operations.next();
            if (operation.getOpcode() == PcodeOp.LOAD && operation.getNumInputs() >= 2) {
                Long offset = offsetFromBase(operation.getInput(1), receiver, 0);
                if (offset != null && offset.longValue() == fieldOffset) {
                    Map<String, Object> access = operationRecord(operation, "read", fieldOffset);
                    access.put("receiverEvidence", "LOAD address reduces structurally to parameter 0 plus the exact offset.");
                    access.put("downstreamUses", traceUses(operation.getOutput(), nestedOffset));
                    candidate.accesses.add(access);
                    if (nestedOffset != null) {
                        candidate.nestedAccesses.addAll(findNestedUses(operation.getOutput(), nestedOffset));
                    }
                }
            }
            else if (operation.getOpcode() == PcodeOp.STORE && operation.getNumInputs() >= 3) {
                Long offset = offsetFromBase(operation.getInput(1), receiver, 0);
                if (offset != null && offset.longValue() == fieldOffset) {
                    Map<String, Object> access = operationRecord(operation, "write", fieldOffset);
                    Map<String, Object> value = traceWrittenValue(
                        highFunction, operation, operation.getInput(2), receiver, 0);
                    access.put("receiverEvidence", "STORE address reduces structurally to parameter 0 plus the exact offset.");
                    access.put("writtenValue", value);
                    access.put("writeKind", writeKind(operation.getInput(2), value));
                    candidate.accesses.add(access);

                    Map<String, Object> provenance = new LinkedHashMap<>();
                    provenance.put("functionName", function.getName());
                    provenance.put("functionAddress", address(function));
                    provenance.put("instructionAddress", sequenceAddress(operation));
                    provenance.put("fieldOffset", fieldOffset);
                    provenance.put("writeKind", access.get("writeKind"));
                    provenance.put("writtenValue", value);
                    provenance.put("provenanceStatus", value.get("status"));
                    provenance.put("evidence", value.get("evidence"));
                    candidate.provenanceRecords.add(provenance);

                    Integer sourceParameter = (Integer) value.get("sourceParameterIndex");
                    if (sourceParameter != null && nestedOffset != null) {
                        HighParam source = getHighParamSafely(highFunction, sourceParameter);
                        if (source != null && source.getRepresentative() != null) {
                            candidate.nestedAccesses.addAll(findOffsetOperations(
                                highFunction, source.getRepresentative(), nestedOffset,
                                "written-value parameter " + sourceParameter));
                        }
                    }
                }
            }
        }
        return candidate;
    }

    private List<Map<String, Object>> traceUses(Varnode start, Long nestedOffset) {
        List<Map<String, Object>> result = new ArrayList<>();
        Set<Varnode> visited = Collections.newSetFromMap(new IdentityHashMap<Varnode, Boolean>());
        traceUses(start, nestedOffset, result, visited, 0, false);
        return result;
    }

    private void traceUses(Varnode value, Long nestedOffset, List<Map<String, Object>> result,
            Set<Varnode> visited, int depth, boolean derivedFromNested) {
        if (value == null || depth > MAX_TRACE_DEPTH || !visited.add(value)) {
            return;
        }
        Iterator<PcodeOp> descendants = value.getDescendants();
        while (descendants.hasNext()) {
            PcodeOp use = descendants.next();
            Map<String, Object> record = pcodeUse(use, value);
            Long relativeOffset = expressionOffsetUsing(use, value);
            boolean matchedNested = false;
            if (relativeOffset != null) {
                record.put("relativeOffset", relativeOffset);
                record.put("relativeOffsetHex", unsignedHex(relativeOffset));
                matchedNested = nestedOffset != null && relativeOffset.equals(nestedOffset);
                record.put("matchesNestedOffset", matchedNested);
            }
            record.put("derivedFromMatchedNestedExpression", derivedFromNested);
            result.add(record);
            if (use.getOutput() != null && isTraceable(use.getOpcode())) {
                traceUses(use.getOutput(), nestedOffset, result, visited, depth + 1,
                    derivedFromNested || matchedNested);
            }
        }
    }

    private List<Map<String, Object>> findNestedUses(Varnode loaded, long nestedOffset) {
        List<Map<String, Object>> uses = traceUses(loaded, nestedOffset);
        List<Map<String, Object>> result = new ArrayList<>();
        for (Map<String, Object> use : uses) {
            if (Boolean.TRUE.equals(use.get("matchesNestedOffset")) ||
                    Boolean.TRUE.equals(use.get("derivedFromMatchedNestedExpression"))) {
                result.add(use);
            }
        }
        return result;
    }

    private List<Map<String, Object>> findOffsetOperations(HighFunction highFunction,
            Varnode base, long offset, String basis) {
        List<Map<String, Object>> result = new ArrayList<>();
        Iterator<? extends PcodeOp> operations = highFunction.getPcodeOps();
        while (operations.hasNext()) {
            PcodeOp operation = operations.next();
            if ((operation.getOpcode() == PcodeOp.LOAD && operation.getNumInputs() >= 2) ||
                    (operation.getOpcode() == PcodeOp.STORE && operation.getNumInputs() >= 3)) {
                Long matched = offsetFromBase(operation.getInput(1), base, 0);
                if (matched != null && matched.longValue() == offset) {
                    Map<String, Object> record = operationRecord(operation,
                        operation.getOpcode() == PcodeOp.LOAD ? "read" : "write", offset);
                    record.put("basis", basis);
                    result.add(record);
                }
            }
        }
        return result;
    }

    private Map<String, Object> pcodeUse(PcodeOp operation, Varnode followedValue) {
        Map<String, Object> result = operationRecord(operation, "downstream-use", 0);
        List<Integer> inputIndexes = new ArrayList<>();
        for (int index = 0; index < operation.getNumInputs(); index++) {
            if (sameIdentity(operation.getInput(index), followedValue)) {
                inputIndexes.add(index);
            }
        }
        result.put("matchingInputIndexes", inputIndexes);
        if (operation.getOpcode() == PcodeOp.CALL || operation.getOpcode() == PcodeOp.CALLIND) {
            List<Integer> argumentIndexes = new ArrayList<>();
            for (Integer index : inputIndexes) {
                if (index > 0) {
                    argumentIndexes.add(index - 1);
                }
            }
            result.put("callArgumentIndexes", argumentIndexes);
            Function callee = operation.getOpcode() == PcodeOp.CALL ? directCalledFunction(operation) : null;
            result.put("calleeName", callee == null ? null : callee.getName());
            result.put("calleeAddress", callee == null ? null : address(callee));
            result.put("referencedCallees", referencedCalleesAt(operation.getSeqnum().getTarget()));
        }
        return result;
    }

    private Long expressionOffsetUsing(PcodeOp operation, Varnode base) {
        if (operation.getOutput() == null) {
            return null;
        }
        return offsetFromBase(operation.getOutput(), base, 0);
    }

    private boolean isTraceable(int opcode) {
        return isWrapper(opcode) || opcode == PcodeOp.INT_ADD || opcode == PcodeOp.PTRSUB ||
            opcode == PcodeOp.PTRADD || opcode == PcodeOp.LOAD;
    }

    private Map<String, Object> traceWrittenValue(HighFunction highFunction, PcodeOp store,
            Varnode value, Varnode receiver, int depth) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("varnode", varnode(value));
        List<String> evidence = new ArrayList<>();
        result.put("evidence", evidence);
        if (depth > MAX_TRACE_DEPTH) {
            result.put("status", "unresolved-depth-limit");
            return result;
        }
        Varnode stripped = stripWrappers(value);
        if (stripped == null) {
            result.put("status", "unresolved-null-varnode");
            return result;
        }
        if (stripped.isConstant() || (stripped.isAddress() && stripped.getAddress().isMemoryAddress())) {
            Address address = addressFromVarnode(stripped);
            result.put("status", stripped.getOffset() == 0 ? "resolved-null-constant" : "resolved-constant-address");
            result.put("address", address == null ? null : formatAddress(address));
            result.put("symbols", address == null ? Collections.emptyList() : symbolsAt(address));
            evidence.add("The stored value is a direct constant/address varnode.");
            return result;
        }
        for (int index = 0; index < getHighParamCount(highFunction); index++) {
            HighParam parameter = getHighParamSafely(highFunction, index);
            if (parameter != null && parameter.getRepresentative() != null &&
                    sameIdentity(stripped, parameter.getRepresentative())) {
                result.put("status", "resolved-function-parameter");
                result.put("sourceParameterIndex", index);
                evidence.add("The stored value has the same high-p-code identity as function parameter " + index + ".");
                return result;
            }
        }
        PcodeOp definition = stripped.getDef();
        result.put("definingOperation", operationSummary(definition));
        if (definition == null) {
            result.put("status", "unresolved-no-definition");
            return result;
        }
        if (definition.getOpcode() == PcodeOp.CALL || definition.getOpcode() == PcodeOp.CALLIND) {
            Function callee = definition.getOpcode() == PcodeOp.CALL ? directCalledFunction(definition) : null;
            result.put("status", "resolved-call-return");
            result.put("callSite", sequenceAddress(definition));
            result.put("calleeName", callee == null ? null : callee.getName());
            result.put("calleeAddress", callee == null ? null : address(callee));
            result.put("downstreamInitializerCalls", callsUsingValueBefore(stripped, store));
            evidence.add("The stored value is the output varnode of a call.");
            return result;
        }
        if (definition.getOpcode() == PcodeOp.LOAD && definition.getNumInputs() >= 2) {
            result.put("status", "resolved-load-expression");
            result.put("loadAddress", sequenceAddress(definition));
            result.put("loadPointer", varnode(definition.getInput(1)));
            Long receiverOffset = offsetFromBase(definition.getInput(1), receiver, 0);
            result.put("sourceReceiverOffset", receiverOffset);
            evidence.add(receiverOffset == null
                ? "The value comes from a LOAD, but its base could not be tied to parameter 0."
                : "The value is loaded from parameter 0 plus " + unsignedHex(receiverOffset) + ".");
            return result;
        }
        if (definition.getOpcode() == PcodeOp.MULTIEQUAL) {
            result.put("status", "unresolved-phi");
            evidence.add("The value is merged by MULTIEQUAL; bounded provenance does not choose a branch.");
            return result;
        }
        result.put("status", "unresolved-unsupported-opcode");
        evidence.add("Defining opcode " + definition.getMnemonic() + " is outside bounded provenance support.");
        return result;
    }

    private static HighParam getHighParamSafely(HighFunction highFunction, int index) {
        if (highFunction == null || index < 0) {
            return null;
        }
        LocalSymbolMap localSymbolMap = highFunction.getLocalSymbolMap();
        if (localSymbolMap == null || index >= localSymbolMap.getNumParams()) {
            return null;
        }
        return localSymbolMap.getParam(index);
    }

    private static int getHighParamCount(HighFunction highFunction) {
        if (highFunction == null) {
            return 0;
        }
        LocalSymbolMap localSymbolMap = highFunction.getLocalSymbolMap();
        return localSymbolMap == null ? 0 : localSymbolMap.getNumParams();
    }

    private void rank(AccessCandidate candidate, Function root, Set<String> rootContext) {
        String fullName = fullName(candidate.function);
        if (fullName.toLowerCase(Locale.ROOT).contains("resourceviewwidget")) {
            candidate.score += 60;
            candidate.receiverEvidence.add("Function symbol/namespace contains ResourceViewWidget.");
            candidate.knownResourceViewWidgetContext = true;
        }
        if (rootContext.contains(functionKey(candidate.function))) {
            candidate.score += 40;
            candidate.receiverEvidence.add("Function is the root or a direct caller/callee of the root.");
            candidate.knownResourceViewWidgetContext = true;
        }
        if (candidate.hasWrite()) {
            candidate.score += 30;
            candidate.receiverEvidence.add("Function directly writes parameter 0 plus the selected offset.");
        }
        candidate.score += 10;
        candidate.receiverEvidence.add("Match is based on parameter 0 identity, not the raw offset alone.");
        candidate.confidence = candidate.score >= 70 ? "high" : candidate.score >= 40 ? "medium" : "low";
    }

    private void enrichCandidateContext(AccessCandidate candidate) throws Exception {
        candidate.callers.addAll(functionSummaries(sortedFunctions(
            candidate.function.getCallingFunctions(monitor))));
        candidate.callees.addAll(functionSummaries(sortedFunctions(
            candidate.function.getCalledFunctions(monitor))));
        candidate.referencedStrings.addAll(collectReferences(candidate.function).strings);
    }

    private List<Map<String, Object>> callsUsingValueBefore(Varnode value, PcodeOp limit) {
        List<Map<String, Object>> result = new ArrayList<>();
        if (value == null || limit == null) {
            return result;
        }
        Iterator<PcodeOp> descendants = value.getDescendants();
        while (descendants.hasNext()) {
            PcodeOp use = descendants.next();
            if ((use.getOpcode() != PcodeOp.CALL && use.getOpcode() != PcodeOp.CALLIND) ||
                    use.getSeqnum().getTarget().compareTo(limit.getSeqnum().getTarget()) > 0) {
                continue;
            }
            List<Integer> argumentIndexes = new ArrayList<>();
            for (int index = 1; index < use.getNumInputs(); index++) {
                if (sameIdentity(use.getInput(index), value)) {
                    argumentIndexes.add(index - 1);
                }
            }
            if (argumentIndexes.isEmpty()) {
                continue;
            }
            Map<String, Object> record = operationSummary(use);
            record.put("argumentIndexes", argumentIndexes);
            Function callee = use.getOpcode() == PcodeOp.CALL ? directCalledFunction(use) : null;
            record.put("calleeName", callee == null ? null : callee.getName());
            record.put("calleeAddress", callee == null ? null : address(callee));
            record.put("interpretation", "Candidate initializer/consumer of the allocated or returned value; semantic role is unproven.");
            result.add(record);
        }
        return result;
    }

    private List<Map<String, Object>> referencedCalleesAt(Address callSite) {
        List<Map<String, Object>> result = new ArrayList<>();
        if (callSite == null) {
            return result;
        }
        for (Reference reference : currentProgram.getReferenceManager().getReferencesFrom(callSite)) {
            if (!reference.getReferenceType().isCall()) {
                continue;
            }
            Function function = currentProgram.getFunctionManager().getFunctionAt(reference.getToAddress());
            if (function != null) {
                result.add(functionSummary(function));
            }
        }
        return result;
    }

    private Set<String> collectRootContext(Function root) throws CancelledException {
        Set<String> result = new LinkedHashSet<>();
        result.add(functionKey(root));
        for (Function function : root.getCallingFunctions(monitor)) {
            result.add(functionKey(function));
        }
        for (Function function : root.getCalledFunctions(monitor)) {
            result.add(functionKey(function));
        }
        return result;
    }

    private List<Function> exportCandidates(List<AccessCandidate> ranked, Path directory,
            Instant generatedAt) throws Exception {
        List<Function> exported = new ArrayList<>();
        Set<String> seen = new LinkedHashSet<>();
        for (AccessCandidate candidate : ranked) {
            if (exported.size() >= MAX_EXPORTED_FUNCTIONS || !seen.add(functionKey(candidate.function))) {
                continue;
            }
            exportFunctionBundle(candidate.function, directory.resolve(safeName(candidate.function)), generatedAt);
            exported.add(candidate.function);
        }
        return exported;
    }

    private void exportFunctionBundle(Function function, Path output, Instant generatedAt) throws Exception {
        Files.createDirectories(output);
        Decompilation decompilation = decompile(function);
        List<Function> callers = sortedFunctions(function.getCallingFunctions(monitor));
        List<Function> callees = sortedFunctions(function.getCalledFunctions(monitor));
        ReferenceContext references = collectReferences(function);
        write(output.resolve("metadata.json"), json(metadata(function, decompilation, generatedAt)));
        write(output.resolve("decompiled.c"), decompilation.text);
        write(output.resolve("callers.json"), json(functionSummaries(callers)));
        write(output.resolve("callees.json"), json(functionSummaries(callees)));
        write(output.resolve("strings.json"), json(references.strings));
        write(output.resolve("globals.json"), json(references.globals));
        write(output.resolve("constants.json"), json(collectConstants(function)));
    }

    private boolean hasInstructionScalar(Function function, long offset) throws CancelledException {
        InstructionIterator instructions = currentProgram.getListing().getInstructions(function.getBody(), true);
        while (instructions.hasNext()) {
            monitor.checkCancelled();
            Instruction instruction = instructions.next();
            for (int index = 0; index < instruction.getNumOperands(); index++) {
                Scalar scalar = instruction.getScalar(index);
                if (scalar != null && scalar.getUnsignedValue() == offset) {
                    return true;
                }
            }
        }
        return false;
    }

    private Long offsetFromBase(Varnode expression, Varnode expectedBase, int depth) {
        if (expression == null || expectedBase == null || depth > MAX_TRACE_DEPTH) {
            return null;
        }
        Varnode value = stripWrappers(expression);
        if (sameIdentity(value, expectedBase)) {
            return 0L;
        }
        PcodeOp definition = value == null ? null : value.getDef();
        if (definition == null) {
            return null;
        }
        int opcode = definition.getOpcode();
        if ((opcode == PcodeOp.INT_ADD || opcode == PcodeOp.PTRSUB) && definition.getNumInputs() == 2) {
            Varnode left = stripWrappers(definition.getInput(0));
            Varnode right = stripWrappers(definition.getInput(1));
            if (right != null && right.isConstant()) {
                Long base = offsetFromBase(left, expectedBase, depth + 1);
                return base == null ? null : base + right.getOffset();
            }
            if (opcode == PcodeOp.INT_ADD && left != null && left.isConstant()) {
                Long base = offsetFromBase(right, expectedBase, depth + 1);
                return base == null ? null : base + left.getOffset();
            }
        }
        if (opcode == PcodeOp.PTRADD && definition.getNumInputs() == 3) {
            Varnode index = stripWrappers(definition.getInput(1));
            Varnode size = stripWrappers(definition.getInput(2));
            if (index != null && index.isConstant() && size != null && size.isConstant()) {
                Long base = offsetFromBase(definition.getInput(0), expectedBase, depth + 1);
                return base == null ? null : base + index.getOffset() * size.getOffset();
            }
        }
        return null;
    }

    private static Varnode stripWrappers(Varnode input) {
        Varnode value = input;
        Set<Varnode> visited = Collections.newSetFromMap(new IdentityHashMap<Varnode, Boolean>());
        while (value != null && visited.add(value)) {
            PcodeOp definition = value.getDef();
            if (definition == null || definition.getNumInputs() == 0 || !isWrapper(definition.getOpcode())) {
                return value;
            }
            value = definition.getInput(0);
        }
        return value;
    }

    private static boolean isWrapper(int opcode) {
        return opcode == PcodeOp.COPY || opcode == PcodeOp.CAST ||
            opcode == PcodeOp.INT_ZEXT || opcode == PcodeOp.INT_SEXT;
    }

    private static boolean sameIdentity(Varnode leftInput, Varnode rightInput) {
        Varnode left = stripWrappers(leftInput);
        Varnode right = stripWrappers(rightInput);
        if (left == null || right == null) {
            return left == right;
        }
        return left == right || left.equals(right) ||
            (left.getHigh() != null && left.getHigh() == right.getHigh());
    }

    private Function directCalledFunction(PcodeOp call) {
        if (call == null || call.getNumInputs() == 0) {
            return null;
        }
        Address target = addressFromVarnode(stripWrappers(call.getInput(0)));
        return target == null ? null : currentProgram.getFunctionManager().getFunctionAt(target);
    }

    private Address addressFromVarnode(Varnode value) {
        if (value == null) {
            return null;
        }
        if (value.isAddress() && value.getAddress().isMemoryAddress()) {
            return value.getAddress();
        }
        if (value.isConstant() && value.getOffset() != 0) {
            return currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(value.getOffset());
        }
        return null;
    }

    private Map<String, Object> operationRecord(PcodeOp operation, String kind, long offset) {
        Map<String, Object> result = operationSummary(operation);
        result.put("accessKind", kind);
        result.put("offset", offset);
        result.put("offsetHex", unsignedHex(offset));
        return result;
    }

    private Map<String, Object> operationSummary(PcodeOp operation) {
        if (operation == null) {
            return null;
        }
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("opcode", operation.getMnemonic());
        result.put("sequenceNumber", operation.getSeqnum().toString());
        result.put("instructionAddress", sequenceAddress(operation));
        result.put("output", varnode(operation.getOutput()));
        List<Map<String, Object>> inputs = new ArrayList<>();
        for (int index = 0; index < operation.getNumInputs(); index++) {
            Map<String, Object> input = new LinkedHashMap<>();
            input.put("index", index);
            input.put("varnode", varnode(operation.getInput(index)));
            inputs.add(input);
        }
        result.put("inputs", inputs);
        return result;
    }

    private Map<String, Object> varnode(Varnode value) {
        if (value == null) {
            return null;
        }
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("encoded", value.encodePiece());
        result.put("size", value.getSize());
        result.put("space", value.getAddress().getAddressSpace().getName());
        result.put("address", formatAddress(value.getAddress()));
        result.put("constant", value.isConstant());
        if (value.isConstant()) {
            result.put("constantValue", value.getOffset());
            result.put("constantHex", unsignedHex(value.getOffset()));
        }
        HighVariable high = value.getHigh();
        if (high != null) {
            Map<String, Object> highRecord = new LinkedHashMap<>();
            highRecord.put("name", high.getName());
            highRecord.put("class", high.getClass().getName());
            DataType type = high.getDataType();
            highRecord.put("dataType", type == null ? null : type.getDisplayName());
            Varnode representative = high.getRepresentative();
            highRecord.put("representativeStorage", representative == null ? null : representative.encodePiece());
            result.put("highVariable", highRecord);
        }
        else {
            result.put("highVariable", null);
        }
        return result;
    }

    private String writeKind(Varnode value, Map<String, Object> provenance) {
        if (value != null && value.isConstant() && value.getOffset() == 0) {
            return "clear";
        }
        String status = String.valueOf(provenance.get("status"));
        if ("resolved-call-return".equals(status) || "resolved-constant-address".equals(status)) {
            return "initialization";
        }
        if ("resolved-function-parameter".equals(status) || "resolved-load-expression".equals(status)) {
            return "assignment";
        }
        return "unknown";
    }

    private Map<String, Object> candidateDocument(String scope, List<AccessCandidate> candidates) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("schemaVersion", 1);
        result.put("scope", scope);
        result.put("candidates", candidates);
        return result;
    }

    private Map<String, Object> provenanceDocument(List<Map<String, Object>> records) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("schemaVersion", 1);
        result.put("maximumTraceDepth", MAX_TRACE_DEPTH);
        result.put("supportedCases", new String[] {
            "constant/address", "function parameter", "call return", "load from a fixed receiver offset"
        });
        result.put("records", records);
        return result;
    }

    private Map<String, Object> writeDocument(List<Map<String, Object>> records) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("schemaVersion", 1);
        result.put("scope", "Ranked direct STORE operations to parameter 0 plus the selected field offset; clear/null writes remain explicit.");
        result.put("writes", records);
        return result;
    }

    private Map<String, Object> manifest(Function root, int baseParameterIndex,
            long fieldOffset, Long nestedOffset, Instant generatedAt, RootResult rootResult,
            List<AccessCandidate> candidates, List<AccessCandidate> writes, List<Function> exported) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("schemaVersion", 1);
        result.put("generatedAtUtc", generatedAt.toString());
        result.put("programName", currentProgram.getName());
        result.put("rootFunction", functionSummary(root));
        result.put("baseParameterIndex", baseParameterIndex);
        result.put("fieldOffset", fieldOffset);
        result.put("fieldOffsetHex", unsignedHex(fieldOffset));
        result.put("nestedOffset", nestedOffset);
        result.put("nestedOffsetHex", nestedOffset == null ? null : unsignedHex(nestedOffset));
        result.put("rootAccessIdentified", rootResult.found);
        result.put("candidateFunctionCount", candidates.size());
        result.put("candidateWriterFunctionCount", writes.size());
        result.put("exportLimit", MAX_EXPORTED_FUNCTIONS);
        result.put("exportedFunctions", functionSummaries(exported));
        result.put("readOnly", true);
        result.put("ranking", "60 ResourceViewWidget symbol/namespace; 40 root/direct caller/callee context; 30 direct write; 10 parameter-0 structural match.");
        result.put("limitations", new String[] {
            "Instruction-scalar prefilter may miss compiler forms that do not preserve the offset as a scalar operand.",
            "Candidate identity is parameter-0 and context based; it is not proof of a common C++ class.",
            "No heap alias analysis, symbolic execution, class recovery, or recursive call tracing is performed.",
            "Nested analysis follows only bounded high-p-code expressions and simple written-value parameter cases."
        });
        return result;
    }

    private Map<String, Object> metadata(Function function, Decompilation decompilation, Instant generatedAt) {
        Map<String, Object> result = functionSummary(function);
        result.put("schemaVersion", 1);
        result.put("exportedAtUtc", generatedAt.toString());
        result.put("signature", function.getPrototypeString(true, true));
        result.put("decompilationCompleted", decompilation.completed);
        result.put("decompilationError", decompilation.error);
        return result;
    }

    private Decompilation decompile(Function function) {
        try {
            DecompileResults results = decompiler.decompileFunction(function, DECOMPILE_TIMEOUT_SECONDS, monitor);
            if (!results.decompileCompleted() || results.getDecompiledFunction() == null) {
                String error = results.getErrorMessage();
                return Decompilation.failed(error == null || error.trim().isEmpty()
                    ? "Decompiler returned no pseudocode." : error);
            }
            return Decompilation.completed(results.getDecompiledFunction().getC(), results.getHighFunction());
        }
        catch (RuntimeException exception) {
            return Decompilation.failed(exception.getClass().getSimpleName() + ": " + safeMessage(exception));
        }
    }

    private ReferenceContext collectReferences(Function function) throws Exception {
        Map<String, Map<String, Object>> strings = new LinkedHashMap<>();
        Map<String, Map<String, Object>> globals = new LinkedHashMap<>();
        InstructionIterator instructions = currentProgram.getListing().getInstructions(function.getBody(), true);
        while (instructions.hasNext()) {
            monitor.checkCancelled();
            Instruction instruction = instructions.next();
            for (Reference reference : instruction.getReferencesFrom()) {
                Address target = reference.getToAddress();
                if (target == null || !target.isMemoryAddress()) {
                    continue;
                }
                Data data = currentProgram.getListing().getDataContaining(target);
                Map<String, Map<String, Object>> destination = data != null && data.hasStringValue() ? strings : globals;
                if (destination == globals && (!reference.getReferenceType().isData() || function.getBody().contains(target))) {
                    continue;
                }
                String key = target.toString();
                Map<String, Object> record = destination.get(key);
                if (record == null) {
                    record = new LinkedHashMap<>();
                    record.put("address", formatAddress(target));
                    record.put("symbol", primarySymbol(target));
                    record.put("dataType", data == null || data.getDataType() == null ? null : data.getDataType().getDisplayName());
                    record.put("value", data != null && data.hasStringValue() ? String.valueOf(data.getValue()) : null);
                    record.put("sourceAddresses", new TreeSet<String>());
                    destination.put(key, record);
                }
                @SuppressWarnings("unchecked")
                Set<String> sources = (Set<String>) record.get("sourceAddresses");
                sources.add(formatAddress(instruction.getAddress()));
            }
        }
        return new ReferenceContext(new ArrayList<>(strings.values()), new ArrayList<>(globals.values()));
    }

    private List<Map<String, Object>> collectConstants(Function function) throws Exception {
        List<Map<String, Object>> result = new ArrayList<>();
        InstructionIterator instructions = currentProgram.getListing().getInstructions(function.getBody(), true);
        while (instructions.hasNext()) {
            monitor.checkCancelled();
            Instruction instruction = instructions.next();
            for (int index = 0; index < instruction.getNumOperands(); index++) {
                Scalar scalar = instruction.getScalar(index);
                if (scalar != null) {
                    Map<String, Object> record = new LinkedHashMap<>();
                    record.put("sourceAddress", formatAddress(instruction.getAddress()));
                    record.put("mnemonic", instruction.getMnemonicString());
                    record.put("operandIndex", index);
                    record.put("bitLength", scalar.bitLength());
                    record.put("signedValue", scalar.getSignedValue());
                    record.put("unsignedHex", unsignedHex(scalar.getUnsignedValue()));
                    result.add(record);
                }
            }
        }
        return result;
    }

    private List<Map<String, Object>> functionSummaries(List<Function> functions) {
        List<Map<String, Object>> result = new ArrayList<>();
        for (Function function : functions) {
            result.add(functionSummary(function));
        }
        return result;
    }

    private Map<String, Object> functionSummary(Function function) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("name", function.getName());
        result.put("fullName", fullName(function));
        result.put("address", address(function));
        result.put("external", function.isExternal());
        return result;
    }

    private List<String> symbolsAt(Address address) {
        List<String> result = new ArrayList<>();
        for (Symbol symbol : currentProgram.getSymbolTable().getSymbols(address)) {
            result.add(symbol.getName(true));
        }
        Collections.sort(result);
        return result;
    }

    private String primarySymbol(Address address) {
        Symbol symbol = currentProgram.getSymbolTable().getPrimarySymbol(address);
        return symbol == null ? null : symbol.getName(true);
    }

    private static List<Function> sortedFunctions(Set<Function> values) {
        List<Function> result = new ArrayList<>(values);
        Collections.sort(result, new Comparator<Function>() {
            @Override public int compare(Function left, Function right) {
                return left.getEntryPoint().compareTo(right.getEntryPoint());
            }
        });
        return result;
    }

    private static int parseNonNegativeInt(String text) {
        int value = Integer.parseInt(text.trim());
        if (value < 0) {
            throw new IllegalArgumentException("Parameter index must be non-negative.");
        }
        return value;
    }

    private static long parseOffset(String text) {
        String value = text.trim();
        return value.startsWith("0x") || value.startsWith("0X")
            ? Long.parseUnsignedLong(value.substring(2), 16)
            : Long.parseLong(value);
    }

    private static String safeName(Function function) {
        String name = function.getName().replaceAll("[^A-Za-z0-9._-]", "_");
        return (name.isEmpty() ? "function" : name) + "__" + address(function).replaceAll("[^A-Za-z0-9._-]", "_");
    }

    private static String fullName(Function function) {
        Symbol symbol = function.getSymbol();
        return symbol == null ? function.getName() : symbol.getName(true);
    }

    private static String functionKey(Function function) {
        return function.getEntryPoint().toString();
    }

    private static String address(Function function) {
        return formatAddress(function.getEntryPoint());
    }

    private static String formatAddress(Address address) {
        return address == null ? null : address.toString().toUpperCase(Locale.ROOT);
    }

    private static String sequenceAddress(PcodeOp operation) {
        return operation == null ? null : formatAddress(operation.getSeqnum().getTarget());
    }

    private static String unsignedHex(long value) {
        return "0x" + Long.toUnsignedString(value, 16).toUpperCase(Locale.ROOT);
    }

    private boolean isInsideGhidraProjectStorage(Path exportRoot) {
        if (state.getProject() == null || state.getProject().getProjectLocator() == null) {
            return false;
        }
        File directory = state.getProject().getProjectLocator().getProjectDir();
        return directory != null && exportRoot.startsWith(directory.toPath().toAbsolutePath().normalize());
    }

    private static String safeMessage(Throwable throwable) {
        String message = throwable.getMessage();
        return message == null || message.trim().isEmpty() ? "No error message was provided." : message;
    }

    private static void write(Path path, String contents) throws IOException {
        Files.write(path, contents.getBytes(StandardCharsets.UTF_8));
    }

    private static String json(Object value) {
        return JSON.toJson(value) + "\n";
    }

    private static final class Decompilation {
        final boolean completed;
        final String text;
        final String error;
        transient final HighFunction highFunction;
        private Decompilation(boolean completed, String text, String error, HighFunction highFunction) {
            this.completed = completed; this.text = text; this.error = error; this.highFunction = highFunction;
        }
        static Decompilation completed(String text, HighFunction highFunction) {
            return new Decompilation(true, text, null, highFunction);
        }
        static Decompilation failed(String error) {
            return new Decompilation(false, "/* Decompilation failed: " + error + " */\n", error, null);
        }
    }

    private static final class RootResult {
        boolean found;
        String error;
        Map<String, Object> baseParameter;
        final List<Map<String, Object>> accesses = new ArrayList<>();
        Map<String, Object> toMap(Function root, int parameterIndex, long fieldOffset, Long nestedOffset) {
            Map<String, Object> result = new LinkedHashMap<>();
            result.put("schemaVersion", 1);
            result.put("rootFunction", summary(root));
            result.put("baseParameterIndex", parameterIndex);
            result.put("fieldOffset", fieldOffset);
            result.put("fieldOffsetHex", unsignedHex(fieldOffset));
            result.put("nestedOffset", nestedOffset);
            result.put("nestedOffsetHex", nestedOffset == null ? null : unsignedHex(nestedOffset));
            result.put("identified", found);
            result.put("error", error);
            result.put("baseParameter", baseParameter);
            result.put("accesses", accesses);
            return result;
        }
        private static Map<String, Object> summary(Function function) {
            Map<String, Object> result = new LinkedHashMap<>();
            result.put("name", function.getName());
            result.put("address", address(function));
            return result;
        }
    }

    private static final class AccessCandidate {
        static final Comparator<AccessCandidate> ORDER = new Comparator<AccessCandidate>() {
            @Override public int compare(AccessCandidate left, AccessCandidate right) {
                int score = Integer.compare(right.score, left.score);
                return score != 0 ? score : left.functionAddress.compareTo(right.functionAddress);
            }
        };
        transient final Function function;
        final String functionName;
        final String functionAddress;
        final String functionFullName;
        int score;
        String confidence;
        boolean knownResourceViewWidgetContext;
        final List<String> receiverEvidence = new ArrayList<>();
        final List<Map<String, Object>> accesses = new ArrayList<>();
        final List<Map<String, Object>> nestedAccesses = new ArrayList<>();
        final List<Map<String, Object>> callers = new ArrayList<>();
        final List<Map<String, Object>> callees = new ArrayList<>();
        final List<Map<String, Object>> referencedStrings = new ArrayList<>();
        transient final List<Map<String, Object>> provenanceRecords = new ArrayList<>();
        AccessCandidate(Function function) {
            this.function = function;
            this.functionName = function.getName();
            this.functionAddress = address(function);
            this.functionFullName = fullName(function);
        }
        boolean hasWrite() {
            for (Map<String, Object> access : accesses) {
                if ("write".equals(access.get("accessKind"))) return true;
            }
            return false;
        }
    }

    private static final class ReferenceContext {
        final List<Map<String, Object>> strings;
        final List<Map<String, Object>> globals;
        ReferenceContext(List<Map<String, Object>> strings, List<Map<String, Object>> globals) {
            this.strings = strings; this.globals = globals;
        }
    }
}
