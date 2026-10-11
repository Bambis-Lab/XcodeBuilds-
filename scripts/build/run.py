#!/usr/bin/env python3
"""Run strictly unsigned Xcode/Swift operations in the checked-out caller repository."""
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import sys

KINDS = {"swift-package", "xcode-project", "xcode-workspace"}
CONFIGS = {"Debug", "Release"}

def resolve_project(workspace, name, kind):
    base = Path(workspace).resolve()
    if not name or Path(name).is_absolute():
        raise ValueError("Project path must be nonempty and relative")
    path = (base / name).resolve()
    if not path.is_relative_to(base) or ".xcodebuilds-tools" in path.relative_to(base).parts:
        raise ValueError("Project path escapes source checkout or points at tooling")
    if kind == "swift-package":
        if not (path / "Package.swift").is_file():
            raise ValueError(f"No Package.swift at {path}")
    else:
        suffix = ".xcodeproj" if kind == "xcode-project" else ".xcworkspace"
        if path.suffix != suffix or not path.is_dir():
            raise ValueError(f"Expected existing {suffix} at {path}")
    return path

def build_command(mode, workspace, env):
    kind = env["XB_PROJECT_KIND"]
    configuration = env.get("XB_CONFIGURATION", "Debug")
    if kind not in KINDS or configuration not in CONFIGS or mode not in {"build", "test"}:
        raise ValueError("Invalid project type, configuration or operation")
    path = resolve_project(workspace, env["XB_SOURCE_PATH"], kind)
    if kind == "swift-package":
        return ["swift", mode, "--package-path", str(path), "-c", configuration.lower()]
    scheme = env.get("XB_SCHEME", "").strip()
    destination = env.get("XB_DESTINATION", "").strip()
    if not scheme or not destination:
        raise ValueError("Xcode builds require explicit scheme and destination")
    if "\n" in scheme or "\n" in destination:
        raise ValueError("Multiline arguments not permitted")
    flag = "-project" if kind == "xcode-project" else "-workspace"
    output = Path(workspace) / ".xb-output"
    command = ["xcodebuild", flag, str(path), "-scheme", scheme,
               "-configuration", configuration, "-destination", destination,
               "-derivedDataPath", str(output / "DerivedData"),
               "CODE_SIGNING_ALLOWED=NO"]
    if mode == "test":
        command.extend(["-resultBundlePath", str(output / "Results" / "Test.xcresult")])
    command.append(mode)
    return command

def execute(mode):
    workspace = Path(os.environ.get("GITHUB_WORKSPACE", os.getcwd())).resolve()
    output = workspace / ".xb-output"
    (output / "logs").mkdir(parents=True, exist_ok=True)
    (output / "Results").mkdir(parents=True, exist_ok=True)
    metadata = {
        "mode": mode, "project_kind": os.environ.get("XB_PROJECT_KIND"),
        "source_path": os.environ.get("XB_SOURCE_PATH"),
        "runner": os.environ.get("RUNNER_NAME"),
        "repository": os.environ.get("GITHUB_REPOSITORY"),
        "commit": os.environ.get("GITHUB_SHA"),
        "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "code_signing_allowed": False
    }
    result = 1
    try:
        cmd = build_command(mode, workspace, os.environ)
        # Commands are argument arrays, never interpolated into a shell.
        with (output / "logs" / f"{mode}.log").open("w") as log:
            process = subprocess.Popen(cmd, cwd=workspace, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT, text=True, errors="replace")
            assert process.stdout is not None
            for line in process.stdout:
                print(line, end="", flush=True)
                log.write(line)
            result = process.wait()
    except (ValueError, KeyError, OSError) as error:
        metadata["error"] = str(error)
        print(f"ERROR: {error}", file=sys.stderr)
    finally:
        metadata["exit_code"] = result
        (output / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    return result

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in {"build", "test"}:
        raise SystemExit("Usage: run.py build|test")
    raise SystemExit(execute(sys.argv[1]))
