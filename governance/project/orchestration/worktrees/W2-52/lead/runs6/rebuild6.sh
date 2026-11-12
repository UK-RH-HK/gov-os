#!/usr/bin/env bash
# Run 6: the full rebuild (flock, this worktree's code), then gov.__file__ and gov check, each with an exit file.
WT=/home/usain/gov-os-worktrees/W2-52
OUT=$WT/.gov-runtime/scratch/lead/runs6
cd "$WT" || exit 2
export TMPDIR=/tmp/gov-os-lead-W2-52
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh > "$OUT/disk.txt" 2>&1
PYTHONPATH=$WT/src python3 -c "import gov; print(gov.__file__)" > "$OUT/govfile.txt" 2>&1
PYTHONPATH=$WT/src flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json > "$OUT/rebuild.json" 2>&1
echo $? > "$OUT/rebuild.exit"
PYTHONPATH=$WT/src python3 -m gov.cli.main check --json > "$OUT/check.json" 2>&1
echo $? > "$OUT/check.exit"
echo done > "$OUT/rebuild6.done"
