# Codex Brief — Integrate Stack-Object Correlation into Virtual Receiver Resolution

## Context

This repository supports reverse engineering of Starfield's runtime inorganic resource-generation system.

Before making changes, read:

- `AGENTS.md`
- `README.md`
- `docs/known-facts.md`
- `docs/hypotheses.md`
- `docs/function-register.md`
- `ghidra/README.md`
- `ghidra/scripts/ExportSelectedFunctionContext.java`
- `ghidra/scripts/ExportFunctionNeighbourhood.java`

The current exporter has been live-tested repeatedly against:

```text
FUN_1431bc320
0x1431BC320
CreationKit.exe
```

The relevant virtual call is:

```text
CALLIND at 0x1431BC350
```

The analyzer already knows:

```text
kind: vtable
vtableByteOffset: 0x50
vtableSlotIndex: 10
```

Previous attempts to resolve the receiver failed with:

```text
unresolved-receiver-provenance
```

The latest diagnostic iteration established the missing relationship mechanically.

For `CALLIND 0x1431BC350`:

```text
arguments[0].stackAddressProvenance.stackOffset = -168
```

which corresponds to:

```text
stack[-0xA8]
```

The call-target definition independently identifies stack-backed storage at:

```text
stack[-0xA8]
```

and the diagnostic result reports:

```text
receiverStorageCorrelation.status = matched-stack-object
sameStackObject = true
```

The important semantic relationship is now established:

```text
CALLIND argument 0 = address of stack[-0xA8]
call-target vptr source = contents of stack[-0xA8]
```

Conceptually:

```text
this = &local_a8
vptr = local_a8[0]
```

This is the expected C++ virtual-dispatch relationship.

The next task is to use that proven stack-object correlation in the actual receiver resolver.

---

# Goal

Enhance the real virtual-call receiver-resolution logic so that it can accept this supported pattern:

```text
argument 0 resolves to address of stack object X
AND
call target reads vptr from stack object X
```

When both sides resolve to the same stack offset, treat them as the same receiver object for purposes of constructor/vptr provenance.

Then allow the existing initializer/constructor-provenance logic to continue.

The immediate acceptance target is:

```text
CALLIND at 0x1431BC350
```

in:

```text
FUN_1431bc320
```

The hoped-for full chain is:

```text
CALLIND argument 0
    ↓
&stack[-0xA8]

call-target vptr source
    ↓
stack[-0xA8]

same stack object
    ↓
receiver established
    ↓
find earlier initializer call
    ↓
resolve initializer/thunk
    ↓
recover vptr store
    ↓
identify vtable
    ↓
resolve slot 10
    ↓
export concrete target function
```

---

# Required Resolver Enhancement

Add a new conservative receiver-resolution basis:

```text
stack-object-address-vptr-match
```

or similarly clear terminology.

For a vtable-style `CALLIND`, attempt the following only when existing direct/high-variable normalization does not already resolve the receiver:

1. derive stack-address provenance for the first actual call argument;
2. identify stack-backed base storage in the call-target vptr expression;
3. require both to resolve to exactly one stack offset;
4. require the offsets to match exactly;
5. require compatible pointer/object sizes where practical;
6. accept the argument as the address of the receiver object;
7. pass that recovered receiver identity into the existing constructor/vptr provenance path.

Do not use approximate or nearest-offset matching.

Do not infer based on variable names.

Do not infer based on storage reuse alone unless the address-vs-contents relationship is explicitly established.

---

# Preferred Evidence

For the supported case, the resolver should record evidence such as:

```json
{
  "receiverResolution": {
    "status": "resolved-stack-object",
    "resolutionBasis": "stack-object-address-vptr-match",
    "argumentIndex": 0,
    "argumentStackOffset": -168,
    "targetVptrStorageStackOffset": -168,
    "sameStackObject": true
  }
}
```

The exact schema may differ if the current implementation already has a better location for this data.

Preserve the diagnostics that established the match.

---

# Existing Receiver Resolution Order

Prefer a conservative resolution order like:

1. exact varnode / high-variable relationship;
2. existing simple normalization;
3. stack-object address/vptr-storage correlation;
4. otherwise unresolved.

Do not make the new rule override a stronger existing result.

If two independent methods disagree, report ambiguity rather than choosing one.

---

# Constructor / Initializer Provenance

Once the receiver is accepted through the new stack-object rule, reuse the existing constructor/vptr provenance implementation.

Do not rewrite it unless the live result exposes a separate bug.

The existing logic should attempt to:

1. find earlier direct calls whose argument 0 matches the recovered receiver;
2. resolve thunks;
3. inspect the initializer implementation;
4. locate offset-zero vptr stores through parameter 0;
5. identify uniquely named `vtable` / `vftable` symbols;
6. reject ambiguity;
7. use the recovered vtable to resolve the known slot.

---

# Important INDIRECT Evidence

The latest diagnostics showed that the target-side stack value:

```text
stack[-0xA8]
```

is defined by an `INDIRECT` p-code operation associated with an earlier call near:

```text
0x1431BC331
```

This is useful supporting evidence that the earlier call may modify the vptr-bearing storage.

Preserve this evidence in diagnostics/provenance where practical.

Do not treat `INDIRECT` alone as proof of constructor semantics.

---

# Expected Immediate Result

A successful live run should progress beyond:

```text
unresolved-receiver-provenance
```

for:

```text
0x1431BC350
```

The next expected possibilities are:

```text
resolved-static-vtable
```

or a more specific constructor/vptr failure such as:

```text
unresolved-no-initializer-call
unresolved-no-vptr-store
unresolved-vtable-symbol
unresolved-ambiguous-vptr-stores
unresolved-no-function-at-slot
```

Any of those would demonstrate that the receiver-resolution barrier has been crossed.

---

# Best-Case Acceptance Result

The ideal output is conceptually:

```text
callSiteAddress: 1431BC350
receiverResolutionBasis: stack-object-address-vptr-match
receiverStackOffset: -168
initializer: FUN_140d7ce60 (or resolved implementation)
vtableName: TESContainer::vftable
vtableByteOffset: 80
vtableSlotIndex: 10
resolvedFunctionName: FUN_...
resolvedFunctionAddress: ...
status: resolved-static-vtable
```

Do not hard-code:

- `FUN_140d7ce60`;
- `TESContainer::vftable`;
- the target function;
- addresses beyond the acceptance-test call site.

Discover them from Ghidra.

---

# Graph and Export Integration

If the virtual call resolves successfully:

- add/update the virtual edge in `graph.json`;
- preserve the call-site address;
- preserve the vtable name/address;
- preserve the slot offset/index;
- preserve the receiver-resolution basis;
- export the resolved target's standard seven-file bundle;
- deduplicate by resolved function entry address.

Do not alter the existing direct-edge schema unnecessarily.

---

# `indirect-calls.json`

Increment schema version only if required by the added receiver-resolution fields.

Preserve:

- previous diagnostics;
- initializer candidates;
- vptr-store diagnostics;
- failure reasons;
- call-target metadata;
- stack provenance evidence.

A successful resolution should retain the evidence chain rather than replacing diagnostics with only the final answer.

---

# P-code Diagnostics

Keep `pcode-diagnostics.json`.

Do not remove or reduce the useful argument-provenance diagnostics now that they have served their purpose.

They are valuable evidence if constructor provenance fails in the next stage.

Do not expand diagnostic scope further unless necessary for a concrete failure.

---

# Safety Requirements

The script must remain read-only with respect to the Ghidra program.

Do not:

- begin transactions;
- rename functions;
- create labels;
- add comments;
- change signatures;
- apply types;
- modify memory;
- intentionally alter analysis state.

Only write export files.

---

# Documentation

Update:

```text
ghidra/README.md
```

to explain:

- the new stack-object receiver-resolution rule;
- that it specifically correlates `&stack[X]` with vptr storage at `stack[X]`;
- that exact stack-offset equality is required;
- that this is still a conservative supported case rather than general alias analysis;
- how to interpret the new resolution basis;
- the live-test target.

---

# Research Documentation

Do not update `known-facts.md` with semantic claims about the virtual target until a live run resolves it and the exported implementation is inspected.

If the live result successfully identifies the concrete function, it is acceptable to update:

```text
docs/function-register.md
```

with the directly supported call relationship only.

Do not rename the function in Ghidra.

---

# Explicit Non-Goals

Do not implement yet:

- general pointer alias analysis;
- `MULTIEQUAL` receiver resolution;
- arbitrary stack-object reconstruction;
- heap-object provenance;
- class hierarchy reconstruction;
- multiple inheritance support;
- symbolic execution;
- deeper recursive call-tree export;
- automatic function naming;
- headless Ghidra execution;
- resource-algorithm interpretation.

This iteration should only integrate the already-proven stack-object correlation into receiver resolution.

---

# Live Acceptance Test

Run:

```text
ExportFunctionNeighbourhood.java
```

with the cursor inside:

```text
FUN_1431bc320
0x1431BC320
```

Inspect the record for:

```text
CALLIND @ 0x1431BC350
```

Minimum success criterion:

> The call no longer fails at `unresolved-receiver-provenance` because the receiver is established via the `stack[-0xA8]` address/vptr correlation.

Best-case success:

> The analyzer resolves the constructor vptr, identifies the concrete vtable, resolves slot 10, and exports the target function.

---

# Deliverables

When finished, report:

1. files modified;
2. files added, if any;
3. exact resolver rule added;
4. resolver precedence/order;
5. how stack-address provenance is reused;
6. how target vptr-storage offset is selected;
7. how ambiguity/conflict is handled;
8. receiver-resolution schema changes;
9. whether constructor/vptr logic was modified;
10. graph/output changes;
11. exact live-test instructions;
12. expected minimum and best-case results;
13. known limitations.

Do not broaden receiver resolution beyond this proven case unless the live test exposes a specific need.
