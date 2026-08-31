# Codex Mini-Brief — Precision Corrections Before Commit

Repository:

```text
gooberpede/starfield-resource-research
```

## Purpose

Make a small precision pass over the documentation reconciliation completed in the previous brief.

Do **not** reopen the broader reconciliation.
Do **not** begin new Ghidra analysis.
Do **not** rewrite sections that are already correct merely for style.

The goal is to tighten a few claims so the repository does not overstate what has actually been proven, and to add an explicit text-encoding / mojibake safeguard.

After making these corrections, stop and report the diff. Do not commit or push.

---

## 1. SurveyAggregator / `planet-all-resources.csv` — soften the semantic claim

The current documentation now correctly says that `planet-all-resources.csv` is not a complete oracle for every planetary inorganic resource because atmospheric resources may be absent.

However, some wording goes too far in the opposite direction by treating SurveyAggregator / `planet-all-resources.csv` as if it were **proven** to represent exactly the CK/biome-generation-visible channel.

That exact semantic contract has **not** been proven.

### Required wording direction

Use language along these lines:

> `planet-all-resources.csv` remains a valuable empirical oracle/proxy for the resource set exposed by the existing SurveyAggregator-based extraction and appears to correspond closely to the CK/biome-visible resource set. Its exact semantic contract remains unresolved.

or:

> Current evidence suggests that `planet-all-resources.csv` is useful for reconciling the CK/biome-generation-visible channel, but this correspondence should not be treated as a proven engine contract.

The important points are:

- **PROVEN:** the dataset omits at least some atmosphere-derived resources.
- **PROVEN:** it remains useful and must still be reconciled independently.
- **STRONG / PROVISIONAL:** it appears to correspond to the CK/biome-visible resource channel.
- **OPEN:** the exact semantics of SurveyAggregator and exactly what upstream state it exposes.

### Places to review

At minimum check:

```text
AGENTS.md
README.md
docs/known-facts.md
docs/hypotheses.md
docs/function-register.md
docs/experiments/x64dbg-runtime-generation-findings.md
```

Do not leave an unqualified statement in `known-facts.md` that SurveyAggregator *is* the CK/biome-visible channel.

### Preserve the validation rule

Keep the important provenance rule:

```text
atmospheric Chlorine
```

must not be allowed to satisfy or hide an independent biome-generation Chlorine mismatch.

That part of the previous reconciliation is correct.

---

## 2. Five-family guard — distinguish the proven comparison from its semantics

The x64dbg trace directly observed:

```text
0x1415DD0D3  cmp dword ptr [rsi], 5
0x1415DD0D6  jae ...
```

The repository should preserve that as **PROVEN**.

What is not yet fully proven is the broad semantic description of the structure/count as a universal:

```text
five generated Common-family configurations per planet
```

### Required wording direction

Prefer something like:

> **PROVEN:** the generation path contains a `count >= 5` guard on the structure associated with generated/cached Common-family configurations.

Then separately:

> **PROVISIONAL:** the most likely semantic interpretation is a five-family / five-generated-family-configuration limit, but the exact general role of that structure has not yet been independently established.

Do not phrase the semantic interpretation itself as fully proven merely because the numeric comparison is proven.

### Places to review

Especially:

```text
docs/known-facts.md
docs/function-register.md
docs/experiments/x64dbg-runtime-generation-findings.md
README.md
AGENTS.md
```

if the guard is summarized there.

---

## 3. `FUN_1415DCFB0` / `FUN_14157F120` — clarify execution context

The live traces were taken in the **Creation Kit Galaxy View Apply** path.

Do not casually describe these functions as proven functions in the retail `Starfield.exe` runtime unless the repository has separate evidence establishing that identity.

The word “runtime” may still be used in the generic sense of:

```text
observed executing live
```

but the source/execution context must remain explicit.

### Required wording direction

For function-register entries, use a source context such as:

```text
Creation Kit / Galaxy View Apply
```

or:

```text
Creation Kit executable, live Galaxy View Apply path
```

Then state that these functions implement the live-traced resource-generation path used by the CK operation and that the reconstructed behaviour agrees with known game/resource results.

Avoid wording that implies:

```text
we directly traced these exact addresses in Starfield.exe
```

unless such evidence already exists independently in the repository.

### Preserve the core status

These remain:

- `FUN_1415DCFB0` — **PROVEN primary per-biome generator in the live-traced CK generation path**
- `FUN_14157F120` — **PROVEN descendant helper in that path**

This correction is about executable/context attribution, not about weakening the observed algorithmic evidence.

---

## 4. Add an explicit anti-mojibake / encoding rule to `AGENTS.md`

Add a short repository-text rule under an appropriate documentation or repository-policy section.

The purpose is to prevent Codex or scripts from introducing mojibake such as:

```text
ÔÇö
ÔåÆ
├ö├Ç├ö
```

when UTF-8 punctuation, arrows, or box-drawing characters are transcoded incorrectly.

### Required rule

Use wording substantially like:

> **Preserve UTF-8 text encoding.** Do not introduce mojibake or replace valid Unicode punctuation/diagram characters with mis-decoded byte sequences. Before finalising documentation changes, inspect modified text for common mojibake patterns (for example `Ã`, `Â`, `ÔÇ`, `â€`, or corrupted box-drawing/arrows). If the surrounding repository already uses valid Unicode characters such as em dashes, arrows, multiplication signs, or box-drawing characters, preserve them as valid UTF-8 rather than transliterating or re-encoding them.

Also add:

> If a diff/export display appears mojibaked but the repository file itself is valid UTF-8, do not “fix” the source file based only on the broken display. Verify the actual file bytes/text first.

This is important because the previous exported diff appeared to contain mojibake even though the repository files may have been correct.

Do **not** replace all Unicode with ASCII merely to avoid this issue.

---

## 5. Data and implementation-brief directories

The following repository additions are intentional and should be treated as normal tracked project content:

```text
data/
docs/implementation-briefs/
```

The CSVs in `data/` are the same three datasets used by the standalone reproducer and are intentionally present so future Codex sessions have the referenced evidence locally.

The implementation brief in:

```text
docs/implementation-briefs/
```

is also intentionally tracked as research/workflow provenance.

Do not remove, ignore, or relocate these files as part of this correction pass.

No need to add their large CSV contents to the response diff unless ordinary Git output naturally includes them; a summary/status entry is sufficient.

---

## 6. Scope guard

Do not alter the following unless needed to implement the corrections above:

- the established RSCS → MT19937 finding;
- the two distinct bounded RNG mechanisms;
- PNDT RSGD override precedence;
- Common/root weighted selection;
- IRES child-resource graph;
- unconditional root insertion;
- family caching;
- descendant structural continuation;
- zero-candidate RNG consumption;
- the proven `>= 8` descendant early return;
- ATMO REFL/RFDP/RDIF inheritance findings;
- atmospheric extraction counts;
- Maal VIII atmospheric-capacity interpretation;
- provenance-aware validation architecture;
- the superseded/deprioritised status of the old leveled-list trail;
- the documented next Ghidra question.

This is a precision correction, not a second full rewrite.

---

## 7. Verification

After edits:

1. run `git diff --check`;
2. inspect modified Markdown files for likely mojibake sequences, including at least:

```text
Ã
Â
ÔÇ
â€
```

and any visibly corrupted arrow/box-drawing sequences;

3. confirm that valid UTF-8 arrows, em dashes, multiplication signs, and box-drawing characters remain intact where intentionally used;
4. scan for stale overclaims such as:
   - SurveyAggregator **is** the CK/biome resource channel;
   - the five-family semantic interpretation is fully proven;
   - `FUN_1415DCFB0` / `FUN_14157F120` were directly traced in retail `Starfield.exe` if that is not independently established.

---

## 8. Deliverables

Stop after the correction pass and report:

- files changed;
- concise description of each correction;
- any ambiguity encountered;
- result of `git diff --check`;
- result of the mojibake scan;
- `git diff --stat`;
- `git status --short`.

Do not commit.
Do not push.
Do not begin the next Ghidra investigation.
