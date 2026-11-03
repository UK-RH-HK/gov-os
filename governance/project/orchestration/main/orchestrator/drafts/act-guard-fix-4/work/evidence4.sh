#!/usr/bin/env bash
# ACT-GUARD-FIX-4's evidence, one run through the gate: bash heavy_slot.sh bash work/evidence4.sh <out folder>
set -u
OUT=$1
W=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
D=$W/drafts/act-guard-fix-4
PIN=/home/usain/.local/share/gov-os/pin-9894b0cf/bin/python
export GOV_PIN_PY=$PIN
cd "$D/work" || exit 1
echo "== replay (87 logged refusals)"; python3 replay4.py --json "$OUT/replay4.json" > "$OUT/replay.txt" 2>&1; echo "exit $?"
echo "== today's two"; python3 today4.py > "$OUT/today.txt" 2>&1; echo "exit $?"
echo "== guard4_check, today's hook"; python3 "$W/tools/guard4_check.py" "$W/drafts/act-guard-fix-3/pretooluse.py" > "$OUT/guard4-fix3.txt" 2>&1; echo "exit $?"
echo "== guard4_check, candidate"; python3 "$W/tools/guard4_check.py" "$D/pretooluse.py" > "$OUT/guard4-fix4.txt" 2>&1; echo "exit $?"
echo "== test_guard_fix_3, today's hook"; GUARD_FIX3_HOOK=$W/drafts/act-guard-fix-3/pretooluse.py python3 -m pytest -q -n 6 \
  -o tmp_path_retention_policy=failed -p no:cacheprovider "$W/tools/test_guard_fix_3.py" > "$OUT/fix3-on-fix3.txt" 2>&1; echo "exit $?"
echo "== test_guard_fix_3, candidate"; GUARD_FIX3_HOOK=$D/pretooluse.py python3 -m pytest -q -n 6 -rf \
  -o tmp_path_retention_policy=failed -p no:cacheprovider "$W/tools/test_guard_fix_3.py" > "$OUT/fix3-on-fix4.txt" 2>&1; echo "exit $?"
echo "== guard4_check candidate (drafts), candidate hook"; python3 "$D/guard4_check.py" "$D/pretooluse.py" > "$OUT/guard4c-fix4.txt" 2>&1; echo "exit $?"
echo "== guard4_check candidate (drafts), today's hook"; python3 "$D/guard4_check.py" "$W/drafts/act-guard-fix-3/pretooluse.py" > "$OUT/guard4c-fix3.txt" 2>&1; echo "exit $?"
echo "== test_guard_fix_4, candidate"; python3 -m pytest -q -n 6 -rf -o tmp_path_retention_policy=failed -p no:cacheprovider \
  "$D/test_guard_fix_4.py" > "$OUT/fix4-on-fix4.txt" 2>&1; echo "exit $?"
echo "== test_guard_fix_4, today's hook"; GUARD_FIX4_HOOK=$W/drafts/act-guard-fix-3/pretooluse.py python3 -m pytest -q -n 6 \
  -o tmp_path_retention_policy=failed -p no:cacheprovider "$D/test_guard_fix_4.py" > "$OUT/fix4-on-fix3.txt" 2>&1; echo "exit $?"
echo "== rm history"; "$PIN" -E rm_history.py "$D" "$OUT/rm_history.json" > "$OUT/rm_history.txt" 2>&1; echo "exit $?"
