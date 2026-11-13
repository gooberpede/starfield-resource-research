# SRR-002 — Retail planetary-resource allocation static reconnaissance

## Question and disposition

Which functions or connected regions in the pinned retail executable correspond
to CK planetary and per-biome inorganic resource allocation, and what can static
evidence establish about them? A connected implementation is present. Static
instructions establish the two prepopulation passes, the shuffled per-biome
call, and the per-biome Special, Common, descendant and fallback control flows
within the bounds below. Ordinary gameplay dispatch, effective form resolution
across plugin configurations, cache lifetime and full algorithmic equivalence
remain open. Landing-site raster masks and outpost geometry were out of scope.

## Executable, project and starting state

The installed executable and the separate analysis copy both reported product
and file version 1.16.244.0 and SHA-256
**7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28**.
Steam app 1716740 locally recorded build 23518663. The executable SHA identifies
the bytes, and the manifest records the installation build independently.

Ghidra 12.1.2 PUBLIC (Temurin 21.0.12+8) opened the existing local
Starfield project, program /Starfield.exe, domain file ID
c0a816bc892993545618675600. The saved program reported the same executable SHA
and MD5 0a73ecdc1d54b14a91818cddeb03aa9e, independently matched to the PE.
Ghidra and the PE header gave base 0x140000000. Ghidra reported language
x86:LE:64:default and compiler ID windows. This associates the saved program
with the pinned image at import. The original import path and analyzer history
were not established. Instruction addresses across all nine focal Ghidra bodies
matched a separate decode of the corresponding PE bytes. Critical branches,
operands, direct calls and referenced constants were checked on both sides.
Those tests qualify the relevant listing and leave the broader analysis state
unqualified.

Starting HEAD was c97381e46e5abc042f7d1334cd2dd28e151aefec, tree
e91e09575c60cf5861600a75705d05c2557e6af3, with empty staged and tracked diffs.
The supplied brief was already untracked and remained outside the patch. All
four Ghidra runs processed the existing project with -process Starfield.exe,
-readOnly and -noanalysis. The program database and project files were hashed
before and after. The investigation used static reads and local reports under
the brief's permissions. No runtime execution or analysis changes were needed.

## Search and prior art

- Used the existing [explicit-address exporter](../ghidra/README.md) for nine
  functions after discovery. It gives full defined bodies, callsites, inbound
  xrefs, data references and decompilation status. All nine decompiled and all
  nine listing start sets matched Capstone at the Ghidra body bounds. The
  neighbourhood exporter expands direct and selected virtual edges from a known
  root. Here explicit addresses kept the fan-out from generic helpers bounded.
  Call-signature and field/resource-provenance exporters offer targeted p-code
  follow-up once a receiver or indirect call is selected. The relevant direct
  calls and offsets were visible in the listing, so those exporters were
  unnecessary for this pass.
- Used the maintainer's OutpostRecon.java in place at sibling revision
  d116bc63ff394b0156539161c8d1addfc902665a for identity, exact function windows,
  symbols and xrefs. Adapted the launch method of Invoke-OutpostRecon.ps1 to
  place settings, cache, temp files and both logs in this task directory. The
  sibling wrapper's output destination and reader allowlist would have put
  receipts in that project and excluded the resource exporter. The sibling
  script README explains the fixed caps and read-only invocation. One broad
  BGSPlanet symbol query hit its 256-result cap, and one control-function
  listing hit 600 instructions. Its PE decode was complete. Narrow symbol and
  reference queries provided the retained context. No outpost address or
  placement finding was used as an allocation premise.
- Used the local reproducer at a8ff1c788bca415f571f06769ab3e712fa674f75 as a
  semantic reference. Its generation.py and prng.py distinguish shared IDs,
  cached families, occurrence types, ordered selection and the separate RNG
  consumers. The CK comparison uses the
  [v1 baseline](v1-research-baseline.md), [live notes](experiments/x64dbg-runtime-generation-findings.md),
  [pre-biome bundle](experiments/evidence/pre-biome-resource-state/) and
  [selector bundle](experiments/evidence/special-common-selector/). No model,
  oracle or plugin data was fed into the executable.
- Scanned all 236,427 unique x64 PE exception-directory ranges contained in
  file-backed .text (RVA 0x1000–0x3A3EF6B inclusive). The guard prefilter
  selected 559 ranges with byte shapes for memory comparisons against 5 and 8.
  Capstone 5.0.7 on Python 3.14.3 resolved one ordered pair of unsigned
  greater-or-equal branches to the same target within 48 bytes. It also had
  direct calls to the same selector within the pre/post windows (100 and
  48 bytes). Then traced the caller and small callee set, using the PE rel32
  callsites checked at decoded instruction boundaries and the saved Ghidra xrefs.
- Independent record and RNG leads served as controls. The old CK stride/rarity
  byte combination produced 258 ranges, and the stride/count/list combination
  produced 433. No decoded range passed the combined CK rarity-offset,
  stride and scalar float-operation filter. At 0x14079B520, the 0x2F8
  occurrences are stack slots and the 0x238 walks are elsewhere in the body.
  The retail rarity displacement 0x110 gave 684 prefilter ranges with stride
  0x238, and three decoded bodies also had the byte compare and scalar
  multiply/add/compare. They are the selector, its out-of-line loop, and
  the orchestrator. The latter's float operations elsewhere in the body
  demonstrate why the coarse filter alone cannot classify the pass.
- ASCII search in file-backed .rdata and .data and a defined-symbol search
  did not recover the CK manager name as an anchor. Exact xref probes at the
  raw RSGD spelling 0x144B02E60 and RTTI name interior 0x145A58328 returned
  zero rows. The RSGD vtable at 0x144B6FD98 had two references from
  FUN_1409efdb0, a separate factory/vptr lead. RTTI factory vtables at
  0x144B6E320, 0x144B6FD48 and 0x144B6D600 associate 0xA0 with BGSBiome,
  0xAB with BGSResourceGenerationData and 0xAD with BGSAtmosphere,
  respectively. This matches the three retail type-byte checks. The adjacent
  ASCII form-tag sequence was not used to assign numeric type codes because
  the simple positional index did not agree with RTTI.
- The raw conventional MT temper-mask pair produced zero ranges. A twist
  prefilter yielded seven, and the seed multiplier yielded 18. The alternate
  MT-looking functions at 0x14030B440 and 0x14030B640 have other callers and
  were outside the established allocation call graph. The actual probability
  primitive uses pre-shift versions of two masks, and the first mask is
  state-resident. The matching primitive was qualified from connected calls,
  its state machine and the scalar constants, independently of the seed hit.
  PE exception ranges omit leaf code without unwind records and can divide a
  single routine into multiple entries. The initial raw mask and guard counts
  have that limitation. Capstone stopped before the end in 31/559 guard
  ranges, 37/684 retail-shape ranges, 14/258 CK stride/rarity ranges, 28/433
  CK stride/count/list ranges and 1/18 MT seed ranges. All seven twist
  ranges decoded to their ends. Negative and uniqueness findings apply to
  decoded prefixes under the stated predicates. The direct-call census
  excludes indirect calls, tail jumps and callsites outside successfully
  decoded ranges. The mapped edges are supported by the focal listings.

## Retail mapping on the pinned image

Preferred VAs use image base 0x140000000. CK VAs refer to the separately
fingerprinted CK evidence and historical live trace. **PROVEN** below grades
directly inspected static behavior. **STRONG** grades interpretations of
matched roles with remaining semantic gaps. The mapping status applies to
the bounded role in each row.

| Retail RVA / preferred VA | CK preferred VA | Mapping status and instruction basis | Remaining alternatives or differences |
| --- | --- | --- | --- |
| 0x779760 / 0x140779760 | 0x14152CBC0 | **STATICALLY ESTABLISHED / PROVEN** enclosing implementation. A planet-keyed atmosphere lookup at 0x140779973 returns a type-0xAD form or fallback. The 0xF8 count and 0x100 pointer are walked before the category-6 pass, with duplicate-checked form IDs stored at 0x140779AA6. The loop at 0x140779C86 passes each shuffled object plus RNG (RDX), family array (R8) and the same shared ID array (R9). | CK atmosphere field layout differs. Invocation and cache invalidation upstream are open. |
| 0x779B32 / 0x140779B32 within that body | 0x141548920 | **STATICALLY ESTABLISHED / PROVEN** inlined Everywhere pass. A type-0xA0 biome supplies a list at 0x308/0x310. Nested 0x238-byte entries are walked, category 6 tested at 0x140779B93, ID stored to biome +0x68 and shared-ID insert called at 0x140779BB8. Selection in this loop uses the first nonzero match without a probability draw. | CK has an outlined helper. Membership of an actual game biome has not been observed here. |
| 0x777870 / 0x140777870 | 0x1415DCFB0 | **STATICALLY ESTABLISHED / PROVEN** per-biome allocation. BIOM and optional RSGD type gates are at 0x140777900 and 0x14077791A. Same selector receives 5 then 0 at 0x140777954 and 0x1407779A4. Special can write +0x64 and insert its ID between the calls. Both count checks (0x140777986 and 0x14077798F) enter 0x140777AF8. A new root calls descendants 1–4 and appends a configuration pointer if allocation succeeds at 0x140777A88–0x140777A8B. Normal reuse copies five IDs. | Effective form data and observed gameplay membership remain untested. |
| 0x777E30 / 0x140777E30 and 0x777FF0 / 0x140777FF0 | 0x141580660 and 0x14157C470 | **STATICALLY ESTABLISHED / PROVEN** Special/Common selector and ordered entry scanner. Draw at 0x140777E69 precedes enumeration. Primary RSGD scan is inline; when both output pointers are zero, the biome list loop can call the outlined scanner at 0x140777FAD. Both scan 0x238-byte entries, compare category at form +0x110 and accumulate entry +0x24 + category × 0x28 scaled by binary32 0.01. For finite ordered comparisons they return the form and entry +8 when roll is strictly less than cumulative. Equality falls through at 0x140777F3D and 0x140778069. The same carry branches accept unordered operands if the comparison completes. Nonfinite record weights were untested. | CK record count/pointer, rarity and FormID offsets differ. CK diagnostics are not a retail anchor. Full override and null-case equivalence is outside this mapping. |
| 0x7780B0 / 0x1407780B0; child append 0x7784D0 / 0x1407784D0 | 0x14157F120 (enclosing helper) | **STRONG CORRESPONDENCE / STRONG** descendant helper, with **PROVEN** call and draw mechanics. The count-eight branch at 0x1407780E6 bypasses RNG. Otherwise a draw precedes root and optional distinct-node child scans. A nonempty pool triggers a second draw and float-scaled index, with an independent chance test for emission on ordered finite values. Nonfinite chance behavior was untested. The chosen node can be returned even when the ID is not emitted. | The append loop at 0x140778533–0x1407785CD filters by rarity and has no visible per-entry duplicate check. Overlapping lists could change candidate multiplicity versus the CK model if duplicate pointers reach these calls. Upstream uniqueness is unqualified. |
| 0x77C0E0 / 0x14077C0E0 and 0x2FCEE0 / 0x1402FCEE0 | 0x14154C710 and 0x14015B4A0 | **STATICALLY ESTABLISHED / PROVEN** guarded fallback construction and selection. The helper scans the passed biome list, flags category 0 at 0x14077C183–0x14077C191 and compares root ID with cached configuration IDs at 0x14077C1B7. The caller draws against matching configurations or the whole cache if Common exists and the matching list is empty. The zero-lower-bound calls at 0x140777B48 and 0x140777B64 use float multiply and truncation, then copy five IDs when the selected pointer is nonnull, without descendant calls. | At 0x140777B22 the helper receives BIOM +0x308. The optional RSGD resolved from work-object +0x4C is unused at this callsite. CK likewise walks BIOM +0x728/+0x730 before the fallback call at 0x1415DD33C. PNDT field provenance, repeated matches, allocation failure and empty-cache edge cases remain open. |
| 0x2FBC20 / 0x1402FBC20 | 0x140924800 | **STATICALLY ESTABLISHED / PROVEN** MT-to-binary32 primitive. State advance, 624-word boundary, twist constant and equivalent pre-shift temper masks lead to uint32 conversion and division by binary32 2^32 at 0x1402FBE25 on the one-word path. Retail callers separately apply the 0 to 0.99999 range at 0x14591F4C8. | The primitive has unrelated callers. Its identity alone is insufficient for allocation or shuffle classification. |
| 0x77C6E0 / 0x14077C6E0, full-width sibling 0x77C4D0 / 0x14077C4D0 | CK shuffle call at 0x14152CEBD | **STRONG CORRESPONDENCE / STRONG** shuffle machinery. Integer draw at 0x1407798EB feeds pointer swaps. Rejection and unsigned remainder are visible at 0x14077C8CE–0x14077C936. The other branch is at 0x1407798E0. The orchestrator seeds an MT state from its input and passes that same stack state to the biome loop, with a per-biome reseed path when the planet seed is zero. | The full-width branch and field-to-record seed provenance were not tested against live vectors. |
| 0x779610 / 0x140779610 and 0x77C470 / 0x14077C470 | No pairing asserted | **CANDIDATE / PROVISIONAL** upstream dispatch boundary. Two direct edges at 0x14077C482 and 0x1407796D2 are **PROVEN**; Ghidra records data xrefs to 0x14077C470. | Data xrefs may be table entries or bookkeeping. Their owner, dispatch condition, lifecycle and gameplay reachability are unresolved. |

The shared insert helper FUN_1403c9970 searches the uint32 ID array before
appending. The same helper serves Everywhere, Special, newly generated Common
roots and emitted descendants at the sites above. The prepopulation loop has
its own duplicate check. The family array follows a separate path. New entries
point at biome configuration storage, ordinary reuse matches the root ID, and
fallback consumes cached configuration pointers. These mechanics explain why a
shared ID count and a family count can independently route to one fallback.

## Reproduction, publication and next experiment

Start at the [retail pin](PROVENANCE.md#current-retail-identity) and the
[CK register](function-register.md). On a lawful matching image, check version
and SHA-256, confirm the PE base, then open an already analyzed Ghidra program
with the matching executable SHA. For example, from the repository root,
export the two core entries to a fresh ignored destination:

    analyzeHeadless <project-directory> Starfield -process Starfield.exe -readOnly -noanalysis -scriptPath ghidra/scripts -postScript ExportFunctionsByAddress.java <local-output> 140779760 140777870

The resulting orchestrator listing and generator callers expose the same
direct edge at 0x140779C86. The generator listing independently gives the
category calls and the two guard branches. Compare that flow with CK
0x14152D28F and 0x1415DD09E–0x1415DD0F2 in the linked bundles. The table's
other branch, field and RNG claims follow the same route using the listed
addresses and lawful image data. The search can be reproduced with a PE32+
reader by enumerating 12-byte exception-directory records, restricting to
file-backed .text and applying the stated predicates before decoding. Local
scripts and outputs record the exact filters, matched ranges, address
coverage, referenced constants and additional lookups.

The dossier, register and provenance supply project-authored metadata and
a lawful-image verification route for the static claims, subject to the
maintainer's release decision. Full native listings, decompilation, PE-derived
payloads, database files, and diagnostic reports stay local. Exact gameplay
dispatch, universal descendant deduplication, and full algorithm/lifecycle
equivalence remain on publication hold as claims of established behavior.

Next, resolve the two adjacent data references at 0x144B3D9F0 and 0x144B3D9F8
and classify the separate reference at 0x1485F1500 to FUN_14077c470. Identify
their owning table or metadata structure, then verify one inbound dispatch
through its receiver or registration site. This bounded static test offers
the shortest route from the established generator to a named trigger while
allowing the references to be rejected as bookkeeping. A live test would
require separate authorization.

## Local verification and handoff

Receipts and selected native evidence are in .local-work/codex/SRR-002/.
start.json and verification-final.json record Git state, external input
hashes and project inventory. identity.tsv, core/manifest.json, the core
exports, context.tsv, code-checks.txt and flow1.txt through flow3.txt support
the mapped edges. scan.json and qualify.txt preserve the unsuccessful paths
and census counts. coverage.txt records partial decodes and execution.json records tool exits and caps. The project and executable identity checks use byte
identity. No scratch output was made a protected repository dependency.

The caller-available space floor was 40,000,000,000 bytes on C: and D:.
Checks preceded write stages with growth reserves, including 1 GiB per drive
for each headless run. space.log and space-during.json record preflight and in-run readings. The task patch is .local-work/diffs/SRR-002.diff.
The replay applies it to bytes retrieved from the starting Git objects in
isolation and checks the result against all delivered file bytes. The brief,
original Git index, CK evidence and unrelated tracked paths are preserved.

<!-- review-status:start -->
## Review status

**COMPLETE.** The independent internal challenger reproduced the core
mapping and accepted the revised substantive snapshot against AC1–AC6.
The first round required partial-decode counts, ordered-float comparison
limits, precise fallback inputs and conditional copies, and exact RTTI
reproduction locators. The second round confirmed those corrections.
The challenger verified the final patch against the reviewed content.

Reviewed manifest SHA-256
5bdc27053ce2d46125410e2985a97a7674665c56e9e43af9b44ad79d5129158d.
The manifest sorts the six task paths and records each file's SHA-256,
two spaces, its repository-relative path and LF. The dossier digest
excludes this entire review-status block, including the marker lines.
Detailed challenge rounds and the manifest are retained in
.local-work/independent-review/SRR-002/.

<!-- review-status:end -->
