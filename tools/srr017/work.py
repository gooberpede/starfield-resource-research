"""Combined work limits for one integrated SRR-017 title acquisition."""

from hashlib import sha256
import os
from pathlib import Path

from tools.srr016.census import RETAIL_LIMITS
from memory import require


MIB = 1024 * 1024
# Manifest values for the production command; the owned suite may lower limits.
IDENTITIES = 8  # Opening, marker, four collection boundaries and closeout margin.
IDENTITY_QUERIES = 22  # Two checks per mapped window, and twelve anchor regions.
IDENTITY_READS = 5
IDENTITY_BYTES = 0x10000 + 115
OUTPUT_BYTES = 64 * MIB
SOURCE_FILES = 256
SOURCE_DISK_BYTES = 4 * 1024 * MIB  # Per stability pass, across the admitted roster.
SOURCE_MANIFEST_BYTES = 64 * MIB
STEAM_IMAGE_BYTES = 16 * MIB
GAME_IMAGE_BYTES = 128 * MIB
MINIMUM_FREE_BYTES = 40_000_000_000
WRITE_RESERVE_BYTES = 512 * MIB


def backend_caps(limits):
    return {
        "virtual_query_calls": limits["events"] + IDENTITIES * IDENTITY_QUERIES,
        "read_process_memory_calls": limits["events"] + IDENTITIES * IDENTITY_READS,
        "read_process_memory_bytes": limits["requested_bytes"] + IDENTITIES * IDENTITY_BYTES,
    }


RETAIL_WORK = {
    "census": RETAIL_LIMITS,
    "backend": backend_caps(RETAIL_LIMITS),
    "identity_brackets_max": IDENTITIES,
    "steam_process_rows_per_census": 32768,
    "steam_census_calls_max": 24,
    "steam_log_tail_bytes": 4096,
    "steam_log_append_bytes": MIB,
    "steam_client_hashes": 12,
    "steam_client_max_bytes": STEAM_IMAGE_BYTES,
    "game_image_hashes": 10,
    "game_image_max_bytes": GAME_IMAGE_BYTES,
    "source_files": SOURCE_FILES,
    "source_disk_bytes_per_pass": SOURCE_DISK_BYTES,
    "source_stability_passes": 2,
    "source_manifest_bytes": SOURCE_MANIFEST_BYTES,
    "portable_output_bytes": OUTPUT_BYTES,
    "minimum_free_bytes_each_drive": MINIMUM_FREE_BYTES,
    "write_reserve_bytes_each_drive": WRITE_RESERVE_BYTES,
}


def meter_backend(api, limits):
    """Apply aggregate caps before dispatching the existing Windows read operations."""
    caps = backend_caps(limits)
    actual = dict.fromkeys(caps, 0)
    query, read = api.VirtualQueryEx, api.ReadProcessMemory

    def charge(metric, amount):
        require(0 <= amount <= caps[metric] - actual[metric], "backend_budget", f"{metric} cap exceeded")
        actual[metric] += amount

    def query_region(*args):
        charge("virtual_query_calls", 1)
        return query(*args)

    def read_window(handle, address, buffer, size, returned):
        charge("read_process_memory_calls", 1)
        charge("read_process_memory_bytes", size)
        return read(handle, address, buffer, size, returned)

    api.VirtualQueryEx = query_region
    api.ReadProcessMemory = read_window
    return actual, caps


class ImageDigestMeter:
    """Charge each bounded file hash before reading, including attribution rechecks."""

    def __init__(self, cancelled=None):
        self.counts = {"steam": 0, "game": 0}
        self.bytes = dict.fromkeys(self.counts, 0)
        self.cancelled = cancelled

    def __call__(self, stream):
        kind = "steam" if Path(stream.name).name.casefold() == "steam.exe" else "game"
        limit = RETAIL_WORK["steam_client_max_bytes"] if kind == "steam" else RETAIL_WORK["game_image_max_bytes"]
        calls = RETAIL_WORK["steam_client_hashes"] if kind == "steam" else RETAIL_WORK["game_image_hashes"]
        length = os.fstat(stream.fileno()).st_size
        require(0 < length < limit and self.counts[kind] < calls,
                "image_hash_budget", "image hash inputs exceed the reviewed bounds")
        self.counts[kind] += 1
        self.bytes[kind] += length + 1
        digest = sha256()
        stream.seek(0)
        remaining = length
        while remaining:
            require(self.cancelled is None or not self.cancelled(), "operator_cancelled",
                    "operator cancelled the observation")
            data = stream.read(min(remaining, MIB))
            require(bool(data), "image_hash_changed", "image shortened during hashing")
            digest.update(data)
            remaining -= len(data)
        require(not stream.read(1), "image_hash_changed", "image grew during hashing")
        return digest.hexdigest()
