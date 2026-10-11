import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("build_run", ROOT / "scripts/build/run.py")
build_run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_run)

class BuildTests(unittest.TestCase):
    def test_swift_path(self):
        p = build_run.resolve_project(ROOT, "fixtures/swift-smoke", "swift-package")
        self.assertTrue((p / "Package.swift").is_file())
    def test_escape_rejected(self):
        with self.assertRaises(ValueError):
            build_run.resolve_project(ROOT, "../", "swift-package")
    def test_absolute_rejected(self):
        with self.assertRaises(ValueError):
            build_run.resolve_project(ROOT, "/tmp", "swift-package")
    def test_missing_scheme_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "Example.xcodeproj").mkdir()
            env = {"XB_PROJECT_KIND": "xcode-project", "XB_SOURCE_PATH": "Example.xcodeproj",
                   "XB_SCHEME": "", "XB_DESTINATION": "generic/platform=iOS Simulator"}
            with self.assertRaises(ValueError):
                build_run.build_command("build", d, env)
    def test_swift_command_no_shell(self):
        env = {"XB_PROJECT_KIND": "swift-package", "XB_SOURCE_PATH": "fixtures/swift-smoke"}
        cmd = build_run.build_command("test", ROOT, env)
        self.assertEqual(cmd[:2], ["swift", "test"])
        self.assertNotIn("sh", cmd)
