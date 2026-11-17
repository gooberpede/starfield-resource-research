# SRR-015 — Lead register

Each disposition applies to the scoped question in its row. The prior
[SRR-011](SRR-011-lifecycle-lead-register.md),
[SRR-012](SRR-012-lead-register.md),
[SRR-013](SRR-013-lead-register.md) and
[SRR-014](SRR-014-lead-register.md) dispositions remain historical evidence.

| Lead | Disposition | Evidence and remaining work |
| --- | --- | --- |
| Reachable +0x300 coverage | RESOLVED as a design for admitted layouts | Root children, leaf links, record descriptors, key order/fences and mixed count give independent reconciliation checks. A census prototype and population-shaped fixtures must demonstrate the contract before retail use. [Native design](SRR-015-native-extraction.md) |
| Use native copy as external export | EXHAUSTED for this experiment | The native reader is a keyed first-match copy and takes caller-owned output, with guard admission at verified upstream sites. It can conceal a duplicate and requires an in-process receiver and caller state. Static semantics are reusable by the external traversal. [Database operations](SRR-014-database-evidence.md#operation-catalogue) |
| Authoritative expected key ledger | BLOCKED for unconditional comparison | Need a population-wide winning PPBD/ENAM/CSV admission and replacement ledger, plus canonical owner/key mapping and effective load-order coverage. The historical model corpus and observed key set cannot establish this ledger by themselves. [Native design](SRR-015-native-extraction.md) · [Oracle comparison](SRR-015-oracle-comparison.md) |
| Independent seven-slot expectation | RESOLVED for conditional sample feasibility, BLOCKED for universal projection | The production model preserves biome selections, family levels and occupancy. The native writes add output-admission, ordering and precision requirements. Qualify entire owner sequences under those rules, including supported zero lanes, before admitting them to a whole-owner oracle. [Oracle comparison](SRR-015-oracle-comparison.md) |
| A9 sweep-wide drain | BLOCKED for sweep attribution, outside checkpoint coverage proof | The prior exact-target scan distinguished the typed owner +0x40 attachment from adjacent application/reset receivers. An epoch-qualified observation of the typed host, queued commands and outstanding work at sweep entry remains missing. Pair agreement and full enumeration alone supply no schedule witness. [A9 and bounded census](SRR-014-lead-register.md) |
| B8 notification and computed mirror | RESOLVED for tested direct notification and separate factory capability. Concrete registration paths outside the examined set are DEFERRED | The [bounded follow-up](#b8-bounded-follow-up) joins the actual notification receiver to its constructor and confirms direct key-only dispatch. Need concrete subscriber installation and same-key generated source/destination accesses to establish a possible mirror, then an epoch-qualified execution witness to establish its use. That work matters to a cross-store question. The present extraction explicitly names +0x300. |
| Shared admission as atomicity witness | EXHAUSTED for checked writer and readers | Writer and readers can share admission while stores execute separately. Stable intermediate zeroes and ABA are already demonstrated limitations of paired read interpretation. A native guard counter adds no completion proof here. [Guard modes](SRR-014-database-evidence.md#native-synchronization-and-state-transitions) · [Budget recovery](SRR-013-live-observation-budget-recovery.md) |
| Epoch-wide invocation, persistence and discovery/survey | DEFERRED | Invocation attribution needs an execution join. Save-state questions additionally need attributable serializer/restore evidence and a design that discriminates restored slots from replay. [Deferred research](SRR-015-retained-allocation-extraction-feasibility.md#later-checkpoints-and-deferred-save-research) |
| Universal alternate stores or arbitrary subscribers | UNEXAMINED / OUT OF SCOPE | No claim about every subscriber, store or serializer follows from this +0x300 investigation. Return to a concrete callback, mismatch or storage locator before broadening the scope. |

## B8 bounded follow-up

On the pinned retail PE, `0x142406BD3` forms DB +0x38 and
`0x142406BDC–BE8` supplies the two key qwords in caller stack storage
to `FUN_14240F5F0`. The dispatcher reads its collection at receiver
+0x80 (`0x14240F602)), the per-entry callable at +0x28
(`0x14240F64A)), and invokes its vtable slot +0x10 at
`0x14240F659`. The DB constructor reaches `FUN_142412830` at
`0x142405A1C` with DB +0x38. This initializer installs
`0x144D6A540` and zeros the collection +0x80 at `0x142412894`.
The image vtable's +0x10 entry (`FUN_1407B3280`) clears storage
associated with receiver +8 when its +0x18 is populated. It is an
operation of the containing object. The runtime subscriber call at
`0x14240F659` instead obtains its vtable from the loaded callable.

The exact-target scan for `142406B70 14240F5F0` returned 110 decoded
references from 110 candidates in 236,427 selected exception ranges.
This includes both edge-insert calls at `0x1407767C1` and
`0x140777784`. The alternate nearby path at `0x140775D3F–D54`
also uses DB +0x38 and supplies a 16-byte key. The constructor scan
returned one decoded direct reference to `0x142412830`, at
`0x142405A1C`. The exact vtable scan flags `0x142412834` outside
the selected unwind ranges. Bounded window decoding recovers the
instruction beginning at `0x142412832`.

These checks cover direct rel32 and supported RIP-relative candidates in
file-backed .text and exact qword hits, plus the explicit windows. They
leave computed subscriber registration, concrete callback receivers and
indirect calls open. The separate +0x268 factory can copy all seven
fields from its typed source. A key-only callback, reverse-key command,
and the factory capability supply no same-key source-to-destination
join on their own. See the [SRR-014 B8 history](SRR-014-lead-register.md#b8-coverage-and-history).

```powershell
$image = '<path to the pinned Starfield.exe>'
python -B tools/srr011/inspect_pe.py $image window 142406B70 8B
python -B tools/srr011/inspect_pe.py $image functions 14240F5F0 1424059F0 1407B3280
python -B tools/srr011/inspect_pe.py $image window 142412830 70
python -B tools/srr011/inspect_pe.py $image window 140775D03 56
python -B tools/srr011/inspect_pe.py $image data 144D6A540 20
python -B tools/srr011/inspect_pe.py $image scan 142406B70 14240F5F0
python -B tools/srr011/inspect_pe.py $image scan 142412830 144D6A540
```
