#!/usr/bin/env bash
# The lead's check (W2-73): the two named cases 30 times in a row alone, then the whole of W1-03 alone.
cd /home/usain/gov-os-worktrees/W2-73 || exit 2
export TMPDIR=/tmp/gov-os-lead-W2-73
mkdir -p "$TMPDIR"
F=tests/acceptance/W1-03/test_w1_03_head_move_and_acceptance_test.py
CASES="test_while_another_actor_s_call_is_open_the_test_is_flagged_and_not_restored test_the_restore_next_to_a_head_move_takes_back_the_acceptance_tests_and_nothing_else"
fails=0
for c in $CASES; do
  pass=0
  for i in $(seq 1 30); do
    if PYTHONPATH=/home/usain/gov-os-worktrees/W2-73/src python3 -m pytest "$F::$c" -q -p no:cacheprovider --no-header > "$TMPDIR/rep-last.txt" 2>&1; then
      pass=$((pass+1))
    else
      fails=$((fails+1)); echo "FAIL $c run $i"; tail -20 "$TMPDIR/rep-last.txt"
    fi
  done
  echo "$c: $pass of 30 passed"
done
echo "--- whole W1-03 alone"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-73/src python3 -m pytest tests/acceptance/W1-03 -q -p no:cacheprovider --no-header 2>&1 | tail -5
whole=${PIPESTATUS[0]}
echo "whole_exit=$whole repeat_fails=$fails"
[ "$fails" -eq 0 ] && [ "$whole" -eq 0 ]
