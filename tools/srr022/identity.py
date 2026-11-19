"""Map a unit-6 stream word to its saved plugin/local identity, if justified."""

import struct
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path


def plugin_lists(block):
    """Read the form-version 153 profile of FUN_141813760 / FUN_141812E80."""
    pos = 0

    def take(size):
        nonlocal pos
        if size > len(block) - pos:
            raise ValueError("truncated plugin entry")
        start = pos
        pos += size
        return block[start:pos]

    def integer(size):
        return int.from_bytes(take(size), "little")

    def string():
        return take(integer(2))

    groups = []
    names = set()
    for count_width in (1, 2, 4):
        group = []
        count = integer(count_width)
        if count > (len(block) - pos) // 4:
            raise ValueError("plugin count exceeds bounded block")
        for _ in range(count):
            start = pos
            name = bytes(string()).decode("ascii").lower()
            if not name or name in names or any(c in name for c in "/\\:\x00"):
                raise ValueError("invalid or ambiguous saved plugin name")
            names.add(name)
            group.append((name, start))
            metadata = integer(1)
            if metadata not in (0, 1):
                raise ValueError("unsupported plugin metadata flag")
            if metadata:
                for _ in range(3):
                    string()
                take(1)
        groups.append(tuple(group))
    take(2)  # Paired load advances by two at 0x141813A56.
    if pos != len(block):
        raise ValueError("trailing bytes in plugin block")
    return tuple(groups)


@dataclass
class IdentityMap:
    raw: bytes
    plugins: tuple
    array_offset: int
    count: int
    plugin_offsets: tuple
    full_flags: tuple
    header_evidence: dict

    @classmethod
    def from_stream(cls, raw, plugin_size_offset, flt_offset, plugin_directory=None):
        """Offsets refer to the entire decompressed SFS_SAVEGAME stream."""
        if not 0 <= plugin_size_offset <= flt_offset - 4 <= len(raw) - 104:
            raise ValueError("invalid plugin block or file location table offset")
        size, = struct.unpack_from("<I", raw, plugin_size_offset)
        if plugin_size_offset + 4 + size != flt_offset:
            raise ValueError("plugin size disagrees with file location table")
        plugin_start = plugin_size_offset + 4
        entries = plugin_lists(memoryview(raw)[plugin_start:flt_offset])
        groups = tuple(tuple(name for name, _ in group) for group in entries)
        locations = tuple(tuple(plugin_start + pos for _, pos in group) for group in entries)
        start, end = struct.unpack_from("<II", raw, flt_offset)
        if not flt_offset + 100 <= start <= end - 4 <= len(raw) - 4:
            raise ValueError("invalid form array bounds")
        count, = struct.unpack_from("<I", raw, start)
        if start + 4 + 4 * count != end:
            raise ValueError("form array count disagrees with next location")
        evidence = {}
        if plugin_directory is not None:
            for path in Path(plugin_directory).iterdir():
                name = path.name.lower()
                if name not in groups[0] or not path.is_file():
                    continue
                if name in evidence:
                    raise ValueError("ambiguous local plugin filename")
                with path.open("rb") as stream:
                    header = stream.read(24)
                if len(header) != 24 or header[:4] != b"TES4":
                    raise ValueError(f"invalid TES4 header for {name}")
                evidence[name] = dict(flags=struct.unpack_from("<I", header, 8)[0],
                                      header_offset=0, header_bytes=24,
                                      header_sha256=sha256(header).hexdigest())
        flags = tuple(evidence[name]["flags"] if name in evidence else None for name in groups[0])
        return cls(raw, groups, start, count, locations, flags, evidence)

    def full_index(self, slot):
        # 14180AED1–AF17 increments a nonzero slot for each leading overlay,
        # stopping at the first ordinary plugin after slot zero. A selected
        # overlay redirects through a master at 1405B78DC; leave it unresolved.
        selected = slot
        for i, flags in enumerate(self.full_flags):
            if flags is None or flags & 0x500:
                return None, []
            if flags & 0x200:
                selected += 1
            elif i:
                break
        if selected >= len(self.full_flags):
            return None, []
        flags = self.full_flags[selected]
        if flags is None or flags & 0x700:
            return None, []
        return selected, sorted(set(range(i + 1)) | {selected})

    def resolve(self, word):
        """Return saved identity. Runtime plugin presence and redirects are separate."""
        result = dict(raw=word, normalized=None, status="UNRESOLVED_IDENTITY",
                      saved_form_id=None, array_offset=None)
        if not 0 <= word <= 0xFFFFFF:
            return dict(result, reason="outside native writer's 24-bit output")
        tag = word >> 22
        payload = word & 0x3FFFFF
        result["tag"] = tag
        if tag == 3:
            return dict(result, reason="overlapping tag bits; writer origin ambiguous")
        if tag == 2:
            return dict(result, saved_form_id=0xFF000000 | payload,
                        reason="save-scoped dynamic ID")
        if tag == 1:
            if not payload:
                return dict(result, reason="noncanonical direct zero")
            value = payload
        elif word == 0:
            return dict(result, saved_form_id=0, status="NULL_ID", reason="reserved zero key")
        elif word > self.count:
            return dict(result, reason="index outside saved form array")
        else:
            # Native reset reserves key zero. The first serialized row uses key one.
            offset = self.array_offset + 4 * word
            result["array_offset"] = offset
            value, = struct.unpack_from("<I", self.raw, offset)
        result["saved_form_id"] = value
        kind = value >> 24
        if kind == 0xFE:
            group, index, local = 1, (value >> 12) & 0xFFF, value & 0xFFF
        elif kind == 0xFD:
            group, index, local = 2, (value >> 16) & 0xFF, value & 0xFFFF
        elif kind == 0:
            if not value:
                return dict(result, status="NULL_ID", reason="zero form-array value")
            group, index, local = 0, 0, value
        elif kind == 0xFF:
            return dict(result, reason="save-scoped dynamic array value")
        else:
            index, consulted = self.full_index(kind)
            if index is None:
                return dict(result, reason="full-plugin flags missing or slot unsupported")
            group, local = 0, value & 0xFFFFFF
            result["identity_basis"] = "SAVED_PLUGIN_LIST_WITH_PRESENT_TES4_FLAGS"
            result["header_plugins"] = [self.plugins[0][i] for i in consulted]
        if index >= len(self.plugins[group]):
            return dict(result, reason="index outside saved plugin list")
        plugin = self.plugins[group][index]
        result.setdefault("identity_basis", "SAVED_PLUGIN_LIST")
        return dict(result, normalized=f"{plugin}:{local:06X}", status="SAVED_PLUGIN_LOCAL",
                    plugin_name_length_offset=self.plugin_offsets[group][index])
