"""Qualify bounded-progress acquisition on disposable Windows processes."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import checkpoint
import observe
from qualify import FIXTURE, ROOT, digest
from qualify_retail import run_case
from qualify_structural import NONZERO_REASON, check_result, require_refused, run as qualify_structural


WORK = ROOT / ".local-work" / "codex" / "SRR-013-budget-recovery"


def check_window(directory, fixture, case, reasons, *, scenario=None, first_collection_only=False):
    result = run_case(directory, fixture, case, mode="structural", scenario=scenario)
    path = directory / f"{case}.jsonl"
    if first_collection_only and (len(result["collections"]) != 1 or len(result["identity_brackets"]) != 1
                                  or not all(row["observed_words"] and row["repeat_words"] is None
                                             for row in result["samples"])):
        raise AssertionError(f"{case}: completed first collection was lost or a partial second was promoted")
    record = check_result(path, result, "structural", reasons)
    return {**record, "failure": result["failure"], "detail": result["detail"], "timing": result["timing"],
            "calls": result["read_and_identity_calls"], "requested_bytes": result["requested_bytes"]}


def replace_declared_limit(source, target, key, value):
    original = source.read_bytes().splitlines(keepends=True)
    header = json.loads(original[0])
    header["limits"][key] = value
    body = observe.encode(header) + b"\n" + b"".join(original[1:-1])
    target.write_bytes(body + observe.encode({"kind": "seal", "sha256": sha256(body).hexdigest()}) + b"\n")


def check_work_caps(directory, fixture, successful_receipt):
    observations, challenges = [], {}
    cases = (
        ("operation-cap", "MAX_EVENTS", "events", 16, "calls", "acquisition operation limit exceeded"),
        ("requested-byte-cap", "MAX_BYTES", "requested_bytes", 32, "requested_bytes",
         "acquisition requested-byte limit exceeded"),
    )
    for case, constant, key, limit, statistic, detail in cases:
        configured = getattr(observe, constant)
        with patch.object(observe, constant, limit):
            result = check_window(directory, fixture, case, ("observation_budget",) * 4)
            if result["detail"] != detail or not 0 < result[statistic] <= limit:
                raise AssertionError(f"{case}: invalid finite-work refusal accounting")
            observations.append({**result, "test_policy_override": {key: limit}})
            overrun = directory / f"resealed-{case}-overrun.jsonl"
            replace_declared_limit(successful_receipt, overrun, key, limit)
            # The header now agrees with the fixture policy. Refusal must also
            # inspect the recorded events that exceed the declared allowance.
            require_refused(overrun, "structural")
            challenges[overrun.stem] = digest(overrun)

        early_refusal = directory / f"resealed-{case}-early-refusal.jsonl"
        replace_declared_limit(directory / f"{case}.jsonl", early_refusal, key, configured)
        require_refused(early_refusal, "structural")
        challenges[early_refusal.stem] = digest(early_refusal)
    return observations, challenges


def check_seal_failure(directory, fixture):
    original_seal = observe.Journal.seal

    def fail_sync(journal):
        with patch.object(observe.os, "fsync", side_effect=OSError("disposable seal sync failure")):
            return original_seal(journal)

    with patch.object(observe.Journal, "seal", fail_sync):
        try:
            run_case(directory, fixture, "seal-sync-failure", mode="structural")
        except observe.JournalFailure as error:
            if error.code != "journal_seal":
                raise AssertionError("wrong journal failure classification") from error
        else:
            raise AssertionError("failed seal returned an acquisition verdict")
    published = directory / "seal-sync-failure.jsonl"
    partial = directory / "seal-sync-failure.jsonl.partial"
    if published.exists() or not partial.is_file():
        raise AssertionError("seal failure published a receipt or discarded the private prefix")
    require_refused(partial, "structural")
    return {"reason": "journal_seal", "partial_sha256": digest(partial)}


def run(directory):
    directory.mkdir(parents=True, exist_ok=False)
    legacy = directory / "regression"
    baseline = qualify_structural(legacy)
    fixture = legacy / "baseline" / "baseline" / "build" / FIXTURE.name
    first_only = {"cancel-between": "operator_cancelled", "process-exited": "process_exited"}
    controls = [check_window(directory, fixture, case, (reason,) * 4, first_collection_only=True)
                for case, reason in first_only.items()]
    controls.append(check_window(directory, fixture, "cancel-during", ("operator_cancelled",) * 4))
    with patch.object(checkpoint, "MARKER_MAX_AGE_NS", 1_000_000_000):
        # The real disposable admission deliberately outlasts the test intake
        # freshness threshold after a freshly supplied marker was consumed.
        controls.append(check_window(directory, fixture, "slow-admission", (NONZERO_REASON,) * 4))

    cases = (
        ("depth-budget", ("traversal_budget",) * 4),
        ("excessive", ("traversal_budget",) * 4),
        ("chain-budget", (NONZERO_REASON, "traversal_budget", NONZERO_REASON, NONZERO_REASON)),
        ("map-loop", (NONZERO_REASON, "form_map_unverified", NONZERO_REASON, NONZERO_REASON)),
        ("loop", ("pointer_alias",) * 4),
    )
    controls += [check_window(directory, fixture, case, reasons, scenario=case) for case, reasons in cases]
    caps, challenges = check_work_caps(directory, fixture, legacy / "same-populated-structural.jsonl")
    summary = {"build": baseline["build"], "regressions": {"original": baseline["original_cases"],
               "retail_like": baseline["prior_retail_like_cases"], "structural": len(baseline["new_observations"])},
               "changed_duration_control": baseline["changed_duration_control"], "extra_controls": controls + caps,
               "work_limit_replay_challenges": challenges, "seal_failure": check_seal_failure(directory, fixture)}
    (directory / "summary-budget.json").write_bytes(observe.encode(summary) + b"\n")
    print(f"Recovered slow paired control and passed {len(controls) + len(caps)} additional external controls.")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", help="new private qualification directory name")
    name = parser.parse_args().name
    if not name.isascii() or not name.replace("-", "").replace("_", "").isalnum():
        parser.error("evidence directory name must contain letters, digits, hyphens or underscores")
    run(WORK / Path(name))
