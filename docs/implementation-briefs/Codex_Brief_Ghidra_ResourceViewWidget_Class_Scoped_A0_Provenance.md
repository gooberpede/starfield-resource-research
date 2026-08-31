# Codex Brief — ResourceViewWidget Class Discovery and Class-Scoped `+0xA0` Provenance

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

The current tooling has established:

```text
ResourceViewWidget::OnApplySeed
    ↓
FUN_1431bc320
```

Inside `FUN_1431bc320`, the following chain is live-confirmed:

```text
ResourceViewWidget + 0xA0
    ↓ LOAD
loaded pointer + 0x20
    ↓
passed into a virtual TESContainer-style copy operation
    ↓
FUN_140e0aab0
```

The virtual call itself has been resolved through:

```text
TESContainer::vftable + 0x50
    ↓
FUN_140e0aab0
```

The field-provenance analyzer then performed a whole-program scan for structural:

```text
parameter 0 + 0xA0
```

matches.

Live result:

- 3,171 scalar-prefilter functions inspected;
- 161 skipped because no decompiler parameter 0 was available;
- 55 structural `parameter 0 + 0xA0` candidates;
- 26 writers;
- no candidate had strong `ResourceViewWidget` class context;
- strongest exported writers were unrelated Qt/editor/Havok/etc. structures.

This means raw structural offset matching is insufficient.

The new bottleneck is:

> Prove which functions actually belong to `ResourceViewWidget`, then search `+0xA0` only within that class/method family.

---

# Research Question

Answer, with machine-readable evidence:

> What functions can be tied to `ResourceViewWidget`, and among those functions, which ones read, write, initialize, clear, or otherwise manipulate `this + 0xA0`?

A secondary question is:

> Can the constructor or another strongly class-bound method identify the type or provenance of the object stored at `+0xA0`?

Do not infer class membership solely from offset use.

---

# Goal

Add a focused class-scoped analysis capability that:

1. identifies `ResourceViewWidget` class anchors available in the Ghidra program;
2. discovers functions strongly associated with that class;
3. distinguishes strong vs weak class-membership evidence;
4. searches only those class-associated functions for `this + 0xA0`;
5. prioritizes writes/initialization/cleanup;
6. exports the strongest candidates and evidence;
7. preserves uncertainty.

The immediate target remains:

```text
ResourceViewWidget
field offset 0xA0
nested offset 0x20
```

---

# Preferred Implementation

Prefer a new focused script if that keeps responsibilities clean, for example:

```text
AnalyzeClassFieldProvenance.java
```

or:

```text
AnalyzeClassMethods.java
```

It is acceptable to reuse helpers from `AnalyzeFieldProvenance.java`.

Do not turn the existing field analyzer into a broad class-reconstruction framework.

---

# Class Anchors to Attempt

Try these evidence sources, in descending order of strength.

## 1. Exact class/vtable symbols

Search for symbols containing:

```text
ResourceViewWidget
```

with particular interest in:

```text
ResourceViewWidget::vftable
ResourceViewWidget::vtable
```

or MSVC RTTI-related class symbols.

Record all exact matches and addresses.

Do not assume a vtable exists if Ghidra has not named one.

---

## 2. Known named method anchor

Use the existing named/known method:

```text
ResourceViewWidget::OnApplySeed
```

as an anchor.

Record:

- symbol name/address;
- containing function;
- callers/callees;
- receiver shape;
- nearby same-class symbols if present;
- namespace/class symbol relationships if available.

---

## 3. Constructor/destructor candidates

If a vtable symbol is found, search for functions that:

```text
STORE ResourceViewWidget::vftable -> this + 0
```

or equivalent.

These are strong constructor/destructor candidates.

For each candidate, record:

- function;
- store address;
- vtable address/name;
- whether the write appears early or late;
- whether multiple class/base vptrs are written;
- whether the function is called from allocation/new patterns;
- whether the function later reads/writes `this + 0xA0`.

Do not identify constructor vs destructor from naming alone.

---

## 4. Vtable slot functions

If a concrete `ResourceViewWidget` vtable is found:

- enumerate pointer-sized entries over a conservative bounded range;
- resolve entries to functions where possible;
- follow thunks;
- record slot index and byte offset;
- export direct class-method candidates.

Suggested initial bound:

```text
up to first null/invalid region
or max 256 slots
```

Use a smaller bound if layout evidence supports it.

Do not walk arbitrary data indefinitely.

---

## 5. Same-class named symbols / RTTI

Use:

- namespaces;
- demangled symbols;
- RTTI;
- Complete Object Locator / Class Hierarchy Descriptor if available;
- nearby type descriptors;

only as supporting evidence.

Do not require full RTTI reconstruction.

---

# Class Membership Confidence

Assign each candidate function a class-membership confidence.

Suggested categories:

```text
strong
medium
weak
```

## Strong evidence examples

- appears directly in `ResourceViewWidget` vtable;
- writes `ResourceViewWidget::vftable` to `this`;
- exact class-qualified symbol;
- function is a thunk to one of the above.

## Medium evidence examples

- direct caller/callee in constructor/init chain with matching receiver;
- same object passed repeatedly into known `ResourceViewWidget` method family;
- exact RTTI/class linkage but not direct vtable membership.

## Weak evidence examples

- raw caller proximity;
- same offset use;
- nearby address;
- generic Qt relationship.

Weak evidence alone must not establish class membership.

---

# Class-Scoped `+0xA0` Analysis

Once a candidate class-method set exists, inspect each strongly or moderately associated function for structural accesses to:

```text
this + 0xA0
```

Use high p-code, not decompiled variable names.

Record:

- read or write;
- instruction/sequence address;
- base parameter identity;
- offset;
- written/read value;
- nested `+0x20` use if present;
- function class-confidence;
- class-membership evidence;
- field-access evidence.

Prioritize writers.

---

# Writer Classification

For each class-scoped `+0xA0` writer, classify conservatively:

```text
initialization
assignment
clear/null
destruction/cleanup
copy
unknown
```

Use actual value/control-flow evidence.

Examples:

```text
this+0xA0 = 0
```

→ likely clear/null, not initialization.

```text
this+0xA0 = return_value_from_allocator_or_factory
```

→ initialization candidate.

```text
this+0xA0 = param_2
```

→ setter/assignment candidate.

Do not infer semantics from function names alone.

---

# Trace the Written Value

For the strongest class-scoped writer candidates, reuse bounded provenance tracing.

Supported cases:

- constant/global address;
- function parameter;
- call return;
- allocator return;
- constructor/factory return;
- copy from another field;
- direct address arithmetic.

Record:

- provenance chain;
- unresolved step;
- function addresses;
- call sites;
- symbols/strings;
- confidence.

Do not implement general alias analysis.

---

# Nested `+0x20` Follow-Up

If a class-scoped `+0xA0` writer identifies a credible source object:

inspect functions operating on that object for:

```text
object + 0x20
```

Look for structural clues that may identify the nested component:

- vptr assignment at `+0x20`;
- method calls with `object+0x20` as receiver;
- destructor calls;
- copy-component calls;
- RTTI casts;
- known TESContainer-related functions;
- repeated size/layout behavior.

Do not force the nested type to be `TESContainer`.

---

# Output

Suggested output:

```text
exports/
└─ class-provenance/
   └─ ResourceViewWidget/
      ├─ manifest.json
      ├─ class-anchors.json
      ├─ class-methods.json
      ├─ field-A0-accesses.json
      ├─ field-A0-writes.json
      ├─ provenance.json
      └─ functions/
         ├─ <function>__<address>/
         │  └─ standard seven-file bundle
         └─ ...
```

If exact class name cannot be sanitized safely for a directory, use a documented encoded/safe name.

---

# `class-anchors.json`

Record all discovered anchor evidence:

```json
{
  "className": "ResourceViewWidget",
  "symbols": [],
  "vtableCandidates": [],
  "rttiCandidates": [],
  "knownMethodAnchors": [],
  "constructorCandidates": []
}
```

Each candidate must include evidence and confidence.

---

# `class-methods.json`

For each candidate method:

```json
{
  "functionName": "...",
  "functionAddress": "...",
  "confidence": "strong",
  "membershipEvidence": [
    "vtable-slot",
    "exact-class-qualified-symbol"
  ],
  "vtableSlotIndex": 12,
  "vtableByteOffset": 96
}
```

Omit slot fields when not applicable.

---

# `field-A0-accesses.json`

Only include functions in the class-scoped candidate set.

Suggested fields:

```json
{
  "functionName": "...",
  "functionAddress": "...",
  "classConfidence": "strong",
  "accessType": "write",
  "instructionAddress": "...",
  "fieldOffset": 160,
  "valueSummary": "...",
  "nestedOffset20Observed": false,
  "evidence": []
}
```

---

# Candidate Export Limit

Export a bounded set of strongest functions.

Suggested order:

1. constructors / vtable writers;
2. `+0xA0` writers;
3. methods containing nested `+0x20` usage;
4. named class methods;
5. selected vtable methods relevant to initialization.

Suggested cap:

```text
20 functions
```

Do not export the entire class vtable blindly if it is very large.

---

# Root Anchor Verification

The script should explicitly verify that the known root anchor:

```text
ResourceViewWidget::OnApplySeed
```

maps to the expected function context.

If the symbol does not resolve exactly, record:

```text
anchor-unresolved
```

rather than silently substituting a similarly named function.

---

# Expected Strong Outcomes

Any of the following count as substantial progress.

## Outcome A — Concrete vtable

```text
ResourceViewWidget::vftable
    ↓
enumerated method set
```

## Outcome B — Constructor

```text
constructor candidate
    ↓
writes ResourceViewWidget::vftable
    ↓
writes this+0xA0
```

## Outcome C — Setter/initializer

```text
strong class-bound method
    ↓
this+0xA0 = <source>
```

## Outcome D — Source object type/provenance

```text
this+0xA0
    ↓
allocated/constructed object
    ↓
object+0x20 structurally identified
```

## Outcome E — Resource-specific upstream edge

A strong class-scoped path reaches:

- BIOM;
- RSGD;
- PNDT;
- RSCS;
- resource leveled lists;
- resource-specific strings or symbols;
- or another clearly resource-related structure.

Do not force this result if evidence does not support it.

---

# Failure / Negative Results

A useful negative result is acceptable.

Examples:

```text
no ResourceViewWidget vtable symbol found
known method anchor exists but no additional class-qualified symbols
no class-scoped writer to +0xA0 found
constructor found but +0xA0 initialized indirectly
```

Record these explicitly.

Do not fall back automatically to the previous global offset scan.

---

# Documentation

Update:

```text
ghidra/README.md
```

with:

- purpose of class-scoped provenance;
- how class anchors are discovered;
- confidence model;
- vtable walking limits;
- `+0xA0` analysis;
- output structure;
- limitations.

---

# Research Documentation

If new directly supported class/function relationships are established, update:

```text
docs/function-register.md
```

Examples:

```text
ResourceViewWidget::vftable slot N -> FUN_xxx
constructor candidate writes ResourceViewWidget::vftable
strong ResourceViewWidget method writes this+0xA0
```

Use cautious language.

Do not update `known-facts.md` with speculative type semantics.

Use `docs/hypotheses.md` only if a new useful but unproven structural theory emerges.

Do not rename Ghidra functions.

---

# Safety Requirements

The script must remain read-only.

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

# Explicit Non-Goals

Do not implement yet:

- full MSVC class reconstruction;
- arbitrary class hierarchy recovery;
- multiple inheritance modeling;
- secondary vtable reconstruction;
- generalized heap alias analysis;
- symbolic execution;
- automatic semantic renaming;
- headless Ghidra orchestration;
- resource algorithm reconstruction itself.

This iteration is only about:

```text
prove ResourceViewWidget class context
        ↓
derive a bounded method family
        ↓
revisit this+0xA0 inside that family
```

---

# Live Acceptance Test

Run the new analyzer from a function associated with:

```text
ResourceViewWidget::OnApplySeed
```

or provide the class name explicitly if the script uses prompts.

Use:

```text
class name: ResourceViewWidget
field offset: 0xA0
nested offset: 0x20
```

Minimum success criterion:

- class anchors are exported;
- at least one strong/medium class-associated function is identified;
- `+0xA0` accesses are searched only within that candidate method set;
- output clearly states if no class-scoped writer is found.

Best case:

- `ResourceViewWidget` vtable or constructor is identified;
- a strong class-scoped function writes `this+0xA0`;
- written-value provenance identifies the source object;
- the `+0x20` component gains independent structural identity.

---

# Deliverables

When finished, report:

1. files added;
2. files modified;
3. script name and usage;
4. class anchors discovered;
5. whether a concrete vtable was found;
6. how class membership is scored;
7. how vtable functions are enumerated;
8. constructor/destructor candidate logic;
9. how `+0xA0` accesses are matched;
10. class-scoped writers found;
11. written-value provenance behavior;
12. nested `+0x20` analysis;
13. export limits;
14. output schema;
15. exact live-test instructions;
16. expected minimum and best-case outcomes;
17. known limitations.

Do not broaden into general class reconstruction until this class-scoped field trace has been live-tested.
