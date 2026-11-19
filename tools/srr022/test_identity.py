"""Adversarial save-local identity fixtures, constructed entirely in memory."""

import struct
import unittest

from tools.srr022.identity import IdentityMap


def fixture(values, *, full=("Base.esm", "Extra.esm"), small=(), medium=()):
    block = bytearray()
    for width, group in zip((1, 2, 4), (full, small, medium)):
        block.extend(len(group).to_bytes(width, "little"))
        for name in group:
            name = name.encode("ascii")
            block.extend(struct.pack("<H", len(name)) + name + b"\x00")
    block.extend(b"\x00\x00")
    offset = len(block) + 4
    start = offset + 100
    table = struct.pack("<II", start, start + 4 + 4 * len(values)) + bytes(92)
    array = struct.pack("<I", len(values)) + b"".join(struct.pack("<I", v) for v in values)
    return struct.pack("<I", len(block)) + block + table + array, offset


class IdentityTests(unittest.TestCase):
    def test_direct_dynamic_index_and_zero(self):
        raw, flt = fixture([0xFE000123, 0xFD00BEEF, 0, 0x01000042],
                           small=("Small.esm",), medium=("Medium.esm",))
        ids = IdentityMap.from_stream(raw, 0, flt)
        self.assertEqual(ids.resolve(0x4057D5)["normalized"], "base.esm:0057D5")
        self.assertEqual(ids.resolve(1)["normalized"], "small.esm:000123")
        self.assertEqual(ids.resolve(2)["normalized"], "medium.esm:00BEEF")
        self.assertEqual(ids.resolve(1)["array_offset"], ids.array_offset + 4)
        self.assertEqual(ids.resolve(0)["status"], "NULL_ID")
        self.assertEqual(ids.resolve(3)["status"], "NULL_ID")
        self.assertEqual(ids.resolve(0x800123)["saved_form_id"], 0xFF000123)
        for ambiguous in (0x800123, 0xC00123, 0x1000000, 0x400000, 4, 5, -1):
            self.assertIsNone(ids.resolve(ambiguous)["normalized"])

    def test_unavailable_or_ambiguous_name(self):
        raw, flt = fixture([0xFE001044])
        ids = IdentityMap.from_stream(raw, 0, flt)
        self.assertEqual(ids.resolve(1)["saved_form_id"], 0xFE001044)
        self.assertIsNone(ids.resolve(1)["normalized"])
        raw, flt = fixture([], full=("Extra.esm", "EXTRA.ESM"))
        with self.assertRaises(ValueError):
            IdentityMap.from_stream(raw, 0, flt)

    def test_full_slot_skips_leading_overlay(self):
        raw, flt = fixture([0x01000042], full=("Base.esm", "Overlay.esm", "Extra.esm"))
        ids = IdentityMap.from_stream(raw, 0, flt)
        ids.full_flags = (0x81, 0x281, 0x81)
        result = ids.resolve(1)
        self.assertEqual(result["normalized"], "extra.esm:000042")
        self.assertEqual(result["header_plugins"], ["base.esm", "overlay.esm", "extra.esm"])
        ids.full_flags = (0x81, None, 0x81)
        self.assertIsNone(ids.resolve(1)["normalized"])

    def test_array_drift(self):
        raw, flt = fixture([0xFE000123])
        with self.assertRaises(ValueError):
            IdentityMap.from_stream(raw[:-1], 0, flt)
        bad = bytearray(raw)
        struct.pack_into("<I", bad, flt + 100, 2)
        with self.assertRaisesRegex(ValueError, "form array count"):
            IdentityMap.from_stream(bad, 0, flt)
