import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "scripts/artifacts/index.py"

class ArtifactTests(unittest.TestCase):
    def test_sha256_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            (path / "src").mkdir()
            (path / "src" / "hello.log").write_text("hello")
            output = path / "index.json"
            subprocess.run([sys.executable, str(INDEX), "--root", str(path / "src"),
                            "--output", str(output)], check=True)
            data = json.loads(output.read_text())
            self.assertEqual(data["count"], 1)
            self.assertEqual(len(data["files"][0]["sha256"]), 64)
    def test_empty_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = subprocess.run([sys.executable, str(INDEX), "--root", tmp,
                                   "--output", str(Path(tmp) / "index.json")])
            self.assertNotEqual(proc.returncode, 0)
    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            src.mkdir()
            (src / "linked").symlink_to("/etc/hosts")
            proc = subprocess.run([sys.executable, str(INDEX), "--root", str(src),
                                   "--output", str(Path(tmp) / "index.json")])
            self.assertNotEqual(proc.returncode, 0)
