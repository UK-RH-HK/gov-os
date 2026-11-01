"""The failure lines (-rf) of W2-54's two remaining reds, alone, with the head's code and with the base's."""
import os
import subprocess
from pathlib import Path

WT = Path("/home/usain/gov-os-worktrees/W2-87")
LOG = WT / ".gov-runtime/scratch/lead/log/rerun-msgs.txt"
CASES = ["tests/acceptance/W2-54/test_w2_54_green_here.py",
         "tests/acceptance/W2-54/test_w2_54_time_limit.py::test_the_check_run_as_declared_on_this_repository_ends_green_within_its_limit"]
with open(LOG, "w") as out:
    for side, src in (("head", f"{WT}/src"), ("base", "/home/usain/gov-os-runs/W2-87/base/src")):
        env = {**os.environ, "PYTHONPATH": src, "TMPDIR": "/tmp/gov-os-lead-W2-87"}
        done = subprocess.run(["python3", "-m", "pytest", *CASES, "-q", "-p", "no:cacheprovider", "--timeout=1800",
                               "-rf", "-o", "tmp_path_retention_policy=failed"], cwd=WT, env=env,
                              capture_output=True, text=True, stdin=subprocess.DEVNULL)
        lines = [line for line in done.stdout.splitlines() if line.startswith(("FAILED", "ERROR")) or " in " in line]
        out.write(f"== {side} (exit {done.returncode}, load {open('/proc/loadavg').read().split()[0]})\n")
        out.write("\n".join(line[:400] for line in lines[-6:]) + "\n")
        out.flush()
