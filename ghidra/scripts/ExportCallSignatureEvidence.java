// Export raw call-signature evidence for one caller/call-site/callee triple.
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
import java.util.Map;
import java.util.Set;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileOptions;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.data.DataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.pcode.HighFunction;
import ghidra.program.model.pcode.HighParam;
import ghidra.program.model.pcode.HighVariable;
import ghidra.program.model.pcode.PcodeOp;
import ghidra.program.model.pcode.PcodeOpAST;
import ghidra.program.model.pcode.Varnode;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.Symbol;

public class ExportCallSignatureEvidence extends GhidraScript {

    private static final String DEFAULT_CALLER = "1431BC320";
    private static final String DEFAULT_CALL_SITE = "1431BC350";
    private static final String DEFAULT_CALLEE = "140E0AAB0";
    private static final String DEFAULT_WINDOW_START = "1431BC320";
    private static final String DEFAULT_WINDOW_END = "1431BC370";
    private static final int DECOMPILE_TIMEOUT_SECONDS = 120;
    private static final int TREE_DEPTH = 10;
    private static final int USE_DEPTH = 8;
    private static final int MAX_OTHER_CALLERS = 10;
    private static final Gson JSON = new GsonBuilder().setPrettyPrinting()
        .disableHtmlEscaping().serializeNulls().create();

    private final Map<String, Decompilation> decompilations = new LinkedHashMap<>();

    @Override
    public void run() throws Exception {
        if (currentProgram == null) {
            printerr("No program is open.");
            return;
        }

        String[] args = getScriptArgs();
        Path exportRoot;
        if (args.length > 0 && !args[0].trim().isEmpty()) {
            exportRoot = new File(args[0]).toPath().toAbsolutePath().normalize();
        }
        else if (isRunningHeadless()) {
            throw new IllegalArgumentException("Headless use requires an export-root argument.");
        }
        else {
            exportRoot = askDirectory("Choose export root", "Export").toPath()
                .toAbsolutePath().normalize();
        }

        Address callerAddress = address(args, 1, DEFAULT_CALLER);
        Address callSite = address(args, 2, DEFAULT_CALL_SITE);
        Address calleeAddress = address(args, 3, DEFAULT_CALLEE);
        Address windowStart = address(args, 4, DEFAULT_WINDOW_START);
        Address windowEnd = address(args, 5, DEFAULT_WINDOW_END);
        Function caller = currentProgram.getFunctionManager().getFunctionAt(callerAddress);
        Function callee = currentProgram.getFunctionManager().getFunctionAt(calleeAddress);
        if (caller == null || callee == null) {
            throw new IllegalStateException("Required function is undefined: caller=" + callerAddress +
                " callee=" + calleeAddress);
        }

        Path output = exportRoot.resolve("call-signatures")
            .resolve(caller.getName() + "__" + fmt(callerAddress) + "__call_" + fmt(callSite));
        Files.createDirectories(output);

        Decompilation callerDec = decompile(caller);
        Decompilation calleeDec = decompile(callee);
        if (!callerDec.completed || !calleeDec.completed) {
            throw new IllegalStateException("Decompilation failed: caller=" + callerDec.error +
                " callee=" + calleeDec.error);
        }
        PcodeOpAST call = findCall(callerDec.highFunction, callSite);
        if (call == null || call.getOpcode() != PcodeOp.CALLIND) {
            throw new IllegalStateException("No CALLIND high-p-code op at " + callSite);
        }

        List<Map<String, Object>> disassembly = disassembly(windowStart, windowEnd);
        write(output.resolve("callsite-disassembly.txt"), disassemblyText(disassembly));
        write(output.resolve("callsite-disassembly.json"), json(disassembly));
        write(output.resolve("callsite-low-pcode.json"), json(lowPcode(windowStart, windowEnd)));
        write(output.resolve("callsite-high-pcode.json"), json(highCallEvidence(caller, call)));
        write(output.resolve("abi-arguments.json"), json(abiArguments(caller, call, callSite)));
        write(output.resolve("caller-decompiled.c"), callerDec.text);
        write(output.resolve("callee-decompiled.c"), calleeDec.text);

        Address calleeWindowEnd = callee.getEntryPoint().add(0x100);
        List<Map<String, Object>> calleeEntry = disassembly(callee.getEntryPoint(), calleeWindowEnd);
        write(output.resolve("callee-entry-disassembly.txt"), disassemblyText(calleeEntry));
        write(output.resolve("callee-entry-disassembly.json"), json(calleeEntry));
        write(output.resolve("callee-high-pcode.json"), json(highFunctionEvidence(callee, calleeDec.highFunction)));
        write(output.resolve("callee-parameters.json"), json(calleeParameters(callee, calleeDec.highFunction)));
        write(output.resolve("callee-first-use.json"), json(firstUses(callee, calleeDec.highFunction)));
        write(output.resolve("other-callers.json"), json(otherCallers(callee)));
        write(output.resolve("slot-comparison.json"), json(slotEvidence(calleeAddress)));
        write(output.resolve("manifest.json"), json(manifest(caller, callSite, callee, output)));
        println("Exported call-signature evidence to " + output);
    }

    private Address address(String[] args, int index, String fallback) throws Exception {
        String text = index < args.length && !args[index].trim().isEmpty() ? args[index] : fallback;
        text = text.startsWith("0x") || text.startsWith("0X") ? text.substring(2) : text;
        Address result = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(text);
        if (result == null) throw new IllegalArgumentException("Invalid address: " + text);
        return result;
    }

    private Decompilation decompile(Function function) {
        String key = function.getEntryPoint().toString();
        if (decompilations.containsKey(key)) return decompilations.get(key);
        DecompInterface decompiler = new DecompInterface();
        try {
            decompiler.setOptions(new DecompileOptions());
            decompiler.toggleCCode(true);
            decompiler.toggleSyntaxTree(true);
            if (!decompiler.openProgram(currentProgram)) {
                return cache(key, Decompilation.failed(decompiler.getLastMessage()));
            }
            DecompileResults results = decompiler.decompileFunction(
                function, DECOMPILE_TIMEOUT_SECONDS, monitor);
            if (!results.decompileCompleted() || results.getHighFunction() == null) {
                return cache(key, Decompilation.failed(results.getErrorMessage()));
            }
            return cache(key, Decompilation.completed(
                results.getDecompiledFunction().getC(), results.getHighFunction()));
        }
        catch (Exception e) {
            return cache(key, Decompilation.failed(e.getClass().getSimpleName() + ": " + e.getMessage()));
        }
        finally {
            decompiler.dispose();
        }
    }

    private Decompilation cache(String key, Decompilation value) {
        decompilations.put(key, value);
        return value;
    }

    private PcodeOpAST findCall(HighFunction highFunction, Address address) {
        Iterator<PcodeOpAST> operations = highFunction.getPcodeOps(address);
        while (operations.hasNext()) {
            PcodeOpAST operation = operations.next();
            if (operation.getOpcode() == PcodeOp.CALLIND || operation.getOpcode() == PcodeOp.CALL) {
                return operation;
            }
        }
        return null;
    }

    private List<Map<String, Object>> disassembly(Address start, Address end) throws Exception {
        List<Map<String, Object>> result = new ArrayList<>();
        AddressSet set = new AddressSet(start, end);
        InstructionIterator instructions = currentProgram.getListing().getInstructions(set, true);
        while (instructions.hasNext()) {
            monitor.checkCancelled();
            Instruction instruction = instructions.next();
            Map<String, Object> row = new LinkedHashMap<>();
            row.put("address", fmt(instruction.getAddress()));
            row.put("bytes", hex(instruction.getBytes()));
            row.put("mnemonic", instruction.getMnemonicString());
            List<String> operands = new ArrayList<>();
            for (int i = 0; i < instruction.getNumOperands(); i++) {
                operands.add(instruction.getDefaultOperandRepresentation(i));
            }
            row.put("operands", operands);
            row.put("text", instruction.toString());
            row.put("flowType", instruction.getFlowType().toString());
            result.add(row);
        }
        return result;
    }

    private String disassemblyText(List<Map<String, Object>> rows) {
        StringBuilder text = new StringBuilder();
        for (Map<String, Object> row : rows) {
            text.append(String.format("%-12s %-30s %-9s %s%n", row.get("address"), row.get("bytes"),
                row.get("mnemonic"), join((List<?>) row.get("operands"), ", ")));
        }
        return text.toString();
    }

    private List<Map<String, Object>> lowPcode(Address start, Address end) throws Exception {
        List<Map<String, Object>> result = new ArrayList<>();
        InstructionIterator instructions = currentProgram.getListing().getInstructions(
            new AddressSet(start, end), true);
        while (instructions.hasNext()) {
            Instruction instruction = instructions.next();
            Map<String, Object> item = new LinkedHashMap<>();
            item.put("instructionAddress", fmt(instruction.getAddress()));
            item.put("instruction", instruction.toString());
            List<Map<String, Object>> operations = new ArrayList<>();
            for (PcodeOp operation : instruction.getPcode()) operations.add(op(operation));
            item.put("operations", operations);
            result.add(item);
        }
        return result;
    }

    private Map<String, Object> highCallEvidence(Function caller, PcodeOpAST call) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("caller", function(caller));
        result.put("rule", "CALLIND input 0 is target; inputs 1..N are actual arguments");
        result.put("call", op(call));
        result.put("target", callInput(call, 0, "target", -1));
        List<Map<String, Object>> arguments = new ArrayList<>();
        for (int i = 1; i < call.getNumInputs(); i++) {
            arguments.add(callInput(call, i, "argument", i - 1));
        }
        result.put("arguments", arguments);
        return result;
    }

    private Map<String, Object> callInput(PcodeOp call, int inputIndex, String role, int argumentIndex) {
        Varnode input = call.getInput(inputIndex);
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("inputIndex", inputIndex);
        result.put("role", role);
        result.put("argumentIndex", argumentIndex < 0 ? null : argumentIndex);
        result.put("varnode", varnode(input));
        result.put("definitionTree", definitionTree(input, 0,
            Collections.newSetFromMap(new IdentityHashMap<Varnode, Boolean>())));
        return result;
    }

    private Map<String, Object> abiArguments(Function caller, PcodeOp call, Address callSite) {
        String[] registers = { "RCX", "RDX", "R8", "R9" };
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("abi", currentProgram.getCompilerSpec().getCompilerSpecID().toString());
        result.put("callingConvention", caller.getCallingConventionName());
        result.put("callSite", fmt(callSite));
        result.put("actualArgumentCount", call.getNumInputs() - 1);
        List<Map<String, Object>> args = new ArrayList<>();
        for (int i = 1; i < call.getNumInputs(); i++) {
            Map<String, Object> item = callInput(call, i, "argument", i - 1);
            item.put("windowsX64Storage", i <= 4 ? registers[i - 1] : "stack[return-address+" +
                String.format("0x%X", 0x28 + (i - 5) * 8) + "]");
            item.put("confidence", "machine-ABI plus high-p-code");
            args.add(item);
        }
        result.put("arguments", args);
        List<Map<String, Object>> absent = new ArrayList<>();
        for (int i = call.getNumInputs(); i <= 4; i++) {
            Map<String, Object> item = new LinkedHashMap<>();
            item.put("register", registers[i - 1]);
            item.put("status", "not-an-actual-argument");
            absent.add(item);
        }
        result.put("unusedArgumentRegisters", absent);
        result.put("stackArguments", call.getNumInputs() <= 5 ? Collections.emptyList() :
            args.subList(4, args.size()));
        result.put("note", "Register definitions are preserved in callsite disassembly and low p-code; " +
            "argument expressions are preserved here from high p-code.");
        return result;
    }

    private Map<String, Object> highFunctionEvidence(Function function, HighFunction highFunction) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("function", function(function));
        List<Map<String, Object>> operations = new ArrayList<>();
        Iterator<PcodeOpAST> iterator = highFunction.getPcodeOps();
        while (iterator.hasNext()) operations.add(op(iterator.next()));
        result.put("operations", operations);
        return result;
    }

    private Map<String, Object> calleeParameters(Function function, HighFunction highFunction) {
        String[] registers = { "RCX", "RDX", "R8", "R9" };
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("function", function(function));
        result.put("callingConvention", function.getCallingConventionName());
        result.put("signatureSource", function.getSignatureSource().toString());
        result.put("hasCustomVariableStorage", function.hasCustomVariableStorage());
        result.put("functionParameterCount", function.getParameterCount());
        result.put("highParameterCount", highFunction.getLocalSymbolMap().getNumParams());
        List<Map<String, Object>> parameters = new ArrayList<>();
        int count = Math.max(function.getParameterCount(), highFunction.getLocalSymbolMap().getNumParams());
        Parameter[] listingParameters = function.getParameters();
        for (int i = 0; i < count; i++) {
            Map<String, Object> item = new LinkedHashMap<>();
            item.put("index", i);
            item.put("windowsX64Storage", i < 4 ? registers[i] : "stack[return-address+" +
                String.format("0x%X", 0x28 + (i - 4) * 8) + "]");
            if (i < listingParameters.length) {
                Parameter parameter = listingParameters[i];
                item.put("listingName", parameter.getName());
                item.put("listingOrdinal", parameter.getOrdinal());
                item.put("listingStorage", parameter.getVariableStorage().toString());
                item.put("listingDataType", datatype(parameter.getDataType()));
                item.put("listingSource", parameter.getSource().toString());
            }
            HighParam high = highParam(highFunction, i);
            item.put("highParameter", high == null ? null : highVariable(high));
            parameters.add(item);
        }
        result.put("parameters", parameters);
        return result;
    }

    private Map<String, Object> firstUses(Function function, HighFunction highFunction) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("function", function(function));
        List<Map<String, Object>> parameters = new ArrayList<>();
        int count = highFunction.getLocalSymbolMap().getNumParams();
        for (int i = 0; i < count; i++) {
            HighParam parameter = highParam(highFunction, i);
            Map<String, Object> item = new LinkedHashMap<>();
            item.put("index", i);
            item.put("parameter", highVariable(parameter));
            List<UseRecord> uses = traceUses(parameter);
            Collections.sort(uses, UseRecord.ORDER);
            item.put("firstInstructionUse", uses.isEmpty() ? null : uses.get(0).record);
            List<Map<String, Object>> records = new ArrayList<>();
            for (UseRecord use : uses) records.add(use.record);
            item.put("boundedUses", records);
            parameters.add(item);
        }
        result.put("parameters", parameters);
        return result;
    }

    private List<UseRecord> traceUses(HighVariable variable) {
        List<UseRecord> result = new ArrayList<>();
        Set<Varnode> visited = Collections.newSetFromMap(new IdentityHashMap<Varnode, Boolean>());
        Set<PcodeOp> emitted = Collections.newSetFromMap(new IdentityHashMap<PcodeOp, Boolean>());
        for (Varnode instance : variable.getInstances()) {
            traceUses(instance, 0, visited, emitted, result);
        }
        return result;
    }

    private void traceUses(Varnode value, int depth, Set<Varnode> visited, Set<PcodeOp> emitted,
            List<UseRecord> result) {
        if (value == null || depth > USE_DEPTH || !visited.add(value)) return;
        Iterator<PcodeOp> descendants = value.getDescendants();
        while (descendants.hasNext()) {
            PcodeOp use = descendants.next();
            if (emitted.add(use)) {
                Map<String, Object> record = op(use);
                record.put("depth", depth);
                List<Integer> positions = new ArrayList<>();
                for (int i = 0; i < use.getNumInputs(); i++) if (use.getInput(i) == value) positions.add(i);
                record.put("inputPositions", positions);
                result.add(new UseRecord(use, record));
            }
            if (use.getOutput() != null && propagates(use.getOpcode())) {
                traceUses(use.getOutput(), depth + 1, visited, emitted, result);
            }
        }
    }

    private boolean propagates(int opcode) {
        return opcode == PcodeOp.COPY || opcode == PcodeOp.CAST || opcode == PcodeOp.INT_ZEXT ||
            opcode == PcodeOp.INT_SEXT || opcode == PcodeOp.INT_ADD || opcode == PcodeOp.PTRADD ||
            opcode == PcodeOp.PTRSUB || opcode == PcodeOp.MULTIEQUAL || opcode == PcodeOp.SUBPIECE;
    }

    private Map<String, Object> otherCallers(Function callee) throws Exception {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("callee", function(callee));
        List<Function> callers = new ArrayList<>(callee.getCallingFunctions(monitor));
        Collections.sort(callers, Comparator.comparing(f -> f.getEntryPoint().toString()));
        result.put("totalGhidraCallingFunctions", callers.size());
        List<Map<String, Object>> records = new ArrayList<>();
        for (Function caller : callers) {
            if (records.size() >= MAX_OTHER_CALLERS) break;
            Decompilation dec = decompile(caller);
            if (!dec.completed) continue;
            Iterator<PcodeOpAST> operations = dec.highFunction.getPcodeOps();
            while (operations.hasNext() && records.size() < MAX_OTHER_CALLERS) {
                PcodeOpAST operation = operations.next();
                if (operation.getOpcode() != PcodeOp.CALL || operation.getNumInputs() == 0) continue;
                Address target = addressOf(operation.getInput(0));
                if (!callee.getEntryPoint().equals(target)) continue;
                Map<String, Object> record = new LinkedHashMap<>();
                record.put("caller", function(caller));
                record.put("callSite", fmt(operation.getSeqnum().getTarget()));
                record.put("call", op(operation));
                List<Map<String, Object>> arguments = new ArrayList<>();
                for (int i = 1; i < operation.getNumInputs(); i++) {
                    arguments.add(callInput(operation, i, "argument", i - 1));
                }
                record.put("arguments", arguments);
                record.put("decompiledC", dec.text);
                records.add(record);
            }
        }
        result.put("representativeCalls", records);
        result.put("limit", MAX_OTHER_CALLERS);
        result.put("sameInitializerSlotCalls", sameInitializerSlotCalls());
        return result;
    }

    private List<Map<String, Object>> sameInitializerSlotCalls() throws Exception {
        List<Map<String, Object>> result = new ArrayList<>();
        Address thunkAddress = currentProgram.getAddressFactory().getDefaultAddressSpace()
            .getAddress("1400ED0F9");
        Function thunk = currentProgram.getFunctionManager().getFunctionAt(thunkAddress);
        Function initializer = resolveThunk(thunk);
        if (initializer == null) return result;
        Set<Function> callers = new LinkedHashSet<>();
        callers.addAll(thunk.getCallingFunctions(monitor));
        callers.addAll(initializer.getCallingFunctions(monitor));
        List<Function> ordered = new ArrayList<>(callers);
        Collections.sort(ordered, new Comparator<Function>() {
            @Override public int compare(Function left, Function right) {
                boolean leftTarget = fmt(left.getEntryPoint()).equals(DEFAULT_CALLER);
                boolean rightTarget = fmt(right.getEntryPoint()).equals(DEFAULT_CALLER);
                if (leftTarget != rightTarget) return leftTarget ? -1 : 1;
                return left.getEntryPoint().compareTo(right.getEntryPoint());
            }
        });
        for (Function caller : ordered) {
            if (result.size() >= MAX_OTHER_CALLERS) break;
            Decompilation dec = decompile(caller);
            if (!dec.completed) continue;
            Iterator<PcodeOpAST> operations = dec.highFunction.getPcodeOps();
            while (operations.hasNext() && result.size() < MAX_OTHER_CALLERS) {
                PcodeOpAST operation = operations.next();
                if (operation.getOpcode() != PcodeOp.CALLIND || operation.getNumInputs() < 2 ||
                        !isFixedSlotTarget(operation.getInput(0), 0x50)) {
                    continue;
                }
                Map<String, Object> record = new LinkedHashMap<>();
                record.put("caller", function(caller));
                record.put("initializerThunk", function(thunk));
                record.put("initializerResolved", function(initializer));
                record.put("callSite", fmt(operation.getSeqnum().getTarget()));
                record.put("call", op(operation));
                List<Map<String, Object>> arguments = new ArrayList<>();
                for (int i = 1; i < operation.getNumInputs(); i++) {
                    arguments.add(callInput(operation, i, "argument", i - 1));
                }
                record.put("arguments", arguments);
                record.put("decompiledC", dec.text);
                result.add(record);
            }
        }
        return result;
    }

    private boolean isFixedSlotTarget(Varnode target, long expectedOffset) {
        PcodeOp load = target == null ? null : target.getDef();
        if (load == null || load.getOpcode() != PcodeOp.LOAD || load.getNumInputs() < 2) return false;
        Varnode pointer = stripWrappers(load.getInput(1));
        PcodeOp addition = pointer == null ? null : pointer.getDef();
        if (addition == null || (addition.getOpcode() != PcodeOp.INT_ADD &&
                addition.getOpcode() != PcodeOp.PTRSUB) || addition.getNumInputs() != 2) return false;
        return (addition.getInput(0).isConstant() && addition.getInput(0).getOffset() == expectedOffset) ||
            (addition.getInput(1).isConstant() && addition.getInput(1).getOffset() == expectedOffset);
    }

    private Varnode stripWrappers(Varnode value) {
        Set<Varnode> visited = Collections.newSetFromMap(new IdentityHashMap<Varnode, Boolean>());
        Varnode current = value;
        while (current != null && visited.add(current)) {
            PcodeOp definition = current.getDef();
            if (definition == null || definition.getNumInputs() < 1 ||
                    (definition.getOpcode() != PcodeOp.COPY && definition.getOpcode() != PcodeOp.CAST &&
                     definition.getOpcode() != PcodeOp.INT_ZEXT && definition.getOpcode() != PcodeOp.INT_SEXT)) {
                return current;
            }
            current = definition.getInput(0);
        }
        return current;
    }

    private Map<String, Object> slotEvidence(Address calleeAddress) throws Exception {
        Map<String, Object> result = new LinkedHashMap<>();
        List<Map<String, Object>> matches = new ArrayList<>();
        Symbol targetVtable = null;
        List<Symbol> componentVtables = new ArrayList<>();
        String[] componentNames = { "TESContainer::vftable", "TESFullName::vftable",
            "TESDescription::vftable", "TESModel::vftable", "BGSKeywordForm::vftable",
            "BGSPropertySheet::vftable", "BGSPreviewTransform::vftable",
            "BGSDestructibleObjectForm::vftable", "BGSSkinForm::vftable",
            "TESSpellList::vftable" };
        for (Symbol symbol : currentProgram.getSymbolTable().getAllSymbols(true)) {
            String name = symbol.getName(true);
            if ("TESContainer::vftable".equals(name)) {
                targetVtable = symbol;
            }
            if (name != null) for (String componentName : componentNames) {
                if (componentName.equals(name)) componentVtables.add(symbol);
            }
        }
        if (targetVtable != null) {
            Address slot = targetVtable.getAddress().add(0x50);
            long pointer = currentProgram.getMemory().getLong(slot);
            Map<String, Object> item = new LinkedHashMap<>();
            item.put("vtableName", targetVtable.getName(true));
            item.put("vtableAddress", fmt(targetVtable.getAddress()));
            item.put("slotIndex", 10);
            item.put("slotByteOffset", 0x50);
            item.put("slotAddress", fmt(slot));
            item.put("rawPointer", String.format("%016X", pointer));
            Function rawFunction = currentProgram.getFunctionManager().getFunctionAt(
                currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(pointer));
            Function resolvedFunction = resolveThunk(rawFunction);
            item.put("rawFunction", rawFunction == null ? null : function(rawFunction));
            item.put("resolvedFunction", resolvedFunction == null ? null : function(resolvedFunction));
            item.put("matchesResolvedCallee", resolvedFunction != null &&
                resolvedFunction.getEntryPoint().equals(calleeAddress));
            matches.add(item);
        }
        result.put("tesContainerSlot10", matches);
        List<Map<String, Object>> equivalentSlots = new ArrayList<>();
        for (Symbol symbol : componentVtables) {
            Address slot = symbol.getAddress().add(0x50);
            long pointer = currentProgram.getMemory().getLong(slot);
            Address pointerAddress = currentProgram.getAddressFactory().getDefaultAddressSpace()
                .getAddress(pointer);
            Function slotFunction = currentProgram.getFunctionManager().getFunctionAt(pointerAddress);
            Function resolved = resolveThunk(slotFunction);
            Map<String, Object> item = new LinkedHashMap<>();
            item.put("vtableName", symbol.getName(true));
            item.put("vtableAddress", fmt(symbol.getAddress()));
            item.put("slotAddress", fmt(slot));
            item.put("slotIndex", 10);
            item.put("slotByteOffset", 0x50);
            item.put("rawPointer", fmt(pointerAddress));
            item.put("slotFunction", slotFunction == null ? null : function(slotFunction));
            item.put("resolvedFunction", resolved == null ? null : function(resolved));
            equivalentSlots.add(item);
        }
        result.put("representativeComponentSlot10", equivalentSlots);
        List<Map<String, Object>> references = new ArrayList<>();
        ReferenceIterator iterator = currentProgram.getReferenceManager().getReferencesTo(calleeAddress);
        while (iterator.hasNext()) {
            Reference reference = iterator.next();
            Map<String, Object> item = new LinkedHashMap<>();
            item.put("from", fmt(reference.getFromAddress()));
            item.put("type", reference.getReferenceType().toString());
            Symbol primary = currentProgram.getSymbolTable().getPrimarySymbol(reference.getFromAddress());
            item.put("fromSymbol", primary == null ? null : primary.getName(true));
            references.add(item);
        }
        result.put("referencesToCallee", references);
        result.put("classification", "mechanical slot identity only; no semantic slot name is inferred");
        return result;
    }

    private Function resolveThunk(Function function) {
        if (function == null) return null;
        Set<Address> visited = new LinkedHashSet<>();
        Function current = function;
        while (current != null && current.isThunk() && visited.add(current.getEntryPoint())) {
            current = current.getThunkedFunction(false);
        }
        return current;
    }

    private Map<String, Object> manifest(Function caller, Address callSite, Function callee, Path output) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("schemaVersion", 1);
        result.put("generatedAt", Instant.now().toString());
        result.put("program", currentProgram.getName());
        result.put("executablePath", currentProgram.getExecutablePath());
        result.put("caller", function(caller));
        result.put("callSite", fmt(callSite));
        result.put("callee", function(callee));
        result.put("outputDirectory", output.toString());
        result.put("readOnly", true);
        result.put("modifiesProgram", false);
        result.put("notes", "The script starts no transaction and performs no symbol, type, signature, comment, label, memory, or analysis-state writes.");
        return result;
    }

    private Map<String, Object> definitionTree(Varnode value, int depth, Set<Varnode> visited) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("varnode", varnode(value));
        if (value == null) return result;
        if (depth >= TREE_DEPTH) { result.put("stopReason", "maximum-depth"); return result; }
        if (!visited.add(value)) { result.put("stopReason", "visited-varnode"); return result; }
        PcodeOp definition = value.getDef();
        if (definition == null) { result.put("stopReason", "no-definition"); return result; }
        result.put("definition", op(definition));
        List<Map<String, Object>> inputs = new ArrayList<>();
        for (int i = 0; i < definition.getNumInputs(); i++) {
            Map<String, Object> item = definitionTree(definition.getInput(i), depth + 1, visited);
            item.put("inputIndex", i);
            inputs.add(item);
        }
        result.put("inputs", inputs);
        return result;
    }

    private Map<String, Object> op(PcodeOp operation) {
        if (operation == null) return null;
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("sequenceAddress", fmt(operation.getSeqnum().getTarget()));
        result.put("sequenceOrder", operation.getSeqnum().getOrder());
        result.put("mnemonic", operation.getMnemonic());
        if ((operation.getOpcode() == PcodeOp.CALL || operation.getOpcode() == PcodeOp.CALLIND) &&
                operation.getNumInputs() > 0) {
            Address targetAddress = operation.getOpcode() == PcodeOp.CALL
                ? addressOf(operation.getInput(0)) : null;
            Function target = targetAddress == null ? null :
                currentProgram.getFunctionManager().getFunctionAt(targetAddress);
            Function resolved = resolveThunk(target);
            result.put("directTarget", target == null ? null : function(target));
            result.put("resolvedTarget", resolved == null ? null : function(resolved));
        }
        result.put("output", varnode(operation.getOutput()));
        List<Map<String, Object>> inputs = new ArrayList<>();
        for (int i = 0; i < operation.getNumInputs(); i++) {
            Map<String, Object> item = varnode(operation.getInput(i));
            item.put("inputIndex", i);
            inputs.add(item);
        }
        result.put("inputs", inputs);
        return result;
    }

    private Map<String, Object> varnode(Varnode value) {
        if (value == null) return null;
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("text", value.toString());
        result.put("address", value.getAddress() == null ? null : value.getAddress().toString());
        result.put("addressSpace", value.getAddress() == null ? null : value.getAddress().getAddressSpace().getName());
        result.put("offset", value.getOffset());
        result.put("offsetHex", String.format("0x%X", value.getOffset()));
        result.put("size", value.getSize());
        result.put("isAddress", value.isAddress());
        result.put("isConstant", value.isConstant());
        result.put("isRegister", value.isRegister());
        result.put("isUnique", value.isUnique());
        HighVariable high = value.getHigh();
        result.put("highVariable", high == null ? null : highVariable(high));
        return result;
    }

    private Map<String, Object> highVariable(HighVariable variable) {
        if (variable == null) return null;
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("class", variable.getClass().getSimpleName());
        result.put("name", variable.getName());
        result.put("dataType", datatype(variable.getDataType()));
        result.put("representative", simpleVarnode(variable.getRepresentative()));
        result.put("instanceCount", variable.getInstances().length);
        if (variable.getSymbol() != null) {
            result.put("symbolId", variable.getSymbol().getId());
            result.put("symbolName", variable.getSymbol().getName());
            result.put("symbolStorage", variable.getSymbol().getStorage().toString());
        }
        return result;
    }

    private Map<String, Object> simpleVarnode(Varnode value) {
        if (value == null) return null;
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("text", value.toString());
        result.put("address", value.getAddress() == null ? null : value.getAddress().toString());
        result.put("size", value.getSize());
        return result;
    }

    private Map<String, Object> datatype(DataType type) {
        if (type == null) return null;
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("name", type.getName());
        result.put("displayName", type.getDisplayName());
        result.put("path", type.getPathName());
        result.put("length", type.getLength());
        result.put("class", type.getClass().getSimpleName());
        return result;
    }

    private Map<String, Object> function(Function function) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("name", function.getName());
        result.put("fullName", function.getName(true));
        result.put("address", fmt(function.getEntryPoint()));
        result.put("callingConvention", function.getCallingConventionName());
        result.put("parameterCount", function.getParameterCount());
        result.put("signature", function.getSignature().getPrototypeString());
        return result;
    }

    private HighParam highParam(HighFunction function, int index) {
        if (index < 0 || index >= function.getLocalSymbolMap().getNumParams()) return null;
        return function.getLocalSymbolMap().getParam(index);
    }

    private Address addressOf(Varnode value) {
        if (value == null || (!value.isAddress() && !value.isConstant())) return null;
        return currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(value.getOffset());
    }

    private static String fmt(Address address) {
        return address == null ? null : address.toString().toUpperCase();
    }

    private static String hex(byte[] bytes) {
        StringBuilder result = new StringBuilder();
        for (byte value : bytes) result.append(String.format("%02X", value & 0xff));
        return result.toString();
    }

    private static String join(List<?> values, String separator) {
        StringBuilder result = new StringBuilder();
        for (int i = 0; i < values.size(); i++) {
            if (i > 0) result.append(separator);
            result.append(String.valueOf(values.get(i)));
        }
        return result.toString();
    }

    private static String json(Object value) { return JSON.toJson(value) + "\n"; }

    private static void write(Path path, String contents) throws IOException {
        Files.write(path, contents.getBytes(StandardCharsets.UTF_8));
    }

    private static final class Decompilation {
        final boolean completed;
        final String text;
        final String error;
        final HighFunction highFunction;
        private Decompilation(boolean completed, String text, String error, HighFunction highFunction) {
            this.completed = completed; this.text = text; this.error = error; this.highFunction = highFunction;
        }
        static Decompilation completed(String text, HighFunction highFunction) {
            return new Decompilation(true, text, null, highFunction);
        }
        static Decompilation failed(String error) {
            return new Decompilation(false, "/* decompilation failed */\n", error, null);
        }
    }

    private static final class UseRecord {
        static final Comparator<UseRecord> ORDER = new Comparator<UseRecord>() {
            @Override public int compare(UseRecord left, UseRecord right) {
                int address = left.operation.getSeqnum().getTarget().compareTo(right.operation.getSeqnum().getTarget());
                return address != 0 ? address : Integer.compare(
                    left.operation.getSeqnum().getOrder(), right.operation.getSeqnum().getOrder());
            }
        };
        final PcodeOp operation;
        final Map<String, Object> record;
        UseRecord(PcodeOp operation, Map<String, Object> record) {
            this.operation = operation; this.record = record;
        }
    }
}
