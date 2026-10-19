#!/bin/bash
# The W1-02 round of DEC-685 after its probe: probe record, merge, residuals, fresh checkpoint, one commit each.
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
S=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
T=(--trailer "Task: DAEO-emkd" --trailer "Role: orchestrator" --trailer "Implements: CAP-58.a" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>")
[ -z "$(git status --porcelain --untracked-files=no)" ] || { echo "tree not clean"; exit 1; }
git add docs/probes/DAEO-emkd/PR-DAEO-emkd-round-DEC-685.md
git commit -q -m "W1-02 round on tools the guard does not know: probe record (DEC-685)" "${T[@]}" || exit 1
git merge -q --no-ff w1/W1-02 -m "Merge w1/W1-02: the guard refuses a tool it does not know, MultiEdit judged like Edit (DEC-685)" || exit 1
git commit -q --amend --no-edit "${T[@]}" || exit 1
python3 "$S/append.py" drafts/bootstrap-W1-02-round9.md bootstrap || exit 1
git add governance/project/bootstrap.md
git commit -q -m "W1-02 round (DEC-685): residuals for the Wave 2 list in bootstrap.md" "${T[@]}" || exit 1
PYTHONPATH=src python3 -m gov.cli.main checkpoint --ticket DAEO-emkd --role orchestrator --trigger ticket-transition \
  --next "The round of DEC-685 is merged and probed (pass); run the regression, then gov close DAEO-emkd once; exit 4 stops for the owner (DEC-651)." --json | head -c 400
echo
git add docs/checkpoints/DAEO-emkd
git commit -q -m "Checkpoint: the W1-02 round of DEC-685 merged and probed, before its close" "${T[@]}" || exit 1
git log -4 --format='%h %s'
git status --short | head
