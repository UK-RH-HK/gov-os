"""Commits DEC-943 to DEC-946's records first, then the three new tickets (W2-82, W2-83a, W2-83b), then the four ticket
edits, each with its own Task. Run only after the checks are green (the context check's untracked-ticket errors aside,
which clear once the tickets are committed and the store rebuilt)."""
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS")
ids = json.loads((ROOT / ".gov-runtime/scratch/orchestrator/log/tickets-2026-10-29b.json").read_text())
CO = "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
OWNER = "Decided-by: owner (chat, 2026-10-29)"


def commit(msg, trailers, paths):
    args = ["git", "commit", "-q", "-m", msg]
    for t in trailers + ["Role: orchestrator", CO]:
        args += ["--trailer", t]
    r = subprocess.run(args + ["--"] + paths, cwd=ROOT, capture_output=True, text=True)
    if r.returncode:
        sys.exit("commit failed: " + msg[:70] + "\n" + r.stdout + r.stderr)
    print(subprocess.run(["git", "log", "-1", "--format=%h %s"], cwd=ROOT, capture_output=True, text=True).stdout.strip()[:110])


commit("Decision records DEC-943 (brief gaps, the orchestrator's drift), DEC-944 (the Gov OS as a software company: the "
       "mapping; a light Definition of Ready and the kernel's playbook form in EXAMIN's minimum), DEC-945 (Pushover "
       "reversed: ACT-PUSHOVER-1 and its sender removed), DEC-946 (standing priorities until EXAMIN's copy; the Wave 3 "
       "parking list; the nightly frozen); prompt v3.40, the lead brief's brief_gaps section, K9 and the three cards",
       ["Task: decision-record", "Implements: DEC-943, DEC-944, DEC-945, DEC-946", OWNER],
       ["docs/DECISION_REGISTER.md", "docs/plan/WAVE_2_WBS.md", "docs/plan/WAVE_3_PARKING.md",
        "governance/project/briefs/LEAD-w2-common.md", "governance/project/prompts/w2-orchestrator.md",
        "governance/project/orchestration/nightly/", "governance/project/orchestration/brief-gaps.md",
        "governance/project/orchestration/packages/COMPANY-MAP-2026-10-29.md",
        "governance/project/orchestration/packages/ACT-PUSHOVER-1.md"])
for w2, tid in ids.items():
    commit(tid + " (" + w2 + "): new ticket file (DEC-944)", ["Task: " + tid, "Implements: DEC-944"],
           [".tickets/" + tid + ".md"])
EDITS = [
    ("DAEO-av72", "W2-79: a KPI that each fixed brief gap stays fixed (DEC-943 item 1)", "DEC-943"),
    ("DAEO-0uhh", "W2-64: the schema glob narrowed to close.schema.json, split by file beside W2-78 and W2-83a (DEC-942)", "DEC-942"),
    ("DAEO-siiz", "W2-52: the third copy of the adopt skill it changes named as an allowed path, for its merge-back", "DEC-814, DEC-941"),
    ("DAEO-2ds6", "W2-26: its evidence record named for the close's evidence gate, for its merge-back", "DEC-941"),
]
for tid, what, impl in EDITS:
    commit(tid + ": " + what, ["Task: " + tid, "Implements: " + impl], [".tickets/" + tid + ".md"])
print("status: " + subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True).stdout.strip())
