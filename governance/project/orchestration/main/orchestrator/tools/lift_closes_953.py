#!/usr/bin/env python3
"""DEC-1132 (1): the lift's closes by DEC-953's practices: a close record each, then `tk close`, then one commit per
ticket with its Task: trailer. Run from the main tree; stops at the first failure."""
import subprocess, sys, datetime

R = "/home/usain/Dynamic-Agentic-Engineering-OS"
ACC = ".gov-runtime/scratch/orchestrator/log/lift-accepts-1/summary.txt (`gov accept` on w2/integrate at 74110bb34, 15:19-15:29 UTC 11-11, through the heavy slot)"
D10 = ("D-10 run 2 (day head `078e972d5647`, 11-10 23:13): 9,612 + 134 passed, verdict red 2, the two reds the warm-query "
       "latency of W1-19 and W2-13 that the owner ruled a named red (DEC-1125 (1)); the owner counts it as this ticket's "
       "green run (DEC-1126 (7), DEC-1083 (7))")

T = [
 ("W2-122", "DAEO-blwa", "STANDARD", f"`gov accept W2-122`: 22 passed, 0 failed, 0 skipped ({ACC}).",
  "S3 (the measure) met in part, by the evidence note's own words: a cold rebuild strictly alone was not measured and the seed base was the cold run's tree (`docs/changes/W2-122-evidence.md`)."),
 ("W2-123", "DAEO-qzrq", "STANDARD", f"`gov accept W2-123`: 50 passed, 0 failed, 0 skipped ({ACC}).",
  "S7 is also the start half of W2-20's S12 (D9-FATES)."),
 ("W2-126", "DAEO-jpr0", "STANDARD", f"`gov accept W2-126`: 28 passed, 0 failed, 0 skipped ({ACC}).",
  "S6 met in part: its per-day 'after' figure needs the shared embedder's log after the cache lands (`docs/changes/W2-126-evidence.md`)."),
 ("W2-92", "DAEO-n0wb", "STANDARD", f"`gov accept W2-92`: 144 passed, 0 failed, 0 skipped ({ACC}); `tests/conftest.py` `_CBM_SUITES` carries W2-92 since `aef1d2517`.",
  "none."),
 ("W2-96", "DAEO-ouet", "FULL", f"`gov accept W2-96`: 190 passed, 0 failed, 0 skipped, run with SIGINT and SIGHUP at their defaults ({ACC}); last probe `8f6e66a17` (pass); the three later commits are README and record wording, reviewed READY (`reviews/D10-lift-maps-review.md`).",
  "S6 is a brief line with no case; met by reading (`role-engineer.md` names `{CMD:accept}`; `LEAD-w2-common.md` names it)."),
 ("W1-01b", "DAEO-vhad", "STANDARD", D10 + ".", "none."),
 ("W2-66b", "DAEO-zuiy", "STANDARD", D10 + ".",
  "the literal `.ps1` suffix rule was not built; D-10's W2-66c fix covers the same record-only case another way (batch prep, `drafts/batch-prep/BATCH-PREP.md`)."),
 ("W2-90c", "DAEO-fu3n", "STANDARD", D10 + ".", "closed on the owner's word with its cases covered by D-10 run 2."),
 ("W2-151", "DAEO-qzca", "LITE", "a recorded CTO close (DEC-1112 (3)): no acceptance folder (LITE); its two lines hold on the CTO's read-only checks in LIFT-CLOSES-1 §3 (`gov links --all`: 0 STATUS_CONFLICT; MR-1 to MR-6 regenerated from `contract.yaml`).",
  "none."),
 ("feon", "DAEO-feon", "-", "not needed: the repair ticket of the CTO's refused `gov close DAEO-blwa` (11-11 13:38); its findings (WORK_WITHOUT_TASK, LOAD_SENSITIVE_REFUSED) are gates lifted here by DEC-953 and DEC-1052 Q-8; W2-122 closed by DEC-953 (DEC-1132 (1)).",
  "none."),
]

def run(*a):
    r = subprocess.run(a, cwd=R, capture_output=True, text=True)
    if r.returncode:
        print("FAILED:", " ".join(a), r.stdout[-400:], r.stderr[-400:]); sys.exit(1)
    return r.stdout

head = run("git", "rev-parse", "--short", "HEAD").strip()
for w2, tid, prof, evidence, part in T:
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    name = f"governance/project/orchestration/closes/{w2}-{tid}.md" if w2 != "feon" else f"governance/project/orchestration/closes/repair-{tid}.md"
    open(f"{R}/{name}", "w").write(
        f"# {w2 if w2 != 'feon' else 'Repair ticket'} ({tid}) closed: by DEC-953's practices at the lift (DEC-1132 (1))\n\n"
        f"- Head at close: {head} (w2/integrate); profile {prof}\n"
        f"- Evidence: {evidence}\n"
        f"- Lines met in part or by reading: {part}\n"
        f"- Route: `tk close` and this record (DEC-953 items 1 and 5); `gov close` and its gates are lifted here (DEC-953, DEC-1052 Q-8) and return through W2-115 on evidence (DEC-1128 (2), DEC-1132 (1))\n"
        f"- Closed: {now} UTC, by the orchestrator (session 8ddb8b14)\n")
    run("tk", "close", tid)
    run("git", "add", name, f".tickets/{tid}.md")
    run("git", "commit", "-q", "-m",
        f"{w2 if w2 != 'feon' else 'DAEO-feon'} closed by DEC-953's practices at the lift (DEC-1132 (1)): the close record and tk close\n\n"
        f"Task: {tid}\nRole: orchestrator\nImplements: DEC-1132, DEC-953\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>")
    print(f"closed {w2} {tid}")
print("ALL DONE")
