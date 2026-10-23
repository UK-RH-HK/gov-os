#!/bin/bash
# Measure the copying suites (W1-07, W1-25, W1-26, W1-27) in the close's form:
# one parallel run, then their serial-only entries; peak inodes and size of TMPDIR, wall time.
# Usage: measure.sh <label>   (writes .gov-runtime/scratch/lead/log/measure-<label>.*)
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
SUITES="tests/acceptance/W1-07 tests/acceptance/W1-25 tests/acceptance/W1-26 tests/acceptance/W1-27"
SERIAL=$(grep -v '^\s*#' tests/acceptance/serial-only.txt | sed 's/#.*//; s/[[:space:]]*$//' | grep -E '^tests/acceptance/W1-(07|25|26|27)/' )

sample() {  # $1 = pid to watch, $2 = phase name
  local peak=0 peaksz=0 n sz
  while kill -0 "$1" 2>/dev/null; do
    n=$(du -s --inodes "$TMPDIR" 2>/dev/null | cut -f1); sz=$(du -s -k "$TMPDIR" 2>/dev/null | cut -f1)
    [ "${n:-0}" -gt "$peak" ] && peak=$n
    [ "${sz:-0}" -gt "$peaksz" ] && peaksz=$sz
    echo "$(date +%T) $2 inodes=$n kb=$sz" >> "$LOG/measure-$L.samples"
    if [ "${n:-0}" -gt 5500000 ] || [ "${sz:-0}" -gt 57671680 ]; then
      echo "$(date +%T) WATCHDOG: cap neared, stopping $2" >> "$LOG/measure-$L.samples"; pkill -TERM -P "$1"; kill -TERM "$1"
    fi
    sleep 10
  done
  echo "$2 peak_inodes=$peak peak_kb=$peaksz" >> "$LOG/measure-$L.summary"
}

echo "label=$L start=$(date -Is) tmp_before_inodes=$(du -s --inodes $TMPDIR | cut -f1)" > "$LOG/measure-$L.summary"
t0=$(date +%s)
python3 -m pytest $SUITES -n auto -q -p no:cacheprovider -p gov_close_serial_only -rs \
  --junitxml="$LOG/measure-$L-parallel.xml" > "$LOG/measure-$L-parallel.out" 2>&1 &
p=$!; sample $p parallel; wait $p; e1=$?
t1=$(date +%s)
echo "parallel exit=$e1 seconds=$((t1-t0))" >> "$LOG/measure-$L.summary"
export GOV_CLOSE_SERIAL_ONLY_GIVEN="$SERIAL"
python3 -m pytest $SERIAL -q -p no:cacheprovider -p gov_close_serial_only -rs \
  --junitxml="$LOG/measure-$L-serial.xml" > "$LOG/measure-$L-serial.out" 2>&1 &
p=$!; sample $p serial; wait $p; e2=$?
t2=$(date +%s)
echo "serial exit=$e2 seconds=$((t2-t1))" >> "$LOG/measure-$L.summary"
echo "end=$(date -Is) tmp_after_inodes=$(du -s --inodes $TMPDIR | cut -f1) tmp_after=$(du -sh $TMPDIR | cut -f1) basefolders=$(ls -d $TMPDIR/pytest-of-*/pytest-* 2>/dev/null | wc -l)" >> "$LOG/measure-$L.summary"
echo done > "$LOG/measure-$L.exit"
