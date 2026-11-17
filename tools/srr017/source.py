"""Build a typed Starfield plugin inventory and join it to a separate namespace witness."""

import argparse
from collections import Counter
from hashlib import file_digest, sha256
import json
import ntpath
import os
from pathlib import Path, PureWindowsPath
import re
import stat
from struct import Struct


MANIFEST_SCHEMA = "srr017-source-manifest-v1"
NAMESPACE_SCHEMA = "srr017-namespace-v1"
FILE_PROFILE_SCHEMA = "srr017-source-files-v1"
SIGNATURES = frozenset(("PNDT", "BIOM", "RSGD", "IRES"))
INDEX_MAX = {"full": 0xFC, "medium": 0xFF, "small": 0xFFF}
LOCAL_MASK = {"full": 0xFFFFFF, "medium": 0xFFFF, "small": 0xFFF}
MAX_PLUGINS = sum(limit + 1 for limit in INDEX_MAX.values())
MAX_RECORDS = 1_000_000
MAX_MANIFEST_BYTES = 64 * 1024 * 1024
MAX_SOURCE_FILES = 256
MAX_SOURCE_BYTES = 4 * 1024 * 1024 * 1024
MAX_GROUPS_PER_FILE = 4096
SOURCE_HASH_CHUNK = 1024 * 1024
HEADER = Struct("<4s5I")
SUBRECORD = Struct("<4sH")
NAME = re.compile(r"[a-z0-9][a-z0-9 _.'()-]{0,191}\.(?:esm|esp|esl)")
DIGEST = re.compile(r"[0-9a-f]{64}")


class SourceIdentityError(ValueError):
    def __init__(self, code, detail):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=True, allow_nan=False).encode("ascii")).hexdigest()


def _integer(value, ceiling):
    return type(value) is int and 0 <= value <= ceiling


def _plugin(name):
    if not isinstance(name, str) or not NAME.fullmatch(name):
        raise SourceIdentityError("unsupported_plugin_name", repr(name))
    return name


def _kind(plugin, flags):
    if flags & 0x500 == 0x500:
        raise SourceIdentityError("conflicting_plugin_scale", plugin)
    if plugin.endswith(".esl") or flags & 0x100:
        return "small"
    return "medium" if flags & 0x400 else "full"


def _split(form_id):
    if not _integer(form_id, 0xFFFFFFFF) or form_id == 0 or form_id >> 24 == 0xFF:
        raise SourceIdentityError("unsupported_form_id", f"{form_id!r}")
    high = form_id >> 24
    if high == 0xFD:
        return "medium", (form_id >> 16) & 0xFF, form_id & 0xFFFF
    if high == 0xFE:
        return "small", (form_id >> 12) & 0xFFF, form_id & 0xFFF
    return "full", high, form_id & 0xFFFFFF


def _fingerprint(info):
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns


def _read_exact(stream, size):
    data = stream.read(size)
    if len(data) != size:
        raise SourceIdentityError("source_short_read", str(size))
    return data


def _masters(data):
    masters = []
    cursor = 0
    while cursor < len(data):
        if len(data) - cursor < SUBRECORD.size:
            raise SourceIdentityError("truncated_tes4_field", str(cursor))
        kind, size = SUBRECORD.unpack_from(data, cursor)
        cursor += SUBRECORD.size
        if kind == b"XXXX":
            if size != 4 or cursor + 4 + SUBRECORD.size > len(data):
                raise SourceIdentityError("invalid_extended_tes4_field", str(cursor))
            size = int.from_bytes(data[cursor:cursor + 4], "little")
            cursor += 4
            kind, nominal = SUBRECORD.unpack_from(data, cursor)
            if kind in (b"XXXX", b"MAST") or nominal not in (0, size):
                raise SourceIdentityError("invalid_extended_tes4_field", str(cursor))
            cursor += SUBRECORD.size
        end = cursor + size
        if end > len(data):
            raise SourceIdentityError("truncated_tes4_field", str(cursor))
        if kind == b"MAST":
            field = data[cursor:end]
            if not field.endswith(b"\0") or b"\0" in field[:-1] or not field.isascii():
                raise SourceIdentityError("invalid_tes4_master", str(cursor))
            masters.append(_plugin(field[:-1].decode("ascii").lower()))
        cursor = end
    return masters


def _target_headers(stream, file_size, check=None):
    signatures = {signature.encode("ascii") for signature in SIGNATURES}
    visited_groups = set()
    group_count = 0
    while stream.tell() < file_size:
        if check is not None:
            check()
        group_count += 1
        if group_count > MAX_GROUPS_PER_FILE:
            raise SourceIdentityError("source_group_limit", "too many top-level groups")
        start = stream.tell()
        kind, size, label, group_type, _, _ = HEADER.unpack(_read_exact(stream, HEADER.size))
        end = start + size
        if kind != b"GRUP" or group_type != 0 or not start + HEADER.size <= end <= file_size:
            raise SourceIdentityError("invalid_top_level_group", f"offset {start:#x}")
        signature = label.to_bytes(4, "little")
        if signature in signatures:
            if signature in visited_groups:
                raise SourceIdentityError("duplicated_target_group", signature.decode("ascii"))
            visited_groups.add(signature)
            while stream.tell() < end:
                if check is not None:
                    check()
                record_start = stream.tell()
                kind, payload_size, flags, form_id, _, _ = HEADER.unpack(_read_exact(stream, HEADER.size))
                if kind != signature or record_start + HEADER.size + payload_size > end:
                    raise SourceIdentityError("invalid_target_record", f"offset {record_start:#x}")
                yield [signature.decode("ascii"), form_id, flags]
                stream.seek(payload_size, os.SEEK_CUR)
        stream.seek(end)


def inspect_plugin(path, *, expected_bytes=None, check=None):
    """Read one on-disk plugin and detect file identity changes during the scan."""
    path = Path(path)
    name = _plugin(path.name.lower())
    path_before = _fingerprint(path.stat())
    if expected_bytes is not None and path_before[2] != expected_bytes:
        raise SourceIdentityError("source_file_size_mismatch", name)
    with path.open("rb") as stream:
        before = _fingerprint(os.fstat(stream.fileno()))
        if before[:4] != path_before[:4]:
            raise SourceIdentityError("source_file_changed", name)
        kind, size, flags, form_id, _, _ = HEADER.unpack(_read_exact(stream, HEADER.size))
        if kind != b"TES4" or form_id or not 0 < size <= min(before[2] - HEADER.size, 16 * 1024 * 1024):
            raise SourceIdentityError("invalid_tes4_header", name)
        masters = _masters(_read_exact(stream, size))
        records = []
        for record in _target_headers(stream, before[2], check):
            if len(records) >= MAX_RECORDS:
                raise SourceIdentityError("source_record_limit", name)
            records.append(record)
        stream.seek(0)
        if expected_bytes is None:
            fingerprint = file_digest(stream, "sha256").hexdigest()
        else:
            hasher = sha256()
            remaining = expected_bytes
            while remaining:
                if check is not None:
                    check()
                block = _read_exact(stream, min(remaining, SOURCE_HASH_CHUNK))
                hasher.update(block)
                remaining -= len(block)
            fingerprint = hasher.hexdigest()
        if before != _fingerprint(os.fstat(stream.fileno())) or path_before != _fingerprint(path.stat()):
            raise SourceIdentityError("source_file_changed", name)
    item = {"plugin": name, "sha256": fingerprint, "bytes": before[2], "flags": flags,
            "masters": masters, "records": sorted(records, key=lambda row: row[1])}
    return item if expected_bytes is None else (item, list(before))


def build_manifest(paths):
    files = []
    count = 0
    for path in paths:
        if len(files) >= MAX_PLUGINS:
            raise SourceIdentityError("source_plugin_limit", "too many input files")
        item = inspect_plugin(path)
        count += len(item["records"])
        if count > MAX_RECORDS:
            raise SourceIdentityError("source_record_limit", "too many target headers")
        files.append(item)
    manifest = {"schema": MANIFEST_SCHEMA, "files": sorted(files, key=lambda item: item["plugin"])}
    _validate_manifest(manifest)
    return manifest


def _validate_manifest(manifest):
    if (not isinstance(manifest, dict) or set(manifest) != {"schema", "files"}
            or manifest["schema"] != MANIFEST_SCHEMA or not isinstance(manifest["files"], list)
            or not 0 < len(manifest["files"]) <= MAX_PLUGINS):
        raise SourceIdentityError("invalid_source_manifest", MANIFEST_SCHEMA)
    files = {}
    count = 0
    for file in manifest["files"]:
        if not isinstance(file, dict) or set(file) != {"plugin", "sha256", "bytes", "masters", "records", "flags"}:
            raise SourceIdentityError("invalid_source_manifest", "file fields")
        name = _plugin(file["plugin"])
        if (name in files or not isinstance(file["sha256"], str) or not DIGEST.fullmatch(file["sha256"])
                or not _integer(file["bytes"], 1 << 40) or file["bytes"] < HEADER.size
                or not _integer(file["flags"], 0xFFFFFFFF) or not isinstance(file["masters"], list)
                or len(file["masters"]) > MAX_PLUGINS or not isinstance(file["records"], list)):
            raise SourceIdentityError("invalid_source_manifest", name)
        count += len(file["records"])
        if count > MAX_RECORDS:
            raise SourceIdentityError("source_record_limit", name)
        masters = [_plugin(master) for master in file["masters"]]
        if name in masters or len(set(masters)) != len(masters):
            raise SourceIdentityError("invalid_master_list", name)
        _kind(name, file["flags"])
        seen_ids = set()
        for record in file["records"]:
            if (not isinstance(record, list) or len(record) != 3 or not isinstance(record[0], str)
                    or record[0] not in SIGNATURES or not _integer(record[1], 0xFFFFFFFF)
                    or not _integer(record[2], 0xFFFFFFFF)):
                raise SourceIdentityError("invalid_source_record", name)
            if record[1] in seen_ids:
                raise SourceIdentityError("duplicate_source_record_id", f"{name}:{record[1]:08X}")
            seen_ids.add(record[1])
        files[name] = file
    return files


def _absolute_path(value):
    if not isinstance(value, str) or not value.isascii() or any(ord(char) < 32 for char in value):
        raise SourceIdentityError("invalid_source_path", "expected an ASCII local absolute path")
    path = PureWindowsPath(value)
    if not path.is_absolute() or not re.fullmatch(r"[A-Za-z]:", path.drive) or ".." in path.parts:
        raise SourceIdentityError("unresolved_native_source_path", value)
    if any(part.endswith((" ", ".")) or ":" in part for part in path.parts[1:]):
        raise SourceIdentityError("invalid_source_path_component", value)
    return path


def _file_profile(profile):
    if (not isinstance(profile, dict) or set(profile) != {"schema", "files"}
            or profile["schema"] != FILE_PROFILE_SCHEMA or not isinstance(profile["files"], list)
            or not 0 < len(profile["files"]) <= MAX_SOURCE_FILES):
        raise SourceIdentityError("invalid_file_profile", FILE_PROFILE_SCHEMA)
    seen = set()
    total = 0
    for item in profile["files"]:
        if not isinstance(item, dict) or set(item) != {"plugin", "path", "bytes", "sha256"}:
            raise SourceIdentityError("invalid_file_profile", "file fields")
        name = _plugin(item["plugin"])
        path = _absolute_path(item["path"])
        if (name in seen or path.name.lower() != name or not _integer(item["bytes"], MAX_SOURCE_BYTES)
                or item["bytes"] < HEADER.size or not isinstance(item["sha256"], str)
                or not DIGEST.fullmatch(item["sha256"])):
            raise SourceIdentityError("invalid_file_profile", name)
        seen.add(name)
        total += item["bytes"]
        if total > MAX_SOURCE_BYTES:
            raise SourceIdentityError("source_file_byte_limit", name)
    return profile["files"]


def snapshot_source_files(profile, *, cancelled=None):
    """Check independently prescribed local source files and retain portable header evidence privately."""
    def check():
        if cancelled is not None and cancelled():
            raise SourceIdentityError("source_file_cancelled", "source file operation cancelled")

    files, records = [], []
    seen_ids = set()
    total_records = 0
    for expected in _file_profile(profile):
        check()
        path = Path(expected["path"])
        try:
            resolved = path.resolve(strict=True)
            if ntpath.normcase(str(resolved)) != ntpath.normcase(str(path)) or not stat.S_ISREG(path.stat().st_mode):
                raise SourceIdentityError("source_path_alias", expected["plugin"])
            item, stamp = inspect_plugin(path, expected_bytes=expected["bytes"], check=check)
        except OSError as error:
            raise SourceIdentityError("source_file_io", expected["plugin"]) from error
        if not stamp[1] or tuple(stamp[:2]) in seen_ids:
            raise SourceIdentityError("ambiguous_source_file_identity", expected["plugin"])
        if any(item[field] != expected[field] for field in ("plugin", "bytes", "sha256")):
            raise SourceIdentityError("source_file_digest_mismatch", expected["plugin"])
        seen_ids.add(tuple(stamp[:2]))
        total_records += len(item["records"])
        if total_records > MAX_RECORDS:
            raise SourceIdentityError("source_record_limit", expected["plugin"])
        files.append({**expected, "stamp": stamp})
        records.append(item)
    manifest = {"schema": MANIFEST_SCHEMA, "files": sorted(records, key=lambda item: item["plugin"])}
    _validate_manifest(manifest)
    return {"profile_sha256": digest(profile), "manifest": manifest, "files": files}


def bind_source_files(native_namespace, snapshot, *, authority="RETAIL_NATIVE_WITNESS"):
    """Join an admitted epoch's directory and slot witnesses to independently pinned disk headers."""
    if (not isinstance(snapshot, dict) or set(snapshot) != {"profile_sha256", "manifest", "files"}
            or not isinstance(snapshot["files"], list)):
        raise SourceIdentityError("invalid_source_snapshot", "snapshot fields")
    pinned = {}
    file_profile = {"schema": FILE_PROFILE_SCHEMA, "files": []}
    seen_ids = set()
    for file in snapshot["files"]:
        if not isinstance(file, dict) or set(file) != {"plugin", "path", "bytes", "sha256", "stamp"}:
            raise SourceIdentityError("invalid_source_snapshot", "snapshot file fields")
        name = _plugin(file["plugin"])
        stamp = file["stamp"]
        if (not isinstance(stamp, list) or len(stamp) != 5 or any(type(value) is not int for value in stamp)
                or not stamp[1] or stamp[2] != file["bytes"] or name in pinned or tuple(stamp[:2]) in seen_ids):
            raise SourceIdentityError("ambiguous_source_file_identity", name)
        pinned[name] = file
        seen_ids.add(tuple(stamp[:2]))
        file_profile["files"].append({key: value for key, value in file.items() if key != "stamp"})
    _file_profile(file_profile)
    if snapshot["profile_sha256"] != digest(file_profile):
        raise SourceIdentityError("source_profile_digest_mismatch", "disk evidence")
    headers = _validate_manifest(snapshot["manifest"])
    if set(headers) != set(pinned) or any(
            pinned[name][field] != headers[name][field] for name in headers for field in ("bytes", "sha256")):
        raise SourceIdentityError("source_snapshot_manifest_disagreement", "pinned disk headers")
    slots = native_namespace.get("compiled", [])
    paths = native_namespace.get("paths", {})
    resolved = native_namespace.get("resolved_paths", {})
    if not isinstance(paths, dict) or not isinstance(resolved, dict) or (
            set(paths) != {entry["plugin"] for entry in slots} or not set(resolved).issubset(paths)):
        raise SourceIdentityError("incomplete_native_source_paths", "compiled namespace")
    path_witnesses = {}
    for slot in slots:
        name = _plugin(slot["plugin"])
        if name not in pinned:
            raise SourceIdentityError("missing_plugin_source", name)
        expected = _absolute_path(pinned[name]["path"])
        try:
            observed = _absolute_path(paths[name]) / name
        except SourceIdentityError as error:
            if error.code != "unresolved_native_source_path" or name not in resolved:
                raise
            observed = _absolute_path(resolved[name])
            path_witnesses[name] = "RETAINED_OPEN_STREAM"
        else:
            if name in resolved:
                raise SourceIdentityError("unexpected_native_stream_path", name)
            path_witnesses[name] = "ABSOLUTE_PACKED_FILE_DIRECTORY"
        if observed != expected:
            raise SourceIdentityError("native_source_path_disagreement", name)
    witnessed = {"schema": NAMESPACE_SCHEMA, "authority": authority, "plugins": slots}
    index = SourceIndex(snapshot["manifest"], witnessed, defining_only=True)
    index.provenance["path_witnesses"] = path_witnesses
    return index


def bind_native_namespace(native_namespace, *, authority="RETAIL_NATIVE_WITNESS"):
    """Resolve defining identities from a checked native loaded-plugin roster."""
    if not isinstance(native_namespace, dict):
        raise SourceIdentityError("invalid_namespace", "native namespace is missing")
    return NativeIdentityIndex({
        "schema": NAMESPACE_SCHEMA, "authority": authority,
        "plugins": native_namespace.get("compiled"),
    })


class NativeIdentityIndex:
    """Join native-validated FormIDs to the independently collected plugin slots.

    The acquisition validates each form's stored ID, native type and relevant
    resource vptr. The index supplies its defining namespace and local bits.
    """

    def __init__(self, namespace):
        if (not isinstance(namespace, dict) or set(namespace) != {"schema", "authority", "plugins"}
                or namespace["schema"] != NAMESPACE_SCHEMA
                or namespace["authority"] not in ("OWNED_DISPOSABLE", "RETAIL_NATIVE_WITNESS")
                or not isinstance(namespace["plugins"], list)
                or not 0 < len(namespace["plugins"]) <= MAX_PLUGINS):
            raise SourceIdentityError("invalid_namespace", NAMESPACE_SCHEMA)
        self.by_slot = {}
        names = set()
        plugins = []
        for entry in namespace["plugins"]:
            if not isinstance(entry, dict) or set(entry) != {"plugin", "kind", "index"}:
                raise SourceIdentityError("invalid_namespace_entry", "expected plugin/kind/index")
            name, kind, index = _plugin(entry["plugin"]), entry["kind"], entry["index"]
            if not isinstance(kind, str) or kind not in INDEX_MAX or not _integer(index, INDEX_MAX[kind]):
                raise SourceIdentityError("invalid_namespace_slot", name)
            if name in names or (kind, index) in self.by_slot:
                raise SourceIdentityError("ambiguous_namespace", name)
            names.add(name)
            self.by_slot[kind, index] = name
            plugins.append({"plugin": name, "kind": kind, "index": index})
        ordered = sorted(plugins, key=lambda entry: (entry["kind"], entry["index"]))
        normalized = {**namespace, "plugins": ordered}
        self.identity_sha256 = digest(normalized)
        self.provenance = {
            "authority": namespace["authority"], "namespace_sha256": self.identity_sha256,
            "identity_method": "NATIVE_LOADED_PLUGIN_NAMESPACE",
            "type_evidence": "NATIVE_FORM_MAP",
            "plugins": ordered,
        }
        self.signatures = {}

    def resolve(self, runtime_id, signature):
        if not isinstance(signature, str) or signature not in SIGNATURES:
            raise SourceIdentityError("unsupported_native_signature", repr(signature))
        kind, index, local = _split(runtime_id)
        plugin = self.by_slot.get((kind, index))
        if plugin is None:
            raise SourceIdentityError("unwitnessed_runtime_namespace", f"{runtime_id:08X}")
        previous = self.signatures.setdefault(runtime_id, signature)
        if previous != signature:
            raise SourceIdentityError("native_form_type_conflict", f"{runtime_id:08X}")
        return {
            "plugin": plugin, "local_id": f"{local:06X}", "signature": signature,
            "source_record_id": None, "winning_record_id": None, "winning_plugin": None,
            "comparator_id": f"{plugin}:{local:06X}", "attribution": "WINNING_CONTENT_UNRESOLVED",
        }

    def validate_observed_sources(self, resolved, observed):
        """Retain attribution independently from defining identity and native type."""
        return None


class SourceIndex:
    """Consume ordered loaded plugin slots from a separately authenticated witness.

    The caller owns witness authorization, epoch checks and completeness. This
    class validates the contents against the source inventory and can also be
    used with a labeled counterfactual. It never queries a process or an oracle.
    """

    def __init__(self, manifest, namespace, *, defining_only=False):
        files = _validate_manifest(manifest)
        if (not isinstance(namespace, dict) or set(namespace) != {"schema", "authority", "plugins"}
                or namespace["schema"] != NAMESPACE_SCHEMA
                or namespace["authority"] not in ("OWNED_DISPOSABLE", "DISK_COUNTERFACTUAL", "RETAIL_NATIVE_WITNESS")
                or not isinstance(namespace["plugins"], list)
                or not 0 < len(namespace["plugins"]) <= MAX_PLUGINS):
            raise SourceIdentityError("invalid_namespace", NAMESPACE_SCHEMA)
        self.by_slot = {}
        ordered = {}
        records = {}
        for entry in namespace["plugins"]:
            if not isinstance(entry, dict) or set(entry) != {"plugin", "kind", "index"}:
                raise SourceIdentityError("invalid_namespace_entry", "expected plugin/kind/index")
            plugin, kind, index = _plugin(entry["plugin"]), entry["kind"], entry["index"]
            if not isinstance(kind, str) or kind not in INDEX_MAX or not _integer(index, INDEX_MAX[kind]):
                raise SourceIdentityError("invalid_namespace_slot", plugin)
            if plugin in ordered or (kind, index) in self.by_slot:
                raise SourceIdentityError("ambiguous_namespace", plugin)
            if plugin not in files:
                raise SourceIdentityError("missing_plugin_source", plugin)
            file = files[plugin]
            if kind != _kind(plugin, file["flags"]):
                raise SourceIdentityError("source_scale_disagreement", plugin)
            self.by_slot[kind, index] = plugin
            ordered[plugin] = kind
        known = {}
        candidates = {}
        for plugin, kind in ordered.items():
            file = files[plugin]
            known[plugin] = kind
            master_kinds = ordered if defining_only else known
            if any(master not in master_kinds for master in file["masters"]):
                raise SourceIdentityError("unknown_master_or_precedence", plugin)
            master_slots = {scale: [] for scale in INDEX_MAX}
            for master in file["masters"]:
                master_slots[master_kinds[master]].append(master)
            master_slots[kind].append(plugin)
            if defining_only:
                self._define(records, candidates, plugin, file, master_slots)
            else:
                self._register(records, plugin, file, master_slots)
        self.records = records
        self.candidates = candidates
        self.defining_only = defining_only
        identity = {"manifest": manifest, "namespace": namespace}
        if defining_only:
            identity["defining_only"] = True
        self.identity_sha256 = digest(identity)
        self.provenance = {
            "authority": namespace["authority"], "source_sha256": digest(manifest),
            "namespace_sha256": digest(namespace),
            "plugins": [{key: files[name][key] for key in ("plugin", "sha256", "bytes")}
                        for name in ordered],
        }

    @staticmethod
    def _define(records, candidates, plugin, file, master_slots):
        if file["records"] and file["flags"] & 0xA00:
            raise SourceIdentityError("unsupported_update_or_blueprint_source", plugin)
        for signature, raw_id, flags in file["records"]:
            scale, index, local = _split(raw_id)
            slots = master_slots[scale]
            if index >= len(slots):
                raise SourceIdentityError("unknown_file_relative_slot", f"{plugin}:{raw_id:08X}")
            defining = slots[index]
            key = defining, local
            contributions = candidates.setdefault(key, {})
            if plugin in contributions:
                raise SourceIdentityError("canonical_source_collision", f"{plugin}:{raw_id:08X}")
            contributions[plugin] = (signature, flags)
            if plugin == defining:
                records[key] = {"plugin": defining, "local_id": f"{local:06X}", "signature": signature,
                                "source_record_id": f"{raw_id:08X}", "winning_record_id": None,
                                "winning_plugin": None, "deleted": bool(flags & 0x20),
                                "comparator_id": f"{defining}:{local:06X}"}

    @staticmethod
    def _register(records, plugin, file, master_slots):
        if file["records"] and file["flags"] & 0xA00:
            raise SourceIdentityError("unsupported_update_or_blueprint_source", plugin)
        for signature, raw_id, flags in file["records"]:
            scale, index, local = _split(raw_id)
            slots = master_slots[scale]
            if index >= len(slots):
                raise SourceIdentityError("unknown_file_relative_slot", f"{plugin}:{raw_id:08X}")
            defining = slots[index]
            key = defining, local
            previous = records.get(key)
            if previous is None and defining != plugin:
                raise SourceIdentityError("source_injected_or_missing_definition", f"{plugin}:{raw_id:08X}")
            if previous is not None and (previous["signature"] != signature or previous["winning_plugin"] == plugin):
                raise SourceIdentityError("canonical_source_collision", f"{plugin}:{raw_id:08X}")
            records[key] = {"plugin": defining, "local_id": f"{local:06X}", "signature": signature,
                            "source_record_id": previous["source_record_id"] if previous else f"{raw_id:08X}",
                            "winning_record_id": f"{raw_id:08X}", "winning_plugin": plugin,
                            "deleted": bool(flags & 0x20), "comparator_id": f"{defining}:{local:06X}"}

    def resolve(self, runtime_id, signature):
        kind, index, local = _split(runtime_id)
        plugin = self.by_slot.get((kind, index))
        if plugin is None:
            raise SourceIdentityError("unwitnessed_runtime_namespace", f"{runtime_id:08X}")
        source = self.records.get((plugin, local))
        if source is None:
            raise SourceIdentityError("missing_typed_source_record", f"{plugin}:{local:06X}")
        if source["signature"] != signature:
            raise SourceIdentityError("source_type_mismatch", f"{runtime_id:08X}: expected {signature}")
        if self.defining_only:
            contributors = self.candidates[plugin, local]
            if any(kind != signature for kind, _ in contributors.values()):
                raise SourceIdentityError("canonical_source_collision", f"{runtime_id:08X}")
            return {**{key: value for key, value in source.items() if key != "deleted"},
                    "attribution": "WINNING_CONTENT_UNRESOLVED", "candidate_plugins": sorted(contributors),
                    "tombstone_plugins": sorted(name for name, (_, flags) in contributors.items() if flags & 0x20)}
        if source["deleted"]:
            raise SourceIdentityError("deleted_winning_source_record", f"{runtime_id:08X}")
        return {key: value for key, value in source.items() if key != "deleted"}

    def validate_observed_sources(self, resolved, observed):
        """Check corroboration against exact canonical disk records without assuming history completeness."""
        if self.defining_only and observed is not None:
            for name in observed:
                if name not in resolved["candidate_plugins"]:
                    raise SourceIdentityError("native_source_identity_conflict", name)


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise SourceIdentityError("ambiguous_json_member", key)
        result[key] = value
    return result


def load_json(path):
    with Path(path).open("rb") as stream:
        raw = stream.read(MAX_MANIFEST_BYTES + 1)
    if len(raw) > MAX_MANIFEST_BYTES:
        raise SourceIdentityError("source_manifest_size_limit", str(MAX_MANIFEST_BYTES))
    return json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_pairs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plugins", nargs="+", type=Path, help="explicit installed or owned plugin files")
    parser.add_argument("--manifest", required=True, type=Path, help="new private JSON output")
    args = parser.parse_args()
    manifest = build_manifest(args.plugins)
    payload = json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    if len(payload) > MAX_MANIFEST_BYTES:
        parser.error("compiled source manifest exceeds its byte limit")
    with args.manifest.open("xb") as stream:
        stream.write(payload)
    counts = {file["plugin"]: dict(Counter(record[0] for record in file["records"]))
              for file in manifest["files"]}
    print(json.dumps({"source_sha256": digest(manifest), "counts": counts}, sort_keys=True))


if __name__ == "__main__":
    main()
