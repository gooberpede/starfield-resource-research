# SRR-017 — Operator-Initiated Live Extraction Correction

**Maintainer decision: simplify the live workflow. Implementation authorized; live game access is not authorized by this brief.**

## Objective

Replace the SRR-017 pre-launch/Steam-attestation/authorization controller with a minimal operator-initiated command for an **already running Starfield process**. The operator will launch Starfield normally, hold at the responsive title card, tell Codex to run the extraction, and receive a clear completion/failure message before quitting. The scientific deliverable remains a **complete, identity-resolved Planet → Biome → Resource export** from the rooted `BSComponentDB2::DB +0x300` index: every admitted biome, its native and normalized PNDT/BIOM identities, and all seven resource slots including zeros. The export must remain suitable for later oracle comparison; oracle evaluation is not part of acquisition.

The 18 November attempt never opened a game process. It failed at `HKCU\Software\Valve\Steam\SteamPath` before the launch prompt. **Do not diagnose, repair, or substitute for that registry check. Remove the dependency.** Preserve the historical attempt as `ADMISSION_REFUSED — NO_OBSERVATION`; do not change its result.

## Required interaction and command

1. The operator launches Starfield and waits at the title card **before** invoking the extractor.
2. Codex runs one simple extraction command against the already running process. Select the unique compatible `Starfield.exe` or accept an **operator-specified PID** if multiple plausible processes exist. Do not launch or close the game on the operator's behalf. Tell the operator what process was selected. An explicit operator response in the current conversation is the trigger; no authorization JSON or written approval record is needed.
3. Read the retained database using the existing qualified **read/query-only** memory interface and produce the paired full-store observation, normalized dataset, and enough acquisition evidence to check/replay the result. Give the operator a clear **finished / incomplete / failed** message and the output location; they may then Quit normally.
4. If there is a real acquisition problem, preserve useful partial diagnostic evidence and explain the specific technical failure. Do not automatically retry, relaunch, require a second approval file, or enlarge limits during the same run. The operator may explicitly request a later attempt.

Implement and document the actual invocation. Prefer the existing reader and export code rather than a new control framework. An output directory may be supplied or created as normal program output, **not** used as an authorization credential or one-use lock.

## Remove operational gates, not scientific validation

**Remove as mandatory admission/runtime conditions:** Steam installation registry, Steam parent/session/log attribution, launch orchestration, preflight and postflight suites, protected-save inventory/backup attestations, overlay/Cloud configuration, disk-space floor/reserve checks, independent exit witness, authorization JSON/claim/signature/expiry/trust infrastructure, and special administrative setup. Do not replace any of them with different identity, provenance, environment, credential, or filesystem checks. The operator owns launch, title-card state, and eventual Quit.

**Keep:** validation that the selected process is the intended compatible Starfield executable/layout (using only what is needed to interpret its data); read/query-only access; published DB and component registry checks; full rooted mixed-tree traversal and coverage/count reconciliation; PNDT/BIOM/RSGD/resource FormID and native type checks; full/medium/small loaded-plugin namespace resolution; seven-slot capture including zero rows; paired independently rooted collections and agreement; legitimate bounded read/memory/work limits, cancellation, and checked evidence replay/export. Keep meaningful errors for ambiguous process selection, unreadable/changed memory, invalid structure, wrong executable layout, or incomplete acquisition. **No arbitrary elapsed-time deadline.**

Do not reinstate physical ESM provenance, VFS-provider proof, winning-content attribution, oracle coverage, or any other previously withdrawn condition as an extraction gate. No promise of atomicity or of all-galaxy completeness beyond the admitted rooted store.

Treat standard output-directory write errors as ordinary errors. Preserve raw runtime data where possible, but do not call an incomplete/identity-unresolved extraction qualified. Avoid verbose administrative reporting when the observation succeeds.

## Qualification and proportionality audit

- Implement the smallest changes to the committed SRR-017 code. Preserve qualified `srr016` census and `srr017` native-identity/export logic where possible.
- Exercise the **same operator-triggered command/controller** against disposable owned processes, including one complete 3,210-row and one 4,096-row pair, exact seven-slot export/replay, explicit PID selection, absent/multiple target, read failure, cancellation, changed native identity, and work-budget refusal.
- Assert the path never consults the Steam registry, authorization files, save files or preflight/postflight/exit-witness interfaces and never launches/closes Starfield. Fail tests if an old admission function is invoked. Do not silently bypass native scientific checks.
- Have an independent challenger assess both scientific correctness **and whether every remaining prerequisite is genuinely necessary**. At most **two concurrent sub-agents**; apply evidence-grounded lead exhaustion rather than hypothetical safeguards.
- If a mandatory blocker is discovered, report its exact predicate and effect; **do not invent substitute infrastructure** or expand into unrelated reverse engineering.

## Documentation and handoff

**Do not create another research dossier, lead register or procedural history.** Edit the existing SRR-017 run card and the minimum existing authoritative SRR-017 documentation needed to state the current procedure, source/work identity and scientific limitations. Mark obsolete admission instructions as superseded where needed; don't narrate the correction history. The committed research documentation must not depend on `.local-work/` evidence files. Keep detailed independent review under `.local-work/independent-review/` (singular); summarize only material findings in the existing dossier. The repository-wide documentation consolidation is a **separate later task**.

Return: the exact simple command; focused task-only diff; test results, with source identity and limits; concise independent review; and a short explanation of any genuine remaining blocker. **Leave all changes unstaged, uncommitted and unpushed.**

**Authorization boundary:** This brief allows implementation, offline fixtures and review only. After accepting and committing the correction, the maintainer will launch Starfield and explicitly instruct Codex to execute the live extraction. That instruction is the live-operation authorization. Do not open the live game process while implementing this brief.
