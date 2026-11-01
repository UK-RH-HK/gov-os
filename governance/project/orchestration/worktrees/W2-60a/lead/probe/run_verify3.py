"""Round 3's scoped verification in the close's form (DEC-952, DEC-968): the selection's pytest_options added to the
parallel run, then the selected serial-route entries alone. Usage: run_verify3.py <selection.json>.
Writes log/verify3-<phase>.txt, .exit and log/parallel3.xml, log/serial3.xml.
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = "/home/usain/gov-os-worktrees/W2-60a"
LOG = Path(ROOT) / ".gov-runtime/scratch/lead/log"
LOCK = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh"


def serial_entries(selection):
    ignored = [p.split("=", 1)[1] for p in selection["pytest_options"] if p.startswith("--ignore=")]
    deselected = set(selection.get("deselect") or [])
    found = []
    for line in (Path(ROOT) / "tests/acceptance/serial-only.txt").read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#") or " #" not in line:
            continue
        entry, comment = (part.strip() for part in line.split(" #", 1))
        if not comment.startswith("serial"):
            continue
        full = f"{ROOT}/{entry}"
        if any(full == ig or full.startswith(ig.rstrip("/") + "/") or full.startswith(ig + "::") for ig in ignored):
            continue
        if entry in deselected:
            continue
        found.append(entry)
    return found


def run(phase, env, command):
    started = time.time()
    with open(LOG / f"verify3-{phase}.txt", "w", encoding="utf-8") as out:
        code = subprocess.run(command, cwd=ROOT, env=env, stdout=out, stderr=subprocess.STDOUT,
                              stdin=subprocess.DEVNULL).returncode
    (LOG / f"verify3-{phase}.exit").write_text(f"exit {code} {time.time() - started:.0f}s\n", encoding="utf-8")


def main():
    selection = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    options = selection["pytest_options"]
    env = dict(os.environ)
    env["PATH"] = "/home/usain/.nvm/versions/node/v22.23.3/bin:" + env.get("PATH", "")
    env["PYTHONPATH"] = f"{ROOT}/src:{ROOT}/src/gov/close/pytest_plugin"
    env["GOV_CLOSE_SERIAL_ONLY_OF"] = ROOT
    env["TMPDIR"] = "/tmp/gov-os-lead-W2-60a"
    common = ["-q", "-p", "no:cacheprovider", "-p", "gov_close_serial_only", "-o", "tmp_path_retention_policy=failed",
              "-rs"]
    prefix = [] if os.environ.get("V3_NO_LOCK") else ["bash", LOCK]
    run("parallel", env, [*prefix, "python3", "-m", "pytest", "tests", "-n", "auto", *common, *options,
                          f"--junitxml={LOG}/parallel3.xml"])
    listed = serial_entries(selection)
    (LOG / "verify3-serial-entries.txt").write_text("\n".join(listed) + "\n", encoding="utf-8")
    if listed:
        senv = {**env, "GOV_CLOSE_SERIAL_ONLY_GIVEN": "\n".join(listed)}
        run("serial", senv, [*prefix, "python3", "-m", "pytest", *listed, *common, *options,
                             f"--junitxml={LOG}/serial3.xml"])
    else:
        (LOG / "verify3-serial.exit").write_text("exit none-selected 0s\n", encoding="utf-8")


if __name__ == "__main__":
    main()
