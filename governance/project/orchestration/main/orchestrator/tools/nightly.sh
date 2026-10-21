#!/usr/bin/env bash
# The nightly full uncached regression on w2/integrate's head (DEC-852 item 3; owner, 2026-10-21: P-H-3 (a), started
# now as an orchestrator script; W2-66's nightly replaces it). It runs in the close's form, on a fresh clone of the
# head under the orchestrator's own run folder (DEC-728), with the clone's own code:
#   the parallel run of all of tests/ less the serial-only list, then the listed cases alone and serially
#   (the close's own plugin, gov_close_serial_only); JUnit XML for both; every failing case re-run alone
#   (lens H, P-H-9: a red that passes alone is a flaky candidate, not a red of the head).
# It waits for a quiet machine and no close (CLOSE-RUNNING), holds NIGHTLY-RUNNING while it runs, writes nothing
# in the repository, and appends one line to log/nightly/digest.txt. A red of the head is a P1 package (the
# orchestrator brings it).
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
REPO=/home/usain/Dynamic-Agentic-Engineering-OS
STAMP=$(date +%Y%m%d-%H%M)
OUT=$ORCH/log/nightly/$STAMP
RUNS=/home/usain/gov-os-runs/W2-00/nightly
mkdir -p "$OUT" "$RUNS"
quiet=0
while [ "$quiet" -lt 5 ]; do
  if [ ! -e "$ORCH/CLOSE-RUNNING" ] && awk '{exit !($1 < 3)}' /proc/loadavg; then quiet=$((quiet + 1)); else quiet=0; fi
  sleep 60
done
date '+%F %T nightly: lock set' > "$ORCH/NIGHTLY-RUNNING"
date '+%F %T quiet' > "$OUT/run.txt"
CLONE=$RUNS/$STAMP
git clone -q --no-hardlinks --branch w2/integrate "$REPO" "$CLONE" || { echo "clone failed" >> "$OUT/run.txt"; rm -f "$ORCH/NIGHTLY-RUNNING"; exit 2; }
HEAD=$(git -C "$CLONE" rev-parse --short HEAD)
echo "head $HEAD" >> "$OUT/run.txt"
cd "$CLONE" || exit 2
PLUG=$CLONE/src/gov/close/pytest_plugin
# The tests that read the repository's own state (W2-54's green-here and time-limit cases) need its stores, as a
# close has them after its rebuild: a fresh clone has none (the first rehearsal's two reds, 2026-10-21 19:00).
env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONPATH="$CLONE/src" python3 -m gov.cli.main rebuild --json \
  > "$OUT/rebuild.json" 2> "$OUT/rebuild.err" || { echo "clone rebuild failed" >> "$OUT/run.txt"; rm -f "$ORCH/NIGHTLY-RUNNING"; exit 2; }
echo "clone rebuilt" >> "$OUT/run.txt"
ENTRIES=$(python3 -c "import sys; sys.path.insert(0, 'src'); from gov.close.pytest_plugin.gov_close_serial_only import entries; print('\n'.join(entries(__import__('pathlib').Path('.'))))")
start=$(date +%s)
env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONPATH="$CLONE/src:$PLUG" GOV_CLOSE_SERIAL_ONLY_OF="$CLONE" \
  python3 -m pytest tests -n auto --dist worksteal -q -p no:cacheprovider --no-header -p gov_close_serial_only \
  --junitxml="$OUT/parallel.xml" > "$OUT/parallel.txt" 2>&1
p_exit=$?
mid=$(date +%s)
# shellcheck disable=SC2086
env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONPATH="$CLONE/src:$PLUG" GOV_CLOSE_SERIAL_ONLY_OF="$CLONE" \
  GOV_CLOSE_SERIAL_ONLY_GIVEN="$ENTRIES" \
  python3 -m pytest $ENTRIES -q -p no:cacheprovider --no-header -p gov_close_serial_only \
  --junitxml="$OUT/serial.xml" > "$OUT/serial.txt" 2>&1
s_exit=$?
end=$(date +%s)
echo "parallel exit $p_exit in $((mid - start)) s: $(tail -1 "$OUT/parallel.txt")" >> "$OUT/run.txt"
echo "serial exit $s_exit in $((end - mid)) s: $(tail -1 "$OUT/serial.txt")" >> "$OUT/run.txt"
# Every failing case, alone (the close's environment), once.
python3 "$ORCH/tools/nightly_alone.py" "$CLONE" "$OUT" >> "$OUT/run.txt" 2>&1
rm -f "$ORCH/NIGHTLY-RUNNING"
date '+%F %T done' >> "$OUT/run.txt"
echo "$(date '+%F %T') head $HEAD: $(grep -E '^(parallel|serial|verdict)' "$OUT/run.txt" | tr '\n' ' ')" >> "$ORCH/log/nightly/digest.txt"
cat "$OUT/run.txt"
