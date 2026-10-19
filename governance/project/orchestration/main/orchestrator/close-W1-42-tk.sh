#!/bin/bash
# DEC-717: record the decision; close DAEO-gjjf with tk close and a note; bootstrap note. Each commit: stage, rebuild (DEC-709), commit.
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
export GOV_DEV_TIERS=/home/usain/gov-os-workbench/synthetic
export PATH="$HOME/.nvm/versions/node/v22.23.3/bin:$PATH"
L=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log
O=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
CO="Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
echo "hooks: $(ls .git/hooks | grep -v '\.sample$' | tr '\n' ' ')"
rb() { PYTHONPATH=src python3 -m gov.cli.main rebuild --no-embeddings --json > $L/rebuild-$1.json 2> $L/rebuild-$1.err; echo "rebuild $1 exit $?"; }

# 1. DEC-717
python3 $O/append.py drafts/register-219.md register
echo "validator: $(python3 docs/plan/tools/validate_s1.py 2>&1 | tail -1)"
git add docs/DECISION_REGISTER.md
rb v0219
git commit -q -m "Decision register v0.219: DEC-717 (owner: W1-42 closed with the ticket tool, its 22 findings named for the exit auditor, the W1-43 audit in place of the missing probe, w1/W1-42 kept for DEC-711)" --trailer "Task: decision-record" --trailer "Role: orchestrator" --trailer "$CO"
echo "commit 1 exit $?"; git log --oneline -1

# 2. tk close with a note
tk add-note DAEO-gjjf "Closed with tk close by the owner's decision of 2026-10-16 (DEC-717), named for the exit auditor: gov close at ca426ca9 refused (exit 3) on 22 findings: the two named red cases RETR-X-02 and the governance share (DEC-713, DEC-714); 15 trailer findings (six commits before the trailers base 1c33dd28, seven merges in the merge form, the claim 93bcb247); one change without a task (76ce6416); two containment findings on the operator's Role: owner adapter commits (8bb34efe, 71ae763f); no probe (the W1-43 exit audit stands in); a stale checkpoint (no run 8c, DEC-716). Merged at ccc32181; regression 13,190 + 263 passed, 2 failed (the named cases); validator ALL PASS."
echo "note exit $?"
tk close DAEO-gjjf
echo "tk close exit $?"
git add .tickets/DAEO-gjjf.md
git status --short
rb W1-42-tkclose
git commit -q -m "W1-42 closed with the ticket tool by the owner's decision (DEC-717; gov close refused on the two named red cases, history findings, no probe and a stale checkpoint; regression green but for the named cases)" --trailer "Task: DAEO-gjjf" --trailer "Role: orchestrator" --trailer "Implements: CAP-28.b, CAP-38.b, CAP-40.c, CAP-23.c" --trailer "$CO"
echo "commit 2 exit $?"; git log --oneline -1

# 3. bootstrap note
python3 $O/append.py drafts/bootstrap-W1-42-close.md bootstrap
git add governance/project/bootstrap.md
rb W1-42-bootstrap
git commit -q -m "Bootstrap: DAEO-gjjf (W1-42) closed with the ticket tool, for the exit auditor (DEC-717)" --trailer "Task: DAEO-gjjf" --trailer "Role: orchestrator" --trailer "Implements: CAP-28.b, CAP-38.b, CAP-40.c, CAP-23.c" --trailer "$CO"
echo "commit 3 exit $?"
git log --oneline -4
git status --short | head -5
grep -m1 '^status:' .tickets/DAEO-gjjf.md
