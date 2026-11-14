"""Qualify the integrated late-attach entry point using only its disposable child."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time

from qualify import ExactChild, durable_prefix, journal, space


SCENARIOS = (
    "baseline", "busy", "crash", "unexpected-module", "unreadable", "slot-loss",
    "overflow", "write-error", "reject-retail-profile", "handoff", "emergency",
    "emergency-denied", "conflict", "readback", "anomalous-return",
    "competing-breakpoint", "recover-detach", "recover-refusal", "recover-wait", "recover-continue",
    "recover-partial", "recover-detach-error",
)


def send(folder, run, name, ordinal, label, prior=0):
    space()
    path = folder / f"{name}.request"
    temporary = path.with_suffix(".writing")
    temporary.write_bytes(f"{run} {ordinal} {label} {prior}\n".encode("ascii"))
    temporary.replace(path)


def ack(status, label):
    return next((int(line.split()[1]) for line in status.splitlines(keepends=True)
                 if line.startswith(label + b" ") and line.endswith(b"\n")), 0)


def exercise(binary, output, mode):
    space()
    folder = output / mode
    transcript = output / f"{mode}.console.txt"
    witness = None
    sent = set()
    notifications = {}
    with transcript.open("xb") as console:
        proc = subprocess.Popen([binary, "--fixture-attach", mode, folder], stdout=console,
                                stderr=subprocess.STDOUT)
        start = time.monotonic()
        try:
            while proc.poll() is None:
                status = transcript.read_bytes()
                if witness is None and b"EXACT_CHILD " in status and status.endswith(b"\n"):
                    witness = ExactChild(status)
                    digest = hashlib.sha256(binary.read_bytes()).hexdigest()
                    run = f"{digest}-{witness.pid}-{witness.birth}"
                if witness is not None:
                    def submit(name, ordinal, label, prior=0):
                        if name not in sent:
                            send(folder, run, name, ordinal, label, prior)
                            sent.add(name)

                    title = ack(status, b"PHASE_DURABLE")
                    stop = ack(status, b"STOP_DURABLE")
                    if b"COMPETING_BREAKPOINT_GO" in status and "compete" not in sent:
                        (folder / "compete").touch()
                        sent.add("compete")
                    if b"ATTACH_ARMED" in status and "bad-title" not in sent:
                        # Wrong epoch and old unbound markers cannot advance the state.
                        send(folder, f"{digest}-{witness.pid}-{witness.birth + 1}", "title", 1, "TITLE_CARD")
                        send(folder, run, "menu", 2, "MAIN_MENU")
                        send(folder, run, "retire", 4, "RETIRE")
                        (folder / "phase").touch()
                        notifications["bad_title_at"] = time.monotonic()
                        sent.add("bad-title")
                    if "bad-title" in sent and time.monotonic() - notifications["bad_title_at"] > 0.4:
                        if "title" not in sent:
                            assert b"PHASE_DURABLE" not in status
                        submit("title", 1, "TITLE_CARD")
                    if title and "advance" not in sent:
                        assert not ack(status, b"MENU_DURABLE")
                        space()
                        (folder / "advance").touch()
                        sent.add("advance")
                    if title and (folder / "ready").exists():
                        submit("menu", 2, "MAIN_MENU", title)
                    if ack(status, b"MENU_DURABLE"):
                        submit("stop", 3, "STOP")
                    if stop:
                        submit("retire", 4, "RETIRE", stop)
                    if ack(status, b"RETIRE_DURABLE") and mode.startswith("recover-"):
                        submit("emergency", 5, "EMERGENCY")
                        submit("recover", 6, "RECOVER", stop)
                    recovery_ready = not mode.startswith("recover-") or b"RECOVERY_RESULT " in status
                    if ack(status, b"RETIRE_DURABLE") and "quit" not in sent and recovery_ready:
                        if mode == "crash":
                            prefix, watermark = durable_prefix(folder)
                            assert prefix[-1]["kind"] == "retire"
                            assert any(row.get("verdict") == 5 for row in prefix)
                            notifications["pre_crash_prefix"] = prefix
                            notifications["pre_crash_hash"] = watermark["sha256"]
                        space()
                        (folder / ("crash-now" if mode == "crash" else "quit")).touch()
                        sent.add("quit")
                    if mode in ("overflow", "write-error") and (folder / "ready").exists():
                        # The broken journal must never acknowledge STOP or retirement.
                        submit("stop", 3, "STOP")
                        if "quit" not in sent:
                            assert b"STOP_DURABLE" not in status and b"RETIRE_DURABLE" not in status
                            space()
                            (folder / "quit").touch()
                            sent.add("quit")
                    if mode in ("emergency", "emergency-denied") and "advance" in sent:
                        submit("emergency", 5, "EMERGENCY")
                        if mode == "emergency-denied" and "quit" not in sent and (
                            b'"kind":"exact_child_emergency"' in (folder / "events.jsonl").read_bytes()
                        ):
                            assert witness.kernel.WaitForSingleObject(witness.handle, 0) == 258
                            space()
                            (folder / "quit").touch()
                            sent.add("quit")
                    if time.monotonic() - start > 30:
                        submit("emergency", 5, "EMERGENCY")
                if time.monotonic() - start > 45:
                    raise RuntimeError(f"disposable observer {proc.pid} did not exit")
                time.sleep(0.025)
            assert proc.returncode == 0, (mode, transcript.read_text())
            raw, rows, receipt = journal(folder)
            assert receipt["method"] == "late_attach" and not receipt["fixture_complete"]
            assert receipt["same_handle_signaled"]
            assert bool(receipt["exit_event"]) != bool(receipt["detached"])
            assert rows[0]["kind"] == "startup" and not rows[0]["covered"]
            assert rows[0]["pid"] == receipt["pid"]
            if witness is not None:
                assert witness.exited()["exit_code"] == receipt["exit_code"]
            assert receipt["science"] != "NOT_OBSERVED"
            assert not any(row.get("verdict") in (4, 5) and row["stopped"] for row in rows)
            if mode.startswith("recover-"):
                assert receipt["non_killing"] and not receipt["forced"] and not receipt["target_failed"]
                assert receipt["stop_durable"] and receipt["science"] == "OBSERVED_REACHED_ALLOCATOR"
                assert any(row["kind"] == "termination_refused" for row in rows)
                outcome, = (row for row in rows if row["kind"] == "recovery_outcome")
                assert outcome["suspensions_released"]
                restores = [row for row in rows if row["kind"] == "restore_debug_state"]
                post_continue = [row for row in rows if row["kind"] == "post_continue_debug_state"]
                if mode in ("recover-refusal", "recover-partial", "recover-detach-error"):
                    assert not outcome["detached"] and receipt["recovery_unconfirmed"]
                    if mode == "recover-refusal":
                        assert not restores and not outcome["detach_attempted"]
                    if mode == "recover-partial":
                        assert {row["verified"] for row in restores} == {0, 1}
                        assert not outcome["detach_attempted"]
                    if mode == "recover-detach-error":
                        assert outcome["detach_attempted"] and outcome["detach_error"] == 5
                        assert post_continue and all(row["verified"] for row in restores + post_continue)
                else:
                    assert outcome["detached"] and not receipt["recovery_unconfirmed"]
                    assert len(restores) >= 2 and len(restores) == len(post_continue)
                    assert all(row["verified"] for row in restores + post_continue)
                if mode == "recover-wait":
                    assert any(row["kind"] == "pump_failure" for row in rows)
                if mode == "recover-continue":
                    assert any(row["kind"] == "recovery_continue" and row["success"] for row in rows)
            if mode in ("reject-retail-profile", "conflict", "readback"):
                assert receipt["forced"] and not any(row["kind"] == "attach_barrier" for row in rows)
                if mode == "reject-retail-profile":
                    assert not any(row["kind"] == "arm_attempt" for row in rows)
                    assert any(row.get("mapping_failure") == "creation_image_file_identity" for row in rows)
                return receipt
            barrier, = (row for row in rows if row["kind"] == "attach_barrier")
            assert barrier["continued"] and receipt["windows"][0]["begin"] == barrier["seq"]
            creation, = (row for row in rows if row.get("event_code") == 3)
            assert creation["creation_start_address"] == 0
            assert creation["base"] != 0x140000000
            arms = [row for row in rows if row["kind"] == "arm_readback"]
            assert len({row["generation"] for row in arms if row["seq"] < barrier["seq"]}) >= 2
            assert all(row["dr7"] & 0xffff20ff == 0x55 and len(set(row["dr"])) == 4 for row in arms)
            assert not any("verdict" in row and row["seq"] < barrier["seq"] for row in rows)
            if mode == "competing-breakpoint":
                refused, = (row for row in rows if row.get("attach_candidate_refused"))
                owned, = (row for row in rows if row.get("owner") == "loader")
                assert refused["address"] == owned["address"] and refused["tid"] != owned["tid"]
                assert refused["seq"] < owned["seq"] < barrier["seq"]
                assert refused["disposition"] == 0x80010001 and owned["disposition"] == 0x10002
                assert (folder / "competitor-handled").exists() and not receipt["target_failed"]
                assert receipt["science"] == "OBSERVED_REACHED_ALLOCATOR"
            if mode in ("baseline", "busy", "crash", "unexpected-module", "unreadable",
                        "slot-loss", "anomalous-return"):
                order = ("operator_phase", "operator_menu", "stop", "retire", "retire_outcome")
                phase, menu, stop, retire, outcome = [
                    next(row for row in rows if row["kind"] == kind) for kind in order
                ]
                assert barrier["seq"] < phase["seq"] < menu["seq"] < stop["seq"] < retire["seq"] < outcome["seq"]
                assert retire["seq"] <= receipt["flushed"] and receipt["stop_durable"]
                sealed = json.loads((folder / "stop-prefix.json").read_bytes())
                assert sealed["sequence"] == stop["seq"]
                stop_bytes = b"".join(raw.splitlines(keepends=True)[:stop["seq"]])
                assert len(stop_bytes) == sealed["bytes"]
                assert hashlib.sha256(stop_bytes).hexdigest() == sealed["sha256"]
                assert phase["qpc"] - barrier["qpc"] >= phase["qpc_frequency"] * 0.4
                if mode in ("baseline", "busy", "crash"):
                    assert receipt["science"] == "OBSERVED_REACHED_ALLOCATOR"
                    assert all(window["allocator_complete"] for window in receipt["windows"])
                    observed = [row for row in rows if row.get("verdict") == 5]
                    assert all(rows[row["ingress"] - 1]["generation"] == row["generation"] and
                               rows[row["callback"] - 1]["generation"] == row["generation"]
                               for row in observed)
                    assert observed and all(row["seq"] < stop["seq"] for row in observed)
                    if mode != "crash":
                        assert receipt["hits"] == [10, (4112 if mode == "busy" else 144), 16, 8]
                        assert all(any(row["seq"] < hit["seq"] and row["generation"] == hit["generation"]
                                       for row in arms) for hit in rows if hit.get("owner") == "hardware")
                assert bool(outcome["clean"]) == (mode != "crash")
                if mode == "crash":
                    assert receipt["target_failed"] and not receipt["forced"] and receipt["exit_code"] == 0xe1230043
                    prefix = notifications["pre_crash_prefix"]
                    assert rows[:len(prefix)] == prefix
                    raw_prefix = b"".join(raw.splitlines(keepends=True)[:len(prefix)])
                    assert hashlib.sha256(raw_prefix).hexdigest() == notifications["pre_crash_hash"]
                if mode == "unexpected-module":
                    assert all(window["invocation_complete"] for window in receipt["windows"][:1])
                    assert not receipt["windows"][1]["invocation_complete"]
                    assert {row["event_code"] for row in rows if row.get("module_name") == "version.dll"} == {6, 7}
                    unload, = (row for row in rows if row.get("module_name") == "version.dll"
                               and row["event_code"] == 7)
                    assert any(row.get("verdict") == 5 and row["seq"] > unload["seq"] for row in rows)
                    assert receipt["windows"][2]["allocator_complete"]
                if mode == "unreadable":
                    assert receipt["science"] == "OBSERVED_INVOKED" and not receipt["target_failed"]
                    assert not receipt["windows"][1]["allocator_complete"]
                if mode == "slot-loss":
                    assert not stop["checkpoint"] and receipt["science"] == "INSTRUMENTATION_INCOMPLETE"
                if mode == "anomalous-return":
                    anomaly, = (row for row in rows if row.get("site") == 2 and row.get("verdict") == 1)
                    assert receipt["science"] == "OBSERVED_REACHED_ALLOCATOR"
                    assert any(row.get("verdict") == 5 and row["seq"] > anomaly["seq"] for row in rows)
                    assert not receipt["forced"] and not receipt["target_failed"]
            if mode == "handoff":
                assert receipt["handoff_refused"] and not receipt["target_failed"]
            if mode == "overflow":
                assert receipt["first_lost"] and not receipt["stop_durable"] and not receipt["target_failed"]
            if mode == "write-error":
                assert receipt["writer_failed"] and not raw.endswith(b"\n") and not receipt["stop_durable"]
            if mode == "emergency":
                assert receipt["forced"] and receipt["exit_code"] == 0x6006
            if mode == "emergency-denied":
                assert receipt["emergency_error"] == 5 and not receipt["forced"] and not receipt["target_failed"]
            return receipt
        finally:
            if witness is not None:
                witness.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binary", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("scenario", choices=SCENARIOS, nargs="*")
    args = parser.parse_args()
    space()
    output = args.output.resolve()
    output.mkdir()
    binary = output / "observer.exe"
    shutil.copyfile(args.binary, binary)
    assert hashlib.sha256(binary.read_bytes()).digest() == hashlib.sha256(args.binary.read_bytes()).digest()
    for command in (["--retail-attach", "123", output / "refused"],
                 ["--fixture-attach", "123", output / "refused"],
                 ["steam://rungameid/1716740", output / "refused"]):
        assert subprocess.run([binary, *command]).returncode == 2
        assert not (output / "refused").exists()
    for mode in args.scenario or SCENARIOS:
        receipt = exercise(binary, output, mode)
        print(mode, receipt["science"], receipt["accepted"], receipt["flushed"], flush=True)


if __name__ == "__main__":
    main()
