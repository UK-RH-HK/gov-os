"""Compose docs/probes/DAEO-6ox0/PR-DAEO-6ox0-r1.md: front matter, a header paragraph, the reviewer's record as returned."""
import os
import sys

sys.path.insert(0, "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools")
import verdict  # noqa: E402

TREE = "/home/usain/gov-os-worktrees/W2-40"
SRC = TREE + "/.gov-runtime/scratch/lead/probes/rev-1-result.md"
DEST = TREE + "/docs/probes/DAEO-6ox0/PR-DAEO-6ox0-r1.md"
PROBED = "9f71c6bc42407e3ace234e3625581eb1950a1527"

body = open(SRC, encoding="utf-8").read()
ok, reasons = verdict.ready(body)
if ok is not True:
    sys.exit(f"not READY: {reasons}")

head = f"""---
type: probe
task: DAEO-6ox0
reviewer_session: 4b4d039a-3285-4d5f-8dac-6de87558bd60
implementer_session: df631877-f230-437b-91a2-9912883cb87e
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: {PROBED}
---

# FULL probe of W2-40 (DAEO-6ox0) at {PROBED[:12]}: EXP-002's hook-limit record, review round 1 of at most 2

- **What was probed:** the evidence record `experiments/EXP-002/hook-limit-record.md`, its script, README and thirteen result lines, against the ticket's one live KPI line S1 (the harness's behaviour at a hook's time limit, so that the guard's deadline sits below it; DEC-1083 lifted the other three). The script round's research session wrote the script (`37320b6a5889`); the ticket lead ran the thirteen cases outside the sandbox on 2026-11-11 (Claude Code 2.1.322, `claude-haiku-4-5-20251001`); the record round's research session (`implementer_session` above) wrote the record (`6b01098c505e`); the lead merged `w2/integrate` (W2-105's land, no cited file) into the branch, giving the probed head.
- **Reviewer:** a fresh, read-only independent auditor (Opus 5.5, effort high, class C2), launched sandboxed by the lead with `launch_worker.sh`; brief `.gov-runtime/scratch/lead/briefs/rev-1.md` (with `governance/project/briefs/JUDGEMENT.md` word for word); tripwire clean; sandbox trial file absent. READY computed by `verdict.ready`: True, no blocking finding. The lead's judgement: pass.
- **The reviewer's record follows, as returned.**

"""
os.makedirs(os.path.dirname(DEST), exist_ok=True)
with open(DEST, "w", encoding="utf-8") as f:
    f.write(head + body.rstrip("\n") + "\n")
print("wrote", DEST, "ready", ok)
