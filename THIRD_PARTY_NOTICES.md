# Third-Party Notices

Starfield, Creation Kit, Bethesda, ZeniMax, and related names, marks, software,
and content belong to their respective rights holders. This is an unofficial
community research and modding project and is not affiliated with, endorsed
by, or sponsored by Bethesda Softworks or ZeniMax Media.

This repository retains limited, targeted reverse-engineering evidence derived
from legitimately obtained software. The selected excerpts and metadata exist
only to document specific technical findings and make those findings
inspectable and reproducible. The repository does not distribute Starfield or
Creation Kit executables, DLLs, Ghidra project databases, raw debugger traces,
memory dumps, or bulk binary-reconstruction material. Users must obtain the
game and tools through legitimate channels.

The project license applies only to material for which the repository owner
holds the relevant rights. It does not purport to relicense proprietary
third-party content, executable-derived evidence, or third-party trademarks
and names.

## SRR-001 sources and permissions

The maintainer designated the installed Steam copies for read-only identity
checks and supplied the Creation Kit About capture for local inspection.
Bethesda/ZeniMax are credited for the software and About dialog, and the
maintainer for supplying the capture and the outpost workflow references
that informed this investigation. The Ghidra project and x64dbg contributors
provided the analysis tools. The reproducer maintainers provided the canonical
validation and its documentation. The historical `SurveyAggregator` observer
contributed the empirical oracle. Individual attribution for that observer
is unrecorded in the consulted research records.

Inspection and credit establish provenance. Redistribution clearance for the
About image and additional executable-derived material was not established in
SRR-001. The capture stays local. Any future disclosure involving such material
requires a documented basis specific to its scope and purpose. See the
[SRR-001 release scope](docs/PROVENANCE.md)
for claim-specific holds.

## SRR-003 analysis tools

SRR-003 used the maintainer-authored `OutpostRecon.java` from
`starfield-outpost-research` in place for read-only reference and
data queries. Ghidra and Capstone contributors provided the analysis and
decoding tools. The [dossier](docs/retail-execution-lifecycle.md)
records the tool revisions, local inspection scope and publication holds.

## SRR-008 save policy and inventory tooling

`tools/srr008/save_policy.py` adapts the filename classification and
policy digest from `starfield-outpost-research`, revision
`d116bc63ff394b0156539161c8d1addfc902665a`,
`research/resource-carinae-source-context/save_policy.py`,
source SHA-256 `d48192098cd8cf80acae0e4096130b635af1c3cd931a4a0b82bff6d695b23ecc`.
It preserves the upstream GPL-3.0-or-later notice. Copyright remains with
the respective upstream authors. Only reusable code was adapted.

The SRR-008 inventory fixture uses the outpost repository's Tool Help
pattern from `research/q-branch-030-procedure/environment.py` at the same
revision. That source bears GPL-3.0-or-later. The promoted fixture preserves
the original local adaptation and its attribution. The [tooling notes](tools/srr008/README.md)
identify both sources and document their use.

Private policies, backup inventories, saves, Steam records and installed
executable bytes remain in local custody. Inclusion of reusable GPL code
leaves their existing rights and publication holds in place.
