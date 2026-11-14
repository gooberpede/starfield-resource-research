"""Generate SRR-006's offline retail code-window manifest from a lawful PE."""
import argparse
import hashlib
import json
from pathlib import Path
import struct


PIN = "7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28"
BASE = 0x140000000
EXTENT = 0x89C2000
# These windows cover the four sites and the static relationships needed for
# the caller-return and frame predicates. Ranges are half-open.
WINDOWS = (
    (0x9518FB, 0x95190A), (0x593280, 0x5932FF), (0x77C470, 0x77C491),
    (0x779760, 0x779780), (0x94E542, 0x94E57C), (0x94EF37, 0x94EF5C),
    (0x779610, 0x7796D7),
)
DATA_WINDOWS = (
    (0x85F1398, 0x85F13B0), (0x85F1500, 0x85F150C),
)
EDGES = (
    (0x94E577, 0x593280), (0x94EF57, 0x593280), (0x77C482, 0x779610),
    (0x7796D2, 0x779760),
)


def manifest(path):
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != PIN:
        raise ValueError(f"retail image hash mismatch ({digest})")
    pe, = struct.unpack_from("<I", data, 0x3C)
    machine, count = struct.unpack_from("<HH", data, pe + 4)
    optional_size, = struct.unpack_from("<H", data, pe + 20)
    optional = pe + 24
    magic, = struct.unpack_from("<H", data, optional)
    base, = struct.unpack_from("<Q", data, optional + 24)
    extent, headers = struct.unpack_from("<II", data, optional + 56)
    if (data[pe:pe + 4], machine, magic, base, extent) != (b"PE\0\0", 0x8664, 0x20B, BASE, EXTENT):
        raise ValueError("unexpected PE mapping")
    sections = [struct.unpack_from("<IIII", data, optional + optional_size + i*40 + 8)
                for i in range(count)]

    def read(rva, size):
        if 0 <= rva <= headers and 0 < size <= headers - rva:
            return data[rva:rva + size]
        for _, start, raw_size, raw_offset in sections:
            if start <= rva and rva + size <= start + raw_size:
                index = raw_offset + rva - start
                return data[index:index + size]
        raise ValueError(f"RVA {rva:#x} has no disk bytes")

    for site, target in EDGES:
        op, offset = struct.unpack("<Bi", read(site, 5))
        if op != 0xE8 or site + 5 + offset != target:
            raise ValueError(f"unexpected direct call at {site:#x}")
    if read(0x5932EF, 3) != bytes.fromhex("ff5010"):
        raise ValueError("unexpected iterator dispatch")
    slots = (0x4B3D9F0, 0x4B3D9F8)
    for slot in slots:
        if struct.unpack("<Q", read(slot, 8))[0] != BASE + 0x77C470:
            raise ValueError("unexpected vtable slot")
    # Include each saved-runtime-function record's referenced unwind header.
    runtime_records = (0x85F1398, 0x85F13A4, 0x85F1500)
    unwind = []
    for record, entry in zip(runtime_records, (0x779610, 0x779760, 0x77C470), strict=True):
        begin, end, info = struct.unpack("<III", read(record, 12))
        if begin != entry or not begin < end <= extent:
            raise ValueError("unexpected runtime-function entry")
        _, _, codes, _ = read(info, 4)
        unwind.append((info, info + 4 + ((codes + 1) & ~1)*2))
    if pe + 24 + optional_size + count*40 > headers:
        raise ValueError("section headers exceed mapped PE headers")
    dll_flags, = struct.unpack_from("<H", data, optional + 70)
    if not dll_flags & 0x40:
        raise ValueError("image lacks dynamic-base support")
    reloc, reloc_length = struct.unpack_from("<II", data, optional + 112 + 5*8)
    relocs = read(reloc, reloc_length)
    positions = {}
    offset = 0
    while offset < len(relocs):
        page, size = struct.unpack_from("<II", relocs, offset)
        if page & 0xfff or size < 8 or size % 4 or size > len(relocs) - offset:
            raise ValueError("invalid relocation block")
        for entry, in struct.iter_unpack("<H", relocs[offset+8:offset+size]):
            kind = entry >> 12
            if kind == 0:
                continue
            rva = page + (entry & 0xfff)
            if kind != 10 or rva > extent - 8 or rva in positions:
                raise ValueError("unexpected relocation")
            positions[rva] = kind
        offset += size
    if any(positions.get(slot) != 10 for slot in slots):
        raise ValueError("vtable slot is missing its DIR64 relocation")
    windows = [(start, end, True) for start, end in WINDOWS]
    windows += [(start, end, False) for start, end in ((0, headers),) + DATA_WINDOWS + tuple(unwind)]
    if any(start < rva + 8 and rva < end for start, end, _ in windows for rva in positions):
        raise ValueError("immutable window overlaps a base relocation")
    profile = {
        "schema": 2, "sha256": digest, "file_size": len(data), "preferred_base": BASE, "extent": EXTENT,
        "windows": [{"rva": start, "size": end - start, "executable": executable,
                     "sha256": hashlib.sha256(read(start, end - start)).hexdigest()}
                    for start, end, executable in windows],
        "relocated_slots": [{"rva": slot, "target_rva": 0x77C470, "width": 8} for slot in slots],
    }
    canonical = json.dumps(profile, separators=(",", ":"), sort_keys=True).encode("ascii")
    profile["profile_sha256"] = hashlib.sha256(canonical).hexdigest()
    return profile


def header(profile):
    windows = "\n".join(
        f'    {{0x{w["rva"]:X}, {w["size"]}, "{w["sha256"]}", {str(w["executable"]).lower()}}},'
        for w in profile["windows"]
    )
    slots = "\n".join(
        f'    {{0x{s["rva"]:X}, 0x{s["target_rva"]:X}}},'
        for s in profile["relocated_slots"]
    )
    return f'''// Generated by pin_pe.py --format header from the lawful pinned image.
// Only derived hashes and address metadata are included.
#pragma once

namespace srr006 {{
inline constexpr ImageWindow retail_windows[] = {{
{windows}
}};
inline constexpr ImageSlot retail_slots[] = {{
{slots}
}};
inline constexpr ImageProfile retail_image_profile{{
    "{profile["sha256"]}",
    "{profile["profile_sha256"]}",
    {profile["file_size"]}, 0x{profile["preferred_base"]:X}, 0x{profile["extent"]:X},
    retail_windows, retail_slots
}};
}} // namespace srr006'''


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--format", choices=("json", "header"), default="json")
    parser.add_argument("--self-test", action="store_true", help="compare the generated header to the checked-in pin")
    args = parser.parse_args()
    profile = manifest(args.image)
    if args.self_test:
        generated = Path(__file__).with_name("retail_manifest.h")
        if generated.read_text(encoding="utf-8") != header(profile) + "\n":
            parser.error("generated manifest differs from retail_manifest.h")
    print(header(profile) if args.format == "header" else json.dumps(profile, indent=2))
