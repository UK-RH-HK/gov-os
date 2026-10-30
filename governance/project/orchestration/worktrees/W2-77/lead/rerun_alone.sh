#!/usr/bin/env bash
# The lead's re-runs alone of the load-sensitive reds of the full run, one process each, after the gates.
LOG=/home/usain/gov-os-worktrees/W2-77/.gov-runtime/scratch/lead/log
WT=/home/usain/gov-os-worktrees/W2-77
rm -f "$LOG/alone.exit"
bash "$WT/.gov-runtime/scratch/lead/gates.sh" > "$LOG/alone-gates.txt" 2>&1 || { echo 9 > "$LOG/alone.exit"; exit 9; }
cd "$WT" || exit 8
export TMPDIR=/tmp/gov-os-lead-W2-77
export PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH
export PYTHONPATH=$WT/src
n=0
for t in "tests/acceptance/W2-54/test_w2_54_green_here.py::test_gov_check_gives_context_reproducibility_green_here" "tests/acceptance/W1-19/test_w1_19_real_models.py::test_a_warm_query_answers_within_half_a_second_at_p95" "tests/acceptance/W1-46/test_w1_46_live_sessions.py"; do
  n=$((n+1))
  flock /tmp/gov-os-verify.lock python3 -m pytest "$t" -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs > "$LOG/alone-$n.txt" 2>&1
  echo "$n $? $t" >> "$LOG/alone-codes.txt"
done
echo done > "$LOG/alone.exit"
