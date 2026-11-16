"""Query and exact-read adapter for an AMD64 fixture started by this inspector."""

from contextlib import contextmanager
import ctypes
from ctypes import wintypes
import hashlib
import os
from pathlib import Path
import struct
import subprocess
import sys


PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
MEM_COMMIT = 0x1000
MEM_IMAGE = 0x1000000
AMD64 = 0x8664
PE32_PLUS = 0x20B
ROOT_END = 0x82EEC30
STILL_ACTIVE = 259
FIXTURE_NAME = "srr013-fixture.exe"


class ReadFailure(Exception):
    def __init__(self, code, detail):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def require(condition, code, detail):
    if not condition:
        raise ReadFailure(code, detail)


class MemoryInfo(ctypes.Structure):
    _fields_ = [
        ("base", ctypes.c_void_p),
        ("allocation_base", ctypes.c_void_p),
        ("allocation_protect", wintypes.DWORD),
        ("partition_id", wintypes.WORD),
        ("region_size", ctypes.c_size_t),
        ("state", wintypes.DWORD),
        ("protect", wintypes.DWORD),
        ("type", wintypes.DWORD),
    ]


class ModuleInfo(ctypes.Structure):
    _fields_ = [
        ("base", ctypes.c_void_p),
        ("size", wintypes.DWORD),
        ("entry_point", ctypes.c_void_p),
    ]


class Windows:
    def __init__(self):
        require(
            sys.platform == "win32" and ctypes.sizeof(ctypes.c_void_p) == 8,
            "unsupported_platform",
            "owned fixture inspection requires 64-bit Windows Python",
        )
        dll = ctypes.WinDLL("kernel32", use_last_error=True)
        ptr = ctypes.c_void_p
        dword = wintypes.DWORD
        size = ctypes.c_size_t
        bool_ = wintypes.BOOL
        filetime = ctypes.POINTER(wintypes.FILETIME)
        dword_ptr = ctypes.POINTER(dword)
        signatures = (
            ("OpenProcess", ptr, dword, bool_, dword),
            ("CloseHandle", bool_, ptr),
            ("GetProcessId", dword, ptr),
            ("GetProcessTimes", bool_, ptr, filetime, filetime, filetime, filetime),
            ("GetExitCodeProcess", bool_, ptr, dword_ptr),
            ("QueryFullProcessImageNameW", bool_, ptr, dword, wintypes.LPWSTR, dword_ptr),
            ("GetFinalPathNameByHandleW", dword, ptr, wintypes.LPWSTR, dword, dword),
            ("K32EnumProcessModulesEx", bool_, ptr, ctypes.POINTER(ptr), dword, dword_ptr, dword),
            ("K32GetModuleInformation", bool_, ptr, ptr, ctypes.POINTER(ModuleInfo), dword),
            ("K32GetMappedFileNameW", dword, ptr, ptr, wintypes.LPWSTR, dword),
            ("VirtualQueryEx", size, ptr, ptr, ctypes.POINTER(MemoryInfo), size),
            ("ReadProcessMemory", bool_, ptr, ptr, ptr, size, ctypes.POINTER(size)),
        )
        for name, restype, *argtypes in signatures:
            binding = getattr(dll, name)
            binding.restype = restype
            binding.argtypes = argtypes
            setattr(self, name, binding)


def win_call(result, code, operation):
    require(result, code, f"{operation} failed with Windows error {ctypes.get_last_error()}")
    return result


def epoch(api, handle):
    creation, exit_, kernel, user = (wintypes.FILETIME() for _ in range(4))
    refs = [ctypes.byref(field) for field in (creation, exit_, kernel, user)]
    win_call(api.GetProcessTimes(handle, *refs), "epoch_unverified", "GetProcessTimes")
    exit_code = wintypes.DWORD()
    win_call(api.GetExitCodeProcess(handle, ctypes.byref(exit_code)), "epoch_unverified", "GetExitCodeProcess")
    require(exit_code.value == STILL_ACTIVE and not (exit_.dwLowDateTime or exit_.dwHighDateTime),
            "process_exited", "owned process is no longer active")
    pid = win_call(api.GetProcessId(handle), "epoch_unverified", "GetProcessId")
    return pid, creation.dwHighDateTime << 32 | creation.dwLowDateTime


def file_digest(stream):
    stream.seek(0)
    return hashlib.file_digest(stream, "sha256").hexdigest()


def pinned_stat(status):
    return status.st_dev, status.st_ino, status.st_size, status.st_mtime_ns


def native_disk_path(api, stream):
    import msvcrt

    buffer = ctypes.create_unicode_buffer(32768)
    length = win_call(
        api.GetFinalPathNameByHandleW(msvcrt.get_osfhandle(stream.fileno()), buffer, len(buffer), 2),
        "mapping_unverified", "GetFinalPathNameByHandleW(VOLUME_NAME_NT)",
    )
    require(length < len(buffer), "mapping_unverified", "native file path truncated")
    return buffer.value


def disk_profile(stream):
    """Pin full PE headers and bounded relocation-free fixture code windows."""
    stream.seek(0)
    dos = stream.read(64)
    require(len(dos) == 64 and dos[:2] == b"MZ", "mapping_unverified", "invalid disk DOS header")
    pe_offset = struct.unpack_from("<I", dos, 0x3C)[0]
    require(64 <= pe_offset <= 0x10000, "mapping_unverified", "PE header offset out of bounds")
    stream.seek(pe_offset)
    coff = stream.read(24)
    require(len(coff) == 24 and coff[:4] == b"PE\0\0", "mapping_unverified", "invalid disk PE header")
    machine, sections = struct.unpack_from("<HH", coff, 4)
    opt_size = struct.unpack_from("<H", coff, 20)[0]
    require(machine == AMD64 and 0 < sections <= 96 and 112 <= opt_size <= 4096,
            "mapping_unverified", "unsupported disk image type")
    opt = stream.read(opt_size)
    table = stream.read(sections * 40)
    require(len(opt) == opt_size and len(table) == sections * 40, "mapping_unverified", "truncated disk PE metadata")
    magic = struct.unpack_from("<H", opt)[0]
    entry = struct.unpack_from("<I", opt, 16)[0]
    image_size, header_size = struct.unpack_from("<II", opt, 56)
    require(
        magic == PE32_PLUS and ROOT_END <= image_size < 1 << 31
        and pe_offset + 24 + opt_size + len(table) <= header_size <= 0x10000,
        "mapping_unverified",
        "fixture image extent or disk PE header bounds disagree",
    )
    stream.seek(0)
    headers = stream.read(header_size)
    require(len(headers) == header_size, "mapping_unverified", "truncated disk PE headers")
    windows = [(0, headers)]
    fixture_section = False
    for row in struct.iter_unpack("<8sIIIIIIHHI", table):
        name, virtual_size, rva, physical_size, physical_offset = row[:5]
        name = name.rstrip(b"\0")
        if name == b".srr":
            flags = row[-1]
            fixture_section = (
                rva <= 0x4B3D258 < ROOT_END <= rva + virtual_size <= image_size
                and physical_size == 0 and flags & 0x80000000 and not flags & 0x20000000
            )
        elif name == b".text":
            size = min(virtual_size, physical_size)
            require(size >= 64 and rva <= entry <= rva + size - 32 and rva + size <= image_size,
                    "mapping_unverified", "unsupported .text shape or entry point")
            for start in sorted({rva, entry, rva + size - 32}):
                stream.seek(physical_offset + start - rva)
                code = stream.read(32)
                require(len(code) == 32, "mapping_unverified", "truncated disk .text window")
                windows.append((start, code))
    require(fixture_section and len(windows) > 1, "mapping_unverified",
            "fixture code or synthetic zero-fill image section is absent")
    return image_size, entry, pe_offset + 48, tuple(windows)


class OwnedReader:
    def __init__(self, api, handle, expected_epoch, path, stream, expected_sha256, profile, query_only):
        self.api, self.handle, self.expected_epoch = api, handle, expected_epoch
        self.path, self.stream = path, stream
        self.sha256, self.profile = expected_sha256, profile
        self.query_only = query_only
        self.stat = pinned_stat(os.fstat(stream.fileno()))
        self.native_path = native_disk_path(api, stream)
        self.base = None
        self.identity()

    def region(self, address, size):
        info = MemoryInfo()
        returned = self.api.VirtualQueryEx(self.handle, address, ctypes.byref(info), ctypes.sizeof(info))
        require(returned == ctypes.sizeof(info), "read_incomplete",
                f"VirtualQueryEx failed at {address:#x}, Windows error {ctypes.get_last_error()}")
        require(
            info.state == MEM_COMMIT and info.base is not None
            and info.base <= address <= address + size <= info.base + info.region_size
            and not info.protect & 0x100
            and info.protect & 0xFF in {0x02, 0x04, 0x08, 0x20, 0x40, 0x80},
            "unreadable_region",
            f"range at {address:#x}, size {size} crosses an inaccessible region",
        )
        return info

    def read(self, address, size, alignment=1):
        require(
            alignment in (1, 2, 4, 8) and 0 < size <= 0x10000
            and address >= 0x10000 and address % alignment == 0 and address + size <= 1 << 64,
            "invalid_pointer",
            f"invalid read at {address:#x}, size {size}, alignment {alignment}",
        )
        self.region(address, size)
        buffer = ctypes.create_string_buffer(size)
        actual = ctypes.c_size_t()
        result = self.api.ReadProcessMemory(self.handle, address, buffer, size, ctypes.byref(actual))
        require(
            result and actual.value == size,
            "read_incomplete",
            f"ReadProcessMemory at {address:#x}: read {actual.value}/{size} bytes, Windows error {ctypes.get_last_error()}",
        )
        return buffer.raw

    def image_read(self, base, offset, size):
        info = self.region(base + offset, size)
        require(info.type == MEM_IMAGE and info.allocation_base == base, "mapping_unverified",
                f"RVA {offset:#x} is outside the admitted image allocation")
        return self.read(base + offset, size)

    def identity(self):
        api, handle = self.api, self.handle
        actual_epoch = epoch(api, handle)
        require(actual_epoch == self.expected_epoch, "epoch_mismatch", "opened process epoch disagrees")
        executable = ctypes.create_unicode_buffer(32768)
        length = wintypes.DWORD(len(executable))
        win_call(api.QueryFullProcessImageNameW(handle, 0, executable, ctypes.byref(length)),
                 "mapping_unverified", "QueryFullProcessImageNameW")
        try:
            image_path = Path(executable.value).resolve(strict=True)
            metadata = image_path.stat()
            pinned_metadata = os.fstat(self.stream.fileno())
            digest = file_digest(self.stream)
        except OSError as error:
            raise ReadFailure("mapping_unverified", "cannot identify process image path") from error
        require(
            image_path == self.path
            and pinned_stat(metadata) == pinned_stat(pinned_metadata) == self.stat
            and digest == self.sha256,
            "mapping_unverified",
            "process image path or pinned file identity changed",
        )
        modules = (ctypes.c_void_p * 1024)()
        module_bytes = wintypes.DWORD()
        rights_failure = "insufficient_read_rights" if self.query_only else "mapping_unverified"
        win_call(api.K32EnumProcessModulesEx(handle, modules, ctypes.sizeof(modules), ctypes.byref(module_bytes), 0x02),
                 rights_failure, "K32EnumProcessModulesEx")
        require(0 < module_bytes.value <= ctypes.sizeof(modules) and modules[0], "mapping_unverified",
                "module census incomplete or empty")
        main = ModuleInfo()
        win_call(api.K32GetModuleInformation(handle, modules[0], ctypes.byref(main), ctypes.sizeof(main)),
                 rights_failure, "K32GetModuleInformation")
        size, entry, base_offset, windows = self.profile
        require(
            main.base == modules[0] and main.size == size and main.entry_point == main.base + entry
            and (self.base is None or main.base == self.base),
            "mapped_image_mismatch",
            "main module base, extent or entry point disagrees with pinned AMD64 PE",
        )
        mapped_path = ctypes.create_unicode_buffer(32768)
        length = win_call(api.K32GetMappedFileNameW(handle, main.base, mapped_path, len(mapped_path)),
                          rights_failure, "K32GetMappedFileNameW")
        require(length < len(mapped_path) and mapped_path.value.casefold() == self.native_path.casefold(),
                "mapped_image_mismatch", "mapped backing path disagrees with pinned file handle")
        for start, expected in windows:
            actual = self.image_read(main.base, start, len(expected))
            if start == 0 and actual != expected:
                # The loader can rebase the mapped OptionalHeader.ImageBase.
                # Compare every other PE header byte, including COFF timestamp.
                header = bytearray(expected)
                struct.pack_into("<Q", header, base_offset, main.base)
                expected = header
            require(actual == expected, "mapped_image_mismatch",
                    f"mapped PE header or code window at RVA {start:#x} disagrees")
        for offset, width in (
            (0x4B3D258, 8), (0x4D5FAC8, 8), (0x4D6A6C0, 8),
            (0x5E60EA0, 8), (0x61DFA4C, 2), (0x61FA160, 8),
            (0x82EE5C0, 8), (0x82EE8C0, 8), (0x82EE908, 8),
            (0x82EEBB0, 8), (0x82EEC20, 16),
        ):
            info = self.region(main.base + offset, width)
            require(info.type == MEM_IMAGE and info.allocation_base == main.base, "mapping_unverified",
                    f"fixed profile RVA {offset:#x} lacks an admitted image region")
        require(epoch(api, handle) == actual_epoch, "epoch_mismatch", "process changed during admission")
        self.base = main.base
        return {
            "pid": actual_epoch[0],
            "creation": actual_epoch[1],
            "image_base": self.base,
            "image_size": size,
            "image_sha256": self.sha256,
            "profile": "srr013-owned-amd64",
        }


@contextmanager
def open_owned(process, image_path, expected_sha256, *, expected_creation=None, query_only=False):
    """Bind a fixed-rights handle to a caller-owned Popen fixture and image pin.

    The query-only test switch reduces rights for negative qualification.
    No PID-taking entry point or retail profile is provided.
    """
    api = Windows()
    require(isinstance(process, subprocess.Popen) and isinstance(process.args, (tuple, list)) and process.args,
            "ownership_unverified", "expected an owned Popen fixture launched with explicit argv")
    try:
        path = Path(image_path).resolve(strict=True)
        launch_path = Path(process.args[0]).resolve(strict=True)
    except (OSError, TypeError) as error:
        raise ReadFailure("ownership_unverified", "cannot identify owned launch executable") from error
    require(
        path.name.casefold() == FIXTURE_NAME and launch_path == path,
        "ownership_unverified",
        "owned launch path or disposable image disagrees",
    )
    pid, creation = epoch(api, int(process._handle))
    require(
        pid == process.pid and (expected_creation is None or creation == expected_creation),
        "epoch_mismatch",
        "owned launch epoch disagrees with selected process",
    )
    try:
        source = path.open("rb")
    except OSError as error:
        raise ReadFailure("mapping_unverified", "cannot open pinned fixture disk image") from error
    with source as stream:
        try:
            require(file_digest(stream) == expected_sha256, "mapping_unverified", "fixture disk image digest disagrees")
            profile = disk_profile(stream)
        except OSError as error:
            raise ReadFailure("mapping_unverified", "cannot read pinned fixture disk image") from error
        access = PROCESS_QUERY_INFORMATION | (0 if query_only else PROCESS_VM_READ)
        handle = win_call(api.OpenProcess(access, False, pid), "read_access_denied", "OpenProcess")
        try:
            reader = OwnedReader(api, handle, (pid, creation), path, stream, expected_sha256, profile, query_only)
            yield reader
        finally:
            api.CloseHandle(handle)
