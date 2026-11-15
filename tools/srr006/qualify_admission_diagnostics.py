"""Check the bytes and attribution of previously collected diagnostic fixtures."""
import argparse
import hashlib
import json
from pathlib import Path


CASES = {
    "debugger-query-denied": ("preflight", "target_debugger_query", "CheckRemoteDebuggerPresent", 5),
    "target-open-invalid": ("target_open", "target_handle_open", "OpenProcess", 87),
    "pid": ("preflight", "process_pid_mismatch", None, None),
    "epoch": ("preflight", "process_epoch_mismatch", None, None),
    "file-id": ("preflight", "file_id_mismatch", None, None),
    "mapping": ("preflight", "mapped_window_digest", None, None),
    "first-module": ("preflight", "module_first", "Module32FirstW", 24),
    "iteration": ("preflight", "module_iteration", "Module32NextW", 299),
    "missing-loader": ("preflight", "ntdll_missing", None, None),
    "missing-main": ("preflight", "main_image_missing", None, None),
    "overlay": ("preflight", "backing_path_mismatch", None, None),
    "eligibility": ("eligibility", "operator_cancel", None, None),
    "attach-api": ("debug_attach", "debug_attach_api", "DebugActiveProcess", 5),
}


def sealed_rows(folder):
    seal = json.loads((folder / "durable-prefix.json").read_bytes())
    raw = (folder / "events.jsonl").read_bytes()
    durable, tail = raw[:seal["bytes"]], raw[seal["bytes"]:]
    assert durable.endswith(b"\n") and len(durable) == seal["bytes"]
    assert hashlib.sha256(durable).hexdigest() == seal["sha256"]
    rows = list(map(json.loads, durable.splitlines()))
    assert [row["seq"] for row in rows] == list(range(1, seal["sequence"] + 1))
    assert not (folder / "stop-prefix.json").exists()
    return rows, tail, seal


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    parser.add_argument("console", type=Path)
    args = parser.parse_args()
    rows, tail, seal = sealed_rows(args.folder)
    assert not tail and [row["case"] for row in rows] == list(CASES)
    for row in rows:
        assert row["kind"] == "attach_refused" and row["diagnostic_schema"] == 1
        assert tuple(row[key] for key in ("stage", "predicate", "operation", "winerror")) == CASES[row["case"]]
        assert bool(row["attach_attempted"]) == (row["stage"] == "debug_attach")
        assert bool(row["preflight"]) == (row["stage"] in ("eligibility", "debug_attach"))
        if row["case"] == "target-open-invalid":
            assert row["expected"] == 0x100410
        if row["case"] in ("pid", "epoch"):
            assert row["expected"] == row["observed"] + 1
        if row["case"] == "mapping":
            assert row["rva"] == 512 and row["detail"] == "main_image_mapping"
    prior, torn, prior_seal = sealed_rows(args.folder / "write-failure")
    assert len(prior) == 64 and all(row["kind"] == "fixture_prefix" for row in prior)
    assert b'"kind":"attach_refused"' in torn and not torn.endswith(b"\n")
    tag = b"ATTACH_REFUSAL_NOT_DURABLE "
    fallback, = [json.loads(line[len(tag):]) for line in args.console.read_bytes().splitlines()
                 if line.startswith(tag)]
    assert fallback["stage"] == "preflight" and fallback["predicate"] == "target_already_debugged"
    assert not fallback["attach_attempted"] and fallback["winerror"] is None
    print(json.dumps({"checked_refusals": len(rows), "durable": seal,
                      "write_failure_verified_prefix": prior_seal,
                      "write_failure_unverified_tail_bytes": len(torn)}, sort_keys=True))


if __name__ == "__main__":
    main()
