#!/bin/bash
# Register v0.208, then the two closes with the ticket tool (DEC-689, DEC-690), their sections, worktrees removed.
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
S=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
C="Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
[ -z "$(git status --porcelain)" ] || { echo "tree not clean"; git status --short | head; exit 1; }
python3 "$S/append.py" drafts/register-208.md register || exit 1
git add docs/DECISION_REGISTER.md
git commit -q -m "Decision register v0.208: DEC-686 to DEC-692 (owner: the empty semantic index, ORION's cycle and ARGUS as reported, the containment restores traced, two closes with the ticket tool, the backup, the W1-42 merge held)" --trailer "Task: decision-record" --trailer "$C" || exit 1
python3 "$S/append.py" drafts/bootstrap-two-closes.md bootstrap || exit 1
tk close DAEO-6mk8 || exit 1
git add .tickets/DAEO-6mk8.md governance/project/bootstrap.md
git commit -q -m "W1-31 closed with the ticket tool after the round of DEC-655, by the owner's decision (DEC-689; the one further gov close refused on one live network case that passes alone)" --trailer "Task: DAEO-6mk8" --trailer "Role: orchestrator" --trailer "Implements: CAP-04.b" --trailer "$C" || exit 1
tk close DAEO-emkd || exit 1
git add .tickets/DAEO-emkd.md
git commit -q -m "W1-02 closed with the ticket tool after the round of DEC-685, by the owner's decision (DEC-690; gov close refused on history from before the round, every test green)" --trailer "Task: DAEO-emkd" --trailer "Role: orchestrator" --trailer "Implements: CAP-58.a" --trailer "$C" || exit 1
git worktree remove /home/usain/gov-os-worktrees/W1-31b && git branch -d w1/W1-31b
git worktree remove --force /home/usain/gov-os-worktrees/W1-02 && git branch -d w1/W1-02
git log -3 --format='%h %s' | cut -c1-110
git worktree list
git status --short | head
