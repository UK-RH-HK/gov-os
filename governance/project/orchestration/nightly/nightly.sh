#!/usr/bin/env bash
# The nightly full uncached regression on w2/integrate's head (owner, standing: DEC-852 item 3, DEC-933 item 2,
# DEC-934). It runs in the close's form, on a fresh clone of the head under the orchestrator's run folder (DEC-728),
# with the clone's own code:
#   the parallel run of all of tests/ less the serial-only list, then every listed case alone and serially (the
#   close's own plugin, gov_close_serial_only; the nightly-routed entries included); JUnit XML for both; every failing
#   case re-run alone (lens H, P-H-9: a red that passes alone is a flaky candidate, not a red of the head).
# It writes nothing in the repository. Its state and logs are the orchestrator's scratch (.gov-runtime/, ignored).
#
# `nightly.sh night` (started by nightly_cron.sh, which cron runs at 02:00):
#   - window 02:00 to 05:00. The run books only its measured estimate (nightly_estimate.py: the last full runs'
#     per-test durations and their measured effective parallelism, the serial phase, setup, 10 %), and starts no
#     later than 05:00 less that estimate;
#   - it starts once the state is clean: no close (CLOSE-RUNNING) and no merge in progress, the main tree clean, and
#     w2/integrate's head unchanged for 5 minutes. Past the latest start it does not start (a P1);
#   - while it runs it holds NIGHTLY-RUNNING (the close queue waits for it) and the verification lock for both its
#     test phases (a lead's or a trial's full run waits for it); it lets both go the moment it ends;
#   - an estimate that no longer fits the window is never cut short: the run starts once the state is clean, and
#     the owner gets a package ping with the options (DEC-933 item 2.6);
#   - a red verdict, or a night that ends without a verdict, pings P1; the orchestrator writes the package;
#   - after a green or flaky night it removes its own clone; after a red one it keeps it for the diagnosis.
# By day (no argument) it waits for 5 quiet minutes (load below 3) and no close: a manual run, which keeps its clone.
HERE=$(cd "$(dirname "$0")" && pwd)
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
REPO=/home/usain/Dynamic-Agentic-Engineering-OS
STAMP=$(date +%Y%m%d-%H%M)
OUT=$ORCH/log/nightly/$STAMP
RUNS=/home/usain/gov-os-runs/W2-00/nightly
# DEC-911: JUnit XML holds every test name and failure text (full hashes), so it is written outside .gov-runtime/,
# where the secrets-indexing check reads.
JUNIT=/tmp/gov-os-nightly-junit/$STAMP
LOCKFILE=/tmp/gov-os-verify.lock
PING=/home/usain/.local/bin/owner-ping
mkdir -p "$OUT" "$RUNS" "$JUNIT"
MODE=${1:-day}
OWN_FLAG=0
# At night, a run that ends without a verdict (not started, clone or rebuild failed, cut) is a P1 too. The flag is
# removed on every way out, if this run set it.
trap '[ "$OWN_FLAG" = 1 ] && rm -f "$ORCH/NIGHTLY-RUNNING"; [ "$MODE" = night ] && ! grep -q "^verdict:" "$OUT/run.txt" 2>/dev/null && "$PING" "P1 NIGHTLY-NOT-RUN | $(tail -1 "$OUT/run.txt" 2>/dev/null | cut -c1-140) | the orchestrator'"'"'s package follows"' EXIT
if [ -n "$(find "$ORCH/NIGHTLY-RUNNING" -mmin -360 2>/dev/null)" ]; then
  date "+%F %T nightly NOT STARTED: another nightly holds NIGHTLY-RUNNING" > "$OUT/run.txt"; exit 2
fi
EST=""
if [ "$MODE" = night ]; then
  now=$(date +%s)
  window_end=$(date -d "today 05:00" +%s)
  [ "$now" -lt "$window_end" ] || { date "+%F %T nightly NOT STARTED: started after 05:00" > "$OUT/run.txt"; exit 2; }
  est_json=$(python3 "$HERE/nightly_estimate.py" estimate)
  EST=$(echo "$est_json" | python3 -c "import json, sys; print(json.load(sys.stdin).get('estimate_s') or '')")
  date "+%F %T nightly night: estimate $est_json" > "$OUT/run.txt"
  if [ -z "$EST" ]; then
    EST=10800; echo "no full run measured: the estimate is the whole window" >> "$OUT/run.txt"
  fi
  latest=$((window_end - EST))
  if [ "$latest" -lt "$now" ]; then
    "$PING" "P2 NIGHTLY-WINDOW | estimate $((EST / 60)) min no longer fits 02:00-05:00 | the orchestrator's package with the options follows; tonight's run is not cut"
    echo "estimate does not fit the window: starts once clean, not cut" >> "$OUT/run.txt"
    latest=$window_end
  fi
  echo "latest start $(date -d "@$latest" '+%H:%M')" >> "$OUT/run.txt"
  last_head=""
  while :; do
    head=$(git -C "$REPO" rev-parse w2/integrate)
    age=$(( $(date +%s) - $(git -C "$REPO" log -1 --format=%ct w2/integrate) ))
    why=""
    [ -e "$ORCH/CLOSE-RUNNING" ] && why="a close is running"
    [ -z "$why" ] && [ -e "$REPO/.git/MERGE_HEAD" ] && why="a merge is in progress"
    [ -z "$why" ] && [ -n "$(git -C "$REPO" status --porcelain)" ] && why="the main tree is not clean"
    [ -z "$why" ] && [ "$age" -lt 300 ] && why="w2/integrate's head is under 5 minutes old"
    [ -z "$why" ] && [ -n "$last_head" ] && [ "$head" != "$last_head" ] && why="w2/integrate's head moved"
    [ -z "$why" ] && break
    if [ "$(date +%s)" -gt "$latest" ]; then
      date "+%F %T nightly NOT STARTED: by the latest start, $why" >> "$OUT/run.txt"; exit 2
    fi
    last_head=$head
    sleep 60
  done
else
  quiet=0
  while [ "$quiet" -lt 5 ]; do
    if [ ! -e "$ORCH/CLOSE-RUNNING" ] && awk '{exit !($1 < 3)}' /proc/loadavg; then quiet=$((quiet + 1)); else quiet=0; fi
    sleep 60
  done
  date '+%F %T nightly day: quiet' > "$OUT/run.txt"
fi
# DEC-898: free disk space and free inodes above the floor, or no run.
disk=$(bash "$HERE/disk_gate.sh" 2>&1) || { date "+%F %T nightly NOT STARTED: $disk" >> "$OUT/run.txt"; exit 2; }
date '+%F %T nightly: lock set' > "$ORCH/NIGHTLY-RUNNING"
OWN_FLAG=1
t0=$(date +%s)
CLONE=$RUNS/$STAMP
git clone -q --no-hardlinks --branch w2/integrate "$REPO" "$CLONE" || { echo "clone failed" >> "$OUT/run.txt"; exit 2; }
HEAD=$(git -C "$CLONE" rev-parse --short=12 HEAD)
echo "head $HEAD" >> "$OUT/run.txt"
cd "$CLONE" || exit 2
PLUG=$CLONE/src/gov/close/pytest_plugin
# The tests that read the repository's own state (W2-54's green-here and time-limit cases) need its stores, as a
# close has them after its rebuild: a fresh clone has none (the first rehearsal's two reds, 2026-10-21 19:00).
env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONPATH="$CLONE/src" python3 -m gov.cli.main rebuild --json \
  > "$OUT/rebuild.json" 2> "$OUT/rebuild.err" || { echo "clone rebuild failed" >> "$OUT/run.txt"; exit 2; }
echo "clone rebuilt" >> "$OUT/run.txt"
ENTRIES=$(python3 -c "import sys; sys.path.insert(0, 'src'); from gov.close.pytest_plugin.gov_close_serial_only import entries; print('\n'.join(entries(__import__('pathlib').Path('.'))))")
[ -n "$ENTRIES" ] || { echo "no serial-only entry read" >> "$OUT/run.txt"; exit 2; }
# The verification lock, for both test phases. At night it is held on descriptor 9 by this script alone: each test
# command runs with 9 closed, so no process a test leaves behind can keep the lock. By day each phase takes it.
if [ "$MODE" = night ]; then
  exec 9> "$LOCKFILE"
  wait_s=$(( latest - $(date +%s) )); [ "$wait_s" -gt 0 ] || wait_s=1
  flock -w "$wait_s" 9 || { date "+%F %T nightly NOT STARTED: the verification lock was held past the latest start" >> "$OUT/run.txt"; exit 2; }
  WITH_LOCK=""
else
  WITH_LOCK="flock $LOCKFILE"
fi
setup=$(( $(date +%s) - t0 ))
start=$(date +%s)
# shellcheck disable=SC2086
env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONPATH="$CLONE/src:$PLUG" GOV_CLOSE_SERIAL_ONLY_OF="$CLONE" \
  $WITH_LOCK python3 -m pytest tests -n auto -q -p no:cacheprovider --no-header -p gov_close_serial_only ${NIGHTLY_PYTEST_EXTRA:--o tmp_path_retention_policy=failed} \
  --junitxml="$JUNIT/parallel.xml" > "$OUT/parallel.txt" 2>&1 9>&-
p_exit=$?
mid=$(date +%s)
# shellcheck disable=SC2086
env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONPATH="$CLONE/src:$PLUG" GOV_CLOSE_SERIAL_ONLY_OF="$CLONE" \
  GOV_CLOSE_SERIAL_ONLY_GIVEN="$ENTRIES" \
  $WITH_LOCK python3 -m pytest $ENTRIES -q -p no:cacheprovider --no-header -p gov_close_serial_only ${NIGHTLY_PYTEST_EXTRA:--o tmp_path_retention_policy=failed} \
  --junitxml="$JUNIT/serial.xml" > "$OUT/serial.txt" 2>&1 9>&-
s_exit=$?
end=$(date +%s)
echo "parallel exit $p_exit in $((mid - start)) s: $(tail -1 "$OUT/parallel.txt")" >> "$OUT/run.txt"
echo "serial exit $s_exit in $((end - mid)) s: $(tail -1 "$OUT/serial.txt")" >> "$OUT/run.txt"
# Every failing case, alone (the close's environment), once.
python3 "$HERE/nightly_alone.py" "$CLONE" "$JUNIT" >> "$OUT/run.txt" 2>&1 9>&-
actual=$(( $(date +%s) - t0 ))
# The run is over: the lock and the flag go at once, so closes resume whatever the time (DEC-933 item 2.5).
if [ "$MODE" = night ]; then flock -u 9; exec 9>&-; fi
rm -f "$ORCH/NIGHTLY-RUNNING"; OWN_FLAG=0
echo "duration: estimate ${EST:-none} s, actual $actual s (setup $setup s)" >> "$OUT/run.txt"
python3 "$HERE/nightly_estimate.py" record "$JUNIT/parallel.xml" "$JUNIT/serial.xml" "$setup" "$actual" "$EST" >> "$OUT/run.txt" 2>&1
verdict=$(grep -E '^verdict:' "$OUT/run.txt" | tail -1)
# A night's clone goes once its run is green or flaky; a red night's clone stays for the diagnosis (DEC-934).
if [ "$MODE" = night ]; then
  case "$verdict" in
    "verdict: green"|"verdict: flaky-candidates"*)
      # Only this night's own clone, by its stamp under the nightly's run folder; never any other path.
      case "$CLONE" in
        /home/usain/gov-os-runs/W2-00/nightly/20[0-9][0-9][0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9])
          cd / && rm -rf "$CLONE" && echo "clone removed" >> "$OUT/run.txt" ;;
        *) echo "clone NOT removed: unexpected path $CLONE" >> "$OUT/run.txt" ;;
      esac ;;
    *) echo "clone kept for the diagnosis: $CLONE" >> "$OUT/run.txt" ;;
  esac
fi
date '+%F %T done' >> "$OUT/run.txt"
echo "$(date '+%F %T') $MODE head $HEAD: $(grep -E '^(parallel|serial|verdict|duration)' "$OUT/run.txt" | tr '\n' ' ')" >> "$ORCH/log/nightly/digest.txt"
# A red of the head (cases that fail alone too) is a P1 package (owner, DEC-852, DEC-933): the ping says so at once,
# with counts only; the orchestrator writes the package from run.txt.
case "$verdict" in
  "verdict: red"*) "$PING" "P1 NIGHTLY-RED head $HEAD | $verdict | the orchestrator's package follows" ;;
esac
cat "$OUT/run.txt"
