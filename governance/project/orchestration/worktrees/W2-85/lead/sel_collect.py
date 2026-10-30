"""Collect-only with the selection's pytest_options and the close's plugin; count cases per suite folder."""
import collections
import json
import os
import subprocess
import sys

ROOT = "/home/usain/gov-os-worktrees/W2-85"
sel = json.load(open(f"{ROOT}/.gov-runtime/scratch/lead/log/select.txt"))
print("W2-54 in ignore:", [i for i in sel["ignore"] if "W2-54" in i])
print("W2-54 in deselect:", [i for i in sel["deselect"] if "W2-54" in i])
env = dict(os.environ, PYTHONPATH=f"{ROOT}/src:{ROOT}/src/gov/close/pytest_plugin", GOV_CLOSE_SERIAL_ONLY_OF=ROOT,
           TMPDIR="/tmp/gov-os-lead-W2-85")
cmd = [sys.executable, "-m", "pytest", "tests", "--collect-only", "-q", "-p", "no:cacheprovider", "--no-header",
       "-p", "gov_close_serial_only", *sel["pytest_options"]]
done = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True)
lines = done.stdout.splitlines()
print("rc", done.returncode, "last:", lines[-1] if lines else done.stderr[-500:])
per = collections.Counter("/".join(l.split("::")[0].split("/")[:3]) for l in lines if "::" in l)
for k, v in sorted(per.items()):
    print(f"  {k}: {v}")
