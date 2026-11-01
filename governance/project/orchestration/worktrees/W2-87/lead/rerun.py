"""Re-run each remaining red alone (DEC-953: a red that fails alone is a red), with this worktree's code and then,
back to back, with the base's code (the base clone's src on PYTHONPATH), so a load red and a red of this ticket
can be told apart. One line per run in log/rerun.txt."""
import os
import subprocess
import time
from pathlib import Path

WT = Path("/home/usain/gov-os-worktrees/W2-87")
LOG = WT / ".gov-runtime/scratch/lead/log/rerun.txt"
CASES = [
    "tests/acceptance/W1-02/test_w1_02_guard_hook.py::test_decision_p95_is_under_100_ms",
    "tests/acceptance/W1-05/test_w1_05_live_hooks.py::test_a_call_waits_under_100_ms_p95_for_the_hook",
    "tests/acceptance/W2-54/test_w2_54_green_here.py",
    "tests/acceptance/W2-54/test_w2_54_time_limit.py::test_the_check_run_as_declared_on_this_repository_ends_green_within_its_limit",
]
SIDES = {"head": f"{WT}/src", "base": "/home/usain/gov-os-runs/W2-87/base/src"}
with open(LOG, "w") as out:
    for case in CASES:
        for side, src in SIDES.items():
            env = {**os.environ, "PYTHONPATH": f"{src}:{WT}/src/gov/close/pytest_plugin",
                   "TMPDIR": "/tmp/gov-os-lead-W2-87"}
            started = time.time()
            done = subprocess.run(["python3", "-m", "pytest", case, "-q", "-p", "no:cacheprovider", "--timeout=1800",
                                   "-o", "tmp_path_retention_policy=failed"], cwd=WT, env=env,
                                  capture_output=True, text=True, stdin=subprocess.DEVNULL)
            tail = [line for line in done.stdout.splitlines() if line.strip()][-1:]
            load = open("/proc/loadavg").read().split()[0]
            out.write(f"{side} | {case} | exit {done.returncode} | {time.time() - started:.0f}s | load {load} | "
                      f"{tail[0][:200] if tail else ''}\n")
            out.flush()
            if side == "head" and done.returncode == 0:
                break  # passes alone on this code: no comparison needed
