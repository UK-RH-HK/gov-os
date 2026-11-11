#!/bin/bash
# DEC-1132 (1): fresh `gov accept` for the lift's closes on w2/integrate, one at a time through the heavy slot, before
# each `tk close` and close record (DEC-953). W2-96's signal cases need SIGHUP/SIGINT not ignored: restored here.
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 2
O=.gov-runtime/scratch/orchestrator; OUT=$O/log/lift-accepts-1; mkdir -p "$OUT"
echo "$(date -u '+%F %T') start at $(git rev-parse --short HEAD); SigIgn=$(awk '/^SigIgn:/{print $2}' /proc/self/status)" | tee -a "$OUT/summary.txt"
for w in W2-122 W2-123 W2-126 W2-92 W2-96; do
  env --default-signal=INT,HUP bash $O/tools/heavy_slot.sh gov accept "$w" > "$OUT/$w.json" 2> "$OUT/$w.err"; rc=$?
  t=$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); t=d.get('totals') or d.get('result',{}).get('totals'); print(t)" "$OUT/$w.json" 2>/dev/null)
  echo "$(date -u '+%F %T') $w rc=$rc totals=$t" | tee -a "$OUT/summary.txt"
done
echo "$(date -u '+%F %T') done" | tee -a "$OUT/summary.txt"
