// Export read-only function evidence for explicit addresses, including in headless mode.
// @category Starfield Research
// @keybinding
// @menupath
// @toolbar

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.Instant;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileOptions;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.Symbol;

public class ExportFunctionsByAddress extends GhidraScript {

    private static final int DECOMPILE_TIMEOUT_SECONDS = 120;
    private static final Gson JSON = new GsonBuilder()
        .setPrettyPrinting()
        .disableHtmlEscaping()
        .serializeNulls()
        .create();

    @Override
    public void run() throws Exception {
        String[] arguments = getScriptArgs();
        if (arguments.length < 2) {
            printerr("Usage: ExportFunctionsByAddress <output-directory> <address> [address ...]");
            return;
        }

        Path root = Paths.get(arguments[0]).toAbsolutePath().normalize();
        Files.createDirectories(root);
        List<Map<String, Object>> manifestFunctions = new ArrayList<>();

        DecompInterface decompiler = new DecompInterface();
        try {
            DecompileOptions options = new DecompileOptions();
            options.grabFromProgram(currentProgram);
            decompiler.setOptions(options);
            if (!decompiler.openProgram(currentProgram)) {
                throw new IllegalStateException("Decompiler could not open program: " + decompiler.getLastMessage());
            }

            for (int index = 1; index < arguments.length; index++) {
                monitor.checkCancelled();
                Address requested = toAddr(arguments[index]);
                Function function = currentProgram.getFunctionManager().getFunctionContaining(requested);
                Map<String, Object> item = new LinkedHashMap<>();
                item.put("requestedAddress", requested.toString());
                if (function == null) {
                    item.put("status", "no-function-containing-address");
                    manifestFunctions.add(item);
                    continue;
                }

                Path directory = root.resolve(safeName(function) + "__" + function.getEntryPoint());
                Files.createDirectories(directory);
                DecompileResults results = decompiler.decompileFunction(
                    function, DECOMPILE_TIMEOUT_SECONDS, monitor);
                boolean decompiled = results.decompileCompleted() && results.getDecompiledFunction() != null;
                String decompiledText = decompiled
                    ? results.getDecompiledFunction().getC()
                    : "/* Decompilation failed: " + results.getErrorMessage() + " */\n";

                write(directory.resolve("decompiled.c"), decompiledText);
                write(directory.resolve("instructions.txt"), instructions(function));
                write(directory.resolve("callers.json"), JSON.toJson(callers(function)) + "\n");
                write(directory.resolve("callees.json"), JSON.toJson(callees(function)) + "\n");
                write(directory.resolve("data-references.json"), JSON.toJson(dataReferences(function)) + "\n");

                Map<String, Object> metadata = new LinkedHashMap<>();
                metadata.put("schemaVersion", 1);
                metadata.put("exportedAtUtc", Instant.now().toString());
                metadata.put("programName", currentProgram.getName());
                metadata.put("md5", currentProgram.getExecutableMD5());
                metadata.put("imageBase", currentProgram.getImageBase().toString());
                metadata.put("requestedAddress", requested.toString());
                metadata.put("functionName", function.getName());
                metadata.put("entryAddress", function.getEntryPoint().toString());
                metadata.put("signature", function.getPrototypeString(true, true));
                metadata.put("bodyMin", function.getBody().getMinAddress().toString());
                metadata.put("bodyMax", function.getBody().getMaxAddress().toString());
                metadata.put("decompilationCompleted", decompiled);
                metadata.put("decompilationError", decompiled ? null : results.getErrorMessage());
                write(directory.resolve("metadata.json"), JSON.toJson(metadata) + "\n");

                item.put("status", "exported");
                item.put("functionName", function.getName());
                item.put("entryAddress", function.getEntryPoint().toString());
                item.put("directory", directory.getFileName().toString());
                manifestFunctions.add(item);
                println("Exported " + function.getName() + " at " + function.getEntryPoint());
            }
        }
        finally {
            decompiler.dispose();
        }

        Map<String, Object> manifest = new LinkedHashMap<>();
        manifest.put("schemaVersion", 1);
        manifest.put("exportedAtUtc", Instant.now().toString());
        manifest.put("programName", currentProgram.getName());
        manifest.put("functions", manifestFunctions);
        write(root.resolve("manifest.json"), JSON.toJson(manifest) + "\n");
    }

    private String instructions(Function function) throws Exception {
        StringBuilder output = new StringBuilder();
        InstructionIterator iterator = currentProgram.getListing().getInstructions(function.getBody(), true);
        while (iterator.hasNext()) {
            monitor.checkCancelled();
            Instruction instruction = iterator.next();
            output.append(instruction.getAddress()).append("  ")
                .append(instruction.toString()).append('\n');
        }
        return output.toString();
    }

    private List<Map<String, Object>> callers(Function function) throws Exception {
        List<Map<String, Object>> output = new ArrayList<>();
        ReferenceIterator iterator = currentProgram.getReferenceManager()
            .getReferencesTo(function.getEntryPoint());
        while (iterator.hasNext()) {
            monitor.checkCancelled();
            Reference reference = iterator.next();
            if (!reference.getReferenceType().isCall()) {
                continue;
            }
            Function caller = currentProgram.getFunctionManager().getFunctionContaining(reference.getFromAddress());
            Map<String, Object> row = new LinkedHashMap<>();
            row.put("callSite", reference.getFromAddress().toString());
            row.put("referenceType", reference.getReferenceType().toString());
            row.put("callerName", caller == null ? null : caller.getName());
            row.put("callerEntry", caller == null ? null : caller.getEntryPoint().toString());
            output.add(row);
        }
        return output;
    }

    private List<Map<String, Object>> callees(Function function) throws Exception {
        List<Map<String, Object>> output = new ArrayList<>();
        InstructionIterator iterator = currentProgram.getListing().getInstructions(function.getBody(), true);
        while (iterator.hasNext()) {
            monitor.checkCancelled();
            Instruction instruction = iterator.next();
            if (!instruction.getFlowType().isCall()) {
                continue;
            }
            Address[] flows = instruction.getFlows();
            if (flows.length == 0) {
                Map<String, Object> row = new LinkedHashMap<>();
                row.put("callSite", instruction.getAddress().toString());
                row.put("instruction", instruction.toString());
                row.put("target", null);
                row.put("calleeName", null);
                row.put("calleeEntry", null);
                output.add(row);
                continue;
            }
            for (Address target : flows) {
                Function callee = currentProgram.getFunctionManager().getFunctionAt(target);
                Map<String, Object> row = new LinkedHashMap<>();
                row.put("callSite", instruction.getAddress().toString());
                row.put("instruction", instruction.toString());
                row.put("target", target.toString());
                row.put("calleeName", callee == null ? null : callee.getName());
                row.put("calleeEntry", callee == null ? null : callee.getEntryPoint().toString());
                output.add(row);
            }
        }
        return output;
    }

    private List<Map<String, Object>> dataReferences(Function function) throws Exception {
        List<Map<String, Object>> output = new ArrayList<>();
        InstructionIterator iterator = currentProgram.getListing().getInstructions(function.getBody(), true);
        AddressSetView body = function.getBody();
        while (iterator.hasNext()) {
            monitor.checkCancelled();
            Instruction instruction = iterator.next();
            for (Reference reference : instruction.getReferencesFrom()) {
                Address target = reference.getToAddress();
                if (!reference.getReferenceType().isData() || target == null || body.contains(target)) {
                    continue;
                }
                Symbol symbol = currentProgram.getSymbolTable().getPrimarySymbol(target);
                Data data = currentProgram.getListing().getDataContaining(target);
                Map<String, Object> row = new LinkedHashMap<>();
                row.put("sourceAddress", instruction.getAddress().toString());
                row.put("referenceType", reference.getReferenceType().toString());
                row.put("targetAddress", target.toString());
                row.put("symbol", symbol == null ? null : symbol.getName(true));
                row.put("dataType", data == null ? null : data.getDataType().getDisplayName());
                row.put("value", data != null && data.hasStringValue() ? data.getValue().toString() : null);
                output.add(row);
            }
        }
        return output;
    }

    private static String safeName(Function function) {
        return function.getName().replaceAll("[^A-Za-z0-9._-]", "_");
    }

    private static void write(Path path, String text) throws Exception {
        Files.write(path, text.getBytes(StandardCharsets.UTF_8));
    }
}
