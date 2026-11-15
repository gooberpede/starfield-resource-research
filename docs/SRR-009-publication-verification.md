# SRR-009 publication dependency inventory

The [Stage A finding](SRR-009-retail-debugger-admission-and-stage-a.md#finding)
is a **custody-backed historical observation**. The tracked synthetic and
offline methods below have a **reproducible method** route. Actual retail
invocation outside the qualified windows, the relation to gameplay and
normal observer retirement remain **provisional/unresolved claims**. They
would require appropriately scoped runtime evidence or, for retirement,
a terminal observer record. These labels describe verification routes.

## Material dependencies and disposition

In the table, a version or SHA-256 identifies the source or input family.
Exact local input and evidence identities remain in the private manifests
where filenames, paths or records are sensitive.

| Procedure or claim | Source and identity | Role and clean checkout | Rights, action and verification |
| --- | --- | --- | --- |
| [SRR-001 identity and focused CK evidence](SRR-001-executable-identity.md#release-scope) | [Provenance pins](PROVENANCE.md), tracked CK metadata and [pre-biome bundle](experiments/evidence/pre-biome-resource-state/), reproducer v1.0.0 for the model validation | Reusable evidence is tracked. Matching Steam PE, x64 tooling and any analyzed Ghidra program are lawful external inputs. The About capture and exact host receipts are custody-only. | Follow the tracked bundle and executable identity method. The About capture, full traces and CK binaries remain outside publication. |
| [SRR-002/003 static mapping, selector and dispatch](SRR-003-retail-allocator-invocation-and-dispatch.md#reproduction-publication-and-next-experiment) | Pinned retail 1.16.244.0 PE, Ghidra 12.1.2 PUBLIC, [explicit-address exporter](../ghidra/README.md), Capstone 5.0.7 for the recorded analysis. Exact scans used SRR-002 `scan.py` and `identity.tsv`, SRR-003 `inspect_pe.py`, and outpost `OutpostRecon.java` at `d116bc63ff394b0156539161c8d1addfc902665a`. | Tracked exporter and documented matching-PE walk verify focal claims. Export products are generated. The exact local census and sibling commands are custody-only. | Review the focal edges and exception metadata on a lawfully obtained image. The clean-snapshot PE self-test checked bounded call edges, RTTI-adjacent dispatch slots and unwind metadata. Native listings and analyzed Ghidra state stay local. |
| SRR-004 editorial diagrams and registers | Mermaid source in the [SRR-002](SRR-002-retail-static-reconnaissance.md) and [SRR-003](SRR-003-retail-allocator-invocation-and-dispatch.md) dossiers. [SRR-004 review](research-workflow.md#srr-004-editorial-review) identifies its reviewed snapshot. | Tracked diagrams can be rendered with Mermaid. Original VS Code/Chrome render artifacts and tool-specific command receipts are custody-only. | Keep the diagrams as authored source. Exact historic render bytes are outside the current method. |
| [SRR-005 causal sites and Save2 menu check](SRR-005-live-observation-preparation.md) | Pinned retail locators. Earlier `check-sites.py` reused the SRR-002 parser and identity export. `test-correlation.py`, `build-fixture.cmd` and the HIST-0245 menu receipt are retained locally. | Current PE self-test and [SRR-006 synthetic controls](SRR-006-four-site-hardware-observer.md#reproduce-the-fixture-controls) use tracked source. Earlier scripts and exact menu records are custody-only. | Keep save bytes and private records out of publication. The optional private HIST-0245 retention copy does not establish live loading or gameplay behavior. |
| [SRR-006/007/009 observer fixtures and admission](SRR-006-four-site-hardware-observer.md#reproduce-the-fixture-controls) | Tracked `tools/srr006/` source, x64 MSVC 14.51.36231 and SDK 10.0.26100.0, CPython 3.14.3, pinned lawful retail file, matching native Windows runtime. Observer marker imports the tracked qualification helper. | Source, build and fixture methods are supported from the candidate tracked tree. Executables, objects and receipts are rebuildable outputs. Frozen candidate binaries and exact run journals are custody-only. | Do not distribute executable or runtime bytes. The observer and sites were unchanged by this remediation. Verification uses disposable test children only. |
| [SRR-008 survey](SRR-008-retail-title-time-environment-survey.md#current-protection-and-environment-checks) | Tracked [disposable inventory](../tools/srr008/inventory.py), promoted from original `inventory.py` SHA-256 `7cbdbfad27d10faa1cc0d3fb4113f3ee910b65da9ee8f5af363a942d768415f4`. Source pattern from outpost `research/q-branch-030-procedure/environment.py`, SHA-256 `0bd379190ef6bbfaf39323b340c9b3fb6f5a98731b1f88408fad98d6890f6180`. | Tracked reusable source and native Tool Help prerequisite. Interactive controller `survey.py`, logs, module snapshots and exact live receipts are custody-only. | Preserve tool attribution and the 146-module historical evidence. The checked fixture sampled only its own child and rejected a wrong epoch. |
| SRR-008/009 protection and on-disk environment | Tracked [preflight tool](../tools/srr008/README.md), including [GPL classifier provenance](../THIRD_PARTY_NOTICES.md#srr-008-save-policy-and-inventory-tooling). Historic checker `check-saves.py` SHA-256 `44f6aa6c5dbaefa81916dbec2512cbe3110a8d0ebcc50ebdebc12a50c364cceb`; `environment.ps1` SHA-256 `80d664be39e57644c586a4668783ae19bf83ef46a5c169eb17f84e860622b4e7`. | Tracked code has no sibling import. Private config, the pinned policy and independent backings are supplied explicitly. The old `preflight.json`, helper chain and historical receipts remain custody-only. | On-disk checks preserve the protection semantics and expose failure fields. The selected Documents Data junction needs an explicit target for the SFSE inventory. Account, process state, URI handler and NVIDIA overlay remain separate live gates. |
| SRR-009 retail observations, audit and closure | [Dossier](SRR-009-retail-debugger-admission-and-stage-a.md), [brief summary](implementation-briefs/README.md#srr-009-stage-a), [audit index](audits/README.md), exact STOP and closure pins in the dossier. | Tracked summaries reference private historical custody. Exact authorization texts, attribution logs, reviews and manifests were retained locally. | Neither audit archives nor public patch include private capture or save bytes. No new live operation is implied by the documented method. |

## Offline verification

The candidate source was reconstructed from Git HEAD and the task files,
with no ignored files in the resulting source tree. CPython 3.14.3 x64,
MSVC 14.51.36231, SDK 10.0.26100.0 and the matching installed Windows
runtime were supplied. The lawful PE was used for data-only tests. Matching
SHA-256 values for the retail image and native runtime are in the
[Stage A dossier](SRR-009-retail-debugger-admission-and-stage-a.md#inputs-and-applicability).

| Check | Result |
| --- | --- |
| `python -E -B tools/srr008/test_preflight.py` | Ten synthetic controls passed, including same-size hash mismatch, missing backup, wrong designation, unknown entries, wrong policy version and namespace, shared file identity, output collision and ambiguous overlay settings. |
| `python -E -B tools/srr008/inventory.py <new-receipt>` | Two equal 15-module snapshots of a disposable Python child, wrong-epoch refusal and cooperative exit 0. The module count describes this fixture only. |
| [Observer build and focused tests](SRR-006-four-site-hardware-observer.md#reproduce-the-fixture-controls) | A fresh native build passed the correlation, window and retail profile checks. The [admission verifier](../tools/srr006/qualify_admission_diagnostics.py) checked 13 refusals and a retained prefix after injected write failure. |
| `tools/srr006/pin_pe.py <lawful-image> --self-test` under Python `-E -B` | Matched the tracked profile, including bounded retail call edges, sites, vtable slots and exception records. No Ghidra database was opened or modified. The exact SRR-002/003 sweeps were outside this run. |
| Observer disposable scenarios | Creation `baseline`, `quiet`, `callback-only`; attach `baseline`, `competing-breakpoint`; all nine staged scenarios. Other legacy scenarios and live controls were excluded. Use the published harnesses and fresh output directories. |
| Private before/after receipt reconciliation | The new reports matched all 98 Documents and 95 remote pair records, two designations, transient metadata, policy digest and recorded backup count against both the SRR-008 and SRR-009 receipts. The on-disk game and build pins, stored Cloud and overlay flags and cache hash matched the scoped historical observations. |
| Publication surface | Markdown links and archive payloads checked offline. Existing archive drive examples and checkout locators are historical context. Archive bytes were preserved. Loose SRR-009 briefs, real protection policy, private Save2 copy and all raw evidence remain outside the patch and tracked-tree release inputs. External URLs were not fetched. |

The private run record retains the exact command output, source and
protection receipts and the original audit manifest identities. Existing
third-party holds apply to installed game files, unpublished native
excerpts, account records and saves. The repository license covers
incorporated reusable code subject to its source-specific notices.
