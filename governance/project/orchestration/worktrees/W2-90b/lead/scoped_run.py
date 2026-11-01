#!/usr/bin/env python3
"""The scoped verification in the close's form: the parallel run, then the serial-only cases, each with JUnit XML.

Usage: scoped_run.py parallel|serial
Reads select_tests.py's pytest_options from log/select.json. Writes log/<phase>.txt, .xml and .exit.
"""
import json
import os
import subprocess
import sys

TREE = "/home/usain/gov-os-worktrees/W2-90b"
LOG = TREE + "/.gov-runtime/scratch/lead/log"
LOCK = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh"

phase = sys.argv[1]
options = json.load(open(LOG + "/select.json", encoding="utf-8"))["pytest_options"]
env = dict(os.environ)
env["TMPDIR"] = "/tmp/gov-os-lead-W2-90b"
env["PATH"] = "/home/usain/.nvm/versions/node/v22.23.3/bin:" + env["PATH"]
env["PYTHONPATH"] = TREE + "/src:" + TREE + "/src/gov/close/pytest_plugin"
env["GOV_CLOSE_SERIAL_ONLY_OF"] = TREE
common = ["-q", "-p", "no:cacheprovider", "-p", "gov_close_serial_only", "-o", "tmp_path_retention_policy=failed",
          "-rs", f"--junitxml={LOG}/{phase}.xml"]
if phase == "parallel":
    args = ["tests", "-n", "auto"] + common + options
else:
    entries = []
    for line in open(TREE + "/tests/acceptance/serial-only.txt", encoding="utf-8"):
        if line.startswith("#") or not line.strip():
            continue
        entries.append(line.split(" #")[0].strip())
    env["GOV_CLOSE_SERIAL_ONLY_GIVEN"] = "\n".join(entries)
    args = entries + common + options
if len(sys.argv) > 2 and sys.argv[2] == "collect":
    args = [a for a in args if not a.startswith("--junitxml")] + ["--collect-only"]
    with open(f"{LOG}/{phase}-collect.txt", "w", encoding="utf-8") as out:
        sys.exit(subprocess.run([sys.executable, "-m", "pytest"] + args, cwd=TREE, env=env, stdout=out,
                                stderr=subprocess.STDOUT).returncode)
cmd = ["bash", LOCK, sys.executable, "-m", "pytest"] + args
with open(f"{LOG}/{phase}.txt", "w", encoding="utf-8") as out:
    code = subprocess.run(cmd, cwd=TREE, env=env, stdout=out, stderr=subprocess.STDOUT).returncode
open(f"{LOG}/{phase}.exit", "w").write(f"{code}\n")
sys.exit(code)
