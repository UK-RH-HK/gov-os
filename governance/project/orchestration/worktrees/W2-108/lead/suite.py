"""The lead's scoped verification (DEC-952, DEC-968), in the close's form: the selected set in one parallel run, then
the selected serial-only cases alone, each with JUnit XML and an exit-code file.
usage: suite.py <selection json> <tag>   writes log/<tag>-parallel.{txt,xml,exit} and log/<tag>-serial.{txt,xml,exit}"""
import json
import os
import subprocess
import sys

ROOT = "/home/usain/gov-os-worktrees/W2-108"
LOG = ROOT + "/.gov-runtime/scratch/lead/log/"
LOCK = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh"
selection = json.load(open(sys.argv[1]))
tag = sys.argv[2]
options = selection["pytest_options"]
targets = [s["target"] for s in selection["selected"]]
ignored = [o.split("=", 1)[1].replace(ROOT + "/", "") for o in options if o.startswith("--ignore=")]
deselected = [o.split("=", 1)[1] for o in options if o.startswith("--deselect=")]

entries = []
for line in open(ROOT + "/tests/acceptance/serial-only.txt", encoding="utf-8"):
    entry = line.split(" #", 1)[0].strip()
    if not entry or entry.startswith("#"):
        continue
    path = entry.split("::", 1)[0]
    in_scope = any(entry.startswith(t.rstrip("/")) or t.startswith(entry) for t in targets)
    out = any(path == i or path.startswith(i.rstrip("/") + "/") for i in ignored) or entry in deselected
    if in_scope and not out:
        entries.append(entry)
open(LOG + tag + "-serial-entries.txt", "w").write("\n".join(entries) + "\n")

env = dict(os.environ)
env.update({
    "PATH": "/home/usain/.nvm/versions/node/v22.23.3/bin:" + env.get("PATH", ""),
    "PYTHONPATH": ROOT + "/src:" + ROOT + "/src/gov/close/pytest_plugin",
    "GOV_CLOSE_SERIAL_ONLY_OF": ROOT,
    "TMPDIR": "/tmp/gov-os-lead-W2-108",
})
common = ["-q", "-p", "no:cacheprovider", "-p", "gov_close_serial_only", "-o", "tmp_path_retention_policy=failed", "-rs"]


def run(name, args, extra_env):
    with open(LOG + tag + "-" + name + ".txt", "w") as out:
        code = subprocess.call(["bash", LOCK, "python3", "-m", "pytest", *args], cwd=ROOT, env={**env, **extra_env},
                               stdout=out, stderr=subprocess.STDOUT)
    open(LOG + tag + "-" + name + ".exit", "w").write(str(code) + "\n")
    return code


run("parallel", ["tests", "-n", "auto", *common, "--junitxml=" + LOG + tag + "-parallel.xml", *options], {})
if entries:
    run("serial", [*entries, *common, "--junitxml=" + LOG + tag + "-serial.xml", *options],
        {"GOV_CLOSE_SERIAL_ONLY_GIVEN": "\n".join(entries)})
else:
    open(LOG + tag + "-serial.exit", "w").write("no-entries\n")
