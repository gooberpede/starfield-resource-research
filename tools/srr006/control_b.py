"""Publish and verify Control B markers in an existing private run directory."""

import argparse
import hashlib
import json
from pathlib import Path
import re

from stage_b_marker import publish
from verify_stage_b_stop import require

PHASES = ("CONTROL_MENU_CONFIRMED", "CONTROL_LOAD_BEGIN", "SETTLED_GAMEPLAY", "CONTROL_END")
RUN = re.compile(r"([0-9a-f]{64})-([1-9][0-9]*)-([1-9][0-9]*)(?:-[1-9][0-9]*)?")
BOUNDARIES = {
    "ready": "debugger_only_barrier",
    "menu": "control_menu",
    "load": "control_load_begin",
    "settled": "control_settled",
    "end": "control_end",
}


def verify_boundary(folder, run, name, sequence):
    epoch = RUN.fullmatch(run)
    require(epoch and sequence > 0, "Invalid run token or sequence")
    digest, pid, birth = epoch.groups()
    sidecar = "operational-end-prefix.json" if name == "end" else "durable-prefix.json"
    seal = json.loads((folder / sidecar).read_bytes())
    require(seal["schema"] == 1 and seal["sequence"] >= sequence > 0 and seal["bytes"] > 0,
            "Boundary is outside the durable prefix")
    if name == "end":
        require(seal["sequence"] == sequence, "Wrong operational end sequence")
    with (folder / "events.jsonl").open("rb") as stream:
        prefix = stream.read(seal["bytes"])
    require(len(prefix) == seal["bytes"] and prefix.endswith(b"\n") and
            hashlib.sha256(prefix).hexdigest() == seal["sha256"], "Durable prefix bytes or digest differ")
    rows = [json.loads(line) for line in prefix.splitlines()]
    require(len(rows) == seal["sequence"], "Journal row count differs")
    bound = False
    for index, row in enumerate(rows, 1):
        require(row["seq"] == index and row["control_mode"] == "debugger_only",
                "Unexpected sequence or observer mode")
        if row["run"] == run:
            require(bound or row["kind"] in ("startup", "target_bound"), "Wrong first bound row")
            bound = True
            require((row["pid"], row["process_birth"], row["image_sha256"]) == (int(pid), int(birth), digest),
                    "Process epoch or image differs")
        else:
            require(not bound and not row["run"] and row["kind"] in ("steam_component_drift", "steam_baseline"),
                    "Unexpected unbound row")
    boundary = rows[sequence - 1]
    require(boundary["run"] == run and boundary["kind"] == BOUNDARIES[name] and boundary["healthy"],
            "Wrong or unhealthy boundary")
    require(not any(row["kind"] == "arm_attempt" or row.get("owner") == "hardware" for row in rows),
            "Research breakpoint activity in Control B")
    if name == "ready":
        prior = rows[:sequence - 1]
        require(boundary["continued"] and boundary["research_context_writes"] == 0 and
                any(r["kind"] == "non_killing_policy" and r["confirmed"] for r in prior) and
                any(r["kind"] == "stopped_admission" and r["prearm_checks"] for r in prior) and
                any(r["kind"] == "event" and r.get("owner") == "loader" and r["continued"] for r in prior),
                "Readiness lacks native attach or continuation proof")
    else:
        require(boundary["checkpoint"] == 1 and 0 < boundary["prior"] < sequence,
                "Invalid read-only checkpoint")
        predecessor = tuple(BOUNDARIES.values())[tuple(BOUNDARIES).index(name) - 1]
        require(rows[boundary["prior"] - 1]["kind"] == predecessor, "Unexpected predecessor")
    return dict(seal=seal, run=run, boundary=boundary)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    marker = commands.add_parser("marker")
    marker.add_argument("folder", type=Path)
    marker.add_argument("run")
    marker.add_argument("label", choices=PHASES)
    marker.add_argument("prior", type=int)
    marker.add_argument("challenge")
    verify = commands.add_parser("verify")
    verify.add_argument("folder", type=Path)
    verify.add_argument("run")
    verify.add_argument("boundary", choices=BOUNDARIES)
    verify.add_argument("sequence", type=int)
    args = parser.parse_args()
    try:
        if args.command == "marker":
            require(RUN.fullmatch(args.run) and args.prior > 0 and
                    re.fullmatch("[0-9a-f]{32}", args.challenge), "Malformed phase binding")
            require((args.folder / "events.jsonl").is_file(), "Use an existing observer run directory")
            publish(args.folder, args.run, args.label, args.prior, args.challenge)
        else:
            print(json.dumps(verify_boundary(args.folder, args.run, args.boundary, args.sequence), indent=2))
    except (OSError, ValueError, KeyError, TypeError, IndexError, RuntimeError) as error:
        parser.exit(1, f"Control B: {error}\n")


if __name__ == "__main__":
    main()
