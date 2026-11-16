"""Exercise explicit SRR-013 structural mode against disposable Windows children."""

import argparse
from hashlib import sha256
import json
from pathlib import Path

from checkpoint import issue, mark
from contract import INDETERMINATE, POPULATED as STRICT_POPULATED
from memory import ReadFailure, Windows, epoch
from observe import encode, replay
from qualify import FIXTURE, ROOT, digest, owned_fixture
from qualify_retail import REFUSE as ADMISSION_REFUSALS
from qualify_retail import forbidden_admission, run as baseline_run
from qualify_retail import run_case, simulated_append
from retail_admission import begin_simulated, open_simulated
from retail_controller import observe_window
from structural_title import SCOPE, reserve_authorization, source_identity


WORK = ROOT / ".local-work" / "codex" / "SRR-013-structural"
POPULATED = "STRUCTURALLY_POPULATED"
ZERO = "STRUCTURALLY_ZERO"
NONZERO_REASON = "validated_nonzero_resource_ids"
ZERO_REASON = "validated_zero_fields"
CONTROL_FAILURE = "comparison_control_failed"
COVERAGE_FAILURE = "range_coverage"


def expected_for_second(reason):
    return (NONZERO_REASON, reason, NONZERO_REASON, NONZERO_REASON)


EXPECTATIONS = {
    "title": (NONZERO_REASON,) * 4,
    "menu": (ZERO_REASON,) * 4,
    "settled-gameplay": (NONZERO_REASON, ZERO_REASON, NONZERO_REASON, NONZERO_REASON),
    "structural-different": (NONZERO_REASON,) * 4,
    "structural-missing": expected_for_second("resource_form_absent"),
    "structural-wrong-type": expected_for_second("resource_form_type_mismatch"),
    "structural-alias": expected_for_second("resource_pointer_alias"),
    "structural-wrong-header": expected_for_second("resource_form_id_mismatch"),
    "structural-resource-vptr": expected_for_second("resource_form_vptr_mismatch"),
    "structural-duplicate-resource": expected_for_second("resource_form_duplicate"),
    "structural-table-resource": expected_for_second("resource_pointer_alias"),
    "structural-control-zero": (NONZERO_REASON, NONZERO_REASON, NONZERO_REASON, ZERO_REASON),
    "structural-control-bad": (CONTROL_FAILURE,) * 3 + ("resource_form_absent",),
    "structural-zero-wrong-type": ("edge_type_mismatch",) * 3 + (CONTROL_FAILURE,),
    "structural-zero-wrong-map": (ZERO_REASON, "pointer_alias", ZERO_REASON, ZERO_REASON),
    "structural-zero-table-biom": (ZERO_REASON, "pointer_alias", ZERO_REASON, ZERO_REASON),
    "structural-zero-wrong-pndt": ("pndt_key_mismatch",) * 3 + (CONTROL_FAILURE,),
    "structural-zero-absent": (COVERAGE_FAILURE, "component_absent", COVERAGE_FAILURE, CONTROL_FAILURE),
    "context-absent": ("context_absent",) * 4,
    "context-decoy": ("context_ambiguous",) * 4,
    "wrong-context-vptr": ("owner_type_mismatch",) * 4,
    "wrong-registry": ("registry_unverified",) * 4,
    "unregistered": ("registry_unverified",) * 4,
    "wrong-owner": (COVERAGE_FAILURE, "component_absent", COVERAGE_FAILURE, CONTROL_FAILURE),
    "wrong-biom": ("edge_biom_mismatch",) * 3 + (CONTROL_FAILURE,),
    "wrong-seed": (NONZERO_REASON,) * 4,
    "wrong-rnam": (NONZERO_REASON,) * 4,
    "wrong-override": (NONZERO_REASON,) * 4,
    "duplicate": (COVERAGE_FAILURE, COVERAGE_FAILURE, "component_duplicate", CONTROL_FAILURE),
    "lying-minimum": ("block_minimum",) * 4,
    "bad-directory": ("index_shape",) * 4,
    "excessive": ("traversal_budget",) * 4,
    "short-read": ("read_incomplete",) * 4,
    "clear": ("inconsistent_pair",) * 4,
    "drift-resource": ("inconsistent_pair",) * 4,
    "mid-read-insert": ("structural_change",) * 4,
    "aba": (NONZERO_REASON,) * 4,
    "stable-clear": (ZERO_REASON,) * 4,
    "budget-expired": ("observation_budget",) * 4,
    "marker-mode": ("marker_mode",) * 4,
    **{case: (reason,) * 4 for case, reason in ADMISSION_REFUSALS.items()},
}


def check_result(path, report, mode, reasons):
    replayed = replay(path, expected_mode=mode)
    if report.get("mode") != mode or encode(replayed) != encode(report):
        raise AssertionError(f"{path.stem}: bound mode or replay differs")
    rows = report["samples"]
    if tuple(row["reason"] for row in rows) != reasons:
        raise AssertionError(f"{path.stem}: expected {reasons}, got {[row['reason'] for row in rows]}")
    qualified = {NONZERO_REASON: POPULATED, ZERO_REASON: ZERO} if mode == "structural" else {
        "tuple_match": STRICT_POPULATED,
    }
    for row in rows:
        if row["outcome"] != qualified.get(row["reason"], INDETERMINATE):
            raise AssertionError(f"{path.stem}: reason does not support the classification")
        if mode == "structural" and row["prediction_comparison"] != "conditional":
            raise AssertionError(f"{path.stem}: structural mode asserted prediction applicability")
        if row["outcome"] in (POPULATED, ZERO):
            words = row["observed_words"]
            if len(words) != 7 or words != row["repeat_words"]:
                raise AssertionError(f"{path.stem}: qualified outcome lacks complete agreeing words")
            witnesses = [(item["slot"], item["form_id"]) for item in row["resource_forms"]]
            if witnesses != [(i, word) for i, word in enumerate(words) if word]:
                raise AssertionError(f"{path.stem}: nonzero fields lack exact independent witnesses")
            if any(words) != (row["outcome"] == POPULATED):
                raise AssertionError(f"{path.stem}: result contradicts the observed words")
    return {"case": path.stem, "mode": mode, "reasons": reasons, "receipt_sha256": digest(path)}


def compare_modes(directory, fixture, scenario, reason):
    log = directory / f"same-{scenario}.steam.log"
    log.write_bytes(b"disposable Steam attribution baseline\n")
    baseline = begin_simulated(fixture, digest(fixture), log)
    with owned_fixture(scenario, fixture) as (proc, _command):
        pid, creation = epoch(Windows(), int(proc._handle))
        simulated_append(log, pid, fixture)
        observed = {}
        for mode in ("strict", "structural"):
            attempt = issue(directory, mode=mode)
            marker = mark(attempt, {"pid": pid, "creation": creation}, "title")
            binding = {"target_kind": "simulated", "attempt": attempt, "marker": marker}
            path = directory / f"same-{scenario}-{mode}.jsonl"
            observed[mode] = (
                path,
                observe_window(path, directory, open_simulated(baseline, proc), binding, None, mode=mode),
            )
    strict, structural = (observed[mode][1] for mode in ("strict", "structural"))
    if strict["identity_brackets"] != structural["identity_brackets"]:
        raise AssertionError("mode comparison did not retain the same authenticated target")
    if [row["observed_words"] for row in strict["samples"]] != [
        row["observed_words"] for row in structural["samples"]
    ]:
        raise AssertionError("mode comparison did not observe the same words")
    return [
        check_result(*observed["strict"], "strict", ("effective_inputs_unverified",) * 4),
        check_result(*observed["structural"], "structural", (reason,) * 4),
    ]


def require_refused(path, expected_mode):
    try:
        replay(path, expected_mode=expected_mode)
    except (ValueError, ReadFailure):
        return
    raise AssertionError(f"{path.stem}: replay accepted altered evidence or a different mode")


def check_replay_boundaries(directory):
    negatives = []
    for source_mode, destination_mode in (("strict", "structural"), ("structural", "strict")):
        source = directory / f"same-populated-{source_mode}.jsonl"
        require_refused(source, destination_mode)
        lines = source.read_bytes().splitlines(keepends=True)
        header, trailer = json.loads(lines[0]), json.loads(lines[-2])
        header["mode"] = destination_mode
        header["binding"]["attempt"]["mode"] = destination_mode
        header["binding"]["marker"]["mode"] = destination_mode
        trailer["data"]["mode"] = destination_mode
        edited = encode(header) + b"\n" + b"".join(lines[1:-2]) + encode(trailer) + b"\n"
        digest_hex = sha256(edited).hexdigest()
        path = directory / f"resealed-{source_mode}-to-{destination_mode}.jsonl"
        path.write_bytes(edited + encode({"kind": "seal", "sha256": digest_hex}) + b"\n")
        require_refused(path, destination_mode)
        negatives.append(path)
    source = directory / "same-populated-structural.jsonl"
    raw = source.read_bytes()
    for variant, data in (("partial", raw.rsplit(b"\n", 2)[0] + b"\n"),
                          ("corrupted", raw.replace(b"validated_nonzero_resource_ids", b"changed", 1))):
        path = directory / f"{variant}-structural.jsonl"
        path.write_bytes(data)
        require_refused(path, "structural")
        negatives.append(path)
    return {path.stem: digest(path) for path in negatives}


def check_authorization(directory):
    custody = directory / "disposable-authorization-control"
    custody.mkdir()
    record = custody / "authorization.json"
    exact = {"scope": SCOPE, "source_sha256": source_identity(), "custody": str(custody.resolve()),
             "approval_reference": "Disposable reservation control only"}
    for field, value in (("scope", "wrong-scope"), ("source_sha256", "0" * 64), ("custody", "wrong-custody")):
        record.write_bytes(encode({**exact, field: value}))
        try:
            reserve_authorization(record, custody)
        except ValueError:
            continue
        raise AssertionError(f"unexpectedly accepted invalid authorization {field}")
    record.write_bytes(encode(exact))
    reserved = reserve_authorization(record, custody)
    if reserved["authorization_sha256"] != digest(record):
        raise AssertionError("reservation failed to bind the reviewed source and exact record")
    try:
        reserve_authorization(record, custody)
    except FileExistsError:
        pass
    else:
        raise AssertionError("duplicate authorization reserve succeeded")
    receipt = custody / "guarded-retail.jsonl"
    binding = {"target_kind": "retail", "marker": {"label": "title"}}
    guarded = observe_window(receipt, custody, forbidden_admission(), binding, None, mode="structural")
    check_result(receipt, guarded, "structural", ("retail_authorization_required",) * 4)
    return {"offline_reservation_controls": ["scope", "source", "custody", "duplicate"],
            "guarded_retail_receipt_sha256": digest(receipt)}


def run(directory):
    directory.mkdir(parents=True, exist_ok=False)
    baseline_run(directory / "baseline")
    baseline = json.loads((directory / "baseline" / "summary-retail-like.json").read_bytes())
    fixture = directory / "baseline" / "baseline" / "build" / FIXTURE.name
    matrix = [
        *compare_modes(directory, fixture, "populated", NONZERO_REASON),
        *compare_modes(directory, fixture, "zero", ZERO_REASON),
    ]
    strict = run_case(directory, fixture, "explicit-strict", mode="strict")
    matrix.append(check_result(directory / "explicit-strict.jsonl", strict, "strict", ("tuple_match",) * 4))
    for case, reasons in EXPECTATIONS.items():
        scenario = case if case.startswith("structural-") or case in {
            "context-absent", "context-decoy", "wrong-context-vptr", "unregistered", "wrong-biom", "excessive",
            "wrong-seed", "wrong-rnam", "wrong-override",
        } else None
        result = run_case(directory, fixture, case, mode="structural", scenario=scenario)
        if case == "structural-different":
            row = result["samples"][1]
            if row["observed_words"][0] != 0xE100:
                raise AssertionError("divergent validated FormID was lost or replaced by a prediction")
        matrix.append(check_result(directory / f"{case}.jsonl", result, "structural", reasons))
    invalid = check_replay_boundaries(directory)
    summary = {"build": baseline["build"], "original_cases": baseline["baseline_cases"],
               "prior_retail_like_cases": len(baseline["cases"]), "new_observations": matrix,
               "invalid_receipts": invalid, "authorization_checks": check_authorization(directory)}
    (directory / "summary-structural.json").write_bytes(encode(summary) + b"\n")
    print(f"Passed {len(matrix)} new external observations and {len(invalid)} replay challenges.")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", help="new private qualification directory name")
    args = parser.parse_args()
    name = args.name
    if not name.isascii() or not name.replace("-", "").replace("_", "").isalnum():
        parser.error("evidence directory name must contain letters, digits, hyphens or underscores")
    run(WORK / Path(name))
