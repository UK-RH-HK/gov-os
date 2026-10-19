#!/bin/bash
# Own verification of the W1-02 fix round, run from the W1-02 worktree.
cd /home/usain/gov-os-worktrees/W1-02 || exit 1
git log --oneline -1
for s in W1-02 W1-05 W1-47 W1-50; do
  echo "== $s"
  env -u PYTHONPATH python3 -m pytest tests/acceptance/$s -q -p no:cacheprovider -n 6 2>&1 | tail -3
done
echo "== unit"
PYTHONPATH=src python3 -m pytest tests/unit -q -p no:cacheprovider -n 6 2>&1 | tail -2
python3 docs/plan/tools/validate_s1.py | tail -1
PYTHONPATH=src python3 -m gov.cli.main check --json > /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/check-at-W1-02R-premerge.json 2>/dev/null
echo "check exit $?"
cut -d' ' -f1-3 /proc/loadavg
