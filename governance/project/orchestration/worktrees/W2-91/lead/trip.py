"""Runs the tripwire compare against a snapshot and prints its changes, one line each, by tree."""
import json
import subprocess
import sys

done = subprocess.run(["python3", "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/tripwire.py",
                       "compare", sys.argv[1]], capture_output=True, text=True)
print("exit", done.returncode)
try:
    changes = json.loads(done.stdout).get("changes", [])
except ValueError:
    print(done.stdout[:2000], done.stderr[:2000])
    sys.exit(1)
for c in changes:
    print(c.get("tree"), "|", c.get("change"), "|", c.get("line") or c.get("folder") or f"{c.get('before')} -> {c.get('after')}")
