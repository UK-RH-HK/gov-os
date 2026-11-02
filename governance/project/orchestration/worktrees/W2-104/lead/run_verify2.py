"""The lead's run-2 verification for W2-104, in the close's form (DEC-952, DEC-889 items 6 and 12, DEC-905).

    python3 run_verify2.py w1_26|parallel|serial

Output (JUnit XML) goes outside the worktree, to /tmp/gov-os-lead-W2-104/run2/. Reads select_tests.py's output
(log/select-3.json), adds its pytest_options, and runs under verify_lock.sh (a heavy-job slot).
w1_26: W1-26's folder alone (-n auto), no selection options.
parallel: the scoped set (-n auto). serial: the serial-only entries the selection keeps, without -n.
"""
import json
import os
import subprocess
import sys

TREE = "/home/usain/gov-os-worktrees/W2-104"
LOG = TREE + "/.gov-runtime/scratch/lead/log"
OUT = "/tmp/gov-os-lead-W2-104/run2"
LOCK = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh"
sys.path.insert(0, TREE + "/src/gov/close/pytest_plugin")
import gov_close_serial_only as plugin  # noqa: E402

os.makedirs(OUT, exist_ok=True)
mode = sys.argv[1]
selection = json.load(open(LOG + "/select-3.json"))
options = selection["pytest_options"]


def values(flag):
    found = []
    for i, o in enumerate(options):
        if o == flag:
            found.append(options[i + 1])
        elif o.startswith(flag + "="):
            found.append(o.split("=", 1)[1])
    return [p[len(TREE) + 1:] if p.startswith(TREE + "/") else p for p in found]


ignored = values("--ignore")
deselected = values("--deselect")

env = dict(os.environ)
env["PATH"] = "/home/usain/.nvm/versions/node/v22.23.3/bin:" + env.get("PATH", "")
env["PYTHONPATH"] = TREE + "/src:" + TREE + "/src/gov/close/pytest_plugin"
env["GOV_CLOSE_SERIAL_ONLY_OF"] = TREE
env["TMPDIR"] = "/tmp/gov-os-lead-W2-104"
base = ["bash", LOCK, "python3", "-m", "pytest"]
common = ["-q", "-p", "no:cacheprovider", "-p", "gov_close_serial_only", "-o", "tmp_path_retention_policy=failed",
          "-rs"]

if mode == "w1_26":
    command = base + ["tests/acceptance/W1-26", "-n", "auto"] + common + ["--junitxml=" + OUT + "/w1_26.xml"]
elif mode == "parallel":
    command = base + ["tests", "-n", "auto"] + common + ["--junitxml=" + OUT + "/parallel.xml"] + options
else:
    def kept(entry):
        path = entry.split("::", 1)[0]
        if any(path == i.rstrip("/") or path.startswith(i.rstrip("/") + "/") for i in ignored):
            return False
        return not any(plugin.declares(d, entry) for d in deselected)
    entries = [e for e in plugin.entries(TREE) if kept(e)]
    print("serial entries kept:", len(entries), "of", len(plugin.entries(TREE)), flush=True)
    if not entries:
        sys.exit(0)
    env["GOV_CLOSE_SERIAL_ONLY_GIVEN"] = "\n".join(entries)
    command = base + entries + common + ["--junitxml=" + OUT + "/serial.xml"] + options
print("running:", " ".join(command[:12]), "...", len(command), "arguments", flush=True)
sys.exit(subprocess.run(command, cwd=TREE, env=env).returncode)
