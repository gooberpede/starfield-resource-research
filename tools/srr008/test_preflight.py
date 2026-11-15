"""Synthetic integration controls for the self-contained SRR-008 tooling."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

CLI = Path(__file__).with_name("preflight.py")
SAVE = "Save1_DEADBEEFM4142_000100_20261012010203_1_0_4.sfs"
AUTO = "Autosave1_DEADBEEFM4142_000100_20261012010203_1_0_4.sfs"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def put(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return path


class PreflightTests(unittest.TestCase):
    def setUp(self):
        # Test payloads are synthetic. No installed Starfield or sibling inputs.
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        docs = self.docs = self.root / "Documents"
        steam = self.root / "Steam"
        profile = steam / "userdata/123"
        remote = profile / "1716740/remote/Saves"
        self.backup = self.root / "backup"
        game = steam / "steamapps/common/Starfield"
        put(docs / "Saves/Chosen.sfs", b"synthetic designated")
        put(docs / "Saves" / AUTO, b"synthetic transient")
        put(remote / SAVE, b"synthetic manual")
        put(self.backup / "Chosen.sfs", b"synthetic designated")
        put(self.backup / SAVE, b"synthetic manual")
        put(game / "Starfield.exe", b"synthetic executable fingerprint")
        put(steam / "steamapps/appmanifest_1716740.acf",
            b'"AppState" { "appid" "1716740" "buildid" "123" "StateFlags" "4" "installdir" "Starfield" }')
        self.overlay = put(profile / "config/localconfig.vdf",
                           b'"UserLocalConfigStore" { "apps" { "1716740" { "OverlayAppEnable" "0" } } }')
        put(profile / "7/remote/sharedconfig.vdf",
            b'"UserRoamingConfigStore" { "Software" { "Valve" { "Steam" { '
            b'"apps" { "1716740" { "cloudenabled" "0" } } } } } }')
        put(profile / "1716740/remotecache.vdf", b"synthetic cache")
        policy = {"schema": "sor-save-protection/1", "native_build": "1.16.244.0", "classified": {},
                  "designated": {"Chosen.sfs": {"bytes": len(b"synthetic designated"),
                                               "sha256": sha(b"synthetic designated"), "evidence": "fixture"}}}
        raw = json.dumps(policy).encode()
        policy_path = put(self.root / "policy.json", raw)
        self.config = self.root / "local-settings.json"
        self.settings = {
            "schema": "srr-save-environment/1", "documents_root": str(docs), "documents_save_directory": "Saves",
            "steam_root": str(steam), "steam_profile": str(profile), "backup_root": str(self.backup),
            "policy": str(policy_path), "policy_sha256": sha(raw), "native_build": "1.16.244.0",
            "expected_protected_counts": {"documents": 1, "remote": 1},
            "expected_game_sha256": sha(b"synthetic executable fingerprint"), "expected_steam_build": "123",
            "additional_configuration": [], "documents_data_target": None,
        }
        self.update_config()

    def update_config(self):
        self.config.write_text(json.dumps(self.settings), encoding="utf-8")

    def cli(self, mode="protection", output="receipt"):
        result = subprocess.run([sys.executable, "-E", "-B", str(CLI), mode, "--config", str(self.config),
                                 "--output", str(self.root / output)], capture_output=True, text=True)
        path = self.root / output / "receipt.json"
        return result.returncode, json.loads(path.read_bytes()) if path.exists() else None, result.stderr

    def test_success_and_refuse_overwrite(self):
        code, data, errors = self.cli()
        self.assertEqual((code, errors), (0, ""))
        self.assertTrue(data["ok"] and data["designations"]["Chosen.sfs"])
        self.assertEqual(data["documents"]["counts"], {"PROTECTED": 1, "TRANSIENT": 1})
        self.assertEqual(data["remote"]["matched"], 1)
        code, same, errors = self.cli()
        self.assertEqual(code, 2)
        self.assertIn("Output already exists", errors)
        self.assertEqual(same, data)

    def test_same_size_hash_mismatch_fails(self):
        put(self.backup / SAVE, b"Synthetic manual")
        code, data, _ = self.cli()
        self.assertEqual(code, 1)
        self.assertFalse(data["ok"] or data["remote"]["pairs"][0]["match"])

    def test_missing_backup_and_wrong_designation_fail(self):
        (self.backup / SAVE).unlink()
        altered = b"different but equally backed"
        put(self.docs / "Saves/Chosen.sfs", altered)
        put(self.backup / "Chosen.sfs", altered)
        code, data, _ = self.cli()
        self.assertEqual(code, 1)
        self.assertFalse(data["designations"]["Chosen.sfs"])
        self.assertIsNone(data["remote"]["pairs"][0]["candidate"])

    def test_missing_config(self):
        self.config.unlink()
        self.assertEqual(self.cli()[:2], (2, None))

    def test_wrong_namespace(self):
        put(self.docs / "Other/Chosen.sfs", b"synthetic designated")
        self.settings["documents_save_directory"] = "Other"
        self.update_config()
        code, receipt, errors = self.cli()
        self.assertEqual((code, receipt), (2, None))
        self.assertIn("effective save-directory", errors)

    def test_output_inside_input_root_fails(self):
        self.assertEqual(self.cli(output="Documents/Saves/new")[:2], (2, None))
        self.assertEqual(self.cli(output="Documents./Saves/new")[:2], (2, None))
        target = self.root / "read-only-configuration-target"
        target.mkdir()
        self.settings["documents_data_target"] = str(target)
        self.update_config()
        self.assertEqual(self.cli("environment", "read-only-configuration-target/new")[:2], (2, None))

    def test_unclassified_and_other_are_failures(self):
        put(self.docs / "Saves/unknown.sfs", b"ambiguous")
        put(self.docs / "Saves/notes.txt", b"unexpected")
        code, data, _ = self.cli()
        self.assertEqual(code, 1)
        self.assertEqual(data["documents"]["counts"]["UNCLASSIFIED"], 1)
        self.assertEqual(data["documents"]["other"], ["notes.txt"])

    def test_wrong_policy_version_fails(self):
        raw = Path(self.settings["policy"]).read_bytes().replace(b"sor-save-protection/1", b"sor-save-protection/2")
        put(Path(self.settings["policy"]), raw)
        self.settings["policy_sha256"] = sha(raw)
        self.update_config()
        self.assertEqual(self.cli()[:2], (2, None))

    def test_hard_link_is_not_independent(self):
        (self.backup / "Chosen.sfs").unlink()
        os.link(self.docs / "Saves/Chosen.sfs", self.backup / "Chosen.sfs")
        code, data, _ = self.cli()
        self.assertEqual(code, 1)
        self.assertFalse(data["documents"]["pairs"][0]["match"])

    def test_environment_checks_on_disk_app_settings(self):
        code, data, _ = self.cli("environment")
        self.assertEqual(code, 0)
        self.assertEqual((data["cloud_flag"], data["overlay_flag"]), ("0", "0"))
        prior = self.overlay.read_bytes()
        put(self.overlay, prior + prior.replace(b'"0"', b'"1"'))
        code, data, _ = self.cli("environment", "ambiguous")
        self.assertEqual(code, 1)
        self.assertIsNone(data["overlay_flag"])
        put(self.overlay, b'"UserLocalConfigStore" { "apps" { '
            b'"1716740" { "OverlayAppEnable" "0" } '
            b'"1716740" { "OverlayAppEnable" "1" "extra" { "x" "y" } } } }')
        code, data, _ = self.cli("environment", "ambiguous-nested")
        self.assertEqual(code, 1)
        self.assertIsNone(data["overlay_flag"])
        put(self.overlay, prior.replace(b"UserLocalConfigStore", b"Unrelated"))
        code, data, _ = self.cli("environment", "outside-setting-store")
        self.assertEqual(code, 1)
        self.assertIsNone(data["overlay_flag"])


if __name__ == "__main__":
    unittest.main()
