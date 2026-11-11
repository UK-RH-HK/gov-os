#!/usr/bin/env bash
# A/B of two W2-96 signal cases: $1 = tree (this ticket's or the main tree at integrate); normal HOME; no bytecode.
T=$1
L=/home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead/log
name=$(basename "$T")
mkdir -p /tmp/gov-os-lead-W2-05
cd "$T" || exit 2
env TMPDIR=/tmp/gov-os-lead-W2-05 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$T/src \
  python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
  "tests/unit/accept/test_w2_96_run2.py::test_w2_96_r9_r12_ctrl_c_during_the_run_stops_it" \
  "tests/unit/accept/test_w2_96_review3.py::test_w2_96_r14_a_stopped_run_keeps_128_plus_the_signal[True-2]" \
  > "$L/ab-$name.txt" 2>&1
echo "exit $?"
tail -3 "$L/ab-$name.txt"
