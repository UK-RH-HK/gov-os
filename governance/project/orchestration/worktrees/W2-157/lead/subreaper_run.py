"""Run the W2-157 acceptance folder as gov accept does: this process the child subreaper, never reaping orphans
during the run, pytest in its own session, a junit report; print each failed case and its message."""
import ctypes
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

root = "/home/usain/gov-os-worktrees/W2-157"
out = "/tmp/w2-157-lead/subreaper"
os.makedirs(out, exist_ok=True)
ctypes.CDLL(None, use_errno=True).prctl(36, 1, 0, 0, 0)  # PR_SET_CHILD_SUBREAPER
env = {k: v for k, v in os.environ.items() if not k.startswith(("PYTEST_", "PYTHON"))}
env.update(PYTHONUSERBASE="/home/usain/.local", PYTHONPATH=root + "/src", PYTHONDONTWRITEBYTECODE="1", TMPDIR=out)
report = out + "/report.xml"
args = sys.argv[1:] or ["tests/acceptance/W2-157"]
code = subprocess.Popen([sys.executable, "-B", "-m", "pytest", *args, f"--rootdir={root}", "-p", "no:cacheprovider",
                         f"--junitxml={report}", "-q"], cwd=root, env=env, stdin=subprocess.DEVNULL,
                        stdout=open(out + "/stdout.txt", "w"), stderr=subprocess.STDOUT, start_new_session=True).wait()
print("exit", code)
for case in ET.parse(report).iter("testcase"):
    for child in case:
        if child.tag in ("failure", "error"):
            print("FAILED", case.get("classname"), case.get("name"))
            print((child.text or child.get("message") or "")[-2500:])
