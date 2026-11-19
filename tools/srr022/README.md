# Compare serialized PlayerKnowledge

Run from the repository root with Python 3.14 and its standard library.
Supply two lawfully obtained SFS files. The optional Data directory supplies
the first 24 bytes of locally available full-plugin TES4 headers. Use a private
output directory for the resulting inventory.

```powershell
python -B -m tools.srr022.compare $save2 $save52 --plugin-directory $data > $privateComparison
python -B -m unittest discover -s tools/srr022 -v
```

The command reads files, writes JSON to stdout and operates entirely offline.
It needs neither a running game nor a Ghidra project. For a save-only run
omit `--plugin-directory`. In each inventory `layout.chunks` gives physical
and decompressed spans, `layout.units` contains inflated coordinates, and
`section`, record offsets and item offsets are unit-relative. Add
`layout.unit_start` to a record offset to inspect the inflated SFS.
Identity array and plugin-name offsets already address that inflated SFS.
Each comparison row references the full side-specific records or entries by
offset. For example, `left = null` and a right offset denote a missing left
entry among comparable keys. An explicit zero in `progress_21` denotes a
stored byte. A null `items` means bit 3 was clear and an empty list means the
serialized count was zero.

## Supported profile

The input profile is BCPS v1 ZIP, independent 256 KiB decoded blocks and
16-byte alignment, SFS header version 27, form version 153, two recorded
1.16.244.0 strings and the observed 17-unit directory layout. The decoder
checks compressed lengths, zlib integrity, section extents, the save-local
FormID table and the fixed-order unit-6 prefix. It skips the remaining
unit-6 contents after verifying the boundary of the next keyed table.
Both historical inputs contain version 3 components. Versions 0–2 exercise
the pinned reader branches in synthetic tests only. Other component versions,
unsupported framing and ambiguous duplicate keys raise an error.

Serialized comparisons use the body identity plus the low u16 and use item
identity within that body. Auxiliary and nested ID vectors and bounded
12-byte trailer tuples retain stream order. The second item byte and positive
progress byte are separate. Counts by changed field overlap. Only-left and
only-right concern the comparable identities. Dynamic or unmapped keys remain
in side-specific rows. Unresolved references can make sequence equality
indeterminate. Equal saved values and any predicted fresh-destination state
have no implication for a particular runtime plugin redirect or display.

## Native checks

Use the [pinned PE reader](../srr011/inspect_pe.py) with the executable and
dependency versions in [provenance](../../docs/PROVENANCE.md). For example:

```powershell
python -B tools/srr011/inspect_pe.py $image window 141823C71 80
python -B tools/srr011/inspect_pe.py $image window 1418225B5 199
python -B tools/srr011/inspect_pe.py $image functions 141411190 141413570
python -B tools/srr011/inspect_pe.py $image window 142337790 2C0
python -B tools/srr011/inspect_pe.py $image window 142337A50 820
python -B tools/srr011/inspect_pe.py $image functions 14186BD40 14186BC80
python -B tools/srr011/inspect_pe.py $image window 14180AE89 120
```

The ordered writer VAs and byte widths needed to reach the component count
are in [section.py](section.py). The [component database](../../docs/component-database.md#playerknowledge-in-save2-and-save52)
gives specimen counts, the separate screenshot comparison and reconstruction
limits.
