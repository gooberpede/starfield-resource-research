# SRR-014 — Startup path and scheduling evidence

All native locators here are preferred VAs for retail Starfield.exe
1.16.244.0, SHA-256
`7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28`.
Subtract `0x140000000` for an image RVA. The
[technical dossier](SRR-014-startup-allocation-component-database-lifecycle.md)
integrates these paths with component operations and the write predicates.

## Owner, registration and application dispatch

| Evidence class | Applicable path and effect | Native test |
| --- | --- | --- |
| PRIOR ESTABLISHED | Lazy process-global owner initialization zeroes the authoritative published-context slot. The context occupies owner +0x2C0. | `FUN_1423FF640` returns the image object at `0x1482EE300`. Store `0x1423FE0E9` zeroes owner +0x8B0. The published slot RVA is `0x82EEBB0` and the embedded object RVA is `0x82EE5C0`. [SRR-012](SRR-012-acquisition-evidence.md#published-context-and-identity) |
| NEW STATIC FINDING | On the inspected application startup continuation, the DB is constructed, published and attached to the owner's queue host before the guarded galaxy constructor. The preceding guard concerns a separate global. | `FUN_141898870` branches on qword `[0x145E758E8]` at `0x141899379–0x141899381`. Its arms join at `0x1418993BE`. Both reach the embedded `FUN_1424059F0` call at `0x1418993DE` and publication at `0x1418993E3`. The call at `0x1418993F1` passes owner +0x40 and the DB to `FUN_1428D8130`. Its add path stores the host at DB +0x30 at `0x1428D8211`. |
| PRIOR ESTABLISHED | Both indexes are initialized within the DB constructor before successful return and publication. | `0x142405AD8` installs the DB vptr. The two initialization arms for +0x268 start at `0x142405C64` and `0x142405CE9`. Those for +0x300 start at `0x142405E01` and `0x142405E86`. Both root headers start empty. The two stores and the process-wide type registry have distinct identities. [SRR-012](SRR-012-acquisition-evidence.md#exact-mixed-index-model) |
| NEW STATIC FINDING | Publication and `PerBiomeData` registration have a concrete normal-path order. The registered `BSGalaxy::ModuleState` can already exist, in which case construction and registration are bypassed at this site. | At `0x14189A687`, `FUN_14187F4F0` requests a 0x500-byte allocation. Null bypasses `0x14189A69E → FUN_141881660`. In that callee, a zero `[0x1461FA160]` at `0x141882092` admits construction at `0x1418820A3 → FUN_14231D000`. The constructor stores the receiver at `0x14231D032` and submits registration at `0x14231D7D9–0x14231D7F1`, using its +0x100 descriptor and the word at `0x1461DFA4C`. The caller stores the returned receiver at `0x1418820A8`. The setup then reaches `0x14189A80C` on normal continuation. |
| PRIOR ESTABLISHED | The application route can call its startup continuation inline or through a service command. | `0x14365D891 → FUN_1418814C0`, `0x14188155B → FUN_141898870`, `0x14189A80C → FUN_1418A2520`, and `0x1418A257E → FUN_1418A37C0`. This driver reaches `FUN_14189A970` via `0x1418A3A34` or command vptr `0x144CB2AD0` slot +8 at `0x1418A3C70`. Earlier startup failures can return false, which bypasses the application loop at `0x141881562`. The initial transfer from the PE's .bind entry remains unresolved. [SRR-011](SRR-011-planetary-allocation-execution-and-result-lifecycle.md#invocation) |
| NEW STATIC FINDING | The optional direct loader and state-0 dispatch can both be reached during one normal continuation. Their predicates are separate. | In `FUN_14189A970`, the arm at `0x14189AB58–0x14189ABB4` calls the loader if the pointer at `0x14591AC00` is nonnull with a nonzero target byte, or each pointer and target byte at `0x14591AC20/40/60` is nonzero. At the later join `0x14189AC9D–0x14189ACAD`, a zero byte at `0x145E71718` and nonzero saved AL from the virtual call at `0x14189AB43` admit `FUN_14187FEA0(0)`. No test of whether the direct loader ran appears in these two final admission checks. Intervening work and repeated setting tests can affect admission. The precise user-facing meanings of these predicates and their actual values remain open. |
| PRIOR ESTABLISHED | Both initial entries converge on the file/group loader and guarded Starfield module entry. | State-0 worker call `0x14187FA0F` and the direct arm `0x14189ABB4` reach `FUN_141893EE0`. Its call at `0x141894C8E` enters `FUN_141883440`, which calls `FUN_1405994A0` at `0x141883DC9`. The normal wrapper return at `0x141894C93` reaches `FUN_1409518B0` at `0x141894CC3` after three intervening calls. Qword `[0x1461E2288]` gates the normal module constructor at `0x140951904`. Nonzero bypasses it to `0x140951A3C`. |

`FUN_14187FEA0` stores the dispatch state at `0x14187FF0D`, creates
the initially unsignaled event at `0x14187FF1B` and publishes its control
pointer at `0x14187FF29` on the successful path. The service call at
`0x14187FF3B` reaches `FUN_14187F9D0` inline through `0x1418A1A9D`
or through vptr `0x144CB2F78` slot +8, whose thunk at `0x1418A2CA0`
jumps to the worker. The startup callback creates no independent ambiguity
about synchronous execution *inside* the allocator visit. With normal
return and no intervening clear of the Starfield guard, the second module
entry sees the first entry's already published pointer and bypasses
construction. That is a conditional native consequence. [SRR-003
conditional dispatch](SRR-003-retail-allocator-invocation-and-dispatch.md#conditional-dispatch-in-pseudocode)

## Optional first sweep and CSV input

**NEW STATIC FINDING.** The early comparison at `0x14094E542` reads
the current value of the native default-false `bImportCSVBiomeData:Data`
setting. The previous exact-reference search in SRR-011 understandably
found only the comparison because the writers use a computed field address.
The evidence resolves the initialization and one configuration writer for
this build. The effective value at the historical title checkpoint is open.

| Join | Native evidence |
| --- | --- |
| Name and default | Initializer `FUN_14008C050` loads `R8D=0`, the name string at `0x144B65898` and the setting address `0x145EA5FF8` before calling `FUN_140305FD0` at `0x14008C065`. The latter writes the name to +0x18, clears the value dword and sets the value byte at `0x140305FEF–0x140305FF6`, then copies the initialized value to +0x10. The consumed byte is `0x145EA5FF8 + 8`. An exact qword reference to the initializer occurs at `0x143A566C8`. |
| Membership in the INI collection | `FUN_1403061C0` returns a singleton whose vptr is installed as `0x144AFB330` at `0x140306213`. Its RTTI locator at `0x144F678E0` resolves to `INISettingCollection` (type-name VA `0x1459BB140`). The call at `0x140306062` uses the collection's slot +8, `FUN_140308070`, which adds the setting pointer to the list at collection +0x118 when its name is absent. |
| Load and dispatch | Startup calls `FUN_140C80E60` with this collection at `0x141898D05`, `0x141898DBF` and `0x141898E05`. The latter path uses `StarfieldCustom.ini` at `0x144CB3518`. The callee sets its path, then calls collection slot +0x30. The resolved method `FUN_1428CD970` establishes +0x110 and returns true. The +0x58 method `FUN_140307FA0` iterates the +0x118 setting list and calls its collection slot +0x28 with each nonnull setting. That slot resolves to `FUN_1428CDBE0`. |
| Configured write | The reader parses the name and section from setting +0x18. `FUN_1428CD500` maps the initial `b` via byte table `0x1428CD58C` and jump table `0x1428CD56C` to type 0. The reader's table at `0x1428CE004` sends 0 to `0x1428CDF83`. It passes section, key, current boolean default and path to the integer profile reader at `0x1428CDF9B`, normalizes nonzero and writes setting +8 at `0x1428CDFA8`. These startup load calls precede construction at `0x1418993DE`. |
| Neighbor controls | The preceding guard at `0x14094E4C1` reads `bImportCSVStarData:Data` (initializer `0x14008C020`, object `0x145EA5FD8` +8). The guard at `0x14094E4EC` reads `bImportCSVCelestialBodyData:Data` (`0x14008C190`, object `0x145EA6128` +8). Their calls at `0x14094E4DA`, `0x14094E50A` and `0x14094E531` precede the early-sweep decision. They are distinct inputs and are not substitutes for inspecting the biome CSV branch. |

**PRIOR ESTABLISHED.** For nonzero `bImportCSVBiomeData:Data`, the
constructor calls the early PNDT iterator at `0x14094E577`, its BIOM
follow-up at `0x14094E57C` and the biome CSV parser at `0x14094E608`,
in that order. The parser's file source is a setting object with default
`Space\BiomeData.csv` (string `0x144D609C8`, pointer at `0x145920A88`). The file acceptance branch requires a nonnull
stream and its bit 0x08 at `0x14233F34D–0x14233F361`. Accepted buffered
rows start with zero at +0x50..+0x68 (`0x142340535–0x14234053F)).
Both flush sites call `FUN_142340990` and reach
`FUN_142340AB0`, which checks the separate +0x268 record type
`0x1461E1D90` before the row submission path at `0x14234103A`.
That site copies the row into a typed command via `FUN_140773BE0`.
The CSV loader may return without a submitted row. The later iterator at
`0x14094EF57` is on the common normal continuation of both flag paths.
[SRR-011 authored and CSV inputs](SRR-011-planetary-allocation-execution-and-result-lifecycle.md#result)

**NEW STATIC FINDING.** The common-tail call at `0x14094EECC` consumes
the published DB. Within `FUN_1407873D0` the search at
`0x14078742A–0x140787468` uses +0x268 and discriminator
`0x1461DD80C`. The subsequent write at `0x140787559` is to that
edge's +0x20, populated from a type-0x75 form's +0x28 or zero. This
provides a positive control for nearby DB activity on a different record.
The follow-up directly after each allocation visit similarly gathers BIOM
identity and can install jobs with a separate discriminator. Neither
call provides an allocation-result count. CSV submission, command service,
and the later collector's successful fetch are distinct boundaries.
An indexed payload seen by a collector has been inserted by the time of that
lookup. These paths alone leave global queue quiescence and complete
visibility of every accepted row before the later sweep open.
[Database command and guards](SRR-014-database-evidence.md) ·
[SRR-011 follow-up controls](SRR-011-planetary-allocation-execution-and-result-lifecycle.md#readers-and-reuse)

## Return, reset and disposal

| Evidence class | Candidate boundary | Defensible ordering |
| --- | --- | --- |
| NEW STATIC FINDING | Latches at `0x145E7B57C` and `0x145E758AF` | The former is written to 1 at `0x14189932A`, before DB construction. The latter is written to 1 at `0x14189947E`, after context attachment and a separate type registration (`0x1461DD824`), but before `PerBiomeData` registration and guarded loader dispatch. Shutdown writes zero to the latter at `0x141882F6F` after context disposal. The positive stores are too early to mark allocation completion on this path. |
| NEW STATIC FINDING | Byte at `0x145E614D9` | The initial loader exchanges byte 1 at `0x141894CBD`, before the Starfield module call. Signed reset exchanges zero at `0x1418975FF` before replay and writes 1 at `0x141897C01` after re-entry. Its different placement across initial and reset legs and the module-guard bypass preclude a common productive-write completion interpretation. |
| PRIOR ESTABLISHED | Worker event and first-transition latch | State 0 calls SetEvent at `0x14187FB52` after initial loader return and intervening work. State 1 signals at `0x14187FBA4` after the reset call returns. `FUN_141898210` sets its own latch at `0x141898230` **before** entering `FUN_14187FBD0`. If worker control exists, the latter loops on a zero-timeout WaitForSingleObject at `0x14187FBF6` against control +8. The first-transition gate can order a qualifying request after worker progress. An event can signal after a guard bypass, an empty sweep, or via state 1 after a reset that skips replay. [SRR-011 startup and manual-load admission](SRR-011-planetary-allocation-execution-and-result-lifecycle.md#invocation) |
| PRIOR ESTABLISHED | Reset and repeat construction | Signed-negative receiver mode at `0x141897167–0x14189716B` admits data-handler reset, then the index clear at `0x141897552` using the already-published context, distinct module teardown at `0x141897557`, loader replay at `0x141897B19`, and module re-entry at `0x141897B59`. The Starfield teardown uses `FUN_1409501A0` on the nonnull path and clears the Starfield guard at `0x14095028E` and `0x140951CDD`. Its known destructor removes a receiver at galaxy module +0x38. Type deregistration has a separate call. |
| NEW STATIC FINDING | Shutdown order for the separate lifetimes | In `FUN_141882BB0`, `0x141882F32–0x141882F4E` detaches the owner, disposes the DB and zeros the publication slot. The same body later calls the Starfield teardown at `0x141882FA8`, checks the galaxy module pointer at `0x141882FD8` and invokes slot +0 at `0x141882FE9` before zeroing its pointer at `0x141882FEB`. The galaxy vtable `0x144D5FAC8` resolves slot +0 to `FUN_14231DDA0 → FUN_14231DA10`, which deregisters `PerBiomeData` at `0x14231DAFB–0x14231DB02`. This order applies to that shutdown continuation. The reset clear and Starfield destructor examined above leave the publication slot and registration in place through the shown operations. |
| HISTORICAL RUNTIME OBSERVATION | Earlier startup and menu-return captures | The locally verified startup report has return sites `0x141883DCE / 0x141894C93 / 0x14187FA14` in its startup loader stack. The separately pinned menu-return report directly witnessed `0x141897535` (data-handler reset) and `0x141897B19` (loader replay). Both use the pinned executable hash. These observations locate their sampled upstream work. The SRR-013 title sample measures retained output later in its own process. [Startup report][startup] · [Menu-return report][menu] · [Title samples](SRR-013-retail-title-paired-structural-observation.md) |

The same-build load-order callbacks, pending handler and application
service commands can reach reset conditional on the mode and receiver
read at dispatch. The signed reset path does not establish that an ordinary
Save2 load enters it. The known visual-demand receiver was previously
followed through its scene visit without a resolved edge to the allocator.
Exact flag execution, complete insertion visibility, title-epoch writes and
repeat counts need corresponding observations in a qualified epoch.
[SRR-011 limits](SRR-011-planetary-allocation-execution-and-result-lifecycle.md#lead-audit)

## Offline reproduction

The [tracked decoder](../tools/srr011/inspect_pe.py) verifies the hash,
machine and PE base on each invocation, reads only the supplied file and
prints to stdout. These commands were checked with CPython 3.14.3 and
Capstone 5.0.7. Set `$srrPython` to the interpreter and `$srrExe` to a
lawful matching image. No runtime process or Ghidra program was opened.
Listings and checks remain in ignored `.local-work/codex/SRR-014/startup/`.

```powershell
& $srrPython -B tools/srr011/inspect_pe.py $srrExe functions 141898870 141881660 1424059f0 14231d000 14189a970
& $srrPython -B tools/srr011/inspect_pe.py $srrExe functions 14187fea0 14187f9d0 14187fbd0 1418a1820 1428d8130
& $srrPython -B tools/srr011/inspect_pe.py $srrExe functions 141893ee0 141883440 141896280 141882bb0 1424063b0 1409518b0 140951c80
& $srrPython -B tools/srr011/inspect_pe.py $srrExe window 14189822b 29
& $srrPython -B tools/srr011/inspect_pe.py $srrExe window 1418a2ca0 8
& $srrPython -B tools/srr011/inspect_pe.py $srrExe functions 14008c050 140305fd0 1403061c0 140308070 140c80e60 140307fa0
& $srrPython -B tools/srr011/inspect_pe.py $srrExe data 144b65898 17
& $srrPython -B tools/srr011/inspect_pe.py $srrExe data 144afb328 68
& $srrPython -B tools/srr011/inspect_pe.py $srrExe data 144f678e0 18
& $srrPython -B tools/srr011/inspect_pe.py $srrExe data 1459bb140 18
& $srrPython -B tools/srr011/inspect_pe.py $srrExe window 1428cd500 69
& $srrPython -B tools/srr011/inspect_pe.py $srrExe data 1428cd56c 43
& $srrPython -B tools/srr011/inspect_pe.py $srrExe data 1428ce004 1c
& $srrPython -B tools/srr011/inspect_pe.py $srrExe window 1428cdbe0 430
& $srrPython -B tools/srr011/inspect_pe.py $srrExe functions 14094e3d0 14233f2c0 142340990 142340ab0 1407873d0
& $srrPython -B tools/srr011/inspect_pe.py $srrExe window 142340f40 1d0
& $srrPython -B tools/srr011/inspect_pe.py $srrExe scan 145ea5fe0 145ea5ff0 145ea5ff8 145ea6000 145ea6010 145ea6128 145ea6130
```

The scan covers file-backed .text VAs `[0x140001000, 0x143A3EF6C)`
using 236,427 unique exception ranges, with a separate exact-qword census of
the file-backed section extents. Its decoded relative-operand scope explains
why the object base needed examination. The result cannot rule out other
computed references. `functions` uses unwind ranges. `window` follows
selected checked instruction starts across split ranges.

The sibling startup and menu-return documents were read from their pinned
commits in local Git. Their respective blobs are
`b5e88cb244f303fe08088f5f65d9fae543f5e0a9` and
`6799d994d4cc2730909c55e2f708032f9798b1f0`.
The experiment reports support the historical association. The pinned PE
decodes independently support the code edges documented here.

[startup]: https://github.com/gooberpede/starfield-reference-handles/blob/7be6624893ef8a1abfdbbef7b50ed35e90b8f970/docs/experiments/pack-in-storage-reference-startup-construction.md
[menu]: https://github.com/gooberpede/starfield-reference-handles/blob/5dd46ff91d24761d9b67f4a25a07419c1e87bc0c/docs/experiments/subtype-3-menu-return-teardown-reconstruction.md
