#!/bin/bash
# one pytest run per folder, each through the heavy slot; exit codes and summaries in files next to this one
cd /home/usain/gov-os-worktrees/W2-146 || exit 1
out=/home/usain/gov-os-worktrees/W2-146/.gov-runtime/scratch/eng
for folder in tests/unit/retrieval tests/unit/retrieve tests/acceptance/W2-13 tests/acceptance/W1-20 tests/acceptance/W1-21 tests/acceptance/W2-138; do
  name=$(echo "$folder" | tr '/' '_')
  mkdir -p "$TMPDIR/run-$name"
  env TMPDIR="$TMPDIR/run-$name" HOME=/home/usain/gov-os-worktrees/W2-146/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-146/src \
    bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest "$folder" -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" > "$out/$name.log" 2>&1
  echo $? > "$out/$name.exit"
done
echo done > "$out/all.done"
