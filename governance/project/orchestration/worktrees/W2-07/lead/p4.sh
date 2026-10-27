#!/usr/bin/env bash
# Lead verification, run 4, part B: the full parallel run in the close's form, under the machine-wide lock, with the
# retention option (DEC-889 items 6 and 12, DEC-904, DEC-905). Exit code in log/p4-parallel.exit; log/p4.done at the end.
cd /home/usain/gov-os-worktrees/W2-07 || exit 90
L=/home/usain/gov-os-worktrees/W2-07/.gov-runtime/scratch/lead/log
GATE=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh
CLOSE=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING
SRC=/home/usain/gov-os-worktrees/W2-07/src
export TMPDIR=/tmp/gov-os-lead-W2-07
rm -f "$L/p4.done"
trap 'echo done > "$L/p4.done"' EXIT
( until [ -e "$L/p4.done" ]; do
    echo "$(date -Is) $(cut -d' ' -f1 /proc/loadavg) $(du -s --inodes "$TMPDIR" 2>/dev/null | cut -f1) $(du -sb "$TMPDIR" 2>/dev/null | cut -f1)" >> "$L/p4-scratch-watch.txt"
    sleep 180
  done ) &
until [ ! -e "$CLOSE" ]; do sleep 60; done
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
{ date -Is; cat /proc/loadavg; bash "$GATE"; du -s --inodes "$TMPDIR"; du -sh "$TMPDIR"; } > "$L/p4-parallel.gate" 2>&1 \
  || { echo 91 > "$L/p4-parallel.exit"; exit 91; }
export PATH="/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH"
export PYTHONPATH="$SRC:$SRC/gov/close/pytest_plugin"
export GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-07
flock /tmp/gov-os-verify.lock bash -c "date -Is > $L/p4-parallel.start; exec python3 -m pytest tests -n auto -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs --junitxml=$L/parallel4.xml" \
  > "$L/p4-parallel.txt" 2>&1; echo $? > "$L/p4-parallel.exit"
date -Is > "$L/p4-parallel.end"
{ du -s --inodes "$TMPDIR"; du -sh "$TMPDIR"; } >> "$L/p4-parallel.gate" 2>&1
