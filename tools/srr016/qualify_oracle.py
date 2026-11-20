"""Independent controlled inputs and reference decisions for SRR-016 comparison."""

from copy import deepcopy
from contextlib import redirect_stdout
from decimal import Decimal
from io import StringIO
import json
import os
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase, main
from unittest.mock import patch

from .compare import compare, main as compare_main
from .ledger import (
    AUTHORED, FREEZE, LEDGER, OBSERVATION, ORACLE, REPRODUCER_COMMIT, RETAIL_SHA256,
    base_id, digest, resolve_authority,
)
from .oracle import choose, descendant_flags, freeze, native_weight, slot_special


INPUT = "a" * 64
REMAP = "b" * 64
FIXED_WORDS = {
    (0x3F59F, 0xD9BAC): (0x57EA, 0, 0, 0x57E9, 0, 0, 0x83EC),
    (0x3F59F, 0x23C0CE): (0x57C7, 0x57C9, 0, 0, 0, 0, 0),
    (0x3F59F, 0x2C9985): (0x57C1, 0x57C3, 0, 0, 0, 0, 0),
    (0x5DF7F, 0xC5717): (0x57EB, 0x57EC, 0, 0, 0x5DF8, 0x57F5, 0),
}


def ids(words):
    return [base_id(word) if word else None for word in words]


def observed_row(owner, biome, slots):
    return {
        "key": ids((owner, biome)),
        "raw_key": [(owner << 32) | 0x10009, biome],
        "typed": "VERIFIED",
        "slots": ids(slots),
        "raw_slots": list(slots),
    }


def observation(rows):
    return {
        "schema": OBSERVATION, "structure": "QUALIFIED", "acquisition": "QUALIFIED",
        "retail_sha256": RETAIL_SHA256, "input_sha256": INPUT, "remap_sha256": REMAP,
        "source": "OWNED_DISPOSABLE", "mixed": len(rows) + 2, "rows": rows,
    }


def sealed_fixture(ledger, predictions, *, applicability="QUALIFIED"):
    oracle = {
        "schema": ORACLE, "reproducer_commit": REPRODUCER_COMMIT, "retail_sha256": RETAIL_SHA256,
        "input_sha256": INPUT, "remap_sha256": REMAP, "ledger_sha256": digest(ledger),
        "rows": [{"key": ids(key), "slots": ids(words), "applicability": applicability}
                 for key, words in sorted(predictions.items())],
    }
    receipt = {
        "schema": FREEZE, "oracle_sha256": digest(oracle),
        "ledger_sha256": digest(ledger), "reproducer_commit": REPRODUCER_COMMIT,
    }
    return oracle, receipt


def scope(owner, status):
    return {
        "owner": base_id(owner), "status": status, "workset_closed": status != "UNKNOWN",
        "source": "Independent synthetic source", "reason": "Declared work set",
    }


def ledger_row(key, status):
    return {"key": ids(key), "status": status, "source": "Authored fixture", "reason": "Fixture path"}


class ComparisonFixtures(TestCase):
    def setUp(self):
        self.reference = {(1, 3): (10, 0, 0, 0, 0, 0, 20), (2, 3): (0,) * 7}
        self.observation = observation([
            observed_row(1, 3, (10, 0, 0, 0, 0, 0, 20)),
            observed_row(2, 3, (0,) * 7),
        ])
        self.ledger = {
            "schema": LEDGER, "scope": "COMPLETE", "retail_sha256": RETAIL_SHA256,
            "input_sha256": INPUT, "remap_sha256": REMAP, "owners": [scope(i, "EXPECTED") for i in (1, 2)],
            "rows": [ledger_row(key, "EXPECTED") for key in self.reference],
        }
        self.oracle, self.receipt = sealed_fixture(self.ledger, self.reference)

    def test_exact_mixed_fixture_with_shared_biom_and_zero_tuple(self):
        report = self.run_compare()
        self.assertEqual(report["combined"], "FIXTURE_COMPLETE_MATCH")
        self.assertEqual(report["counts"]["observed_mixed"], 4)
        self.assertEqual(report["counts"]["all_zero"], 1)
        self.assertNotIn("observed_slots", report["rows"][0])
        self.assertEqual(report["rows"][1]["observed_slots"], "OBSERVED_ALL_ZERO")
        self.assertEqual(report["counts"]["strict_comparable"], 0)

    def test_cli_preserves_structure_when_oracle_document_cannot_be_read(self):
        documents = [self.observation, self.ledger, json.JSONDecodeError("truncated", "[", 1), self.receipt]
        command = ["compare", "observation.json", "ledger.json", "oracle.json", "receipt.json",
                   "--receipt-sha256", digest(self.receipt)]
        with (patch("sys.argv", command), patch("tools.srr016.compare.read_json", side_effect=documents),
              redirect_stdout(StringIO()) as stdout):
            compare_main()
        report = json.loads(stdout.getvalue())
        self.assertEqual(report["structure"], "QUALIFIED")
        self.assertEqual(report["population"], "MATCH")
        self.assertEqual(report["values"], "INDETERMINATE")
        self.assertIn({
            "axis": "values", "status": "INPUT_PROVENANCE_MISMATCH",
            "reason": "DOCUMENT_READ_FAILED", "document": "oracle", "error_type": "JSONDecodeError",
        }, report["issues"])

    def test_one_and_many_field_slot_mismatches(self):
        self.observation["rows"] = [
            observed_row(1, 3, (11, 0, 0, 0, 0, 0, 20)),
            observed_row(2, 3, (0, 12, 0, 0, 0, 13, 0)),
        ]
        report = self.run_compare()
        self.assertEqual(report["counts"]["mismatched"], 2)
        self.assertEqual([len(row["differences"]) for row in report["rows"]], [1, 2])
        self.assertEqual([item["offset"] for item in report["rows"][1]["differences"]], [0x54, 0x64])

    def test_raw_and_normalized_lane_reorder(self):
        self.observation["rows"][0] = observed_row(1, 3, (20, 0, 0, 0, 0, 0, 10))
        report = self.run_compare()
        self.assertEqual(report["rows"][0]["values"], "SLOT_MISMATCH")
        self.assertEqual([item["offset"] for item in report["rows"][0]["differences"]], [0x50, 0x68])

    def test_duplicate_keys_fail_before_membership(self):
        self.observation["rows"].append(deepcopy(self.observation["rows"][0]))
        report = self.run_compare()
        self.assertEqual(report["issues"][0]["status"], "DUPLICATE_IDENTITY")
        self.assertEqual(report["structure"], "ACQUISITION_INDETERMINATE")
        self.assertFalse(report["rows"])

    def test_raw_key_namespace_and_discriminators_are_checked(self):
        for low in (1, 0x1FFFF, 0x10008):
            self.observation["rows"][1]["raw_key"][0] = (2 << 32) | low
            self.assertEqual(self.run_compare()["issues"][0]["reason"],
                             "INVALID_OR_CONFLICTING_DISCRIMINATOR")

    def test_conflicting_resource_mapping_refused_in_both_directions(self):
        self.observation["rows"][1] = observed_row(2, 3, (10, 0, 0, 0, 0, 0, 0))
        for raw, canonical in ((10, base_id(20)), (20, base_id(10))):
            self.observation["rows"][1]["raw_slots"][0] = raw
            self.observation["rows"][1]["slots"][0] = canonical
            self.assertEqual(self.run_compare()["issues"][0]["reason"], "CONTRADICTORY_FORMID_REMAP")

    def test_input_and_remap_axes(self):
        self.observation["input_sha256"] = None
        report = self.run_compare()
        self.assertEqual(report["structure"], "QUALIFIED")
        self.assertEqual(report["rows"][0]["values"], "RETAIL_APPLICABILITY_UNRESOLVED")
        for bad_input in ("0" * 64, "invalid"):
            self.observation["input_sha256"] = bad_input
            report = self.run_compare()
            self.assertEqual(report["structure"], "QUALIFIED")
            self.assertEqual(report["rows"][0]["values"], "INPUT_PROVENANCE_MISMATCH")
        self.observation["input_sha256"] = INPUT
        self.observation["remap_sha256"] = "0" * 64
        row = self.run_compare()["rows"][0]
        self.assertEqual((row["membership"], row["values"]),
                         ("INPUT_PROVENANCE_MISMATCH", "INPUT_PROVENANCE_MISMATCH"))

    def test_conflicting_expected_runtime_key_withholds_population_closure(self):
        self.ledger["rows"][0]["witness"] = {"runtime_owner": 101, "runtime_biom": 3}
        self.oracle, self.receipt = sealed_fixture(self.ledger, self.reference)
        report = self.run_compare()
        self.assertEqual((report["structure"], report["population"]), ("QUALIFIED", "INDETERMINATE"))
        self.assertEqual(report["rows"][0]["membership_reason"], "OWNER_RUNTIME_KEY_MAP_DRIFT")
        self.assertEqual(report["rows"][0]["values"], "INPUT_PROVENANCE_MISMATCH")
        self.assertEqual(report["rows"][1]["values"], "MATCH")

    def test_complete_ledger_without_bound_remap_withholds_population_match(self):
        self.ledger.pop("remap_sha256")
        self.oracle, self.receipt = sealed_fixture(self.ledger, self.reference)
        report = self.run_compare()
        self.assertEqual((report["structure"], report["population"]), ("QUALIFIED", "INDETERMINATE"))
        self.assertEqual(report["combined"], "PARTIAL_MATCH")

    def test_never_fit_predictions_to_observations(self):
        genuine = digest(self.receipt)
        self.oracle["rows"][0]["slots"][0] = base_id(11)
        self.observation["rows"][0]["raw_slots"][0] = 11
        self.observation["rows"][0]["slots"][0] = base_id(11)
        report = self.run_compare(genuine)
        self.assertEqual(report["population"], "MATCH")
        self.assertEqual(report["issues"][0]["reason"], "FROZEN_ORACLE_DRIFT")
        self.receipt["oracle_sha256"] = digest(self.oracle)
        report = self.run_compare(genuine)
        self.assertEqual(report["issues"][0]["reason"], "FROZEN_RECEIPT_DIGEST_DRIFT")
        self.assertEqual(report["counts"]["comparable"], 0)

    def test_oracle_schema_and_version_drift_preserve_structure_population(self):
        for field in ("schema", "reproducer_commit"):
            original = self.oracle[field]
            self.oracle[field] = "stale"
            report = self.run_compare()
            self.assertEqual((report["structure"], report["population"]), ("QUALIFIED", "MATCH"))
            self.assertEqual(report["counts"]["comparable"], 0)
            self.oracle[field] = original

    def test_missing_extra_unknown_excluded_and_zero_overlap(self):
        self.ledger["scope"] = "CONDITIONAL"
        self.ledger["owners"].extend([scope(4, "UNKNOWN"), scope(5, "EXCLUDED")])
        self.ledger["rows"].extend([ledger_row((4, 3), "UNKNOWN"), ledger_row((5, 3), "EXCLUDED")])
        self.oracle, self.receipt = sealed_fixture(self.ledger, self.reference)
        self.observation["rows"] = [observed_row(owner, 3, (0,) * 7) for owner in (4, 5, 6)]
        report = self.run_compare()
        self.assertEqual(report["population"], "SCOPED_DIFFERENCES")
        self.assertEqual(report["combined"], "INDETERMINATE")
        self.assertEqual([row["membership"] for row in report["rows"]],
                         ["MISSING_EXPECTED", "MISSING_EXPECTED", "UNKNOWN", "UNEXPECTED_OBSERVED", "UNKNOWN"])
        self.assertEqual(report["counts"]["comparable"], 0)
        self.assertEqual(report["counts"]["all_zero"], 3)

    def test_missing_sibling_invalidates_values_for_whole_owner(self):
        self.ledger["rows"].append(ledger_row((1, 4), "EXPECTED"))
        self.reference[1, 4] = (0,) * 7
        self.oracle, self.receipt = sealed_fixture(self.ledger, self.reference)
        report = self.run_compare()
        self.assertEqual(report["rows"][0]["value_reason"], "INCOMPLETE_OR_UNQUALIFIED_OWNER_WORKSET")
        self.assertEqual(report["rows"][1]["membership"], "MISSING_EXPECTED")
        self.assertEqual(report["rows"][2]["values"], "MATCH")

    def test_missing_oracle_sibling_invalidates_values_even_when_observed(self):
        self.ledger["rows"].append(ledger_row((1, 4), "EXPECTED"))
        self.observation["rows"].append(observed_row(1, 4, (0,) * 7))
        self.oracle, self.receipt = sealed_fixture(self.ledger, self.reference)
        report = self.run_compare()
        self.assertEqual(report["population"], "MATCH")
        self.assertEqual(report["rows"][0]["value_reason"], "INCOMPLETE_OR_UNQUALIFIED_OWNER_WORKSET")
        self.assertEqual(report["counts"]["comparable"], 1)

    def test_pair_structure_survives_normalization_refusal(self):
        self.observation["acquisition"] = "ACQUISITION_INDETERMINATE"
        self.observation["rows"] = []
        report = self.run_compare()
        self.assertEqual(report["structure"], "QUALIFIED")
        self.assertEqual(report["acquisition"], "ACQUISITION_INDETERMINATE")
        self.assertEqual(report["counts"]["observed_mixed"], 4)
        self.assertFalse(report["rows"])
        self.observation["structure"] = "ACQUISITION_INDETERMINATE"
        self.assertEqual(self.run_compare()["structure"], "ACQUISITION_INDETERMINATE")

    def test_structurally_empty_does_not_vacuously_match(self):
        self.ledger["owners"] = self.ledger["rows"] = []
        self.oracle, self.receipt = sealed_fixture(self.ledger, {})
        self.observation["rows"] = []
        self.observation["mixed"] = 0
        report = self.run_compare()
        self.assertEqual((report["structure"], report["combined"]), ("QUALIFIED", "INDETERMINATE"))

    def test_conditional_owner_matches_remain_scoped(self):
        self.ledger["scope"] = "CONDITIONAL"
        self.oracle, self.receipt = sealed_fixture(self.ledger, self.reference, applicability="CONDITIONAL")
        report = self.run_compare()
        self.assertEqual((report["combined"], report["values"]), ("PARTIAL_MATCH", "SCOPED_MATCH"))
        self.assertEqual(report["counts"]["conditional_comparable"], 2)

    def run_compare(self, frozen_digest=None):
        return compare(self.observation, self.ledger, self.oracle, self.receipt,
                       receipt_sha256=frozen_digest or digest(self.receipt))


class AuthorAndProjectionFixtures(TestCase):
    def authored_profile(self):
        def operation(route, target=None, index=None, admitted=True):
            result = {
                "route": route, "admitted": admitted, "winning_plugin": "patch.esm",
                "winner_sha256": INPUT,
            }
            if target is not None:
                result["runtime_biom"] = target
            if index is not None:
                result["authored_index"] = index
            return result

        return {
            "schema": AUTHORED, "source": "Ordered independent winner fixture", "source_sha256": INPUT,
            "forms": [
                [0x01000001, base_id(1), "PNDT"], [3, base_id(3), "BIOM"], [4, base_id(4), "BIOM"],
                [0xFE000801, "patch.esl:000801", "BIOM"],
            ],
            "owners": [{
                "runtime": 0x01000001, "workset_closed": True, "scope": "Ordered winning operation stream",
                "operations": [
                    operation("PPBD", target=3, index=0), operation("PPBD", target=4, index=1),
                    operation("ENAM_CLEAR"), operation("ENAM_PPBD", target=4, index=0),
                    operation("CSV", target=0xFE000801),
                ],
            }],
        }

    def test_authored_remap_and_ordered_enam_replacement_then_csv(self):
        profile = self.authored_profile()
        owners, rows = resolve_authority(profile)
        self.assertTrue(owners[base_id(1)]["workset_closed"])
        self.assertEqual(rows[base_id(1), base_id(3)]["status"], "EXCLUDED")
        self.assertEqual(rows[base_id(1), base_id(4)]["status"], "EXPECTED")
        csv = rows[base_id(1), "patch.esl:000801"]
        self.assertEqual(csv["witness"]["runtime_owner"], 0x01000001)
        self.assertEqual(csv["witness"]["runtime_biom"], 0xFE000801)
        self.assertEqual(csv["witness"]["winning_plugin"], "patch.esm")

    def test_unresolved_csv_guard_invalidates_owner_scope(self):
        profile = self.authored_profile()
        profile["owners"][0]["operations"][-1]["admitted"] = None
        owners, rows = resolve_authority(profile)
        self.assertFalse(owners[base_id(1)]["workset_closed"])
        self.assertEqual({item["status"] for item in rows.values()}, {"UNKNOWN"})

    def test_duplicate_admission_and_contradictory_maps_refused(self):
        profile = self.authored_profile()
        operations = profile["owners"][0]["operations"]
        operations.append(operations[-1])
        with self.assertRaisesRegex(ValueError, "AMBIGUOUS_DUPLICATE_SUBMISSION"):
            resolve_authority(profile)
        operations.pop()
        profile["forms"].append([5, base_id(3), "BIOM"])
        with self.assertRaisesRegex(ValueError, "CONTRADICTORY_FORMID_REMAP"):
            resolve_authority(profile)

    def test_source_rejects_observation_fields(self):
        profile = self.authored_profile()
        profile["owners"][0]["operations"][0]["raw_slots"] = [0] * 7
        with self.assertRaisesRegex(ValueError, "OBSERVATION_FIELDS_IN_AUTHORED_PROFILE"):
            resolve_authority(profile)

    def test_special_at_count_eight_even_if_occurrence_can_be_accepted(self):
        ref = SimpleNamespace(form_id=SimpleNamespace(numeric=41))
        entry = SimpleNamespace(resource=ref, resource_form_id=ref.form_id)
        for occupied in (list(range(1, 9)), list(range(1, 8)) + [41]):
            modeled_acceptance = 41 in occupied or len(occupied) < 8
            self.assertEqual(modeled_acceptance, 41 in occupied)
            self.assertEqual(slot_special(entry, len(occupied)), 0)
        self.assertEqual(slot_special(entry, 7), 41)
        self.assertEqual(slot_special(None, 7), 0)

    def test_same_roll_biom_retry_carries_cumulative(self):
        rarity = SimpleNamespace(value="Special")
        primary = SimpleNamespace(entries=(SimpleNamespace(
            special_chance=Decimal("20"), resource_rarity=rarity),))
        biom = SimpleNamespace(entries=(SimpleNamespace(
            special_chance=Decimal("40"), resource_rarity=rarity),))
        self.assertIs(choose((primary, biom), "Special", 0.5, native=True)[0], biom)
        self.assertEqual(choose((biom,), "Special", 0.5, native=True), (None, None))

    def test_binary32_weight_boundary_refuses_apparent_selector_parity(self):
        chance = Decimal("10")
        roll = native_weight(chance)
        definition = SimpleNamespace(entries=(SimpleNamespace(
            special_chance=chance, resource_rarity=SimpleNamespace(value="Special")),))
        self.assertIsNone(choose((definition,), "Special", roll, native=True)[1])
        self.assertNotEqual(choose((definition,), "Special", roll, native=False),
                            choose((definition,), "Special", roll, native=True))

    def test_descendant_duplicate_across_distinct_root_and_current(self):
        uncommon = SimpleNamespace(value="Uncommon")
        rare = SimpleNamespace(value="Rare")
        child = SimpleNamespace(form_id=2, rarity=uncommon)
        shared = SimpleNamespace(form_id=3, rarity=rare)
        root = SimpleNamespace(form_id=1)
        family = SimpleNamespace(root=root, origin=SimpleNamespace(biome_index=0), levels=(
            SimpleNamespace(rarity=uncommon, inclusion_roll=0.4, inclusion_threshold=1.0,
                            candidates=(child,), selected_candidate=child),
            SimpleNamespace(rarity=rare, inclusion_roll=0.4, inclusion_threshold=0.5,
                            candidates=(shared,), selected_candidate=shared),
            *(SimpleNamespace(rarity=SimpleNamespace(value=name), inclusion_roll=None,
                              candidates=(), selected_candidate=None) for name in ("Exotic", "Unique")),
        ))
        nodes = {1: SimpleNamespace(children=(child, shared)), 2: SimpleNamespace(children=(shared,)),
                 3: SimpleNamespace(children=())}
        entry = SimpleNamespace(resource_form_id=1, uncommon_chance=Decimal("100"), rare_chance=Decimal("50"))
        flags = descendant_flags(SimpleNamespace(family_results=(family,)), nodes, {0: entry})
        self.assertEqual(flags, {"DESCENDANT_CANDIDATE_SEQUENCE_OR_MULTIPLICITY"})


class PinnedControlFixtures(TestCase):
    @classmethod
    def setUpClass(cls):
        checkout = os.environ.get("SRR016_REPRODUCER")
        if not checkout:
            raise ValueError("Set SRR016_REPRODUCER to the separately obtained pinned checkout")
        cls.ledger, cls.oracle, cls.receipt = freeze(Path(checkout))

    def test_all_four_slots_against_independent_offline_words(self):
        expected = {tuple(ids(key)): ids(words) for key, words in FIXED_WORDS.items()}
        self.assertEqual({tuple(row["key"]): row["slots"] for row in self.oracle["rows"]}, expected)
        self.assertTrue(all(row["applicability"] == "CONDITIONAL" for row in self.oracle["rows"]))
        data = observation([observed_row(*key, slots) for key, slots in FIXED_WORDS.items()])
        data["input_sha256"] = self.ledger["input_sha256"]
        report = compare(data, self.ledger, self.oracle, self.receipt, receipt_sha256=digest(self.receipt))
        self.assertEqual(report["combined"], "PARTIAL_MATCH")
        self.assertEqual(report["counts"]["conditional_comparable"], 4)
        self.assertEqual(report["counts"]["unknown"], 3206)

    def test_all_three_full_count_special_negatives(self):
        cases = self.receipt["special_at_eight"]
        self.assertEqual([item["extract_key"] for item in cases], [
            ["0005E0BE", "000C5717"], ["0005E45F", "001862BD"], ["0005E591", "000C5716"],
        ])
        self.assertEqual([(item["word"], item["count_before"], item["native_slot"]) for item in cases],
                         [(0x57F5, 8, 0)] * 3)


if __name__ == "__main__":
    main()
