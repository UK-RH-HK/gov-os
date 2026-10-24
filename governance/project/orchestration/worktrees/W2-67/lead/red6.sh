#!/bin/bash
# Run 3's red check of batch 6 (td-6): each plant against its revised cases, then the head; JUnit XML under /tmp.
set -u
W=/home/usain/gov-os-worktrees/W2-67
P=$W/.gov-runtime/scratch/td-6/plant
OUT=/tmp/gov-os-lead-W2-67/red6
LOG=$W/.gov-runtime/scratch/lead/log/red6.txt
export TMPDIR=/tmp/gov-os-lead-W2-67
mkdir -p "$OUT"
cd "$W" || exit 99
C=tests/acceptance/W1-30/test_w1_30_close.py
declare -A CASES=(
  [PF13]="$C::test_close_requires_implements_trailer $C::test_close_requires_task_trailer"
  [PF5]="$C::test_close_refuses_when_acceptance_tests_fail $C::test_close_runs_acceptance_tests"
  [PF11]="$C::test_regression_runs_to_end_all_failures_collected"
  [PF12]="$C::test_regression_failure_blocks_close $C::test_regression_runs_to_end_all_failures_collected"
  [PF16]="$C::test_close_runs_regression_tests_when_present $C::test_regression_failure_blocks_close"
  [PF4]="$C::test_containment_blocks_close_for_out_of_scope_commit"
  [PF15]="$C::test_task_trailer_exact_match_not_substring"
  [PF9]="tests/acceptance/W1-30/test_w1_30_receipt.py::test_close_record_packet_hash_matches_context"
  [PF10]="tests/acceptance/W1-30/test_w1_30_iteration.py::test_owner_decision_checker_failing_refuses"
  [PF1]="tests/acceptance/W1-30/test_w1_30_disposition.py::test_all_six_dispositions_recognized"
  [PF2]="tests/acceptance/W1-30/test_w1_30_disposition.py::test_disposition_with_context_failure"
  [PF2b]="tests/acceptance/W1-30/test_w1_30_disposition.py::test_disposition_with_context_failure"
)
: > "$LOG"
for plant in PF13 PF5 PF11 PF12 PF16 PF4 PF15 PF9 PF10 PF1 PF2 PF2b; do
  rm -f "$OUT/$plant.marker"
  GOV_TD6_PLANT=$plant GOV_TD6_MARKER=$OUT/$plant.marker PYTHONPATH=$W/src:$P \
    python3 -m pytest -p td6_plant_plugin -p no:cacheprovider -o tmp_path_retention_policy=failed -q --no-header \
    -n 3 -rA --junitxml="$OUT/$plant.xml" ${CASES[$plant]} > "$OUT/$plant.out" 2>&1
  echo "$plant exit=$? $(tail -1 "$OUT/$plant.out") marker_lines=$(wc -l < "$OUT/$plant.marker" 2>/dev/null || echo 0)" >> "$LOG"
done
GOV_TD6_GUARD_PLANT=other PYTHONPATH=$W/src:$P python3 -m pytest -p td6_guard_plant -p no:cacheprovider \
  -o tmp_path_retention_policy=failed -q -p no:xdist --junitxml="$OUT/guard-other.xml" \
  tests/acceptance/W1-27/test_w2_67_temp_folders.py::test_no_source_of_round_1_passes_a_per_run_basetemp_or_changes_the_retention > "$OUT/guard-other.out" 2>&1
echo "guard-other exit=$? $(tail -1 "$OUT/guard-other.out")" >> "$LOG"
ALL=$(for k in "${!CASES[@]}"; do echo ${CASES[$k]}; done | tr ' ' '\n' | sort -u | tr '\n' ' ')
PYTHONPATH=$W/src python3 -m pytest -p no:cacheprovider -o tmp_path_retention_policy=failed -q --no-header -n 4 -rA \
  --junitxml="$OUT/head.xml" $ALL tests/acceptance/W1-27/test_w2_67_temp_folders.py tests/acceptance/W1-27/test_w2_67_basetemp_refusal.py > "$OUT/head.out" 2>&1
echo "head exit=$? $(tail -1 "$OUT/head.out")" >> "$LOG"
echo done >> "$LOG"
