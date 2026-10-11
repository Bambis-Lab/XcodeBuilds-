#!/usr/bin/env python3
"""Optionally export raw XCTest attachments; named app screenshots stay separate."""
import argparse
from pathlib import Path
import subprocess
import sys

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--xcresult", default=".xb-output/Results/Test.xcresult")
    p.add_argument("--out", default=".xb-output/raw-attachments")
    args = p.parse_args()
    if not Path(args.xcresult).exists():
        print("No xcresult bundle; no attachment export", file=sys.stderr)
        return 0
    Path(args.out).mkdir(parents=True, exist_ok=True)
    return subprocess.run(["xcrun", "xcresulttool", "export", "attachments",
                           "--path", args.xcresult, "--output-path", args.out], check=False).returncode

if __name__ == "__main__":
    sys.exit(main())
