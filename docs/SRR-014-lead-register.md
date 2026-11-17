# SRR-014 — Lead register

Scope and executable identity follow the [technical dossier](SRR-014-startup-allocation-component-database-lifecycle.md).
All dispositions concern this build and the bounded paths named in the
evidence column. A resolved static lead can leave a dynamic question open.

| Lead | Disposition | Evidence, attempted join and remaining scope |
| --- | --- | --- |
| A1. Startup loader ancestry and application alternatives | RESOLVED | Joined setup, application dispatch, initial loader return and the guarded Starfield module entry. Checked the pinned sibling startup report against the same image hash. [Startup evidence](SRR-014-startup-evidence.md) |
| A2. Context creation, publication, queue-host attachment and type registration | RESOLVED | Followed fixed owner getter, embedded initializer, publication, host attachment and the guarded registration continuation. Distinct guards permit reuse. Reset clear and owner shutdown have different effects on the published slot. [Startup evidence](SRR-014-startup-evidence.md) |
| A3. Optional first sweep and CSV input route | RESOLVED | Recovered the default-false INI setting identity and generic boolean loader, checked early sweep/follow-up/CSV order and common-tail continuation. Authored or CSV records begin with seven zero words. Checked the CSV append route against the earlier supply/replace possibility and kept explicit ENAM removal separate. [Startup evidence](SRR-014-startup-evidence.md) · [Database evidence](SRR-014-database-evidence.md) |
| A4. Loader-produced input visibility and execution | RESOLVED | Traced typed submission, host/service dispatch and insert callback. Presence in the collector proves insertion by collection for that edge. Bounds on queue drain and configured-source behavior are recorded where static coverage ends. [Database evidence](SRR-014-database-evidence.md) |
| A5. PNDT, edge and BIOM admission | RESOLVED | Joined installed visitor, generic iterator, adapter, collector and two payload passes through nonzero/zero stores. Absent optional RSGD can still permit a BIOM list selection. [Productive writes](SRR-014-startup-allocation-component-database-lifecycle.md#sweep-and-productive-writes) |
| A6. Completion and readiness alternatives | EXHAUSTED/EXCLUDED | Publication, guard pointers, tree counts, worker signal, readiness latch and follow-up visitors have independent purposes. Checked the latch write before wait, guarded constructor bypass and the empty-work branches. They do not adjudicate productive writes. Late iterator return orders completed visits for one normal invocation. [Sweep](SRR-014-startup-allocation-component-database-lifecycle.md#sweep-and-productive-writes) · [Startup evidence](SRR-014-startup-evidence.md) |
| A7. Reset, callbacks, re-entry and menu-return ancestry | RESOLVED | Traced signed mode, index clear, Starfield guard teardown, replay and module re-entry. Rechecked the pinned menu-return record. A route from a load-order callback proves conditional reachability. [Startup evidence](SRR-014-startup-evidence.md) · [SRR-011 invocation](SRR-011-planetary-allocation-execution-and-result-lifecycle.md#invocation) |
| A8. Actual title-epoch allocator invocation, timing, repetition and ordinary Save2 | BLOCKED | SRR-013 supplies checkpoint samples. Earlier historical captures end outside the allocator join or begin after startup. Offline native analysis can establish guarded paths but lacks an execution witness that ties the epoch and payload to a store. A separately approved, identity-joined observation would address startup; save-load behavior would need its own qualified scenario. [Future boundaries](SRR-014-startup-allocation-component-database-lifecycle.md#future-observation-boundaries) |
| A9. Sweep-wide drain of the attached database queue | BLOCKED | Traced the host through scheduler state/TLS admission at `FUN_1428D8FE0` and the direct/deferred service into owner +0x40. `FUN_140472890` drains a different image queue. Reset drains `[0x145E71710]+0x200`, on a separately allocated receiver. The direct-reference census below checks adjacent application calls against those receiver identities. The remaining missing join is an identity-qualified schedule and completion for the selected commands in the startup epoch, including the direct-vs-deferred choice and outstanding work at sweep entry. No retained startup evidence measures those states. [Database evidence](SRR-014-database-evidence.md#command-order-and-visibility) |
| B1. Typed edge identity, alternate store and input copies | RESOLVED | Joined registration, PNDT key, discriminator, range bounds, inline edge identity and separate +0x268 lookup/records. Indexed +0x44 coverage adjustment uses a separate discriminator. [Database evidence](SRR-014-database-evidence.md) |
| B2. Insert, duplicate behavior and change publication | RESOLVED | Checked typed callback, index insertion primitive, component copy and notification. Scoped duplicate conclusion to inspected insertion and explicit remove-and-create paths. [Database evidence](SRR-014-database-evidence.md) |
| B3. Keyed lookup, enumeration, FormID validation and consumption | RESOLVED | Checked the range fences, iterator and matching BIOM copy. Reused independent consumer stack-frame and FormID joins, including the separately validated resource form path. [Database evidence](SRR-014-database-evidence.md) · [SRR-011 readers](SRR-011-planetary-allocation-execution-and-result-lifecycle.md#readers-and-reuse) |
| B4. Guard participation, in-place update, pointer borrowing and invalidation | RESOLVED | Traced shared entry and release around the writer and representative readers, and the distinct ticket and page-mode path in the examined mutators. Borrowed pointers alias inline payloads. Removal and clear destroy entries, with compaction on the inspected targeted path. [Database evidence](SRR-014-database-evidence.md) |
| B5. Writer-wide transactional visibility or immutable retained cache | EXHAUSTED/EXCLUDED | Shared reader/writer mode, multiple stores, unguarded external collection, no skip-on-result test in the sweep and no generation on the reader's miss branch defeat those interpretations for the examined paths. A bounded call graph establishes no universal absence claim. [Database evidence](SRR-014-database-evidence.md) |
| B6. Removal, context reset, owner teardown and type-registration disposal | RESOLVED | Separated typed removal callback, guarded tree clear, published pointer disposal and registry teardown. The signed reset path can reinsert through loader replay. [Database evidence](SRR-014-database-evidence.md) |
| B7. Observed cross-thread visibility, actual flag value and retained lifetime | BLOCKED | Compared native guard modes, configuration default and SRR-013 paired samples. No authorized startup-time sequence or matching effective configuration witness exists for the observed epoch. A static path to a write cannot disambiguate a reset, concurrent shared-mode read or an intervening rewrite. Future scoped evidence would require effective setting attribution and event/read ordering; continuous lifetime would additionally require observing invalidation boundaries. |
| B8. Computed result mirror through notification | UNRESOLVED | The traced key-only notification and +0x358 reverse-key command establish their own effects. The +0x268 typed factory can copy result slots from an existing typed source. A join from a computed +0x300 payload to the same-key +0x268 destination remains open. [B8 coverage and history](#b8-coverage-and-history) |
| B9. CSV hook as a same-key replacement mechanism | EXHAUSTED/EXCLUDED for the joined PNDT leg | Bounded direct references to the hook globals show initial null/null/function values. The PNDT reader submits its own form pointer to the `ProxyFormPtr` store. For that lookup hit, the +0x1A0 method sets a form flag. The inspected CSV submit path supports append. Actual runtime proxy population and dispatch through other concrete vtables remain unqualified; the examined producers provide no other attributed replacement target. [CSV hook evidence](SRR-014-database-evidence.md#command-order-and-visibility) |
| B10. Persisted resource slots across process epochs | BLOCKED | Rechecked SRR-011's PNDT serialization candidates, conditional reset/replay and SRR-013's single-epoch title result. No mapped writer/reader proves that the seven words cross a save or restart boundary. A byte-level serialization join or a separately authorized comparison that discriminates persistence from replay would be required. [Prior persistence audit](SRR-011-planetary-allocation-execution-and-result-lifecycle.md#invalidation-and-persistence) |

The startup and database workstreams were assigned independently. The
parent reconciled their publication-to-registration order, queue attachment,
guard usage and reset lifetime with the sweep return and productive-write
predicates. The database workstream traced the adapter's shared entry after
the parent identified its refcount and entry calls, and compared it with
mutation guards and the checked copy readers. Both paths are needed to
interpret ordering and snapshot limits.

For A9 the parent scanned seven exact PE targets, including drain/service
entries `0x1428D8640`, `0x1428D8060`, `0x1428D89B0` and owner
`0x1482EE300` plus its host alias. The tracked decoder reported 60
candidate byte positions, 59 decoded references across 236,427 selected
exception ranges, one out-of-range candidate and one partial decode.
The census covers direct rel32 branches, supported RIP operand encodings
and exact qword matches. The candidate at `0x1428D9569` is the already
resolved scheduler callback's tail into `FUN_1428D89B0`. Among adjacent
application paths, `0x141888609` and `0x14189B44A` drain the same
distinct `[0x145E71710]+0x200` receiver as reset. `0x14189B2E5`
uses image object `0x145F940C0`. `0x14189B437` uses the other
application owner's +0x280 subobject. Those calls cannot stand in for
the typed host drain at `0x1428D8A49`. This bounds the tested candidate
set without ruling out computed calls or other transitive scheduling.
[Custody receipt](SRR-014-startup-allocation-component-database-lifecycle.md#provenance-and-reproduction)

## B8 coverage and history

- **Inspected.** The prior work traced the registered type, exact discriminator
  references, the +0x268 typed factory and the edge-insert notification.
  SRR-014 traced the +0x358 reverse-key command and the immediate dispatch
  through subscriber slot +0x10 at `0x14240F659`. The factory copies all seven
  slots from the typed source it receives. The reverse command updates the
  key index, and the immediate dispatch passes a key copy. None of those
  inspected bodies joins a generated +0x300 payload to a same-key +0x268
  destination. [Database catalogue](SRR-014-database-evidence.md#operation-catalogue) · [Prior lead D03a](SRR-011-lifecycle-lead-register.md)
- **Plausible static work outside this documentation correction.** Further
  tracing could follow computed subscriber registration or receiver value
  origins to concrete callbacks, then check their lookups and assignments
  for the same-key source and destination. The existing record identifies
  the dispatch interface and leaves the registration-to-receiver join
  unresolved for this notification.
- **Runtime evidence gap.** The subscriber set and receiver selected in a
  particular startup epoch are unrecorded. Static tracing could establish
  that a particular callback can mirror the payload. Attributing an actual
  mirror in that epoch requires an execution witness that identifies the
  receiver and the matching source and destination payloads.

The original SRR-014 register marked B8 `BLOCKED` because the concrete
subscriber set and same-key payload join were missing. The disposition
now distinguishes the unexamined static paths from the runtime evidence gap.
The mirror claim remains unresolved.
