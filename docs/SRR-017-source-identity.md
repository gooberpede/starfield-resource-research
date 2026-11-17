# SRR-017 FormID source identity

**PROVEN STATIC** on retail 1.16.244.0, SHA-256
7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28.
The pinned native image exposes an independent loaded plugin namespace and
ordered per-form source vectors. The inspected disk controls and independent
native-shaped byte tests establish the source join on their defined inputs.

## Native load and read paths

| Pinned retail site | Evidence |
| --- | --- |
| 0x140573774..0x14057378D | The null global leads to FUN_140592890 and data-handler pointer publication at image+0x5FD9B28. |
| 0x142011503..0x14201152B, FUN_14200A5A0 | Papyrus registration names the wrapper GetFormFromFile. It reads the data-handler global, calls FUN_140598430, rejects unmatched or unassigned files (TESFile+0x218=FF), rewrites the FormID, and tail-calls the independent FormID lookup FUN_1405DE3B0. |
| FUN_140598430 | Walks the embedded singly linked node at data handler +0x1570. Each node holds the TESFile pointer at +0 and successor at +8. The native name operand is TESFile +0x38. |
| FUN_1405994A0, FUN_14059FCF0 | The traversal at 0x140599680 assigns files with native flag bit 2 set. Bit 3 defers one file via data handler +0x1568. Assignment sites are 0x1405996AE and 0x14059975B. Reset and startup callers are 0x141897B19 and 0x141883DC9. The three array writers are FUN_14058D880, FUN_14058D8D0 and FUN_14058D930. |
| FUN_1405B78C0 | TESFile flags at +0x1B8 select full, medium (bit 10) or small (bit 8). The routine keeps 24, 16 or 12 local bits and uses +0x218 for the high byte, +0x219 for the medium index and +0x21A for the small index. Bit 9 takes a distinct update-file path through +0x1D8. |
| 0x14058E577..0x14058E64C | On the FormID diagnostic's absent-result path, the high byte chooses full, FD medium, FE small or FF runtime-created. Full uses data handler +0x1580/+0x1588, small +0x1590/+0x1598, medium +0x15A0/+0x15A8. Each accessor checks index against the count and the array result against null before reading the file name. Native writers read capacity at header +4. |
| 0x14058E453..0x14058E508 | The diagnostic's successful lookup path reads a u16 source index from TESForm +0x30 with FFFF sentinel. The table count is at image+0x5E881E8 and pointer at image+0x5E881F0. Indexed bucket +0 points to TESFile pointers, +8 holds u32 length. The diagnostic prints source names in order. |
| FUN_1405E0D50, FUN_1405E3980, FUN_1405DC730 | The writer canonicalizes through TESFile +0x18 and can filter non-master history before supplying TESForm +0x30 at 0x1405E0EB6. It then interns the list and stores its index. The append path preserves prior order and adds the supplied file unless already present. Matching and append are at 0x1405DC7A3..0x1405DC7D7 and 0x1405DC851..0x1405DC883. The loader region FUN_14059E000 calls the writer at 0x14059E280. |

The arrays establish the runtime slot for the defining plugin. The ordered
source vector independently describes native file attribution for a resolved
form. The writer can filter prior non-master contributors. Registration's
deferred branch and the vector filter prevent treating either list as
universal proof of winning bytes.

## Effective file backing

The continuation qualifies an absolute packed-file directory and an
independently typed retained open stream as pathname witnesses. Both
paths use the same exact manifest, signature and file identity checks.
The implementation reads file bytes independently of native FormIDs and
uses the approved profile as a pin before opening any of its sources.

| Pinned instruction or typed location | Evidence |
| --- | --- |
| `0x140573968..0x14057396F`, `0x140597319..0x140597350`, `0x1405973FA`, `0x140597C86` | Startup submits the handler to `FUN_1405972B0`. The first scan builds `DATA\\` and can construct a packed source with that relative directory. The later scan at `0x140597971` supplies a separate directory from the `%sdata/` formatter. |
| `0x144B29B80` and `0x1405B694C..0x1405B6966` | RTTI identifies the packed file vtable. Header load dispatches slot `+0x18` if the file fails the already-open check. Its destination `0x1405B5BE0` passes directory `+0x268` and basename `+0x38` to `FUN_1405B9950`. |
| `0x1405B99D8..0x1405B9A0B`, `0x1405B9F52..0x1405B9F7F` | The open routine retains both 260-byte buffers, joins them, and distinguishes the direct path by a leading slash or a colon. The observer admits an ordinary absolute local drive pathname, excluding ambiguous roots and Windows device paths. |
| `0x1405B9FB2..0x1405B9FD3`, `FUN_1427D8950`, `FUN_1427D7FA0` | Relative opens use `LocationTree` (`0x144D9C578`) with the object at image `+0x61FAB68`. The wrapper delegates at `+0x30`. `GlobalLocations` (`0x144D9C498`) iterates ordered location nodes at object `+0x28`. Each node's first qword links the successor and its next qword supplies the provider. Dispatch stops on the first zero result. |
| `0x1427D95DD..0x1427D9692`, `FUN_1427F6810`, `0x1427FB1A0` | The default setup installs multiple location holders. The loose-file provider (`0x144D9D0B8`) returns its selected prefix from the object at `+0x10`. The object graph has candidate roots and ordering, with no per-plugin record of which provider succeeded at startup. |
| `0x1405BA022..0x1405BA053`, `0x1405BA126..0x1405BA13C`, `0x1428E4340..0x1428E4360` | A successful provider can contribute the effective backing prefix before the packed file constructs a `BSFile`. The live pointer is at packed file `+0x378` and its typed vtable is `0x144DA7FB8`. The constructor copies the resulting filename to `BSFile +0x6C`. The caller tests open state `+0x4C` at `0x1405BA1EE`. |
| `0x140597C98`, `0x1405B6890`, `0x1405BA859..0x1405BA86D` | The registry walk can retire the packed stream through the file close virtual method. The native close disposes of the open-file object and clears `+0x378`. The populated directory field can survive that close. |

For a relative descriptor, the collector checks the stream vtable and
open flag and requires an absolute backing filename with the same
basename. These bytes are reread within each pass and compared across
both passes. Every relative plugin adds at most two first reads and
376 requested bytes under the native namespace ceilings. A closed or
absent stream leaves the relative descriptor unresolved. The private
journal retains the raw witness and the portable dataset records the
refusal code. The export includes path witness classes and digests
without physical paths.

**Retail readiness remains conditional on the effective backing.** The
ordinary startup route can retain `DATA\\` and close the stream. The
active provider list offers a positive alternate-root mechanism. A
basename, the current Steam install directory and a file hash therefore
leave the relative backing ambiguous. A live provider result can be
qualified with the retained-open-stream route above if available. If it
is absent, a subsequent candidate needs equivalent retained
source-specific backing evidence, or a bounded demonstration that
every earlier applicable provider and path in the authenticated epoch
either misses or resolves to the same pinned file. An install directory
listing or last-writer guess cannot supply either check.

## Independent disk controls

| File | SHA-256 | PNDT / BIOM / RSGD / IRES |
| --- | --- | ---: |
| Starfield.esm | 1dabed00c3f4282dd3bb54d2e9601e40b577d8742d078b7ccef203adbfef0da7 | 1,765 / 431 / 32 / 332 |
| ShatteredSpace.esm | f8b9333000aba2a4a8a417cb74a11ede6f5b824d27db1918fd1c1f7b64385a43 | 11 / 3 / 0 / 0 |

The base file has no MAST. The DLC's sole MAST is Starfield.esm.
The base records include runtime-observed Kreet PNDT 0003F59F,
BIOM 000D9BAC and IRES 000057EA. A typed disk example for RSGD is
000083D8. The four previously observed SRR-013 sample prefixes agree with
the base file-local prefix 00. DLC PNDT 01000801 and BIOM 01012244
define shatteredspace.esm:000801 and shatteredspace.esm:012244. Their
retail runtime prefix was unobserved. [Prior sample scope](SRR-013-retail-title-paired-structural-observation.md)

The 39 installed Data candidates include full IRES 01033E3F in
sfbgs00d.esm, base PNDT overrides, and medium definitions FD002810 in
sfbgs003.esm, FD006D06 in sfbgs00b.esm, FD0113AB in sfta03.esm and
FD0196AB in sfta06.esm. Both SFTA files list one medium MAST before their
own records. A counterfactual topological sort over all inspected files
using lexically sorted filenames on each pass admitted 2,586 canonical
definitions across the four signatures. Its assigned full slot 5 made
05000801 the DLC PNDT runtime word. The disk word would select
BlueprintShips-Starfield.esm in that counterfactual. Disk counts describe
source coverage. [Independent file-relative format experiments](https://github.com/Ortham/esplugin/issues/42)

## Tools and reproduction

Run **python -B -m tools.srr017.source --manifest $newPrivateManifest @plugins**
with the explicit installation Data .esm, .esp and .esl paths. The tool
prints counts and the canonical manifest hash. It hashes each named file and
scans its top-level PNDT, BIOM, RSGD and IRES record headers. The new file
contains filename, SHA-256, byte size, flags, ordered MAST names and typed
headers. The 39-file manifest canonical SHA-256 was
b08681ada86d1fbda7e3b801f93dd01d420b5e062adaaa674036fc2fba5f5cef.

Run **python -B -m tools.srr017.probe_namespace $pinnedRetailPE** to
verify the pinned PE SHA-256 and print the listed instruction windows and
decoded caller references and RTTI vtables using Capstone. The probe reads one local disk
PE and writes only to stdout. Neither tool modifies a Ghidra project.

Instantiate **SourceIndex(load_json(manifest), load_json(namespace))**
using the independently reviewed namespace. For example, an owned source
at full slot zero uses the following witness.

    {"authority":"OWNED_DISPOSABLE","plugins":[{"index":0,"kind":"full","plugin":"fixture.esm"}],"schema":"srr017-namespace-v1"}

Supply the plugin entries in independently established record precedence.
The caller binds evidence authority and process epoch. The identity digest
binds both complete inputs. Resolved identities include defining plugin,
local ID, typed signature, defining and winning file-relative words, and
the comparator key. Unsupported typed update or blueprint records,
injected records, corrupt signatures, duplicate source words and deleted
winners refuse. Supported filenames are ASCII plugin basenames.

That ordered-winner mode serves the historical owned tests. The
continuation's `bind_source_files(native_namespace, snapshot)` instead
resolves defining identity by native slot, file-local master domains,
local ID and typed signature. It lists candidate contributor and
tombstone filenames with winning-content attribution unresolved.
A missing, filtered or incomplete source vector preserves a corroborated
defining identity. A vector that names a loaded plugin without the
corresponding canonical typed record is recorded as a contradiction.
Registry order is unused for winning content.

The signed source profile uses schema `srr017-source-files-v1` and a
`files` array with `plugin`, absolute `path`, `bytes` and `sha256` for
each independently prescribed candidate. `snapshot_source_files`
checks stable canonical file paths, regular-file identity and the
prescribed digest, and builds the typed header manifest from those bytes
before launch and after the observed pair. A snapshot admits at most
256 files, 4 GiB of prescribed input bytes, 4,096 top-level groups per
file and one million extracted typed records in total. The hash reads
at most one MiB before checking cancellation again. Current source
comparison uses the complete ordered snapshot, including separate local
file identity, size and time stamps. Duplicate file identities, path and
hash discrepancies, and missing loaded source files refuse. Private
snapshots contain paths and OS file stamps. The portable index publishes
only source hashes, basenames and evidence classes.

An offline disk check independently read the two pinned ESMs via this
path. The snapshot held 1,457,098,709 and 501,394,621 file bytes and the
canonical two-file typed manifest SHA-256 was
`a17f7176b9090fb728efbfc37cc105397378904cdce2d38ef5f848434e5d7777`.
The base test resolved the historical PNDT, BIOM and IRES examples and
the RSGD disk control. A **COUNTERFACTUAL** DLC full slot `0x11`
resolved `11000801` and `11012244` to the two DLC identities above,
with the original on-disk words `01000801` and `01012244` preserved.

The native decoder cross-checks compiled slots against each TESFile's
index and the name registry. Defaults admit 256 slots and 512 registry
files with 1,024-read and 512 KiB limits per collection. The ordered-vector
decoder caps forms at 8,192, vectors at 1,024, and each vector at 64 names.
It requests at most 11,265 reads and 1 MiB per collection, plus paired and
closing rechecks. Native addresses remain in private evidence.

The owned title profile integrates both decoders into the two complete
rooted collections. It reads source history after graph coverage and
typed form validation. The vector lookup uses every distinct verified
PNDT, BIOM, RSGD and nonzero resource FormID actually encountered. It
checks that source pointers refer to admitted compiled files. Source
table and vector extents are disjoint from claimed tree, map and form
extents. Each consumed window is reread before its epoch bracket closes.
Separate source digests cover the exact read windows. Paired namespace
or source history drift preserves both reports and prevents normalized
release. A failed backend operation exits through the same acquisition
refusal as a failed form or tree read.

| Owned case | Mixed / typed rows per pass | Form source vectors observed per pass | Source verdict |
| --- | ---: | ---: | --- |
| Direct root | 6 / 4 | 16 | Agreement |
| Corpus-shaped | 3,600 / 3,210 | 350 | Agreement |
| Upper | 5,120 / 4,096 | 424 | Agreement |
| Paired namespace mutation | 6 / 4 | 16 | Disagreed despite equal raw rows |
| Invalid namespace slot tag | 6 / 4 | 0 | Namespace refused, complete raw rows retained |

Run **python -B -m tools.srr017.qualify_title owned-title $newRunName**
to create and check this native-shaped process evidence. The recorded
qualification report SHA-256 is
74fcec91433323658c99a974b2d97ccf8e6c59b350687a9f5eb4c4cd9c05ea47.
The fixture PE SHA-256 is
96109beeb4accb823b2b8fe7cc82d6e37be223f80398d7edb02074be934d3ecd.

Run **python -B -m unittest -v tools.srr017.test_source** for the fourteen
independently constructed tests. They construct their own plugin headers
and native byte windows, covering all three scales, a null array slot,
inactive registry entries, wrong tags, namespace collisions, a wrong
typed source, malformed extents, vector order and corrupted vectors.
The continuation added independent controls for pinned file substitution,
cooperative cancellation, absolute and relative source witnesses, a closed
stream, omitted contributors and a contradictory contributor.

## Identity lead register

| Lead | Disposition and remaining discriminator |
| --- | --- |
| Base fields are a pointer or handle | **Excluded** for the SRR-013 sample scope. Native typed lookup and independent source headers agree. The active-file wrapper also forwards encoded FormIDs to that same lookup. |
| Runtime prefix always equals the disk high byte | **Excluded.** Native scale arrays and independently authored disk examples demonstrate the need for a separate loaded prefix. Base prefix 00 agrees for the observed samples. |
| CommonLibSF singleton locates the collection directly | **Excluded** on this image. Local Address Library 1.16.244.0 maps ID 825890 to 0x145912E10. The target is a service slot with registered vptr at 0x14395A8DB. Native lookup and the constructor independently identify the loader data-handler pointer. [Upstream ID](https://github.com/Starfield-Reverse-Engineering/CommonLibSF/blob/main/include/RE/IDs.h) |
| Native plugin namespace can be joined independently | **PROVEN STATIC** for ordinary full, medium and small entries. The name registry and vector reads identify basenames. The checked constructor fields at +0x140..+0x150 initialize as qwords, and destruction calls a resource retirement helper on +0x140. This does not establish a retained path or usable handle at title. A retail epoch still requires a witnessed runtime roster, a complete relevant disk manifest and a binding from the actual loaded paths or open file identities to those digests. |
| Registry order or the last source diagnostic always proves the winning record | **BLOCKED.** Native register deferral and source-history filtering are affirmative counterexamples to treating these mechanisms as complete winner evidence. Capture and replay both paired namespace and source vectors with the typed forms, then qualify the winner join against the effective loaded inputs. |
| Alternate plugin or CSV sources change comparison | **BLOCKED** for oracle applicability. The sources above establish identity layouts and candidate headers. A loaded-file witness and effective reconstruction are needed for an input attestation. [Existing effective-input gates](SRR-013-retail-effective-inputs.md) |

No retail process or save was accessed.
