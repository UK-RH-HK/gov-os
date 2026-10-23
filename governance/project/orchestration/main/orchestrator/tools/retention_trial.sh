#!/usr/bin/env bash
# DEC-904 item 1: the retention trial. One full parallel run in the close's form on a clone of w2/integrate's head,
# with pytest's -o tmp_path_retention_policy=failed, under the verification lock, measured: the temp folder's peak
# inodes and size (sampled every 30 s), the wall time, the results (against W2-50's close: 14,830 passed, 31 skipped),
# and that a failing test's folder is kept (one planted failing test, in the clone only). Writes only under
# /tmp/gov-os-trial-retention/. Its own scratch budget is the bridge cap: 6,000,000 inodes, 60 GB.
T=/tmp/gov-os-trial-retention
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
OUT=$T/out
mkdir -p "$OUT" "$T/tmp"
log() { echo "$(date '+%F %T') $*" >> "$OUT/run.txt"; }
bash "$ORCH/tools/disk_gate.sh" 2>> "$OUT/run.txt" || { log "NOT STARTED: the disk gate is shut"; exit 2; }
[ -e "$ORCH/CLOSE-RUNNING" ] && { log "NOT STARTED: a close is running"; exit 2; }
rm -rf "$T/clone"
git clone -q --no-hardlinks --branch w2/integrate /home/usain/Dynamic-Agentic-Engineering-OS "$T/clone" || { log "clone failed"; exit 2; }
log "clone at $(git -C "$T/clone" log -1 --format=%h)"
cd "$T/clone" || exit 2
mkdir -p tests/acceptance/ZZ-retention-trial
printf '%s\n' 'def test_a_failing_test_keeps_its_folder(tmp_path):' \
  '    (tmp_path / "kept-marker.txt").write_text("kept")' \
  '    assert False, "planted failure for the retention trial (DEC-904)"' > tests/acceptance/ZZ-retention-trial/test_zz_retention_trial.py
env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONPATH="$T/clone/src" TMPDIR="$T/tmp" python3 -m gov.cli.main rebuild --json \
  > "$OUT/rebuild.json" 2> "$OUT/rebuild.err" || { log "clone rebuild failed"; exit 2; }
log "clone rebuilt"
PLUG=$(python3 -c "import pathlib, gov.close.pytest_plugin as p; print(pathlib.Path(p.__file__).parent)" 2>/dev/null)
# The sampler: the temp folder's inodes and bytes every 30 s, until the run ends.
( while [ ! -e "$OUT/done" ]; do
    n=$(find "$T/tmp" -xdev 2>/dev/null | wc -l); b=$(du -sb "$T/tmp" 2>/dev/null | cut -f1)
    echo "$(date +%s) $n $b" >> "$OUT/samples.txt"; sleep 30
  done ) &
log "waiting for the verification lock"
start=$(date +%s)
flock /tmp/gov-os-verify.lock env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONPATH="$T/clone/src:$T/clone/src/gov/close/pytest_plugin" \
  GOV_CLOSE_SERIAL_ONLY_OF="$T/clone" TMPDIR="$T/tmp" \
  python3 -m pytest tests -n auto -q -p no:cacheprovider --no-header -p gov_close_serial_only \
  -o tmp_path_retention_policy=failed --junitxml="$OUT/parallel.xml" > "$OUT/parallel.txt" 2>&1
code=$?
end=$(date +%s)
touch "$OUT/done"
sleep 31
log "parallel exit $code in $((end - start)) s (lock wait included): $(tail -1 "$OUT/parallel.txt")"
kept=$(find "$T/tmp" -name kept-marker.txt 2>/dev/null | wc -l)
log "the planted failing test's folder kept: $kept file(s) named kept-marker.txt"
log "peak: $(sort -k2 -n "$OUT/samples.txt" | tail -1 | awk '{print $2 " inodes, " $3 / 1e9 " GB"}'); after the run: $(find "$T/tmp" -xdev | wc -l) inodes"
log "trial done"
