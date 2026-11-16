"""Check Stage B admission refuses a genuinely unarmed or unread thread."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time

from qualify import ExactChild, journal, space
from qualify_attach import send


def qualify(binary, output, fault):
    folder = output / fault
    transcript = output / f"{fault}.console.txt"
    with transcript.open("xb") as log:
        proc = subprocess.Popen([binary, "--fixture-attach", "admission-stage-b-quiet", folder],
                                stdout=log, stderr=subprocess.STDOUT)

    def wait(predicate):
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            result = predicate(transcript.read_bytes())
            if result:
                return result
            if proc.poll() is not None:
                break
            time.sleep(0.025)
        raise AssertionError((fault, transcript.read_bytes()))

    identity = ExactChild(wait(lambda text: text if b"EXACT_CHILD " in text and text.endswith(b"\n") else None))
    run = f"{hashlib.sha256(binary.read_bytes()).hexdigest()}-{identity.pid}-{identity.birth}"

    def finish_fixture():
        for signal in ("advance", "simulate-load", "simulate-lodge", "quit"):
            (folder / signal).touch()

    try:
        (folder / fault).touch()
        send(folder, run, "title", 1, "TITLE_CONFIRMED")
        wait(lambda text: b"ARMING_REFUSED" in text)
        finish_fixture()
        assert proc.wait(timeout=30) == 0
        assert identity.exited()["exit_code"] == 0
        _, rows, receipt = journal(folder)
        assert not any(r["kind"] == "arm_readback" and r["verified"] for r in rows)
        assert not any(r.get("owner") == "hardware" for r in rows)
        assert b"ATTACH_ARMED" not in transcript.read_bytes()
        assert receipt["science"] == "INSTRUMENTATION_INCOMPLETE" and not receipt["stop_durable"]
        barrier, = (r for r in rows if r["kind"] == "attach_barrier")
        assert barrier["continued"] and not barrier["healthy"]
        if fault == "fixture-omit-arm":
            assert any(r["kind"] == "fixture_arm_omitted" for r in rows)
            assert not any(r["kind"] in ("arm_rollback", "arm_readback") for r in rows)
        else:
            rollback, = (r for r in rows if r["kind"] == "arm_rollback")
            missing, = (r for r in rows if r["kind"] == "arm_readback")
            assert rollback["verified"] and not missing["context_sampled"]
            assert rollback["generation"] == missing["generation"]
        return dict(fault=fault, barrier=barrier["seq"], exit_code=receipt["exit_code"],
                    result=receipt["science"])
    finally:
        if proc.poll() is None:
            finish_fixture()
        identity.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binary", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    space()
    args.output.mkdir()
    for fault in ("fixture-omit-arm", "fixture-withhold-arm-readback"):
        print(json.dumps(qualify(args.binary.resolve(strict=True), args.output, fault)), flush=True)


if __name__ == "__main__":
    main()
