// Discover a bounded class method family and analyze one this-relative field without modifying the program.
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
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolIterator;
import ghidra.util.exception.CancelledException;

public class AnalyzeClassFieldProvenance extends GhidraScript {

    private static final int DECOMPILE_TIMEOUT_SECONDS = 60;
    private static final int MAX_TRACE_DEPTH = 8;
    private static final int MAX_VTABLE_VALUE_DEPTH = 8;
    private static final int MAX_VTABLE_SLOTS = 256;
    private static final int MAX_THUNK_HOPS = 100;
    private static final int MAX_EXPORTED_FUNCTIONS = 20;
    private static final int MAX_RECEIVER_FAMILY_DEPTH = 2;
    private static final String EXPECTED_ANCHOR_SUFFIX = "::OnApplySeed";
    private static final Gson JSON = new GsonBuilder()
        .setPrettyPrinting().disableHtmlEscaping().serializeNulls().create();

    private final Map<String, Decompilation> decompilationCache = new LinkedHashMap<>();
    private DecompInterface decompiler;

    @Override
    public void run() throws Exception {
        if (currentProgram == null || currentAddress == null) {
            printerr("Open a program and place the cursor inside a function associated with the target class.");
            return;
        }
        Function selected = currentProgram.getFunctionManager().getFunctionContaining(currentAddress);
        if (selected == null) {
            printerr("The cursor is not inside a defined function: " + currentAddress);
            return;
        }

        String className = askString("Class name", "Exact class name to investigate", "ResourceViewWidget").trim();
        if (className.isEmpty()) {
            printerr("Class name must not be blank.");
            return;
        }
        long fieldOffset = parseOffset(askString(
            "Field byte offset", "this-relative field offset in decimal or hexadecimal", "0xA0"));
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
        Path output = exportRoot.resolve("class-provenance").resolve(safeText(className));
        Path functionsOutput = output.resolve("functions");
        Files.createDirectories(functionsOutput);
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

            AnchorDiscovery anchors = discoverAnchors(className, selected);
            VtableAnalysis vtableAnalysis = analyzeVtableReferences(anchors);
            Map<String, MethodCandidate> methods = discoverMethods(className, anchors, vtableAnalysis);
            addMediumReceiverFamily(methods, MAX_RECEIVER_FAMILY_DEPTH);
            finalizeKnownRootConnection(anchors, methods);
            List<MethodCandidate> methodList = new ArrayList<>(methods.values());
            Collections.sort(methodList, MethodCandidate.ORDER);

            List<FieldAccess> accesses = analyzeFieldAccesses(methodList, fieldOffset, nestedOffset);
            Collections.sort(accesses, FieldAccess.ORDER);
            List<FieldAccess> writes = new ArrayList<>();
            List<Map<String, Object>> provenance = new ArrayList<>();
            for (FieldAccess access : accesses) {
                if ("write".equals(access.accessType)) {
                    writes.add(access);
                    provenance.add(access.provenanceRecord());
                }
            }

            List<Function> exported = exportStrongest(
                methodList, accesses, vtableAnalysis, functionsOutput, generatedAt);
            write(output.resolve("class-anchors.json"), json(anchors.document(className)));
            write(output.resolve("vtable-xrefs.json"), json(vtableAnalysis.xrefDocument(className)));
            write(output.resolve("lifecycle-candidates.json"), json(vtableAnalysis.lifecycleDocument(className)));
            write(output.resolve("class-methods.json"), json(methodDocument(className, methodList)));
            write(output.resolve("receiver-family.json"), json(receiverFamilyDocument(className, methodList)));
            write(output.resolve("field-" + offsetLabel(fieldOffset) + "-accesses.json"),
                json(accessDocument(className, fieldOffset, nestedOffset, accesses)));
            write(output.resolve("field-" + offsetLabel(fieldOffset) + "-writes.json"),
                json(writeDocument(className, fieldOffset, writes)));
            write(output.resolve("provenance.json"), json(provenanceDocument(provenance)));
            write(output.resolve("manifest.json"), json(manifest(
                className, selected, fieldOffset, nestedOffset, generatedAt,
                anchors, vtableAnalysis, methodList, accesses, writes, exported)));

            println("Exported class-scoped field provenance to " + output.toAbsolutePath());
            if (!anchors.anchorResolvedExactly()) {
                printerr("The exact root anchor was not resolved; class-anchors.json records anchor-unresolved.");
            }
            if (writes.isEmpty()) {
                printerr("No class-scoped writer was found; this negative result is explicit in the output.");
            }
        }
        finally {
            if (decompiler != null) {
                decompiler.dispose();
            }
        }
    }

    private AnchorDiscovery discoverAnchors(String className, Function selected) throws Exception {
        AnchorDiscovery result = new AnchorDiscovery(selected);
        String expectedAnchor = className + EXPECTED_ANCHOR_SUFFIX;
        Set<String> discoveredVtableAddresses = new LinkedHashSet<>();
        SymbolIterator symbols = currentProgram.getSymbolTable().getAllSymbols(true);
        while (symbols.hasNext()) {
            monitor.checkCancelled();
            Symbol symbol = symbols.next();
            String fullName = symbol.getName(true);
            if ("FUN_1431bc320".equals(symbol.getName())) {
                Function knownRoot = functionForSymbol(symbol);
                if (knownRoot != null && result.knownRootFunction == null) {
                    result.knownRootFunction = knownRoot;
                    result.knownRoot.put("function", functionSummary(knownRoot));
                    result.knownRoot.put("status", "independently-known-root");
                    result.knownRoot.put("references", functionPointerReferences(knownRoot));
                }
            }
            if (fullName == null || !containsIgnoreCase(fullName, className)) {
                continue;
            }
            Map<String, Object> record = symbolRecord(symbol);
            result.symbols.add(record);
            if (fullName.equals(expectedAnchor)) {
                Function containing = functionForSymbol(symbol);
                Map<String, Object> anchor = new LinkedHashMap<>(record);
                anchor.put("status", containing == null ? "anchor-symbol-without-function" : "resolved-exact");
                anchor.put("containingFunction", containing == null ? null : functionSummary(containing));
                anchor.put("selectedFunctionRelationship", selectedRelationship(selected, containing));
                if (containing != null) {
                    anchor.put("callers", functionSummaries(sortedFunctions(containing.getCallingFunctions(monitor))));
                    anchor.put("callees", functionSummaries(sortedFunctions(containing.getCalledFunctions(monitor))));
                }
                result.knownMethodAnchors.add(anchor);
            }
            if (isVtableName(fullName)) {
                if (discoveredVtableAddresses.add(formatAddress(symbol.getAddress()))) {
                    VtableCandidate vtable = new VtableCandidate(symbol);
                    enumerateVtable(vtable);
                    result.vtables.add(vtable);
                }
            }
            if (isRttiName(fullName)) {
                Map<String, Object> rtti = new LinkedHashMap<>(record);
                rtti.put("confidence", "medium");
                rtti.put("evidence", "Symbol contains the exact class text and an RTTI-related marker.");
                result.rttiCandidates.add(rtti);
            }
        }
        if (result.knownMethodAnchors.isEmpty()) {
            Map<String, Object> unresolved = new LinkedHashMap<>();
            unresolved.put("requestedSymbol", expectedAnchor);
            unresolved.put("status", "anchor-unresolved");
            unresolved.put("containingFunction", null);
            unresolved.put("selectedFunction", functionSummary(selected));
            unresolved.put("evidence", "No symbol full name exactly matched the requested anchor; no similar symbol was substituted.");
            result.knownMethodAnchors.add(unresolved);
        }
        return result;
    }

    private List<Map<String, Object>> functionPointerReferences(Function target) {
        List<Map<String, Object>> result = new ArrayList<>();
        ReferenceIterator references = currentProgram.getReferenceManager().getReferencesTo(target.getEntryPoint());
        while (references.hasNext()) {
            Reference reference = references.next();
            Map<String, Object> item = new LinkedHashMap<>();
            item.put("fromAddress", formatAddress(reference.getFromAddress()));
            item.put("referenceType", reference.getReferenceType().toString());
            Function containing = currentProgram.getFunctionManager().getFunctionContaining(reference.getFromAddress());
            item.put("containingFunction", containing == null ? null : functionSummary(containing));
            result.add(item);
        }
        return result;
    }

    private void finalizeKnownRootConnection(AnchorDiscovery anchors, Map<String, MethodCandidate> methods) {
        if (anchors.knownRootFunction == null) {
            anchors.knownRoot.put("status", "FUN_1431bc320-unresolved");
            anchors.knownRoot.put("classFamilyConnection", "not-tested-no-defined-function");
            return;
        }
        MethodCandidate candidate = methods.get(functionKey(anchors.knownRootFunction));
        anchors.knownRoot.put("classFamilyConnection", candidate == null ? "not-connected" : "connected");
        anchors.knownRoot.put("classFamilyConfidence", candidate == null ? null : candidate.confidence);
        anchors.knownRoot.put("receiverFamilyDepth", candidate == null ? null : candidate.receiverFamilyDepth);
        anchors.knownRoot.put("limitation", candidate == null ?
            "Preserved as an independently known root; no bounded receiver-preserving class-family path was found." : null);
    }

    private VtableAnalysis analyzeVtableReferences(AnchorDiscovery anchors) throws Exception {
        VtableAnalysis result = new VtableAnalysis();
        Map<String, LifecycleCandidate> lifecycleByFunction = new LinkedHashMap<>();
        Map<String, VtableCandidate> knownVtables = new LinkedHashMap<>();
        for (VtableCandidate vtable : anchors.vtables)
            if (!vtable.slots.isEmpty()) knownVtables.put(vtable.address, vtable);
        for (VtableCandidate vtable : anchors.vtables) {
            VtableReferenceGroup group = new VtableReferenceGroup(vtable);
            result.groups.add(group);
            ReferenceIterator references = currentProgram.getReferenceManager().getReferencesTo(vtable.rawAddress);
            while (references.hasNext()) {
                monitor.checkCancelled();
                Reference reference = references.next();
                VtableReference record = analyzeVtableReference(vtable, reference, knownVtables);
                group.references.add(record);
                if (!vtable.slots.isEmpty() && isInternal(record.function)) {
                    result.directInternalXrefFunctions.put(functionKey(record.function), record.function);
                }
                if (!"vptr-store".equals(record.referenceKind) || record.function == null ||
                        record.receiverOffset == null) {
                    continue;
                }
                String key = functionKey(record.function);
                LifecycleCandidate lifecycle = lifecycleByFunction.get(key);
                if (lifecycle == null) {
                    lifecycle = new LifecycleCandidate(record.function);
                    lifecycleByFunction.put(key, lifecycle);
                }
                boolean duplicate = false;
                for (VptrWrite existing : lifecycle.vptrStores) {
                    duplicate |= existing.storeAddress.equals(record.storeAddress) &&
                        existing.vtableAddress.equals(record.vtableAddress) &&
                        existing.receiverOffset == record.receiverOffset.longValue();
                }
                if (!duplicate) lifecycle.vptrStores.add(record.toVptrWrite());
            }
            group.finalizeCounts();
        }
        for (LifecycleCandidate candidate : lifecycleByFunction.values()) {
            Collections.sort(candidate.vptrStores, new Comparator<VptrWrite>() {
                @Override public int compare(VptrWrite left, VptrWrite right) {
                    return Integer.compare(left.operationIndex, right.operationIndex);
                }
            });
            for (VptrWrite write : candidate.vptrStores) {
                if (write.receiverOffset == 0) candidate.primaryVptrOffset = Long.valueOf(0);
                else candidate.secondaryVptrOffsets.add(Long.valueOf(write.receiverOffset));
            }
            for (VptrWrite selected : candidate.vptrStores) {
                for (VptrWrite other : candidate.vptrStores) {
                    if (selected == other) continue;
                    Map<String, Object> context = new LinkedHashMap<>();
                    context.put("storeAddress", other.storeAddress);
                    context.put("vtableName", other.vtableName);
                    context.put("vtableAddress", other.vtableAddress);
                    context.put("receiverOffset", other.receiverOffset);
                    context.put("receiverOffsetHex", other.receiverOffsetHex);
                    context.put("relativeOrder", other.operationIndex < selected.operationIndex ? "before" : "after");
                    selected.otherVptrWrites.add(context);
                }
            }
            classifyLifecycle(candidate);
            result.lifecycleCandidates.add(candidate);
            anchors.constructorCandidates.add(candidate.toLegacyMap());
        }
        Collections.sort(result.lifecycleCandidates, LifecycleCandidate.ORDER);
        return result;
    }

    private VtableReference analyzeVtableReference(VtableCandidate vtable, Reference reference,
            Map<String, VtableCandidate> knownVtables) {
        Address from = reference.getFromAddress();
        Function function = currentProgram.getFunctionManager().getFunctionContaining(from);
        VtableReference result = new VtableReference(vtable, reference, function);
        if (function == null || function.isExternal()) {
            return result;
        }
        Decompilation decompilation = decompile(function);
        if (decompilation.highFunction == null) {
            result.analysisError = decompilation.error;
            return result;
        }
        HighParam receiver = highParam(decompilation.highFunction, 0);
        Varnode receiverNode = receiver == null ? null : receiver.getRepresentative();
        List<PcodeOp> operationList = new ArrayList<>();
        Iterator<? extends PcodeOp> operationIterator = decompilation.highFunction.getPcodeOps();
        while (operationIterator.hasNext()) operationList.add(operationIterator.next());
        for (int operationIndex = 0; operationIndex < operationList.size(); operationIndex++) {
            PcodeOp operation = operationList.get(operationIndex);
            if (!from.equals(operation.getSeqnum().getTarget()) || !operationMentionsAddress(operation, vtable.rawAddress)) {
                continue;
            }
            result.pcodeOperations.add(operationSummary(operation));
            result.pcodeOp = operation.getMnemonic();
            if (operation.getOpcode() == PcodeOp.LOAD) {
                result.referenceKind = "LOAD/use";
            }
            else {
                result.referenceKind = "constant/address materialization";
            }
        }
        if (!"vptr-store".equals(result.referenceKind) && receiverNode != null) {
            for (int operationIndex = 0; operationIndex < operationList.size(); operationIndex++) {
                PcodeOp operation = operationList.get(operationIndex);
                if (operation.getOpcode() != PcodeOp.STORE || operation.getNumInputs() < 3) continue;
                VtableValueResolution valueResolution = resolveKnownVtableValue(
                    operation.getInput(2), knownVtables);
                if (!valueResolution.resolved || valueResolution.vtable != vtable) continue;
                Long receiverOffset = offsetFromBase(operation.getInput(1), receiverNode, 0);
                if (receiverOffset == null) continue;
                if (operation.getInput(2).getSize() != currentProgram.getDefaultPointerSize()) continue;
                result.referenceKind = "vptr-store";
                result.confidence = "strong";
                result.writtenToMemory = true;
                result.storeAddress = sequenceAddress(operation);
                result.resolvedStoreOperation = operationSummary(operation);
                result.destinationExpression = varnode(operation.getInput(1));
                result.receiverOffset = receiverOffset;
                result.valueResolutionBasis = valueResolution.basis;
                result.valueDefinitionPath.addAll(valueResolution.definitionPath);
                result.operationIndex = operationIndex;
                result.operationCount = operationList.size();
                result.position = operationIndex * 4 <= operationList.size() ? "early" :
                    operationIndex * 4 >= operationList.size() * 3 ? "late" : "middle";
                result.receiverEvidence.add("Vtable materialization reaches a STORE whose destination reduces to parameter 0 plus " +
                    unsignedHex(receiverOffset.longValue()) + ".");
                result.pcodeOperations.add(operationSummary(operation));
                break;
            }
        }
        return result;
    }

    private VtableValueResolution resolveKnownVtableValue(Varnode input,
            Map<String, VtableCandidate> knownVtables) {
        VtableValueResolution result = new VtableValueResolution();
        result.maximumDepth = MAX_VTABLE_VALUE_DEPTH;
        if (input == null || input.getSize() != currentProgram.getDefaultPointerSize()) {
            result.status = "unresolved-pointer-size-mismatch";
            return result;
        }
        NumericResolution numeric = resolveAddressValue(input, 0,
            Collections.newSetFromMap(new IdentityHashMap<Varnode, Boolean>()));
        result.definitionPath.addAll(numeric.definitionPath);
        if (!numeric.resolved) {
            result.status = numeric.status;
            return result;
        }
        Address address;
        try {
            address = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(numeric.value);
        }
        catch (RuntimeException exception) {
            result.status = "unresolved-address-conversion";
            return result;
        }
        VtableCandidate vtable = knownVtables.get(formatAddress(address));
        if (vtable == null) {
            result.status = "resolved-address-not-known-vtable";
            result.resolvedAddress = formatAddress(address);
            return result;
        }
        result.resolved = true;
        result.status = "resolved-known-vtable";
        result.basis = "resolved-vtable-through-pcode";
        result.resolvedAddress = vtable.address;
        result.vtable = vtable;
        result.definitionPath.add("CONSTANT_ADDRESS " + vtable.address);
        return result;
    }

    private NumericResolution resolveAddressValue(Varnode input, int depth, Set<Varnode> visited) {
        NumericResolution result = new NumericResolution();
        if (input == null) return result.fail("unresolved-null-varnode");
        if (depth > MAX_VTABLE_VALUE_DEPTH) return result.fail("unresolved-depth-limit");
        if (!visited.add(input)) return result.fail("unresolved-cycle");
        if (input.isConstant()) {
            result.resolved = true; result.value = input.getOffset();
            result.status = "resolved-constant";
            return result;
        }
        if (input.isAddress() && input.getAddress().isMemoryAddress()) {
            result.resolved = true; result.value = input.getAddress().getOffset();
            result.status = "resolved-program-address";
            return result;
        }
        PcodeOp definition = input.getDef();
        if (definition == null) return result.fail("unresolved-no-definition");
        int opcode = definition.getOpcode();
        result.definitionPath.add(definition.getMnemonic() + " at " + sequenceAddress(definition));
        if (isWrapper(opcode) && definition.getNumInputs() == 1) {
            return result.merge(resolveAddressValue(definition.getInput(0), depth + 1, visited));
        }
        if (opcode == PcodeOp.MULTIEQUAL) return result.fail("unresolved-multiequal");
        if (opcode == PcodeOp.LOAD) return result.fail("unresolved-load-derived");
        if (opcode == PcodeOp.CALL || opcode == PcodeOp.CALLIND)
            return result.fail("unresolved-call-result");
        if ((opcode == PcodeOp.PTRSUB || opcode == PcodeOp.INT_ADD) && definition.getNumInputs() == 2) {
            Varnode left = definition.getInput(0), right = definition.getInput(1);
            if (right.isConstant()) {
                NumericResolution base = resolveAddressValue(left, depth + 1, visited);
                if (!base.resolved) return result.merge(base);
                result.definitionPath.addAll(base.definitionPath);
                result.definitionPath.add("CONSTANT_ADDEND " + unsignedHex(right.getOffset()));
                result.resolved = true; result.status = "resolved-constant-arithmetic";
                result.value = base.value + right.getOffset(); return result;
            }
            if (opcode == PcodeOp.INT_ADD && left.isConstant()) {
                NumericResolution base = resolveAddressValue(right, depth + 1, visited);
                if (!base.resolved) return result.merge(base);
                result.definitionPath.addAll(base.definitionPath);
                result.definitionPath.add("CONSTANT_ADDEND " + unsignedHex(left.getOffset()));
                result.resolved = true; result.status = "resolved-constant-arithmetic";
                result.value = base.value + left.getOffset(); return result;
            }
            return result.fail("unresolved-nonconstant-arithmetic");
        }
        if (opcode == PcodeOp.PTRADD && definition.getNumInputs() == 3) {
            Varnode index = definition.getInput(1), size = definition.getInput(2);
            if (!index.isConstant() || !size.isConstant())
                return result.fail("unresolved-nonconstant-ptradd");
            NumericResolution base = resolveAddressValue(definition.getInput(0), depth + 1, visited);
            if (!base.resolved) return result.merge(base);
            result.definitionPath.addAll(base.definitionPath);
            result.definitionPath.add("CONSTANT_PTRADD " + unsignedHex(index.getOffset()) + " * " +
                unsignedHex(size.getOffset()));
            result.resolved = true; result.status = "resolved-constant-arithmetic";
            result.value = base.value + index.getOffset() * size.getOffset(); return result;
        }
        return result.fail("unresolved-unsupported-opcode-" + definition.getMnemonic());
    }

    private boolean operationMentionsAddress(PcodeOp operation, Address expected) {
        for (int index = 0; index < operation.getNumInputs(); index++) {
            if (expected.equals(addressFromVarnode(stripWrappers(operation.getInput(index))))) return true;
        }
        return false;
    }

    private void classifyLifecycle(LifecycleCandidate candidate) throws CancelledException {
        candidate.calledFromAllocationPattern = calledFromAllocationPattern(candidate.function);
        candidate.callers.addAll(functionSummaries(sortedFunctions(candidate.function.getCallingFunctions(monitor))));
        candidate.callees.addAll(functionSummaries(sortedFunctions(candidate.function.getCalledFunctions(monitor))));
        boolean cleanup = false;
        boolean deallocation = false;
        boolean teardownAfterVptr = false;
        int latestVptrStoreIndex = -1;
        for (VptrWrite write : candidate.vptrStores)
            latestVptrStoreIndex = Math.max(latestVptrStoreIndex, write.operationIndex);
        Decompilation decompilation = decompile(candidate.function);
        if (decompilation.highFunction != null) {
            HighParam receiver = highParam(decompilation.highFunction, 0);
            Varnode receiverNode = receiver == null ? null : receiver.getRepresentative();
            Iterator<? extends PcodeOp> operations = decompilation.highFunction.getPcodeOps();
            int operationIndex = 0;
            while (operations.hasNext()) {
                PcodeOp operation = operations.next();
                if (operation.getOpcode() == PcodeOp.RETURN && operation.getNumInputs() >= 2 &&
                        receiverNode != null && Long.valueOf(0).equals(
                            offsetFromBase(operation.getInput(1), receiverNode, 0))) {
                    candidate.returnBehavior = "returns-receiver";
                }
                if (operation.getOpcode() == PcodeOp.STORE && operation.getNumInputs() >= 3 && receiverNode != null) {
                    Long offset = offsetFromBase(operation.getInput(1), receiverNode, 0);
                    if (offset != null) candidate.receiverRelativeStoreCount++;
                }
                if (operation.getOpcode() == PcodeOp.CALL) {
                    Function callee = directCalledFunction(operation);
                    String lower = callee == null ? "" : fullName(callee).toLowerCase(Locale.ROOT);
                    boolean teardownCall = lower.contains("::~") || lower.contains("destruct") ||
                        lower.contains("destroy") || lower.contains("cleanup");
                    if (teardownCall && operationIndex > latestVptrStoreIndex) teardownAfterVptr = true;
                }
                operationIndex++;
            }
        }
        for (Function callee : candidate.function.getCalledFunctions(monitor)) {
            String lower = fullName(callee).toLowerCase(Locale.ROOT);
            cleanup |= lower.contains("::~") || lower.contains("destruct") ||
                lower.contains("destroy") || lower.contains("cleanup");
            deallocation |= lower.contains("operator delete") || lower.contains("dealloc") || lower.contains("free");
        }
        boolean lateStore = false;
        boolean earlyOrMiddleStore = false;
        for (VptrWrite write : candidate.vptrStores) {
            lateStore |= "late".equals(write.position);
            earlyOrMiddleStore |= !"late".equals(write.position);
        }
        candidate.teardownCallAfterVptr = teardownAfterVptr;
        if (deallocation || teardownAfterVptr || (cleanup && lateStore)) {
            candidate.classification = "destructor-like";
            candidate.confidence = deallocation || teardownAfterVptr ? "strong" : "medium";
            candidate.evidence.add(deallocation ? "Calls a deallocation/delete-named function." :
                teardownAfterVptr ? "Restores class vptrs before a destructor/teardown call." :
                "Has cleanup/destruction-named callees and a late class-vptr store.");
        }
        else if ((candidate.calledFromAllocationPattern && earlyOrMiddleStore) ||
                ("returns-receiver".equals(candidate.returnBehavior) && earlyOrMiddleStore &&
                 candidate.receiverRelativeStoreCount > candidate.vptrStores.size())) {
            candidate.classification = "constructor-like";
            candidate.confidence = candidate.calledFromAllocationPattern ? "strong" : "medium";
            candidate.evidence.add(candidate.calledFromAllocationPattern ?
                "A direct caller has allocation/new context and the function installs a non-late class vptr." :
                "Returns the receiver, performs additional receiver-relative stores, and installs a non-late class vptr.");
        }
        else if (!candidate.vptrStores.isEmpty()) {
            candidate.classification = "lifecycle-helper";
            candidate.confidence = "medium";
            candidate.evidence.add("Structurally installs a class vptr, but constructor/destructor indicators are inconclusive.");
        }
        else {
            candidate.limitations.add("No structural class-vptr store was recovered.");
        }
        candidate.limitations.add("Classification is structural and conservative; it is not recovered C++ type information.");
    }

    private Map<String, MethodCandidate> discoverMethods(String className, AnchorDiscovery anchors,
            VtableAnalysis vtableAnalysis)
            throws Exception {
        Map<String, MethodCandidate> result = new LinkedHashMap<>();

        for (Map<String, Object> symbol : anchors.symbols) {
            Address address = addressFromText((String) symbol.get("address"));
            Function function = address == null ? null : currentProgram.getFunctionManager().getFunctionAt(address);
            String name = (String) symbol.get("fullName");
            if (function != null && isExactClassQualifiedFunction(name, className)) {
                addEvidence(result, function, "strong", "exact-class-qualified-symbol", name, null, null);
            }
        }
        for (Map<String, Object> anchor : anchors.knownMethodAnchors) {
            @SuppressWarnings("unchecked")
            Map<String, Object> summary = (Map<String, Object>) anchor.get("containingFunction");
            Function function = functionFromSummary(summary);
            if (function != null) {
                addEvidence(result, function, "strong", "exact-class-qualified-symbol",
                    "Exact root anchor " + className + EXPECTED_ANCHOR_SUFFIX, null, null);
            }
        }
        for (VtableCandidate vtable : anchors.vtables) {
            for (VtableSlot slot : vtable.slots) {
                if (slot.resolvedFunction != null) {
                    addEvidence(result, slot.resolvedFunction, "strong", "vtable-slot",
                        vtable.name + " slot " + slot.slotIndex, slot.slotIndex, slot.byteOffset);
                }
            }
        }

        for (LifecycleCandidate lifecycle : vtableAnalysis.lifecycleCandidates) {
            addEvidence(result, lifecycle.function, "strong", "vtable-writer",
                "Structurally stores a ResourceViewWidget vtable through parameter 0.", null, null);
            MethodCandidate candidate = result.get(functionKey(lifecycle.function));
            candidate.vptrWrites.addAll(lifecycle.vptrStores);
        }
        return result;
    }

    private void addMediumReceiverFamily(Map<String, MethodCandidate> methods, int maximumDepth) throws Exception {
        List<MethodCandidate> frontier = new ArrayList<>();
        for (MethodCandidate method : methods.values()) {
            if ("strong".equals(method.confidence) && isInternal(method.function)) {
                method.receiverFamilyDepth = 0;
                frontier.add(method);
            }
        }
        for (int depth = 1; depth <= maximumDepth && !frontier.isEmpty(); depth++) {
            List<MethodCandidate> next = new ArrayList<>();
            Set<String> queued = new LinkedHashSet<>();
            for (MethodCandidate source : frontier) {
            Decompilation decompilation = decompile(source.function);
            if (decompilation.highFunction != null) {
                HighParam receiver = highParam(decompilation.highFunction, 0);
                if (receiver != null && receiver.getRepresentative() != null) {
                    Iterator<? extends PcodeOp> operations = decompilation.highFunction.getPcodeOps();
                    while (operations.hasNext()) {
                        PcodeOp operation = operations.next();
                        if (operation.getOpcode() != PcodeOp.CALL || operation.getNumInputs() < 2 ||
                                !Long.valueOf(0).equals(offsetFromBase(
                                    operation.getInput(1), receiver.getRepresentative(), 0))) {
                            continue;
                        }
                        Function callee = directCalledFunction(operation);
                        if (isInternal(callee)) {
                            addEvidence(methods, callee, "medium", "matching-receiver-callee",
                                "Receiver-family function at depth " + (depth - 1) +
                                " passes its parameter 0 as callee argument 0 at " +
                                sequenceAddress(operation), null, null);
                            MethodCandidate added = methods.get(functionKey(callee));
                            if (added.receiverFamilyDepth == null || depth < added.receiverFamilyDepth.intValue()) {
                                added.receiverFamilyDepth = depth;
                                added.receiverFamilySourceFunction = source.functionName;
                                added.receiverFamilySourceAddress = source.functionAddress;
                                added.receiverFamilyCallSite = sequenceAddress(operation);
                                added.receiverArgumentIndex = 0;
                                added.relationship = "receiver-preserving-callee";
                                if (depth < maximumDepth && queued.add(functionKey(callee))) next.add(added);
                            }
                        }
                    }
                }
            }
            }
            frontier = next;
        }
    }

    private boolean callsTargetWithReceiver(HighFunction highFunction, Function target, Varnode receiver) {
        Iterator<? extends PcodeOp> operations = highFunction.getPcodeOps();
        while (operations.hasNext()) {
            PcodeOp operation = operations.next();
            if (operation.getOpcode() == PcodeOp.CALL && operation.getNumInputs() >= 2 &&
                    target.equals(directCalledFunction(operation)) &&
                    Long.valueOf(0).equals(offsetFromBase(operation.getInput(1), receiver, 0))) {
                return true;
            }
        }
        return false;
    }

    private List<FieldAccess> analyzeFieldAccesses(List<MethodCandidate> methods,
            long fieldOffset, Long nestedOffset) throws Exception {
        List<FieldAccess> result = new ArrayList<>();
        for (MethodCandidate method : methods) {
            if ("weak".equals(method.confidence) || !isInternal(method.function)) {
                continue;
            }
            Decompilation decompilation = decompile(method.function);
            if (decompilation.highFunction == null) {
                method.analysisError = decompilation.error;
                continue;
            }
            HighParam receiver = highParam(decompilation.highFunction, 0);
            if (receiver == null || receiver.getRepresentative() == null) {
                method.analysisError = "Decompiler high p-code exposed no parameter 0 representative.";
                continue;
            }
            Iterator<? extends PcodeOp> operations = decompilation.highFunction.getPcodeOps();
            while (operations.hasNext()) {
                monitor.checkCancelled();
                PcodeOp operation = operations.next();
                if (operation.getOpcode() == PcodeOp.LOAD && operation.getNumInputs() >= 2 &&
                        fieldOffset == value(offsetFromBase(
                            operation.getInput(1), receiver.getRepresentative(), 0), Long.MIN_VALUE)) {
                    FieldAccess access = new FieldAccess(
                        method, operationSummary(operation), operation, "read", fieldOffset);
                    access.valueSummary = "value loaded from parameter 0 plus " + unsignedHex(fieldOffset);
                    if (nestedOffset != null) {
                        access.nestedEvidence.addAll(traceNestedUses(operation.getOutput(), nestedOffset));
                        access.nestedOffset20Observed = !access.nestedEvidence.isEmpty();
                    }
                    result.add(access);
                }
                else if (operation.getOpcode() == PcodeOp.STORE && operation.getNumInputs() >= 3 &&
                        fieldOffset == value(offsetFromBase(
                            operation.getInput(1), receiver.getRepresentative(), 0), Long.MIN_VALUE)) {
                    Map<String, Object> provenance = traceWrittenValue(
                        decompilation.highFunction, operation.getInput(2), receiver.getRepresentative(), 0,
                        Collections.newSetFromMap(new IdentityHashMap<Varnode, Boolean>()));
                    FieldAccess access = new FieldAccess(
                        method, operationSummary(operation), operation, "write", fieldOffset);
                    access.provenance = provenance;
                    access.writeKind = classifyWrite(operation.getInput(2), provenance);
                    access.valueSummary = summarizeProvenance(provenance);
                    if (nestedOffset != null) {
                        Integer sourceParameter = integerValue(provenance.get("sourceParameterIndex"));
                        if (sourceParameter != null) {
                            HighParam source = highParam(decompilation.highFunction, sourceParameter);
                            if (source != null && source.getRepresentative() != null) {
                                access.nestedEvidence.addAll(findOffsetOperations(
                                    decompilation.highFunction, source.getRepresentative(), nestedOffset,
                                    "written-value-parameter"));
                                access.nestedOffset20Observed = !access.nestedEvidence.isEmpty();
                            }
                        }
                    }
                    result.add(access);
                }
            }
        }
        return result;
    }

    private List<VptrWrite> findVptrWrites(Function function, VtableCandidate vtable) {
        List<VptrWrite> result = new ArrayList<>();
        Decompilation decompilation = decompile(function);
        HighFunction highFunction = decompilation.highFunction;
        HighParam receiver = highParam(highFunction, 0);
        if (receiver == null || receiver.getRepresentative() == null) {
            return result;
        }
        int operationIndex = 0;
        List<PcodeOp> operations = new ArrayList<>();
        Iterator<? extends PcodeOp> iterator = highFunction.getPcodeOps();
        while (iterator.hasNext()) {
            operations.add(iterator.next());
        }
        for (PcodeOp operation : operations) {
            if (operation.getOpcode() == PcodeOp.STORE && operation.getNumInputs() >= 3) {
                Long offset = offsetFromBase(operation.getInput(1), receiver.getRepresentative(), 0);
                Address stored = addressFromVarnode(stripWrappers(operation.getInput(2)));
                if (offset != null && vtable.rawAddress.equals(stored)) {
                    String position = operationIndex * 4 <= operations.size() ? "early" :
                        operationIndex * 4 >= operations.size() * 3 ? "late" : "middle";
                    VptrWrite write = new VptrWrite(operation, vtable, offset.longValue(), position,
                        operationIndex, operations.size());
                    write.otherVptrWrites.addAll(findOtherVptrWrites(
                        operations, receiver.getRepresentative(), operation));
                    result.add(write);
                }
            }
            operationIndex++;
        }
        return result;
    }

    private List<Map<String, Object>> findOtherVptrWrites(
            List<PcodeOp> operations, Varnode receiver, PcodeOp selected) {
        List<Map<String, Object>> result = new ArrayList<>();
        for (PcodeOp operation : operations) {
            if (operation == selected || operation.getOpcode() != PcodeOp.STORE || operation.getNumInputs() < 3 ||
                    offsetFromBase(operation.getInput(1), receiver, 0) == null) {
                continue;
            }
            Address stored = addressFromVarnode(stripWrappers(operation.getInput(2)));
            List<String> symbols = stored == null ? Collections.<String>emptyList() : symbolsAt(stored);
            boolean vtable = false;
            for (String symbol : symbols) {
                vtable |= isVtableName(symbol);
            }
            if (vtable) {
                Map<String, Object> item = new LinkedHashMap<>();
                item.put("storeAddress", sequenceAddress(operation));
                item.put("vtableAddress", formatAddress(stored));
                item.put("symbolNames", symbols);
                Long receiverOffset = offsetFromBase(operation.getInput(1), receiver, 0);
                item.put("receiverOffset", receiverOffset);
                item.put("receiverOffsetHex", receiverOffset == null ? null : unsignedHex(receiverOffset.longValue()));
                result.add(item);
            }
        }
        return result;
    }

    private boolean calledFromAllocationPattern(Function candidate) throws CancelledException {
        for (Function caller : candidate.getCallingFunctions(monitor)) {
            for (Function callee : caller.getCalledFunctions(monitor)) {
                String name = fullName(callee).toLowerCase(Locale.ROOT);
                if (name.contains("operator new") || name.contains("alloc")) {
                    return true;
                }
            }
        }
        return false;
    }

    private void enumerateVtable(VtableCandidate candidate) throws CancelledException {
        int pointerSize = currentProgram.getDefaultPointerSize();
        candidate.pointerSize = pointerSize;
        candidate.maximumSlots = MAX_VTABLE_SLOTS;
        if (pointerSize <= 0 || pointerSize > Long.BYTES) {
            candidate.stopReason = "invalid-program-pointer-size";
            return;
        }
        Map<String, Long> firstResolvedSlot = new LinkedHashMap<>();
        for (int index = 0; index < MAX_VTABLE_SLOTS; index++) {
            monitor.checkCancelled();
            Address slotAddress;
            try {
                slotAddress = candidate.rawAddress.add((long) index * pointerSize);
            }
            catch (RuntimeException exception) {
                candidate.stopReason = "slot-address-overflow";
                break;
            }
            Address pointer;
            try {
                pointer = readPointer(slotAddress, pointerSize);
            }
            catch (Exception exception) {
                candidate.stopReason = "unreadable-slot";
                candidate.stopDetail = exception.getClass().getSimpleName() + ": " + safeMessage(exception);
                break;
            }
            if (pointer == null) {
                candidate.stopReason = "null-slot";
                break;
            }
            Function slotFunction = currentProgram.getFunctionManager().getFunctionAt(pointer);
            if (slotFunction == null) {
                candidate.stopReason = "slot-pointer-not-defined-function";
                candidate.stopDetail = formatAddress(pointer);
                break;
            }
            ThunkResolution thunk = resolveThunk(slotFunction);
            Function resolved = thunk.resolvedFunction;
            VtableSlot slot = new VtableSlot(
                index, (long) index * pointerSize, slotAddress, pointer, slotFunction, resolved, thunk);
            if (resolved != null) {
                String key = functionKey(resolved);
                slot.duplicateOfSlot = firstResolvedSlot.get(key);
                if (slot.duplicateOfSlot == null) firstResolvedSlot.put(key, Long.valueOf(index));
            }
            candidate.slots.add(slot);
        }
        if (candidate.stopReason == null) {
            candidate.stopReason = "maximum-slot-limit";
        }
        candidate.discoveredSlotCount = candidate.slots.size();
        for (VtableSlot slot : candidate.slots) {
            if (slot.internal) candidate.internalFunctionCount++;
            if (slot.external) candidate.externalFunctionCount++;
            if (slot.duplicateOfSlot != null) candidate.duplicateResolvedFunctionCount++;
        }
    }

    private Map<String, Object> traceWrittenValue(HighFunction highFunction, Varnode input,
            Varnode receiver, int depth, Set<Varnode> visited) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("maximumDepth", MAX_TRACE_DEPTH);
        result.put("varnode", varnode(input));
        List<String> chain = new ArrayList<>();
        result.put("provenanceChain", chain);
        if (input == null) {
            result.put("status", "unresolved-null-varnode");
            return result;
        }
        Varnode value = stripWrappers(input);
        if (depth > MAX_TRACE_DEPTH) {
            result.put("status", "unresolved-depth-limit");
            return result;
        }
        if (!visited.add(value)) {
            result.put("status", "unresolved-cycle");
            return result;
        }
        if (value.isConstant() || (value.isAddress() && value.getAddress().isMemoryAddress())) {
            Address address = addressFromVarnode(value);
            result.put("status", value.getOffset() == 0 ? "resolved-null-constant" : "resolved-constant-address");
            result.put("address", formatAddress(address));
            result.put("symbols", address == null ? Collections.emptyList() : symbolsAt(address));
            chain.add("constant/address " + (address == null ? unsignedHex(value.getOffset()) : formatAddress(address)));
            return result;
        }
        for (int index = 0; index < highParamCount(highFunction); index++) {
            HighParam parameter = highParam(highFunction, index);
            if (parameter != null && parameter.getRepresentative() != null &&
                    sameIdentity(value, parameter.getRepresentative())) {
                result.put("status", "resolved-function-parameter");
                result.put("sourceParameterIndex", index);
                chain.add("function parameter " + index);
                return result;
            }
        }
        PcodeOp definition = value.getDef();
        result.put("definingOperation", operationSummary(definition));
        if (definition == null) {
            result.put("status", "unresolved-no-definition");
            return result;
        }
        chain.add(definition.getMnemonic() + " at " + sequenceAddress(definition));
        if (definition.getOpcode() == PcodeOp.CALL || definition.getOpcode() == PcodeOp.CALLIND) {
            Function callee = definition.getOpcode() == PcodeOp.CALL ? directCalledFunction(definition) : null;
            result.put("status", "resolved-call-return");
            result.put("callSite", sequenceAddress(definition));
            result.put("callee", callee == null ? null : functionSummary(callee));
            result.put("allocatorOrFactoryNameHint", callee == null ? null : allocatorFactoryHint(callee));
            return result;
        }
        if (definition.getOpcode() == PcodeOp.LOAD && definition.getNumInputs() >= 2) {
            result.put("status", "resolved-load-expression");
            result.put("sourceReceiverOffset", offsetFromBase(definition.getInput(1), receiver, 0));
            result.put("loadPointer", varnode(definition.getInput(1)));
            return result;
        }
        if (definition.getOpcode() == PcodeOp.PTRSUB || definition.getOpcode() == PcodeOp.INT_ADD ||
                definition.getOpcode() == PcodeOp.PTRADD) {
            OffsetExpression expression = extractBasePlusConstant(value);
            if (expression != null && expression.base != value) {
                Map<String, Object> base = traceWrittenValue(
                    highFunction, expression.base, receiver, depth + 1, visited);
                result.put("status", "resolved-address-arithmetic");
                result.put("constantOffset", expression.offset);
                result.put("constantOffsetHex", unsignedHex(expression.offset));
                result.put("baseProvenance", base);
                return result;
            }
        }
        if (definition.getOpcode() == PcodeOp.MULTIEQUAL) {
            result.put("status", "unresolved-phi");
            result.put("unresolvedStep", "MULTIEQUAL branch merge");
            return result;
        }
        result.put("status", "unresolved-unsupported-opcode");
        result.put("unresolvedStep", definition.getMnemonic());
        return result;
    }

    private List<Map<String, Object>> traceNestedUses(Varnode start, long nestedOffset) {
        List<Map<String, Object>> result = new ArrayList<>();
        Set<Varnode> visited = Collections.newSetFromMap(new IdentityHashMap<Varnode, Boolean>());
        traceNestedUses(start, nestedOffset, false, 0, visited, result);
        return result;
    }

    private void traceNestedUses(Varnode value, long nestedOffset, boolean matched, int depth,
            Set<Varnode> visited, List<Map<String, Object>> result) {
        if (value == null || depth > MAX_TRACE_DEPTH || !visited.add(value)) {
            return;
        }
        Iterator<PcodeOp> uses = value.getDescendants();
        while (uses.hasNext()) {
            PcodeOp use = uses.next();
            Long offset = use.getOutput() == null ? null : offsetFromBase(use.getOutput(), value, 0);
            boolean nowMatched = matched || Long.valueOf(nestedOffset).equals(offset);
            if (nowMatched) {
                Map<String, Object> record = operationSummary(use);
                record.put("relativeOffset", offset);
                record.put("relativeOffsetHex", offset == null ? null : unsignedHex(offset));
                record.put("matchesNestedOffset", Long.valueOf(nestedOffset).equals(offset));
                record.put("callArgumentIndexes", callArgumentIndexes(use, value));
                Function callee = use.getOpcode() == PcodeOp.CALL ? directCalledFunction(use) : null;
                record.put("callee", callee == null ? null : functionSummary(callee));
                result.add(record);
            }
            if (use.getOutput() != null && isTraceable(use.getOpcode())) {
                traceNestedUses(use.getOutput(), nestedOffset, nowMatched, depth + 1, visited, result);
            }
        }
    }

    private List<Map<String, Object>> findOffsetOperations(
            HighFunction highFunction, Varnode base, long offset, String basis) {
        List<Map<String, Object>> result = new ArrayList<>();
        Iterator<? extends PcodeOp> operations = highFunction.getPcodeOps();
        while (operations.hasNext()) {
            PcodeOp operation = operations.next();
            if (((operation.getOpcode() == PcodeOp.LOAD && operation.getNumInputs() >= 2) ||
                    (operation.getOpcode() == PcodeOp.STORE && operation.getNumInputs() >= 3)) &&
                    Long.valueOf(offset).equals(offsetFromBase(operation.getInput(1), base, 0))) {
                Map<String, Object> record = operationSummary(operation);
                record.put("basis", basis);
                record.put("accessType", operation.getOpcode() == PcodeOp.LOAD ? "read" : "write");
                result.add(record);
            }
        }
        return result;
    }

    private List<Integer> callArgumentIndexes(PcodeOp operation, Varnode value) {
        List<Integer> result = new ArrayList<>();
        if (operation.getOpcode() != PcodeOp.CALL && operation.getOpcode() != PcodeOp.CALLIND) {
            return result;
        }
        for (int index = 1; index < operation.getNumInputs(); index++) {
            if (sameIdentity(operation.getInput(index), value)) {
                result.add(index - 1);
            }
        }
        return result;
    }

    private String classifyWrite(Varnode input, Map<String, Object> provenance) {
        Varnode value = stripWrappers(input);
        if (value != null && value.isConstant() && value.getOffset() == 0) {
            return "clear/null";
        }
        String status = String.valueOf(provenance.get("status"));
        if ("resolved-call-return".equals(status)) {
            return "initialization";
        }
        if ("resolved-function-parameter".equals(status)) {
            return "assignment";
        }
        if ("resolved-load-expression".equals(status)) {
            return "copy";
        }
        return "unknown";
    }

    private String summarizeProvenance(Map<String, Object> provenance) {
        String status = String.valueOf(provenance.get("status"));
        if ("resolved-function-parameter".equals(status)) {
            return "function parameter " + provenance.get("sourceParameterIndex");
        }
        if ("resolved-call-return".equals(status)) {
            @SuppressWarnings("unchecked")
            Map<String, Object> callee = (Map<String, Object>) provenance.get("callee");
            return callee == null ? "indirect/unknown call return" : "return from " + callee.get("functionName");
        }
        if ("resolved-null-constant".equals(status)) {
            return "null constant";
        }
        if ("resolved-load-expression".equals(status)) {
            return "value copied from a load expression";
        }
        return status;
    }

    private String allocatorFactoryHint(Function function) {
        String name = fullName(function).toLowerCase(Locale.ROOT);
        return name.contains("operator new") || name.contains("alloc") || name.contains("create") ||
            name.contains("factory") ? "name-only allocator/factory hint; not semantic proof" : null;
    }

    private void addEvidence(Map<String, MethodCandidate> methods, Function function,
            String confidence, String kind, String detail, Long slotIndex, Long byteOffset) {
        String key = functionKey(function);
        MethodCandidate candidate = methods.get(key);
        if (candidate == null) {
            candidate = new MethodCandidate(function);
            methods.put(key, candidate);
        }
        candidate.upgrade(confidence);
        candidate.addEvidence(kind, detail);
        if (slotIndex != null && candidate.vtableSlotIndex == null) {
            candidate.vtableSlotIndex = slotIndex;
            candidate.vtableByteOffset = byteOffset;
        }
        if (function.isThunk()) {
            ThunkResolution thunk = resolveThunkUnchecked(function);
            if (thunk.resolvedFunction != null) {
                candidate.addEvidence("thunk", "Thunk resolves to " + fullName(thunk.resolvedFunction) +
                    " at " + address(thunk.resolvedFunction));
                MethodCandidate target = methods.get(functionKey(thunk.resolvedFunction));
                if (target == null) {
                    target = new MethodCandidate(thunk.resolvedFunction);
                    methods.put(functionKey(thunk.resolvedFunction), target);
                }
                target.upgrade(confidence);
                target.addEvidence("thunk-target", "Implementation of class-bound thunk " + fullName(function));
            }
        }
    }

    private List<Function> exportStrongest(List<MethodCandidate> methods, List<FieldAccess> accesses,
            VtableAnalysis vtableAnalysis, Path directory, Instant generatedAt) throws Exception {
        final Map<String, Integer> priority = new LinkedHashMap<>();
        for (MethodCandidate method : methods) {
            if (!isInternal(method.function)) continue;
            int score = !method.vptrWrites.isEmpty() ? 6000 :
                method.vtableSlotIndex != null ? 5000 :
                "strong".equals(method.confidence) ? 3000 : 1000;
            priority.put(functionKey(method.function), score);
        }
        for (FieldAccess access : accesses) {
            String key = functionKey(access.method.function);
            if (!priority.containsKey(key)) continue;
            int score = priority.get(key);
            score += "write".equals(access.accessType) ? 500 : 100;
            if (!access.nestedEvidence.isEmpty()) {
                score += 200;
            }
            priority.put(key, score);
        }
        List<MethodCandidate> ordered = new ArrayList<>(methods);
        for (Iterator<MethodCandidate> iterator = ordered.iterator(); iterator.hasNext();) {
            if (!priority.containsKey(functionKey(iterator.next().function))) iterator.remove();
        }
        Collections.sort(ordered, new Comparator<MethodCandidate>() {
            @Override public int compare(MethodCandidate left, MethodCandidate right) {
                int compared = Integer.compare(priority.get(functionKey(right.function)),
                    priority.get(functionKey(left.function)));
                return compared != 0 ? compared : address(left.function).compareTo(address(right.function));
            }
        });
        List<Function> result = new ArrayList<>();
        Set<String> exportedKeys = new LinkedHashSet<>();
        for (Function function : vtableAnalysis.directInternalXrefFunctions.values()) {
            exportFunctionBundle(function, directory.resolve(safeFunctionName(function)), generatedAt);
            result.add(function);
            exportedKeys.add(functionKey(function));
        }
        int ordinaryExportCount = 0;
        for (MethodCandidate candidate : ordered) {
            if (ordinaryExportCount >= MAX_EXPORTED_FUNCTIONS) {
                break;
            }
            if (!exportedKeys.add(functionKey(candidate.function))) continue;
            exportFunctionBundle(candidate.function, directory.resolve(safeFunctionName(candidate.function)), generatedAt);
            result.add(candidate.function);
            ordinaryExportCount++;
        }
        return result;
    }

    private void exportFunctionBundle(Function function, Path output, Instant generatedAt) throws Exception {
        Files.createDirectories(output);
        Decompilation decompilation = decompile(function);
        ReferenceContext references = collectReferences(function);
        write(output.resolve("metadata.json"), json(metadata(function, decompilation, generatedAt)));
        write(output.resolve("decompiled.c"), decompilation.text);
        write(output.resolve("callers.json"), json(functionSummaries(sortedFunctions(function.getCallingFunctions(monitor)))));
        write(output.resolve("callees.json"), json(functionSummaries(sortedFunctions(function.getCalledFunctions(monitor)))));
        write(output.resolve("strings.json"), json(references.strings));
        write(output.resolve("globals.json"), json(references.globals));
        write(output.resolve("constants.json"), json(collectConstants(function)));
    }

    private Decompilation decompile(Function function) {
        if (function == null) {
            return Decompilation.failed("No function was supplied.");
        }
        String key = functionKey(function);
        Decompilation cached = decompilationCache.get(key);
        if (cached != null) {
            return cached;
        }
        try {
            DecompileResults results = decompiler.decompileFunction(function, DECOMPILE_TIMEOUT_SECONDS, monitor);
            if (!results.decompileCompleted() || results.getDecompiledFunction() == null) {
                String error = results.getErrorMessage();
                return cache(key, Decompilation.failed(error == null || error.trim().isEmpty()
                    ? "Decompiler returned no pseudocode." : error));
            }
            return cache(key, Decompilation.completed(
                results.getDecompiledFunction().getC(), results.getHighFunction()));
        }
        catch (RuntimeException exception) {
            return cache(key, Decompilation.failed(exception.getClass().getSimpleName() + ": " + safeMessage(exception)));
        }
    }

    private Decompilation cache(String key, Decompilation value) {
        decompilationCache.put(key, value);
        return value;
    }

    private ThunkResolution resolveThunk(Function original) throws CancelledException {
        if (original == null || !original.isThunk()) {
            return ThunkResolution.resolved(original, 0);
        }
        Set<String> visited = new LinkedHashSet<>();
        Function current = original;
        int hops = 0;
        while (current != null && current.isThunk()) {
            monitor.checkCancelled();
            if (!visited.add(functionKey(current)) || hops >= MAX_THUNK_HOPS) {
                return ThunkResolution.failed("Thunk cycle or safety limit reached.", hops);
            }
            current = current.getThunkedFunction(false);
            hops++;
        }
        return current == null ? ThunkResolution.failed("Thunk target is null.", hops)
            : ThunkResolution.resolved(current, hops);
    }

    private ThunkResolution resolveThunkUnchecked(Function function) {
        try {
            return resolveThunk(function);
        }
        catch (CancelledException exception) {
            return ThunkResolution.failed("Cancelled.", 0);
        }
    }

    private Address readPointer(Address address, int pointerSize) throws Exception {
        byte[] bytes = new byte[pointerSize];
        currentProgram.getMemory().getBytes(address, bytes);
        long value = 0;
        if (currentProgram.getLanguage().isBigEndian()) {
            for (byte item : bytes) value = (value << 8) | (item & 0xffL);
        }
        else {
            for (int index = bytes.length - 1; index >= 0; index--) value = (value << 8) | (bytes[index] & 0xffL);
        }
        return value == 0 ? null : currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(value);
    }

    private OffsetExpression extractBasePlusConstant(Varnode input) {
        Varnode value = stripWrappers(input);
        if (value == null) return null;
        PcodeOp definition = value.getDef();
        if (definition == null) return new OffsetExpression(value, 0);
        if ((definition.getOpcode() == PcodeOp.INT_ADD || definition.getOpcode() == PcodeOp.PTRSUB) &&
                definition.getNumInputs() == 2) {
            Varnode left = stripWrappers(definition.getInput(0));
            Varnode right = stripWrappers(definition.getInput(1));
            if (right != null && right.isConstant()) return new OffsetExpression(left, right.getOffset());
            if (definition.getOpcode() == PcodeOp.INT_ADD && left != null && left.isConstant())
                return new OffsetExpression(right, left.getOffset());
        }
        if (definition.getOpcode() == PcodeOp.PTRADD && definition.getNumInputs() == 3) {
            Varnode index = stripWrappers(definition.getInput(1));
            Varnode size = stripWrappers(definition.getInput(2));
            if (index != null && index.isConstant() && size != null && size.isConstant())
                return new OffsetExpression(stripWrappers(definition.getInput(0)), index.getOffset() * size.getOffset());
        }
        return null;
    }

    private Long offsetFromBase(Varnode expression, Varnode expectedBase, int depth) {
        if (expression == null || expectedBase == null || depth > MAX_TRACE_DEPTH) return null;
        Varnode value = stripWrappers(expression);
        if (sameIdentity(value, expectedBase)) return 0L;
        OffsetExpression offset = extractBasePlusConstant(value);
        if (offset == null || offset.base == value) return null;
        Long base = offsetFromBase(offset.base, expectedBase, depth + 1);
        return base == null ? null : base + offset.offset;
    }

    private static Varnode stripWrappers(Varnode input) {
        Varnode value = input;
        Set<Varnode> visited = Collections.newSetFromMap(new IdentityHashMap<Varnode, Boolean>());
        while (value != null && visited.add(value)) {
            PcodeOp definition = value.getDef();
            if (definition == null || definition.getNumInputs() == 0 || !isWrapper(definition.getOpcode())) return value;
            value = definition.getInput(0);
        }
        return value;
    }

    private static boolean sameIdentity(Varnode leftInput, Varnode rightInput) {
        Varnode left = stripWrappers(leftInput), right = stripWrappers(rightInput);
        return left == right || (left != null && right != null &&
            (left.equals(right) || (left.getHigh() != null && left.getHigh() == right.getHigh())));
    }

    private static boolean isWrapper(int opcode) {
        return opcode == PcodeOp.COPY || opcode == PcodeOp.CAST ||
            opcode == PcodeOp.INT_ZEXT || opcode == PcodeOp.INT_SEXT;
    }

    private static boolean isTraceable(int opcode) {
        return isWrapper(opcode) || opcode == PcodeOp.INT_ADD || opcode == PcodeOp.PTRSUB ||
            opcode == PcodeOp.PTRADD || opcode == PcodeOp.LOAD;
    }

    private Function directCalledFunction(PcodeOp call) {
        if (call == null || call.getNumInputs() == 0) return null;
        Address target = addressFromVarnode(stripWrappers(call.getInput(0)));
        return target == null ? null : currentProgram.getFunctionManager().getFunctionAt(target);
    }

    private Address addressFromVarnode(Varnode value) {
        if (value == null) return null;
        if (value.isAddress() && value.getAddress().isMemoryAddress()) return value.getAddress();
        if (value.isConstant() && value.getOffset() != 0)
            return currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(value.getOffset());
        return null;
    }

    private Function functionForSymbol(Symbol symbol) {
        Function function = currentProgram.getFunctionManager().getFunctionAt(symbol.getAddress());
        return function == null ? currentProgram.getFunctionManager().getFunctionContaining(symbol.getAddress()) : function;
    }

    private Function functionFromSummary(Map<String, Object> summary) {
        if (summary == null) return null;
        Address address = addressFromText((String) summary.get("functionAddress"));
        return address == null ? null : currentProgram.getFunctionManager().getFunctionAt(address);
    }

    private Address addressFromText(String text) {
        if (text == null) return null;
        try { return currentProgram.getAddressFactory().getAddress(text); }
        catch (RuntimeException exception) { return null; }
    }

    private static HighParam highParam(HighFunction function, int index) {
        if (function == null || index < 0) return null;
        LocalSymbolMap map = function.getLocalSymbolMap();
        return map == null || index >= map.getNumParams() ? null : map.getParam(index);
    }

    private static int highParamCount(HighFunction function) {
        return function == null || function.getLocalSymbolMap() == null ? 0 : function.getLocalSymbolMap().getNumParams();
    }

    private Map<String, Object> symbolRecord(Symbol symbol) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("name", symbol.getName());
        result.put("fullName", symbol.getName(true));
        result.put("address", formatAddress(symbol.getAddress()));
        result.put("symbolType", symbol.getSymbolType().toString());
        result.put("primary", symbol.isPrimary());
        result.put("source", symbol.getSource().toString());
        return result;
    }

    private Map<String, Object> functionSummary(Function function) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("functionName", function.getName());
        result.put("functionFullName", fullName(function));
        result.put("functionAddress", address(function));
        result.put("external", function.isExternal());
        result.put("thunk", function.isThunk());
        return result;
    }

    private List<Map<String, Object>> functionSummaries(List<Function> functions) {
        List<Map<String, Object>> result = new ArrayList<>();
        for (Function function : functions) result.add(functionSummary(function));
        return result;
    }

    private String selectedRelationship(Function selected, Function anchor) {
        if (anchor == null) return "anchor-unresolved";
        if (selected.equals(anchor)) return "selected-function-is-exact-anchor";
        if (anchor.getCalledFunctions(monitor).contains(selected)) return "selected-function-is-direct-callee-of-anchor";
        if (anchor.getCallingFunctions(monitor).contains(selected)) return "selected-function-is-direct-caller-of-anchor";
        return "selected-function-not-anchor-or-direct-neighbour";
    }

    private Map<String, Object> operationSummary(PcodeOp operation) {
        if (operation == null) return null;
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("opcode", operation.getMnemonic());
        result.put("sequenceNumber", operation.getSeqnum().toString());
        result.put("instructionAddress", sequenceAddress(operation));
        result.put("output", varnode(operation.getOutput()));
        List<Map<String, Object>> inputs = new ArrayList<>();
        for (int index = 0; index < operation.getNumInputs(); index++) {
            Map<String, Object> item = new LinkedHashMap<>();
            item.put("index", index);
            item.put("varnode", varnode(operation.getInput(index)));
            inputs.add(item);
        }
        result.put("inputs", inputs);
        return result;
    }

    private Map<String, Object> varnode(Varnode value) {
        if (value == null) return null;
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
            result.put("highVariable", highRecord);
        }
        return result;
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
                if (target == null || !target.isMemoryAddress()) continue;
                Data data = currentProgram.getListing().getDataContaining(target);
                boolean isString = data != null && data.hasStringValue();
                if (!isString && (!reference.getReferenceType().isData() || function.getBody().contains(target))) continue;
                Map<String, Map<String, Object>> destination = isString ? strings : globals;
                String key = target.toString();
                Map<String, Object> record = destination.get(key);
                if (record == null) {
                    record = new LinkedHashMap<>();
                    record.put("address", formatAddress(target));
                    record.put("symbol", primarySymbol(target));
                    record.put("dataType", data == null || data.getDataType() == null ? null : data.getDataType().getDisplayName());
                    record.put("value", isString ? String.valueOf(data.getValue()) : null);
                    record.put("sourceAddresses", new TreeSet<String>());
                    destination.put(key, record);
                }
                @SuppressWarnings("unchecked") Set<String> sources = (Set<String>) record.get("sourceAddresses");
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
                if (scalar == null) continue;
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
        return result;
    }

    private Map<String, Object> metadata(Function function, Decompilation decompilation, Instant generatedAt) {
        Map<String, Object> result = functionSummary(function);
        result.put("schemaVersion", 1);
        result.put("exportedAtUtc", generatedAt.toString());
        result.put("programName", currentProgram.getName());
        result.put("signature", function.getPrototypeString(true, true));
        result.put("decompilationCompleted", decompilation.completed);
        result.put("decompilationError", decompilation.error);
        return result;
    }

    private Map<String, Object> methodDocument(String className, List<MethodCandidate> methods) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("schemaVersion", 2);
        result.put("className", className);
        result.put("confidenceModel", confidenceModel());
        result.put("methods", methods);
        return result;
    }

    private Map<String, Object> receiverFamilyDocument(String className, List<MethodCandidate> methods) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("schemaVersion", 2);
        result.put("className", className);
        result.put("maximumDepth", MAX_RECEIVER_FAMILY_DEPTH);
        result.put("semantics", "Receiver-family provenance; medium entries are not proven C++ member methods.");
        List<MethodCandidate> family = new ArrayList<>();
        for (MethodCandidate method : methods) {
            if (method.receiverFamilyDepth != null && method.receiverFamilyDepth.intValue() > 0) family.add(method);
        }
        result.put("members", family);
        result.put("negativeResult", family.isEmpty() ? "no-receiver-preserving-helper-found" : null);
        return result;
    }

    private Map<String, Object> accessDocument(String className, long fieldOffset, Long nestedOffset,
            List<FieldAccess> accesses) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("schemaVersion", 1);
        result.put("className", className);
        result.put("scope", "Only internal strong/medium class-method and receiver-family candidates are searched.");
        result.put("fieldOffset", fieldOffset);
        result.put("fieldOffsetHex", unsignedHex(fieldOffset));
        result.put("nestedOffset", nestedOffset);
        result.put("nestedOffsetHex", nestedOffset == null ? null : unsignedHex(nestedOffset));
        result.put("accesses", accesses);
        return result;
    }

    private Map<String, Object> writeDocument(String className, long fieldOffset, List<FieldAccess> writes) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("schemaVersion", 1);
        result.put("className", className);
        result.put("fieldOffset", fieldOffset);
        result.put("fieldOffsetHex", unsignedHex(fieldOffset));
        result.put("writerCount", writes.size());
        result.put("negativeResult", writes.isEmpty() ? "no-class-scoped-writer-found" : null);
        result.put("writes", writes);
        return result;
    }

    private Map<String, Object> provenanceDocument(List<Map<String, Object>> records) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("schemaVersion", 1);
        result.put("maximumTraceDepth", MAX_TRACE_DEPTH);
        result.put("supportedCases", new String[] {
            "constant/global address", "function parameter", "call return", "fixed-offset load",
            "bounded direct address arithmetic"
        });
        result.put("records", records);
        return result;
    }

    private Map<String, Object> manifest(String className, Function selected, long fieldOffset,
            Long nestedOffset, Instant generatedAt, AnchorDiscovery anchors, VtableAnalysis vtableAnalysis,
            List<MethodCandidate> methods, List<FieldAccess> accesses,
            List<FieldAccess> writes, List<Function> exported) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("schemaVersion", 3);
        result.put("generatedAtUtc", generatedAt.toString());
        result.put("programName", currentProgram.getName());
        result.put("className", className);
        result.put("selectedFunction", functionSummary(selected));
        result.put("rootAnchor", className + EXPECTED_ANCHOR_SUFFIX);
        result.put("rootAnchorStatus", anchors.anchorResolvedExactly() ? "resolved-exact" : "anchor-unresolved");
        result.put("concreteVtableFound", !anchors.vtables.isEmpty());
        result.put("fieldOffset", fieldOffset);
        result.put("fieldOffsetHex", unsignedHex(fieldOffset));
        result.put("nestedOffset", nestedOffset);
        result.put("nestedOffsetHex", nestedOffset == null ? null : unsignedHex(nestedOffset));
        result.put("classMethodCount", methods.size());
        result.put("fieldAccessCount", accesses.size());
        result.put("fieldWriterCount", writes.size());
        result.put("negativeWriterResult", writes.isEmpty() ? "no-class-scoped-writer-found" : null);
        result.put("vtableSlotLimit", MAX_VTABLE_SLOTS);
        result.put("vtableValueMaximumDepth", MAX_VTABLE_VALUE_DEPTH);
        result.put("vtableReferenceCount", vtableAnalysis.totalReferenceCount());
        result.put("lifecycleCandidateCount", vtableAnalysis.lifecycleCandidates.size());
        result.put("receiverFamilyMaximumDepth", MAX_RECEIVER_FAMILY_DEPTH);
        result.put("exportLimit", MAX_EXPORTED_FUNCTIONS);
        result.put("directInternalVtableXrefExportCount", vtableAnalysis.directInternalXrefFunctions.size());
        result.put("directInternalVtableXrefExports", functionSummaries(
            new ArrayList<>(vtableAnalysis.directInternalXrefFunctions.values())));
        result.put("exportLimitSemantics",
            "Direct internal vtable-xref functions are forced first and do not consume the ordinary internal-function quota.");
        result.put("exportedFunctions", functionSummaries(exported));
        result.put("readOnly", true);
        result.put("limitations", new String[] {
            "Depends on symbols, defined functions, references, memory, and high p-code in the current analysis database.",
            "Each concrete vtable symbol is walked independently; observed nonzero vptr offsets are reported without inferring exact inheritance semantics.",
            "Vtable STORE values are resolved only through bounded, non-branching wrappers and constant arithmetic; LOAD, CALL, MULTIEQUAL, and ambiguous forms stop resolution.",
            "Medium membership requires bounded outbound parameter-0 receiver flow from a strong anchor; raw proximity and offset reuse are excluded.",
            "No general alias analysis, class hierarchy reconstruction, symbolic execution, or heap graph traversal is performed.",
            "Lifecycle role and nested-component type remain unresolved unless independently supported by exported evidence."
        });
        return result;
    }

    private List<Map<String, String>> confidenceModel() {
        List<Map<String, String>> result = new ArrayList<>();
        result.add(pair("strong", "exact class-qualified symbol, direct vtable slot, vtable writer, or thunk relationship"));
        result.add(pair("medium", "direct caller/callee receiver flow involving parameter 0 and a strong class method"));
        result.add(pair("weak", "recordable supporting context only; never establishes membership and is not searched for field accesses"));
        return result;
    }

    private static Map<String, String> pair(String confidence, String meaning) {
        Map<String, String> result = new LinkedHashMap<>();
        result.put("confidence", confidence);
        result.put("meaning", meaning);
        return result;
    }

    private static boolean containsIgnoreCase(String text, String expected) {
        return text.toLowerCase(Locale.ROOT).contains(expected.toLowerCase(Locale.ROOT));
    }

    private static boolean isVtableName(String name) {
        String lower = name == null ? "" : name.toLowerCase(Locale.ROOT);
        return lower.contains("vftable") || lower.contains("vtable");
    }

    private static boolean isRttiName(String name) {
        String lower = name == null ? "" : name.toLowerCase(Locale.ROOT);
        return lower.contains("rtti") || lower.contains("type descriptor") || lower.contains("type_info") ||
            lower.contains("complete object locator") || lower.contains("class hierarchy descriptor");
    }

    private static boolean isExactClassQualifiedFunction(String fullName, String className) {
        return fullName != null && (fullName.startsWith(className + "::") ||
            fullName.contains("::" + className + "::")) && !isVtableName(fullName);
    }

    private static boolean isInternal(Function function) {
        return function != null && !function.isExternal() && function.getBody() != null && !function.getBody().isEmpty();
    }

    private static String fullName(Function function) {
        Symbol symbol = function.getSymbol();
        return symbol == null ? function.getName() : symbol.getName(true);
    }

    private static List<Function> sortedFunctions(Set<Function> functions) {
        List<Function> result = new ArrayList<>(functions);
        Collections.sort(result, new Comparator<Function>() {
            @Override public int compare(Function left, Function right) {
                return left.getEntryPoint().compareTo(right.getEntryPoint());
            }
        });
        return result;
    }

    private List<String> symbolsAt(Address address) {
        List<String> result = new ArrayList<>();
        for (Symbol symbol : currentProgram.getSymbolTable().getSymbols(address)) result.add(symbol.getName(true));
        Collections.sort(result);
        return result;
    }

    private String primarySymbol(Address address) {
        Symbol symbol = currentProgram.getSymbolTable().getPrimarySymbol(address);
        return symbol == null ? null : symbol.getName(true);
    }

    private static long parseOffset(String text) {
        String value = text.trim();
        return value.startsWith("0x") || value.startsWith("0X")
            ? Long.parseUnsignedLong(value.substring(2), 16) : Long.parseLong(value);
    }

    private static String offsetLabel(long value) {
        return unsignedHex(value).substring(2);
    }

    private static String safeText(String value) {
        String safe = value.replaceAll("[^A-Za-z0-9._-]", "_");
        return safe.isEmpty() ? "class" : safe;
    }

    private static String safeFunctionName(Function function) {
        return safeText(function.getName()) + "__" + address(function).replaceAll("[^A-Za-z0-9._-]", "_");
    }

    private static String functionKey(Function function) { return function.getEntryPoint().toString(); }
    private static String address(Function function) { return formatAddress(function.getEntryPoint()); }
    private static String sequenceAddress(PcodeOp operation) {
        return operation == null ? null : formatAddress(operation.getSeqnum().getTarget());
    }
    private static String formatAddress(Address address) {
        return address == null ? null : address.toString().toUpperCase(Locale.ROOT);
    }
    private static String unsignedHex(long value) {
        return "0x" + Long.toUnsignedString(value, 16).toUpperCase(Locale.ROOT);
    }
    private static long value(Long value, long fallback) { return value == null ? fallback : value.longValue(); }
    private static Integer integerValue(Object value) { return value instanceof Number ? ((Number) value).intValue() : null; }
    private static String safeMessage(Throwable throwable) {
        String message = throwable.getMessage();
        return message == null || message.trim().isEmpty() ? "No error message was provided." : message;
    }

    private boolean isInsideGhidraProjectStorage(Path exportRoot) {
        if (state.getProject() == null || state.getProject().getProjectLocator() == null) return false;
        File directory = state.getProject().getProjectLocator().getProjectDir();
        return directory != null && exportRoot.startsWith(directory.toPath().toAbsolutePath().normalize());
    }

    private static void write(Path path, String contents) throws IOException {
        Files.write(path, contents.getBytes(StandardCharsets.UTF_8));
    }
    private static String json(Object value) { return JSON.toJson(value) + "\n"; }

    private static final class AnchorDiscovery {
        transient final Function selected;
        final List<Map<String, Object>> symbols = new ArrayList<>();
        final List<VtableCandidate> vtables = new ArrayList<>();
        final List<Map<String, Object>> rttiCandidates = new ArrayList<>();
        final List<Map<String, Object>> knownMethodAnchors = new ArrayList<>();
        final List<Map<String, Object>> constructorCandidates = new ArrayList<>();
        final Map<String, Object> knownRoot = new LinkedHashMap<>();
        transient Function knownRootFunction;
        AnchorDiscovery(Function selected) { this.selected = selected; }
        boolean anchorResolvedExactly() {
            for (Map<String, Object> anchor : knownMethodAnchors)
                if ("resolved-exact".equals(anchor.get("status"))) return true;
            return false;
        }
        Map<String, Object> document(String className) {
            Map<String, Object> result = new LinkedHashMap<>();
            result.put("schemaVersion", 1);
            result.put("className", className);
            result.put("symbols", symbols);
            result.put("vtableCandidates", vtables);
            result.put("rttiCandidates", rttiCandidates);
            result.put("knownMethodAnchors", knownMethodAnchors);
            result.put("constructorCandidates", constructorCandidates);
            result.put("knownRootFUN_1431bc320", knownRoot);
            return result;
        }
    }

    private static final class VtableCandidate {
        final String name;
        final String fullName;
        final String confidence = "strong";
        final String evidence = "Symbol contains the exact class text and vtable/vftable marker.";
        final String address;
        transient final Address rawAddress;
        int pointerSize;
        int maximumSlots;
        String stopReason;
        String stopDetail;
        int discoveredSlotCount;
        int internalFunctionCount;
        int externalFunctionCount;
        int duplicateResolvedFunctionCount;
        final List<VtableSlot> slots = new ArrayList<>();
        VtableCandidate(Symbol symbol) {
            name = symbol.getName(); fullName = symbol.getName(true);
            rawAddress = symbol.getAddress(); address = formatAddress(rawAddress);
        }
    }

    private static final class VtableSlot {
        final long slotIndex;
        final long byteOffset;
        final String byteOffsetHex;
        final String slotAddress;
        final String pointerValue;
        final String slotFunctionName;
        final String slotFunctionAddress;
        final String resolvedFunctionName;
        final String resolvedFunctionAddress;
        final int thunkHopCount;
        final String thunkError;
        final boolean internal;
        final boolean external;
        Long duplicateOfSlot;
        transient final Function resolvedFunction;
        VtableSlot(long slotIndex, long byteOffset, Address slotAddress, Address pointer,
                Function slotFunction, Function resolved, ThunkResolution thunk) {
            this.slotIndex = slotIndex; this.byteOffset = byteOffset; this.byteOffsetHex = unsignedHex(byteOffset);
            this.slotAddress = formatAddress(slotAddress); this.pointerValue = formatAddress(pointer);
            this.slotFunctionName = slotFunction.getName(); this.slotFunctionAddress = address(slotFunction);
            this.resolvedFunctionName = resolved == null ? null : resolved.getName();
            this.resolvedFunctionAddress = resolved == null ? null : address(resolved);
            this.thunkHopCount = thunk.hops; this.thunkError = thunk.error; this.resolvedFunction = resolved;
            this.internal = isInternal(resolved);
            this.external = resolved != null && resolved.isExternal();
        }
    }

    private static final class MethodCandidate {
        static final Comparator<MethodCandidate> ORDER = new Comparator<MethodCandidate>() {
            @Override public int compare(MethodCandidate left, MethodCandidate right) {
                int compared = Integer.compare(confidenceRank(right.confidence), confidenceRank(left.confidence));
                return compared != 0 ? compared : left.functionAddress.compareTo(right.functionAddress);
            }
        };
        transient final Function function;
        final String functionName;
        final String functionFullName;
        final String functionAddress;
        String confidence = "weak";
        final List<MembershipEvidence> membershipEvidence = new ArrayList<>();
        Long vtableSlotIndex;
        Long vtableByteOffset;
        final List<VptrWrite> vptrWrites = new ArrayList<>();
        Integer receiverFamilyDepth;
        String relationship;
        String receiverFamilySourceFunction;
        String receiverFamilySourceAddress;
        String receiverFamilyCallSite;
        Integer receiverArgumentIndex;
        String analysisError;
        MethodCandidate(Function function) {
            this.function = function; functionName = function.getName();
            functionFullName = fullName(function); functionAddress = address(function);
        }
        void upgrade(String value) { if (confidenceRank(value) > confidenceRank(confidence)) confidence = value; }
        void addEvidence(String kind, String detail) {
            for (MembershipEvidence item : membershipEvidence)
                if (item.kind.equals(kind) && item.detail.equals(detail)) return;
            membershipEvidence.add(new MembershipEvidence(kind, detail));
        }
        static int confidenceRank(String value) {
            return "strong".equals(value) ? 3 : "medium".equals(value) ? 2 : 1;
        }
    }

    private static final class MembershipEvidence {
        final String kind;
        final String detail;
        MembershipEvidence(String kind, String detail) { this.kind = kind; this.detail = detail; }
    }

    private static final class FieldAccess {
        static final Comparator<FieldAccess> ORDER = new Comparator<FieldAccess>() {
            @Override public int compare(FieldAccess left, FieldAccess right) {
                int writes = Boolean.compare("write".equals(right.accessType), "write".equals(left.accessType));
                if (writes != 0) return writes;
                int confidence = Integer.compare(MethodCandidate.confidenceRank(right.classConfidence),
                    MethodCandidate.confidenceRank(left.classConfidence));
                return confidence != 0 ? confidence : left.instructionAddress.compareTo(right.instructionAddress);
            }
        };
        transient final MethodCandidate method;
        final String functionName;
        final String functionAddress;
        final String classConfidence;
        final List<MembershipEvidence> classMembershipEvidence;
        final String accessType;
        final String instructionAddress;
        final long fieldOffset;
        final String fieldOffsetHex;
        final Map<String, Object> operation;
        String valueSummary;
        String writeKind;
        Map<String, Object> provenance;
        boolean nestedOffset20Observed;
        final List<String> evidence = new ArrayList<>();
        final List<Map<String, Object>> nestedEvidence = new ArrayList<>();
        FieldAccess(MethodCandidate method, Map<String, Object> operationRecord,
                PcodeOp operation, String accessType, long fieldOffset) {
            this.method = method; functionName = method.functionName; functionAddress = method.functionAddress;
            classConfidence = method.confidence; classMembershipEvidence = method.membershipEvidence;
            this.accessType = accessType; instructionAddress = sequenceAddress(operation);
            this.fieldOffset = fieldOffset; fieldOffsetHex = unsignedHex(fieldOffset);
            this.operation = operationRecord;
            evidence.add(operation.getMnemonic() + " address reduces structurally to parameter 0 plus " +
                unsignedHex(fieldOffset) + ".");
            evidence.add("Class membership is independently supported at " + method.confidence + " confidence.");
        }
        Map<String, Object> provenanceRecord() {
            Map<String, Object> result = new LinkedHashMap<>();
            result.put("functionName", functionName); result.put("functionAddress", functionAddress);
            result.put("classConfidence", classConfidence); result.put("instructionAddress", instructionAddress);
            result.put("fieldOffset", fieldOffset); result.put("writeKind", writeKind);
            result.put("valueSummary", valueSummary); result.put("writtenValueProvenance", provenance);
            result.put("nestedOffset20Observed", nestedOffset20Observed); result.put("nestedEvidence", nestedEvidence);
            return result;
        }
    }

    private static final class VptrWrite {
        final String storeAddress;
        final String vtableName;
        final String vtableAddress;
        final long receiverOffset;
        final String receiverOffsetHex;
        final String position;
        final int operationIndex;
        final int operationCount;
        final String valueResolutionBasis;
        final List<String> valueDefinitionPath;
        final List<Map<String, Object>> otherVptrWrites = new ArrayList<>();
        VptrWrite(PcodeOp operation, VtableCandidate vtable, long receiverOffset,
                String position, int operationIndex, int operationCount) {
            storeAddress = sequenceAddress(operation); vtableName = vtable.fullName;
            vtableAddress = vtable.address; this.receiverOffset = receiverOffset;
            receiverOffsetHex = unsignedHex(receiverOffset); this.position = position;
            this.operationIndex = operationIndex; this.operationCount = operationCount;
            valueResolutionBasis = "direct-vtable-address";
            valueDefinitionPath = Collections.singletonList("CONSTANT_ADDRESS " + vtable.address);
        }
        VptrWrite(VtableReference reference) {
            storeAddress = reference.storeAddress; vtableName = reference.vtableName;
            vtableAddress = reference.vtableAddress; receiverOffset = reference.receiverOffset.longValue();
            receiverOffsetHex = unsignedHex(receiverOffset); position = reference.position;
            operationIndex = reference.operationIndex; operationCount = reference.operationCount;
            valueResolutionBasis = reference.valueResolutionBasis;
            valueDefinitionPath = new ArrayList<>(reference.valueDefinitionPath);
        }
        Map<String, Object> toMap() {
            Map<String, Object> result = new LinkedHashMap<>();
            result.put("storeAddress", storeAddress); result.put("vtableName", vtableName);
            result.put("vtableAddress", vtableAddress); result.put("receiverOffset", receiverOffset);
            result.put("receiverOffsetHex", receiverOffsetHex);
            result.put("position", position); result.put("operationIndex", operationIndex);
            result.put("operationCount", operationCount);
            result.put("valueResolutionBasis", valueResolutionBasis);
            result.put("valueDefinitionPath", valueDefinitionPath);
            result.put("otherVptrWrites", otherVptrWrites);
            return result;
        }
    }

    private static final class VtableAnalysis {
        final List<VtableReferenceGroup> groups = new ArrayList<>();
        final List<LifecycleCandidate> lifecycleCandidates = new ArrayList<>();
        transient final Map<String, Function> directInternalXrefFunctions = new LinkedHashMap<>();
        int totalReferenceCount() {
            int count = 0;
            for (VtableReferenceGroup group : groups) count += group.references.size();
            return count;
        }
        Map<String, Object> xrefDocument(String className) {
            Map<String, Object> result = new LinkedHashMap<>();
            result.put("schemaVersion", 3); result.put("className", className);
            result.put("vtables", groups);
            result.put("negativeResult", totalReferenceCount() == 0 ? "no-vtable-references" : null);
            return result;
        }
        Map<String, Object> lifecycleDocument(String className) {
            Map<String, Object> result = new LinkedHashMap<>();
            result.put("schemaVersion", 3); result.put("className", className);
            result.put("classifications", new String[] {
                "constructor-like", "destructor-like", "lifecycle-helper", "unknown"
            });
            result.put("candidates", lifecycleCandidates);
            result.put("negativeResult", lifecycleCandidates.isEmpty() ? "no-structural-vptr-store" : null);
            return result;
        }
    }

    private static final class VtableReferenceGroup {
        final String vtableName;
        final String vtableAddress;
        final int discoveredSlotCount;
        final List<VtableReference> references = new ArrayList<>();
        int referenceCount;
        int structuralVptrStoreCount;
        String negativeResult;
        VtableReferenceGroup(VtableCandidate vtable) {
            vtableName = vtable.fullName; vtableAddress = vtable.address;
            discoveredSlotCount = vtable.slots.size();
        }
        void finalizeCounts() {
            referenceCount = references.size();
            Set<String> stores = new LinkedHashSet<>();
            for (VtableReference reference : references) {
                if ("vptr-store".equals(reference.referenceKind)) stores.add(
                    reference.functionAddress + ":" + reference.storeAddress + ":" + reference.receiverOffset);
            }
            structuralVptrStoreCount = stores.size();
            negativeResult = references.isEmpty() ? "no-vtable-references" :
                structuralVptrStoreCount == 0 ? "no-structural-vptr-stores" : null;
        }
    }

    private static final class VtableReference {
        final String vtableName;
        final String vtableAddress;
        final String fromAddress;
        String instructionAddress;
        final String ghidraReferenceType;
        String referenceKind;
        String confidence = "supporting";
        String functionName;
        String functionAddress;
        transient final Function function;
        String pcodeOp;
        boolean writtenToMemory;
        String storeAddress;
        Map<String, Object> resolvedStoreOperation;
        Map<String, Object> destinationExpression;
        Long receiverOffset;
        String valueResolutionBasis;
        final List<String> valueDefinitionPath = new ArrayList<>();
        final List<String> receiverEvidence = new ArrayList<>();
        final List<Map<String, Object>> pcodeOperations = new ArrayList<>();
        int operationIndex;
        int operationCount;
        String position;
        String analysisError;
        VtableReference(VtableCandidate vtable, Reference reference, Function function) {
            vtableName = vtable.fullName; vtableAddress = vtable.address;
            fromAddress = formatAddress(reference.getFromAddress()); instructionAddress = fromAddress;
            ghidraReferenceType = reference.getReferenceType().toString(); this.function = function;
            referenceKind = reference.getReferenceType().isData() ? "direct data reference" : "other";
            if (function != null) { functionName = function.getName(); functionAddress = address(function); }
        }
        VptrWrite toVptrWrite() { return new VptrWrite(this); }
    }

    private static final class LifecycleCandidate {
        static final Comparator<LifecycleCandidate> ORDER = new Comparator<LifecycleCandidate>() {
            @Override public int compare(LifecycleCandidate left, LifecycleCandidate right) {
                return left.functionAddress.compareTo(right.functionAddress);
            }
        };
        transient final Function function;
        final String functionName;
        final String functionAddress;
        String classification = "unknown";
        String confidence = "supporting";
        boolean calledFromAllocationPattern;
        boolean teardownCallAfterVptr;
        String returnBehavior = "not-observed";
        int receiverRelativeStoreCount;
        Long primaryVptrOffset;
        final Set<Long> secondaryVptrOffsets = new TreeSet<>();
        final List<VptrWrite> vptrStores = new ArrayList<>();
        final List<Map<String, Object>> callers = new ArrayList<>();
        final List<Map<String, Object>> callees = new ArrayList<>();
        final List<String> evidence = new ArrayList<>();
        final List<String> limitations = new ArrayList<>();
        LifecycleCandidate(Function function) {
            this.function = function; functionName = function.getName(); functionAddress = address(function);
        }
        Map<String, Object> toLegacyMap() {
            Map<String, Object> result = new LinkedHashMap<>();
            result.put("function", functionName); result.put("functionAddress", functionAddress);
            result.put("classification", classification); result.put("confidence", confidence);
            result.put("vptrStores", vptrStores); result.put("evidence", evidence);
            result.put("limitations", limitations); return result;
        }
    }

    private static final class VtableValueResolution {
        boolean resolved;
        String status;
        String basis;
        String resolvedAddress;
        int maximumDepth;
        final List<String> definitionPath = new ArrayList<>();
        transient VtableCandidate vtable;
    }

    private static final class NumericResolution {
        boolean resolved;
        long value;
        String status;
        final List<String> definitionPath = new ArrayList<>();
        NumericResolution fail(String value) { status = value; resolved = false; return this; }
        NumericResolution merge(NumericResolution child) {
            definitionPath.addAll(child.definitionPath);
            resolved = child.resolved; value = child.value; status = child.status;
            return this;
        }
    }

    private static final class ThunkResolution {
        final Function resolvedFunction; final int hops; final String error;
        private ThunkResolution(Function function, int hops, String error) {
            resolvedFunction = function; this.hops = hops; this.error = error;
        }
        static ThunkResolution resolved(Function function, int hops) { return new ThunkResolution(function, hops, null); }
        static ThunkResolution failed(String error, int hops) { return new ThunkResolution(null, hops, error); }
    }

    private static final class OffsetExpression {
        final Varnode base; final long offset;
        OffsetExpression(Varnode base, long offset) { this.base = base; this.offset = offset; }
    }

    private static final class Decompilation {
        final boolean completed; final String text; final String error; transient final HighFunction highFunction;
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

    private static final class ReferenceContext {
        final List<Map<String, Object>> strings; final List<Map<String, Object>> globals;
        ReferenceContext(List<Map<String, Object>> strings, List<Map<String, Object>> globals) {
            this.strings = strings; this.globals = globals;
        }
    }
}
