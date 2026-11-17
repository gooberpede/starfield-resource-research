"""Retail launch attribution and separately labeled disposable qualification.

The retail entry points are proposed for a separately authorized session.
They do not launch a program or accept a caller-selected PID.
"""

from contextlib import ExitStack, contextmanager
import ctypes
from ctypes import wintypes
from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import re
import subprocess
from time import time_ns

from contract import RETAIL_APPLICABILITY
from memory import (FIXTURE_NAME, PROCESS_QUERY_INFORMATION, PROCESS_VM_READ,
                    ImageReader, ReadFailure, Windows, disk_profile, epoch,
                    file_digest, pinned_stat, require, win_call)

RETAIL_NAME = "Starfield.exe"
STEAM_APP = 1716740
STEAM_APP_BUILD = 23518663
SIMULATED_PROFILE = "srr013-retail-like-disposable"
RETAIL_PROFILE = "srr013-retail-1.16.244.0"
LOG_TAIL_BYTES = 4096
MAX_LOG_APPEND = 1024 * 1024
MAX_PROCESSES = 32768
FILETIME_UNIX_EPOCH = 116444736000000000
TOKEN_QUERY = 0x0008
TH32CS_SNAPPROCESS = 0x0002
ERROR_NO_MORE_FILES = 18


class ProcessEntry(ctypes.Structure):
    _fields_ = [
        ("size", wintypes.DWORD), ("usage", wintypes.DWORD), ("pid", wintypes.DWORD),
        ("default_heap", ctypes.c_size_t), ("module", wintypes.DWORD), ("threads", wintypes.DWORD),
        ("parent", wintypes.DWORD), ("priority", wintypes.LONG), ("flags", wintypes.DWORD),
        ("exe", wintypes.WCHAR * 260),
    ]


class ProcessMetadata(Windows):
    def __init__(self):
        super().__init__()
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        advapi = ctypes.WinDLL("advapi32", use_last_error=True)
        ptr, dword, boolean = ctypes.c_void_p, wintypes.DWORD, wintypes.BOOL
        dp = ctypes.POINTER(dword)
        signatures = (
            (kernel, "CreateToolhelp32Snapshot", ptr, dword, dword),
            (kernel, "Process32FirstW", boolean, ptr, ctypes.POINTER(ProcessEntry)),
            (kernel, "Process32NextW", boolean, ptr, ctypes.POINTER(ProcessEntry)),
            (kernel, "ProcessIdToSessionId", boolean, dword, dp),
            (kernel, "GetCurrentProcess", ptr),
            (advapi, "OpenProcessToken", boolean, ptr, dword, ctypes.POINTER(ptr)),
            (advapi, "GetTokenInformation", boolean, ptr, ctypes.c_int, ptr, dword, dp),
            (advapi, "EqualSid", boolean, ptr, ptr),
            (advapi, "GetSidSubAuthorityCount", ctypes.POINTER(wintypes.BYTE), ptr),
            (advapi, "GetSidSubAuthority", dp, ptr, dword),
        )
        for dll, name, restype, *argtypes in signatures:
            binding = getattr(dll, name)
            binding.restype, binding.argtypes = restype, argtypes
            setattr(self, name, binding)

    @contextmanager
    def open(self, pid, *, read):
        access = PROCESS_QUERY_INFORMATION | (PROCESS_VM_READ if read else 0)
        handle = win_call(self.OpenProcess(access, False, pid), "read_access_denied", "OpenProcess")
        try:
            yield handle
        finally:
            self.CloseHandle(handle)

    def census(self, names):
        snapshot = self.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        require(snapshot not in (None, ctypes.c_void_p(-1).value), "process_census_unverified",
                "Toolhelp process snapshot unavailable")
        try:
            records = {name.casefold(): [] for name in names}
            row = ProcessEntry()
            row.size = ctypes.sizeof(row)
            win_call(self.Process32FirstW(snapshot, ctypes.byref(row)),
                     "process_census_unverified", "Process32FirstW")
            for _ in range(MAX_PROCESSES):
                if row.exe.casefold() in records:
                    records[row.exe.casefold()].append((row.pid, row.parent))
                if not self.Process32NextW(snapshot, ctypes.byref(row)):
                    require(ctypes.get_last_error() == ERROR_NO_MORE_FILES,
                            "process_census_unverified", "incomplete process census")
                    return records
            raise ReadFailure("process_census_unverified", "process census exceeded its bound")
        finally:
            self.CloseHandle(snapshot)

    def session(self, pid):
        session = wintypes.DWORD()
        win_call(self.ProcessIdToSessionId(pid, ctypes.byref(session)),
                 "session_unverified", "ProcessIdToSessionId")
        return session.value

    def process_path(self, handle):
        buffer = ctypes.create_unicode_buffer(32768)
        length = wintypes.DWORD(len(buffer))
        win_call(self.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(length)),
                 "process_path_unverified", "QueryFullProcessImageNameW")
        return canonical(Path(buffer.value), "process_path_unverified")

    @contextmanager
    def token(self, process):
        token = ctypes.c_void_p()
        win_call(self.OpenProcessToken(process, TOKEN_QUERY, ctypes.byref(token)),
                 "account_unverified", "OpenProcessToken(TOKEN_QUERY)")
        try:
            yield token
        finally:
            self.CloseHandle(token)

    def token_field(self, token, kind, limit=4096):
        result = ctypes.create_string_buffer(limit)
        size = wintypes.DWORD()
        win_call(self.GetTokenInformation(token, kind, result, len(result), ctypes.byref(size)),
                 "account_unverified", "GetTokenInformation")
        require(0 < size.value <= len(result), "account_unverified", "invalid token field size")
        return result

    def verify_account(self, handle, pid, expected_session):
        require(expected_session and self.session(os.getpid()) == self.session(pid) == expected_session,
                "session_mismatch", "target, inspector and selected interactive session differ")
        with self.token(self.GetCurrentProcess()) as ours, self.token(handle) as theirs:
            for token in (ours, theirs):
                elevation = self.token_field(token, 20, ctypes.sizeof(wintypes.DWORD))  # TokenElevation
                require(wintypes.DWORD.from_buffer(elevation).value == 0,
                        "elevation_disallowed", "inspector or selected process is elevated")
                label = self.token_field(token, 25)  # TokenIntegrityLevel
                sid = ctypes.c_void_p.from_buffer(label).value
                count = self.GetSidSubAuthorityCount(sid)
                require(count and count.contents.value, "account_unverified", "integrity SID unavailable")
                integrity = self.GetSidSubAuthority(sid, count.contents.value - 1).contents.value
                require(0x2000 <= integrity < 0x3000, "elevation_disallowed", "token integrity is not medium")
            mine, other = self.token_field(ours, 1), self.token_field(theirs, 1)  # TokenUser
            require(self.EqualSid(ctypes.c_void_p.from_buffer(mine).value,
                                  ctypes.c_void_p.from_buffer(other).value),
                    "account_mismatch", "inspector and selected process have different user SIDs")


def canonical(path, code):
    try:
        path = Path(path)
        require(path.is_absolute() and len(path.drive) == 2 and path.drive[1] == ":" and ".." not in path.parts,
                code, "an absolute local path is required")
        return path.resolve(strict=True)
    except (OSError, TypeError, ValueError) as error:
        raise ReadFailure(code, "cannot resolve the designated path") from error


def bytes_sha(value):
    return hashlib.sha256(value).hexdigest()


@dataclass(frozen=True)
class LogBaseline:
    path: Path
    file_id: tuple
    size: int
    tail_sha256: str

    @classmethod
    def record(cls, path):
        designated = Path(path)
        path = canonical(designated, "steam_log_unverified")
        require(path == designated, "steam_log_unverified", "Steam log resolves outside the designated path")
        try:
            with path.open("rb") as stream:
                before = os.fstat(stream.fileno())
                count = min(before.st_size, LOG_TAIL_BYTES)
                stream.seek(before.st_size - count)
                tail = stream.read(count)
                require(pinned_stat(os.fstat(stream.fileno())) == pinned_stat(before) == pinned_stat(path.stat())
                        and len(tail) == count and tail.endswith(b"\n"),
                        "steam_log_unverified", "baseline changed or lacks a complete final line")
        except OSError as error:
            raise ReadFailure("steam_log_unverified", "cannot read the Steam baseline") from error
        return cls(path, (before.st_dev, before.st_ino), before.st_size, bytes_sha(tail))

    def match(self, pid, image, *, with_source=False):
        try:
            with self.path.open("rb") as stream:
                before = os.fstat(stream.fileno())
                require((before.st_dev, before.st_ino) == self.file_id
                        and self.size <= before.st_size <= self.size + MAX_LOG_APPEND,
                        "steam_log_unverified", "Steam log was replaced, truncated or exceeds the append bound")
                count = min(self.size, LOG_TAIL_BYTES)
                stream.seek(self.size - count)
                tail = stream.read(count)
                delta = stream.read(before.st_size - self.size)
                require(pinned_stat(os.fstat(stream.fileno())) == pinned_stat(before) == pinned_stat(self.path.stat())
                        and bytes_sha(tail) == self.tail_sha256 and len(delta) == before.st_size - self.size
                        and delta.endswith(b"\n"),
                        "steam_log_unverified", "Steam log prefix, append length or final boundary changed")
        except OSError as error:
            raise ReadFailure("steam_log_unverified", "cannot read the Steam log append") from error
        try:
            target = f'AppID {STEAM_APP} adding PID {pid} as a tracked process ""{image}""'.encode("ascii")
        except UnicodeEncodeError as error:
            raise ReadFailure("steam_log_unverified", "non-ASCII Steam log path profile is unqualified") from error
        prefix = re.compile(rb"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\] ")
        exact = []
        offset = self.size
        for line in delta.split(b"\n")[:-1]:
            raw = line + b"\n"
            stamp = prefix.match(raw)
            if stamp and raw[stamp.end():].removesuffix(b"\n").removesuffix(b"\r").lower() == target.lower():
                exact.append((offset, raw))
            offset += len(raw)
        require(len(exact) == 1, "steam_attribution_failed", "expected exactly one new AppID/PID/full-image line")
        offset, raw = exact[0]
        evidence = {"baseline_tail_sha256": self.tail_sha256, "baseline_size": self.size,
                    "tracking_sha256": bytes_sha(raw), "tracking_offset": offset,
                    "tracking_line": raw.decode("ascii"), "file_id": list(self.file_id)}
        return (evidence, tail, delta) if with_source else evidence


@dataclass(frozen=True)
class LaunchBaseline:
    api: ProcessMetadata
    image: Path
    image_hash: str
    log: LogBaseline
    parent_pid: int
    parent_epoch: int
    session: int
    after_creation: int
    profile_name: str
    parent_check: object
    parent_sha256: str | None = None

    def select(self, *, with_source=False):
        self.parent_check()
        candidates = self.api.census([self.image.name])[self.image.name.casefold()]
        require(len(candidates) == 1, "process_ambiguous", "expected one candidate in the Windows process census")
        pid, parent = candidates[0]
        require(parent == self.parent_pid, "steam_parent_mismatch", "selected candidate has the wrong launch parent")
        return pid, self.log.match(pid, self.image, with_source=with_source)


def publication_floor():
    return FILETIME_UNIX_EPOCH + time_ns() // 100


def begin_simulated(fixture, image_hash, steam_log):
    api = ProcessMetadata()
    fixture = canonical(fixture, "ownership_unverified")
    require(fixture.name.casefold() == FIXTURE_NAME, "ownership_unverified", "expected the owned fixture executable")
    require(not api.census([FIXTURE_NAME])[FIXTURE_NAME], "process_ambiguous", "fixture already present before baseline")
    parent_pid, parent_epoch = epoch(api, api.GetCurrentProcess())
    session = api.session(parent_pid)

    def check_parent():
        require(epoch(api, api.GetCurrentProcess()) == (parent_pid, parent_epoch),
                "epoch_mismatch", "simulated launcher epoch changed")

    return LaunchBaseline(api, fixture, image_hash, LogBaseline.record(steam_log), parent_pid, parent_epoch,
                          session, publication_floor(), SIMULATED_PROFILE, check_parent)


def verify_manifest(steam_root):
    """Narrow read of the identity fields corroborated in SRR-009."""
    manifest = steam_root / "steamapps" / f"appmanifest_{STEAM_APP}.acf"
    try:
        with manifest.open("rb") as stream:
            before = os.fstat(stream.fileno())
            data = stream.read(128 * 1024 + 1)
            require(pinned_stat(os.fstat(stream.fileno())) == pinned_stat(before) == pinned_stat(manifest.stat())
                    and len(data) == before.st_size, "steam_install_unverified", "Steam app manifest changed")
    except OSError as error:
        raise ReadFailure("steam_install_unverified", "Steam app manifest is unavailable") from error
    require(len(data) <= 128 * 1024 and data.startswith(b'"AppState"'),
            "steam_install_unverified", "Steam app manifest shape or size disagrees")
    for field, value in ((b"appid", str(STEAM_APP).encode()), (b"StateFlags", b"4"),
                         (b"buildid", str(STEAM_APP_BUILD).encode()), (b"installdir", b"Starfield")):
        rows = re.findall(rb'^\s*"' + field + rb'"[ \t]+"([^"\r\n]+)"[ \t\r]*$', data,
                          re.MULTILINE | re.IGNORECASE)
        require(rows == [value], "steam_install_unverified", "Steam app manifest identity disagrees")


def registered_steam_root():
    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam", access=winreg.KEY_QUERY_VALUE) as key:
            path, value_type = winreg.QueryValueEx(key, "SteamPath")
    except OSError as error:
        raise ReadFailure("steam_install_unverified", "Steam installation registry witness unavailable") from error
    require(value_type == winreg.REG_SZ, "steam_install_unverified", "SteamPath registry witness is not a string")
    return canonical(path, "steam_install_unverified")


@contextmanager
def begin_retail(steam_root, *, digest_file=file_digest):
    """Retain the ordinary-account Steam client and pre-launch provenance.

    For a future authorized reader. The caller controls Steam and the game.
    """
    api = ProcessMetadata()
    root = canonical(steam_root, "steam_install_unverified")
    require(root == registered_steam_root(), "steam_install_unverified", "selected root differs from SteamPath")
    steam = canonical(root / "steam.exe", "steam_install_unverified")
    image = canonical(root / "steamapps/common/Starfield" / RETAIL_NAME, "steam_install_unverified")
    require(steam == root / "steam.exe" and image == root / "steamapps/common/Starfield" / RETAIL_NAME,
            "steam_install_unverified", "designated Steam path or game executable resolves outside the installation")
    verify_manifest(root)
    session = api.session(os.getpid())

    def select_steam():
        census = api.census([RETAIL_NAME, "steam.exe"])
        candidates = [pid for pid, _ in census["steam.exe"] if api.session(pid) == session]
        require(len(candidates) == 1, "steam_process_ambiguous", "expected one Steam process in the interactive session")
        return candidates[0], census[RETAIL_NAME.casefold()]

    steam_pid, targets = select_steam()
    require(not targets, "process_ambiguous", "retail process already present before the Steam baseline")
    with api.open(steam_pid, read=False) as steam_handle, ExitStack() as opened:
        try:
            steam_file = opened.enter_context(steam.open("rb"))
            stamp = pinned_stat(os.fstat(steam_file.fileno()))
            steam_hash = digest_file(steam_file)
        except OSError as error:
            raise ReadFailure("steam_install_unverified", "cannot pin the Steam client backing file") from error
        steam_epoch = epoch(api, steam_handle)[1]

        def check_parent():
            api.verify_account(steam_handle, steam_pid, session)
            require(epoch(api, steam_handle) == (steam_pid, steam_epoch) and select_steam()[0] == steam_pid,
                    "steam_epoch_mismatch", "selected Steam client changed or is ambiguous")
            try:
                paths_match = (api.process_path(steam_handle) == steam
                               and pinned_stat(steam.stat()) == pinned_stat(os.fstat(steam_file.fileno())) == stamp
                               and digest_file(steam_file) == steam_hash)
            except OSError as error:
                raise ReadFailure("steam_install_unverified", "cannot recheck Steam client backing identity") from error
            require(paths_match, "steam_install_unverified", "Steam client backing identity changed")
            verify_manifest(root)

        check_parent()
        yield LaunchBaseline(api, image, RETAIL_APPLICABILITY["sha256"],
                             LogBaseline.record(root / "logs/gameprocess_log.txt"), steam_pid,
                             steam_epoch, session, publication_floor(), RETAIL_PROFILE, check_parent, steam_hash)


@contextmanager
def _open_selected(baseline, expected_epoch, expected_session, *, query_only, digest_file=file_digest):
    api = baseline.api
    pid, (log, tail, append) = baseline.select(with_source=True)
    append_sha256 = bytes_sha(append)
    if expected_epoch is not None:
        require(pid == expected_epoch[0], "epoch_mismatch", "census selected a different PID than the owned launch")
    with ExitStack() as opened:
        try:
            stream = opened.enter_context(baseline.image.open("rb"))
            before = pinned_stat(os.fstat(stream.fileno()))
            require(digest_file(stream) == baseline.image_hash, "image_hash_mismatch", "selected disk executable disagrees")
            disk = disk_profile(stream, retail=baseline.profile_name == RETAIL_PROFILE)
            require(pinned_stat(os.fstat(stream.fileno())) == pinned_stat(baseline.image.stat()) == before,
                    "mapping_unverified", "selected executable changed during disk qualification")
        except OSError as error:
            raise ReadFailure("mapping_unverified", "cannot pin the selected disk executable") from error
        handle = opened.enter_context(api.open(pid, read=not query_only))
        selected = epoch(api, handle)
        require(selected[0] == pid and selected[1] >= baseline.after_creation > baseline.parent_epoch
                and (expected_epoch is None or selected == expected_epoch),
                "epoch_mismatch", "selected process creation is stale or differs from the owned launch")

        def attribution(current_handle, actual_epoch):
            found, evidence = baseline.select()
            require(found == pid and evidence == log and actual_epoch == selected,
                    "steam_attribution_failed", "selected process or matching log witness changed")
            api.verify_account(current_handle, found, expected_session)
            return {"app_id": STEAM_APP, "parent_pid": baseline.parent_pid, "parent_epoch": baseline.parent_epoch,
                    "parent_image_sha256": baseline.parent_sha256, "session": expected_session,
                    "admission_append_sha256": append_sha256, **evidence}

        reader = ImageReader(api, handle, selected, baseline.image, stream, baseline.image_hash, disk, query_only,
                             profile_name=baseline.profile_name, attribution=attribution, digest_file=digest_file)
        reader.admission_log = {"baseline_tail": tail, "append": append}
        yield reader


@contextmanager
def open_simulated(baseline, process, *, query_only=False, expected_creation=None, expected_session=None,
                   digest_file=file_digest):
    require(baseline.profile_name == SIMULATED_PROFILE and isinstance(process, subprocess.Popen)
            and isinstance(process.args, (tuple, list)) and process.args,
            "ownership_unverified", "retail-like qualification requires an owned fixture launch")
    require(canonical(process.args[0], "ownership_unverified") == baseline.image,
            "ownership_unverified", "owned fixture launch path disagrees with the baseline")
    pid, creation = epoch(baseline.api, int(process._handle))
    require(pid == process.pid, "epoch_mismatch", "owned launch handle PID disagrees")
    expected_epoch = pid, creation if expected_creation is None else expected_creation
    session = baseline.session if expected_session is None else expected_session
    with _open_selected(baseline, expected_epoch, session, query_only=query_only, digest_file=digest_file) as reader:
        yield reader


@contextmanager
def open_retail(baseline, *, digest_file=file_digest):
    require(baseline.profile_name == RETAIL_PROFILE and baseline.image.name == RETAIL_NAME
            and baseline.image_hash == RETAIL_APPLICABILITY["sha256"],
            "retail_profile_unverified", "the separately designated retail baseline is required")
    with _open_selected(baseline, None, baseline.session, query_only=False, digest_file=digest_file) as reader:
        yield reader
