"""The scoped verification of DAEO-h2k3 in the close's form: the parallel run, then the serial-only cases."""
import json
import os
import subprocess
import sys
from pathlib import Path

TREE = Path("/home/usain/gov-os-worktrees/W2-61h")
LOG = TREE / ".gov-runtime/scratch/lead/log"
TOOLS = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools"
sys.path.insert(0, str(TREE / "src"))

from gov.close import serial, select as _select  # noqa: E402
from gov.close.pytest_plugin import gov_close_serial_only as serial_only  # noqa: E402

sel = json.loads((LOG / "select-3.json").read_text())
options = sel["pytest_options"]
listed = serial_only.entries(TREE)
declared = [e for e in listed if e.startswith("tests/") and _select.runs(e, sel["ignore"], sel["deselect"])]
declared = serial.phase(TREE, declared)
(LOG / "serial-entries-3.txt").write_text("\n".join(declared) + "\n")

env = dict(os.environ)
env["PATH"] = "/home/usain/.nvm/versions/node/v22.23.3/bin:" + env["PATH"]
env["PYTHONPATH"] = f"{TREE}/src:{TREE}/src/gov/close/pytest_plugin"
env["GOV_CLOSE_SERIAL_ONLY_OF"] = str(TREE)
env["TMPDIR"] = "/tmp/gov-os-lead-W2-61h"
base = ["bash", f"{TOOLS}/verify_lock.sh", "python3", "-m", "pytest"]
common = ["-q", "-p", "no:cacheprovider", "-p", "gov_close_serial_only", "-o", "tmp_path_retention_policy=failed",
          "-rs"]

part = sys.argv[1]
if part == "parallel":
    cmd = base + ["tests", "-n", "auto"] + common + [f"--junitxml={LOG}/parallel.xml"] + options
    out = LOG / "parallel.out"
else:
    if not declared:
        (LOG / "serial.out").write_text("no serial-only case selected\n")
        sys.exit(0)
    env["GOV_CLOSE_SERIAL_ONLY_GIVEN"] = "\n".join(declared)
    cmd = base + declared + common + [f"--junitxml={LOG}/serial.xml"] + options
    out = LOG / "serial.out"
with open(out, "w") as fh:
    code = subprocess.run(cmd, cwd=TREE, env=env, stdout=fh, stderr=subprocess.STDOUT).returncode
sys.exit(code)
