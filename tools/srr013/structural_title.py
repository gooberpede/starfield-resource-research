"""Proposed single-use title-only entry point for a separately authorized run."""

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path

from checkpoint import issue, mark
from contract import STRUCTURAL_MODE
from memory import ReadFailure
from observe import capture_refusal, encode
from retail_admission import begin_retail, open_retail
from retail_controller import _observe

SCOPE = "srr013-structural-title"
SOURCES = ("checkpoint.py", "contract.py", "memory.py", "native.py", "observe.py", "retail_admission.py",
           "retail_controller.py", "retail_inputs.py", "structural_title.py")


def source_identity():
    here = Path(__file__).resolve().parent
    manifest = "".join(f"{sha256((here / name).read_bytes()).hexdigest()}  {name}\n" for name in SOURCES)
    return sha256(manifest.encode("ascii")).hexdigest()


def reserve_authorization(path, custody):
    """Check the scope of the operator's separately approved private record."""
    path = Path(path).resolve(strict=True)
    custody = Path(custody).resolve(strict=True)
    if path.parent != custody:
        raise ValueError("the separate authorization record must be in the approved private custody directory")
    with path.open("rb") as stream:
        raw = stream.read(4097)
    if len(raw) > 4096:
        raise ValueError("authorization record exceeds its size bound")
    data = json.loads(raw)
    if (not isinstance(data, dict) or set(data) != {"scope", "source_sha256", "approval_reference", "custody"}
            or data["scope"] != SCOPE or data["source_sha256"] != source_identity()
            or data["custody"] != str(custody)
            or not isinstance(data["approval_reference"], str) or not data["approval_reference"].strip()):
        raise ValueError("authorization record does not identify this title-only candidate and separate written approval")
    receipt = {"scope": SCOPE, "source_sha256": data["source_sha256"],
               "authorization_sha256": sha256(raw).hexdigest()}
    # The approved private directory is the stable custody boundary for this one run.
    # An existing claim, including one from a failed attempt, prevents another open.
    with (custody / "title-authorization.used").open("xb") as stream:
        stream.write(encode(receipt) + b"\n")
        stream.flush()
        os.fsync(stream.fileno())
    return receipt


def operator_response(prompt):
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt) as error:
        raise ReadFailure("operator_declined", "operator confirmation was interrupted") from error


def run(steam_root, custody, authorization):
    custody = Path(custody).resolve(strict=True)
    approved = reserve_authorization(authorization, custody)
    receipt = custody / "title.jsonl"
    binding = {"target_kind": "retail", "marker": {"label": "title"}, "authority": approved}
    try:
        with begin_retail(steam_root) as baseline:
            operator_response("Steam baseline retained. Perform the authorized launch, then press Enter at the responsive title card. ")
            with open_retail(baseline) as reader:
                identity = reader.identity()
                attempt = issue(custody, STRUCTURAL_MODE)
                answer = operator_response("Confirm the authenticated title card is responsive and held. Type title to observe once. ")
                if answer.strip() != "title":
                    raise ReadFailure("operator_declined", "operator did not confirm the title-card checkpoint")
                marker = mark(attempt, identity, "title")
                binding.update(attempt=attempt, marker=marker)
                report = _observe(receipt, custody, lambda: reader, binding, None, STRUCTURAL_MODE)
    except ReadFailure as error:
        report = capture_refusal(receipt, "title", error, mode=STRUCTURAL_MODE, binding=binding)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="action", required=True)
    subcommands.add_parser("source-identity", help="hash inspector sources offline")
    observe = subcommands.add_parser("observe-title", help="perform the separately authorized one-time title observation")
    observe.add_argument("steam_root", type=Path)
    observe.add_argument("custody", type=Path)
    observe.add_argument("authorization", type=Path)
    args = parser.parse_args()
    if args.action == "source-identity":
        print(source_identity())
    else:
        report = run(args.steam_root, args.custody, args.authorization)
        print(json.dumps({"outcomes": report["counts"], "failure": report["failure"]}, indent=2))


if __name__ == "__main__":
    main()
