"""Build the disposable SRR-013 AMD64 target and record local build identities."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import struct
import subprocess


SOURCE = Path(__file__).resolve().with_name("fixture.c")
DEFAULT_OUTPUT = SOURCE.parents[2] / ".local-work" / "codex" / "SRR-013" / "build"
COMPILE = ("/nologo", "/std:c17", "/W4", "/WX", "/O2", "/Brepro", "/Bv")
LINK = ("/Brepro", "/out:srr013-fixture.exe", "advapi32.lib")


def file_digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def find_vcvars():
    vswhere = Path(os.environ["ProgramFiles(x86)"]) / "Microsoft Visual Studio" / "Installer" / "vswhere.exe"
    installation = subprocess.check_output(
        [str(vswhere), "-latest", "-products", "*", "-requires",
         "Microsoft.VisualStudio.Component.VC.Tools.x86.x64", "-property", "installationPath"],
        text=True,
    ).strip()
    if not installation:
        raise RuntimeError("MSVC x64 tools are required; specify --vcvars for a custom location")
    return Path(installation) / "VC" / "Auxiliary" / "Build" / "vcvars64.bat"


def compiler_environment(vcvars):
    # Pass the batch file path through the environment, with delayed expansion disabled.
    child_env = dict(os.environ, SRR013_VCVARS=str(vcvars.resolve(strict=True)))
    command = r'cmd.exe /d /v:off /u /s /c ""%SRR013_VCVARS%" > nul && set"'
    output = subprocess.check_output(command, env=child_env, encoding="utf-16le")
    environment = {}
    for line in output.splitlines():
        name, equals, value = line.partition("=")
        if name and equals:
            environment[name.upper()] = value
    # Prevent implicit caller-supplied compiler/linker flags from changing the binary.
    for name in ("CL", "_CL_", "LINK", "_LINK_"):
        environment.pop(name, None)
    return environment


def inspect_fixture(path):
    with path.open("rb") as stream:
        header = stream.read(4096)
    pe_offset, = struct.unpack_from("<I", header, 0x3C)
    signature, machine, count = struct.unpack_from("<4sHH", header, pe_offset)
    optional_size, = struct.unpack_from("<H", header, pe_offset + 20)
    optional = pe_offset + 24
    magic, = struct.unpack_from("<H", header, optional)
    image_size, = struct.unpack_from("<I", header, optional + 56)
    if (signature, machine, magic) != (b"PE\0\0", 0x8664, 0x20B):
        raise RuntimeError("fixture build did not produce AMD64 PE32+")
    for i in range(count):
        section = optional + optional_size + i * 40
        name, virtual_size, rva, raw_size = struct.unpack_from("<8sIII", header, section)
        attributes, = struct.unpack_from("<I", header, section + 36)
        if name.rstrip(b"\0") == b".srr":
            if not (rva <= 0x4B3D258 < 0x82EEC30 <= rva + virtual_size <= image_size
                    and raw_size == 0 and attributes & 0x80000000 and not attributes & 0x20000000):
                raise RuntimeError("fixture .srr section must be writable, zero-filled, non-executable and cover the SRR RVAs")
            return image_size
    raise RuntimeError("fixture build did not retain its .srr section")


def build(destination=DEFAULT_OUTPUT, vcvars=None):
    if os.name != "nt" or struct.calcsize("P") != 8:
        raise RuntimeError("64-bit Windows Python is required")
    destination = Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    environment = compiler_environment(vcvars or find_vcvars())
    compiler = shutil.which("cl.exe", path=environment["PATH"])
    linker = shutil.which("link.exe", path=environment["PATH"])
    if not compiler or not linker:
        raise RuntimeError("MSVC compiler and linker did not initialize")
    source_sha256 = file_digest(SOURCE)
    response = subprocess.run(
        [compiler, *COMPILE, str(SOURCE), "/link", *LINK], cwd=destination, env=environment,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    (destination / "build.log").write_bytes(response.stdout)
    response.check_returncode()
    if file_digest(SOURCE) != source_sha256:
        raise RuntimeError("disposable fixture source changed during build")
    target = destination / "srr013-fixture.exe"
    manifest = {
        "schema": 1,
        "python_version": platform.python_version(),
        "source_sha256": source_sha256,
        "compiler_sha256": file_digest(Path(compiler)),
        "linker_sha256": file_digest(Path(linker)),
        "msvc_toolset": environment.get("VCTOOLSVERSION"),
        "windows_sdk": environment.get("WINDOWSSDKVERSION", "").rstrip("\\"),
        "compile_flags": COMPILE,
        "link_flags": LINK,
        "fixture_sha256": file_digest(target),
        "fixture_size": target.stat().st_size,
        "fixture_image_size": inspect_fixture(target),
    }
    (destination / "build-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--vcvars", type=Path)
    args = parser.parse_args()
    manifest = build(args.output, args.vcvars)
    print(f"Disposable fixture SHA-256 {manifest['fixture_sha256']}")


if __name__ == "__main__":
    main()
