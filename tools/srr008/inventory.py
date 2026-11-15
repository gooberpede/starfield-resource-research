# SPDX-License-Identifier: GPL-3.0-or-later
# Tool Help enumeration adapted from starfield-outpost-research.
"""SRR-008 offline qualification of the read-only inventory core (schema 1)."""
import ctypes as C
from ctypes import wintypes as W
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys

ACCESS = 0x101000  # SYNCHRONIZE | PROCESS_QUERY_LIMITED_INFORMATION
INVALID_HANDLE = C.c_void_p(-1).value
MODULE_FLAGS = 0x18
kernel = C.WinDLL("kernel32", use_last_error=True)


class Module(C.Structure):
    _fields_ = [
        ("size", W.DWORD), ("module_id", W.DWORD), ("pid", W.DWORD),
        ("global_usage", W.DWORD), ("process_usage", W.DWORD),
        ("base", C.c_void_p), ("extent", W.DWORD), ("module", W.HMODULE),
        ("name", W.WCHAR * 256), ("path", W.WCHAR * 260),
    ]


def bind(name, result, *args):
    function = getattr(kernel, name)
    function.restype = result
    function.argtypes = args
    return function


open_process = bind("OpenProcess", W.HANDLE, W.DWORD, W.BOOL, W.DWORD)
close = bind("CloseHandle", W.BOOL, W.HANDLE)
wait = bind("WaitForSingleObject", W.DWORD, W.HANDLE, W.DWORD)
get_pid = bind("GetProcessId", W.DWORD, W.HANDLE)
filetime_ptr = C.POINTER(W.FILETIME)
times = bind("GetProcessTimes", W.BOOL, W.HANDLE, *([filetime_ptr] * 4))
image = bind("QueryFullProcessImageNameW", W.BOOL, W.HANDLE, W.DWORD,
             W.LPWSTR, C.POINTER(W.DWORD))
machine_ptr = C.POINTER(W.USHORT)
wow = bind("IsWow64Process2", W.BOOL, W.HANDLE, machine_ptr, machine_ptr)
snapshot = bind("CreateToolhelp32Snapshot", W.HANDLE, W.DWORD, W.DWORD)
first = bind("Module32FirstW", W.BOOL, W.HANDLE, C.POINTER(Module))
next_module = bind("Module32NextW", W.BOOL, W.HANDLE, C.POINTER(Module))


class IdentityError(RuntimeError):
    pass


def utc():
    return datetime.now(timezone.utc).isoformat()


def check(ok):
    if not ok:
        raise C.WinError(C.get_last_error())


def identity(handle, pid, expected=None):
    status = wait(handle, 0)
    if status == 0xFFFFFFFF:
        raise C.WinError(C.get_last_error())
    if status != 258 or get_pid(handle) != pid:
        raise IdentityError("Retained handle is no longer live for the requested PID")
    created, exited, kernel_time, user_time = (W.FILETIME() for _ in range(4))
    check(times(handle, created, exited, kernel_time, user_time))
    creation = (created.dwHighDateTime << 32) | created.dwLowDateTime
    if expected is not None and creation != expected:
        raise IdentityError("Process creation FILETIME mismatch")
    path = C.create_unicode_buffer(32768)
    length = W.DWORD(len(path))
    check(image(handle, 0, path, length))
    process_machine, native_machine = W.USHORT(), W.USHORT()
    check(wow(handle, process_machine, native_machine))
    return dict(pid=pid, creation_filetime=creation, path=path.value,
                process_machine=process_machine.value, native_machine=native_machine.value)


def enumerate_modules(pid):
    attempts = []
    for _ in range(3):
        handle = snapshot(MODULE_FLAGS, pid)
        if handle != INVALID_HANDLE:
            break
        error = C.get_last_error()
        attempts.append(error)
        if error != 24:
            return [], attempts, error
    else:
        return [], attempts, error

    rows = []
    try:
        row = Module()
        row.size = C.sizeof(row)
        if not first(handle, row):
            return rows, attempts, C.get_last_error()
        while len(rows) < 2048:
            if row.pid != pid or not row.base or not row.extent:
                return rows, attempts, "invalid_module_entry"
            rows.append(dict(path=row.path, base=row.base, extent=row.extent))
            if not next_module(handle, row):
                error = C.get_last_error()
                return rows, attempts, None if error == 18 else error
        return rows, attempts, "module_count_limit"
    finally:
        close(handle)


def pe_identity(stream):
    dos = stream.read(64)
    if len(dos) != 64 or dos[:2] != b"MZ":
        raise ValueError("Invalid DOS header")
    stream.seek(struct.unpack_from("<I", dos, 60)[0])
    header = stream.read(24)
    if len(header) != 24 or header[:4] != b"PE\0\0":
        raise ValueError("Invalid PE signature")
    machine, sections, timestamp, _, _, optional_size, _ = struct.unpack_from("<HHIIIHH", header, 4)
    optional = stream.read(optional_size)
    if len(optional) != optional_size or len(optional) < 68:
        raise ValueError("Truncated optional header")
    magic = struct.unpack_from("<H", optional)[0]
    if magic not in (0x10B, 0x20B):
        raise ValueError("Unsupported optional header")
    extent, _, checksum = struct.unpack_from("<III", optional, 56)
    return dict(machine=machine, sections=sections, timestamp=timestamp,
                magic=magic, image_extent=extent, checksum=checksum)


def file_stamp(stat):
    return dict(volume=stat.st_dev, file_id=stat.st_ino, size=stat.st_size,
                mtime_ns=stat.st_mtime_ns)


def describe_file(raw_path):
    result = {}
    try:
        path = Path(raw_path)
        if not path.is_absolute() or len(path.drive) != 2 or path.drive[1] != ":":
            raise ValueError("Expected an absolute local drive path")
        resolved = path.resolve(strict=True)
        if len(resolved.drive) != 2 or resolved.drive[1] != ":":
            raise ValueError("Resolved path is outside local drives")
        if kernel_drive_type(resolved.anchor) not in (2, 3, 5, 6):
            raise ValueError("Resolved drive is unavailable or remote")
        result["resolved_path"] = str(resolved)
        with resolved.open("rb") as stream:
            before = file_stamp(os.fstat(stream.fileno()))
            result["file"] = before
            if before["size"] > 512 * 1024**2:
                raise ValueError("File size exceeds hashing limit")
            try:
                result["disk_pe"] = pe_identity(stream)
            except (OSError, ValueError) as exc:
                result["pe_error"] = str(exc)
            stream.seek(0)
            digest = hashlib.sha256()
            remaining = before["size"]
            while remaining:
                chunk = stream.read(min(1024**2, remaining))
                if not chunk:
                    raise ValueError("File shortened during hashing")
                remaining -= len(chunk)
                digest.update(chunk)
            if (stream.read(1) or before != file_stamp(os.fstat(stream.fileno()))
                    or before != file_stamp(resolved.stat())
                    or before != file_stamp(path.stat())):
                raise ValueError("File identity or metadata changed during read")
            result["sha256"] = digest.hexdigest()
    except (OSError, ValueError) as exc:
        result["file_error"] = str(exc)
    return result


kernel_drive_type = bind("GetDriveTypeW", W.UINT, W.LPCWSTR)


def inventory(handle, pid, creation, sequence):
    started = utc()
    before = identity(handle, pid, creation)
    rows, attempts, error = enumerate_modules(pid)
    enumerated = utc()
    after_enumeration = identity(handle, pid, creation)
    if before != after_enumeration:
        raise IdentityError("Process identity changed across enumeration")
    for row in rows:
        row.update(describe_file(row["path"]))
    after = identity(handle, pid, creation)
    if before != after:
        raise IdentityError("Process identity changed across file reads")
    return dict(sequence=sequence, started_utc=started, enumerated_utc=enumerated,
                ended_utc=utc(), process_before=before, process_after_enumeration=after_enumeration,
                process_after=after, enumeration_attempt_errors=attempts,
                enumeration_error=error, modules=rows)


def difference(a, b):
    def index(sample):
        return {(row["base"], row["path"].casefold()): row for row in sample["modules"]}

    left, right = index(a), index(b)
    return dict(only_first=[left[key] for key in sorted(left.keys() - right.keys())],
                only_second=[right[key] for key in sorted(right.keys() - left.keys())],
                changed=[dict(first=left[key], second=right[key])
                         for key in sorted(left.keys() & right.keys()) if left[key] != right[key]])


def main():
    if len(sys.argv) != 2 or C.sizeof(C.c_void_p) != 8:
        raise SystemExit("Usage with x64 Python: python -E -B inventory.py <new-fixture-report.json>")
    output = Path(sys.argv[1])
    if output.exists():
        raise SystemExit("Fixture output already exists")
    python = str(Path(sys.executable).resolve())
    program = "import sys; print('ready', flush=True); sys.stdin.read()"
    child = subprocess.Popen([python, "-I", "-S", "-B", "-c", program],
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             creationflags=subprocess.CREATE_NO_WINDOW)
    handle = None
    try:
        if child.stdout.readline() != b"ready\r\n":
            raise RuntimeError("Fixture did not acknowledge readiness")
        handle = open_process(ACCESS, False, child.pid)
        check(handle)
        target = identity(handle, child.pid)
        if not os.path.samefile(target["path"], python):
            raise IdentityError("Fixture executable path mismatch")
        image_pin = describe_file(python)
        creation = target["creation_filetime"]
        samples = [inventory(handle, child.pid, creation, i) for i in (1, 2)]
        for sample in samples:
            main_image = [row for row in sample["modules"]
                          if row.get("resolved_path", "").casefold() == python.casefold()]
            if (sample["enumeration_error"] is not None or len(main_image) != 1
                    or not image_pin.get("sha256")
                    or main_image[0].get("sha256") != image_pin["sha256"]
                    or main_image[0]["file"] != image_pin["file"]
                    or main_image[0]["extent"] != image_pin["disk_pe"]["image_extent"]):
                raise RuntimeError("Fixture main image evidence incomplete")
        try:
            inventory(handle, child.pid, creation + 1, 3)
        except IdentityError as exc:
            refusal = str(exc)
            if refusal != "Process creation FILETIME mismatch":
                raise
        else:
            raise AssertionError("Incorrect process epoch admitted")
        child.stdin.close()
        if wait(handle, 5000) != 0 or child.wait(timeout=5) != 0:
            raise RuntimeError("Fixture cooperative exit unconfirmed")
        report = dict(schema=1, mode="disposable_only", windows=list(sys.getwindowsversion()),
                      runtime=sys.version, source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                      access_mask=ACCESS, module_flags=MODULE_FLAGS, process=target, image=image_pin,
                      snapshots=samples, difference=difference(*samples), mismatch_refusal=refusal,
                      fixture_exit_code=child.returncode)
        with output.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(report, stream, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        if handle:
            close(handle)
        child.stdin.close()
        child.stdout.close()
        child.wait(timeout=5)


if __name__ == "__main__":
    main()
