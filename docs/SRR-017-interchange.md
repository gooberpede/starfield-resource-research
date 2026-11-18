# SRR-017 allocation dataset v1

This export represents every qualified PNDT → BIOM allocation edge reachable
from the registered mixed store at the recorded checkpoint. The operator producer
replays a sealed native receipt and resolves IDs through the independently
read paired native loaded-plugin namespaces and typed native FormID map.
Every acquisition decision uses native evidence. Historical owned-source
receipts retain their original typed source-index interpretation.
[Native store contract](SRR-015-native-extraction.md) ·
[SRR-016 interchange](SRR-016-interchange.md)

| Field | Meaning |
| --- | --- |
| `schema` | `srr017-allocations-v1` |
| `source` | `OWNED_DISPOSABLE` for fixture processes or `RETAIL_ATTESTED` for the operator-selected retail process with a verified executable/epoch (not Steam attribution) |
| `scope` | Reachable mixed store at the responsive title-card checkpoint, simulated for owned targets |
| `retail_layout_version`, `retail_sha256`, `target_image_sha256` | Layout applicability and actual observed target image |
| `capture_reader_sha256`, `replay_reader_sha256`, `receipt_sha256` | Reader identities at capture and replay, and original private receipt byte hash |
| `exporter_source_sha256` | Canonical manifest digest for the source resolver, portable exporter and comparator adapter |
| `source_provenance`, `remap_sha256` | Native loaded-plugin namespace and deterministic namespace digest in the retail-facing profile |
| `input_sha256` | Null until separately attested comparison inputs exist |
| `structure`, `pair`, `acquisition` | Reader's structural qualification, independent agreement tests on covered passes, and whole-export admission |
| `native_namespaces`, `namespace_matches_source`, `namespace_refusals` | Per-pass portable plugin slots, check against the typed source index, and refusal codes. Null values denote absent witnesses, checks or refusals. |
| `source_binding_failure`, `native_source_attribution` | For the retail-facing profile, native namespace binding refusal and separate attribution diagnostics |
| `collection_counts` | Per-pass published count, visited and excluded mixed records, separate mixed and target refusal counts, attempted, verified and source-unresolved targets, per-code source issues, and terminal coverage |
| `rows` | Qualified canonical rows in `[PNDT, BIOM]` order |
| `unqualified_collections`, `failure` | Observed target/refusal rows in native walk order per pass, plus an acquisition failure code when available |

A canonical ID is the lowercased defining plugin name followed by a colon
and six uppercase hexadecimal local-ID digits. Each raw u64 index word
is a fixed-width 16-digit uppercase hexadecimal string. This preserves
all 64 bits in JSON runtimes with binary64 numbers. The row also preserves
the separate observed u32 PNDT and BIOM IDs,
PNDT seed, inline biome seed, raw coverage word, ordered BIOM RSGD
references and the inline optional RSGD word. A typed optional override
that resolves to null keeps its observed nonzero word and native reason.
A null metadata field indicates insufficient evidence for that field.
The row's BIOM ID comes from the index key. On a refusal for disagreement
with the inline biome word, use the original private block bytes to
recover the conflicting value.
When the namespace profile is captured, independently read source-name
vectors accompany the typed form witnesses as `native_source_plugins`.
These observed names preserve native order and provenance. The
`winning_plugin` and `winning_record_id` fields in the original owned
profile come from the supplied namespace order and are corroborated by
its synthetic vectors. The retail-facing profile emits null winners and
`WINNING_CONTENT_UNRESOLVED`. Its defining identity uses the paired
namespace and the authoritative native FormID map's stored-ID/type checks.
`source_record_id` is null because the extraction observes runtime records.
Missing, partial, filtered, contradictory or unreadable attribution remains
diagnostic. Genuine namespace assignments, native record types and
resource vptrs must validate independently.

Each row carries seven lane objects. Ordinals 0 through 6 correspond to
Common, Uncommon, Rare, Exotic, Unique, Special and Everywhere, at native
payload offsets `+0x50`, `+0x54`, `+0x58`, `+0x5C`, `+0x60`,
`+0x64` and `+0x68`. Every lane has its observed u32. A zero lane has a
null source and a `ZERO` native status. A verified nonzero lane has an
independent native FormID, type and BGSResource vptr witness in the private
receipt, together with its defining source identity in a qualified row.
An all-zero typed row remains present.

The rooted reader refuses duplicate raw keys. The export refuses aliases
between different runtime IDs and one source identity, and between one
runtime ID and different source identities. Failed source joins retain
raw rows and field-specific issue codes. A partial collection may have
fewer visited records than declared. Refused descriptors can lack a
decoded payload. The public output carries no addresses, absolute paths,
process epochs or free-form native diagnostics. Keep the raw bytes and
unabridged failures in private custody.

For a human-readable view, group `rows` by
`row.pndt.source.comparator_id`, and display one line per
`row.biom.source.comparator_id` with each lane in ordinal order. Show the
lane's canonical source ID for a nonzero value and a dash for an explicit
zero. Only render this as a complete view when `acquisition` is `QUALIFIED`.
Inspect `unqualified_collections` and the pair/count fields for diagnostics.

## Operator replay and comparison

The active operator receipt schema is `srr017-operator-census-v2`. Its
checked replay requires its exact reader source, bounded event stream,
seal, selected executable/epoch binding, unchanged native decisions and
terminal report. It needs no original authorization, custody claim,
Steam attribution, source JSON or physical ESM files. It opens no process.
The controller checks replay before writing `dataset.json`; qualified
results also produce the deterministic `srr016-observation-v1` projection
in `observation.json`. The original raw words remain exact integers in
that projection. Its adapter checks count conservation and redundant
native witnesses. Neither export reads a ledger or oracle.

For independent replay from Python:

```python
from pathlib import Path
from tools.srr017.extract import replay_dataset
report, dataset = replay_dataset(Path("output/receipt.jsonl"))
```

Historical operator-v1 receipts require their original pinned reader; v2
records the population-independent work envelope. The command's offline
replay option is documented in the
[run card](SRR-017-title-run-card.md). Compare regenerated canonical
`output_bytes(dataset)` with the retained `dataset.json` and independently
retained manifest/receipt hashes. A changed or unfinished journal refuses;
a readable incomplete pair retains diagnostic collections without claiming
a qualified export. A self-consistent seal establishes internal integrity,
not authenticity against deliberate wholesale replacement. Retain the
output manifest and reviewed source identity independently for that purpose.

Older `tools.srr017.export --retail` and three-positional-input invocations
belong to historical authorization/source-index receipts. Their original
checks remain available for those schemas and are superseded for new
operator captures. They are not prerequisites of operator replay.

A compatible projection can remain outside an applicable comparison when
independent effective-input or expected-population evidence is unknown.
That comparison is subsequent work, not an acquisition gate.
