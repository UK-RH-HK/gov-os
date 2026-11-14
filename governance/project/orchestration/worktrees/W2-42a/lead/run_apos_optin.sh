#!/usr/bin/env bash
# The scoped set again with the opt-in tiers collected (GOV_TESTS_OPTIN=lifted,breadth), so no guard or DEC-409 case is left out.
TREE=/home/usain/gov-os-worktrees/W2-42a
L=$TREE/.gov-runtime/scratch/lead/log
mkdir -p /tmp/w2-42a-lead/tmp "$TREE/.gov-runtime/scratch/empty-home"
cd "$TREE"
env HOME=$TREE/.gov-runtime/scratch/empty-home TMPDIR=/tmp/w2-42a-lead/tmp PYTHONUSERBASE=/home/usain/.local \
  PYTHONPATH=$TREE/src GOV_TESTS_OPTIN=lifted,breadth \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest tests/unit/guard tests/acceptance/W2-42a tests/unit/hooks \
  tests/unit/pause tests/unit/containment/test_w1_50_freeze_flag.py \
  tests/acceptance/W1-50 tests/acceptance/W1-28 tests/acceptance/W2-16 \
  -q -n auto -p no:cacheprovider -o tmp_path_retention_policy=failed \
  -m "not local_only" -k "not real and not green_here and not time_limit" \
  --junitxml=$L/apos-scoped-optin.xml > $L/apos-scoped-optin.log 2>&1
echo $? > $L/apos-scoped-optin.rc
