# Codex Brief — ResourceViewWidget Vtable Xrefs, Constructor Discovery, and `+0xA0` Revisit

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
- `ghidra/scripts/AnalyzeFieldProvenance.java`
- `ghidra/scripts/AnalyzeClassFieldProvenance.java`

The current class-scoped analysis has now live-confirmed concrete `CKGalaxyView::ResourceViewWidget` vtables.

Observed live anchors:

```text
CKGalaxyView::ResourceViewWidget::vftable
0x148B7CFB0
```

and a second vtable:

```text
CKGalaxyView::ResourceViewWidget::vftable
0x148B7D170
```

The first table contains 45 slots. Early internal Creation Kit functions include:

```text
slot 0 -> FUN_143546880
slot 1 -> FUN_14354dd30
slot 2 -> FUN_143549f80
slot 3 -> FUN_1431e7d20
```

The second table contains 7 slots, with:

```text
slot 0 -> FUN_1431e74d0
```

and the remaining slots largely resolving to Qt methods.

The exact `ResourceViewWidget::OnApplySeed` symbol did not resolve through the class analyzer, and `FUN_1431bc320` is not directly present in either vtable. This is not surprising for a Qt slot/callback, which need not be virtual.

The previous class-scoped analyzer therefore found no class-scoped `+0xA0` writer.

The important new direction is:

> Use xrefs to the confirmed `ResourceViewWidget` vtables to find constructor/destructor candidates and build a broader nonvirtual receiver-preserving method family.

Then revisit:

```text
this + 0xA0
```

within that stronger class-specific set.

---

# Research Question

Answer, with machine-readable evidence:

> Which functions reference or install the confirmed `CKGalaxyView::ResourceViewWidget` vtables, which of those are constructor/destructor/lifecycle candidates, and can that class-specific lifecycle/method family reveal where `this + 0xA0` is initialized or assigned?

Secondary question:

> Can the second vtable be tied to a secondary base/subobject at a nonzero offset within `ResourceViewWidget`?

Do not assume a precise inheritance layout unless supported.

---

# Goal

Add focused analysis that:

1. searches xrefs to both confirmed `ResourceViewWidget` vtable addresses;
2. classifies reference kinds;
3. identifies functions that write either vtable through a receiver pointer;
4. records the receiver offset of each vptr store;
5. identifies constructor/destructor/lifecycle candidates;
6. exports internal Creation Kit vtable functions before inherited external Qt slots;
7. expands a bounded receiver-preserving nonvirtual method family from strong anchors;
8. searches that family for structural `this + 0xA0` reads/writes;
9. traces strong `+0xA0` writers if found.

---

# Preferred Implementation

Prefer a focused extension to:

```text
AnalyzeClassFieldProvenance.java
```

if the logic fits cleanly.

A separate script such as:

```text
AnalyzeVtableXrefs.java
```

is also acceptable if that keeps responsibilities clearer.

Do not create a general-purpose whole-program class reconstruction engine.

---

# Confirmed Vtable Anchors

The implementation must discover the vtables by symbol/name or class-anchor logic.

Do not hard-code their addresses in normal analysis logic.

The known addresses may be used only as live-test acceptance evidence:

```text
0x148B7CFB0
0x148B7D170
```

The script should record:

- symbol name;
- address;
- table size/slot count discovered;
- valid internal functions;
- external/imported functions;
- duplicate/thunk-resolved functions.

---

# Required Analysis 1 — Xrefs to Vtables

For each confirmed vtable symbol/address:

find all program references to it.

Classify each reference:

```text
direct data reference
LOAD/use
STORE source
constant/address materialization
other
```

For code references, record:

- containing function;
- instruction address;
- p-code op;
- whether the vtable value is written to memory;
- destination expression;
- receiver/base provenance;
- destination offset if recoverable.

Prefer Ghidra reference APIs plus p-code confirmation.

---

# Required Analysis 2 — Structural Vptr Stores

Strong constructor/lifecycle evidence is a structural store like:

```text
STORE [this + offset] <- ResourceViewWidget::vftable
```

or equivalent.

For each such store, recover:

- function;
- store address;
- vtable symbol/address;
- receiver/base parameter identity;
- receiver offset;
- whether offset is zero or nonzero;
- surrounding vptr stores in same function;
- order of stores;
- return behavior;
- callers;
- allocation/new context if visible.

Example evidence:

```text
this + 0x00 <- primary ResourceViewWidget vtable
this + 0xNN <- secondary ResourceViewWidget vtable
```

Do not assume `0xNN` corresponds to a specific base class without more evidence.

---

# Constructor / Destructor / Lifecycle Classification

Classify candidates conservatively:

```text
constructor-like
destructor-like
lifecycle-helper
unknown
```

Use structural evidence such as:

## Constructor-like indicators

- object allocation or factory caller;
- base-class constructors called first;
- final ResourceViewWidget vptr stores;
- member initialization;
- returns receiver or initialized object;
- not dominated by cleanup/destruction patterns.

## Destructor-like indicators

- ResourceViewWidget vptr restored before teardown;
- member destructors/cleanup;
- deallocation/free paths;
- base destructor calls.

Do not classify solely from function order or name.

---

# Required Analysis 3 — Secondary Vtable Offset

For the second confirmed vtable:

```text
CKGalaxyView::ResourceViewWidget::vftable
```

determine whether vptr stores place it at:

```text
this + nonzero_offset
```

If yes, record:

- offset;
- function;
- store order;
- relationship to primary vptr store;
- whether methods from the second table receive adjusted `this`.

This may indicate a secondary base/subobject.

Do not infer exact inheritance beyond the evidence.

---

# Required Analysis 4 — Internal Vtable Export Priority

Fix the previous export-priority issue.

Internal Creation Kit functions must be prioritized above inherited external Qt methods.

Suggested export order:

1. constructor/destructor/lifecycle candidates;
2. internal functions from ResourceViewWidget vtables;
3. `+0xA0` writers;
4. receiver-preserving internal callees;
5. external/imported Qt methods only if directly relevant.

External inherited functions must not consume the function-export quota ahead of internal candidates.

Suggested internal function cap:

```text
20
```

External exports may be omitted entirely unless needed.

---

# Required Analysis 5 — Receiver-Preserving Nonvirtual Method Expansion

Starting from strong anchors:

- constructor/lifecycle candidates;
- internal vtable functions;
- known root `FUN_1431bc320` if it can be structurally connected;
- any exact `ResourceViewWidget::...` symbols;

perform a bounded one- or two-hop call expansion.

A candidate callee may enter the method family with `medium` confidence if:

1. caller is strong class-context function;
2. caller passes the same receiver object as argument 0 to callee;
3. receiver identity is proven structurally;
4. callee is internal Creation Kit code;
5. no conflicting receiver transformation is observed.

This is receiver-family provenance, not proof that the callee is literally a C++ member method.

Record that distinction.

Do not expand recursively without a small bound.

Suggested maximum:

```text
depth 2
```

---

# Receiver Identity

Reuse existing conservative receiver matching where possible:

- exact varnode/high variable;
- COPY/CAST/extension stripping;
- constant PTRSUB/PTRADD/INT_ADD;
- stack-object correlation if applicable.

Do not add general alias analysis.

---

# Required Analysis 6 — Revisit `this + 0xA0`

Search:

- strong class functions;
- medium receiver-preserving helpers;

for structural:

```text
parameter/receiver + 0xA0
```

reads and writes.

Record:

- function;
- class/method-family confidence;
- receiver evidence;
- LOAD/STORE;
- instruction;
- written/read value;
- whether nested `+0x20` is observed.

Prioritize writers.

---

# Required Analysis 7 — Writer Provenance

For any credible `+0xA0` writer:

trace the written value using existing bounded provenance support:

- parameter;
- call return;
- allocator/factory return;
- fixed-field load;
- constant/global;
- bounded arithmetic.

Record the chain.

If the source object is identified, inspect relevant `object + 0x20` operations as before.

---

# Output

Suggested structure:

```text
exports/
└─ class-provenance/
   └─ ResourceViewWidget/
      ├─ manifest.json
      ├─ class-anchors.json
      ├─ vtable-xrefs.json
      ├─ lifecycle-candidates.json
      ├─ class-methods.json
      ├─ receiver-family.json
      ├─ field-A0-accesses.json
      ├─ field-A0-writes.json
      ├─ provenance.json
      └─ functions/
```

Existing files may be preserved/extended.

---

# `vtable-xrefs.json`

Suggested fields:

```json
{
  "vtableName": "CKGalaxyView::ResourceViewWidget::vftable",
  "vtableAddress": "...",
  "references": [
    {
      "functionName": "...",
      "functionAddress": "...",
      "instructionAddress": "...",
      "referenceKind": "vptr-store",
      "receiverOffset": 0,
      "receiverEvidence": [],
      "confidence": "strong"
    }
  ]
}
```

---

# `lifecycle-candidates.json`

For each candidate:

```json
{
  "functionName": "...",
  "functionAddress": "...",
  "classification": "constructor-like",
  "confidence": "strong",
  "vptrStores": [
    {
      "vtableName": "...",
      "receiverOffset": 0,
      "storeAddress": "..."
    }
  ],
  "evidence": [],
  "limitations": []
}
```

---

# `receiver-family.json`

For each nonvirtual helper:

```json
{
  "functionName": "...",
  "functionAddress": "...",
  "confidence": "medium",
  "relationship": "receiver-preserving-callee",
  "sourceFunction": "...",
  "callSite": "...",
  "receiverArgumentIndex": 0,
  "evidence": []
}
```

Do not label these as proven class members.

---

# Root `FUN_1431bc320` Connection

Attempt to determine whether:

```text
FUN_1431bc320
```

can be connected to the ResourceViewWidget class family through:

- receiver-preserving calls;
- exact class-qualified callers;
- signal/slot registration;
- function pointer references;
- class-bound callback setup.

Do not force a connection.

If none is found, preserve it as an independently known root function.

---

# Qt Signal/Slot Evidence

Because `OnApplySeed` may be a nonvirtual Qt callback/slot, look for bounded evidence such as:

- function pointer references to `FUN_1431bc320`;
- Qt connect/setup calls nearby;
- exact `OnApplySeed` strings/symbols;
- callback tables.

This is supporting evidence only.

Do not attempt general Qt meta-object reconstruction in this iteration.

---

# Negative Results

Explicitly report useful negatives, including:

```text
no vtable code xrefs
no structural vptr stores
no constructor-like candidate
no receiver-preserving helper reaches +0xA0
no class-family writer to +0xA0
```

Do not silently fall back to global raw-offset search.

---

# Documentation

Update:

```text
ghidra/README.md
```

with:

- vtable-xref analysis;
- constructor/lifecycle classification;
- secondary vptr offset handling;
- receiver-family expansion;
- internal export prioritization;
- updated live-test process.

---

# Research Documentation

Update:

```text
docs/function-register.md
```

only for live-confirmed relationships after the test.

Potential examples:

```text
ResourceViewWidget vtable xref -> constructor-like FUN_xxx
primary vptr at this+0
secondary vptr at this+0xNN
strong receiver-family helper writes this+0xA0
```

Do not update `known-facts.md` with speculative class-layout semantics.

---

# Safety Requirements

The analysis must remain read-only.

Do not:

- begin Ghidra transactions;
- rename symbols/functions;
- create labels;
- add comments;
- change signatures;
- apply types;
- modify memory;
- alter analysis state intentionally.

Only export files.

---

# Explicit Non-Goals

Do not implement:

- full MSVC RTTI/class reconstruction;
- multiple inheritance semantics beyond observed secondary vptr offsets;
- generalized Qt meta-object reconstruction;
- arbitrary alias analysis;
- symbolic execution;
- deep recursive method-family expansion;
- headless Ghidra orchestration;
- resource algorithm reconstruction itself.

This iteration is specifically:

```text
confirmed ResourceViewWidget vtables
        ↓
xrefs / vptr stores
        ↓
constructor/lifecycle candidates
        ↓
bounded receiver-family expansion
        ↓
revisit this+0xA0
```

---

# Live Acceptance Test

Run against:

```text
class name: ResourceViewWidget
field offset: 0xA0
nested offset: 0x20
```

Expected known vtable anchors should include the live-observed addresses:

```text
0x148B7CFB0
0x148B7D170
```

Minimum success criterion:

- vtable xrefs are exported;
- constructor/lifecycle candidates are reported or a clear negative result is given;
- internal vtable functions are exported ahead of inherited externals;
- receiver-family expansion runs with bounded depth;
- class-family `+0xA0` accesses are reported.

Best case:

- a constructor-like function writes both ResourceViewWidget vtables;
- primary/secondary receiver offsets are established;
- a strong or medium class-family function writes `this+0xA0`;
- written-value provenance identifies the source object;
- the `+0x20` component gains stronger structural identity.

---

# Deliverables

When finished, report:

1. files modified;
2. files added;
3. script/usage changes;
4. confirmed vtables;
5. xref count per vtable;
6. structural vptr-store candidates;
7. lifecycle classifications;
8. primary/secondary receiver offsets;
9. internal vtable functions exported;
10. receiver-family expansion method and depth;
11. whether `FUN_1431bc320` joined the class family;
12. `+0xA0` reads/writes found;
13. written-value provenance results;
14. output schema changes;
15. exact live-test instructions;
16. expected minimum and best-case outcomes;
17. known limitations.

Do not broaden into general class reconstruction until this vtable-xref path has been live-tested.
