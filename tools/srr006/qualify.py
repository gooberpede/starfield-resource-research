"""Run the SRR-006 disposable controls from a fresh local evidence directory."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time
import ctypes
from ctypes import wintypes


SCENARIOS = (
    "baseline", "busy", "quiet", "delay", "conflict", "readback",
    "overflow", "write-error", "crash", "emergency", "callback-only", "unreadable", "handoff",
    "foreign-step", "continue-error", "slot-loss", "stop-burst",
    "wait-persistent", "continue-persistent", "emergency-denied", "abrupt-observer",
    "reject-retail-profile", "combined-failure", "cross-window", "unexpected-module",
)
PERSISTENT = ("wait-persistent", "continue-persistent", "combined-failure")


def space():
    # Windows GetDiskFreeSpaceEx caller-available bytes.
    for drive in ("C:\\", "D:\\"):
        free = ctypes.c_ulonglong()
        if not ctypes.windll.kernel32.GetDiskFreeSpaceExW(
            ctypes.c_wchar_p(drive), ctypes.byref(free), None, None
        ) or free.value < 40_000_000_000 + 134_217_728:
            raise RuntimeError(f"projected free space unavailable on {drive}")


def journal(folder):
    raw = (folder / "events.jsonl").read_bytes()
    receipt = json.loads((folder / "receipt.json").read_bytes())
    assert receipt["journal_sha256"] == hashlib.sha256(raw).hexdigest()
    lines = raw.splitlines(keepends=True)
    durable = [json.loads(line) for line in lines[:receipt["flushed"]]]
    assert len(durable) == receipt["flushed"]
    assert all(line.endswith(b"\n") for line in lines[:receipt["flushed"]])
    assert [row["seq"] for row in durable] == list(range(1, len(durable) + 1))
    assert all(row["pid"] == receipt["pid"] for row in durable)
    assert all(row["process_birth"] == receipt["process_birth"] for row in durable)
    prefix, saved = durable_prefix(folder)
    assert saved["sequence"] == receipt["flushed"] and prefix == durable
    return raw, durable, receipt


def durable_prefix(folder):
    saved = json.loads((folder / "durable-prefix.json").read_bytes())
    raw = (folder / "events.jsonl").read_bytes()
    assert 0 < saved["bytes"] <= len(raw)
    assert raw[saved["bytes"] - 1 : saved["bytes"]] == b"\n"
    assert hashlib.sha256(raw[:saved["bytes"]]).hexdigest() == saved["sha256"]
    prefix = [json.loads(line) for line in raw[:saved["bytes"]].splitlines()]
    assert [row["seq"] for row in prefix] == list(range(1, saved["sequence"] + 1))
    identity = {(row["run"], row["pid"], row["process_birth"]) for row in prefix}
    assert len(identity) == 1
    return prefix, saved


class ExactChild:
    """Read-only supervisor witness. Open while alive and retain the handle."""

    def __init__(self, console):
        self.kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        self.kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
        self.kernel.OpenProcess.restype = wintypes.HANDLE
        self.kernel.GetProcessTimes.argtypes = (wintypes.HANDLE,) + (ctypes.POINTER(wintypes.FILETIME),) * 4
        self.kernel.GetExitCodeProcess.argtypes = (wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD))
        self.kernel.WaitForSingleObject.argtypes = (wintypes.HANDLE, wintypes.DWORD)
        self.kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
        line, = (line for line in console.splitlines() if line.startswith(b"EXACT_CHILD "))
        _, pid, birth = line.split()
        self.pid, self.birth = int(pid), int(birth)
        self.handle = self.kernel.OpenProcess(0x101000, False, self.pid)
        if not self.handle:
            raise ctypes.WinError(ctypes.get_last_error())
        times = [wintypes.FILETIME() for _ in range(4)]
        assert self.kernel.GetProcessTimes(self.handle, *(ctypes.byref(value) for value in times))
        assert times[0].dwHighDateTime << 32 | times[0].dwLowDateTime == self.birth
        assert self.kernel.WaitForSingleObject(self.handle, 0) == 258

    def exited(self):
        # Fixture-only safety watchdog. An unsignaled handle is an unresolved
        # recovery, never proof that a scientific observation did not occur.
        assert self.kernel.WaitForSingleObject(self.handle, 10000) == 0
        code = wintypes.DWORD()
        assert self.kernel.GetExitCodeProcess(self.handle, ctypes.byref(code))
        return {"pid": self.pid, "process_birth": self.birth, "exit_code": code.value}

    def close(self):
        self.kernel.CloseHandle(self.handle)


def verify(folder, mode):
    raw, rows, r = journal(folder)
    windows = r["windows"]
    assert [w["index"] for w in windows] == list(range(len(windows))), windows
    for window in windows:
        if window["journal_complete"]:
            assert 0 < window["begin"] < window["end"] <= r["flushed"], window
        if window["invocation"] == "NOT_OBSERVED":
            assert window["invocation_complete"], window
        if window["allocator"] == "NOT_OBSERVED":
            assert window["allocator_complete"], window
        for join in window["first_invocations"] + window["first_allocator_chains"]:
            end = join["allocator"] or join["callback"]
            assert window["begin"] <= end < window["end"] <= r["attempted"], window
            assert join["ingress"] < join["callback"] <= end <= r["flushed"], join
    if mode in PERSISTENT:
        assert r["recovery_unconfirmed"] and r["target_failed"] is None, r
        assert not r["same_handle_signaled"] and not r["exit_event"], r
        if mode == "combined-failure":
            assert r["emergency_error"] == 5 and not r["forced"], r
        else:
            assert r["forced"], r
        assert not r["fixture_complete"] and r["science"] == "INSTRUMENTATION_INCOMPLETE", r
        assert any(row["kind"] == "recovery_unconfirmed" for row in rows)
        if mode == "continue-persistent":
            assert r["events"] == r["continued"] + 1
            assert any(row["kind"] == "emergency_continue" and not row["success"] for row in rows)
        return r
    assert r["exit_event"] and r["same_handle_signaled"], r
    assert r["events"] == r["continued"], r
    if mode in ("baseline", "busy"):
        assert r["fixture_complete"] and not r["target_failed"], r
        assert r["science"] == "OBSERVED_REACHED_ALLOCATOR", r
        assert r["hits"] == [10, 8 * ((512 if mode == "busy" else 16) + 2), 16, 8], r
        assert r["after_stop"] == [1, 0, 0, 0] and r["foreign"] == 1, r
        arm = [row for row in rows if row["kind"] == "arm_readback"]
        assert len(arm) == r["thread_births"] >= 9, r
        assert all(row["verified"] and row["dr7"] & 0xffff20ff == 0x55
                   and len(set(row["dr"])) == 4 for row in arm)
        assert len({row["generation"] for row in arm}) == len(arm)
        assert len({row["thread_birth"] for row in arm}) >= 1
        for event in (row for row in rows if row.get("owner") == "hardware"):
            assert event["resume_flags"] & 0x10100 == 0x10000
            assert event["resume_dr6"] & 0xe00f == 0
            birth = next(row for row in arm if row["generation"] == event["generation"])
            assert birth["tid"] == event["tid"] and birth["seq"] < event["seq"]
            assert birth["dr"][event["site"]] == event["address"] == event["base"] + event["rva"]
        invocations = [row for row in rows if row.get("verdict") == 4]
        arrivals = [row for row in rows if row.get("verdict") == 5]
        assert len(invocations) == 16 and len(arrivals) == 8
        for row in invocations + arrivals:
            entry = rows[row["ingress"] - 1]
            assert entry["generation"] == row["generation"] and entry["verdict"] == 3
            if row.get("verdict") == 5:
                callback = rows[row["callback"] - 1]
                assert callback["generation"] == row["generation"]
                assert callback["ingress"] == row["ingress"] and callback["type"] == 0xba
            else:
                assert row["type"] == (0xba if row["sweep"] else 0)
        assert sum(row.get("owner") == "loader" for row in rows) == 1
        tls = next(row for row in rows if row.get("owner") == "hardware")
        assert tls["generation"] == 1 and tls["site"] == 0
        assert any(row.get("exception") == 0xe1230042 and row["disposition"] == 0x80010001
                   for row in rows)
    elif mode in ("quiet", "delay"):
        assert r["fixture_complete"] and not r["target_failed"], r
        assert r["science"] == "NOT_OBSERVED" and sum(r["hits"]) == 0, r
        assert [w["name"] for w in windows] == ["fixture_startup", "fixture_title", "fixture_menu"]
        assert all(w["invocation_complete"] and w["allocator_complete"] for w in windows), windows
    elif mode in ("conflict", "readback", "emergency", "reject-retail-profile"):
        assert r["forced"] and r["exit_code"] == 0x6006 and r["target_failed"], r
        assert not r["fixture_complete"], r
        if mode != "emergency":
            assert not any(row.get("verified") for row in rows), rows
            assert not sum(r["hits"]), r
        if mode == "reject-retail-profile":
            assert not any(row["kind"] == "arm_attempt" for row in rows)
            assert any(row.get("mapping_failure") == "creation_image_file_identity" for row in rows)
    elif mode == "overflow":
        assert r["first_lost"] == r["accepted"] + 1 and not r["fixture_complete"], r
        assert r["flushed"] == r["accepted"] and not r["target_failed"], r
    elif mode == "write-error":
        assert r["writer_failed"] and r["first_uncommitted"] == r["flushed"] + 1, r
        assert r["flushed"] > 0 and not raw.endswith(b"\n") and not r["fixture_complete"], r
        assert not r["target_failed"], r
    elif mode == "crash":
        assert r["target_failed"] and not r["forced"] and not r["fixture_complete"], r
        assert r["exit_code"] == 0xe1230043, r
        assert any(row.get("exception") == r["exit_code"] and not row["first_chance"]
                   for row in rows)
    elif mode == "callback-only":
        assert r["fixture_complete"] and not r["target_failed"], r
        assert r["science"] == "OBSERVED_INVOKED" and r["hits"] == [10, 136, 8, 0], r
    elif mode == "unreadable":
        assert not r["fixture_complete"] and not r["target_failed"], r
        assert r["science"] == "OBSERVED_INVOKED" and r["hits"] == [1, 1, 1, 0], r
        callback, = [row for row in rows if row.get("verdict") == 4]
        assert callback["type"] is None
        assert any(read["error"] and read["width"] == 1 for read in callback["reads"])
        assert windows[0]["invocation"] == "OBSERVED_INVOKED" and not windows[0]["allocator_complete"]
    elif mode == "handoff":
        assert r["handoff_refused"] and not r["fixture_complete"] and not r["target_failed"], r
        assert r["science"] == "INSTRUMENTATION_INCOMPLETE" and r["hits"] == [1, 0, 0, 0], r
        assert int((folder / "handoff-pid").read_text()) != r["pid"]
    elif mode == "foreign-step":
        assert not r["fixture_complete"] and not r["target_failed"], r
        assert any(row.get("exception") == 0x80000004 and row.get("owner") == "foreign"
                   and row["disposition"] == 0x80010001 for row in rows)
    elif mode == "continue-error":
        assert r["forced"] and r["exit_code"] == 0x6006 and not r["fixture_complete"], r
        assert any(row.get("continue_error") == 31 for row in rows)
    elif mode == "slot-loss":
        assert not r["fixture_complete"] and not r["target_failed"], r
        assert r["science"] == "INSTRUMENTATION_INCOMPLETE" and sum(r["hits"]) == 0, r
        assert any(row.get("fixture_slot_loss") for row in rows)
        assert any(row["kind"] == "stop" and not row["checkpoint"] for row in rows)
    elif mode == "stop-burst":
        assert r["fixture_complete"] and not r["target_failed"], r
        assert r["hits"] == [4106, 0, 0, 0] and r["after_stop"] == [3850, 0, 0, 0], r
        stop, = (row for row in rows if row["kind"] == "stop")
        generations = {row["generation"] for row in rows[stop["seq"]:]
                       if row.get("owner") == "hardware"}
        assert len(generations) >= 9
    elif mode == "emergency-denied":
        assert r["emergency_error"] == 5 and r["emergency_requested"] and not r["forced"], r
        assert not r["fixture_complete"] and not r["target_failed"], r
        assert any(row["kind"] == "exact_child_emergency" and row["winerror"] == 5 for row in rows)
    elif mode == "cross-window":
        assert r["fixture_complete"] and r["hits"] == [1, 1, 1, 1], r
        startup, title, menu = windows
        assert startup["invocation"] == "NOT_OBSERVED"
        callback, = title["first_invocations"]
        allocator, = menu["first_allocator_chains"]
        assert callback["ingress_window"] == allocator["ingress_window"] == 0
        assert callback["callback_window"] == allocator["callback_window"] == 1
        assert callback["callback"] == allocator["callback"]
        assert startup["allocator_requires_through"] == allocator["allocator"]
    elif mode == "unexpected-module":
        assert not r["fixture_complete"] and not r["target_failed"], r
        assert any(row.get("module_name", "").lower() == "version.dll" and
                   not row["module_expected"] and row["module_mapped_image"] for row in rows)
        assert any(row["event_code"] == 7 and row.get("module_name", "").lower() == "version.dll"
                   for row in rows if "event_code" in row)
        assert all(not window["invocation_complete"] for window in windows)
    return r


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binary", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("scenario", choices=SCENARIOS, nargs="*")
    args = parser.parse_args()
    space()
    args.output.mkdir()
    pinned = args.output / "observer.exe"
    digest = hashlib.sha256(args.binary.read_bytes()).hexdigest()
    shutil.copyfile(args.binary, pinned)
    assert hashlib.sha256(pinned.read_bytes()).hexdigest() == digest
    # Neither a target URI nor an attach request is a supported launch mode.
    for mode in ("steam://rungameid/1716740", "--attach"):
        rejected = args.output / "must-not-open"
        assert subprocess.run([pinned.resolve(), mode, rejected.resolve()]).returncode == 2
        assert not rejected.exists()
    for mode in args.scenario or SCENARIOS:
        space()
        folder = args.output / mode
        witness = None
        supervised = mode in PERSISTENT + ("abrupt-observer", "emergency-denied")
        with (args.output / f"{mode}.console.txt").open("xb") as output:
            proc = subprocess.Popen([pinned.resolve(), mode, folder.resolve()],
                                    stdout=output, stderr=subprocess.STDOUT)
            start = time.monotonic()
            quit_sent = False
            while proc.poll() is None:
                elapsed = time.monotonic() - start
                if folder.is_dir():
                    console = (args.output / f"{mode}.console.txt").read_bytes()
                    if supervised and witness is None and b"EXACT_CHILD " in console:
                        witness = ExactChild(console)
                    if witness is not None:
                        space()
                        if mode == "abrupt-observer" and elapsed > 0.25:
                            if not (folder / "phase").exists():
                                (folder / "phase").touch()
                            if b"UNCOMMITTED_TAIL_WRITTEN" in console:
                                assert b"PHASE_DURABLE " in console
                                proc.terminate()  # deliberate disposable observer-loss stimulus
                                proc.wait(timeout=10)
                                break
                        if mode in PERSISTENT and elapsed > 0.3:
                            if not (folder / "fault").exists():
                                (folder / "fault").touch()
                        if mode == "emergency-denied" and elapsed > 0.25:
                            if not (folder / "emergency").exists():
                                (folder / "emergency").touch()
                            rows = (folder / "events.jsonl").read_bytes()
                            if b'"kind":"exact_child_emergency"' in rows and not quit_sent:
                                assert witness.kernel.WaitForSingleObject(witness.handle, 0) == 258
                                (folder / "quit").touch()
                                quit_sent = True
                    if mode in ("quiet", "delay", "slot-loss") or (folder / "ready").is_file():
                        if elapsed > (2.0 if mode == "delay" else 0.25):
                            space()
                            if not (folder / "phase").exists():
                                (folder / "phase").touch()
                            if mode in ("quiet", "delay") and b"PHASE_DURABLE " in console:
                                if not (folder / "menu").exists():
                                    (folder / "menu").touch()
                            menu_ready = mode not in ("quiet", "delay") or b"MENU_DURABLE " in console
                            if (menu_ready and elapsed > (2.8 if mode == "delay" else 0.3)
                                    and not (folder / "stop").exists()):
                                (folder / "stop").touch()
                            if not quit_sent and (b"STOP_DURABLE " in console or
                                                  (folder / "stop").exists() and
                                                  mode in ("overflow", "write-error")):
                                (folder / "quit").touch()
                                quit_sent = True
                    if mode == "emergency" and elapsed > 1:
                        (folder / "emergency").touch()
                    if mode == "crash" and elapsed > 0.4:
                        (folder / "crash-now").touch()
                    if elapsed > 35 and not (folder / "emergency").exists():
                        # A finite fixture has failed to complete its prescribed
                        # scenario. Request exact-child recovery, never kill the
                        # debug pump or use the watchdog as scientific evidence.
                        (folder / "emergency").touch()
                        print(f"{mode} watchdog requested", flush=True)
                if elapsed > 55:
                    raise RuntimeError(f"fixture recovery unconfirmed for observer PID {proc.pid}")
                time.sleep(0.05)
        if supervised:
            assert witness is not None
            try:
                observed_exit = witness.exited()
            finally:
                witness.close()
            space()
            (folder / "supervisor.json").write_text(json.dumps(observed_exit) + "\n", encoding="utf-8")
        if mode == "abrupt-observer":
            assert proc.returncode != 0 and not (folder / "receipt.json").exists()
            prefix, saved = durable_prefix(folder)
            raw = (folder / "events.jsonl").read_bytes()
            assert len(raw) > saved["bytes"] and not raw.endswith(b"\n")
            assert prefix[-1]["kind"] == "operator_phase"
            assert not any(row["kind"] == "stop" for row in prefix)
            assert prefix[-1]["pid"] == observed_exit["pid"] and observed_exit["exit_code"] != 0
            outcome = {"durable_through": saved["sequence"],
                       "unverified_tail_bytes": len(raw) - saved["bytes"], **observed_exit,
                       "science": "INSTRUMENTATION_INCOMPLETE", "receipt_absent": True}
        else:
            expected = 4 if mode in PERSISTENT else 0
            assert proc.returncode == expected, (mode, proc.returncode)
            outcome = verify(folder, mode)
            if supervised:
                assert outcome["pid"] == observed_exit["pid"] and outcome["process_birth"] == observed_exit["process_birth"]
                assert (observed_exit["exit_code"] == 0) == (mode == "emergency-denied"), observed_exit
                if mode == "combined-failure":
                    assert observed_exit["exit_code"] != 0x6006
                outcome["supervisor"] = observed_exit
        print(mode, json.dumps(outcome, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
