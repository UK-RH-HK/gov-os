"""The lead's verification of round 3 (DEC-952, DEC-968): one step per call, each with its own exit file.

Steps: rebuild | parallel | serial | check | collect. Output under .gov-runtime/scratch/lead/log/verify-4/.
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

WT = Path("/home/usain/gov-os-worktrees/W2-16")
LOG = WT / ".gov-runtime/scratch/lead/log/verify-4"
TOOLS = Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools")
SRC = str(WT / "src")
LOG.mkdir(parents=True, exist_ok=True)


def wait_for_capacity():
    while True:
        load = os.getloadavg()
        if min(load[0], load[2]) < os.cpu_count():
            return
        time.sleep(60)


def disk_gate(name):
    done = subprocess.run(["bash", str(TOOLS / "disk_gate.sh")], capture_output=True, text=True)
    (LOG / f"{name}.disk").write_text(done.stdout + done.stderr)
    return done.returncode == 0


def env(**extra):
    e = dict(os.environ)
    e.update({"PYTHONPATH": SRC, "TMPDIR": "/tmp/gov-os-lead-W2-16"})
    e.update(extra)
    return e


def run(name, cmd, environment):
    with open(LOG / f"{name}.txt", "w") as out:
        code = subprocess.run(cmd, cwd=str(WT), env=environment, stdout=out, stderr=subprocess.STDOUT).returncode
    (LOG / f"{name}.exit").write_text(f"{code}\n")
    return code


def options():
    data = json.loads((WT / ".gov-runtime/scratch/lead/log/select-4.json").read_text())
    return data["pytest_options"]


def serial_entries():
    """The list as the close reads it (gov_close_serial_only.entries): each line's ` #` comment dropped."""
    sys.path.insert(0, f"{SRC}/gov/close/pytest_plugin")
    import gov_close_serial_only
    return gov_close_serial_only.entries(WT)


def main(step):
    wait_for_capacity()
    if step in ("rebuild", "parallel", "serial") and not disk_gate(step):
        (LOG / f"{step}.exit").write_text("SHUT\n")
        return
    if step == "rebuild":
        gov_file = subprocess.run([sys.executable, "-c", "import gov; print(gov.__file__)"], env=env(),
                                  capture_output=True, text=True).stdout
        (LOG / "gov-file.txt").write_text(gov_file)
        run("rebuild", ["flock", "/tmp/gov-os-rebuild.lock", sys.executable, "-m", "gov.cli.main", "rebuild", "--json"],
            env())
    elif step in ("parallel", "serial"):
        plugin = f"{SRC}:{SRC}/gov/close/pytest_plugin"
        e = env(PATH="/home/usain/.nvm/versions/node/v22.23.3/bin:" + os.environ["PATH"], PYTHONPATH=plugin,
                GOV_CLOSE_SERIAL_ONLY_OF=str(WT))
        base = ["bash", str(TOOLS / "verify_lock.sh"), sys.executable, "-m", "pytest"]
        common = ["-q", "-p", "no:cacheprovider", "-p", "gov_close_serial_only", "-o",
                  "tmp_path_retention_policy=failed", "-rfEs"]
        if step == "parallel":
            cmd = base + ["tests", "-n", "auto"] + common + [f"--junitxml={LOG}/parallel.xml"] + options()
        else:
            entries = serial_entries()
            e["GOV_CLOSE_SERIAL_ONLY_GIVEN"] = "\n".join(entries)
            cmd = base + entries + common + [f"--junitxml={LOG}/serial.xml"] + options()
        run(step, cmd, e)
    elif step == "check":
        run("check", [sys.executable, "-m", "gov.cli.main", "check", "--json"], env())
    elif step == "collect":
        run("collect", [sys.executable, "-m", "pytest", "tests", "--collect-only", "-q", "-p", "no:cacheprovider",
                        "--no-header"], env())


if __name__ == "__main__":
    for step in sys.argv[1:]:
        main(step)
