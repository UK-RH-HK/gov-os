"""The lead's scoped verification in the close's form (DEC-952, DEC-968, DEC-889): the selection, one parallel run,
then the selected serial-only cases alone, each through verify_lock.sh (the heavy-job slot), each with JUnit XML.
Run in the background: writes log/select.json, log/serial-list.txt, log/parallel.{xml,txt}, log/serial.{xml,txt}
and log/verify.rc (the two exit codes)."""
import json
import os
import subprocess
import sys

WT = "/home/usain/gov-os-worktrees/W2-97"
LOG = WT + "/.gov-runtime/scratch/lead/log"
TOOLS = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools"
NODE = "/home/usain/.nvm/versions/node/v22.23.3/bin"

os.makedirs("/tmp/gov-os-lead-W2-97", exist_ok=True)
base = dict(os.environ, TMPDIR="/tmp/gov-os-lead-W2-97")
sel = subprocess.run([sys.executable, TOOLS + "/select_tests.py", WT, "W2-97", "DAEO-wq2b"], cwd=WT,
                     env=dict(base, PYTHONPATH=WT + "/src"), capture_output=True, text=True)
open(LOG + "/select.json", "w").write(sel.stdout)
open(LOG + "/select.err", "w").write(sel.stderr)
if sel.returncode != 0:
    open(LOG + "/verify.rc", "w").write(f"select {sel.returncode}\n")
    sys.exit(0)
s = json.loads(sel.stdout)

sys.path.insert(0, WT + "/src")
from gov.close import select as gsel  # noqa: E402
from gov.close.pytest_plugin.gov_close_serial_only import entries  # noqa: E402
from gov.close.serial import phase  # noqa: E402
from pathlib import Path  # noqa: E402
serial = [e for e in phase(Path(WT), entries(Path(WT))) if gsel.runs(e, s["ignore"], s["deselect"])]
open(LOG + "/serial-list.txt", "w").write("\n".join(serial) + "\n")

env = dict(base, PATH=NODE + ":" + base.get("PATH", ""),
           PYTHONPATH=WT + "/src:" + WT + "/src/gov/close/pytest_plugin", GOV_CLOSE_SERIAL_ONLY_OF=WT)
common = ["-q", "-p", "no:cacheprovider", "-p", "gov_close_serial_only", "-o", "tmp_path_retention_policy=failed", "-rs"]
par = subprocess.run(["bash", TOOLS + "/verify_lock.sh", sys.executable, "-m", "pytest", "tests", "-n", "auto", *common,
                      *s["pytest_options"], "--junitxml=" + LOG + "/parallel.xml"], cwd=WT, env=env,
                     capture_output=True, text=True)
open(LOG + "/parallel.txt", "w").write(par.stdout[-30000:] + "\n--- stderr\n" + par.stderr[-8000:])
ser_rc = "none"
if serial:
    ser = subprocess.run(["bash", TOOLS + "/verify_lock.sh", sys.executable, "-m", "pytest", *serial, *common,
                          "--junitxml=" + LOG + "/serial.xml"], cwd=WT,
                         env=dict(env, GOV_CLOSE_SERIAL_ONLY_GIVEN="\n".join(serial)), capture_output=True, text=True)
    open(LOG + "/serial.txt", "w").write(ser.stdout[-30000:] + "\n--- stderr\n" + ser.stderr[-8000:])
    ser_rc = ser.returncode
open(LOG + "/verify.rc", "w").write(f"parallel {par.returncode} serial {ser_rc} entries {len(serial)}\n")
