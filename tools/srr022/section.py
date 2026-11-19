"""Locate PlayerKnowledge from the start of the pinned unit-6 payload."""

import struct


# Writer calls in FUN_141822570 order, before 0x141822732. Each prefix
# table has a u32 count. Fixed widths include the key. Variable records
# have a six-byte key, zero or more u32-length strings, then fixed fields.
# Only lengths are needed here. Section 10 uses a different (10-byte) key.
PREFIX = (
    # writer VA, fixed bytes per record, number of length-prefixed strings
    (0x1424B5AA0, 6, 1),
    (0x14140E8C0, 22, 0),
    (0x14140EB70, 31, 1),
    (0x14140EE40, 7, 0),
    (0x14140F0B0, 10, 0),
    (0x14140F320, 7, 1),
    (0x14140F5A0, 10, 0),
    (0x14140F810, 10, 0),
    (0x14140FA80, 10, 0),
    (0x14140FCF0, 14, 0),
    (0x14140FF80, 30, 0),
    (0x141410220, 6, 0),
    (0x141410470, 31, 0),
    (0x141410770, 10, 0),
    (0x1414109E0, 66, 0),
    (0x141410C60, 18, 0),
    (0x141410EE0, 10, 5),
)


def locate_records(unit):
    """Return count offset and the half-open spans of the preceding tables."""
    def count_at(offset):
        if offset + 4 > len(unit):
            raise ValueError("truncated component count or string length")
        return struct.unpack_from("<I", unit, offset)[0]

    pos = 0
    prefix = []
    for writer, fixed, strings in PREFIX:
        start = pos
        count = count_at(pos)
        pos += 4
        if count * (fixed + 4 * strings) > len(unit) - pos:
            raise ValueError(f"component table at {start} exceeds unit 6")
        if strings:
            for _ in range(count):
                pos += 6
                for _ in range(strings):
                    pos += 4 + count_at(pos)
                pos += fixed - 6
                if pos > len(unit):
                    raise ValueError(f"component string at table {start} exceeds unit 6")
        else:
            pos += fixed * count
        prefix.append(dict(writer=hex(writer), offset=start, end=pos, count=count))
    count_at(pos)
    return pos, prefix
