#!/bin/bash
# DEC-709: stage, rebuild the index (no embeddings), then commit. Hooks are uninstalled (DEC-712).
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
export GOV_DEV_TIERS=/home/usain/gov-os-workbench/synthetic
export PATH="$HOME/.nvm/versions/node/v22.23.3/bin:$PATH"
L=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log
ls .git/hooks | grep -v '\.sample$' | head -3
python3 .gov-runtime/scratch/orchestrator/append.py drafts/register-216.md register
python3 .gov-runtime/scratch/orchestrator/append.py drafts/bootstrap-W2-first.md bootstrap
echo "validator: $(python3 docs/plan/tools/validate_s1.py 2>&1 | tail -1)"
git add docs/DECISION_REGISTER.md governance/project/bootstrap.md
git status --short
PYTHONPATH=src python3 -m gov.cli.main rebuild --no-embeddings --json > $L/rebuild-v0216.json 2> $L/rebuild-v0216.err
echo "rebuild exit $?"
git commit -q -m "Decision register v0.216: DEC-710 to DEC-714 (owner: w1/W1-42 restored, the hook's foreign commits kept and named, hooks removed until W1-42 is merged and the hook's git environment first on the Wave 2 list, W1-42 merged with three red cases, the intended exit with named exceptions)" --trailer "Task: decision-record" --trailer "Role: orchestrator" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
echo "commit exit $?"
git log --oneline -1
git status --short | head -5
