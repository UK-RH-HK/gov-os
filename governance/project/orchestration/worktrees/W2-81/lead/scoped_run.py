"""Lead's scoped verification of W2-81 in the close's form (DEC-952, DEC-889 items 6 and 12, DEC-905, DEC-979 D1).

Reads the selection select_tests.py printed (log/select.json), runs the selected tests in one parallel run with the
serial-only plugin, then the selected serial-only cases alone, each through verify_lock.sh, each with JUnit XML.
Run with this worktree's src first on PYTHONPATH (DEC-732). Writes exit codes to log/parallel.exit, log/serial.exit.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path("/home/usain/gov-os-worktrees/W2-81")
LOG = ROOT / ".gov-runtime/scratch/lead/log"
LOCK = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh"

sys.path.insert(0, str(ROOT / "src"))
from gov.close import select, serial  # noqa: E402
from gov.close.pytest_plugin import gov_close_serial_only as serial_only  # noqa: E402

sel = json.loads((LOG / "select.json").read_text())
opts = sel["pytest_options"]
declared = [e for e in serial_only.entries(ROOT)
            if e.startswith("tests/") and select.runs(e, sel["ignore"], sel["deselect"])]
declared = serial.phase(ROOT, declared)
(LOG / "serial-entries.txt").write_text("\n".join(declared) + "\n")

env = dict(os.environ)
env.update({
    "PATH": "/home/usain/.nvm/versions/node/v22.23.3/bin:" + env.get("PATH", ""),
    "PYTHONPATH": f"{ROOT}/src:{ROOT}/src/gov/close/pytest_plugin",
    "GOV_CLOSE_SERIAL_ONLY_OF": str(ROOT),
    "TMPDIR": "/tmp/gov-os-lead-W2-81",
})
env.pop("GOV_CLOSE_SERIAL_ONLY_GIVEN", None)
base = ["bash", LOCK, "python3", "-m", "pytest"]
common = ["-q", "-p", "no:cacheprovider", "-p", "gov_close_serial_only", "-o", "tmp_path_retention_policy=failed",
          "-rs"]

with open(LOG / "parallel.out", "w") as out:
    rc = subprocess.run(base + ["tests", "-n", "auto"] + common + [f"--junitxml={LOG}/parallel.xml"] + opts,
                        cwd=ROOT, env=env, stdout=out, stderr=subprocess.STDOUT).returncode
(LOG / "parallel.exit").write_text(f"{rc}\n")

if declared:
    senv = dict(env, GOV_CLOSE_SERIAL_ONLY_GIVEN="\n".join(declared))
    with open(LOG / "serial.out", "w") as out:
        rc = subprocess.run(base + declared + common + [f"--junitxml={LOG}/serial.xml"] + opts,
                            cwd=ROOT, env=senv, stdout=out, stderr=subprocess.STDOUT).returncode
else:
    (LOG / "serial.out").write_text("no serial-only case is selected\n")
    rc = 0
(LOG / "serial.exit").write_text(f"{rc}\n")
