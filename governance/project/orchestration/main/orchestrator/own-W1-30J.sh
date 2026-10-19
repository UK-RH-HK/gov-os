#!/bin/bash
# Own verification of the W1-30 fix round (DEC-612, DEC-613, DEC-616, DEC-620, DEC-621) at its head, run from the W1-30 worktree.
cd /home/usain/gov-os-worktrees/W1-30 || exit 1
git log --oneline -1
for s in W1-30 W1-26 W1-24 W1-08 W1-13 W1-38 W1-01; do
  echo "== $s"
  env -u PYTHONPATH python3 -m pytest tests/acceptance/$s -q -p no:cacheprovider -n 6 2>&1 | tail -3
done
echo "== unit"
PYTHONPATH=src python3 -m pytest tests/unit -q -p no:cacheprovider -n 6 2>&1 | tail -3
python3 docs/plan/tools/validate_s1.py | tail -1
export PYTHONPATH=/home/usain/gov-os-worktrees/W1-30/src
python3 -m gov.cli.main check --json > /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/check-at-W1-30J-premerge.json 2>/dev/null
echo "check exit $?"
cut -d' ' -f1-3 /proc/loadavg
