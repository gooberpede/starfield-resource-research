"""Synthetic controls for the bounded component reader. Run via unittest discover."""

import struct
import unittest

from tools.srr022.records import decode_records


def component(version, mask, item_bytes=b"", auxiliary=(), trailer=(), key_low=0):
    data = struct.pack("<IHIHiI", 0x1234, key_low, mask, version, -1, len(auxiliary))
    data += b"".join(struct.pack("<I", value) for value in auxiliary)
    data += item_bytes
    if version >= 3:
        data += struct.pack("<Q", len(trailer)) + b"".join(trailer)
    return data


def population(*components):
    return struct.pack("<I", len(components)) + b"".join(components)


class TestRecords(unittest.TestCase):
    def test_version_gates_and_offsets(self):
        for version in range(4):
            with self.subTest(version=version):
                item = struct.pack("<QIB", 1, 0x2345, 0)
                if version >= 2:
                    item += bytes([25])
                if version >= 1:
                    item += struct.pack("<QI", 1, 0x3456)
                tail = (bytes(range(12)),) if version == 3 else ()
                chunk = population(component(version, 10, item, [1], tail))
                rows, end = decode_records(b"pad" + chunk + b"suffix", 3)
                self.assertEqual(end, 3 + len(chunk))
                row, = rows
                self.assertEqual((row["offset"], row["scan_level"]), (7, -1))
                self.assertEqual(row["auxiliary_ids"], [{"offset": 27, "raw": 1}])
                entry, = row["items"]
                self.assertEqual(entry["progress_21"], 0)
                self.assertEqual(entry["byte_20"], 25 if version >= 2 else None)
                self.assertEqual(entry["nested_ids"] is None, version == 0)
                if version >= 1:
                    self.assertEqual(entry["nested_ids"][0]["raw"], 0x3456)
                if version == 3:
                    self.assertEqual(bytes.fromhex(row["trailer"][0]["hex"]), tail[0])
                else:
                    self.assertIsNone(row["trailer"])

    def test_absent_and_empty(self):
        data = population(component(3, 2), component(3, 10, bytes(8), key_low=1))
        rows, end = decode_records(data)
        self.assertEqual(end, len(data))
        self.assertIsNone(rows[0]["items"])
        self.assertEqual(rows[1]["items"], [])
        self.assertEqual(decode_records(bytes(4)), ([], 4))

    def test_refusals(self):
        single = component(3, 0)
        item = struct.pack("<IBBQ", 3, 0, 1, 0)
        invalid = [
            population(single, single),
            population(component(3, 8, struct.pack("<Q", 2) + item * 2)),
            population(component(3, 8)),  # Missing count or trailer.
            population(component(2, 8, struct.pack("<Q", 1) + item[:-1])),
            population(component(3, 8, struct.pack("<Q", 2**64 - 1))),
            population(component(4, 0)),
            population(single)[:-1],
            struct.pack("<I", 2**32 - 1),
        ]
        for data in invalid:
            with self.subTest(data=data.hex()), self.assertRaises(ValueError):
                decode_records(data)
        with self.assertRaises(ValueError):
            decode_records(population(single), -1)


if __name__ == "__main__":
    unittest.main()
