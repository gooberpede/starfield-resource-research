# Allocation interchange contracts

This export represents every qualified PNDT → BIOM allocation edge reachable
from the registered mixed store at the recorded checkpoint. The operator producer
replays a sealed native receipt and resolves IDs through the independently
read paired native loaded-plugin namespaces and typed native FormID map.
Every acquisition decision uses native evidence. Historical owned-source
receipts retain their original typed source-index interpretation.
[Native store contract](../../docs/component-database.md) ·
[comparison envelope](#srr-016-interchange-v1)

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
[run card](README.md). Compare regenerated canonical
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


## SRR-016 interchange v1

Use UTF-8 JSON. Hash canonical JSON with sorted object keys, compact separators,
ASCII escaping and no terminating newline. File hashes, when recorded, refer to
the original bytes. Each envelope has `schema`, `retail_sha256` and `input_sha256`
(null for unresolved effective input). Canonical FormIDs are strings
`defining-plugin:LLLLLL`, lowercase plugin and six uppercase hex digits of
local ID. In a slot array, null encodes an empty resource lane.
A row key is `[pndt, biom]`.
Normalize by sorting on the two canonical IDs. Keep runtime ID witnesses in
their row fields and retain addresses only in private acquisition evidence.

| Schema | Payload |
| --- | --- |
| `srr016-observation-v1` | `structure` (paired raw coverage), `acquisition` (qualified normalized pair), `mixed`, `rows`, `source`, `target_image_sha256` and `remap_sha256`. Both states use `QUALIFIED` or `ACQUISITION_INDETERMINATE`. |
| `srr016-ledger-v1` | `scope` (`COMPLETE` or `CONDITIONAL`), `owners` with their closure and source, `rows` with `key`, `status` (`EXPECTED`, `EXCLUDED`, `UNKNOWN`), `source` and `reason`. A complete population match requires the ledger's independently attested `remap_sha256`. |
| `srr016-oracle-v1` | `reproducer_commit`, `ledger_sha256`, `rows` with `key`, `slots`, `applicability` (`QUALIFIED` or `CONDITIONAL`) |
| `srr016-freeze-v1` | `reproducer_commit`, `ledger_sha256`, `oracle_sha256` and source/corpus pins. Freeze before observation and retain the canonical receipt digest independently of the comparison inputs. |

An observed row has `key`, `raw_key` (two u64 integers), `typed` (`VERIFIED`),
`raw_slots` (seven u32 integers) and `slots` (seven canonical IDs or null).
Slot order is increasing native address, payload offsets +0x50 through +0x68
by four. Preserve raw bytes privately in little-endian order. An all-zero
row retains its identity and all seven positions. Adapter functions may take
an independent resolver to convert validated runtime IDs. A missing or
contradictory resolution prevents admission. A qualified empty observation
has `mixed: 0` and `rows: []`. Qualification requires a full admitted pair.
Raw structural qualification can survive a value disagreement or unresolved
canonical remap. In these situations the producer retains the raw evidence
privately and withholds normalized rows. The layout's `retail_sha256`
identifies its pinned semantics. `target_image_sha256` identifies the actual
process's executable. `OWNED_DISPOSABLE` marks software fixture evidence.

Acquisition owns structural refusal and evidence custody. Its sanitized
envelope carries counts and canonical rows. Private receipts carry the read
protocol, brackets, raw bytes, failure details, addresses and replay data.
Frozen offline expectations carry independent source provenance. Effective
input attestation and oracle owner qualification are separate from structural
admission. Comparison reports structural, population and value decisions
independently. Reject identity collisions and provenance disagreements.
