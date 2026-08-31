# Codex Brief — Fix Vptr-Store Recognition Through Address Materialization

## Context

The latest live run of:

```text
AnalyzeClassFieldProvenance.java
```

successfully found both confirmed:

```text
CKGalaxyView::ResourceViewWidget::vftable
```

objects and their code xrefs.

The two relevant internal xref functions are:

```text
FUN_1431e7d20
FUN_1431e29f0
```

Inspection of the exported `FUN_1431e7d20` bundle shows clear destructor-like behavior:

```c
*(undefined ***)param_1 =
    CKGalaxyView::ResourceViewWidget::vftable;

*(undefined ***)(param_1 + 0x10) =
    CKGalaxyView::ResourceViewWidget::vftable;

QWidget::~QWidget(param_1);

if ((param_2 & 1) != 0) {
    FUN_14014eca5();
}
```

This establishes directly that:

```text
primary ResourceViewWidget vptr   = this + 0x00
secondary ResourceViewWidget vptr = this + 0x10
```

However, the current analyzer did not classify this function as a structural vptr writer/lifecycle candidate.

The likely cause is that the vtable address is first materialized through one or more p-code temporaries before being used as the value input to the final `STORE`.

The next task is to fix that narrow recognition gap.

---

# Goal

Enhance vptr-store recognition so that a store is accepted when:

```text
STORE [this + offset] <- value
```

and `value` resolves conservatively, through simple p-code value propagation, to one of the known class vtable addresses.

Then rerun lifecycle classification.

Also ensure the two direct internal vtable-xref functions are exported regardless of the normal class-method export quota.

Do not broaden the analysis beyond this.

---

# Required Fix 1 — Trace Vtable Values Into STORE

Current recognition appears to require the vtable constant/symbol to be directly visible enough at the `STORE`.

Add a bounded helper that resolves the `STORE` value input backward through simple non-branching p-code wrappers.

Supported operations should include at least:

```text
COPY
CAST
INT_ZEXT
INT_SEXT
PTRSUB
PTRADD with constant zero/simple constant form
INT_ADD with one constant zero/simple address-preserving form
```

Also support address materialization from a constant program address / symbolic vtable address where Ghidra represents the address via a temporary.

The resolver should stop on:

- `MULTIEQUAL`;
- nonconstant arithmetic;
- LOAD-derived values;
- CALL results;
- ambiguous definitions;
- cycles;
- excessive depth.

Suggested max depth:

```text
8
```

Do not use symbolic execution.

---

# Acceptance Rule

A `STORE` should be classified as a structural vptr store only if:

1. destination resolves structurally to:

```text
parameter 0 + constant offset
```

2. value resolves uniquely to one known class vtable address;
3. pointer size matches the program pointer size;
4. no ambiguous alternate definition is encountered.

Record:

```text
receiverOffset
vtableName
vtableAddress
storeAddress
valueResolutionBasis
valueDefinitionPath
```

Suggested basis:

```text
resolved-vtable-through-pcode
```

---

# Required Fix 2 — Preserve Direct Evidence

For each accepted vptr store, retain the propagation chain.

Example:

```json
{
  "storeAddress": "1431E7D2A",
  "receiverOffset": 0,
  "vtableName": "CKGalaxyView::ResourceViewWidget::vftable",
  "valueResolutionBasis": "resolved-vtable-through-pcode",
  "valueDefinitionPath": [
    "COPY",
    "CAST",
    "CONSTANT_ADDRESS"
  ]
}
```

The exact schema may differ.

Do not replace the existing xref evidence; add the resolved store evidence alongside it.

---

# Required Fix 3 — Lifecycle Reclassification

Once structural vptr stores are recovered, rerun the existing lifecycle classifier.

Expected live behavior for:

```text
FUN_1431e7d20
```

is likely:

```text
destructor-like
```

because it:

- installs both ResourceViewWidget vtables;
- tears down QWidget;
- conditionally deallocates.

Do not hard-code that classification.

For:

```text
FUN_1431e29f0
```

allow existing evidence to determine:

```text
constructor-like
destructor-like
lifecycle-helper
unknown
```

Do not assume it is the constructor merely because it is the other xref function.

---

# Required Fix 4 — Record Secondary Vptr Offset

If both accepted stores occur in the same function and target:

```text
this + 0x00
this + 0x10
```

record that fact explicitly.

Suggested structure:

```json
{
  "primaryVptrOffset": 0,
  "secondaryVptrOffsets": [16]
}
```

or equivalent.

Do not infer exact base-class identity from offset `0x10`.

---

# Required Fix 5 — Force-Export Direct Internal Vtable Xref Functions

The previous export quota omitted:

```text
FUN_1431e29f0
```

even though it is one of only two internal code xrefs to both confirmed vtables.

Change export priority so that:

> every internal function directly referencing a confirmed ResourceViewWidget vtable is exported before applying the ordinary 20-function quota.

At minimum, this should force export of:

```text
FUN_1431e7d20
FUN_1431e29f0
```

if rediscovered live.

Do not hard-code the function addresses.

Discover them from vtable xrefs.

External Qt functions should still not consume the internal quota.

---

# Required Fix 6 — Revisit `+0xA0` Only After Lifecycle Recovery

Do not alter the existing `+0xA0` matching logic in this iteration.

Once lifecycle candidates are admitted into the strong/medium class family, rerun the current field-access analysis.

The important question is whether:

```text
FUN_1431e29f0
```

or a receiver-preserving helper reached from it writes:

```text
this + 0xA0
```

If no writer is found, report the negative result normally.

---

# Root Anchor

Do not attempt to solve the unresolved exact `ResourceViewWidget::OnApplySeed` symbol in this iteration.

`FUN_1431bc320` may remain an independently known root.

This task is only about fixing vptr-store recognition and export priority.

---

# Output

Preserve the existing output set:

```text
class-anchors.json
vtable-xrefs.json
lifecycle-candidates.json
class-methods.json
receiver-family.json
field-A0-accesses.json
field-A0-writes.json
provenance.json
manifest.json
functions/
```

Increment relevant schema versions only if needed.

---

# Documentation

Update:

```text
ghidra/README.md
```

to explain:

- vtable values may be materialized through p-code temporaries;
- the analyzer now resolves simple value-definition chains before classifying a `STORE`;
- direct internal vtable-xref functions are always prioritized for export;
- the live acceptance targets.

Do not update research documentation until after a successful live rerun.

---

# Safety Requirements

The analyzer must remain read-only.

Do not:

- begin transactions;
- rename symbols/functions;
- create labels;
- add comments;
- change signatures;
- apply types;
- modify memory;
- alter analysis state.

Only write export files.

---

# Explicit Non-Goals

Do not add:

- general alias analysis;
- `MULTIEQUAL` resolution;
- symbolic execution;
- general constructor reconstruction;
- new field-offset heuristics;
- deeper receiver-family recursion;
- Qt meta-object analysis;
- headless Ghidra execution.

This is a narrow recognition fix.

---

# Live Acceptance Test

Run:

```text
AnalyzeClassFieldProvenance.java
```

with:

```text
ResourceViewWidget
0xA0
0x20
```

Expected known anchors:

```text
0x148B7CFB0
0x148B7D170
```

Minimum success:

1. `FUN_1431e7d20` is rediscovered through vtable xrefs;
2. its two vptr stores are structurally recognized;
3. offsets `0x0` and `0x10` are recorded;
4. lifecycle classification progresses beyond "no candidate";
5. `FUN_1431e29f0` is exported regardless of normal quota.

Best case:

```text
FUN_1431e7d20 -> destructor-like
FUN_1431e29f0 -> constructor-like
```

and the constructor/class-family path reveals a write or provenance path for:

```text
this + 0xA0
```

Do not require the best-case result for acceptance.

---

# Deliverables

When finished, report:

1. files modified;
2. files added;
3. vtable-value resolution algorithm;
4. supported p-code wrappers;
5. depth/cycle handling;
6. structural STORE acceptance criteria;
7. lifecycle reclassification behavior;
8. primary/secondary vptr offsets found;
9. direct vtable-xref functions force-exported;
10. whether `FUN_1431e29f0` was exported;
11. whether any `+0xA0` writer appeared after lifecycle recovery;
12. schema changes;
13. exact live-test instructions;
14. expected minimum/best-case results;
15. known limitations.
