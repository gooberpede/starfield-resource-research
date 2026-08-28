// Export the selected function and its direct internal callee neighbourhood.
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

        Files.createDirectories(neighbourhoodDirectory);
        write(neighbourhoodDirectory.resolve("graph.json"), json(graph(root, edges)));
        write(
            neighbourhoodDirectory.resolve("manifest.json"),
            json(manifest(root, generatedAt, successfullyExported.size(), failures)));

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
        DecompInterface decompiler = new DecompInterface();
        try {
            DecompileOptions options = new DecompileOptions();
            options.grabFromProgram(currentProgram);
            decompiler.setOptions(options);
            if (!decompiler.openProgram(currentProgram)) {
                String message = "Decompiler could not open the current program: " + decompiler.getLastMessage();
                return Decompilation.failed(message);
            }

            DecompileResults results = decompiler.decompileFunction(
                function, DECOMPILE_TIMEOUT_SECONDS, monitor);
            if (!results.decompileCompleted() || results.getDecompiledFunction() == null) {
                String message = results.getErrorMessage();
                if (message == null || message.trim().isEmpty()) {
                    message = "Decompiler returned no pseudocode (possibly timed out).";
                }
                return Decompilation.failed(message);
            }
            return Decompilation.completed(results.getDecompiledFunction().getC());
        }
        catch (RuntimeException exception) {
            return Decompilation.failed(exception.getClass().getSimpleName() + ": " + safeMessage(exception));
        }
        finally {
            decompiler.dispose();
        }
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

    private Map<String, Object> graph(Function root, List<CallEdge> edges) {
        Map<String, Object> rootSummary = new LinkedHashMap<>();
        rootSummary.put("name", root.getName());
        rootSummary.put("address", address(root));

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("schemaVersion", 1);
        result.put("root", rootSummary);
        result.put("edges", edges);
        return result;
    }

    private Map<String, Object> manifest(
            Function root,
            Instant generatedAt,
            int exportedFunctionCount,
            List<ExportFailure> failures) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("schemaVersion", 1);
        result.put("rootFunctionName", root.getName());
        result.put("rootFunctionAddress", address(root));
        result.put("depth", EXPORT_DEPTH);
        result.put("exportedFunctionCount", exportedFunctionCount);
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

    private static final class Decompilation {
        final boolean completed;
        final String text;
        final String error;

        private Decompilation(boolean completed, String text, String error) {
            this.completed = completed;
            this.text = text;
            this.error = error;
        }

        static Decompilation completed(String text) {
            return new Decompilation(true, text, null);
        }

        static Decompilation failed(String error) {
            return new Decompilation(false, "/* Decompilation failed: " + error + " */\n", error);
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
