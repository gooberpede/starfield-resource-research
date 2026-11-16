"""Orchestrate one bound read window after profile-specific admission."""

from contextlib import ExitStack
from time import monotonic_ns, time_ns

from checkpoint import claim, validate_marker
from contract import MODES, STRUCTURAL_MODE
from memory import ReadFailure
from observe import capture, capture_refusal
from retail_inputs import verify_inputs


def observe_window(path, attempt_directory, admission, binding, evidence,
                   *, between=None, after_read=None, mode=None):
    """Acquire one owned disposable window through the selected contract."""
    label = binding["marker"]["label"]
    if binding["target_kind"] != "simulated":
        decision = verify_inputs(binding["target_kind"], evidence)
        failure = (ReadFailure("retail_authorization_required", "use the separately authorized title-only entry point")
                   if mode == STRUCTURAL_MODE else
                   ReadFailure(decision.reason or "retail_runtime_gate_unqualified", decision.detail))
        return capture_refusal(path, label, failure, binding=binding, inputs=evidence, mode=mode)
    with ExitStack() as stack:
        def authenticate():
            return stack.enter_context(admission)

        return _observe(path, attempt_directory, authenticate, binding, evidence, mode, between, after_read)


def _observe(path, attempt_directory, authenticate, binding, evidence, mode, between=None, after_read=None):
    if mode is not None and mode not in MODES:
        raise ValueError("unknown observation mode")
    label = binding["marker"]["label"]
    try:
        claim(attempt_directory, binding["attempt"])
        validate_marker(binding, label, monotonic_ns(), time_ns(), mode)
        reader = authenticate()
    except ReadFailure as error:
        return capture_refusal(path, label, error, binding=binding, inputs=evidence, mode=mode)
    binding = {**binding, "steam_log": {name: raw.hex() for name, raw in reader.admission_log.items()}}
    return capture(path, reader, label, evidence, binding=binding, between=between, after_read=after_read, mode=mode)
