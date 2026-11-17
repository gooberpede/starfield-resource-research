"""Freeze a conditional native-slot oracle from the pinned production model."""

import argparse
from collections import Counter
import json
import math
from pathlib import Path
import struct
import subprocess
import sys

from .ledger import (
    FREEZE, ORACLE, REPRODUCER_COMMIT, RETAIL_SHA256, base_id, build_ledger,
    control_authority, digest, file_digest, require,
)


DATA_DIGESTS = {
    "ires-hierarchy.csv": "5e266537b816c7669ca6bb0a8f3184025023eaab4eab5664734643764acc50ae",
    "planet-resource-generation.csv": "22a4335aa5481093845f770efa660356b0d03c023b0efdd4b63d7d816f8207ca",
    "planet-atmospheric-resources.csv": "315a305dbb053d715c158a1f1306e5822826e4b14b979eba7ff9393db0655d4e",
    "planet-directory.csv": "c460062747126a2168109739e75742d325cedf54b98577e5a017b5108ec5eb90",
}


def binary32(value):
    return struct.unpack("<f", struct.pack("<f", value))[0]


def native_weight(weight):
    value = binary32(float(weight))
    require(math.isfinite(value), "NONFINITE_NATIVE_WEIGHT")
    return binary32(value * binary32(0.01))


def resource_word(resource):
    return resource.form_id.numeric if resource is not None else 0


def slot_special(selected_entry, count_before):
    """The retail count branch precedes both the slot store and shared helper."""
    if selected_entry is None or count_before >= 8:
        return 0
    word = resource_word(selected_entry.resource)
    require(word and word == selected_entry.resource_form_id.numeric,
            "UNRESOLVED_SPECIAL_POINTER_PAIR")
    return word


def eligible(definition, rarity):
    if definition is None:
        return ()
    return tuple(entry for entry in definition.entries if entry.resource_rarity.value == rarity)


def choose(definitions, rarity, roll, native):
    """Finite-weight selection, carrying cumulative across the BIOM retry."""
    cumulative = 0.0
    for definition in definitions:
        for entry in eligible(definition, rarity):
            weight = entry.common_chance if rarity == "Common" else entry.special_chance
            cumulative = (binary32(cumulative + native_weight(weight)) if native
                          else cumulative + float(weight) / 100.0)
            require(math.isfinite(cumulative), "NONFINITE_NATIVE_CUMULATIVE")
            if roll < cumulative:
                return definition, entry
    return None, None


def occupancy_after(words):
    ordered = list(dict.fromkeys(words))
    return set(ordered[:8])


def descendant_flags(result, ires_nodes, common_entries):
    names = ("Uncommon", "Rare", "Exotic", "Unique")
    flags = set()
    for family in result.family_results:
        root = family.root.form_id
        current = root
        for name, level in zip(names, family.levels, strict=True):
            require(level.rarity.value == name, "INVALID_DESCENDANT_LANE")
            # A skipped full-state level returns the unchanged node. An empty
            # candidate level has no selected node and need not advance it.
            if level.inclusion_roll is None and level.selected_candidate is not None:
                require(level.selected_candidate.form_id == current, "INVALID_DESCENDANT_GUARD")
                continue
            children = ires_nodes[root].children
            if current != root:
                children += ires_nodes[current].children
            native_pool = tuple(child.form_id for child in children if child.rarity is level.rarity)
            if native_pool != tuple(child.form_id for child in level.candidates):
                flags.add("DESCENDANT_CANDIDATE_SEQUENCE_OR_MULTIPLICITY")
            if level.inclusion_roll is not None:
                root_entry = common_entries[family.origin.biome_index]
                require(root_entry.resource_form_id == root, "FAMILY_ORIGIN_DRIFT")
                chance = getattr(root_entry, f"{name.lower()}_chance")
                if ((level.inclusion_roll < native_weight(chance)) !=
                        (level.inclusion_roll < level.inclusion_threshold)):
                    flags.add("DESCENDANT_BINARY32_BOUNDARY")
            if level.selected_candidate is not None:
                current = level.selected_candidate.form_id
    return flags


def screen_owner(result, ires_nodes):
    """Check the whole owner along recorded rolls. Refuse a divergent path."""
    flags = set()
    biomes = {biome.index: biome for biome in result.initial_biomes}
    order = [biome.form_id.numeric for biome in result.initial_biomes]
    if len(biomes) != len(order) or len(set(order)) != len(order) or order != sorted(order):
        flags.add("AUTHORED_ORDER_OR_KEY_MULTIPLICITY")
    if not result.planet.resource_creation_seed:
        flags.add("ZERO_SEED_RETAIL_STATE")

    atmosphere = [resource_word(item.resource) for item in result.atmospheric_occurrences]
    everywhere = {}
    for biome in result.shuffled_biomes:
        entries = eligible(biome.biom_rsgd, "Everywhere")
        require(all(entry.resource_form_id.numeric for entry in entries), "INVALID_EVERYWHERE_RESOURCE")
        everywhere[biome.index] = entries[0].resource_form_id.numeric if entries else 0
    native_occupied = occupancy_after([*atmosphere, *(word for word in everywhere.values() if word)])

    occupied = set()
    selected = {}
    special = {}
    common_entries = {}
    for event in result.events:
        name = event.kind.value
        if name == "RESOURCE_OCCURRENCE_RECORDED":
            if event["occupied_new_slot"]:
                occupied.add(resource_word(event["resource"]))
            require(len(occupied) == event["occupied_count_after"], "OCCUPANCY_EVENT_DRIFT")
        elif name == "EVERYWHERE_PREPASS_END" and occupied != native_occupied:
            flags.add("EVERYWHERE_PREPASS_OCCUPANCY")
        elif name in {"SPECIAL_PASS_RESULT", "COMMON_ROLL"}:
            biome = biomes[event["biome_index"]]
            rarity, roll = event["category"].value, event["roll"]
            model = choose((biome.effective_rsgd,), rarity, roll, native=False)
            require(resource_word(model[1].resource if model[1] else None) ==
                    resource_word(event["selected_resource"]), "SELECTOR_EVENT_DRIFT")
            retail = choose((biome.pndt_rsgd, biome.biom_rsgd), rarity, roll, native=True)
            if model != retail:
                flags.add("BINARY32_SELECTION_OR_SAME_ROLL_BIOM_RETRY")
            if name == "SPECIAL_PASS_RESULT":
                selected[biome.index] = {
                    "word": resource_word(event["selected_resource"]),
                    "count_before": len(occupied),
                    "already_occupied": resource_word(event["selected_resource"]) in occupied,
                }
                special[biome.index] = slot_special(model[1], len(occupied))
            elif model[1] is not None:
                common_entries[biome.index] = model[1]
        elif name == "COMMON_GUARD_FALLBACK_CANDIDATES":
            biome = biomes[event["biome_index"]]
            native_common = tuple(entry.resource_form_id for entry in eligible(biome.biom_rsgd, "Common"))
            if native_common != tuple(root.form_id for root in event["rsgd_common_roots"]):
                flags.add("GUARD_BIOM_COMMON_SEQUENCE")
            if native_common:
                flags.add("GUARD_CACHE_ORDER_AND_MULTIPLICITY_UNATTESTED")

    flags.update(descendant_flags(result, ires_nodes, common_entries))
    words = {}
    for row in result.biome_results:
        biome = row.orchestration.biome
        family = row.common_assignment.family
        common = (0,) * 5
        if family is not None:
            common = (
                resource_word(family.root),
                *(resource_word(level.selected_candidate) if level.emitted else 0
                  for level in family.levels),
            )
            require(len(common) == 5, "INVALID_FAMILY_LANES")
        words[biome.index] = (*common, special[biome.index], everywhere[biome.index])
    return words, selected, flags


def pinned_tree(root):
    def git(*args):
        command = ["git", "-c", f"safe.directory={root.as_posix()}", "-C", str(root),
                   "--no-optional-locks", *args]
        return subprocess.check_output(command, text=True, encoding="utf-8").strip()

    require(git("rev-parse", "HEAD") == REPRODUCER_COMMIT, "REPRODUCER_COMMIT_DRIFT")
    require(not git("status", "--porcelain=v1", "--untracked-files=all"), "DIRTY_REPRODUCER")
    data = {name: file_digest(root / "data" / name) for name in DATA_DIGESTS}
    require(data == DATA_DIGESTS, "CANONICAL_DATA_DIGEST_DRIFT")
    source = {
        path: file_digest(root / path)
        for path in git("ls-files", "src").splitlines()
    }
    return {"data": data, "source_sha256": digest(source)}


def control_inputs(result):
    return {
        "seed": result.planet.resource_creation_seed,
        "atmosphere": [resource_word(item.resource) for item in result.atmospheric_occurrences],
        "rsgds": [
            [definition.form_id.numeric if definition is not None else 0
             for definition in (biome.pndt_rsgd, biome.biom_rsgd)]
            for biome in result.initial_biomes
        ],
    }


def freeze(root):
    root = root.resolve(strict=True)
    pins = pinned_tree(root)
    require("starfield_resource_reproducer" not in sys.modules, "REPRODUCER_ALREADY_IMPORTED")
    sys.path.insert(0, str(root / "src"))
    try:
        from starfield_resource_reproducer.load_data import load_production_data
        from starfield_resource_reproducer.product import generate_all_planets
        project = load_production_data(root / "data")
        generations = generate_all_planets(project)
    finally:
        sys.path.pop(0)
    require(not project.oracle, "VALIDATION_ORACLE_LEAKAGE")

    profile = control_authority()
    control_input_witnesses = {item["runtime"]: item["generation_inputs"] for item in profile["owners"]}
    input_sha256 = digest({
        "model_corpus": pins["data"],
        "winning_inputs": profile,
        "retail_qualification": "SRR-012 conditional base input and model parity assumptions",
    })
    ledger = build_ledger(project, input_sha256, profile)
    expected = {
        tuple(row["key"]): row for row in ledger["rows"] if row["status"] == "EXPECTED"
    }
    expected_owners = {key[0] for key in expected}
    predicted = []
    cap_cases = []
    screens = Counter()
    for form_id, result in sorted(generations.items()):
        owner = base_id(form_id.numeric) if form_id.numeric <= 0xFFFFFF else None
        words, selected, flags = screen_owner(result, project.ires_nodes)
        for flag in sorted(flags):
            screens[flag] += 1
        all_base_biomes = all(biome.form_id.numeric <= 0xFFFFFF for biome in result.initial_biomes)
        model_keys = {
            (owner, base_id(biome.form_id.numeric)) for biome in result.initial_biomes
        } if all_base_biomes else set()
        expected_keys = {key for key in expected if key[0] == owner}
        complete = (owner in expected_owners and control_inputs(result) == control_input_witnesses[form_id.numeric] and
                    model_keys == expected_keys and
                    all(expected[owner, base_id(biome.form_id.numeric)]["witness"]["authored_index"] ==
                        biome.index for biome in result.initial_biomes))
        for biome in result.initial_biomes:
            state = selected[biome.index]
            if state["word"] and state["count_before"] == 8:
                require(words[biome.index][5] == 0, "FULL_COUNT_SPECIAL_WRONG_SLOT")
                cap_cases.append({
                    "extract_key": [str(form_id), str(biome.form_id)],
                    **state, "native_slot": 0,
                })
            if complete and not flags:
                predicted.append({
                    "key": [owner, base_id(biome.form_id.numeric)],
                    "slots": [base_id(word) if word else None for word in words[biome.index]],
                    "applicability": "CONDITIONAL",
                    "reason": "Whole-model owner passed screens under pinned base input assumptions.",
                })

    oracle = {
        "schema": ORACLE,
        "reproducer_commit": REPRODUCER_COMMIT,
        "retail_sha256": RETAIL_SHA256,
        "input_sha256": input_sha256,
        "ledger_sha256": digest(ledger),
        "rows": sorted(predicted, key=lambda row: row["key"]),
    }
    require(pinned_tree(root) == pins, "REPRODUCER_CHANGED_DURING_FREEZE")
    receipt = {
        "schema": FREEZE,
        "oracle_sha256": digest(oracle),
        "ledger_sha256": digest(ledger),
        "reproducer_commit": REPRODUCER_COMMIT,
        "projection_sha256": file_digest(Path(__file__)),
        "ledger_source_sha256": file_digest(Path(__file__).with_name("ledger.py")),
        "authored_profile_sha256": digest(profile),
        "pins": pins,
        "special_at_eight": sorted(cap_cases, key=lambda row: row["extract_key"]),
        "screened_owners": len(generations),
        "screen_failure_counts": dict(sorted(screens.items())),
    }
    return ledger, oracle, receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reproducer", type=Path)
    parser.add_argument("out", type=Path, help="New output directory in private experiment custody")
    args = parser.parse_args()
    sys.dont_write_bytecode = True
    ledger, oracle, receipt = freeze(args.reproducer)
    args.out.mkdir()
    for filename, payload in (("ledger", ledger), ("oracle", oracle), ("freeze", receipt)):
        (args.out / f"{filename}.json").write_text(
            json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n",
            encoding="utf-8", newline="\n",
        )
    print(json.dumps({
        "joinable_ledger_rows": len(ledger["rows"]),
        "unresolved_candidate_identities": len(ledger["unresolved_candidates"]),
        "ledger_owners": len(ledger["owners"]) + len(ledger["unresolved_owners"]),
        "oracle_rows": len(oracle["rows"]), "oracle_sha256": receipt["oracle_sha256"],
        "ledger_sha256": receipt["ledger_sha256"], "special_at_eight": len(receipt["special_at_eight"]),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
