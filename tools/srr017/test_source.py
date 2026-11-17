"""Independent byte-level controls for source identity and the native namespace decoder."""

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import struct
import tempfile
import unittest

from tools.srr017.namespace import FormSourceVectors, NamespaceLimits, collect_namespace
from tools.srr017.source import (FILE_PROFILE_SCHEMA, NAMESPACE_SCHEMA, SourceIdentityError, SourceIndex,
                                 bind_source_files, build_manifest, load_json, snapshot_source_files)


def plugin_bytes(flags, masters, groups):
    """Author only the minimal TES4 shape needed by these controls."""
    payload = bytes.fromhex("484544520c008fc2753f0100000000080000")
    for master in masters:
        name = master.encode("ascii") + b"\0"
        payload += b"MAST" + len(name).to_bytes(2, "little") + name
    result = b"TES4" + struct.pack("<II", len(payload), flags) + bytes(12) + payload
    for signature, records in groups.items():
        entries = b"".join(signature + struct.pack("<III", 0, flag, record_id) + bytes(8)
                           for record_id, flag in records)
        result += b"GRUP" + (len(entries) + 24).to_bytes(4, "little") + signature + bytes(12) + entries
    return result


def entry(name, kind, index):
    return {"plugin": name, "kind": kind, "index": index}


class SourceIdentityTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.folder = Path(self.directory.name)
        self.paths = {
            "Starfield.esm": plugin_bytes(1, (), {b"PNDT": [(0x0801, 0)], b"BIOM": [(0x0802, 0)],
                                                 b"IRES": [(0x0803, 0)], b"RSGD": [(0x0804, 0)]}),
            "Middle.esm": plugin_bytes(0x401, ["Starfield.esm"], {b"IRES": [(0xFD000803, 0)]}),
            "ShatteredSpace.esm": plugin_bytes(1, ["Starfield.esm", "Middle.esm"],
                                               {b"PNDT": [(0x01000801, 0), (0x00000801, 0)],
                                                b"BIOM": [(0x01000802, 0)], b"IRES": [(0xFD000803, 0)]}),
            "Small.esm": plugin_bytes(0x101, ["Starfield.esm"], {b"RSGD": [(0xFE000804, 0)]}),
        }
        for name, data in self.paths.items():
            (self.folder / name).write_bytes(data)
        self.manifest = build_manifest(self.folder.iterdir())
        self.witness = {"schema": NAMESPACE_SCHEMA, "authority": "OWNED_DISPOSABLE", "plugins": [
            entry("starfield.esm", "full", 0), entry("middle.esm", "medium", 0x22),
            entry("shatteredspace.esm", "full", 0x17), entry("small.esm", "small", 0x123)]}

    def test_independent_disk_and_runtime_words(self):
        index = SourceIndex(self.manifest, self.witness)
        truth = [
            (0x00000801, "PNDT", "starfield.esm:000801", "00000801", "shatteredspace.esm"),
            (0x17000801, "PNDT", "shatteredspace.esm:000801", "01000801", "shatteredspace.esm"),
            (0x17000802, "BIOM", "shatteredspace.esm:000802", "01000802", "shatteredspace.esm"),
            (0xFD220803, "IRES", "middle.esm:000803", "FD000803", "shatteredspace.esm"),
            (0xFE123804, "RSGD", "small.esm:000804", "FE000804", "small.esm"),
        ]
        for word, signature, canonical, disk_word, winner in truth:
            with self.subTest(word=hex(word)):
                result = index.resolve(word, signature)
                self.assertEqual((result["comparator_id"], result["source_record_id"], result["winning_plugin"]),
                                 (canonical, disk_word, winner))
        self.assertEqual(index.identity_sha256,
                         SourceIndex(build_manifest(reversed(sorted(self.folder.iterdir()))), self.witness).identity_sha256)

    def test_unwitnessed_same_local_id_and_wrong_signature(self):
        index = SourceIndex(self.manifest, self.witness)
        for word, kind, reason in ((0x01000801, "PNDT", "unwitnessed_runtime_namespace"),
                                   (0x17000803, "IRES", "missing_typed_source_record"),
                                   (0xFD220803, "RSGD", "source_type_mismatch"),
                                   (0xFF000801, "PNDT", "unsupported_form_id")):
            with self.subTest(word=hex(word)), self.assertRaisesRegex(SourceIdentityError, reason):
                index.resolve(word, kind)

    def test_bad_witnesses(self):
        alternatives = [
            ("ambiguous_namespace", [entry("shatteredspace.esm", "full", 0)]),
            ("missing_plugin_source", [entry("missing.esm", "full", 4)]),
            ("source_scale_disagreement", [entry("middle.esm", "full", 4)]),
            ("invalid_namespace_slot", [entry("middle.esm", "medium", 256)]),
        ]
        for reason, addition in alternatives:
            witness = {**self.witness, "plugins": self.witness["plugins"][:1] + addition}
            with self.subTest(reason=reason), self.assertRaisesRegex(SourceIdentityError, reason):
                SourceIndex(self.manifest, witness)
        reversed_order = {**self.witness, "plugins": self.witness["plugins"][::-1]}
        with self.assertRaisesRegex(SourceIdentityError, "unknown_master_or_precedence"):
            SourceIndex(self.manifest, reversed_order)

    def test_typed_override_collision_and_tombstone(self):
        manifest = deepcopy(self.manifest)
        shattered = next(plugin for plugin in manifest["files"] if plugin["plugin"] == "shatteredspace.esm")
        override = next(record for record in shattered["records"] if record[1] == 0x00000801)
        override[0] = "BIOM"
        with self.assertRaisesRegex(SourceIdentityError, "canonical_source_collision"):
            SourceIndex(manifest, self.witness)
        override[:] = ["PNDT", 0x00000801, 0x20]
        with self.assertRaisesRegex(SourceIdentityError, "deleted_winning_source_record"):
            SourceIndex(manifest, self.witness).resolve(0x801, "PNDT")
        shattered["records"].append(["IRES", 0x00000801, 0])
        with self.assertRaisesRegex(SourceIdentityError, "duplicate_source_record_id"):
            SourceIndex(manifest, self.witness)

    def test_ambiguous_json_and_malformed_group(self):
        file = self.folder / "dup.json"
        file.write_bytes(b'{"schema": 1, "schema": 1}')
        with self.assertRaisesRegex(SourceIdentityError, "ambiguous_json_member"):
            load_json(file)
        path = self.folder / "Starfield.esm"
        path.write_bytes(path.read_bytes()[:-1])
        with self.assertRaisesRegex(SourceIdentityError, "invalid_top_level_group"):
            build_manifest([path])

    def file_profile(self):
        return {"schema": FILE_PROFILE_SCHEMA, "files": [
            {"plugin": name.lower(), "path": str(self.folder.resolve() / name),
             "bytes": len(data), "sha256": sha256(data).hexdigest()} for name, data in self.paths.items()
        ]}

    def test_pinned_binding_canonical_identity_without_winner_order(self):
        profile = self.file_profile()
        snapshot = snapshot_source_files(profile)
        namespace = {"compiled": self.witness["plugins"][::-1],
                     "paths": {item["plugin"]: str(self.folder.resolve()) for item in profile["files"]}}
        index = bind_source_files(namespace, snapshot, authority="OWNED_DISPOSABLE")
        self.assertEqual(snapshot_source_files(profile), snapshot)
        for runtime, sig, canon in ((0x0801, "PNDT", "starfield.esm:000801"),
                                    (0x17000801, "PNDT", "shatteredspace.esm:000801"),
                                    (0xFD220803, "IRES", "middle.esm:000803"),
                                    (0xFE123804, "RSGD", "small.esm:000804")):
            with self.subTest(runtime=hex(runtime)):
                result = index.resolve(runtime, sig)
                self.assertEqual(result["comparator_id"], canon)
                self.assertIsNone(result["winning_plugin"])
        base = index.resolve(0x0801, "PNDT")
        for observed in (None, [], ["starfield.esm"], ["shatteredspace.esm"],
                         ["starfield.esm", "shatteredspace.esm"]):
            index.validate_observed_sources(base, observed)
        with self.assertRaisesRegex(SourceIdentityError, "native_source_identity_conflict"):
            index.validate_observed_sources(base, ["middle.esm"])

    def test_paths_refuse_swaps_relative_and_missing_files(self):
        profile = self.file_profile()
        snapshot = snapshot_source_files(profile)
        directories = {item["plugin"]: str(self.folder.resolve()) for item in profile["files"]}
        slots = self.witness["plugins"]
        for path, code in (
            (str(self.folder.resolve() / "another"), "native_source_path_disagreement"),
            ("Data\\", "unresolved_native_source_path"),
        ):
            with self.subTest(code=code), self.assertRaisesRegex(SourceIdentityError, code):
                bind_source_files({"compiled": slots, "paths": {**directories, "starfield.esm": path}}, snapshot)
        with self.assertRaisesRegex(SourceIdentityError, "incomplete_native_source_paths"):
            bind_source_files({"compiled": slots, "paths": {}}, snapshot)
        missing = {"compiled": slots + [entry("absent.esm", "full", 5)],
                   "paths": {**directories, "absent.esm": str(self.folder.resolve())}}
        with self.assertRaisesRegex(SourceIdentityError, "missing_plugin_source"):
            bind_source_files(missing, snapshot)
        forged = deepcopy(snapshot)
        forged["files"][0]["path"] = str(self.folder.resolve() / "another" / "Starfield.esm")
        with self.assertRaisesRegex(SourceIdentityError, "source_profile_digest_mismatch"):
            bind_source_files({"compiled": slots, "paths": directories}, forged)

    def test_relative_descriptor_with_independent_open_stream_path(self):
        profile = self.file_profile()
        snapshot = snapshot_source_files(profile)
        directories = {item["plugin"]: str(self.folder.resolve()) for item in profile["files"]}
        ns = {"compiled": self.witness["plugins"], "paths": {**directories, "starfield.esm": "Data\\"},
              "resolved_paths": {"starfield.esm": profile["files"][0]["path"]}}
        result = bind_source_files(ns, snapshot, authority="OWNED_DISPOSABLE")
        self.assertEqual(result.provenance["path_witnesses"]["starfield.esm"], "RETAINED_OPEN_STREAM")
        with self.assertRaisesRegex(SourceIdentityError, "unexpected_native_stream_path"):
            bind_source_files({**ns, "paths": directories}, snapshot)
        wrong_file = {**ns, "resolved_paths": {"starfield.esm": profile["files"][1]["path"]}}
        with self.assertRaisesRegex(SourceIdentityError, "native_source_path_disagreement"):
            bind_source_files(wrong_file, snapshot)

    def test_changed_bytes_size_and_cancellation(self):
        profile = self.file_profile()
        path = self.folder / "Starfield.esm"
        first = path.read_bytes()
        path.write_bytes(first[:-1] + b"X")
        with self.assertRaisesRegex(SourceIdentityError, "source_file_digest_mismatch"):
            snapshot_source_files(profile)
        path.write_bytes(first[:-1])
        with self.assertRaisesRegex(SourceIdentityError, "source_file_size_mismatch"):
            snapshot_source_files(profile)
        with self.assertRaisesRegex(SourceIdentityError, "source_file_cancelled"):
            snapshot_source_files(profile, cancelled=lambda: True)


def native_bytes():
    """Construct explicit bytes with shuffled registry positions and a hole in the full array."""
    sections = {
        0x145FD9B28: struct.pack("<Q", 0x220000),
        0x221570: struct.pack("<QQIIQIIQIIQ", 0x444000, 0x330000,
                             3, 8, 0x331000, 1, 4, 0x332000, 1, 4, 0x333000),
        0x330000: struct.pack("<QQ", 0x440000, 0x330010),
        0x330010: struct.pack("<QQ", 0x442000, 0x330020),
        0x330020: struct.pack("<QQ", 0x443000, 0x330030),
        0x330030: struct.pack("<QQ", 0x441000, 0),
        0x331000: struct.pack("<QQQ", 0x440000, 0, 0x441000),
        0x332000: struct.pack("<Q", 0x442000),
        0x333000: struct.pack("<Q", 0x443000),
    }
    files = [
        ("Starfield.esm", 0x81, bytes.fromhex("00000000")),
        ("ShatteredSpace.esm", 0x81, bytes.fromhex("02000000")),
        ("Small.esm", 0x181, bytes.fromhex("fe000000")),
        ("Medium.esm", 0x481, bytes.fromhex("fd000000")),
        ("Inactive.esm", 0x81, bytes.fromhex("ff000000")),
    ]
    for i, (name, flags, index) in enumerate(files):
        fields = bytearray(0x1E4)
        fields[:len(name)] = name.encode("ascii")
        fields[0x180:0x184] = flags.to_bytes(4, "little")
        fields[0x1E0:0x1E4] = index
        sections[0x440038 + i * 0x1000] = fields
    return sections


def read_sections(sections):
    return lambda address, width, label: bytes(sections.get(address, b"")[:width])


class NamespaceDecoderTests(unittest.TestCase):
    def test_three_scales_and_inactive_registry_file(self):
        observed = collect_namespace(read_sections(native_bytes()), 0x140000000)
        self.assertEqual(observed["compiled"], [
            entry("starfield.esm", "full", 0), entry("shatteredspace.esm", "full", 2),
            entry("small.esm", "small", 0), entry("medium.esm", "medium", 0)])
        self.assertEqual(observed["registry"][0]["plugin"], "inactive.esm")
        self.assertEqual((observed["slot_count"], observed["reads"], observed["requested_bytes"]), (5, 14, 2596))

    def test_native_packed_file_paths_and_vtable(self):
        sections = native_bytes()
        for idx in range(4):
            sections[0x440000 + idx * 0x1000] = struct.pack("<Q", 0x144B29B80)
            sections[0x440268 + idx * 0x1000] = f"D:\\Sources{idx}\\".encode("ascii").ljust(260, b"\0")
        observed = collect_namespace(read_sections(sections), 0x140000000, include_paths=True)
        self.assertEqual(observed["paths"], {
            "starfield.esm": "D:\\Sources0\\", "shatteredspace.esm": "D:\\Sources1\\",
            "small.esm": "D:\\Sources2\\", "medium.esm": "D:\\Sources3\\",
        })
        self.assertEqual((observed["reads"], observed["requested_bytes"]), (22, 3668))
        wrong_vptr = {**sections, 0x440000: struct.pack("<Q", 0x144B29A70)}
        with self.assertRaisesRegex(SourceIdentityError, "namespace_unknown_file_class"):
            collect_namespace(read_sections(wrong_vptr), 0x140000000, include_paths=True)
        bad_directory = {**sections, 0x440268: b"x" * 260}
        with self.assertRaisesRegex(SourceIdentityError, "namespace_invalid_file_directory"):
            collect_namespace(read_sections(bad_directory), 0x140000000, include_paths=True)

    def test_retained_backing_stream_and_retirement(self):
        sections = native_bytes()
        for idx in range(4):
            sections[0x440000 + idx * 0x1000] = struct.pack("<Q", 0x144B29B80)
            sections[0x440268 + idx * 0x1000] = b"D:\\Sources\\".ljust(260, b"\0")
        sections[0x440268] = b"Data\\".ljust(260, b"\0")
        sections[0x440378] = struct.pack("<Q", 0x660000)
        stream = bytearray(0x170)
        struct.pack_into("<Q", stream, 0, 0x144DA7FB8)
        stream[0x4C] = 1
        backing = b"D:\\Effective\\Starfield.esm\0"
        stream[0x6C:0x6C + len(backing)] = backing
        sections[0x660000] = stream
        found = collect_namespace(read_sections(sections), 0x140000000, include_paths=True)
        self.assertEqual(found["resolved_paths"], {"starfield.esm": "D:\\Effective\\Starfield.esm"})
        self.assertEqual((found["reads"], found["requested_bytes"]), (24, 4044))
        stream[0x4C] = 0
        closed = collect_namespace(read_sections(sections), 0x140000000, include_paths=True)
        self.assertFalse(closed["resolved_paths"])
        sections[0x440378] = bytes(8)
        retired = collect_namespace(read_sections(sections), 0x140000000, include_paths=True)
        self.assertFalse(retired["resolved_paths"])
        self.assertEqual(retired["paths"]["starfield.esm"], "Data\\")

    def test_mutated_native_windows(self):
        controls = [
            (0x331000, struct.pack("<QQQ", 0x440000, 0x440000, 0x441000), "namespace_plugin_pointer_alias"),
            (0x331000, struct.pack("<QQQ", 0x445000, 0, 0x441000), "namespace_plugin_outside_registry"),
            (0x330030, struct.pack("<QQ", 0x441000, 0x330000), "namespace_registry_cycle"),
            (0x333000, bytes(4), "namespace_partial_read"),
        ]
        for address, replacement, reason in controls:
            with self.subTest(reason=reason), self.assertRaisesRegex(SourceIdentityError, reason):
                collect_namespace(read_sections({**native_bytes(), address: replacement}), 0x140000000)
        sections = native_bytes()
        sections[0x443038][-4] = 0xFE
        with self.assertRaisesRegex(SourceIdentityError, "namespace_file_slot_disagreement"):
            collect_namespace(read_sections(sections), 0x140000000)
        for limits, reason in ((NamespaceLimits(slots=4), "namespace_slot_budget"),
                               (NamespaceLimits(registry_nodes=4), "namespace_registry_budget"),
                               (NamespaceLimits(requested_bytes=150), "namespace_read_budget")):
            with self.subTest(reason=reason), self.assertRaisesRegex(SourceIdentityError, reason):
                collect_namespace(read_sections(native_bytes()), 0x140000000, limits)

    def test_form_source_vectors_and_corrupt_witnesses(self):
        sections = {**native_bytes(),
                    0x145E881E8: struct.pack("<I4xQ", 3, 0x550000),
                    0x550008: struct.pack("<Q", 0x551000),
                    0x551000: struct.pack("<QI4x", 0x552000, 2),
                    0x552000: struct.pack("<QQ", 0x440000, 0x441000),
                    0x660030: b"\x01\x00",
                    0x661030: b"\x01\x00",
                    0x662030: b"\xFF\xFF"}
        namespace = collect_namespace(read_sections(sections), 0x140000000)
        vectors = FormSourceVectors(read_sections(sections), 0x140000000, namespace)
        self.assertEqual(vectors.lookup(0x660000), ("starfield.esm", "shatteredspace.esm"))
        self.assertEqual(vectors.lookup(0x661000), ("starfield.esm", "shatteredspace.esm"))
        self.assertIsNone(vectors.lookup(0x662000))
        self.assertEqual((vectors.reads, vectors.requested_bytes), (7, 62))
        controls = [
            (0x660030, b"\x03\x00", "source_vector_index_range"),
            (0x552000, struct.pack("<QQ", 0x440000, 0x444000), "source_vector_namespace_disagreement"),
            (0x551000, struct.pack("<QI4x", 0x552000, 65), "source_vector_width"),
            (0x550008, bytes(8), "invalid_source_vector_pointer"),
        ]
        for address, replacement, reason in controls:
            with self.subTest(reason=reason), self.assertRaisesRegex(SourceIdentityError, reason):
                FormSourceVectors(read_sections({**sections, address: replacement}), 0x140000000,
                                  namespace).lookup(0x660000)
        with self.assertRaisesRegex(SourceIdentityError, "source_vector_read_budget"):
            FormSourceVectors(read_sections(sections), 0x140000000, namespace,
                              byte_limit=24).lookup(0x660000)


if __name__ == "__main__":
    unittest.main()
