"""Audit the pinned production corpus and replay the SRR-012 control projection.

Run with the sibling reproducer's src on PYTHONPATH and pass its data path.
Read four production CSVs and write diagnostics to stdout only. This probe
follows recorded model rolls. It does not simulate a divergent native run.
"""

import argparse
from collections import defaultdict
from pathlib import Path
import struct

from starfield_resource_reproducer.diagnostics import EventKind
from starfield_resource_reproducer.domain import GenerationRarity
from starfield_resource_reproducer.load_data import load_production_data
from starfield_resource_reproducer.product import audit_biome_identities, generate_all_planets


CONTROLS = {
    ("0003F59F", "000D9BAC"): (0x57EA, 0, 0, 0x57E9, 0, 0, 0x83EC),
    ("0003F59F", "0023C0CE"): (0x57C7, 0x57C9, 0, 0, 0, 0, 0),
    ("0003F59F", "002C9985"): (0x57C1, 0x57C3, 0, 0, 0, 0, 0),
    ("0005DF7F", "000C5717"): (0x57EB, 0x57EC, 0, 0, 0x5DF8, 0x57F5, 0),
}


def binary32(value):
    return struct.unpack("<f", struct.pack("<f", value))[0]


def resource_id(resource):
    return resource.form_id.numeric if resource is not None else 0


def entry_ids(definition, rarity):
    if definition is None:
        return ()
    return tuple(
        entry.resource_form_id.numeric
        for entry in definition.entries
        if entry.resource_rarity is rarity
    )


def scan_selector(definitions, rarity, roll):
    """Replay just the finite, well-formed singleton-list branch."""
    cumulative = 0.0
    for definition in definitions:
        for entry in definition.entries:
            if entry.resource_rarity is not rarity:
                continue
            weight = entry.common_chance if rarity is GenerationRarity.COMMON else entry.special_chance
            cumulative = binary32(cumulative + binary32(binary32(float(weight)) * binary32(0.01)))
            if roll < cumulative:
                return entry
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", type=Path)
    project = load_production_data(parser.parse_args().data)
    identities = audit_biome_identities(project.planets.values())
    generations = generate_all_planets(project)
    print(
        f"directory={len(project.planet_directory)} modeled={len(project.planets)} "
        f"directory_only={len(project.planet_directory.keys() - project.planets.keys())}"
    )
    print(f"candidate_rows={sum(len(result.biome_results) for result in generations.values())}")
    print(f"duplicate_biome_formid_groups={len(identities.repeated_form_id_groups)}")
    flags = defaultdict(set)
    controls = {}
    for owner, result in sorted(generations.items(), key=lambda item: item[0].numeric):
        owner_id = str(owner)
        ordered = tuple(str(biome.form_id) for biome in result.initial_biomes)
        if ordered != tuple(sorted(ordered)):
            flags["authored_order_differs_from_base_key_sort"].add((owner_id,))

        biomes_by_index = {biome.index: biome for biome in result.initial_biomes}
        occupied = 0
        occupied_ids = set()
        special = {}
        for event in result.events:
            if event.kind is EventKind.RESOURCE_OCCURRENCE_RECORDED:
                occupied = event["occupied_count_after"]
                if event["accepted"]:
                    occupied_ids.add(resource_id(event["resource"]))
            if event.kind not in {EventKind.SPECIAL_PASS_RESULT, EventKind.COMMON_ROLL}:
                continue
            rarity = event["category"]
            biome = biomes_by_index[event["biome_index"]]
            key = (owner_id, str(biome.form_id))
            primary = scan_selector((biome.effective_rsgd,), rarity, event["roll"])
            observed_selection = resource_id(event["selected_resource"])
            if resource_id(primary.resource if primary else None) != observed_selection:
                flags["binary32_primary_changes_selected_id_on_model_roll"].add(key)
            if primary is None and biome.pndt_rsgd is not None and biome.biom_rsgd is not None:
                retry = scan_selector((biome.pndt_rsgd, biome.biom_rsgd), rarity, event["roll"])
                if retry is not None:
                    flags["biom_retry_selects_after_primary_miss_on_model_roll"].add(key)
            if event.kind is EventKind.SPECIAL_PASS_RESULT:
                special[biome.index] = observed_selection if occupied < 8 else 0
                if observed_selection and occupied >= 8:
                    flags["selected_special_at_full_model_count"].add(key)
                    if observed_selection in occupied_ids:
                        flags["duplicate_special_accepted_at_full_model_count"].add(
                            (*key, f"{observed_selection:08X}")
                        )

        for row in result.biome_results:
            biome = row.orchestration.biome
            key = (owner_id, str(biome.form_id))
            model_everywhere = entry_ids(biome.effective_rsgd, GenerationRarity.EVERYWHERE)
            biom_everywhere = entry_ids(biome.biom_rsgd, GenerationRarity.EVERYWHERE)
            if model_everywhere != biom_everywhere[:1]:
                flags["everywhere_candidate_sequence_differs"].add(key)
            if row.common_assignment.guard_reason is not None:
                model_roots = entry_ids(biome.effective_rsgd, GenerationRarity.COMMON)
                biom_roots = entry_ids(biome.biom_rsgd, GenerationRarity.COMMON)
                if model_roots != biom_roots:
                    flags["guard_common_candidate_sequence_differs"].add(key)
            if key not in CONTROLS:
                continue
            family = row.common_assignment.family
            assert family is not None and row.common_assignment.guard_reason is None
            slots = (
                resource_id(family.root),
                *(resource_id(level.selected_candidate) if level.emitted else 0 for level in family.levels),
                special[biome.index],
                (biom_everywhere or (0,))[0],
            )
            controls[key] = slots
            print(owner_id, key[1], *(f"{word:08X}" for word in slots))

    assert controls == CONTROLS, controls
    for reason in sorted(flags):
        print(f"{reason}={len(flags[reason])} first={':'.join(min(flags[reason]))}")
    print("Control assertions passed.")


if __name__ == "__main__":
    main()
