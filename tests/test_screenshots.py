import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
GENERATE = ROOT / "scripts/screenshots/generate_fixture.py"
VALIDATOR = ROOT / "scripts/screenshots/validate.py"
MANIFEST = ROOT / "fixtures/screenshots/manifest.json"

class ScreenshotTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        subprocess.run([sys.executable, str(GENERATE), str(self.dir)], check=True)
    def validate(self, manifest=MANIFEST):
        return subprocess.run([sys.executable, str(VALIDATOR), "--root", str(self.dir),
                               "--manifest", str(manifest), "--report", str(self.dir.parent / "report.json")],
                              capture_output=True, text=True)
    def test_valid_three_named_states(self):
        proc = self.validate()
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertEqual(json.loads(proc.stdout)["count"], 3)
    def test_missing_filename(self):
        (self.dir / "factory-offline.png").unlink()
        self.assertNotEqual(self.validate().returncode, 0)
    def test_extra_file(self):
        (self.dir / "extra.png").write_bytes((self.dir / "factory-offline.png").read_bytes())
        self.assertNotEqual(self.validate().returncode, 0)
    def test_duplicate_content(self):
        (self.dir / "vpn-no-profile.png").write_bytes((self.dir / "factory-offline.png").read_bytes())
        self.assertNotEqual(self.validate().returncode, 0)
    def test_invalid_png(self):
        (self.dir / "factory-offline.png").write_text("not png")
        self.assertNotEqual(self.validate().returncode, 0)
    def test_missing_required_state(self):
        payload = json.loads(MANIFEST.read_text())
        payload["required_states"].append("wireguard-connected")
        custom = self.dir.parent / "extra-states.json"
        custom.write_text(json.dumps(payload))
        self.assertNotEqual(self.validate(custom).returncode, 0)
    def test_unsafe_manifest(self):
        payload = json.loads(MANIFEST.read_text())
        payload["shots"][0]["file"] = "../outside.png"
        custom = self.dir.parent / "bad.json"
        custom.write_text(json.dumps(payload))
        self.assertNotEqual(self.validate(custom).returncode, 0)
