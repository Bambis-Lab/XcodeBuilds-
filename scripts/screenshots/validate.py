#!/usr/bin/env python3
"""Exact screenshot manifest validation, PNG integrity and duplicate-content detection."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys

MAGIC = b"\x89PNG\r\n\x1a\n"

def validate(root, manifest_path):
    root = Path(root).resolve()
    manifest_path = Path(manifest_path).resolve()
    data = json.loads(manifest_path.read_text())
    if data.get("version") != 1 or not isinstance(data.get("shots"), list):
        raise ValueError("Manifest requires version=1 and shots list")
    expected = {}
    for shot in data["shots"]:
        if set(shot) != {"file", "state"} or not isinstance(shot["file"], str) or not isinstance(shot["state"], str):
            raise ValueError("Each shot requires file and state strings")
        relative = Path(shot["file"])
        if relative.is_absolute() or ".." in relative.parts or relative.suffix.lower() != ".png" or shot["file"] in expected:
            raise ValueError(f"Unsafe, non-PNG or repeated manifest name: {shot['file']}")
        if not shot["state"].strip():
            raise ValueError("Empty state")
        expected[relative.as_posix()] = shot["state"]
    if not root.is_dir():
        raise ValueError(f"Screenshot directory missing: {root}")
    # Reject links, including links to files outside this directory.
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"Symlink prohibited: {path}")
    actual_paths = {p.relative_to(root).as_posix(): p for p in root.rglob("*") if p.is_file()}
    if set(expected) != set(actual_paths):
        raise ValueError(f"Exact filename mismatch: missing={sorted(set(expected)-set(actual_paths))}, extra={sorted(set(actual_paths)-set(expected))}")
    found_hashes = {}
    items = []
    for filename in sorted(expected):
        data_bytes = actual_paths[filename].read_bytes()
        if len(data_bytes) < 33 or data_bytes[:8] != MAGIC or data_bytes[12:16] != b"IHDR":
            raise ValueError(f"Not a valid PNG header: {filename}")
        width, height = struct.unpack(">II", data_bytes[16:24])
        if width < 1 or height < 1:
            raise ValueError(f"Invalid PNG dimensions: {filename}")
        digest = hashlib.sha256(data_bytes).hexdigest()
        if digest in found_hashes:
            raise ValueError(f"Byte-identical duplicate screenshots: {found_hashes[digest]} and {filename}")
        found_hashes[digest] = filename
        items.append({"file": filename, "state": expected[filename], "sha256": digest, "bytes": len(data_bytes), "width": width, "height": height})
    required_states = set(data.get("required_states", []))
    present_states = {item["state"] for item in items}
    if not required_states.issubset(present_states):
        raise ValueError(f"Missing simulated states: {sorted(required_states-present_states)}")
    return {"status": "PASS", "count": len(items), "states": sorted(present_states), "screenshots": items}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--report")
    args = parser.parse_args()
    try:
        result = validate(args.root, args.manifest)
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as error:
        result = {"status": "FAIL", "error": str(error)}
    if args.report:
        destination = Path(args.report)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1

if __name__ == "__main__":
    sys.exit(main())
