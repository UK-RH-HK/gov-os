"""Commits DEC-950's application: the plan card and the parking list first, then W2-84's ticket file, W2-61h's
dependency and W2-20's amendment, each with its own Task."""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS")
CO = "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
STEPS = [
    ("W2-84's card (DEC-950) and Wave 3 parking list W3-P11", ["Task: decision-record", "Implements: DEC-950, DEC-946"],
     ["docs/plan/WAVE_2_WBS.md", "docs/plan/WAVE_3_PARKING.md"]),
    ("DAEO-m1u3 (W2-84): new ticket file: the hidden-set refusal in every tree (DEC-950 item 1)",
     ["Task: DAEO-m1u3", "Implements: DEC-950"], [".tickets/DAEO-m1u3.md"]),
    ("DAEO-h2k3 (W2-61h): depends on W2-84, the hidden-set refusal in every tree (DEC-950 item 1)",
     ["Task: DAEO-h2k3", "Implements: DEC-950"], [".tickets/DAEO-h2k3.md"]),
    ("DAEO-r30l (W2-20): KPIs amended for run 3, aligned with DEC-942 and DEC-947 (DEC-950 item 2)",
     ["Task: DAEO-r30l", "Implements: DEC-950, DEC-942, DEC-947"], [".tickets/DAEO-r30l.md"]),
]
for msg, trailers, paths in STEPS:
    args = ["git", "commit", "-q", "-m", msg]
    for t in trailers + ["Role: orchestrator", CO]:
        args += ["--trailer", t]
    r = subprocess.run(args + ["--"] + paths, cwd=ROOT, capture_output=True, text=True)
    if r.returncode:
        sys.exit("commit failed: " + msg[:60] + "\n" + r.stdout + r.stderr)
    print(subprocess.run(["git", "log", "-1", "--format=%h %s"], cwd=ROOT, capture_output=True, text=True).stdout.strip()[:100])
