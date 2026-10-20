"""Run each named acceptance suite in its own pytest process, to its end; one log and one exit code per suite."""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path("/home/usain/gov-os-worktrees/W2-03")
LOG = ROOT / ".gov-runtime/scratch/lead/log"
batch = sys.argv[1]
suites = sys.argv[2:]
env = {**os.environ, "PYTHONPATH": str(ROOT / "src"),
       "PATH": "/home/usain/.nvm/versions/node/v22.23.3/bin:" + os.environ["PATH"]}
summary = []
for suite in suites:
    name = Path(suite).name
    out = LOG / f"suite-{name}.txt"
    with out.open("w") as handle:
        code = subprocess.run([sys.executable, "-m", "pytest", suite, "-q", "-p", "no:cacheprovider", "-rs", "-rf"],
                              cwd=ROOT, env=env, stdout=handle, stderr=subprocess.STDOUT).returncode
    last = [line for line in out.read_text().splitlines() if line.strip()][-1:]
    summary.append(f"{name} exit {code}: {last[0] if last else ''}")
    (LOG / f"batch-{batch}.progress").write_text("\n".join(summary) + "\n")
(LOG / f"batch-{batch}.exit").write_text("done\n")
