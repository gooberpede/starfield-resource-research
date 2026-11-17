"""Capture and replay bounded acquisition using the same native decoder."""

from contextlib import contextmanager
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
from time import monotonic_ns, sleep, time_ns

from contract import CHECKPOINTS, DISPOSABLE_INPUTS, MODES, SAMPLES, STRICT_MODE, STRUCTURAL_MODE, classify
from memory import ReadFailure
from native import NativeFailure, collect, work_limits as native_work_limits

SCHEMA = "srr013-disposable-observation-v1"
BOUND_SCHEMA = "srr013-epoch-bound-observation-v2"
MODE_SCHEMA = "srr013-mode-bound-observation-v3"
WORK_SCHEMA = "srr013-work-bound-observation-v4"
LEGACY_SCHEMAS = (SCHEMA, BOUND_SCHEMA, MODE_SCHEMA)
MAX_EVENTS = 8192
MAX_BYTES = 2 * 1024 * 1024
GAP_SEC = 0.025
GAP_NS = 25_000_000
MAX_JOURNAL_BYTES = 8 * MAX_BYTES
# One final refused operation, four collection boundaries, and start/report/seal.
MAX_JOURNAL_LINES = MAX_EVENTS + 8
LEGACY_LIMITS = {"events": MAX_EVENTS, "requested_bytes": MAX_BYTES,
                 "window_ns": 5_000_000_000, "gap_ns": GAP_NS, "pairs": 1}


def work_limits():
    return {"events": MAX_EVENTS, "requested_bytes": MAX_BYTES,
            "gap_ns": GAP_NS, "pairs": 1, "native": native_work_limits()}


class AcquisitionStop(Exception):
    """End the only pair, bypassing native read refusals scoped to one range or row."""

    def __init__(self, code, detail):
        self.code, self.detail = code, detail
        super().__init__(f"{code}: {detail}")


class JournalFailure(OSError):
    """The attempt cannot publish a durable receipt. Keep the pending bytes."""

    def __init__(self, code, cause):
        self.code = code
        super().__init__(f"{code}: {cause}")


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("ascii")


class Journal:
    """Append complete events and their terminal hash to a new local receipt."""

    def __init__(self, stream):
        self.stream = stream
        self.digest = sha256()

    def write(self, event):
        line = encode(event) + b"\n"
        try:
            self.stream.write(line)
            self.stream.flush()
        except OSError as error:
            raise JournalFailure("journal_write", error) from error
        self.digest.update(line)

    def seal(self):
        self.write({"kind": "seal", "sha256": self.digest.hexdigest()})
        try:
            os.fsync(self.stream.fileno())
        except OSError as error:
            raise JournalFailure("journal_seal", error) from error


@contextmanager
def pending_journal(path):
    """Publish only after the seal is flushed and the pending file is closed."""
    path = Path(path)
    pending = path.with_name(path.name + ".partial")
    try:
        if path.exists():
            raise FileExistsError(path)
        stream = pending.open("xb")
    except OSError as error:
        raise JournalFailure("journal_open", error) from error
    try:
        journal = Journal(stream)
        yield journal
        journal.seal()
    finally:
        try:
            stream.close()
        except OSError as error:
            raise JournalFailure("journal_close", error) from error
    try:
        # Windows rename does not replace an existing path. On other hosts use
        # a no-replace hard link so offline qualification has the same rule.
        if os.name == "nt":
            pending.rename(path)
        else:
            path.hardlink_to(pending)
            pending.unlink()
    except OSError as error:
        raise JournalFailure("journal_publish", error) from error


def budget_fault(limits, calls, byte_count, size):
    if calls >= limits["events"]:
        return "acquisition operation limit exceeded"
    if byte_count + size > limits["requested_bytes"]:
        return "acquisition requested-byte limit exceeded"
    return None


def collection_event(kind, ordinal, instant):
    return {"kind": f"collection_{kind}", "ordinal": ordinal, "mono_ns": instant}


class RecordingReader:
    def __init__(self, reader, journal, limits, after_read, cancelled):
        self.reader = reader
        self.journal = journal
        self.limits = limits
        self.after_read = after_read
        self.cancelled = cancelled
        self.calls = self.bytes = 0
        self.timing = []

    def collection_boundary(self, kind, ordinal):
        instant = monotonic_ns()
        self.journal.write(collection_event(kind, ordinal, instant))
        self.timing.append(instant)

    def _check_cancelled(self):
        if self.cancelled is not None and self.cancelled():
            raise AcquisitionStop("operator_cancelled", "operator cancelled the observation")

    def _record(self, kind, args, operation):
        size = args[1] if kind == "read" else 0
        event = {"kind": kind, "args": args, "performed": False}
        try:
            self._check_cancelled()
            failure = budget_fault(self.limits, self.calls, self.bytes, size)
            if failure is not None:
                raise AcquisitionStop("observation_budget", failure)
            self.calls += 1
            self.bytes += size
            event["performed"] = True
            value = operation(*args)
            if kind == "read" and self.after_read is not None:
                self.after_read(*args)
            self._check_cancelled()
            event["value"] = value.hex() if kind == "read" else value
        except (AcquisitionStop, ReadFailure) as error:
            event["failure"] = [error.code, error.detail]
            raise
        finally:
            self.journal.write(event)
        return value

    def read(self, address, size, alignment=1):
        return self._record("read", [address, size, alignment], self.reader.read)

    def identity(self, mode=None):
        args = [] if mode is None else [mode]
        return self._record("identity", args, lambda *_: self.reader.identity())


class ReplayReader:
    def __init__(self, events, limits=None):
        self.events = iter(events)
        self.limits = limits
        self.historical = limits is None
        self.calls = self.bytes = 0
        self.timing = []

    def collection_boundary(self, kind, ordinal):
        if self.historical:
            return
        event = next(self.events, None)
        if (not isinstance(event, dict) or type(instant := event.get("mono_ns")) is not int
                or type(event.get("ordinal")) is not int
                or event != collection_event(kind, ordinal, instant)):
            raise ValueError("receipt collection boundaries differ from traversal")
        self.timing.append(instant)

    def _take(self, kind, args):
        event = next(self.events, None)
        if event is None or (event.get("kind"), event.get("args")) != (kind, args):
            raise ValueError(f"receipt diverged at acquisition event {self.calls + 1}")
        size = args[1] if kind == "read" else 0
        if self.historical:
            self.calls += 1
            self.bytes += size
            if "failure" in event:
                raise ReadFailure(*event["failure"])
            return event["value"]

        outcome = set(event) - {"kind", "args", "performed"}
        if (type(performed := event.get("performed")) is not bool or outcome not in ({"value"}, {"failure"})
                or encode(event["args"]) != encode(args)):
            raise ValueError("receipt operation has no unique execution state and result")
        refusal = event.get("failure")
        if "failure" in event and (not isinstance(refusal, list) or len(refusal) != 2
                                   or not all(isinstance(field, str) and field for field in refusal)):
            raise ValueError("receipt operation refusal is malformed")
        expected = budget_fault(self.limits, self.calls, self.bytes, size)
        if not performed:
            if refusal == ["operator_cancelled", "operator cancelled the observation"]:
                raise AcquisitionStop(*refusal)
            if expected is None or refusal != ["observation_budget", expected]:
                raise ValueError("receipt refusal contradicts the declared work limits")
            raise AcquisitionStop(*refusal)
        if expected is not None:
            raise ValueError("receipt dispatched work past the declared cap")
        self.calls += 1
        self.bytes += size
        if refusal == ["operator_cancelled", "operator cancelled the observation"]:
            raise AcquisitionStop(*refusal)
        if refusal is not None:
            if refusal[0] in ("observation_budget", "operator_cancelled"):
                raise ValueError("receipt operation refusal disagrees with its execution state")
            raise ReadFailure(*refusal)
        return event["value"]

    def read(self, address, size, alignment=1):
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
            reader.collection_boundary("start", ordinal)
            try:
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
            finally:
                reader.collection_boundary("end", ordinal)
            if ordinal == 0:
                between()
    except (NativeFailure, ReadFailure, AcquisitionStop) as error:
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
    header["mode"] = mode


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


def add_timing(report, boundaries, start, end):
    if (len(boundaries) not in (0, 2, 4) or boundaries != sorted(boundaries)
            or boundaries and not start <= boundaries[0] <= boundaries[-1] <= end):
        raise ValueError("receipt collection times are out of order")
    if len(boundaries) == 4 and boundaries[2] - boundaries[1] < GAP_NS:
        raise ValueError("receipt collections lack the required separation")
    report["timing"] = {
        "elapsed_ns": end - start,
        "pair_elapsed_ns": boundaries[-1] - boundaries[0] if boundaries else None,
        "collections": [{"started_ns": opening, "ended_ns": closing, "elapsed_ns": closing - opening}
                        for opening, closing in zip(boundaries[::2], boundaries[1::2], strict=True)],
    }


def capture(path, reader, checkpoint, inputs=DISPOSABLE_INPUTS, *, between=None, after_read=None, binding=None,
            mode=None, cancelled=None):
    if checkpoint not in CHECKPOINTS:
        raise ValueError("unknown operator-supplied checkpoint label")
    start = monotonic_ns()
    started_utc = time_ns()
    decision = None if binding is None else _input_decision(binding, inputs)
    limits = work_limits()
    with pending_journal(path) as journal:
        header = {"kind": "start", "schema": WORK_SCHEMA, "checkpoint": checkpoint,
                  "label_source": "disposable operator metadata", "base": reader.base,
                  "inputs": inputs, "limits": limits, "start_ns": start,
                  "utc": datetime.now(timezone.utc).isoformat()}
        if binding is not None:
            header.update(binding=binding, start_utc_ns=started_utc,
                          label_source="operator responsiveness declaration")
        _declare_mode(header, binding, mode)
        journal.write(header)

        def gap():
            if between is not None:
                between()
            sleep(GAP_SEC)

        try:
            if binding is not None:
                from checkpoint import validate_capture_marker

                validate_capture_marker(binding, checkpoint, start, started_utc, mode)
        except ReadFailure as error:
            journal.write(_refusal("marker_refused", error, mode))
            report = _report([], [], None, error.code, error.detail, 0, 0, mode)
            boundaries = []
        else:
            bounded = RecordingReader(reader, journal, limits, after_read, cancelled)
            report = _pair(bounded, reader.base, inputs if decision is None else decision.profile, gap, binding, mode)
            boundaries = bounded.timing
        _attach_input_result(report, decision, mode)
        end = monotonic_ns()
        add_timing(report, boundaries, start, end)
        journal.write({"kind": "report", "data": report, "end_ns": end})
    return report


def capture_refusal(path, checkpoint, error, *, binding=None, inputs=None, mode=None):
    if checkpoint not in CHECKPOINTS:
        raise ValueError("unknown operator-supplied checkpoint label")
    start = monotonic_ns()
    report = _report([], [], None, error.code, error.detail, 0, 0, mode)
    header = {"kind": "start", "schema": WORK_SCHEMA, "checkpoint": checkpoint,
              "label_source": "disposable operator metadata", "base": None,
              "inputs": None, "limits": work_limits(), "start_ns": start,
              "utc": datetime.now(timezone.utc).isoformat()}
    if binding is not None:
        header.update(binding=binding, inputs=inputs, start_utc_ns=time_ns(),
                      label_source="operator responsiveness declaration")
        _attach_input_result(report, _input_decision(binding, inputs), mode)
    _declare_mode(header, binding, mode)
    with pending_journal(path) as journal:
        journal.write(header)
        journal.write(_refusal("admission_refused", error, mode))
        end = monotonic_ns()
        add_timing(report, [], start, end)
        journal.write({"kind": "report", "data": report, "end_ns": end})
    return report


def replay(path, *, expected_mode=None):
    path = Path(path)
    if path.suffix == ".partial":
        raise ValueError("pending receipt was not durably published")
    with path.open("rb") as stream:
        lines = stream.read(MAX_JOURNAL_BYTES + 1).splitlines(keepends=True)
    if not 3 <= len(lines) <= MAX_JOURNAL_LINES or sum(map(len, lines)) > MAX_JOURNAL_BYTES:
        raise ValueError("receipt exceeds size bounds or is incomplete")
    actual = json.loads(lines[-1])
    if actual != {"kind": "seal", "sha256": sha256(b"".join(lines[:-1])).hexdigest()}:
        raise ValueError("receipt seal missing or invalid")
    header = json.loads(lines[0])
    trailer = json.loads(lines[-2])
    schema = header.get("schema")
    if schema not in (*LEGACY_SCHEMAS, WORK_SCHEMA) or (header.get("kind"), trailer.get("kind")) != ("start", "report"):
        raise ValueError("unrecognized receipt schema")
    historical = schema in LEGACY_SCHEMAS
    limits = LEGACY_LIMITS if historical else work_limits()
    if encode(header["limits"]) != encode(limits) or header["checkpoint"] not in CHECKPOINTS:
        raise ValueError("unrecognized receipt configuration")
    start, end = header["start_ns"], trailer["end_ns"]
    if type(start) is not int or type(end) is not int or end < start:
        raise ValueError("receipt has a reversed acquisition interval")
    mode = header.get("mode")
    if (schema == MODE_SCHEMA and mode not in MODES
            or "mode" in header and (schema not in (MODE_SCHEMA, WORK_SCHEMA) or mode not in MODES)):
        raise ValueError("invalid observation mode declaration")
    if expected_mode is not None and expected_mode != (mode or STRICT_MODE):
        raise ValueError("receipt mode differs from expected mode")
    binding = header.get("binding")
    if (schema == SCHEMA and binding is not None or schema in (BOUND_SCHEMA, MODE_SCHEMA) and binding is None
            or mode is not None and binding is None):
        raise ValueError("receipt binding does not match the declared schema")
    decision = None if binding is None else _input_decision(binding, header["inputs"])
    boundaries = []
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
        from checkpoint import validate_capture_marker

        code, detail = refusal["failure"]
        if code not in ("marker_duplicate", "marker_token"):
            try:
                validate_capture_marker(binding, header["checkpoint"], start, header["start_utc_ns"], mode,
                                        historical=historical)
            except ReadFailure as error:
                if (code, detail) != (error.code, error.detail):
                    raise ValueError("marker refusal reason differs") from error
            else:
                raise ValueError("receipt refused a valid marker")
        reproduced = _report([], [], None, code, detail, 0, 0, mode)
    else:
        if binding is not None:
            from checkpoint import validate_capture_marker

            validate_capture_marker(binding, header["checkpoint"], start, header["start_utc_ns"], mode,
                                    historical=historical)
        reader = ReplayReader(map(json.loads, lines[1:-2]), None if historical else limits)
        profile = header["inputs"] if decision is None else decision.profile
        reproduced = _pair(reader, header["base"], profile, lambda: None, binding, mode)
        if next(reader.events, None) is not None:
            raise ValueError("receipt contains extra acquisition events")
        boundaries = reader.timing
    _attach_input_result(reproduced, decision, mode)
    if not historical:
        add_timing(reproduced, boundaries, start, end)
    if encode(reproduced) != encode(trailer["data"]):
        raise ValueError("receipt result differs from native-traversal replay")
    return reproduced
