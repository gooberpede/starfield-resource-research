"""Compare identical Stage B disposable runs from two frozen observer builds."""

import argparse
import json
from collections import Counter
from pathlib import Path

from qualify import journal
from qualify_stage_b import CASES


def summarize(directory, case, candidate):
    _, rows, receipt = journal(directory / case)
    events = [row for row in rows if row["kind"] == "event"]
    traps = [row for row in events if row.get("owner") == "hardware"]
    arming = [row for row in rows if row["kind"] == "arm_readback"]
    periodic = [row for row in rows if row["kind"] == "periodic_readback"]
    for row in traps:
        if not row["continue_error"] and row["disposition"] == 0x10002:
            assert row["readback"] and row["first_chance"]
            assert row["before_dr6"] & 0xE00F == 1 << row["site"]
            assert row["resume_dr6"] & 0xE00F == 0
            assert row["resume_flags"] & 0x10100 == 0x10000
            if candidate:
                assert row["execution_state_preserved"], (case, row["seq"])
    if candidate:
        assert all(not row["census_attempted"] for row in periodic)
        assert all(row["execution_state_preserved"] for row in arming if row["verified"])
    if case == "load-busy":
        load, = (row["seq"] for row in rows if row["kind"] == "load_begin")
        control, = (row["seq"] for row in rows if row["kind"] == "player_control")
        active = [row for row in traps if load < row["seq"] < control]
        assert Counter(row["site"] for row in active) == {site: 512 for site in range(4)}
        assert len({row["generation"] for row in active}) == 8
        for hit in active:
            assert any(row["verified"] and row["seq"] < hit["seq"] and
                       row["generation"] == hit["generation"] for row in arming)
    return dict(verdict=receipt["science"], sealed=bool(receipt["stop_durable"]),
                target_exit=receipt["exit_code"], continued=receipt["continued"],
                verified_arms=sum(row["verified"] for row in arming),
                owned_sites=dict(Counter(row["site"] for row in traps)),
                timer_running_sweeps=sum(row["census_attempted"] for row in periodic),
                event_held_samples=sum(not row["census_attempted"] and
                                       not row["thread_readback_deferred"] for row in periodic),
                windows=[(w["name"], w["invocation"], w["allocator"]) for w in receipt["windows"]])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args()
    result = {}
    for case in CASES:
        baseline = summarize(args.baseline, case, False)
        candidate = summarize(args.candidate, case, True)
        for field in ("verdict", "sealed", "target_exit", "windows"):
            assert baseline[field] == candidate[field], (case, field)
        result[case] = dict(baseline=baseline, candidate=candidate)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
