"""Run 3's scoped verification in the close's form (DEC-952, DEC-968): the parallel run, then the selected
serial-only cases alone. Each with JUnit XML and an exit file. Usage: python3 run3-verify.py <parallel|serial>"""
import json
import os
import subprocess
import sys

WT = "/home/usain/gov-os-worktrees/W2-49"
LOG = WT + "/.gov-runtime/scratch/lead/log"
LOCK = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh"
sel = json.load(open(LOG + "/run3-select.json"))
opts = sel["pytest_options"]

env = dict(os.environ)
env["PATH"] = "/home/usain/.nvm/versions/node/v22.23.3/bin:" + env["PATH"]
env["PYTHONPATH"] = WT + "/src:" + WT + "/src/gov/close/pytest_plugin"
env["GOV_CLOSE_SERIAL_ONLY_OF"] = WT
env["TMPDIR"] = "/tmp/gov-os-lead-W2-49"


def serial_entries():
    out = []
    for line in open(WT + "/tests/acceptance/serial-only.txt", encoding="utf-8"):
        entry = line.split("#", 1)[0].strip()
        if entry:
            out.append(entry)
    return out


def selected(entry):
    path = entry.split("::", 1)[0]
    if entry in sel["deselect"]:
        return False
    for ig in sel["ignore"]:
        if path == ig.rstrip("/") or path.startswith(ig if ig.endswith("/") else ig + "/"):
            return False
    for s in sel["selected"]:
        t = s["target"]
        if "::" in t:
            if entry == t:
                return True
        elif t.endswith("/") or os.path.isdir(os.path.join(WT, t)):
            if path.startswith(t.rstrip("/") + "/"):
                return True
        elif path == t:
            return True
    return False


base = ["bash", LOCK, sys.executable, "-m", "pytest"]
common = ["-q", "-p", "no:cacheprovider", "-p", "gov_close_serial_only", "-o", "tmp_path_retention_policy=failed", "-rs"]
mode = sys.argv[1]
if mode == "parallel":
    cmd = base + ["tests", "-n", "auto"] + common + ["--junitxml=" + LOG + "/run3-parallel.xml"] + opts
else:
    given = [e for e in serial_entries() if selected(e)]
    open(LOG + "/run3-serial-given.txt", "w").write("\n".join(given) + "\n")
    if not given:
        open(LOG + "/run3-serial.txt", "w").write("no serial-only case is in the selection\n")
        open(LOG + "/run3-serial.exit", "w").write("0\n")
        sys.exit(0)
    env["GOV_CLOSE_SERIAL_ONLY_GIVEN"] = "\n".join(given)
    cmd = base + given + common + ["--junitxml=" + LOG + "/run3-serial.xml"] + opts
with open(LOG + "/run3-" + mode + ".txt", "w") as fh:
    rc = subprocess.call(cmd, cwd=WT, env=env, stdout=fh, stderr=subprocess.STDOUT)
open(LOG + "/run3-" + mode + ".exit", "w").write(f"{rc}\n")
sys.exit(rc)
