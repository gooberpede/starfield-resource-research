"""Bounded decoder for the SRR-012 retail layout, used on owned fixtures."""

from bisect import bisect_left
from dataclasses import dataclass
import hashlib
import struct
import time

from memory import ReadFailure


CONTEXT_SLOT = 0x82EEBB0
CONTEXT = 0x82EE5C0
CONTEXT_VPTR = 0x4D6A6C0
TYPE_WORD = 0x61DFA4C
REGISTRY = 0x82EEC20
RECEIVER_SLOT = 0x61FA160
RECEIVER_VPTR = 0x4D5FAC8
EDGE_VPTR = 0x4B3D258
FORM_MAP_SLOT = 0x5E60EA0
# Pinned retail BGSResource ctor stores the vptr at VA 0x1409E74E6
# and the type byte at VA 0x1409E75D9. The factory returns the same type.
RESOURCE_VPTR = 0x4B6F0B0
RESOURCE_TYPE = 0x9F
MAX_BIOM_RSGDS = 32

MAX_LEVEL = 8
MAX_NODES = 128
MAX_ENTRIES = 512
MAX_CHAIN = 256
MAX_READS = 12_000
MAX_BYTES = 1024 * 1024
MAX_SECONDS = 8
NODE_END = 0xFE0
MAX_KEYS = 0xA8
BLOCK = 0xFFFFFFFF


class NativeFailure(Exception):
    def __init__(self, code, detail):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def require(condition, code, detail):
    if not condition:
        raise NativeFailure(code, detail)


def pointer(address, size=1, alignment=8):
    require(
        0x10000 <= address and address + size <= 1 << 64 and address % alignment == 0,
        "invalid_pointer",
        f"invalid {alignment}-aligned range at {address:#x}, size {size}",
    )
    return address


def unpack(format_, data):
    return struct.unpack("<" + format_, data)


@dataclass(frozen=True)
class Node:
    address: int
    level: int
    keys: tuple
    pointers: tuple
    previous: int = 0
    next: int = 0


@dataclass(frozen=True)
class Record:
    address: int
    size: int
    key: tuple


class Collection:
    def __init__(self, reader, base, *, structural=False):
        self.reader = reader
        self.base = pointer(base)
        self.structural = structural
        self.deadline = time.monotonic() + MAX_SECONDS
        self.read_count = self.byte_count = self.entries = 0
        self.structure = {}
        self.nodes = {}
        self.block_headers = {}
        self.blocks = {}
        self.extents = {}
        self.tree_parents = {}
        self.block_parents = {}
        self.forms = {}

    def read(self, address, size, alignment=1, *, structural=True):
        pointer(address, size, alignment)
        bounds = (address, size, alignment)
        if structural and bounds in self.structure:
            return self.structure[bounds]
        data = self.exact(*bounds)
        if structural:
            self.structure[bounds] = data
        return data

    def exact(self, address, size, alignment):
        self.read_count += 1
        self.byte_count += size
        require(
            self.read_count <= MAX_READS and self.byte_count <= MAX_BYTES
            and time.monotonic() <= self.deadline,
            "traversal_budget",
            "collection read, byte or time safety limit exceeded",
        )
        data = self.reader.read(address, size, alignment)
        require(len(data) == size, "read_incomplete", f"short read at {address:#x}")
        return data

    def scalar(self, address, format_):
        width = struct.calcsize("<" + format_)
        return unpack(format_, self.read(address, width, width))[0]

    def claim(self, address, size, identity):
        pointer(address, size)
        end = address + size
        for other, (other_end, other_identity) in self.extents.items():
            if address < other_end and other < end:
                require(
                    (address, end, identity) == (other, other_end, other_identity),
                    "pointer_alias",
                    f"{identity} at {address:#x} overlaps {other_identity} at {other:#x}",
                )
        self.extents[address] = (end, identity)

    def anchors(self):
        base = self.base
        owner = self.scalar(base + CONTEXT_SLOT, "Q")
        require(owner != 0, "context_absent", "context publication slot is null")
        require(owner == base + CONTEXT, "context_ambiguous", "unexpected published owner")
        owner_vptr = self.scalar(owner, "Q")
        require(owner_vptr == base + CONTEXT_VPTR, "owner_type_mismatch", "wrong DB vptr")

        discriminator = self.scalar(base + TYPE_WORD, "H")
        count = self.scalar(base + REGISTRY, "I")
        table = self.scalar(base + REGISTRY + 8, "Q")
        receiver = self.scalar(base + RECEIVER_SLOT, "Q")
        require(
            discriminator != 0xFFFF and discriminator < count and receiver and table,
            "registry_unverified",
            "unpublished, unregistered or out-of-bounds PerBiomeData registration",
        )
        pointer(table, count * 0x18)
        receiver_vptr = self.scalar(pointer(receiver, 0x108), "Q")
        descriptor = self.scalar(table + 0x18 * discriminator, "Q")
        require(
            receiver_vptr == base + RECEIVER_VPTR and descriptor == receiver + 0x100,
            "registry_unverified",
            "PerBiomeData registry descriptor or registration receiver disagrees",
        )
        if self.structural:
            self.claim(owner, 0x350, "published context and index header")
            self.claim(base + REGISTRY, 0x10, "type registry header")
            self.claim(table, count * 0x18, "type registry table")
            self.claim(receiver, 0x108, "registration receiver and descriptor")

        index = owner + 0x300
        self.root = self.scalar(index, "Q")
        self.total = self.scalar(index + 0x48, "Q")
        self.discriminator = discriminator
        require(bool(self.root) == bool(self.total), "index_shape", "root/count disagree")
        return {
            "publication_slot": base + CONTEXT_SLOT,
            "owner": owner,
            "owner_vptr": owner_vptr,
            "index": index,
            "root": self.root,
            "count": self.total,
            "discriminator": discriminator,
            "registry_table": table,
            "registry_count": count,
            "registry_descriptor": descriptor,
            "registration_receiver": receiver,
            "registration_receiver_vptr": receiver_vptr,
        }

    def node(self, address, parent, level=None):
        pointer(address, NODE_END)
        require(
            self.tree_parents.setdefault(address, parent) == parent,
            "pointer_alias",
            f"tree node {address:#x} has multiple positions",
        )
        if address not in self.nodes:
            require(len(self.nodes) < MAX_NODES, "traversal_budget", "tree node cap exceeded")
            self.claim(address, NODE_END, "index node")
            marker, count = unpack("II", self.read(address, 8, 8))
            if marker == BLOCK:
                require(parent is None, "index_shape", "block used as internal child")
                node = Node(address, marker, (), ())
            else:
                require(marker <= MAX_LEVEL, "traversal_budget", "node level cap exceeded")
                require(count <= MAX_KEYS, "index_shape", "node array count out of bounds")
                if marker == 0:
                    require(count > 0, "index_shape", "empty leaf directory")
                    next_, previous = unpack("QQ", self.read(address + 8, 16, 8))
                    key_offset, pointer_offset, pointer_count = 0x18, 0xA98, count
                    for link in (next_, previous):
                        if link:
                            pointer(link, NODE_END)
                            require(link != address, "pointer_alias", "cyclic leaf link")
                else:
                    previous = next_ = 0
                    key_offset, pointer_offset, pointer_count = 8, 0xA88, count + 1
                keys = ()
                if count:
                    keys = tuple(struct.iter_unpack("<QQ", self.read(address + key_offset, count * 16, 8)))
                require(keys == tuple(sorted(keys)), "index_order", "unsorted node keys")
                pointers = unpack("Q" * pointer_count, self.read(address + pointer_offset, pointer_count * 8, 8))
                for child in pointers:
                    pointer(child, NODE_END)
                require(
                    len(set(pointers)) == len(pointers) and address not in pointers,
                    "pointer_alias",
                    "repeated or cyclic child pointer",
                )
                node = Node(address, marker, keys, pointers, previous, next_)
                if marker == 0:
                    for index, (block, key) in enumerate(zip(pointers, keys, strict=True)):
                        actual = self.block_header(block, (address, index))[4]
                        require(actual == key, "block_minimum", "leaf minimum disagrees with packed first key")
            self.nodes[address] = node
        node = self.nodes[address]
        require(level is None or node.level == level, "index_shape", "child level disagrees")
        return node

    def descend(self, node, path=(), *, key=None, rightmost=False):
        while node.level:
            self.check_fences(node.keys, path)
            child = len(node.keys) if rightmost else 0
            if key is not None:
                child = bisect_left(node.keys, key)
            path += ((node, child),)
            node = self.node(node.pointers[child], (node.address, child), node.level - 1)
        self.check_fences(node.keys, path)
        return node, path

    def neighbor(self, leaf, path, direction):
        """Derive the adjacent leaf independently of the on-leaf links."""
        link = leaf.next if direction == 1 else leaf.previous
        for index in range(len(path) - 1, -1, -1):
            parent, child = path[index]
            sibling = child + direction
            if 0 <= sibling < len(parent.pointers):
                position = (parent.address, sibling)
                node = self.node(parent.pointers[sibling], position, parent.level - 1)
                adjacent, adjacent_path = self.descend(
                    node, path[:index] + ((parent, sibling),), rightmost=direction == -1,
                )
                back = adjacent.previous if direction == 1 else adjacent.next
                require(
                    link == adjacent.address and back == leaf.address,
                    "leaf_link_mismatch",
                    "leaf links disagree with root-derived neighbors",
                )
                return adjacent, adjacent_path
        require(link == 0, "leaf_link_mismatch", "leaf points beyond root traversal")
        return None, ()

    def count_entries(self, count):
        self.entries += count
        require(self.entries <= MAX_ENTRIES, "traversal_budget", "record descriptor cap exceeded")

    def block_header(self, address, location):
        """Check the packed header and the one record advertised by a leaf minimum."""
        require(
            self.block_parents.setdefault(address, location) == location,
            "pointer_alias",
            f"block {address:#x} has multiple positions",
        )
        if address not in self.block_headers:
            self.claim(address, NODE_END, "index node" if location is None else "record block")
            marker, count, directory_end, holes, frontier = unpack("IIHHI", self.read(address, 16, 8))
            require(marker == BLOCK, "index_shape", "invalid packed record block marker")
            require(
                0 < count <= (NODE_END - 0x10) // (4 + 0x20)
                and directory_end == 0x10 + 4 * count
                and directory_end <= frontier < NODE_END
                and holes <= NODE_END - frontier,
                "index_shape",
                "record block count or occupancy metadata out of bounds",
            )
            self.count_entries(1)
            size, offset = unpack("HH", self.read(address + 0x10, 4, 4))
            require(
                size >= 0x20 and frontier <= offset and offset + size <= NODE_END,
                "record_span",
                "first packed record is truncated or out of bounds",
            )
            minimum = unpack("QQ", self.read(address + offset + 0x10, 16))
            self.block_headers[address] = (count, holes, frontier, (size, offset), minimum)
        return self.block_headers[address]

    def block(self, address, location):
        if address not in self.blocks:
            count, holes, frontier, first_desc, _ = self.block_header(address, location)
            self.count_entries(count - 1)
            descriptors = (first_desc,)
            if count > 1:
                remaining = self.read(address + 0x14, 4 * (count - 1), 4)
                descriptors += tuple(struct.iter_unpack("<HH", remaining))
            spans = sorted((offset, offset + size) for size, offset in descriptors)
            previous_end = frontier
            for start, end in spans:
                require(
                    previous_end <= start and start + 0x20 <= end <= NODE_END,
                    "record_span",
                    "overlapping, truncated or out-of-bounds packed records",
                )
                previous_end = end
            require(
                NODE_END - frontier - sum(size for size, _ in descriptors) == holes,
                "index_shape",
                "block free-space credit disagrees with occupied spans",
            )
            records = tuple(
                Record(address + offset, size, unpack("QQ", self.read(address + offset + 0x10, 16)))
                for size, offset in descriptors
            )
            keys = tuple(record.key for record in records)
            require(keys == tuple(sorted(keys)), "index_order", "unsorted packed record keys")
            self.blocks[address] = records
        return self.blocks[address]

    def leaf_block(self, leaf, path, index):
        records = self.block(leaf.pointers[index], (leaf.address, index))
        first, last = records[0].key, records[-1].key
        require(first == leaf.keys[index], "block_minimum", "leaf minimum disagrees with block")
        if index + 1 < len(leaf.keys):
            require(last <= leaf.keys[index + 1], "index_order", "overlapping adjacent block keys")
        self.check_fences((first, last), path)
        return records

    @staticmethod
    def check_fences(keys, path):
        if not keys:
            return
        for parent, child in path:
            require(
                (child == 0 or parent.keys[child - 1] <= keys[0])
                and (child == len(parent.keys) or keys[-1] <= parent.keys[child]),
                "index_fence",
                "keys cross a root-derived separator",
            )

    def range_blocks(self, lower):
        root = self.node(self.root, None)
        if root.level == BLOCK:
            records = self.block(root.address, None)
            require(len(records) == self.total, "index_shape", "direct block total disagrees")
            yield records
            return

        leaf, path = self.descend(root, key=lower)
        insertion = bisect_left(leaf.keys, lower)
        if insertion:
            index = insertion - 1
        else:
            previous, previous_path = self.neighbor(leaf, path, -1)
            if previous is None:
                index = 0
            else:
                leaf, path = previous, previous_path
                index = len(leaf.keys) - 1
        # The chosen block must have no predecessor that could contain a hit.
        # Verify the immediate root-backed boundary even when descent stayed
        # in the same leaf, so a forged separator cannot hide an adjacent hit.
        if index:
            before = self.leaf_block(leaf, path, index - 1)
        else:
            adjacent, adjacent_path = self.neighbor(leaf, path, -1)
            before = () if adjacent is None else self.leaf_block(adjacent, adjacent_path, len(adjacent.keys) - 1)
        require(not before or before[-1].key < lower, "index_fence", "preceding block reaches sample range")

        while True:
            yield self.leaf_block(leaf, path, index)
            index += 1
            if index == len(leaf.keys):
                leaf, path = self.neighbor(leaf, path, 1)
                if leaf is None:
                    return
                index = 0

    def typed_edge(self, record, targets):
        require(record.size == 0x90, "edge_size", "in-range descriptor size disagrees")
        edge = record.address
        vptr = unpack("Q", self.read(edge, 8))[0]
        require(vptr == self.base + EDGE_VPTR, "edge_type_mismatch", "wrong in-range edge vptr")
        biom = unpack("I", self.read(edge + 0x60, 4))[0]
        require(
            biom != 0 and record.key[1] == biom,
            "edge_biom_mismatch",
            "edge second key and payload BIOM disagree",
        )
        override = words = None
        if biom in targets:
            override = unpack("I", self.read(edge + 0x6C, 4))[0]
            words = list(unpack("7I", self.read(edge + 0x70, 28, structural=False)))
        return {
            "edge": edge,
            "payload": edge + 0x20,
            "key": list(record.key),
            "biom": biom,
            "override": override,
            "vptr": vptr,
            "size": record.size,
            "words": words,
        }

    def collect_range(self, pndt, targets):
        k0 = (pndt << 32) | 0x10000 | self.discriminator
        lower, upper = (k0, 0), (k0, 0x0000FFFFFFFFFFFF)
        result = {
            "pndt": pndt,
            "lower": list(lower),
            "upper": list(upper),
            "preceding": None,
            "termination": None,
            "terminal": None,
            "entries": [],
            "reason": None,
        }
        if not self.root:
            result["termination"] = "empty_root"
            return result
        previous = None
        try:
            for block in self.range_blocks(lower):
                for record in block:
                    require(
                        previous is None or previous <= record.key,
                        "index_order",
                        "key order breaks between blocks",
                    )
                    previous = record.key
                    if record.key < lower:
                        result["preceding"] = list(record.key)
                    elif record.key > upper:
                        result["termination"] = "upper_fence"
                        result["terminal"] = list(record.key)
                        return result
                    else:
                        result["entries"].append(self.typed_edge(record, targets))
            result["termination"] = "root_end"
        except (NativeFailure, ReadFailure) as error:
            result["reason"], result["detail"] = error.code, error.detail
        return result

    def form_map(self):
        map_ = self.scalar(self.base + FORM_MAP_SLOT, "Q")
        require(map_ != 0, "form_map_unverified", "unpublished FormID map")
        pointer(map_, 0x20)
        self.claim(map_, 0x20, "form map")
        table, capacity = unpack("QQ", self.read(map_ + 0x10, 16, 8))
        require(
            0 < capacity < 0xFFFFFFFF and capacity & (capacity - 1) == 0,
            "form_map_unverified",
            "FormID capacity is not a supported power of two",
        )
        pointer(table, capacity * 0x18)
        if self.structural:
            # Reserve the full known allocation so unvisited bucket bytes
            # cannot also pass as independently owned form storage.
            self.claim(table, capacity * 0x18, "form map table")
        return {"map": map_, "table": table, "capacity": capacity}

    def form(self, form_id, expected_type):
        if form_id not in self.forms:
            if not hasattr(self, "map"):
                self.map = self.form_map()
            capacity, table = self.map["capacity"], self.map["table"]
            h = 0xCBF29CE484222325
            for byte in form_id.to_bytes(4, "little"):
                h = ((h ^ byte) * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
            index, seen = h & (capacity - 1), set()
            matched = None
            while True:
                require(index < capacity and index not in seen, "form_map_unverified", "invalid or cyclic FormID chain index")
                require(len(seen) < MAX_CHAIN, "traversal_budget", "FormID chain cap exceeded")
                seen.add(index)
                entry = table + 0x18 * index
                if not self.structural:
                    self.claim(entry, 0x18, "form map entry")
                key, address, next_ = unpack("I4xQI", self.read(entry, 20, 8))
                if next_ == 0xFFFFFFFF:
                    code = "form_absent" if len(seen) == 1 else "form_map_unverified"
                    raise NativeFailure(code, f"empty FormID chain slot for {form_id:08X}")
                require(next_ <= capacity, "form_map_unverified", "unknown FormID next sentinel")
                if key == form_id:
                    require(matched is None, "form_duplicate", f"duplicate FormID {form_id:08X} in chain")
                    matched = address
                    if not self.structural:
                        break
                if next_ == capacity:
                    require(matched is not None, "form_absent", f"FormID {form_id:08X} not in chain")
                    break
                index = next_
            address = matched
            size = {0xBA: 0x58, 0xA0: 0x318, RESOURCE_TYPE: 0x118}.get(expected_type, 0x2F)
            self.claim(address, size, f"form {form_id:08X}")
            actual_id, actual_type = unpack("I2xB", self.read(address + 0x28, 7, 4))
            require(actual_id == form_id, "form_id_mismatch", f"mapped form ID disagrees for {form_id:08X}")
            self.forms[form_id] = (address, actual_type)
        address, actual_type = self.forms[form_id]
        require(actual_type == expected_type, "form_type_mismatch", f"wrong record type for {form_id:08X}")
        return address

    def biome_rsgds(self, count, list_):
        """Join the actual BIOM pointer list to independent typed RSGD entries."""
        require(count <= MAX_BIOM_RSGDS, "rsgd_list_budget", "BIOM RSGD pointer count exceeds bound")
        if not count:
            return []
        self.claim(list_, count * 8, "BIOM RSGD list")
        addresses = unpack(f"{count}Q", self.read(list_, count * 8, 8))
        result = []
        for address in addresses:
            pointer(address, 0x2F)
            form_id = self.scalar(address + 0x28, "I")
            require(form_id != 0 and self.form(form_id, 0xAB) == address,
                    "rsgd_list_identity", "BIOM RSGD pointer differs from the authoritative form")
            result.append({"form_id": form_id, "address": address})
        return result

    def resource_forms(self, words, evidence):
        """Verify every observed nonzero ID independently of reference predictions."""
        for slot, form_id in enumerate(words):
            if not form_id:
                continue
            try:
                address = self.form(form_id, RESOURCE_TYPE)
                vptr = self.scalar(address, "Q")
                require(vptr == self.base + RESOURCE_VPTR, "form_vptr_mismatch", "wrong BGSResource vptr")
            except (NativeFailure, ReadFailure) as error:
                code = error.code if error.code in ("read_incomplete", "traversal_budget") else f"resource_{error.code}"
                raise NativeFailure(code, f"output slot {slot}, FormID {form_id:08X}: {error.detail}") from error
            evidence.append({"slot": slot, "form_id": form_id, "address": address, "type": RESOURCE_TYPE,
                             "vptr": vptr})

    def sample(self, request, range_):
        sample = {
            "pndt": request.pndt,
            "biom": request.biom,
            "edge": None,
            "payload": None,
            "override": None,
            "words": None,
            "reason": None,
        }
        if self.structural:
            sample["resource_forms"] = []
        try:
            matches = [entry for entry in range_["entries"] if entry["biom"] == request.biom]
            if len(matches) == 1:
                sample.update(matches[0])
            require(range_["reason"] is None, range_["reason"], range_.get("detail"))
            require(matches, "component_absent", "no matching typed edge")
            require(len(matches) == 1, "component_duplicate", "multiple matching typed edges")
            pndt = self.form(request.pndt, 0xBA)
            seed, key = unpack("II", self.read(pndt + 0x50, 8, 4))
            if self.structural:
                require(key == request.pndt, "pndt_key_mismatch", "PNDT generation key disagrees")
            else:
                require(key == request.pndt and seed == request.seed, "input_drift", "PNDT seed or generation key differs")
            biom = self.form(request.biom, 0xA0)
            count = self.scalar(biom + 0x308, "I")
            list_ = self.scalar(biom + 0x310, "Q")
            override = sample["override"]
            if self.structural:
                rsgd = {"biom_rsgds": self.biome_rsgds(count, list_)}
            else:
                expected = self.form(request.biom_rsgd, 0xAB)
                require(count == 1, "input_drift", "expected singleton BIOM RSGD list")
                require(self.scalar(list_, "Q") == expected, "input_drift", "BIOM RSGD pointer disagrees with independent map")
                require(override == request.override, "input_drift", "raw PNDT RSGD override differs")
                rsgd = {"biom_rsgd": expected}
            override_form = self.form(override, 0xAB) if override else None
            sample["forms"] = {
                "pndt": pndt,
                "pndt_seed": seed,
                "pndt_key": key,
                "biom": biom,
                "biom_rsgd_list": list_,
                **rsgd,
                "override": override_form,
            }
            require(range_["coverage_verified"], "range_coverage", "BIOM order or cardinality differs")
            if self.structural:
                self.resource_forms(sample["words"], sample["resource_forms"])
        except (NativeFailure, ReadFailure) as error:
            sample["reason"], sample["detail"] = error.code, error.detail
        return sample

    def revalidate(self, anchors):
        digest = hashlib.sha256()
        for bounds, prior in self.structure.items():
            require(
                self.exact(*bounds) == prior,
                "structural_change",
                f"structural witness changed at {bounds[0]:#x}",
            )
            digest.update(struct.pack("<QII", *bounds))
            digest.update(prior)
        for bounds in anchors:
            require(
                self.exact(*bounds) == self.structure[bounds],
                "structural_change",
                f"closing anchor changed at {bounds[0]:#x}",
            )
        return digest.hexdigest()


def collect(reader, image_base, requests, *, mode="strict"):
    """Collect one address-bearing typed witness from an admitted reader."""
    if mode not in ("strict", "structural"):
        raise ValueError("unknown observation mode")
    collection = Collection(reader, image_base, structural=mode == "structural")
    anchors = collection.anchors()
    anchor_reads = tuple(collection.structure)
    expected = {}
    for request in requests:
        expected.setdefault(request.pndt, []).append(request.biom)
    ranges = {}
    for pndt, bioms in expected.items():
        result = collection.collect_range(pndt, set(bioms))
        result["expected_bioms"] = bioms
        result["coverage_verified"] = result["reason"] is None and [
            entry["biom"] for entry in result["entries"]
        ] == bioms
        ranges[pndt] = result
    require(
        sum(len(block) for block in collection.blocks.values()) <= collection.total,
        "index_shape",
        "inspected unique entries exceed the tree total",
    )
    samples = [collection.sample(request, ranges[request.pndt]) for request in requests]
    structural_sha256 = collection.revalidate(anchor_reads)
    return {
        "anchors": anchors,
        "ranges": list(ranges.values()),
        "samples": samples,
        "form_map": getattr(collection, "map", None),
        "structural_sha256": structural_sha256,
        "read_count": collection.read_count,
        "bytes_read": collection.byte_count,
    }
