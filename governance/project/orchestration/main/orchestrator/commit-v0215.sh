#!/bin/bash
# DEC-709: stage, rebuild the index (no embeddings), then commit through the pre-commit hook. A refusal is reported, never worked round.
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
export GOV_DEV_TIERS=/home/usain/gov-os-workbench/synthetic
export PATH="$HOME/.nvm/versions/node/v22.23.3/bin:$PATH"
L=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log
python3 .gov-runtime/scratch/orchestrator/append.py drafts/bootstrap-B3-hook.md bootstrap
echo "validator: $(python3 docs/plan/tools/validate_s1.py 2>&1 | tail -1)"
git add docs/DECISION_REGISTER.md governance/project/bootstrap.md
git status --short
PYTHONPATH=src python3 -m gov.cli.main rebuild --no-embeddings --json > $L/rebuild-v0215.json 2> $L/rebuild-v0215.err
echo "rebuild exit $?"
git commit -q -m "Decision register v0.215: DEC-706 to DEC-709 (owner: B3 done, lefthook hooks installed; B2 part 2 done on this repository, W1-42's manual-check KPI line met; a-dev backed up; the close of ade-ke2y accepted; rebuild after staging before each commit, fast pre-commit checks to the Wave 2 list)" --trailer "Task: decision-record" --trailer "Role: orchestrator" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" > $L/commit-v0215b.txt 2>&1
echo "commit exit $?"
grep -E 'CHECK_FAILED|exit status|secrets"|summary|✔️|🥊' $L/commit-v0215b.txt
git log --oneline -1
git status --short | head -5
