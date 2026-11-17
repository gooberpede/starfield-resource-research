"""Qualify single-use title admission with an owned SRR-016 fixture."""

from hashlib import sha256
import json
import os
from pathlib import Path

from tools.srr016.census import (
    FIXTURE_NAME, OWNED_EXTENDED_LIMITS, OWNED_NAMESPACE_PROFILE, PRIOR_OWNED_SOURCE_SHA256,
    _checked_limits, _load_receipt, capture, encode, replay,
    source_identity as census_source_identity,
)
from tools.srr016.qualify_census import (
    fixture_remap, measure_backend, simulated_append, simulated_baseline,
)
from build_fixture import file_digest
from checkpoint import issue, mark
from contract import STRUCTURAL_MODE
from memory import disk_profile, epoch
from retail_admission import open_simulated


ROOT = Path(__file__).resolve().parents[2]
CLAIM = "srr017-owned-title.used"
SCOPE = "srr017-owned-title"
PRIOR_OWNED_MANIFEST_SHA256 = "167ac0480ec392c1dbc00291836380a359569f5a7226c1b6d4401b8cb96b8c32"
LIMITS = OWNED_EXTENDED_LIMITS
SOURCES = (
    "tools/srr008/inventory.py",
    "tools/srr008/preflight.py",
    "tools/srr008/save_policy.py",
    "tools/srr008/watch_exit.py",
    "tools/srr013/build_fixture.py",
    "tools/srr013/qualify.py",
    "tools/srr013/qualify_retail.py",
    "tools/srr013/retail_controller.py",
    "tools/srr013/retail_inputs.py",
    "tools/srr016/census_fixture.c",
    "tools/srr016/qualify_census.py",
    "tools/srr017/qualify_title.py",
    "tools/srr017/title.py",
)


def digest(value):
    return sha256(encode(value)).hexdigest()


def source_manifest():
    return {
        "schema": "srr017-owned-title-source-v1",
        "census_sha256": census_source_identity(),
        "files": {name: sha256((ROOT / name).read_bytes()).hexdigest() for name in SOURCES},
    }


def private_directory(directory):
    directory = Path(directory).resolve(strict=True)
    private_root = (ROOT / ".local-work").resolve(strict=True)
    if not directory.is_dir() or not directory.is_relative_to(private_root) or directory == private_root:
        raise ValueError("owned title evidence requires a private run directory")
    return directory


def checked_profile(image_sha256, limits):
    limits = _checked_limits(limits)
    return {
        "scope": SCOPE,
        "custody": None,
        "source_sha256": digest(source_manifest()),
        "work_sha256": digest(limits),
        "input_sha256": digest({"fixture_sha256": image_sha256, "remap": fixture_remap()}),
    }


def write_exclusive(path, value):
    with path.open("xb") as stream:
        stream.write(encode(value) + b"\n")
        stream.flush()
        os.fsync(stream.fileno())


def read_bounded(path):
    with path.open("rb") as stream:
        raw = stream.read(8193)
    if len(raw) > 8192:
        raise ValueError("owned authorization evidence exceeds its byte ceiling")
    value = json.loads(raw)
    if not isinstance(value, dict) or raw != encode(value) + b"\n":
        raise ValueError("owned authorization evidence must use canonical JSON")
    return value, sha256(raw).hexdigest()


def reserve_owned(directory, authorization, image_sha256, limits):
    """Consume only an owned-test authorization in a canonical private directory."""
    directory = private_directory(directory)
    authorization = Path(authorization).resolve(strict=True)
    if authorization != directory / "authorization.json":
        raise ValueError("authorization must be the designated separate file in the run directory")
    expected = checked_profile(image_sha256, limits)
    expected["custody"] = str(directory)
    value, auth_sha256 = read_bounded(authorization)
    reference = value.get("approval_reference")
    if (not isinstance(reference, str) or not reference.startswith("owned-fixture:") or
            not reference.removeprefix("owned-fixture:").strip() or
            value != {**expected, "approval_reference": reference}):
        raise ValueError("owned authorization disagrees with source, work, input, custody or scope")
    claim = {**expected, "authorization_sha256": auth_sha256}
    write_exclusive(directory / CLAIM, claim)
    return claim


def owned_title(directory, authorization, target, image_sha256, launch, limits, *, cancelled=None,
                between=None):
    """Reuse the metered Windows acquisition path after an owned-only one-use claim."""
    directory = private_directory(directory)
    target = Path(target).resolve(strict=True)
    if target.name.casefold() != FIXTURE_NAME or target.parent != directory.parent:
        raise ValueError("only the designated fixture built for this qualification run is admitted")
    if file_digest(target) != image_sha256:
        raise ValueError("owned fixture bytes differ from the reviewed input")
    with target.open("rb") as stream:
        disk_profile(stream)
    authority = reserve_owned(directory, authorization, image_sha256, limits)
    log = directory / "steam.log"
    with log.open("xb") as stream:
        stream.write(b"owned fixture tracking baseline\n")
    baseline = simulated_baseline(target, image_sha256, log)
    actual, caps = measure_backend(baseline.api, limits)
    path = directory / "title.jsonl"
    with launch(target) as (process, command):
        simulated_append(log, process.pid, target)
        pid, creation = epoch(baseline.api, int(process._handle))
        attempt = issue(directory, STRUCTURAL_MODE)
        marker = mark(attempt, {"pid": pid, "creation": creation}, "title")
        binding = {"target_kind": "simulated", "authority": authority, "attempt": attempt, "marker": marker,
                   "namespace_profile": OWNED_NAMESPACE_PROFILE}
        report = capture(path, directory, open_simulated(baseline, process), binding, fixture_remap(),
                         limits=limits, cancelled=cancelled, between=(lambda: between(command)) if between else None)
        truth = command("truth") if report["failure"] is None else None
    return report, truth, actual, caps


def replay_owned(path):
    """Check replay and its independently retained owned admission claim."""
    path = Path(path).resolve(strict=True)
    directory = private_directory(path.parent)
    before = file_digest(path)
    report = replay(path)
    header = next(_load_receipt(path))
    claim, _ = read_bounded(directory / CLAIM)
    authorization, authorization_sha256 = read_bounded(directory / "authorization.json")
    expected_source = (PRIOR_OWNED_MANIFEST_SHA256
                       if header["reader_source_sha256"] == PRIOR_OWNED_SOURCE_SHA256
                       else digest(source_manifest()))
    if (header["binding"].get("authority") != claim or claim.get("scope") != SCOPE or
            header["binding"].get("namespace_profile") != OWNED_NAMESPACE_PROFILE or
            claim.get("source_sha256") != expected_source or claim.get("custody") != str(directory) or
            claim.get("work_sha256") != digest(header["limits"]) or
            claim.get("authorization_sha256") != authorization_sha256 or
            {key: value for key, value in authorization.items() if key != "approval_reference"} !=
            {key: value for key, value in claim.items() if key != "authorization_sha256"}):
        raise ValueError("replayed binding disagrees with its owned admission evidence")
    image = report["observation"]["target_image_sha256"]
    if image is not None and claim.get("input_sha256") != digest({"fixture_sha256": image, "remap": header["remap"]}):
        raise ValueError("replayed input disagrees with its owned admission evidence")
    if before != file_digest(path):
        raise ValueError("owned title receipt changed during review")
    return report
