#!/usr/bin/env bash
# The lead's checks for DAEO-ebmh (W2-75): both routes of W2-54's green-here fixture, planted bad results,
# and collection over tests. Run from the worktree, outside any sandbox. Output in log/checks/.
set -u
WT=/home/usain/gov-os-worktrees/W2-75
L=$WT/.gov-runtime/scratch/lead
OUT=$L/log/checks
mkdir -p "$OUT"
export TMPDIR=/tmp/gov-os-lead-W2-75
export PYTHONPATH=$WT/src
cd "$WT" || exit 9
unset GOV_CLOSE_CHECK_RESULT
GREEN=tests/acceptance/W2-54/test_w2_54_green_here.py
CASES="$GREEN::test_gov_check_gives_context_reproducibility_green_here $GREEN::test_gov_check_gives_core_schema_green_here $GREEN::test_the_w1_43_audit_report_is_untouched"

python3 -c "import gov; print(gov.__file__)" > "$OUT/gov_file.txt"

# 0. A real gov check --json in this worktree (the stand-in for gate (b)'s result).
start=$(date +%s)
python3 -m gov.cli.main check --json > "$OUT/check-result.json" 2> "$OUT/check-result.err"
echo "gov check exit $? in $(( $(date +%s) - start )) s" > "$OUT/check-result.exit"

# The spy: every 2 s, list python processes whose command line runs gov's CLI with "check --json".
spy() {
  : > "$1"
  while [ -e "$OUT/.spy-on" ]; do
    ps -eo pid,args | grep -E "gov(\.cli\.main| *check|.*_m\.main)" | grep -E "check --json|check$" \
      | grep -v grep | grep -v "spy" >> "$1"
    sleep 2
  done
}

run_case() {  # name, value of GOV_CLOSE_CHECK_RESULT or "-" for unset, cases
  name=$1; value=$2; shift 2
  touch "$OUT/.spy-on"; spy "$OUT/$name.spy" & spid=$!
  start=$(date +%s)
  if [ "$value" = "-" ]; then
    python3 -m pytest "$@" -q -p no:cacheprovider -rA --durations=0 --setup-show > "$OUT/$name.log" 2>&1
  else
    GOV_CLOSE_CHECK_RESULT=$value python3 -m pytest "$@" -q -p no:cacheprovider -rA --durations=0 --setup-show > "$OUT/$name.log" 2>&1
  fi
  code=$?
  rm -f "$OUT/.spy-on"; wait $spid
  echo "$name: exit $code in $(( $(date +%s) - start )) s; spy lines $(wc -l < "$OUT/$name.spy")" | tee -a "$OUT/summary.txt"
}

: > "$OUT/summary.txt"
cat "$OUT/check-result.exit" >> "$OUT/summary.txt"
# 1. The close's route: the variable set to the real result. Expect green, no gov check started.
run_case set-green "$OUT/check-result.json" $CASES
# 2. Planted bad results: never green.
run_case set-missing "$OUT/no-such-result.json" $CASES
printf 'this is not JSON {\n' > "$OUT/not-json.json"
run_case set-notjson "$OUT/not-json.json" $CASES
python3 "$L/make_red.py" "$OUT/check-result.json" "$OUT/red-context.json" >> "$OUT/summary.txt" 2>&1
run_case set-redcontext "$OUT/red-context.json" $CASES
# 3. Outside a close: the variable unset. Expect green, gov check run by the fixture.
run_case unset $CASES
# 4. The whole green-here file with the variable set (the designer's own cases included).
run_case file-set-green "$OUT/check-result.json" $GREEN
# 5. Collection over tests, in one process, as the close does (DEC-868).
python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header > "$OUT/collect.log" 2>&1
echo "collect: exit $? last: $(tail -n 1 "$OUT/collect.log")" | tee -a "$OUT/summary.txt"
echo done > "$OUT/DONE"
