# Codex Brief — Ordered Constructor vptr Writes and Final Vtable Selection

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

The current exporter has now successfully crossed the virtual-receiver provenance barrier for:

```text
FUN_1431bc320
0x1431BC320
CreationKit.exe
```

The relevant virtual call is:

```text
CALLIND at 0x1431BC350
```

Receiver resolution now succeeds using:

```text
stack-object-address-vptr-match
```

with:

```text
argumentStackOffset: -168
targetVptrStorageStackOffset: -168
sameStackObject: true
```

The analyzer then proceeds into the earlier initializer/constructor and finds two accepted vptr stores to offset zero of the receiver:

```text
0x140D7CE70  BaseFormComponent::vftable
0x140D7CE87  TESContainer::vftable
```

The current result is:

```text
status: unresolved-ambiguous-vptr-stores
```

The constructor decompilation is approximately:

```c
*param_1 = BaseFormComponent::vftable;
thunk_FUN_140d6edb0((longlong)(param_1 + 1));
*param_1 = TESContainer::vftable;
```

This is consistent with normal C++ base-to-derived construction behavior:

```text
base-class vptr installed
    ↓
base/member initialization
    ↓
derived-class vptr installed
```

The next task is to allow the resolver to select a single final vtable only when the constructor's ordered control flow makes that choice deterministic.

---

# Goal

Enhance the existing constructor/vptr provenance logic so that multiple accepted vptr stores to the same receiver offset can be resolved when one store is demonstrably the final effective vptr before function return.

The immediate target is:

```text
FUN_140d7ce60
```

as reached from:

```text
FUN_1431bc320
```

The expected final vtable is believed to be:

```text
TESContainer::vftable
```

but this must not be hard-coded.

The analyzer must derive the result from actual ordered control-flow evidence.

---

# Core Rule

Do NOT implement:

```text
"last vtable store in source/decompiler order wins"
```

as a global heuristic.

Instead, implement a conservative supported case:

> When multiple accepted vptr stores target the same receiver offset, select one only if a unique final store can be proven to dominate all normal returns / be the final reachable write on all supported execution paths before return.

If that cannot be established confidently, preserve ambiguity.

---

# Supported Immediate Pattern

This iteration only needs to support a simple constructor-like sequence such as:

```text
STORE this+0 <- BaseClass::vftable
...
STORE this+0 <- DerivedClass::vftable
RETURN
```

where:

- both stores target the same offset;
- control flow between them is linear or otherwise unambiguous;
- the later store is always executed before any normal return;
- there is no later competing store to the same vptr slot;
- there is no branch where an earlier vtable remains the final value.

This should be sufficient for the immediate `TESContainer` case if the Ghidra control flow confirms it.

---

# Required Analysis

For each accepted vptr store candidate, record:

- store instruction / sequence address;
- receiver offset;
- vtable name/address;
- containing basic block;
- order within block where relevant;
- outgoing control-flow relationships;
- whether the store can reach a normal return without another accepted vptr store to the same offset;
- whether another accepted store post-dominates or supersedes it.

Use whichever Ghidra CFG / p-code APIs are appropriate.

Prefer structured control-flow analysis over decompiled-C text order.

---

# Conservative Final-Store Selection

A candidate may be selected as the final effective vptr only if:

1. all accepted vptr candidates write the same receiver offset;
2. exactly one candidate is reachable after all earlier candidates on supported normal execution paths;
3. every normal return reachable from the constructor sees that candidate as the last accepted vptr write to that offset;
4. no later ambiguous write to the same offset exists;
5. there is no conflicting branch in which another candidate remains final.

If those conditions are not met:

```text
unresolved-ambiguous-vptr-stores
```

should remain.

Do not guess based on class-name specificity or "derived-looking" symbol names.

---

# Suggested Resolution Basis

For a successful case, record:

```text
resolutionBasis: ordered-final-vptr-store
```

or similar.

Suggested provenance:

```json
{
  "vptrSelection": {
    "status": "resolved-final-store",
    "resolutionBasis": "ordered-final-vptr-store",
    "receiverOffset": 0,
    "candidateCount": 2,
    "selectedStoreAddress": "140D7CE87",
    "selectedVtableName": "TESContainer::vftable",
    "selectedVtableAddress": "...",
    "supersededStores": [
      {
        "storeAddress": "140D7CE70",
        "vtableName": "BaseFormComponent::vftable"
      }
    ],
    "evidence": [
      "all candidates write receiver offset 0",
      "selected store occurs after earlier candidate",
      "selected store is the final accepted vptr write on all supported normal return paths"
    ]
  }
}
```

The exact schema may differ if the current structure has a cleaner location.

---

# Existing Constructor Provenance to Preserve

Do not rewrite the successful parts of the current pipeline.

Preserve:

- receiver resolution;
- earlier initializer-call discovery;
- thunk resolution;
- parameter-0 identification;
- offset-zero vptr-store detection;
- vtable symbol filtering;
- pointer-size handling;
- slot calculation;
- target pointer read;
- target thunk resolution;
- function bundle export;
- graph integration;
- diagnostics.

Only change how multiple accepted vptr stores are disambiguated.

---

# Best-Case Full Resolution Flow

The expected pipeline after this change is:

```text
CALLIND @ 1431BC350
    ↓
receiver established via stack-object correlation
    ↓
initializer resolved
    ↓
two vptr stores found
    ↓
ordered CFG analysis selects final effective vptr
    ↓
TESContainer::vftable
    ↓
slot +0x50 / index 10
    ↓
concrete function pointer
    ↓
resolved Ghidra function
    ↓
export full seven-file bundle
```

Do not hard-code any function or vtable name in the implementation.

---

# Failure Modes

Add or refine failure reasons such as:

```text
unresolved-ambiguous-vptr-stores
unresolved-branching-vptr-final-state
unresolved-no-unique-final-vptr
unresolved-vptr-control-flow
```

A failed control-flow proof should not fall back to "take last store".

Preserve all candidate vptr diagnostics.

---

# Control-Flow Scope

This is not a request for a full post-dominator framework unless that is the cleanest available Ghidra API.

A simpler bounded analysis is acceptable for the immediate case if it can prove the property safely.

Possible approaches:

- basic-block reachability;
- path exploration from each store to normal returns;
- checking whether every path from an earlier store to return passes through the selected later store;
- using existing dominator/post-dominator facilities if available.

Prefer correctness and transparency over sophistication.

Document the method used.

---

# Return Handling

Consider normal returns only for this supported case.

If exception/unwind edges or indirect control flow make the proof unclear:

- record the limitation;
- preserve ambiguity.

Do not attempt full exception-flow analysis in this iteration.

---

# Output and Schema

Preserve:

```text
indirect-calls.json
graph.json
pcode-diagnostics.json
manifest.json
```

If schema changes are needed:

- increment only the relevant schema version;
- document the new fields;
- preserve backward-compatible existing fields where practical.

The successful virtual-call record should retain:

- receiver-resolution basis;
- initializer provenance;
- all vptr candidates;
- final-vptr selection evidence;
- vtable name/address;
- slot offset/index;
- resolved target function.

---

# Graph Integration

If resolution succeeds:

- add/update the virtual edge in `graph.json`;
- preserve:
  - call-site address;
  - edge kind;
  - receiver-resolution basis;
  - final-vptr selection basis;
  - vtable name/address;
  - byte offset;
  - slot index;
  - resolved function name/address.

Do not alter direct edges unnecessarily.

---

# Function Export

If the slot resolves to an internal function:

- export the normal seven-file bundle;
- deduplicate by function entry address;
- retain how the function was reached.

Do not rename the function.

---

# Research Documentation

Do not add semantic claims to `known-facts.md` merely because the virtual target resolves.

If the live result identifies a concrete target, it is appropriate to update:

```text
docs/function-register.md
```

with the directly supported relationship:

```text
FUN_1431bc320
    ↓ virtual dispatch through selected final vtable + 0x50
FUN_xxxxxxxxx
```

Use cautious interpretation language.

Do not rename Ghidra symbols.

---

# Safety Requirements

The exporter must remain read-only.

Do not:

- start transactions;
- rename symbols/functions;
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

- why constructors may contain multiple vptr writes;
- the new final-vptr selection rule;
- that simple source/decompiler "last write wins" is NOT used;
- what evidence is required;
- how ambiguity is preserved;
- the live-test target.

---

# Explicit Non-Goals

Do not implement yet:

- general C++ constructor reconstruction;
- class hierarchy inference;
- multiple inheritance vptr selection;
- secondary vptr handling;
- exception-flow modeling;
- heap-object provenance;
- symbolic execution;
- deeper call-tree recursion;
- automatic semantic naming;
- headless Ghidra execution;
- resource-algorithm interpretation.

This iteration is only about selecting a unique final vptr from multiple constructor writes when control flow proves it.

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

Inspect:

```text
CALLIND @ 0x1431BC350
```

Minimum success criterion:

> The previous `unresolved-ambiguous-vptr-stores` result progresses to either a unique final-vptr selection or a more precise control-flow ambiguity reason.

Best-case success:

```text
receiverResolution: resolved-stack-object
vptrSelection: resolved-final-store
selectedVtableName: TESContainer::vftable
vtableByteOffset: 80
vtableSlotIndex: 10
status: resolved-static-vtable
resolvedFunctionName: FUN_...
resolvedFunctionAddress: ...
```

and the resolved target's full context bundle is exported.

---

# Deliverables

When finished, report:

1. files modified;
2. files added, if any;
3. final-vptr selection algorithm;
4. control-flow APIs used;
5. how normal returns are identified;
6. how earlier stores are proven superseded;
7. how branches/conflicts are handled;
8. any new statuses;
9. schema changes;
10. whether constructor/vptr detection itself changed;
11. exact live-test instructions;
12. expected minimum and best-case outcomes;
13. known limitations.

Do not broaden constructor analysis beyond this supported case until the live result has been reviewed.
