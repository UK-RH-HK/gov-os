"""ACT 1: time the five-rule hook on a sample event, as the measured role engineer. Prints seconds per call."""
import os
import subprocess
import time

ROOT = "/home/usain/Dynamic-Agentic-Engineering-OS"
PY = open(os.path.expanduser("~/.local/bin/gov")).readline()[2:].strip()
event = open(ROOT + "/.gov-runtime/scratch/orchestrator/drafts/act1-sample-event.json").read()
env = dict(os.environ, GOV_ROLE="engineer", GOV_TICKET="DAEO-sdxk", CLAUDE_PROJECT_DIR=ROOT)
times = []
for _ in range(5):
    t = time.time()
    p = subprocess.run([PY, "-E", ROOT + "/.claude/hooks/pretooluse.py"], input=event, capture_output=True, text=True,
                       env=env)
    times.append(time.time() - t)
print("exit", p.returncode, "out", repr(p.stdout[:80]), "seconds", [round(x, 2) for x in times])
