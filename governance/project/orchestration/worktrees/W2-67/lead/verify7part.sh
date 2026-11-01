#!/bin/bash
# Run 7's scoped run in two parts (the one-part run, verify-r7, was stopped at 30% at 14:07: under a load of 55-65 it
# projected past the background task's two-hour limit). Same form as verify7.sh: the selection's pytest_options
# (log/select-7.json), the serial-only plugin, the close's per-test limit, the retention option; serial7.list is empty.
#   part A: tests/acceptance/W1-30 (45% of run 6's test time)    part B: tests, with W1-30 ignored
# Usage: verify7part.sh A|B
set -u
P=$1
W=/home/usain/gov-os-worktrees/W2-67
LOG=$W/.gov-runtime/scratch/lead/log
VL=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh
export TMPDIR=/tmp/gov-os-lead-W2-67
mkdir -p /tmp/gov-os-lead-W2-67/verify-r7
cd "$W" || exit 99
mapfile -t OPTS < "$LOG/select-7.options"
if [ "$P" = "A" ]; then TGT=(tests/acceptance/W1-30); else TGT=(tests --ignore=$W/tests/acceptance/W1-30); fi
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh > "$LOG/verify-r7$P.gate" 2>&1 || { echo gate-shut > "$LOG/verify-r7$P.exit"; exit 1; }
export PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH
export PYTHONPATH=$W/src:$W/src/gov/close/pytest_plugin
export GOV_CLOSE_SERIAL_ONLY_OF=$W

sample() {  # $1 = pid
  local peak=0 peaksz=0 n sz
  while kill -0 "$1" 2>/dev/null; do
    n=$(du -s --inodes /tmp/gov-os-lead-W2-67 2>/dev/null | cut -f1); sz=$(du -s -k /tmp/gov-os-lead-W2-67 2>/dev/null | cut -f1)
    [ "${n:-0}" -gt "$peak" ] && peak=$n
    [ "${sz:-0}" -gt "$peaksz" ] && peaksz=$sz
    echo "$(date +%T) inodes=$n kb=$sz load=$(cut -d' ' -f1 /proc/loadavg)" >> "$LOG/verify-r7$P.samples"
    sleep 15
  done
  echo "peak_inodes=$peak peak_kb=$peaksz" >> "$LOG/verify-r7$P.summary"
}

echo "head=$(git rev-parse --short=12 HEAD) start=$(date -Is) tmp_before_inodes=$(du -s --inodes /tmp/gov-os-lead-W2-67 | cut -f1) basefolders_before=$(ls -d /tmp/gov-os-lead-W2-67/pytest-of-*/pytest-* 2>/dev/null | wc -l)" >> "$LOG/verify-r7$P.summary"
t0=$(date +%s)
bash "$VL" python3 -m pytest "${TGT[@]}" -n auto -q -p no:cacheprovider -p gov_close_serial_only \
  --timeout=900 --timeout_method=signal -o tmp_path_retention_policy=failed -rs \
  --junitxml=/tmp/gov-os-lead-W2-67/verify-r7/parallel-$P.xml "${OPTS[@]}" > "$LOG/verify-r7$P-parallel.out" 2>&1 &
p=$!; sample $p; wait $p; e=$?
t1=$(date +%s)
echo "parallel exit=$e seconds=$((t1-t0)) end=$(date -Is) tmp_after_inodes=$(du -s --inodes /tmp/gov-os-lead-W2-67 | cut -f1) tmp_after=$(du -sh /tmp/gov-os-lead-W2-67 | cut -f1) basefolders=$(ls -d /tmp/gov-os-lead-W2-67/pytest-of-*/pytest-* 2>/dev/null | wc -l)" >> "$LOG/verify-r7$P.summary"
ls -d /tmp/gov-os-lead-W2-67/pytest-of-*/pytest-* > "$LOG/verify-r7$P.basefolders" 2>/dev/null
echo "$e" > "$LOG/verify-r7$P.exit"
