#!/usr/bin/env bash
# The owner's tool trials (DEC-889 item 13), with lens H's remaining trials first. In quiet windows, never during a
# close or a nightly run: every step waits for both locks to be absent and the load below 3 for 5 minutes.
#   0. lens H's remaining trials (its own runner, which waits on the close lock itself);
#   1-5. full parallel runs in the close's parallel form on one fresh, rebuilt clone, all with the owner's trial venv
#        (/tmp/gov-os-tooltrial, --system-site-packages): (1) --dist load, (2) --dist worksteal, (3) worksteal with
#        pytest-timeout (--timeout 900), (4) worksteal with pytest-rerunfailures (--reruns 2), (5) worksteal with
#        pytest-randomly (-p randomly);
#   6. trial a: a hang planted in a child-only path (gov doctor's command) of a second clone, and W1-07's doctor case
#      with --timeout 60, alone and under -n 2: does the limit fire, and is any child left behind;
#   7. trial c: grimp's selection on lens H's planted faults (tooltrial_grimp.py).
# Results: .gov-runtime/scratch/orchestrator/log/tooltrials/<stamp>/. Writes nothing in the repository.
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
REPO=/home/usain/Dynamic-Agentic-Engineering-OS
VENV=/tmp/gov-os-tooltrial/bin/python
STAMP=$(date +%Y%m%d-%H%M)
OUT=$ORCH/log/tooltrials/$STAMP
RUNS=/home/usain/gov-os-runs/W2-00/tooltrials/$STAMP
mkdir -p "$OUT" "$RUNS"
quiet() {
  q=0
  while [ "$q" -lt 5 ]; do
    if [ ! -e "$ORCH/CLOSE-RUNNING" ] && [ ! -e "$ORCH/NIGHTLY-RUNNING" ] && awk '{exit !($1 < 3)}' /proc/loadavg; then
      q=$((q + 1)); else q=0; fi
    sleep 60
  done
  # DEC-898: free disk space and free inodes above the floor, or the trials stop.
  disk=$(bash "$ORCH/tools/disk_gate.sh" 2>&1) || { log "STOPPED: $disk"; exit 2; }
}
log() { echo "$(date '+%F %T') $*" >> "$OUT/run.txt"; }

quiet; log "0 lens H rest: start"
bash /tmp/gov-os-assessment-H/scripts/run_rest.sh > "$OUT/lensH-rest.txt" 2>&1
log "0 lens H rest: exit $? ($(tail -1 /tmp/gov-os-assessment-H/logs/rest.log))"
python3 -I /tmp/gov-os-assessment-H/scripts/analyse_b2.py > "$OUT/lensH-analyse_b2.txt" 2>&1
python3 -I /tmp/gov-os-assessment-H/scripts/analyse_a6.py > "$OUT/lensH-analyse_a6.txt" 2>&1

quiet
CLONE=$RUNS/repo
git clone -q --no-hardlinks --branch w2/integrate "$REPO" "$CLONE"
log "clone $(git -C "$CLONE" rev-parse --short HEAD)"
( cd "$CLONE" && env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONPATH="$CLONE/src" python3 -m gov.cli.main rebuild --json > "$OUT/rebuild.json" 2> "$OUT/rebuild.err" )
log "clone rebuilt: exit $?"
PLUG=$CLONE/src/gov/close/pytest_plugin
run() {  # name, extra pytest arguments...
  name=$1; shift
  quiet
  log "$name: start (load $(cut -d' ' -f1 /proc/loadavg))"
  s=$(date +%s)
  ( cd "$CLONE" && env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONPATH="$CLONE/src:$PLUG" GOV_CLOSE_SERIAL_ONLY_OF="$CLONE" \
      "$VENV" -m pytest tests -n auto -q -p no:cacheprovider --no-header -p gov_close_serial_only "$@" \
      --junitxml="$OUT/$name.xml" > "$OUT/$name.txt" 2>&1 )
  e=$?
  log "$name: exit $e in $(( $(date +%s) - s )) s: $(tail -1 "$OUT/$name.txt")"
}
run b1-load --dist load
run b2-worksteal --dist worksteal
run a-cost-timeout --dist worksteal -p timeout --timeout 900
run d1-rerunfailures --dist worksteal -p rerunfailures --reruns 2
run d2-randomly --dist worksteal -p randomly

# Trial a: a hang in a child-only path.
quiet
HANG=$RUNS/repo-hang
git clone -q --no-hardlinks "$CLONE" "$HANG"
python3 - "$HANG/src/gov/doctor/command.py" <<'PY'
import sys, re
p = sys.argv[1]; t = open(p).read()
m = re.search(r"^def run\(.*?\):\n", t, re.M)
assert m, "no run() in gov/doctor/command.py"
t = t[:m.end()] + "    import time; time.sleep(3600)  # tool trial a: a planted hang in a child-only path\n" + t[m.end():]
open(p, "w").write(t)
PY
log "a: hang planted in $(git -C "$HANG" diff --stat | tail -1)"
for form in alone n2; do
  extra=""; [ "$form" = n2 ] && extra="-n 2"
  s=$(date +%s)
  # shellcheck disable=SC2086
  ( cd "$HANG" && env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONPATH="$HANG/src" timeout 900 "$VENV" -m pytest -q -p no:cacheprovider \
      --no-header -p timeout --timeout 60 $extra "tests/acceptance/W1-07/test_w1_07_envelope.py::test_every_command_returns_the_envelope[doctor]" \
      > "$OUT/a-hang-$form.txt" 2>&1 )
  e=$?
  sleep 5
  left=$(pgrep -fc "$HANG/src" || true)
  log "a ($form): exit $e in $(( $(date +%s) - s )) s; children of the hang clone still alive: $left; $(grep -m1 -o 'Timeout[^\n]*' "$OUT/a-hang-$form.txt" | head -c 200)"
  pkill -f "$HANG/src" 2>/dev/null || true
done

# Trial c: grimp.
"$VENV" "$ORCH/tools/tooltrial_grimp.py" "$CLONE" > "$OUT/c-grimp.txt" 2>&1
log "c: grimp analysis exit $?"
log "done"
cat "$OUT/run.txt"
