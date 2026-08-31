# Codex Brief — ResourceViewWidget `+0xA0` Field Provenance and Source-Container Trace

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

The current Ghidra tooling has now successfully resolved the previously indirect virtual call in:

```text
FUN_1431bc320
0x1431BC320
CreationKit.exe
```

The resolved call path is:

```text
FUN_1431bc320
    ↓
receiver resolved from stack object
    ↓
initializer / constructor provenance
    ↓
final vptr = TESContainer::vftable
    ↓
slot +0x50 / index 10
    ↓
FUN_140e0aab0
```

Inspection of `FUN_140e0aab0` strongly suggests that it is generic `TESContainer` copy/clone-style machinery rather than the resource-generation algorithm itself.

The broader flow now appears approximately:

```text
create temporary TESContainer
        ↓
copy/populate it from another component
        ↓
read a QSpinBox value
        ↓
FUN_140e457b0
        ↓
resolve/flatten TESLevItem entries
```

The important source argument passed into the copy operation originates from:

```c
*(longlong *)(param_1 + 0xa0) + 0x20
```

where `param_1` is the `ResourceViewWidget` / current UI object.

This means the next promising lead is:

```text
ResourceViewWidget + 0xA0
        ↓
object
        ↓
object + 0x20
        ↓
source component / TESContainer-like data
```

The goal of this task is to trace that field and determine where it comes from and how it is populated.

---

# Research Question

Answer, with machine-readable evidence:

> What is stored at `ResourceViewWidget + 0xA0`, what is the component/data at `+0x20` inside that object, and where is that data populated before `FUN_1431bc320` copies and resolves it?

Do not assume the answer is resource-specific until the evidence supports it.

---

# Goal

Add a focused field-provenance analysis capability for a selected function/member offset.

Immediate target:

```text
root function: FUN_1431bc320
base object: param_1 / ResourceViewWidget
field offset: 0xA0
nested offset: 0x20
```

The analysis should:

1. identify the p-code expression corresponding to `param_1 + 0xA0`;
2. identify how the pointer loaded from that field is used;
3. identify the nested component at `loaded_pointer + 0x20`;
4. find other reads and writes involving the `+0xA0` member on the same object type/context;
5. identify candidate functions that assign or initialize the field;
6. export relevant candidate functions for inspection;
7. preserve uncertainty and evidence.

This is provenance analysis, not semantic renaming.

---

# Preferred Implementation

Add a focused script or extend existing tooling cleanly.

Suitable names include:

```text
AnalyzeFieldProvenance.java
```

or:

```text
ExportFieldProvenance.java
```

Do not overload `ExportFunctionNeighbourhood.java` with unrelated complexity if a separate script is cleaner.

Reuse existing helpers where practical.

---

# Target Selection

The script may:

- operate on the function containing the cursor;
- prompt for or use a configurable field offset;
- or be temporarily focused on the known `0xA0` case if clearly documented.

Prefer generic-but-small support for:

```text
base parameter index
field byte offset
optional nested byte offset
```

For the first test:

```text
base parameter index: 0 / this
field offset: 0xA0
nested offset: 0x20
```

Do not hard-code semantic names such as "resource container".

---

# Required Analysis 1 — Identify the `+0xA0` Access in the Root

In `FUN_1431bc320`, identify the p-code/dataflow corresponding to:

```text
param_1 + 0xA0
```

Record:

- instruction / sequence address;
- p-code op;
- base varnode;
- constant offset;
- load result varnode;
- datatype if known;
- high-variable identity if available;
- downstream uses.

Then identify the nested:

```text
loaded_pointer + 0x20
```

used as the source argument to the resolved virtual/copy function.

Record the complete chain.

---

# Required Analysis 2 — Find Same-Field Reads/Writes

Search the analysed program for candidate accesses equivalent to:

```text
this/base + 0xA0
```

with particular interest in:

- `STORE` / assignment to the field;
- constructor/initializer writes;
- destructor/cleanup writes;
- getter-like reads;
- functions that pass the loaded object onward.

Because raw offset `0xA0` may appear in unrelated structures, do not treat every matching constant as relevant.

Use contextual evidence where possible:

- same known class/vtable context;
- same caller family;
- methods associated with `ResourceViewWidget`;
- same `this`/receiver type if Ghidra exposes it;
- references from known ResourceViewWidget methods;
- shared vtable or class namespace symbols.

If class identity cannot be proven, rank candidates instead of declaring matches.

---

# Required Analysis 3 — Candidate Assignment Sites

For likely relevant writes to `ResourceViewWidget + 0xA0`, record:

- function name/address;
- instruction address;
- written value expression;
- source of written pointer/value;
- whether the write is nulling/cleanup or real initialization;
- callers/callees;
- nearby strings/symbols;
- confidence/relevance basis.

Prefer actual write sites over pure readers.

The immediate goal is to find where the object later read by `FUN_1431bc320` is installed.

---

# Required Analysis 4 — Trace the Written Value

For each credible assignment candidate, attempt a bounded backward provenance trace of the written value.

Supported simple cases:

- function return value;
- address of known global/object;
- argument passed into setter/initializer;
- result of `new`/allocator followed by constructor;
- copy from another object field;
- direct constant/data address.

Do not implement general symbolic execution or heap alias analysis.

Record unresolved cases clearly.

---

# Required Analysis 5 — Inspect `+0x20` Inside the Source Object

Once a likely object type or initializer for the `+0xA0` field is found, search for accesses to:

```text
source_object + 0x20
```

within functions operating on that object.

The purpose is to understand whether `+0x20` is:

- an embedded `TESContainer`;
- a `BaseFormComponent`-derived subobject;
- a pointer;
- a list/array;
- or another structure.

Use evidence such as:

- vtable assignment at offset `+0x20`;
- calls taking `object + 0x20` as `this`;
- RTTI casts;
- destructor calls on `+0x20`;
- known `TESContainer` methods;
- copy-component calls;
- size/layout patterns.

Do not assign a type solely because it is passed to `FUN_140e0aab0`.

---

# Output

Suggested structure:

```text
exports/
└─ field-provenance/
   └─ FUN_1431bc320__field_A0/
      ├─ manifest.json
      ├─ root-access.json
      ├─ candidate-accesses.json
      ├─ candidate-writes.json
      ├─ provenance.json
      └─ functions/
         ├─ <candidate-function>__<address>/
         │  └─ standard seven-file bundle
         └─ ...
```

If a different structure fits the existing tooling better, document it.

---

# `root-access.json`

Record the exact root-function chain.

Suggested schema:

```json
{
  "rootFunction": {
    "name": "FUN_1431bc320",
    "address": "1431BC320"
  },
  "baseParameterIndex": 0,
  "fieldOffset": 160,
  "nestedOffset": 32,
  "access": {
    "fieldLoadInstruction": "...",
    "fieldLoadExpression": "param_1 + 0xA0",
    "loadedValue": { "...": "..." },
    "nestedExpression": "loaded + 0x20",
    "use": {
      "callSite": "...",
      "callee": "FUN_140e0aab0",
      "argumentIndex": 2
    }
  }
}
```

Do not depend on decompiled variable names for identity.

---

# `candidate-accesses.json`

For every candidate same-field access, include:

- function;
- instruction;
- read/write;
- offset;
- receiver evidence;
- relevance score or confidence;
- why it was considered related;
- whether the function is already in known ResourceViewWidget context.

A simple confidence scale is acceptable:

```text
high
medium
low
```

but include evidence, not just a score.

---

# `candidate-writes.json`

Prioritize writes to `+0xA0`.

For each:

```json
{
  "functionName": "FUN_...",
  "functionAddress": "...",
  "instructionAddress": "...",
  "fieldOffset": 160,
  "writeKind": "initialization | assignment | clear | unknown",
  "writtenValue": {
    "...": "..."
  },
  "provenanceStatus": "...",
  "evidence": [
    "..."
  ]
}
```

---

# Function Export

Export the normal seven-file context bundle for a bounded number of the strongest candidate writer/initializer functions.

Suggested limit:

```text
top 10
```

or fewer if confidence is high.

Do not export hundreds of unrelated `+0xA0` users.

Deduplicate by function entry address.

---

# Candidate Ranking

Prefer candidates in this order:

1. direct methods/callers related to `ResourceViewWidget`;
2. functions sharing strong class/vtable context;
3. direct writers to `+0xA0`;
4. functions reached from known ResourceViewWidget initialization paths;
5. generic raw-offset matches.

If no strong class context exists, say so.

Do not hide low confidence.

---

# Xref / Symbol Support

Use Ghidra structured program data where possible:

- references;
- symbols;
- functions;
- p-code;
- decompiler high variables;
- vtables;
- RTTI;
- call graph.

Avoid raw text grep of decompiled C unless used only as a supplemental diagnostic.

---

# Important Research Direction

The current working interpretation is:

```text
FUN_140e0aab0
    ≈ TESContainer copy/component machinery

FUN_140e457b0
    ≈ generic leveled-list flatten/resolve machinery
```

Therefore the source component supplied from:

```text
(ResourceViewWidget + 0xA0) + 0x20
```

is now more interesting than either generic function.

However, do not encode those semantic interpretations as hard truth in the script.

The task is to discover where the source data comes from.

---

# What Would Count as a Strong Result?

Any of the following would be valuable:

### Result A — Concrete setter/initializer

```text
ResourceViewWidget method
    ↓
writes pointer to this+0xA0
    ↓
allocated/constructed object
```

### Result B — Concrete object type

Evidence establishes the type/vtable of the object stored at `+0xA0`.

### Result C — Embedded component identity

Evidence establishes what lives at `source_object + 0x20`.

### Result D — Resource-specific upstream data

The initialization path reaches:

- BIOM;
- RSGD;
- PNDT;
- RSCS;
- resource leveled lists;
- resource-specific strings/types;
- or another clearly resource-specific structure.

Do not force the analysis to find these if they are not present.

---

# Updating Research Documentation

Do not modify `known-facts.md` based only on tentative type inference.

If concrete new call/field relationships are established, update:

```text
docs/function-register.md
```

with directly supported evidence.

If a new structural theory emerges but remains unproven, update:

```text
docs/hypotheses.md
```

only if useful.

Do not rename Ghidra functions.

---

# Safety Requirements

All analysis must remain read-only.

Do not:

- start Ghidra transactions;
- rename symbols/functions;
- create labels;
- add comments;
- change signatures/types;
- modify memory;
- intentionally alter analysis state.

Only export files.

---

# Documentation

Update:

```text
ghidra/README.md
```

with:

- purpose of field-provenance analysis;
- how to run it;
- supported offset-based tracing;
- candidate-ranking approach;
- output structure;
- known limitations.

---

# Explicit Non-Goals

Do not implement yet:

- whole-program arbitrary struct recovery;
- full class reconstruction;
- generalized alias analysis;
- heap graph recovery;
- symbolic execution;
- automatic function renaming;
- deep recursive call tracing;
- headless Ghidra orchestration;
- resource algorithm reconstruction itself.

This iteration is focused on tracing one field and its nested component.

---

# Live Acceptance Test

Run the new analysis against:

```text
FUN_1431bc320
0x1431BC320
```

using:

```text
base parameter: 0
field offset: 0xA0
nested offset: 0x20
```

Minimum successful result:

- exact root access is identified;
- candidate same-field accesses are exported;
- at least one likely writer/initializer is ranked or the output clearly explains why none can be tied confidently.

Best-case result:

- the object stored at `+0xA0` is identified;
- the `+0x20` component is structurally identified;
- one or more upstream resource-specific functions/data structures are exposed.

---

# Deliverables

When finished, report:

1. files added;
2. files modified;
3. script name and usage;
4. how the root field access is identified;
5. how same-field accesses are searched;
6. how class/context relevance is determined;
7. how writes are distinguished from reads;
8. how value provenance is traced;
9. how nested offset `+0x20` is analyzed;
10. candidate ranking method;
11. export limits;
12. output schema;
13. exact live-test instructions;
14. expected minimum and best-case outcomes;
15. known limitations.

Do not expand into general class/heap analysis until this field trace has been live-tested.
