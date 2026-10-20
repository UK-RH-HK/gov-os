"""The lead's verification runner: each named suite in its own pytest
process, to its end, with its output, exit code and duration under
log/verify-<name>.*; 'unit' is tests/unit, 'check' is gov check."""
import os
import subprocess
import sys
import time

ROOT = "/home/usain/gov-os-worktrees/W2-62"
LOG = ROOT + "/.gov-runtime/scratch/lead/log"
ENV = dict(os.environ, PYTHONPATH=ROOT + "/src",
           PATH="/home/usain/.nvm/versions/node/v22.23.3/bin:" + os.environ["PATH"])
CLOSE = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING"

for name in sys.argv[1:]:
    while os.path.exists(CLOSE):
        time.sleep(60)
    if name == "check":
        cmd = ["python3", "-m", "gov.cli.main", "check", "--json"]
    elif name == "unit":
        cmd = ["python3", "-m", "pytest", "tests/unit", "-q", "-p", "no:cacheprovider"]
    elif name.endswith("-live"):
        cmd = ["python3", "-m", "pytest", "tests/acceptance/" + name[:-5], "-q", "-p", "no:cacheprovider", "-rs",
               "-m", "local_only"]
    else:
        cmd = ["python3", "-m", "pytest", "tests/acceptance/" + name, "-q", "-p", "no:cacheprovider", "-rs"]
    start = time.time()
    with open(f"{LOG}/verify-{name}.txt", "w") as out:
        code = subprocess.run(cmd, cwd=ROOT, env=ENV, stdout=out, stderr=subprocess.STDOUT).returncode
    with open(f"{LOG}/verify-{name}.exit", "w") as f:
        f.write(f"{code} {time.time() - start:.0f}s\n")
