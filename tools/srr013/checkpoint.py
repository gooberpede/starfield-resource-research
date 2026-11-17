"""Bind one operator report to an authenticated process epoch and attempt."""

import os
from hashlib import sha256
from pathlib import Path
import re
from secrets import token_hex
from time import monotonic_ns, time_ns

from contract import CHECKPOINTS, MODES, RETAIL_APPLICABILITY, STRUCTURAL_MODE
from memory import ReadFailure
from retail_admission import FILETIME_UNIX_EPOCH, LOG_TAIL_BYTES, MAX_LOG_APPEND, RETAIL_PROFILE, SIMULATED_PROFILE

MARKER_MAX_AGE_NS = 30_000_000_000
CLOCK_TOLERANCE_NS = 2_000_000_000
TARGET_PROFILES = {"simulated": SIMULATED_PROFILE, "retail": RETAIL_PROFILE}


def _issued_bytes(attempt):
    text = f"{attempt['issued_ns']} {attempt['issued_utc_ns']}"
    if attempt.get("mode") is not None:
        text += f" {attempt['mode']}"
    return (text + "\n").encode("ascii")


def issue(directory, mode=None):
    """Make an attempt token before the marker. Claim it once before acquisition."""
    directory = Path(directory).resolve(strict=True)
    attempt = {"token": token_hex(16), "issued_ns": monotonic_ns(), "issued_utc_ns": time_ns()}
    if mode is not None:
        require(mode in MODES, "marker_mode", "unknown observation mode")
        attempt["mode"] = mode
    path = directory / f"{attempt['token']}.issued"
    with path.open("xb") as stream:
        stream.write(_issued_bytes(attempt))
        stream.flush()
        os.fsync(stream.fileno())
    return attempt


def mark(attempt, identity, label):
    """Record the caller's explicit responsiveness declaration as operator metadata."""
    marker = {"token": attempt["token"], "pid": identity["pid"], "creation": identity["creation"],
              "label": label, "mono_ns": monotonic_ns(), "utc_ns": time_ns()}
    if "mode" in attempt:
        marker["mode"] = attempt["mode"]
    return marker


def require(predicate, code, detail):
    if not predicate:
        raise ReadFailure(code, detail)


def token_valid(token):
    return isinstance(token, str) and re.fullmatch(r"[0-9a-f]{32}", token) is not None


def claim(directory, attempt):
    require(token_valid(attempt.get("token")), "marker_token", "attempt token is invalid")
    directory = Path(directory).resolve(strict=True)
    stem = attempt["token"]
    issued = directory / f"{stem}.issued"
    expected = _issued_bytes(attempt)
    try:
        with issued.open("rb") as stream:
            require(stream.read(128) == expected, "marker_token", "attempt issuance receipt disagrees")
        with (directory / f"{stem}.used").open("xb") as stream:
            stream.write(expected)
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError as error:
        raise ReadFailure("marker_duplicate", "attempt token has already been consumed") from error
    except FileNotFoundError as error:
        raise ReadFailure("marker_token", "attempt token was not issued in this custody") from error


def validate_marker(binding, label, start_ns, start_utc_ns, mode=None):
    attempt, marker = binding["attempt"], binding["marker"]
    require(label in CHECKPOINTS and marker.get("label") == label,
            "marker_label", "unknown or mismatched operator declaration")
    require(token_valid(attempt.get("token")) and marker.get("token") == attempt["token"],
            "marker_token", "operator token disagrees with issued attempt")
    require(attempt.get("mode") == marker.get("mode") == mode,
            "marker_mode", "operator declaration and issued mode disagree")
    require(all(type(marker.get(field)) is int and marker[field] > 0 for field in ("pid", "creation")),
            "marker_epoch", "operator marker has no valid process epoch")
    issued, confirmed = attempt.get("issued_ns"), marker.get("mono_ns")
    issued_utc, confirmed_utc = attempt.get("issued_utc_ns"), marker.get("utc_ns")
    require(all(type(value) is int for value in (issued, confirmed, issued_utc, confirmed_utc))
            and 0 < issued <= confirmed <= start_ns and 0 < issued_utc <= confirmed_utc <= start_utc_ns,
            "marker_order", "issuance, operator confirmation and acquisition are out of order")
    require(start_ns - confirmed <= MARKER_MAX_AGE_NS, "marker_stale", "operator confirmation expired")
    require(abs((start_utc_ns - confirmed_utc) - (start_ns - confirmed)) <= CLOCK_TOLERANCE_NS
            and abs((confirmed_utc - issued_utc) - (confirmed - issued)) <= CLOCK_TOLERANCE_NS,
            "marker_clock", "wall and monotonic intervals disagree")


def validate_capture_marker(binding, label, start_ns, start_utc_ns, mode=None, *, historical=False):
    """Keep the freshness check at operator intake before acquisition begins."""
    if historical:
        validate_marker(binding, label, start_ns, start_utc_ns, mode)
        return
    intake = binding.get("marker_intake")
    require(isinstance(intake, dict) and type(intake.get("mono_ns")) is int
            and type(intake.get("utc_ns")) is int and type(start_utc_ns) is int
            and 0 < intake["mono_ns"] <= start_ns and start_utc_ns > 0,
            "marker_order", "approved operator intake must precede acquisition")
    validate_marker(binding, label, intake["mono_ns"], intake["utc_ns"], mode)


def validate_identity(binding, identity):
    marker = binding["marker"]
    require(identity.get("profile") == TARGET_PROFILES.get(binding.get("target_kind"))
            and binding.get("target_kind") in TARGET_PROFILES,
            "admission_profile", "identity does not match the admitted acquisition profile")
    if binding["target_kind"] == "retail":
        authority = binding.get("authority", {})
        require(marker.get("mode") == STRUCTURAL_MODE and marker["label"] == "title"
                and identity.get("image_sha256") == RETAIL_APPLICABILITY["sha256"]
                and authority.get("scope") == "srr013-structural-title"
                and all(isinstance(authority.get(key), str) and re.fullmatch(r"[0-9a-f]{64}", authority[key])
                        for key in ("source_sha256", "authorization_sha256")),
                "retail_authorization_required", "retail receipt is outside the authorized title-only structural profile")
    require((identity.get("pid"), identity.get("creation")) == (marker["pid"], marker["creation"]),
            "marker_epoch", "operator marker belongs to a different process epoch")
    created_utc_ns = (marker["creation"] - FILETIME_UNIX_EPOCH) * 100
    require(marker["utc_ns"] >= created_utc_ns,
            "marker_before_epoch", "operator confirmation predates process creation")
    proof, source = binding.get("steam_log", {}), identity.get("attribution", {})
    try:
        tail_hex, append_hex = proof["baseline_tail"], proof["append"]
        require(len(tail_hex) <= 2 * LOG_TAIL_BYTES and len(append_hex) <= 2 * MAX_LOG_APPEND,
                "steam_witness_mismatch", "Steam witness exceeds retained bounds")
        tail, append = bytes.fromhex(tail_hex), bytes.fromhex(append_hex)
        line = source["tracking_line"].encode("ascii")
        offset = source["tracking_offset"] - source["baseline_size"]
        require(len(tail) == min(source["baseline_size"], LOG_TAIL_BYTES) and tail.endswith(b"\n")
                and append.endswith(b"\n") and line.endswith(b"\n") and offset >= 0
                and (offset == 0 or append[offset - 1:offset] == b"\n")
                and append[offset:offset + len(line)] == line
                and sha256(tail).hexdigest() == source["baseline_tail_sha256"]
                and sha256(append).hexdigest() == source["admission_append_sha256"]
                and sha256(line).hexdigest() == source["tracking_sha256"],
                "steam_witness_mismatch", "Steam receipt does not match the retained admission witness")
    except (KeyError, TypeError, AttributeError, ValueError) as error:
        raise ReadFailure("steam_witness_mismatch", "Steam receipt is missing or malformed") from error
