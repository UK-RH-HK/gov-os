#!/bin/bash
# latency_interleaved.sh: W2-13's real-model warm latency case, base code and head code alternately (P-1 (a)),
# two passes each, one at a time, each with the machine's load before it. Logs in the lead's log folder.
cd /home/usain/gov-os-worktrees/W2-13 || exit 9
for pass in base-1 head-1 base-2 head-2; do
  case "$pass" in
    base-*) src=/home/usain/gov-os-runs/W2-13/base/src ;;
    head-*) src=/home/usain/gov-os-worktrees/W2-13/src ;;
  esac
  {
    echo "pass $pass src $src start $(date -u +%H:%M:%S) load $(cut -d' ' -f1-3 /proc/loadavg)"
    TMPDIR=/tmp/gov-os-lead-W2-13 PYTHONPATH=$src python3 -c "import gov; print(gov.__file__)"
    TMPDIR=/tmp/gov-os-lead-W2-13 PYTHONPATH=$src python3 -m pytest tests/acceptance/W2-13/test_w2_13_latency.py -k real_models -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs
    echo "exit $? end $(date -u +%H:%M:%S) load $(cut -d' ' -f1-3 /proc/loadavg)"
  } >> /home/usain/gov-os-worktrees/W2-13/.gov-runtime/scratch/lead/log/latency-interleaved.txt 2>&1
done
echo 0 > /home/usain/gov-os-worktrees/W2-13/.gov-runtime/scratch/lead/log/latency-interleaved.exit
