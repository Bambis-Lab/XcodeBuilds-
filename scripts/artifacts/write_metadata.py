#!/usr/bin/env python3
"""Create informational environment provenance, not an attestation."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import subprocess

p = argparse.ArgumentParser()
p.add_argument("--output", required=True)
p.add_argument("--project", required=True)
p.add_argument("--runner", required=True)
args = p.parse_args()
def run(cmd):
    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT, timeout=15).strip()
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return "unavailable"
content = {"project": args.project, "runner_label": args.runner,
           "runner_name": os.getenv("RUNNER_NAME"), "github_repository": os.getenv("GITHUB_REPOSITORY"),
           "github_sha": os.getenv("GITHUB_SHA"), "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
           "xcode": run(["xcodebuild", "-version"]), "swift": run(["swift", "--version"]),
           "code_signing_allowed": False}
target = Path(args.output)
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps(content, indent=2) + "\n")
