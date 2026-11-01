"""Run 3's scoped run in the close's form (DEC-952, DEC-889, DEC-968): the parallel run, then the selected serial-only cases alone.

Reads select_tests.py's JSON (log/select4.json); writes log/parallel4.xml, log/serial4.xml, their outputs and exit codes.
"""
import json
import os
import subprocess
import sys

TREE = "/home/usain/gov-os-worktrees/W2-96"
LOG = TREE + "/.gov-runtime/scratch/lead/log/"
LOCK = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh"

selection = json.load(open(LOG + "select4.json", encoding="utf-8"))
options = selection["pytest_options"]
ignored = [p.rstrip("/") for p in selection["ignore"]]
deselected = set(selection["deselect"])

env = dict(os.environ)
env.update({
    "PATH": "/home/usain/.nvm/versions/node/v22.23.3/bin:" + env.get("PATH", ""),
    "PYTHONPATH": TREE + "/src:" + TREE + "/src/gov/close/pytest_plugin",
    "GOV_CLOSE_SERIAL_ONLY_OF": TREE,
    "TMPDIR": "/tmp/gov-os-lead-W2-96",
})
base = ["bash", LOCK, sys.executable, "-m", "pytest"]
common = ["-q", "-p", "no:cacheprovider", "-o", "tmp_path_retention_policy=failed", "-rs",
          # the close's per-test limit (gov.close.command), from select_tests.py's per_test_timeout
          "--timeout=" + str(selection["per_test_timeout"]), "--timeout_method=signal"]


def run(name, argv, extra_env):
    with open(LOG + name + ".out", "w", encoding="utf-8") as out:
        done = subprocess.run(argv, cwd=TREE, env={**env, **extra_env}, stdout=out, stderr=subprocess.STDOUT)
    open(LOG + name + ".exit", "w").write(f"{done.returncode}\n")
    return done.returncode


part = sys.argv[1] if len(sys.argv) > 1 else "both"
if part in ("both", "parallel"):
    run("parallel4", base + ["tests", "-n", "auto", "-p", "gov_close_serial_only", *common,
                             "--junitxml=" + LOG + "parallel4.xml", *options], {})

if part in ("both", "serial"):
    entries = []
    for line in open(TREE + "/tests/acceptance/serial-only.txt", encoding="utf-8"):
        entry = line.split("#", 1)[0].strip()
        if not entry:
            continue
        path = entry.split("::", 1)[0].rstrip("/")
        if any(path == p or path.startswith(p + "/") for p in ignored) or entry in deselected:
            continue
        entries.append(entry)
    open(LOG + "serial4-entries.txt", "w", encoding="utf-8").write("\n".join(entries) + "\n")
    if entries:
        run("serial4", base + [*entries, *common, "--junitxml=" + LOG + "serial4.xml", *options],
            {"GOV_CLOSE_SERIAL_ONLY_GIVEN": "\n".join(entries)})
    else:
        open(LOG + "serial4.exit", "w").write("none-selected\n")
