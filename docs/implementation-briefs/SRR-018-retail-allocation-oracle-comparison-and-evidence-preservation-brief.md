# SRR-018 — Retail Allocation Oracle Comparison and Evidence Preservation

**Implementation / research brief for Codex**  
**Authority:** Offline analysis, read-only use of existing evidence, and preservation of that evidence. **No live Starfield operation.**  
**Concurrency:** At most **two concurrent sub-agents**.

## Objective

Compare the successful SRR-017 title-card extraction against the pinned Starfield resource reproducer, establish precisely where population and resource assignments agree or differ, and preserve the **smallest complete reusable comparison dataset** alongside the original acquisition evidence. Do not turn this task into another tooling or documentation project.

The existing extraction is the observation, **not** an oracle-derived reconstruction. Its qualified scope is the rooted `BSComponentDB2::DB +0x300` index at the responsive retail title card, not every possible resource store or a proved atomic snapshot. The independently reviewed live result reports **18,314** mixed descriptors, **3,211** uniquely identified PNDT/BIOM rows, **22,477** seven-slot words (**7,445** nonzero, **15,032** zero), **one** all-zero row, and two complete agreeing collections. No refusal or unresolved native identity was reported. The underlying live evidence must be verified afresh from its local original before it is used.

The known all-zero row is `starfield.esm:05E3A5` (`VoliiAlphaPlanetData`) / `starfield.esm:120C76` (`OceanLifeVoliiAlpha`). Volii Alpha's known inorganic resources are atmospheric. **Test**, rather than assume, that this explains the observed 3,211 versus modelled 3,210 biome-row difference. An all-zero terrestrial component is not a claim of zero planet-wide resources.

## Inputs and custody

1. Locate the **original local** SRR-017 extraction directory, expected at `.local-work/srr017-extract-20261118T051333Z-909249f7/`. **Do not use or depend upon the temporary chat-upload ZIP**; it has been deleted. Inspect the actual files, not merely their names or a historical summary. Require the original sealed `receipt.jsonl`, `dataset.json`, `observation.json`, `result.json` and `manifest.json` (and preserve any other original capture artifacts that materially contribute to replay).
2. Verify the original files against the hashes recorded in the committed/accepted SRR-017 findings and the original manifest. The reported anchors are:

   | Original file | SHA-256 |
   | --- | --- |
   | `receipt.jsonl` | `3a48b04479bf88a8821a704a77d684cd6941585c075323ce53c0d6a14a1efea3` |
   | `dataset.json` | `15711109761112c3ce3b2f5bf2a03966ccdb26a277ea7ec0961f0147b16eedb4` |
   | `observation.json` | `496ccd835e2e3de062aa07f812f15f406097c8f8948610a3f7952d6b08ae7c16` |
   | `result.json` | `df9fed288b61e6a5a48603b5b5e4497a001ef441562ed28f24f40a98c09f0bd4` |
   | `manifest.json` | `3441ccf092bef63ed7c9046a21ae99bb343e303443f85b1064d8215b2e971357` |

   If the original source is missing or fails verification, report the precise limitation **without reconstructing purported original evidence from a derivative**. Retain whatever qualified inputs are actually available. Do not rerun Starfield.
3. Read the current, committed **research** and **sibling reproducer** sources, their manifests, validation boundaries and existing SRR-015/016 oracle/comparison machinery. Pin the exact revisions and input corpus used for each comparison. Do not silently substitute a historical or chat-derived oracle snapshot.
4. Preserve the current uncommitted SRR-017 documentation work without staging, overwriting or incorporating unrelated changes. Record the starting Git/worktree state succinctly.

## Workstream A — Oracle comparison

Use the **unchanged existing reproducer** to generate the applicable predictions independently of the retail extraction. Prefer reuse of existing SRR-016 comparator/ledger and SRR-015 native-slot analysis; build only small missing comparison or reporting helpers. Do not modify the production reproducer or its canonical inputs without a later, separate maintainer decision.

Perform the following **separately classified** comparisons:

**1. PNDT/BIOM membership.** Compare full normalized `(defining plugin, PNDT local ID, defining plugin, BIOM local ID)` keys between the extracted 3,211 rows and the modelled corpus. Report exact intersection, retail-only, model-only, duplicated/ambiguous keys, and unsupported model inputs. Identify whether the one Volii Alpha all-zero record is precisely the single additional key; do not infer this from aggregate counts alone. Do not call an absent model row an engine error if the model never admitted that owner/biome.

**2. Seven-slot native values.** On genuinely corresponding keys, compare **each of the seven ordered native lanes**, including null/zero positions, with a separately qualified **native-slot** prediction. Do **not** equate the reproducer's accepted resource occurrences with native retained slot writes. Respect known SRR-015 differences, especially the Special-at-eight write gate, Everywhere handling, order and precision, and owner-wide RNG/cache dependencies. Where the present reproducer cannot provide a defensible seven-slot prediction, mark the owner/row `UNQUALIFIED_ORACLE` or an equally explicit applicability classification; do not score it as match or mismatch. Preserve a complete, machine-readable mismatch inventory with observed versus predicted ID, slot ordinal, source/applicability evidence, and reason.

**3. Planet-wide resource membership.** Compute observed terrestrial resource membership by aggregating the seven native biome slots per PNDT, then separately incorporate the **independently modelled effective atmospheric resources** for a comparison with the reproducer's planet-wide predictions. Clearly label this as a **derived comparison**: the atmospheric portion is not measured in the `+0x300` biome slots. Preserve distinct provenance for terrestrial observations and atmosphere-model contributions; do not claim that matching planet-wide totals proves identical seven-slot values. Explain any owners for which the model inputs are missing or source applicability is unqualified.

**4. Diagnostic distributions and counterexamples.** Report concise totals for comparable/unsupported owners and rows, exact matches, genuine value differences, zeros, Special-at-eight cases and planet-wide membership differences. Run focused tests of the Volii Alpha case, one matched nontrivial owner, at least one unsupported owner, and any concrete mismatch. Investigate observed discrepancies to the point supported by existing code/data/native evidence; **do not invent alternate mechanisms** to explain them. A genuine novel algorithm discrepancy is a research finding requiring a separate, evidence-grounded proposal, not permission to change the reproducer during SRR-018.

Make the comparison reproducible with tracked source and declared inputs. Avoid committing copies of large or redundant data merely to run the tests.

## Workstream B — Preservation and independent verification

**Re-create** a complete original-evidence ZIP from the verified **local capture directory**, not from the deleted chat attachment. Put it under `.local-work/release-assets/`, with a descriptive stable name including SRR-017 and the observation date. Preserve original bytes, names and relative paths; do not regenerate or normalize the sealed receipt or pretend a new archive is the original temporary ZIP. Create a small archive manifest containing member names, original byte lengths, SHA-256 hashes, provenance of the source directory, and archive SHA-256. Reopen the ZIP and verify each member against the original file. Keep raw address-bearing evidence private.

Identify and generate the **smallest complete derived dataset** needed to reproduce the population/slot comparisons: ideally one row per `(PNDT, BIOM)` with both canonical identities and seven ordered resource FormIDs, retaining explicit zero lanes and the all-zero row. A compact CSV and small manifest are appropriate if independently proven lossless for that purpose. Reconstruct it from the verified original dataset, not the earlier chat derivative. Compare **every one** of the 3,211 keys and 22,477 slots to the original normalized dataset and independently to `observation.json` or checked replay; reject dropped, duplicated, reordered-without-definition, or conflated zero/null values. The compact derivative does **not** replace the sealed receipt for validating native acquisition.

Store the compact dataset and its hash/provenance manifest initially under `.local-work/release-assets/` alongside the preserved full evidence. Make a reasoned, concise recommendation for whether this small dataset should become tracked reference data **after** the oracle results are assessed; do not commit it automatically. Explicitly distinguish: (i) reproducibility of analysis from the compact dataset and frozen oracle inputs; (ii) reproducibility of the native acquisition claim from the sealed original journal, qualified reader and replay. Include only material necessary for those claims. No wholesale evidence hoarding.

Independently challenge the comparison using source-independent key/slot reconciliation, negative fixtures for missing/extra keys and mismatched slots, source/applicability refusal, and Volii Alpha's zero terrestrial row with atmospheric membership. Independently verify both archive restoration and derived-data hashes. A reviewer must not merely run the producer's test and repeat its success claim.

## Scientific and engineering discipline

- **No live game or process access, save-file operations, debugger, Steam procedures, authorization mechanisms, arbitrary new gates or unapproved data modifications.** Work only from existing local evidence and permitted offline research inputs.
- **At most two concurrent sub-agents.** Suggested division is comparison and preservation/challenge, with the parent reconciling any overlapping claims.
- **Evidence-grounded lead exhaustion:** resolve or precisely bound actual observed discrepancies; do not pursue unlimited unexcluded possibilities. Distinguish known results, model-derived results, native static evidence and measured retail state.
- **Documentation restraint:** Use existing authoritative documents and the existing single research lead register where applicable. **Do not create a new lead register, serial diary, collection of review dossiers or lengthy implementation history.** Put the substantive new comparison result in the most appropriate existing research document; add at most a small purpose-specific reference if genuinely necessary. Keep independent review and working inventories under `.local-work/independent-review/` (singular), with **no tracked documentation dependency on `.local-work/` files**. The Git history already preserves previous drafts and methods.
- Do not stage, commit or push either repository. Keep the currently uncommitted SRR-017 findings intact for the subsequent combined maintainer review.

## Deliverables and acceptance

Return a concise maintainer handoff containing:

1. Full **membership comparison** and a complete machine-readable difference list, with an explicit Volii Alpha result.
2. **Seven-slot** and **planet-wide** comparison results, each with exact applicability denominators and clear `MATCH`, `DIFFERENCE` or `UNQUALIFIED` classifications. Any unresolved model limitation must be explicit; do not imply full oracle parity unless established.
3. Verified **original-evidence ZIP** in `.local-work/release-assets/`, plus a **minimal derived dataset** and its manifest there. Include exact sizes and SHA-256 digests, and demonstrate re-extraction or replay of the derived comparison input.
4. A small reproducible comparison command/test suite and independent challenge report in `.local-work/independent-review/`; the tracked research conclusions should stand on their own.
5. A **task-only diff**, assessment of the pre-existing uncommitted SRR-017 documentation, and proposed tracked-data decision. Everything remains unstaged/uncommitted/unpushed.

Success is a reproducible and honest comparison with qualified scope **and** independently verified preservation of both the primary live evidence and the minimal reusable derived dataset. A partial oracle remains a valid result when its exact limitations and unsupported rows are reported. Do not delay preservation while trying to force an oracle match.
