"""Build the portable allocation dataset from checked private census replay."""

import argparse
from collections import Counter
from hashlib import file_digest, sha256
import json
from pathlib import Path
import re
import sys

from tools.srr016 import census, compare
from .source import SourceIdentityError, SourceIndex, load_json
from .work import OUTPUT_BYTES


SCHEMA = "srr017-allocations-v1"
SLOTS = ("Common", "Uncommon", "Rare", "Exotic", "Unique", "Special", "Everywhere")
OUTPUT_LIMIT = OUTPUT_BYTES
INDETERMINATE = "ACQUISITION_INDETERMINATE"
RAW_WORD = re.compile(r"[0-9A-F]{16}")


def file_sha256(path):
    with path.open("rb") as stream:
        return file_digest(stream, "sha256").hexdigest()


def export_source_sha256():
    root = Path(__file__).resolve().parents[1]
    sources = ("srr017/export.py", "srr017/source.py", "srr017/work.py", "srr016/compare.py", "srr016/ledger.py")
    return sha256(census.encode({name: file_sha256(root / name) for name in sources})).hexdigest()


def portable_row(descriptor, source, identities, vectors, *, retail_flow=False):
    raw_key = descriptor["raw_key"]
    verified = descriptor["classification"] == "TARGET"
    issues = []
    forms = descriptor.get("forms", {})
    resource_witnesses = {item["slot"]: item["form_id"] for item in descriptor.get("resources", [])}

    def form(word, signature, field, witnessed):
        result = {"runtime_form_id": word, "source": None,
                  "native_status": "VERIFIED" if witnessed else "ZERO" if word == 0 else "UNVERIFIED"}
        if not witnessed:
            return result
        if vectors is not None:
            vector_key = f"{word:08X}"
            if vector_key in vectors:
                result["native_source_plugins"] = vectors[vector_key]
            elif not retail_flow:
                issues.append({"field": field, "code": "native_source_vector_unwitnessed"})
        if source is None:
            issues.append({"field": field, "code": "namespace_source_mismatch"})
            return result
        try:
            resolved = source.resolve(word, signature)
            if retail_flow:
                source.validate_observed_sources(resolved, result.get("native_source_plugins"))
            canonical = resolved["comparator_id"]
            if (identities["canonical"].setdefault(canonical, word) != word
                    or identities["runtime"].setdefault(word, canonical) != canonical):
                raise SourceIdentityError("identity_collision", "conflicting source identity")
        except SourceIdentityError as error:
            issues.append({"field": field, "code": error.code})
        else:
            result["source"] = resolved
            if (not retail_flow and vectors is not None
                    and resolved["winning_plugin"] not in (result.get("native_source_plugins") or [])):
                issues.append({"field": field, "code": "owned_source_vector_disagreement"})
        return result

    slots = None
    if "raw_slots" in descriptor:
        slots = [
            {"ordinal": lane, "payload_offset": 0x50 + 4 * lane, "role": role,
             **form(word, "IRES", f"slots[{lane}]", bool(word and resource_witnesses.get(lane) == word))}
            for lane, (role, word) in enumerate(zip(SLOTS, descriptor["raw_slots"], strict=True))
        ]
    override = None
    if "override" in descriptor:
        override = form(descriptor["override"], "RSGD", "override_rsgd", bool(forms.get("override")))
        if forms.get("override_reason"):
            override["native_status"] = "RESOLVED_NULL"
            override["reason"] = forms["override_reason"]
    return {
        "raw_key": [f"{word:016X}" for word in raw_key],
        "state": "VERIFIED_PRESENT" if verified else "REFUSED",
        "native_refusal": descriptor.get("failure", [None])[0],
        "pndt": form(raw_key[0] >> 32, "PNDT", "pndt", bool(forms.get("pndt"))),
        "biom": form(raw_key[1] if raw_key[1] <= 0xFFFFFFFF else None, "BIOM", "biom", bool(forms.get("biom"))),
        "slots": slots,
        "pndt_seed": forms.get("pndt_seed"),
        "biome_seed": descriptor.get("seed"),
        "coverage_word": descriptor.get("coverage_word"),
        "biom_rsgds": [
            form(item["form_id"], "RSGD", f"biom_rsgds[{ordinal}]", True)
            for ordinal, item in enumerate(forms["biom_rsgds"])
        ] if "biom_rsgds" in forms else None,
        "override_rsgd": override,
        "source_issues": issues,
    }


def pair_verdict(collections, field):
    if len(collections) != 2 or not all(item["coverage_verified"] for item in collections):
        return "INCOMPLETE"
    first, second = (item[field] for item in collections)
    return "AGREE" if first == second else "DISAGREE"


def make_export(report, source, receipt_sha256, capture_reader_sha256, *, source_binding_failure=None):
    source_kind = report["observation"]["source"]
    retail_flow = report.get("title_flow") == census.RETAIL_NAMESPACE_PROFILE
    expected_authority = "RETAIL_NATIVE_WITNESS" if source_kind == "RETAIL_ATTESTED" else "OWNED_DISPOSABLE"
    if source is not None and source.provenance["authority"] != expected_authority:
        raise ValueError("source namespace authority differs from checked acquisition")
    if source is None and (not retail_flow or not source_binding_failure):
        raise ValueError("raw-only export requires a recorded source binding refusal")
    if source_binding_failure is not None and not re.fullmatch(r"[a-z0-9_]{1,128}", source_binding_failure):
        raise ValueError("source binding refusal must be a portable reason code")
    collections = report["collections"]
    structure = pair_verdict(collections, "tree_identity_sha256")
    typed = pair_verdict(collections, "typed_input_sha256")
    values = pair_verdict(collections, "raw_rows")
    witnesses = pair_verdict(collections, "witness_sha256")
    failure = report["failure"][0] if report["failure"] else None
    source_profile = any("source_witness" in item for item in collections)
    source_pair = pair_verdict(collections, "source_identity_sha256") if source_profile else "UNOBSERVED"
    if source_profile and any(not item.get("source_identity_sha256") for item in collections):
        source_pair = "INCOMPLETE"
    counts = []
    diagnostics = []
    namespaces = []
    namespace_matches = []
    namespace_refusals = []
    identities = {"canonical": {}, "runtime": {}}
    for item in collections:
        source_witness = item.get("source_witness")
        compiled = source_witness["namespace"]["compiled"] if source_witness else None
        vectors = source_witness["vectors"] if source_witness else None
        namespaces.append(compiled)
        namespace_match = None if compiled is None else (
            source is not None and
            {(entry["kind"], entry["index"]): entry["plugin"] for entry in compiled} == source.by_slot)
        namespace_matches.append(namespace_match)
        source_failure = item.get("source_failure")
        namespace_refusals.append(source_failure[0] if source_failure else None)
        row_source = source if not source_profile or namespace_match else None
        rows = [portable_row(entry, row_source, identities, vectors, retail_flow=retail_flow)
                for entry in item["descriptors"]
                if entry["classification"] != "MIXED_EXCLUSION"]
        verified = len(item["raw_rows"])
        target_refusals = item["attempted_targets"] - verified
        refusals = sum(row["state"] == "REFUSED" for row in rows)
        source_issue_counts = Counter(issue["code"] for row in rows for issue in row["source_issues"])
        counts.append({
            "coverage_verified": item["coverage_verified"],
            "mixed_declared": item["publication"]["count"] if item["publication"] else None,
            "mixed_visited": item["mixed_visited"],
            "mixed_excluded": item["mixed_excluded"],
            "targets_attempted": item["attempted_targets"],
            "targets_verified": verified,
            "targets_refused": target_refusals,
            "mixed_refused": refusals - target_refusals,
            "targets_with_source_issues": sum(bool(row["source_issues"]) for row in rows),
            "source_issue_counts": dict(source_issue_counts),
        })
        diagnostics.append(rows)
    candidate_rows = diagnostics[0] if diagnostics else []
    qualified = source is not None and source_binding_failure is None and failure is None and all(
        verdict == "AGREE" for verdict in (structure, typed, values, witnesses)) and all(
        not count["targets_with_source_issues"] and not count["targets_refused"] for count in counts)
    if source_profile:
        qualified = qualified and source_pair == "AGREE" and all(namespace_matches)
    if qualified:
        # The checked replay enforces unique raw keys. The bidirectional identity join
        # above rejects distinct runtime IDs that would introduce a canonical alias.
        candidate_rows.sort(key=lambda row: (
            row["pndt"]["source"]["comparator_id"], row["biom"]["source"]["comparator_id"]))
    result = {
        "schema": SCHEMA,
        "source": source_kind,
        "scope": "TITLE_CARD_REACHABLE_COMPONENT_DB_2_PLUS_0X300",
        "retail_layout_version": "1.16.244.0",
        "retail_sha256": census.RETAIL_SHA256,
        "target_image_sha256": report["observation"]["target_image_sha256"],
        "capture_reader_sha256": capture_reader_sha256,
        "replay_reader_sha256": census.source_identity(),
        "exporter_source_sha256": export_source_sha256(),
        "receipt_sha256": receipt_sha256,
        "source_provenance": source.provenance if source is not None else None,
        "remap_sha256": source.identity_sha256 if source is not None else None,
        "input_sha256": None,
        "structure": report["structure"],
        "pair": {"tree": structure, "typed_inputs": typed, "values": values,
                 "complete_form_witnesses": witnesses, "source_identity": source_pair},
        "native_namespaces": namespaces,
        "namespace_matches_source": namespace_matches,
        "namespace_refusals": namespace_refusals,
        "acquisition": "QUALIFIED" if qualified else INDETERMINATE,
        "failure": failure,
        "collection_counts": counts,
        "rows": candidate_rows if qualified else [],
        "unqualified_collections": [] if qualified else diagnostics,
    }
    if retail_flow:
        provenance = [item.get("source_witness", {}) for item in collections]
        digests = [item.get("provenance_sha256") for item in provenance]
        failures = [item.get("provenance_failure") for item in provenance]
        result["source_binding_failure"] = source_binding_failure
        result["native_source_attribution"] = {
            "agreement": ("INCOMPLETE" if len(digests) != 2 or not all(digests) or any(failures)
                          else "AGREE" if digests[0] == digests[1] else "DISAGREE"),
            "refusals": failures,
        }
    return result


def comparator_observation(dataset):
    if dataset.get("schema") != SCHEMA:
        raise ValueError("unsupported allocation dataset schema")
    observation = {field: dataset[field] for field in (
        "retail_sha256", "input_sha256", "target_image_sha256", "source", "remap_sha256",
        "structure", "acquisition")}
    counts = dataset["collection_counts"]
    rows = dataset["rows"]
    observation.update(
        schema=census.OBSERVATION_SCHEMA,
        mixed=counts[0]["mixed_visited"] if dataset["structure"] == "QUALIFIED" else None,
        rows=[],
    )
    if observation["acquisition"] == "QUALIFIED":
        required_pair = dict.fromkeys(("tree", "typed_inputs", "values", "complete_form_witnesses"), "AGREE")
        witnessed_namespace = any(item is not None for item in dataset["native_namespaces"])
        required_pair["source_identity"] = "AGREE" if witnessed_namespace else "UNOBSERVED"
        if (observation["structure"] != "QUALIFIED" or dataset["failure"] is not None
                or dataset.get("source_binding_failure") is not None
                or observation["source"] == "RETAIL_ATTESTED" and (
                    not witnessed_namespace or observation["target_image_sha256"] != census.RETAIL_SHA256
                    or dataset["source_provenance"]["authority"] != "RETAIL_NATIVE_WITNESS")
                or dataset["unqualified_collections"]
                or dataset["pair"] != required_pair
                or len(dataset["native_namespaces"]) != 2
                or dataset["namespace_refusals"] != [None, None]
                or dataset["namespace_matches_source"] != ([True, True] if witnessed_namespace else [None, None])
                or len(counts) != 2 or counts[0] != counts[1]
                or not counts[0]["coverage_verified"]
                or not counts[0]["mixed_declared"] == observation["mixed"] == counts[0]["mixed_excluded"] + len(rows)
                or not counts[0]["targets_verified"] == counts[0]["targets_attempted"] == len(rows)
                or any(counts[0][field] for field in (
                    "targets_refused", "mixed_refused", "targets_with_source_issues", "source_issue_counts"))):
            raise ValueError("qualified export coverage disagrees with its rows")
    for row in rows:
        slots = row["slots"]
        if (observation["acquisition"] != "QUALIFIED" or row["state"] != "VERIFIED_PRESENT"
                or row["source_issues"]
                or [(lane["ordinal"], lane["payload_offset"], lane["role"]) for lane in slots]
                != [(i, 0x50 + 4 * i, role) for i, role in enumerate(SLOTS)]):
            raise ValueError("unqualified row or incorrect lane ordering")
        raw_key = row["raw_key"]
        if not isinstance(raw_key, list) or len(raw_key) != 2 or not all(
                isinstance(value, str) and RAW_WORD.fullmatch(value) for value in raw_key):
            raise ValueError("invalid portable raw key words")
        first, second = (int(word, 16) for word in raw_key)
        for field, runtime, signature in (("pndt", first >> 32, "PNDT"), ("biom", second, "BIOM")):
            witness = row[field]
            if (witness["runtime_form_id"] != runtime or witness["native_status"] != "VERIFIED"
                    or witness["source"]["signature"] != signature):
                raise ValueError(f"inconsistent {field} identity witnesses")
        for lane in slots:
            if lane["runtime_form_id"]:
                if lane["native_status"] != "VERIFIED" or lane["source"]["signature"] != "IRES":
                    raise ValueError("inconsistent nonzero resource witness")
            elif lane["native_status"] != "ZERO" or lane["source"] is not None:
                raise ValueError("inconsistent zero resource witness")
        observation["rows"].append({
            "key": [row["pndt"]["source"]["comparator_id"], row["biom"]["source"]["comparator_id"]],
            "raw_key": [first, second],
            "typed": "VERIFIED",
            "raw_slots": [lane["runtime_form_id"] for lane in slots],
            "slots": [lane["source"]["comparator_id"] if lane["source"] else None for lane in slots],
        })
    compare.observed_header(observation)
    if observation["acquisition"] == "QUALIFIED":
        compare.observed_rows(observation)
    return observation


def replay_export(receipt, source, expected_receipt_sha256):
    if receipt.stat().st_size > census.RETAIL_LIMITS["journal_bytes"]:
        raise ValueError("receipt exceeds the acquisition journal ceiling")
    if file_sha256(receipt) != expected_receipt_sha256:
        raise ValueError("receipt differs from custody SHA-256")
    with receipt.open("rb") as stream:
        header = json.loads(stream.readline(OUTPUT_LIMIT))
    if "authority" in header["binding"]:
        from .title import replay_owned

        report = replay_owned(receipt)
    else:
        report = census.replay(receipt)
    if file_sha256(receipt) != expected_receipt_sha256:
        raise ValueError("receipt changed during replay")
    return make_export(report, source, expected_receipt_sha256, header["reader_source_sha256"])


def bound_dataset(report, receipt_sha256, reader_sha256):
    """Resolve defining identities from the checked paired native namespace."""
    from .source import bind_native_namespace

    if report.get("title_flow") != census.RETAIL_NAMESPACE_PROFILE:
        raise ValueError("unsupported evidence for a bound title export")
    failure = report.get("source_binding_failure")
    source = None
    if not failure and len(report["collections"]) == 2:
        try:
            witnesses = [item.get("source_witness", {}).get("namespace") for item in report["collections"]]
            if not all(witnesses):
                raise SourceIdentityError("loaded_namespace_incomplete", "paired namespace was not witnessed")
            kind = report["observation"]["source"]
            authority = "RETAIL_NATIVE_WITNESS" if kind == "RETAIL_ATTESTED" else "OWNED_DISPOSABLE"
            indices = [bind_native_namespace(witness, authority=authority) for witness in witnesses]
            if indices[0].identity_sha256 != indices[1].identity_sha256:
                raise SourceIdentityError("loaded_namespace_changed", "source file join differs across passes")
            source = indices[0]
        except SourceIdentityError as error:
            failure = error.code
    return make_export(report, source, receipt_sha256, reader_sha256,
                       source_binding_failure=failure or ("source_binding_incomplete" if source is None else None))


def replay_retail_export(receipt, expected_receipt_sha256, attempt_sha256):
    from .retail_title import replay_retail

    if receipt.stat().st_size > census.RETAIL_LIMITS["journal_bytes"]:
        raise ValueError("receipt exceeds the acquisition journal ceiling")
    if file_sha256(receipt) != expected_receipt_sha256:
        raise ValueError("receipt differs from custody SHA-256")
    header = next(census._load_receipt(receipt))
    report = replay_retail(receipt, attempt_sha256=attempt_sha256)
    if file_sha256(receipt) != expected_receipt_sha256:
        raise ValueError("receipt changed during replay")
    return bound_dataset(report, expected_receipt_sha256, header["reader_source_sha256"])


def output_bytes(document, *, ceiling=OUTPUT_LIMIT):
    payload = census.encode(document) + b"\n"
    if len(payload) > ceiling:
        raise ValueError("portable output exceeds declared ceiling")
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    parser.add_argument("manifest", type=Path, nargs="?")
    parser.add_argument("namespace", type=Path, nargs="?")
    parser.add_argument("--receipt-sha256", required=True)
    parser.add_argument("--identity-sha256")
    parser.add_argument("--attempt-sha256", help="independently retained retail attempt byte digest")
    parser.add_argument("--retail", action="store_true", help="replay the signed retail bundle in its private custody")
    parser.add_argument("--comparator", action="store_true")
    args = parser.parse_args()
    try:
        if args.retail:
            if any((args.manifest, args.namespace, args.identity_sha256)):
                raise ValueError("retail replay uses only the source documents retained in signed custody")
            if not args.attempt_sha256:
                raise ValueError("retail replay needs the independently retained attempt SHA-256")
            output = replay_retail_export(args.receipt, args.receipt_sha256, args.attempt_sha256)
        else:
            if args.attempt_sha256 or not all((args.manifest, args.namespace, args.identity_sha256)):
                raise ValueError("owned export requires source manifest, namespace and identity SHA-256")
            source = SourceIndex(load_json(args.manifest), load_json(args.namespace))
            if source.identity_sha256 != args.identity_sha256:
                raise ValueError("source manifest or namespace differs from reviewed SHA-256")
            output = replay_export(args.receipt, source, args.receipt_sha256)
        sys.stdout.buffer.write(output_bytes(comparator_observation(output) if args.comparator else output))
    except (OSError, RuntimeError, ValueError, TypeError, KeyError) as error:
        parser.exit(2, f"Export refused: {error}\n")
    return 0 if output["acquisition"] == "QUALIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
