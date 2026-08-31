# Codex Brief — Targeted CALLIND High-P-Code Diagnostics

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

The neighbourhood exporter has now been live-tested through several iterations against:

```text
FUN_1431bc320
0x1431BC320
CreationKit.exe
```

The current virtual-call analyzer successfully detects the relevant indirect call:

```text
callSiteAddress: 0x1431BC350
kind: vtable
vtableByteOffset: 0x50
vtableSlotIndex: 10
```

However, the latest live result failed before constructor provenance could be attempted:

```text
status: unresolved-receiver-provenance
failureReason:
"The receiver could not be normalized conservatively from high p-code."
```

`initializerCandidates` was empty because the analyzer could not recover a trustworthy receiver identity from the actual high-p-code representation of the `CALLIND`.

The decompiler renders the relevant source approximately as:

```c
(**(code **)(local_a8[0] + 0x50))
    (local_a8,
     *(undefined8 *)(param_1 + 0x30),
     *(longlong *)(param_1 + 0xa0) + 0x20);
```

The problem is now very specific:

> We need to see exactly how Ghidra's high p-code represents the `CALLIND` target expression and its arguments before adding another receiver-normalization heuristic.

This iteration is therefore diagnostic, not interpretive.

---

# Goal

Add targeted, machine-readable high-p-code diagnostics for unresolved indirect calls.

The immediate purpose is to inspect the exact p-code expression tree around:

```text
CALLIND at 0x1431BC350
```

in:

```text
FUN_1431bc320
```

so that a later iteration can adapt receiver extraction to the actual Ghidra IR rather than the conceptual decompiled-C form.

Do not add speculative new receiver-resolution rules in this iteration unless they are strictly necessary to emit the diagnostic tree.

---

# Main Requirement

When an indirect call reaches:

```text
unresolved-receiver-provenance
```

export a focused diagnostic description of:

1. the `CALLIND` p-code op itself;
2. the call-target varnode;
3. the defining op chain for the call target;
4. all inputs to each defining op;
5. the `CALLIND` argument varnodes;
6. high-variable identities where available;
7. storage/address/size information for each varnode;
8. constant values and address-space names;
9. sequence numbers / instruction addresses for relevant p-code ops;
10. a bounded recursive expression tree for the call target.

The intent is to answer:

> What exact p-code structure corresponds to the decompiler expression `(local_a8[0] + 0x50)` and where is the receiver represented inside it?

---

# Preferred Output

Add a diagnostic section to `indirect-calls.json`, or a sibling file such as:

```text
pcode-diagnostics.json
```

Either is acceptable.

A separate file may be cleaner if the diagnostics are verbose.

Suggested location:

```text
exports/
└─ neighbourhoods/
   └─ FUN_1431bc320__1431BC320/
      ├─ graph.json
      ├─ manifest.json
      ├─ indirect-calls.json
      ├─ pcode-diagnostics.json
      └─ functions/
```

---

# Suggested Diagnostic Schema

A possible structure:

```json
{
  "rootFunction": {
    "name": "FUN_1431bc320",
    "address": "1431BC320"
  },
  "calls": [
    {
      "callSiteAddress": "1431BC350",
      "opcode": "CALLIND",
      "status": "unresolved-receiver-provenance",

      "callTarget": {
        "varnode": {
          "id": "...",
          "size": 8,
          "space": "unique",
          "offset": "...",
          "isConstant": false,
          "isAddress": false,
          "highVariable": {
            "name": "...",
            "class": "...",
            "identity": "..."
          }
        },

        "definitionTree": {
          "opcode": "LOAD",
          "sequenceAddress": "...",
          "inputs": [
            {
              "role": "space",
              "varnode": { "...": "..." }
            },
            {
              "role": "pointer",
              "definition": {
                "opcode": "INT_ADD",
                "inputs": [
                  {
                    "definition": {
                      "opcode": "LOAD",
                      "inputs": [
                        {
                          "varnode": {
                            "...": "possible receiver-related node"
                          }
                        }
                      ]
                    }
                  },
                  {
                    "varnode": {
                      "isConstant": true,
                      "value": 80
                    }
                  }
                ]
              }
            }
          ]
        }
      },

      "arguments": [
        {
          "index": 0,
          "varnode": { "...": "..." }
        },
        {
          "index": 1,
          "varnode": { "...": "..." }
        }
      ]
    }
  ]
}
```

The exact schema can differ.

The key requirement is that the diagnostic preserve the real IR structure without forcing it into our assumed shape.

---

# Bounded Recursive Definition Tree

Implement a small recursive diagnostic walker for a varnode's defining operation.

For each varnode:

1. record basic metadata;
2. if it has a defining p-code op, record:
   - opcode;
   - sequence number / address;
   - output varnode;
   - all input varnodes;
3. recurse into input definitions;
4. stop at a conservative depth limit.

Suggested maximum depth:

```text
8
```

or another modest value.

Also stop on:

- already visited varnodes/ops;
- null definitions;
- constants;
- inputs without definitions.

Record cycle/visited markers rather than recursing forever.

This is diagnostic tooling, not a full IR serializer.

---

# Varnode Metadata

For each relevant varnode, export where available:

- size;
- address space name;
- offset;
- address string;
- `isConstant`;
- `isAddress`;
- `isRegister`;
- `isUnique`;
- `isPersistent`;
- `isInput`;
- `isUnaffected`;
- high-variable name;
- high-variable class/type;
- stable identity information that helps compare whether two varnodes belong to the same `HighVariable`;
- datatype name if available.

Avoid relying on decompiled local variable names as identity.

Names are useful diagnostics but not proof of equivalence.

---

# P-code Op Metadata

For each relevant p-code op, record:

- mnemonic/opcode name;
- sequence number;
- target/instruction address where available;
- output varnode;
- input count;
- input varnodes;
- parent function.

Use Ghidra's structured high-p-code objects.

Do not parse decompiled C text with regex to reconstruct the tree.

---

# CALLIND Arguments

The existing problem is receiver provenance.

Therefore explicitly export all inputs to the `CALLIND` op, preserving their indexes.

Be careful about Ghidra's `CALLIND` convention:

- input 0 is normally the indirect target;
- subsequent inputs are call arguments.

Document the convention actually observed through the API.

For the target call, we especially want to compare:

```text
CALLIND argument 0 after target
```

conceptually the C++ `this` receiver,

against varnodes nested inside the call-target definition tree.

If they share a `HighVariable` or a recoverable defining chain, the later resolver can exploit that.

This iteration should report the relationship, not yet guess at normalization rules.

---

# Comparison Diagnostics

For the call at `0x1431BC350`, add a small comparison section if practical.

Compare the first actual call argument (`this`) against every nonconstant varnode encountered in the call-target definition tree.

Record simple evidence such as:

```text
sameHighVariable: true/false
sameVarnode: true/false
sameStorage: true/false
sameDefiningOp: true/false
```

Do not treat storage equality alone as proof.

This diagnostic may make the receiver relationship immediately obvious.

---

# Focused Scope

The script does not need to emit these diagnostics for every p-code op in every function.

Prefer:

- unresolved indirect calls only;
- especially `unresolved-receiver-provenance`;
- the selected root function only for now.

It is acceptable to make diagnostic export conditional on unresolved status.

Avoid producing huge files.

---

# Human-Readable Companion

In addition to JSON, it is acceptable to produce a compact text file such as:

```text
pcode-diagnostics.txt
```

showing an indented tree:

```text
CALLIND @ 1431BC350
  target:
    LOAD
      input[0]: const(space)
      input[1]:
        INT_ADD
          input[0]:
            LOAD
              ...
          input[1]: const 0x50

  args:
    arg0: ...
    arg1: ...
    arg2: ...
```

This is optional.

The structured JSON is the required output.

---

# Do Not Change Resolution Behaviour Yet

This is important.

Do not broaden receiver normalization in this task merely because the p-code walker exposes a new possible path.

The purpose of this live iteration is to obtain the evidence first.

The existing resolver should continue to produce:

```text
unresolved-receiver-provenance
```

if its current conservative rules still fail.

A later Codex task can implement the exact missing normalization rule after we inspect the diagnostic output.

---

# Existing Behaviour to Preserve

Do not regress:

- direct callee export;
- thunk resolution;
- depth-1 neighbourhood export;
- virtual-call detection;
- fixed vtable offset detection;
- vtable slot calculation;
- constructor-vptr provenance logic;
- graph output;
- bundle deduplication;
- non-destructive behaviour.

The diagnostic code should be additive.

---

# Safety Requirements

The script must remain read-only with respect to the Ghidra program.

Do not:

- begin transactions;
- rename functions;
- modify symbols;
- create labels;
- add comments;
- change signatures;
- apply types;
- modify memory;
- intentionally alter analysis state.

Only export files.

---

# Documentation

Update:

```text
ghidra/README.md
```

to explain:

- why p-code diagnostics exist;
- when they are emitted;
- where they are written;
- that they are intended to diagnose unresolved indirect-call provenance;
- that they are not a general p-code dump;
- the recursion/depth limit;
- how to inspect the target call at `0x1431BC350`.

---

# Live Acceptance Test

Run against:

```text
FUN_1431bc320
0x1431BC320
```

The relevant call should remain identifiable as:

```text
CALLIND @ 0x1431BC350
```

If receiver resolution still fails, the new diagnostic output must provide enough detail to reconstruct the actual high-p-code shape of:

- the call target;
- the fixed `0x50` addition;
- the inner pointer/vtable load;
- the first call argument / likely `this`;
- their high-variable relationships.

A successful diagnostic run does not require resolving the virtual target.

Success means:

> We can now see exactly why the receiver normalizer failed.

---

# Deliverables

When finished, report:

1. files modified;
2. files added, if any;
3. diagnostic output schema;
4. recursion/depth limit;
5. how cycles are prevented;
6. which varnode metadata is recorded;
7. which p-code op metadata is recorded;
8. how `CALLIND` arguments are represented;
9. whether comparison diagnostics were added;
10. exact live-test instructions;
11. expected output files;
12. any Ghidra API assumptions that still require live validation;
13. known limitations.

Do not implement new receiver-resolution heuristics until the diagnostic output has been live-tested and reviewed.
