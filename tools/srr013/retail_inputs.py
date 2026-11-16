"""Verify SRR-012 disk provenance and gate prediction applicability by target kind.

The offline receipt authenticates the prediction sources against pinned digests.
It supplies no witness of the process loader, resolved inputs or native CSV path.
Only a qualified simulation can project its graph evidence into the fixture classifier.
"""

import argparse
from dataclasses import dataclass
from hashlib import file_digest, sha1, sha256
import json
import os
from pathlib import Path

from contract import DISPOSABLE_INPUTS


MASTER_SHA256 = "1dabed00c3f4282dd3bb54d2e9601e40b577d8742d078b7ccef203adbfef0da7"
PACK_COMMIT = "a8ff1c788bca415f571f06769ab3e712fa674f75"
PACK_BLOBS = {
    "data/planet-resource-generation.csv": "418492f44c9b1c2b5d70d57c8e6a93d4cbdd22f1",
    "data/ires-hierarchy.csv": "25bba09fb205d32b392e179e92fc77fdf0db3c36",
    "data/planet-atmospheric-resources.csv": "d7a204a8ad23dc12c826952eac7d44b4de5ca8d5",
    "data/planet-directory.csv": "7eb7a9dcc8d76220daf35c9683af885f299cc0d0",
    "src/starfield_resource_reproducer/generation.py": "3dfedb5d4450bd4b996ddfd09266e1f9812df1c0",
    "tests/test_worked_case_validation.py": "a5b73f92c121b7bde048aa28f4d9ace1ae6098fd",
}

OFFLINE_SCHEMA = "srr013-retail-disk-inputs-v1"
SIMULATED_INPUT_EVIDENCE = {
    "schema": "srr013-retail-like-fixture-inputs-v1",
    "sample_plan": "SRR-012-sample-plan",
    "source": "owned-fixture-graph",
    "loader": "fixture-no-external-inputs",
}


@dataclass(frozen=True)
class InputDecision:
    profile: dict | None
    reason: str | None
    detail: str | None

    def as_dict(self):
        return {"profile": self.profile, "reason": self.reason, "detail": self.detail}


def verify_inputs(target_kind, evidence=None):
    """Project independent target admission and the receipt into the existing classifier."""
    if target_kind == "simulated":
        if evidence == SIMULATED_INPUT_EVIDENCE:
            return InputDecision(DISPOSABLE_INPUTS, None, None)
        if (isinstance(evidence, dict) and evidence.get("schema") == SIMULATED_INPUT_EVIDENCE["schema"]
                and evidence.get("loader") != SIMULATED_INPUT_EVIDENCE["loader"]):
            return InputDecision(None, "unsupported_native_input_source", "input loader conflicts with the qualified fixture graph")
        return InputDecision(None, "simulated_inputs_unverified", "fixture input evidence missing or contradictory")
    if target_kind != "retail":
        return InputDecision(None, "input_target_unverified", "target has no admitted input evidence kind")
    if not isinstance(evidence, dict) or evidence.get("schema") != OFFLINE_SCHEMA:
        return InputDecision(None, "offline_inputs_unverified", "retail requires a pinned disk source receipt")
    if evidence.get("master_sha256") != MASTER_SHA256:
        return InputDecision(None, "source_master_mismatch", "base master digest disagrees with SRR-012")
    if evidence.get("pack_commit") != PACK_COMMIT or evidence.get("pack_blobs") != PACK_BLOBS:
        return InputDecision(None, "prediction_source_mismatch", "pinned prediction sources disagree with SRR-012")
    if evidence.get("loose_csv_present") is True:
        return InputDecision(None, "unsupported_native_input_source", "loose BiomeData.csv needs independent applicability evidence")
    if evidence.get("loose_csv_present") is not False:
        return InputDecision(None, "offline_inputs_unverified", "loose BiomeData.csv check is inconclusive")
    return InputDecision(None, "runtime_effective_inputs_unverified",
                         "no qualified epoch-bound runtime loader, winner and native input evidence source")


def _blob_identity(path):
    # The pinned Git blobs have LF text. Worktree checkout can use CRLF.
    with path.open("rb") as stream:
        raw = stream.read(32 * 1024 * 1024 + 1)
    if len(raw) > 32 * 1024 * 1024:
        raise ValueError("prediction source exceeds the pinned-pack size bound")
    data = raw.replace(b"\r\n", b"\n")
    return sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest(), sha256(raw).hexdigest()


def _file_identity(stat):
    return stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns


def inspect_offline(master, pack):
    """Read the baseline master and pack. Return hashes and a limited disk inventory."""
    master = Path(master).resolve(strict=True)
    if master.name.casefold() != "starfield.esm" or master.parent.name.casefold() != "data":
        raise ValueError("supply the installed Data/Starfield.esm")
    with master.open("rb") as stream:
        before = os.fstat(stream.fileno())
        master_digest = file_digest(stream, "sha256").hexdigest()
        after = os.fstat(stream.fileno())
        if _file_identity(before) != _file_identity(after) or _file_identity(after) != _file_identity(master.stat()):
            raise ValueError("base master identity changed while reading")
    pack = Path(pack).resolve(strict=True)
    fingerprints = {name: _blob_identity(pack / name) for name in PACK_BLOBS}
    data = master.parent
    plugin_file_count = sum(
        path.is_file() for path in data.iterdir() if path.suffix.casefold() in (".esm", ".esp", ".esl")
    )
    try:
        (data / "Space" / "BiomeData.csv").stat()
        loose_csv_present = True
    except FileNotFoundError:
        loose_csv_present = False
    evidence = {
        "schema": OFFLINE_SCHEMA,
        "master_sha256": master_digest,
        "master_bytes": before.st_size,
        "pack_commit": PACK_COMMIT,
        "pack_blobs": {name: pair[0] for name, pair in fingerprints.items()},
        "pack_worktree_sha256": {name: pair[1] for name, pair in fingerprints.items()},
        "installed_plugin_file_count": plugin_file_count,
        "loose_csv_present": loose_csv_present,
    }
    return evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("master", type=Path, help="installed Data/Starfield.esm (read-only)")
    parser.add_argument("pack", type=Path, help="pinned sibling reproducer checkout (read-only)")
    args = parser.parse_args()
    evidence = inspect_offline(args.master, args.pack)
    decision = verify_inputs("retail", evidence)
    print(json.dumps({"evidence": evidence, "decision": decision.as_dict()}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
