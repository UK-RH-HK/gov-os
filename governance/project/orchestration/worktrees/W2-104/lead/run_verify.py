"""The lead's scoped verification for W2-104, in the close's form (DEC-952, DEC-889 items 6 and 12, DEC-905).

    python3 run_verify.py parallel|serial

Reads select_tests.py's output (log/select.json), adds its pytest_options, and runs under verify_lock.sh.
The serial run is given the serial-only entries that the selection keeps (none under an --ignore path, none
deselected), as GOV_CLOSE_SERIAL_ONLY_GIVEN and as arguments, without -n.
"""
import json
import os
import subprocess
import sys

TREE = "/home/usain/gov-os-worktrees/W2-104"
LOG = TREE + "/.gov-runtime/scratch/lead/log"
LOCK = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh"
sys.path.insert(0, TREE + "/src/gov/close/pytest_plugin")
import gov_close_serial_only as plugin  # noqa: E402

mode = sys.argv[1]
selection = json.load(open(LOG + "/select.json"))
options = selection["pytest_options"]
ignored = [options[i + 1] if options[i] == "--ignore" else options[i].split("=", 1)[1]
           for i in range(len(options)) if options[i] == "--ignore" or options[i].startswith("--ignore=")]
deselected = [options[i + 1] if options[i] == "--deselect" else options[i].split("=", 1)[1]
              for i in range(len(options)) if options[i] == "--deselect" or options[i].startswith("--deselect=")]
# select_tests.py gives absolute paths; the serial-only list gives paths relative to the tree.
ignored = [p[len(TREE) + 1:] if p.startswith(TREE + "/") else p for p in ignored]
deselected = [p[len(TREE) + 1:] if p.startswith(TREE + "/") else p for p in deselected]

env = dict(os.environ)
env["PATH"] = "/home/usain/.nvm/versions/node/v22.23.3/bin:" + env.get("PATH", "")
env["PYTHONPATH"] = TREE + "/src:" + TREE + "/src/gov/close/pytest_plugin"
env["GOV_CLOSE_SERIAL_ONLY_OF"] = TREE
env["TMPDIR"] = "/tmp/gov-os-lead-W2-104"
base = ["bash", LOCK, "python3", "-m", "pytest"]
common = ["-q", "-p", "no:cacheprovider", "-p", "gov_close_serial_only", "-o", "tmp_path_retention_policy=failed",
          "-rs"]

if mode == "parallel":
    command = base + ["tests", "-n", "auto"] + common + ["--junitxml=" + LOG + "/parallel.xml"] + options
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
    command = base + entries + common + ["--junitxml=" + LOG + "/serial.xml"] + options
print("running:", " ".join(command[:12]), "...", len(command), "arguments", flush=True)
sys.exit(subprocess.run(command, cwd=TREE, env=env).returncode)
