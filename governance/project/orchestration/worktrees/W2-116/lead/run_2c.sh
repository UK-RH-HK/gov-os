#!/usr/bin/env bash
# Pass 2c: rebuild, the seven revised files (the 17 cases), then gov accept W2-116.
L=/home/usain/gov-os-worktrees/W2-116/.gov-runtime/scratch/lead/log
T=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools
mkdir -p /tmp/gov-os-lead-W2-116-2c
cd /home/usain/gov-os-worktrees/W2-116 || exit 2
env PYTHONPATH=/home/usain/gov-os-worktrees/W2-116/src bash $T/rebuild_slot.sh /home/usain/gov-os-worktrees/W2-116 > $L/rebuild-2c.txt 2>&1
echo "rc=$?" >> $L/rebuild-2c.txt
env TMPDIR=/tmp/gov-os-lead-W2-116-2c PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-116/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-116/src \
  bash $T/heavy_slot.sh python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
  -m "not local_only" -k "not real and not green_here and not time_limit" \
  --junitxml=$L/seven-2c.xml \
  tests/acceptance/W2-131/test_w2_131_unchanged.py tests/acceptance/W2-133/test_w2_133_unchanged.py \
  tests/acceptance/W2-135/test_w2_135_unchanged.py tests/unit/retrieval/test_w2_131_register_ids.py \
  tests/unit/retrieval/test_w2_133_gap_label.py tests/unit/retrieval/test_w2_135_item_cap.py \
  tests/unit/status/test_status.py > $L/seven-2c.txt 2>&1
echo "rc=$?" >> $L/seven-2c.txt
env TMPDIR=/tmp/gov-os-lead-W2-116-2c PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-116/src \
  bash $T/heavy_slot.sh gov accept W2-116 --root /home/usain/gov-os-worktrees/W2-116 > $L/accept-4.txt 2>&1
echo "rc=$?" >> $L/accept-4.txt
