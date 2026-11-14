#!/bin/bash
# 2026-11-13 evening (CTO): fresh `gov accept` for W2-128, W2-136, W2-147 before each close (DEC-953), one at a time
# through the heavy slot, in a clean detached worktree at w2/integrate's head (lift_accepts_1.sh's form).
R=/home/usain/Dynamic-Agentic-Engineering-OS; O=$R/.gov-runtime/scratch/orchestrator
WT=/home/usain/gov-os-runs/W2-00/accept-20261113-eve; OUT=$O/log/accepts-20261113-eve; mkdir -p "$OUT"
[ -e "$WT" ] || git -C "$R" worktree add -q --detach "$WT" w2/integrate || exit 2
cd "$WT" || exit 2
export TMPDIR=/tmp/gov-os-cto-f388; mkdir -p "$TMPDIR"
echo "$(date -u '+%F %T') start at $(git rev-parse --short HEAD) in $WT" | tee -a "$OUT/summary.txt"
for w in W2-128 W2-136 W2-147; do
  env --default-signal=INT,HUP bash $O/tools/heavy_slot.sh gov accept "$w" --json > "$OUT/$w.json" 2> "$OUT/$w.err"; rc=$?
  t=$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); t=d.get('totals') or d.get('result',{}).get('totals'); print(t)" "$OUT/$w.json" 2>/dev/null)
  echo "$(date -u '+%F %T') $w rc=$rc totals=$t" | tee -a "$OUT/summary.txt"
done
echo "$(date -u '+%F %T') done" | tee -a "$OUT/summary.txt"
