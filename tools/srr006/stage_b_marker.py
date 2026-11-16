"""Publish one challenged Stage B phase marker in a private observer run directory."""

import argparse
from pathlib import Path
import re

from qualify import space


LABELS = ("MAIN_MENU_CONFIRMED", "LOAD_BEGIN", "PLAYER_CONTROL", "LODGE_BEGIN", "LODGE_END")


def publish(folder, run, label, prior, challenge):
    space()
    temporary = folder / "phase.writing"
    with temporary.open("xb") as stream:
        stream.write(f"{run} {label} {prior} {challenge}\n".encode("ascii"))
    try:
        # Windows rename refuses if a prior submission is still pending.
        temporary.rename(folder / "phase.request")
    except OSError:
        temporary.unlink()
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    parser.add_argument("run")
    parser.add_argument("label", choices=LABELS)
    parser.add_argument("prior", type=int)
    parser.add_argument("challenge")
    args = parser.parse_args()
    if (not re.fullmatch(r"[0-9a-f]{64}-[1-9][0-9]*-[1-9][0-9]*(?:-[1-9][0-9]*)?", args.run)
            or args.prior <= 0 or not re.fullmatch("[0-9a-f]{32}", args.challenge)):
        parser.error("use the full run token, sequence and challenge from the preceding acknowledgement")
    if not (args.folder / "events.jsonl").is_file():
        parser.error("expected an existing observer run directory")
    publish(args.folder, args.run, args.label, args.prior, args.challenge)


if __name__ == "__main__":
    main()
