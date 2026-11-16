"""Pinned sample identities and separate exact-tuple and structural verdicts."""

from dataclasses import asdict, dataclass

POPULATED = "POPULATED_RESULT_OBSERVED"
UNPOPULATED = "QUALIFIED_UNPOPULATED"
INDETERMINATE = "STATE_INDETERMINATE"
STRUCTURALLY_POPULATED = "STRUCTURALLY_POPULATED"
STRUCTURALLY_ZERO = "STRUCTURALLY_ZERO"
STRICT_MODE = "strict"
STRUCTURAL_MODE = "structural"
MODES = (STRICT_MODE, STRUCTURAL_MODE)
EMPTY = (0,) * 7
CHECKPOINTS = ("title", "menu", "settled-gameplay")
SLOT_ROLES = ("Common", "Uncommon", "Rare", "Exotic", "Unique", "Special", "Everywhere")
RETAIL_APPLICABILITY = {
    "version": "1.16.244.0",
    "sha256": "7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28",
}


@dataclass(frozen=True)
class SampleRequest:
    pndt: int
    biom: int
    seed: int
    override: int
    biom_rsgd: int
    editor_id: str
    expected: tuple[int, ...]
    control: int


SAMPLES = (
    SampleRequest(0x3F59F, 0xD9BAC, 2842708811, 0, 0x83F0, "FrozenLifeKreet",
                  (0x57EA, 0, 0, 0x57E9, 0, 0, 0x83EC), 3),
    SampleRequest(0x3F59F, 0x23C0CE, 2842708811, 0x244CCB, 0x7EDD, "MountainsLifeKreet",
                  (0x57C7, 0x57C9, 0, 0, 0, 0, 0), 3),
    SampleRequest(0x3F59F, 0x2C9985, 2842708811, 0x244CCC, 0x83EA, "VolcanicRoughLifeKreet",
                  (0x57C1, 0x57C3, 0, 0, 0, 0, 0), 3),
    SampleRequest(0x5DF7F, 0xC5717, 1633829920, 0x18CE00, 0x83E0, "CrateredNoLife11",
                  (0x57EB, 0x57EC, 0, 0, 0x5DF8, 0x57F5, 0), 0),
)

# These pins identify the disposable controlled profile and its prediction source.
# Admission of this profile supplies no effective-input attestation in retail.
DISPOSABLE_INPUTS = {
    "id": "srr013-controlled-disposable-v1",
    "sample_plan": "SRR-012-sample-plan",
    "key_origin": "base-game FormIDs represented in a synthetic graph",
    "runtime_load_order": "disposable fixture with no plugin loader",
}


def _precheck(sample, observed, input_profile):
    if observed["reason"]:
        return observed["reason"]
    if input_profile != DISPOSABLE_INPUTS:
        return "effective_inputs_unverified"
    words = observed["words"]
    if words is None or len(words) != len(EMPTY) or any(
        type(word) is not int or not 0 <= word <= 0xFFFFFFFF for word in words
    ):
        return "output_invalid"
    if tuple(words) not in (sample.expected, EMPTY):
        return "unexpected_output"
    return None


def _structural_check(observed):
    if observed["reason"]:
        return observed["reason"]
    words = observed["words"]
    if words is None or len(words) != len(EMPTY) or any(
        type(word) is not int or not 0 <= word <= 0xFFFFFFFF for word in words
    ):
        return "output_invalid"
    witnesses = observed.get("resource_forms")
    if witnesses is None or [(form["slot"], form["form_id"]) for form in witnesses] != [
        (slot, word) for slot, word in enumerate(words) if word
    ]:
        return "resource_witness_incomplete"
    return None


def classify(collections, input_profile, window_failure=None, *, mode=STRICT_MODE):
    """Interpret complete native collections, requiring the declared control per sample."""
    first, second = (collections + [None, None])[:2]
    paired = window_failure is None and first is not None and first == second
    failure = window_failure or (None if paired else "inconsistent_pair")
    first_rows = first["samples"] if first is not None else [{} for _ in SAMPLES]
    second_rows = second["samples"] if second is not None else [{} for _ in SAMPLES]
    if mode not in MODES:
        raise ValueError("unknown observation mode")
    structural = mode == STRUCTURAL_MODE
    checks = [] if failure else [
        _structural_check(row) if structural else _precheck(sample, row, input_profile)
        for sample, row in zip(SAMPLES, first_rows, strict=True)
    ]
    results = []
    for index, (sample, row, repeat) in enumerate(zip(SAMPLES, first_rows, second_rows, strict=True)):
        reason = failure or checks[index]
        control_reason = checks[sample.control] if checks else None
        if reason is None and control_reason is not None:
            reason = "comparison_control_failed"
        words = row.get("words")
        if reason is not None:
            outcome = INDETERMINATE
        elif tuple(words) == EMPTY:
            outcome, reason = ((STRUCTURALLY_ZERO, "validated_zero_fields") if structural
                               else (UNPOPULATED, "validated_all_zero"))
        else:
            outcome, reason = ((STRUCTURALLY_POPULATED, "validated_nonzero_resource_ids") if structural
                               else (POPULATED, "tuple_match"))
        result = {
            "sample": asdict(sample), "outcome": outcome, "reason": reason,
            "comparison_control_reason": control_reason,
            "prediction_comparison": "applicable" if not structural and paired and not row.get("reason")
            and input_profile == DISPOSABLE_INPUTS else "conditional",
            "observed_words": words, "repeat_words": repeat.get("words"),
            "slot_roles": SLOT_ROLES,
        }
        if structural:
            result["resource_forms"] = row.get("resource_forms")
            result["repeat_resource_forms"] = repeat.get("resource_forms")
        results.append(result)
    return results
