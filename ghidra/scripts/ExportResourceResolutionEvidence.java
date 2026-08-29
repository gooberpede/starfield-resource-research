// Export the static evidence and runtime capture contract for resource resolution.
// @category Starfield Research
// @keybinding
// @menupath
// @toolbar

import java.io.File;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Iterator;
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
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.pcode.HighFunction;
import ghidra.program.model.pcode.PcodeOp;
import ghidra.program.model.pcode.PcodeOpAST;
import ghidra.program.model.pcode.Varnode;

/**
 * This script deliberately does not claim to capture live CK heap contents.
 * It exports the exact static call sites, ABI contract, container record layout,
 * and output schemas needed by a debugger/runtime observer.  Empty stage files
 * state that runtime evidence is required instead of presenting static memory as
 * a live observation.
 */
public class ExportResourceResolutionEvidence extends GhidraScript {

    private static final String DEFAULT_CALLER = "1431BC320";
    private static final String DEFAULT_COPY_CALL = "1431BC350";
    private static final String DEFAULT_RESOLVER = "140E457B0";
    private static final String DEFAULT_CASE = "runtime-capture-template";
    private static final int DECOMPILE_TIMEOUT_SECONDS = 120;
    private static final Gson JSON = new GsonBuilder().setPrettyPrinting()
        .disableHtmlEscaping().serializeNulls().create();

    @Override
    public void run() throws Exception {
        if (currentProgram == null) {
            printerr("No program is open.");
            return;
        }

        String[] args = getScriptArgs();
        Path exportRoot = exportRoot(args);
        String caseName = textArg(args, 1, DEFAULT_CASE);
        Address callerAddress = addressArg(args, 2, DEFAULT_CALLER);
        Address copyCallAddress = addressArg(args, 3, DEFAULT_COPY_CALL);
        Address resolverAddress = addressArg(args, 4, DEFAULT_RESOLVER);
        int maximumDepth = intArg(args, 5, 8);
        String expectedBiom = optionalArg(args, 6);
        String expectedRsgd = optionalArg(args, 7);
        String expectedFamily = optionalArg(args, 8);

        Function caller = requireFunction(callerAddress, "caller");
        Function resolver = requireFunction(resolverAddress, "resolver");
        Instruction copyCall = currentProgram.getListing().getInstructionAt(copyCallAddress);
        if (copyCall == null || !isCall(copyCall)) {
            throw new IllegalStateException("No call instruction at copy site " + copyCallAddress);
        }
        Instruction resolverCall = findCallTo(caller, resolver);
        if (resolverCall == null) {
            throw new IllegalStateException("No call from " + caller.getName() + " to " +
                resolver.getName() + " (including thunks)");
        }
        Instruction afterResolver = resolverCall.getNext();
        if (afterResolver == null) {
            throw new IllegalStateException("Resolver call has no fall-through instruction");
        }

        Decompilation callerDec = decompile(caller);
        Decompilation resolverDec = decompile(resolver);
        if (!callerDec.completed || !resolverDec.completed) {
            throw new IllegalStateException("Decompilation failed: caller=" + callerDec.error +
                " resolver=" + resolverDec.error);
        }

        Path output = exportRoot.resolve("resource-resolution").resolve(safe(caseName));
        Files.createDirectories(output);

        Map<String, Object> context = context(caseName, caller, copyCall, resolver,
            resolverCall, afterResolver, maximumDepth);
        context.put("expectedBIOM", expectedBiom);
        context.put("expectedRSGD", expectedRsgd);
        context.put("expectedSelectedFamily", expectedFamily);
        Map<String, Object> selector = selector(callerDec.highFunction, resolverCall);
        Map<String, Object> layout = layout();
        Map<String, Object> plan = capturePlan(copyCall, resolverCall, afterResolver, maximumDepth);

        writeJson(output.resolve("context.json"), context);
        writeJson(output.resolve("static-layout.json"), layout);
        writeJson(output.resolve("capture-plan.json"), plan);
        writeJson(output.resolve("selector.json"), selector);
        write(output.resolve("caller-decompiled.c"), callerDec.text);
        write(output.resolve("resolver-decompiled.c"), resolverDec.text);
        writeJson(output.resolve("caller-listing.json"), listing(caller));
        writeJson(output.resolve("resolver-entry-listing.json"), listingWindow(resolver.getEntryPoint(), 0x100));

        writeJson(output.resolve("source-container.json"), emptyStage("source-component",
            "Capture R8 at the copy call before execution, then enumerate R8+0x40/+0x48."));
        writeJson(output.resolve("pre-resolution-container.json"), emptyStage("pre-resolution",
            "Capture RCX at resolver entry; this is the copied temporary TESContainer."));
        writeJson(output.resolve("post-resolution-container.json"), emptyStage("post-resolution",
            "At resolver return, dereference the saved resolver-entry RDX output slot."));
        writeJson(output.resolve("source-vs-pre-diff.json"), emptyDiff("source-component", "pre-resolution"));
        writeJson(output.resolve("pre-vs-post-diff.json"), emptyDiff("pre-resolution", "post-resolution"));
        writeJson(output.resolve("leveled-tree.json"), emptyRecursive("TESLevItem", maximumDepth));
        writeJson(output.resolve("ires-leaves.json"), emptyRecursive("IRES", maximumDepth));
        writeJson(output.resolve("rsgd-correlation.json"),
            emptyCorrelation(expectedBiom, expectedRsgd, expectedFamily));
        write(output.resolve("family-topology-analysis.md"), familyTopologyTemplate(caseName));

        List<String> files = new ArrayList<>();
        String[] names = { "context.json", "static-layout.json", "capture-plan.json", "selector.json",
            "caller-decompiled.c", "resolver-decompiled.c", "caller-listing.json",
            "resolver-entry-listing.json", "source-container.json", "pre-resolution-container.json",
            "post-resolution-container.json", "source-vs-pre-diff.json", "pre-vs-post-diff.json",
            "leveled-tree.json", "ires-leaves.json", "rsgd-correlation.json", "manifest.json" };
        files.add("family-topology-analysis.md");
        for (String name : names) files.add(name);
        Map<String, Object> manifest = map();
        manifest.put("schemaVersion", 1);
        manifest.put("exportedAtUtc", Instant.now().toString());
        manifest.put("caseName", caseName);
        manifest.put("captureStatus", "runtime-required");
        manifest.put("staticEvidenceComplete", true);
        manifest.put("runtimeEvidenceComplete", false);
        manifest.put("modifiesGhidraProgram", false);
        manifest.put("files", files);
        manifest.put("caution", "Placeholder stage files contain no observations. Populate them only from a live CK capture.");
        writeJson(output.resolve("manifest.json"), manifest);

        println("Exported resource-resolution evidence contract to " + output);
    }

    private Path exportRoot(String[] args) throws Exception {
        if (args.length > 0 && !args[0].trim().isEmpty()) {
            return new File(args[0]).toPath().toAbsolutePath().normalize();
        }
        if (isRunningHeadless()) {
            throw new IllegalArgumentException("Headless use requires an export-root argument.");
        }
        return askDirectory("Choose export root", "Export").toPath().toAbsolutePath().normalize();
    }

    private String textArg(String[] args, int index, String fallback) {
        return index < args.length && !args[index].trim().isEmpty() ? args[index].trim() : fallback;
    }

    private String optionalArg(String[] args, int index) {
        return index < args.length && !args[index].trim().isEmpty() ? args[index].trim() : null;
    }

    private Address addressArg(String[] args, int index, String fallback) throws Exception {
        String value = textArg(args, index, fallback);
        if (value.startsWith("0x") || value.startsWith("0X")) value = value.substring(2);
        Address result = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(value);
        if (result == null) throw new IllegalArgumentException("Invalid address: " + value);
        return result;
    }

    private int intArg(String[] args, int index, int fallback) {
        String value = textArg(args, index, Integer.toString(fallback));
        return Integer.decode(value);
    }

    private Function requireFunction(Address address, String role) {
        Function result = currentProgram.getFunctionManager().getFunctionAt(address);
        if (result == null) throw new IllegalStateException("Undefined " + role + " function at " + address);
        return result;
    }

    private boolean isCall(Instruction instruction) {
        return instruction.getFlowType().isCall();
    }

    private Instruction findCallTo(Function caller, Function expected) {
        InstructionIterator instructions = currentProgram.getListing().getInstructions(caller.getBody(), true);
        while (instructions.hasNext()) {
            Instruction instruction = instructions.next();
            if (!isCall(instruction)) continue;
            for (Address flow : instruction.getFlows()) {
                Function target = currentProgram.getFunctionManager().getFunctionAt(flow);
                if (sameResolvedFunction(target, expected)) return instruction;
            }
        }
        return null;
    }

    private boolean sameResolvedFunction(Function candidate, Function expected) {
        Function resolved = candidate;
        int hops = 0;
        while (resolved != null && resolved.isThunk() && hops++ < 16) {
            resolved = resolved.getThunkedFunction(false);
        }
        return resolved != null && resolved.getEntryPoint().equals(expected.getEntryPoint());
    }

    private Decompilation decompile(Function function) {
        DecompInterface decompiler = new DecompInterface();
        try {
            decompiler.setOptions(new DecompileOptions());
            decompiler.toggleCCode(true);
            decompiler.toggleSyntaxTree(true);
            if (!decompiler.openProgram(currentProgram)) {
                return Decompilation.failed(decompiler.getLastMessage());
            }
            DecompileResults results = decompiler.decompileFunction(function,
                DECOMPILE_TIMEOUT_SECONDS, monitor);
            if (!results.decompileCompleted() || results.getHighFunction() == null) {
                return Decompilation.failed(results.getErrorMessage());
            }
            return Decompilation.completed(results.getDecompiledFunction().getC(),
                results.getHighFunction());
        }
        catch (Exception error) {
            return Decompilation.failed(error.getClass().getSimpleName() + ": " + error.getMessage());
        }
        finally {
            decompiler.dispose();
        }
    }

    private Map<String, Object> context(String caseName, Function caller, Instruction copyCall,
            Function resolver, Instruction resolverCall, Instruction afterResolver, int maximumDepth) {
        Map<String, Object> result = map();
        result.put("schemaVersion", 1);
        result.put("caseName", caseName);
        result.put("programName", currentProgram.getName());
        result.put("imageBase", fmt(currentProgram.getImageBase()));
        result.put("languageId", currentProgram.getLanguageID().toString());
        result.put("compilerSpecId", currentProgram.getCompilerSpec().getCompilerSpecID().toString());
        result.put("caller", function(caller));
        result.put("copyCall", instruction(copyCall));
        result.put("resolver", function(resolver));
        result.put("resolverCall", instruction(resolverCall));
        result.put("postResolutionBreakpoint", instruction(afterResolver));
        result.put("maximumRecursiveDepth", maximumDepth);
        result.put("evidenceMode", "static-contract-only");
        result.put("runtimeLimitation", "Static Ghidra has no CK heap or QSpinBox state; exact entries and selector value require a live process.");
        return result;
    }

    private Map<String, Object> selector(HighFunction highFunction, Instruction resolverCall) {
        Map<String, Object> result = map();
        result.put("schemaVersion", 1);
        result.put("captureStatus", "runtime-required");
        result.put("callSite", fmt(resolverCall.getAddress()));
        result.put("abiLocation", "R9W (low 16 bits of R9 under Windows x64 ABI)");
        result.put("widthBits", 16);
        result.put("signed", false);
        result.put("staticProvenance", "(ushort)QSpinBox::value(*(ResourceViewWidget+0x98))");
        result.put("displayedInputRelationship", "The displayed QSpinBox integer is narrowed modulo 2^16 at the resolver call.");
        result.put("exactRuntimeValue", null);
        result.put("reasonValueUnavailable", "The QSpinBox value is live UI state, not static program data.");
        PcodeOpAST operation = findCall(highFunction, resolverCall.getAddress());
        result.put("highPcode", operation == null ? null : pcode(operation));
        return result;
    }

    private Map<String, Object> layout() {
        Map<String, Object> result = map();
        result.put("schemaVersion", 1);
        result.put("confidence", "mechanically-supported");
        result.put("containerCountOffset", hex(0x40));
        result.put("containerCapacityOffset", hex(0x44));
        result.put("containerEntriesPointerOffset", hex(0x48));
        result.put("entrySize", hex(0x18));
        List<Map<String, Object>> fields = new ArrayList<>();
        fields.add(field("count", 0x0, 4, "signed quantity used by FUN_140e457b0"));
        fields.add(field("unknownOrPadding", 0x4, 4, "not semantically identified"));
        fields.add(field("formPointer", 0x8, 8, "TESBoundObject pointer; dynamically cast to TESLevItem"));
        fields.add(field("metadataPointer", 0x10, 8, "passed through for ordinary entries"));
        result.put("entryFields", fields);
        result.put("leveledListEntryStorage", "TESLevItem object +0x340 is passed to FUN_140dddba0");
        result.put("formIdentityLimitation", "FormID, EditorID, form type, and TESLevItem child layout need live helper/type evidence; offsets are not guessed here.");
        result.put("evidence", list(
            "FUN_140e0aab0 reads source +0x40/+0x48 and copies 0x18-byte records.",
            "FUN_140e457b0 iterates param_1 +0x40/+0x48 in 0x18-byte steps.",
            "FUN_140e457b0 reads entry count at +0x0, form pointer at +0x8, and metadata pointer at +0x10.",
            "FUN_140e457b0 dynamically casts the form pointer from TESBoundObject to TESLevItem."
        ));
        return result;
    }

    private Map<String, Object> capturePlan(Instruction copyCall, Instruction resolverCall,
            Instruction afterResolver, int maximumDepth) {
        Map<String, Object> result = map();
        result.put("schemaVersion", 1);
        result.put("observationOnly", true);
        result.put("addressRule", "runtime address = CreationKit.exe module base + RVA");
        List<Map<String, Object>> points = new ArrayList<>();
        points.add(capturePoint("source-component", copyCall, "before",
            "save R8 as source; save RCX as temporary; enumerate source now"));
        points.add(capturePoint("pre-resolution-and-selector", resolverCall, "before",
            "RCX = temporary TESContainer; RDX = resolved-container output slot; R8 = context; R9W = selector"));
        points.add(capturePoint("post-resolution", afterResolver, "after-resolver-return",
            "dereference saved output-slot pointer from resolver-entry RDX; do not treat RCX/pre as the post container"));
        result.put("capturePoints", points);
        result.put("recursiveMaximumDepth", maximumDepth);
        result.put("stopConditions", list("cycle", "repeated object address", "null form",
            "unsupported form type", "depth limit"));
        result.put("requiredCaseMetadata", list("case name", "BIOM", "RSGD",
            "RSGD candidates and percentages", "expected selected family", "displayed Resource Seed"));
        result.put("requiredComparisons", list("source vs pre", "pre vs post",
            "leveled topology vs known family topology", "RSGD alternatives vs source structure"));
        result.put("safety", "Breakpoints and memory reads only. Do not call engine helpers, patch code/data, or alter seed logic.");
        return result;
    }

    private Map<String, Object> capturePoint(String stage, Instruction instruction, String timing,
            String registers) {
        Map<String, Object> result = map();
        result.put("stage", stage);
        result.put("staticAddress", fmt(instruction.getAddress()));
        result.put("rva", rva(instruction.getAddress()));
        result.put("timing", timing);
        result.put("instruction", instruction.toString());
        result.put("registerContract", registers);
        return result;
    }

    private Map<String, Object> emptyStage(String stage, String procedure) {
        Map<String, Object> result = map();
        result.put("schemaVersion", 1);
        result.put("stage", stage);
        result.put("captureStatus", "not-captured");
        result.put("evidenceModeRequired", "live CK debugger/runtime observer");
        result.put("procedure", procedure);
        result.put("containerAddress", null);
        result.put("entryCount", null);
        result.put("entries", new ArrayList<Object>());
        result.put("warning", "An empty entries array is a placeholder, not evidence of an empty container.");
        return result;
    }

    private Map<String, Object> emptyDiff(String from, String to) {
        Map<String, Object> result = map();
        result.put("schemaVersion", 1);
        result.put("from", from);
        result.put("to", to);
        result.put("captureStatus", "blocked-on-runtime-capture");
        result.put("sameEntryCount", null);
        result.put("sameOrder", null);
        result.put("added", new ArrayList<Object>());
        result.put("removed", new ArrayList<Object>());
        result.put("changed", new ArrayList<Object>());
        return result;
    }

    private Map<String, Object> emptyRecursive(String kind, int maximumDepth) {
        Map<String, Object> result = map();
        result.put("schemaVersion", 1);
        result.put("kind", kind);
        result.put("captureStatus", "blocked-on-runtime-capture");
        result.put("maximumDepth", maximumDepth);
        result.put("nodes", new ArrayList<Object>());
        return result;
    }

    private Map<String, Object> emptyCorrelation(String biom, String rsgd, String family) {
        Map<String, Object> result = map();
        result.put("schemaVersion", 1);
        result.put("captureStatus", "case-metadata-required");
        result.put("biom", biom);
        result.put("rsgd", rsgd);
        result.put("expectedSelectedFamily", family);
        result.put("candidates", new ArrayList<Object>());
        result.put("sourceContainsAllCandidates", null);
        result.put("sourceContainsSelectedFamilyOnly", null);
        result.put("modelClassification", "insufficient evidence");
        return result;
    }

    private String familyTopologyTemplate(String caseName) {
        return "# Family topology analysis — " + caseName + "\n\n" +
            "Capture status: **runtime evidence not yet captured**\n\n" +
            "Static analysis establishes the observation points and generic container layout, " +
            "but it cannot establish which ordinary or leveled entries occur in this case.\n\n" +
            "- Linear-family topology: insufficient evidence\n" +
            "- Branching-family topology: insufficient evidence\n" +
            "- Root-invariant representation: insufficient evidence\n" +
            "- RSGD family-choice model: insufficient evidence\n\n" +
            "Replace these classifications only after the source, pre-resolution, post-resolution, " +
            "leveled-tree, IRES-leaf, and RSGD-correlation artifacts are populated from one coherent " +
            "live breakpoint run.\n";
    }

    private Map<String, Object> field(String name, int offset, int size, String interpretation) {
        Map<String, Object> result = map();
        result.put("name", name);
        result.put("offset", hex(offset));
        result.put("size", size);
        result.put("interpretation", interpretation);
        return result;
    }

    private Map<String, Object> function(Function function) {
        Map<String, Object> result = map();
        result.put("name", function.getName());
        result.put("entryAddress", fmt(function.getEntryPoint()));
        result.put("rva", rva(function.getEntryPoint()));
        result.put("signature", function.getSignature().getPrototypeString());
        return result;
    }

    private Map<String, Object> instruction(Instruction instruction) {
        Map<String, Object> result = map();
        result.put("address", fmt(instruction.getAddress()));
        result.put("rva", rva(instruction.getAddress()));
        result.put("length", instruction.getLength());
        result.put("mnemonic", instruction.getMnemonicString());
        result.put("text", instruction.toString());
        List<String> flows = new ArrayList<>();
        for (Address flow : instruction.getFlows()) flows.add(fmt(flow));
        result.put("flows", flows);
        return result;
    }

    private List<Map<String, Object>> listing(Function function) {
        List<Map<String, Object>> result = new ArrayList<>();
        InstructionIterator instructions = currentProgram.getListing().getInstructions(function.getBody(), true);
        while (instructions.hasNext()) result.add(instruction(instructions.next()));
        return result;
    }

    private List<Map<String, Object>> listingWindow(Address start, long byteCount) {
        List<Map<String, Object>> result = new ArrayList<>();
        Address end = start.add(byteCount);
        InstructionIterator instructions = currentProgram.getListing().getInstructions(start, true);
        while (instructions.hasNext()) {
            Instruction instruction = instructions.next();
            if (instruction.getAddress().compareTo(end) > 0) break;
            result.add(instruction(instruction));
        }
        return result;
    }

    private PcodeOpAST findCall(HighFunction highFunction, Address address) {
        Iterator<PcodeOpAST> operations = highFunction.getPcodeOps(address);
        while (operations.hasNext()) {
            PcodeOpAST operation = operations.next();
            if (operation.getOpcode() == PcodeOp.CALL || operation.getOpcode() == PcodeOp.CALLIND) {
                return operation;
            }
        }
        return null;
    }

    private Map<String, Object> pcode(PcodeOp operation) {
        Map<String, Object> result = map();
        result.put("mnemonic", operation.getMnemonic());
        result.put("sequenceAddress", operation.getSeqnum().getTarget().toString());
        List<Map<String, Object>> inputs = new ArrayList<>();
        for (int i = 0; i < operation.getNumInputs(); i++) {
            Varnode node = operation.getInput(i);
            Map<String, Object> item = map();
            item.put("index", i);
            item.put("role", i == 0 ? "call-target" : "argument-" + (i - 1));
            item.put("varnode", node.toString());
            item.put("size", node.getSize());
            inputs.add(item);
        }
        result.put("inputs", inputs);
        return result;
    }

    private String rva(Address address) {
        return hex(address.subtract(currentProgram.getImageBase()));
    }

    private String fmt(Address address) {
        return address == null ? null : address.toString().toUpperCase();
    }

    private String hex(long value) {
        return "0x" + Long.toUnsignedString(value, 16).toUpperCase();
    }

    private String safe(String value) {
        String cleaned = value.replaceAll("[^A-Za-z0-9._-]+", "_");
        return cleaned.isEmpty() ? DEFAULT_CASE : cleaned;
    }

    private Map<String, Object> map() {
        return new LinkedHashMap<>();
    }

    private List<String> list(String... values) {
        List<String> result = new ArrayList<>();
        for (String value : values) result.add(value);
        return result;
    }

    private void writeJson(Path path, Object value) throws Exception {
        write(path, JSON.toJson(value) + System.lineSeparator());
    }

    private void write(Path path, String value) throws Exception {
        Files.createDirectories(path.getParent());
        Files.write(path, value.getBytes(StandardCharsets.UTF_8));
    }

    private static final class Decompilation {
        final boolean completed;
        final String text;
        final String error;
        final HighFunction highFunction;

        private Decompilation(boolean completed, String text, String error, HighFunction highFunction) {
            this.completed = completed;
            this.text = text;
            this.error = error;
            this.highFunction = highFunction;
        }

        static Decompilation completed(String text, HighFunction highFunction) {
            return new Decompilation(true, text, null, highFunction);
        }

        static Decompilation failed(String error) {
            return new Decompilation(false, "/* Decompilation failed: " + error + " */\n", error, null);
        }
    }
}
