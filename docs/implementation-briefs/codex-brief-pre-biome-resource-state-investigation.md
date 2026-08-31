# Codex Implementation Brief — Identify Pre-Biome Resource-State Population

Repository:

```text
gooberpede/starfield-resource-research
```

## Objective

Perform a narrowly scoped Ghidra investigation around the proven per-biome generator:

```text
FUN_1415DCFB0
```

The central research question is:

> **What function encloses the per-biome calls to `FUN_1415DCFB0`, and what happens to the shared planet-wide resource state before the first of those calls?**

The immediate motivation is the atmospheric-resource question, especially Maal VIII's atmospheric Chlorine, but do **not** assume in advance that the pre-biome population path is atmospheric.

The goal is to recover the actual enclosing control flow and identify all relevant pre-biome population of the resource container/state that later participates in the proven `count >= 8` checks.

This is a **static Ghidra investigation only**.

Do not perform live x64dbg work.
Do not modify the standalone reproducer.
Do not begin a broad reverse-engineering sweep.
Do not revisit the old `ResourceViewWidget::OnApplySeed -> FUN_1431bc320 -> FUN_140e457b0` trail unless new evidence from the current path directly requires it.

---

# 1. Evidence discipline

Follow the repository's current evidence labels:

- **PROVEN**
- **STRONG**
- **PROVISIONAL**
- **COUNTERFACTUAL**
- **SUPERSEDED**

Preserve the current rule:

> When static Ghidra interpretation conflicts with later live x64dbg evidence, the live observation governs the current model.

Do not semantically rename `FUN_...` functions unless there is strong evidence and the original generated name remains preserved in the register.

Do not convert an interpretation into a fact merely because it fits the atmospheric hypothesis.

---

# 2. Known starting point

Treat the following as established context from the repository.

## 2.1 Proven per-biome generator

```text
FUN_1415DCFB0
Address: 0x1415DCFB0
Context: Creation Kit / live Galaxy View Apply generation path
```

It is the proven primary per-biome generator in the live-traced CK path.

It handles at least:

- Common/root generation;
- Special generation;
- family-cache reuse;
- descendant-generation dispatch;
- capacity / count checks.

## 2.2 Proven descendant helper

```text
FUN_14157F120
Address: 0x14157F120
```

It is the proven descendant helper in the same live-traced path.

## 2.3 Proven capacity behavior

Relevant observed checks include:

```text
0x1415DD0A3  cmp dword ptr [r12], 8
0x1415DD0A8  jae ...

0x1415DD0D3  cmp dword ptr [rsi], 5
0x1415DD0D6  jae ...

0x1415DD0DC  cmp dword ptr [r12], 8
0x1415DD0E1  jae ...
```

and in the descendant helper:

```text
0x14157F14D  mov rax,[rcx+20h]
0x14157F151  cmp dword ptr [rax],8
0x14157F154  jae 14157F371
```

The `>= 8` resource-count guard is proven.

The `count >= 5` guard is proven as a comparison on the structure associated with generated/cached Common-family configurations; the exact broad semantics of that structure remain provisional.

---

# 3. Why Maal VIII matters

Maal VIII is the preferred diagnostic case.

Static/CK evidence:

```text
ATMO_MaalVIII
    -> atmospheric Chlorine
    -> IRES FormID 000057D5
```

The CK Resource Generation view shows seven surface/biome resources:

```text
Iron
Nickel
Water
Uranium
Iridium
Vanadium
Copper
```

The in-game survey reports eight resources and additionally includes:

```text
Chlorine
```

The old `planet-all-resources.csv` / SurveyAggregator-derived data omits that atmospheric Chlorine.

A later live trace showed that during the final Iron-family generation, the shared internal resource count reaches `8`, after which the descendant helper returns immediately and Alkanes is not emitted.

Current **STRONG** interpretation:

```text
atmospheric Chlorine
        ↓
pre-populates / enters planet-wide resource state
        ↓
occupies one of the same 8 internal slots
        ↓
changes later biome-generation outcome
```

The exact insertion function and exact ordering are still **OPEN**.

This investigation exists to narrow that gap.

---

# 4. Primary task

Starting from `FUN_1415DCFB0`:

1. find all callers/xrefs;
2. identify the caller corresponding to the Creation Kit Galaxy View Apply generation path;
3. recover the enclosing biome-processing loop or orchestration function;
4. identify the object/structure passed into `FUN_1415DCFB0` that corresponds to the shared planet-wide resource state/container seen by the later `count >= 8` checks;
5. work backward inside the enclosing orchestration boundary to identify:
   - initialization of that state;
   - writes/appends/inserts into that state;
   - helper calls that can populate it;
   - population that occurs before the first per-biome call;
6. determine where the inserted resource forms or resource records come from;
7. test whether any of those paths are consistent with atmosphere/ATMO-derived resource population;
8. stop once enough static evidence exists to design a small live x64dbg trace window.

The objective is **not** to statically prove the complete atmospheric mechanism if the evidence does not support it.

---

# 5. Bounded caller/helper traversal rule

Do not recurse upward or downward without limit.

Use this stopping rule:

> Follow callers/helpers only as far as necessary to identify the smallest function boundary that owns both:
>
> 1. pre-biome resource-state setup/population; and  
> 2. the loop or repeated calls into `FUN_1415DCFB0`.

If the immediate caller is only a thin wrapper, move upward until that orchestration boundary is found.

Once that boundary is identified, stop broad caller expansion.

For helper calls inside the orchestration function, follow only those that materially contribute to:

- the shared resource container/state;
- resource-form insertion;
- atmosphere/ATMO access;
- upstream resource initialization;
- biome-order/setup required to understand the call sequence.

Avoid exploring unrelated engine infrastructure.

---

# 6. Questions the investigation should answer

At minimum, try to answer:

### A. Enclosing control flow

- What function owns the repeated calls to `FUN_1415DCFB0`?
- Is there a recognizable biome iteration loop?
- Where in that function is the first biome call?
- What setup executes before it?

### B. Shared resource state

- Which argument/object passed to `FUN_1415DCFB0` leads to the structure later checked against `8`?
- What is the relevant pointer/offset chain?
- Is the same object mutated before the first biome call?
- What helper functions write to it?

### C. Pre-biome population

- Are any resource forms inserted before biome processing begins?
- If so, how many distinct insertion paths exist?
- Are they unconditional, category-specific, atmosphere-specific, or otherwise data-driven?
- Do they use the same insertion/storage representation as biome-generated resources?

### D. Atmosphere evidence

Look specifically for evidence consistent with:

```text
PNDT / planet
    ↓
ATMO or resolved atmosphere data
    ↓
effective Inorganic Resources
    ↓
resource-form insertion
    ↓
shared planet-wide resource state
```

But do not assume this exact path exists.

Useful evidence would include:

- ATMO form access;
- reflection-resolved atmosphere object access;
- iteration over resource/IRES-like form pointers;
- known IRES values;
- resource-list helper calls;
- a helper that appends forms before `FUN_1415DCFB0`.

### E. Maal VIII target value

If the static path permits concrete form identity reasoning, pay special attention to:

```text
Chlorine IRES FormID: 000057D5
```

Do not claim that a helper inserts Maal VIII Chlorine merely because it could theoretically do so.

---

# 7. Desired evidence products

Do not return only prose.

Produce durable, inspectable evidence in the repository.

For the enclosing orchestration function and any strong candidate helper, preserve as appropriate:

```text
decompiled pseudocode
callers
callees
relevant basic-block / instruction addresses
argument/register flow
structure offsets
writes to shared resource state
resource-form source dataflow
ATMO-related references, if any
```

Use existing Ghidra export tooling where practical.

Prefer machine-readable/plain-text exports already consistent with repository conventions.

If a new small exporter/helper script is necessary, keep it:

- non-destructive by default;
- narrowly scoped;
- documented;
- reusable for later verification.

Do not build large new tooling unless required.

---

# 8. Documentation updates

Update:

```text
docs/function-register.md
```

for any newly implicated function whose relationship is supported by evidence.

Add a focused experiment note under:

```text
docs/experiments/
```

Suggested name:

```text
pre-biome-resource-state-investigation.md
```

or similar.

The experiment note should distinguish:

```text
PROVEN STATIC FACTS
STRONG INTERPRETATIONS
OPEN QUESTIONS
```

and should explicitly identify which claims are static-only and which derive from previously established live x64dbg results.

Update `docs/known-facts.md` or `docs/hypotheses.md` only if the new evidence genuinely changes the durable research state.

Do not rewrite unrelated documentation.

---

# 9. What counts as success

The best outcome would be evidence resembling:

```text
FUN_14XXXXXXXX   orchestration function
    |
    |-- initialise shared planet resource state
    |
    |-- call FUN_14YYYYYYYY
    |      |
    |      `-- append resource forms to shared state
    |
    |-- prepare / iterate shuffled biomes
    |
    `-- call FUN_1415DCFB0
```

with enough dataflow evidence to say whether the helper is plausibly atmosphere-related.

A weaker but still successful result would be:

> The immediate orchestration function and shared resource state are identified; the state is already populated before the first biome call; the prepopulation occurs in helper `FUN_...`; the upstream source remains unresolved.

That is still sufficient to define a much smaller live trace.

Do not force a stronger conclusion than the evidence supports.

---

# 10. What not to do

Do not:

- perform x64dbg/live debugging;
- modify the standalone reproducer;
- modify xEdit exporters;
- attempt a full ATMO reflection reverse engineering pass;
- revisit the old leveled-list trail without direct necessity;
- recursively export huge call graphs;
- bulk-rename functions;
- alter Ghidra symbols/types/comments unless explicitly required for the investigation;
- claim that a helper is "the atmospheric insertion function" without direct supporting evidence;
- collapse atmosphere and biome resource provenance;
- use final resource-set agreement as proof that the correct origin path was reconstructed.

---

# 11. Final deliverables

At completion, stop and provide:

1. identified caller/orchestration function(s);
2. exact relevant addresses;
3. description of the shared resource-state argument/object;
4. any pre-biome population path found;
5. any evidence for or against ATMO participation;
6. recommended x64dbg breakpoint/start-stop window based on the static findings;
7. files changed/added;
8. concise confidence-labelled findings:
   - PROVEN
   - STRONG
   - PROVISIONAL
   - OPEN
9. `git diff`;
10. `git status --short`.

Do not commit.
Do not push.
Do not begin live tracing.

The purpose of this brief is to produce a precise static map that we can review before designing the next x64dbg experiment.
