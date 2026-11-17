"""Compare comparable native slots and membership against independently frozen inputs."""

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

from .ledger import (
    FREEZE, LEDGER, OBSERVATION, ORACLE, REPRODUCER_COMMIT, RETAIL_SHA256, IdentityMap,
    digest, identity, require, u32, valid_digest,
)


ACQUISITION_INDETERMINATE = "ACQUISITION_INDETERMINATE"
PROVENANCE_MISMATCH = "INPUT_PROVENANCE_MISMATCH"
APPLICABILITY_UNRESOLVED = "RETAIL_APPLICABILITY_UNRESOLVED"
NO_PREDICTION = "NO_APPLICABLE_PREDICTION"
MEMBERSHIP = {"EXPECTED", "EXCLUDED", "UNKNOWN"}


def read_json(path):
    def unique_object(items):
        result = {}
        for key, value in items:
            require(key not in result, f"DUPLICATE_JSON_MEMBER: {key}")
            result[key] = value
        return result

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)


def index_rows(rows):
    indexed = {}
    require(isinstance(rows, list), "INVALID_ROWS")
    for row in rows:
        require(isinstance(row["key"], list) and len(row["key"]) == 2, "INVALID_KEY_WIDTH")
        key = tuple(identity(value) for value in row["key"])
        require(key not in indexed, "DUPLICATE_IDENTITY")
        indexed[key] = row
    return indexed


def slot_ids(slots):
    require(isinstance(slots, list) and len(slots) == 7, "INVALID_SLOT_LANES")
    return [identity(slot) if slot is not None else None for slot in slots]


def observed_header(observation):
    require(observation["schema"] == OBSERVATION, "OBSERVATION_SCHEMA_DRIFT")
    require(observation["acquisition"] in {"QUALIFIED", ACQUISITION_INDETERMINATE},
            "INVALID_ACQUISITION_VERDICT")
    structure = observation.get("structure", observation["acquisition"])
    require(structure in {"QUALIFIED", ACQUISITION_INDETERMINATE}, "INVALID_STRUCTURE_VERDICT")
    mixed = observation["mixed"]
    require(structure != "QUALIFIED" or (type(mixed) is int and mixed >= 0),
            "INVALID_MIXED_DENOMINATOR")
    return structure


def observed_rows(observation):
    rows = index_rows(observation["rows"])
    mixed = observation["mixed"]
    require(type(mixed) is int and mixed >= len(rows), "INVALID_MIXED_DENOMINATOR")
    ids = IdentityMap()
    raw_keys = set()
    discriminator = None
    for (owner, biome), row in rows.items():
        require(row["typed"] == "VERIFIED", "UNRESOLVED_TYPED_WITNESS")
        first, second = raw_key = tuple(row["raw_key"])
        require(type(first) is int and 0 <= first <= 0xFFFFFFFFFFFFFFFF, "INVALID_RAW_KEY_WORD")
        low = first & 0xFFFFFFFF
        require(0x10000 <= low < 0x1FFFF and discriminator in {None, low},
                "INVALID_OR_CONFLICTING_DISCRIMINATOR")
        discriminator = low
        require(raw_key not in raw_keys, "DUPLICATE_IDENTITY")
        raw_keys.add(raw_key)
        ids.bind(first >> 32, owner, "PNDT")
        ids.bind(u32(second), biome, "BIOM")
        for word, slot in zip(row["raw_slots"], slot_ids(row["slots"]), strict=True):
            require((u32(word) == 0) == (slot is None), "RAW_SLOT_NULL_MISMATCH")
            if word:
                ids.bind(word, slot, "IRES")
    return rows


def input_decision(observed, ledger):
    if observed.get("retail_sha256") != ledger["retail_sha256"]:
        return PROVENANCE_MISMATCH
    if (observed.get("source") == "RETAIL_ATTESTED" and
            observed.get("target_image_sha256") != ledger["retail_sha256"]):
        return PROVENANCE_MISMATCH
    observed_input = observed.get("input_sha256")
    if observed_input is None or ledger["input_sha256"] is None:
        return APPLICABILITY_UNRESOLVED
    if ledger.get("remap_sha256") is not None:
        if not valid_digest(observed.get("remap_sha256")):
            return APPLICABILITY_UNRESOLVED
        if observed["remap_sha256"] != ledger["remap_sha256"]:
            return PROVENANCE_MISMATCH
    return ("BOUND" if observed_input == ledger["input_sha256"]
            else PROVENANCE_MISMATCH)


def ledger_rows(ledger, receipt):
    require(ledger["schema"] == LEDGER, "LEDGER_SCHEMA_DRIFT")
    require(ledger["scope"] in {"CONDITIONAL", "COMPLETE"}, "INVALID_LEDGER_SCOPE")
    require(ledger["retail_sha256"] == RETAIL_SHA256, "LEDGER_EXECUTABLE_DRIFT")
    require(ledger["input_sha256"] is None or valid_digest(ledger["input_sha256"]),
            "INVALID_LEDGER_INPUT_DIGEST")
    require(ledger.get("remap_sha256") is None or valid_digest(ledger["remap_sha256"]),
            "INVALID_LEDGER_REMAP_DIGEST")
    require(receipt["schema"] == FREEZE and receipt["reproducer_commit"] == REPRODUCER_COMMIT and
            receipt["ledger_sha256"] == digest(ledger), "FROZEN_LEDGER_DRIFT")
    rows = index_rows(ledger["rows"])
    owners = {}
    for item in ledger["owners"]:
        owner = identity(item["owner"])
        require(owner not in owners, "DUPLICATE_IDENTITY")
        require(item["status"] in MEMBERSHIP and type(item["workset_closed"]) is bool and
                item["source"] and item["reason"], "INVALID_OWNER_SCOPE")
        require(item["workset_closed"] == (item["status"] != "UNKNOWN"), "AMBIGUOUS_OWNER_SCOPE")
        owners[owner] = item
    expected_owners = set()
    runtime_witnesses = IdentityMap()
    for key, row in rows.items():
        require(row["status"] in MEMBERSHIP and row["source"] and row["reason"],
                "INVALID_LEDGER_ROW")
        require(key[0] in owners, "MISSING_OWNER_SCOPE")
        if row["status"] == "EXPECTED":
            require(owners[key[0]]["status"] == "EXPECTED", "EXPECTED_WITHOUT_CLOSED_OWNER")
            expected_owners.add(key[0])
        if row["status"] == "UNKNOWN":
            require(not owners[key[0]]["workset_closed"], "UNKNOWN_KEY_INSIDE_CLOSED_OWNER")
        if "witness" in row:
            witness = row["witness"]
            runtime_witnesses.bind(witness["runtime_owner"], key[0], "PNDT")
            runtime_witnesses.bind(witness["runtime_biom"], key[1], "BIOM")
    require(expected_owners == {owner for owner, item in owners.items() if item["status"] == "EXPECTED"},
            "EXPECTED_OWNER_WITHOUT_EXPECTED_KEY")
    unresolved = ledger.get("unresolved_candidates", [])
    unresolved_owners = ledger.get("unresolved_owners", [])
    require(all(row["status"] == "UNKNOWN" for row in [*unresolved, *unresolved_owners]),
            "UNRESOLVED_RECORD_ADMISSION")
    require(ledger["scope"] != "COMPLETE" or
            (not unresolved and not unresolved_owners and
             all(scope["workset_closed"] for scope in owners.values())), "UNKNOWN_COMPLETE_LEDGER")
    return rows, owners


def oracle_rows(oracle, receipt, ledger, expected):
    require(oracle["schema"] == ORACLE, "ORACLE_SCHEMA_DRIFT")
    require(oracle["reproducer_commit"] == REPRODUCER_COMMIT, "REPRODUCER_COMMIT_DRIFT")
    require(oracle["ledger_sha256"] == receipt["ledger_sha256"] and
            receipt["oracle_sha256"] == digest(oracle), "FROZEN_ORACLE_DRIFT")
    require(oracle["retail_sha256"] == ledger["retail_sha256"] and
            oracle["input_sha256"] == ledger["input_sha256"], "ORACLE_PROVENANCE_DRIFT")
    rows = index_rows(oracle["rows"])
    for key, row in rows.items():
        require(key in expected, "ORACLE_WITHOUT_EXPECTED_KEY")
        require(row["applicability"] in {"QUALIFIED", "CONDITIONAL"}, "INVALID_ORACLE_APPLICABILITY")
        slot_ids(row["slots"])
    return rows


def group_owners(keys):
    grouped = defaultdict(set)
    for key in keys:
        grouped[key[0]].add(key)
    return grouped


def compare(observation, ledger, oracle, receipt, *, receipt_sha256):
    report = {
        "schema": "srr016-comparison-v1",
        "structure": ACQUISITION_INDETERMINATE,
        "acquisition": ACQUISITION_INDETERMINATE,
        "population": "INDETERMINATE",
        "values": "INDETERMINATE",
        "combined": "INDETERMINATE",
        "issues": [],
        "counts": {
            "observed_mixed": None, "admitted_targets": None,
            "expected": None, "excluded": None, "unknown": None, "unknown_owners": None,
            "missing": None, "unexpected": None, "all_zero": None, "comparable": 0,
            "matched": 0, "mismatched": 0, "qualified_projection_comparable": 0,
            "strict_comparable": 0, "conditional_comparable": 0,
        },
        "rows": [],
    }

    def issue(axis, error, fallback):
        reason = str(error)
        report["issues"].append({
            "axis": axis,
            "status": "DUPLICATE_IDENTITY" if reason == "DUPLICATE_IDENTITY" else fallback,
            "reason": reason,
        })

    bad_input = (KeyError, TypeError, ValueError, AttributeError, OverflowError)
    try:
        structure = observed_header(observation)
        if observation["acquisition"] == ACQUISITION_INDETERMINATE:
            report["structure"] = structure
            report["counts"]["observed_mixed"] = observation["mixed"] if structure == "QUALIFIED" else None
            issue("acquisition", "NORMALIZED_ACQUISITION_NOT_QUALIFIED", ACQUISITION_INDETERMINATE)
            return report
        require(structure == "QUALIFIED", "ACQUISITION_REQUIRES_QUALIFIED_STRUCTURE")
        observed = observed_rows(observation)
    except bad_input as error:
        issue("structure", error, ACQUISITION_INDETERMINATE)
        return report
    report["structure"] = "QUALIFIED"
    report["acquisition"] = "QUALIFIED"
    source = observation.get("source")
    report["source"] = source
    report["counts"].update(observed_mixed=observation["mixed"], admitted_targets=len(observed))

    try:
        require(valid_digest(receipt_sha256) and receipt_sha256 == digest(receipt),
                "FROZEN_RECEIPT_DIGEST_DRIFT")
        submitted, owners = ledger_rows(ledger, receipt)
    except bad_input as error:
        issue("population", error, PROVENANCE_MISMATCH)
        submitted, owners = {}, {}
        input_status = PROVENANCE_MISMATCH
    else:
        input_status = input_decision(observation, ledger)
        report["ledger_scope"] = ledger["scope"]
        statuses = Counter(row["status"] for row in submitted.values())
        report["counts"].update(
            expected=statuses["EXPECTED"], excluded=statuses["EXCLUDED"],
            unknown=statuses["UNKNOWN"] + len(ledger.get("unresolved_candidates", [])),
            unknown_owners=sum(not item["workset_closed"] for item in owners.values()) +
            len(ledger.get("unresolved_owners", [])),
        )
    report["input"] = input_status
    expected = {key for key, row in submitted.items() if row["status"] == "EXPECTED"}
    try:
        predicted = oracle_rows(oracle, receipt, ledger, expected)
    except bad_input as error:
        issue("values", error, PROVENANCE_MISMATCH)
        predicted = {}

    exp_owners = group_owners(expected)
    obs_owners = group_owners(observed)
    pred_owners = group_owners(predicted)
    unresolved_owners = {key[0] for key, row in submitted.items() if row["status"] == "UNKNOWN"}
    discordant_owners = set()
    for key in submitted.keys() & observed.keys():
        witness = submitted[key].get("witness")
        if witness is not None:
            k0, k1 = observed[key]["raw_key"]
            if (k0 >> 32, k1) != (witness["runtime_owner"], witness["runtime_biom"]):
                discordant_owners.add(key[0])
    owner_flags = {}
    for owner, predicted_keys in pred_owners.items():
        if owner in discordant_owners:
            owner_flags[owner] = (PROVENANCE_MISMATCH, "OWNER_RUNTIME_KEY_MAP_DRIFT")
            continue
        if (owner in unresolved_owners or exp_owners[owner] != predicted_keys or
                exp_owners[owner] != obs_owners[owner] or
                len({predicted[key]["applicability"] for key in predicted_keys}) != 1):
            owner_flags[owner] = (APPLICABILITY_UNRESOLVED, "INCOMPLETE_OR_UNQUALIFIED_OWNER_WORKSET")
            continue
        if any(predicted[key]["applicability"] == "QUALIFIED" for key in predicted_keys):
            remap = observation.get("remap_sha256")
            if not valid_digest(remap) or not valid_digest(oracle.get("remap_sha256")):
                owner_flags[owner] = (APPLICABILITY_UNRESOLVED, "REMAP_ATTESTATION_MISSING")
            elif remap != oracle["remap_sha256"]:
                owner_flags[owner] = (PROVENANCE_MISMATCH, "REMAP_DIGEST_DRIFT")
    counts = Counter()
    for key in sorted(submitted.keys() | observed.keys()):
        owner = key[0]
        actual = observed.get(key)
        wanted = submitted.get(key)
        scope = owners.get(owner)
        eligibility = wanted["status"] if wanted else "UNKNOWN"
        row = {"key": list(key), "eligibility": eligibility}
        if actual is not None and all(slot is None for slot in actual["slots"]):
            row["observed_slots"] = "OBSERVED_ALL_ZERO"
            counts["all_zero"] += 1

        if input_status != "BOUND":
            row["membership"] = input_status
        elif owner in discordant_owners:
            row["membership"] = PROVENANCE_MISMATCH
            row["membership_reason"] = "OWNER_RUNTIME_KEY_MAP_DRIFT"
        elif eligibility == "EXPECTED":
            row["membership"] = "EXPECTED_OBSERVED" if actual is not None else "MISSING_EXPECTED"
        elif actual is not None and (
            eligibility == "EXCLUDED" or (wanted is None and scope and scope["workset_closed"]) or
            (wanted is None and ledger["scope"] == "COMPLETE")
        ):
            row["membership"] = "UNEXPECTED_OBSERVED"
        else:
            row["membership"] = "EXCLUDED_ABSENT" if eligibility == "EXCLUDED" else "UNKNOWN"
        counts[row["membership"]] += 1

        if actual is not None:
            row["values"] = NO_PREDICTION
            if key in predicted:
                if input_status != "BOUND":
                    row["values"] = input_status
                elif owner in owner_flags:
                    row["values"], row["value_reason"] = owner_flags[owner]
                else:
                    prediction = predicted[key]
                    row["applicability"] = prediction["applicability"]
                    counts[prediction["applicability"]] += 1
                    differences = []
                    for lane, (wanted_slot, observed_slot) in enumerate(zip(
                        prediction["slots"], actual["slots"], strict=True
                    )):
                        if wanted_slot != observed_slot:
                            differences.append({
                                "offset": 0x50 + lane * 4,
                                "expected": wanted_slot,
                                "observed": observed_slot,
                            })
                    row["values"] = "SLOT_MISMATCH" if differences else "MATCH"
                    if differences:
                        row["differences"] = differences
            counts[row["values"]] += 1
        report["rows"].append(row)

    matches, mismatches = counts["MATCH"], counts["SLOT_MISMATCH"]
    comparable = matches + mismatches
    report["counts"].update(
        missing=counts["MISSING_EXPECTED"] if input_status == "BOUND" else None,
        unexpected=counts["UNEXPECTED_OBSERVED"] if input_status == "BOUND" else None,
        all_zero=counts["all_zero"], comparable=comparable, matched=matches,
        mismatched=mismatches, qualified_projection_comparable=counts["QUALIFIED"],
        strict_comparable=counts["QUALIFIED"] if source == "RETAIL_ATTESTED" else 0,
        conditional_comparable=counts["CONDITIONAL"],
    )

    closed_population = (input_status == "BOUND" and ledger["scope"] == "COMPLETE" and
                         valid_digest(ledger.get("remap_sha256")) and not unresolved_owners and
                         not discordant_owners and bool(expected))
    if counts["MISSING_EXPECTED"] or counts["UNEXPECTED_OBSERVED"]:
        report["population"] = "DIFFERENCES" if closed_population else "SCOPED_DIFFERENCES"
    elif closed_population and set(observed) == expected:
        report["population"] = "MATCH"
    if comparable:
        all_expected = counts["QUALIFIED"] == len(expected)
        report["values"] = (("DIFFERENCES" if mismatches else "MATCH") if all_expected
                            else ("SCOPED_DIFFERENCES" if mismatches else "SCOPED_MATCH"))
    if (report["population"] == "MATCH" and bool(matches) and
            matches == len(expected) == counts["QUALIFIED"]):
        report["combined"] = {
            "RETAIL_ATTESTED": "COMPLETE_MATCH",
            "OWNED_DISPOSABLE": "FIXTURE_COMPLETE_MATCH",
        }.get(source, "PARTIAL_MATCH")
    elif matches:
        report["combined"] = "PARTIAL_MATCH"
    elif closed_population and (
        report["population"] == "DIFFERENCES" or comparable == len(expected)
    ):
        report["combined"] = "NO_MATCH"
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    axes = {"observation": "structure", "ledger": "population",
            "oracle": "values", "receipt": "population"}
    for field in axes:
        parser.add_argument(field, type=Path)
    parser.add_argument("--receipt-sha256", required=True,
                        help="Canonical hash independently retained at oracle freeze")
    files = parser.parse_args()
    documents = []
    read_issues = []
    for field, axis in axes.items():
        try:
            documents.append(read_json(getattr(files, field)))
        except (OSError, ValueError) as error:
            documents.append({})
            read_issues.append({
                "axis": axis,
                "status": ACQUISITION_INDETERMINATE if field == "observation" else PROVENANCE_MISMATCH,
                "reason": "DOCUMENT_READ_FAILED",
                "document": field,
                "error_type": type(error).__name__,
            })
    report = compare(*documents, receipt_sha256=files.receipt_sha256)
    report["issues"].extend(read_issues)
    print(json.dumps(report, ensure_ascii=True, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
