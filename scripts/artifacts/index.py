#!/usr/bin/env python3
"""SHA256 index of downloaded upstream artifacts, refusing symlinks."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

def index(root):
    root = Path(root)
    if not root.is_dir():
        raise ValueError("Missing source artifact directory")
    entries = []
    for p in sorted(root.rglob("*")):
        if p.is_symlink():
            raise ValueError(f"Refusing artifact symlink: {p}")
        if p.is_file():
            entries.append({"path": p.relative_to(root).as_posix(), "bytes": p.stat().st_size,
                            "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
    if not entries:
        raise ValueError("Source artifact directory empty")
    return {"schema_version": 1, "files": entries, "count": len(entries)}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()
    try:
        result = index(a.root)
        out = Path(a.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2) + "\n")
        print(f"Indexed {result['count']} artifacts")
        return 0
    except (ValueError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
