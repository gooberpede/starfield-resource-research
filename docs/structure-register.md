# Native structure register

Offsets are byte displacements from the base specified in each row. Widths are
in bytes. The tables describe partial layouts and argument relationships.
Descriptive names are research aliases unless explicitly identified as native.

## Retail dispatch

Pinned [Starfield.exe 1.16.244.0](PROVENANCE.md#current-retail-identity).
Locators are preferred VAs in that image. See the [dispatch evidence](retail-execution-lifecycle.md).

| Owning context and field or relationship | Offset, width and operation | Evidence and confidence | Open detail |
| --- | --- | --- | --- |
| Stack callback receiver implementing the native RTTI base `stl::local_function_detail::ILocalFunction<BSContainer::ForEachResult, TESForm*>` | Object +0x00, 8-byte vptr store and load. Receiver begins at `[rsp+0x70]` early and `[rbp-0x60]` later. | **PROVEN STATIC** stores at `0x14094E55B` and `0x14094EF3E`, load at `0x1405932E9`, RTTI locator `0x144FD4B68`. The vptr value is `0x144B3D9E8`. | Layout beyond the observed vptr relationship and other uses of the type. |
| Callback vtable, iterator's virtual slot | Table +0x10, 8-byte function pointer read for indirect call. The +0x08 entry is also an 8-byte pointer to the same target. | **PROVEN STATIC** table entries `0x144B3D9F8` and `0x144B3D9F0` contain `FUN_14077c470`. This iterator uses +0x10 at `0x1405932EF`. | Role or callers of +0x08. |
| Iterator owner to form bucket | Owner +0x11E8 for type 0xBA, address computed as `(uint8(type)+5)*0x18`. | **PROVEN STATIC** address computation at `0x1405932A2–0x1405932AD`. | Native owner type and lifecycle. |
| Form bucket count and array pointer | Bucket +0x08, 4-byte count read. Bucket +0x10, 8-byte pointer read on nonzero count. The array has 8-byte form-pointer elements. | **PROVEN STATIC** reads and stride at `0x1405932C7–0x1405932E1` and `0x1405932F8`. | Population, ownership and validity rules outside the sweep. |
| Callback form type | Form +0x2E, 1-byte read and comparison with 0xBA after the null check. | **PROVEN STATIC** `0x14077C474–0x14077C47D` and PNDT descriptor at `0x1458CF6A0`. | Broader form layout. |
| `bImportCSVBiomeData:Data` boolean setting | Setting base VA `0x145EA5FF8`, +0x08 byte write/read. | **PROVEN STATIC** default zero passed at `0x14008C054–0x14008C065`, stored at `0x140305FF6`, profile byte store at `0x1428CDFA8` and tested at `0x14094E542`. [SRR-014 startup evidence](retail-execution-lifecycle.md) | Effective value in the historical title run. |

## Retail planet allocation state

Same [retail pin](PROVENANCE.md#current-retail-identity). Stack displacements
are locations at the indicated instructions, rather than class member offsets.
See the [allocator evidence](component-database.md).

| Owning context and field or relationship | Offset, width and operation | Evidence and confidence | Open detail |
| --- | --- | --- | --- |
| Orchestrator's work-list count and array | Header at `[rsp+0x48]`. Header +0x00, 4-byte count read. Header +0x10, 8-byte array pointer read. Shuffle swaps 8-byte work pointers. | **PROVEN STATIC** `0x1407797CC`, `0x14077987D–0x14077988E`, `0x1407798F8–0x140779902` and `0x140779C30`. | Native container and work-object names, ownership and lifetime. |
| PNDT seed read and shared RNG argument | Form +0x50, 4-byte read. Stack state at `[rbp-0x60]` is passed by address to shuffle and in RDX to the per-biome call. Its first 4 bytes receive `0x270` on seed initialization and reseed. | **PROVEN STATIC** `0x1407797F0`, `0x14077983F–0x14077986F`, `0x1407798B0–0x1407798EB`, `0x140779C6F–0x140779C86`. **STRONG** shuffle correspondence with CK. | Retail field-to-record seed provenance and live seed vectors. |
| Per-biome family cache argument and configuration pointer | R8 points to `[rbp-0x80]` in the caller. Header +0x00, 4-byte count read. Header +0x10, 8-byte array pointer read. Entries are 8-byte pointers. An appended entry points at work object +0x50, where the five 4-byte configuration IDs begin. | **PROVEN STATIC** `0x140779C7B`, `0x140777986`, `0x1407779C2–0x1407779E6`, `0x140777A88–0x140777A97`, `0x140777B7C–0x140777B96`. | This identifies the referenced storage within the call path. Ownership and lifetime outside it are unresolved. |
| Per-biome shared resource-ID argument | R9 points to `[rsp+0x30]` in the caller. Header +0x00, 4-byte count read. Header +0x10, 8-byte array pointer read. Elements are 4-byte IDs read during duplicate checks and written on successful append. | **PROVEN STATIC** `0x140779AA1–0x140779AA6`, `0x140779BB3–0x140779BB8`, `0x140779C76`, `0x14077798F` and `0x1403C9986–0x1403C99F9`. | Lifecycle outside this orchestration and behavior under untested data and allocation conditions. |

## Retail retained biome component

Same [retail pin](PROVENANCE.md#current-retail-identity). See
[SRR-011](component-database.md)
for the edge-key scope, borrowed work pointers and reader.
See [SRR-012 acquisition evidence](component-database.md) for
the supported root, node and record decoding and acquisition limits.

| Owning context and field or relationship | Offset, width and operation | Evidence and confidence | Open detail |
| --- | --- | --- | --- |
| Image owner context publication | Owner at module RVA `0x82EE300`. Embedded context at owner +0x2C0. Published context pointer at owner +0x8B0, 8 bytes. | **PROVEN STATIC** getter `0x1423FF660/0x1423FF69F`, initializer and publish `0x1418993C6–0x1418993E3`, allocator read `0x140779676`, shutdown store `0x141882F4E`. | Which measurement phases expose a published, ready context. |
| Attached queue host and DB control object | Context +0x30, 8-byte host link store. Context +0x238, 8-byte control-pointer read. | **PROVEN STATIC** `0x1428D8211`, `0x14077967D`. [SRR-014 database evidence](component-database.md) | Complete cross-thread ordering for the selected startup producers. |
| Queue service state | Image owner +0x296, u16. The six u16 masks at owner +0x28A through +0x294 initialize to 1, 2, 4, 8, 0x10 and 0x20 respectively. Configuration exchanges the state to 1. | **PROVEN retail static** initialization at `0x1428D872B–0x1428D8749`, exchange at `0x1428D8890`, notification and service transitions in the [lifecycle](retail-execution-lifecycle.md#typed-input-readiness-at-sweep-entry-srr014-a9). | Several submissions can share a pending service request. The state word supplies no per-command completion count. |
| Context edge-index root and size | Tree = context +0x300. Tree +0x00 qword root pointer. Tree +0x48 qword mixed-entry count. | **PROVEN STATIC** root read `0x1405F7AF0`, entry count increments `0x1403827DF/0x140382FE0`. | SRR-017 measures a complete admitted rooted store at paired title checkpoints; other phases remain unmeasured. |
| Edge record descriptor within a block | At block +0x10+4×slot, 2-byte record size, then 2-byte record offset. A record of the admitted type begins at block + stored offset. | **PROVEN STATIC** descriptor read `0x14077BDA5` and payload address `0x14077BDB1`. | Runtime stability of the block and descriptor across reads. |
| Context edge index | Embedded tree at +0x300. A 0x90-byte entry has a 16-byte edge key at +0x10 and inline `BSGalaxy::CTPerBiomeData` at +0x20. | **PROVEN STATIC** collector `0x14077BD31–0x14077BD63`, pointer math `0x14077BDA5–0x14077BDB1`, insert copy at `0x1407767A4`. | Full key schema and epoch of each context instance. |
| Context reverse-key index | Embedded index at context +0x358. Key-change handling prepares a two-word key. Context-wide reset clears the index. | **PROVEN STATIC** key preparation in `FUN_1424069F0`, guarded command in `FUN_142413190`, clear call `0x142406424`. [SRR-014 database evidence](component-database.md) | Full reverse traversal uses outside the observed update path. |
| Context edge notification receiver | Receiver = context +0x38. Receiver +0x0 qword vptr and +0x80 qword collection pointer. A dispatched entry supplies a callable pointer at entry +0x28. | **PROVEN STATIC** on retail 1.16.244.0. Constructor call `0x142405A1C`, vptr store `0x142412839`, zero store `0x142412894`, pointer reads `0x14240F602/0x14240F64A`, indirect call `0x14240F659`. [SRR-015 bounded follow-up](component-database.md) | Concrete subscribers, installation paths and whether a callback accesses matching allocation values. |
| CTPerBiomeData biome and resource fields | +0x40 BIOM key read and +0x4C optional RSGD key read, both four bytes. +0x50 through +0x68 hold seven four-byte result IDs. | **PROVEN STATIC** key match `0x140771FB6`, RSGD lookup in `FUN_140777870`, result clear/writes in `FUN_140779760` and `FUN_140777870`, seven-slot copy `0x14076E86A–0x14076E886`. | Formal field names and byte-level save-stream mapping. |
| Resolved `BGSResource` identity | Object +0x00, eight-byte primary vptr at image RVA `0x4B6F0B0`. Object +0x28, four-byte FormID. Object +0x2E, one-byte enum `0x9F`. | **PROVEN STATIC** constructor vptr/type stores `0x1409E74E6` and `0x1409E75D9`, independent output-ID lookup and consumer type check `0x14079BC52` and `0x14079BC63`. [Resource identity](component-database.md) | SRR-017 attests typed identities at its paired title checkpoints; other epochs need fresh resolution. |

## Retail FormID source namespace

Same [retail pin](PROVENANCE.md#current-retail-identity). See the
[SRR-017 instruction evidence](component-database.md).

| Owning context and field or relationship | Offset, width and operation | Evidence and confidence | Open detail |
| --- | --- | --- | --- |
| Data-handler publication and file-name registry | Image +0x5FD9B28 qword pointer. Handler +0x1570 inline node, file pointer +0 and successor +8. TESFile name begins at +0x38. | **PROVEN STATIC** constructor/publication at `0x140573788` and `0x14057378D`, registry lookup at `0x140598449..0x140598487`. | SRR-017 resolves defining namespace (38 plugins); winning effective source digests remain unattested. |
| Compiled plugin namespace | Handler +0x1580 full, +0x1590 small, +0x15A0 medium. Array header u32 count, u32 capacity and qword pointer. TESFile +0x1B8 flags and index fields +0x218 u8, +0x219 u8 and +0x21A u16. | **PROVEN STATIC** assignment at `FUN_14059FCF0` and ordinal read at `0x14058E59E..0x14058E64C`. | SRR-017 resolves its title-card namespace; winning-content provenance is a separate question. |
| Packed source backing | `TESPackedFile` vtable at image +0x4B29B80. Directory at +0x268 and basename at +0x38, each 260 bytes. The optional open-stream qword at +0x378 points to a `BSFile` (image +0x4DA7FB8 vtable) with open predicate at +0x4C and pathname at +0x6C. | **PROVEN STATIC** at `0x1405B5BE4..0x1405B5BEF`, `0x1405B99D8..0x1405B9A0B`, `0x1405BA126..0x1405BA1EE`, and `0x1428E4340..0x1428E4360`. [Source identity](component-database.md) | A closed source can retain a relative directory and no effective-file stream at title. |
| Relative-source provider list | The relative packed-file open uses the `GlobalLocations` pointer at image +0x61FAB68, with list head at +0x28. Nodes carry the next pointer at +0 and provider at +8; provider vtable slot +0x30 resolves the request. | **PROVEN STATIC** at `0x1405B9FB2..0x1405B9FD3`, `FUN_1427D8950` and `0x1427D7FD6..0x1427D8005`. | Effective per-file route after stream retirement. |
| Per-form source vector | TESForm +0x30 holds u16 index, with FFFF sentinel. Image +0x5E881E8 u32 count, +0x5E881F0 qword index pointer. Bucket +0 qword TESFile-pointer array, +8 u32 length. | **PROVEN STATIC** diagnostic at `0x14058E453..0x14058E508`, writer and append at `FUN_1405E0D50` and `FUN_1405DC730`. | Complete winning-record provenance across loader variants. |

## Retail survey state and caller snapshot

**PROVEN, retail static** on 1.16.244.0. Offsets are bytes. A stored wrapper
includes a 0x20-byte prefix. The snapshot is a separate caller-owned object.

| Base | Field and operation | Locator |
| --- | --- | --- |
| PlayerKnowledge payload | +0 u32 mask (bits 0, 1), +4 i32 level. +0x18 item lookup structure, +0x40 backing pointer, +0x48 index limit used for miss comparison. Item stride 0x30, byte +0x21 tested for positive progress and +0x20 separately updated. Body ID keys the component, item FormID keys the lookup. | `0x1416D0F4C–0FBB`, `0x1416D10D3–1102`, `FUN_1407B77D0`. |
| Actor-location-change event | +0 actor reference pointer, +8 old and +0x10 new location pointers, all 64-bit. The spaceship sink compares the actor and passes the new location to the body resolver. | `0x140B96EE5–6EEF`, `0x142108A42–8A50`. These offsets describe the event delivered to this callback. |
| Missing-key PlayerKnowledge command | +8 callback pointer, +0x18 staged payload, +0x88 u64 key and +0x90 DB pointer in a 0x98-byte allocation. | `FUN_1407BF210`, `FUN_140777350`. Command storage and the final keyed row have distinct lifetimes. |
| Stored PlayerKnowledge wrapper and archive | Wrapper+0x10 u64 composed key, +0x20 payload. Stream includes u32 mask, u16 component version and i32 level. Mask bit 3 admits item records. Paired ID helpers handle body and item identities. Item byte +0x21 precedes +0x20 on the stream (second byte present from version 2). | `0x141411343–138B`, `0x1414135BB–164A`, `FUN_142337790/142337A50`. |
| Unit-6 PlayerKnowledge stream, pinned four-byte ID mode | After u32 record count each key is an encoded ID and u16 low word. The mask/version/level are followed by a u32 auxiliary count and encoded IDs. Bit 3 admits a u64 item count. From v1 each item has a u64 nested count and IDs after its byte fields. From v3 the component ends with a u64 count and 12 bytes per entry, including when bit 3 is clear. | `0x141411299`, `0x142337807/7831/783D`, `0x142337E60–7EC3`, `0x142338172–820A`. Field widths and ordering **PROVEN** on the pinned pair. Trailer bytes retain no additional semantic label. |
| Locations body detail | +0x168 vector of 0x28-byte resource rows, +0x188 embedded snapshot. The copy preserves its u32 counts at detail+0x24C/+0x250. The exposed array and its disabled bytes supply the Locations counter. | `0x1416D04E0–0527`, `0x141360436/0x14136043E`, `0x1416B69B8–6AAF`. |
| Survey snapshot | +0xC4 and +0xC8 u32 computed resource credit and span length sum, +0x1B0 visit byte, +0x1B8 resolved atmosphere form pointer, +0x1C8 body ID, +0x1CC binary32 aggregate survey fraction, +0x1D0/+0x1E8 pointer vectors. | `FUN_1417D6520/1417D7540/1417D7EB0` and [matrix](component-database.md#resource-membership-player-knowledge-and-the-locations-page). |
| Resource row input to UI setter | Stride 0x28, string values at +0/+0x10, +0x20 packed u32 color, +0x24 rarity byte, +0x25 disabled, +0x26 show-color, +0x27 tagged. | `0x1416D194A–19D1`, `FUN_1416B6180`, `FUN_14136CFD0`. |
| Monocle wheel row schema | UI wrappers at +0x08 name, +0x28 symbol, +0x48 color, +0x68 disabled, +0x88 tracking. Disabled controls both the wheel icon frame and its color transform. Picked-resource color and discovery have separate wrappers at +0xC8 and +0x328 on the pick model. | `FUN_1415971C0`, `FUN_141597680`, `FUN_14159A0B0`, `FUN_14159AE80`. |
| Body-inspect state | Selection key at +0xC90, body-info provider at +0x6B0, embedded interface at +0x6D0. The common projected detail carries its selected key at +0x184. | `0x141681686–6E3`, `0x14168FC7F–FCFB`, `0x1416CD553`, `FUN_141685E30`. |

## Creation Kit reference

Use the separately [fingerprinted CK static evidence](PROVENANCE.md#creation-kit-static-evidence)
and [live evidence qualification](PROVENANCE.md#creation-kit-live-evidence)
for CK. The [pre-biome bundle](experiments/evidence/pre-biome-resource-state/)
provides the CK-side comparison. The retail entries above carry retail
offsets and evidence grades only.


These CK offsets belong only to the CK evidence domain above; do not apply
retail form offsets to them. Fields below are **PROVEN STATIC**, with live
behavior qualified separately in the [baseline](v1-research-baseline.md).
Widths are bytes and all offsets are byte displacements.

| Base and field | Offset / width / operation | Native locator and qualification |
| --- | --- | --- |
| CK shared-ID array header | +0 u32 count, +4 u32 capacity, +8 eight-byte allocator/reserved state, +0x10 pointer to four-byte FormIDs | `FUN_14152CBC0`, setup `0x14152CEC2–0x14152CF00`; `0x14152D034` loads form+0x70, `0x14152D0E9` appends after duplicate check. Stack-local `local_1568`. |
| CK generator arguments | RCX current work; RDX MT state; R8 family-cache header; R9 shared-ID header | `0x14152D28F`; temporary descendant context+0x20 stores R9, read `0x14157F14D`. Separate cache/shared state, not interchangeable. |
| CK selector context | +0 MT-state pointer, +8 work pointer, +0x10 pointer to optional direct generation pointer, +0x18 pointer to resolved dependency source | Constructed `0x1415DD07A–0x1415DD08F`; source scans `0x1415806FA–70C`, fallback count/data `0x141580737–74C`. Exact source C++ types unnamed. |
| CK generation object and entries | +0x118 u32 count, +0x120 array pointer; entry stride 0x238; +0 resource dependency pointer; +0x24+category×0x28 four-byte chance | `FUN_14157C470`; chance arithmetic `0x14157C5B3–5CA`. Resource category +0x2F8 byte; FormID +0x70 u32. Chance semantic names STRONG, raw offsets PROVEN STATIC. |
| CK selector output | 16-byte pair, +0 resource pointer, +8 entry+8 pointer | Stores `0x14157C5F7/5FA`; caller owns output. |
| CK atmosphere lookup/list | planet+0x134 u32 key; resolved object+0x88 type byte 0xAD; object+0x1D8 array accessor | `FUN_1419FE120`, `FUN_141A46660`; no recovered engine field name. Enclosing atmospheric role PROVEN LIVE. |
| CK work result | +0x50..+0x68 cleared; +0x68 four-byte Everywhere FormID | `FUN_14152CBC0`, write `0x141548ADA`; not a universal class layout. |
| Historical CK TESContainer | +0x40 u32 count, +0x44 u32 capacity, +0x48 entry-array pointer | `FUN_140e0aab0` and `FUN_140e457b0` static copy/resolver. Count/capacity-like source reads are established; generic CopyComponent name remains proposed. |
| Historical container entry | stride 0x18; +0 int32 quantity, +4 unknown/padding, +8 form pointer, +0x10 metadata pointer | Same copy/resolver; TESBoundObject/TESLevItem identity via dynamic cast, not a live IRES-family finding. |
| Historical concrete widget source | widget+0xA0 pointer, adjusted +0x20 component; widget+0x30 copy context; widget+0x98 QSpinBox pointer | Call `0x1431BC350`, resolver `0x1431BC375`; source +0x20 inheritance/containment unresolved. Stock QTreeWidget layout not established. |
