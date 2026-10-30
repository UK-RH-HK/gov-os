"""The lead's full verification run in the close's form (DEC-889 items 6 and 12, DEC-905).

Usage: python3 run_verify.py parallel|serial
- parallel: every suite under tests/, -n auto, with the close's serial-only plugin, retention 'failed', JUnit XML.
- serial: the serial-only list's entries alone, without -n, GOV_CLOSE_SERIAL_ONLY_GIVEN set to them.
Both under flock /tmp/gov-os-verify.lock, with this worktree's src/ (DEC-732) and TMPDIR the lead's temp folder.
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = "/home/usain/gov-os-worktrees/W2-60a"
LOG = Path(ROOT) / ".gov-runtime/scratch/lead/log"


def entries():
    found = []
    for line in (Path(ROOT) / "tests/acceptance/serial-only.txt").read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        entry = line.split(" #", 1)[0].strip()
        if entry:
            found.append(entry)
    return found


def main(phase):
    env = dict(os.environ)
    env["PATH"] = "/home/usain/.nvm/versions/node/v22.23.3/bin:" + env.get("PATH", "")
    env["PYTHONPATH"] = f"{ROOT}/src:{ROOT}/src/gov/close/pytest_plugin"
    env["GOV_CLOSE_SERIAL_ONLY_OF"] = ROOT
    env["TMPDIR"] = "/tmp/gov-os-lead-W2-60a"
    base = ["flock", "/tmp/gov-os-verify.lock", "python3", "-m", "pytest"]
    common = ["-q", "-p", "no:cacheprovider", "-p", "gov_close_serial_only", "-o", "tmp_path_retention_policy=failed",
              "-rs"]
    if phase == "parallel":
        command = [*base, "tests", "-n", "auto", *common, f"--junitxml={LOG}/parallel.xml"]
    else:
        listed = entries()
        env["GOV_CLOSE_SERIAL_ONLY_GIVEN"] = "\n".join(listed)
        command = [*base, *listed, *common, f"--junitxml={LOG}/serial.xml"]
    with open(LOG / f"verify-{phase}.txt", "w", encoding="utf-8") as out:
        code = subprocess.run(command, cwd=ROOT, env=env, stdout=out, stderr=subprocess.STDOUT,
                              stdin=subprocess.DEVNULL).returncode
    (LOG / f"verify-{phase}.exit").write_text(f"exit {code}\n", encoding="utf-8")
    print(phase, "exit", code)


if __name__ == "__main__":
    main(sys.argv[1])
