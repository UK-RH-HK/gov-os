#!/bin/bash
# 2026-11-13 (CTO): W2-37's close check after ACT-CLAUDE-COPIES-9 (e437c799c): a fresh `gov accept W2-37` and the four
# cases COPIES-9 was to turn green (W2-37 [claude-copy], W2-11 four-places [change], W1-35 :845 and :991), in a clean
# detached worktree at w2/integrate's head, through the heavy slot.
R=/home/usain/Dynamic-Agentic-Engineering-OS; O=$R/.gov-runtime/scratch/orchestrator
WT=/home/usain/gov-os-runs/W2-00/accept-w237-20261113; OUT=$O/log/accept-w237-20261113; mkdir -p "$OUT"
[ -e "$WT" ] || git -C "$R" worktree add -q --detach "$WT" w2/integrate || exit 2
cd "$WT" || exit 2
export TMPDIR=/tmp/gov-os-cto-f388; mkdir -p "$TMPDIR"
echo "$(date -u '+%F %T') start at $(git rev-parse --short HEAD)" | tee -a "$OUT/summary.txt"
env --default-signal=INT,HUP bash $O/tools/heavy_slot.sh gov accept W2-37 --json > "$OUT/W2-37.json" 2> "$OUT/W2-37.err"; rc=$?
t=$(python3 -c "import json,sys; d=json.load(open(sys.argv[1])); t=d.get('totals') or d.get('result',{}).get('totals'); print(t)" "$OUT/W2-37.json" 2>/dev/null)
echo "$(date -u '+%F %T') W2-37 accept rc=$rc totals=$t" | tee -a "$OUT/summary.txt"
PYTHONPATH="$WT/src" PYTHONUSERBASE=/home/usain/.local bash $O/tools/heavy_slot.sh python3 -m pytest -q -p no:cacheprovider \
  -o tmp_path_retention_policy=failed tests/acceptance/W2-11/test_w2_11_skills.py tests/acceptance/W1-35/test_w1_35.py \
  -k "one_version or change or 845 or 991" > "$OUT/copies.txt" 2>&1; rc=$?
echo "$(date -u '+%F %T') W2-11/W1-35 rc=$rc $(tail -1 "$OUT/copies.txt")" | tee -a "$OUT/summary.txt"
