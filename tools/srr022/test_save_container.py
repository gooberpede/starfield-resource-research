"""Synthetic framing controls. Run with unittest discovery from tools/srr022."""

import struct
import unittest
import zlib

from tools.srr022.save_container import extract_container, inflate, locate


def pack_i(*words):
    return struct.pack(f"<{len(words)}I", *words)


def sfs_fixture():
    version = b"\x0a\x001.16.244.0"
    header = b"SFS_SAVEGAME" + pack_i(5, 27) + b"\x99\x99" + version * 2 + pack_i(0)
    first = len(header) + 100
    units = bytearray()
    for tag in range(17):
        units.extend(pack_i(tag))
        if tag in (0, 2):
            units.extend(pack_i(0))
        else:
            if tag in (1, 3):
                units.extend(b"\x04\x01\x00")  # one u16 entry
            units.extend(pack_i(1) + bytes([tag]))
    after = first + len(units)
    directory = pack_i(after + 3, after + 4, first, after, after + 1, after + 2, 17)
    return header + directory.ljust(100, b"\0") + units + b"\0" * 4


def bcps_fixture(raw):
    compressed = zlib.compress(raw)
    header = struct.pack("<4sI7Q4x4sI", b"BCPS", 1, 72, 0, 80, len(raw), 0,
                         262144, 16, b"ZIP ", len(compressed))
    source = header.ljust(80, b"\0") + compressed
    return source.ljust((len(source) + 15) & ~15, b"p")


class FramingTests(unittest.TestCase):
    def test_coordinate_round_trip(self):
        raw = sfs_fixture()
        source = bcps_fixture(raw)
        decoded, index = extract_container(source)
        self.assertEqual(decoded, raw)
        self.assertEqual(raw[index["unit_start"]:index["unit_end"]], b"\x06")
        self.assertEqual(index["units"][-1]["end"], len(raw) - 4)

    def test_compression_refusals(self):
        source = bcps_fixture(sfs_fixture())
        for field, value in ((24, 81), (32, 32), (68, 0), (72, 1), (80, 0)):
            with self.subTest(field=field):
                modified = bytearray(source)
                struct.pack_into("<I", modified, field, value)
                with self.assertRaises(ValueError):
                    inflate(modified)
        for modified in (source[:-1], source + bytes(16)):
            with self.assertRaises(ValueError):
                inflate(modified)

    def test_stream_index_and_unit_refusals(self):
        raw = sfs_fixture()
        index = locate(raw)
        for field, value in ((index["plugin_size_offset"], 9),
                             (index["flt_offset"] + 24, 18),
                             (index["units"][1]["header"] + 4, 3),
                             (index["units"][6]["header"], 5),
                             (index["units"][6]["header"] + 4, 0xffffffff),
                             (index["units"][16]["header"] + 4, 0)):
            with self.subTest(field=field):
                modified = bytearray(raw)
                struct.pack_into("<I", modified, field, value)
                with self.assertRaises(ValueError):
                    locate(modified)
