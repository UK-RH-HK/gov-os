#!/usr/bin/env bash
# Runs the score-once harness's own tests, each file alone, on CPU, stub scorers only (no reranker, no GPU, no
# question read). The script-style files run with python3 (each prints "N of M passed"); test_rx_e0b.py runs with
# plain pytest. Run it through the heavy-job gate:
#   bash .gov-runtime/scratch/orchestrator/tools/heavy_slot.sh bash <this folder>/run_harness_tests.sh
# TMPDIR defaults to /tmp/gov-os-emg-e0b.
HERE=$(cd "$(dirname "$0")" && pwd)
export TMPDIR=${TMPDIR:-/tmp/gov-os-emg-e0b}
mkdir -p "$TMPDIR"
rc=0
for t in test_rx_combine.py test_rx_l5.py test_rx_l6.py test_rx_live.py test_live_tools.py test_live_window.py \
         test_yes_logit.py test_e4.py; do
  echo "=== $t"
  python3 "$HERE/$t" > "$TMPDIR/$t.out" 2>&1
  code=$?
  grep -E "FAIL|passed|Error" "$TMPDIR/$t.out" | tail -n 15
  echo "exit $code"
  [ "$code" -ne 0 ] && rc=1
done
if [ -f "$HERE/test_rx_e0b.py" ]; then
  echo "=== test_rx_e0b.py (pytest)"
  python3 -m pytest -q -o tmp_path_retention_policy=failed -p no:cacheprovider "$HERE/test_rx_e0b.py" 2>&1 | tail -n 25
  code=${PIPESTATUS[0]}
  echo "exit $code"
  [ "$code" -ne 0 ] && rc=1
fi
exit $rc
