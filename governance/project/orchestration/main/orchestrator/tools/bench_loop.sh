#!/usr/bin/env bash
# CAPACITY-1: the same test run, timed at whatever load the machine has, every 30 minutes, so the cost of overload is
# measured on one fixed workload: `tests/unit` at a frozen commit, with 4 test workers, in its own clone.
# One JSON line per run to log/capacity/bench.jsonl. Runs until killed.
B=/home/usain/gov-os-runs/W2-00/bench/repo
OUT=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/capacity/bench.jsonl
export TMPDIR=/tmp/gov-os-bench; mkdir -p "$TMPDIR"
while true; do
  l0=$(cut -d' ' -f1-3 /proc/loadavg); a0=$(awk '/MemAvailable/{print $2}' /proc/meminfo); t0=$(date +%s.%N)
  res=$(cd "$B" && env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONPATH="$B/src" python3 -m pytest tests/unit -n 4 -q -p no:cacheprovider \
        --no-header -o tmp_path_retention_policy=failed 2>&1 | tail -1)
  t1=$(date +%s.%N); l1=$(cut -d' ' -f1-3 /proc/loadavg)
  python3 - "$t0" "$t1" "$l0" "$l1" "$a0" "$res" >> "$OUT" <<'EOF'
import json, sys, time
t0, t1, l0, l1, a0, res = sys.argv[1:7]
print(json.dumps({"t": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(float(t0))), "wall_s": round(float(t1) - float(t0), 1),
                  "load_before": [float(x) for x in l0.split()], "load_after": [float(x) for x in l1.split()],
                  "mem_available_kb_before": int(a0), "result": res}))
EOF
  sleep $(( 1800 - ${t1%.*} + ${t0%.*} > 60 ? 1800 - ${t1%.*} + ${t0%.*} : 60 ))
done
