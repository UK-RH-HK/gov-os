#!/bin/bash
# The measure (KPI 7), the secrets stage alone: the base code on a base clone, then the ticket's code on a clone of the
# ticket's head with an empty cache (cold), the same clone again (unchanged tree), and a second clone after the first.
# The ticket's runs share one scratch cache file, never the machine's. One JSON line each in /tmp/gov-os-lead-W2-107/filter-r2.jsonl.
set -u
export TMPDIR=/tmp/gov-os-lead-W2-107
F=/home/usain/gov-os-worktrees/W2-107/.gov-runtime/scratch/lead/measure_filter.py
OUT=/tmp/gov-os-lead-W2-107/filter-r2.jsonl
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh || exit 3
git clone -q --no-hardlinks --branch w2/W2-107 /home/usain/gov-os-worktrees/W2-107 /tmp/gov-os-lead-W2-107/m-r2-a
git -C /tmp/gov-os-lead-W2-107/m-r2-a log --oneline -1 >> /tmp/gov-os-lead-W2-107/filter-r2.heads
(cd /tmp/gov-os-lead-W2-107/m-r2-a && GOV_SECRETS_CACHE=/tmp/gov-os-lead-W2-107/cache-measure-r2.sqlite PYTHONPATH=/tmp/gov-os-lead-W2-107/m-r2-a/src python3 "$F" after-first-cold) >> "$OUT" 2>> /tmp/gov-os-lead-W2-107/filter-r2.err
(cd /tmp/gov-os-lead-W2-107/m-r2-a && GOV_SECRETS_CACHE=/tmp/gov-os-lead-W2-107/cache-measure-r2.sqlite PYTHONPATH=/tmp/gov-os-lead-W2-107/m-r2-a/src python3 "$F" after-second-unchanged) >> "$OUT" 2>> /tmp/gov-os-lead-W2-107/filter-r2.err
git clone -q --no-hardlinks --branch w2/W2-107 /home/usain/gov-os-worktrees/W2-107 /tmp/gov-os-lead-W2-107/m-r2-b
(cd /tmp/gov-os-lead-W2-107/m-r2-b && GOV_SECRETS_CACHE=/tmp/gov-os-lead-W2-107/cache-measure-r2.sqlite PYTHONPATH=/tmp/gov-os-lead-W2-107/m-r2-b/src python3 "$F" after-second-clone) >> "$OUT" 2>> /tmp/gov-os-lead-W2-107/filter-r2.err
echo done >> /tmp/gov-os-lead-W2-107/filter-r2.heads
