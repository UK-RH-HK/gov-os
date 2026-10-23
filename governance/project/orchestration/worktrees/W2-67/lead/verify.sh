#!/bin/bash
# Round 1's verification in the close's form (DEC-889 items 6 and 12, DEC-905): one parallel run of tests/,
# then the serial-only cases alone, each under flock /tmp/gov-os-verify.lock, with JUnit XML; scratch sampled.
# Usage: verify.sh <label>
set -u
W=/home/usain/gov-os-worktrees/W2-67
LOG=$W/.gov-runtime/scratch/lead/log
L=$1
export TMPDIR=/tmp/gov-os-lead-W2-67
mkdir -p "$TMPDIR"
cd "$W" || exit 99
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

echo "label=$L start=$(date -Is) tmp_before_inodes=$(du -s --inodes $TMPDIR | cut -f1)" > "$LOG/verify-$L.summary"
t0=$(date +%s)
flock /tmp/gov-os-verify.lock python3 -m pytest tests -n auto -q -p no:cacheprovider -p gov_close_serial_only \
  -o tmp_path_retention_policy=failed -rs --junitxml="$LOG/verify-$L-parallel.xml" > "$LOG/verify-$L-parallel.out" 2>&1 &
p=$!; sample $p parallel; wait $p; e1=$?
t1=$(date +%s)
echo "parallel exit=$e1 seconds=$((t1-t0))" >> "$LOG/verify-$L.summary"
export GOV_CLOSE_SERIAL_ONLY_GIVEN="$SERIAL"
flock /tmp/gov-os-verify.lock python3 -m pytest $SERIAL -q -p no:cacheprovider -p gov_close_serial_only \
  -o tmp_path_retention_policy=failed -rs --junitxml="$LOG/verify-$L-serial.xml" > "$LOG/verify-$L-serial.out" 2>&1 &
p=$!; sample $p serial; wait $p; e2=$?
t2=$(date +%s)
echo "serial exit=$e2 seconds=$((t2-t1))" >> "$LOG/verify-$L.summary"
echo "end=$(date -Is) tmp_after_inodes=$(du -s --inodes $TMPDIR | cut -f1) tmp_after=$(du -sh $TMPDIR | cut -f1) basefolders=$(ls -d $TMPDIR/pytest-of-*/pytest-* 2>/dev/null | wc -l)" >> "$LOG/verify-$L.summary"
echo done > "$LOG/verify-$L.exit"
