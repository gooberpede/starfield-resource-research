# SPDX-License-Identifier: GPL-3.0-or-later
"""Read-only SRR-008/009 save protection and on-disk environment checks."""

import argparse
from collections import Counter
import ctypes
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys

import save_policy

APP_ID = "1716740"
FLOOR = 40_000_000_000
RESERVE = 134_217_728
INI_NAMES = ("Starfield.ini", "StarfieldCustom.ini", "StarfieldPrefs.ini")
HEX_256 = re.compile(r"[0-9a-f]{64}")


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def distinct_keys(pairs):
    result = {}
    for name, value in pairs:
        require(name not in result, f"Duplicate JSON key: {name}")
        result[name] = value
    return result


def identity(file_stat):
    return file_stat.st_dev, file_stat.st_ino, file_stat.st_size, file_stat.st_mtime_ns


def checked_stat(path):
    info = path.lstat()
    require(not stat.S_ISLNK(info.st_mode) and not getattr(info, "st_file_attributes", 0) & 0x400,
            f"Link/reparse point: {path}")
    return info


def safe_path(path):
    require(path.is_absolute() and ".." not in path.parts, f"Expected an absolute normalized path: {path}")
    for part in (*reversed(path.parents), path):
        checked_stat(part)
    return path


def read_file(path, content=False):
    before = checked_stat(path)
    require(stat.S_ISREG(before.st_mode), f"Not a regular file: {path}")
    with path.open("rb") as stream:
        opened = os.fstat(stream.fileno())
        if content:
            require(opened.st_size <= 16 * 1024**2, f"Config file too large: {path}")
            data = stream.read(16 * 1024**2 + 1)
            require(len(data) == opened.st_size, f"Config file size changed: {path}")
            digest = hashlib.sha256(data).hexdigest()
        else:
            data = None
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        after = os.fstat(stream.fileno())
    require(identity(before) == identity(opened) == identity(after) == identity(checked_stat(path)),
            f"File changed during read: {path}")
    return dict(volume=opened.st_dev, file_id=opened.st_ino, size=opened.st_size, sha256=digest), data


def read_json(path):
    pin, raw = read_file(safe_path(path), content=True)
    return json.loads(raw.decode("utf-8-sig"), object_pairs_hook=distinct_keys), pin


def tree(path):
    for entry in sorted(path.iterdir()):
        info = checked_stat(entry)
        if stat.S_ISDIR(info.st_mode):
            yield from tree(entry)
        else:
            require(stat.S_ISREG(info.st_mode), f"Unsupported namespace entry: {entry}")
            yield entry


def absolute(value):
    path = Path(value)
    require(path.is_absolute() and ".." not in path.parts, f"Expected absolute path: {path}")
    if os.name == "nt":
        require(len(path.drive) == 2 and path.drive[1] == ":", f"Expected local drive path: {path}")
        require(not any(os.path.isreserved(part) for part in path.parts[1:]), f"Reserved path component: {path}")
    return path


def directory(path):
    require(safe_path(path).is_dir(), f"Directory unavailable: {path}")
    return path.resolve(strict=True)


def has_overlap(a, b):
    return a.is_relative_to(b) or b.is_relative_to(a)


def read_config(path):
    cfg, _ = read_json(absolute(path.absolute()))
    require(set(cfg) == {"schema", "documents_root", "documents_save_directory", "steam_root",
                         "steam_profile", "backup_root", "policy", "policy_sha256", "native_build",
                         "expected_protected_counts", "expected_game_sha256", "expected_steam_build",
                         "additional_configuration", "documents_data_target"}, "Invalid configuration fields")
    require(cfg["schema"] == "srr-save-environment/1", "Unexpected configuration version")
    for key in ("policy_sha256", "expected_game_sha256"):
        require(isinstance(cfg[key], str) and HEX_256.fullmatch(cfg[key]), f"Invalid {key}")
    for key in ("documents_root", "steam_root", "steam_profile", "backup_root"):
        cfg[key] = directory(absolute(cfg[key]))
    require(cfg["steam_profile"].parent == cfg["steam_root"] / "userdata" and
            cfg["steam_profile"].name.isascii() and cfg["steam_profile"].name.isdecimal(),
            "Steam profile is outside the configured userdata namespace")
    require(isinstance(cfg["additional_configuration"], list), "Invalid additional_configuration")
    cfg["additional_configuration"] = [absolute(value) for value in cfg["additional_configuration"]]
    cfg["policy"] = absolute(cfg["policy"])
    if cfg["documents_data_target"] is not None:
        cfg["documents_data_target"] = directory(absolute(cfg["documents_data_target"]))
    name = cfg["documents_save_directory"]
    require(isinstance(name, str) and re.fullmatch(r"[^/\\:]+", name) and name not in {".", ".."},
            "Expected a single Documents save-directory name")
    cfg["documents"] = directory(cfg["documents_root"] / name)
    cfg["remote"] = directory(cfg["steam_profile"] / APP_ID / "remote/Saves")
    roots = [cfg[k] for k in ("documents", "remote", "backup_root")]
    require(not any(has_overlap(a, b) for i, a in enumerate(roots) for b in roots[i + 1:]),
            "Save and backup roots must be separate")
    counts = cfg["expected_protected_counts"]
    require(set(counts) == {"documents", "remote"} and all(type(n) is int and n > 0 for n in counts.values()),
            "Each namespace requires a positive protected-pair count")
    for field in ("native_build", "expected_steam_build"):
        require(isinstance(cfg[field], str) and bool(cfg[field]), f"Missing {field}")
    return cfg


def load_policy(cfg):
    policy, pin = read_json(cfg["policy"])
    require(pin["sha256"] == cfg["policy_sha256"], "Private policy content pin differs")
    require(set(policy) == {"schema", "native_build", "designated", "classified"} and
            policy["schema"] == "sor-save-protection/1" and policy["native_build"] == cfg["native_build"] == "1.16.244.0",
            "Unsupported save-policy schema or native grammar")
    mapped = set()
    for group in ("designated", "classified"):
        require(isinstance(policy[group], dict), f"Invalid {group} rules")
        for name, rule in policy[group].items():
            require(re.fullmatch(r"[^/\\:]+\.sfs", name, re.I) and name.casefold() not in mapped,
                    "Invalid or ambiguous policy basename")
            mapped.add(name.casefold())
            require(isinstance(rule["evidence"], str) and rule["evidence"].strip(), "Policy provenance missing")
            if group == "designated":
                require(type(rule["bytes"]) is int and rule["bytes"] > 0 and HEX_256.fullmatch(rule["sha256"]),
                        "Invalid designation identity")
            else:
                require(rule["kind"] in save_policy.KINDS.values(), "Invalid explicit classification")
    require(bool(policy["designated"]), "No protected research designations")
    return policy, pin


def check_namespace(path, candidates, policy, expected):
    counts, pairs, other, transient, seen = Counter(), [], [], {}, set()
    for file in tree(path):
        relative = file.relative_to(path).as_posix()
        require(relative.casefold() not in seen, f"Case-colliding save entry: {relative}")
        seen.add(relative.casefold())
        if file.suffix.lower() != ".sfs":
            other.append(relative)
            continue
        protection = save_policy.classify(relative, policy)["protection"]
        counts[protection] += 1
        if protection == "TRANSIENT":
            item = checked_stat(file)
            transient[relative] = dict(file_id=item.st_ino, size=item.st_size, mtime_ns=item.st_mtime_ns)
            continue
        original, _ = read_file(file)
        backup = candidates.get(file.name.casefold())
        counterpart = read_file(backup)[0] if backup else None
        match = bool(counterpart
                     and (original["volume"], original["file_id"]) != (counterpart["volume"], counterpart["file_id"])
                     and (original["size"], original["sha256"]) == (counterpart["size"], counterpart["sha256"]))
        pairs.append(dict(relative=relative, original=original, candidate=counterpart, match=match))
    matched = sum(row["match"] for row in pairs)
    ok = not other and not counts["UNCLASSIFIED"] and matched == expected == len(pairs) == counts["PROTECTED"]
    return dict(path=str(path), counts=dict(counts), pairs=pairs, other=other, transient=transient,
                matched=matched, expected_protected=expected, ok=ok)


def protection(cfg):
    policy, policy_pin = load_policy(cfg)
    _, _, path_agrees = configuration(cfg, cfg["steam_root"] / "steamapps/common/Starfield")
    require(path_agrees, "Configured Documents root does not match the effective save-directory setting")
    backup = cfg["backup_root"]
    candidates = {}
    entries = list(tree(backup))
    for file in entries:
        if file.parent == backup:
            key = file.name.casefold()
            require(key not in candidates, "Ambiguous backup basename")
            candidates[key] = file
    checks = {key: check_namespace(cfg[key], candidates, policy, cfg["expected_protected_counts"][key])
              for key in ("documents", "remote")}
    designations = {name: any(row["relative"] == name and row["match"]
                             and (row["original"]["size"], row["original"]["sha256"]) == (rule["bytes"], rule["sha256"])
                             for row in checks["documents"]["pairs"])
                    for name, rule in policy["designated"].items()}
    ok = all(row["ok"] for row in checks.values()) and all(designations.values())
    return dict(ok=ok, **checks, designations=designations, backup_entry_count=len(entries),
                backup_path=str(backup), policy_file_sha256=policy_pin["sha256"], policy_digest=save_policy.policy_hash(policy))


def available_bytes():
    require(os.name == "nt", "Drive guard requires Windows")
    api = ctypes.windll.kernel32.GetDiskFreeSpaceExW
    api.argtypes = (ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_ulonglong), ctypes.c_void_p, ctypes.c_void_p)
    available = {}
    for drive in ("C", "D"):
        free = ctypes.c_ulonglong()
        require(api(drive + ":\\", ctypes.byref(free), None, None), f"Could not read available space on {drive}:")
        available[drive] = free.value
    require(all(value - RESERVE >= FLOOR for value in available.values()), "Insufficient disk space after reserve")
    return available


def disk_text(path):
    pin, data = read_file(safe_path(path), content=True)
    return pin, data.decode("utf-8-sig", errors="strict")


VDF_TOKEN = re.compile(r'//[^\n]*|"(?:[^"\\]|\\.)*"|[{}]|[^"{}\s]+|\s+')


def vdf(text):
    """Read ordinary Steam KeyValues while retaining duplicate and nested keys."""
    position = 0
    tokens = []
    for token in VDF_TOKEN.finditer(text):
        require(token.start() == position, "Invalid Steam configuration token")
        position = token.end()
        value = token.group()
        if not value.isspace() and not value.startswith("//"):
            tokens.append(value)
    require(position == len(text), "Incomplete Steam configuration token")
    stream = iter(tokens)

    def pairs(depth):
        require(depth < 64, "Steam configuration nesting limit")
        output = []
        for name in stream:
            if name == "}":
                require(depth > 0, "Unexpected Steam configuration closing brace")
                return output
            require(name != "{", "Missing Steam configuration key")
            value = next(stream, None)
            require(value not in {None, "}"}, "Missing Steam configuration value")
            output.append((name.strip('"'), pairs(depth + 1) if value == "{" else value.strip('"')))
        require(depth == 0, "Unclosed Steam configuration block")
        return output

    return pairs(0)


def vdf_value(tree, *path):
    """Look up one unambiguous KeyValues path, using Steam's case-insensitive keys."""
    for part in path:
        if not isinstance(tree, list):
            return None
        matches = [value for name, value in tree if name.casefold() == part.casefold()]
        if len(matches) != 1:
            return None
        tree = matches[0]
    return tree if isinstance(tree, str) else None


def namespace(path, optional=False):
    if optional:
        for part in (*reversed(path.parents), path):
            try:
                checked_stat(part)
            except FileNotFoundError:
                return {"path": str(path), "entries": [], "present": False}
    directory(path)
    result = []
    for item in sorted(path.iterdir()):
        info = checked_stat(item)
        result.append(dict(name=item.name, bytes=info.st_size, mtime_ns=info.st_mtime_ns,
                           directory=stat.S_ISDIR(info.st_mode)))
    return {"path": str(path), "entries": result, "present": True}


def configuration(cfg, game):
    configurations = []
    save_paths = []
    for path in [*(cfg["documents_root"] / name for name in INI_NAMES), game / "Starfield.ini",
                 *cfg["additional_configuration"]]:
        try:
            pin, data = disk_text(path)
        except FileNotFoundError:
            configurations.append({"path": str(path), "present": False})
            continue
        configurations.append({"path": str(path), "present": True, **pin})
        if path.suffix.casefold() == ".ini":
            save_paths.extend(re.findall(r"^\s*sLocalSavePath\s*=\s*([^\r\n]+)", data, re.M | re.I))
    path_agrees = (bool(save_paths) or cfg["documents_save_directory"].casefold() == "saves") and all(line.split(";", 1)[0].strip().strip('"').rstrip("/\\").casefold()
                      == cfg["documents_save_directory"].casefold() for line in save_paths)
    return configurations, save_paths, path_agrees


def environment(cfg):
    game = directory(cfg["steam_root"] / "steamapps/common/Starfield")
    retail, _ = read_file(game / "Starfield.exe")
    manifest, text = disk_text(cfg["steam_root"] / "steamapps/appmanifest_1716740.acf")
    app_state = vdf(text)
    fields = {key: vdf_value(app_state, "AppState", key)
              for key in ("appid", "buildid", "StateFlags", "installdir")}
    app = dict(appid=APP_ID, buildid=cfg["expected_steam_build"], StateFlags="4", installdir="Starfield")
    local, local_text = disk_text(cfg["steam_profile"] / "config/localconfig.vdf")
    shared, shared_text = disk_text(cfg["steam_profile"] / "7/remote/sharedconfig.vdf")
    cache, _ = read_file(safe_path(cfg["steam_profile"] / APP_ID / "remotecache.vdf"))
    cloud = vdf_value(vdf(shared_text), "UserRoamingConfigStore", "Software", "Valve", "Steam",
                      "apps", APP_ID, "cloudenabled")
    overlay = vdf_value(vdf(local_text), "UserLocalConfigStore", "apps", APP_ID, "OverlayAppEnable")
    configurations, save_paths, path_agrees = configuration(cfg, game)
    data = cfg["documents_root"] / "Data"
    target = cfg["documents_data_target"]
    if target is not None:
        info = data.lstat()
        require((stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400)
                and data.resolve(strict=True) == target, "Documents Data junction target differs")
        data = target
    sfse_dirs = {"install": namespace(game / "Data/SFSE/Plugins", optional=True),
                 "documents": namespace(data / "SFSE/Plugins", optional=True)}
    sfse_loader = (game / "sfse_loader.exe").exists() or (game / "sfse_loader.exe").is_symlink()
    installed = namespace(game)
    native_candidates = [entry for entry in installed["entries"]
                         if re.search(r"sfse|\.dll$", entry["name"], re.I)]
    return dict(ok=(retail["sha256"] == cfg["expected_game_sha256"] and fields == app and
                    cloud == overlay == "0" and path_agrees),
                retail_executable=retail, manifest=manifest, manifest_fields=fields, cloud_flag=cloud,
                overlay_flag=overlay, steam_files={"local": local, "shared": shared, "cache": cache},
                configurations=configurations, configured_save_paths=save_paths, configured_save_path_agrees=path_agrees,
                sfse_loader=sfse_loader, sfse_directories=sfse_dirs, native_candidates=native_candidates,
                documents=namespace(cfg["documents"]), remote=namespace(cfg["remote"]),
                limits="On-disk only. Effective account/session, process state, URI handler and NVIDIA overlay require separate checks.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("protection", "environment"))
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path, help="New private directory under an existing parent")
    args = parser.parse_args()
    try:
        require(sys.flags.ignore_environment and sys.dont_write_bytecode and not sys.flags.optimize,
                "Run with -E -B and no -O or -OO")
        cfg = read_config(args.config)
        output = absolute(args.output.absolute())
        output = directory(output.parent) / output.name
        for key in ("documents_root", "steam_root", "backup_root", "documents_data_target"):
            if cfg[key] is not None:
                require(not has_overlap(output, cfg[key]), "Output overlaps a protected input root")
        require(not output.exists() and not output.is_symlink(), "Output already exists")
        available = available_bytes()
        report = (protection if args.mode == "protection" else environment)(cfg)
        report.update(schema="srr-save-environment-receipt/1", mode=args.mode,
                      utc=datetime.now(timezone.utc).isoformat(), available_bytes=available,
                      floor_per_drive=FLOOR, reserve_per_drive=RESERVE)
        output.mkdir()
        with (output / "receipt.json").open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(report, stream, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        print(f"{args.mode}: {'PASS' if report['ok'] else 'FAILED'}")
        return 0 if report["ok"] else 1
    except (KeyError, OSError, TypeError, ValueError) as error:
        print(f"Input or evidence error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
