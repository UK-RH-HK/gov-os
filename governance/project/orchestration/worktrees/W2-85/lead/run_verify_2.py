"""After the rebuild at the head: the time-limit case alone again, as the nightly runs it (log/alone-time-limit-2.*)."""
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path("/home/usain/gov-os-worktrees/W2-85")
LOG = ROOT / ".gov-runtime/scratch/lead/log"
NODE = "/home/usain/.nvm/versions/node/v22.23.3/bin"
ENV = dict(os.environ, TMPDIR="/tmp/gov-os-lead-W2-85", PATH=NODE + ":" + os.environ.get("PATH", ""),
           PYTHONPATH=str(ROOT / "src"))
for var in ("GOV_CLOSE_SERIAL_ONLY_OF", "GOV_CLOSE_SERIAL_ONLY_GIVEN", "GOV_CLOSE_CHECK_RESULT"):
    ENV.pop(var, None)
CASE = ("tests/acceptance/W2-54/test_w2_54_time_limit.py::"
        "test_the_check_run_as_declared_on_this_repository_ends_green_within_its_limit")


def load():
    return open("/proc/loadavg").read().split()[0]


t0 = time.time()
while float(load()) >= 20 and time.time() - t0 < 1800:
    time.sleep(60)
t1, l0 = time.time(), load()
done = subprocess.run([sys.executable, "-m", "pytest", CASE, "-q", "-p", "no:cacheprovider", "--no-header",
                       "-o", "tmp_path_retention_policy=failed", "-rs", f"--junitxml={LOG}/alone-time-limit-2.xml"],
                      cwd=ROOT, env=ENV, capture_output=True, text=True)
(LOG / "alone-time-limit-2.txt").write_text(f"load at start {l0}, at end {load()}, {int(time.time() - t1)} s\n"
                                             + done.stdout[-30000:] + "\n--- stderr\n" + done.stderr[-5000:])
(LOG / "alone-time-limit-2.rc").write_text(str(done.returncode))
