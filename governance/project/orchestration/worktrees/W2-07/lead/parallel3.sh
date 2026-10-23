#!/usr/bin/env bash
# The full parallel run in the close's form, under the machine-wide lock, with the retention option (DEC-904, DEC-905).
# Re-run of verify3.sh step 4, which the Bash tool's two-hour limit stopped at 94% (its load and lock waits took
# about 95 minutes). The lead waits for the close flag and the load in the foreground before starting this.
cd /home/usain/gov-os-worktrees/W2-07 || exit 90
L=/home/usain/gov-os-worktrees/W2-07/.gov-runtime/scratch/lead/log
GATE=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh
SRC=/home/usain/gov-os-worktrees/W2-07/src
export TMPDIR=/tmp/gov-os-lead-W2-07
rm -f "$L/p3.done"
trap 'echo done > "$L/p3.done"' EXIT
( until [ -e "$L/p3.done" ]; do
    echo "$(date -Is) $(cut -d' ' -f1 /proc/loadavg) $(du -s --inodes "$TMPDIR" 2>/dev/null | cut -f1) $(du -sb "$TMPDIR" 2>/dev/null | cut -f1)" >> "$L/p3-scratch-watch.txt"
    sleep 180
  done ) &
{ date -Is; cat /proc/loadavg; bash "$GATE"; du -s --inodes "$TMPDIR"; du -sh "$TMPDIR"; } > "$L/p3-parallel.gate" 2>&1 \
  || { echo 91 > "$L/p3-parallel.exit"; exit 91; }
export PATH="/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH"
export PYTHONPATH="$SRC:$SRC/gov/close/pytest_plugin"
export GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-07
flock /tmp/gov-os-verify.lock bash -c "date -Is > $L/p3-parallel.start; exec python3 -m pytest tests -n auto -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs --junitxml=$L/parallel3.xml" \
  > "$L/p3-parallel.txt" 2>&1; echo $? > "$L/p3-parallel.exit"
date -Is > "$L/p3-parallel.end"
{ du -s --inodes "$TMPDIR"; du -sh "$TMPDIR"; } >> "$L/p3-parallel.gate" 2>&1
