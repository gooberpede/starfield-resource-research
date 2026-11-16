"""Capture and replay bounded acquisition using the same native decoder."""

from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
from time import monotonic_ns, sleep, time_ns

from contract import CHECKPOINTS, DISPOSABLE_INPUTS, MODES, SAMPLES, STRICT_MODE, STRUCTURAL_MODE, classify
from memory import ReadFailure
from native import NativeFailure, collect

SCHEMA = "srr013-disposable-observation-v1"
BOUND_SCHEMA = "srr013-epoch-bound-observation-v2"
MODE_SCHEMA = "srr013-mode-bound-observation-v3"
MAX_EVENTS = 8192
MAX_BYTES = 2 * 1024 * 1024
WINDOW_NS = 5_000_000_000
GAP_SEC = 0.025
LIMITS = {"events": MAX_EVENTS, "requested_bytes": MAX_BYTES,
          "window_ns": WINDOW_NS, "gap_ns": int(GAP_SEC * 1e9), "pairs": 1}


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("ascii")


class Journal:
    """Append complete events and their terminal hash to a new local receipt."""

    def __init__(self, stream):
        self.stream = stream
        self.digest = sha256()

    def write(self, event):
        line = encode(event) + b"\n"
        self.stream.write(line)
        self.stream.flush()
        self.digest.update(line)

    def seal(self):
        self.write({"kind": "seal", "sha256": self.digest.hexdigest()})
        os.fsync(self.stream.fileno())


class RecordingReader:
    def __init__(self, reader, journal, deadline, after_read):
        self.reader = reader
        self.journal = journal
        self.deadline = deadline
        self.after_read = after_read
        self.calls = self.bytes = 0

    def _record(self, kind, args, operation):
        self.calls += 1
        event = {"kind": kind, "args": args}
        try:
            if monotonic_ns() > self.deadline or self.calls > MAX_EVENTS or self.bytes > MAX_BYTES:
                raise ReadFailure("observation_budget", "disposable checkpoint budget exhausted")
            value = operation(*args)
            if kind == "read" and self.after_read is not None:
                self.after_read(*args)
            if monotonic_ns() > self.deadline:
                raise ReadFailure("observation_budget", "operation finished after checkpoint deadline")
            event["value"] = value.hex() if kind == "read" else value
        except ReadFailure as error:
            event["failure"] = [error.code, error.detail]
            raise
        finally:
            self.journal.write(event)
        return value

    def read(self, address, size, alignment=1):
        self.bytes += size
        return self._record("read", [address, size, alignment], self.reader.read)

    def identity(self, mode=None):
        args = [] if mode is None else [mode]
        return self._record("identity", args, lambda *_: self.reader.identity())


class ReplayReader:
    def __init__(self, events):
        self.events = iter(events)
        self.calls = self.bytes = 0

    def _take(self, kind, args):
        event = next(self.events, None)
        if event is None or (event.get("kind"), event.get("args")) != (kind, args):
            raise ValueError(f"receipt diverged at acquisition event {self.calls + 1}")
        self.calls += 1
        if "failure" in event:
            raise ReadFailure(*event["failure"])
        return event["value"]

    def read(self, address, size, alignment=1):
        self.bytes += size
        data = bytes.fromhex(self._take("read", [address, size, alignment]))
        if len(data) != size:
            raise ValueError("receipt contains a truncated successful read")
        return data

    def identity(self, mode=None):
        return self._take("identity", [] if mode is None else [mode])


def _pair(reader, base, inputs, between, binding=None, mode=None):
    collections = []
    brackets = []
    failure = None
    detail = None
    try:
        for ordinal in range(2):
            beginning = reader.identity(mode)
            if binding is not None:
                from checkpoint import validate_identity

                validate_identity(binding, beginning)
            data = collect(reader, base, SAMPLES, mode=mode or STRICT_MODE)
            collections.append(data)
            end = reader.identity(mode)
            brackets.append([beginning, end])
            if beginning != end or beginning != brackets[0][0]:
                raise ReadFailure("process_identity_changed", "process or mapped image drifted")
            if ordinal == 0:
                between()
    except (NativeFailure, ReadFailure) as error:
        failure, detail = error.code, error.detail
    return _report(collections, brackets, inputs, failure, detail, reader.calls, reader.bytes, mode)


def _report(collections, brackets, inputs, failure, detail, calls, byte_count, mode=None):
    if failure is None and len(collections) == 2 and collections[0] != collections[1]:
        failure = "inconsistent_pair"
    results = classify(collections, inputs, failure, mode=mode or STRICT_MODE)
    report = {
        "failure": failure, "detail": detail, "samples": results,
        "collections": collections, "identity_brackets": brackets,
        "read_and_identity_calls": calls, "requested_bytes": byte_count,
        "counts": {outcome: sum(row["outcome"] == outcome for row in results)
                   for outcome in sorted({row["outcome"] for row in results})},
    }
    if mode is not None:
        report["mode"] = mode
    return report


def _input_decision(binding, evidence):
    from retail_inputs import verify_inputs

    return verify_inputs(binding["target_kind"], evidence)


def _declare_mode(header, binding, mode):
    if mode is None:
        return
    if binding is None or mode not in MODES:
        raise ValueError("an explicit mode requires an epoch-bound observation")
    header.update(schema=MODE_SCHEMA, mode=mode)


def _attach_input_result(report, decision, mode):
    if decision is not None:
        report["input_admission"] = decision.as_dict()
        if mode == STRUCTURAL_MODE:
            report["input_admission"]["required_for_mode"] = False


def _refusal(kind, error, mode):
    event = {"kind": kind, "failure": [error.code, error.detail]}
    if mode is not None:
        event["mode"] = mode
    return event


def capture(path, reader, checkpoint, inputs=DISPOSABLE_INPUTS, *, between=None, after_read=None, binding=None,
            mode=None):
    if checkpoint not in CHECKPOINTS:
        raise ValueError("unknown operator-supplied checkpoint label")
    start = monotonic_ns()
    started_utc = time_ns()
    decision = None if binding is None else _input_decision(binding, inputs)
    with Path(path).open("xb") as stream:
        journal = Journal(stream)
        header = {"kind": "start", "schema": SCHEMA, "checkpoint": checkpoint,
                  "label_source": "disposable operator metadata", "base": reader.base,
                  "inputs": inputs, "limits": LIMITS, "start_ns": start,
                  "utc": datetime.now(timezone.utc).isoformat()}
        if binding is not None:
            header.update(schema=BOUND_SCHEMA, binding=binding, start_utc_ns=started_utc,
                          label_source="operator responsiveness declaration")
        _declare_mode(header, binding, mode)
        journal.write(header)

        def gap():
            if between is not None:
                between()
            sleep(GAP_SEC)

        try:
            if binding is not None:
                from checkpoint import validate_marker

                validate_marker(binding, checkpoint, start, started_utc, mode)
            bounded = RecordingReader(reader, journal, start + WINDOW_NS, after_read)
            report = _pair(bounded, reader.base, inputs if decision is None else decision.profile, gap, binding, mode)
        except ReadFailure as error:
            journal.write(_refusal("marker_refused", error, mode))
            report = _report([], [], None, error.code, error.detail, 0, 0, mode)
        _attach_input_result(report, decision, mode)
        journal.write({"kind": "report", "data": report, "end_ns": monotonic_ns()})
        journal.seal()
    return report


def capture_refusal(path, checkpoint, error, *, binding=None, inputs=None, mode=None):
    if checkpoint not in CHECKPOINTS:
        raise ValueError("unknown operator-supplied checkpoint label")
    start = monotonic_ns()
    report = _report([], [], None, error.code, error.detail, 0, 0, mode)
    header = {"kind": "start", "schema": SCHEMA, "checkpoint": checkpoint,
              "label_source": "disposable operator metadata", "base": None,
              "inputs": None, "limits": LIMITS, "start_ns": start,
              "utc": datetime.now(timezone.utc).isoformat()}
    if binding is not None:
        header.update(schema=BOUND_SCHEMA, binding=binding, inputs=inputs, start_utc_ns=time_ns(),
                      label_source="operator responsiveness declaration")
        _attach_input_result(report, _input_decision(binding, inputs), mode)
    _declare_mode(header, binding, mode)
    with Path(path).open("xb") as stream:
        journal = Journal(stream)
        journal.write(header)
        journal.write(_refusal("admission_refused", error, mode))
        journal.write({"kind": "report", "data": report, "end_ns": monotonic_ns()})
        journal.seal()
    return report


def replay(path, *, expected_mode=None):
    with Path(path).open("rb") as stream:
        lines = stream.read(8 * MAX_BYTES + 1).splitlines(keepends=True)
    if not 3 <= len(lines) <= MAX_EVENTS + 8 or sum(map(len, lines)) > 8 * MAX_BYTES:
        raise ValueError("receipt exceeds size bounds or is incomplete")
    actual = json.loads(lines[-1])
    if actual != {"kind": "seal", "sha256": sha256(b"".join(lines[:-1])).hexdigest()}:
        raise ValueError("receipt seal missing or invalid")
    header = json.loads(lines[0])
    trailer = json.loads(lines[-2])
    if header.get("schema") not in (SCHEMA, BOUND_SCHEMA, MODE_SCHEMA) or (header.get("kind"), trailer.get("kind")) != ("start", "report"):
        raise ValueError("unrecognized receipt schema")
    if header["limits"] != LIMITS or header["checkpoint"] not in CHECKPOINTS:
        raise ValueError("unrecognized receipt configuration")
    if trailer["end_ns"] < header["start_ns"]:
        raise ValueError("receipt has a reversed acquisition interval")
    mode = header.get("mode")
    if (header["schema"] == MODE_SCHEMA and mode not in MODES) or (header["schema"] != MODE_SCHEMA and "mode" in header):
        raise ValueError("invalid observation mode declaration")
    if expected_mode is not None and expected_mode != (mode or STRICT_MODE):
        raise ValueError("receipt mode differs from expected mode")
    binding = header["binding"] if header["schema"] != SCHEMA else None
    decision = None if binding is None else _input_decision(binding, header["inputs"])
    if header["base"] is None:
        refusal = json.loads(lines[1])
        if (len(lines) != 4 or refusal.get("kind") != "admission_refused" or refusal.get("mode") != mode
                or (binding is None and header["inputs"] is not None)):
            raise ValueError("invalid refusal receipt")
        code, detail = refusal["failure"]
        reproduced = _report([], [], None, code, detail, 0, 0, mode)
    elif binding is not None and (refusal := json.loads(lines[1])).get("kind") == "marker_refused":
        if len(lines) != 4 or refusal.get("mode") != mode:
            raise ValueError("marker refusal includes acquisition events")
        from checkpoint import validate_marker

        code, detail = refusal["failure"]
        if code not in ("marker_duplicate", "marker_token"):
            try:
                validate_marker(binding, header["checkpoint"], header["start_ns"], header["start_utc_ns"], mode)
            except ReadFailure as error:
                if (code, detail) != (error.code, error.detail):
                    raise ValueError("marker refusal reason differs") from error
            else:
                raise ValueError("receipt refused a valid marker")
        reproduced = _report([], [], None, code, detail, 0, 0, mode)
    else:
        if binding is not None:
            from checkpoint import validate_marker

            validate_marker(binding, header["checkpoint"], header["start_ns"], header["start_utc_ns"], mode)
        reader = ReplayReader(map(json.loads, lines[1:-2]))
        profile = header["inputs"] if decision is None else decision.profile
        reproduced = _pair(reader, header["base"], profile, lambda: None, binding, mode)
        if next(reader.events, None) is not None:
            raise ValueError("receipt contains extra acquisition events")
    _attach_input_result(reproduced, decision, mode)
    if encode(reproduced) != encode(trailer["data"]):
        raise ValueError("receipt result differs from native-traversal replay")
    return reproduced
