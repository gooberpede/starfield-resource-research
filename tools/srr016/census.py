"""Whole-tree +0x300 census and checked replay for an owned fixture."""

from bisect import bisect_left
from contextlib import ExitStack
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import struct
import sys
from time import monotonic_ns, sleep, time_ns

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "srr013"))
from checkpoint import claim, validate_capture_marker, validate_identity, validate_marker
from contract import RETAIL_APPLICABILITY, STRUCTURAL_MODE
from memory import ReadFailure
from native import (
    BLOCK, EDGE_VPTR, MAX_BIOM_RSGDS, MAX_CHAIN, MAX_KEYS, NODE_END,
    RESOURCE_TYPE, Collection, NativeFailure, Node, pointer, require, unpack,
)
from observe import (
    GAP_NS, GAP_SEC, AcquisitionStop, JournalFailure, RecordingReader, ReplayReader,
    add_timing, encode, pending_journal,
)


RECEIPT_SCHEMA = "srr016-disposable-census-v1"
OBSERVATION_SCHEMA = "srr016-observation-v1"
RETAIL_SHA256 = RETAIL_APPLICABILITY["sha256"]
CANONICAL = re.compile(r"[^:/\\\x00-\x1f]{1,255}\.(?:esm|esl|esp):[0-9A-F]{6}")
RUNTIME_ID = re.compile(r"[0-9A-F]{8}")
ERRORS = (NativeFailure, ReadFailure, AcquisitionStop)
FIXTURE_NAME = "srr016-fixture.exe"

# Disposable envelope. The large fixture reaches 5,120 descriptors in under 512
# windows. Leave capacity for uneven final groups, finite decoy chains and
# explicit refusal controls. These are independent of the read tree header.
LIMITS = {
    "entries": 5120,
    "tree_windows": 512,
    "tree_depth": 4,
    "form_capacity": 16384,
    "form_chain": MAX_CHAIN,
    "biom_rsgds": MAX_BIOM_RSGDS,
    "map_entries": 4096,
    "remap_entries": 8192,
    "events": 40_000,
    "requested_bytes": 16 * 1024 * 1024,
    "journal_bytes": 64 * 1024 * 1024,
}


def validate_remap(remap):
    """Validate an independently furnished, one-to-one runtime ID witness."""
    if not isinstance(remap, dict) or len(remap) > LIMITS["remap_entries"]:
        raise ValueError("invalid remap manifest size")
    seen = set()
    for runtime, canonical in remap.items():
        if (not isinstance(runtime, str) or not RUNTIME_ID.fullmatch(runtime)
                or runtime == "00000000" or not isinstance(canonical, str)
                or not CANONICAL.fullmatch(canonical) or canonical in seen
                or canonical.rsplit(":", 1)[0] != canonical.rsplit(":", 1)[0].lower()):
            raise ValueError("invalid or contradictory runtime ID remap")
        seen.add(canonical)


class WholeCollection(Collection):
    """Reuse the SRR-013 structural witnesses within a full-root census."""

    def __init__(self, reader, base, remap, limits):
        super().__init__(reader, base, structural=True)
        self.remap = remap
        self.limits = limits
        self.starts = []
        self.windows = set()
        self.slot_offsets = {}
        self.map_indices = {}
        self.map_keys = {}
        self.form_chains = {}
        self.input_refs = set()
        self.records = []
        self.attempted = []
        self.raw_rows = []
        self.rows = []
        self.leaves = []
        self.block_count = 0
        self.non_target_count = 0
        self.previous_key = None
        self.coverage_verified = False
        self.remap_missing = set()
        self.reading_inputs = False

    def exact(self, address, size, alignment):
        self.read_count += 1
        self.byte_count += size
        data = self.reader.read(address, size, alignment)
        require(len(data) == size, "read_incomplete", f"short read at {address:#x}")
        return data

    def claim(self, address, size, identity):
        pointer(address, size)
        end = address + size
        if address in self.extents:
            require(self.extents[address] == (end, identity), "pointer_alias",
                    f"conflicting ownership at {address:#x} for {identity}")
            return
        position = bisect_left(self.starts, address)
        require(
            (not position or self.extents[self.starts[position - 1]][0] <= address)
            and (position == len(self.starts) or end <= self.starts[position]),
            "pointer_alias", f"{identity} overlaps another claimed range at {address:#x}",
        )
        self.starts.insert(position, address)
        self.extents[address] = (end, identity)

    def window(self, address):
        require(address not in self.windows, "pointer_alias", f"revisited tree window {address:#x}")
        require(len(self.windows) < self.limits["tree_windows"], "traversal_budget", "tree window cap exceeded")
        self.claim(address, NODE_END, "tree window")
        self.windows.add(address)
        return self.read(address, NODE_END, 8)

    def form_map(self):
        mapping = super().form_map()
        require(mapping["capacity"] <= self.limits["form_capacity"], "traversal_budget",
                "FormID capacity exceeds the independent envelope")
        return mapping

    def map_entry(self, index):
        if index not in self.map_indices:
            require(len(self.map_indices) < self.limits["map_entries"], "traversal_budget",
                    "distinct FormID chain entry cap exceeded")
            address = self.map["table"] + index * 0x18
            key, form, next_ = unpack("I4xQI", self.read(address, 20, 8))
            if next_ != 0xFFFFFFFF:
                require(key and next_ <= self.map["capacity"], "form_map_unverified",
                        f"invalid occupied FormID entry at index {index}")
                require(key not in self.map_keys, "form_duplicate",
                        f"duplicate FormID {key:08X} at indices {self.map_keys.get(key)} and {index}")
                # Read and claim a header for every traversed occupant, even a decoy.
                # Check the prefix before dereferencing it to read the type byte.
                pointer(form, 0x2F)
                require(not self.map["table"] <= form < self.map["table"] + 0x18 * self.map["capacity"],
                        "pointer_alias", "FormID chain object points into the table")
                actual_id, actual_type = unpack("I2xB", self.read(form + 0x28, 7, 4))
                require(actual_id == key, "form_id_mismatch", f"mapped form ID disagrees for {key:08X}")
                size = {0xBA: 0x58, 0xA0: 0x318, RESOURCE_TYPE: 0x118}.get(actual_type, 0x2F)
                self.claim(form, size, f"form {key:08X}")
                self.map_keys[key] = index
                result = (key, form, actual_type, next_)
            else:
                result = (key, form, None, next_)
            self.map_indices[index] = result
        return self.map_indices[index]

    def form(self, form_id, expected_type):
        if self.reading_inputs:
            self.input_refs.add(form_id)
        if form_id not in self.forms:
            capacity = self.map["capacity"]
            hash_ = 0xCBF29CE484222325
            for byte in form_id.to_bytes(4, "little"):
                hash_ = ((hash_ ^ byte) * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
            index = hash_ & (capacity - 1)
            seen = self.form_chains[form_id] = set()
            matched = None
            while index != capacity:
                self.reader.pulse()
                require(index not in seen, "form_map_unverified", "cyclic FormID chain")
                require(len(seen) < self.limits["form_chain"], "traversal_budget", "FormID chain cap exceeded")
                seen.add(index)
                key, address, actual_type, index = self.map_entry(index)
                if index == 0xFFFFFFFF:
                    code = "form_absent" if len(seen) == 1 else "form_map_unverified"
                    raise NativeFailure(code, f"empty FormID chain slot for {form_id:08X}")
                if key == form_id:
                    matched = address, actual_type
            require(matched is not None, "form_absent", f"FormID {form_id:08X} not in chain")
            self.forms[form_id] = matched
        address, actual_type = self.forms[form_id]
        require(actual_type == expected_type, "form_type_mismatch", f"wrong record type for {form_id:08X}")
        return address

    def normalize_id(self, runtime):
        key = f"{runtime:08X}"
        canonical = self.remap.get(key)
        if canonical is None:
            self.remap_missing.add(key)
        return canonical

    def typed_inputs(self, pndt, biom, override):
        self.reading_inputs = True
        try:
            owner_form = self.form(pndt, 0xBA)
            owner_seed, owner_key = unpack("II", self.read(owner_form + 0x50, 8, 4))
            require(pndt == owner_key, "pndt_key_mismatch", "PNDT generation key disagrees")
            biom_form = self.form(biom, 0xA0)
            count = self.scalar(biom_form + 0x308, "I")
            require(count <= self.limits["biom_rsgds"], "rsgd_list_budget",
                    "BIOM RSGD list exceeds the independent envelope")
            list_ = self.scalar(biom_form + 0x310, "Q")
            rsgds = self.biome_rsgds(count, list_)
            override_form = None
            override_reason = None
            if override:
                try:
                    override_form = self.form(override, 0xAB)
                except NativeFailure as error:
                    if error.code not in {"form_absent", "form_type_mismatch"}:
                        raise
                    # A completed lookup can resolve this optional input to null.
                    override_reason = error.code
            return {"pndt": owner_form, "pndt_seed": owner_seed, "biom": biom_form,
                    "biom_rsgd_list": list_, "biom_rsgds": rsgds,
                    "override": override_form, "override_reason": override_reason}
        finally:
            self.reading_inputs = False

    def typed(self, data, diagnostic, offset, k0, k1, size, wrapper):
        require(wrapper and (k0 & 0xFFFFFFFF) == (0x10000 | self.discriminator) and k0 >> 32,
                "edge_type_mismatch", "target discriminator, key encoding or wrapper disagrees")
        require(size == 0x90, "edge_size", "typed edge is not 0x90 bytes")
        biom, coverage, seed, override, *slots = struct.unpack_from("<11I", data, offset + 0x60)
        diagnostic.update(coverage_word=coverage, seed=seed, override=override, raw_slots=slots,
                          slot_bytes=data[offset + 0x70:offset + 0x8C].hex())
        require(biom and biom == k1, "edge_biom_mismatch", "raw key BIOM and inline BIOM disagree")
        diagnostic["forms"] = self.typed_inputs(k0 >> 32, biom, override)
        resources = diagnostic["resources"] = []
        self.resource_forms(slots, resources)
        return {
            "raw_key": [k0, k1],
            "typed": "VERIFIED",
            "raw_slots": slots,
        }

    def classify_record(self, data, address, path, ordinal, size, offset):
        self.reader.pulse()
        vptr, k0, k1 = struct.unpack_from("<Q8xQQ", data, offset)
        key = k0, k1
        diagnostic = {"path": list(path), "ordinal": ordinal, "edge": address + offset,
                      "size": size, "vptr": vptr, "raw_key": list(key)}
        self.records.append(diagnostic)
        wrapper = vptr == self.base + EDGE_VPTR
        target = wrapper or k0 & 0xFFFF == self.discriminator
        if target:
            self.attempted.append(diagnostic)
        try:
            require(self.previous_key != key, "duplicate_identity", "duplicate mixed key")
            require(self.previous_key is None or self.previous_key < key,
                    "index_order", "descriptor order breaks across the root traversal")
            self.previous_key = key
            if not target:
                require(vptr != 0 and (k0 or k1), "mixed_prefix_unverified",
                        "mixed edge prefix contains no wrapper or key")
                self.non_target_count += 1
                diagnostic["classification"] = "MIXED_EXCLUSION"
                return key
            row = self.typed(data, diagnostic, offset, k0, k1, size, wrapper)
        except ERRORS as error:
            diagnostic.update(classification="REFUSED", failure=[error.code, error.detail])
            raise
        self.raw_rows.append(row)
        self.slot_offsets.setdefault(address, []).append(offset + 0x70)
        diagnostic["classification"] = "TARGET"
        return key

    def packed(self, data, address, path, fences, advertised=None):
        self.block_count += 1
        marker, count, directory, holes, frontier = struct.unpack_from("<IIHHI", data)
        require(marker == BLOCK and 0 < count <= (NODE_END - 0x10) // (4 + 0x20)
                and directory == 0x10 + count * 4 and directory <= frontier < NODE_END
                and holes <= NODE_END - frontier,
                "index_shape", "malformed packed block header or occupancy")
        require(len(self.records) + count <= min(self.total, self.limits["entries"]),
                "index_shape", "packed descriptors exceed the admitted mixed count")
        descriptors = list(struct.iter_unpack("<HH", data[0x10:directory]))
        occupied = 0
        end = frontier
        for size, offset in sorted(descriptors, key=lambda descriptor: descriptor[1]):
            require(size >= 0x20 and end <= offset and offset + size <= NODE_END,
                    "record_span", "overlapping, truncated or out-of-fence packed span")
            occupied += size
            end = offset + size
        require(NODE_END - frontier - occupied == holes, "index_shape", "incorrect packed hole credit")
        keys = tuple(self.classify_record(data, address, path, ordinal, size, offset)
                     for ordinal, (size, offset) in enumerate(descriptors))
        require(advertised is None or keys[0] == advertised, "block_minimum", "invalid leaf block minimum")
        self.check_fences(keys, fences)

    def walk(self, address, path=(), fences=(), level=None):
        data = self.window(address)
        marker, count = struct.unpack_from("<II", data)
        if marker == BLOCK:
            require(level is None, "index_shape", "packed block at an internal child position")
            self.packed(data, address, path, fences)
            return
        require(marker <= self.limits["tree_depth"], "traversal_budget", "tree depth cap exceeded")
        require(level is None or marker == level, "index_shape", "child level disagrees")
        require(count <= MAX_KEYS and (marker or count), "index_shape", "invalid node directory count")
        if marker:
            key_base, children_base, children_count = 0x8, 0xA88, count + 1
        else:
            key_base, children_base, children_count = 0x18, 0xA98, count
        keys = tuple(struct.iter_unpack("<QQ", data[key_base:key_base + count * 16]))
        require(keys == tuple(sorted(keys)), "index_order", "node keys are not ordered")
        self.check_fences(keys, fences)
        children = struct.unpack_from(f"<{children_count}Q", data, children_base)
        if marker:
            node = Node(address, marker, keys, children)
            for index, child in enumerate(children):
                self.walk(child, path + (index,), fences + ((node, index),), marker - 1)
        else:
            next_, previous = struct.unpack_from("<QQ", data, 8)
            if self.leaves:
                prior, prior_next, _ = self.leaves[-1]
                require(previous == prior and prior_next == address,
                        "leaf_link_mismatch", "leaf links disagree with root traversal")
            else:
                require(previous == 0, "leaf_link_mismatch", "first leaf has a predecessor")
            self.leaves.append((address, next_, previous))
            for index, (minimum, child) in enumerate(zip(keys, children, strict=True)):
                self.packed(self.window(child), child, path + (index,), fences, minimum)

    def collect(self):
        self.publication = self.anchors()
        self.map = self.form_map()
        opening_reads = tuple(self.structure)
        require(self.total <= self.limits["entries"], "traversal_budget", "mixed descriptor cap exceeded")
        if self.root:
            self.walk(self.root)
        require(not self.leaves or self.leaves[-1][1] == 0,
                "leaf_link_mismatch", "last leaf has a successor")
        require(len(self.records) == self.total == self.non_target_count + len(self.raw_rows),
                "index_shape", "mixed descriptor count does not reconcile")

        self.normalize()
        self.witness_sha256 = self.revalidate(opening_reads)
        structure_digest = sha256()
        for bounds, prior in self.structure.items():
            self.reader.pulse()
            if bounds not in opening_reads and bounds[0] not in self.windows:
                continue
            offsets = self.slot_offsets.get(bounds[0]) if bounds[1] == NODE_END else None
            if offsets:
                projected = bytearray(prior)
                for offset in offsets:
                    projected[offset:offset + 28] = b"\0" * 28
            else:
                projected = prior
            structure_digest.update(struct.pack("<QII", *bounds))
            structure_digest.update(projected)
        self.tree_identity_sha256 = structure_digest.hexdigest()
        input_digest = sha256()
        indices = set()
        for form in self.input_refs:
            self.reader.pulse()
            indices.update(self.form_chains[form])
        for index in sorted(indices):
            self.reader.pulse()
            input_digest.update(encode([index, self.map_indices[index]]))
        for row in self.attempted:
            self.reader.pulse()
            input_digest.update(encode(row["forms"]))
        self.typed_input_sha256 = input_digest.hexdigest()
        self.coverage_verified = True

    def normalize(self):
        rows = []
        for row in self.raw_rows:
            self.reader.pulse()
            k0, k1 = row["raw_key"]
            rows.append({**row, "key": [self.normalize_id(k0 >> 32), self.normalize_id(k1)],
                         "slots": [self.normalize_id(slot) if slot else None for slot in row["raw_slots"]]})
        if self.remap_missing:
            return
        self.rows = sorted(rows, key=lambda row: row["key"])
        reconstructed = sorted((self.remap[f"{record['raw_key'][0] >> 32:08X}"],
                                self.remap[f"{record['raw_key'][1]:08X}"]) for record in self.attempted)
        require(reconstructed == [tuple(row["key"]) for row in self.rows]
                and len(set(reconstructed)) == len(reconstructed),
                "duplicate_identity", "raw-to-canonical target key sets do not reconcile")

    def report(self):
        return {
            "publication": getattr(self, "publication", None),
            "form_map": getattr(self, "map", None),
            "coverage_verified": self.coverage_verified,
            "tree_identity_sha256": getattr(self, "tree_identity_sha256", None),
            "typed_input_sha256": getattr(self, "typed_input_sha256", None),
            "witness_sha256": getattr(self, "witness_sha256", None),
            "tree_windows": len(self.windows),
            "internal_nodes": len(self.windows) - len(self.leaves) - self.block_count,
            "blocks": self.block_count,
            "leaves": [list(leaf) for leaf in self.leaves],
            "mixed_visited": len(self.records),
            "mixed_excluded": self.non_target_count,
            "attempted_targets": len(self.attempted),
            "map_entries": len(self.map_indices),
            "remap_missing": sorted(self.remap_missing),
            "descriptors": self.records,
            "raw_rows": self.raw_rows,
            "rows": self.rows,
        }


class BoundedJournal:
    def __init__(self, journal, ceiling):
        self.journal = journal
        self.ceiling = ceiling
        self.size = 0

    def write(self, event):
        self.size += len(encode(event)) + 1
        if self.size + 128 > self.ceiling:
            raise JournalFailure("journal_budget", ValueError("private receipt byte cap exceeded"))
        self.journal.write(event)


class ExactRecordingReader(RecordingReader):
    pulse_count = 0

    def pulse(self):
        self.pulse_count += 1
        try:
            self._check_cancelled()
        except AcquisitionStop:
            self.journal.write({"kind": "compute_cancelled", "pulse": self.pulse_count})
            raise

    def read(self, address, size, alignment=1):
        def exact(address, size, alignment):
            data = self.reader.read(address, size, alignment)
            if len(data) != size:
                raise ReadFailure("read_incomplete", f"short read at {address:#x}")
            return data

        return self._record("read", [address, size, alignment], exact)


class ReceiptEvents:
    def __init__(self, first, remaining):
        self.current = first
        self.remaining = iter(remaining)

    def __iter__(self):
        return self

    def __next__(self):
        if self.current is None:
            raise StopIteration
        prior = self.current
        self.current = next(self.remaining, None)
        return prior


class CheckedReplayReader(ReplayReader):
    pulse_count = 0

    def pulse(self):
        self.pulse_count += 1
        if self.events.current == {"kind": "compute_cancelled", "pulse": self.pulse_count}:
            next(self.events)
            raise AcquisitionStop("operator_cancelled", "operator cancelled the observation")


def pair(reader, binding, remap, limits, gap):
    passes = []
    brackets = []
    failure = None
    try:
        for ordinal in range(2):
            reader.collection_boundary("start", ordinal)
            brackets.append([])
            collection = None
            try:
                start = reader.identity(STRUCTURAL_MODE)
                brackets[-1].append(start)
                validate_identity(binding, start)
                require(start == brackets[0][0], "process_identity_changed", "epoch or mapped image changed")
                collection = WholeCollection(reader, start["image_base"], remap, limits)
                collection.collect()
                end = reader.identity(STRUCTURAL_MODE)
                brackets[-1].append(end)
                require(start == end, "process_identity_changed", "epoch or mapped image changed")
            finally:
                if collection is not None:
                    passes.append(collection.report())
                reader.collection_boundary("end", ordinal)
            if ordinal == 0:
                gap()
        first, second = passes
        reader.pulse()
        require(first["tree_identity_sha256"] == second["tree_identity_sha256"],
                "pair_structure_mismatch", "the observations cover different rooted graphs")
        require(first["typed_input_sha256"] == second["typed_input_sha256"],
                "pair_identity_mismatch", "the observations cover different typed input witnesses")
        require(first["raw_rows"] == second["raw_rows"],
                "pair_value_mismatch", "seven raw slot words disagree between observations")
        require(first["witness_sha256"] == second["witness_sha256"],
                "pair_identity_mismatch", "the observations cover different complete form or map witnesses")
    except ERRORS as error:
        failure = [error.code, error.detail]
    return make_report(passes, brackets, failure, reader.calls, reader.bytes, remap)


def make_report(passes, brackets, failure, calls, byte_count, remap, *, admission_refused=False):
    structural = failure is None or failure[0] == "pair_value_mismatch"
    normalized = failure is None and not passes[0]["remap_missing"]
    status = "QUALIFIED" if structural else "ACQUISITION_INDETERMINATE"
    counts = {"mixed": passes[0]["mixed_visited"],
              "typed": len(passes[0]["raw_rows"])} if structural else None
    return {
        "collections": passes,
        "identity_brackets": brackets,
        "failure": failure,
        "admission_refusal_source": "ATTESTED_AT_ACQUISITION" if admission_refused else None,
        "structure": status,
        "normalization": ("QUALIFIED" if normalized else
                          "REMAP_UNRESOLVED" if failure is None else "ACQUISITION_INDETERMINATE"),
        "coverage_counts": counts,
        "events": calls,
        "requested_bytes": byte_count,
        "observation": {
            "schema": OBSERVATION_SCHEMA,
            "retail_sha256": RETAIL_SHA256,
            "input_sha256": None,
            "source": "OWNED_DISPOSABLE",
            "structure": status,
            "remap_sha256": sha256(encode(remap)).hexdigest(),
            "target_image_sha256": brackets[0][0]["image_sha256"] if brackets and brackets[0] else None,
            "acquisition": "QUALIFIED" if normalized else "ACQUISITION_INDETERMINATE",
            "mixed": passes[0]["mixed_visited"] if structural else None,
            "rows": passes[0]["rows"] if normalized else [],
        },
    }


def _checked_limits(limits):
    if limits is None:
        return dict(LIMITS)
    if not isinstance(limits, dict) or limits.keys() != LIMITS.keys() or any(
            type(value) is not int or not 0 < value <= LIMITS[key] for key, value in limits.items()):
        raise ValueError("receipt limits exceed the disposable qualification envelope")
    return limits


def source_identity():
    paths = ("srr016/census.py", "srr013/checkpoint.py", "srr013/contract.py",
             "srr013/memory.py", "srr013/native.py", "srr013/observe.py",
             "srr013/retail_admission.py")
    root = Path(__file__).resolve().parents[1]
    return sha256(encode({name: sha256((root / name).read_bytes()).hexdigest() for name in paths})).hexdigest()


def capture(path, attempt_directory, admission, binding, remap, *, limits=None,
            cancelled=None, between=None, after_read=None):
    """Capture exactly one bound pair. The admission context must be disposable."""
    if binding.get("target_kind") != "simulated" or binding.get("marker", {}).get("label") != "title":
        raise ValueError("only simulated title bindings are admitted by this implementation")
    custody = Path(attempt_directory).resolve(strict=True)
    private_root = (Path(__file__).resolve().parents[2] / ".local-work").resolve(strict=True)
    path = Path(path)
    if path.parent.resolve(strict=True) != custody or not custody.is_relative_to(private_root):
        raise ValueError("address-bearing capture must stay in private attempt custody")
    validate_remap(remap)
    limits = _checked_limits(limits)
    if len(remap) > limits["remap_entries"]:
        raise ValueError("remap exceeds the declared independent row ceiling")
    with pending_journal(path) as raw_journal, ExitStack() as stack:
        journal = BoundedJournal(raw_journal, limits["journal_bytes"])
        start = monotonic_ns()
        start_utc = time_ns()
        header = {"kind": "start", "schema": RECEIPT_SCHEMA, "limits": limits, "remap": remap,
                  "reader_source_sha256": source_identity(), "remap_sha256": sha256(encode(remap)).hexdigest(),
                  "start_ns": start, "start_utc_ns": start_utc,
                  "utc": datetime.now(timezone.utc).isoformat()}
        try:
            claim(custody, binding["attempt"])
            intake = {"mono_ns": monotonic_ns(), "utc_ns": time_ns()}
            validate_marker(binding, "title", intake["mono_ns"], intake["utc_ns"], STRUCTURAL_MODE)
            binding = {**binding, "marker_intake": intake}
            source = stack.enter_context(admission)
            if source.path.name.casefold() != FIXTURE_NAME:
                raise ReadFailure("ownership_unverified", "only the designated SRR-016 fixture is admitted")
            binding = {**binding, "steam_log": {name: raw.hex() for name, raw in source.admission_log.items()}}
        except ReadFailure as error:
            journal.write({**header, "binding": binding})
            failure = [error.code, error.detail]
            journal.write({"kind": "admission_refused", "failure": failure})
            report = make_report([], [], failure, 0, 0, remap, admission_refused=True)
            timing = []
        else:
            # Use the intake marker as the freshness boundary, before admission and acquisition.
            start = monotonic_ns()
            start_utc = time_ns()
            header.update(start_ns=start, start_utc_ns=start_utc)
            validate_capture_marker(binding, "title", start, start_utc, STRUCTURAL_MODE)
            journal.write({**header, "binding": binding})
            reader = ExactRecordingReader(source, journal, limits, after_read, cancelled)

            def gap():
                if between is not None:
                    between()
                sleep(GAP_SEC)

            report = pair(reader, binding, remap, limits, gap)
            timing = reader.timing
        end = monotonic_ns()
        add_timing(report, timing, start, end)
        journal.write({"kind": "report", "data": report, "end_ns": end})
    return report


def _load_receipt(path):
    if path.suffix == ".partial":
        raise ValueError("pending receipt was not durably published")
    if path.stat().st_size > LIMITS["journal_bytes"]:
        raise ValueError("receipt exceeds the disposable journal ceiling")
    digest = sha256()
    with path.open("rb") as stream:
        line = stream.readline(LIMITS["journal_bytes"])
        while line:
            if not line.endswith(b"\n"):
                raise ValueError("receipt line is unfinished")
            event = json.loads(line)
            if not isinstance(event, dict) or line != encode(event) + b"\n":
                raise ValueError("receipt event encoding is invalid")
            if event.get("kind") == "seal":
                if event != {"kind": "seal", "sha256": digest.hexdigest()} or stream.read(1):
                    raise ValueError("receipt seal disagrees")
                return
            digest.update(line)
            yield event
            line = stream.readline(LIMITS["journal_bytes"])
    raise ValueError("receipt has no seal")


def replay(path):
    """Reperform every declared acquisition operation and verify the sealed result."""
    path = Path(path)
    events = _load_receipt(path)
    header = next(events, None)
    if header is None or header.get("kind") != "start" or header.get("schema") != RECEIPT_SCHEMA:
        raise ValueError("unsupported receipt schema")
    if set(header) != {"kind", "schema", "limits", "remap", "reader_source_sha256", "remap_sha256",
                       "start_ns", "start_utc_ns", "utc", "binding"}:
        raise ValueError("invalid receipt header")
    if not all(type(header[field]) is int and header[field] > 0 for field in ("start_ns", "start_utc_ns")):
        raise ValueError("invalid receipt opening clocks")
    if header.get("reader_source_sha256") != source_identity():
        raise ValueError("receipt reader source differs from the replay source")
    limits = _checked_limits(header["limits"])
    if path.stat().st_size > limits["journal_bytes"]:
        raise ValueError("receipt exceeds the declared journal ceiling")
    binding, remap = header["binding"], header["remap"]
    if binding.get("target_kind") != "simulated" or binding.get("marker", {}).get("label") != "title":
        raise ValueError("unsupported target binding")
    validate_remap(remap)
    if len(remap) > limits["remap_entries"]:
        raise ValueError("remap exceeds the declared independent row ceiling")
    if header.get("remap_sha256") != sha256(encode(remap)).hexdigest():
        raise ValueError("receipt remap digest disagrees")
    first = next(events, None)
    if first is None:
        raise ValueError("receipt has no acquisition events or refusal")
    if first.get("kind") == "admission_refused":
        failure = first.get("failure")
        if set(first) != {"kind", "failure"} or not isinstance(failure, list) or len(failure) != 2 or not all(
                isinstance(field, str) and field for field in failure):
            raise ValueError("malformed admission refusal")
        report = make_report([], [], failure, 0, 0, remap, admission_refused=True)
        timing = []
    else:
        validate_capture_marker(binding, "title", header["start_ns"], header["start_utc_ns"], STRUCTURAL_MODE)
        events = ReceiptEvents(first, events)
        reader = CheckedReplayReader(events, limits)
        report = pair(reader, binding, remap, limits, lambda: None)
        timing = reader.timing
    recorded = next(events, None)
    if (recorded is None or recorded.get("kind") != "report" or type(recorded.get("end_ns")) is not int
            or recorded["end_ns"] < header["start_ns"]):
        raise ValueError("receipt does not close at the reproduced operation boundary")
    add_timing(report, timing, header["start_ns"], recorded["end_ns"])
    if recorded != {"kind": "report", "data": report, "end_ns": recorded["end_ns"]}:
        raise ValueError("receipt report differs from checked replay")
    if next(events, None) is not None:
        raise ValueError("receipt contains events after the report")
    return report
