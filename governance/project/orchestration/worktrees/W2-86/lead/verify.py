"""W2-86's scoped verification in the close's form (DEC-952, DEC-968): the selection's pytest options added to the
parallel run, then the selected serial-only cases alone. usage: python3 verify.py <select json> <tag>"""
import json
import os
import subprocess
import sys
from pathlib import Path

WT = "/home/usain/gov-os-worktrees/W2-86"
LOG = Path(WT) / ".gov-runtime/scratch/lead/log"
LOCK = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh"

selection = json.load(open(sys.argv[1]))
tag = sys.argv[2]
options = selection["pytest_options"]
ignored = [entry.rstrip("/") for entry in selection["ignore"]]
deselected = set(selection["deselect"])

serial = []
for line in (Path(WT) / "tests/acceptance/serial-only.txt").read_text().splitlines():
    entry = line.split("#", 1)[0].strip()
    if not entry:
        continue
    path = entry.split("::", 1)[0]
    if any(path == item or path.startswith(item + "/") for item in ignored) or entry in deselected:
        continue
    if not (Path(WT) / path).exists():
        continue
    serial.append(entry)
(LOG / f"serial-{tag}.txt").write_text("\n".join(serial) + "\n")

env = dict(os.environ)
env.pop("PYTHONPATH", None)
env.update({"PATH": "/home/usain/.nvm/versions/node/v22.23.3/bin:" + env["PATH"],
            "PYTHONPATH": f"{WT}/src:{WT}/src/gov/close/pytest_plugin",
            "GOV_CLOSE_SERIAL_ONLY_OF": WT, "TMPDIR": "/tmp/gov-os-lead-W2-86"})
os.makedirs("/tmp/gov-os-lead-W2-86", exist_ok=True)
base = ["bash", LOCK, "python3", "-m", "pytest"]
common = ["-q", "-p", "no:cacheprovider", "-p", "gov_close_serial_only", "-o", "tmp_path_retention_policy=failed", "-rs"]

with open(LOG / f"parallel-{tag}.out", "w") as out:
    rc = subprocess.run(base + ["tests", "-n", "auto"] + common + options
                        + [f"--junitxml={LOG}/parallel-{tag}.xml"], cwd=WT, env=env, stdout=out,
                        stderr=subprocess.STDOUT).returncode
(LOG / f"parallel-{tag}.exit").write_text(f"{rc}\n")

if serial:
    env["GOV_CLOSE_SERIAL_ONLY_GIVEN"] = "\n".join(serial)
    with open(LOG / f"serial-{tag}.out", "w") as out:
        rc = subprocess.run(base + common + options + [f"--junitxml={LOG}/serial-{tag}.xml"] + serial, cwd=WT,
                            env=env, stdout=out, stderr=subprocess.STDOUT).returncode
else:
    rc = "none"
(LOG / f"serial-{tag}.exit").write_text(f"{rc}\n")
