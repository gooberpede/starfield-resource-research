"""Exercise SRR-017 title admission and checked replay on owned fixtures only."""

import argparse
from contextlib import contextmanager
from functools import partial
import json
from pathlib import Path
import re
import struct
import subprocess
import sys
from time import monotonic, sleep

from tools.srr016.qualify_census import build_fixture, check_truth, fixture
from .title import (
    CLAIM, LIMITS, ROOT, checked_profile, digest, encode, file_digest, fixture_remap,
    owned_title, replay_owned, reserve_owned, source_manifest, write_exclusive,
)
from observe import JournalFailure
from memory import Windows, epoch
from native import FORM_MAP_SLOT


WORK = ROOT / ".local-work" / "codex" / "SRR-017"


def authorize(directory, image_sha256, limits, **overrides):
    authority = checked_profile(image_sha256, limits)
    authority["custody"] = str(directory)
    data = {**authority, "approval_reference": "owned-fixture:qualification", **overrides}
    path = directory / "authorization.json"
    write_exclusive(path, data)
    return path


def expect_exception(kind, action):
    try:
        action()
    except kind:
        return
    raise AssertionError(f"expected {kind.__name__}")


def observed_map_access(path, image_base, expected_capacity):
    """Check the high-capacity case from byte-level read evidence, not fixture input."""
    metadata, entries = [], []
    map_slot = image_base + FORM_MAP_SLOT
    map_address = table = None
    with path.open("rb") as stream:
        for line in stream:
            event = json.loads(line)
            if event["kind"] != "read" or "value" not in event:
                continue
            address, size, _ = event["args"]
            if address == map_slot and size == 8:
                map_address, = struct.unpack("<Q", bytes.fromhex(event["value"]))
            if map_address is not None and address == map_address + 0x10 and size == 16:
                table, capacity = struct.unpack("<QQ", bytes.fromhex(event["value"]))
                metadata.append(capacity)
            if table is not None and table <= address < table + expected_capacity * 0x18:
                if size != 20 or (address - table) % 0x18:
                    raise AssertionError("native-scale map collection read outside individual entry geometry")
                entries.append((address - table) // 0x18)
    # Opening, consumed-window reread and closing-anchor reread in each pass.
    if metadata != [expected_capacity] * 6 or not entries or max(entries) < expected_capacity // 2:
        raise AssertionError("two complete plans and rereads did not exercise the grown table extent")
    return {"capacity": expected_capacity, "entry_reads": len(entries), "highest_bucket": max(entries)}


@contextmanager
def with_exit_witness(directory, target, image_sha256):
    """Bind the predecessor's separate query-and-wait witness to an owned PID."""
    with (directory / "exit-witness.log").open("xb") as log:
        with fixture(target, "direct") as (process, command):
            pid, creation = epoch(Windows(), int(process._handle))
            run_token = f"{image_sha256}-{pid}-{creation}"
            watcher = subprocess.Popen([sys.executable, "-E", "-B", str(ROOT / "tools/srr008/watch_exit.py"),
                                        run_token, str(target), str(directory)],
                                       stdout=log, stderr=subprocess.STDOUT,
                                       creationflags=subprocess.CREATE_NO_WINDOW)
            try:
                bound_path = directory / "exit-witness-bound.json"
                watchdog = monotonic() + 30
                while not bound_path.is_file():
                    if watcher.poll() is not None or monotonic() >= watchdog:
                        raise RuntimeError("owned fixture exit witness did not bind")
                    sleep(0.025)
                yield process, command
            except BaseException:
                # This branch can terminate only the disposable witness we launched.
                if watcher.poll() is None:
                    watcher.terminate()
                    watcher.wait(timeout=30)
                raise
        try:
            if watcher.wait(timeout=30):
                raise RuntimeError("owned fixture exit witness failed after cooperative Quit")
        except subprocess.TimeoutExpired:
            watcher.terminate()
            watcher.wait(timeout=30)
            raise
        result = json.loads((directory / "exit-witness-result.json").read_bytes())
        if ((result["pid"], result["process_birth"], result["run"], result["exit_code"]) !=
                (pid, creation, run_token, 0) or result["signaled"] is not True):
            raise AssertionError("independent exit witness disagrees with the owned process epoch")


def run(directory):
    directory.mkdir(parents=True, exist_ok=False)
    target, build = build_fixture(directory, map_capacity=LIMITS["form_capacity"])
    image_sha256 = build["fixture_sha256"]
    checks = {}
    for case, scenario, overrides, failure in (
        ("direct", "direct", {}, None),
        ("corpus", "corpus", {}, None),
        ("upper", "upper", {}, None),
        ("namespace-drift", "direct", {}, "pair_namespace_mismatch"),
        ("namespace-invalid", "namespace-invalid", {}, "namespace_witness_refused"),
        ("entries", "direct", {"entries": 5}, "traversal_budget"),
        ("capacity", "direct", {"form_capacity": 0x400000}, "traversal_budget"),
        ("cancel", "direct", {}, "operator_cancelled"),
        ("journal", "direct", {"journal_bytes": 24 * 1024}, "journal_budget"),
    ):
        case_dir = directory / case
        case_dir.mkdir()
        auth_limits = {**LIMITS, **overrides}
        authorization = authorize(case_dir, image_sha256, auth_limits)

        def launch(binary):
            if case == "direct":
                return with_exit_witness(case_dir, binary, image_sha256)
            return fixture(binary, scenario)

        action = partial(owned_title, case_dir, authorization, target, image_sha256, launch, auth_limits,
                         cancelled=lambda: case == "cancel",
                         between=(lambda command: command("namespace-drift")) if case == "namespace-drift" else None)
        path = case_dir / "title.jsonl"
        if case == "journal":
            expect_exception(JournalFailure, action)
            pending_bytes = path.with_name(path.name + ".partial").stat().st_size
            assert not path.exists() and 0 < pending_bytes < auth_limits["journal_bytes"]
            assert (case_dir / CLAIM).is_file()
            expect_exception(FileExistsError, action)
            checks[case] = {"failure": failure, "pending_bytes": pending_bytes}
            continue

        report, truth, counts, caps = action()
        expect_exception(FileExistsError, action)
        if report != replay_owned(path) or (report["failure"] or [None])[0] != failure:
            raise AssertionError(f"{case} acquisition or replay differs: {report['failure']}")
        if failure is None:
            check_truth(case, truth, report, fixture_remap())
            for collection in report["collections"]:
                namespace = collection["source_witness"]["namespace"]
                vectors = collection["source_witness"]["vectors"]
                assert namespace["compiled"] == [{"plugin": "fixture.esm", "kind": "full", "index": 0}]
                assert vectors and all(names == ["fixture.esm"] for names in vectors.values())
        elif case.startswith("namespace-"):
            first, second = report["collections"]
            assert all(item["coverage_verified"] and item["mixed_visited"] == 6 for item in (first, second))
            assert first["raw_rows"] == second["raw_rows"] and report["structure"] == "QUALIFIED"
            if case == "namespace-drift":
                assert first["source_identity_sha256"] != second["source_identity_sha256"]
                assert all(names == ["drifted.esm"] for names in second["source_witness"]["vectors"].values())
            else:
                assert all(item["source_failure"][0] == "namespace_file_slot_disagreement"
                           for item in (first, second))
        checks[case] = {"failure": failure, "coverage": report["coverage_counts"],
                        "backend": counts, "backend_caps": caps,
                        "events": report["events"], "requested_bytes": report["requested_bytes"],
                        "receipt_sha256": file_digest(path), "receipt_bytes": path.stat().st_size}
        if failure is None:
            checks[case]["form_map"] = observed_map_access(
                path, report["identity_brackets"][0][0]["image_base"], LIMITS["form_capacity"])
        print(f"{case}: {failure or report['normalization']}", flush=True)

    for field, wrong in (("scope", "srr013-structural-title"), ("custody", str(directory)),
                         ("input_sha256", "a" * 64), ("work_sha256", "b" * 64), ("source_sha256", "c" * 64),
                         ("approval_reference", "outside-fixture-scope")):
        case_dir = directory / f"wrong-{field}"
        case_dir.mkdir()
        authorization = authorize(case_dir, image_sha256, LIMITS, **{field: wrong})
        expect_exception(ValueError, lambda: reserve_owned(case_dir, authorization, image_sha256, LIMITS))
        assert not (case_dir / CLAIM).exists()

    # Change validly encoded evidence outside the sealed acquisition file.
    direct = directory / "direct"
    claim = direct / CLAIM
    original = claim.read_bytes()
    try:
        claim.write_bytes(original.replace(b'"scope":"srr017-owned-title"', b'"scope":"srr013-structural-title"'))
        expect_exception(ValueError, lambda: replay_owned(direct / "title.jsonl"))
    finally:
        claim.write_bytes(original)

    manifest = source_manifest()
    write_exclusive(directory / "source-manifest.json", manifest)
    write_exclusive(directory / "qualification.json", {
        "source_sha256": digest(manifest), "work_sha256": digest(LIMITS), "limits": LIMITS,
        "fixture_build": build, "controls": checks, "authorization_negatives": 6, "replay_authority_negative": True,
        "independent_owned_exit_witness_sha256": file_digest(direct / "exit-witness-result.json"),
    })
    print(f"{len(checks)} owned acquisition controls, 6 authorization refusals, 1 replay authority refusal")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    qualify = commands.add_parser("owned-title", help="build and test the owned path")
    qualify.add_argument("run", type=str)
    commands.add_parser("source-manifest", help="emit the owned execution source manifest")
    replay = commands.add_parser("replay-owned", help="check one sealed owned title receipt")
    replay.add_argument("receipt", type=Path)
    args = parser.parse_args()
    if args.command == "source-manifest":
        print(encode(source_manifest()).decode("ascii"))
    elif args.command == "replay-owned":
        print(encode(replay_owned(args.receipt)["observation"]).decode("ascii"))
    elif re.fullmatch(r"[a-zA-Z0-9-]{1,64}", args.run):
        run(WORK / args.run)
    else:
        parser.error("use a fresh run name of 1–64 letters, digits or hyphens")


if __name__ == "__main__":
    main()
