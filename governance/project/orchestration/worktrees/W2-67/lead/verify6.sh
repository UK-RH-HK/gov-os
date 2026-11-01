#!/bin/bash
# Run 6's scoped verification in the close's form (DEC-889 items 6 and 12, DEC-905, DEC-952, DEC-968): the tests
# select_tests.py selects (log/select-6.json; its pytest_options and per-test limit added), one parallel run with the
# serial-only plugin; scoped with no core change, so no verify_lock.sh wrapper (DEC-968: "Your scoped run needs no
# wrapper"; its gate counted it as a full run's 7.4 GB peak and stayed shut on memory alone). The selection reaches no "serial" route entry (log/serial6.list
# is empty), so there is no serial phase. TMPDIR is the lead's folder; KPI 4's count of base folders after the run.
set -u
W=/home/usain/gov-os-worktrees/W2-67
LOG=$W/.gov-runtime/scratch/lead/log
L=r6
export TMPDIR=/tmp/gov-os-lead-W2-67
mkdir -p /tmp/gov-os-lead-W2-67/verify-r6b
cd "$W" || exit 99
python3 -c "import json; print('\n'.join(json.load(open('$LOG/select-6.json'))['pytest_options']))" > "$LOG/select-6.options"
mapfile -t OPTS < "$LOG/select-6.options"
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh > "$LOG/verify-r6b.gate" 2>&1 || { echo gate-shut > "$LOG/verify-r6b-parallel.exit"; exit 1; }
export PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH
export PYTHONPATH=$W/src:$W/src/gov/close/pytest_plugin
export GOV_CLOSE_SERIAL_ONLY_OF=$W

sample() {  # $1 = pid
  local peak=0 peaksz=0 n sz
  while kill -0 "$1" 2>/dev/null; do
    n=$(du -s --inodes /tmp/gov-os-lead-W2-67 2>/dev/null | cut -f1); sz=$(du -s -k /tmp/gov-os-lead-W2-67 2>/dev/null | cut -f1)
    [ "${n:-0}" -gt "$peak" ] && peak=$n
    [ "${sz:-0}" -gt "$peaksz" ] && peaksz=$sz
    echo "$(date +%T) inodes=$n kb=$sz load=$(cut -d' ' -f1 /proc/loadavg)" >> "$LOG/verify-r6b.samples"
    sleep 15
  done
  echo "peak_inodes=$peak peak_kb=$peaksz" >> "$LOG/verify-r6b.summary"
}

echo "head=$(git rev-parse --short=12 HEAD) start=$(date -Is) tmp_before_inodes=$(du -s --inodes /tmp/gov-os-lead-W2-67 | cut -f1) basefolders_before=$(ls -d /tmp/gov-os-lead-W2-67/pytest-of-*/pytest-* 2>/dev/null | wc -l)" >> "$LOG/verify-r6b.summary"
t0=$(date +%s)
python3 -m pytest tests -n auto -q -p no:cacheprovider -p gov_close_serial_only \
  --timeout=900 --timeout_method=signal -o tmp_path_retention_policy=failed -rs \
  --junitxml=/tmp/gov-os-lead-W2-67/verify-r6b/parallel.xml "${OPTS[@]}" > "$LOG/verify-r6b-parallel.out" 2>&1 &
p=$!; sample $p; wait $p; e=$?
t1=$(date +%s)
echo "parallel exit=$e seconds=$((t1-t0)) end=$(date -Is) tmp_after_inodes=$(du -s --inodes /tmp/gov-os-lead-W2-67 | cut -f1) tmp_after=$(du -sh /tmp/gov-os-lead-W2-67 | cut -f1) basefolders=$(ls -d /tmp/gov-os-lead-W2-67/pytest-of-*/pytest-* 2>/dev/null | wc -l)" >> "$LOG/verify-r6b.summary"
ls -d /tmp/gov-os-lead-W2-67/pytest-of-*/pytest-* > "$LOG/verify-r6b.basefolders" 2>/dev/null
echo "$e" > "$LOG/verify-r6b-parallel.exit"
