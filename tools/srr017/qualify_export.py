"""Check every exported field against independent owned fixture truth."""

import argparse
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from struct import pack

from tools.srr016 import census, compare, qualify_census
from .export import comparator_observation, file_sha256, replay_export
from .source import NAMESPACE_SCHEMA, SourceIndex, build_manifest


def fixture_sources(path, exclude=None):
    # Independent fixture input inventory. Do not derive it from a receipt or the oracle.
    records = [("PNDT", word) for word in (*range(0x100000, 0x100000 + 342), 0x1FFFE0)]
    records += [("BIOM", word) for word in range(0x200000, 0x20000D)]
    records += [("RSGD", word) for word in range(0x300000, 0x300005)]
    records += [("IRES", word) for word in range(0x400000, 0x400040)]
    records = [(signature, word) for signature, word in records if word != exclude]
    hedr = b"HEDR" + pack("<HfII", 12, 1.0, len(records), 0)
    with path.open("xb") as stream:
        stream.write(pack("<4s5I", b"TES4", len(hedr), 1, 0, 0, 0) + hedr)
        for kind in ("PNDT", "BIOM", "RSGD", "IRES"):
            tag = kind.encode("ascii")
            group = b"".join(pack("<4s5I", tag, 0, 0, word, 0, 0)
                             for signature, word in records if signature == kind)
            stream.write(pack("<4sI4s3I", b"GRUP", 24 + len(group), tag, 0, 0, 0) + group)
    manifest = build_manifest([path])
    namespace = {"schema": NAMESPACE_SCHEMA, "authority": "OWNED_DISPOSABLE",
                 "plugins": [{"plugin": "fixture.esm", "kind": "full", "index": 0}]}
    return manifest, namespace


def canonical(word):
    return f"fixture.esm:{word:06X}" if word else None


def check_identity(value, word, signature, *, defining_only=False, native_only=False):
    assert value["runtime_form_id"] == word
    if word:
        assert value["native_status"] == "VERIFIED"
        assert value["source"]["signature"] == signature
        assert value["source"]["plugin"] == "fixture.esm"
        assert value["source"]["local_id"] == f"{word:06X}"
        assert value["source"]["source_record_id"] == (None if native_only else f"{word:08X}")
        assert value["source"]["winning_plugin"] == (None if defining_only else "fixture.esm")
        assert value["source"]["winning_record_id"] == (None if defining_only else f"{word:08X}")
        if defining_only:
            assert value["source"]["attribution"] == "WINNING_CONTENT_UNRESOLVED"
            if not native_only:
                assert value["source"]["candidate_plugins"] == ["fixture.esm"]
        assert value["source"]["comparator_id"] == canonical(word)
    else:
        assert value["native_status"] == "ZERO"
        assert value["source"] is None


def check_fields(case, dataset, *, expected_namespace=False, defining_only=False, native_only=False,
                 optional_history=False):
    expected = qualify_census.independent_truth(case)
    reference = [(first, second, lanes) for first, second, width, *lanes in expected if width == 144]
    assert dataset["acquisition"] == "QUALIFIED"
    pair = dict.fromkeys(("tree", "typed_inputs", "values", "complete_form_witnesses"), "AGREE")
    pair["source_identity"] = "AGREE" if expected_namespace else "UNOBSERVED"
    assert dataset["pair"] == pair
    compiled = [{"kind": "full", "index": 0, "plugin": "fixture.esm"}] if expected_namespace else None
    assert dataset["native_namespaces"] == [compiled, compiled]
    assert dataset["namespace_matches_source"] == ([True, True] if expected_namespace else [None, None])
    assert dataset["namespace_refusals"] == [None, None]
    assert dataset["unqualified_collections"] == []
    for count in dataset["collection_counts"]:
        assert count == {"coverage_verified": True, "mixed_declared": len(expected),
                         "mixed_visited": len(expected), "mixed_excluded": len(expected) - len(reference),
                         "targets_attempted": len(reference), "targets_verified": len(reference),
                         "targets_refused": 0, "mixed_refused": 0, "targets_with_source_issues": 0,
                         "source_issue_counts": {}}
    projected = compare.observed_rows(comparator_observation(dataset))
    for ordinal, (native, expected_row) in enumerate(zip(dataset["rows"], reference, strict=True)):
        first, second, lanes = expected_row
        owner = first >> 32
        key = canonical(owner), canonical(second)
        assert native["raw_key"] == [f"{first:016X}", f"{second:016X}"]
        assert native["source_issues"] == []
        check_identity(native["pndt"], owner, "PNDT", defining_only=defining_only, native_only=native_only)
        check_identity(native["biom"], second, "BIOM", defining_only=defining_only, native_only=native_only)
        assert native["pndt_seed"] == (owner * 17) & 0xFFFFFFFF
        assert native["biome_seed"] == (second * 313) & 0xFFFFFFFF
        assert native["coverage_word"] == 0x3F800000
        biome_relative = second - 0x200000
        for index, ref in enumerate(native["biom_rsgds"]):
            check_identity(ref, 0x300000 + (biome_relative + index) % 5, "RSGD",
                           defining_only=defining_only, native_only=native_only)
        assert len(native["biom_rsgds"]) == (513 if case == "many-rsgds" else 2)
        override = native["override_rsgd"]
        if case == "optional-absent" and ordinal == 0:
            assert override == {"runtime_form_id": 0x750000, "source": None,
                                "native_status": "RESOLVED_NULL", "reason": "form_absent"}
        else:
            check_identity(override, 0x300000 if second & 1 else 0, "RSGD",
                           defining_only=defining_only, native_only=native_only)
        for index, (word, slot) in enumerate(zip(lanes, native["slots"], strict=True)):
            assert (slot["ordinal"], slot["payload_offset"], slot["role"]) == (
                index, 80 + 4 * index, ("Common", "Uncommon", "Rare", "Exotic", "Unique",
                                        "Special", "Everywhere")[index])
            check_identity(slot, word, "IRES", defining_only=defining_only, native_only=native_only)
        assert projected[key]["raw_key"] == [first, second]
        assert projected[key]["raw_slots"] == lanes
        assert projected[key]["slots"] == list(map(canonical, lanes))
        if expected_namespace:
            typed_forms = [native["pndt"], native["biom"], override, *native["biom_rsgds"], *native["slots"]]
            assert all((optional_history and "native_source_plugins" not in form)
                       or form["native_source_plugins"] == ["fixture.esm"]
                       for form in typed_forms if form["native_status"] == "VERIFIED")
    assert set(projected) == {(canonical(first >> 32), canonical(second)) for first, second, _ in reference}
    return {"mixed": len(expected), "rows": len(reference), "lane_words": 7 * len(reference),
            "zero_rows": sum(not any(lanes) for _, _, lanes in reference),
            "all_seven_rows": sum(all(lanes) for _, _, lanes in reference)}


def check_portable(payload):
    for private_key in ("image_base", "address", "binding", "creation", "edge", "vptr", "identity_brackets"):
        assert f'"{private_key}":'.encode("ascii") not in payload
    assert b".local-work" not in payload


def write_json(path, value):
    payload = census.encode(value) + b"\n"
    check_portable(payload)
    with path.open("xb") as stream:
        stream.write(payload)
    return sha256(payload).hexdigest()


def check_adapter_refusals(dataset):
    missing_row, wrong_runtime, wrong_status = [deepcopy(dataset) for _ in range(3)]
    missing_row["rows"].pop()
    wrong_runtime["rows"][0]["pndt"]["runtime_form_id"] += 1
    wrong_status["rows"][0]["biom"]["native_status"] = "UNVERIFIED"
    for altered in (missing_row, wrong_runtime, wrong_status):
        try:
            comparator_observation(altered)
        except ValueError:
            continue
        raise AssertionError("adapter admitted inconsistent portable evidence")


def run(receipts, output, admitted=None):
    output.mkdir()
    manifest, namespace = fixture_sources(output / "fixture.esm")
    source = SourceIndex(manifest, namespace)
    write_json(output / "source.json", manifest)
    write_json(output / "namespace.json", namespace)
    summary = {"identity_sha256": source.identity_sha256, "positive": {}, "negative": {}}
    for case in ("empty", "direct", "all-seven", "corpus", "upper", "optional-absent", "aba", "missing-remap"):
        path = receipts / f"{case}.jsonl"
        receipt_sha256 = file_sha256(path)
        dataset = replay_export(path, source, receipt_sha256)
        if case == "all-seven":
            check_adapter_refusals(dataset)
        summary["positive"][case] = {
            **check_fields(case, dataset),
            "receipt_sha256": receipt_sha256,
            "dataset_sha256": write_json(output / f"{case}.json", dataset),
            "comparator_sha256": write_json(output / f"{case}-comparator.json", comparator_observation(dataset)),
        }
    for case, verdict in {"pair-clear": ("values", "DISAGREE"),
                          "pair-input-drift-clear": ("typed_inputs", "DISAGREE"),
                          "pair-repack": ("tree", "DISAGREE"),
                          "bad-resource-vptr": ("values", "INCOMPLETE"),
                          "blank-mixed": ("tree", "INCOMPLETE"),
                          "cancel-second": ("tree", "INCOMPLETE"),
                          "entry-limit": ("tree", "INCOMPLETE"),
                          "missing-steam-witness": ("tree", "INCOMPLETE")}.items():
        path = receipts / f"{case}.jsonl"
        dataset = replay_export(path, source, file_sha256(path))
        assert dataset["acquisition"] == "ACQUISITION_INDETERMINATE" and not dataset["rows"]
        assert dataset["pair"][verdict[0]] == verdict[1]
        observation = comparator_observation(dataset)
        assert not observation["rows"]
        if case == "pair-clear":
            assert observation["structure"] == "QUALIFIED"
            assert len(dataset["unqualified_collections"]) == 2
            assert any(lane["runtime_form_id"] for row in dataset["unqualified_collections"][0] for lane in row["slots"])
            assert all(not lane["runtime_form_id"]
                       for row in dataset["unqualified_collections"][1] for lane in row["slots"])
        if case == "bad-resource-vptr":
            assert any(row["native_refusal"] == "resource_form_vptr_mismatch"
                       for row in dataset["unqualified_collections"][0])
            assert dataset["collection_counts"][0]["targets_refused"] == 1
        if case == "blank-mixed":
            assert dataset["collection_counts"][0]["mixed_refused"] == 1
            assert dataset["collection_counts"][0]["targets_refused"] == 0
        if case == "cancel-second":
            assert len(dataset["unqualified_collections"]) == 1
            assert len(dataset["unqualified_collections"][0]) == 4
        summary["negative"][case] = write_json(output / f"{case}.json", dataset)
    path = receipts / "all-seven.jsonl"
    missing_source = output / "missing-source"
    missing_source.mkdir()
    no_resource = SourceIndex(*fixture_sources(missing_source / "fixture.esm", exclude=0x400001))
    refusal = replay_export(path, no_resource, file_sha256(path))
    assert refusal["acquisition"] == "ACQUISITION_INDETERMINATE" and refusal["structure"] == "QUALIFIED"
    assert any({"field": "slots[1]", "code": "missing_typed_source_record"} in row["source_issues"]
               for row in refusal["unqualified_collections"][0])
    assert any(row["slots"][1]["runtime_form_id"] == 0x400001
               for row in refusal["unqualified_collections"][0])
    summary["negative"]["source-missing"] = write_json(output / "source-missing.json", refusal)
    try:
        replay_export(path, source, "0" * 64)
    except ValueError as error:
        assert "custody SHA-256" in str(error)
    else:
        raise AssertionError("wrong independent receipt hash admitted")
    if admitted is not None:
        summary["owned_admission"] = {}
        for case in ("direct", "corpus", "upper"):
            path = admitted / case / "title.jsonl"
            receipt_sha256 = file_sha256(path)
            dataset = replay_export(path, source, receipt_sha256)
            summary["owned_admission"][case] = {
                **check_fields(case, dataset, expected_namespace=True),
                "receipt_sha256": receipt_sha256,
                "dataset_sha256": write_json(output / f"owned-{case}.json", dataset),
                "comparator_sha256": write_json(output / f"owned-{case}-comparator.json",
                                                comparator_observation(dataset)),
            }
        wrong_manifest, wrong_namespace = deepcopy((manifest, namespace))
        wrong_manifest["files"][0]["plugin"] = "wrong.esm"
        wrong_namespace["plugins"][0]["plugin"] = "wrong.esm"
        path = admitted / "direct" / "title.jsonl"
        mismatched = replay_export(path, SourceIndex(wrong_manifest, wrong_namespace), file_sha256(path))
        assert mismatched["acquisition"] == "ACQUISITION_INDETERMINATE"
        assert mismatched["namespace_matches_source"] == [False, False]
        assert len(mismatched["unqualified_collections"][0]) == 4
        assert all(row["source_issues"] and row["pndt"]["source"] is None
                   for row in mismatched["unqualified_collections"][0])
        summary["negative"]["namespace-source-mismatch"] = write_json(
            output / "namespace-source-mismatch.json", mismatched)
        for case, verdict in (("namespace-drift", "DISAGREE"), ("namespace-invalid", "INCOMPLETE")):
            path = admitted / case / "title.jsonl"
            dataset = replay_export(path, source, file_sha256(path))
            assert dataset["structure"] == "QUALIFIED"
            assert dataset["acquisition"] == "ACQUISITION_INDETERMINATE"
            assert dataset["pair"]["source_identity"] == verdict
            assert dataset["pair"]["values"] == "AGREE"
            assert not dataset["rows"]
            assert [len(rows) for rows in dataset["unqualified_collections"]] == [4, 4]
            summary["negative"][case] = write_json(output / f"{case}.json", dataset)
    write_json(output / "summary.json", summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("owned_receipts", type=Path)
    parser.add_argument("new_output_dir", type=Path)
    parser.add_argument("--owned-admission", type=Path)
    args = parser.parse_args()
    print(census.encode(run(args.owned_receipts, args.new_output_dir, args.owned_admission)).decode("ascii"))


if __name__ == "__main__":
    main()
