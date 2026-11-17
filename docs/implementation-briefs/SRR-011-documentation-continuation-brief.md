# SRR-011 — Documentation Continuation: Lifecycle Explanation and Scientific Implications

**Task type:** Documentation-only continuation of the independently reviewed SRR-011 static investigation.  
**Disposition sought:** `READY FOR SRR-011 DOCUMENTATION ACCEPTANCE`, subject to independent review.  
**Historical starting state.** An unstaged, uncommitted nine-file SRR-011 patch stack and retained native evidence. The [SRR-011 dossier](../SRR-011-planetary-allocation-execution-and-result-lifecycle.md) records the resulting science and review disposition.

**Authority:** Offline document editing and read-only verification only. No live Starfield launch or attachment, no changes to the observer, no new debugger, no alteration of the Ghidra program/database, and no Git staging, commit, or push. Up to two concurrent sub-agents remain permitted; the parent owns the integrated result and final lead/evidence audit.

## 1. Purpose

The original SRR-011 investigation is scientifically substantive but too difficult to understand without manually reconstructing the control flow and storage relationships from addresses and disassembly paragraphs. Improve its conceptual explanation **without weakening its native evidence, overstating static reachability as runtime observation, or expanding the research scope**.

The review identified three particular deficiencies:

1. New SRR-011 discoveries are intermingled with findings already established by SRR-002/003/005/006, historical sibling captures, and SRR-009/010.
2. The construction/reset route, generation/lookup separation, and retained `BSGalaxy::CTPerBiomeData` layout merit executable-looking **conceptual pseudocode** and native-source-linked diagrams.
3. The dossier's implications should explicitly distinguish supported startup/reset reachability from **unproven** ordinary Save2 execution, lazy generation, serialization, and any reason to revisit SRR-010.

User direction: SRR-010 is **closed, inconclusive and resumable**. This continuation must **not** recommend reopening the Stage B Save2 observer as the default next step. A future experiment may be mentioned only as a scientific discriminator contingent on fresh evidence, qualification, and authorization. Do not initiate an SRR-012 or other new research project.

## 2. Baseline facts and exact source anchors

The continuation used the SRR-011 dossier and lead register, prior tracked
documentation and primary native evidence. Its focal anchors were:

- **Prior SRR-003:** conditional `StarField::ModuleState` construction and PNDT iterator/callback/orchestrator path; its reachability is *not* newly discovered by SRR-011.
- **SRR-011 extension:** upstream startup loader and signed reset/replay pathways, load-order callback predicates, and a possible reopening of the module construction guard; entry into the allocator, productive work, and observed runtime execution are separate propositions.
- **SRR-011 result-storage discovery:** the orchestrator gets a pointer to the current context through an adapter (`0x140779676`, stored at `0x1407796BA`, passed by address at `0x1407796C2`); the collector dereferences it at `0x14077BD2E` and retrieves **borrowed pointers** from context's `+0x300` indexed edges. An edge has a `0x90`-byte record, a key at edge `+0x10`, and inline `CTPerBiomeData` at edge `+0x20`. Inside the **payload**, biome and optional RSGD identifiers are at `+0x40` and `+0x4C`; seven 32-bit generated resource slots occupy `+0x50..+0x68` (five Common, Special, Everywhere). Be explicit about the different coordinate origins for edge offsets and payload offsets.
- **SRR-011 writer and lookup:** authored PNDT/CSV input paths initialize the result slots to zero; the orchestrator clears/recomputes fields on the existing component aliases; `FUN_140771F30` searches the relevant planet/biome range and calls `FUN_14076E810` to copy the matched component into caller storage. Its directly inspected miss returns false; it does **not** generate on miss. Other identified consumers read copied slots or derive transient relationships.
- **SRR-011 invalidation:** targeted range removal, context `+0x268/+0x300` clearing during qualifying reset, and distinct module type-registry disposal paths. In-place recomputation, component removal, context clearing, and type-registration teardown are **not** interchangeable events. Exact runtime owner epoch, startup execution count, Save2 branch selection, possible separate generation routes, and cross-process serialization remain unresolved.
- **Lead register:** Preserve all lead identities and statuses. Especially retain the bounded scope of D06/D07/D08/C01/C02/C03 exclusions, D07b's persistence block, and challenger D09's type-registry disposition. An exhaustive negative about all game serialization, all demand triggers, or all possible callers is *not* supported.

## 3. Required dossier improvements

### A. New findings versus prior knowledge

Near the executive conclusion, add a short structured **provenance/novelty comparison** with at least these classes:

- **Previously established:** native allocator algorithm, PNDT callback/orchestrator linkage, conditional module construction, four-site observation contract, SRR-009 bounded post-title negative, and SRR-010's incomplete Save2 experiments.
- **New native relationships demonstrated by SRR-011:** upstream loader/reset/load-order ancestry with exact guards; output aliases and context-owned `CTPerBiomeData` storage; keyed hit-and-copy/miss-without-generation; inspected consumers; scoped removal/clearing/type-registry disposal.
- **New integration or corroboration:** connecting new static paths with pre-existing startup/menu-return sibling observations; distinguishing prior direct evidence from revised interpretation.
- **Still unverified:** actual allocator invocation at startup, on ordinary Save2 load, on demand or more than once in an epoch; cache-hit suppression of generation; lifetime across game operations; serialization of all seven slots.

Use native links and source locations rather than vaguely calling findings “new.” Keep the executive conclusion results-first and compact.

### B. Guarded execution-route pseudocode

Provide **pseudocode, not claimed decompilation**, for the actual conditional chain. Include the distinctions among:

1. state-0 initial loader continuation and guarded module-state construction;
2. optional early sweep flag versus the later sweep reachable on ordinary continuation;
3. signed-mode reset/replay path, guard clearing, and reconstruction;
4. qualifying load-order callbacks and their pending state / mode dispatch;
5. eligibility checks that can prevent productive PNDT or per-biome allocation despite reaching a parent routine.

Represent *tested predicates accurately*, or explicitly omit branches behind an `...`/`unresolved` annotation rather than inventing executable semantics. Relevant predicates described in the dossier include `DL==0xFF` early return, `DL==0`, pending `+0xC1C`, `0x84` reset dispatch, signed receiver `+0x2E`, optional byte `[0x145EA6000]`, and the separate `0x86` alternate's four conditions. The pseudocode should clarify relationships, **not** pretend that every qualifying reset always allocates or that `0x86` always selects ordinary Save2 loading. Reference the exact native section next to the reconstruction.

### C. Result-write and keyed-read pseudocode

Add a concise conceptual writer/reader pair illustrating:

- collection of borrowed existing component pointers from the context index;
- clearing and rewriting seven result slots in place when the appropriate generator path executes;
- matching a keyed planet/biome component and copying its payload to caller-owned output;
- a missing/invalid key returning false on the **inspected** reader path, with no implicit generation;
- temporary work buffers versus retained component storage.

Avoid coding a fabricated cache-miss → generate → insert loop. Do not claim all inputs use the same creation path, or that the reader necessarily observes previously generated rather than default-zero fields in every runtime state.

### D. Explanatory diagrams

Add lightweight, source-maintainable **Mermaid** diagrams and/or Markdown ASCII diagrams:

1. **Invocation flow:** initial loader and reset/load-order paths converging on guarded construction, optional/later PNDT sweeps, eligibility gates, and per-biome writer. Mark *static reachability* separately from historical startup/menu-return sampling and any unobserved retail allocator execution.
2. **Ownership and storage:** context `+0x300` keyed edge, edge `+0x10` key, edge `+0x20` inline `CTPerBiomeData`, payload biome/RSGD fields, seven result IDs, writer aliases, reader copy-out, representative consumers, and scoped invalidation. Visually distinguish in-place mutation from lookup copy, and context erase from type-registry teardown.

Test diagrams for readable rendering where available. Keep each modest in size. If diagram complexity obscures guards or address provenance, simplify the figure and link to the detailed native table.

### E. Cache and persistence semantics

Add one plain-language paragraph/table differentiating **(i)** retained writable results, **(ii)** later keyed lookup and copied reuse, **(iii)** hypothetical lazy fill on miss, **(iv)** suppression of repeat generation, and **(v)** persistence across process/save boundaries. State precisely which are `PROVEN STATIC`, which have scoped exclusions, and which remain unsupported. A context-owned container is not proof of a lazy cache; zero-initialized authored inputs are not proof that all serialized sources lack outputs.

### F. Blocked-lead and research-implications summary

Without modifying lead dispositions merely for presentation, summarize outstanding blocks and **why available static evidence cannot currently resolve them**, pointing to corresponding register entries. Distinguish an actual access/evidence obstruction from a remaining scientific uncertainty that can be framed as a testable prediction. Do not manufacture reasons for a block.

Add a compact conclusion explaining that startup/reset *reachability* is strengthened, on-demand pathways are not globally excluded, and SRR-010 remains closed because ordinary Save2 **branch selection and actual allocator execution have not been established**, while the four-site Save2 load has already failed four times. Any future dynamic recommendation must specify exactly what it could discriminate and explicitly require separate approval; the existing report's limit of at most two options remains, but it is acceptable to recommend **none**.

## 4. Boundaries and edit policy

- Documentation-first. Prefer modifications to `docs/SRR-011-planetary-allocation-execution-and-result-lifecycle.md`; update the lead register or related registers only when strictly necessary to repair a concrete inconsistency, citing the reason. Avoid extraneous changes to `tools/srr011/inspect_pe.py` or other code.
- No new native research campaign or unbounded lead discovery. **Read-only spot checks** of exact instructions and existing archived evidence are allowed to prevent inaccurate pseudocode. If a substantive gap requires fresh analysis, flag it as a blocked correction with the exact needed verification, rather than silently claiming proof.
- Preserve existing addresses, evidence grades, prior-art citations, witness status, hypotheses, documented uncertainties, and review blocks. Do not rewrite the previously accepted scientific outcomes or conflate historical observations with this task.
- The original SRR-011 lead-exhaustion commitment remains intact. The new presentation must not hide an unresolved plausible lead. Do not automatically mark blocked leads as exhausted, or recategorize them solely to make the dossier sound complete.
- Do not include proprietary game bytes, private capture contents, saves, credentials, personal paths, or executable files in tracked outputs.
- The existing SRR-011 source and patch remain **unstaged, uncommitted, unpushed**. Do not alter the frozen historical evidence; retain a clearly reviewable incremental documentation-only diff. No live execution or authorized next experiment.

## 5. Verification, independent challenge, and handoff

Codex should:

1. Record the starting HEAD, index and status, identify the exact reviewed SRR-011 base patch, and confirm the intended edit scope.
2. Draft conceptual sections, pseudocode and diagrams using exact existing evidence. Check that each pseudocode conditional and diagram edge has the intended bounded scientific meaning.
3. Perform a targeted editorial consistency audit of the executive conclusion, new/old claims, cache terminology, lead statuses, registers, and links/anchors. Run an ordinary Markdown/Mermaid validation where supported.
4. Obtain **independent challenger review** against this brief. In particular, challenge whether any simplified figure turns possible reachability into observed execution, turns a zero initialization into a universal persistence exclusion, misplaces an edge offset as a payload offset, or quietly prescribes reopening SRR-010.
5. Apply and reverse-check the incremental patch in an isolated replay against the frozen SRR-011 starting snapshot; compare other reviewed files and historical review blocks byte-for-byte. Verify UTF-8, local links and no unauthorized path additions.
6. Return a concise results-first summary, actual changed-file inventory, incremental `.diff`, verification receipt and independent review. Explain any unresolved documentation gaps. **Stop before staging or committing.**

### Acceptance criteria

- **DC-01:** Clear and accurate “what is new” versus prior source evidence; no old finding claimed as newly discovered.
- **DC-02:** Guarded invocation/reset pseudocode agrees with native predicates and expresses runtime uncertainties explicitly.
- **DC-03:** Writer/reader pseudocode accurately distinguishes in-place mutation, lookup copy, and no-generation-on-miss for the inspected path.
- **DC-04:** Readable, source-maintainable invocation and ownership diagrams correctly distinguish static paths, historical observations, and storage-offset origins.
- **DC-05:** Cache semantics and persistence limitations are properly qualified; no invented lazy-fill, repeated-run suppression or cross-epoch evidence.
- **DC-06:** Blocked leads and implications are explained honestly; no unsupported justification for repeating SRR-010.
- **DC-07:** Exact existing scientific outcomes, provenance, lead statuses, evidence identifiers and history remain intact, except for independently justified accuracy fixes.
- **DC-08:** Independent challenge, isolated replay, exact patch scope and no-commit/no-live requirements pass.

**Expected final disposition:** `READY FOR SRR-011 DOCUMENTATION ACCEPTANCE`, or an explicitly identified, evidence-backed documentation block. This brief does **not** authorize a new runtime experiment, a new SRR-011 scientific phase, SRR-010 reopening, or a Git commit.
