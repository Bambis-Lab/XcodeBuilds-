#!/usr/bin/env python3
"""Offline registry/profile consistency check; standard library only."""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
PLATFORMS = {"ios", "ipados", "macos", "watchos", "tvos", "visionos", "swift-package"}
PROFILES = {"ios", "macos", "watchos", "tvos", "visionos", "swift-package"}

def validate(root=ROOT):
    registry = json.loads((root / "registry/projects.json").read_text())
    assert registry["schema_version"] == 1
    ids = set()
    for item in registry["projects"]:
        assert set(item) == {"id", "description", "platforms", "profile", "source_repository", "source_path", "signing", "enabled"}
        assert re.fullmatch(r"[a-z0-9][a-z0-9-]*", item["id"]), item
        assert item["id"] not in ids, item["id"]
        ids.add(item["id"])
        assert item["profile"] in PROFILES
        assert item["platforms"] and set(item["platforms"]).issubset(PLATFORMS)
        assert re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", item["source_repository"])
        assert item["signing"] == "disabled"
        assert type(item["enabled"]) is bool
        if item["enabled"]:
            assert item["source_path"] is not None
            if item["source_repository"] == "Bambis-Lab/XcodeBuilds-":
                assert (root / item["source_path"]).resolve().is_relative_to(root.resolve())
                assert (root / item["source_path"]).is_dir()
    for name in PROFILES:
        profile = json.loads((root / f"profiles/{name}.json").read_text())
        assert profile["id"] == name
        assert profile["runner"] == "xcode-27", profile
        assert profile["code_signing_allowed"] is False
        assert profile["release_enabled"] is False
    print(f"PASS registry: {len(ids)} projects, {len(PROFILES)} profiles, unsigned only")

if __name__ == "__main__":
    try:
        validate()
    except (AssertionError, KeyError, ValueError, OSError) as error:
        print(f"FAIL registry: {error}", file=sys.stderr)
        raise SystemExit(1)
