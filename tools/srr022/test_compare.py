import struct
import unittest

from tools.srr022.compare import compare
from tools.srr022.section import locate_records, PREFIX


def component(name, offset=0, items=None):
    return {"identity": {"normalized": name}, "offset": offset, "key_low": 0,
            "mask": 8 if items is not None else 0, "scan_level": -1, "version": 3,
            "auxiliary_ids": [], "trailer": [], "items": items,
            "item_section_bit": items is not None}


class ComparisonTests(unittest.TestCase):
    def test_zero_progress_and_missing_component_or_section(self):
        item = {"identity": {"normalized": "sample:000001"}, "offset": 16,
                "progress_21": 0, "byte_20": 5, "nested_ids": []}
        left = [component("a", items=[item]), component("b"), component("c", items=[])]
        right = [component("a", items=[]), component("b", items=[])]
        diff = compare(left, right)
        self.assertEqual(diff["body_counts"], {"changed": 2, "only_left": 1})
        self.assertEqual(diff["item_counts"], {"only_left": 1})
        item_copy = dict(item, progress_21=1)
        delta = compare(left[:1], [component("a", items=[item_copy])])
        self.assertEqual(delta["item_fields_changed"], {"progress_21": 1})

    def test_unjoinable_and_duplicate(self):
        pair = compare([component(None)], [component(None)])
        self.assertEqual(pair["body_counts"], {"unjoinable_left": 1, "unjoinable_right": 1})
        with self.assertRaisesRegex(ValueError, "ambiguous normalized key"):
            compare([component("a"), component("a", 10)], [])

    def test_null_and_unresolved_reference(self):
        a, b = component("a"), component("a")
        for row in (a, b):
            row["auxiliary_ids"] = [{"identity": {"normalized": None, "status": "NULL_ID"}}]
        self.assertEqual(compare([a], [b])["body_counts"], {"equal": 1})
        b["auxiliary_ids"][0]["identity"]["status"] = "UNRESOLVED_IDENTITY"
        self.assertEqual(compare([a], [b])["body_counts"], {"indeterminate": 1})

    def test_prefix_bounds(self):
        empty = bytes(4 * (len(PREFIX) + 1))
        self.assertEqual(locate_records(empty)[0], len(empty) - 4)
        # First section: one six-byte key plus one length-prefixed string.
        sample = struct.pack("<I", 1) + bytes(6) + struct.pack("<I", 3) + b"abc" + empty[4:]
        self.assertEqual(locate_records(sample)[0], len(sample) - 4)
        for bad in (empty[:-1], sample[:15], struct.pack("<I", 0xffffffff) + empty[4:]):
            with self.assertRaises(ValueError):
                locate_records(bad)
