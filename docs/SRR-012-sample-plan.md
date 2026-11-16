# SRR-012 sample plan and slot evidence

Use four components across two base-game bodies. Kreet's three components
test multiple BIOM targets under one planet key, including a sparse Common
family and a nonzero Everywhere slot. Decaran VII-b is a different planet
key with its own BIOM and a populated Special slot. Helium-3 is atmospheric
on Kreet in the accepted inputs and a terrestrial Special selection on
Decaran VII-b. These four identities yield distinct seven-slot vectors.
Confidence in the layout and native predicates is **PROVEN STATIC** on the
[pinned retail image](PROVENANCE.md#current-retail-identity). Confidence in
the expected vectors is **STRONG** under the stated input and native-path
conditions. The vectors are offline predictions for future measurements.

## Eligibility and identity

The allocator's collector uses the nonzero PNDT generation key at +0x54
to find the context-owned edge range. On the authored PPBD path
`FUN_14076EC00` writes the PNDT FormID at `0x14076EC81–0x14076EC86` and
submits owner FormID and BIOM target at `0x14076F340–0x14076F360`.
The selector payload begins at the edge's +0x20. Read the BIOM FormID at
payload +0x40 and match it both to the logical target and to the typed
BIOM record. Read the optional RSGD reference at payload +0x4C. The PPBD
path reads that word at `0x14076EF56–0x14076EF65` and remaps the FormID
where necessary at `0x14076EFB1–0x14076EFF5`. The native lookup at
`0x14077790D–0x140777923` accepts only a resolved type-0xAB record.
The native BIOM gate at `0x1407778F0–0x14077792B` requires type 0xA0 for
per-biome selection. The Everywhere pass independently applies the BIOM
gate at `0x140779B32–0x140779B48`. The constructor's PNDT callback
tests type 0xBA before reaching the collector. See
[SRR-003](SRR-003-retail-allocator-invocation-and-dispatch.md#native-path-and-predicates)
and [SRR-011](SRR-011-planetary-allocation-execution-and-result-lifecycle.md#result).

Compare normalized master/FormID and record type, editor ID when
available, the PNDT's runtime key and seed, the verified BIOM edge and
field identity, and the expected raw override under the current form
mapping. The Kreet frozen BIOM expects no PPBD override, with an
authored no-override value of zero. Its BIOM RSGD is resolved through
the BIOM list. The other three rows require the listed override at
+0x4C and the matching referenced type. For an exact vector comparison
also establish equivalence of the effective input pack, including
the ordered PNDT work set before shuffle, BIOM-side lists, RSGD
entries, IRES hierarchy and ATMO inputs. A matching executable, record
name or ID does not attest to unchanged inputs. Use an attributable,
qualified offline load-order/input manifest and the authoritative
runtime identity and edge checks in the contract. A later CSV or override
path must be qualified by its observed input equivalence. Missing or
unresolved effective inputs, ambiguous record identities, unexplained
extra edge entries and missing eligible components prevent a qualified
negative. Record proven identity and eligibility separately from whether
the exact prediction is applicable.

## Native slot checks

All seven fields are unsigned little-endian 32-bit FormIDs relative to the
**payload**. Their offsets are fixed across the inspected BIOM categories.
A slot's numerical category and whether an ID occupies the slot are distinct
from biome type, selection order and planet-wide membership.

| Offset | Meaning and admission | Pinned retail evidence |
| --- | --- | --- |
| +0x50 | Common family root. Zero after a normal selector miss or a fallback that cannot supply a configuration. A fallback may reuse a family rooted outside this BIOM's local candidate entries. | Type/category-0 selector call `0x1407779A4`; new store `0x1407779FC`; no result `0x140777AEF`; normal reuse `0x140777AD1–0x140777AEA`; guarded reuse `0x140777B7E–0x140777B96`. |
| +0x54, +0x58, +0x5C, +0x60 | Uncommon, Rare, Exotic, Unique within the assigned Common family. Each slot is independently vacant or emitted. A sparse vector may have later emissions after holes. A structurally selected intermediary may participate in the IRES traversal without being emitted. | Rarity argument 1–4 at `0x140777A26–0x140777A5D`; cap at `0x1407780E6`; slot indexed by rarity and initialized at `0x140778123`; candidate scan `0x140778154–0x14077816C`; inclusion branch and indexed store `0x1407781EC–0x1407781F9`. Cache and fallback copy the full five-word configuration. |
| +0x64 | Special category 5. The selector runs before the two Common guards. Both selector result pointers and shared count below eight are required for the write. | `0x140777949–0x140777971`; Common guard comparisons `0x140777986–0x140777993`. |
| +0x68 | Everywhere category 6. The pre-pass uses the first nonzero category-6 result in native BIOM list and entry order, with no weight draw. | BIOM +0x308/+0x310 list at `0x140779B4E–0x140779B67`; 0x238-byte entry walk and store `0x140779B70–0x140779BCE`. |

The PPBD, ENAM-associated and CSV input-building paths initialize
these result words to zero. The allocator clears them again and then
performs multiple conditional stores. The seven-slot copy can preserve
both cleared and populated states. A seven-nonzero requirement
would reject all four selected results. The BIOM/RSGD inputs,
zero-initialized fields, copy-out results and temporary family/shared-ID
state must be checked at their native locations. The atmosphere contributes
to shared occupancy and can affect output, but there is no atmosphere
slot in this vector. Check the selected slot categories and FormID
identities against the IRES dictionary and validate Common descendants
against the allowed structural path or the verified cached configuration.
Do not infer the descendant path from emitted words alone. In a matched
input pack, require the whole expected vector for the primary positive
test. An unexpected but plausible vector is indeterminate pending
input or native-rule reconciliation. A stable all-zero vector is a
negative candidate only if at least one output is expected under the
validated eligibility and complete coverage contract. This is scoped to
the retained state at the checkpoint. A clear-before-write interval or a
newly reconstructed object can give a genuine zero vector after an
earlier allocation. See [SRR-011 storage and clears](SRR-011-planetary-allocation-execution-and-result-lifecycle.md#result)
and [the reader](SRR-011-planetary-allocation-execution-and-result-lifecycle.md#readers-and-reuse).

### Retail and reference-model boundary

The accepted model uses the single effective PNDT-over-BIOM RSGD for
ordinary weighting, Everywhere discovery and the candidate description
for Common fallback. The retail mapping requires separate native checks
at these boundaries. The category-5 and category-0 selector scans the
optional PNDT record first, then scans the BIOM list when both result
pointers are still zero. The fallback scan receives the same roll and
cumulative pointer initialized earlier in the call. The category-6
pre-pass uses the BIOM list directly and stops on the first nonzero
category-6 ID. The guarded Common fallback also receives BIOM +0x308.
These are scoped retail observations. This task retains the validated
reproducer and its Creation Kit-derived contract as they stand. The four
sample predictions do not depend on these differing list paths given
the input conditions below. A wider sample plan needs a new applicability
check at each of these boundaries. See `0x140777E60`, `0x140777E90–0x140777E98`,
`0x140777F25–0x140777F34`, `0x140777F67–0x140777FAD`,
`0x140777FF0–0x14077807F`, `0x140777B22–0x140777B31` and
[SRR-002 retail mapping](SRR-002-retail-static-reconnaissance.md#retail-mapping-on-the-pinned-image).

## Fixed samples and controls

All IDs in the table are from `Starfield.esm` in the pinned reproducer
extracts. The order of values is Common root, Uncommon, Rare, Exotic,
Unique, Special, Everywhere. Each `0` denotes `00000000`.

| Body, PNDT and seed | Biome index, BIOM and EDID | PNDT override and BIOM RSGD | Expected slots | Selection rationale |
| --- | --- | --- | --- | --- |
| Kreet `0003F59F`, 2842708811 | 0 · `000D9BAC` · `FrozenLifeKreet` | None · `000083F0` | `[000057EA, 0, 0, 000057E9, 0, 0, 000083EC]` | Primary positive. Argon, Neon and Water test a root, a sparse descendant and the earlier Everywhere pass. |
| Kreet `0003F59F`, 2842708811 | 1 · `0023C0CE` · `MountainsLifeKreet` | `00244CCB` · `00007EDD` | `[000057C7, 000057C9, 0, 0, 0, 0, 0]` | Iron and Alkanes test the other biome key and a guaranteed Common override draw, with no category-6 entry. |
| Kreet `0003F59F`, 2842708811 | 2 · `002C9985` · `VolcanicRoughLifeKreet` | `00244CCC` · `000083EA` | `[000057C1, 000057C3, 0, 0, 0, 0, 0]` | Lead and Silver distinguish the second override from the Mountains override and from the BIOM-side uranium/lead ordering. |
| Decaran VII-b `0005DF7F`, 1633829920 | 0 · `000C5717` · `CrateredNoLife11` | `0018CE00` · `000083E0` | `[000057EB, 000057EC, 0, 0, 00005DF8, 000057F5, 0]` | Cross-planet control. Uranium, Iridium, Vytinium and Helium-3 distinguish owner routing, a sparse family and an actual Special slot. |

The Kreet seed gives shuffle order 2, 0, 1. For the two overrides,
the Common weight is 100%, so the reproduced rolls select the override
roots without a BIOM retry. Both source paths give no Special or
Everywhere for those biomes. The frozen BIOM has one category-6 Water,
no Special candidates and its Common selection uses the BIOM list.
Helium-3 `000057F5` is atmospheric input on Kreet. For the Decaran
VII-b override, the Common and Special weights are each 100%, there
is no category-6 entry on either path and the ATMO extract has no
inorganic entry for that body. The reproduced paths do not hit the
Common guards. The CK live Kreet trace anchors the shuffle and the
empty-candidate draws. Reproducer regressions support the final
terrestrial membership for both planets. Planet-wide validation alone
does not establish their exact seven-slot vectors. See
[CK trace findings](experiments/x64dbg-runtime-generation-findings.md)
and [pinned worked-case tests][worked-tests].

The native collector starts in sorted edge-key order before shuffling.
The BIOM key order `000D9BAC < 0023C0CE < 002C9985` agrees with
Kreet's authored PPBD order and the model input order. Decaran is a
singleton. Require the observed full key order and cardinality to agree
with the admitted profile. A different native input order can change
the expected vectors even if the set of biome keys agrees.

Use Decaran VII-b as the comparison control for each Kreet component and
Kreet's frozen BIOM as the comparison control for Decaran VII-b.
For a mismatched-key fixture, request Kreet's frozen BIOM under the
Decaran VII-b PNDT. The accepted input lists give no such pairing.
A returned and accepted component for that artificial request fails
identity validation. A missing edge for that request tests reader
behavior without qualifying scientific absence. The set includes all
three modeled Kreet PPBD biomes and the single modeled Decaran VII-b
PPBD biome, conditional on independently verified live edge coverage.
Any valid negative applies to these component identities and the
checkpoint only. A positive in an expected sparse component retains
its per-key coverage if a different non-control sample has unexpected
slots, provided shared admission and coverage still pass. For the
whole four-sample view, qualify a negative only when all four qualify.

## Offline reproduction

Use the [pinned reproducer tree][reproducer] at
`a8ff1c788bca415f571f06769ab3e712fa674f75`. These are Git blob IDs for
the input packs and generation source.

| Path | Blob |
| --- | --- |
| `data/planet-resource-generation.csv` | `418492f44c9b1c2b5d70d57c8e6a93d4cbdd22f1` |
| `data/ires-hierarchy.csv` | `25bba09fb205d32b392e179e92fc77fdf0db3c36` |
| `data/planet-atmospheric-resources.csv` | `d7a204a8ad23dc12c826952eac7d44b4de5ca8d5` |
| `data/planet-directory.csv` | `7eb7a9dcc8d76220daf35c9683af885f299cc0d0` |
| `src/starfield_resource_reproducer/generation.py` | `3dfedb5d4450bd4b996ddfd09266e1f9812df1c0` |
| `tests/test_worked_case_validation.py` | `a5b73f92c121b7bde048aa28f4d9ace1ae6098fd` |

An independent read of the installed base master,
SHA-256 `1dabed00c3f4282dd3bb54d2e9601e40b577d8742d078b7ccef203adbfef0da7`
before and after, verified the two authored RSCS seeds, the ordered
PPBD BIOM and override keys and exactly one authored BIOM RNAM per
selected BIOM, with the values above. It also confirmed the referenced
RSGD records. This corroborates the base definitions and leaves plugin
overrides and the selected process's effective inputs open. To reproduce,
use the [pinned sibling ESM reader][esm-reader] (blob
`391dd8fb007b8ed8ceff48fce2f6ba97a61bd618`) in its own checkout.
With its directory on `PYTHONPATH`, import `esm_records` from
`inspect_outpost_definitions` and call
`esm_records(esm_path, {b"PNDT", b"BIOM", b"RSGD"}, repeated=True)`.
Filter by the table IDs before inspecting the records. Compare the
ordered PPBD prefixes (`<IfII`, BIOM ID, coverage, per-biome seed,
override ID), the PNDT RSCS seeds and each BIOM's ordered list of
four-byte RNAM references. Use the parser only as a reader and retain
only the field-level verification. No raw records are needed.

From the research checkout, re-decode the focal functions using the
[hash-enforcing PE reader](../tools/srr011/inspect_pe.py), the matching
file as offline data and an interpreter with Capstone installed.
The command reads the image and prints bounded disassembly to stdout.
It requires no game process or Ghidra project. The optional local
native listing is `.local-work/codex/SRR-012/sample-native.txt`,
SHA-256 `0a9ce69f88c51a8776b7b1a6fa79dcf8c6c5e3bb29b1f3d2d55d4ab4fc257b71`.

```powershell
& $srrPython -B tools/srr011/inspect_pe.py $srrExe functions 140777870 140777e30 140777ff0 1407780b0 140779760 14076ec00 142340AB0
```

Inspect the branches at the locators above. The PE reader's exception
ranges can end at a native continuation, so use `window` at a known
instruction boundary if a range ends early. Then use the pinned
reproducer worktree directly with Python and bytecode writes disabled.
Set `$srrReproducer` to that checkout and confirm `HEAD` and cleanliness
before running. The example reads the four CSV inputs and prints
only selected fixture results. The generation path does not load
the canonical oracle. The category-6 projection below uses the BIOM
RSGD from the accepted extract after the separate retail-path check.

```powershell
$env:PYTHONPATH = Join-Path $srrReproducer src
Push-Location $srrReproducer
try {
@'
from pathlib import Path
from starfield_resource_reproducer.domain import FormId, GenerationRarity
from starfield_resource_reproducer.generation import generate_planet
from starfield_resource_reproducer.load_data import load_production_data

data = load_production_data(Path("data"))
expected = {
    "0003F59F": {
        "000D9BAC": (0x57EA, 0, 0, 0x57E9, 0, 0, 0x83EC),
        "0023C0CE": (0x57C7, 0x57C9, 0, 0, 0, 0, 0),
        "002C9985": (0x57C1, 0x57C3, 0, 0, 0, 0, 0),
    },
    "0005DF7F": {
        "000C5717": (0x57EB, 0x57EC, 0, 0, 0x5DF8, 0x57F5, 0),
    },
}

def form_id(resource):
    return resource.form_id.numeric if resource is not None else 0

for owner, expected_components in expected.items():
    key = FormId(owner)
    atmosphere = data.atmospheric_resources.get(key, ())
    result = generate_planet(data.planets[key], data.ires_nodes,
                             atmospheric_records=atmosphere)
    actual = {}
    for row in result.biome_results:
        biome = row.orchestration.biome
        assert row.common_assignment.guard_reason is None
        family = row.common_assignment.family
        assert family is not None and len(family.levels) == 4
        assert biome.biom_rsgd is not None
        category6 = next(
            (entry.resource for entry in biome.biom_rsgd.entries
             if entry.resource_rarity is GenerationRarity.EVERYWHERE),
            None,
        )
        vector = (
            form_id(family.root),
            *(form_id(level.selected_candidate) if level.emitted else 0
              for level in family.levels),
            form_id(row.orchestration.special_selection),
            form_id(category6),
        )
        assert str(biome.form_id) not in actual
        actual[str(biome.form_id)] = vector
        print(owner, biome.form_id, *(f"{word:08X}" for word in vector))
    assert actual == expected_components
'@ | & $srrPython -B -
} finally {
    Pop-Location
}
```

For a disposable read-validation fixture, encode a vector as seven
little-endian words at payload +0x50 with the independently labeled
PNDT edge and BIOM fields. Include the exact sparse Kreet positive,
its stable all-zero counterpart with validated eligibility, Decaran
VII-b's populated Special control, the wrong owner/BIOM pairing,
an unstable collection, and an ineligible all-zero component. Vary
identity and completeness independently of vector values. The
[measurement contract](SRR-012-measurement-contract.md) governs outcomes.

## Sample lead dispositions

| Lead | Disposition and evidence |
| --- | --- |
| B01 · Authored inputs versus result words | **Resolved.** Native PPBD, ENAM-associated and CSV builders initialize the result words; allocator clears and conditionally writes; typed copy preserves them. Locator anchors in [eligibility](#eligibility-and-identity) and [native slot checks](#native-slot-checks). |
| B02 · Fixed size versus required occupancy | **Resolved.** Fixed offsets and rarity-indexed write. Sparse results and conditions that leave Special and Everywhere vacant rule out dense-slot validation. A candidate can be structurally selected without a slot write. |
| B03 · Planet, BIOM and control coverage | **Resolved offline.** Stable four-key input set, modeled vectors and wrong-owner control are fixed. Full live range enumeration and one matching component per pair are admission checks. |
| B04 · Native source precedence and pre-pass differences | **Resolved for the chosen samples.** Native BIOM-list and optional-PNDT semantics compared against separate export columns. These samples bypass the differing outcomes under the matched inputs. Wider equivalence is outside their scope. |
| B05 · Live input-pack equivalence and lifecycle | **Blocked for retail measurement.** Offline CSV and native evidence supply conditional values. They cannot prove the selected process's resolved inputs, state, object lifetime or consistency. A qualified future inspector and authenticated live input/process evidence at each authorized checkpoint are required. |
| B06 · Entire-galaxy negative | **Excluded for this design.** The four identities are eligible controls across two owners. No evidence grants them representative coverage over other owners or earlier intervals. |

[reproducer]: https://github.com/gooberpede/starfield-resource-reproducer/tree/a8ff1c788bca415f571f06769ab3e712fa674f75
[worked-tests]: https://github.com/gooberpede/starfield-resource-reproducer/blob/a8ff1c788bca415f571f06769ab3e712fa674f75/tests/test_worked_case_validation.py
[esm-reader]: https://github.com/gooberpede/starfield-outpost-research/blob/d116bc63ff394b0156539161c8d1addfc902665a/save-analysis/scripts/inspect_outpost_definitions.py
