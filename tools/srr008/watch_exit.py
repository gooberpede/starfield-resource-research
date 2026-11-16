# SPDX-License-Identifier: GPL-3.0-or-later
"""Witness exit using an independent, read-only handle to a pinned process epoch."""

import argparse
import ctypes as C
from ctypes import wintypes as W
import json
import os
from pathlib import Path
import re

import inventory as inv
from preflight import available_bytes


def record(folder, name, value):
    available_bytes()
    temporary = folder / (name + ".partial")
    with temporary.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    temporary.rename(folder / (name + ".json"))


def watch(run, expected_image, output):
    token = re.fullmatch(r"([0-9a-f]{64})-([1-9][0-9]*)-([1-9][0-9]*)(?:-[1-9][0-9]*)?", run)
    if not token:
        raise ValueError("Malformed run token")
    digest, pid_text, birth_text = token.groups()
    pid, birth = int(pid_text), int(birth_text)
    if C.sizeof(C.c_void_p) != 8 or not expected_image.is_absolute() or not output.is_dir():
        raise ValueError("Use x64 Python, an absolute executable path and an existing private output directory")
    handle = inv.open_process(inv.ACCESS, False, pid)
    inv.check(handle)
    try:
        target = inv.identity(handle, pid, birth)
        if (target["path"].casefold() != str(expected_image).casefold() or
                target["process_machine"] != 0 or target["native_machine"] != 0x8664):
            raise inv.IdentityError("Process image path or machine mismatch")
        observed = inv.describe_file(target["path"])
        if observed.get("sha256") != digest:
            raise inv.IdentityError("Executable digest mismatch")
        record(output, "exit-witness-bound",
               dict(run=run, target=target, image=observed, access_mask=inv.ACCESS, utc=inv.utc()))
        inv.check(inv.wait(handle, 0xFFFFFFFF) == 0)
        code = W.DWORD()
        exit_code = inv.bind("GetExitCodeProcess", W.BOOL, W.HANDLE, C.POINTER(W.DWORD))
        inv.check(exit_code(handle, C.byref(code)))
        record(output, "exit-witness-result",
               dict(run=run, pid=pid, process_birth=birth, signaled=True, exit_code=code.value, utc=inv.utc()))
    finally:
        inv.close(handle)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", help="Full TARGET_BOUND run token")
    parser.add_argument("image", type=Path, help="Exact absolute executable path")
    parser.add_argument("output", type=Path, help="Existing private run directory")
    args = parser.parse_args()
    try:
        watch(args.run, args.image, args.output)
    except (OSError, RuntimeError, ValueError) as error:
        parser.exit(1, f"Exit witness failed: {error}\n")


if __name__ == "__main__":
    main()
