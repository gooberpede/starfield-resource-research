"""Build an owned whole-tree target, verify independent truth and check replay."""

import argparse
from contextlib import contextmanager
from hashlib import sha256
import json
from pathlib import Path
from queue import Empty, Queue
import shutil
import subprocess
import sys
from threading import Thread

from .census import (
    FIXTURE_NAME, LIMITS, NODE_END, STRUCTURAL_MODE, capture, encode, replay, source_identity,
)
from build_fixture import COMPILE, compiler_environment, file_digest, find_vcvars, inspect_fixture
from checkpoint import issue, mark
from memory import ReadFailure, epoch, require
from qualify_retail import simulated_append
from retail_admission import (
    LaunchBaseline, LogBaseline, ProcessMetadata, SIMULATED_PROFILE, open_simulated, publication_floor,
)


ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / ".local-work" / "codex" / "SRR-016"
SOURCE = Path(__file__).with_name("census_fixture.c")
WAIT = 30
TREE_CASES = {
    "empty": (0, 0, 0, 0, 0),
    "direct": (6, 1, 1, 0, 0),
    "holes": (6, 1, 1, 0, 0),
    "ordinary": (48, 13, 7, 4, 2),
    "corpus": (3600, 181, 150, 22, 3),
    "upper": (5120, 472, 394, 57, 4),
    "decoy-valid": (48, 13, 7, 4, 2),
    "long-chain": (48, 13, 7, 4, 2),
    "optional-absent": (48, 13, 7, 4, 2),
    "stable-clear": (6, 1, 1, 0, 0),
    "aba": (48, 13, 7, 4, 2),
    "missing-remap": (48, 13, 7, 4, 2),
}
NEGATIVES = {
    "bad-hole": "index_shape", "bad-count": "index_shape",
    "bad-span": "record_span", "bad-fence": "index_fence",
    "bad-minimum": "block_minimum", "bad-link": "leaf_link_mismatch",
    "cycle": "pointer_alias", "bad-level": "traversal_budget",
    "bad-child": "index_shape", "wrapper": "edge_type_mismatch",
    "alias-child": "pointer_alias", "blank-mixed": "mixed_prefix_unverified",
    "wrong-type": "edge_type_mismatch", "duplicate": "duplicate_identity",
    "bad-owner-key": "pndt_key_mismatch", "bad-biome-type": "form_type_mismatch",
    "bad-biom": "edge_biom_mismatch", "bad-rsgd-list": "rsgd_list_identity",
    "bad-resource-vptr": "resource_form_vptr_mismatch", "bad-resource-type": "resource_form_type_mismatch",
    "map-alias": "form_id_mismatch", "map-table-edge": "pointer_alias",
    "map-cycle": "form_map_unverified", "map-sentinel": "form_map_unverified",
    "map-duplicate": "form_duplicate", "decoy-invalid": "form_id_mismatch",
    "unreadable": "unreadable_region", "short-read": "read_incomplete",
    "mid-clear": "structural_change", "mid-insert": "structural_change",
    "mid-remove": "structural_change", "mid-repack": "structural_change",
    "mid-reuse": "structural_change", "pair-clear": "pair_value_mismatch",
    "pair-repack": "pair_structure_mismatch", "pair-input-drift-clear": "pair_identity_mismatch",
    "event-limit": "observation_budget",
    "byte-limit": "observation_budget", "window-limit": "traversal_budget",
    "entry-limit": "traversal_budget", "chain-limit": "traversal_budget",
    "rsgd-list-limit": "rsgd_list_budget",
    "cancel": "operator_cancelled", "compute-cancel": "operator_cancelled",
    "missing-steam-witness": "steam_log_unverified",
}
SCENARIO = {
    "stable-clear": "direct", "mid-clear": "direct", "pair-clear": "direct",
    "aba": "switch", "mid-repack": "switch", "pair-repack": "switch",
    "mid-insert": "insert", "mid-remove": "remove", "mid-reuse": "reuse",
    "short-read": "direct", "compute-cancel": "direct",
    "chain-limit": "long-chain",
}
MID = {
    "mid-clear": "clear", "mid-repack": "repack", "mid-insert": "insert",
    "mid-remove": "remove", "mid-reuse": "reuse",
}
BETWEEN = {"pair-clear": "clear", "pair-repack": "repack", "aba": "aba",
           "pair-input-drift-clear": "input-drift-clear"}


def build_fixture(directory):
    environment = compiler_environment(find_vcvars())
    compiler = Path(shutil.which("cl.exe", path=environment["PATH"]))
    linker = Path(shutil.which("link.exe", path=environment["PATH"]))
    target = directory / FIXTURE_NAME
    source_digest = file_digest(SOURCE)
    flags = ("/Brepro", f"/out:{FIXTURE_NAME}")
    with (directory / "build.log").open("xb") as log:
        subprocess.run([compiler, *COMPILE, SOURCE, "/link", *flags], cwd=directory,
                       env=environment, stdout=log, stderr=subprocess.STDOUT, check=True)
    if source_digest != file_digest(SOURCE):
        raise RuntimeError("fixture source changed during build")
    return target, {
        "source_sha256": source_digest, "compiler_sha256": file_digest(compiler),
        "linker_sha256": file_digest(linker), "msvc_toolset": environment["VCTOOLSVERSION"],
        "windows_sdk": environment["WINDOWSSDKVERSION"].rstrip("\\"),
        "fixture_sha256": file_digest(target), "image_size": inspect_fixture(target),
        "compile": COMPILE, "link": flags, "python": sys.version.split()[0],
    }


@contextmanager
def fixture(target, scenario):
    process = subprocess.Popen([target, scenario], cwd=target.parent, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, text=True, encoding="ascii",
                               creationflags=subprocess.CREATE_NO_WINDOW)
    replies = Queue()

    def read_replies():
        for line in process.stdout:
            replies.put(line.strip())
        replies.put(None)

    thread = Thread(target=read_replies, daemon=True)
    thread.start()

    def receive():
        try:
            line = replies.get(timeout=WAIT)
        except Empty as error:
            raise RuntimeError("fixture watchdog expired") from error
        if line is None:
            raise RuntimeError("fixture exited before replying")
        return line

    def command(text):
        process.stdin.write(text + "\n")
        process.stdin.flush()
        if text == "quit":
            return None
        if text == "truth":
            marker = receive().split()
            if len(marker) != 6 or marker[0] != "TRUTH":
                raise ValueError("malformed independent fixture truth")
            shape = tuple(map(int, marker[1:]))
            if not 0 <= shape[0] <= LIMITS["entries"]:
                raise ValueError("fixture truth exceeds the cap")
            rows = [tuple(map(int, receive().split())) for _ in range(shape[0])]
        if receive() != "ACK":
            raise RuntimeError("fixture command not acknowledged")
        return (shape, rows) if text == "truth" else None

    try:
        if receive() != "READY":
            raise RuntimeError("fixture not ready")
        yield process, command
    finally:
        if process.poll() is None:
            command("quit")
        process.stdin.close()
        try:
            code = process.wait(timeout=WAIT)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=WAIT)
            raise
        finally:
            thread.join(timeout=WAIT)
            process.stdout.close()
        if code:
            raise RuntimeError(f"owned fixture retired with status {code}")


def simulated_baseline(fixture_path, expected_hash, log):
    api = ProcessMetadata()
    parent_pid, parent_epoch = epoch(api, api.GetCurrentProcess())
    require(not api.census([FIXTURE_NAME])[FIXTURE_NAME], "process_ambiguous", "owned fixture name is already active")

    def check_parent():
        require(epoch(api, api.GetCurrentProcess()) == (parent_pid, parent_epoch),
                "epoch_mismatch", "disposable launcher epoch changed")

    return LaunchBaseline(api, fixture_path, expected_hash, LogBaseline.record(log), parent_pid, parent_epoch,
                          api.session(parent_pid), publication_floor(), SIMULATED_PROFILE, check_parent)


def measure_backend(api, limits):
    """Meter both calls below ImageReader, including its opening admission."""
    query_, process_read = api.VirtualQueryEx, api.ReadProcessMemory
    # Five ImageReader identities: initial qualification and four brackets.
    # Each has at most four mapped windows with two queries per window, plus
    # twelve pinned RVA protection checks. The PE header is bounded at 64 KiB.
    identity_query_cost = 5 * (2 * 4 + 12)
    identity_read_cost = 5 * 4
    identity_byte_cost = 5 * (0x10000 + 3 * 32)
    caps = {
        "virtual_query_calls": limits["events"] + identity_query_cost,
        "read_process_memory_calls": limits["events"] + identity_read_cost,
        "read_process_memory_bytes": limits["requested_bytes"] + identity_byte_cost,
    }
    actual = dict.fromkeys(caps, 0)

    def charge(metric, value):
        if actual[metric] + value > caps[metric]:
            raise ReadFailure("backend_budget", f"disposable {metric} cap exceeded")
        actual[metric] += value

    def query(*args):
        charge("virtual_query_calls", 1)
        return query_(*args)

    def read(handle, address, buffer, size, returned):
        charge("read_process_memory_calls", 1)
        charge("read_process_memory_bytes", size)
        return process_read(handle, address, buffer, size, returned)

    api.VirtualQueryEx = query
    api.ReadProcessMemory = read
    return actual, caps


def independent_truth(case):
    # Separate construction from the C builder. Use level-agnostic key/slot
    # arithmetic and sort composite identities once without parsing native memory.
    if case == "empty":
        return []
    count, mixed = {"direct": (4, 2), "holes": (4, 2), "stable-clear": (4, 2),
                    "corpus": (3210, 390), "upper": (4096, 1024)}.get(case, (36, 12))
    targets = []
    for ordinal in range(count):
        owner, biome = divmod(ordinal, 12)
        owner = 0x1FFFE0 if ordinal == count - 1 else 0x100000 + owner
        first = owner * (1 << 32) + 0x10025
        slots = [0] * 7
        if ordinal % 17:
            for offset, lane in enumerate((0, 2, 6)):
                slots[lane] = 0x400000 + ((ordinal + offset) % 64)
        targets.append((first, 0x200000 + biome, 0x90, *slots))
    excluded = [(0x100000 * (1 << 32) + (ordinal % ((count + 11) // 12)) * (1 << 32) + 0x10026,
                 0xFEED0000 + ordinal, 0x20 if ordinal % 2 else 0x38, *([0] * 7))
                for ordinal in range(mixed)]
    return sorted((*targets, *excluded))


def fixture_remap():
    # Independent fixture namespace manifest. It includes unused valid IDs and
    # never consults captured process values.
    ids = [*range(0x100000, 0x100000 + 342), 0x1FFFE0,
           *range(0x200000, 0x200000 + 13), *range(0x400000, 0x400000 + 64)]
    # Reverse source IDs so canonical sort cannot be obtained from raw key order.
    return {f"{value:08X}": f"fixture.esm:{0xFFFFFF - value:06X}" for value in ids}


def check_truth(case, truth, report, remap):
    shape, rows = truth
    if shape != TREE_CASES[case] or rows != independent_truth(case):
        raise AssertionError(f"{case}: fixture truth differs from independent shape/row reference: {shape}")
    for pass_ in report["collections"]:
        if ((pass_["mixed_visited"], pass_["tree_windows"], pass_["blocks"], len(pass_["leaves"]))
                != shape[:4] or not pass_["coverage_verified"]):
            raise AssertionError(f"{case}: root-backed extent count differs")
        actual = []
        for entry in pass_["descriptors"]:
            slots = entry.get("raw_slots", [0] * 7)
            actual.append((*entry["raw_key"], entry["size"], *slots))
        expected = rows if case != "stable-clear" else [(*row[:3], *([0] * 7)) for row in rows]
        if actual != expected:
            raise AssertionError(f"{case}: raw walked descriptor truth differs")
        if len({entry["edge"] for entry in pass_["descriptors"]}) != shape[0]:
            raise AssertionError(f"{case}: repeated physical edge")
        if case == "missing-remap":
            if pass_["rows"] or not pass_["remap_missing"]:
                raise AssertionError("unresolved remap leaked a normalized row")
            continue
        canonical = []
        for first, second, width, *slots in expected:
            if width == 0x90:
                canonical.append({"key": [remap[f"{first >> 32:08X}"], remap[f"{second:08X}"]],
                                  "raw_key": [first, second], "raw_slots": slots, "typed": "VERIFIED",
                                  "slots": [remap[f"{slot:08X}"] if slot else None for slot in slots]})
        if pass_["rows"] != sorted(canonical, key=lambda row: row["key"]):
            raise AssertionError(f"{case}: canonical sorted reference differs")


@contextmanager
def shorten_first_window(admission, case):
    with admission as source:
        if case == "short-read":
            original = source.read

            def read(address, size, alignment=1):
                value = original(address, size, alignment)
                return value[:-1] if size == NODE_END else value

            source.read = read
        yield source


def run_case(directory, target, image_hash, case):
    path = directory / f"{case}.jsonl"
    log = directory / f"{case}.steam.log"
    log.write_bytes(b"disposable tracking baseline\n")
    baseline = simulated_baseline(target, image_hash, log)
    remap = fixture_remap()
    if case == "missing-remap":
        del remap["001FFFE0"]
    limits = dict(LIMITS)
    overrides = {"event-limit": ("events", 13), "byte-limit": ("requested_bytes", 1024),
                 "window-limit": ("tree_windows", 3), "entry-limit": ("entries", 12),
                 "chain-limit": ("form_chain", 8), "rsgd-list-limit": ("biom_rsgds", 1)}
    if case in overrides:
        key, value = overrides[case]
        limits[key] = value
    backend_actual, backend_caps = measure_backend(baseline.api, limits)
    affected = False
    polls_until_cancel = None
    with fixture(target, SCENARIO.get(case, case)) as (process, command):
        if case != "missing-steam-witness":
            simulated_append(log, process.pid, target)
        truth = command("truth") if case in TREE_CASES else None
        if case == "stable-clear":
            command("clear")
        pid, creation = epoch(baseline.api, int(process._handle))
        attempt = issue(directory, STRUCTURAL_MODE)
        marker = mark(attempt, {"pid": pid, "creation": creation}, "title")
        binding = {"target_kind": "simulated", "attempt": attempt, "marker": marker}

        def after_read(_address, size, _alignment):
            nonlocal affected, polls_until_cancel
            if size == NODE_END and not affected:
                affected = True
                if case in MID:
                    command(MID[case])
                if case == "compute-cancel":
                    polls_until_cancel = 1

        def cancelled():
            nonlocal polls_until_cancel
            if case == "cancel":
                return True
            if polls_until_cancel is None:
                return False
            result = polls_until_cancel == 0
            polls_until_cancel -= 1
            return result

        def between():
            if case in BETWEEN:
                command(BETWEEN[case])

        admission = shorten_first_window(open_simulated(baseline, process), case)
        report = capture(path, directory, admission, binding, remap, limits=limits,
                         cancelled=cancelled, between=between, after_read=after_read)
    if replay(path) != report:
        raise AssertionError(f"{case}: private checked replay differs")
    failure = report["failure"]
    if (failure[0] if failure else None) != NEGATIVES.get(case):
        raise AssertionError(f"{case}: expected {NEGATIVES.get(case)}, got {failure}")
    if truth:
        check_truth(case, truth, report, remap)
    if case == "optional-absent" and not all(
            pass_["descriptors"][0]["forms"]["override_reason"] == "form_absent"
            for pass_ in report["collections"]):
        raise AssertionError("independent missing optional-RSGD witness was discarded")
    state = report["observation"]
    if case in ("missing-remap", "pair-clear"):
        if state["structure"] != "QUALIFIED" or state["acquisition"] != "ACQUISITION_INDETERMINATE":
            raise AssertionError(f"{case}: structure and normalized admission were conflated")
    elif (state["acquisition"] == "QUALIFIED") != (case in TREE_CASES):
        raise AssertionError(f"{case}: unexpected acquisition classification")
    stats = {
        "failure": failure[0] if failure else None, "structure": report["structure"],
        "normalization": report["normalization"], "counts": report["coverage_counts"],
        "events": report["events"], "bytes": report["requested_bytes"],
        "backend_costs": backend_actual, "backend_caps": backend_caps,
        "receipt_bytes": path.stat().st_size, "receipt_sha256": file_digest(path),
        "timing_ns": report["timing"]["elapsed_ns"],
    }
    if case in ("corpus", "upper", "direct"):
        (directory / f"{case}-observation.json").write_bytes(encode(state) + b"\n")
    if case == "compute-cancel" and b'"kind":"compute_cancelled"' not in path.read_bytes():
        raise AssertionError("compute-only cancellation was not exercised")
    if case == "missing-steam-witness" and report["admission_refusal_source"] != "ATTESTED_AT_ACQUISITION":
        raise AssertionError("admission refusal did not preserve its evidence class")
    return stats


def tamper_checks(directory):
    source = directory / "direct.jsonl"
    checks = ("replay-source", "replay-remap", "replay-gap", "replay-short",
              "replay-report", "replay-budget", "replay-seal", "replay-pending")
    for case in checks:
        events = [json.loads(line) for line in source.read_bytes().splitlines()][:-1]
        if case == "replay-source":
            events[0]["reader_source_sha256"] = "a" * 64
        if case == "replay-remap":
            events[0]["remap_sha256"] = "b" * 64
        if case == "replay-gap":
            boundaries = [row for row in events if row["kind"].startswith("collection_")]
            boundaries[2]["mono_ns"] = boundaries[1]["mono_ns"]
        if case == "replay-short":
            read = next(row for row in events if row["kind"] == "read")
            read["value"] = read["value"][:-2]
        if case == "replay-report":
            events[-1]["data"]["events"] += 1
        if case == "replay-budget":
            events[0]["limits"]["events"] = 13
        raw = b"".join(encode(event) + b"\n" for event in events)
        seal = "0" * 64 if case == "replay-seal" else sha256(raw).hexdigest()
        target = directory / (f"{case}.partial" if case == "replay-pending" else f"{case}.jsonl")
        target.write_bytes(raw + encode({"kind": "seal", "sha256": seal}) + b"\n")
        try:
            replay(target)
        except ValueError:
            continue
        raise AssertionError(f"{case}: tampered receipt was accepted")
    return checks


def remap_collision_control(directory):
    from .census import validate_remap

    remap = fixture_remap()
    remap["00100001"] = remap["00100000"]
    try:
        validate_remap(remap)
    except ValueError:
        (directory / "remap-collision-refused.txt").write_text(
            "Two runtime PNDT IDs map to one canonical PNDT identity. Refused before admission.\n",
            encoding="utf-8")
        return
    raise AssertionError("contradictory remap was accepted")


def run(directory):
    directory.mkdir(parents=True, exist_ok=False)
    target, build = build_fixture(directory)
    stats = {}
    for case in (*TREE_CASES, *NEGATIVES):
        stats[case] = run_case(directory, target, build["fixture_sha256"], case)
        print(f"{case}: {stats[case]['failure'] or stats[case]['normalization']}", flush=True)
    challenges = tamper_checks(directory)
    remap_collision_control(directory)
    result = {"fixture_build": build, "reader_source_sha256": source_identity(), "limits": LIMITS,
              "process_controls": stats, "replay_negatives": challenges, "remap_collision_refused": True}
    (directory / "qualification.json").write_bytes(encode(result) + b"\n")
    print(f"{len(stats)} owned-process controls, {len(challenges)} tamper controls, 1 remap preflight control")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", nargs="?")
    parser.add_argument("--replay", type=Path)
    args = parser.parse_args()
    if args.replay is not None and args.run is None:
        print(encode(replay(args.replay)["observation"]).decode("ascii"))
    elif args.replay is None and args.run and args.run.replace("-", "").isalnum():
        run(WORK / args.run)
    else:
        parser.error("supply a unique run name or --replay to check a sealed receipt")


if __name__ == "__main__":
    main()
