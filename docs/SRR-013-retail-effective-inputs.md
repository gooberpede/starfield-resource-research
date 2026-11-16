# SRR-013 retail effective-input gate

**Blocked for retail classification.** The installed base master and six
pinned source blobs verify the offline predictions. No qualified witness
identifies the effective input pack of the process that would supply the
retained resource words. The controller refuses retail acquisition at the
input gate. For acquired disposable data with failed input admission, the
classifier keeps the seven structurally readable words with a conditional
comparison. The official verdict remains `STATE_INDETERMINATE` for either
an exact-looking tuple or an all-zero tuple under that gate. See the
[measurement contract](SRR-012-measurement-contract.md) and [sample plan](SRR-012-sample-plan.md).

## Verified offline

- The installed `Starfield.esm` matched the SRR-012 master SHA-256
  `1dabed00c3f4282dd3bb54d2e9601e40b577d8742d078b7ccef203adbfef0da7`.
  The pinned sibling generation, IRES, atmosphere and planet-directory CSVs,
  generator and worked-case test matched their six Git blob IDs.
- Direct installation `Data` contained 39 candidate plugin files and had no
  loose `Space/BiomeData.csv` at the inspected path. Configuration files were
  read only for identity. The inventory and configuration remain disk evidence.
  Installed files can be inactive or loaded implicitly. An archive or an
  alternate resource path can supply a CSV even when that loose path is absent.
- The repeated SRR-012 authored base check and extract projection cover the two
  PNDT seeds and ordered PPBD records, typed BIOM/RSGD links and four expected
  vectors. Kreet has Helium-3 atmospheric input. The matched extract has no
  Decaran VII-b inorganic atmosphere contribution. The retained layout
  measurements have no atmosphere output slot.
- The optional PNDT override is separate from the BIOM-side RSGD list. Retail
  may continue the same weight roll on the BIOM list and its Everywhere pre-pass
  uses that list directly. SRR-012 establishes applicability of its reference
  projection for these four samples under the matched inputs. Keep the native
  source paths independent when checking a changed input. [Native sample analysis](SRR-012-sample-plan.md#retail-and-reference-model-boundary)

## Missing independent witnesses

| Lead | Disposition and least intrusive discriminator |
| --- | --- |
| Actual plugin list, FormID namespace and winning records | **Blocked.** Capture the authoritative loaded plugin table, its full, medium and small FormID assignments and order from a qualified read-only source bound to the admitted epoch. Join its file identities to hashed source files and re-resolve the relevant winning records offline. Include implicit masters, Creations, and any relevant loose or archived overrides. The configured list and executable digest cannot distinguish dormant plugins, remapping or a different active order. No qualified table decoder or equivalent runtime witness has been established for this profile. |
| Ordered PNDT work set, seed, BIOM list and override | **Partly resolved.** The current decoder checks the complete ordered edge ranges for the two planet keys, PNDT +0x50/+0x54, typed FormID resolution, the singleton BIOM RSGD lists and component override words. Repeat those joins under the authenticated effective profile. A readable replacement record can preserve a FormID, type and seed while changing its data or provenance. [Acquisition evidence](SRR-012-acquisition-evidence.md#independent-form-identity) |
| RSGD contents and IRES dependencies | **Blocked.** Qualify the winning versions of all seven referenced RSGD forms, their ordered entries and binary32 weights, and the reachable IRES category/descendant graph including intermediaries and alternate selector candidates. Reconcile against the pinned extracts or a separately reviewed effective projection. The allocator can independently read the BIOM list even when a PPBD override exists. Compare runtime typed references and scope any further native reads to witnesses the source-file join leaves ambiguous. [Retail layout](SRR-002-retail-static-reconnaissance.md#retail-mapping-on-the-pinned-image) |
| Atmosphere resolution and inheritance | **Blocked.** Resolve the two winning PNDT/ATMO assignments and any RFDP/REFL/RDIF inheritance needed for their effective inorganic lists. The runtime planet-keyed lookup and ATMO list fields are mapped statically at `0x140779973` and ATMO `+0xF8/+0x100`. An independently reviewed bounded lookup would discriminate a changed runtime list if the winning-data join remains inconclusive. [Retail layout](SRR-002-retail-static-reconnaissance.md#retail-mapping-on-the-pinned-image) |
| `Space/BiomeData.csv` and other input substitution | **Blocked.** The optional constructor path can source replacement component inputs before allocation. At `0x14094E542`, the branch tests the global byte at `0x145EA6000` before the optional path with the CSV load call at `0x14094E608`. The address and predicate are **PROVEN STATIC**. A later single byte value or missing loose file cannot exclude a previous load. Need attributable loader/resource-resolution evidence or a qualified input-equivalence demonstration for any active substitution path. Reject an unresolved alternate source. [SRR-011 result lifecycle](SRR-011-planetary-allocation-execution-and-result-lifecycle.md#result) |
| Substitute the fixture or infer inputs from the retained tuple | **Excluded.** Fixture provenance is admitted only for the disposable profile. Runtime source proofs must originate independently of the result words. Decisive evidence would require the bounded joins above. |

The least intrusive next verification is an independently grounded loader
table and a winning-record comparison against the hashed files, combined
with the existing two-collection native checks. A future method must give
one epoch-bound result for both collections and refuse unresolved sources.
There is no game-process qualification in this continuation. The witness
gap requires reviewed implementation work before proposing live acquisition.

## Reproduce the disk check

```powershell
python -B tools/srr013/retail_inputs.py $installedStarfieldMaster $pinnedReproducer
```

Use the installed `Data/Starfield.esm` and the pinned sibling checkout named
in the [sample plan](SRR-012-sample-plan.md#offline-reproduction). The tool
reads the master, the named sibling files and a narrow `Data` inventory. It
prints disk identities and a structured gate disposition. It writes no files
and leaves the Ghidra project untouched. Capture output and any nominated
configuration identities privately under `.local-work/`. The sample plan
gives separate base-parser and prediction replay commands.
