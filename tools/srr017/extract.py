"""Read one paired rooted-store observation from an already running target.

Run ``python -m tools.srr017.extract --output DIRECTORY [--pid PID]`` only
after the operator has placed Starfield at its responsive title card. This
command never launches or closes the target and never retries acquisition.
"""

import argparse
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import signal
from uuid import uuid4

from tools.srr016 import census
from .export import bound_dataset, comparator_observation, file_sha256, output_bytes
from .work import GAME_IMAGE_BYTES, OUTPUT_BYTES, backend_caps, meter_backend
from contract import RETAIL_APPLICABILITY
from memory import ImageReader, ReadFailure, disk_profile, epoch, require
from retail_admission import MAX_PROCESSES, ProcessMetadata


ROOT = Path(__file__).resolve().parents[2]
FILES = ("tools/srr017/extract.py", "tools/srr017/export.py", "tools/srr017/source.py",
         "tools/srr017/namespace.py", "tools/srr017/work.py", "tools/srr016/census.py",
         "tools/srr016/compare.py", "tools/srr016/ledger.py", "tools/srr013/memory.py",
         "tools/srr013/native.py", "tools/srr013/observe.py", "tools/srr013/contract.py",
         "tools/srr013/checkpoint.py", "tools/srr013/retail_admission.py")


@dataclass(frozen=True)
class Services:
    api_factory: object = ProcessMetadata
    target_name: str = "Starfield.exe"
    expected_sha256: str = RETAIL_APPLICABILITY["sha256"]
    retail_layout: bool = True
    profile_name: str = "srr017-operator-retail"
    target_kind: str = "retail"


REAL = Services()


def work_manifest(limits=None):
    limits = census._checked_limits(census.RETAIL_LIMITS if limits is None else limits, retail_flow=True)
    return {"census": limits, "backend": backend_caps(limits),
            "process_census_rows": MAX_PROCESSES, "process_census_calls": 1,
            "image_hashes": MAX_PROCESSES + 8, "image_hash_bytes_each": GAME_IMAGE_BYTES,
            "portable_output_bytes_each": OUTPUT_BYTES}


def source_manifest():
    return {"schema": "srr017-operator-source-v1",
            "files": {name: file_sha256(ROOT / name) for name in FILES}}


def digest(value):
    return sha256(census.encode(value)).hexdigest()


class ImageHashes:
    """Bound executable hashing; no Steam or ESM file is opened."""

    def __init__(self, cancelled):
        self.cancelled, self.calls, self.bytes = cancelled, 0, 0

    def __call__(self, stream):
        size = os.fstat(stream.fileno()).st_size
        require(0 < size <= GAME_IMAGE_BYTES and self.calls < MAX_PROCESSES + 8,
                "image_hash_budget", "executable hash work exceeded")
        self.calls += 1
        self.bytes += size + 1
        stream.seek(0)
        result, remaining = sha256(), size
        while remaining:
            require(not self.cancelled(), "operator_cancelled", "operator cancelled observation")
            block = stream.read(min(remaining, 1024 * 1024))
            require(bool(block), "image_hash_changed", "executable shortened during hashing")
            result.update(block)
            remaining -= len(block)
        require(not stream.read(1), "image_hash_changed", "executable grew during hashing")
        return result.hexdigest()


@contextmanager
def selected_reader(api, services, pid, hashes, notify):
    """Select by executable name, pinned image and PE layout, then bind its epoch."""
    candidates = api.census((services.target_name,))[services.target_name.casefold()]
    if pid is not None:
        require(isinstance(pid, int) and pid > 0, "process_selection", "PID must be positive")
        candidates = [item for item in candidates if item[0] == pid]
    require(candidates, "process_absent", "no selected target process is running")
    compatible, refused = [], []
    for candidate, _parent in candidates:
        try:
            with api.open(candidate, read=False) as handle:
                expected_epoch = epoch(api, handle)
                path = api.process_path(handle)
                with path.open("rb") as stream:
                    require(hashes(stream) == services.expected_sha256,
                            "wrong_executable", "selected executable SHA-256 is incompatible")
                    profile = disk_profile(stream, retail=services.retail_layout)
                compatible.append((candidate, expected_epoch, path, profile))
        except (ReadFailure, OSError) as error:
            if isinstance(error, ReadFailure) and error.code == "operator_cancelled":
                raise
            refused.append(str(error))
    require(compatible, "wrong_executable", "no compatible target: " + "; ".join(refused))
    require(len(compatible) == 1, "process_ambiguous", "multiple compatible targets; specify --pid")
    candidate, expected_epoch, path, profile = compatible[0]
    notify(f"Selected {services.target_name} PID {candidate}: {path}")
    with api.open(candidate, read=True) as handle, path.open("rb") as stream:
        reader = ImageReader(api, handle, expected_epoch, path, stream,
                             services.expected_sha256, profile, True,
                             profile_name=services.profile_name, digest_file=hashes)
        yield reader


def write_json(path, value):
    with path.open("xb") as stream:
        stream.write(output_bytes(value))


def replay_dataset(receipt):
    before = file_sha256(receipt)
    report = census.replay_operator(receipt)
    require(file_sha256(receipt) == before, "evidence_changed", "receipt changed during replay")
    return report, bound_dataset(report, before, census.source_identity())


def run(output=None, *, pid=None, services=REAL, cancelled=None, limits=None,
        between=None, notify=print):
    """Execute once; fixture injection changes only the expected executable identity."""
    cancelled = cancelled or (lambda: False)
    if output is None:
        output = Path(".local-work") / ("srr017-extract-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                                         + "-" + uuid4().hex[:8])
    output = Path(output).absolute()
    output.mkdir(parents=True, exist_ok=True)
    names = ("receipt.jsonl", "dataset.json", "observation.json", "result.json", "manifest.json")
    if any((output / name).exists() for name in names):
        raise FileExistsError("output filenames already exist; choose another output directory")
    work, source = work_manifest(limits), source_manifest()
    summary = {"status": "FAILED", "output": str(output), "source_sha256": digest(source),
               "work_sha256": digest(work), "failure": None}
    receipt = output / "receipt.jsonl"
    try:
        api = services.api_factory()
        backend, caps = meter_backend(api, work["census"])
        hashes = ImageHashes(cancelled)
        with selected_reader(api, services, pid, hashes, notify) as reader:
            summary["process"] = {"pid": reader.expected_epoch[0], "creation": reader.expected_epoch[1],
                                  "path": str(reader.path), "image_sha256": reader.sha256}
            census.capture_operator(receipt, reader, limits=work["census"], cancelled=cancelled,
                                    between=between, target_kind=services.target_kind)
        report, dataset = replay_dataset(receipt)
        write_json(output / "dataset.json", dataset)
        summary["failure"] = report.get("failure")
        summary["acquisition"] = dataset["acquisition"]
        summary["rows"] = len(dataset["rows"])
        if dataset["acquisition"] == "QUALIFIED":
            write_json(output / "observation.json", comparator_observation(dataset))
            summary["status"] = "FINISHED"
        else:
            summary["status"] = "INCOMPLETE"
        summary["backend"] = {"actual": backend, "caps": caps}
        summary["executable_hashes"] = {"calls": hashes.calls, "bytes": hashes.bytes}
        require(source_manifest() == source, "source_changed", "execution source changed during observation")
    except (ReadFailure, OSError, ValueError) as error:
        summary["status"] = "INCOMPLETE" if receipt.exists() else "FAILED"
        summary["failure"] = [getattr(error, "code", type(error).__name__), str(error)]
    write_json(output / "result.json", summary)
    manifest = {"source": source, "work": work,
                "files": {name: file_sha256(output / name) for name in names[:-1] if (output / name).exists()}}
    write_json(output / "manifest.json", manifest)
    notify(f"{summary['status']}: {output}" + (f" — {summary['failure']}" if summary["failure"] else ""))
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--pid", type=int)
    parser.add_argument("--replay", type=Path, help="check a retained receipt without opening a process")
    parser.add_argument("--identity", action="store_true", help="print source/work identities without opening a process")
    args = parser.parse_args()
    if args.replay:
        report, dataset = replay_dataset(args.replay)
        print(json.dumps({"acquisition": dataset["acquisition"], "rows": len(dataset["rows"]),
                          "failure": report.get("failure")}, indent=2))
        return 0 if dataset["acquisition"] == "QUALIFIED" else 1
    if args.identity:
        print(json.dumps({"source": source_manifest(), "source_sha256": digest(source_manifest()),
                          "work": work_manifest(), "work_sha256": digest(work_manifest())}, indent=2))
        return 0
    cancellation = [False]
    signal.signal(signal.SIGINT, lambda *_args: cancellation.__setitem__(0, True))
    try:
        result = run(args.output, pid=args.pid, cancelled=lambda: cancellation[0])
    except (OSError, ValueError) as error:
        print(f"FAILED: {error}")
        return 1
    return 0 if result["status"] == "FINISHED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
