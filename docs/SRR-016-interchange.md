# SRR-016 interchange v1

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
