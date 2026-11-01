"""The lead's scoped verification in the close's form (DEC-952, DEC-968, DEC-889 items 6 and 12, DEC-905).

    python3 verify.py <select.json> <out folder>

Runs, through verify_lock.sh: (1) the parallel run of `tests` with select_tests.py's pytest_options, the serial-only
plugin and JUnit XML; (2) the selected serial-only cases alone (the list's entries the selection keeps), without -n.
Writes parallel.xml, parallel.log, parallel.exit, serial.xml, serial.log, serial.exit, serial-entries.txt in <out>.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

TREE = "/home/usain/gov-os-worktrees/W2-91"
LOCK = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh"
sel = json.load(open(sys.argv[1], encoding="utf-8"))
out = Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
opts = sel["pytest_options"]
ignore = sel.get("ignore", [])
deselect = set(sel.get("deselect", []))

env = dict(os.environ)
env["PATH"] = "/home/usain/.nvm/versions/node/v22.23.3/bin:" + env["PATH"]
env["PYTHONPATH"] = f"{TREE}/src:{TREE}/src/gov/close/pytest_plugin"
env["GOV_CLOSE_SERIAL_ONLY_OF"] = TREE
env["TMPDIR"] = "/tmp/gov-os-lead-W2-91"
env.pop("GOV_CLOSE_SERIAL_ONLY_GIVEN", None)

common = ["-q", "-p", "no:cacheprovider", "-p", "gov_close_serial_only", "-o", "tmp_path_retention_policy=failed", "-rs"]


def run(name, args, env):
    with open(out / f"{name}.log", "w", encoding="utf-8") as log:
        rc = subprocess.run(["bash", LOCK, "python3", "-m", "pytest", *args], cwd=TREE, env=env,
                            stdout=log, stderr=subprocess.STDOUT).returncode
    (out / f"{name}.exit").write_text(f"{rc}\n", encoding="utf-8")
    return rc


run("parallel", ["tests", "-n", "auto", *common, f"--junitxml={out}/parallel.xml", *opts], env)

# The serial-only entries the selection keeps: not under an ignored path, not deselected.
entries = []
for raw in Path(TREE, "tests/acceptance/serial-only.txt").read_text(encoding="utf-8").splitlines():
    entry = raw.split("#", 1)[0].strip()
    if not entry:
        continue
    path = entry.split("::", 1)[0]
    if any(path == i.rstrip("/") or path.startswith(i if i.endswith("/") else i + "/") for i in ignore):
        continue
    if entry in deselect:
        continue
    entries.append(entry)
(out / "serial-entries.txt").write_text("\n".join(entries) + "\n", encoding="utf-8")
if entries:
    senv = dict(env)
    senv["GOV_CLOSE_SERIAL_ONLY_GIVEN"] = "\n".join(entries)
    run("serial", [*entries, *common, f"--junitxml={out}/serial.xml", *opts], senv)
else:
    (out / "serial.exit").write_text("none selected\n", encoding="utf-8")
