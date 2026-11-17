"""Proposed single-use retail title-card command. A real signed approval is required."""

import argparse
from contextlib import nullcontext
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
from time import time_ns

from tools.srr016 import census
from checkpoint import issue, mark
from contract import RETAIL_APPLICABILITY, STRUCTURAL_MODE
from memory import ReadFailure
from observe import JournalFailure
from retail_admission import ProcessMetadata, STEAM_APP, STEAM_APP_BUILD, begin_retail, open_retail
from structural_title import cancellation_signal, operator_response


ROOT = Path(__file__).resolve().parents[2]
COMMAND = ("python", "-E", "-B", "-m", "tools.srr017.retail_title", "observe-title",
           "<steam-root>", "<custody>", "<authorization.json>", "<authorization.json.sig>")
SIGNER = "srr017-maintainer"
SIGN_NAMESPACE = "srr017-retail-title"
TRUST_PATH = Path("C:/Program Files/SRR017/allowed_signers")
SSH_PATH = Path("C:/Windows/System32/OpenSSH/ssh-keygen.exe")
CLAIM = "retail-authorization.used"
RECEIPT = "title.jsonl"
IDENTITY_CONTRACT = {"schema": "srr017-native-formid-identity-v1", "namespace": "native-loaded-plugins",
                     "types": ["PNDT", "BIOM", "RSGD", "IRES"]}
ATTEMPT = "retail-attempt.json"
PROTECTION_SIZE = 2 * 1024 * 1024
AUTH_SIZE = 8192
TRUST_SIZE = 1024
APPROVAL_MAX_NS = 24 * 60 * 60 * 1_000_000_000
HEX_256 = re.compile(r"[0-9a-f]{64}")
SIGNED_FIELDS = {
    "schema", "scope", "approval_id", "purpose", "operator_sid", "steam_session", "steam_root", "custody",
    "source_sha256", "work_sha256", "input_sha256", "trust_sha256", "verifier_sha256", "retail_sha256",
    "pre_environment_sha256", "pre_protection_sha256", "issued_utc_ns", "expires_utc_ns",
}
SOURCES = (
    "tools/srr008/inventory.py", "tools/srr008/preflight.py", "tools/srr008/save_policy.py",
    "tools/srr008/watch_exit.py", "tools/srr013/checkpoint.py", "tools/srr013/contract.py",
    "tools/srr013/memory.py", "tools/srr013/native.py", "tools/srr013/observe.py",
    "tools/srr013/retail_admission.py", "tools/srr013/retail_controller.py",
    "tools/srr013/retail_inputs.py", "tools/srr013/structural_title.py", "tools/srr016/census.py",
    "tools/srr016/compare.py", "tools/srr016/ledger.py", "tools/srr017/export.py", "tools/srr017/namespace.py",
    "tools/srr017/retail_title.py", "tools/srr017/source.py", "tools/srr017/work.py",
)


def demand(condition, code, detail):
    if not condition:
        raise ReadFailure(code, detail)


def digest(data):
    return sha256(data).hexdigest()


def file_bytes(path, ceiling):
    path = Path(path)
    with path.open("rb") as stream:
        before = os.fstat(stream.fileno())
        demand(stat.S_ISREG(before.st_mode) and 0 < before.st_size <= ceiling, "evidence_file_budget",
               "evidence input is not a bounded nonempty file")
        value = stream.read(before.st_size + 1)
        stamp = lambda info: (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns)
        demand(len(value) == before.st_size and stamp(before) == stamp(os.fstat(stream.fileno()))
               == stamp(path.stat()), "evidence_file_changed", "evidence input changed")
    return value


def unique_members(pairs):
    value = {}
    for key, field in pairs:
        demand(key not in value, "duplicate_evidence_member", "evidence JSON has a duplicate key")
        value[key] = field
    return value


def object_from(raw, *, canonical=False):
    try:
        value = json.loads(raw, object_pairs_hook=unique_members)
    except (ValueError, UnicodeError, RecursionError) as error:
        raise ReadFailure("evidence_json", "evidence is not a valid JSON object") from error
    demand(type(value) is dict and (not canonical or raw == census.encode(value) + b"\n"),
           "evidence_json", "evidence JSON is not an object in the required encoding")
    return value


def utc_ns(value):
    try:
        clock = datetime.fromisoformat(value)
    except (TypeError, ValueError) as error:
        raise ReadFailure("evidence_clock", "retained evidence lacks an unambiguous timestamp") from error
    demand(clock.tzinfo is not None, "evidence_clock", "retained evidence timestamp lacks a UTC offset")
    elapsed = clock - datetime(1970, 1, 1, tzinfo=timezone.utc)
    return (elapsed.days * 86_400 + elapsed.seconds) * 1_000_000_000 + elapsed.microseconds * 1000


def journal_hash(path, ceiling):
    digest_ = sha256()
    with path.open("rb") as stream:
        before = os.fstat(stream.fileno())
        left = before.st_size
        demand(0 < left <= ceiling, "evidence_file_budget", "journal exceeds the retained evidence cap")
        while left:
            data = stream.read(min(left, 1024 * 1024))
            demand(bool(data), "evidence_file_changed", "journal shortened while hashing")
            digest_.update(data)
            left -= len(data)
        demand(not stream.read(1) and before.st_size == path.stat().st_size
               and before.st_mtime_ns == path.stat().st_mtime_ns, "evidence_file_changed",
               "journal changed while hashing")
    return digest_.hexdigest()


def write_exclusive(path, value, ceiling=PROTECTION_SIZE):
    raw = census.encode(value) + b"\n"
    demand(len(raw) <= ceiling, "evidence_file_budget", "output evidence exceeded its declared byte ceiling")
    with path.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def existing_local(path, *, directory=False):
    path = Path(path)
    demand(path.is_absolute() and re.fullmatch(r"[a-zA-Z]:", path.drive) and ".." not in path.parts,
           "noncanonical_path", "an absolute local path is required")
    resolved = path.resolve(strict=True)
    demand(resolved == path and (resolved.is_dir() if directory else resolved.is_file()),
           "noncanonical_path", "the path resolves outside its designated location")
    return resolved


def private_directory(path):
    path = existing_local(path, directory=True)
    approval_root = (ROOT / ".local-work").resolve(strict=True)
    demand(path != approval_root and path.is_relative_to(approval_root) and path.drive.upper() in {"C:", "D:"},
           "custody_unverified", "a private run directory inside the checkout custody root is required")
    return path


def candidate_manifest():
    from .work import RETAIL_WORK

    return {
        "schema": "srr017-retail-execution-v1",
        "command": list(COMMAND),
        "retail": RETAIL_APPLICABILITY,
        "source_sha256": {name: digest(file_bytes(ROOT / name, 256 * 1024)) for name in SOURCES},
        "python_sha256": digest(file_bytes(Path(sys.executable), 4 * 1024 * 1024)),
        "census_source_sha256": census.source_identity(),
        "work": RETAIL_WORK,
    }


def digest_manifest(value):
    return digest(census.encode(value))


def validate_signed_fields(data, expected, clock):
    demand(set(data) == SIGNED_FIELDS and data["schema"] == "srr017-title-authorization-v1"
           and data["purpose"] == "one-responsive-title-readonly-pair"
           and isinstance(data["approval_id"], str) and re.fullmatch(r"[0-9a-f]{32}", data["approval_id"]),
           "retail_authorization_format", "authorization lacks the exact signed one-use fields")
    demand(all(data.get(key) == value for key, value in expected.items()), "retail_authorization_mismatch",
           "authorization disagrees with source, work, input, path, operator or protected evidence")
    issued, expires = data["issued_utc_ns"], data["expires_utc_ns"]
    demand(type(issued) is int and type(expires) is int and 0 < issued <= clock < expires
           and expires - issued <= APPROVAL_MAX_NS,
           "retail_authorization_stale", "authorization is stale, premature or has an excessive validity interval")


def verify_sshsig(authority_path, signature, payload, verifier):
    """Verify the exact bytes with the maintained OS OpenSSH executable."""
    trust = file_bytes(authority_path, TRUST_SIZE)
    demand(re.fullmatch(rb'srr017-maintainer namespaces="srr017-retail-title" ssh-ed25519 [A-Za-z0-9+/=]{60,100}\r?\n',
                        trust) is not None,
           "retail_trust_invalid", "the OS trust file must contain one scoped maintainer key")
    signature_bytes = file_bytes(signature, AUTH_SIZE)
    result = subprocess.run(
        [str(verifier), "-Y", "verify", "-f", str(authority_path), "-I", SIGNER, "-n", SIGN_NAMESPACE,
         "-s", str(signature)],
        input=payload, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
    )
    demand(result.returncode == 0 and file_bytes(authority_path, TRUST_SIZE) == trust
           and file_bytes(signature, AUTH_SIZE) == signature_bytes,
           "retail_authorization_signature", "maintainer signature or signed input could not be verified")
    return digest(trust), digest(signature_bytes)


def protect_trust_path():
    """Refuse a trust anchor that the ordinary observer could edit or replace."""
    import ctypes as c
    from ctypes import wintypes as w

    trust = existing_local(TRUST_PATH)
    verifier = existing_local(SSH_PATH)
    kernel = c.WinDLL("kernel32", use_last_error=True)
    create = kernel.CreateFileW
    create.argtypes = (w.LPCWSTR, w.DWORD, w.DWORD, w.LPVOID, w.DWORD, w.DWORD, w.HANDLE)
    create.restype = w.HANDLE
    close = kernel.CloseHandle
    close.argtypes, close.restype = (w.HANDLE,), w.BOOL
    invalid = c.c_void_p(-1).value
    # DELETE, WRITE_DAC, WRITE_OWNER, data/write-attributes and (for directories) DELETE_CHILD.
    # Test each independently. A denial of a combined mask would not rule out partial mutation rights.
    for item in (trust, trust.parent, trust.parent.parent, verifier, verifier.parent, verifier.parent.parent):
        demand(not item.is_symlink(), "retail_trust_invalid", "the trust or verifier path is a symlink")
        for access in (0x10000, 0x40000, 0x80000, 2, 4, 0x100, *((0x40,) if item.is_dir() else ())):
            handle = create(str(item), access, 7, None, 3, 0x02000000 if item.is_dir() else 0, None)
            if handle not in (None, invalid):
                close(handle)
                raise ReadFailure("retail_trust_writable", "the observer could modify the trust or verifier chain")
            demand(c.get_last_error() in (5, 1314), "retail_trust_unverified",
                   "the observer's write access to the trust chain could not be ruled out")
    return trust, verifier


def real_operator():
    import ctypes as c
    from ctypes import wintypes as w

    api = ProcessMetadata()
    pid, process = os.getpid(), api.GetCurrentProcess()
    session = api.session(pid)
    api.verify_account(process, pid, session)
    advapi = c.WinDLL("advapi32", use_last_error=True)
    kernel = c.WinDLL("kernel32", use_last_error=True)
    convert = advapi.ConvertSidToStringSidW
    convert.argtypes, convert.restype = (c.c_void_p, c.POINTER(w.LPWSTR)), w.BOOL
    free = kernel.LocalFree
    free.argtypes, free.restype = (w.HLOCAL,), w.HLOCAL
    with api.token(process) as token:
        user = api.token_field(token, 1)
        destination = w.LPWSTR()
        demand(convert(c.c_void_p.from_buffer(user).value, c.byref(destination)),
               "operator_sid_unverified", "could not obtain the native observer SID")
        try:
            return destination.value, session
        finally:
            free(c.cast(destination, w.HLOCAL))


def preflight_receipts(directory, phase):
    reports, pins = {}, {}
    for mode in ("environment", "protection"):
        path = existing_local(directory / f"{phase}-{mode}" / "receipt.json")
        raw = file_bytes(path, PROTECTION_SIZE)
        report = object_from(raw)
        demand(report.get("schema") == "srr-save-environment-receipt/1" and report.get("mode") == mode
               and report.get("ok") is True, "preflight_refused", "protection or environment receipt failed")
        reports[mode], pins[f"{phase}_{mode}_sha256"] = report, digest(raw)
    return reports, pins


def check_protection(report):
    for namespace, count in (("documents", 98), ("remote", 95)):
        group = report[namespace]
        pairs = group["pairs"]
        demand(group["ok"] is True and group["expected_protected"] == group["matched"] == len(pairs) == count
               and group["counts"].get("PROTECTED") == count and not group["counts"].get("UNCLASSIFIED")
               and not group["other"] and len({pair["relative"].casefold() for pair in pairs}) == count,
               "protection_refused", "protected pair count, unexplained entries or backup identities disagree")
        for pair in pairs:
            original, backup = pair["original"], pair["candidate"]
            demand(pair["match"] is True and original["size"] > 0 and original["size"] == backup["size"]
                   and HEX_256.fullmatch(original["sha256"]) and original["sha256"] == backup["sha256"]
                   and (original["volume"], original["file_id"]) != (backup["volume"], backup["file_id"]),
                   "protection_refused", "a protected original/backup pair is not independently matched")
    names = report["designations"]
    protected = {pair["relative"] for pair in report["documents"]["pairs"]}
    demand(len(names) == 2 and all(value is True and name in protected for name, value in names.items()),
           "protection_refused", "both designated save identities must be protected")


def check_environment(report, image_sha256):
    demand(report["retail_executable"]["sha256"] == image_sha256
           and report["manifest_fields"] == {"appid": str(STEAM_APP), "buildid": str(STEAM_APP_BUILD),
                                             "StateFlags": "4", "installdir": "Starfield"}
           and report["cloud_flag"] == report["overlay_flag"] == "0"
           and report["configured_save_path_agrees"] is True and report["sfse_loader"] is False,
           "environment_refused", "the pinned environment, disabled Cloud/overlay or launch path disagrees")


def available_space():
    import ctypes as c
    from ctypes import wintypes as w

    from .work import MINIMUM_FREE_BYTES, WRITE_RESERVE_BYTES

    result = {}
    api = c.WinDLL("kernel32", use_last_error=True).GetDiskFreeSpaceExW
    api.argtypes = (w.LPCWSTR, c.POINTER(c.c_ulonglong), c.c_void_p, c.c_void_p)
    api.restype = w.BOOL
    for drive in ("C:", "D:"):
        value = c.c_ulonglong()
        demand(api(drive + "\\", c.byref(value), None, None)
               and value.value >= MINIMUM_FREE_BYTES + WRITE_RESERVE_BYTES,
               "disk_reserve", "the reviewed caller-available disk floor and full write reserve are required")
        result[drive] = value.value
    return result


def approval_files(custody):
    return tuple(existing_local(custody / name)
                 for name in ("authorization.json", "authorization.json.sig"))


@dataclass(frozen=True)
class Services:
    target_kind: str
    operator: object
    trust: object
    begin: object
    open: object
    prompt: object
    space: object
    between: object | None = None

    @property
    def scope(self):
        return census.RETAIL_SCOPE if self.target_kind == "retail" else census.RETAIL_FIXTURE_SCOPE


REAL = Services("retail", real_operator, protect_trust_path, begin_retail, open_retail,
                operator_response, available_space)


def _verify_approval(steam_root, directory, paths, services, *, replay_clock=None):
    approval, signature = approval_files(directory)
    demand(tuple(Path(x) for x in paths) == (approval, signature),
           "retail_authorization_location", "approval evidence must use the fixed private custody paths")
    raw = file_bytes(approval, AUTH_SIZE)
    value = object_from(raw, canonical=True)
    trust, verifier = services.trust()
    verifier_sha256 = digest(file_bytes(verifier, 4 * 1024 * 1024))
    trust_sha256, signature_sha256 = verify_sshsig(trust, signature, raw, verifier)
    manifest = candidate_manifest()
    preflight, pins = preflight_receipts(directory, "pre")
    if replay_clock is None:
        operator_sid, session = services.operator()
    else:
        operator_sid, session = value.get("operator_sid"), value.get("steam_session")
    demand(type(session) is int and session > 0 and isinstance(operator_sid, str)
           and re.fullmatch(r"S-1-\d+(?:-\d+)+", operator_sid),
           "operator_sid_unverified", "the authorization did not bind a native operator and session")
    expected = {
        "scope": services.scope, "operator_sid": operator_sid, "steam_session": session,
        "steam_root": str(steam_root), "custody": str(directory),
        "source_sha256": digest_manifest(manifest), "work_sha256": digest_manifest(manifest["work"]),
        "input_sha256": digest_manifest(IDENTITY_CONTRACT), "retail_sha256": RETAIL_APPLICABILITY["sha256"],
        "trust_sha256": trust_sha256, "verifier_sha256": verifier_sha256, **pins,
    }
    clock = time_ns() if replay_clock is None else replay_clock
    validate_signed_fields(value, expected, clock)
    demand(all(0 <= clock - utc_ns(receipt["utc"]) <= APPROVAL_MAX_NS for receipt in preflight.values()),
           "preflight_stale", "signed preflight receipts must precede reservation and be current")
    check_environment(preflight["environment"], expected["retail_sha256"])
    check_protection(preflight["protection"])
    claim = {**expected, "approval_id": value["approval_id"], "authorization_sha256": digest(raw),
             "signature_sha256": signature_sha256, "claimed_utc_ns": clock}
    return claim, value["expires_utc_ns"]


def check_exit_bound(directory, identity, image):
    evidence = object_from(file_bytes(existing_local(directory / "exit-witness-bound.json"), AUTH_SIZE))
    target, observed = evidence["target"], evidence["image"]
    token = f'{identity["image_sha256"]}-{identity["pid"]}-{identity["creation"]}'
    demand(evidence["run"] == token and evidence["access_mask"] == 0x101000
           and target["pid"] == identity["pid"] and target["creation_filetime"] == identity["creation"]
           and Path(target["path"]) == image and target["process_machine"] == 0 and target["native_machine"] == 0x8664
           and observed["sha256"] == identity["image_sha256"],
           "exit_witness_unbound", "separate exit watcher does not identify the exact admitted process")
    return token


def raw_source_namespace(collection):
    witness = collection.get("source_witness") or {}
    return witness.get("namespace")


def _bind_pair_sources(report, target_kind):
    from .source import bind_native_namespace

    collections = report["collections"]
    namespaces = [raw_source_namespace(item) for item in collections]
    demand(len(collections) == 2 and all(item["coverage_verified"] for item in collections)
           and all(isinstance(namespace, dict) and namespace.get("compiled") for namespace in namespaces),
           "source_pair_unavailable", "identity binding needs two complete native namespace passes")
    authority = "RETAIL_NATIVE_WITNESS" if target_kind == "retail" else "OWNED_DISPOSABLE"
    bindings = [bind_native_namespace(namespace, authority=authority) for namespace in namespaces]
    demand(bindings[0].provenance == bindings[1].provenance,
           "source_pair_changed", "the loaded native namespace bindings differ")


def poll_no_cancel(cancelled):
    demand(not cancelled(), "operator_cancelled", "operator cancelled before the acquisition concluded")


def meter_process_census(api, initial, maximum):
    count = {"calls": initial}
    census_ = api.census

    def counted(names):
        demand(count["calls"] < maximum, "process_census_budget", "Windows process census limit exceeded")
        count["calls"] += 1
        return census_(names)

    api.census = counted
    return count


def acquire(
    steam, custody, authorization, signature, *,
    services=REAL, limits=None,
):
    """Run the exact integrated command. Only its private services are substituted in owned tests."""
    from .source import SourceIdentityError
    from .work import ImageDigestMeter, RETAIL_WORK, meter_backend

    demand(sys.flags.ignore_environment and sys.dont_write_bytecode and not sys.flags.optimize,
           "observer_flags", "use the reviewed -E -B invocation with optimizations disabled")
    demand("__COMPAT_LAYER" not in os.environ, "compatibility_flags", "inherited compatibility flags are disallowed")
    directory = private_directory(custody)
    steam_root = existing_local(steam, directory=True)
    limits = RETAIL_WORK["census"] if limits is None else limits
    demand(services.target_kind == "simulated" or limits == RETAIL_WORK["census"], "retail_limits",
           "the retail invocation fixes the exact reviewed census work limits")
    authority, expires = _verify_approval(
        steam_root, directory, (authorization, signature), services)
    works = services.space()
    write_exclusive(directory / CLAIM, authority, AUTH_SIZE)
    path = directory / RECEIPT
    state = {"schema": "srr017-retail-attempt-v1", "authorization_sha256": authority["authorization_sha256"],
             "pre_free_bytes": works, "failure": None, "source_binding_failure": None}
    try:
        with cancellation_signal() as cancelled:
            hashes = ImageDigestMeter(cancelled)
            poll_no_cancel(cancelled)
            demand(time_ns() < expires, "retail_authorization_stale", "authorization expired before Steam admission")
            with services.begin(steam_root, digest_file=hashes) as baseline:
                demand(baseline.session == authority["steam_session"], "steam_session_unverified",
                       "authenticated Steam session disagrees with signed approval")
                actual, caps = meter_backend(baseline.api, limits)
                process_censuses = meter_process_census(baseline.api, 2 if services.target_kind == "retail" else 1,
                                                         RETAIL_WORK["steam_census_calls_max"])
                demand(services.prompt("Baseline held. Launch once through Steam. At the responsive title card type launched: ")
                       == "launched", "operator_declined", "operator declined the designated launch or phase")
                poll_no_cancel(cancelled)
                demand(time_ns() < expires, "retail_authorization_stale", "authorization expired before game admission")
                with services.open(baseline, digest_file=hashes) as reader:
                    bound = reader.identity()
                    image = reader.path
                    token = f'{bound["image_sha256"]}-{bound["pid"]}-{bound["creation"]}'
                    phase = {"epoch": token, "image": str(image)}
                    write_exclusive(directory / "target-bound.json", phase, AUTH_SIZE)
                    state["target_bound"] = phase
                    print(f"Independent exit witness token: {token}\nExecutable: {image}", flush=True)
                    attempt = issue(directory, STRUCTURAL_MODE)
                    demand(services.prompt("Bind the independent exit witness. Confirm the responsive held title by typing title: ")
                           == "title", "operator_declined", "operator declined the responsive title marker")
                    check_exit_bound(directory, bound, image)
                    poll_no_cancel(cancelled)
                    demand(time_ns() < expires, "retail_authorization_stale", "authorization expired before marker")
                    marker = mark(attempt, bound, "title")
                    state["epoch"] = token
                    binding = {"target_kind": services.target_kind, "authority": authority, "attempt": attempt,
                               "marker": marker, "namespace_profile": census.RETAIL_NAMESPACE_PROFILE,
                               "identity_contract_sha256": digest_manifest(IDENTITY_CONTRACT),
                               "exit_witness_bound_sha256": digest(file_bytes(
                                   directory / "exit-witness-bound.json", AUTH_SIZE))}
                    report = census.capture(
                        path, directory, nullcontext(reader), binding, {}, limits=limits, cancelled=cancelled,
                        retail_authority=authority, between=services.between,
                    )
                    if report["failure"] is None:
                        try:
                            _bind_pair_sources(report, services.target_kind)
                            close = reader.identity()
                            demand(close == bound, "epoch_mismatch", "authenticated epoch changed before source closeout")
                            state["source_close_identity"] = close
                        except (ReadFailure, SourceIdentityError) as error:
                            state["source_binding_failure"] = error.code
                    else:
                        state["failure"] = report["failure"]
                state["work"] = {"backend": actual, "caps": caps, "image_hashes": hashes.counts, "image_bytes": hashes.bytes}
                state["work"]["process_censuses"] = process_censuses["calls"]
            state["post_free_bytes"] = services.space()
    except (ReadFailure, JournalFailure, SourceIdentityError) as error:
        state["failure"] = [error.code, str(error)]
    except (KeyError, ValueError, OSError, TypeError) as error:
        state["failure"] = ["admission_or_evidence_error", str(error)]
    finally:
        if path.exists():
            state["receipt_sha256"] = journal_hash(path, limits["journal_bytes"])
        write_exclusive(directory / ATTEMPT, state)
    return state


def replay_retail(path, *, attempt_sha256, services=REAL):
    path = existing_local(path)
    directory = private_directory(path.parent)
    demand(path == directory / RECEIPT, "retail_receipt_location", "use the named receipt in original custody")
    claim = object_from(file_bytes(existing_local(directory / CLAIM), AUTH_SIZE), canonical=True)
    clock = claim.get("claimed_utc_ns")
    demand(type(clock) is int and clock > 0, "retail_approval_clock", "claim has an invalid authorization clock")
    authority, expires = _verify_approval(Path(claim["steam_root"]), directory,
                                                   approval_files(directory), services, replay_clock=clock)
    demand(authority == claim, "retail_replay_claim", "independent signed authorization claim disagrees")
    report = census.replay(path, retail_authority=authority)
    header = next(census._load_receipt(path))
    marker = header["binding"]["marker"]
    demand(authority["claimed_utc_ns"] <= marker["utc_ns"] < expires, "retail_replay_marker",
           "the held title declaration falls outside its approval window")
    state = checked_attempt(directory, attempt_sha256, authority)
    demand(state["receipt_sha256"] == journal_hash(path, census.RETAIL_LIMITS["journal_bytes"]),
           "retail_replay_attempt", "attempt closeout does not bind its signed approval")
    source_failure = state["source_binding_failure"]
    if report["failure"] is None and not state["failure"] and source_failure is None:
        identity = report["identity_brackets"][0][0]
        phase = state["target_bound"]
        token = check_exit_bound(directory, identity, Path(phase["image"]))
        demand(digest(file_bytes(directory / "exit-witness-bound.json", AUTH_SIZE))
               == header["binding"]["exit_witness_bound_sha256"] and token == phase["epoch"]
               and header["binding"]["identity_contract_sha256"] == digest_manifest(IDENTITY_CONTRACT)
               and state["source_close_identity"] == identity,
               "retail_replay_identity", "native identity contract or epoch closeout did not reconcile")
        _bind_pair_sources(report, services.target_kind)
    else:
        report["source_binding_failure"] = source_failure or "retail_attempt_incomplete"
    return report


def checked_attempt(directory, attempt_sha256, authority):
    state_bytes = file_bytes(existing_local(directory / ATTEMPT), PROTECTION_SIZE)
    demand(digest(state_bytes) == attempt_sha256, "retail_replay_attempt", "attempt closeout hash disagrees")
    state = object_from(state_bytes, canonical=True)
    demand(state["authorization_sha256"] == authority["authorization_sha256"],
           "retail_replay_attempt", "attempt closeout does not bind its signed approval")
    return state


def exit_details(directory, state, target_kind):
    phase = object_from(file_bytes(existing_local(directory / "target-bound.json"), AUTH_SIZE), canonical=True)
    demand(phase == state.get("target_bound"), "exit_witness_refused", "retained target differs from the pinned attempt")
    token = phase["epoch"]
    match = re.fullmatch(r"([0-9a-f]{64})-([1-9][0-9]*)-([1-9][0-9]*)", token)
    demand(match is not None and (target_kind == "simulated" or match[1] == RETAIL_APPLICABILITY["sha256"]),
           "exit_witness_refused", "retained target has an invalid configured identity")
    identity = {"image_sha256": match[1], "pid": int(match[2]), "creation": int(match[3])}
    check_exit_bound(directory, identity, Path(phase["image"]))
    exit_result = object_from(file_bytes(existing_local(directory / "exit-witness-result.json"), AUTH_SIZE))
    demand(exit_result["run"] == token and exit_result["pid"] == identity["pid"]
           and exit_result["process_birth"] == identity["creation"] and exit_result["signaled"] is True
           and exit_result["exit_code"] == 0, "exit_witness_refused", "independent exit witness missed normal retirement")
    return token, utc_ns(exit_result["utc"])


def verify_closeout(directory, *, attempt_sha256, services=REAL):
    directory = private_directory(directory)
    claim = object_from(file_bytes(existing_local(directory / CLAIM), AUTH_SIZE), canonical=True)
    authority, _ = _verify_approval(Path(claim["steam_root"]), directory, approval_files(directory),
                                       services, replay_clock=claim["claimed_utc_ns"])
    demand(authority == claim, "retail_replay_claim", "independent signed authorization claim disagrees")
    state = checked_attempt(directory, attempt_sha256, authority)
    error = None
    try:
        token, exit_utc = exit_details(directory, state, services.target_kind)
    except (ReadFailure, OSError, KeyError, TypeError, ValueError) as problem:
        error = getattr(problem, "code", "exit_witness_unavailable")
        token, exit_utc = None, authority["claimed_utc_ns"]

    pre, _ = preflight_receipts(directory, "pre")
    post, hashes = preflight_receipts(directory, "post")
    demand(all(utc_ns(receipt["utc"]) >= exit_utc for receipt in post.values()),
           "postflight_before_exit", "postflight receipts precede the required independent boundary")
    check_protection(post["protection"])
    check_environment(post["environment"], RETAIL_APPLICABILITY["sha256"])
    for field in ("documents", "remote", "designations", "backup_path", "backup_entry_count", "policy_file_sha256"):
        demand(pre["protection"][field] == post["protection"][field], "postflight_protection_changed",
               "protected or transient save inventories differ")
    for field in ("retail_executable", "manifest_fields", "cloud_flag", "overlay_flag", "configured_save_paths"):
        demand(pre["environment"][field] == post["environment"][field], "postflight_environment_changed",
               "material launch or protection settings changed")
    value = {"epoch": token, "disposition": "RETIRED_PROTECTION_UNCHANGED" if error is None else "EXIT_UNVERIFIED",
             "protection": "UNCHANGED", "exit_refusal": error, **hashes}
    write_exclusive(directory / "retail-closeout.json", value, AUTH_SIZE)
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("execution-manifest", help="show the exact source, work and invocation offline")
    observe = commands.add_parser("observe-title", help="use one separately signed maintainer approval")
    for field in ("steam", "custody", "authorization", "signature"):
        observe.add_argument(field, type=Path)
    replay = commands.add_parser("replay-retail")
    replay.add_argument("path", type=Path)
    replay.add_argument("--attempt-sha256", required=True)
    close = commands.add_parser("verify-closeout")
    close.add_argument("path", type=Path)
    close.add_argument("--attempt-sha256", required=True)
    args = parser.parse_args()
    try:
        if args.command == "execution-manifest":
            manifest = candidate_manifest()
            result = {"manifest": manifest, "sha256": digest_manifest(manifest)}
        elif args.command == "observe-title":
            result = acquire(args.steam, args.custody, args.authorization, args.signature)
            attempt_hash = digest(file_bytes(args.custody / ATTEMPT, PROTECTION_SIZE))
            result = {"failure": result["failure"], "source_binding_failure": result["source_binding_failure"],
                      "attempt_sha256": attempt_hash, "receipt_sha256": result.get("receipt_sha256")}
        elif args.command == "replay-retail":
            replayed = replay_retail(args.path, attempt_sha256=args.attempt_sha256)
            result = {"failure": replayed["failure"], "source_binding_failure": replayed.get("source_binding_failure"),
                      "coverage": replayed["coverage_counts"]}
        else:
            closed = verify_closeout(args.path, attempt_sha256=args.attempt_sha256)
            result = {"closeout": closed["disposition"], "failure": closed["exit_refusal"]}
    except (ReadFailure, JournalFailure, OSError, KeyError, TypeError, ValueError) as error:
        print(f"Refused: {error}", file=sys.stderr)
        return 1
    print(census.encode(result).decode("ascii"))
    return bool(result.get("failure") or result.get("source_binding_failure"))


if __name__ == "__main__":
    raise SystemExit(main())
