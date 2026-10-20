#!/bin/bash
# Own verification of the W1-15 round (DEC-595, DEC-596) at its head, run from the W1-15 worktree.
cd /home/usain/gov-os-worktrees/W1-15 || exit 1
git log --oneline -1
for s in W1-38 W1-39 W1-40 W1-41 W1-47 W1-03; do
  echo "== $s"
  env -u PYTHONPATH python3 -m pytest tests/acceptance/$s -q -p no:cacheprovider -n 6 2>&1 | tail -3
done
echo "== unit"
PYTHONPATH=src python3 -m pytest tests/unit -q -p no:cacheprovider -n 6 2>&1 | tail -3
python3 docs/plan/tools/validate_s1.py | tail -1
PYTHONPATH=src python3 -m gov.cli.main check --json > /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/check-at-W1-15H2-premerge.json 2>/dev/null
echo "check exit $?"
cut -d' ' -f1-3 /proc/loadavg
