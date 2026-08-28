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
                    callsBySite.put(key, resolveIndirectCall(decompilation.highFunction, operation));
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

        Map<String, VtableEvidence> candidates = new LinkedHashMap<>();
        VtableEvidence propagated = vtableAtConstant(slotExpression.base);
        if (propagated != null) {
            candidates.put(propagated.address.toString(), propagated);
        }
        if (receiver != null) {
            collectConstructorVtables(highFunction, callOperation, receiver, candidates, result.evidence);
        }

        if (candidates.isEmpty()) {
            result.fail(
                "unresolved-unknown-vtable",
                "No unique vtable could be tied to the receiver from direct program data.");
            return result;
        }
        if (candidates.size() != 1) {
            for (VtableEvidence candidate : candidates.values()) {
                result.vtableCandidates.add(candidate.summary());
            }
            result.fail(
                "unresolved-multiple-candidates",
                "More than one vtable was tied to the receiver; no target was guessed.");
            return result;
        }

        VtableEvidence vtable = candidates.values().iterator().next();
        result.vtableName = vtable.name;
        result.vtableAddress = formatAddress(vtable.address);
        result.evidence.add(vtable.description);

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
            List<String> evidence) throws CancelledException {
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
            if (!firstArgumentAliases(operation, receiverIdentity)) {
                continue;
            }

            Function called = directCalledFunction(operation);
            if (called == null) {
                continue;
            }
            ThunkResolution resolution = resolveThunk(called);
            Function implementation = resolution.resolvedFunction;
            if (implementation == null) {
                continue;
            }

            List<VtableEvidence> assignments = collectVtableAssignments(implementation);
            if (!assignments.isEmpty()) {
                evidence.add(
                    "Earlier direct call " + called.getName() + " at " +
                    formatAddress(operation.getSeqnum().getTarget()) +
                    " receives the indirect-call receiver as its first argument.");
            }
            for (VtableEvidence candidate : assignments) {
                candidates.put(candidate.address.toString(), candidate);
            }
        }
    }

    private boolean firstArgumentAliases(PcodeOp call, String receiverIdentity) {
        return call.getNumInputs() >= 2 &&
            receiverIdentity.equals(variableIdentity(call.getInput(1)));
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

    private List<VtableEvidence> collectVtableAssignments(Function function)
            throws CancelledException {
        Map<String, VtableEvidence> results = new LinkedHashMap<>();
        Decompilation decompilation = decompile(function);
        if (!decompilation.completed || decompilation.highFunction == null) {
            return new ArrayList<>(results.values());
        }

        Iterator<? extends PcodeOp> operations = decompilation.highFunction.getPcodeOps();
        while (operations.hasNext()) {
            monitor.checkCancelled();
            PcodeOp operation = operations.next();
            if (operation.getOpcode() != PcodeOp.STORE || operation.getNumInputs() < 3) {
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
                continue;
            }
            for (Symbol symbol : currentProgram.getSymbolTable().getSymbols(assignedAddress)) {
                String name = symbol.getName(true);
                if (isVtableName(name)) {
                    results.put(
                        assignedAddress.toString(),
                        new VtableEvidence(
                            name,
                            assignedAddress,
                            "Resolved implementation " + function.getName() + " stores vtable " +
                            name + " at " + formatAddress(operation.getSeqnum().getTarget()) + "."));
                    break;
                }
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
        if (current.getHigh() != null && current.getHigh().getName() != null) {
            Varnode representative = current.getHigh().getRepresentative();
            return "high:" + current.getHigh().getName() + ":" +
                (representative == null ? "no-storage" : representative.encodePiece());
        }
        PcodeOp definition = current.getDef();
        if (definition != null && definition.getOpcode() == PcodeOp.PTRSUB &&
                definition.getNumInputs() == 2) {
            Varnode offset = stripCopiesAndCasts(definition.getInput(1));
            if (offset != null && offset.isConstant()) {
                return variableIdentity(definition.getInput(0)) + "+" + hex(offset.getOffset());
            }
        }
        return current.encodePiece();
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
        result.put("schemaVersion", 1);
        result.put("rootFunction", rootSummary);
        result.put("pointerSize", currentProgram.getDefaultPointerSize());
        result.put("analysisCompleted", analysis.completed);
        result.put("analysisError", analysis.error);
        result.put("indirectCalls", analysis.calls);
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
        String vtableName;
        String vtableAddress;
        Long vtableByteOffset;
        Long vtableSlotIndex;
        final List<Map<String, String>> vtableCandidates = new ArrayList<>();
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
            this.resolutionBasis = "direct-program-data";
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
