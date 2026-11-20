# Starfield resource research

This repository documents how Starfield derives per-biome inorganic resource
allocations from planet, biome, resource-generation and seed inputs. It owns
native evidence, provenance and evidence status. The executable reference
model, maintained data and regression suite live in
[starfield-resource-reproducer at the validated revision](https://github.com/gooberpede/starfield-resource-reproducer/tree/a8ff1c788bca415f571f06769ab3e712fa674f75).

Start with the [research library](docs/README.md). It separates recovered
generation, retail execution, component storage, measured validation and
current questions. Evidence grades distinguish observation from inference;
Creation Kit addresses and live results never stand in for retail addresses
or retail-live implementation proof.

[Ghidra exporters](ghidra/README.md) read existing analysis without modifying
the project. [Tooling](tools/README.md) distinguishes current operator
extraction from historical observers and offline comparison. No live access
is authorized by reading these instructions.

The project preserves the recovered v1.0 rules unless a reproducible
counterexample supplies new evidence. Follow [AGENTS.md](AGENTS.md) and the
[research workflow](docs/research-workflow.md) for changes. Rights and
redistribution boundaries are in [third-party notices](THIRD_PARTY_NOTICES.md)
and [LICENSE](LICENSE). Obtain game binaries and other required inputs lawfully;
they are not distributed here.

## Proposed first repository release

The v1.0 generation model is the subject of the proposed research release
`v1.0.0-sf1.16.244.0`. Its executable pins are:

| Executable | File and product version | SHA-256 |
| --- | --- | --- |
| Starfield.exe (retail) | 1.16.244.0 | `7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28` |
| CreationKit.exe | 1.16.244.0 | `ed54e4906bc13b0fbc43ec7624fec4af2389a9a1e12b2789d73c5617f5a14020` |

These identities qualify the fingerprinted native evidence. Historical CK
Apply sessions, retail screenshots and holdout scans have their own provenance
limits. Supporting later executable bytes requires revalidation and a new
composite tag. See the [applicability register](docs/PROVENANCE.md) and
[candidate manifest and release notes](docs/release-candidate.md).
