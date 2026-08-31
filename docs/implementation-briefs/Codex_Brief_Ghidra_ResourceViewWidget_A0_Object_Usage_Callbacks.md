# Codex Brief — Identify the `ResourceViewWidget + 0xA0` Object and Trace Constructor-Wired Callbacks

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

The latest live analysis has now established a concrete `CKGalaxyView::ResourceViewWidget` lifecycle.

Live-confirmed structural results include:

```text
FUN_1431e29f0
    ≈ constructor-like ResourceViewWidget lifecycle function
```

It installs:

```text
primary ResourceViewWidget vptr   at this + 0x00
secondary ResourceViewWidget vptr at this + 0x10
```

and performs QWidget construction / member initialization / signal-slot wiring.

A separate live-confirmed lifecycle function:

```text
FUN_1431e7d20
```

restores both ResourceViewWidget vptrs, tears down QWidget state, and conditionally deallocates; this is strongly destructor-like.

The previously important root function remains:

```text
FUN_1431bc320
```

which reads:

```text
this + 0xA0
```

then uses:

```text
loaded_pointer + 0x20
```

as the source component passed into the virtual call resolved as:

```text
TESContainer::vftable + 0x50
    ↓
FUN_140e0aab0
```

The class-scoped analyzer still found no class-family writer to:

```text
this + 0xA0
```

However, it did find class-family reads in:

```text
FUN_1431ef760
```

and its thunk.

Ghidra currently types the value loaded from `this + 0xA0` as:

```text
QTreeWidget *
```

This type is suggestive but NOT yet authoritative.

The constructor also wires several nonvirtual/internal callbacks, including functions around:

```text
thunk_FUN_1431f10b0
thunk_FUN_1431f0fe0
```

and another text-change callback path.

These callbacks are valuable class-specific anchors even though they are not virtual methods.

The next task is to determine:

1. what the object at `this + 0xA0` actually appears to be structurally;
2. what `FUN_1431ef760` does with it;
3. whether the constructor-wired callback family populates, clears, mutates, or reads that object;
4. whether that path reaches the resource-specific data we care about.

---

# Research Questions

Answer, with machine-readable evidence:

> What operations does `FUN_1431ef760` perform on the object loaded from `ResourceViewWidget + 0xA0`?

and:

> Which constructor-wired callbacks or receiver-preserving helpers operate on that same object, and do any of them populate or transform the data later consumed by `FUN_1431bc320`?

A secondary question is:

> Is the `QTreeWidget *` type propagated by Ghidra independently supported by RTTI/vtable/call behavior, or is it merely a weak decompiler type guess?

---

# Goal

Extend focused analysis so that it can:

1. export and inspect `FUN_1431ef760` and its thunk;
2. identify all operations on the value loaded from `this + 0xA0`;
3. classify method calls made on that loaded object;
4. inspect constructor-wired callback targets and their receiver-preserving helper families;
5. detect accesses to `this + 0xA0` and to the loaded object's fields;
6. distinguish pointer assignment from object mutation/population;
7. gather structural evidence for the loaded object's type;
8. expose any path toward resource-specific data structures/functions.

This is object-usage and callback-family analysis, not general class reconstruction.

---

# Preferred Implementation

Prefer extending:

```text
AnalyzeClassFieldProvenance.java
```

if that remains manageable.

A separate focused script such as:

```text
AnalyzeMemberObjectUsage.java
```

is acceptable if cleaner.

Do not duplicate existing helper logic unnecessarily.

---

# Required Analysis 1 — Export `FUN_1431ef760`

Force-export:

```text
FUN_1431ef760
```

and its thunk-resolved implementation if rediscovered structurally through the current class-family analysis.

Do not hard-code the function address in normal logic.

The live-known address/name may be used only for acceptance checking.

Export the standard seven-file bundle.

---

# Required Analysis 2 — Trace the `this + 0xA0` Load in `FUN_1431ef760`

Identify every structural:

```text
LOAD [receiver + 0xA0]
```

in the function.

For each load:

- instruction/sequence address;
- load result varnode;
- HighVariable;
- datatype;
- downstream uses;
- whether the value is null-checked;
- whether arithmetic is applied;
- whether it is passed as `this` / argument 0 to calls;
- whether fields are loaded/stored through it.

Create a bounded use tree.

Suggested max depth:

```text
8
```

Stop on cycles and unrelated merged control flow.

---

# Required Analysis 3 — Classify Calls on the Loaded Object

For each direct or indirect call where the loaded `+0xA0` object is used as the receiver / first argument:

record:

- call site;
- callee function/symbol;
- thunk-resolved callee;
- whether call is direct/indirect;
- receiver adjustment;
- vtable slot if indirect and statically recoverable;
- strings/symbols near the callee;
- whether callee is Qt/external or internal Creation Kit code.

Examples of useful classifications:

```text
QTreeWidget method
QAbstractItemView method
QObject method
internal wrapper/helper
unknown
```

Do not assign semantic method names without evidence.

---

# Required Analysis 4 — Independent Type Evidence

Evaluate whether the loaded `+0xA0` object is genuinely consistent with:

```text
QTreeWidget *
```

Possible strong evidence:

- indirect call resolves through a `QTreeWidget`/Qt vtable;
- direct Qt method signature expects `QTreeWidget *` or compatible base;
- object is constructed by a known `QTreeWidget` constructor;
- RTTI/type descriptor;
- destructor call;
- strongly typed imported Qt API.

Possible weak evidence:

- only decompiler datatype;
- variable name;
- inherited generic QWidget call.

Record:

```text
typeCandidate
confidence
evidence
```

Do not force the type.

---

# Required Analysis 5 — Constructor-Wired Callback Extraction

From the live-confirmed constructor-like function:

```text
FUN_1431e29f0
```

identify signal/slot or callback registration sites.

For each registration:

- constructor call site;
- signal/source object if recoverable;
- callback target;
- thunk-resolved callback target;
- bound receiver/context object;
- nearby strings/signatures;
- connection API if identifiable.

At minimum, rediscover the live-observed callback family around:

```text
thunk_FUN_1431f10b0
thunk_FUN_1431f0fe0
```

and the text-change callback path if present.

Do not hard-code these function addresses.

---

# Required Analysis 6 — Callback Family Expansion

For each constructor-wired internal callback:

perform bounded receiver-preserving expansion, similar to the existing method-family logic.

Suggested bound:

```text
depth 2
```

Only admit an internal callee when:

1. the caller is a confirmed constructor-wired callback or accepted callback-family function;
2. the same ResourceViewWidget receiver/context is structurally passed onward;
3. receiver identity is conservatively proven.

Record:

```text
callback-family.json
```

with source callback, call site, receiver evidence, depth, and confidence.

---

# Required Analysis 7 — Search Callback Family for `this + 0xA0`

Within confirmed/medium callback-family functions, structurally search for:

```text
receiver + 0xA0
```

reads/writes.

Differentiate:

```text
pointer assignment
pointer clear/null
loaded-object method call
loaded-object field write
loaded-object field read
unknown mutation
```

This distinction is central.

The current investigation may have been asking:

> who writes the pointer at `this+0xA0`?

when the more relevant operation may instead be:

> who mutates the object already referenced by `this+0xA0`?

---

# Required Analysis 8 — Loaded-Object Mutation

If a function loads:

```text
obj = [this + 0xA0]
```

then writes through:

```text
[obj + constant_offset]
```

or passes `obj` into internal mutator functions, record these as object-mutation candidates.

For each:

- parent ResourceViewWidget function;
- load site;
- object field offset;
- STORE/call site;
- written value/provenance;
- callee;
- nested object relationships;
- strings/symbols.

Do not assume object field offsets correspond to Qt private layout.

---

# Required Analysis 9 — Revisit `+0x20`

The existing root uses:

```text
obj = [this + 0xA0]
obj + 0x20
```

as a source component.

Search callback-family and `FUN_1431ef760` logic for structural operations involving:

```text
obj + 0x20
```

Record:

- reads/writes;
- method calls using `obj+0x20` as receiver;
- vptr evidence;
- destructors;
- copy/component operations;
- TESContainer-related functions;
- array/list behavior.

This may help determine whether:

```text
obj + 0x20
```

is an embedded component/subobject rather than arbitrary offset arithmetic.

---

# Required Analysis 10 — Resource-Specific Signals

For all internal functions reached from:

- `FUN_1431ef760`;
- constructor-wired callback family;
- loaded-object mutation calls;

collect evidence of resource relevance.

Search for:

- `BIOM`;
- `RSGD`;
- `PNDT`;
- `RSCS`;
- `TESLevItem`;
- `TESContainer`;
- resource strings;
- resource-related RTTI/types;
- known resource-function addresses already in `function-register.md`;
- calls to `FUN_140e457b0`;
- calls to `FUN_140e0aab0`.

Do not declare a resource-specific path based on a single generic `TESContainer` hit.

---

# Output

Suggested additions:

```text
exports/
└─ class-provenance/
   └─ ResourceViewWidget/
      ├─ member-A0-object-usage.json
      ├─ callback-bindings.json
      ├─ callback-family.json
      ├─ callback-A0-accesses.json
      ├─ object-mutations.json
      ├─ object-plus20-usage.json
      ├─ type-evidence.json
      └─ functions/
```

Preserve existing output files.

---

# `member-A0-object-usage.json`

Suggested structure:

```json
{
  "functionName": "FUN_1431ef760",
  "fieldOffset": 160,
  "loads": [
    {
      "instructionAddress": "...",
      "datatype": "QTreeWidget *",
      "nullChecked": true,
      "uses": [
        {
          "kind": "call-receiver",
          "callSite": "...",
          "callee": "..."
        }
      ]
    }
  ]
}
```

---

# `callback-bindings.json`

For each constructor connection:

```json
{
  "constructorFunction": "FUN_1431e29f0",
  "callSite": "...",
  "sourceObject": "...",
  "callbackFunction": "...",
  "resolvedCallbackFunction": "...",
  "receiverContext": "...",
  "evidence": []
}
```

---

# `callback-family.json`

For each expanded callback helper:

```json
{
  "functionName": "...",
  "functionAddress": "...",
  "sourceCallback": "...",
  "depth": 1,
  "relationship": "receiver-preserving-callee",
  "confidence": "medium",
  "evidence": []
}
```

---

# `object-mutations.json`

For each mutation:

```json
{
  "resourceViewWidgetFunction": "...",
  "objectLoadSite": "...",
  "objectFieldOffset": 32,
  "mutationKind": "store | call | clear | unknown",
  "site": "...",
  "callee": "...",
  "valueProvenance": {},
  "evidence": []
}
```

---

# Export Priority

Prioritize internal functions in this order:

1. `FUN_1431ef760` resolved implementation;
2. constructor-wired callback targets;
3. callback-family functions touching `+0xA0`;
4. loaded-object mutator callees;
5. functions touching `obj + 0x20`;
6. other internal callback helpers.

Suggested cap:

```text
30 internal functions
```

External Qt functions need not receive full bundles unless directly necessary to interpret a call.

---

# Documentation

Update:

```text
ghidra/README.md
```

with:

- member-object usage analysis;
- callback extraction;
- callback-family expansion;
- distinction between pointer assignment and object mutation;
- type-evidence scoring;
- `obj+0x20` tracing;
- live-test workflow.

---

# Research Documentation

Do not update `known-facts.md` based only on a Ghidra datatype such as `QTreeWidget *`.

Update:

```text
docs/function-register.md
```

only for new live-confirmed structural relationships.

Possible examples after live validation:

```text
constructor callback -> FUN_xxx
FUN_xxx loads ResourceViewWidget+0xA0
loaded object used as receiver of function Y
obj+0x20 passed to TESContainer copy path
```

Use cautious interpretation language.

---

# Safety Requirements

The tooling must remain read-only.

Do not:

- begin transactions;
- rename functions/symbols;
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

- general Qt meta-object reconstruction;
- full signal/slot graph recovery;
- full Qt private-layout reconstruction;
- arbitrary heap alias analysis;
- symbolic execution;
- deep recursive callback expansion;
- automatic semantic renaming;
- headless Ghidra orchestration;
- resource algorithm reconstruction itself.

This iteration is specifically:

```text
constructor-wired callbacks
        +
FUN_1431ef760
        ↓
what is at this+0xA0?
        ↓
who mutates it?
        ↓
what is obj+0x20?
```

---

# Live Acceptance Test

Run against:

```text
ResourceViewWidget
0xA0
0x20
```

Minimum success:

1. `FUN_1431ef760` is exported and its `+0xA0` use tree is recorded;
2. constructor-wired internal callbacks are enumerated;
3. callback-family expansion completes to bounded depth;
4. `+0xA0` accesses in callback-family functions are reported;
5. type evidence for the loaded object is separated into strong/weak;
6. `obj+0x20` usage is recorded if observed.

Best case:

- `+0xA0` is independently identified as a concrete Qt/internal object type;
- one constructor-wired callback populates or mutates it;
- `obj+0x20` is structurally identified;
- the callback/object-mutation path reaches resource-specific container/list generation.

---

# Deliverables

When finished, report:

1. files modified;
2. files added;
3. script/usage changes;
4. `FUN_1431ef760` object-usage results;
5. constructor callback bindings found;
6. callback-family functions discovered;
7. `+0xA0` reads/writes/mutations found;
8. type evidence for the loaded object;
9. `obj+0x20` evidence;
10. resource-specific functions/data reached;
11. export limits;
12. schema changes;
13. exact live-test instructions;
14. expected minimum/best-case outcomes;
15. known limitations.
