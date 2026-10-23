#!/usr/bin/env bash
# Lead check, run 2: each suite in its own process, with this worktree's src/ (DEC-732).
# Usage: check2.sh  (writes log/check2-<suite>.txt and .exit)
cd /home/usain/gov-os-worktrees/W2-07 || exit 90
L=/home/usain/gov-os-worktrees/W2-07/.gov-runtime/scratch/lead/log
export TMPDIR=/tmp/gov-os-lead-W2-07
export PYTHONPATH=/home/usain/gov-os-worktrees/W2-07/src
mkdir -p "$TMPDIR"
python3 -c "import gov; print(gov.__file__)" > "$L/check2-gov-file.txt"
python3 -m pytest tests/acceptance/W1-30 -n auto -q -p no:cacheprovider -rs > "$L/check2-W1-30.txt" 2>&1; echo $? > "$L/check2-W1-30.exit"
du -s --inodes "$TMPDIR" >> "$L/check2-scratch.txt"; du -sh "$TMPDIR" >> "$L/check2-scratch.txt"
python3 -m pytest tests/acceptance/W2-53 -n auto -q -p no:cacheprovider -rs > "$L/check2-W2-53.txt" 2>&1; echo $? > "$L/check2-W2-53.exit"
python3 -m pytest tests/acceptance/W2-07 -n auto -q -p no:cacheprovider -rs > "$L/check2-W2-07.txt" 2>&1; echo $? > "$L/check2-W2-07.exit"
python3 -m pytest tests/acceptance/W2-01 -n auto -q -p no:cacheprovider -rs > "$L/check2-W2-01.txt" 2>&1; echo $? > "$L/check2-W2-01.exit"
python3 -m pytest tests/unit/close tests/unit/telemetry -n auto -q -p no:cacheprovider -rs > "$L/check2-unit.txt" 2>&1; echo $? > "$L/check2-unit.exit"
du -s --inodes "$TMPDIR" >> "$L/check2-scratch.txt"; du -sh "$TMPDIR" >> "$L/check2-scratch.txt"
echo done > "$L/check2.done"
