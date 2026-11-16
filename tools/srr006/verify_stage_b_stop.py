"""Verify and report an SRR-010 scientific STOP without using a terminal receipt."""

import argparse
import hashlib
import json
from pathlib import Path


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def verify_stop(folder, run, sequence):
    seal = json.loads((folder / "stop-prefix.json").read_bytes())
    require(seal["schema"] == 1 and seal["sequence"] == sequence > 0, "Unexpected STOP sequence")
    digest = hashlib.sha256()
    remaining = seal["bytes"]
    epoch = None
    last = None
    with (folder / "events.jsonl").open("rb") as journal:
        for index in range(1, sequence + 1):
            require(remaining > 0, "STOP byte count ends before its sequence")
            raw = journal.readline(remaining)
            require(raw.endswith(b"\n"), "Incomplete journal row in STOP prefix")
            digest.update(raw)
            remaining -= len(raw)
            last = json.loads(raw)
            require(last["seq"] == index, "Nonconsecutive journal sequence")
            row_epoch = (last["run"], last["pid"], last["process_birth"], last["image_sha256"])
            if epoch is None and last["run"] == run:
                parts = run.split("-")
                require(last["kind"] in ("startup", "target_bound") and
                        row_epoch == (run, int(parts[1]), int(parts[2]), parts[0]),
                        "Invalid bound process identity")
                epoch = row_epoch
            if epoch is not None:
                require(row_epoch == epoch, "Process epoch changed within the STOP prefix")
            else:
                require(not last["run"] and last["kind"] in ("steam_component_drift", "steam_baseline"),
                        "Unexpected record before process binding")
    require(remaining == 0 and digest.hexdigest() == seal["sha256"], "STOP prefix bytes or SHA-256 mismatch")
    require(epoch is not None and last["kind"] == "stop" and last["stopped"] == 1, "Missing bound STOP row")
    windows = last["windows"]
    require(bool(windows) and windows[-1]["end"] == sequence and windows[-1]["stop_boundary"] == 1,
            "Incomplete STOP window summary")
    return dict(seal=seal, run=run, missing_boundary=last["missing_boundary"],
                checkpoint=last["checkpoint"], observer_healthy_at_stop=last["healthy"], windows=windows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    parser.add_argument("run", help="Full TARGET_BOUND run token")
    parser.add_argument("sequence", type=int, help="Sequence from STOP_DURABLE")
    args = parser.parse_args()
    try:
        print(json.dumps(verify_stop(args.folder, args.run, args.sequence), indent=2))
    except (OSError, ValueError, KeyError, IndexError, TypeError) as error:
        parser.exit(1, f"STOP verification failed: {error}\n")


if __name__ == "__main__":
    main()
