#!/usr/bin/env bash
# Run 5: the full rebuild (flock, this worktree's code), then gov.__file__ and gov check, each with an exit file.
WT=/home/usain/gov-os-worktrees/W2-52
OUT=$WT/.gov-runtime/scratch/lead/runs3
cd "$WT" || exit 2
export TMPDIR=/tmp/gov-os-lead-W2-52
PYTHONPATH=$WT/src python3 -c "import gov; print(gov.__file__)" > "$OUT/govfile.txt" 2>&1
PYTHONPATH=$WT/src flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json > "$OUT/rebuild.json" 2>&1
echo $? > "$OUT/rebuild.exit"
PYTHONPATH=$WT/src python3 -m gov.cli.main check --json > "$OUT/check.json" 2>&1
echo $? > "$OUT/check.exit"
echo done > "$OUT/rebuild3.done"
