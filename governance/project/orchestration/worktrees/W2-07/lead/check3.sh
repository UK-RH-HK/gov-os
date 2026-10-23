#!/usr/bin/env bash
# Lead check, run 3: each suite in its own process, with this worktree's src/ (DEC-732) and the retention option (DEC-905).
# Writes log/check3-<suite>.txt and .exit, and log/check3.done at the end.
cd /home/usain/gov-os-worktrees/W2-07 || exit 90
L=/home/usain/gov-os-worktrees/W2-07/.gov-runtime/scratch/lead/log
CLOSE=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING
export TMPDIR=/tmp/gov-os-lead-W2-07
export PYTHONPATH=/home/usain/gov-os-worktrees/W2-07/src
mkdir -p "$TMPDIR"
rm -f "$L/check3.done"
trap 'echo done > "$L/check3.done"' EXIT
python3 -c "import gov; print(gov.__file__)" > "$L/check3-gov-file.txt"
until [ ! -e "$CLOSE" ]; do sleep 60; done
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
{ date -Is; cat /proc/loadavg; du -s --inodes "$TMPDIR"; du -sh "$TMPDIR"; } > "$L/check3-scratch.txt" 2>&1
python3 -m pytest tests/acceptance/W1-30 -n auto -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs > "$L/check3-W1-30.txt" 2>&1; echo $? > "$L/check3-W1-30.exit"
{ date -Is; du -s --inodes "$TMPDIR"; du -sh "$TMPDIR"; } >> "$L/check3-scratch.txt" 2>&1
python3 -m pytest tests/acceptance/W2-53 -n auto -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs > "$L/check3-W2-53.txt" 2>&1; echo $? > "$L/check3-W2-53.exit"
python3 -m pytest tests/acceptance/W2-01 -n auto -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs > "$L/check3-W2-01.txt" 2>&1; echo $? > "$L/check3-W2-01.exit"
python3 -m pytest tests/acceptance/W2-07 -n auto -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs > "$L/check3-W2-07.txt" 2>&1; echo $? > "$L/check3-W2-07.exit"
python3 -m pytest tests/unit/close tests/unit/telemetry -n auto -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs > "$L/check3-unit.txt" 2>&1; echo $? > "$L/check3-unit.exit"
{ date -Is; du -s --inodes "$TMPDIR"; du -sh "$TMPDIR"; } >> "$L/check3-scratch.txt" 2>&1
