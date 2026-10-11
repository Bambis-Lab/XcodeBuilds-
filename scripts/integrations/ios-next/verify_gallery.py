#!/usr/bin/env python3
"""Independent acceptance of 56 named iOS Next PNG screenshots and gallery."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import sys

EXPECTED = {
    "01-independent-services-hub", "02-chat-relay-standalone",
    "03-chat-relay-configuration", "04-chat-security",
    "05-control-center-background-entry", "06-control-center-setup",
    "07-factory-custom-preview", "08-factory-preview-sections",
    "09-runner-standalone-background", "10-runner-configuration",
    "11-factory-command-deck-topology", "12-factory-oauth-connect",
    "13-factory-oauth-security", "14-product-home", "15-product-rooms",
    "16-product-chat", "17-product-media", "18-product-system",
    "19-product-light", "20-product-media-detail", "21-product-owner",
    "22-product-wireguard", "23-factory-no-session-detail",
    "24-control-center-setup-security", "25-factory-keychain-error",
    "26-runner-offline", "27-factory-oauth-rejection",
    "28-wireguard-offline-security",
}

def verify(root):
    root = Path(root).resolve()
    manifest = json.loads((root / "manifest.json").read_text())
    if manifest.get("version") != "1.6.2" or manifest.get("build") != 25:
        raise ValueError("Incorrect screenshot build version")
    if manifest.get("device") != "iPhone 18 Pro Max · iOS 27.0 Simulator":
        raise ValueError("Incorrect simulator identity")
    images = manifest.get("images")
    if not isinstance(images, list) or len(images) != 56:
        raise ValueError("Exactly 56 gallery manifest entries required")
    digests, actual, results = {}, set(), []
    for img in images:
        appearance = img.get("appearance")
        name = img.get("path")
        if appearance not in ("light", "dark") or not isinstance(name, str):
            raise ValueError("Unexpected gallery image record")
        match = re.fullmatch(r"(light|dark)/([0-9]{2}-[a-z0-9-]+)\.png", name)
        if not match or match.group(1) != appearance or match.group(2) not in EXPECTED:
            raise ValueError(f"Unrecognized screenshot: {name}")
        if name in actual:
            raise ValueError(f"Repeated screenshot path: {name}")
        actual.add(name)
        path = root / name
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"Missing/linked screenshot: {name}")
        payload = path.read_bytes()
        if len(payload) <= 25_000 or payload[:8] != b"\x89PNG\r\n\x1a\n" or payload[12:16] != b"IHDR":
            raise ValueError(f"Not a full PNG image: {name}")
        width, height = struct.unpack(">II", payload[16:24])
        if width < 100 or height < 100:
            raise ValueError(f"Invalid screenshot dimensions: {name}")
        digest = hashlib.sha256(payload).hexdigest()
        if digest in digests:
            raise ValueError(f"Duplicate image contents: {digests[digest]} / {name}")
        digests[digest] = name
        results.append({"path": name, "sha256": digest, "bytes": len(payload)})
    expected = {f"{appearance}/{label}.png" for appearance in ("light", "dark") for label in EXPECTED}
    if actual != expected:
        raise ValueError(f"Missing/extra images: {sorted(expected-actual)} / {sorted(actual-expected)}")
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ValueError("Screenshot directory contains links")
    pngs = {p.relative_to(root).as_posix() for p in root.rglob("*.png")}
    if pngs != expected:
        raise ValueError(f"Unexpected on-disk PNGs: {sorted(pngs^expected)}")
    if not (root / "index.html").is_file():
        raise ValueError("Screenshot gallery index.html missing")
    return {"status": "PASS", "version": "1.6.2", "simulator": manifest["device"],
            "count": len(results), "light": 28, "dark": 28, "images": results}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    try:
        result = verify(args.root)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        result = {"status": "FAIL", "error": str(error)}
    out = Path(args.report)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(f"XB05_VISUAL_ACCEPTANCE={result['status']} count={result.get('count','n/a')}")
    if result["status"] != "PASS":
        print(result["error"], file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
