"""Independent native-only FormID normalization counterexamples."""

from copy import deepcopy
import unittest

from tools.srr017.source import SourceIdentityError, bind_native_namespace


class NativeIdentityTests(unittest.TestCase):
    def setUp(self):
        self.roster = {"compiled": [
            {"plugin": "starfield.esm", "kind": "full", "index": 0},
            {"plugin": "shatteredspace.esm", "kind": "full", "index": 0x11},
            {"plugin": "medium.esm", "kind": "medium", "index": 0x82},
            {"plugin": "small.esl", "kind": "small", "index": 0xA37},
        ]}

    def test_all_native_namespace_widths_without_disk_inputs(self):
        index = bind_native_namespace(self.roster, authority="OWNED_DISPOSABLE")
        controls = (
            (0x0003F59F, "PNDT", "starfield.esm:03F59F"),
            (0x11000801, "PNDT", "shatteredspace.esm:000801"),
            (0x11012244, "BIOM", "shatteredspace.esm:012244"),
            (0xFD8298AB, "IRES", "medium.esm:0098AB"),
            (0xFEA37801, "RSGD", "small.esl:000801"),
        )
        for runtime, signature, canonical in controls:
            with self.subTest(runtime=f"{runtime:08X}"):
                row = index.resolve(runtime, signature)
                self.assertEqual(row["comparator_id"], canonical)
                self.assertEqual(row["signature"], signature)
                self.assertIsNone(row["source_record_id"])
                self.assertIsNone(row["winning_plugin"])
                self.assertEqual(row["attribution"], "WINNING_CONTENT_UNRESOLVED")

    def test_relative_directory_and_retired_stream_are_irrelevant(self):
        index = bind_native_namespace(self.roster)
        extra = deepcopy(self.roster)
        extra.update(paths={"starfield.esm": "DATA\\"}, resolved_paths={}, file_handle=None,
                     physical_sha256="not-a-hash", provider="unresolved")
        other = bind_native_namespace(extra)
        self.assertEqual(index.identity_sha256, other.identity_sha256)
        self.assertEqual(index.resolve(0x000057EA, "IRES"), other.resolve(0x000057EA, "IRES"))

    def test_vector_history_never_changes_defining_identity(self):
        index = bind_native_namespace(self.roster)
        expected = index.resolve(0x000057EA, "IRES")
        for history in (None, [], ["starfield.esm"], ["shatteredspace.esm"], ["missing.esp"]):
            index.validate_observed_sources(expected, history)
            self.assertEqual(index.resolve(0x000057EA, "IRES"), expected)

    def test_conflicting_native_slots_or_names_refuse(self):
        for extra in (
            {"plugin": "other.esm", "kind": "full", "index": 0},
            {"plugin": "starfield.esm", "kind": "full", "index": 1},
            {"plugin": "bad/path.esm", "kind": "full", "index": 1},
            {"plugin": "wrong.esm", "kind": "full", "index": 0xFD},
            {"plugin": "wrong.esm", "kind": "medium", "index": 0x100},
            {"plugin": "wrong.esm", "kind": "small", "index": 0x1000},
            {"plugin": "wrong.esm", "kind": "full", "index": True},
        ):
            roster = deepcopy(self.roster)
            roster["compiled"].append(extra)
            with self.subTest(extra=extra), self.assertRaises(SourceIdentityError):
                bind_native_namespace(roster)

    def test_invalid_formids_unassigned_namespaces_and_types_refuse(self):
        index = bind_native_namespace(self.roster)
        for runtime in (0, -1, 1 << 32, True, "000057EA", 0xFF000801, 0x01000801, 0xFD810801):
            with self.subTest(runtime=runtime), self.assertRaises(SourceIdentityError):
                index.resolve(runtime, "IRES")
        with self.assertRaisesRegex(SourceIdentityError, "unsupported_native_signature"):
            index.resolve(0x000057EA, "REFR")
        index.resolve(0x000057EA, "IRES")
        with self.assertRaisesRegex(SourceIdentityError, "native_form_type_conflict"):
            index.resolve(0x000057EA, "PNDT")

    def test_namespace_digest_is_order_independent_and_assignment_sensitive(self):
        roster = deepcopy(self.roster)
        roster["compiled"].reverse()
        self.assertEqual(bind_native_namespace(self.roster).identity_sha256,
                         bind_native_namespace(roster).identity_sha256)
        roster["compiled"][0]["index"] += 1
        self.assertNotEqual(bind_native_namespace(self.roster).identity_sha256,
                            bind_native_namespace(roster).identity_sha256)


if __name__ == "__main__":
    unittest.main()
