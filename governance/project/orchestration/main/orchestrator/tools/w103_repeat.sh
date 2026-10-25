#!/usr/bin/env bash
# W1-03's red-alone case at two heads, ten times each, alone, in run clones under ~/gov-os-runs (never the main tree):
# today's head (the pre-re-pin nightly's clone, 45a6dfd5) and the head before W2-72's merge (c60c9704), to tell the
# same-second amend flake (W2-72's P2) from a regression of W2-72's containment change. Prints counts only.
CASE=tests/acceptance/W1-03/test_w1_03_head_move_and_acceptance_test.py::test_while_another_actor_s_call_is_open_the_test_is_flagged_and_not_restored
NOW=/home/usain/gov-os-runs/W2-00/nightly/20261025-0501
BEFORE=/home/usain/gov-os-runs/W2-00/w103-before-w272
OUT=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/w103-repeat.txt
export TMPDIR=/tmp/gov-os-w103
mkdir -p /tmp/gov-os-w103
[ -d /home/usain/gov-os-runs/W2-00/w103-before-w272 ] || git clone -q --no-hardlinks /home/usain/Dynamic-Agentic-Engineering-OS /home/usain/gov-os-runs/W2-00/w103-before-w272
git -C /home/usain/gov-os-runs/W2-00/w103-before-w272 checkout -q --detach c60c9704
: > /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/w103-repeat.txt
for TREE in "$NOW" "$BEFORE"; do
  pass=0; fail=0
  for i in 1 2 3 4 5 6 7 8 9 10; do
    if (cd "$TREE" && env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONPATH="$TREE/src" python3 -m pytest -q -p no:cacheprovider --no-header -o tmp_path_retention_policy=failed "$CASE" > /dev/null 2>&1); then pass=$((pass + 1)); else fail=$((fail + 1)); fi
  done
  echo "$(git -C "$TREE" rev-parse --short=12 HEAD): $pass passed, $fail failed of 10" >> /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/w103-repeat.txt
done
cat /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/w103-repeat.txt
