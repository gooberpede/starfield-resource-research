"""Qualify SRR-013's proposed admission and checkpoint protocol on owned children."""

import argparse
from contextlib import ExitStack, contextmanager
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
from shutil import copyfile
from time import sleep

from checkpoint import FILETIME_UNIX_EPOCH, MARKER_MAX_AGE_NS, _issued_bytes, issue, mark
from contract import CHECKPOINTS, INDETERMINATE, POPULATED, UNPOPULATED
from memory import PROCESS_QUERY_INFORMATION, PROCESS_VM_READ, ReadFailure, Windows, epoch
from observe import encode, replay
from qualify import FIXTURE, ROOT, check, digest, owned_fixture, qualify
from retail_admission import begin_simulated, open_simulated
from retail_controller import observe_window
from retail_inputs import MASTER_SHA256, OFFLINE_SCHEMA, PACK_BLOBS, PACK_COMMIT, SIMULATED_INPUT_EVIDENCE

WORK = ROOT / ".local-work" / "codex" / "SRR-013-retail"

POSITIVE = {"title": "populated", "menu": "zero", "settled-gameplay": "mixed", "aba": "aba",
            "stable-clear": "stable-clear", "ineligible-zero": "ineligible-zero", "wrong-map": "wrong-map",
            "duplicate": "duplicate", "lying-minimum": "lying-minimum", "wrong-owner": "wrong-owner",
            "absent": "absent", "bad-directory": "bad-directory", "wrong-registry": "wrong-registry",
            "clear": "clear", "mid-read-insert": "mid-read-insert"}
REFUSE = {
    "marker-epoch": "marker_epoch", "marker-token": "marker_token", "marker-stale": "marker_stale",
    "marker-order": "marker_order", "marker-duplicate": "marker_duplicate",
    "marker-before-epoch": "marker_before_epoch",
    "identity-drift": "mapped_image_mismatch", "mapped-image": "mapped_image_mismatch",
    "no-read-rights": "read_access_denied", "query-only": "insufficient_read_rights",
    "wrong-steam": "steam_attribution_failed", "wrong-epoch": "epoch_mismatch",
    "wrong-session": "session_mismatch", "duplicate-process": "process_ambiguous",
    "wrong-hash": "image_hash_mismatch", "wrong-backing": "mapping_unverified",
}


def simulated_append(log, pid, fixture):
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with log.open("a", encoding="utf8", newline="\n") as stream:
        stream.write(f'[{stamp}] AppID 1716740 adding PID {pid} as a tracked process ""{fixture.resolve()}""\n')


def assert_replay(path, report):
    reproduced = replay(path)
    if encode(reproduced) != encode(report):
        raise AssertionError(f"offline replay differed for {path.name}")


def run_case(directory, fixture, case, *, mode=None, scenario=None):
    path = directory / f"{case}.jsonl"
    log = directory / f"{case}.steam.log"
    log.write_bytes(b"disposable Steam attribution baseline\n")
    expected_hash = "0" * 64 if case == "wrong-hash" else digest(fixture)
    baseline = begin_simulated(fixture, expected_hash, log)
    access_requests = []
    open_process = baseline.api.OpenProcess

    def record_access(access, inherit, pid):
        access_requests.append((access, inherit, pid))
        return open_process(access, inherit, pid)

    baseline.api.OpenProcess = record_access
    launch = case if case in ("mapped-image", "no-read-rights") else POSITIVE.get(case, "populated")
    if launch in ("aba", "stable-clear", "clear", "mid-read-insert"):
        launch = "populated"
    if case == "unverified-zero":
        launch = "zero"
    if scenario is not None:
        launch = scenario
    actual_fixture = fixture
    if case == "wrong-backing":
        alternate = directory / "different-backing"
        alternate.mkdir()
        actual_fixture = alternate / fixture.name
        copyfile(fixture, actual_fixture)
    with owned_fixture(launch, actual_fixture) as (proc, command), ExitStack() as stack:
        if case == "wrong-backing":
            # Lie in the launch witness as well as the simulated Steam line.
            # The actual Windows main-image path must still defeat admission.
            proc.args = [str(fixture), launch]
        if case == "duplicate-process":
            stack.enter_context(owned_fixture("populated", fixture))
        pid, creation = epoch(Windows(), int(proc._handle))
        simulated_append(log, pid + (1 if case == "wrong-steam" else 0), fixture)
        mode_options = {} if mode is None else {"mode": mode}
        attempt = issue(directory, **mode_options)
        checkpoint = case if case in CHECKPOINTS else "title"
        marker = mark(attempt, {"pid": pid, "creation": creation}, checkpoint)
        if case == "marker-epoch":
            marker["creation"] += 1
        if case == "marker-token":
            marker["token"] = "0" * 32
        if case == "marker-mode":
            marker["mode"] = "strict"
        if case in ("marker-stale", "marker-order", "marker-before-epoch"):
            delta = (marker["utc_ns"] - (creation - FILETIME_UNIX_EPOCH) * 100 + 1_000_000_000
                     if case == "marker-before-epoch" else MARKER_MAX_AGE_NS + 1_000_000_000)
            # Issue an old, valid token with coherent test clocks instead of waiting 30 seconds.
            if case != "marker-order":
                for name in ("issued_ns", "issued_utc_ns"):
                    attempt[name] -= delta
                (directory / f"{attempt['token']}.issued").write_bytes(_issued_bytes(attempt))
                marker["mono_ns"] -= delta
                marker["utc_ns"] -= delta
            else:
                marker["mono_ns"] += delta
        binding = {"target_kind": "simulated", "attempt": attempt, "marker": marker}
        inputs = SIMULATED_INPUT_EVIDENCE
        if case in ("unverified-positive", "unverified-zero"):
            inputs = None
        if case == "contradictory-inputs":
            inputs = {**SIMULATED_INPUT_EVIDENCE, "loader": "unsupported-native-fallback"}
        options = {"query_only": case == "query-only"}
        if case == "wrong-epoch":
            options["expected_creation"] = creation + 1
        if case == "wrong-session":
            options["expected_session"] = 0xFFFFFFFF
        if case == "stable-clear":
            command("clear")
        between = (lambda: command(case)) if case in ("clear", "aba", "drift-resource") else None
        injected = False

        def disturb(_address, size, _alignment):
            nonlocal injected
            if not injected and size == 7 * 4:
                if case == "budget-expired":
                    sleep(5.05)
                else:
                    command("insert" if case == "mid-read-insert" else "drift-image")
                injected = True

        after_read = disturb if case in ("mid-read-insert", "identity-drift", "budget-expired") else None
        if case == "marker-duplicate":
            initial = directory / "marker-duplicate-first.jsonl"
            first = observe_window(initial, directory, open_simulated(baseline, proc), binding, inputs, **mode_options)
            first_expected = "STRUCTURALLY_POPULATED" if mode == "structural" else POPULATED
            assert all(row["outcome"] == first_expected for row in first["samples"])
            assert_replay(initial, first)
        admission = open_simulated(baseline, proc, **options)
        if case == "short-read":
            admission = shorten_read(admission)
        report = observe_window(path, directory, admission, binding, inputs,
                                between=between, after_read=after_read, **mode_options)
    assert_replay(path, report)
    rights = PROCESS_QUERY_INFORMATION | (0 if case == "query-only" else PROCESS_VM_READ)
    if any(access != rights or inherit or selected != pid for access, inherit, selected in access_requests):
        raise AssertionError(f"{case}: unexpected process rights, inheritance or handle target")
    if case in ("title", "no-read-rights", "query-only") and access_requests != [(rights, False, pid)]:
        raise AssertionError(f"{case}: acquisition must make exactly one process-open request")
    return report


@contextmanager
def shorten_read(admission):
    """Exercise short-count propagation after a genuine external read."""
    with admission as reader:
        original = reader.api.ReadProcessMemory

        def fault(handle, address, buffer, count, received):
            result = original(handle, address, buffer, count, received)
            if result and count == 28:
                received._obj.value -= 4
            return result

        reader.api.ReadProcessMemory = fault
        try:
            yield reader
        finally:
            reader.api.ReadProcessMemory = original


def check_journal_refusals(directory):
    lines = (directory / "title.jsonl").read_bytes().splitlines(keepends=True)
    tampered = list(lines)
    changed = json.loads(tampered[0])
    changed["binding"]["marker"]["creation"] += 1
    tampered[0] = encode(changed) + b"\n"
    resealed = tampered[:-1] + [encode({"kind": "seal", "sha256": sha256(b"".join(tampered[:-1])).hexdigest()}) + b"\n"]
    for case, evidence in {"partial": lines[:-1], "invalid-seal": tampered, "resealed-wrong-marker": resealed}.items():
        path = directory / f"journal-{case}.jsonl"
        path.write_bytes(b"".join(evidence))
        try:
            replay(path)
        except (ValueError, ReadFailure):
            continue
        raise AssertionError(f"replay accepted {case}")


@contextmanager
def forbidden_admission():
    raise AssertionError("retail admission was invoked with unqualified inputs")
    yield


def run(directory):
    directory.mkdir(parents=True, exist_ok=False)
    baseline_summary = qualify(directory / "baseline")
    fixture = directory / "baseline" / "build" / FIXTURE.name
    input_refusals = {"unverified-positive": "simulated_inputs_unverified",
                      "unverified-zero": "simulated_inputs_unverified",
                      "contradictory-inputs": "unsupported_native_input_source"}
    cases = [*POSITIVE, *REFUSE, *input_refusals, "short-read"]
    summary = {"build": baseline_summary["build"], "baseline_cases": len(baseline_summary["cases"]), "cases": []}
    for case in cases:
        report = run_case(directory, fixture, case)
        if case in POSITIVE:
            check(POSITIVE[case], report)
        else:
            if any(row["outcome"] != INDETERMINATE for row in report["samples"]):
                raise AssertionError(f"{case} produced a qualified observation")
            if case in REFUSE and report["failure"] != REFUSE[case]:
                raise AssertionError(f"{case} returned {report['failure']!r} instead of {REFUSE[case]}")
            if case in input_refusals and (report["input_admission"]["reason"] != input_refusals[case]
                    or any(row["reason"] != "effective_inputs_unverified" or row["observed_words"] is None
                           for row in report["samples"])):
                raise AssertionError(f"{case} failed to preserve conditional words and input refusal")
            if case == "short-read" and any(row["reason"] != "read_incomplete" for row in report["samples"]):
                raise AssertionError("short byte count did not invalidate both ranges")
        result = {"case": case, "failure": report["failure"],
                  "reasons": [row["reason"] for row in report["samples"]],
                  "received_sha256": digest(directory / f"{case}.jsonl")}
        summary["cases"].append(result)
        print(result, flush=True)
    disk_shape = {"schema": OFFLINE_SCHEMA, "master_sha256": MASTER_SHA256, "pack_commit": PACK_COMMIT,
                  "pack_blobs": PACK_BLOBS, "loose_csv_present": False}
    blocked_profiles = {
        "fixture-as-retail": (SIMULATED_INPUT_EVIDENCE, "offline_inputs_unverified"),
        "disk-without-runtime": (disk_shape, "runtime_effective_inputs_unverified"),
        "disk-master-mismatch": ({**disk_shape, "master_sha256": "0" * 64}, "source_master_mismatch"),
        "disk-unknown-pack": ({**disk_shape, "pack_blobs": {}}, "prediction_source_mismatch"),
        "disk-loose-csv": ({**disk_shape, "loose_csv_present": True}, "unsupported_native_input_source"),
    }
    for case, (inputs, reason) in blocked_profiles.items():
        blocked = directory / f"{case}.jsonl"
        report = observe_window(blocked, directory, forbidden_admission(),
                                {"target_kind": "retail", "marker": {"label": "title"}}, inputs)
        if report["failure"] != reason or any(row["outcome"] != INDETERMINATE for row in report["samples"]):
            raise AssertionError(f"{case} passed despite unsupported retail provenance")
        assert_replay(blocked, report)
    summary["offline_blockers"] = list(blocked_profiles)
    check_journal_refusals(directory)
    (directory / "summary-retail-like.json").write_bytes(encode(summary) + b"\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", help="new evidence directory name under the ignored SRR-013-retail folder")
    args = parser.parse_args()
    if not args.name.isascii() or not args.name.replace("-", "").replace("_", "").isalnum():
        parser.error("evidence directory name must contain letters, digits, hyphens or underscores")
    run(WORK / args.name)
