"""Extract the bounded unit-6 payload coordinates in the two studied SFS profiles."""

import struct
import zlib


def _bounded(data, start, size, end):
    if not 0 <= start <= start + size <= end <= len(data):
        raise ValueError(f"Field outside its declared bounds at {start:#x} (+{size:#x})")
    return memoryview(data)[start:start + size]


def _uint(data, start, size, end):
    return int.from_bytes(_bounded(data, start, size, end), "little")


def _align16(value):
    return (value + 15) & ~15


def inflate(source):
    """Validate BCPS framing, zlib checksums, output lengths and aligned EOF."""
    if len(source) < 72 or source[:8] != b"BCPS\x01\0\0\0" or source[68:72] != b"ZIP ":
        raise ValueError("Unsupported BCPS compression profile")
    table, _, first, total, _, block, alignment = struct.unpack_from("<7Q", source, 8)
    if (table, block, alignment) != (72, 262144, 16) or total == 0:
        raise ValueError("Unsupported block table, block size or alignment")
    count = (total + block - 1) // block
    if first != _align16(table + 4 * count) or first > len(source):
        raise ValueError("Invalid compressed stream index")
    output = bytearray()
    chunks = []
    physical = first
    for i in range(count):
        size = _uint(source, table + 4 * i, 4, first)
        compressed = _bounded(source, physical, size, len(source))
        expected = min(block, total - len(output))
        decoder = zlib.decompressobj()
        try:
            piece = decoder.decompress(compressed, expected + 1)
        except zlib.error as exc:
            raise ValueError(f"Invalid zlib stream at {physical:#x}") from exc
        if (len(piece) != expected or not decoder.eof or decoder.unused_data
                or decoder.unconsumed_tail):
            raise ValueError(f"Compressed stream does not close at {physical:#x}")
        chunks.append({"physical": physical, "compressed_size": size,
                       "decoded": len(output), "decoded_size": expected})
        output.extend(piece)
        physical = _align16(physical + size)
    if physical != len(source):
        raise ValueError("Physical EOF differs from final aligned block end")
    return bytes(output), chunks


def locate(raw):
    """Walk from the SFS header through table 1, validating all unit boundaries."""
    end = len(raw)
    if raw[:12] != b"SFS_SAVEGAME" or _uint(raw, 16, 4, end) != 27:
        raise ValueError("Unsupported SFS header")
    header_end = 16 + _uint(raw, 12, 4, end)
    if header_end < 21 or _uint(raw, header_end, 1, end) != 153:
        raise ValueError("Unsupported save format")
    pos = header_end + 1
    for _ in range(2):
        size = _uint(raw, pos, 2, end)
        if _bounded(raw, pos + 2, size, end) != b"1.16.244.0":
            raise ValueError("Unsupported recorded version string")
        pos += 2 + size
    plugin_size_offset = pos
    plugin_size = _uint(raw, pos, 4, end)
    plugins_start = pos + 4
    flt = plugins_start + plugin_size
    directory = _bounded(raw, flt, 100, end)
    forms, following, table1, table2, changes, table3, count = struct.unpack_from("<7I", directory)
    if not (flt + 100 == table1 < table2 < changes < table3 < forms < following <= end):
        raise ValueError("Non-monotonic or displaced save sections")
    if count != 17:
        raise ValueError("Unsupported first global table unit count")
    pos = table1
    units = []
    for expected in range(count):
        header = pos
        tag = _uint(raw, pos, 4, table2)
        if tag != expected:
            raise ValueError(f"Expected global unit {expected} at {header:#x}, found {tag}")
        pos += 4
        if tag in (0, 2):
            # Dedicated writer/reader; the following word is not a payload length.
            size = 4
        else:
            if tag in (1, 3):
                # Mode 0x0C writes a variable count, u16 array, then a sized block.
                code = _uint(raw, pos, 1, table2) & 3
                if code == 3:
                    raise ValueError(f"Reserved compact-count tag at {pos:#x}")
                width = 1 << code
                entries = _uint(raw, pos, width, table2) >> 2
                pos += width + entries * 2
            size = _uint(raw, pos, 4, table2)
            pos += 4
        _bounded(raw, pos, size, table2)
        units.append({"tag": tag, "header": header, "data": pos, "end": pos + size})
        pos += size
    if pos != table2:
        raise ValueError("First global table does not close at the next directory entry")
    return {"unit_start": units[6]["data"], "unit_end": units[6]["end"],
            "plugin_size_offset": plugin_size_offset, "plugins_start": plugins_start,
            "plugins_end": flt, "flt_offset": flt, "forms_start": forms,
            "forms_end": following, "units": units}


def extract_container(source):
    """Return the inflated stream and its physical/decoded coordinate index."""
    raw, chunks = inflate(source)
    return raw, {**locate(raw), "chunks": chunks}
