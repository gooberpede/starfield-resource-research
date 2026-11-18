"""Run external reads against children built from the tracked SRR-013 fixture."""

import argparse
from contextlib import ExitStack, contextmanager
from hashlib import file_digest
import json
from pathlib import Path
from queue import Empty, Queue
import subprocess
from threading import Thread

from contract import CHECKPOINTS, DISPOSABLE_INPUTS, EMPTY, INDETERMINATE, POPULATED, SAMPLES, UNPOPULATED
from memory import ReadFailure, open_owned
from observe import capture, capture_refusal, encode, replay

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / ".local-work" / "codex" / "SRR-013"
FIXTURE = WORK / "build" / "srr013-fixture.exe"
IO_SECONDS = 5

ACCEPTED = {
    "populated": (POPULATED,) * 4,
    "direct": (POPULATED,) * 4,
    "depth2": (POPULATED,) * 4,
    "native-boundary": (POPULATED,) * 4,
    "native-depth2": (POPULATED,) * 4,
    "leaf-only": (POPULATED,) * 4,
    "predecessor": (POPULATED,) * 4,
    "holes": (POPULATED,) * 4,
    "root-end": (POPULATED,) * 4,
    "zero": (UNPOPULATED,) * 4,
    "mixed": (POPULATED, UNPOPULATED, INDETERMINATE, POPULATED),
    "effective-inputs-unverified": (INDETERMINATE,) * 4,
    "stable-clear": (UNPOPULATED,) * 4,
    "after-restore": (POPULATED,) * 4,
    "aba": (POPULATED,) * 4,
}
CONTROL = "comparison_control_failed"
GAP = "range_coverage"
MATCH = "tuple_match"
REFUSALS = {
    "absent": (GAP, "component_absent", GAP, CONTROL),
    "empty": ("component_absent",) * 4,
    "duplicate": (GAP, GAP, "component_duplicate", CONTROL),
    "wrong-owner": (GAP, "component_absent", GAP, CONTROL),
    "wrong-type": ("edge_type_mismatch",) * 3 + (CONTROL,),
    "wrong-registry": ("registry_unverified",) * 4,
    "wrong-map": (MATCH, "pointer_alias", MATCH, MATCH),
    "map-loop": (MATCH, "form_map_unverified", MATCH, MATCH),
    "wrong-rnam": (MATCH, "input_drift", MATCH, MATCH),
    "wrong-seed": ("input_drift",) * 3 + (CONTROL,),
    "wrong-override": (MATCH, "input_drift", MATCH, MATCH),
    "ineligible-zero": (MATCH, "input_drift", MATCH, MATCH),
    "wrong-biom": ("edge_biom_mismatch",) * 3 + (CONTROL,),
    "unaligned": ("invalid_pointer",) * 4,
    "unreadable": ("unreadable_region",) * 4,
    "loop": ("pointer_alias",) * 4,
    "bad-count": ("index_shape",) * 4,
    "bad-directory": ("index_shape",) * 4,
    "bad-minimum": ("block_minimum",) * 4,
    "lying-minimum": ("block_minimum",) * 4,
    "overlap": ("record_span",) * 4,
    "excessive": ("traversal_budget",) * 4,
    "leaf-decoy": ("component_duplicate", GAP, GAP, CONTROL),
    "context-absent": ("context_absent",) * 4,
    "context-decoy": ("context_ambiguous",) * 4,
    "wrong-context-vptr": ("owner_type_mismatch",) * 4,
    "unregistered": ("registry_unverified",) * 4,
    "mapped-image": ("mapped_image_mismatch",) * 4,
    "no-read-rights": ("read_access_denied",) * 4,
    "epoch-mismatch": ("epoch_mismatch",) * 4,
    "query-only": ("insufficient_read_rights",) * 4,
    "clear": ("inconsistent_pair",) * 4,
    "insert": ("inconsistent_pair",) * 4,
    "remove": ("inconsistent_pair",) * 4,
    "mid-read-insert": ("structural_change",) * 4,
}

KNOWN_KEYS = ((0xD9BAC, 0x23C0CE, 0x2C9985), (0xC5717,))


def digest(path):
    with path.open("rb") as source:
        return file_digest(source, "sha256").hexdigest()


@contextmanager
def owned_fixture(scenario, fixture):
    proc = subprocess.Popen([str(fixture), scenario], cwd=fixture.parent,
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True,
                            encoding="ascii", creationflags=subprocess.CREATE_NO_WINDOW)
    replies = Queue(maxsize=8)

    def read_replies():
        for line in proc.stdout:
            replies.put(line.rstrip("\r\n"), timeout=IO_SECONDS)
        replies.put(None, timeout=IO_SECONDS)

    Thread(target=read_replies, daemon=True).start()

    def expect(expected):
        try:
            actual = replies.get(timeout=IO_SECONDS)
        except Empty as exc:
            raise RuntimeError(f"fixture timed out waiting for {expected}") from exc
        if actual != expected:
            raise RuntimeError(f"fixture protocol: expected {expected}, got {actual!r}")

    def command(value):
        proc.stdin.write(value + "\n")
        proc.stdin.flush()
        if value != "quit":
            expect("ACK")

    try:
        expect("READY")
        yield proc, command
    finally:
        try:
            if proc.poll() is None:
                command("quit")
        finally:
            proc.stdin.close()
            exit_code = proc.wait(timeout=IO_SECONDS)
            proc.stdout.close()
        if exit_code != 0:
            raise RuntimeError(f"disposable fixture exited with status {exit_code}")


def check(case, report):
    rows = report["samples"]
    actual = tuple(row["outcome"] for row in rows)
    if case in ACCEPTED:
        if actual != ACCEPTED[case]:
            raise AssertionError(f"{case}: expected {ACCEPTED[case]}, got {actual}")
    elif case in REFUSALS:
        reasons = tuple(row["reason"] for row in rows)
        expected = tuple(POPULATED if reason == MATCH else INDETERMINATE for reason in REFUSALS[case])
        if reasons != REFUSALS[case] or actual != expected:
            raise AssertionError(f"{case}: expected {REFUSALS[case]}, got {reasons}")
    if case in ("populated", "direct", "depth2", "leaf-only", "predecessor", "holes", "root-end", "zero", "mixed"):
        for collection in report["collections"]:
            ranges = collection["ranges"]
            keys = tuple(tuple(entry["key"][1] for entry in bounds["entries"]) for bounds in ranges)
            if keys != KNOWN_KEYS or not all(bounds["coverage_verified"] for bounds in ranges):
                raise AssertionError(f"{case}: native enumeration differs from the independent fixture plan")
            if case == "root-end" and ranges[1]["termination"] != "root_end":
                raise AssertionError("Decaran range did not verify the root-backed end")
    if case == "leaf-decoy":
        for collection in report["collections"]:
            kreet = collection["ranges"][0]
            keys = tuple(entry["key"][1] for entry in kreet["entries"])
            if keys != (0xD9BAC, *KNOWN_KEYS[0]) or kreet["coverage_verified"]:
                raise AssertionError("successor-leaf duplicate was hidden from the acquired range")
    if case == "effective-inputs-unverified" and any(
        row["reason"] != "effective_inputs_unverified" or row["prediction_comparison"] != "conditional"
        or tuple(row["observed_words"]) != sample.expected
        for sample, row in zip(SAMPLES, rows, strict=True)
    ):
        raise AssertionError("raw words or conditional comparison were lost")
    if case == "ineligible-zero" and tuple(rows[1]["observed_words"]) != EMPTY:
        raise AssertionError("ineligible zero fixture did not present seven zero words")
    for sample, row in zip(SAMPLES, rows, strict=True):
        if row["outcome"] in (POPULATED, UNPOPULATED):
            expected = sample.expected if row["outcome"] == POPULATED else EMPTY
            if tuple(row["observed_words"]) != expected or tuple(row["repeat_words"]) != expected:
                raise AssertionError(f"{case}: verdict does not match both observed tuples")
    if case in ("clear", "insert", "remove") and report["failure"] != "inconsistent_pair":
        raise AssertionError(f"{case}: observed mutation did not invalidate the pair")


def run_case(case, path, image_hash, checkpoint, *, fixture=FIXTURE):
    mutable = case in ("clear", "insert", "remove", "stable-clear", "after-restore", "aba", "race", "mid-read-insert")
    special = case in ("epoch-mismatch", "query-only", "effective-inputs-unverified")
    scenario = "populated" if mutable or special else case
    options = {}
    if case == "epoch-mismatch":
        options["expected_creation"] = 0
    if case == "query-only":
        options["query_only"] = True
    with owned_fixture(scenario, fixture) as (proc, command), ExitStack() as entered:
        try:
            reader = entered.enter_context(open_owned(proc, fixture, image_hash, **options))
        except ReadFailure as error:
            return capture_refusal(path, checkpoint, error)
        if case in ("stable-clear", "after-restore"):
            command("clear")
        if case == "after-restore":
            command("restore")
        if case == "race":
            command("race")
        try:
            between = (lambda: command(case)) if case in ("clear", "insert", "remove", "aba") else None
            inputs = None if case == "effective-inputs-unverified" else DISPOSABLE_INPUTS
            inserted = False

            def interrupt_collection(_address, size, _alignment):
                nonlocal inserted
                if not inserted and size == 7 * 4:
                    command("insert")
                    inserted = True

            after_read = interrupt_collection if case == "mid-read-insert" else None
            return capture(path, reader, checkpoint, inputs, between=between, after_read=after_read)
        finally:
            if case == "race":
                command("stop")


def qualify(directory):
    from build_fixture import build

    directory.mkdir(parents=True, exist_ok=False)
    fixture = directory / "build" / FIXTURE.name
    build_manifest = build(fixture.parent)
    image_hash = digest(fixture)
    if image_hash != build_manifest["fixture_sha256"]:
        raise RuntimeError("disposable build identity changed before launch")
    summary = {"fixture_sha256": image_hash, "build": build_manifest, "cases": []}
    for number, case in enumerate((*ACCEPTED, *REFUSALS, "race")):
        path = directory / f"{case}.jsonl"
        report = run_case(case, path, image_hash, CHECKPOINTS[number % len(CHECKPOINTS)], fixture=fixture)
        reproduced = replay(path)
        if encode(report) != encode(reproduced):
            raise AssertionError(f"{case}: replay differs")
        check(case, report)
        entry = {"case": case, "evidence_sha256": digest(path), "failure": report["failure"],
                 "samples": [[row["outcome"], row["reason"]] for row in report["samples"]],
                 "calls": report["read_and_identity_calls"], "bytes": report["requested_bytes"]}
        summary["cases"].append(entry)
        print(f"{case}: {entry['samples']}", flush=True)
    (directory / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf8")
    return summary


def main():
    command = argparse.ArgumentParser(description=__doc__)
    subcommands = command.add_subparsers(dest="operation", required=True)
    run = subcommands.add_parser("run", help="build the owned fixture and run the qualification cases")
    run.add_argument("name", help="new receipt directory name under the ignored SRR-013 directory")
    rerun = subcommands.add_parser("replay", help="reproduce a sealed receipt without opening a process")
    rerun.add_argument("receipt", type=Path)
    args = command.parse_args()
    if args.operation == "replay":
        print(json.dumps(replay(args.receipt), indent=2))
    else:
        if not args.name.isascii() or not args.name.replace("-", "").replace("_", "").isalnum():
            command.error("receipt directory name must contain letters, digits, hyphens or underscores")
        qualify(WORK / args.name)


if __name__ == "__main__":
    main()
