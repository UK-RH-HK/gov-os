#!/bin/bash
# Run 9: the four probe-record checks and W2-11's acceptance folder at the new head.
T=/home/usain/gov-os-worktrees/W2-11
mkdir -p /tmp/gov-os-lead-W2-11 "$T/.gov-runtime/scratch/empty-home" "$T/.gov-runtime/scratch/lead/log"
cd "$T" || exit 9
export TMPDIR=/tmp/gov-os-lead-W2-11
export PYTHONUSERBASE=/home/usain/.local
export HOME="$T/.gov-runtime/scratch/empty-home"
export PYTHONPATH="$T/src"
H=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh
git rev-parse --short=12 HEAD
python3 -c "import gov; print(gov.__file__)"
echo "=== four probe-record checks"
bash "$H" python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rf \
  --junitxml="$T/.gov-runtime/scratch/lead/log/r9-probe-checks.xml" \
  "tests/acceptance/W1-08/test_w1_08_probe.py::test_the_probe_schema_accepts_this_repository_s_probe_records" \
  "tests/acceptance/W1-26/test_w1_26_probe_records.py::test_this_repository_s_probe_records_are_well_formed" \
  "tests/acceptance/W1-26/test_w1_26_probe_records.py::test_no_finding_of_the_check_on_this_repository_names_a_probe_record" \
  "tests/acceptance/W2-02/test_w2_02_green_here.py::test_core_schema_is_green_on_this_repository"
echo "exit=$?"
echo "=== W2-11 acceptance folder"
bash "$H" python3 -m pytest tests/acceptance/W2-11 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rf \
  -m "not local_only" -k "not real and not green_here and not time_limit" \
  --junitxml="$T/.gov-runtime/scratch/lead/log/r9-w2-11.xml"
echo "exit=$?"
