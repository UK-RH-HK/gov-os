"""The lead's verification of W2-87 in the close's form (scope full, DEC-952): after this worktree's rebuild, the
parallel run of `tests` (the selection's pytest_options), then the serial-only cases alone, then the ticket's own
acceptance tests; each with JUnit XML and an exit-code file under log/. Run in the background."""
import os
import subprocess
import sys
import time
from pathlib import Path

WT = Path("/home/usain/gov-os-worktrees/W2-87")
LOG = WT / ".gov-runtime/scratch/lead/log"
while not (LOG / "rebuild-1.exit").exists() or not (LOG / "rebuild-1.exit").read_text().strip():
    time.sleep(30)

env = {**os.environ,
       "PATH": "/home/usain/.nvm/versions/node/v22.23.3/bin:" + os.environ["PATH"],
       "PYTHONPATH": f"{WT}/src:{WT}/src/gov/close/pytest_plugin",
       "GOV_CLOSE_SERIAL_ONLY_OF": str(WT), "TMPDIR": "/tmp/gov-os-lead-W2-87"}
env.pop("GOV_CLOSE_SERIAL_ONLY_GIVEN", None)
common = ["-q", "-p", "no:cacheprovider", "-p", "gov_close_serial_only", "-o", "tmp_path_retention_policy=failed",
          "-rs", "--timeout=900"]
selection = []  # select-2.json's pytest_options at cffef92c8534 (select-1 at 060e03ef57ea had --ignore of W2-87's own)


def run(name, argv, extra_env=None):
    started = time.time()
    with open(LOG / f"{name}.txt", "w") as out:
        code = subprocess.run(argv, cwd=WT, env={**env, **(extra_env or {})}, stdout=out, stderr=subprocess.STDOUT,
                              stdin=subprocess.DEVNULL).returncode
    (LOG / f"{name}.exit").write_text(f"{code} {time.time() - started:.0f}s\n")


phase = sys.argv[1]  # one phase per background run, so none passes the Bash tool's two-hour limit
if phase == "parallel":
    run("parallel", ["flock", "/tmp/gov-os-verify.lock", "python3", "-m", "pytest", "tests", "-n", "auto", *common,
                     *selection, f"--junitxml={LOG}/parallel.xml"])
elif phase == "serial":
    entries = []
    for line in (WT / "tests/acceptance/serial-only.txt").read_text().splitlines():
        entry = line.split(" #", 1)[0].strip()
        if entry and not entry.startswith("#") and not entry.startswith("tests/acceptance/W2-87"):
            entries.append(entry)
    run("serial", ["flock", "/tmp/gov-os-verify.lock", "python3", "-m", "pytest", *entries, *common, *selection,
                   f"--junitxml={LOG}/serial.xml"], {"GOV_CLOSE_SERIAL_ONLY_GIVEN": "\n".join(entries)})
elif phase == "own":
    run("own", ["python3", "-m", "pytest", "tests/acceptance/W2-87", "-q", "-p", "no:cacheprovider",
                "-o", "tmp_path_retention_policy=failed", "-rA", f"--junitxml={LOG}/own.xml"])
