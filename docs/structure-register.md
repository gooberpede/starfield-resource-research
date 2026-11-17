# Native structure register

Offsets are byte displacements from the base specified in each row. Widths are
in bytes. The tables describe partial layouts and argument relationships.
Descriptive names are research aliases unless explicitly identified as native.

## Retail dispatch

Pinned [Starfield.exe 1.16.244.0](PROVENANCE.md#current-retail-identity).
Locators are preferred VAs in that image. See the [dispatch evidence](SRR-003-retail-allocator-invocation-and-dispatch.md#native-path-and-predicates).

| Owning context and field or relationship | Offset, width and operation | Evidence and confidence | Open detail |
| --- | --- | --- | --- |
| Stack callback receiver implementing the native RTTI base `stl::local_function_detail::ILocalFunction<BSContainer::ForEachResult, TESForm*>` | Object +0x00, 8-byte vptr store and load. Receiver begins at `[rsp+0x70]` early and `[rbp-0x60]` later. | **PROVEN STATIC** stores at `0x14094E55B` and `0x14094EF3E`, load at `0x1405932E9`, RTTI locator `0x144FD4B68`. The vptr value is `0x144B3D9E8`. | Layout beyond the observed vptr relationship and other uses of the type. |
| Callback vtable, iterator's virtual slot | Table +0x10, 8-byte function pointer read for indirect call. The +0x08 entry is also an 8-byte pointer to the same target. | **PROVEN STATIC** table entries `0x144B3D9F8` and `0x144B3D9F0` contain `FUN_14077c470`. This iterator uses +0x10 at `0x1405932EF`. | Role or callers of +0x08. |
| Iterator owner to form bucket | Owner +0x11E8 for type 0xBA, address computed as `(uint8(type)+5)*0x18`. | **PROVEN STATIC** address computation at `0x1405932A2–0x1405932AD`. | Native owner type and lifecycle. |
| Form bucket count and array pointer | Bucket +0x08, 4-byte count read. Bucket +0x10, 8-byte pointer read on nonzero count. The array has 8-byte form-pointer elements. | **PROVEN STATIC** reads and stride at `0x1405932C7–0x1405932E1` and `0x1405932F8`. | Population, ownership and validity rules outside the sweep. |
| Callback form type | Form +0x2E, 1-byte read and comparison with 0xBA after the null check. | **PROVEN STATIC** `0x14077C474–0x14077C47D` and PNDT descriptor at `0x1458CF6A0`. | Broader form layout. |
| `bImportCSVBiomeData:Data` boolean setting | Setting base VA `0x145EA5FF8`, +0x08 byte write/read. | **PROVEN STATIC** default zero passed at `0x14008C054–0x14008C065`, stored at `0x140305FF6`, profile byte store at `0x1428CDFA8` and tested at `0x14094E542`. [SRR-014 startup evidence](SRR-014-startup-evidence.md) | Effective value in the historical title run. |

## Retail planet allocation state

Same [retail pin](PROVENANCE.md#current-retail-identity). Stack displacements
are locations at the indicated instructions, rather than class member offsets.
See the [allocator evidence](SRR-002-retail-static-reconnaissance.md#retail-mapping-on-the-pinned-image).

| Owning context and field or relationship | Offset, width and operation | Evidence and confidence | Open detail |
| --- | --- | --- | --- |
| Orchestrator's work-list count and array | Header at `[rsp+0x48]`. Header +0x00, 4-byte count read. Header +0x10, 8-byte array pointer read. Shuffle swaps 8-byte work pointers. | **PROVEN STATIC** `0x1407797CC`, `0x14077987D–0x14077988E`, `0x1407798F8–0x140779902` and `0x140779C30`. | Native container and work-object names, ownership and lifetime. |
| PNDT seed read and shared RNG argument | Form +0x50, 4-byte read. Stack state at `[rbp-0x60]` is passed by address to shuffle and in RDX to the per-biome call. Its first 4 bytes receive `0x270` on seed initialization and reseed. | **PROVEN STATIC** `0x1407797F0`, `0x14077983F–0x14077986F`, `0x1407798B0–0x1407798EB`, `0x140779C6F–0x140779C86`. **STRONG** shuffle correspondence with CK. | Retail field-to-record seed provenance and live seed vectors. |
| Per-biome family cache argument and configuration pointer | R8 points to `[rbp-0x80]` in the caller. Header +0x00, 4-byte count read. Header +0x10, 8-byte array pointer read. Entries are 8-byte pointers. An appended entry points at work object +0x50, where the five 4-byte configuration IDs begin. | **PROVEN STATIC** `0x140779C7B`, `0x140777986`, `0x1407779C2–0x1407779E6`, `0x140777A88–0x140777A97`, `0x140777B7C–0x140777B96`. | This identifies the referenced storage within the call path. Ownership and lifetime outside it are unresolved. |
| Per-biome shared resource-ID argument | R9 points to `[rsp+0x30]` in the caller. Header +0x00, 4-byte count read. Header +0x10, 8-byte array pointer read. Elements are 4-byte IDs read during duplicate checks and written on successful append. | **PROVEN STATIC** `0x140779AA1–0x140779AA6`, `0x140779BB3–0x140779BB8`, `0x140779C76`, `0x14077798F` and `0x1403C9986–0x1403C99F9`. | Lifecycle outside this orchestration and behavior under untested data and allocation conditions. |

## Retail retained biome component

Same [retail pin](PROVENANCE.md#current-retail-identity). See
[SRR-011](SRR-011-planetary-allocation-execution-and-result-lifecycle.md#result)
for the edge-key scope, borrowed work pointers and reader.
See [SRR-012 acquisition evidence](SRR-012-acquisition-evidence.md) for
the supported root, node and record decoding and acquisition limits.

| Owning context and field or relationship | Offset, width and operation | Evidence and confidence | Open detail |
| --- | --- | --- | --- |
| Image owner context publication | Owner at module RVA `0x82EE300`. Embedded context at owner +0x2C0. Published context pointer at owner +0x8B0, 8 bytes. | **PROVEN STATIC** getter `0x1423FF660/0x1423FF69F`, initializer and publish `0x1418993C6–0x1418993E3`, allocator read `0x140779676`, shutdown store `0x141882F4E`. | Which measurement phases expose a published, ready context. |
| Attached queue host and DB control object | Context +0x30, 8-byte host link store. Context +0x238, 8-byte control-pointer read. | **PROVEN STATIC** `0x1428D8211`, `0x14077967D`. [SRR-014 database evidence](SRR-014-database-evidence.md) | Complete cross-thread ordering for the selected startup producers. |
| Context edge-index root and size | Tree = context +0x300. Tree +0x00 qword root pointer. Tree +0x48 qword mixed-entry count. | **PROVEN STATIC** root read `0x1405F7AF0`, entry count increments `0x1403827DF/0x140382FE0`. | Actual tree shape, key population and readiness at each phase. |
| Edge record descriptor within a block | At block +0x10+4×slot, 2-byte record size, then 2-byte record offset. A record of the admitted type begins at block + stored offset. | **PROVEN STATIC** descriptor read `0x14077BDA5` and payload address `0x14077BDB1`. | Runtime stability of the block and descriptor across reads. |
| Context edge index | Embedded tree at +0x300. A 0x90-byte entry has a 16-byte edge key at +0x10 and inline `BSGalaxy::CTPerBiomeData` at +0x20. | **PROVEN STATIC** collector `0x14077BD31–0x14077BD63`, pointer math `0x14077BDA5–0x14077BDB1`, insert copy at `0x1407767A4`. | Full key schema and epoch of each context instance. |
| Context reverse-key index | Embedded index at context +0x358. Key-change handling prepares a two-word key. Context-wide reset clears the index. | **PROVEN STATIC** key preparation in `FUN_1424069F0`, guarded command in `FUN_142413190`, clear call `0x142406424`. [SRR-014 database evidence](SRR-014-database-evidence.md) | Full reverse traversal uses outside the observed update path. |
| Context edge notification receiver | Receiver = context +0x38. Receiver +0x0 qword vptr and +0x80 qword collection pointer. A dispatched entry supplies a callable pointer at entry +0x28. | **PROVEN STATIC** on retail 1.16.244.0. Constructor call `0x142405A1C`, vptr store `0x142412839`, zero store `0x142412894`, pointer reads `0x14240F602/0x14240F64A`, indirect call `0x14240F659`. [SRR-015 bounded follow-up](SRR-015-lead-register.md#b8-bounded-follow-up) | Concrete subscribers, installation paths and whether a callback accesses matching allocation values. |
| CTPerBiomeData biome and resource fields | +0x40 BIOM key read and +0x4C optional RSGD key read, both four bytes. +0x50 through +0x68 hold seven four-byte result IDs. | **PROVEN STATIC** key match `0x140771FB6`, RSGD lookup in `FUN_140777870`, result clear/writes in `FUN_140779760` and `FUN_140777870`, seven-slot copy `0x14076E86A–0x14076E886`. | Formal field names and byte-level save-stream mapping. |
| Resolved `BGSResource` identity | Object +0x00, eight-byte primary vptr at image RVA `0x4B6F0B0`. Object +0x28, four-byte FormID. Object +0x2E, one-byte enum `0x9F`. | **PROVEN STATIC** constructor vptr/type stores `0x1409E74E6` and `0x1409E75D9`, independent output-ID lookup and consumer type check `0x14079BC52` and `0x14079BC63`. [Resource identity](SRR-013-structural-state-observation.md#native-resource-identity) | Actual object residence and identity at the selected checkpoint. |

## Retail FormID source namespace

Same [retail pin](PROVENANCE.md#current-retail-identity). See the
[SRR-017 instruction evidence](SRR-017-source-identity.md).

| Owning context and field or relationship | Offset, width and operation | Evidence and confidence | Open detail |
| --- | --- | --- | --- |
| Data-handler publication and file-name registry | Image +0x5FD9B28 qword pointer. Handler +0x1570 inline node, file pointer +0 and successor +8. TESFile name begins at +0x38. | **PROVEN STATIC** constructor/publication at `0x140573788` and `0x14057378D`, registry lookup at `0x140598449..0x140598487`. | Actual admitted files and loaded-source digests. |
| Compiled plugin namespace | Handler +0x1580 full, +0x1590 small, +0x15A0 medium. Array header u32 count, u32 capacity and qword pointer. TESFile +0x1B8 flags and index fields +0x218 u8, +0x219 u8 and +0x21A u16. | **PROVEN STATIC** assignment at `FUN_14059FCF0` and ordinal read at `0x14058E59E..0x14058E64C`. | Title-card contents and admissibility of update aliases. |
| Packed source backing | `TESPackedFile` vtable at image +0x4B29B80. Directory at +0x268 and basename at +0x38, each 260 bytes. The optional open-stream qword at +0x378 points to a `BSFile` (image +0x4DA7FB8 vtable) with open predicate at +0x4C and pathname at +0x6C. | **PROVEN STATIC** at `0x1405B5BE4..0x1405B5BEF`, `0x1405B99D8..0x1405B9A0B`, `0x1405BA126..0x1405BA1EE`, and `0x1428E4340..0x1428E4360`. [Source identity](SRR-017-source-identity.md#effective-file-backing) | A closed source can retain a relative directory and no effective-file stream at title. |
| Relative-source provider list | The relative packed-file open uses the `GlobalLocations` pointer at image +0x61FAB68, with list head at +0x28. Nodes carry the next pointer at +0 and provider at +8; provider vtable slot +0x30 resolves the request. | **PROVEN STATIC** at `0x1405B9FB2..0x1405B9FD3`, `FUN_1427D8950` and `0x1427D7FD6..0x1427D8005`. | Effective per-file route after stream retirement. |
| Per-form source vector | TESForm +0x30 holds u16 index, with FFFF sentinel. Image +0x5E881E8 u32 count, +0x5E881F0 qword index pointer. Bucket +0 qword TESFile-pointer array, +8 u32 length. | **PROVEN STATIC** diagnostic at `0x14058E453..0x14058E508`, writer and append at `FUN_1405E0D50` and `FUN_1405DC730`. | Complete winning-record provenance across loader variants. |

## Creation Kit reference

Use the separately [fingerprinted CK static evidence](PROVENANCE.md#creation-kit-static-evidence)
and [live evidence qualification](PROVENANCE.md#creation-kit-live-evidence)
for CK. The [pre-biome bundle](experiments/evidence/pre-biome-resource-state/)
provides the CK-side comparison. The retail entries above carry retail
offsets and evidence grades only.
