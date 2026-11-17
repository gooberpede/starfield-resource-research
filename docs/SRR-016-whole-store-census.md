# SRR-016 whole-store allocation census and native-slot oracle

This investigation implements an offline route from an independently rooted
pair of whole-store reads to a typed allocation census and a separate
comparison against frozen inputs. Its measurement boundary is every
descriptor reachable through the authenticated `BSComponentDB2::DB +0x300`
mixed tree for the admitted read profile. A qualified empty tree reports
zero visited descriptors. A typed edge with a seven-zero vector remains
present.

The [interchange contract](SRR-016-interchange.md) defines the canonical
join. The [native reader](SRR-016-native.md) and [oracle](SRR-016-oracle.md)
dossiers give test commands, source pins and evidence custody. The [proposed
run card](SRR-016-title-census-run-card.md) requires separate written approval.
This phase uses offline data and owned test processes. The pinned retail
binary was read from disk for identity only.

## Starting state and controls

| Item | Identity or state |
| --- | --- |
| Research HEAD and local `origin/main` | `a06868f25a419939ce8d99f7b1b34de47b112d3a` |
| Research index | Empty staged diff. SHA-256 `7fc07f066aedc2094953ad68507de5848a1d48264fb7c43bf1396fc03d934911`. |
| Pre-existing worktree | Only the untracked SRR-016 brief. SHA-256 `0347407ad5166ea21dfc922556a7d735cb7ac230ee23071717219c579238929e`. |
| Reproducer | Clean local main at `a8ff1c788bca415f571f06769ab3e712fa674f75`, package 1.0.0. |
| Retail image | File version 1.16.244.0. SHA-256 `7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28`. |
| Test host | AMD64 CPython 3.14.3 (SHA-256 `cce21c0e8710e304273e98ac4b2b0f5aceb639acbcd2343cbaa5c4e81619c45b`), Git 2.53.0.windows.1, PowerShell 7.6.9. |
| Caller-available space at entry | C: 87,736,512,512 bytes. D: 68,670,197,760 bytes. |

Repository evidence and executable applicability follow the
[v1 baseline](v1-research-baseline.md), [SRR-012 acquisition evidence](SRR-012-acquisition-evidence.md),
[SRR-013 budget recovery](SRR-013-live-observation-budget-recovery.md),
[SRR-014 lifecycle](SRR-014-startup-allocation-component-database-lifecycle.md)
and [SRR-015 feasibility](SRR-015-retained-allocation-extraction-feasibility.md).
The installed executable hash identifies the native anchors. The fixture's
native-shaped graph and independent truth establish test coverage. Retail
compatibility requires its own admitted runtime evidence.

## Native operations and lead dispositions

| Capability | Direct caller or dispatch | Upstream operation and guard | Evidence and disposition |
| --- | --- | --- | --- |
| Publish embedded DB and register edge type | Pointer store at `0x1418993E3`, registry assignment at `0x14231D7D9–D7F1` | Startup publication, separate registration receiver | Retail SRR-013 witnessed publication and registration in the selected-key epoch. Census starts from these two independently checked anchors. |
| Submit typed value and insert inline edge | `FUN_140777290 → FUN_140774E00 → FUN_1407766B0` | PPBD and ENAM replacement or admitted CSV row, followed by queue service. Ticketed mutation at `0x140774E1C`. | Pinned static path allows duplicate-key insertion and storage movement. The originating command for individual title edges remains unresolved. |
| Erase owner range | `FUN_140774970 → FUN_142409490` | ENAM replacement or PNDT lifetime submission. Ticketed admission at `0x14077498C`. | Static caller and bounded eraser explain why repacking and removals matter. No epoch-wide exclusion or replacement completion follows from paired reads. |
| First-match copy | Verified lookup calls at `0x1407BAA7A`, `0x1407BD677` and `0x14086A798` reach `FUN_140771F30` | Caller holds shared mode and provides output buffer | Semantics define the key range and payload layout. External invocation lead exhausted. Whole-tree enumeration exposes duplicate edges that a first match can conceal. |
| Clear and write seven output lanes | `FUN_140779610 → FUN_140779760 → FUN_14077BCE0` reaches inline targets | Eligible PNDT callback, shared DB admission and resolved typed inputs | Static writer and clear locators. SRR-013 read the retained values, with no invocation attribution. Stable zeroes remain valid census values. |
| Resolve runtime forms | `FUN_1405DE3B0 → FUN_1405ACAD0` | Native lookup includes hash-chain and native-state behavior | External census reconstructs read semantics. Plugin-local namespace and winning input evidence require an independent witness. |
| A9 queue schedule and B8 key notification / possible separate-store mirror | Owner +0x40 service, or DB +0x38 notification and distinct +0x268 factory | Configured scheduler and service guards, or concrete subscriber with matching typed source | No new caller or discrepancy was required for this +0x300 census. A9 still lacks the epoch-qualified outstanding-work/entry join. B8 still lacks a concrete same-key subscriber/source/destination join. |

The native evidence supplies the detailed call sites and guards.
[SRR-014 database operations](SRR-014-database-evidence.md#operation-catalogue) ·
[SRR-015 native census design](SRR-015-native-extraction.md) ·
[SRR-015 lead register](SRR-015-lead-register.md)

The data-handler lead in SRR-012 independently enumerates a counted PNDT
bucket. It supplies neither resource/BIOM identity coverage nor the
runtime plugin assignments for canonical identities. The qualified FormID
lookup addresses the runtime object join. To close the separate canonical
join, qualify the loader's epoch-bound namespace table or an equivalent
independent witness. Expected-population closure additionally needs
winning ordered PPBD inputs, attributable ENAM and admitted CSV effects,
and evidence of which conditional routes constrain the declared scope.
[Independent form identity](SRR-012-acquisition-evidence.md#independent-form-identity) ·
[Effective inputs](SRR-013-retail-effective-inputs.md)

## Inherited verification and receipt custody

Run the legacy process-name tests serially. They rebuild and read an owned
disposable process and write private receipts under `.local-work/`.

```powershell
python -B tools/srr012/check_contract.py
python -B tools/srr013/qualify_budget.py SRR-016-baseline
```

The four SRR-012 contract tests and 49 original, 35 retail-shaped, 61
explicit-mode and 11 additional external legacy observations passed.
Four mode replay challenges passed alongside the existing work-cap and
seal-failure controls. The suite's freshly generated summary SHA-256 is
`ab1f72600b671c2e2ae5282e692f2c7322121adabb0bd62154b3f76f202ba1b3`.
The deterministic legacy fixture PE SHA-256 is
`975e3242c792823e7b7bc68e09effaa93b0e47f9fe12f6fc9e860750058950d0`
with MSVC toolset 14.51.36231 and Windows SDK 10.0.26100.0.
Use a fresh output name when rerunning.

A separate offline pass with the unchanged HEAD reader reproduced 305
historical owned receipts and refused 13 named negative controls across
three retained directories. Twenty additional positive receipts in the
preliminary `continuation-first` directory lack the Steam-log witness
required by the frozen reader. They stopped at identity validation and
replay then refused the remaining events. The final and integrated
qualification directories replayed 241 positive receipts.
All read receipt bytes were preserved. The historical replay inventory
had SHA-256
`2feda84b9418d9551707e5dd158b0938dd237d8cc9db09165c734163d44acbcc`.

The two historical retail receipt directories refused read access to this
account. This phase did not replay the initial v3 title attempt (four
`STATE_INDETERMINATE`, pin `82ab34550fca287e54155f28a9cf6e628587d5eb3bc212ac7289af7d512392dd`)
or the paired v4 attempt (four `STRUCTURALLY_POPULATED`, pin
`b4bbef36415776dd7582a5d3e419e8a2067ca9fcaa75844097824fec7ea3309c`).
The earlier offline checks used SRR-013 structural replay. The historical
reports give the verdicts, receipt identities and evidence limits.
[Initial attempt](SRR-013-retail-title-structural-observation.md) ·
[Paired attempt](SRR-013-retail-title-paired-structural-observation.md)

## Expected population and value scope

The pinned production corpus covers 3,210 modeled biome rows and 1,444
owners. Another 332 body-directory entries carry no terrestrial prediction.
In the initial freeze 3,191 modeled keys are available in the canonical join
namespace. Nineteen rows retain unresolved extractor identities. Of the
joinable rows, four are conditional `EXPECTED` controls, and 3,187 are
`UNKNOWN`. No evidence supports inferring exclusion from the directory
alone. The independent authored operations need source and winner evidence
even when they can be represented by the ledger.

The four projected Kreet and Decaran VII-b vectors match all positions of
the separately authored SRR-012 controls under the documented assumptions.
The reproduction reads the pinned production inputs and event stream before
any comparison. The canonical planet-wide validation suite checks the
unchanged model. Its historical ten-body CK and retail holdout had a different
validation grain and remains historical. [Fixed controls](SRR-012-sample-plan.md#fixed-samples-and-controls) ·
[Retail/model boundaries](SRR-015-oracle-comparison.md)

## Integrated offline verification

The final owned-profile suite passed 57 process controls with checked replay
of each, eight tampered or incomplete receipt refusals and one contradictory
remap preflight refusal. The corpus fixture reached 3,600 mixed descriptors
and 3,210 targets. The upper fixture reached 5,120 mixed descriptors and
4,096 targets. Its normalized observation, file SHA-256
`bf609cd82029fcab22a2bb404ff67f1a2c8372cdf35c46115595d27abbf8451e`,
went through the comparator with the independently frozen pinned ledger and
oracle. Structure qualified. The comparator counted 241 all-zero tuples and
zero comparable targets. Population and value decisions remained indeterminate
because the fixture inputs had no attested retail applicability.
The replay and comparison CLI outputs matched the retained integrated result.

The 28 oracle and comparator fixtures include qualified exact and scoped
comparisons, incomplete owners, key conflicts, slot-order differences and
provenance drift. The pinned sibling passed 183 tests including the canonical
1,444/1,444 exact check. The sibling required no patch. The recorded
integrated comparison had SHA-256 `7569d669ab1685cfca5e5e766205a91d08962314ec60d0fc26a0ff85e859414e`.

## Readiness by layer

| Layer | Disposition | Next evidence |
| --- | --- | --- |
| Whole-store acquisition | Disposable implementation and qualification. Retail release blocked. | Qualify an SRR-016-specific Steam admission and one-use checkpoint binding with the reviewed retail adapter, an independently justified envelope and a runtime-to-canonical identity witness. |
| Expected population | Conditional coverage of the four reference keys. | Resolve epoch-linked winning records, the full FormID namespace and the admitted PPBD, ENAM and CSV operation set. |
| Native-slot applicability | Four conditional vectors across two whole owners. | Verify effective ordered ATMO, BIOM, RSGD and PNDT inputs and native ordering, precision and cache semantics over each additional owner. |
| Combined comparison | Offline comparator with scoped decisions. | Provide an independently qualified retail pair and bound ledger/oracle when making any stronger comparison claim. |

The scope of the proposed first observation is reachable-store structure.
The population and value gates apply to their respective scientific
decisions. The proposed session remains blocked on reader release
prerequisites. [Proposed run card](SRR-016-title-census-run-card.md)

## Review and handoff

<!-- review-status:start -->
**COMPLETE for the reviewed offline scope.** The independent internal
challenger reproduced the owned qualification and oracle freeze, challenged
traversal and comparison with independently constructed fixtures, and
reviewed the proposed run card. Rework addressed BIOM list budget
enforcement, identity changes accompanying slot changes, and comparison
provenance refusals. Forward and reverse patch replay covered all 13 task
paths. Retail release remains blocked by the reader prerequisites above.

The reviewed offline implementation snapshot had source manifest SHA-256
`6891da4b1e3419b0afea6a30d40b871fd601c1f7285a1c11d8b6600f5692b20f`.
That historical manifest listed path hashes in sorted order and excluded
the review-status block. The independent rerun covered 57 process controls,
eight receipt challenges and one remap preflight refusal. The reviewer also
checked a separately packed direct block and multilevel tree, reproduced
the oracle freeze byte-for-byte, and verified that remap conflict or a
malformed comparison input preserves the qualified structural decision
without closing the affected comparison. The ending HEAD and index matched
their starting identities. The supplied brief was preserved outside the
implementation patch.
<!-- review-status:end -->

## Documentation portability correction

The audit covered every tracked path, including 88 Markdown files, source
comments and docstrings, and 23 members of the two documentation archives.
It also examined the five pending SRR-016 documents and seven implementation
files. It replaced historical artifact and review locations with recorded
outcomes, evidence identities or tracked methods. Current fixture examples
build their own inputs or replay receipts from a named fresh run. Output
and custody instructions still identify ignored working areas where needed.
The original review manifests identify their historical snapshots.

The seven accepted SRR-016 implementation files match the offline handoff
byte-for-byte. Historical conclusions, original review dispositions and the
retail release prerequisites above retain their scope.

<!-- portability-review:start -->
**COMPLETE for documentation portability.** The independent challenger
checked the full tracked inventory, archived documentation, source
comments and the pending SRR-016 material. The review confirmed that
remaining local-work references serve generated output, current custody,
fixture replay or historical policy. The seven accepted implementation
files, historical results and provenance pins were preserved. Both the
39-path cumulative patch and 29-path Markdown correction replayed
forward and backward byte-for-byte.

Reviewed content manifest SHA-256
`98c8138ac7f54f6304200e61bfd22af237ebd721c0ede56c19f80caa1cca0536`.
The manifest excludes only this marked portability review block.
<!-- portability-review:end -->
