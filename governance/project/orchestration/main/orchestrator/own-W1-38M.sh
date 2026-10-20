#!/bin/bash
# After the merge of the W1-38 round (DEC-664): residuals to bootstrap.md, fresh checkpoints for DAEO-3ef2 and DAEO-6mk8, one commit each.
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
S=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
python3 "$S/append.py" drafts/bootstrap-W1-38-roundM.md bootstrap || exit 1
git add governance/project/bootstrap.md
git commit -q -m "W1-38 round (DEC-664): residuals for the Wave 2 list in bootstrap.md" \
  --trailer "Task: DAEO-3ef2" --trailer "Role: orchestrator" --trailer "Implements: CAP-38.b" \
  --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || exit 1
PYTHONPATH=src python3 -m gov.cli.main checkpoint --ticket DAEO-3ef2 --role orchestrator --trigger ticket-transition \
  --next "The round of DEC-664 is merged at 99fbb546 and probed (pass); run gov close DAEO-3ef2 once; exit 4 stops for the owner (DEC-651)." --json | head -c 600
echo
git add docs/checkpoints/DAEO-3ef2
git commit -q -m "Checkpoint: the W1-38 round of DEC-664 merged and probed, before its close" \
  --trailer "Task: DAEO-3ef2" --trailer "Role: orchestrator" --trailer "Implements: CAP-38.b" \
  --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || exit 1
PYTHONPATH=src python3 -m gov.cli.main checkpoint --ticket DAEO-6mk8 --role orchestrator --trigger ticket-transition \
  --next "The W1-31 round is merged (9495bf3a); the three DEC-665 cases are rewritten and merged (99fbb546); run the one further gov close DAEO-6mk8 (DEC-672); exit 4 stops for the owner (DEC-651)." --json | head -c 600
echo
git add docs/checkpoints/DAEO-6mk8
git commit -q -m "Checkpoint: the W1-31 round before its one further close (DEC-672)" \
  --trailer "Task: DAEO-6mk8" --trailer "Role: orchestrator" --trailer "Implements: CAP-04.b" \
  --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || exit 1
git log -4 --format='%h %s'
git status --short | head
