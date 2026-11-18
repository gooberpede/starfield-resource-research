"""Exercise the exact written-authorization title controller on disposable children."""

import argparse
import json
from contextlib import ExitStack, contextmanager
from datetime import datetime, timezone
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
from time import monotonic, sleep, time_ns

from tools.srr016 import census, qualify_census
from retail_admission import open_simulated
from . import retail_title as title
from .export import bound_dataset, file_sha256, output_bytes
from .qualify_export import check_fields, fixture_sources


PRIVATE = title.ROOT / ".local-work" / "codex" / "SRR-017-retail-readiness"
SID = "S-1-5-21-300-1001"


def expected_error(action, code=None):
    try:
        action()
    except (title.ReadFailure, ValueError, OSError) as error:
        if code is not None and getattr(error, "code", None) != code:
            raise AssertionError(f"expected {code}, got {error}") from error
    else:
        raise AssertionError("a disallowed run or tampered replay was admitted")


def make_receipts(directory, phase, changed=False):
    kind = "srr-save-environment-receipt/1"
    utc = datetime.now(timezone.utc).isoformat()
    image = census.RETAIL_SHA256
    environment = {"schema": kind, "mode": "environment", "ok": True, "utc": utc,
                   "retail_executable": {"sha256": image}, "manifest_fields": {
                       "appid": str(title.STEAM_APP), "buildid": str(title.STEAM_APP_BUILD),
                       "StateFlags": "4", "installdir": "Starfield"},
                   "cloud_flag": "0", "overlay_flag": "0", "configured_save_path_agrees": True,
                   "configured_save_paths": [], "sfse_loader": False}
    if directory.name == "installed-sfse":
        environment["sfse_loader"] = True
    protection = {"schema": kind, "mode": "protection", "ok": True, "utc": utc, "backup_path": "synthetic backup input",
                  "backup_entry_count": 193, "policy_file_sha256": "5" * 64,
                  "designations": {"owned-000.sfs": True, "owned-001.sfs": True}}
    for offset, (name, count) in enumerate((("documents", 98), ("remote", 95))):
        rows = []
        for index in range(count):
            sha256 = f"{offset + index:064x}"
            original = {"size": index + 1, "sha256": sha256, "volume": 1, "file_id": offset * 100 + index}
            backup = {**original, "volume": 2}
            rows.append({"relative": f"owned-{index:03d}.sfs", "original": original, "candidate": backup,
                         "match": True})
        protection[name] = {"ok": True, "matched": count, "expected_protected": count,
                            "counts": {"PROTECTED": count}, "other": [], "pairs": rows, "transient": {}}
    if changed:
        protection["remote"]["transient"]["unexpected-owned.sfs"] = {"file_id": 177, "size": 1, "mtime_ns": 1}
    for mode, value in (("environment", environment), ("protection", protection)):
        folder = directory / f"{phase}-{mode}"
        folder.mkdir()
        title.write_exclusive(folder / "receipt.json", value)


def authorize(directory, steam, fixture_source=None, *, changes=None):
    make_receipts(directory, "pre")
    manifest = title.candidate_manifest()
    approval = directory / "authorization.json"
    value = {
        "schema": "srr017-title-authorization-v2", "scope": census.RETAIL_FIXTURE_SCOPE,
        "approval_reference": "Maintainer's written approval for this owned fixture run",
        "custody": str(directory), "source_sha256": title.digest_manifest(manifest),
        "work_sha256": title.digest_manifest(manifest["work"]),
    }
    value.update(changes or {})
    # A human-readable JSON record is admitted, as in SRR-013.
    approval.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    return (approval,)


def current_session():
    return title.ProcessMetadata().session(os.getpid())


def fake_space():
    return {"C:": 100_000_000_000, "D:": 100_000_000_000}


def test_no_begin(*args, **kwargs):
    raise AssertionError("an authorization rejection reached a process backend")


def gate_tests(directory, steam, fixture_source):
    cases = (
        ("blank-approval", {"approval_reference": " "}, "retail_authorization_format"),
        ("wrong-work", {"work_sha256": "8" * 64}, "retail_authorization_mismatch"),
        ("wrong-source", {"source_sha256": "8" * 64}, "retail_authorization_mismatch"),
        ("wrong-scope", {"scope": "srr013-structural-title"}, "retail_authorization_mismatch"),
        ("wrong-custody", {"custody": str(steam)}, "retail_authorization_mismatch"),
    )
    services = title.Services("simulated", lambda: (SID, current_session()),
                              test_no_begin, test_no_begin, test_no_begin, fake_space)
    findings = {}
    for name, changes, code in cases:
        custody = directory / name
        custody.mkdir()
        paths = authorize(custody, steam, fixture_source, changes=changes)
        expected_error(lambda: title.acquire(steam, custody, *paths, services=services), code)
        assert not (custody / title.CLAIM).exists()
        findings[name] = code
    custody = directory / "real-unapproved"
    custody.mkdir()
    args = [sys.executable, "-E", "-B", "-m", "tools.srr017.retail_title", "observe-title", str(steam), str(custody),
            str(custody / "authorization.json")]
    result = subprocess.run(args, capture_output=True, cwd=title.ROOT, check=False)
    assert result.returncode == 1 and b"Refused:" in result.stderr and not (custody / title.CLAIM).exists()
    findings["unapproved-production-command"] = result.returncode
    return findings


@contextmanager
def owned_services(directory, target, steam, scenario, case, fixture_source):
    processes = {}
    observed = {"begin_calls": 0, "open_calls": 0}
    original_plugin = fixture_source.read_bytes() if fixture_source.exists() else None
    with ExitStack() as resources:
        @contextmanager
        def begin(approved, *, digest_file):
            assert approved == steam
            observed["begin_calls"] += 1
            log = directory / "fixture-steam.log"
            log.write_bytes(b"owned launch baseline\n")
            baseline = qualify_census.simulated_baseline(target, file_sha256(target), log)
            processes.update(baseline=baseline, log=log)
            yield baseline

        @contextmanager
        def select(baseline, *, digest_file):
            observed["open_calls"] += 1
            if case == "mapped-drift":
                native_get = baseline.api.K32GetMappedFileNameW

                def mismatched_file(handle, image, path, width):
                    result = native_get(handle, image, path, width)
                    if result:
                        path.value += ".drift"
                    return result

                baseline.api.K32GetMappedFileNameW = mismatched_file
            with open_simulated(baseline, processes["process"], digest_file=digest_file) as reader:
                yield reader

        def respond(prompt):
            if "type launched" in prompt:
                process, command = resources.enter_context(qualify_census.fixture(target, scenario))
                processes.update(process=process, command=command)
                qualify_census.simulated_append(processes["log"], process.pid, target)
                if case == "ambiguous-steam":
                    qualify_census.simulated_append(processes["log"], process.pid, target)
                return "launched"
            phase = title.object_from((directory / "target-bound.json").read_bytes())
            log = resources.enter_context((directory / "exit-witness.log").open("xb"))
            watcher = subprocess.Popen([sys.executable, "-E", "-B", str(title.ROOT / "tools/srr008/watch_exit.py"),
                                        phase["epoch"], phase["image"], str(directory)],
                                       stdout=log, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
            processes["watcher"] = watcher
            deadline = monotonic() + 30
            while not (directory / "exit-witness-bound.json").is_file():
                if watcher.poll() is not None or monotonic() >= deadline:
                    raise RuntimeError("owned exit witness failed to bind: " + log.name)
                sleep(0.025)
            return "declined" if case == "decline-title" else "title"

        def between():
            if case == "changed-esm":
                fixture_source.write_bytes(original_plugin[:-1] + bytes([original_plugin[-1] ^ 1]))
            elif case == "cancel":
                signal.raise_signal(signal.SIGINT)
            elif case == "exit":
                processes["command"]("quit")
                processes["process"].wait(timeout=30)
            elif case in {"namespace-drift", "vector-drift"}:
                processes["command"](case)
            elif case == "pair-values":
                processes["command"]("clear")

        services = title.Services("simulated", lambda: (SID, current_session()),
                                  begin, select, respond, fake_space, between)
        try:
            yield services, observed
        finally:
            if case == "changed-esm":
                fixture_source.write_bytes(original_plugin)
            # Retire the child first. The independent witness can then report exit code.
            resources.close()
            watcher = processes.get("watcher")
            if watcher is not None and watcher.wait(timeout=30):
                raise RuntimeError("independent owned exit witness did not observe a normal Quit")


CONTROLS = (
    ("direct", "direct", None, None, {}),
    ("corpus", "corpus", None, None, {}),
    ("upper", "upper", None, None, {}),
    ("installed-sfse", "direct", None, None, {}),
    ("source-filtered", "source-filtered", None, None, {}),
    ("source-unreadable", "source-unreadable", None, None, {}),
    ("vector-drift", "direct", None, None, {}),
    ("relative-data", "relative-data", None, None, {}),
    ("namespace-drift", "direct", "pair_namespace_mismatch", None, {}),
    ("namespace-invalid", "namespace-invalid", "namespace_witness_refused", None, {}),
    ("absent-esm", "direct", None, None, {}),
    ("changed-esm", "direct", None, None, {}),
    ("bad-owner", "bad-owner-key", "pndt_key_mismatch", None, {}),
    ("bad-biome-type", "bad-biome-type", "form_type_mismatch", None, {}),
    ("bad-resource-type", "bad-resource-type", "resource_form_type_mismatch", None, {}),
    ("bad-resource-vptr", "bad-resource-vptr", "resource_form_vptr_mismatch", None, {}),
    ("pair-values", "direct", "pair_value_mismatch", None, {}),
    ("map-cross-region", "map-region-crossing", "unreadable_region", None, {}),
    ("volume", "direct", "traversal_budget", None, {"entries": 5}),
    ("journal", "direct", "journal_budget", None, {"journal_bytes": 24 * 1024}),
    ("mapped-drift", "direct", "mapped_image_mismatch", None, {}),
    ("ambiguous-steam", "direct", "steam_attribution_failed", None, {}),
    ("exit", "direct", "process_exited", None, {}),
    ("cancel", "direct", "operator_cancelled", None, {}),
    ("decline-title", "direct", "operator_declined", None, {}),
)


def run(directory):
    directory.mkdir(parents=True, exist_ok=False)
    steam = directory / "fixture-steam"
    steam.mkdir()
    target, build = qualify_census.build_fixture(directory, map_capacity=census.RETAIL_LIMITS["form_capacity"])
    fixture_source = directory / "fixture.esm"
    fixture_sources(fixture_source)
    controls = gate_tests(directory, steam, fixture_source)
    for name, scenario, failure, source_failure, overrides in CONTROLS:
        custody = directory / name
        custody.mkdir()
        source = fixture_source
        paths = authorize(custody, steam, source)
        if name == "absent-esm":
            fixture_source.unlink()
        limits = {**census.RETAIL_LIMITS, **overrides}
        with owned_services(custody, target, steam, scenario, name, fixture_source) as (services, called):
            state = title.acquire(steam, custody, *paths, services=services, limits=limits)
            assert (state["failure"] or [None])[0] == failure, (name, state)
            assert state["source_binding_failure"] == source_failure, (name, state)
            expected_error(lambda: title.acquire(steam, custody, *paths, services=services, limits=limits))
            assert called["begin_calls"] == called["open_calls"] == 1, (name, called)
        if name == "absent-esm":
            fixture_sources(fixture_source)
        details = {key_: state[key_] for key_ in ("failure", "source_binding_failure", "work") if key_ in state}
        receipt = custody / title.RECEIPT
        attempt_sha256 = file_sha256(custody / title.ATTEMPT)
        if receipt.exists():
            report = title.replay_retail(receipt, attempt_sha256=attempt_sha256, services=services)
            header = next(census._load_receipt(receipt))
            dataset = bound_dataset(report, file_sha256(receipt), header["reader_source_sha256"])
            if name in {"direct", "corpus", "upper"}:
                details["fields"] = check_fields(name, dataset, expected_namespace=True, defining_only=True,
                                                native_only=True)
                output = output_bytes(dataset)
                (custody / "portable.json").write_bytes(output)
                details.update(receipt_sha256=file_sha256(receipt), attempt_sha256=attempt_sha256,
                               portable_sha256=file_sha256(custody / "portable.json"))
                if name == "direct":
                    expected_error(lambda: output_bytes(dataset, ceiling=100))
                    expected_error(lambda: title.replay_retail(receipt, attempt_sha256="0" * 64, services=services))
                    raw = receipt.read_bytes()
                    try:
                        receipt.write_bytes(raw[:-90])
                        expected_error(lambda: title.replay_retail(receipt, attempt_sha256=attempt_sha256,
                                                                   services=services))
                    finally:
                        receipt.write_bytes(raw)
            elif name in {"installed-sfse", "source-filtered", "source-unreadable", "vector-drift",
                          "relative-data", "absent-esm", "changed-esm"}:
                assert dataset["acquisition"] == "QUALIFIED" and len(dataset["rows"]) == 4, (name, dataset)
                assert all(len(row["slots"]) == 7 for row in dataset["rows"])
                if name == "source-unreadable":
                    assert dataset["native_source_attribution"]["agreement"] == "INCOMPLETE"
                    assert dataset["native_source_attribution"]["refusals"] == ["unreadable_region"] * 2
            else:
                assert dataset["acquisition"] != "QUALIFIED", (name, dataset)
            details["coverage"] = report["coverage_counts"]
        elif name == "journal":
            partial = receipt.with_name(receipt.name + ".partial")
            assert 0 < partial.stat().st_size <= limits["journal_bytes"]
            details["pending_bytes"] = partial.stat().st_size
        make_receipts(custody, "post", changed=name == "decline-title")
        close = lambda: title.verify_closeout(custody, attempt_sha256=attempt_sha256, services=services)
        if name == "decline-title":
            expected_error(close, "postflight_protection_changed")
        else:
            result = close()
            expected = "RETIRED_PROTECTION_UNCHANGED" if (custody / "exit-witness-result.json").exists() else "EXIT_UNVERIFIED"
            assert result["disposition"] == expected
            details["closeout"] = expected
        controls[name] = details
        print(name, failure or source_failure or "qualified", flush=True)
    manifest = title.candidate_manifest()
    title.write_exclusive(directory / "execution-manifest.json", manifest)
    title.write_exclusive(directory / "qualification.json", {
        "schema": "srr017-retail-flow-qualification-v1", "controls": controls, "build": build,
        "execution_sha256": title.digest_manifest(manifest), "work_sha256": title.digest_manifest(manifest["work"]),
    })


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run")
    args = parser.parse_args()
    if not re.fullmatch(r"[a-zA-Z0-9-]{1,64}", args.run):
        parser.error("use a fresh run name of 1–64 letters, digits or hyphens")
    run(PRIVATE / args.run)


if __name__ == "__main__":
    main()
