#!/bin/bash
# The parallel run's reds, each re-run alone (DEC-757 reading in DEC-953: a red that fails alone is a red; one that
# passes alone is a flaky candidate). Same environment as the run. Results in log/alone-<n>.out and log/alone.txt.
set -u
L=/home/usain/gov-os-worktrees/W2-107/.gov-runtime/scratch/lead/log
cd /home/usain/gov-os-worktrees/W2-107 || exit 4
export TMPDIR=/tmp/gov-os-lead-W2-107
export PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH
export PYTHONPATH=/home/usain/gov-os-worktrees/W2-107/src:/home/usain/gov-os-worktrees/W2-107/src/gov/close/pytest_plugin
n=0
for case in \
  "tests/acceptance/W1-07/test_w1_07_envelope.py::test_the_envelope_has_no_field_outside_the_interface[check]" \
  "tests/acceptance/W1-07/test_w1_07_read_act.py::test_no_command_writes_outside_its_act_paths[check]" \
  "tests/acceptance/W1-08/test_w1_08_path_map.py::test_every_tracked_path_matches_exactly_one_namespace" \
  "tests/acceptance/W2-69/test_w2_69_unit_folder_renamed.py::test_the_unit_folder_named_secrets_is_gone" \
  "tests/acceptance/W2-54/test_w2_54_green_here.py::test_gov_check_gives_core_schema_green_here" \
  "tests/acceptance/W2-54/test_w2_54_green_here.py::test_the_w1_43_audit_report_is_untouched" \
  "tests/acceptance/W2-54/test_w2_54_green_here.py::test_gov_check_gives_context_reproducibility_green_here" \
  "tests/acceptance/W1-16/test_w1_16_home.py::test_no_index_file_exists_outside_gov_runtime_after_a_run"; do
  n=$((n + 1))
  until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
  python3 -m pytest "$case" -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs --timeout=900 --timeout_method=signal > "$L/alone-$n.out" 2>&1
  echo "$? $case $(tail -1 "$L/alone-$n.out")" >> "$L/alone.txt"
done
echo done >> "$L/alone.txt"
