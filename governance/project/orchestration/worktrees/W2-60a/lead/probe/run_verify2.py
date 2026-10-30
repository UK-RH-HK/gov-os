"""The lead's full run in the close's form, both phases in one job, while hold_lock.sh holds the verification lock
(DEC-889 items 6 and 12, DEC-905). The lock is the holder's, so no second flock is taken here.
Writes log/verify2-<phase>.txt, .exit and log/parallel2.xml, log/serial2.xml.
"""
import os
import subprocess
import time
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


def run(phase, env):
    common = ["-q", "-p", "no:cacheprovider", "-p", "gov_close_serial_only", "-o", "tmp_path_retention_policy=failed",
              "-rs"]
    if phase == "parallel":
        command = ["python3", "-m", "pytest", "tests", "-n", "auto", *common, f"--junitxml={LOG}/parallel2.xml"]
    else:
        listed = entries()
        env = {**env, "GOV_CLOSE_SERIAL_ONLY_GIVEN": "\n".join(listed)}
        command = ["python3", "-m", "pytest", *listed, *common, f"--junitxml={LOG}/serial2.xml"]
    started = time.time()
    with open(LOG / f"verify2-{phase}.txt", "w", encoding="utf-8") as out:
        code = subprocess.run(command, cwd=ROOT, env=env, stdout=out, stderr=subprocess.STDOUT,
                              stdin=subprocess.DEVNULL).returncode
    (LOG / f"verify2-{phase}.exit").write_text(f"exit {code} {time.time() - started:.0f}s\n", encoding="utf-8")


def main():
    env = dict(os.environ)
    env["PATH"] = "/home/usain/.nvm/versions/node/v22.23.3/bin:" + env.get("PATH", "")
    env["PYTHONPATH"] = f"{ROOT}/src:{ROOT}/src/gov/close/pytest_plugin"
    env["GOV_CLOSE_SERIAL_ONLY_OF"] = ROOT
    env["TMPDIR"] = "/tmp/gov-os-lead-W2-60a"
    run("parallel", env)
    run("serial", env)


if __name__ == "__main__":
    main()
