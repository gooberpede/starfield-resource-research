# SRR-022 — PlayerKnowledge Save Serialization and Comparative Analysis

**Implementation brief for Codex**  
**Status:** Authorized scope; implementation and findings subject to independent review and maintainer acceptance  
**Project:** `starfield-resource-research`  
**Working root:** `D:\Projects\starfield-resource-research`  
**Related research:** SRR-019–021, especially `docs/component-database.md`, `docs/structure-register.md`, `docs/function-register.md`, `docs/PROVENANCE.md`, and `docs/hypotheses.md`

## 1. Objective

Recover, as far as the evidence supports, the actual **serialized `BSGalaxy::PlayerKnowledge` population** in the user's **Save2** and **Save52**, and independently compare the two. Work from the native **SaveGlobalData / LoadGlobalData unit 6** writer/reader already established on the pinned retail `Starfield.exe` 1.16.244.0. The question is what the saves contain—not what we presume the player did between them.

The desired output is a qualified, repeatable **offline** method that distinguishes:

1. **Serialized state:** bytes and fields demonstrably present in the save;
2. **Reconstructed runtime state:** fields and tables the pinned native load path would produce;
3. **Displayed gameplay state:** observations from Save2 screenshots or other gameplay evidence, which cannot be inferred automatically from the first two.

A useful partial result is acceptable when a specific, evidence-grounded format or native boundary remains unresolved. However, identifying only a plausible unit header is insufficient if further concrete decoding leads remain.

## 2. Authorized inputs and boundaries

- The user's original **Save2** and **Save52**. Discover their actual files and filenames from the existing local custody/release-assets and known save locations. **Do not assume** an existing Save2 copy or manifest is complete or correctly attributed; verify it. Ask for a missing source only if it truly cannot be found through authorized local project evidence.
- The pinned retail image and previously recovered read-only static evidence, plus tracked source and lawful external tools/inputs needed to interpret save framing or FormID remapping. Do not broaden to Creation Kit mechanisms as though they were retail proof.
- Existing documentation and research tooling in this repository; sibling `starfield-resource-reproducer` is **read-only** and can supply an independently labelled planetary-membership comparison, never assumed serialized content.
- The existing Save2 screenshot evidence under `.local-work/release-assets/SRR-021-save2-screenshots/` as **separate historical gameplay evidence**, not a binary reference for what Save2 necessarily serialized. Screenshots taken after loading Save2 may reflect subsequent actions.

**Strictly offline.** Do not launch/attach to Starfield, open a save in the game, use a debugger against a live process, load a save into a game editor that may rewrite it, or modify the originals. No new gameplay, save mutation, Ghidra-project mutation, network service, credentials, release/publication action, or changes to the reproducer are authorized. Read-only inspection of file bytes and pinned executable disassembly is permitted. Implement only minimal reusable parsing tools required by this task.

## 3. Primary evidence anchors

Start by confirming the present repository documentation and underlying native evidence rather than assuming historical summaries are exhaustive:

- `BSGalaxy::PlayerKnowledge`: **body-keyed** component in `BSComponentDB2::DB` **+0x268**, distinct from retained `CTPerBiomeData` in the **+0x300** mixed store.
- Stored wrapper: composed key at **+0x10**, payload at **+0x20**. Payload contains a knowledge **mask at +0**, stored signed **scan level at +4**, item lookup/index state, and **0x30-byte** item entries. An item's **+0x21** byte participates in positive resource-survey credit; **+0x20** is a distinct byte.
- Save path: `SaveGlobalData` **unit 6**, `FUN_141411190 → FUN_142337790`. Writes body identity, mask, component **version 3**, scan level; **mask bit 3** gates the item section. Item records contain resolved/form-encoded IDs, +0x21 then +0x20, and additional version-dependent data.
- Load path: `LoadGlobalData` **unit 6**, `FUN_141413570 → FUN_142337A50`. Restores body identity, mask and level, and conditionally rebuilds item entries; the second item byte is present from **version ≥2**, with additional nested/version-3 fields. Native FormID read/write translation must be addressed, not guessed.
- Other native `PlayerKnowledge` factory or queued-copy routes are **in-memory component paths**, **not evidence of save serialization**. Likewise, saving this component does not prove serialization of the biome-allocation seven slots.

These locators are research-specific aliases/offsets for the pinned retail executable. Verify address-domain, type registration, record framing and byte widths against native evidence before using them to interpret bytes. Treat unsupported schema assumptions as hypotheses.

## 4. Execution plan

### A. Evidence inventory and custody — perform first

1. Capture starting HEAD, index/worktree status, existing changes and relevant original/release-asset hashes; preserve all pre-existing material. Identify Save2 and Save52 from actual source files and existing manifests, avoiding ambiguous matching by filename alone.
2. Determine whether **Save2** is already preserved under `.local-work/release-assets/`. If yes, verify bytes, provenance and manifest identity against its available original source. Do not duplicate or replace a verified preservation merely for uniform naming.
3. Preserve an **unchanged Save52** in the existing private release-assets corpus, and preserve Save2 if not already present. Use a small custody manifest recording evidence ID, source/original filename, actual source location (private only), byte length, SHA-256, acquisition/copy method, known save provenance and limitations, and source-to-archive verification. Retain original bytes; no save decoding changes an archived original.
4. All parsing, decompression, extraction and adversarial tests operate on **read-only inputs or disposable copies** under `.local-work/`. Never write beside or over a game-managed original save. Do not conflate the Save2 screenshot timeline with a single unchanged saved state.
5. If the source save, its identity, or lawful offline access is missing, report that precise blocker. Do not fabricate a source or manufacture a synthetic save and present it as observed data.

### B. Locate and bound PlayerKnowledge within the save container

From the actual save bytes and the pinned native I/O path, establish enough framing to find **GlobalData unit 6** reliably in both files. Decode only the necessary container header/index, compression, offset/size, subrecord or stream boundaries. Track exact offsets and byte lengths and enforce bounds and declared sizes. Distinguish apparent unit numbers from demonstrated dispatch identities. If existing public parsers help, verify their output against native framing and source bytes; do not silently treat their schema as authoritative.

For each save, report whether the relevant unit is present, genuinely absent, truncated, unsupported or indeterminate. Verify that extracted payloads conserve bytes and that independent extraction can reproduce them. Do not expand into unrelated global-data units or a general-purpose Starfield save decoder without a demonstrated dependency.

### C. Decode PlayerKnowledge and restore identities

Derive the unit's reader from the native **write/read pair**, including container/key framing, component version, FormID mapping, mask, scan level and item-table structure. Treat `mask bit 3` and version branches as explicit conditions; do not infer a missing item section means an absent component. Preserve unknown fields/sections as **bounded uninterpreted bytes**, not invented values. Check item counts, sizes, uniqueness/duplicates as applicable, trailing bytes and cross-references; distinguish unknown FormIDs from zero or known IDs.

For each qualified record retain:

- body identity (raw saved ID and normalized plugin-local identity where justified);
- presence/absence and exact mask, including visit bit and item-section bit;
- stored scan level and component format/version;
- resource/item identities (raw and normalized if established), +0x21 progress and separate +0x20 byte;
- remaining field identities or bounded unknowns and reconstruction limitations;
- source save, unit and byte offsets sufficient for independent verification.

Map the resulting records to expected **in-memory** body-keyed components and item-index entries under the documented loader semantics, but do **not** assert that a particular game session executed the loader or rendered a matching screen. Use explicit names such as `SERIALIZED`, `RECONSTRUCTION_PREDICTED`, `UNRESOLVED_IDENTITY`, and `NOT_OBSERVED` rather than collapsing these into a generic PASS.

### D. Compare Save2 and Save52 independently

Produce a machine-readable **full-population** inventory and a deterministic comparison by normalized body and item identity wherever reliable. Include bodies and items found in only one save; distinguish missing components, empty item tables, absent progress entries, zero progress and unresolved identities. Record differing masks, levels, versions, item progress and other defensible fields. Retain raw evidence coordinates for discrepancies.

Only as a **separate check**, compare decoded state with known planetary resource membership from established generation inputs or with the Save2 screenshots. Declare the independent sources and applicability limits, including atmosphere-vs-terrestrial survey credit and the fact that different save histories are **not** a controlled before/after action test. No inference about what happened between Save2 and Save52 without specific evidence.

### E. Independent verification and adversarial checks

Challenge the strongest claims against raw original bytes and the native writer/reader, not only against producer-generated normalized JSON. Where practical use a separate parser/reconstruction route or independent field/offset checks. Exercise meaningful counterexamples: wrong unit, truncated length, bad count, missing bit-3 section, version-conditional field, invalid/missing FormID mapping, duplicate/ambiguous body or item, zero versus absent progress, wrong container compression/offset, and source/archived-copy drift. Confirm that the parser **refuses or qualifies** unsupported cases rather than silently accepting them.

The reviewer should verify the final evidence identity and complete comparison; a document-only or diff-only review cannot substitute for testing the saved data. No false 100%-coverage claim if some units, versions or identities remain outside the decoded profile.

## 5. Parallel work and lead exhaustion

**At most three concurrent sub-agents**, used when beneficial; the parent owns integration, scope and resolution of disagreements. Suggested separable assignments:

- **A — Container/GlobalData framing:** save structure, extraction and bounds;
- **B — Native PlayerKnowledge format:** writer/reader correspondence, version and FormID interpretation;
- **C — Independent challenge/comparison:** adversarial fixtures and raw-byte corroboration, expanding into final comparison once A/B supply qualified outputs.

A separate independent challenger reviews the integrated substantive result. Sub-agents may conclude early; don't force parallelism when it creates coupling or redundant work.

Continue evidence-grounded leads until the decoding question is resolved, contradicted or has an explicitly documented remaining native/format boundary with no further discriminating route presently available. **No arbitrary time limit, function-count quota, capture-size cap, or requirement to build an unrelated parser.** Do not institute new privilege, trust or provenance gates without a demonstrated scientific or integrity need.

## 6. Deliverables and documentation

1. A **reproducible read-only offline extraction/decoder**, tracked if it is the repeatable method for published conclusions, with minimal usage, format limits and tests. Prefer an existing tool location rather than an unnecessary parallel tool system. Private data, original save bytes, extracted streams and decoded per-save tables are **not tracked**.
2. Private archived original save identities and a qualified custody manifest in `.local-work/release-assets/`; private raw extracts, comparison tables, checks and independent review under the existing `.local-work/` conventions (including `.local-work/independent-review/`, singular). Do not modify or republish SRR-017 evidence or the screenshot corpus.
3. Update only the relevant authoritative docs: principally `docs/component-database.md`, `docs/structure-register.md`, `docs/function-register.md`, `docs/PROVENANCE.md`, and `docs/hypotheses.md` when a genuine unresolved question remains. Document concrete findings, exact decoded coverage, provenance and limitations. **No new numbered research dossier, duplicate lead register, research diary, or hypothetical-mod motivation.** Do not place private paths or indispensable private payloads into tracked docs. Identify the lawful input and reproducible route separately from private historical custody.
4. Final concise report: per-save qualified record counts, component versions, identity-resolution coverage, exact comparison categories and anomalies, unresolved boundaries, independent checks, and minimal next discriminating action where needed. Report no live gameplay observations that were not made.
5. Task-only native Git diff and changed-path inventory; preserve baseline changes. Follow existing repository workflow and independent-review requirements. Retain any pre-existing untracked implementation brief without adding it to the patch unless expressly authorized.

**Do not stage, commit, push, tag, publish or modify the sibling reproducer.** Handoff for maintainer review.

## 7. Acceptance criteria

- Both save source identities and preservation status are independently established; Save52 is archived unchanged, and Save2 is verified or newly preserved if genuinely missing.
- The unit-6 identification and decoded fields are demonstrated against the native paired stream contract and original save bytes, with exact boundaries, counts and limitations.
- The recovered population and full Save2-versus-Save52 differences are reproducible from the same inputs, including missing/zero/unresolved distinctions; **or** a substantive, independently verified partial result specifies a concrete exhausted boundary rather than inventing completeness.
- All material assertions are correctly labelled as serialized observation, native load reconstruction, independent model comparison or prior screenshot observation.
- Independent challenger verifies the important native/save claims, custody, adversarial refusals, tests, documentation scope and task-only patch; `COMPLETE` only if all applicable mandatory conditions pass, otherwise report `REWORK` or `BLOCKED` with the specific issue.
- No originals, live game, project analysis database or sibling repository are mutated; no private saves or proprietary payloads are committed or published.
