"""Publish one SRR-009 operator marker in the private run directory."""
import argparse
import json
import re
from pathlib import Path

from qualify import space


MARKERS = {
    "TITLE_CONFIRMED": ("title", 1, False),
    "MAIN_MENU_CONFIRMED": ("menu", 2, True),
    "STOP": ("stop", 3, False),
    "QUIT_REQUESTED": ("retire", 4, True),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    parser.add_argument("run")
    parser.add_argument("label", choices=MARKERS)
    parser.add_argument("prior", type=int, nargs="?", default=0)
    args = parser.parse_args()
    name, ordinal, requires_prior = MARKERS[args.label]
    if (not re.fullmatch(r"[0-9a-f]{64}-[1-9][0-9]*-[1-9][0-9]*-[1-9][0-9]*", args.run)
            or args.prior < 0 or bool(args.prior) != requires_prior):
        parser.error("use the full TARGET_BOUND token and the required sequence")
    if not (args.folder / "events.jsonl").is_file():
        parser.error("expected an existing observer run directory")
    if args.label == "MAIN_MENU_CONFIRMED":
        # Bind the menu statement to the acknowledged arming barrier.
        with (args.folder / "events.jsonl").open("rb") as stream:
            for line in stream:
                if not line.endswith(b"\n"):
                    parser.error("arming receipt is incomplete")
                row = json.loads(line)
                if row["seq"] == args.prior:
                    if row["kind"] == "attach_barrier" and row["run"] == args.run:
                        break
                    parser.error("prior must be the ATTACH_ARMED sequence for this run")
            else:
                parser.error("attach_barrier sequence missing")
    space()
    temporary = args.folder / (name + ".writing")
    with temporary.open("xb") as stream:
        stream.write(f"{args.run} {ordinal} {args.label} {args.prior}\n".encode("ascii"))
    temporary.replace(args.folder / (name + ".request"))


if __name__ == "__main__":
    main()
