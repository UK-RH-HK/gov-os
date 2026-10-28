#!/usr/bin/env bash
# A full run in the close's form, WITH THE CURRENT PIN, on a fresh clone of w2/integrate's head with a path-map patch
# applied to its tree (owner, standing, DEC-925 item 2; asked for ACT-W2-57-LS-1 on 2026-10-28).
# Usage: act_clone_run.sh <name> <patch>
# The close's form, as the pinned `gov close` builds it (gov/close/command.py of the current pin):
#   the pin's interpreter; PYTHONPATH = the clone's src/ (the close sets it so); the parallel run of tests/ with the
#   pin's serial-only plugin, -n auto, --dist load, --timeout=900 --timeout_method=signal (the test map's
#   per_test_timeout and distribution), tmp_path retention "failed"; then the declared cases alone and serially;
#   every failing case re-run alone with the pin's interpreter. No load_sensitive re-run: a plain run reports raw reds,
#   so a removed entry's test that fails shows here as a red.
# Writes nothing in the repository; JUnit XML outside .gov-runtime/ (DEC-911).
NAME=$1
PATCH=$2
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
REPO=/home/usain/Dynamic-Agentic-Engineering-OS
# The current pin, whichever it is: the interpreter on the first line of ~/.local/bin/gov (as close_queue.sh reads it),
# so this script follows every re-pin (DEC-933 item 1).
PY=$(head -1 /home/usain/.local/bin/gov | sed 's/^#!//')
PIN=$(dirname "$(dirname "$PY")")
[ -x "$PY" ] || { echo "the pinned gov names no interpreter that runs: $PY"; exit 2; }
PLUG=$PIN/lib/python3.12/site-packages/gov/close/pytest_plugin
STAMP=$(date +%Y%m%d-%H%M)
OUT=$ORCH/log/act-runs/$NAME-$STAMP
CLONE=/home/usain/gov-os-runs/W2-00/act-runs/$NAME-$STAMP
JUNIT=/tmp/gov-os-act-junit/$NAME-$STAMP
mkdir -p "$OUT" "$JUNIT" /home/usain/gov-os-runs/W2-00/act-runs
[ -e "$ORCH/CLOSE-RUNNING" ] && { echo "a close is running: no run" > "$OUT/run.txt"; exit 2; }
disk=$(bash "$ORCH/tools/disk_gate.sh" 2>&1) || { echo "NOT STARTED: $disk" > "$OUT/run.txt"; exit 2; }
date '+%F %T start' > "$OUT/run.txt"
git clone -q --no-hardlinks --branch w2/integrate "$REPO" "$CLONE" || { echo "clone failed" >> "$OUT/run.txt"; exit 2; }
echo "head $(git -C "$CLONE" rev-parse --short=12 HEAD)" >> "$OUT/run.txt"
git -C "$CLONE" apply "$PATCH" || { echo "patch does not apply" >> "$OUT/run.txt"; exit 2; }
echo "patch applied to the tree: $(git -C "$CLONE" diff --stat | tail -1)" >> "$OUT/run.txt"
cd "$CLONE" || exit 2
# The close runs after a rebuild: the tests that read the repository's own state need its stores.
env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONPATH="$CLONE/src" "$PY" -m gov.cli.main rebuild --json \
  > "$OUT/rebuild.json" 2> "$OUT/rebuild.err" || { echo "clone rebuild failed" >> "$OUT/run.txt"; exit 2; }
echo "clone rebuilt" >> "$OUT/run.txt"
# No -E here: -E drops PYTHONPATH, and the plugin then never loads (2026-10-28: 0 entries read, run stopped).
ENTRIES=$(env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONPATH="$PLUG" "$PY" -c "import pathlib, gov_close_serial_only as s; print('\n'.join(s.entries(pathlib.Path('.'))))" 2>> "$OUT/run.txt")
count=$(echo "$ENTRIES" | grep -c .)
echo "serial-only entries (pin's reading): $count" >> "$OUT/run.txt"
# The list holds well over a hundred entries; none read means the reading failed, and the serial run would be the
# whole suite.
[ "$count" -gt 0 ] || { echo "STOPPED: no serial-only entry read" >> "$OUT/run.txt"; exit 2; }
OPTS="-q -p no:cacheprovider --tb=line --no-header --timeout=900 --timeout_method=signal -o tmp_path_retention_policy=failed"
start=$(date +%s)
# shellcheck disable=SC2086
env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONPATH="$CLONE/src:$PLUG" GOV_CLOSE_SERIAL_ONLY_OF="$CLONE" \
  flock /tmp/gov-os-verify.lock "$PY" -m pytest "$CLONE/tests" $OPTS -n auto --dist load -p gov_close_serial_only \
  --junitxml="$JUNIT/parallel.xml" > "$OUT/parallel.txt" 2>&1
p_exit=$?
mid=$(date +%s)
# shellcheck disable=SC2086
env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONPATH="$CLONE/src:$PLUG" GOV_CLOSE_SERIAL_ONLY_OF="$CLONE" \
  GOV_CLOSE_SERIAL_ONLY_GIVEN="$ENTRIES" \
  flock /tmp/gov-os-verify.lock "$PY" -m pytest $ENTRIES $OPTS -p gov_close_serial_only \
  --junitxml="$JUNIT/serial.xml" > "$OUT/serial.txt" 2>&1
s_exit=$?
end=$(date +%s)
echo "parallel exit $p_exit in $((mid - start)) s: $(tail -1 "$OUT/parallel.txt")" >> "$OUT/run.txt"
echo "serial exit $s_exit in $((end - mid)) s: $(tail -1 "$OUT/serial.txt")" >> "$OUT/run.txt"
"$PY" /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/nightly/nightly_alone.py "$CLONE" "$JUNIT" >> "$OUT/run.txt" 2>&1
du -sh "$CLONE" >> "$OUT/run.txt" 2>&1
date '+%F %T done' >> "$OUT/run.txt"
cat "$OUT/run.txt"
