"""Bounded read plan for the pinned retail FormID source namespace."""

from dataclasses import dataclass
import struct

from tools.srr017.source import INDEX_MAX, SourceIdentityError, _absolute_path, _plugin


HANDLER_RVA = 0x5FD9B28
SOURCE_TABLE_RVA = 0x5E881E8
REGISTRY_OFFSET = 0x1570
COLLECTION_OFFSET = 0x1580
PREFIX_START = 0x38
PREFIX_END = 0x21C
PACKED_FILE_VTABLE_RVA = 0x4B29B80
PACKED_FILE_DIRECTORY = 0x268
PACKED_FILE_DIRECTORY_BYTES = 260
PACKED_FILE_STREAM = 0x378
BSFILE_VTABLE_RVA = 0x4DA7FB8
BSFILE_OPEN = 0x4C
BSFILE_PATH = 0x6C
SCALES = ("full", "small", "medium")
REGISTRY_IMPLEMENTATION_MAX = 8192
PLUGIN_CHUNK = 256 * 8


@dataclass(frozen=True)
class NamespaceLimits:
    slots: int = 256
    registry_nodes: int = 512
    reads: int = 1024
    requested_bytes: int = 512 * 1024


def collect_namespace(read, image_base, limits=NamespaceLimits(), *, claim=None, include_paths=False):
    """Read one namespace witness through the caller's metered read callable.

    The caller must admit the image, run consumed-window stability checks, and
    acquire an independent second witness within the same process epoch.
    The registry order is retained for evidence and conveys no winner ranking.
    """
    if (not 1 <= limits.slots <= sum(INDEX_MAX.values()) + len(INDEX_MAX)
            or not 1 <= limits.registry_nodes <= REGISTRY_IMPLEMENTATION_MAX
            or not 1 <= limits.reads <= 32_768
            or not 1 <= limits.requested_bytes <= 16 * 1024 * 1024):
        raise SourceIdentityError("invalid_namespace_limits", "invalid work limits")
    reads = requested = 0
    extents = []

    def fetch(address, size, label):
        nonlocal reads, requested
        if type(address) is not int or address % 8 or not 0x10000 <= address < address + size <= 1 << 47:
            raise SourceIdentityError("invalid_namespace_pointer", label)
        if reads == limits.reads or requested + size > limits.requested_bytes:
            raise SourceIdentityError("namespace_read_budget", label)
        reads += 1
        requested += size
        value = read(address, size, label)
        if not isinstance(value, bytes) or len(value) != size:
            raise SourceIdentityError("namespace_partial_read", label)
        extents.append((address, address + size, label))
        return value

    handler, = struct.unpack("<Q", fetch(image_base + HANDLER_RVA, 8, "namespace_handler"))
    header = fetch(handler + REGISTRY_OFFSET if handler else 0, 64, "namespace_header")
    first_file, next_node = struct.unpack_from("<QQ", header)
    slots = []
    occupied = set()
    counts = 0
    for offset, scale in enumerate(SCALES):
        count, capacity, data = struct.unpack_from("<IIQ", header,
                                                   COLLECTION_OFFSET - REGISTRY_OFFSET + offset * 16)
        counts += count
        if count > INDEX_MAX[scale] + 1 or count > capacity or counts > limits.slots:
            raise SourceIdentityError("namespace_slot_budget", scale)
        pointers = []
        for start in range(0, count * 8, PLUGIN_CHUNK):
            raw = fetch(data + start if data else 0,
                        min(PLUGIN_CHUNK, count * 8 - start), f"namespace_{scale}_array")
            pointers.extend(pointer for pointer, in struct.iter_unpack("<Q", raw))
        for index, pointer in enumerate(pointers):
            if not pointer:
                continue  # Native inverse lookup checks for null slots.
            if pointer in occupied:
                raise SourceIdentityError("namespace_plugin_pointer_alias", scale)
            occupied.add(pointer)
            slots.append((scale, index, pointer))

    if not slots or not first_file:
        raise SourceIdentityError("namespace_unpublished", "compiled files or registry missing")
    file_data = {}
    names = set()
    seen_nodes = set()
    file_pointer = first_file
    while True:
        if len(file_data) >= limits.registry_nodes:
            raise SourceIdentityError("namespace_registry_budget", "too many file nodes")
        if file_pointer in file_data:
            raise SourceIdentityError("namespace_plugin_pointer_alias", "registry")
        window = fetch(file_pointer + PREFIX_START if file_pointer else 0, PREFIX_END - PREFIX_START,
                       "namespace_file_fields")
        name, terminator, _ = window[:260].partition(b"\0")
        if not terminator or not name.isascii():
            raise SourceIdentityError("namespace_invalid_plugin_name", "TESFile name")
        plugin = _plugin(name.decode("ascii").lower())
        if plugin in names:
            raise SourceIdentityError("ambiguous_namespace", plugin)
        names.add(plugin)
        flags, = struct.unpack_from("<I", window, 0x1B8 - PREFIX_START)
        full, medium, small = struct.unpack_from("<BBH", window, 0x218 - PREFIX_START)
        file_data[file_pointer] = {"plugin": plugin, "flags": flags, "full": full,
                                   "medium": medium, "small": small}
        if not next_node:
            break
        if next_node == handler + REGISTRY_OFFSET or next_node in seen_nodes:
            raise SourceIdentityError("namespace_registry_cycle", "TESFile list")
        seen_nodes.add(next_node)
        file_pointer, next_node = struct.unpack("<QQ", fetch(next_node, 16, "namespace_registry_node"))

    compiled = []
    paths = {}
    resolved_paths = {}
    for scale, index, pointer in slots:
        witness = file_data.get(pointer)
        if witness is None:
            raise SourceIdentityError("namespace_plugin_outside_registry", scale)
        flags = witness["flags"]
        expected_kind = "small" if flags & 0x100 else "medium" if flags & 0x400 else "full"
        expected_tag = {"full": index, "medium": 0xFD, "small": 0xFE}[scale]
        if (flags & 0x500 == 0x500 or flags & 0x200 or expected_kind != scale
                or witness[scale] != index or witness["full"] != expected_tag):
            raise SourceIdentityError("namespace_file_slot_disagreement", witness["plugin"])
        if include_paths:
            vtable, = struct.unpack("<Q", fetch(pointer, 8, "namespace_file_vtable"))
            if vtable != image_base + PACKED_FILE_VTABLE_RVA:
                raise SourceIdentityError("namespace_unknown_file_class", witness["plugin"])
            raw = fetch(pointer + PACKED_FILE_DIRECTORY, PACKED_FILE_DIRECTORY_BYTES,
                        "namespace_file_directory")
            directory, terminator, _ = raw.partition(b"\0")
            if not terminator or not directory or not directory.isascii():
                raise SourceIdentityError("namespace_invalid_file_directory", witness["plugin"])
            name = witness["plugin"]
            paths[name] = directory.decode("ascii")
            try:
                _absolute_path(paths[name])
            except SourceIdentityError as error:
                if error.code != "unresolved_native_source_path":
                    raise
                stream, = struct.unpack("<Q", fetch(pointer + PACKED_FILE_STREAM, 8, "namespace_stream_pointer"))
                if stream:
                    data = fetch(stream, BSFILE_PATH + PACKED_FILE_DIRECTORY_BYTES, "namespace_stream_path")
                    stream_vtable, = struct.unpack_from("<Q", data)
                    if stream_vtable != image_base + BSFILE_VTABLE_RVA:
                        raise SourceIdentityError("namespace_unknown_stream_class", name)
                    backing, terminator, _ = data[BSFILE_PATH:].partition(b"\0")
                    if data[BSFILE_OPEN] and terminator and backing and backing.isascii():
                        try:
                            path = _absolute_path(backing.decode("ascii"))
                        except SourceIdentityError:
                            pass
                        else:
                            if path.name.lower() != name:
                                raise SourceIdentityError("namespace_stream_name_disagreement", name)
                            resolved_paths[name] = str(path)
        compiled.append({"plugin": witness["plugin"], "kind": scale, "index": index})
    if any(witness["full"] != 0xFF and pointer not in occupied for pointer, witness in file_data.items()):
        raise SourceIdentityError("namespace_assigned_file_outside_collections", "unclassified assigned source")
    extents.sort()
    for previous, current in zip(extents, extents[1:]):
        if previous[1] > current[0]:
            raise SourceIdentityError("namespace_extent_alias", f"{previous[2]} / {current[2]}")
    if claim is not None:
        for start, end, label in extents:
            claim(start, end - start, label)
    result = {"compiled": compiled, "registry": list(file_data.values()), "file_pointers": file_data,
              "reads": reads, "requested_bytes": requested, "slot_count": counts}
    if include_paths:
        result["paths"] = paths
        result["resolved_paths"] = resolved_paths
    return result


class FormSourceVectors:
    """Read ordered native source-name vectors for independently validated forms.

    Addresses and read windows stay with private custody. A fresh instance is
    required for each collection. The enclosing reader owns the closing
    consumed-window recheck and epoch bracket.
    """

    def __init__(self, read, image_base, namespace, *, forms=8192, vectors=1024, sources_per_form=64,
                 byte_limit=1024 * 1024, claim=None):
        if (not 1 <= forms <= 65_535 or not 1 <= vectors <= 65_535
                or not 1 <= sources_per_form <= 256 or not 16 <= byte_limit <= 16 * 1024 * 1024):
            raise SourceIdentityError("invalid_source_vector_limits", "invalid work limits")
        self.read = read
        self.claim = claim
        self.forms = forms
        self.vectors = vectors
        self.sources_per_form = sources_per_form
        self.byte_limit = byte_limit
        claimed_names = {entry["plugin"] for entry in namespace["compiled"]}
        self.names = {address: fields["plugin"] for address, fields in namespace["file_pointers"].items()
                      if fields["plugin"] in claimed_names}
        self.by_index = {}
        self.by_form = {}
        self.by_bucket = set()
        self.reads = self.requested_bytes = 0
        self.count, self.root = struct.unpack("<I4xQ", self._fetch(image_base + SOURCE_TABLE_RVA, 16, 8))
        if not 0 < self.count <= 65_535 or not self._valid_pointer(self.root, 8, self.count * 8):
            raise SourceIdentityError("invalid_source_vector_table", "source table extent")
        if self.claim is not None:
            self.claim(image_base + SOURCE_TABLE_RVA, 16, "form source table anchor")
            self.claim(self.root, self.count * 8, "form source table index")

    @staticmethod
    def _valid_pointer(address, alignment, size):
        return type(address) is int and address % alignment == 0 and 0x10000 <= address < address + size <= 1 << 47

    def _fetch(self, address, size, alignment):
        if not self._valid_pointer(address, alignment, size):
            raise SourceIdentityError("invalid_source_vector_pointer", "source vector data")
        if self.requested_bytes + size > self.byte_limit:
            raise SourceIdentityError("source_vector_read_budget", "source vector byte limit")
        self.reads += 1
        self.requested_bytes += size
        value = self.read(address, size, "form_source_vector")
        if not isinstance(value, bytes) or len(value) != size:
            raise SourceIdentityError("source_vector_partial_read", "source vector data")
        return value

    def lookup(self, form_address):
        if form_address in self.by_form:
            return self.by_form[form_address]
        if len(self.by_form) == self.forms:
            raise SourceIdentityError("source_form_budget", "too many witnessed forms")
        if not self._valid_pointer(form_address, 8, 0x32):
            raise SourceIdentityError("invalid_source_form_pointer", "form source index")
        index, = struct.unpack("<H", self._fetch(form_address + 0x30, 2, 2))
        if index == 0xFFFF:
            names = None
        elif index >= self.count:
            raise SourceIdentityError("source_vector_index_range", "form source index")
        else:
            names = self.by_index.get(index)
            if names is None:
                names = self._vector(index)
                self.by_index[index] = names
        self.by_form[form_address] = names
        return names

    def _vector(self, index):
        if len(self.by_index) == self.vectors:
            raise SourceIdentityError("source_vector_budget", "too many distinct source vectors")
        bucket, = struct.unpack("<Q", self._fetch(self.root + index * 8, 8, 8))
        if bucket in self.by_bucket:
            raise SourceIdentityError("source_vector_bucket_alias", "conflicting source vector table slots")
        if self.claim is not None:
            self.claim(bucket, 16, f"form source vector {index}")
        data, count = struct.unpack("<QI4x", self._fetch(bucket, 16, 8))
        if not 0 < count <= self.sources_per_form or count > len(self.names):
            raise SourceIdentityError("source_vector_width", "source files per form")
        if self.claim is not None:
            self.claim(data, count * 8, f"form source vector entries {index}")
        pointers = [value for value, in struct.iter_unpack("<Q", self._fetch(data, count * 8, 8))]
        if len(set(pointers)) != count or any(pointer not in self.names for pointer in pointers):
            raise SourceIdentityError("source_vector_namespace_disagreement", "duplicate or unbound source file")
        self.by_bucket.add(bucket)
        return tuple(self.names[pointer] for pointer in pointers)
