// Export the selected function, direct internal callees, and simple resolved vtable calls.
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
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.pcode.HighFunction;
import ghidra.program.model.pcode.HighParam;
import ghidra.program.model.pcode.HighVariable;
import ghidra.program.model.pcode.PcodeOp;
import ghidra.program.model.pcode.Varnode;
import ghidra.program.model.scalar.Scalar;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.Symbol;
import ghidra.util.exception.CancelledException;

public class ExportFunctionNeighbourhood extends GhidraScript {

    private static final int EXPORT_DEPTH = 1;
    private static final int DECOMPILE_TIMEOUT_SECONDS = 60;
    private static final int MAX_THUNK_HOPS = 100;
    private static final int PCODE_DIAGNOSTIC_MAX_DEPTH = 8;
    private static final Gson JSON = new GsonBuilder()
        .setPrettyPrinting()
        .disableHtmlEscaping()
        .serializeNulls()
        .create();
    private final Map<String, Decompilation> decompilationCache = new LinkedHashMap<>();

    @Override
    public void run() throws Exception {
        if (currentProgram == null) {
            printerr("No program is open.");
            return;
        }
        if (currentAddress == null) {
            printerr("No cursor address is available. Open a program in CodeBrowser and place the cursor in a function.");
            return;
        }

        Function root = currentProgram.getFunctionManager().getFunctionContaining(currentAddress);
        if (root == null) {
            printerr("The cursor is not inside a defined function: " + currentAddress);
            return;
        }

        File chosenRoot = askDirectory(
            "Choose export root (for example, the repository's exports directory)",
            "Export");
        Path exportRoot = chosenRoot.toPath().toAbsolutePath().normalize();
        if (isInsideGhidraProjectStorage(exportRoot)) {
            printerr("The export root must be outside the Ghidra project storage: " + exportRoot);
            return;
        }

        Path neighbourhoodDirectory = exportRoot
            .resolve("neighbourhoods")
            .resolve(safeDirectoryName(root));
        Path functionsDirectory = neighbourhoodDirectory.resolve("functions");
        Files.createDirectories(functionsDirectory);

        Instant generatedAt = Instant.now();
        List<Function> directCallees = sortedFunctions(root.getCalledFunctions(monitor));
        monitor.checkCancelled();

        List<CallEdge> edges = new ArrayList<>();
        Map<String, Function> functionsToExport = new LinkedHashMap<>();
        functionsToExport.put(functionKey(root), root);

        for (Function callee : directCallees) {
            monitor.checkCancelled();
            ThunkResolution resolution = resolveThunk(callee);
            CallEdge edge = new CallEdge(root, callee, callSiteAddresses(root, callee), resolution);
            edges.add(edge);

            Function resolved = resolution.resolvedFunction;
            if (resolved != null && isInternalExportable(resolved)) {
                functionsToExport.put(functionKey(resolved), resolved);
                edge.exportEligible = true;
            }
        }

        IndirectAnalysis indirectAnalysis = analyzeIndirectCalls(root);
        for (IndirectCall call : indirectAnalysis.calls) {
            Function resolved = call.resolvedFunction;
            if (resolved != null && isInternalExportable(resolved)) {
                functionsToExport.put(functionKey(resolved), resolved);
                call.exportEligible = true;
            }
        }

        List<ExportFailure> failures = new ArrayList<>();
        Set<String> successfullyExported = new LinkedHashSet<>();
        for (Function function : sortedFunctions(new LinkedHashSet<>(functionsToExport.values()))) {
            monitor.checkCancelled();
            Path outputDirectory = functionsDirectory.resolve(safeDirectoryName(function));
            try {
                exportFunctionBundle(function, outputDirectory, generatedAt);
                successfullyExported.add(functionKey(function));
                println("Exported " + function.getName() + " to " + outputDirectory.toAbsolutePath());
            }
            catch (CancelledException exception) {
                throw exception;
            }
            catch (Exception exception) {
                String error = exception.getClass().getSimpleName() + ": " + safeMessage(exception);
                failures.add(new ExportFailure(function, error));
                printerr("Could not export " + function.getName() + " at " + address(function) + ": " + error);
            }
        }

        for (CallEdge edge : edges) {
            if (edge.resolvedFunctionKey != null) {
                edge.exported = successfullyExported.contains(edge.resolvedFunctionKey);
                if (edge.exportEligible && !edge.exported) {
                    edge.exportError = failureFor(edge.resolvedFunctionKey, failures);
                }
            }
        }
        for (IndirectCall call : indirectAnalysis.calls) {
            if (call.resolvedFunctionKey != null) {
                call.exported = successfullyExported.contains(call.resolvedFunctionKey);
                if (call.exportEligible && !call.exported) {
                    call.exportError = failureFor(call.resolvedFunctionKey, failures);
                }
            }
        }

        Files.createDirectories(neighbourhoodDirectory);
        write(neighbourhoodDirectory.resolve("graph.json"), json(graph(root, edges, indirectAnalysis.calls)));
        write(
            neighbourhoodDirectory.resolve("indirect-calls.json"),
            json(indirectCalls(root, indirectAnalysis)));
        write(
            neighbourhoodDirectory.resolve("pcode-diagnostics.json"),
            json(pcodeDiagnostics(root, indirectAnalysis)));
        write(
            neighbourhoodDirectory.resolve("manifest.json"),
            json(manifest(
                root,
                generatedAt,
                successfullyExported.size(),
                indirectAnalysis,
                failures)));

        println(
            "Exported depth-" + EXPORT_DEPTH + " neighbourhood for " + root.getName() +
            " to " + neighbourhoodDirectory.toAbsolutePath());
        if (!failures.isEmpty()) {
            printerr(failures.size() + " function bundle(s) could not be exported; see manifest.json.");
        }
    }

    private void exportFunctionBundle(Function function, Path outputDirectory, Instant generatedAt)
            throws Exception {
        Files.createDirectories(outputDirectory);

        monitor.setMessage("Decompiling " + function.getName());
        Decompilation decompilation = decompile(function);
        monitor.checkCancelled();

        List<Function> callers = sortedFunctions(function.getCallingFunctions(monitor));
        monitor.checkCancelled();
        List<Function> callees = sortedFunctions(function.getCalledFunctions(monitor));
        monitor.checkCancelled();

        ReferenceContext references = collectReferences(function);
        List<ScalarContext> constants = collectConstants(function);

        write(outputDirectory.resolve("metadata.json"), json(metadata(function, decompilation, generatedAt)));
        write(outputDirectory.resolve("decompiled.c"), decompilation.text);
        write(outputDirectory.resolve("callers.json"), json(functionSummaries(callers)));
        write(outputDirectory.resolve("callees.json"), json(functionSummaries(callees)));
        write(outputDirectory.resolve("strings.json"), json(references.strings));
        write(outputDirectory.resolve("globals.json"), json(references.globals));
        write(outputDirectory.resolve("constants.json"), json(constants));

        if (!decompilation.completed) {
            printerr(
                "Decompilation did not complete for " + function.getName() + ": " +
                decompilation.error);
        }
    }

    private ThunkResolution resolveThunk(Function original) throws CancelledException {
        if (!original.isThunk()) {
            return ThunkResolution.resolved(original, false, 0);
        }

        Set<String> visited = new LinkedHashSet<>();
        Function current = original;
        int hops = 0;
        while (current != null && current.isThunk()) {
            monitor.checkCancelled();
            String key = functionKey(current);
            if (!visited.add(key)) {
                return ThunkResolution.failed("Thunk cycle detected at " + address(current), hops);
            }
            if (hops >= MAX_THUNK_HOPS) {
                return ThunkResolution.failed(
                    "Thunk chain exceeded the safety limit of " + MAX_THUNK_HOPS + " hops", hops);
            }

            Function next;
            try {
                next = current.getThunkedFunction(false);
            }
            catch (RuntimeException exception) {
                return ThunkResolution.failed(
                    "Ghidra could not resolve thunk " + current.getName() + ": " +
                    exception.getClass().getSimpleName() + ": " + safeMessage(exception),
                    hops);
            }
            if (next == null) {
                return ThunkResolution.failed(
                    "Ghidra reported no target for thunk " + current.getName(), hops);
            }
            current = next;
            hops++;
        }

        if (current == null) {
            return ThunkResolution.failed("Thunk resolution reached a null target", hops);
        }
        return ThunkResolution.resolved(current, true, hops);
    }

    private List<String> callSiteAddresses(Function caller, Function callee) throws CancelledException {
        Set<String> addresses = new TreeSet<>();
        ReferenceIterator references = currentProgram.getReferenceManager()
            .getReferencesTo(callee.getEntryPoint());
        while (references.hasNext()) {
            monitor.checkCancelled();
            Reference reference = references.next();
            if (reference.getReferenceType().isCall() && caller.getBody().contains(reference.getFromAddress())) {
                addresses.add(reference.getFromAddress().toString());
            }
        }
        return new ArrayList<>(addresses);
    }

    private boolean isInternalExportable(Function function) {
        return !function.isExternal() && function.getBody() != null && !function.getBody().isEmpty();
    }

    private Decompilation decompile(Function function) {
        String key = functionKey(function);
        Decompilation cached = decompilationCache.get(key);
        if (cached != null) {
            return cached;
        }

        DecompInterface decompiler = new DecompInterface();
        try {
            DecompileOptions options = new DecompileOptions();
            options.grabFromProgram(currentProgram);
            decompiler.setOptions(options);
            if (!decompiler.openProgram(currentProgram)) {
                String message = "Decompiler could not open the current program: " + decompiler.getLastMessage();
                return cacheDecompilation(key, Decompilation.failed(message));
            }

            DecompileResults results = decompiler.decompileFunction(
                function, DECOMPILE_TIMEOUT_SECONDS, monitor);
            if (!results.decompileCompleted() || results.getDecompiledFunction() == null) {
                String message = results.getErrorMessage();
                if (message == null || message.trim().isEmpty()) {
                    message = "Decompiler returned no pseudocode (possibly timed out).";
                }
                return cacheDecompilation(key, Decompilation.failed(message));
            }
            return cacheDecompilation(
                key,
                Decompilation.completed(
                    results.getDecompiledFunction().getC(), results.getHighFunction()));
        }
        catch (RuntimeException exception) {
            return cacheDecompilation(
                key,
                Decompilation.failed(exception.getClass().getSimpleName() + ": " + safeMessage(exception)));
        }
        finally {
            decompiler.dispose();
        }
    }

    private Decompilation cacheDecompilation(String key, Decompilation result) {
        decompilationCache.put(key, result);
        return result;
    }

    private IndirectAnalysis analyzeIndirectCalls(Function root) throws CancelledException {
        Decompilation decompilation = decompile(root);
        if (!decompilation.completed || decompilation.highFunction == null) {
            return IndirectAnalysis.failed(
                decompilation.error == null
                    ? "Decompiler returned no high p-code."
                    : decompilation.error,
                collectRawIndirectCalls(root));
        }

        Map<String, IndirectCall> callsBySite = new LinkedHashMap<>();
        Iterator<? extends PcodeOp> operations = decompilation.highFunction.getPcodeOps();
        while (operations.hasNext()) {
            monitor.checkCancelled();
            PcodeOp operation = operations.next();
            if (operation.getOpcode() != PcodeOp.CALLIND) {
                continue;
            }

            Address callSite = operation.getSeqnum().getTarget();
            String key = callSite.toString().toUpperCase(Locale.ROOT);
            if (!callsBySite.containsKey(key)) {
                try {
                    IndirectCall call = resolveIndirectCall(decompilation.highFunction, operation);
                    if ("unresolved-receiver-provenance".equals(call.status)) {
                        try {
                            call.pcodeDiagnostic = pcodeDiagnostic(root, operation, call.status);
                        }
                        catch (RuntimeException exception) {
                            call.pcodeDiagnostic = failedPcodeDiagnostic(
                                operation,
                                call.status,
                                exception.getClass().getSimpleName() + ": " + safeMessage(exception));
                        }
                    }
                    callsBySite.put(key, call);
                }
                catch (CancelledException exception) {
                    throw exception;
                }
                catch (RuntimeException exception) {
                    callsBySite.put(
                        key,
                        IndirectCall.unsupported(
                            callSite,
                            currentProgram.getDefaultPointerSize(),
                            "Indirect-call analysis failed: " +
                            exception.getClass().getSimpleName() + ": " + safeMessage(exception)));
                }
            }
        }

        for (IndirectCall rawCall : collectRawIndirectCalls(root)) {
            String key = rawCall.callSiteAddress.toUpperCase(Locale.ROOT);
            if (!callsBySite.containsKey(key)) {
                callsBySite.put(key, rawCall);
            }
        }

        return IndirectAnalysis.completed(new ArrayList<>(callsBySite.values()));
    }

    private Map<String, Object> pcodeDiagnostic(
            Function parentFunction, PcodeOp callOperation, String status) {
        PcodeDiagnosticContext context = new PcodeDiagnosticContext();
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("callSiteAddress", formatAddress(callOperation.getSeqnum().getTarget()));
        result.put("opcode", callOperation.getMnemonic());
        result.put("status", status);
        result.put("diagnosticCompleted", true);
        result.put("diagnosticError", null);
        result.put("callOperation", pcodeOpMetadata(callOperation, parentFunction, context));

        Varnode target = callOperation.getNumInputs() == 0 ? null : callOperation.getInput(0);
        Map<String, Object> callTarget = new LinkedHashMap<>();
        callTarget.put("varnode", varnodeMetadata(target, context));
        callTarget.put(
            "definitionTree",
            definitionTree(target, parentFunction, context, 0));
        result.put("callTarget", callTarget);

        List<Map<String, Object>> arguments = new ArrayList<>();
        for (int inputIndex = 1; inputIndex < callOperation.getNumInputs(); inputIndex++) {
            Map<String, Object> argument = new LinkedHashMap<>();
            argument.put("argumentIndex", inputIndex - 1);
            argument.put("pcodeInputIndex", inputIndex);
            argument.put("varnode", varnodeMetadata(callOperation.getInput(inputIndex), context));
            arguments.add(argument);
        }
        result.put("arguments", arguments);
        result.put(
            "callindConvention",
            "input 0 is the indirect target; inputs 1..N are call arguments, so argumentIndex 0 is pcodeInputIndex 1.");

        List<Map<String, Object>> comparisons = new ArrayList<>();
        Varnode receiverArgument = callOperation.getNumInputs() > 1
            ? callOperation.getInput(1)
            : null;
        if (receiverArgument != null) {
            for (Varnode encountered : context.targetTreeVarnodes) {
                if (encountered == null || encountered.isConstant()) {
                    continue;
                }
                Map<String, Object> comparison = new LinkedHashMap<>();
                comparison.put("argumentIndex", 0);
                comparison.put("argumentVarnodeId", context.id(receiverArgument));
                comparison.put("targetTreeVarnodeId", context.id(encountered));
                comparison.put("sameVarnode", sameVarnode(receiverArgument, encountered));
                comparison.put("sameHighVariable", sameHighVariable(receiverArgument, encountered));
                comparison.put("sameStorage", sameStorage(receiverArgument, encountered));
                comparison.put("sameDefiningOp", receiverArgument.getDef() != null &&
                    receiverArgument.getDef() == encountered.getDef());
                comparisons.add(comparison);
            }
        }
        result.put("receiverComparisons", comparisons);
        return result;
    }

    private Map<String, Object> failedPcodeDiagnostic(
            PcodeOp callOperation, String status, String error) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("callSiteAddress", formatAddress(callOperation.getSeqnum().getTarget()));
        result.put("opcode", callOperation.getMnemonic());
        result.put("status", status);
        result.put("diagnosticCompleted", false);
        result.put("diagnosticError", error);
        return result;
    }

    private Map<String, Object> definitionTree(
            Varnode varnode,
            Function parentFunction,
            PcodeDiagnosticContext context,
            int depth) {
        Map<String, Object> node = new LinkedHashMap<>();
        node.put("depth", depth);
        node.put("varnode", varnodeMetadata(varnode, context));
        if (varnode == null) {
            node.put("stopReason", "null-varnode");
            return node;
        }
        context.addTargetTreeVarnode(varnode);
        if (varnode.isConstant()) {
            node.put("stopReason", "constant");
            return node;
        }
        if (depth >= PCODE_DIAGNOSTIC_MAX_DEPTH) {
            node.put("stopReason", "maximum-depth");
            return node;
        }
        if (!context.visitedTreeVarnodes.add(varnode)) {
            node.put("stopReason", "visited-varnode");
            return node;
        }

        PcodeOp definition = varnode.getDef();
        if (definition == null) {
            node.put("stopReason", "no-definition");
            return node;
        }
        if (!context.visitedTreeOps.add(definition)) {
            node.put("stopReason", "visited-definition");
            node.put("definition", pcodeOpMetadata(definition, parentFunction, context));
            return node;
        }

        Map<String, Object> definitionNode = pcodeOpMetadata(definition, parentFunction, context);
        List<Map<String, Object>> inputs = new ArrayList<>();
        for (int index = 0; index < definition.getNumInputs(); index++) {
            Map<String, Object> input = new LinkedHashMap<>();
            input.put("index", index);
            input.put("role", pcodeInputRole(definition, index));
            input.put(
                "expression",
                definitionTree(definition.getInput(index), parentFunction, context, depth + 1));
            inputs.add(input);
        }
        definitionNode.put("inputs", inputs);
        node.put("definition", definitionNode);
        return node;
    }

    private Map<String, Object> pcodeOpMetadata(
            PcodeOp operation, Function parentFunction, PcodeDiagnosticContext context) {
        if (operation == null) {
            return null;
        }
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("id", context.id(operation));
        result.put("opcode", operation.getMnemonic());
        result.put("opcodeValue", operation.getOpcode());
        result.put("sequenceNumber", operation.getSeqnum().toString());
        result.put("sequenceAddress", formatAddress(operation.getSeqnum().getTarget()));
        result.put("sequenceTime", operation.getSeqnum().getTime());
        result.put("parentFunctionName", parentFunction.getName());
        result.put("parentFunctionAddress", address(parentFunction));
        result.put("output", varnodeMetadata(operation.getOutput(), context));
        result.put("inputCount", operation.getNumInputs());
        List<Map<String, Object>> inputs = new ArrayList<>();
        for (int index = 0; index < operation.getNumInputs(); index++) {
            Map<String, Object> input = new LinkedHashMap<>();
            input.put("index", index);
            input.put("role", pcodeInputRole(operation, index));
            input.put("varnode", varnodeMetadata(operation.getInput(index), context));
            inputs.add(input);
        }
        result.put("inputs", inputs);
        return result;
    }

    private Map<String, Object> varnodeMetadata(
            Varnode varnode, PcodeDiagnosticContext context) {
        if (varnode == null) {
            return null;
        }
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("id", context.id(varnode));
        result.put("encoded", varnode.encodePiece());
        result.put("size", varnode.getSize());
        result.put("space", varnode.getAddress().getAddressSpace().getName());
        result.put("offset", hex(varnode.getOffset()));
        result.put("address", formatAddress(varnode.getAddress()));
        result.put("isConstant", varnode.isConstant());
        result.put("isAddress", varnode.isAddress());
        result.put("isRegister", varnode.isRegister());
        result.put("isUnique", varnode.isUnique());
        result.put("isPersistent", varnode.isPersistent());
        result.put("isInput", varnode.isInput());
        result.put("isUnaffected", varnode.isUnaffected());
        if (varnode.isConstant()) {
            result.put("constantValue", varnode.getOffset());
            result.put("constantHex", hex(varnode.getOffset()));
        }

        HighVariable high = varnode.getHigh();
        if (high == null) {
            result.put("highVariable", null);
        }
        else {
            Map<String, Object> highMetadata = new LinkedHashMap<>();
            highMetadata.put("name", high.getName());
            highMetadata.put("class", high.getClass().getName());
            highMetadata.put("identity", context.id(high));
            Varnode representative = high.getRepresentative();
            highMetadata.put(
                "representativeStorage",
                representative == null ? null : representative.encodePiece());
            DataType dataType = high.getDataType();
            highMetadata.put("dataType", dataType == null ? null : dataType.getDisplayName());
            result.put("highVariable", highMetadata);
        }
        return result;
    }

    private static String pcodeInputRole(PcodeOp operation, int index) {
        if (operation.getOpcode() == PcodeOp.CALLIND) {
            return index == 0 ? "target" : "argument-" + (index - 1);
        }
        if (operation.getOpcode() == PcodeOp.LOAD) {
            return index == 0 ? "space" : index == 1 ? "pointer" : "input-" + index;
        }
        return "input-" + index;
    }

    private static boolean sameVarnode(Varnode left, Varnode right) {
        return left != null && left == right;
    }

    private static boolean sameHighVariable(Varnode left, Varnode right) {
        return left != null && right != null && left.getHigh() != null &&
            left.getHigh() == right.getHigh();
    }

    private static boolean sameStorage(Varnode left, Varnode right) {
        return left != null && right != null && left.getSize() == right.getSize() &&
            left.getAddress().equals(right.getAddress());
    }

    private List<IndirectCall> collectRawIndirectCalls(Function root) throws CancelledException {
        List<IndirectCall> calls = new ArrayList<>();
        InstructionIterator instructions = currentProgram.getListing().getInstructions(root.getBody(), true);
        while (instructions.hasNext()) {
            monitor.checkCancelled();
            Instruction instruction = instructions.next();
            if (instruction.getFlowType().isCall() && instruction.getFlowType().isComputed()) {
                calls.add(IndirectCall.unsupported(
                    instruction.getAddress(),
                    currentProgram.getDefaultPointerSize(),
                    "Decompiler high p-code was unavailable or did not expose this computed call as CALLIND."));
            }
        }
        return calls;
    }

    private IndirectCall resolveIndirectCall(HighFunction highFunction, PcodeOp callOperation)
            throws CancelledException {
        int pointerSize = currentProgram.getDefaultPointerSize();
        IndirectCall result = new IndirectCall(callOperation.getSeqnum().getTarget(), pointerSize);
        if (callOperation.getNumInputs() == 0) {
            result.fail("unsupported-pattern", "CALLIND has no target input.");
            return result;
        }

        Varnode target = stripCopiesAndCasts(callOperation.getInput(0));
        PcodeOp targetDefinition = target == null ? null : target.getDef();
        if (targetDefinition == null || targetDefinition.getOpcode() != PcodeOp.LOAD ||
                targetDefinition.getNumInputs() < 2) {
            result.fail(
                "unsupported-pattern",
                "Indirect target is not a decompiler LOAD from a vtable slot.");
            return result;
        }

        OffsetExpression slotExpression = extractBasePlusConstant(targetDefinition.getInput(1));
        if (slotExpression == null) {
            result.fail(
                "unresolved-nonconstant-offset",
                "Could not express the indirect target address as a base plus a fixed byte offset.");
            return result;
        }
        result.kind = "vtable";
        result.vtableByteOffset = slotExpression.offset;
        if (pointerSize <= 0) {
            result.fail("unsupported-pattern", "The program reports an invalid pointer size: " + pointerSize);
            return result;
        }
        if (Long.remainderUnsigned(slotExpression.offset, pointerSize) == 0) {
            result.vtableSlotIndex = Long.divideUnsigned(slotExpression.offset, pointerSize);
        }
        else {
            result.evidence.add(
                "Fixed byte offset " + hex(slotExpression.offset) +
                " is not aligned to the program pointer size of " + pointerSize + " bytes.");
        }
        result.evidence.add(
            "Decompiler high p-code represents the call target as a LOAD at fixed offset " +
            hex(slotExpression.offset) + ".");

        Varnode vptr = stripCopiesAndCasts(slotExpression.base);
        PcodeOp vptrDefinition = vptr == null ? null : vptr.getDef();
        Varnode receiver = null;
        if (vptrDefinition != null && vptrDefinition.getOpcode() == PcodeOp.LOAD &&
                vptrDefinition.getNumInputs() >= 2) {
            receiver = stripCopiesAndCasts(vptrDefinition.getInput(1));
        }
        result.receiverExpression = describeVarnode(receiver);
        result.receiverIdentity = variableIdentity(receiver);

        Map<String, VtableEvidence> candidates = new LinkedHashMap<>();
        VtableEvidence propagated = vtableAtConstant(slotExpression.base);
        if (propagated != null) {
            candidates.put(propagated.address.toString(), propagated);
        }
        if (receiver != null) {
            collectConstructorVtables(
                highFunction, callOperation, receiver, candidates, result);
        }

        if (candidates.isEmpty()) {
            setConstructorFailure(result);
            return result;
        }
        if (candidates.size() != 1) {
            for (VtableEvidence candidate : candidates.values()) {
                result.vtableCandidates.add(candidate.summary());
            }
            result.fail(
                "unresolved-ambiguous-vptr-stores",
                "More than one distinct vtable was tied to the receiver; no target was guessed.");
            return result;
        }

        VtableEvidence vtable = candidates.values().iterator().next();
        result.vtableName = vtable.name;
        result.vtableAddress = formatAddress(vtable.address);
        result.evidence.add(vtable.description);
        result.provenance.addAll(vtable.provenance);

        Address slotAddress;
        try {
            slotAddress = vtable.address.add(result.vtableByteOffset);
        }
        catch (RuntimeException exception) {
            result.fail(
                "unresolved-no-function-at-slot",
                "Vtable slot address overflowed: " + safeMessage(exception));
            return result;
        }
        result.targetPointerAddress = formatAddress(slotAddress);

        Address pointedAddress;
        try {
            pointedAddress = readPointer(slotAddress, pointerSize);
        }
        catch (Exception exception) {
            result.fail(
                "unresolved-no-function-at-slot",
                "Could not read the vtable slot: " + exception.getClass().getSimpleName() +
                ": " + safeMessage(exception));
            return result;
        }
        if (pointedAddress == null) {
            result.fail("unresolved-no-function-at-slot", "The vtable slot contains a null pointer.");
            return result;
        }
        result.slotPointerValue = formatAddress(pointedAddress);

        Function slotFunction = currentProgram.getFunctionManager().getFunctionAt(pointedAddress);
        if (slotFunction == null) {
            result.fail(
                "unresolved-no-function-at-slot",
                "The slot pointer does not match the entry point of a defined Ghidra function.");
            return result;
        }
        result.slotFunctionName = slotFunction.getName();
        result.slotFunctionAddress = address(slotFunction);

        ThunkResolution thunkResolution = resolveThunk(slotFunction);
        if (!thunkResolution.succeeded || thunkResolution.resolvedFunction == null) {
            result.fail(
                "unsupported-pattern",
                "The slot points to a thunk whose implementation could not be resolved: " +
                thunkResolution.error);
            return result;
        }

        result.resolve(thunkResolution.resolvedFunction, thunkResolution.hopCount);
        result.evidence.add(
            "Read a " + pointerSize + "-byte pointer from " + formatAddress(slotAddress) +
            " and mapped it to defined function " + result.resolvedFunctionName + ".");
        return result;
    }

    private void collectConstructorVtables(
            HighFunction highFunction,
            PcodeOp indirectCall,
            Varnode receiver,
            Map<String, VtableEvidence> candidates,
            IndirectCall result) throws CancelledException {
        String receiverIdentity = variableIdentity(receiver);
        if (receiverIdentity == null) {
            return;
        }

        Address indirectSite = indirectCall.getSeqnum().getTarget();
        Iterator<? extends PcodeOp> operations = highFunction.getPcodeOps();
        while (operations.hasNext()) {
            monitor.checkCancelled();
            PcodeOp operation = operations.next();
            if (operation.getOpcode() != PcodeOp.CALL || operation.getNumInputs() < 2 ||
                    operation.getSeqnum().getTarget().compareTo(indirectSite) >= 0) {
                continue;
            }
            String argumentIdentity = variableIdentity(operation.getInput(1));
            if (!sameVariableIdentity(receiver, operation.getInput(1))) {
                continue;
            }

            InitializerCallDiagnostic diagnostic = new InitializerCallDiagnostic(operation);
            diagnostic.receiverArgumentIdentity = argumentIdentity;
            result.initializerCandidates.add(diagnostic);

            Function called = directCalledFunction(operation);
            if (called == null) {
                diagnostic.analysisError =
                    "Argument 0 matches, but the CALL target is not a defined direct function.";
                continue;
            }
            diagnostic.calledFunctionName = called.getName();
            diagnostic.calledFunctionAddress = address(called);
            ThunkResolution resolution = resolveThunk(called);
            diagnostic.thunkResolutionSucceeded = resolution.succeeded;
            diagnostic.thunkHopCount = resolution.hopCount;
            diagnostic.thunkResolutionError = resolution.error;
            Function implementation = resolution.resolvedFunction;
            if (implementation == null) {
                continue;
            }
            diagnostic.initializerFunctionName = implementation.getName();
            diagnostic.initializerFunctionAddress = address(implementation);

            List<VtableEvidence> assignments = collectVtableAssignments(
                implementation, diagnostic, called, operation.getSeqnum().getTarget());
            if (!assignments.isEmpty()) {
                result.evidence.add(
                    "Earlier direct call " + called.getName() + " at " +
                    formatAddress(operation.getSeqnum().getTarget()) +
                    " receives the indirect-call receiver as its first argument.");
            }
            for (VtableEvidence candidate : assignments) {
                VtableEvidence existing = candidates.get(candidate.address.toString());
                if (existing == null) {
                    candidates.put(candidate.address.toString(), candidate);
                }
                else {
                    existing.provenance.addAll(candidate.provenance);
                }
            }
        }
    }

    private void setConstructorFailure(IndirectCall result) {
        if (result.receiverIdentity == null) {
            result.fail(
                "unresolved-receiver-provenance",
                "The receiver could not be normalized conservatively from high p-code.");
            return;
        }
        if (result.initializerCandidates.isEmpty()) {
            result.fail(
                "unresolved-no-initializer-call",
                "No earlier direct CALL passed the normalized receiver as argument 0.");
            return;
        }

        boolean sawOffsetZeroStore = false;
        boolean sawStoredAddress = false;
        for (InitializerCallDiagnostic initializer : result.initializerCandidates) {
            for (VptrStoreDiagnostic store : initializer.vptrStores) {
                if (store.throughThis && Long.valueOf(0).equals(store.storeOffset)) {
                    sawOffsetZeroStore = true;
                    if (store.storedAddress != null) {
                        sawStoredAddress = true;
                    }
                }
            }
        }
        if (!sawOffsetZeroStore) {
            result.fail(
                "unresolved-no-vptr-store",
                "Candidate initializer implementations exposed no STORE through argument 0 at offset zero.");
        }
        else if (sawStoredAddress) {
            result.fail(
                "unresolved-vtable-symbol",
                "Offset-zero stores were found, but no stored address had exactly one vtable/vftable symbol name.");
        }
        else {
            result.fail(
                "unresolved-no-vptr-store",
                "Offset-zero stores were found, but their stored values were not constant program addresses.");
        }
    }

    private Function directCalledFunction(PcodeOp call) {
        Varnode target = stripCopiesAndCasts(call.getInput(0));
        try {
            Address address = addressFromVarnode(target);
            if (address == null) {
                return null;
            }
            return currentProgram.getFunctionManager().getFunctionAt(address);
        }
        catch (RuntimeException exception) {
            return null;
        }
    }

    private List<VtableEvidence> collectVtableAssignments(
            Function function,
            InitializerCallDiagnostic initializerDiagnostic,
            Function calledFunction,
            Address initializerCallSite)
            throws CancelledException {
        Map<String, VtableEvidence> results = new LinkedHashMap<>();
        Decompilation decompilation = decompile(function);
        if (!decompilation.completed || decompilation.highFunction == null) {
            initializerDiagnostic.analysisError = decompilation.error == null
                ? "Initializer decompilation returned no high p-code."
                : decompilation.error;
            return new ArrayList<>(results.values());
        }

        HighParam thisParameter = decompilation.highFunction.getLocalSymbolMap().getParam(0);
        if (thisParameter == null || thisParameter.getRepresentative() == null) {
            initializerDiagnostic.analysisError =
                "Decompiler high p-code exposed no parameter 0 representative.";
            return new ArrayList<>(results.values());
        }
        String thisIdentity = variableIdentity(thisParameter.getRepresentative());
        initializerDiagnostic.thisParameterIdentity = thisIdentity;
        if (thisIdentity == null) {
            initializerDiagnostic.analysisError =
                "Parameter 0 could not be normalized conservatively.";
            return new ArrayList<>(results.values());
        }

        Iterator<? extends PcodeOp> operations = decompilation.highFunction.getPcodeOps();
        while (operations.hasNext()) {
            monitor.checkCancelled();
            PcodeOp operation = operations.next();
            if (operation.getOpcode() != PcodeOp.STORE || operation.getNumInputs() < 3) {
                continue;
            }

            VptrStoreDiagnostic storeDiagnostic = new VptrStoreDiagnostic(operation);
            initializerDiagnostic.vptrStores.add(storeDiagnostic);
            OffsetExpression destination = extractBasePlusConstant(operation.getInput(1));
            if (destination == null) {
                storeDiagnostic.rejectionReason =
                    "STORE destination is not a conservatively supported base-plus-constant expression.";
                continue;
            }
            storeDiagnostic.storeOffset = destination.offset;
            storeDiagnostic.destinationBaseIdentity = variableIdentity(destination.base);
            storeDiagnostic.throughThis = sameVariableIdentity(
                thisParameter.getRepresentative(), destination.base);
            if (!storeDiagnostic.throughThis) {
                storeDiagnostic.rejectionReason = "STORE destination is not based on parameter 0.";
                continue;
            }
            if (destination.offset != 0) {
                storeDiagnostic.rejectionReason = "STORE through parameter 0 is not at offset zero.";
                continue;
            }

            Address assignedAddress;
            try {
                assignedAddress = addressFromVarnode(stripCopiesAndCasts(operation.getInput(2)));
            }
            catch (RuntimeException exception) {
                continue;
            }
            if (assignedAddress == null) {
                storeDiagnostic.rejectionReason =
                    "Stored value is not a constant program address.";
                continue;
            }
            storeDiagnostic.storedAddress = formatAddress(assignedAddress);
            Set<String> vtableNames = new TreeSet<>();
            for (Symbol symbol : currentProgram.getSymbolTable().getSymbols(assignedAddress)) {
                String name = symbol.getName(true);
                storeDiagnostic.symbolNames.add(name);
                if (isVtableName(name)) {
                    vtableNames.add(name);
                }
            }
            Collections.sort(storeDiagnostic.symbolNames);
            if (vtableNames.size() != 1) {
                storeDiagnostic.rejectionReason = vtableNames.isEmpty()
                    ? "Stored address has no symbol name containing vtable or vftable."
                    : "Stored address has more than one vtable/vftable symbol name.";
                continue;
            }

            String vtableName = vtableNames.iterator().next();
            storeDiagnostic.accepted = true;
            storeDiagnostic.acceptedVtableName = vtableName;
            InitializerProvenance provenance = new InitializerProvenance(
                initializerCallSite, calledFunction, function, operation.getSeqnum().getTarget());
            VtableEvidence evidence = new VtableEvidence(
                vtableName,
                assignedAddress,
                "Resolved implementation " + function.getName() + " stores vtable " +
                vtableName + " through parameter 0 at offset zero at " +
                formatAddress(operation.getSeqnum().getTarget()) + ".");
            evidence.provenance.add(provenance);
            VtableEvidence existing = results.get(assignedAddress.toString());
            if (existing == null) {
                results.put(assignedAddress.toString(), evidence);
            }
            else {
                existing.provenance.add(provenance);
            }
        }
        return new ArrayList<>(results.values());
    }

    private VtableEvidence vtableAtConstant(Varnode varnode) {
        Varnode stripped = stripCopiesAndCasts(varnode);
        try {
            Address address = addressFromVarnode(stripped);
            if (address == null) {
                return null;
            }
            for (Symbol symbol : currentProgram.getSymbolTable().getSymbols(address)) {
                String name = symbol.getName(true);
                if (isVtableName(name)) {
                    return new VtableEvidence(
                        name,
                        address,
                        "Decompiler propagated vtable symbol " + name + " directly into the call target.");
                }
            }
        }
        catch (RuntimeException exception) {
            return null;
        }
        return null;
    }

    private Address addressFromVarnode(Varnode varnode) {
        if (varnode == null) {
            return null;
        }
        if (varnode.isAddress() && varnode.getAddress() != null &&
                varnode.getAddress().isMemoryAddress()) {
            return varnode.getAddress();
        }
        if (varnode.isConstant()) {
            return currentProgram.getAddressFactory().getDefaultAddressSpace()
                .getAddress(varnode.getOffset());
        }
        OffsetExpression expression = extractBasePlusConstant(varnode);
        if (expression != null && expression.base != varnode) {
            Address base = addressFromVarnode(expression.base);
            if (base != null) {
                return base.add(expression.offset);
            }
        }
        return null;
    }

    private static boolean isVtableName(String name) {
        if (name == null) {
            return false;
        }
        String lower = name.toLowerCase(Locale.ROOT);
        return lower.contains("vftable") || lower.contains("vtable");
    }

    private OffsetExpression extractBasePlusConstant(Varnode input) {
        Varnode current = stripCopiesAndCasts(input);
        if (current == null) {
            return null;
        }
        PcodeOp definition = current.getDef();
        if (definition == null) {
            return new OffsetExpression(current, 0);
        }

        if ((definition.getOpcode() == PcodeOp.INT_ADD || definition.getOpcode() == PcodeOp.PTRSUB) &&
                definition.getNumInputs() == 2) {
            Varnode left = stripCopiesAndCasts(definition.getInput(0));
            Varnode right = stripCopiesAndCasts(definition.getInput(1));
            if (right != null && right.isConstant()) {
                return new OffsetExpression(left, right.getOffset());
            }
            if (definition.getOpcode() == PcodeOp.INT_ADD && left != null && left.isConstant()) {
                return new OffsetExpression(right, left.getOffset());
            }
        }

        if (definition.getOpcode() == PcodeOp.PTRADD && definition.getNumInputs() == 3) {
            Varnode index = stripCopiesAndCasts(definition.getInput(1));
            Varnode elementSize = stripCopiesAndCasts(definition.getInput(2));
            if (index != null && index.isConstant() && elementSize != null && elementSize.isConstant()) {
                return new OffsetExpression(
                    stripCopiesAndCasts(definition.getInput(0)),
                    index.getOffset() * elementSize.getOffset());
            }
        }
        return null;
    }

    private static Varnode stripCopiesAndCasts(Varnode input) {
        Varnode current = input;
        Set<Varnode> visited = new LinkedHashSet<>();
        while (current != null && visited.add(current)) {
            PcodeOp definition = current.getDef();
            if (definition == null || definition.getNumInputs() == 0 ||
                    (definition.getOpcode() != PcodeOp.COPY &&
                     definition.getOpcode() != PcodeOp.CAST &&
                     definition.getOpcode() != PcodeOp.INT_ZEXT &&
                     definition.getOpcode() != PcodeOp.INT_SEXT)) {
                return current;
            }
            current = definition.getInput(0);
        }
        return current;
    }

    private static String variableIdentity(Varnode input) {
        Varnode current = stripCopiesAndCasts(input);
        if (current == null) {
            return null;
        }
        PcodeOp definition = current.getDef();
        if (definition != null &&
                (definition.getOpcode() == PcodeOp.PTRSUB ||
                 definition.getOpcode() == PcodeOp.INT_ADD) &&
                definition.getNumInputs() == 2) {
            Varnode left = stripCopiesAndCasts(definition.getInput(0));
            Varnode right = stripCopiesAndCasts(definition.getInput(1));
            if (right != null && right.isConstant()) {
                String baseIdentity = variableIdentity(left);
                return baseIdentity == null ? null :
                    "offset(" + baseIdentity + "," + hex(right.getOffset()) + ")";
            }
            if (definition.getOpcode() == PcodeOp.INT_ADD && left != null && left.isConstant()) {
                String baseIdentity = variableIdentity(right);
                return baseIdentity == null ? null :
                    "offset(" + baseIdentity + "," + hex(left.getOffset()) + ")";
            }
        }
        if (definition != null && definition.getOpcode() == PcodeOp.PTRADD &&
                definition.getNumInputs() == 3) {
            Varnode index = stripCopiesAndCasts(definition.getInput(1));
            Varnode elementSize = stripCopiesAndCasts(definition.getInput(2));
            if (index != null && index.isConstant() &&
                    elementSize != null && elementSize.isConstant()) {
                String baseIdentity = variableIdentity(definition.getInput(0));
                return baseIdentity == null ? null :
                    "offset(" + baseIdentity + "," +
                    hex(index.getOffset() * elementSize.getOffset()) + ")";
            }
        }
        if (current.getHigh() != null && current.getHigh().getName() != null) {
            Varnode representative = current.getHigh().getRepresentative();
            return "high-storage:" +
                (representative == null ? "no-storage" : representative.encodePiece());
        }
        return "varnode:" + current.encodePiece();
    }

    private boolean sameVariableIdentity(Varnode leftInput, Varnode rightInput) {
        return sameVariableIdentity(leftInput, rightInput, 0);
    }

    private boolean sameVariableIdentity(Varnode leftInput, Varnode rightInput, int depth) {
        if (depth > 32) {
            return false;
        }
        Varnode left = stripCopiesAndCasts(leftInput);
        Varnode right = stripCopiesAndCasts(rightInput);
        if (left == null || right == null) {
            return left == right;
        }
        if (left == right || left.equals(right)) {
            return true;
        }

        OffsetExpression leftOffset = extractBasePlusConstant(left);
        OffsetExpression rightOffset = extractBasePlusConstant(right);
        boolean leftIsExpression = leftOffset != null && leftOffset.base != left;
        boolean rightIsExpression = rightOffset != null && rightOffset.base != right;
        if (leftIsExpression || rightIsExpression) {
            Varnode leftBase = leftIsExpression ? leftOffset.base : left;
            Varnode rightBase = rightIsExpression ? rightOffset.base : right;
            long leftValue = leftIsExpression ? leftOffset.offset : 0;
            long rightValue = rightIsExpression ? rightOffset.offset : 0;
            return leftValue == rightValue &&
                sameVariableIdentity(leftBase, rightBase, depth + 1);
        }

        if (left.getHigh() != null && right.getHigh() != null) {
            return left.getHigh() == right.getHigh();
        }
        return false;
    }

    private static String describeVarnode(Varnode varnode) {
        if (varnode == null) {
            return null;
        }
        if (varnode.getHigh() != null && varnode.getHigh().getName() != null) {
            return varnode.getHigh().getName();
        }
        return varnode.encodePiece();
    }

    private Address readPointer(Address slotAddress, int pointerSize) throws Exception {
        if (pointerSize <= 0 || pointerSize > Long.BYTES) {
            throw new IOException("Unsupported pointer size: " + pointerSize + " bytes");
        }
        byte[] bytes = new byte[pointerSize];
        currentProgram.getMemory().getBytes(slotAddress, bytes);
        long value = 0;
        if (currentProgram.getLanguage().isBigEndian()) {
            for (byte item : bytes) {
                value = (value << 8) | (item & 0xffL);
            }
        }
        else {
            for (int index = bytes.length - 1; index >= 0; index--) {
                value = (value << 8) | (bytes[index] & 0xffL);
            }
        }
        if (value == 0) {
            return null;
        }
        return currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(value);
    }

    private ReferenceContext collectReferences(Function function) throws Exception {
        Map<String, StringContext> strings = new LinkedHashMap<>();
        Map<String, GlobalContext> globals = new LinkedHashMap<>();
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
                if (data != null && data.hasStringValue()) {
                    String key = data.getAddress().toString();
                    StringContext context = strings.get(key);
                    if (context == null) {
                        context = new StringContext(data);
                        strings.put(key, context);
                    }
                    context.sourceAddresses.add(instruction.getAddress().toString());
                    continue;
                }

                if (reference.getReferenceType().isData() && !function.getBody().contains(target)) {
                    String key = target.toString();
                    GlobalContext context = globals.get(key);
                    if (context == null) {
                        context = new GlobalContext(target, symbolAt(target), data);
                        globals.put(key, context);
                    }
                    context.referenceTypes.add(reference.getReferenceType().toString());
                    context.sourceAddresses.add(instruction.getAddress().toString());
                }
            }
        }
        return new ReferenceContext(sortedValues(strings), sortedValues(globals));
    }

    private List<ScalarContext> collectConstants(Function function) throws Exception {
        List<ScalarContext> constants = new ArrayList<>();
        InstructionIterator instructions = currentProgram.getListing().getInstructions(function.getBody(), true);
        while (instructions.hasNext()) {
            monitor.checkCancelled();
            Instruction instruction = instructions.next();
            for (int operand = 0; operand < instruction.getNumOperands(); operand++) {
                Scalar scalar = instruction.getScalar(operand);
                if (scalar != null) {
                    constants.add(new ScalarContext(instruction, operand, scalar));
                }
            }
        }
        return constants;
    }

    private Map<String, Object> metadata(
            Function function, Decompilation decompilation, Instant generatedAt) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("schemaVersion", 1);
        result.put("exportedAtUtc", generatedAt.toString());
        result.put("programName", currentProgram.getName());
        result.put("languageId", currentProgram.getLanguageID().toString());
        result.put("compilerSpecId", currentProgram.getCompilerSpec().getCompilerSpecID().toString());
        result.put("imageBase", currentProgram.getImageBase().toString());
        result.put("cursorAddress", currentAddress.toString());
        result.put("functionName", function.getName());
        result.put("entryAddress", function.getEntryPoint().toString());
        result.put("signature", function.getPrototypeString(true, true));
        result.put("external", function.isExternal());
        result.put("thunk", function.isThunk());
        result.put("decompilationCompleted", decompilation.completed);
        result.put("decompilationError", decompilation.error);
        return result;
    }

    private Map<String, Object> graph(
            Function root, List<CallEdge> edges, List<IndirectCall> indirectEdges) {
        Map<String, Object> rootSummary = new LinkedHashMap<>();
        rootSummary.put("name", root.getName());
        rootSummary.put("address", address(root));

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("schemaVersion", 1);
        result.put("root", rootSummary);
        result.put("edges", edges);
        result.put("indirectEdges", indirectGraphEdges(root, indirectEdges));
        return result;
    }

    private Map<String, Object> indirectCalls(Function root, IndirectAnalysis analysis) {
        Map<String, Object> rootSummary = new LinkedHashMap<>();
        rootSummary.put("name", root.getName());
        rootSummary.put("address", address(root));

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("schemaVersion", 2);
        result.put("rootFunction", rootSummary);
        result.put("pointerSize", currentProgram.getDefaultPointerSize());
        result.put("analysisCompleted", analysis.completed);
        result.put("analysisError", analysis.error);
        result.put("indirectCalls", analysis.calls);
        return result;
    }

    private Map<String, Object> pcodeDiagnostics(Function root, IndirectAnalysis analysis) {
        Map<String, Object> rootSummary = new LinkedHashMap<>();
        rootSummary.put("name", root.getName());
        rootSummary.put("address", address(root));

        List<Map<String, Object>> calls = new ArrayList<>();
        for (IndirectCall call : analysis.calls) {
            if (call.pcodeDiagnostic != null) {
                calls.add(call.pcodeDiagnostic);
            }
        }

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("schemaVersion", 1);
        result.put("rootFunction", rootSummary);
        result.put("maximumDefinitionDepth", PCODE_DIAGNOSTIC_MAX_DEPTH);
        result.put(
            "scope",
            "Focused high-p-code diagnostics for unresolved-receiver-provenance CALLIND operations in the selected root function.");
        result.put("calls", calls);
        return result;
    }

    private List<Map<String, Object>> indirectGraphEdges(
            Function root, List<IndirectCall> calls) {
        List<Map<String, Object>> edges = new ArrayList<>();
        for (IndirectCall call : calls) {
            Map<String, Object> edge = new LinkedHashMap<>();
            edge.put("callerName", root.getName());
            edge.put("callerAddress", address(root));
            edge.put("callSiteAddress", call.callSiteAddress);
            edge.put("edgeKind", call.kind == null ? "indirect" : call.kind);
            edge.put("status", call.status);
            edge.put("vtableName", call.vtableName);
            edge.put("vtableByteOffset", call.vtableByteOffset);
            edge.put("resolvedName", call.resolvedFunctionName);
            edge.put("resolvedAddress", call.resolvedFunctionAddress);
            edge.put("resolvedInternal", call.resolvedInternal);
            edge.put("exported", call.exported);
            edge.put("exportError", call.exportError);
            edges.add(edge);
        }
        return edges;
    }

    private Map<String, Object> manifest(
            Function root,
            Instant generatedAt,
            int exportedFunctionCount,
            IndirectAnalysis indirectAnalysis,
            List<ExportFailure> failures) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("schemaVersion", 1);
        result.put("rootFunctionName", root.getName());
        result.put("rootFunctionAddress", address(root));
        result.put("depth", EXPORT_DEPTH);
        result.put("exportedFunctionCount", exportedFunctionCount);
        result.put("indirectCallCount", indirectAnalysis.calls.size());
        int resolvedIndirectCallCount = 0;
        for (IndirectCall call : indirectAnalysis.calls) {
            if ("resolved-static-vtable".equals(call.status)) {
                resolvedIndirectCallCount++;
            }
        }
        result.put("resolvedIndirectCallCount", resolvedIndirectCallCount);
        result.put("indirectAnalysisCompleted", indirectAnalysis.completed);
        result.put("indirectAnalysisError", indirectAnalysis.error);
        int pcodeDiagnosticCount = 0;
        for (IndirectCall call : indirectAnalysis.calls) {
            if (call.pcodeDiagnostic != null) {
                pcodeDiagnosticCount++;
            }
        }
        result.put("pcodeDiagnosticCount", pcodeDiagnosticCount);
        result.put("generatedAt", generatedAt.toString());
        result.put("programName", currentProgram.getName());
        result.put("failures", failures);
        return result;
    }

    private List<Map<String, Object>> functionSummaries(List<Function> functions) {
        List<Map<String, Object>> summaries = new ArrayList<>();
        for (Function function : functions) {
            Map<String, Object> summary = new LinkedHashMap<>();
            summary.put("name", function.getName());
            summary.put("entryAddress", function.getEntryPoint().toString());
            summary.put("signature", function.getPrototypeString(true, true));
            summary.put("external", function.isExternal());
            summary.put("thunk", function.isThunk());
            summaries.add(summary);
        }
        return summaries;
    }

    private static List<Function> sortedFunctions(Set<Function> functions) {
        List<Function> result = new ArrayList<>(functions);
        Collections.sort(result, new Comparator<Function>() {
            @Override
            public int compare(Function left, Function right) {
                return left.getEntryPoint().compareTo(right.getEntryPoint());
            }
        });
        return result;
    }

    private static <T extends Addressed> List<T> sortedValues(Map<String, T> values) {
        List<T> result = new ArrayList<>(values.values());
        Collections.sort(result, new Comparator<T>() {
            @Override
            public int compare(T left, T right) {
                return left.address().compareTo(right.address());
            }
        });
        return result;
    }

    private String symbolAt(Address address) {
        Symbol symbol = currentProgram.getSymbolTable().getPrimarySymbol(address);
        return symbol == null ? null : symbol.getName(true);
    }

    private static String dataTypeName(Data data) {
        if (data == null) {
            return null;
        }
        DataType type = data.getDataType();
        return type == null ? null : type.getDisplayName();
    }

    private static String functionKey(Function function) {
        return function.getEntryPoint().toString();
    }

    private static String address(Function function) {
        return function.getEntryPoint().toString().toUpperCase(Locale.ROOT);
    }

    private static String formatAddress(Address address) {
        return address == null ? null : address.toString().toUpperCase(Locale.ROOT);
    }

    private static String hex(long value) {
        return "0x" + Long.toUnsignedString(value, 16).toUpperCase(Locale.ROOT);
    }

    private static String safeDirectoryName(Function function) {
        String name = function.getName().replaceAll("[^A-Za-z0-9._-]", "_");
        String entry = address(function).replaceAll("[^A-Za-z0-9._-]", "_");
        if (name.isEmpty()) {
            name = "function";
        }
        return name + "__" + entry;
    }

    private boolean isInsideGhidraProjectStorage(Path exportRoot) {
        if (state.getProject() == null || state.getProject().getProjectLocator() == null) {
            return false;
        }
        File projectDirectory = state.getProject().getProjectLocator().getProjectDir();
        if (projectDirectory == null) {
            return false;
        }
        Path normalizedProjectDirectory = projectDirectory.toPath().toAbsolutePath().normalize();
        return exportRoot.startsWith(normalizedProjectDirectory);
    }

    private static String failureFor(String functionKey, List<ExportFailure> failures) {
        for (ExportFailure failure : failures) {
            if (failure.functionKey.equals(functionKey)) {
                return failure.error;
            }
        }
        return null;
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

    private interface Addressed {
        String address();
    }

    private static final class ThunkResolution {
        final Function resolvedFunction;
        final boolean originalIsThunk;
        final boolean succeeded;
        final int hopCount;
        final String error;

        private ThunkResolution(
                Function resolvedFunction,
                boolean originalIsThunk,
                boolean succeeded,
                int hopCount,
                String error) {
            this.resolvedFunction = resolvedFunction;
            this.originalIsThunk = originalIsThunk;
            this.succeeded = succeeded;
            this.hopCount = hopCount;
            this.error = error;
        }

        static ThunkResolution resolved(Function function, boolean originalIsThunk, int hopCount) {
            return new ThunkResolution(function, originalIsThunk, true, hopCount, null);
        }

        static ThunkResolution failed(String error, int hopCount) {
            return new ThunkResolution(null, true, false, hopCount, error);
        }
    }

    private static final class CallEdge {
        final String callerName;
        final String callerAddress;
        final List<String> callSiteAddresses;
        final String calleeName;
        final String calleeAddress;
        final boolean isThunk;
        final boolean resolutionSucceeded;
        final String resolutionError;
        final int thunkHopCount;
        final String resolvedName;
        final String resolvedAddress;
        final boolean resolvedInternal;
        transient final String resolvedFunctionKey;
        boolean exportEligible;
        boolean exported;
        String exportError;

        CallEdge(
                Function caller,
                Function callee,
                List<String> callSiteAddresses,
                ThunkResolution resolution) {
            this.callerName = caller.getName();
            this.callerAddress = address(caller);
            this.callSiteAddresses = callSiteAddresses;
            this.calleeName = callee.getName();
            this.calleeAddress = address(callee);
            this.isThunk = resolution.originalIsThunk;
            this.resolutionSucceeded = resolution.succeeded;
            this.resolutionError = resolution.error;
            this.thunkHopCount = resolution.hopCount;
            this.resolvedName = resolution.resolvedFunction == null
                ? null
                : resolution.resolvedFunction.getName();
            this.resolvedAddress = resolution.resolvedFunction == null
                ? null
                : address(resolution.resolvedFunction);
            this.resolvedInternal = resolution.resolvedFunction != null &&
                !resolution.resolvedFunction.isExternal() &&
                resolution.resolvedFunction.getBody() != null &&
                !resolution.resolvedFunction.getBody().isEmpty();
            this.resolvedFunctionKey = resolution.resolvedFunction == null
                ? null
                : functionKey(resolution.resolvedFunction);
        }
    }

    private static final class ExportFailure {
        final String functionName;
        final String functionAddress;
        final String error;
        transient final String functionKey;

        ExportFailure(Function function, String error) {
            this.functionName = function.getName();
            this.functionAddress = address(function);
            this.error = error;
            this.functionKey = functionKey(function);
        }
    }

    private static final class IndirectAnalysis {
        final boolean completed;
        final String error;
        final List<IndirectCall> calls;

        private IndirectAnalysis(boolean completed, String error, List<IndirectCall> calls) {
            this.completed = completed;
            this.error = error;
            this.calls = calls;
        }

        static IndirectAnalysis completed(List<IndirectCall> calls) {
            return new IndirectAnalysis(true, null, calls);
        }

        static IndirectAnalysis failed(String error, List<IndirectCall> calls) {
            return new IndirectAnalysis(false, error, calls);
        }
    }

    private static final class IndirectCall {
        final String callSiteAddress;
        String status = "unsupported-pattern";
        String kind = "indirect";
        final int pointerSize;
        String receiverExpression;
        String receiverIdentity;
        String vtableName;
        String vtableAddress;
        Long vtableByteOffset;
        Long vtableSlotIndex;
        final List<Map<String, String>> vtableCandidates = new ArrayList<>();
        final List<InitializerCallDiagnostic> initializerCandidates = new ArrayList<>();
        final List<InitializerProvenance> provenance = new ArrayList<>();
        String targetPointerAddress;
        String slotPointerValue;
        String slotFunctionName;
        String slotFunctionAddress;
        String resolvedFunctionName;
        String resolvedFunctionAddress;
        boolean resolvedInternal;
        int thunkHopCount;
        String resolutionBasis;
        String failureReason;
        final List<String> evidence = new ArrayList<>();
        transient Function resolvedFunction;
        transient String resolvedFunctionKey;
        boolean exportEligible;
        boolean exported;
        String exportError;
        transient Map<String, Object> pcodeDiagnostic;

        IndirectCall(Address callSite, int pointerSize) {
            this.callSiteAddress = formatAddress(callSite);
            this.pointerSize = pointerSize;
        }

        static IndirectCall unsupported(Address callSite, int pointerSize, String reason) {
            IndirectCall result = new IndirectCall(callSite, pointerSize);
            result.fail("unsupported-pattern", reason);
            return result;
        }

        void fail(String status, String reason) {
            this.status = status;
            this.failureReason = reason;
        }

        void resolve(Function function, int thunkHopCount) {
            this.status = "resolved-static-vtable";
            this.resolutionBasis = provenance.isEmpty()
                ? "direct-program-data"
                : "constructor-vptr-store";
            this.failureReason = null;
            this.resolvedFunction = function;
            this.resolvedFunctionKey = functionKey(function);
            this.resolvedFunctionName = function.getName();
            this.resolvedFunctionAddress = address(function);
            this.resolvedInternal = !function.isExternal() && function.getBody() != null &&
                !function.getBody().isEmpty();
            this.thunkHopCount = thunkHopCount;
        }
    }

    private static final class PcodeDiagnosticContext {
        private final IdentityHashMap<Object, String> ids = new IdentityHashMap<>();
        private final Set<Varnode> visitedTreeVarnodes =
            Collections.newSetFromMap(new IdentityHashMap<Varnode, Boolean>());
        private final Set<PcodeOp> visitedTreeOps =
            Collections.newSetFromMap(new IdentityHashMap<PcodeOp, Boolean>());
        private final Set<Varnode> targetTreeVarnodeSet =
            Collections.newSetFromMap(new IdentityHashMap<Varnode, Boolean>());
        private final List<Varnode> targetTreeVarnodes = new ArrayList<>();
        private int nextVarnodeId = 1;
        private int nextOpId = 1;
        private int nextHighVariableId = 1;

        String id(Object object) {
            if (object == null) {
                return null;
            }
            String existing = ids.get(object);
            if (existing != null) {
                return existing;
            }
            String id;
            if (object instanceof Varnode) {
                id = "varnode-" + nextVarnodeId++;
            }
            else if (object instanceof PcodeOp) {
                id = "op-" + nextOpId++;
            }
            else if (object instanceof HighVariable) {
                id = "high-variable-" + nextHighVariableId++;
            }
            else {
                id = "object-" + ids.size();
            }
            ids.put(object, id);
            return id;
        }

        void addTargetTreeVarnode(Varnode varnode) {
            if (targetTreeVarnodeSet.add(varnode)) {
                targetTreeVarnodes.add(varnode);
            }
        }
    }

    private static final class OffsetExpression {
        final Varnode base;
        final long offset;

        OffsetExpression(Varnode base, long offset) {
            this.base = base;
            this.offset = offset;
        }
    }

    private static final class VtableEvidence {
        final String name;
        final Address address;
        final String description;
        final List<InitializerProvenance> provenance = new ArrayList<>();

        VtableEvidence(String name, Address address, String description) {
            this.name = name;
            this.address = address;
            this.description = description;
        }

        Map<String, String> summary() {
            Map<String, String> result = new LinkedHashMap<>();
            result.put("name", name);
            result.put("address", formatAddress(address));
            result.put("evidence", description);
            return result;
        }
    }

    private static final class InitializerCallDiagnostic {
        final String initializerCallSite;
        final int receiverArgumentIndex = 0;
        String receiverArgumentIdentity;
        String calledFunctionName;
        String calledFunctionAddress;
        boolean thunkResolutionSucceeded;
        int thunkHopCount;
        String thunkResolutionError;
        String initializerFunctionName;
        String initializerFunctionAddress;
        String thisParameterIdentity;
        String analysisError;
        final List<VptrStoreDiagnostic> vptrStores = new ArrayList<>();

        InitializerCallDiagnostic(PcodeOp operation) {
            this.initializerCallSite = formatAddress(operation.getSeqnum().getTarget());
        }
    }

    private static final class VptrStoreDiagnostic {
        final String storeAddress;
        String destinationBaseIdentity;
        Long storeOffset;
        boolean throughThis;
        String storedAddress;
        final List<String> symbolNames = new ArrayList<>();
        boolean accepted;
        String acceptedVtableName;
        String rejectionReason;

        VptrStoreDiagnostic(PcodeOp operation) {
            this.storeAddress = formatAddress(operation.getSeqnum().getTarget());
        }
    }

    private static final class InitializerProvenance {
        final String method = "constructor-vptr-store";
        final String initializerCallSite;
        final String calledFunctionName;
        final String calledFunctionAddress;
        final String initializerFunctionName;
        final String initializerFunctionAddress;
        final int receiverArgumentIndex = 0;
        final String vptrStoreAddress;
        final long vptrStoreOffset = 0;

        InitializerProvenance(
                Address initializerCallSite,
                Function calledFunction,
                Function initializerFunction,
                Address vptrStoreAddress) {
            this.initializerCallSite = formatAddress(initializerCallSite);
            this.calledFunctionName = calledFunction.getName();
            this.calledFunctionAddress = address(calledFunction);
            this.initializerFunctionName = initializerFunction.getName();
            this.initializerFunctionAddress = address(initializerFunction);
            this.vptrStoreAddress = formatAddress(vptrStoreAddress);
        }
    }

    private static final class Decompilation {
        final boolean completed;
        final String text;
        final String error;
        transient final HighFunction highFunction;

        private Decompilation(
                boolean completed, String text, String error, HighFunction highFunction) {
            this.completed = completed;
            this.text = text;
            this.error = error;
            this.highFunction = highFunction;
        }

        static Decompilation completed(String text, HighFunction highFunction) {
            return new Decompilation(true, text, null, highFunction);
        }

        static Decompilation failed(String error) {
            return new Decompilation(
                false, "/* Decompilation failed: " + error + " */\n", error, null);
        }
    }

    private static final class ReferenceContext {
        final List<StringContext> strings;
        final List<GlobalContext> globals;

        ReferenceContext(List<StringContext> strings, List<GlobalContext> globals) {
            this.strings = strings;
            this.globals = globals;
        }
    }

    private static final class StringContext implements Addressed {
        final String address;
        final String value;
        final String dataType;
        final Set<String> sourceAddresses = new LinkedHashSet<>();

        StringContext(Data data) {
            this.address = data.getAddress().toString();
            this.value = String.valueOf(data.getValue());
            this.dataType = dataTypeName(data);
        }

        @Override
        public String address() {
            return address;
        }
    }

    private static final class GlobalContext implements Addressed {
        final String address;
        final String symbol;
        final String dataType;
        final Set<String> referenceTypes = new LinkedHashSet<>();
        final Set<String> sourceAddresses = new LinkedHashSet<>();

        GlobalContext(Address address, String symbol, Data data) {
            this.address = address.toString();
            this.symbol = symbol;
            this.dataType = dataTypeName(data);
        }

        @Override
        public String address() {
            return address;
        }
    }

    private static final class ScalarContext {
        final String sourceAddress;
        final String mnemonic;
        final int operandIndex;
        final int bitLength;
        final long signedValue;
        final String unsignedHex;

        ScalarContext(Instruction instruction, int operandIndex, Scalar scalar) {
            this.sourceAddress = instruction.getAddress().toString();
            this.mnemonic = instruction.getMnemonicString();
            this.operandIndex = operandIndex;
            this.bitLength = scalar.bitLength();
            this.signedValue = scalar.getSignedValue();
            this.unsignedHex = "0x" + Long.toUnsignedString(scalar.getUnsignedValue(), 16);
        }
    }
}
