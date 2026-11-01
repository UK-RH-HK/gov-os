"""The lead's scoped verification in the close's form (DEC-952, DEC-968; close_build.py's run, one ticket).

Usage: python3 verify_scoped.py <select.json> <tag>
Runs the parallel phase (`tests` plus the selection's pytest_options, -n auto) and then the selected serial-only
cases, each with JUnit XML under log/, behind verify_lock.sh's gate; then re-runs every failing case alone once.
Writes log/scoped-<tag>.out and log/scoped-<tag>.rc (0 when both runs completed).
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path("/home/usain/gov-os-worktrees/W2-84")
ORCH = Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator")
LOG = ROOT / ".gov-runtime/scratch/lead/log"
NODE = "/home/usain/.nvm/versions/node/v22.23.3/bin"
TMP = "/tmp/gov-os-lead-W2-84"

sel = json.loads(Path(sys.argv[1]).read_text())
tag = sys.argv[2]
out = open(LOG / f"scoped-{tag}.out", "a", buffering=1)

sys.path.insert(0, str(ROOT / "src"))
from gov.close import select as gsel  # noqa: E402
from gov.close.pytest_plugin.gov_close_serial_only import entries  # noqa: E402
from gov.close.serial import phase  # noqa: E402

serial = [e for e in phase(ROOT, entries(ROOT)) if gsel.runs(e, sel["ignore"], sel["deselect"])]
(LOG / f"serial-{tag}-entries.txt").write_text("\n".join(serial) + "\n")
print(f"scope {sel['scope']}; core_changed {sel['core_changed']}; unplaced {sel['unplaced']}; "
      f"{len(sel['selected'])} targets; {len(serial)} serial entries", file=out)

env = dict(os.environ, TMPDIR=TMP, PYTHONPATH=f"{ROOT}/src:{ROOT}/src/gov/close/pytest_plugin",
           GOV_CLOSE_SERIAL_ONLY_OF=str(ROOT), PATH=NODE + ":" + os.environ.get("PATH", ""))
common = ["-q", "-p", "no:cacheprovider", "--no-header", "-p", "gov_close_serial_only",
          "-o", "tmp_path_retention_policy=failed", "-rs"]
lock = ["bash", str(ORCH / "tools/verify_lock.sh")]
if len(sys.argv) > 3 and sys.argv[3] == "--load-gate":
    # The brief's base form: "Your scoped run needs no wrapper" (DEC-968); DEC-847/DEC-961's load gate instead.
    lock = ["bash", str(ROOT / ".gov-runtime/scratch/lead/load_gate.sh")]


def run(args, e):
    subprocess.run(["date"], stdout=out)
    print("RUN", " ".join(a for a in args if not a.startswith("--ignore") and not a.startswith("--deselect")),
          file=out)
    rc = subprocess.run(args, cwd=ROOT, env=e, stdout=out, stderr=subprocess.STDOUT).returncode
    subprocess.run(["date"], stdout=out)
    print("EXIT", rc, file=out)
    return rc


par = run([*lock, sys.executable, "-m", "pytest", "tests", "-n", "auto", *common, *sel["pytest_options"],
           f"--junitxml={LOG}/parallel-{tag}.xml"], env)
ser = 0
if serial:
    ser = run([*lock, sys.executable, "-m", "pytest", *serial, *common, f"--junitxml={LOG}/serial-{tag}.xml"],
              dict(env, GOV_CLOSE_SERIAL_ONLY_GIVEN="\n".join(serial)))

import xml.etree.ElementTree as ET  # noqa: E402
failing = []
for name in (f"parallel-{tag}.xml", f"serial-{tag}.xml"):
    p = LOG / name
    if not p.exists():
        continue
    for tc in ET.parse(p).iter("testcase"):
        if tc.find("failure") is not None or tc.find("error") is not None:
            f = tc.get("file") or tc.get("classname", "").replace(".", "/") + ".py"
            failing.append(f"{f}::{tc.get('name')}")
for node in failing:
    rc = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--no-header", node],
                        cwd=ROOT, env=dict(env, PYTHONPATH=f"{ROOT}/src"), stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT, timeout=1800).returncode
    print(("ALONE PASS (flaky candidate): " if rc == 0 else "ALONE RED: ") + node, file=out)
subprocess.run(["du", "-sh", TMP], stdout=out)
subprocess.run(["du", "-s", "--inodes", TMP], stdout=out)
ok = par in (0, 1) and ser in (0, 1, 5)
(LOG / f"scoped-{tag}.rc").write_text(f"{0 if ok else 3} parallel={par} serial={ser}\n")
