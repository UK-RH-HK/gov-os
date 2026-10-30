#!/usr/bin/env bash
# The checks before the DEC-939/940/941 records commit: the record checks, the path-map and record suites, W2-66's
# live test map, the nightly's own tests, and the queue's two tests. One line each; exits non-zero if any is red.
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
OUT=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/checks-dec941
mkdir -p "$OUT"
status=0
bash .gov-runtime/scratch/orchestrator/tools/record_checks.sh > "$OUT/record-checks.txt" 2>&1 || status=1
echo "record checks: $(tail -1 "$OUT/record-checks.txt")"
env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONPATH=/home/usain/Dynamic-Agentic-Engineering-OS/src \
  python3 -m pytest -q -p no:cacheprovider --no-header tests/acceptance/W1-06/test_w1_06_approvals.py \
  tests/acceptance/W1-08/test_w1_08_path_map.py tests/acceptance/W1-27/test_w1_27_path_compliance_r2.py \
  tests/acceptance/W1-07/test_w1_07_envelope.py tests/acceptance/W2-66/test_w2_66_live_test_map.py \
  > "$OUT/suites.txt" 2>&1 || status=1
echo "record suites and W2-66 live map: $(tail -1 "$OUT/suites.txt")"
bash governance/project/orchestration/nightly/test_nightly.sh > "$OUT/nightly.txt" 2>&1 || status=1
echo "nightly tests: $(tail -1 "$OUT/nightly.txt")"
bash .gov-runtime/scratch/orchestrator/tools/test_close_queue_refusal.sh > "$OUT/queue.txt" 2>&1 || status=1
bash .gov-runtime/scratch/orchestrator/tools/test_close_queue_gate_d.sh >> "$OUT/queue.txt" 2>&1 || status=1
echo "queue tests: $(tr '\n' ' ' < "$OUT/queue.txt")"
gitleaks git --staged --redact --no-banner --config .gitleaks.toml . > "$OUT/gitleaks.txt" 2>&1 || status=1
echo "gitleaks staged: $(tail -1 "$OUT/gitleaks.txt")"
python3 .gov-runtime/scratch/orchestrator/tools/keyword_warn.py > "$OUT/keyword.txt" 2>&1 || status=1
echo "keyword warning: $(tail -1 "$OUT/keyword.txt")"
echo "overall: $status"
exit "$status"
