#!/bin/bash
# ACT-GUARD-FIX-6: the earlier bundles' case sets (g14, FIX-3, FIX-4) against one hook dir, through heavy_slot.sh.
# bash run_old_suites.sh <hooks dir> <out dir>      (TMPDIR set by the caller, outside the repository)
set -u
H=${1:?hooks dir}; OUT=${2:?out dir}
O=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
mkdir -p "$OUT/calls" "$OUT/tmp"
export GOV_GUARD_CALLS_DIR="$OUT/calls" PYTHONUSERBASE=/home/usain/.local PYTHONDONTWRITEBYTECODE=1
export GUARD_FIX3_HOOK="$H/pretooluse.py" GUARD_FIX4_HOOK="$H/pretooluse.py" G14_HOOK="$H/pretooluse.py"
export GUARD_FIX3_CORPUS="$O/drafts/act-guard-fix-3/work/corpus.json" GUARD_FIX4_CORPUS="$O/drafts/act-guard-fix-4/work/corpus4.json"
export GUARD_FIX3_TESTS="$O/drafts/act-guard-fix-3/test_guard_fix_3.py"
cd "$OUT" || exit 3
for t in "$O/drafts/act-guard-fix-4/test_guard_fix_4.py" "$O/drafts/act-guard-fix-3/test_guard_fix_3.py" "$O/drafts/g14/test_g14.py"; do
  n=$(basename "$t" .py)
  TMPDIR="$OUT/tmp" bash "$O/tools/heavy_slot.sh" python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
     --rootdir "$OUT" -c /dev/null "$t" -rf --tb=line > "$OUT/$n.txt" 2>&1
  echo "$n exit $? : $(tail -1 "$OUT/$n.txt")"
done
