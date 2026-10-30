"""Claims the given tickets (tk start), commits each claim on its own, then makes each one's worktree from
w2/integrate (git worktree add ~/gov-os-worktrees/<W2> -b w2/<W2> w2/integrate). Prints each worktree's head.
Usage: claim_2026-10-29.py W2-61 W2-61h ...  (ids from log/tickets-2026-10-29.json)."""
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS")
ids = json.loads((ROOT / ".gov-runtime/scratch/orchestrator/log/tickets-2026-10-29.json").read_text())
CO = "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"


def run(args, cwd=ROOT):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("failed: " + " ".join(args)[:120] + "\n" + r.stdout + r.stderr)
    return r.stdout.strip()


for w2 in sys.argv[1:]:
    tid = ids[w2]
    path = ".tickets/" + tid + ".md"
    run(["tk", "start", tid])
    run(["git", "commit", "-q", "-m", tid + " (" + w2 + "): claimed for its first run (DEC-941); Definition of Ready checked by hand with dor_hand.py, READY (DEC-944)",
         "--trailer", "Task: " + tid, "--trailer", "Implements: DEC-941, DEC-944", "--trailer", "Role: orchestrator",
         "--trailer", CO, "--", path])
    print(run(["git", "log", "-1", "--format=%h %s"]))
for w2 in sys.argv[1:]:
    wt = "/home/usain/gov-os-worktrees/" + w2
    run(["git", "worktree", "add", wt, "-b", "w2/" + w2, "w2/integrate"])
    print(w2, run(["git", "rev-parse", "--short=12", "HEAD"], cwd=wt))
