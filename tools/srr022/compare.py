"""Compare two serialized PlayerKnowledge populations in saved plugin namespaces."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct

from .identity import IdentityMap
from .records import decode_records
from .save_container import extract_container
from .section import locate_records


def inventory(source, plugin_directory=None):
    raw, layout = extract_container(source)
    identities = IdentityMap.from_stream(raw, layout["plugin_size_offset"], layout["flt_offset"],
                                         plugin_directory=plugin_directory)
    unit = raw[layout["unit_start"]:layout["unit_end"]]
    start, prefix = locate_records(unit)
    records, end = decode_records(unit, start)
    # FUN_1414113F0 writes the next u32 count and two IDs plus a u16 per row.
    if end + 4 > len(unit):
        raise ValueError("missing successor component table")
    successor_count = struct.unpack_from("<I", unit, end)[0]
    successor_end = end + 4 + 10 * successor_count
    if successor_end + 4 > len(unit):
        raise ValueError("successor component table exceeds unit 6")

    for row in records:
        row["identity"] = identities.resolve(row["body_raw"])
        row["visit_bit"] = bool(row["mask"] & 2)
        row["item_section_bit"] = bool(row["mask"] & 8)
        row["reconstruction"] = {
            "status": "RECONSTRUCTION_PREDICTED",
            "key_low": row["key_low"],
            "stored_scan_level": row["scan_level"],
            "queried_scan_level": 4 if row["mask"] & 1 else row["scan_level"],
            "fresh_destination_item_count": len(row["items"] or []),
            "condition": "successful load with distinct translated item keys",
        }
        for entry in row["auxiliary_ids"]:
            entry["identity"] = identities.resolve(entry["raw"])
        for item in row["items"] or []:
            item["identity"] = identities.resolve(item["item_raw"])
            for entry in item["nested_ids"] or []:
                entry["identity"] = identities.resolve(entry["raw"])
    return {
        "evidence": "SERIALIZED", "sha256": hashlib.sha256(source).hexdigest(),
        "layout": layout, "unit_sha256": hashlib.sha256(unit).hexdigest(),
        "saved_plugin_lists": identities.plugins, "form_array_count": identities.count,
        "consulted_plugin_headers": identities.header_evidence,
        "prefix": prefix, "section": [start, end], "successor": [end, successor_end],
        "successor_count": successor_count, "records": records,
        "coordinate_system": "record and field offsets relative to unit_start in inflated SFS",
        "displayed_gameplay": "NOT_OBSERVED",
    }


def grouped(rows, body=False):
    by_id = {}
    unmatched = []
    for row in rows:
        identity = row["identity"]["normalized"]
        if identity is None:
            unmatched.append(row)
            continue
        key = (identity, row["key_low"]) if body else identity
        if key in by_id:
            raise ValueError(f"ambiguous normalized key {key} at {row['offset']}")
        by_id[key] = row
    return by_id, unmatched


def compare_entries(left, right, body=False):
    a, unknown_a = grouped(left, body)
    b, unknown_b = grouped(right, body)
    pairs = [(a.get(key), b.get(key)) for key in sorted(a.keys() | b.keys())]
    return pairs + [(row, None) for row in unknown_a] + [(None, row) for row in unknown_b]


def ids(entries):
    if entries is None:
        return None
    return ["NULL_ID" if e["identity"]["status"] == "NULL_ID"
            else e["identity"]["normalized"] for e in entries]


def fields(row, body):
    if body:
        return {
            **{key: row[key] for key in ("mask", "scan_level", "version", "item_section_bit")},
            "auxiliary_ids": ids(row["auxiliary_ids"]),
            "trailer": None if row["trailer"] is None else [x["hex"] for x in row["trailer"]],
        }
    return {
        "progress_21": row["progress_21"], "byte_20": row["byte_20"],
        "nested_ids": ids(row["nested_ids"]),
    }


def difference(a, b, body):
    row = a if a is not None else b
    identity = row["identity"]["normalized"]
    changed = []
    indeterminate = []
    if a is None or b is None:
        side = "right" if a is None else "left"
        state = ("only_" if identity is not None else "unjoinable_") + side
    else:
        left, right = fields(a, body), fields(b, body)
        for key, x in left.items():
            y = right[key]
            if (key in ("auxiliary_ids", "nested_ids") and isinstance(x, list)
                    and isinstance(y, list) and len(x) == len(y)):
                if any(i != j and i is not None and j is not None for i, j in zip(x, y)):
                    changed.append(key)
                elif None in x or None in y:
                    indeterminate.append(key)
            elif x != y:
                changed.append(key)
        state = "changed" if changed else "indeterminate" if indeterminate else "equal"
    return {"identity": identity, "state": state, "fields": changed,
            "conditional_on_plugin_headers": any(
                r and r["identity"].get("header_plugins") for r in (a, b)),
            "indeterminate_fields": indeterminate,
            "left": a["offset"] if a is not None else None,
            "right": b["offset"] if b is not None else None}


def compare(left, right):
    result = []
    for a, b in compare_entries(left, right, body=True):
        row = difference(a, b, True)
        row["key_low"] = (a or b)["key_low"]
        items = compare_entries((a or {}).get("items") or [], (b or {}).get("items") or [])
        row["items"] = [difference(x, y, False) for x, y in items]
        if row["state"].startswith("unjoinable_"):
            for item in row["items"]:
                item["state"] = row["state"]
        if a is not None and b is not None:
            states = {i["state"] for i in row["items"]}
            if states & {"unjoinable_left", "unjoinable_right", "indeterminate"}:
                row["indeterminate_fields"].append("items")
                if row["state"] == "equal":
                    row["state"] = "indeterminate"
            if ("changed" in states or len(a["items"] or []) != len(b["items"] or [])
                    or ("only_left" in states and "unjoinable_right" not in states)
                    or ("only_right" in states and "unjoinable_left" not in states)):
                row["fields"].append("items")
                row["state"] = "changed"
        result.append(row)
    return {
        "body_counts": dict(Counter(r["state"] for r in result)),
        "item_counts": dict(Counter(i["state"] for r in result for i in r["items"])),
        "body_fields_changed": dict(Counter(k for r in result for k in r["fields"])),
        "item_fields_changed": dict(Counter(k for r in result for i in r["items"] for k in i["fields"])),
        "bodies": result,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("left", type=Path)
    parser.add_argument("right", type=Path)
    parser.add_argument("--plugin-directory", type=Path,
                        help="optional matching plugin headers for full-slot resolution")
    args = parser.parse_args()
    left, right = (inventory(path.read_bytes(), args.plugin_directory)
                   for path in (args.left, args.right))
    print(json.dumps({"left": left, "right": right,
                      "comparison": compare(left["records"], right["records"])},
                     ensure_ascii=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
