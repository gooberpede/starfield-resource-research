"""Exercise Stage A's stopped admission and marker protocol on exact children."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time

from qualify import ExactChild, journal, space
from qualify_attach import ack, send


def exercise(binary, output, mode):
    space()
    folder = output / mode
    digest = hashlib.sha256(binary.read_bytes()).hexdigest()
    with (output / f"{mode}.console.txt").open("x+b") as console:
        proc = subprocess.Popen([binary, "--fixture-attach", mode, folder],
                                stdout=console, stderr=subprocess.STDOUT)
        witness = None

        def wait(predicate):
            until = time.monotonic() + 15
            while time.monotonic() < until:
                status = Path(console.name).read_bytes()
                value = predicate(status)
                if value:
                    return value
                if proc.poll() is not None:
                    raise AssertionError((mode, proc.returncode, status))
                time.sleep(0.025)
            raise AssertionError((mode, status))

        try:
            witness = ExactChild(wait(lambda s: s if b"EXACT_CHILD " in s and s.endswith(b"\n") else None))
            run = f"{digest}-{witness.pid}-{witness.birth}"
            wrong = f"{digest}-{witness.pid}-{witness.birth + 1}"
            send(folder, wrong, "title", 1, "TITLE_CONFIRMED")
            time.sleep(0.65)
            assert b'"kind":"title_confirmed"' not in (folder / "events.jsonl").read_bytes()
            send(folder, run, "title", 1, "TITLE_CONFIRMED")
            if mode == "admission-overlay-lookalike":
                # A same-named overlay outside the pinned origin is classified
                # incompatible at its (replayed) load event: arming must be
                # refused and no slot writes may occur. In retail the same
                # classification refuses during the pre-attach census.
                wait(lambda s: b"ARMING_REFUSED" in s.splitlines())
            if mode == "admission-competitor":
                wait(lambda s: b"COMPETING_BREAKPOINT_GO" in s)
                _, rows = read_rows(folder)
                title = next(row["seq"] for row in rows if row["kind"] == "title_confirmed")
                send(folder, run, "menu", 2, "MAIN_MENU_CONFIRMED", title)
                time.sleep(0.25)
                assert b"MENU_DURABLE" not in Path(console.name).read_bytes()
                space()
                (folder / "compete").touch()
            if mode == "admission-critical":
                wait(lambda s: b"ARMING_REFUSED" in s.splitlines())
            else:
                outcome = wait(lambda s: ack(s, b"ATTACH_ARMED") or
                               (mode in ("admission-slot-replaced", "admission-overlay-lookalike") and
                                b"ARMING_REFUSED" in s.splitlines() and "R"))
                barrier = 0 if outcome == "R" else outcome
                if barrier:
                    assert b'"kind":"attach_barrier"' in (folder / "events.jsonl").read_bytes()
            if mode == "admission-quiet":
                time.sleep(2.4)
                assert witness.kernel.WaitForSingleObject(witness.handle, 0) == 258
            space()
            (folder / "advance").touch()
            wait(lambda _: (folder / "ready").exists())
            if mode in ("admission-fixture", "admission-competitor", "admission-quiet",
                        "admission-overlay-drift", "admission-drift-arrival"):
                send(folder, run, "menu", 2, "MAIN_MENU_CONFIRMED", barrier)
                wait(lambda s: ack(s, b"MENU_DURABLE"))
            if mode == "admission-drift-arrival":
                (folder / "menu-done").touch()
                wait(lambda _: (folder / "arrived").exists())
                time.sleep(0.4)
            send(folder, run, "stop", 3, "STOP")
            stop = wait(lambda s: ack(s, b"STOP_DURABLE"))
            seal = json.loads((folder / "stop-prefix.json").read_bytes())
            assert seal["sequence"] == stop
            raw, rows = read_rows(folder, seal["bytes"])
            assert hashlib.sha256(raw).hexdigest() == seal["sha256"] and rows[-1]["kind"] == "stop"
            assert all(row["pid"] == witness.pid and row["process_birth"] == witness.birth for row in rows)
            send(folder, run, "retire", 4, "QUIT_REQUESTED", stop)
            wait(lambda s: ack(s, b"RETIRE_DURABLE"))
            space()
            (folder / "quit").touch()
            assert proc.wait(timeout=15) == 0
            _, rows, receipt = journal(folder)
            assert witness.kernel.WaitForSingleObject(witness.handle, 0) == 0
            assert receipt["same_handle_signaled"] and receipt["exit_code"] == 0 and not receipt["forced"]
            admission = next(row for row in rows if row["kind"] == "stopped_admission")
            assert not any(r["kind"] == "arm_attempt" and r["seq"] < admission["seq"] for r in rows)
            if mode == "admission-critical":
                assert not admission["prearm_checks"] and not any(r["kind"] == "arm_attempt" for r in rows)
                assert receipt["science"] == "INSTRUMENTATION_INCOMPLETE"
            elif mode == "admission-fixture":
                target_access, = (r for r in rows if r["kind"] == "fixture_target_access")
                assert target_access["requested_process_access"] == 0x100410
                assert target_access["seq"] < admission["seq"]
                assert admission["prearm_checks"]
                assert any(r.get("module_name") == "optional-fixture.dll" and r.get("module_risk") == "unknown"
                           and r["event_code"] == 6 for r in rows)
                assert any(r.get("module_name") == "optional-fixture.dll" and r["event_code"] == 7 for r in rows)
                assert receipt["science"] == "OBSERVED_REACHED_ALLOCATOR"
                assert receipt["windows"][0]["invocation"] == "INSTRUMENTATION_INCOMPLETE"
                assert receipt["windows"][1]["allocator"] == "OBSERVED_REACHED_ALLOCATOR"
            elif mode == "admission-competitor":
                refused = next(r for r in rows if r.get("attach_candidate_refused"))
                owned = next(r for r in rows if r.get("owner") == "loader")
                assert refused["tid"] != owned["tid"] and refused["seq"] < admission["seq"] < owned["seq"]
                assert (folder / "competitor-handled").exists() and admission["prearm_checks"]
                assert receipt["science"] == "OBSERVED_REACHED_ALLOCATOR"
            elif mode == "admission-slot-replaced":
                assert admission["prearm_checks"] and any(
                    r["kind"] == "periodic_readback" and not r["checkpoint"] for r in rows)
                assert receipt["science"] == "INSTRUMENTATION_INCOMPLETE"
            elif mode == "admission-continue":
                assert admission["prearm_checks"] and any(
                    r["kind"] == "recovery_continue" and r["success"] for r in rows)
                assert receipt["science"] == "OBSERVED_INVOKED"
                assert receipt["windows"][1]["allocator"] == "INSTRUMENTATION_INCOMPLETE"
            elif mode == "admission-overlay-drift":
                # Pre-session drift of an origin-verified overlay is recorded
                # with both identities and must not degrade the science.
                assert admission["prearm_checks"]
                drift = next(r for r in rows if r["kind"] == "steam_component_drift")
                assert drift["component"] == "gameoverlayrenderer64.dll"
                assert drift["srr008_sha256"] == (
                    "688cc70e58cd8d1f31345fdf93ba1b9ab08c77c38df847bd2b0ae2145a437a2f")
                assert drift["observed_sha256"] != drift["srr008_sha256"]
                assert receipt["science"] == "OBSERVED_REACHED_ALLOCATOR"
                assert receipt["observer_healthy"] and receipt["stop_durable"]
                assert receipt["windows"][1]["allocator"] == "OBSERVED_REACHED_ALLOCATOR"
                assert receipt["windows"][1]["allocator_complete"]
            elif mode == "admission-drift-arrival":
                # The same updated overlay arriving mid-observation is a real
                # module transition: the earlier durable positive survives and
                # the affected window is qualified, not silently accepted.
                assert admission["prearm_checks"]
                drift = next(r for r in rows if r["kind"] == "steam_component_drift")
                assert drift["component"] == "gameoverlayrenderer64.dll"
                module = next(r for r in rows if r.get("module_name") == "gameoverlayrenderer64.dll")
                assert module["module_risk"] == "drifting" and module["module_drift"]
                assert receipt["science"] == "OBSERVED_REACHED_ALLOCATOR"
                assert receipt["windows"][1]["allocator"] == "OBSERVED_REACHED_ALLOCATOR"
                assert receipt["windows"][1]["allocator_complete"]
                assert not receipt["windows"][2]["allocator_complete"]
                assert receipt["observer_healthy"] and receipt["stop_durable"]
            elif mode == "admission-overlay-lookalike":
                assert any(r["kind"] == "attach_barrier" for r in rows)
                lookalike = next(r for r in rows if r.get("module_name") == "gameoverlayrenderer64.dll")
                assert lookalike["module_risk"] == "incompatible"
                assert not any(r["kind"] == "steam_component_drift" for r in rows)
                assert not admission["prearm_checks"]
                assert not any(r["kind"] == "arm_attempt" for r in rows)
                assert receipt["science"] == "INSTRUMENTATION_INCOMPLETE"
                assert not receipt["observer_healthy"] and receipt["stop_durable"]
            else:
                assert admission["prearm_checks"] and receipt["science"] == "NOT_OBSERVED"
            return receipt["science"]
        finally:
            if proc.poll() is None:
                # Ask only this fixture child to exit and let its observer drain.
                if witness is not None:
                    space()
                    send(folder, run, "title", 1, "TITLE_CONFIRMED")
                    (folder / "compete").touch()
                    (folder / "advance").touch()
                    (folder / "quit").touch()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print(f"fixture recovery unconfirmed for observer {proc.pid}", flush=True)
            if witness is not None:
                witness.close()


def read_rows(folder, size=None):
    with (folder / "events.jsonl").open("rb") as stream:
        raw = stream.read() if size is None else stream.read(size)
    complete = raw[:raw.rfind(b"\n") + 1]
    return complete, list(map(json.loads, complete.splitlines()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binary", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    space()
    output = args.output.resolve()
    output.mkdir()
    binary = args.binary.resolve()
    wrong = output / "must-not-exist"
    for command in (["--stage-a", "123", wrong], ["--stage-a", wrong],
                    ["--fixture-attach", "123", wrong]):
        assert subprocess.run([binary, *command]).returncode == 2 and not wrong.exists()
    for mode in ("admission-fixture", "admission-critical", "admission-competitor",
                 "admission-slot-replaced", "admission-quiet", "admission-continue",
                 "admission-overlay-drift", "admission-drift-arrival",
                 "admission-overlay-lookalike"):
        print(mode, exercise(binary, output, mode), flush=True)


if __name__ == "__main__":
    main()
