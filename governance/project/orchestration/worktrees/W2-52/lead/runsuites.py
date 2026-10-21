"""Run named acceptance suites one after another, each in its own pytest process, with a log and an exit-code file."""
import os
import subprocess
import sys

WT = "/home/usain/gov-os-worktrees/W2-52"
OUT = os.path.join(WT, ".gov-runtime/scratch/lead/runs2")
env = dict(os.environ)
env["PATH"] = "/home/usain/.nvm/versions/node/v22.23.3/bin:" + env["PATH"]
env["PYTHONPATH"] = WT + "/src"

for suite in sys.argv[1:]:
    target = "tests/unit" if suite == "unit" else "tests/acceptance/" + suite
    args = [sys.executable, "-m", "pytest", target, "-q", "-p", "no:cacheprovider"]
    if suite != "unit":
        args.append("-rs")
    with open(os.path.join(OUT, suite + ".txt"), "w") as log:
        code = subprocess.call(args, cwd=WT, env=env, stdout=log, stderr=subprocess.STDOUT)
    with open(os.path.join(OUT, suite + ".exit"), "w") as f:
        f.write(str(code))
