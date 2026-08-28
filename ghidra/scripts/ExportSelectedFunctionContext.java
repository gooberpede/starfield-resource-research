// Export analysis context for the function containing the current cursor.
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
import java.util.Map;
import java.util.Set;

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
import ghidra.program.model.symbol.Symbol;

public class ExportSelectedFunctionContext extends GhidraScript {

    private static final int DECOMPILE_TIMEOUT_SECONDS = 60;
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

        Function function = currentProgram.getFunctionManager().getFunctionContaining(currentAddress);
        if (function == null) {
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
        Path outputDirectory = exportRoot
            .resolve("functions")
            .resolve(safeDirectoryName(function));
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

        write(outputDirectory.resolve("metadata.json"), json(metadata(function, decompilation)));
        write(outputDirectory.resolve("decompiled.c"), decompilation.text);
        write(outputDirectory.resolve("callers.json"), json(functionSummaries(callers)));
        write(outputDirectory.resolve("callees.json"), json(functionSummaries(callees)));
        write(outputDirectory.resolve("strings.json"), json(references.strings));
        write(outputDirectory.resolve("globals.json"), json(references.globals));
        write(outputDirectory.resolve("constants.json"), json(constants));

        println("Exported " + function.getName() + " to " + outputDirectory.toAbsolutePath());
        if (!decompilation.completed) {
            printerr("Decompilation did not complete: " + decompilation.error);
        }
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
            return Decompilation.failed(exception.getClass().getSimpleName() + ": " + exception.getMessage());
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
                if (scalar == null) {
                    continue;
                }
                constants.add(new ScalarContext(instruction, operand, scalar));
            }
        }
        return constants;
    }

    private Map<String, Object> metadata(Function function, Decompilation decompilation) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("schemaVersion", 1);
        result.put("exportedAtUtc", Instant.now().toString());
        result.put("programName", currentProgram.getName());
        result.put("languageId", currentProgram.getLanguageID().toString());
        result.put("compilerSpecId", currentProgram.getCompilerSpec().getCompilerSpecID().toString());
        result.put("imageBase", currentProgram.getImageBase().toString());
        result.put("cursorAddress", currentAddress.toString());
        result.put("functionName", function.getName());
        result.put("entryAddress", function.getEntryPoint().toString());
        result.put("signature", function.getPrototypeString(true, true));
        result.put("decompilationCompleted", decompilation.completed);
        result.put("decompilationError", decompilation.error);
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

    private static String safeDirectoryName(Function function) {
        String name = function.getName().replaceAll("[^A-Za-z0-9._-]", "_");
        return name.isEmpty() ? function.getEntryPoint().toString() : name;
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

    private static void write(Path path, String contents) throws IOException {
        Files.write(path, contents.getBytes(StandardCharsets.UTF_8));
    }

    private static String json(Object value) {
        return JSON.toJson(value) + "\n";
    }

    private interface Addressed {
        String address();
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
