#!/usr/bin/env bash
# Every acceptance folder that names OPENSPEC_ABSENT / openspec YELLOW / elapsed_s / CHECK_FAILED, at head and on w2/integrate.
# Run without the -k filter too (time-limit cases are what Interface item 7 changes); the -m local_only filter kept.
mkdir -p /tmp/gov-os-lead-W2-45/triage3c
export TMPDIR=/tmp/gov-os-lead-W2-45/triage3c
export PYTHONUSERBASE=/home/usain/.local
export HOME=/home/usain/gov-os-worktrees/W2-45/.gov-runtime/scratch/empty-home
SLOT=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh
DIRS="tests/acceptance/W1-15 tests/acceptance/W1-18 tests/acceptance/W1-26 tests/acceptance/W1-30 tests/acceptance/W1-40 tests/acceptance/W2-54 tests/acceptance/W2-76 tests/acceptance/W2-95"
BASE=/tmp/gov-os-lead-W2-45/triage3b/base
for side in head base; do
  if [ $side = head ]; then R=/home/usain/gov-os-worktrees/W2-45; else R=$BASE; fi
  cd $R
  echo "=== $side $R"
  PYTHONPATH=$R/src bash $SLOT python3 -m pytest -q -n 3 -p no:cacheprovider -o tmp_path_retention_policy=failed \
    -m "not local_only" -rfE $DIRS 2>&1 | grep -E "^(FAILED|ERROR)|passed|failed|error" | sed 's/ - .*//' | sort | uniq
done
