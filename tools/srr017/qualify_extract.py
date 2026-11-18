"""Offline qualification of the actual operator controller using owned processes."""

import argparse
import builtins
from contextlib import ExitStack
from dataclasses import replace
import json
from pathlib import Path
from unittest.mock import patch

from tools.srr016 import census, qualify_census
from . import extract
from . import retail_title
from .export import file_sha256
from .qualify_export import check_adapter_refusals, check_fields
import checkpoint
import retail_admission


def forbidden(*_args, **_kwargs):
    raise AssertionError("operator controller invoked a withdrawn operational interface")


def guarded_run(*args, **kwargs):
    """Fixture lifecycles are outside this guard; acquisition cannot launch/quit."""
    original_open = Path.open
    original_import = builtins.__import__

    def checked_import(name, *import_args, **import_kwargs):
        assert not any(word in name.split(".") for word in ("preflight", "watch_exit", "retail_controller",
                                                             "retail_title", "save_policy")), name
        return original_import(name, *import_args, **import_kwargs)

    def checked_open(path, *open_args, **open_kwargs):
        lowered = str(path).lower()
        assert not any(word in lowered for word in ("authorization.json", "allowed_signers", "steam\\userdata",
                                                    "my games\\starfield", ".sfs", "cloud_log")), lowered
        return original_open(path, *open_args, **open_kwargs)

    with ExitStack() as stack:
        for name in ("begin_retail", "open_retail", "open_simulated", "registered_steam_root"):
            if hasattr(retail_admission, name):
                stack.enter_context(patch.object(retail_admission, name, forbidden))
        for name in ("preflight_receipts", "check_exit_bound", "verify_closeout", "_verify_approval", "available_space"):
            stack.enter_context(patch.object(retail_title, name, forbidden))
        for name in ("verify_account", "session"):
            stack.enter_context(patch.object(retail_admission.ProcessMetadata, name, forbidden))
        for name in ("issue", "mark", "validate_identity"):
            if hasattr(checkpoint, name):
                stack.enter_context(patch.object(checkpoint, name, forbidden))
        stack.enter_context(patch.object(census, "capture", forbidden))
        for name in ("validate_identity", "validate_marker", "claim", "validate_title_binding"):
            if hasattr(census, name):
                stack.enter_context(patch.object(census, name, forbidden))
        stack.enter_context(patch("subprocess.Popen", forbidden))
        stack.enter_context(patch("subprocess.run", forbidden))
        stack.enter_context(patch("os.system", forbidden))
        stack.enter_context(patch("winreg.OpenKey", forbidden))
        stack.enter_context(patch.object(Path, "open", checked_open))
        stack.enter_context(patch.object(builtins, "__import__", checked_import))
        return extract.run(*args, **kwargs)


def run(directory):
    directory = Path(directory).resolve()
    directory.mkdir(parents=True)
    build = directory / "build"
    build.mkdir()
    target, provenance = qualify_census.build_fixture(build)
    services = extract.Services(target_name=target.name, expected_sha256=file_sha256(target),
                                retail_layout=False, profile_name="srr017-operator-owned", target_kind="simulated")
    results = {}

    expected_failures = {
        "read-failure": ("INCOMPLETE", "unreadable_region"),
        "cancel": ("FAILED", "operator_cancelled"),
        "cancel-mid": ("INCOMPLETE", "operator_cancelled"),
        "changed-native-identity": ("INCOMPLETE", "pair_namespace_mismatch"),
        "paired-input-change": ("INCOMPLETE", "pair_identity_mismatch"),
        "namespace-invalid": ("INCOMPLETE", "namespace_witness_refused"),
        "bad-owner-key": ("INCOMPLETE", "pndt_key_mismatch"),
        "bad-biome-type": ("INCOMPLETE", "form_type_mismatch"),
        "bad-resource-type": ("INCOMPLETE", "resource_form_type_mismatch"),
        "work-budget": ("INCOMPLETE", "observation_budget"),
        "byte-budget": ("INCOMPLETE", "observation_budget"),
        "bad-count": ("INCOMPLETE", "index_shape"),
        "bad-span": ("INCOMPLETE", "record_span"),
        "cycle": ("INCOMPLETE", "pointer_alias"),
        "capacity-declared-huge": ("INCOMPLETE", "index_shape"),
        "native-pivot-below": ("INCOMPLETE", "index_fence"),
        "native-pivot-above": ("INCOMPLETE", "index_fence"),
        "native-separator-order": ("INCOMPLETE", "index_order"),
        "native-descending-records": ("INCOMPLETE", "index_order"),
        "native-duplicate-records": ("INCOMPLETE", "duplicate_identity"),
        "native-neighbor-overlap": ("INCOMPLETE", "index_order"),
        "bad-fence": ("INCOMPLETE", "index_fence"),
        "bad-minimum": ("INCOMPLETE", "block_minimum"),
        "bad-link": ("INCOMPLETE", "leaf_link_mismatch"),
        "alias-child": ("INCOMPLETE", "pointer_alias"),
        "wrong-image": ("FAILED", "wrong_executable"),
    }

    def observe(name, *, scenario="direct", success=False, kwargs=None, mutation=None):
        with qualify_census.fixture(target, scenario) as (process, command):
            options = dict(services=services, notify=lambda _text: None)
            options.update(kwargs or {})
            if mutation:
                options["between"] = lambda: command(mutation)
            result = guarded_run(directory / name, **options)
            assert process.poll() is None, "controller exited the owned target"
        if success:
            assert result["status"] == "FINISHED", result
            report, dataset = extract.replay_dataset(directory / name / "receipt.jsonl")
            counts = check_fields("direct" if scenario == "relative-data" else scenario, dataset,
                                  expected_namespace=True, defining_only=True, native_only=True,
                                  optional_history=scenario == "capacity-64k")
            if not scenario.startswith("capacity-"):
                check_adapter_refusals(dataset)
            assert report["failure"] is None
            results[name] = {"status": result["status"], **counts,
                             "events": report["events"], "requested_bytes": report["requested_bytes"],
                             "tree_windows": [item["tree_windows"] for item in report["collections"]],
                             "map_entries": [item["map_entries"] for item in report["collections"]],
                             "backend": result["backend"]["actual"],
                             "receipt_bytes": (directory / name / "receipt.jsonl").stat().st_size,
                             "dataset_bytes": (directory / name / "dataset.json").stat().st_size}
        else:
            assert (result["status"], result["failure"][0]) == expected_failures[name], result
            if result["status"] == "INCOMPLETE":
                report, dataset = extract.replay_dataset(directory / name / "receipt.jsonl")
                assert dataset["acquisition"] != "QUALIFIED"
                assert report["failure"][0] == result["failure"][0], result
            results[name] = {"status": result["status"], "failure": result["failure"]}
        return result

    for case in ("corpus", "upper", "relative-data", "all-seven", "many-rsgds",
                 "native-direct", "native-leaf", "native-two-leaf", "native-multilevel",
                 "native-cross-node", "native-right-equality", "native-gap", "capacity-32k", "capacity-64k"):
        observe(case, scenario=case, success=True)
    with qualify_census.fixture(target, "direct") as (first, _), qualify_census.fixture(target, "direct") as (second, _):
        ambiguous = guarded_run(directory / "multiple", services=services, notify=lambda _text: None)
        assert ambiguous["failure"][0] == "process_ambiguous", ambiguous
        explicit = guarded_run(directory / "explicit-pid", pid=second.pid, services=services, notify=lambda _text: None)
        assert explicit["status"] == "FINISHED" and explicit["process"]["pid"] == second.pid, explicit
        assert first.poll() is None and second.poll() is None
        results["multiple"] = ambiguous
        results["explicit-pid"] = explicit
    absent = guarded_run(directory / "absent", services=services, notify=lambda _text: None)
    assert absent["failure"][0] == "process_absent", absent
    results["absent"] = absent
    observe("read-failure", scenario="unreadable")
    observe("cancel", kwargs={"cancelled": lambda: True})
    pulses = [0]

    def cancel_mid():
        pulses[0] += 1
        return pulses[0] > 40

    observe("cancel-mid", kwargs={"cancelled": cancel_mid})
    observe("changed-native-identity", mutation="namespace-drift")
    observe("paired-input-change", mutation="input-drift-clear")
    observe("namespace-invalid", scenario="namespace-invalid")
    observe("bad-owner-key", scenario="bad-owner-key")
    observe("bad-biome-type", scenario="bad-biome-type")
    observe("bad-resource-type", scenario="bad-resource-type")
    for case in ("bad-count", "bad-span", "cycle", "capacity-declared-huge"):
        observe(case, scenario=case)
    for case in ("native-pivot-below", "native-pivot-above", "native-separator-order",
                 "native-descending-records", "native-duplicate-records", "native-neighbor-overlap",
                 "bad-fence", "bad-minimum", "bad-link", "alias-child"):
        observe(case, scenario=case)
    observe("work-budget", kwargs={"limits": {**census.OPERATOR_LIMITS, "events": 5}})
    observe("byte-budget", kwargs={"limits": {**census.OPERATOR_LIMITS, "requested_bytes": 64}})
    observe("wrong-image", kwargs={"services": replace(services, expected_sha256="0" * 64)})
    receipt = directory / "corpus" / "receipt.jsonl"
    corrupt = directory / "corrupt.jsonl"
    payload = receipt.read_bytes()
    corrupt.write_bytes(payload[:-32])
    try:
        extract.replay_dataset(corrupt)
    except (ValueError, census.ReadFailure, json.JSONDecodeError):
        results["truncated-replay"] = "REFUSED"
    else:
        raise AssertionError("truncated receipt replayed")
    try:
        guarded_run(directory / "corpus", services=services, notify=lambda _text: None)
    except FileExistsError:
        results["existing-output"] = "ORDINARY_FILE_ERROR"
    else:
        raise AssertionError("existing evidence overwritten")
    # Existing directories without colliding output names remain ordinary valid output.
    prepared = directory / "prepared-output"
    prepared.mkdir()
    (prepared / "notes.txt").write_text("operator notes", encoding="utf-8")
    with qualify_census.fixture(target, "direct"):
        result = guarded_run(prepared, services=services, notify=lambda _text: None)
        assert result["status"] == "FINISHED", result
    results["prepared-output"] = "FINISHED"
    summary = {"source_sha256": extract.digest(extract.source_manifest()),
               "work_sha256": extract.digest(extract.work_manifest()),
               "work": extract.work_manifest(), "build": provenance, "cases": results}
    extract.write_json(directory / "qualification.json", summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    summary = run(args.output)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
