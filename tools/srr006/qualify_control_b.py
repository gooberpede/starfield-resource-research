"""Exercise the debugger-only observer against exact disposable children."""

import argparse
from collections import Counter
import ctypes
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

from control_b import PHASES, verify_boundary
from qualify import ExactChild, durable_prefix, space
from qualify_attach import send
from stage_b_marker import publish

CASES = ("quiet", "churn", "competitor", "epoch", "attach-failure", "load-exit",
         "marker-refusal", "seal-fault", "missing-end", "post-end-abnormal")
SURVIVED = "LOAD_SURVIVED_DEBUGGER_ONLY"
FAILED = "LOAD_FAILED_DEBUGGER_ONLY"
INCOMPLETE = "CONTROL_INCOMPLETE"


def exercise(binary, output, case):
    space()
    folder = output / case
    mode = f"admission-control-b-{case if case in ('epoch', 'attach-failure') else 'load'}"
    console_path = output / f"{case}.stdout.txt"
    watcher_path = output / f"{case}.witness.txt"
    with console_path.open("xb") as console, (output / f"{case}.stderr.txt").open("xb") as stderr:
        proc = subprocess.Popen([binary, "--fixture-attach", mode, folder], stdout=console, stderr=stderr)
    witness = watcher = None
    competing = False
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)

    def wait_for(predicate):
        deadline = time.monotonic() + 25
        while time.monotonic() < deadline:
            result = predicate()
            if result:
                return result
            if proc.poll() is not None and not predicate():
                raise AssertionError((case, proc.returncode, console_path.read_text()))
            time.sleep(0.025)
        raise TimeoutError((case, console_path.read_text()))

    def line(label):
        return next((value.decode("ascii").split() for value in console_path.read_bytes().splitlines(True)
                     if value.startswith(label.encode("ascii") + b" ") and value.endswith(b"\n")), None)

    def signal(name):
        (folder / name).touch()

    def ack(label, boundary):
        message = wait_for(lambda: line(label))
        sequence = int(message[1])
        proof = verify_boundary(folder, run, boundary, sequence)
        (output / f"{case}.{boundary}.json").write_text(json.dumps(proof, indent=2) + "\n", encoding="utf-8")
        return sequence, message[2] if len(message) == 3 else None

    def phase(index, prior, label, boundary):
        publish(folder, run, PHASES[index], *prior)
        result = ack(label, boundary)
        assert result[0] > prior[0] and result[1] != prior[1]
        return result

    try:
        witness = ExactChild(" ".join(wait_for(lambda: line("EXACT_CHILD"))).encode("ascii"))
        run = f"{hashlib.sha256(binary.read_bytes()).hexdigest()}-{witness.pid}-{witness.birth}"
        wait_for(lambda: (folder / "attach-ready").exists())
        with watcher_path.open("xb") as stream:
            watcher = subprocess.Popen([sys.executable, "-E", "-B",
                Path(__file__).resolve().parents[1] / "srr008" / "watch_exit.py", run, binary, folder],
                stdout=stream, stderr=subprocess.STDOUT)
        wait_for(lambda: (folder / "exit-witness-bound.json").exists())
        if case == "competitor":
            assert kernel.DebugActiveProcess(witness.pid), ctypes.WinError(ctypes.get_last_error())
            competing = True
            assert kernel.DebugSetProcessKillOnExit(False), ctypes.WinError(ctypes.get_last_error())
        send(folder, run, "title", 1, "TITLE_CONFIRMED")
        if case in ("competitor", "epoch", "attach-failure"):
            assert proc.wait(25) == 4
            if competing:
                assert kernel.DebugActiveProcessStop(witness.pid), ctypes.WinError(ctypes.get_last_error())
                competing = False
            signal("advance")
            signal("quit")
        else:
            ready = ack("DEBUGGER_ONLY_READY", "ready")
            signal("advance")
            wait_for(lambda: (folder / "ready").exists())
            if case == "marker-refusal":
                publish(folder, run, "LOAD_BEGIN", *ready)
                wait_for(lambda: line("PHASE_REFUSED"))
                publish(folder, f"{run}-1", PHASES[0], *ready)
                wait_for(lambda: console_path.read_bytes().count(b"PHASE_REFUSED ") == 2)
            menu = phase(0, ready, "CONTROL_MENU_DURABLE", "menu")
            if case == "marker-refusal":
                publish(folder, run, PHASES[1], ready[0], menu[1])
                wait_for(lambda: console_path.read_bytes().count(b"PHASE_REFUSED ") == 3)
                send(folder, run, "stop", 3, "STOP")
                signal("quit")
            else:
                loading = phase(1, menu, "CONTROL_LOAD_BEGIN_DURABLE", "load")
                if case == "load-exit":
                    signal("abrupt-load")
                if case == "churn":
                    signal("churn-load")
                signal("simulate-load")
                if case != "load-exit":
                    wait_for(lambda: (folder / "load-complete").exists())
                    settled = phase(2, loading, "SETTLED_GAMEPLAY_DURABLE", "settled")
                    if case == "seal-fault":
                        (folder / "operational-end-prefix.json.partial").mkdir()
                        publish(folder, run, PHASES[3], *settled)
                        wait_for(lambda: b"CONTROL_BOUNDARY_UNCONFIRMED" in console_path.read_bytes())
                    elif case != "missing-end":
                        phase(3, settled, "CONTROL_END_DURABLE", "end")
                    if case == "post-end-abnormal":
                        signal("abnormal-quit")
                    signal("quit")
            assert proc.wait(25) == 0
        independent = witness.exited()
        assert watcher.wait(25) == 0, watcher_path.read_text()
        bound = json.loads((folder / "exit-witness-bound.json").read_bytes())
        exit_record = json.loads((folder / "exit-witness-result.json").read_bytes())
        assert bound["run"] == exit_record["run"] == run
        assert int(bound["target"]["pid"]) == independent["pid"]
        assert exit_record["signaled"] and all(exit_record[k] == v for k, v in independent.items())
        rows, prefix = durable_prefix(folder)
        raw = (folder / "events.jsonl").read_bytes()
        receipt = json.loads((folder / "control-receipt.json").read_bytes())
        assert receipt["run"] == run and receipt["durable_sequence"] == prefix["sequence"]
        assert receipt["journal_sha256"] == hashlib.sha256(raw).hexdigest()
        assert not any(x in raw for x in (b'"windows"', b'OBSERVED_', b'NOT_OBSERVED', b'ATTACH_ARMED'))
        assert not {"science", "windows", "hits"}.intersection(receipt)
        assert [receipt[k] for k in ("research_context_writes", "blocked_research_context_writes",
                                     "research_hardware_hits")] == [0, 0, 0]
        forbidden = {"arm_attempt", "arm_readback", "periodic_readback", "stop", "recovery_outcome"}
        assert not forbidden.intersection(r["kind"] for r in rows)
        events = [r for r in rows if r["kind"] == "event"]
        expected = SURVIVED if case in ("quiet", "churn") else FAILED if case == "load-exit" else INCOMPLETE
        assert receipt["result"] == expected, receipt
        if case in ("competitor", "epoch", "attach-failure"):
            refusal, = [row for row in rows if row["kind"] == "attach_refused"]
            assert not events and not line("DEBUGGER_ONLY_READY")
            if case == "competitor":
                assert refusal["predicate"] == "target_already_debugged" and not refusal["attach_attempted"]
            if case == "epoch":
                assert "epoch" in refusal["predicate"] and not refusal["attach_attempted"]
            if case == "attach-failure":
                assert refusal["operation"] == "DebugActiveProcess" and refusal["winerror"] not in (0, 1460)
                assert refusal["attach_attempted"]
        else:
            assert receipt["native_exit_event"] and receipt["native_exit_code"] == independent["exit_code"]
            assert receipt["handle_exit_code"] == independent["exit_code"]
            if case != "seal-fault":
                assert receipt["native_event_service_complete"] and len(events) == receipt["continued_events"]
                assert all(row["continued"] for row in events)
            loader, = [row for row in events if row.get("owner") == "loader"]
            assert loader["continued"]
        if case in ("quiet", "churn", "missing-end", "post-end-abnormal", "seal-fault"):
            exceptions = [r for r in events if r.get("owner") == "foreign"]
            assert {r["exception"] for r in exceptions} == {0x80000004, 0x80000003}
            assert all(r["continued"] and r["disposition"] == 0x80010001 for r in exceptions)
        if case == "churn":
            load_events = Counter(r["event_code"] for r in events if r["phase"] == 3)
            assert all(load_events[code] >= 4 for code in (2, 4, 6, 7)), load_events
        if case == "load-exit":
            assert independent["exit_code"] == 0x80000004
            assert not any(r.get("exception") == 0x80000004 for r in events)
        if case == "seal-fault":
            assert receipt["writer_failed"] and not receipt["operational_end_sealed"]
            assert not line("CONTROL_END_DURABLE") and rows[-1]["kind"] == "control_end"
        if case == "marker-refusal":
            assert sum(r["kind"] == "phase_request_refused" for r in rows) == 3
            assert not line("CONTROL_LOAD_BEGIN_DURABLE") and not (folder / "stop-prefix.json").exists()
        if case == "post-end-abnormal":
            assert receipt["operational_end_sealed"] and receipt["native_exit_code"] == 110
        return dict(case=case, result=expected, durable_sequence=prefix["sequence"],
                    event_count=len(events), exit_code=independent["exit_code"])
    finally:
        if competing:
            kernel.DebugActiveProcessStop(witness.pid)
        if folder.is_dir():
            signal("advance")
            signal("quit")
        if witness:
            witness.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binary", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("cases", nargs="*", choices=CASES)
    args = parser.parse_args()
    binary = args.binary.resolve(strict=True)
    args.output.mkdir()
    for case in args.cases or CASES:
        print(json.dumps(exercise(binary, args.output, case)), flush=True)


if __name__ == "__main__":
    main()
