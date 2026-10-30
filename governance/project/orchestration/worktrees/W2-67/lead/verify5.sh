#!/bin/bash
# Run 5's verification in the close's form (DEC-889 items 6 and 12, DEC-905), split in two background jobs so each
# ends inside the two-hour limit: phase "parallel" (tests/ -n auto) or phase "serial" (the serial-only cases alone).
# Each under flock /tmp/gov-os-verify.lock, with JUnit XML; scratch sampled. Usage: verify5.sh <label> <phase>
set -u
W=/home/usain/gov-os-worktrees/W2-67
LOG=$W/.gov-runtime/scratch/lead/log
L=$1
PH=$2
export TMPDIR=/tmp/gov-os-lead-W2-67
mkdir -p "$TMPDIR/verify-$L"
cd "$W" || exit 99
until [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING ]; do sleep 60; done
until [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING ]; do sleep 60; done
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh > "$LOG/verify-$L-$PH.gate" 2>&1 || { echo gate-shut > "$LOG/verify-$L-$PH.exit"; exit 1; }
export PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH
export PYTHONPATH=$W/src:$W/src/gov/close/pytest_plugin
export GOV_CLOSE_SERIAL_ONLY_OF=$W
SERIAL=$(grep -v '^\s*#' tests/acceptance/serial-only.txt | sed 's/#.*//; s/[[:space:]]*$//' | grep -v '^$')

sample() {  # $1 = pid, $2 = phase
  local peak=0 peaksz=0 n sz
  while kill -0 "$1" 2>/dev/null; do
    n=$(du -s --inodes "$TMPDIR" 2>/dev/null | cut -f1); sz=$(du -s -k "$TMPDIR" 2>/dev/null | cut -f1)
    [ "${n:-0}" -gt "$peak" ] && peak=$n
    [ "${sz:-0}" -gt "$peaksz" ] && peaksz=$sz
    echo "$(date +%T) $2 inodes=$n kb=$sz load=$(cut -d' ' -f1 /proc/loadavg)" >> "$LOG/verify-$L.samples"
    sleep 15
  done
  echo "$2 peak_inodes=$peak peak_kb=$peaksz" >> "$LOG/verify-$L.summary"
}

echo "label=$L phase=$PH start=$(date -Is) tmp_before_inodes=$(du -s --inodes $TMPDIR | cut -f1)" >> "$LOG/verify-$L.summary"
t0=$(date +%s)
if [ "$PH" = parallel ]; then
  flock /tmp/gov-os-verify.lock python3 -m pytest tests -n auto -q -p no:cacheprovider -p gov_close_serial_only \
    -o tmp_path_retention_policy=failed -rs --junitxml="$TMPDIR/verify-$L/parallel.xml" > "$LOG/verify-$L-parallel.out" 2>&1 &
else
  export GOV_CLOSE_SERIAL_ONLY_GIVEN="$SERIAL"
  flock /tmp/gov-os-verify.lock python3 -m pytest $SERIAL -q -p no:cacheprovider -p gov_close_serial_only \
    -o tmp_path_retention_policy=failed -rs --junitxml="$TMPDIR/verify-$L/serial.xml" > "$LOG/verify-$L-serial.out" 2>&1 &
fi
p=$!; sample $p "$PH"; wait $p; e=$?
t1=$(date +%s)
echo "$PH exit=$e seconds=$((t1-t0)) end=$(date -Is) tmp_after_inodes=$(du -s --inodes $TMPDIR | cut -f1) tmp_after=$(du -sh $TMPDIR | cut -f1) basefolders=$(ls -d $TMPDIR/pytest-of-*/pytest-* 2>/dev/null | wc -l)" >> "$LOG/verify-$L.summary"
echo "$e" > "$LOG/verify-$L-$PH.exit"
