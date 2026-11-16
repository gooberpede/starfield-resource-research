"""Capture and replay bounded acquisition using the same native decoder."""

from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
from time import monotonic_ns, sleep

from contract import CHECKPOINTS, DISPOSABLE_INPUTS, SAMPLES, classify
from memory import ReadFailure
from native import NativeFailure, collect

SCHEMA = "srr013-disposable-observation-v1"
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

    def identity(self):
        return self._record("identity", [], self.reader.identity)


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

    def identity(self):
        return self._take("identity", [])


def _pair(reader, base, inputs, between):
    collections = []
    brackets = []
    failure = None
    detail = None
    try:
        for ordinal in range(2):
            beginning = reader.identity()
            data = collect(reader, base, SAMPLES)
            collections.append(data)
            end = reader.identity()
            brackets.append([beginning, end])
            if beginning != end or beginning != brackets[0][0]:
                raise ReadFailure("process_identity_changed", "process or mapped image drifted")
            if ordinal == 0:
                between()
    except (NativeFailure, ReadFailure) as error:
        failure, detail = error.code, error.detail
    return _report(collections, brackets, inputs, failure, detail, reader.calls, reader.bytes)


def _report(collections, brackets, inputs, failure, detail, calls, byte_count):
    if failure is None and len(collections) == 2 and collections[0] != collections[1]:
        failure = "inconsistent_pair"
    results = classify(collections, inputs, failure)
    return {
        "failure": failure, "detail": detail, "samples": results,
        "collections": collections, "identity_brackets": brackets,
        "read_and_identity_calls": calls, "requested_bytes": byte_count,
        "counts": {outcome: sum(row["outcome"] == outcome for row in results)
                   for outcome in sorted({row["outcome"] for row in results})},
    }


def capture(path, reader, checkpoint, inputs=DISPOSABLE_INPUTS, *, between=None, after_read=None):
    if checkpoint not in CHECKPOINTS:
        raise ValueError("unknown operator-supplied checkpoint label")
    start = monotonic_ns()
    with Path(path).open("xb") as stream:
        journal = Journal(stream)
        journal.write({"kind": "start", "schema": SCHEMA, "checkpoint": checkpoint,
                       "label_source": "disposable operator metadata", "base": reader.base,
                       "inputs": inputs, "limits": LIMITS, "start_ns": start,
                       "utc": datetime.now(timezone.utc).isoformat()})

        def gap():
            if between is not None:
                between()
            sleep(GAP_SEC)

        bounded = RecordingReader(reader, journal, start + WINDOW_NS, after_read)
        report = _pair(bounded, reader.base, inputs, gap)
        journal.write({"kind": "report", "data": report, "end_ns": monotonic_ns()})
        journal.seal()
    return report


def capture_refusal(path, checkpoint, error):
    if checkpoint not in CHECKPOINTS:
        raise ValueError("unknown operator-supplied checkpoint label")
    start = monotonic_ns()
    report = _report([], [], None, error.code, error.detail, 0, 0)
    with Path(path).open("xb") as stream:
        journal = Journal(stream)
        journal.write({"kind": "start", "schema": SCHEMA, "checkpoint": checkpoint,
                       "label_source": "disposable operator metadata", "base": None,
                       "inputs": None, "limits": LIMITS, "start_ns": start,
                       "utc": datetime.now(timezone.utc).isoformat()})
        journal.write({"kind": "admission_refused", "failure": [error.code, error.detail]})
        journal.write({"kind": "report", "data": report, "end_ns": monotonic_ns()})
        journal.seal()
    return report


def replay(path):
    with Path(path).open("rb") as stream:
        lines = stream.read(8 * MAX_BYTES + 1).splitlines(keepends=True)
    if not 3 <= len(lines) <= MAX_EVENTS + 8 or sum(map(len, lines)) > 8 * MAX_BYTES:
        raise ValueError("receipt exceeds size bounds or is incomplete")
    actual = json.loads(lines[-1])
    if actual != {"kind": "seal", "sha256": sha256(b"".join(lines[:-1])).hexdigest()}:
        raise ValueError("receipt seal missing or invalid")
    header = json.loads(lines[0])
    trailer = json.loads(lines[-2])
    if (header.get("schema"), header.get("kind"), trailer.get("kind")) != (SCHEMA, "start", "report"):
        raise ValueError("unrecognized receipt schema")
    if header["limits"] != LIMITS or header["checkpoint"] not in CHECKPOINTS:
        raise ValueError("unrecognized receipt configuration")
    if trailer["end_ns"] < header["start_ns"]:
        raise ValueError("receipt has a reversed acquisition interval")
    if header["base"] is None:
        refusal = json.loads(lines[1])
        if len(lines) != 4 or refusal.get("kind") != "admission_refused" or header["inputs"] is not None:
            raise ValueError("invalid refusal receipt")
        code, detail = refusal["failure"]
        reproduced = _report([], [], None, code, detail, 0, 0)
    else:
        reader = ReplayReader(map(json.loads, lines[1:-2]))
        reproduced = _pair(reader, header["base"], header["inputs"], lambda: None)
        if next(reader.events, None) is not None:
            raise ValueError("receipt contains extra acquisition events")
    if encode(reproduced) != encode(trailer["data"]):
        raise ValueError("receipt result differs from native-traversal replay")
    return reproduced
