"""Bounded PlayerKnowledge records for the pinned retail unit-6 stream.

Pass the complete, bounded unit payload and the offset of the component
count established by its enclosing reader. Offsets in the output use that
input's coordinate system. FormIDs here are raw four-byte stream values.
"""

import struct


class Cursor:
    def __init__(self, data, offset):
        if not 0 <= offset <= len(data):
            raise ValueError(f"component offset outside unit: {offset}")
        self.data = data
        self.offset = offset

    def read(self, size):
        start = self.offset
        if size > len(self.data) - start:
            raise ValueError(f"truncated component at {start:#x}, need {size} bytes")
        self.offset += size
        return self.data[start:self.offset]

    def number(self, fmt):
        return struct.unpack("<" + fmt, self.read(struct.calcsize("<" + fmt)))[0]

    def count(self, fmt, min_size):
        start = self.offset
        count = self.number(fmt)
        if count > (len(self.data) - self.offset) // min_size:
            raise ValueError(f"count {count} at {start:#x} exceeds remaining unit bytes")
        return count

    def ids(self, count_format):
        return [
            {"offset": self.offset, "raw": self.number("I")}
            for _ in range(self.count(count_format, 4))
        ]


def read_items(cursor, version):
    # ID and +0x21 always occur. +0x20 and the nested list have independent
    # version gates in FUN_142337A50 at 0x142337E9E and 0x142337EC3.
    min_size = 5 + int(version >= 2) + (8 if version >= 1 else 0)
    count = cursor.count("Q", min_size)
    items = []
    seen = set()
    for _ in range(count):
        start = cursor.offset
        item_id = cursor.number("I")
        if item_id in seen:
            raise ValueError(f"duplicate raw item {item_id:#x} at {start:#x}")
        seen.add(item_id)
        progress = cursor.number("B")
        other = cursor.number("B") if version >= 2 else None
        nested = cursor.ids("Q") if version >= 1 else None
        items.append({
            "offset": start, "end": cursor.offset, "item_raw": item_id,
            "progress_21": progress, "byte_20": other, "nested_ids": nested,
        })
    return items


def decode_records(data, offset=0):
    """Return (serialized records, first unconsumed offset). No identity inference."""
    cursor = Cursor(data, offset)
    records = []
    keys = set()
    for _ in range(cursor.count("I", 20)):
        start = cursor.offset
        body, key_low, mask, version, level = struct.unpack("<IHIHi", cursor.read(16))
        if version > 3:
            raise ValueError(f"unsupported PlayerKnowledge version {version} at {start:#x}")
        key = (body, key_low)
        if key in keys:
            raise ValueError(f"duplicate raw component key {key} at {start:#x}")
        keys.add(key)
        auxiliary = cursor.ids("I")
        items = read_items(cursor, version) if mask & 8 else None
        trailer = None
        if version >= 3:
            # FUN_142337790 writes each tree node's twelve bytes verbatim.
            trailer = [
                {"offset": cursor.offset, "hex": cursor.read(12).hex()}
                for _ in range(cursor.count("Q", 12))
            ]
        records.append({
            "offset": start, "end": cursor.offset, "body_raw": body, "key_low": key_low,
            "mask": mask, "version": version, "scan_level": level,
            "auxiliary_ids": auxiliary, "items": items, "trailer": trailer,
        })
    return records, cursor.offset
