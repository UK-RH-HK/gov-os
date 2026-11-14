#!/usr/bin/env bash
# Pass 2c: the scoped run's 6 reds (all the pass 2b probe record's frontmatter), re-run alone after the fix.
mkdir -p /tmp/gov-os-lead-W2-116-six
cd /home/usain/gov-os-worktrees/W2-116 || exit 2
env TMPDIR=/tmp/gov-os-lead-W2-116-six PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-116/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-116/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
  --junitxml=/home/usain/gov-os-worktrees/W2-116/.gov-runtime/scratch/lead/log/six-2c.xml \
  "tests/acceptance/W2-54/test_w2_54_audit_report.py::test_core_schema_is_green_on_this_repository_with_w1_43_untouched" \
  "tests/acceptance/W1-26/test_w1_26_probe_records.py::test_this_repository_s_probe_records_are_well_formed" \
  "tests/acceptance/W1-26/test_w1_26_probe_records.py::test_no_finding_of_the_check_on_this_repository_names_a_probe_record" \
  "tests/acceptance/W2-02/test_w2_02_green_here.py::test_core_schema_is_green_on_this_repository" \
  "tests/acceptance/W1-08/test_w1_08_probe.py::test_the_probe_schema_accepts_this_repository_s_probe_records" \
  "tests/acceptance/W2-54/test_w2_54_green_here.py::test_gov_check_gives_core_schema_green_here" 2>&1 | tail -8
