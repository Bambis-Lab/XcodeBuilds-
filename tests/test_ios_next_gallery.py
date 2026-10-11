"""Synthetic, deterministic XB-05 negative and positive screenshot validation."""
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import struct
import tempfile
import unittest
import zlib

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "xb05_gallery", ROOT / "scripts/integrations/ios-next/verify_gallery.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)

def chunk(name, payload):
    raw = name + payload
    return struct.pack(">I", len(payload)) + raw + struct.pack(">I", zlib.crc32(raw) & 0xffffffff)

def make_png(seed):
    rng = random.Random(seed)
    w, h = 160, 160
    body = b"".join(b"\\x00" + rng.randbytes(w*3) for _ in range(h))
    return (b"\\x89PNG\\r\\n\\x1a\\n" +
            chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) +
            chunk(b"IDAT", zlib.compress(body)) + chunk(b"IEND", b""))

class XB05GalleryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        images = []
        for index, (appearance, label) in enumerate(
            (a, l) for a in ("light", "dark") for l in sorted(MOD.EXPECTED)
        ):
            rel = f"{appearance}/{label}.png"
            output = self.root / rel
            output.parent.mkdir(exist_ok=True)
            output.write_bytes(make_png(index))
            images.append({"appearance": appearance, "path": rel})
        (self.root / "index.html").write_text("<html>synthetic fixture</html>")
        self.manifest_path = self.root / "manifest.json"
        self.manifest_path.write_text(json.dumps({
            "version": "1.6.2", "build": 25,
            "device": "iPhone 18 Pro Max · iOS 27.0 Simulator",
            "images": images
        }))
    def test_positive_56_unique(self):
        result = MOD.verify(self.root)
        self.assertEqual(result["count"], 56)
        self.assertEqual((result["light"], result["dark"]), (28, 28))
        self.assertEqual(len({i["sha256"] for i in result["images"]}), 56)
    def test_missing_png_rejected(self):
        (self.root / sorted((self.root / "light").glob("*.png"))[0].relative_to(self.root)).unlink()
        with self.assertRaises(ValueError):
            MOD.verify(self.root)
    def test_duplicate_bytes_rejected(self):
        first = sorted((self.root / "light").glob("*.png"))[0]
        second = sorted((self.root / "dark").glob("*.png"))[0]
        second.write_bytes(first.read_bytes())
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            MOD.verify(self.root)
    def test_wrong_device_rejected(self):
        data = json.loads(self.manifest_path.read_text())
        data["device"] = "unknown simulator"
        self.manifest_path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "simulator"):
            MOD.verify(self.root)
    def test_manifest_duplicate_path_rejected(self):
        data = json.loads(self.manifest_path.read_text())
        data["images"][-1] = data["images"][0]
        self.manifest_path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "Repeated screenshot"):
            MOD.verify(self.root)
