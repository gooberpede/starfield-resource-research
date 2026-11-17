# SRR-011 — Planetary allocation execution and result lifecycle

## Executive conclusion

**PARTIALLY RESOLVED.** Static analysis connects the startup loader and
qualifying reset paths to the previously established construction-time
allocator. The allocator
writes directly into existing `BSGalaxy::CTPerBiomeData` payloads in a
context-owned index. A keyed reader copies a matching payload into caller
storage and returns false on a miss. Historical startup and menu-return
captures establish upstream execution. Actual allocator execution in those
captures or during an ordinary Save2 load remains unverified.

This applies to retail `Starfield.exe` file and product version
`1.16.244.0`, SHA-256
`7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28`,
preferred base `0x140000000`. All VAs and structure displacements below
refer to this image. The installed and existing analysis copies match.
The original investigation started at HEAD `4899e79a088ae655d1ff20c213cb939e00a3c4e0`,
with index-entry hash `43b89b01de93aa8ee060e69132d872080f97e2b4`.
The supplied brief was the only pre-existing untracked path.
See the [retail pin](PROVENANCE.md#current-retail-identity) and
[lead register](SRR-011-lifecycle-lead-register.md).

### What SRR-011 adds

| Evidence class | Findings and sources |
| --- | --- |
| Previously established | The allocator algorithm and retail mapping, the PNDT callback-to-orchestrator edges, and conditional module construction predate SRR-011. SRR-003 already mapped the state-0/state-1 switch and both direct module-entry calls at `0x141894CC3` and `0x141897B59`. The v1 scope and validation remain in force. [v1 baseline](v1-research-baseline.md) · [SRR-002 mapping](SRR-002-retail-static-reconnaissance.md) · [SRR-003 dispatch](SRR-003-retail-allocator-invocation-and-dispatch.md#native-path-and-predicates) |
| Previously established observation limits | SRR-005 defines the four-site causal join, and SRR-006 qualifies the observer on a disposable fixture. SRR-009 observed zero hits in 84.281 seconds of verified post-arming title/menu coverage. All four SRR-010 Save2 attempts ended before confirmed player control or scientific STOP. [SRR-005 contract](SRR-005-live-observation-preparation.md#sites-and-causal-join) · [SRR-006 qualification](SRR-006-four-site-hardware-observer.md) · [SRR-009 finding](SRR-009-retail-debugger-admission-and-stage-a.md#finding) · [SRR-010 disposition](SRR-010-stage-b-save-load-observation.md#final-disposition) |
| SRR-011 native findings | The file/group loader's normal return at `0x141894C93` can reach the known state-0 module-entry call. On the signed reset branch, context clear, teardown of the module guard and file/group replay can precede the known re-entry call. The guarded load-order dispatch supplies a conditional route into that reset. The collector at `0x14077BD2E–0x14077BE39` borrows indexed payload pointers. The matching reader copies at `0x14077200D`. Subsequent consumers, targeted removal, context clearing and type deregistration have separate native paths. [Invocation](#invocation) · [Result](#result) · [Readers](#readers-and-reuse) · [Invalidation](#invalidation-and-persistence) |
| Integration with earlier observations | The pre-existing sibling captures sampled startup loader frames and selected menu-return reset/replay calls. SRR-011 connects those sites to conditional static continuations toward allocation. Neither sibling capture measured the allocator join. [Startup capture][startup] · [Menu-return capture][reset] |
| Still unverified | Actual allocator execution at startup, on ordinary Save2 load, on demand, or multiple times in one epoch. Suppression of repeated generation on a lookup hit, actual context lifetime between game operations, and save or cross-process retention of all seven slots are also unverified. [Lifecycle hypotheses](#lifecycle-hypotheses) · [Lead audit](#lead-audit) |

## Invocation

| Route | Native relationship and predicate | Evidence boundary |
| --- | --- | --- |
| Initial loading route | The state-0 dispatch call at `0x14187FA0F` reaches `FUN_141893EE0`. Its loader call at `0x141894C8E` returns at `0x141894C93`. Three calls intervene before the direct module entry at `0x141894CC3`, with no intervening intra-function conditional branch. | **PROVEN STATIC** continuation. **STRONG** startup association. A same-build [sibling startup observation][startup] captured return VAs `0x141883DCE`, `0x141894C93` and `0x14187FA14` on the startup file/group-load stack. That sampled earlier work in the same ancestry. |
| Reset with file/group replay | The diagnostic reference at `0x14189648B` identifies the `PerformGameReset` context of `FUN_141896280`. At `0x141897167–0x14189716B` a nonnegative signed receiver byte +0x2E jumps around this reset/replay/reconstruction branch. In the admitted branch `0x141897557` calls `FUN_140951C80`, which clears `[0x1461E2288]` at `0x140951CDD`. The same branch calls the loader at `0x141897B19` and module entry at `0x141897B59`. | **PROVEN STATIC** route allowing construction again. The [sibling menu-return observation][reset] captured the reset call at `0x141897535` and loader replay at `0x141897B19` in the selected menu-return scenario. Allocator and guard state were outside those captures. |
| Save-load order callbacks | RTTI at `0x14519B758` and `0x14519B7D0` identifies the receivers of the slots at `0x144CAFA08` and `0x144CAFAD0` as `LoadGameDifferentLoadOrderCallBack` and `LoadGameLoadOrderFromInactiveOrMissingCallBack`. Relevant arms write `0x84` to the shared receiver's +0x2E at `0x141840EE0` and `0x14183DFAB` and call `FUN_141896020`. Its `0x84` path waits/drains and dispatches state 1, which can reach `FUN_141896280` at `0x14187FB9B`. It loads the receiver anew at `0x14187FB94`. If the mode remains `0x84`, it meets the signed-negative predicate. The dispatch helper handles `0x85/0x86` through the direct call at `0x1418961D9`. | **PROVEN STATIC** conditional save-related route. The RTTI and state write identify a load-order-dependent operation. The controls establish scoped Save2 load outcomes. They leave selection of this native reset arm, mode by dispatch time and actual allocator execution unresolved. |
| Construction and PNDT dispatch | Zero qword at `0x1461E2288` enters construction through the branch at `0x140951904`. The optional sweep at `0x14094E577` requires nonzero byte `[0x145EA6000]`. Both flag paths can reach the later sweep at `0x14094EF57` on normal continuation. Each passes the stack receiver with vptr `0x144B3D9E8` to `FUN_140593280`. Nonempty type-0xBA bucket and non-null entry reach slot +0x10 at `0x1405932EF`. The callback tests PNDT type, then reaches the adapter at `0x14077C482` and orchestrator at `0x1407796D2`. | **PROVEN STATIC.** `0x144B3D9F0` and `0x144B3D9F8` contain the same callback pointer. This iterator reads the latter. `0x1485F1500` is a PE exception row giving begin, exclusive end and unwind-info RVAs `0x77C470/0x77C491/0x541CC78`. [SRR-003 predicates](SRR-003-retail-allocator-invocation-and-dispatch.md#native-path-and-predicates). |
| Per-biome work | The orchestrator reads the PNDT key at +0x54 and seed at +0x50. The collector returns on zero key or no matching work, and the loop bypasses `0x140779C86` when its work range is empty. A zero seed changes reseeding within the loop. | **PROVEN STATIC.** Entry to the orchestrator alone cannot show a per-biome write. |

Clearing the module pointer enables another sweep in the same process.
A populated bucket, admissible PNDT and matching
component entries are independent prerequisites to later recomputation.
A miss in the result lookup below has its own return path.

The two load-order callbacks return early on callback argument
`DL == 0xFF`. Their mode-0x84 arms require `DL == 0` and
zero pending-load byte +0xC1C, tested at `0x141840E82` and
`0x14183DF4F`. Nonzero +0xC1C instead sets pending state +0xC10
to `0x20` and writes control mode `1` or `0x82`. A separate
pending-load handler, `FUN_141852410`, tests that state at
`0x141852E61`, writes mode `0x84` at `0x141852E80` and
calls the dispatcher at `0x141852E84` on the admitted path.

The application startup driver supplies a second verified ancestry.
`0x14365D891` calls `FUN_1418814C0`, with continuations through
`0x14188155B`, `0x14189A80C` and `0x1418A257E` to
`FUN_1418A37C0`. This driver reaches `FUN_14189A970` inline at
`0x1418A3A34` or through installed command vptr `0x144CB2AD0`,
slot +8, at `0x1418A3C70`. The path to `0x14189ABB4` calls the
same initial loader under the optional byte guard through
`0x14591AC00` or the three byte guards through `0x14591AC20/40/60`.
The PE entry in `.bind` uses an unresolved computed transfer.

The [sibling load-readiness map][load] identifies a first-transition wait
before the ordinary manual-load arm. `FUN_1418501B0` tests pending
+0x50 against mask `0x40D4` at `0x141850226`. The wait route through
`0x141850266` enters `FUN_141898210`, which checks the latch at `0x14189821E`.
The unset-latch branch calls `FUN_14187FBD0` at `0x141898237`.
When a worker control exists it waits on the same handle field
signaled by state 0 at `0x14187FB52`, after initial loading returns.
The set-latch branch skips this wait. The manual-load branch tests
mask `0x4` at `0x1418507AB` and calls into load handling at
`0x1418507CF`. Within the nonzero mask arm, the alternate at
`0x14185022D–0x141850252` requires dword `[0x145F42700] == 2`,
byte `[0x145F42720] != 0`, a non-null pointer in `[0x145E60E98]`
and nonzero byte at that pointer +0x13FE30. All four passing writes
mode `0x86` at `0x14185025B` and leaves the direct path. This
supplies a conditional ordering relationship between startup and load
admission.

The application loop also schedules reset processing.
`FUN_14189D520` exits this region for nonzero +0x28 at
`0x14189D80B`. The arm for +0x2E and byte `[0x145E71718]`
both nonzero at `0x14189D815` and `0x14189D81F` enters the
wait/counter block before scheduling.
It passes callback `0x141884330` at `0x14189D96D`.
`FUN_1418A2D60` can call it inline at `0x1418A2FDC`, or queue
vptr `0x144CB2BE8` slot +8, whose method calls the captured pointer
at `0x1418A3FB5`. The captured thunk jumps to `FUN_141896020`.
Another command path at `0x14189DC08` requires nonzero byte
`[0x145E6D67A]` at `0x14189DBB9`, uses thunk `0x141884340`
and eventually writes mode `0x85` at `0x1417C6B86` before entering
the dispatch helper. Those edges establish mode handling independent of
the two load-order callback bodies.

The registered `CreateViewEvent` receiver supplies a demand-side
control. Module-state construction registers its +0x10 subobject at
`0x1409519B6`. Table `0x144B66650` slot +8 binds `FUN_14094F010`,
which gates on event +0x20 equal to 2. Its resolved visitor is
`FUN_142396D80` through vtable `0x144D64438` slot +0x10. This is
a scene-object walk with nested virtual receivers. The verified
functions contain no direct edge to the focal dispatcher.

### How the guarded routes fit together

Arrows in the diagram show conditional static reachability. The separate
historical samples below it establish execution only at the named upstream
sites. The [native route table](#invocation) gives the call and branch VAs.

```text
Load-order callback arm -> mode 0x84 -> state 1 --------+
Dispatch helper reads mode 0x85 or 0x86 ----------------+
                                                       v
Reset receiver signed +0x2E < 0 -> clear context, teardown, replay
                                   and continue to module entry -+
State 0: initial loader returns -> continue to module entry -----+
                                                                 v
                                            module pointer zero?
                                              |              |
                                             yes             no
                                              v              v
                                   construct module     bypass construction
                                              |
                    flag nonzero: optional PNDT sweep
                    flag zero:    skip early sweep
                                              |
                          either path can continue to later PNDT sweep

Either sweep -> nonempty bucket -> non-null entry -> type 0xBA
             -> adapter -> orchestrator -> nonempty collected work
             -> per-biome writer (individual writes remain conditional)

Historical startup sample: loader frames before module entry.
Historical menu-return sample: reset and file/group replay calls.
Allocator entry and slot writes were outside both captures.
```

The following pseudocode is a conceptual reconstruction. Ellipses omit
unrelated work or branches. Calls within a path are shown on normal
continuation. The [native route table](#invocation) and the [SRR-003
dispatch predicates](SRR-003-retail-allocator-invocation-and-dispatch.md#native-path-and-predicates)
identify the evidence for this sequence.

```text
state_0():
    initial_loader()                              # 0x141894C8E
    ...                                           # three intervening calls
    enter_module()                                # 0x141894CC3

enter_module():
    if qword[0x1461E2288] == 0:                    # 0x140951904
        publish_module_pointer_and_install_vptrs()
        construct_module()                        # 0x1409519BE
    continue_module_entry()                       # 0x140951A3C

construct_module():
    if byte[0x145EA6000] != 0:                     # 0x14094E542
        sweep_pndt_bucket()                        # 0x14094E577
        ...                                       # calls and loops
    ...                                           # common tail, both branches
    sweep_pndt_bucket()                            # 0x14094EF57

sweep_pndt_bucket():
    for entry in counted_type_0xBA_bucket:
        if entry is null:
            continue
        # Native iterator dispatches vptr slot +0x10 at 0x1405932EF.
        # Its resolved callback tests entry +0x2E and returns 1.
        if byte[entry + 0x2E] == 0xBA:
            adapter_calls_orchestrator(entry)      # 0x14077C482, 0x1407796D2
            # A zero key produces no collected work. An empty work range
            # bypasses the per-biome call at 0x140779C86.

reset(receiver):
    if signed_byte[receiver + 0x2E] < 0:           # 0x141897167–0x14189716B
        ...
        clear_context_indexes()                   # 0x141897552
        teardown_module()                         # clear nonzero guard at 0x140951CDD
        ...
        replay_file_group_loader()                # 0x141897B19
        enter_module()                            # 0x141897B59, guard tested again
    ...                                           # other reset work
```

The callback cases below apply to both named load-order callbacks and the
separate pending-state handler. The alternate load-admission arm leaves
the direct load path after setting a mode. Its subsequent dispatch is
conditional. See the [callback and load-admission checks](#invocation).

```text
load_order_callback(DL):
    if DL == 0xFF:
        return
    if DL == 0:
        if byte[pending + 0xC1C] == 0:            # 0x141840E82, 0x14183DF4F
            ...
            set_receiver_mode(0x84)                # 0x141840EE0, 0x14183DFAB
            dispatch()
        else:
            pending.state_at_0xC10 = 0x20
            set_receiver_mode(1 if dword[0x145F42700] == 0 else 0x82)
    ...                                           # other callback work

pending_handler_on_tested_arm():
    if pending.state_at_0xC10 == 0x20:            # 0x141852E61
        ...
        set_receiver_mode(0x84)
        dispatch()                                # 0x141852E84

dispatch():
    ...                                           # earlier dispatcher work
    mode = byte[receiver + 0x2E]                   # reread at 0x1418961AE
    if mode == 0x84:
        wait_or_drain_then_dispatch_state_1()
        # State 1 reloads the receiver before calling reset at 0x14187FB9B.
    else if mode in {0x85, 0x86}:
        reset(receiver)                            # 0x1418961D9
    ...

load_admission_on_tested_arm():
    if (pending.flags_at_0x50 & 0x40D4) != 0:     # 0x141850226
        load_state = pointer[0x145E60E98]
        if dword[0x145F42700] == 2 and byte[0x145F42720] != 0
           and load_state != null and byte[load_state + 0x13FE30] != 0:
            set_receiver_mode(0x86)                # 0x14185025B
            leave_direct_load_path()
        else:
            check_readiness_latch_and_wait_if_required() # 0x141850266
    ...                                           # manual load has its own gates
```

## Result

**PROVEN STATIC.** At `0x140779676` the adapter loads the context
pointer from `[FUN_1423FF640() + 0x8B0]`. It saves that pointer at
`[rsp+0x88]` at `0x1407796BA` and passes the address of the
saved slot to the orchestrator at `0x1407796C2`.
`FUN_14077BCE0` dereferences that argument at `0x14077BD2E`. Its lookup at
`0x14077BD31–0x14077BD63` uses the tree at context +0x300 and a range
of key pairs. The first word is
`(uint64(PNDT_key) << 32) | uint16[0x1461DFA4C] | 0x10000`.
The first pair uses a zero second word and the upper comparison uses
`0x0000FFFFFFFFFFFF`. The collector's payload pointer is
`block + uint16[block + 4*slot + 0x12] + 0x20` at
`0x14077BDA5–0x14077BDB1`. It appends that exact pointer at
`0x14077BE39`. The orchestrator shuffles these borrowed pointers.

In the authored-input path, `FUN_14076EC00` sets PNDT +0x54 to its
FormID at `0x14076EC81–0x14076EC86`. Its PPBD tag compare at
`0x14076ED5C` admits the read of the component inputs. The stack
payload's seven resource slots are explicitly zero at
`0x14076EEED–0x14076EEF6` and the successful path queues creation
at `0x14076F360`, with planet FormID and payload BIOM ID as
owner and target. This reads authored biome inputs and establishes
the pre-allocation values of the result slots on that path.

The constructor's optional branch calls the `Space\BiomeData.csv`
loader at `0x14094E608`. Its buffered component rows explicitly zero
the seven slots at `0x142340535–0x14234053F`. The two flush sites
`0x14234044C` and `0x14234059C` reach the accepted-row submission
at `0x14234103A → FUN_140773BE0` through
`FUN_142340990 → FUN_142340AB0`. The latter checks a separate
component discriminator `0x1461E1D90`. This route can replace or
supply inputs ahead of the later sweep. Its parser supplies zeroed
resource slots.

| Storage | Native observation |
| --- | --- |
| Inline edge payload | The registered discriminator references the name `PerBiomeData` at `0x144D5F0A0` via `0x14231D7D9–0x14231D7E0`. The command vtables at `0x144B3D4E0` and `0x144B3D4A0` resolve through RTTI to `CreateAndDeleteCommand`, `EdgeKey` and `BSGalaxy::CTPerBiomeData`. `FUN_140774E00` passes the captured key/payload at `0x140774E39` to `FUN_1407766B0`, which inserts a 0x90-byte entry, stores the key at entry +0x10 and invokes the component copy at `0x1407767A4` into entry +0x20. |
| Inputs and generated fields | Payload +0x40 supplies the BIOM key. +0x4C conditionally resolves an RSGD input. Seven uint32 generated slots begin at payload +0x50. Common occupies five slots through +0x60, Special is +0x64 and Everywhere is +0x68. At `0x140779AF5–0x140779B2E` the orchestrator clears these fields on each collected pointer before the Everywhere write and per-biome allocation. The copy helpers `FUN_14076E720` and `FUN_14076E810` include all seven fields at `0x14076E7D9–0x14076E7F2` and `0x14076E86A–0x14076E886`. |
| Scratch state | The list of work pointers, family-configuration pointers and shared resource IDs has stack headers and normal-return cleanup. The family pointers alias the Common slots within the work objects. The shared ID array includes prepopulation used by generation. The shown allocation path delivers output through the original component aliases. A separately retained planet-wide vector representing those shared IDs has not been established. |
| Other component store | `FUN_142322520` uses the same registered type with a distinct key encoding in the context +0x268 tree and supports typed insertion/replacement. The edge-insert notification at `0x1407767C1` dispatches a key through `FUN_142406B70` and the callback at `0x14240F659`. A slot-copy join to the generated edge's identity is missing. The allocator also queries +0x268 at `0x140779CD7` using the separate discriminator `0x1461E1D90`. A hit gates numerical adjustments to payload +0x44, including the write at `0x140779DBF`. That post-loop path concerns biome coverage. |

### How the writer and reader share storage

The diagram gives offsets from the context, one indexed edge record,
or its inline payload. The [native storage table](#result) identifies the
entry construction and write sites. [Readers](#readers-and-reuse) and
[invalidation](#invalidation-and-persistence) identify the copy and teardown
sites.

```text
Context +0x300 -> keyed index -> one retained 0x90-byte edge
  Edge +0x10: key
  Edge +0x20: inline BSGalaxy::CTPerBiomeData
    Payload +0x40: BIOM key
    Payload +0x4C: optional RSGD key
    Payload +0x50..+0x60: five Common IDs
    Payload +0x64 / +0x68: Special / Everywhere IDs

  Writer: call-local list of borrowed pointers
            -> clear and conditionally write those retained slots in place
  Reader: planet range + matching BIOM
            -> copy payload to caller storage
            -> selected-ID check / reference filter

  Targeted removal -> selected +0x300 edge range
  Context clear    -> +0x268 and +0x300 trees

BSGalaxy::ModuleState registry teardown -> type entries and type word
```

The inspected PPBD, ENAM-associated and CSV builders initialize the seven
slots to zero. A reader hit can therefore copy default-zero fields as
well as fields already written by generation. The conceptual writer and
reader below follow the [collection and mutation sites](#result) and the
[copy and miss exits](#readers-and-reuse).

```text
write_planet(form, address_of_saved_context):
    context = *address_of_saved_context           # 0x14077BD2E
    work = collect_borrowed_payloads(context + 0x300, form.key_at_0x54)
        # No collected entries on zero key or missing range.
        # Appends the existing payload pointers at 0x14077BE39.
    ...                                           # shuffle work pointers
    prepopulate_call_local_shared_ids_from_atmosphere()
    for payload in work:
        clear_all_seven_slots(payload)            # 0x140779AF5–0x140779B2E
        try_everywhere_selection(payload)         # category-6 pass
    for payload in work:
        ...                                       # reseed if planet seed is zero
        run_per_biome_allocator(payload)          # 0x140779C86
        # BIOM and RSGD tests and selection inside this routine govern writes.
    ...                                           # post-loop work
    release_call_local_work_and_scratch()

read_biome(context, planet_key, biome_key, caller_output):
    if planet_key == 0:
        return false                              # 0x140771F8B
    for edge in planet_range(context + 0x300, planet_key):
        if edge.payload.biome_key_at_0x40 == biome_key: # 0x140771FB6
            copy_payload(caller_output, edge.payload)  # 0x14077200D
            return true
    return false                                  # missing range or unmatched BIOM
```

The writer's pointer list, shared resource IDs and Common-family pointers
are call-local scratch. The context retains the payloads. The reader's
copy exits belong to a separate path.

### Readers and reuse

`FUN_140771F30` looks up the same +0x300 planet range through
`FUN_1405F7A80` at `0x140771F4F`. It scans for a matching BIOM key
at `0x140771FB6`. On a hit it calls `FUN_14076E810` at
`0x14077200D` to assign the component to caller-provided storage
and returns true. A zero planet key, missing range or unmatched BIOM
returns false at `0x140771F8B` or `0x140771FFD`. This is reuse of
stored data by lookup. The reader has no conditional generation on its
miss branch, and the batch writer clears and recomputes the fields without
testing for a retained result.

The hit path of `FUN_1407BA9B0` reads a selected slot at
`0x1407BAAF2` and uses a nonzero value in setting a caller byte at
`0x1407BAB12`. `FUN_1407BD270` tests all seven slots from index 6
to 0 at `0x1407BD701` while filtering its reference entries.
`FUN_14086A6D0` reads the slot range from its copy and resolves
selected IDs with `FUN_1405DE3B0`. These joins follow the actual stack
outputs passed in R9. In two inspected calls in `FUN_1413072A0` and
`FUN_141307BC0`, apparent matching positive RBP offsets instead
belong to a different frame region than the component passed in R9.
Those instructions do not establish a slot reader.

The [sibling input-provenance study][inputs] identified a temporary
root-to-array map under `FUN_1407BC300 → FUN_1407BC3D0`. This path
collects derived relationships from the same planet edge range
through `0x1407BC40D → FUN_1405F7A80`. The loop at
`0x1407BC480–0x1407BC666` stages the nonzero values from all
six slots following the Common root. A nonzero root selects the
map entry for a swap at `0x1407BC669–0x1407BC6FA`. The caller
`FUN_14079B520` supplies its temporary map at `0x14079B920` and
resolves IDs from it at `0x14079BC52–0x14079BC67`. This derives
per-request relationships from the stored slots.

The sweep immediately following each generation sweep is a useful control.
`FUN_14077B1D0` enters `FUN_14077A700`, which dispatches receiver
`0x144B3DA08` to `FUN_14077C450` via the same iterator. Its helper
`FUN_14077D090` walks the same per-planet range but collects payload
+0x40 at `0x14077D165–0x14077D174`. The caller resolves each collected
ID as a type-0xA0 BIOM at `0x14077A9D0–0x14077A9ED`. The later
job installation at `0x14077AFFA–0x14077B027` passes BIOM metadata
and a key using `word[0x1461E1DAC]`. The installed callback reaches
`FUN_14077D400` through `FUN_14077D800` and `FUN_14077D1C0`.
This path starts with BIOM identities. The separate final PNDT sweep
through `FUN_14077C4A0` branches at `0x14077C4A9` to `FUN_140778600`.
Its range query at `0x14077870C → 0x14077B92C` opens a different
edge discriminator `0x1461E1D9C` and copies 24 bytes per matched entry
at `0x14077BA3F–0x14077BA4D`.

### Invalidation and persistence

`FUN_140774970` selects a range for this discriminator and calls
`FUN_142409490` at `0x1407749BF`. The latter calls the range eraser
at `0x142409682` and then publishes a change at `0x142409691`.
The queue helper `FUN_140772EE0` reaches this removal through its
captured callback `FUN_140776680`. Its callers include the PNDT ENAM
path at `0x14076F751`, the PNDT destructor body at `0x14076E9EA`
and the PNDT primary vtable's +0x80 method at `0x14076EB83`.
ENAM-associated inputs can then be queued at `0x14076FCEA` and start
with zeroed result slots. The edge eraser calls the wrapper's virtual
destructor before compacting a multi-entry block. For the PerBiomeData
edge, slot +0 of vtable `0x144B3D258` maps to `FUN_140777810`,
which calls `FUN_14076E8A0` for payload teardown at `0x140777823`.
This provides an explicit path for dropping indexed payloads, distinct
from recomputing their output fields in place. In the signed reset
branch, the context helper at `0x141897552` also calls
`FUN_1424063B0`. That function clears the receiver's +0x268 and +0x300
trees via the calls at `0x1424063DB` and `0x14240640C` before the
module teardown call in the outer path. The reset path obtains the
same context source `[FUN_1423FF640() + 0x8B0]` at
`0x141897546–0x14189754B`. The clear helpers release
entries and zero their tree headers. A separate TES destructor route
reaches the same context clear at `0x140574286`. An end-to-end
observation of the same context and component across reset is missing.

There is also a type-registry teardown. Vtable `0x144D5FAC8` has
locator `0x1452CF788` for native `BSGalaxy::ModuleState`. Its
destructor slot +0 reaches `FUN_14231DA10` from `0x14231DDAF`.
At `0x14231DAFB–0x14231DB02` that body passes the PerBiomeData
discriminator's address to `FUN_1424058B0`. This helper clears
24-byte-indexed registry fields at `0x142405910` and `0x142405923`
and zeroes the discriminator at `0x142405927`. This branch disposes
of type registration. The +0x300 payload destruction is established
by the range and context erasers above.

The primary PNDT vtable at `0x144B3D638` binds +0xD0/+0xD8 to
`FUN_1405DF980` and `FUN_1405DFA40`. The decoded direct save/changeform
handlers use identity and flag operations. Their optional PNDT
slot +0x230 getter resolves to a null-returning function. The
[sibling Save52 save-unit audit][saves] independently identified a different
discriminator in Global Unit 6. The clear prefix at `0x14182E2F2` and
first typed reader at `0x1424B5DCE` use `0x1461DD824`.
The function installed at vtable `0x144CAE268` slot +0x10 accesses
a context ID through the erased callback, as can be checked at
`0x14182F590`. These positive receiver and field distinctions
bound the evidence against a direct stored slot image in the
inspected routes. A complete save streaming or arbitrary external
callback search was outside the eligible native slice.

## Cache and persistence semantics

| Behavior | What the evidence supports |
| --- | --- |
| Writable results retained in memory | **PROVEN STATIC.** The writer changes the existing context-owned payload through a borrowed pointer. Releasing the temporary list leaves the indexed payload in place. Targeted removal and context clearing can end that lifetime. Type deregistration clears registry metadata through a different path. [Storage](#result) · [Invalidation](#invalidation-and-persistence) |
| Later lookup and copied reuse | **PROVEN STATIC.** The reader matches the planet range and BIOM key and copies the component, including its seven resource slots. Payload identity establishes a hit even when the slots hold default zeroes. [Readers and reuse](#readers-and-reuse) |
| Lazy generation on a miss | **Scoped exclusion.** A zero planet key, missing range or unmatched BIOM returns false in `FUN_140771F30`. Other demand paths remain possible. [Reader exits](#readers-and-reuse) |
| Suppression of repeat generation | **Unverified.** The module-pointer guard can bypass construction. When the focal writer reaches its slot pass it clears existing slots without using a previous result as a skip condition. There is no demonstrated link from a keyed lookup hit to suppression of later allocation. [Native invocation](#invocation) · [Writer and reader](#how-the-writer-and-reader-share-storage) |
| Persistence through save or process boundaries | **Unverified.** The inspected input builders initialize slots to zero, and the examined direct save/changeform and sampled save-unit paths lack a matching slot-image handoff. A different source or serializer remains possible. The in-memory copy establishes neither serialization nor cross-process lifetime. [Persistence evidence](#invalidation-and-persistence) |

## Lifecycle hypotheses

| Candidate | Affirmative evidence, counterexample and missing discriminator |
| --- | --- |
| Startup allocation | **STRONG** association of the constructor caller with the sampled startup loader, with a **PROVEN STATIC** conditional continuation. A populated module guard or empty eligible work can still bypass allocation or its inner writes. SRR-009's 84.281 seconds of verified post-title coverage begin after arming. A joined pre-title constructor-to-write trace would establish actual execution in that epoch. |
| Save-load generation or restoration | The load-order callback chain and signed reset branch can reach reconstruction. Connection to ordinary Save2 selection remains unestablished. All four SRR-010 observations ended without a complete scientific window. Control A reported ordinary load success and B observed settled gameplay under debugger-only attachment with no allocator sensitivity. A qualifying Save2-specific reset/generation or serializer-to-component join would distinguish routes. [SRR-010 disposition](SRR-010-stage-b-save-load-observation.md#final-disposition). |
| On-demand, first access or event trigger | The verified result reader can answer a keyed request and miss without generation. The batch constructor can execute independently of that read. Any distinct event-triggered allocator route needs a resolved edge and its guard. Gameplay paths can coexist with batch construction. |
| Process- or object-local retention and reuse | **PROVEN STATIC** same indexed component is writable by generation and copyable by a later lookup. A module reset admits repeated construction. A result miss in the covered reader returns failure. The exact owner epoch across game operations and any separate fill-on-miss path remain unresolved. |
| Persistent or shipped/precomputed allocations | The scoped PNDT and CSV producers initialize the slots to zero. Direct PNDT save/changeform and sampled Save52 unit-6 alternatives operate on other fields and types. Copies can carry initialized fields in memory. A separate typed serializer or other producer remains possible and requires a byte-stream or authored-record join to the same payload. |

The startup, reset and storage claims are compatible with each other.
Historical reference-handle initialization and file replay qualify
upstream operations independently of any resource write. SRR-009 and
SRR-010 retain their original observation scope and dispositions.

## Verification and evidence custody

The [PE reader](../tools/srr011/inspect_pe.py) reads the executable as
data and writes to stdout. It checks SHA-256, AMD64 PE32+ and the
preferred base before analysis. No Ghidra project is needed for this
route. The qualified environment used Python 3.14.3 x64, Capstone 5.0.7
and Git 2.53.0.windows.1. The commands take preferred VAs and a
hexadecimal byte count for `window` and `data`. Send any optional
output redirection to the ignored SRR-011 scratch directory.
Set `$srrPython` to a CPython executable with Capstone 5.0.7 already
installed and `$srrExe` to the matching readable retail image. Use
the resolved interpreter path if Windows exposes a Store alias.

```powershell
& $srrPython -B tools/srr011/inspect_pe.py $srrExe scan 140779760 140777870 140779610 14077C470 144B3D9E8 140778600 14077D090 14077B1D0 14077A700 14077B910 145EA6000 1461DFA4C
& $srrPython -B tools/srr011/inspect_pe.py $srrExe scan 140771F30 1424063B0 142409490
& $srrPython -B tools/srr011/inspect_pe.py $srrExe functions 140779760 14077BCE0 140777870 140771F30 140774970 142322520
& $srrPython -B tools/srr011/inspect_pe.py $srrExe window 140771F98 97
& $srrPython -B tools/srr011/inspect_pe.py $srrExe window 14077C4A0 10
& $srrPython -B tools/srr011/inspect_pe.py $srrExe window 1405E5BF0 8
& $srrPython -B tools/srr011/inspect_pe.py $srrExe data 144B3D9F0 10
& $srrPython -B tools/srr011/inspect_pe.py $srrExe data 1485F1500 C
& $srrPython -B tools/srr011/inspect_pe.py $srrExe functions 141893EE0 141896280 140951C80 1409518B0 1424063B0
& $srrPython -B tools/srr011/inspect_pe.py $srrExe functions 141840E60 14183DF10 141896020 14187F9D0
& $srrPython -B tools/srr011/inspect_pe.py $srrExe window 141898210 117
& $srrPython -B tools/srr011/inspect_pe.py $srrExe functions 14231DA10 14231DDA0 1424058B0
& $srrPython -B tools/srr011/inspect_pe.py $srrExe data 144D5FAC0 10
```

The first scan returned 32 candidate byte positions and 20 distinct
decoded references, plus the two callback pointers. It covers the
file-backed intersection with virtual `.text`, VA
`[0x140001000, 0x143A3EF6C)`, and verifies operands using a decode
from the latest preceding containing exception entry among 236,427
unique ranges. Candidate predicates cover E8/E9 and 0F 80–8F
rel32 branches, plus ModRM mod=00/rm=101 RIP references with zero to
four trailing bytes. Exact qwords are searched across file-backed
section extents. Two candidates fell outside selected ranges. One
is the known `0x14077C4A9` conditional tail branch, independently
decodable from the leaf at `0x14077C4A0`. The other candidate is
inside a leaf whose actual two-byte read is from `0x1461DFA48`.
The second scan found 19 verified candidates from 19 byte
positions, including 11 reader calls, two context-clear calls
and six generic range-erase calls. It found no matching qwords.
Short branches, computed
addresses, dynamic dispatch and unrecognized decodes limit negative
conclusions. Exception ranges are decode boundaries and can divide a
single function body, as at `0x140771F98`. The explicit window
continues from that checked instruction.

For an independent walk of the result, confirm the collector's
`add 0x20` and pointer append, follow the call from the orchestrator,
and compare the slot math in the reader. At a match, verify that
`FUN_14076E810` reads the allocation offsets and assigns to the
caller-provided component. As negative controls verify both the
no-generation miss and the adjacent BIOM-key reader. The RTTI names
can be reconstructed from the vtable's preceding complete-object
locator pointer. The locator type descriptor is image-relative at
locator +0x0C, and the decorated ASCII name begins at type descriptor
+0x10. The locator width, compiler convention and address identities
are those of the pinned retail PE.

The registry control should show the destructor's direct call at
`0x14231DDAF`, the type word passed by address at `0x14231DAFB`,
and the low-width zero at `0x142405927`. Compare that with the
edge-slot destructor and tree clear in the preceding teardown section.

For the early-sweep flag, the native census tested exact RIP
references and qwords, plus a separate neighbor-address query
from `0x145EA5FF0` through `0x145EA6010` at selected byte
offsets in the same decoder scope. The saved-xref check in
Ghidra 12.1.2 PUBLIC used an existing matching program with
`-readOnly -noanalysis` and the sibling `OutpostRecon.java`
at `d116bc63ff394b0156539161c8d1addfc902665a`. It corroborated
the single consuming comparison at `0x14094E542`. The PE maps
the flag as zero-filled data. Actual runtime value and assignment
remain unresolved. Ghidra project file hashes matched before and
after that query.

The startup and menu-return associations additionally depend on
historical, same-build evidence from the sibling reference-handle
repository. The outpost repository supplies prior native
interpretations and the scoped Save52 audit. The linked revisions
were inspected in their local Git repositories. The task ran offline
and remote availability was untested. The core
native route and result claims can be reproduced with this tree and
a lawfully obtained matching PE. Native listings, scratch,
historical captures and executable bytes remain in their existing
local custody. The evidence grades for actual retail allocation
timing and persistence remain open. These claims stay on publication
hold as actual invocation or serialization findings.

The upstream and downstream handoffs recorded focused listings, failed
candidates and prior-source pins. The verification covered input identity,
stage boundaries, Git state and byte-exact patch replay. The task patch
excluded the pre-existing brief and prior evidence. No Git staging, commit,
push or publication occurred.

## Lead audit

The [lead register](SRR-011-lifecycle-lead-register.md) reconciles the
upstream and downstream traces, the adjacent sweeps and the challenger’s
registry-destruction finding. The verified paths distinguish authored
inputs, in-place generated slots, per-call scratch and per-request
derived data. Open leads require a specific missing join, such as a
runtime flag writer, the actual Save2 mode and allocator chain, an
indirect notification receiver linked to both stores or a typed
serializer. The reported search scope leaves these blocked and
supplies a discriminator for each. The sibling contexts and the
negative controls do not establish invocation frequency.

### What remains blocked

| Lead | Evidence obstruction and what would resolve it |
| --- | --- |
| U04 · Early-sweep runtime flag | The exact-address and neighboring native scans and saved Ghidra references locate a reader, while the PE gives only the initial zero. A resolved writer alias or a separately authorized observation of the write would establish its origin. |
| U05b · Ordinary Save2 branch attribution | The incomplete load windows and viability controls lack a qualifying join from the selected request to the callback/mode and allocator. Static guards identify possible routes but cannot supply Save2's actual receiver state or branch choice. |
| D03a · Computed result in the +0x268 store | The typed copy preserves the slots and the notification dispatches a key. A concrete callback receiver and matching source and destination identities are missing, so the evidence cannot connect the generated edge to the other store. |
| D07b · Cross-load persistence | The historic component-read capture was unavailable at its recorded paths. The inspected save and copy routes provide no paired slot image or typed serialization handoff. A serializer dispatch tied to this payload or attributable paired evidence for the same component key would discriminate persistence from recomputation. |

These are the recorded blocks in the [lead register](SRR-011-lifecycle-lead-register.md).
Other open questions are scientific uncertainties. For example, a startup
invocation would predict a joined loader-to-construction path, a qualifying
PNDT and a write to a collected payload in the same epoch. Frequency and
actual owner lifetime require evidence across measured operations. The
bounded exclusions in D06/D07/D08 and C01/C02/C03 concern the inspected
paths and candidates. They leave other callbacks, demand paths and
serializers open.

## Research implications

The static evidence strengthens startup and reset reachability and
identifies the retained write target and a separate copy-out path. A
reader can reuse the current payload without triggering generation.
Other on-demand entry points remain possible.

SRR-010 remains **CLOSED — INCONCLUSIVE; RESUMABLE**. All four
Save2 attempts with the four-site observer ended before confirmed player control or
scientific STOP. Ordinary Save2 branch selection and actual allocator
execution are still unverified. The continuation recommends no new
runtime run. A future proposal would need fresh evidence of a specific
trigger, a qualified observation spanning the relevant branch and
allocator or payload operation, and separate approval under the
[SRR-010 resumption gate](SRR-010-stage-b-save-load-observation.md#resumption-gate).

<!-- review-status:start -->
## Review status

**COMPLETE.** The independent internal challenger accepted AC1–AC8
for the revised substantive snapshot. Round 1 identified the missing
PerBiomeData registry-destruction lead and requested tighter load-mode
predicates and adapter indirection. Round 2 verified the corrected
native claims, lead dispositions, retail identity, historical evidence
boundaries and nine-file patch replay. Review is scoped to the pinned
offline evidence and the stated runtime gaps.

Reviewed manifest SHA-256
`59a2bd41d632b0eeb87559cd7036c441ddc765d813cfd07ed4501ca0127c86b9`.
Each line records the file SHA-256, two spaces and the repository-relative
path, followed by LF in sorted path order. The dossier hash excludes
only this marked review-status block.
<!-- review-status:end -->

<!-- documentation-review:start -->
## Documentation continuation review

**READY FOR SRR-011 DOCUMENTATION ACCEPTANCE.** The independent challenger
accepted DC-01–DC-08. Review tightened attribution of the previously mapped
module-entry calls, marked the executive finding as static and added
representative consumers to the storage figure. The original scientific
review above applies to its own snapshot.

Continuation manifest SHA-256
`0c6165c7a8102c44eed1c770ba8a8bd26750328ce07d04ddd6082066b14ae7c1`.
The manifest hashes the dossier with only this marked continuation block
excluded. The original review block is part of the hashed content.
<!-- documentation-review:end -->

[startup]: https://github.com/gooberpede/starfield-reference-handles/blob/7be6624893ef8a1abfdbbef7b50ed35e90b8f970/docs/experiments/pack-in-storage-reference-startup-construction.md
[reset]: https://github.com/gooberpede/starfield-reference-handles/blob/5dd46ff91d24761d9b67f4a25a07419c1e87bc0c/docs/experiments/subtype-3-menu-return-teardown-reconstruction.md
[inputs]: https://github.com/gooberpede/starfield-outpost-research/blob/e29b7507def041e25884e87222deea32b30d964d/docs/experiments/resource-retained-population/d5ad-input-provenance.md
[load]: https://github.com/gooberpede/starfield-outpost-research/blob/dec9f4de5816f8e7c8f694b064d3298f8a6afad2/docs/experiments/resource-retained-population/d5ae-eligibility-readiness-map.md
[saves]: https://github.com/gooberpede/starfield-outpost-research/blob/b0b7f1b1c8bfb8d62658e0c3ca279d4f305eab5a/docs/experiments/resource-retained-population/d5ar-saved-components-proof.md
