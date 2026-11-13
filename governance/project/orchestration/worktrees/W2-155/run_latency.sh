#!/usr/bin/env bash
# W2-155 run 2 step 3: W1-19's and W2-13's warm real-model latency cases alone, through heavy_slot.sh, the load recorded,
# the GPU sampled (DEC-1159 (3): requests now up to the new 48,000 bound; started only with GPU use near 0 %).
T=/home/usain/gov-os-worktrees/W2-155
S=$T/.gov-runtime/scratch
R=$S/latency-$(date +%H%M%S)
SMI=/usr/lib/wsl/lib/nvidia-smi
mkdir -p "$R" /tmp/w2-155-lat
{ echo "start $(date '+%F %T') load $(cat /proc/loadavg)"; $SMI --query-gpu=utilization.gpu,memory.used,memory.total --format=csv,noheader; } > "$R/load.txt"
$SMI --query-gpu=timestamp,utilization.gpu,memory.used --format=csv,noheader,nounits -lms 500 > "$R/smi.csv" &
SP=$!
( while sleep 15; do echo "$(date +%T) $(cut -d' ' -f1-3 /proc/loadavg)"; done ) > "$R/loadtrace.txt" &
LP=$!
cd "$T"
env -u GOV_ROLE -u GOV_TICKET TMPDIR=/tmp/w2-155-lat PYTHONUSERBASE=/home/usain/.local PYTHONPATH=$T/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rA \
  --junitxml="$R/latency.xml" \
  "tests/acceptance/W1-19/test_w1_19_real_models.py::test_a_warm_query_answers_within_half_a_second_at_p95" \
  "tests/acceptance/W1-19/test_w1_19_real_models.py::test_the_rerank_process_stays_within_two_and_a_half_gigabytes" \
  "tests/acceptance/W2-13/test_w2_13_latency.py::test_a_warm_retrieval_with_the_real_models_answers_within_the_budget" \
  > "$R/pytest.txt" 2>&1
RC=$?
kill $SP $LP 2>/dev/null
echo "end $(date '+%F %T') load $(cat /proc/loadavg) rc=$RC" >> "$R/load.txt"
echo "rc=$RC dir=$R"
