# Pre-biome Resource-State Investigation

## Scope and method

This was a static-only Ghidra investigation of Creation Kit
`FUN_1415DCFB0`. No x64dbg work was performed, the standalone reproducer and
xEdit tooling were not touched, and the Ghidra project was opened read-only
with analysis disabled. Evidence was exported with
`ghidra/scripts/ExportFunctionsByAddress.java`; the exact input identity and
focused outputs are preserved under
`docs/experiments/evidence/pre-biome-resource-state/`.

The traversal stopped at `FUN_14152CBC0`, the smallest function that owns both
pre-biome population and the repeated calls to `FUN_1415DCFB0`. Only helpers
that feed the two pre-biome paths and the two immediate invocation wrappers
were inspected.

## Resulting static map

```text
FUN_14157E850 at 0x14157E850 ─┐
                              ├─ call FUN_14152CBC0
FUN_14158DBE0 at 0x14158DBE0 ─┘

FUN_14152CBC0 at 0x14152CBC0
    |
    |-- construct and shuffle biome pointer array
    |      shuffle call: 0x14152CEBD
    |
    |-- initialise shared uint32 resource-ID array
    |      setup: 0x14152CEC2–0x14152CF00
    |
    |-- resolve a planet-keyed typed form
    |      call FUN_1419FE120: 0x14152CF17
    |      type gate in helper: resolved form +0x88 == 0xAD
    |
    |-- access typed form +0x1D8 as an array
    |      call FUN_141A46660: 0x14152CF28
    |      deduplicate and append each resolved form's uint32 ID
    |      ID load:  0x14152D034
    |      append:   0x14152D0D3 / store 0x14152D0E9
    |
    |-- for every biome, inspect category-6 entries
    |      call FUN_141548920: 0x14152D1B5
    |      category test:      0x141548AC9
    |      biome +0x68 write:  0x141548ADA
    |      shared append:      0x141548AE7
    |
    `-- for every shuffled biome
           call FUN_1415DCFB0: 0x14152D28F
           loop back:          0x14152D29B
```

`FUN_1415DCFB0` has exactly one direct static caller, at `0x14152D28F` in
`FUN_14152CBC0`. The orchestration function itself has two direct callers:
`FUN_14157E850` at `0x14157E8E4` and `FUN_14158DBE0` at `0x14158DC6E`.
Both are thin wrappers that acquire the same manager-like object and invoke the
same orchestration function. `FUN_14158DBE0` has no direct static caller in the
current database, so it may be indirectly dispatched. Static xrefs alone do
not establish which wrapper was used by the previously observed Galaxy View
Apply execution; the shared orchestration boundary is unambiguous.

## Shared resource-state argument

`FUN_14152CBC0` creates a stack-resident dynamic array beginning at its
decompiler local `local_1568`. Its observed layout is:

```text
+0x00  uint32 count
+0x04  uint32 capacity
+0x08  allocator/reserved state (8 bytes in this instantiation)
+0x10  uint32* data
```

The element representation is a 32-bit form ID, not a form pointer. The direct
prepopulation loop resolves a dependency-managed form pointer, loads its form
ID from form `+0x70` at `0x14152D034`, checks the existing ID array for the
same value, grows the array if needed, and stores the ID at
`0x14152D0E9`.

At the biome call site the Windows x64 arguments are:

```text
RCX = current shuffled biome work object
RDX = &MT19937 state
R8  = &generated/cached Common-family configuration array
R9  = &shared uint32 resource-ID array
```

Thus `R9` / `FUN_1415DCFB0` parameter 4 is the object whose count is compared
with `8` at `0x1415DD0A3` and `0x1415DD0DC`. The generator stores that pointer
at offset `+0x20` of the temporary context passed to `FUN_14157F120`; the
descendant helper loads `[RCX+0x20]` at `0x14157F14D` and compares the same
array's count at `0x14157F151`.

The shared array is initialized once before either prepopulation path and is
not reset between calls to `FUN_1415DCFB0`. The separate Common-family cache
array is initialized at `0x14152D1D0` after prepopulation and before the biome
loop.

## Pre-biome population paths

### Planet-keyed `+0x1D8` list

At `0x14152CF17`, `FUN_14152CBC0` calls `FUN_1419FE120` with the manager-like
second input and the current planet object's uint32 field at `+0x134`.
`FUN_1419FE120` performs a component-database lookup and returns either a
resolved form whose type byte at `+0x88` is `0xAD`, or a fallback object.
`FUN_141A46660` is a unique eight-byte accessor that returns that object's
address plus `0x1D8`.

The caller treats `+0x1D8` as a count/pointer array of dependency-managed form
pointers. It resolves each pointer, loads form `+0x70`, manually deduplicates
the 32-bit ID, and appends a previously absent ID to the shared array. The
accessor thunk has only this one direct caller in the current Ghidra database.

### Category-6 / Everywhere path

Before the first generator call, `FUN_14152CBC0` clears each biome work
object's `+0x50` through `+0x68` result fields and, for the expected resolved
biome-data type, calls `FUN_141548920` with a source array at resolved object
`+0x728`, the biome object, and the shared ID array.

`FUN_141548920` walks dependency-managed entries and their `0x238`-byte nested
records. At `0x141548AC9` it tests the resolved record's category byte at
`+0x2F8` against `6`, the established Everywhere category. On the first match,
it copies form `+0x70` to biome `+0x68` and appends the same ID to the shared
array before returning.

## Atmosphere evidence

### PROVEN STATIC FACTS

- `FUN_1415DCFB0` has one direct caller: `FUN_14152CBC0` at
  `0x14152D28F`.
- `FUN_14152CBC0` initializes one shared uint32 form-ID array, populates it by
  the planet-keyed `+0x1D8` list and the category-6 helper, and only then begins
  its repeated per-biome calls.
- Both paths append to the exact array passed as generator argument 4 and later
  reached by the descendant helper through context offset `+0x20`.
- The category-6 path is the Everywhere prepopulation path under the already
  established category mapping.
- The generator diagnostic at `0x1415DD453` is:

  ```text
  No valid generated common resources. Atmosphere and Everywhere resources filled all available slots for biome %s
  ```

- The other prepopulation source is a planet-keyed type-`0xAD` form whose
  `+0x1D8` field is an array of resource-form-like pointers. Its entries supply
  the same `form +0x70` ID representation used for generated resources.
- There is no literal reference to Maal VIII's Chlorine FormID `000057D5` in
  this generic code path.

These are static facts from the CK analysis database. The eight-entry capacity
and Maal VIII count/RNG behavior remain previously established live x64dbg
facts, not new results of this experiment.

### STRONG INTERPRETATIONS

- The planet-keyed type-`0xAD`, `+0x1D8` list is the atmospheric inorganic
  resource list. This is supported jointly by its position as the only other
  pre-biome append path, its resource-form representation, the separately
  proven Everywhere path, and the generator's explicit “Atmosphere and
  Everywhere” diagnostic.
- The static dataflow supplies the missing mechanism for the existing strong
  model in which atmospheric resources occupy the same eight-entry capacity as
  biome-generated resources.

The current database does not name the type as ATMO or decode the `+0x1D8`
field, so those semantic identities are not promoted to PROVEN by static
inference alone.

### OPEN QUESTIONS

- Does a Maal VIII live call to `FUN_1419FE120` return its effective ATMO
  object, and does the `+0x1D8` array contain a resolved Chlorine form whose
  `+0x70` value is `000057D5`?
- Is inherited ATMO resolution already complete before `FUN_1419FE120`
  returns, or does the component-database lookup perform part of it?
- Which thin wrapper (`FUN_14157E850` or the possibly indirect
  `FUN_14158DBE0`) is the exact Galaxy View Apply dispatch observed live?
- Can the shared array contain repeated IDs from category-6 processing, or do
  upstream data constraints make those appends unique?

## Recommended live trace window

For a later, separately authorised Maal VIII x64dbg experiment, start at
`0x14152CF05` (immediately after shared-array initialization) and stop after
the first return from `FUN_1415DCFB0` at `0x14152D294`. The tighter pre-biome
window ends just before the first call at `0x14152D28F`.

Recommended breakpoints/observations:

```text
0x14152CF17  enter/return from planet-keyed typed-form lookup
0x14152CF28  observe returned +0x1D8 array header
0x14152D034  capture each resolved source form and form +0x70 ID
0x14152D0E9  capture each direct-list ID store; test EDI == 0x000057D5
0x14152D1B5  enter per-biome category-6 helper
0x141548AC9  record category-byte comparison against 6
0x141548ADA  record biome +0x68 ID write
0x141548AE7  record append to shared ID array
0x14152D28F  record shared count/IDs immediately before first biome call
0x14152D294  record count/IDs after the first biome call
```

This window is sufficient to test the strong ATMO interpretation, concrete
Maal VIII Chlorine identity, insertion ordering, and whether the same array is
presented to the first generator call without tracing the wider manager or UI
path.
