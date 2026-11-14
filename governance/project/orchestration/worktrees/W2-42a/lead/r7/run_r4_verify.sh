#!/usr/bin/env bash
# The R4 R5 verify (DEC-1157 (12), DEC-968): gov accept, then the scoped run once (opt-in tiers collected, so
# DEC-409's lifted cases are in it).
TREE=/home/usain/gov-os-worktrees/W2-42a
L=$TREE/.gov-runtime/scratch/lead/log
mkdir -p /tmp/w2-42a-lead/tmp "$TREE/.gov-runtime/scratch/empty-home"
cd "$TREE"
export TMPDIR=/tmp/w2-42a-lead/tmp PYTHONUSERBASE=/home/usain/.local
git rev-parse HEAD > $L/r4-verify.head
env PYTHONPATH=$TREE/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh gov accept W2-42a --root $TREE > $L/r4-accept.log 2>&1
echo $? > $L/r4-accept.rc
env HOME=$TREE/.gov-runtime/scratch/empty-home PYTHONPATH=$TREE/src GOV_TESTS_OPTIN=lifted,breadth \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest tests/unit/guard tests/acceptance/W2-42a tests/unit/hooks \
  tests/unit/pause tests/unit/containment/test_w1_50_freeze_flag.py \
  tests/acceptance/W1-50 tests/acceptance/W1-28 tests/acceptance/W2-16 \
  -q -n auto -p no:cacheprovider -o tmp_path_retention_policy=failed \
  -m "not local_only" -k "not real and not green_here and not time_limit" \
  --junitxml=$L/r4-scoped.xml > $L/r4-scoped.log 2>&1
echo $? > $L/r4-scoped.rc
echo done > $L/r4-verify.exit
