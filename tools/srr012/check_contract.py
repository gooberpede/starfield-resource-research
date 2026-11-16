"""Exercise SRR-012 decision gates with disposable, fabricated observations.

This fixture has no process, native traversal, Windows API or file access.
The integers are fabricated tokens and do not represent game FormIDs.
"""

from dataclasses import dataclass, replace
import unittest


POPULATED = "POPULATED_RESULT_OBSERVED"
UNPOPULATED = "QUALIFIED_UNPOPULATED"
INDETERMINATE = "STATE_INDETERMINATE"
EMPTY = (0,) * 7


@dataclass(frozen=True)
class Row:
    logical_key: tuple[int, int]
    eligible: bool
    slots: tuple[int, ...]


@dataclass(frozen=True)
class Collection:
    epoch: int
    context: int
    range_evidence: int
    targets: tuple[Row, ...]
    controls: tuple[Row, ...]
    admitted: bool = True
    complete: bool = True


def classify(first, second, target_key, control_key, expected, control_expected):
    """Model one decision after lower-level acquisition has produced its gates."""
    if not first.admitted or not second.admitted:
        return INDETERMINATE, "admission"
    if not first.complete or not second.complete:
        return INDETERMINATE, "traversal"
    if first != second:
        return INDETERMINATE, "inconsistent_pair"
    if len(first.controls) != 1:
        return INDETERMINATE, "control_count"
    control = first.controls[0]
    if control.logical_key != control_key or not control.eligible:
        return INDETERMINATE, "control_identity_or_eligibility"
    if control.slots not in (control_expected, EMPTY):
        return INDETERMINATE, "control_slots"
    if len(first.targets) != 1:
        return INDETERMINATE, "target_count"
    target = first.targets[0]
    if target.logical_key != target_key or not target.eligible:
        return INDETERMINATE, "target_identity_or_eligibility"
    if len(expected) != len(EMPTY) or expected == EMPTY:
        return INDETERMINATE, "target_reference_invalid"
    if target.slots == expected:
        return POPULATED, "tuple_match"
    if target.slots == EMPTY:
        return UNPOPULATED, "validated_all_zero"
    return INDETERMINATE, "target_slots"


class ContractTests(unittest.TestCase):
    target = Row((1, 2), True, (11, 0, 13, 0, 0, 0, 17))
    control = Row((3, 4), True, (21, 22, 0, 0, 0, 0, 0))
    good = Collection(1, 10, 100, (target,), (control,))

    def decide(self, first, second, expected=None):
        return classify(
            first, second, self.target.logical_key, self.control.logical_key,
            self.target.slots if expected is None else expected, self.control.slots,
        )

    def test_populated_with_optional_zeros(self):
        self.assertEqual(self.decide(self.good, self.good), (POPULATED, "tuple_match"))

    def test_eligible_zeros_including_control(self):
        zeros = replace(self.good, targets=(replace(self.target, slots=EMPTY),),
                        controls=(replace(self.control, slots=EMPTY),))
        self.assertEqual(self.decide(zeros, zeros), (UNPOPULATED, "validated_all_zero"))
        self.assertEqual(self.decide(zeros, zeros, EMPTY),
                         (INDETERMINATE, "target_reference_invalid"))

    def test_equal_incomplete_pairs_cannot_pass(self):
        for change, reason in (
            ({"admitted": False}, "admission"),
            ({"complete": False}, "traversal"),
            ({"targets": ()}, "target_count"),
            ({"targets": (self.target, self.target)}, "target_count"),
            ({"targets": (replace(self.target, eligible=False, slots=EMPTY),)},
             "target_identity_or_eligibility"),
            ({"targets": (replace(self.target, logical_key=(1, 4)),)},
             "target_identity_or_eligibility"),
            ({"targets": (replace(self.target, slots=(11, 0, 0, 0, 0, 0, 0)),)},
             "target_slots"),
            ({"targets": (replace(self.target, slots=(11, 0)),)}, "target_slots"),
            ({"controls": ()}, "control_count"),
            ({"controls": (self.target,)}, "control_identity_or_eligibility"),
            ({"controls": (replace(self.control, slots=self.target.slots),)}, "control_slots"),
        ):
            with self.subTest(reason=reason, change=change):
                changed = replace(self.good, **change)
                self.assertEqual(self.decide(changed, changed), (INDETERMINATE, reason))

    def test_unequal_pairs_cannot_pass(self):
        for change in (
            {"epoch": 2},
            {"context": 11},
            {"range_evidence": 101},
            {"targets": (replace(self.target, slots=EMPTY),)},
            {"controls": (replace(self.control, slots=EMPTY),)},
        ):
            with self.subTest(change=change):
                self.assertEqual(self.decide(self.good, replace(self.good, **change)),
                                 (INDETERMINATE, "inconsistent_pair"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
