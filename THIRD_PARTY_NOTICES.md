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
[SRR-001 release scope](docs/SRR-001-executable-identity.md#release-scope)
for claim-specific holds.

## SRR-003 analysis tools

SRR-003 used the maintainer-authored `OutpostRecon.java` from
`starfield-outpost-research` in place for read-only reference and
data queries. Ghidra and Capstone contributors provided the analysis and
decoding tools. The [dossier](docs/SRR-003-retail-allocator-invocation-and-dispatch.md#reproduction-publication-and-next-experiment)
records the tool revisions, local inspection scope and publication holds.
