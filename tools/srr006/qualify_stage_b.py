"""Qualify Stage B with exact disposable children and retain raw evidence."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

from qualify import ExactChild, durable_prefix, journal, space
from qualify_attach import ack, send
from stage_b_marker import publish
from verify_stage_b_stop import verify_stop


CASES = ("title-stop", "menu-stop", "load-stop", "quiet", "load-busy", "load-slot-loss",
         "preload-gap", "lodge", "lodge-stop", "cross-gap-crash", "chain-before-stop", "seal-fault")
NEGATIVE = "NOT_OBSERVED"
INCOMPLETE = "INSTRUMENTATION_INCOMPLETE"


def exercise(binary, output, case):
    space()
    folder = output / case
    cross = case in ("cross-gap-crash", "seal-fault")
    mode = "admission-stage-b-cross" if cross else "admission-stage-b-quiet"
    with (output / f"{case}.console.txt").open("xb") as console:
        proc = subprocess.Popen([binary, "--fixture-attach", mode, folder],
                                stdout=console, stderr=subprocess.STDOUT)
        witness = None
        exit_watch = None

        def wait(predicate):
            # Only the fixture supervisor has a watchdog. The busy case
            # can have two thousand rows ahead of a durable phase marker.
            deadline = time.monotonic() + (45 if case == "load-busy" else 18)
            while time.monotonic() < deadline:
                status = Path(console.name).read_bytes()
                value = predicate(status)
                if value:
                    return value
                assert proc.poll() is None, (case, proc.returncode, status)
                time.sleep(0.025)
            raise AssertionError((case, status))

        def signal(name):
            space()
            (folder / name).touch()

        def ready(name):
            wait(lambda _: (folder / name).is_file())

        def binding(label):
            prefix = (label + " ").encode("ascii")
            line = wait(lambda s: next((v for v in s.splitlines(keepends=True)
                                        if v.startswith(prefix) and v.endswith(b"\n")), None))
            _, sequence, challenge = line.decode("ascii").split()
            assert len(challenge) == 32
            return int(sequence), challenge

        def phase(label, predecessor, response):
            publish(folder, run, label, *predecessor)
            result = binding(response)
            assert result[0] > predecessor[0] and result[1] != predecessor[1]
            return result

        refusals = 0

        def refuse(label, predecessor, token=None):
            nonlocal refusals
            publish(folder, token or run, label, *predecessor)
            refusals += 1
            wait(lambda s: s.count(b"PHASE_REFUSED ") == refusals)

        try:
            witness = ExactChild(wait(lambda s: s if b"EXACT_CHILD " in s and s.endswith(b"\n") else None))
            binary_digest = hashlib.sha256(binary.read_bytes()).hexdigest()
            run = f"{binary_digest}-{witness.pid}-{witness.birth}"
            if case == "quiet":
                publish(folder, run, "MAIN_MENU_CONFIRMED", 23, "0" * 32)
                refusals += 1
            send(folder, run, "title", 1, "TITLE_CONFIRMED")
            arm = binding("ATTACH_ARMED")
            if case == "quiet":
                wait(lambda s: s.count(b"PHASE_REFUSED ") == refusals)
                assert not ack(Path(console.name).read_bytes(), b"MENU_DURABLE")
                refuse("LOAD_BEGIN", arm)
                refuse("MAIN_MENU_CONFIRMED", arm, f"{binary_digest}-{witness.pid}-{witness.birth + 1}")
            if case == "preload-gap":
                signal("preload-gap-fixture")
            if case == "chain-before-stop":
                signal("preload-chain-fixture")
            signal("advance")
            ready("ready")
            if case != "title-stop":
                menu = phase("MAIN_MENU_CONFIRMED", arm, "MENU_DURABLE")
                if case == "quiet":
                    refuse("MAIN_MENU_CONFIRMED", arm)
                    refuse("LOAD_BEGIN", (arm[0], menu[1]))
                    refuse("PLAYER_CONTROL", menu)
                    time.sleep(2.2)
                elif case == "preload-gap":
                    signal("introduce-preload-gap")
                    ready("preload-gap-complete")
                elif case == "chain-before-stop":
                    signal("start-preload-chain")
                    ready("callback-reached")
            if case not in ("title-stop", "menu-stop"):
                loading = phase("LOAD_BEGIN", menu, "LOAD_BEGIN_DURABLE")
            if case == "chain-before-stop":
                control = phase("PLAYER_CONTROL", loading, "PLAYER_CONTROL_DURABLE")
                lodge = phase("LODGE_BEGIN", control, "LODGE_BEGIN_DURABLE")
                interior = phase("LODGE_END", lodge, "LODGE_END_DURABLE")
                signal("release-callback")
                signal("simulate-load")
                ready("load-complete")
                signal("simulate-lodge")
                ready("lodge-complete")
                signal("crash-before-stop")
                signal("quit")
                assert proc.wait(timeout=15) == 0
                _, rows, receipt = journal(folder)
                assert witness.exited()["exit_code"] == receipt["exit_code"] != 0
                assert not receipt["stop_durable"] and not receipt["retire_requested"] and not receipt["forced"]
                assert receipt["science"] == "OBSERVED_REACHED_ALLOCATOR"
                assert all(w[metric] != NEGATIVE for w in receipt["windows"]
                           for metric in ("invocation", "allocator"))
                joined, = receipt["windows"][-1]["first_allocator_chains"]
                assert joined["ingress"] < joined["callback"] < loading[0] < control[0]
                assert control[0] < lodge[0] < interior[0] < joined["allocator"]
                chain = [rows[joined[key] - 1] for key in ("ingress", "callback", "allocator")]
                assert len({(r["tid"], r["generation"], r["thread_birth"]) for r in chain}) == 1
                assert all(r["continue_error"] == 0 and r["readback"] for r in chain)
                assert chain[-1]["callback"] == joined["callback"] and chain[1]["ingress"] == joined["ingress"]
                return receipt
            if case not in ("title-stop", "menu-stop", "load-stop"):
                if case == "load-busy":
                    signal("busy-load")
                    time.sleep(2.25)
                if case == "load-slot-loss":
                    signal("replace-load-slot")
                signal("simulate-load")
                ready("callback-reached" if cross else "load-complete")
                if case == "quiet":
                    time.sleep(8.25)
                    assert witness.kernel.WaitForSingleObject(witness.handle, 0) == 258
                    assert not ack(Path(console.name).read_bytes(), b"STOP_DURABLE")
                if case == "load-slot-loss":
                    publish(folder, run, "PLAYER_CONTROL", *loading)
                    status = wait(lambda s: s if b"PHASE_BOUNDARY_UNCONFIRMED" in s or b"PHASE_REFUSED " in s else None)
                    refusals += int(b"PHASE_REFUSED " in status)
                    assert not ack(Path(console.name).read_bytes(), b"PLAYER_CONTROL_DURABLE")
                else:
                    control = phase("PLAYER_CONTROL", loading, "PLAYER_CONTROL_DURABLE")
                if cross:
                    time.sleep(2.2)
                    signal("release-callback")
                    ready("load-complete")
                if case in ("lodge", "lodge-stop", "cross-gap-crash"):
                    lodge = phase("LODGE_BEGIN", control, "LODGE_BEGIN_DURABLE")
                    if case != "lodge-stop":
                        if case == "cross-gap-crash":
                            signal("inject-gap")
                        signal("simulate-lodge")
                        ready("lodge-complete")
                        phase("LODGE_END", lodge, "LODGE_END_DURABLE")
            if case == "cross-gap-crash":
                tool = Path(__file__).resolve().parents[1] / "srr008" / "watch_exit.py"
                command = [sys.executable, "-E", "-B", tool]
                wrong = f"{binary_digest}-{witness.pid}-{witness.birth + 1}"
                refusal = subprocess.run([*command, wrong, binary, folder], capture_output=True, timeout=10)
                (folder / "exit-witness-refusal.txt").write_bytes(refusal.stderr)
                assert refusal.returncode == 1 and b"creation FILETIME mismatch" in refusal.stderr
                with (folder / "exit-witness.console.txt").open("xb") as watch_console:
                    exit_watch = subprocess.Popen([*command, run, binary, folder],
                                                  stdout=watch_console, stderr=subprocess.STDOUT)
                ready("exit-witness-bound.json")
                signal("crash-after-stop")
            if case == "seal-fault":
                space()
                (folder / "stop-prefix.json.partial").mkdir()
            send(folder, run, "stop", 3, "STOP")
            if case == "seal-fault":
                def stop_is_operational(_):
                    try:
                        rows, _ = durable_prefix(folder)
                    except (OSError, ValueError, AssertionError):
                        return False
                    return rows[-1]["kind"] == "stop"

                wait(stop_is_operational)
                signal("simulate-lodge")
                signal("quit")
                assert proc.wait(timeout=15) == 0
                assert not ack(Path(console.name).read_bytes(), b"STOP_DURABLE")
                assert not (folder / "stop-prefix.json").exists()
                receipt = json.loads((folder / "receipt.json").read_bytes())
                assert receipt["writer_failed"] and not receipt["stop_durable"]
                assert receipt["science"] == "OBSERVED_REACHED_ALLOCATOR"
                rows, mark = durable_prefix(folder)
                assert receipt["flushed"] == mark["sequence"] == receipt["stop_sequence"]
                assert rows[-1]["windows"][-1]["journal_complete"]
                assert not receipt["windows"][-1]["journal_complete"]
                assert receipt["windows"][-1]["invocation"] == INCOMPLETE
                assert witness.exited()["exit_code"] == 0
                return {"writer_failed": True, "flushed": receipt["flushed"], "science": receipt["science"]}
            stop = wait(lambda s: ack(s, b"STOP_DURABLE"))
            scientific = verify_stop(folder, run, stop)
            if case == "quiet":
                refuse("LODGE_BEGIN", control)
            send(folder, run, "retire", 4, "QUIT_REQUESTED", stop)
            wait(lambda s: ack(s, b"RETIRE_DURABLE"))
            signal("simulate-load")
            signal("simulate-lodge")
            signal("quit")
            assert proc.wait(timeout=15) == 0
            _, rows, receipt = journal(folder)
            assert witness.exited()["exit_code"] == receipt["exit_code"]
            if exit_watch is not None:
                assert exit_watch.wait(timeout=10) == 0
                bound = json.loads((folder / "exit-witness-bound.json").read_bytes())
                observed = json.loads((folder / "exit-witness-result.json").read_bytes())
                assert bound["access_mask"] == 0x101000 and bound["image"]["sha256"] == binary_digest
                assert observed["run"] == run and observed["signaled"]
                assert observed["process_birth"] == witness.birth and observed["exit_code"] == receipt["exit_code"]
            assert not receipt["forced"] and not receipt["detached"] and receipt["non_killing"]
            assert receipt["stop_durable"] and scientific["windows"] == receipt["windows"]
            assert sum(r["kind"] == "phase_request_refused" for r in rows) == refusals
            assert all(r["continue_error"] == 0 for r in rows if r["kind"] == "event")
            windows = {w["name"]: w for w in scientific["windows"]}
            for key, expected in zip(
                ("title-stop", "menu-stop", "load-stop", "quiet", "lodge", "lodge-stop", "cross-gap-crash"),
                ("MAIN_MENU_CONFIRMED", "LOAD_BEGIN", "PLAYER_CONTROL", "", "", "LODGE_END", ""),
                strict=True,
            ):
                if case == key:
                    assert scientific["missing_boundary"] == expected
            for key, window in windows.items():
                if key == "uncovered_startup":
                    assert window["allocator"] == INCOMPLETE
                elif key == "menu_preload" and case != "menu-stop":
                    assert not window["end_verified"] and window["invocation"] == window["allocator"] == INCOMPLETE
                elif (case, key) in (("load-stop", "load_in_progress"), ("lodge-stop", "lodge_transition"),
                                     ("cross-gap-crash", "lodge_transition"),
                                     ("load-slot-loss", "load_in_progress"), ("load-slot-loss", "post_load"),
                                     ("preload-gap", "load_in_progress")):
                    assert window["invocation"] == window["allocator"] == INCOMPLETE
                elif (case, key) == ("load-busy", "load_in_progress"):
                    assert window["invocation"] == "OBSERVED_INVOKED"
                    assert window["allocator"] == "OBSERVED_REACHED_ALLOCATOR"
                    assert window["accepted_site_hits"] == [512] * 4
                elif (case, key) == ("cross-gap-crash", "load_in_progress"):
                    assert window["invocation"] == "OBSERVED_INVOKED" and window["allocator"] == NEGATIVE
                elif (case, key) == ("cross-gap-crash", "post_load"):
                    assert window["invocation"] == NEGATIVE and window["allocator"] == "OBSERVED_REACHED_ALLOCATOR"
                    joined, = window["first_allocator_chains"]
                    ingress, callback, allocator = (rows[joined[k] - 1] for k in ("ingress", "callback", "allocator"))
                    assert ingress["tid"] == callback["tid"] == allocator["tid"]
                    assert ingress["generation"] == callback["generation"] == allocator["generation"]
                    assert callback["seq"] < control[0] < allocator["seq"]
                    assert allocator["callback"] == callback["seq"] and callback["ingress"] == ingress["seq"]
                else:
                    assert window["invocation"] == window["allocator"] == NEGATIVE, (case, key, window)
            expected_science = ("OBSERVED_REACHED_ALLOCATOR" if cross or case == "load-busy" else
                                INCOMPLETE if case in ("title-stop", "menu-stop", "load-stop", "load-slot-loss", "preload-gap")
                                else NEGATIVE)
            assert receipt["science"] == expected_science
            assert bool(receipt["exit_code"]) == cross and bool(receipt["target_failed"]) == cross
            if case not in ("title-stop", "menu-stop"):
                boundary = rows[loading[0] - 1]
                assert boundary["kind"] == "load_begin" and boundary["checkpoint"] == 1
                assert boundary["thread_slot_readback"] == 0
                assert boundary["opening_eligible"] == (case != "preload-gap")
            if case == "quiet":
                preload = [r for r in rows[menu[0]:loading[0] - 1] if r["kind"] == "periodic_readback"]
                assert any(r["thread_readback_deferred"] for r in preload)
                assert not any(r["census_attempted"] for r in preload)
            if case == "preload-gap":
                assert scientific["checkpoint"] and scientific["observer_healthy_at_stop"]
                assert any(r.get("module_risk") == "unknown" for r in rows[menu[0]:loading[0] - 1])
                assert not windows["load_in_progress"]["start_verified"]
                assert windows["load_in_progress"]["end_verified"]
            if case in ("quiet", "load-busy"):
                load_rows = rows[loading[0]:control[0] - 1]
                events = Counter(r["event_code"] for r in load_rows if r["kind"] == "event")
                assert all(events[k] >= 1 for k in (2, 4, 6, 7))
                assert any(r.get("module_risk") == "incidental" for r in load_rows)
                periodic = [r for r in load_rows if r["kind"] == "periodic_readback"]
                assert periodic and all(r["checkpoint"] and not r["census_attempted"] for r in periodic)
                deferred = sum(r["thread_readback_deferred"] for r in periodic)
                assert deferred >= (4 if case == "quiet" else 1)
                boundary = rows[control[0] - 1]
                assert boundary["kind"] == "player_control" and boundary["checkpoint"] == 1
                if case == "load-busy":
                    assert events[2] == events[4] == 8 and events[6] == events[7] == 2
                    assert sum(r["kind"] == "arm_readback" and r["verified"] for r in load_rows) == 8
                    assert len(periodic) > deferred
                    traps = [r for r in load_rows if r.get("owner") == "hardware"]
                    assert len(traps) == 2048
                    assert all(r["first_chance"] and r["disposition"] == 65538 and r["readback"]
                               and (r["before_dr6"] & 0xe00f) == 1 << r["site"]
                               and not (r["resume_dr6"] & 0xe00f)
                               and (r["resume_flags"] & 0x10100) == 0x10000 for r in traps)
            if case == "load-slot-loss":
                assert (not scientific["checkpoint"] and not scientific["observer_healthy_at_stop"]
                        and any(r["kind"] in ("periodic_readback", "player_control") and not r["checkpoint"]
                                and not r.get("thread_readback_deferred") for r in rows[loading[0]:]))
            scientific.update(target_exit=witness.exited(), refusals=refusals, science=receipt["science"])
            return scientific
        finally:
            if proc.poll() is None and witness is not None:
                send(folder, run, "title", 1, "TITLE_CONFIRMED")
                for name in ("advance", "introduce-preload-gap", "start-preload-chain",
                             "simulate-load", "release-callback", "simulate-lodge", "quit"):
                    signal(name)
                proc.wait(timeout=15)
            if witness is not None:
                witness.close()
            if exit_watch is not None and exit_watch.poll() is None:
                exit_watch.wait(timeout=10)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binary", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("case", nargs="*", choices=CASES)
    args = parser.parse_args()
    space()
    args.output.mkdir()
    for case in args.case or CASES:
        result = exercise(args.binary.resolve(), args.output, case)
        space()
        (args.output / f"{case}.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(f"{case}: {result['science']}", flush=True)


if __name__ == "__main__":
    main()
