#!/usr/bin/env bash
# The unset route of W2-54's green-here cases (checks.sh's step 3 passed no "-": fixed here), run alone.
set -u
WT=/home/usain/gov-os-worktrees/W2-75
OUT=$WT/.gov-runtime/scratch/lead/log/checks
export TMPDIR=/tmp/gov-os-lead-W2-75
export PYTHONPATH=$WT/src
cd "$WT" || exit 9
unset GOV_CLOSE_CHECK_RESULT
GREEN=tests/acceptance/W2-54/test_w2_54_green_here.py
: > "$OUT/unset2.spy"
touch "$OUT/.spy-on"
( while [ -e "$OUT/.spy-on" ]; do
    ps -eo pid,args | grep "gov.cli.main as _m" | grep -v grep >> "$OUT/unset2.spy"; sleep 5
  done ) &
spid=$!
start=$(date +%s)
python3 -m pytest "$GREEN::test_gov_check_gives_context_reproducibility_green_here" \
  "$GREEN::test_gov_check_gives_core_schema_green_here" "$GREEN::test_the_w1_43_audit_report_is_untouched" \
  -q -p no:cacheprovider -rA --durations=0 > "$OUT/unset2.log" 2>&1
code=$?
rm -f "$OUT/.spy-on"; wait $spid
echo "unset2: exit $code in $(( $(date +%s) - start )) s; spy lines $(wc -l < "$OUT/unset2.spy")" | tee -a "$OUT/summary.txt"
