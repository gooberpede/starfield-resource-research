"""Resolve independently witnessed component submissions and model coverage."""

import hashlib
import json
import re


RETAIL_SHA256 = "7e9adb1414a8e1b325e5e1f097b9b17b78deb7eebeda37a333351a43a60f9d28"
REPRODUCER_COMMIT = "a8ff1c788bca415f571f06769ab3e712fa674f75"
LEDGER = "srr016-ledger-v1"
ORACLE = "srr016-oracle-v1"
OBSERVATION = "srr016-observation-v1"
FREEZE = "srr016-freeze-v1"
AUTHORED = "srr016-authored-operations-v1"
CONTROL_OWNERS = {
    0x3F59F: (0xD9BAC, 0x23C0CE, 0x2C9985),
    0x5DF7F: (0xC5717,),
}
CONTROL_GENERATION = {
    0x3F59F: {
        "seed": 2842708811,
        "atmosphere": [0x57F5],
        "rsgds": [[0, 0x83F0], [0x244CCB, 0x7EDD], [0x244CCC, 0x83EA]],
    },
    0x5DF7F: {"seed": 1633829920, "atmosphere": [], "rsgds": [[0x18CE00, 0x83E0]]},
}
CONTROL_SOURCE = "SRR-012-sample-plan.md#offline-reproduction"
BASE_MASTER_DIGEST = "1dabed00c3f4282dd3bb54d2e9601e40b577d8742d078b7ccef203adbfef0da7"
FORM_ID = re.compile(r"[^:/\\\x00-\x1f]+\.(?:esm|esl|esp):[0-9A-F]{6}")
SHA256 = re.compile(r"[a-f0-9]{64}")


def require(condition, detail):
    if not condition:
        raise ValueError(detail)


def digest(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                     allow_nan=False).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def file_digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def valid_digest(value):
    return isinstance(value, str) and SHA256.fullmatch(value) is not None


def identity(value):
    require(isinstance(value, str) and FORM_ID.fullmatch(value) and
            value.rsplit(":", 1)[0].lower() == value.rsplit(":", 1)[0],
            "INVALID_CANONICAL_FORMID")
    return value


def u32(value):
    require(type(value) is int and 0 <= value <= 0xFFFFFFFF, "INVALID_U32")
    return value


def base_id(word):
    require(0 < u32(word) <= 0xFFFFFF, "NON_BASE_FORMID")
    return f"starfield.esm:{word:06X}"


class IdentityMap:
    """One-to-one relation supplied by a separately attested mapping or typed witnesses."""

    def __init__(self):
        self.raw = {}
        self.canonical = {}

    def bind(self, word, form, kind):
        require(u32(word) != 0, "ZERO_FORMID")
        identity(form)
        require(self.raw.get(word, (form, kind)) == (form, kind) and
                self.canonical.get(form, (word, kind)) == (word, kind),
                "CONTRADICTORY_FORMID_REMAP")
        self.raw[word] = (form, kind)
        self.canonical[form] = (word, kind)
        return form

    def resolve(self, word, kind):
        match = self.raw.get(u32(word))
        require(match is not None and match[1] == kind, "UNRESOLVED_TYPED_FORMID")
        return match[0]


def control_authority():
    """Independent SRR-012 field corroboration, under a base-only conditional scope."""
    forms = [
        [word, base_id(word), kind]
        for owner, biomes in CONTROL_OWNERS.items()
        for word, kind in [(owner, "PNDT"), *((biome, "BIOM") for biome in biomes)]
    ]
    return {
        "schema": AUTHORED,
        "source": CONTROL_SOURCE,
        "source_sha256": BASE_MASTER_DIGEST,
        "forms": forms,
        "owners": [
            {
                "runtime": owner,
                "workset_closed": True,
                "scope": "Base winner; no later ENAM or CSV submissions in this profile.",
                "generation_inputs": CONTROL_GENERATION[owner],
                "operations": [
                    {
                        "route": "PPBD",
                        "admitted": True,
                        "runtime_biom": biome,
                        "authored_index": index,
                        "winning_plugin": "starfield.esm",
                        "winner_sha256": BASE_MASTER_DIGEST,
                    }
                    for index, biome in enumerate(biomes)
                ],
            }
            for owner, biomes in CONTROL_OWNERS.items()
        ],
    }


def resolve_authority(profile):
    """Fold scoped accepted submissions, preserving route and winner witnesses.

    The supplied operation order and guards need independent evidence. Unknown
    submissions invalidate the owner even when later rows appear well formed.
    """
    require(profile["schema"] == AUTHORED and valid_digest(profile["source_sha256"]) and
            bool(profile["source"]), "INVALID_AUTHORED_PROFILE")
    form_map = IdentityMap()
    seen_raw_forms = set()
    for word, form, kind in profile["forms"]:
        require(kind in {"PNDT", "BIOM"} and word not in seen_raw_forms,
                "INVALID_OR_DUPLICATE_AUTHORED_MAP_ENTRY")
        form_map.bind(word, form, kind)
        seen_raw_forms.add(word)

    owners = {}
    rows = {}
    for owner in profile["owners"]:
        owner_word = owner["runtime"]
        owner_id = form_map.resolve(owner_word, "PNDT")
        require(owner_id not in owners, "DUPLICATE_IDENTITY")
        closed = owner["workset_closed"]
        require(type(closed) is bool and bool(owner["scope"]), "INVALID_AUTHORED_SCOPE")
        live = {}
        seen = {}
        applied_clear = False
        ppbd_index = -1
        for ordinal, operation in enumerate(owner["operations"]):
            require(not ({"slots", "raw_slots", "acquisition"} & operation.keys()),
                    "OBSERVATION_FIELDS_IN_AUTHORED_PROFILE")
            route, admitted = operation["route"], operation["admitted"]
            require(route in {"PPBD", "ENAM_CLEAR", "ENAM_PPBD", "CSV"} and
                    (type(admitted) is bool or admitted is None) and
                    valid_digest(operation["winner_sha256"]) and
                    bool(operation["winning_plugin"]), "INVALID_AUTHORED_OPERATION")
            if admitted is None:
                closed = False
            if route == "ENAM_CLEAR":
                if admitted is True:
                    live.clear()
                    ppbd_index = -1
                    applied_clear = True
                continue
            biome = form_map.resolve(operation["runtime_biom"], "BIOM")
            if route == "ENAM_PPBD" and admitted is True:
                require(applied_clear, "ENAM_REPLACEMENT_WITHOUT_ADMITTED_CLEAR")
            if route != "CSV":
                index = operation["authored_index"]
                require(type(index) is int and index > ppbd_index, "INVALID_PPBD_ORDER")
                ppbd_index = index
            witness = {
                **operation,
                "ordinal": ordinal,
                "runtime_owner": owner_word,
            }
            if admitted is True:
                require(biome not in live, "AMBIGUOUS_DUPLICATE_SUBMISSION")
                live[biome] = witness
            seen.setdefault(biome, []).append(witness)
        owners[owner_id] = {
            "owner": owner_id,
            "status": ("EXPECTED" if live else "EXCLUDED") if closed else "UNKNOWN",
            "workset_closed": closed,
            "reason": owner["scope"],
            "source": profile["source"],
            "source_sha256": profile["source_sha256"],
            "operation_history": owner["operations"],
        }
        for biome, history in seen.items():
            status = ("EXPECTED" if biome in live else "EXCLUDED") if closed else "UNKNOWN"
            rows[owner_id, biome] = {
                "key": [owner_id, biome],
                "status": status,
                "source": profile["source"],
                "reason": {
                    "EXPECTED": "Admitted submission in the declared work set.",
                    "EXCLUDED": "Submission excluded or removed in the declared work set.",
                    "UNKNOWN": "Owner operation coverage or admission unresolved.",
                }[status],
                "witness": live.get(biome, history[-1]),
                "operation_history": history,
            }
    return owners, rows


def build_ledger(project, input_sha256, profile):
    owners, rows = resolve_authority(profile)
    unresolved_owners = []
    unresolved_candidates = []
    for form_id, directory in project.planet_directory.items():
        planet = project.planets.get(form_id)
        owner = base_id(form_id.numeric) if form_id.numeric <= 0xFFFFFF else None
        if owner is None:
            unresolved_owners.append({
                "extract_owner": str(form_id),
                "reported_source_file": directory.source_file,
                "status": "UNKNOWN",
                "reason": "SOURCE_NAMESPACE_UNATTESTED",
                "has_model_rows": planet is not None,
            })
        elif owner not in owners:
            owners[owner] = {
                "owner": owner,
                "status": "UNKNOWN",
                "workset_closed": False,
                "reason": "MODEL_ONLY_WORKSET" if planet else "DIRECTORY_ONLY_OWNER",
                "source": "planet-resource-generation.csv" if planet else "planet-directory.csv",
            }
        if planet is None:
            continue
        for model_biome in planet.biomes:
            form_word = model_biome.form_id.numeric
            if owner is None or form_word > 0xFFFFFF:
                unresolved_candidates.append({
                    "extract_owner": str(form_id),
                    "extract_biom": str(model_biome.form_id),
                    "model_authored_index": model_biome.index,
                    "status": "UNKNOWN",
                    "reason": "SOURCE_NAMESPACE_UNATTESTED",
                })
                continue
            biome = base_id(form_word)
            key = owner, biome
            if key not in rows:
                rows[key] = {
                    "key": list(key),
                    "status": "EXCLUDED" if owners[owner]["workset_closed"] else "UNKNOWN",
                    "source": owners[owner]["source"],
                    "reason": ("Outside closed authored work set." if owners[owner]["workset_closed"]
                               else "Model row alone does not establish component submission."),
                }
            rows[key]["model_authored_index"] = model_biome.index
    return {
        "schema": LEDGER,
        "retail_sha256": RETAIL_SHA256,
        "input_sha256": input_sha256,
        "scope": "CONDITIONAL",
        "owners": [owners[key] for key in sorted(owners)],
        "rows": [rows[key] for key in sorted(rows)],
        "unresolved_owners": sorted(unresolved_owners, key=lambda row: row["extract_owner"]),
        "unresolved_candidates": sorted(
            unresolved_candidates,
            key=lambda row: (row["extract_owner"], row["model_authored_index"]),
        ),
    }
