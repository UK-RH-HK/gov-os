"""Step 4 of the lead's loop for W2-126: the scoped parallel run, then the selected serial-only cases alone, each
through verify_lock.sh, in the close's form. Run with this worktree's src first on PYTHONPATH (DEC-732).

Usage: python3 run_verify.py <select.json> <log folder>
Writes <log folder>/parallel.{log,xml,exit} and serial.{log,xml,exit}, and serial-entries.txt."""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path("/home/usain/gov-os-worktrees/W2-126")
LOCK = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh"

sys.path.insert(0, str(ROOT / "src" / "gov" / "close" / "pytest_plugin"))
from gov.close import select  # noqa: E402
import gov_close_serial_only  # noqa: E402

plan = json.load(open(sys.argv[1]))
logs = Path(sys.argv[2])
options = plan["pytest_options"]

env = dict(os.environ)
env["PATH"] = "/home/usain/.nvm/versions/node/v22.23.3/bin:" + env.get("PATH", "")
env["PYTHONPATH"] = f"{ROOT}/src:{ROOT}/src/gov/close/pytest_plugin"
env["GOV_CLOSE_SERIAL_ONLY_OF"] = str(ROOT)
env["TMPDIR"] = "/tmp/gov-os-lead-W2-126"


def run(name, args, extra_env=None):
    command = ["bash", LOCK, "python3", "-m", "pytest", *args, "-q", "-p", "no:cacheprovider",
               "-p", "gov_close_serial_only", "-o", "tmp_path_retention_policy=failed", "-rs",
               f"--junitxml={logs / (name + '.xml')}", *options]
    with open(logs / f"{name}.log", "w") as out:
        code = subprocess.call(command, cwd=ROOT, env={**env, **(extra_env or {})}, stdout=out,
                               stderr=subprocess.STDOUT)
    (logs / f"{name}.exit").write_text(f"{code}\n")
    return code


run("parallel", ["tests", "-n", "auto"])

serial = [entry for entry in gov_close_serial_only.entries(ROOT)
          if select.runs(entry, plan.get("ignore", []), plan.get("deselect", []))]
(logs / "serial-entries.txt").write_text("".join(f"{entry}\n" for entry in serial))
if serial:
    run("serial", serial, {"GOV_CLOSE_SERIAL_ONLY_GIVEN": "\n".join(serial)})
else:
    (logs / "serial.exit").write_text("none selected\n")
