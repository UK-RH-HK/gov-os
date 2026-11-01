#!/bin/bash
# The measure (KPI 7), the secrets stage alone: the base code on a base clone, then the ticket's code on a clone of the
# ticket's head with an empty cache (cold), the same clone again (unchanged tree), and a second clone after the first.
# The ticket's runs share one scratch cache file, never the machine's. One JSON line each in /tmp/gov-os-lead-W2-107/filter.jsonl.
set -u
export TMPDIR=/tmp/gov-os-lead-W2-107
F=/home/usain/gov-os-worktrees/W2-107/.gov-runtime/scratch/lead/measure_filter.py
OUT=/tmp/gov-os-lead-W2-107/filter.jsonl
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh || exit 3
git -C /tmp/gov-os-lead-W2-107/m-before-a log --oneline -1 >> /tmp/gov-os-lead-W2-107/filter.heads
(cd /tmp/gov-os-lead-W2-107/m-before-a && env -u GOV_SECRETS_CACHE PYTHONPATH=/tmp/gov-os-lead-W2-107/m-before-a/src python3 "$F" before-base) >> "$OUT" 2>> /tmp/gov-os-lead-W2-107/filter.err
git clone -q --no-hardlinks --branch w2/W2-107 /home/usain/gov-os-worktrees/W2-107 /tmp/gov-os-lead-W2-107/m-after-a
git -C /tmp/gov-os-lead-W2-107/m-after-a log --oneline -1 >> /tmp/gov-os-lead-W2-107/filter.heads
(cd /tmp/gov-os-lead-W2-107/m-after-a && GOV_SECRETS_CACHE=/tmp/gov-os-lead-W2-107/cache-measure.sqlite PYTHONPATH=/tmp/gov-os-lead-W2-107/m-after-a/src python3 "$F" after-first-cold) >> "$OUT" 2>> /tmp/gov-os-lead-W2-107/filter.err
(cd /tmp/gov-os-lead-W2-107/m-after-a && GOV_SECRETS_CACHE=/tmp/gov-os-lead-W2-107/cache-measure.sqlite PYTHONPATH=/tmp/gov-os-lead-W2-107/m-after-a/src python3 "$F" after-second-unchanged) >> "$OUT" 2>> /tmp/gov-os-lead-W2-107/filter.err
git clone -q --no-hardlinks --branch w2/W2-107 /home/usain/gov-os-worktrees/W2-107 /tmp/gov-os-lead-W2-107/m-after-b
(cd /tmp/gov-os-lead-W2-107/m-after-b && GOV_SECRETS_CACHE=/tmp/gov-os-lead-W2-107/cache-measure.sqlite PYTHONPATH=/tmp/gov-os-lead-W2-107/m-after-b/src python3 "$F" after-second-clone) >> "$OUT" 2>> /tmp/gov-os-lead-W2-107/filter.err
echo done >> /tmp/gov-os-lead-W2-107/filter.heads
