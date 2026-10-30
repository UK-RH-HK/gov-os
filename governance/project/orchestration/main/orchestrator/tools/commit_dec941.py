"""Commits DEC-939 to DEC-941's records first (the register before any ticket that cites DEC-941), then each new
ticket file on its own with its own Task. Run only after checks_dec941.sh is green. Stops at the first failure."""
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS")
ids = json.loads((ROOT / ".gov-runtime/scratch/orchestrator/log/tickets-2026-10-29.json").read_text())
CO = "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
RECORDS = ["docs/DECISION_REGISTER.md", "docs/plan/WAVE_2_LIST.md", "docs/plan/WAVE_2_WBS.md",
           "governance/project/briefs/LEAD-w2-common.md", "governance/project/prompts/w2-orchestrator.md",
           "governance/project/orchestration/nightly/", "governance/project/orchestration/packages/ACT-PUSHOVER-1.md",
           "governance/project/orchestration/packages/ACT-RUNS-SWEEP-1.md",
           "governance/project/orchestration/packages/P-SCOPE-RECORDS-1.md",
           "governance/project/orchestration/packages/P-TOOLS-REVIEW-1.md",
           "governance/project/orchestration/packages/REPLAN-W2.md"]


def commit(msg, trailers, paths):
    args = ["git", "commit", "-q", "-m", msg]
    for t in trailers:
        args += ["--trailer", t]
    r = subprocess.run(args + ["--"] + paths, cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("commit failed: " + msg[:80] + "\n" + r.stdout + r.stderr)
    print(subprocess.run(["git", "log", "-1", "--format=%h %s"], cwd=ROOT, capture_output=True, text=True).stdout.strip()[:140])


commit("Decision records DEC-939 (owner: answers to P1-MORNING-2026-10-29), DEC-940 (the state of the Gov OS) and "
       "DEC-941 (the re-plan accepted with eight amendments); prompt v3.38, the lead brief's guard command forms, "
       "K9's entry criteria and the new cards, rows W2-M408, W2-L451, W2-L452, the nightly's rebuild lock, "
       "lock-wait, emergency push and runs_sweep.sh, ACT-PUSHOVER-1, ACT-RUNS-SWEEP-1, REPLAN-W2, "
       "P-SCOPE-RECORDS-1, P-TOOLS-REVIEW-1",
       ["Task: decision-record", "Implements: DEC-939, DEC-940, DEC-941", "Role: orchestrator",
        "Decided-by: owner (chat, 2026-10-29)", CO], RECORDS)
for w2, tid in ids.items():
    path = ".tickets/" + tid + ".md"
    title = re.search(r"^title: '(.*)'$", (ROOT / path).read_text(encoding="utf-8"), re.M).group(1).replace("''", "'")
    commit(tid + " (" + w2 + "): new ticket file under the re-plan (DEC-941): " + title,
           ["Task: " + tid, "Implements: DEC-941", "Role: orchestrator", CO], [path])
print("status: " + subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True).stdout.strip())
