import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]

class RegistryTests(unittest.TestCase):
    def test_registry_validation(self):
        subprocess.run([sys.executable, str(ROOT / "scripts/preflight/validate_repo.py")], check=True)
    def test_all_project_references_have_profiles(self):
        reg = json.loads((ROOT / "registry/projects.json").read_text())
        for project in reg["projects"]:
            self.assertTrue((ROOT / "profiles" / (project["profile"] + ".json")).is_file())
    def test_real_app_disabled(self):
        reg = json.loads((ROOT / "registry/projects.json").read_text())
        self.assertFalse(next(x for x in reg["projects"] if x["id"] == "ios-next")["enabled"])
