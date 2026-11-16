# SRR-013 — Read-Only Allocation State Inspector: Implementation and Disposable Qualification

**Type:** Codex implementation and independent-audit brief  
**Disposition requested:** Offline implementation and qualification only; **no live retail authorization**  
**Project:** `starfield-resource-research`  
**Starting point:** Committed/synced SRR-012, *Retained Planetary Allocation State Observation Feasibility*  
**Agent allowance:** Up to **two concurrently active sub-agents**, coordinated by the parent agent  
**Git policy:** Leave all changes **unstaged, uncommitted and unpushed** for maintainer review.

## 1. Purpose and scientific boundary

Implement and independently qualify a **small, external, read-only inspector** capable of acquiring the **four predefined SRR-012 `CTPerBiomeData` samples** from a Windows process exposing the verified native layout and classifying each under the existing SRR-012 measurement contract:

- `POPULATED_RESULT_OBSERVED`
- `QUALIFIED_UNPOPULATED`
- `STATE_INDETERMINATE`

The purpose of SRR-013 is **engineering readiness** for a future separately authorized measurement at a responsive title card, main menu, or settled gameplay. It must **not** claim that any allocator result was actually observed in a live Starfield process. In particular, a qualified all-zero sampled payload does **not** prove the allocator never ran, and matching data at two checkpoints does **not** prove that the same object persisted, that no regeneration occurred, or that the values were serialized in a save.

Treat the accepted SRR-012 dossier, acquisition evidence, sample plan, measurement contract, lead register, and `tools/srr012/check_contract.py` as authoritative inputs. Reuse SRR-011's established owner/index/component representation, distinguishing **retained allocation results** from source records, intermediate state and presentation data. Do not reopen broad native lifecycle research unless implementation reveals a concrete contradiction that directly blocks the narrow acquisition path.

## 2. Target acquisition and identity contract

Implement the source-supported path from an **authenticated external process** and verified mapped `Starfield.exe` image base `M` to the published context pointer (SRR-012 identifies the slot as `M + 0x82EEBB0` and expected embedded context as `M + 0x82EE5C0` for the pinned retail build), then to the registered `BSComponentDB2::DB` owner, its `+0x300` component index, exact matching typed edge records, inline `CTPerBiomeData` payloads, and the seven resource FormID fields at payload offsets `+0x50` through `+0x68`. **Check the canonical SRR-012 evidence for exact byte layouts, traversal rules and admission predicates rather than treating this summary as a complete structure specification.**

Require independent, mutually consistent checks on process epoch/executable mapping, pointer publication, context owner and registration, index/container shape, planet and BIOM keys, unique matching component and field validity. Use the documented independent FormID-map path where the SRR-012 contract makes it necessary to eliminate wrong-owner, key alias or record-substitution risks. Do not accept an arbitrary matching byte pattern, embedded image address alone, plausible resource FormIDs alone, or the mere presence of a readable page as proof of correct object identity. Preserve exact provenance for each accepted read.

Retain the current retail version profile (Starfield `1.16.244.0`, `Starfield.exe` SHA-256 `7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28`) as the **only approved retail applicability target for the future**. Do not silently generalize layout offsets or permit fallback memory scans when identity checks fail.

### Read-only access constraints

- Separate **target admission** from **memory acquisition** and **scientific classification**. Fix the minimal previously reviewed Windows query/read rights; do not elevate privileges or retry with stronger rights. Do not inherit or invoke the SRR-010 debugger path.
- **No** `DebugActiveProcess`, hardware/software breakpoints, `SetThreadContext`, `WriteProcessMemory`, remote thread/call/code execution, thread suspension, forced target termination, memory patching or executable injection.
- Bounded `ReadProcessMemory`-style reads only for the exact verified owner/index/keys/payloads and their necessary identity evidence. No broad dumps, long-running telemetry service or unrelated target-object inspection.
- Reads that fail or disagree yield a precise `STATE_INDETERMINATE` reason; never repair or modify the target to make the sample readable.
- A future retail observation must have its **own explicit written authorization**. The implementation and fixtures in this brief may open/read only Codex-owned disposable processes created for qualification.

## 3. Realistic native traversal and qualification target

The most important task is implementing and testing the **actual source-derived component-index traversal**, not only exercising the three-way result classifier. The native index includes internal and leaf nodes, directory/record-block representations, bounded successor/search conditions and typed edge payloads. Build the decoder around the pinned evidence, including exact field widths, offsets, alignment, unsigned comparisons and end/sentinel behaviour. Define finite bounds for pointer-depth, node count, visited entries, bytes and repeated visits; these are **safety bounds for malformed structures**, not assumed limits on valid retail population. If a genuine population exceeds a safety bound, report incomplete rather than silently truncating and asserting absence.

Provide an **owned disposable x64 Windows process** exposing realistic instances of the documented layouts; the inspector must access it **externally through the same read-side acquisition interface** intended for future retail use. Use variants that exercise at least:

1. Correctly published owner/context, registered type, index, keys, component payloads and exact known populated output tuples.
2. Structurally valid and eligible **all-zero** output slots, including a structurally valid all-zero comparison/control.
3. Multiple index depths, internal nodes, leaf and packed record-block forms, boundary keys and successor paths, with independently known expected enumerations.
4. Missing key/BIOM, duplicate matches, wrong owner, wrong type, wrong registry and wrong FormID mapping, including readable but incorrect decoy structures.
5. Invalid/unaligned/unreadable pointers, loops, malformed counts/bounds, inconsistent directory metadata and excessive traversal: deterministic refusal, no crash or unbounded scan.
6. Target process-epoch mismatch, mapped-image mismatch and insufficient read rights, with no privilege fallback.
7. Concurrent mutation of tree structure and resource slots, including insertion/removal, intermediate clear, ABA-like changes where demonstrable, and two agreeing reads that can still represent a stable intermediate state. Disclose what cannot be detected.
8. Mixed results and per-sample eligibility, including unexpected nonzero tuples; no coercion into all-zero or population verdicts.
9. Repeatable independent replay of acquisition evidence and classification without a running target.

Construct at least one adverse fixture that a simplistic **flat-array** or **first-leaf-only** decoder would incorrectly pass. The independent challenger must verify that the test exercises the same production traversal code, not a specially simplified fixture-only shortcut.

## 4. Sample and measurement contract

Implement the **four exact samples** defined in `docs/SRR-012-sample-plan.md`: **three Kreet biomes** and **one Decaran VII-b control**. Retain their pinned planet/BIOM/PNDT/RSGD identities, effective-input assumptions, key ordering, predicted seven-word tuples and individual eligibility conditions; read the source plan directly. Do not substitute arbitrary planets or broaden into an exhaustive planetary dump.

Keep expected offline tuples separate from observed bytes. An exact prediction check is admissible only when the contract's effective-input and load-order equivalence requirements have been met; in their absence label the comparison conditional and preserve raw typed field observations without inventing equivalence. Correctly distinguish:

- **`POPULATED_RESULT_OBSERVED`:** unique, correctly owned and eligible component; consistent bounded read; accepted populated tuple and required identity/effective-input checks.
- **`QUALIFIED_UNPOPULATED`:** same positive identity, presence, eligibility and consistency requirements; all seven resource fields zero. Limit the conclusion to that **sampled component at that checkpoint**.
- **`STATE_INDETERMINATE`:** absent or duplicate component, invalid owner/identity/eligibility, unexpected output, inconclusive effective inputs, read failure, partial traversal, inconsistency or any unresolved prerequisite.

Report each sample separately and retain exact reason codes, key identities, seven observed words, verification status, read count, relevant read boundaries and evidence hashes where appropriate. A process-level summary must **not** promote isolated zeros into a claim that the entire allocation catalogue was unpopulated. A partial populated result can still stand for its valid sample when other samples are indeterminate.

The inspector should accept a **caller/operator-supplied checkpoint label** (`title`, `menu`, `settled-gameplay`) as external metadata, not infer the game's UI state from memory. Use the **same binary and classifier** for all three; labels do not change thresholds or the scientific contract. The present phase does not authorize taking any of these checkpoints in retail Starfield.

## 5. Consistency, evidence and privacy

Implement the SRR-012 **paired-read/structural revalidation** protocol (or a more strongly supported equivalent): collect the exact relevant owner, index and typed sample identities and resource values twice, with checks for structural change, incomplete traversal, process identity and source validity. Prefer narrow, bounded rereads. Preserve original typed values and classify disagreements as indeterminate.

Do not claim an atomic snapshot: even agreeing samples may miss intervening clear/rewrite cycles or ABA. An eligible zero may represent the actual state sampled during an intermediate clearing pass. Record that limitation prominently. Do not infer execution frequency, startup timing, cache-hit suppression, write causation, persistence or serialized state from mere field presence or absence.

Store only necessary **disposable** observations, structural summaries and reproducible hashes. Keep host/participant identifiers and target process data out of tracked fixtures and Markdown; no proprietary image bytes, real game memory or private save files may enter the commit patch. Any future live collection must specify an appropriately limited private evidence-custody policy separately.

## 6. Work organization and lead-exhaustion rule

Up to **two concurrent sub-agents** are approved. Suggested initial split:

- **Agent A:** read-only process interface, owner/context discovery, native tree and FormID mapping traversal, malformed structure defences.
- **Agent B:** sample contract, classification, concurrency/adversarial fixtures, replay verification.

The parent agent owns integration, shared native identity reconciliation, scope control and independent-review handoff. Completed sub-agents may be replaced without ever exceeding two concurrently active agents.

Retain a **lead register** for any new, relevant contradictions or implementation uncertainties. Do not end while credible actionable leads within SRR-013's narrow scope remain. Give each a defensible disposition of **resolved**, **exhausted/excluded**, or **blocked with concrete obstruction and means to unblock**. Do not follow unrelated engine subsystems simply because they appear in a cross-reference. A blocker is not merely that a branch is inconvenient or difficult.

## 7. Staged offline work and explicit stopping gates

**Stage A — Contract translation:** Reconcile the exact SRR-012 native data layout, sample definitions, read permissions, index invariants, scientific reasons and reporting schema. Highlight any contradictions before choosing a decoder.

**Stage B — Native implementation:** Implement a minimal external reader, owned disposable target with realistic native structures, and acquisition/classification/replay split. Reuse existing source-derived tools when appropriate. No retail access.

**Stage C — Disposable qualification:** Run all nominal/adverse scenarios above against actual separate-process reads. Demonstrate coverage of nontrivial tree shapes, independently verify expected enumerations, and check false populated, false qualified zero and indeterminate cases. Retain bounded failure records and any early failed tests; fix material defects rather than documenting a passing simplified subset.

**Stage D — Freeze and independent challenge:** Pin exact source, binaries and toolchain; independently reproduce build where practical; provide a complete source diff and representative disposable receipts. Independent reviewer challenges the real traversal against counterexamples, read-only constraints, identity/effective-input handling, concurrent modification and scientific conclusions. Do not authorize live retail activity on the strength of offline pass alone.

Stop with **`READY FOR RETAIL STATE-OBSERVATION AUTHORIZATION`** only if all essential requirements pass and the candidate is frozen. Otherwise return **`IMPLEMENTATION_BLOCKED`** or **`QUALIFICATION_INCOMPLETE`**, with explicit blockers and what remains usable. Do not fabricate success by weakening the SRR-012 contract. A realistic disposable surrogate validates engineering behaviour, not actual runtime compatibility or accessibility of the retail context.

## 8. Save2 versus Save52 and eventual travel — future-live planning only

**No travel, retail load, save copying or alteration is authorized by SRR-013.** Reading retained Kreet or Decaran VII-b components **does not itself require visiting either planet**: the initial checkpoint experiment measures in-memory allocation records, not surface resources. Therefore do **not** change the proposed measurement to include travel merely because the sample planet names are Kreet and Decaran VII-b.

If a **later separately authorized live experiment really requires physical travel or planet access**, especially to **Decaran VII-b** in the distant level-75 Decaran system, plan around **Save52**, **not Save2**. The Save2 character lacks the level/equipment and Grav Drive needed for that journey, while the Save52 character can reach all systems. Such a plan must explicitly account for differences in save state and checkpoint comparability; do not silently mix Save2 and Save52 as if they were equivalent controls.

Before any authorized live use of Save52, create and verify a **separate retained copy of Save52 under `.local-work/release-assets/`**, following the same non-destructive pattern and custody/protection practices previously used for Save2. Pin original, backup and retained-copy identity and hash and obtain specific approval for any copying or live use; do not infer Save52's path or digest. Keep the original populated Saves directories intact. **That copy is not a deliverable or authorized operation in this offline brief.**

For a title/menu/settled-gameplay **state-only** measurement not involving travel, select the save and checkpoints on scientific grounds after reviewing the feasibility evidence. Do not presume Save52 is mandatory merely because one sampled allocation belongs to Decaran VII-b.

## 9. Deliverables and acceptance checklist

Create or update durable research documents consistent with existing `docs/` registers and `docs/research-workflow.md`:

1. Short engineering dossier explaining the actual read path, native layouts and invariants, minimal design, decision logic, known limitations and retail-readiness conditions, with compact pseudocode/structure diagrams where useful.
2. A single tested native reader implementation, an owned disposable process/fixture, adversarial qualification scripts and replayable classifier tests.
3. Per-case disposable evidence, expected-versus-actual results and a frozen artifact/identity manifest; no private/proprietary bytes tracked.
4. An updated lead register disposing of every relevant plausible implementation lead.
5. A **proposed** single-checkpoint future live run card emphasizing title-card observation and preservation; clearly mark it **NOT AUTHORIZED**. Retain the Save52 conditional travel constraint above.
6. Independent challenge and exact patch replay; concise results-first handoff showing which criteria passed, whether the binary is frozen and what remains unknown.

**Acceptance criteria:**

- **SRR013-AC1:** Canonical SRR-012 contract and exactly four sample identities retained; no scientific widening.
- **SRR013-AC2:** Genuine externally read, source-faithful traversal and contextual identity validation, including multi-level/packed native layouts.
- **SRR013-AC3:** Fixed read-only access with no debugger, target write, target code execution, suspension, privilege fallback or retail open.
- **SRR013-AC4:** All populated, eligible-zero and indeterminate decisions correct and per-sample; absent/duplicate/decoy and effective-input uncertainties fail closed.
- **SRR013-AC5:** Paired-read checks and adverse mutation cases exercised; temporal limits accurately disclosed.
- **SRR013-AC6:** Realistic native disposable/adversarial results, replay and exact binary/source identities are independently reproduced and reviewed.
- **SRR013-AC7:** Complete relevant lead register, correctly scoped scientific interpretation, and explicit Save52 travel/copy requirement **without undertaking live work**.
- **SRR013-AC8:** Exact task-only source/documentation patch, private/proprietary exclusion, baseline integrity, independent review, and **no stage, commit or push**.

**Final authorization boundary:** Implement and qualify **only on disposable processes**. Return the frozen candidate and independently reviewed run card for maintainer consideration. **Do not start, attach to, read memory from, travel within, or otherwise instrument live Starfield; do not copy Save52 during SRR-013; and do not stage, commit or push files.**
