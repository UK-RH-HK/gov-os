#!/usr/bin/env bash
# Tool trial a, redone (DEC-889 item 13 a): does pytest-timeout's per-test limit fire inside a test whose code runs in
# a child gov process, and is the child left behind? A hang is planted at the top of gov doctor's run() (a path only
# a child gov process runs) in a clone of the trials' clone. W1-07's doctor envelope case runs with --timeout 60,
# alone and under -n 2, each with the default method (signal) and with --timeout-method thread.
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
VENV=/tmp/gov-os-tooltrial/bin/python
OUT=$(ls -td "$ORCH"/log/tooltrials/*/ | head -1)
SRC=$(ls -td /home/usain/gov-os-runs/W2-00/tooltrials/*/ | head -1)repo
HANG=${SRC}-hang2
rm -rf "$HANG"
git clone -q --no-hardlinks "$SRC" "$HANG"
python3 "$ORCH/tools/plant_hang.py" "$HANG/src/gov/doctor/command.py" || exit 2
echo "$(date '+%F %T') a2: hang planted: $(git -C "$HANG" diff --stat | tail -1)" >> "$OUT/run.txt"
for method in signal thread; do
  for form in alone n2; do
    extra=""; [ "$form" = n2 ] && extra="-n 2"
    s=$(date +%s)
    # shellcheck disable=SC2086
    ( cd "$HANG" && env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONPATH="$HANG/src" timeout 900 "$VENV" -m pytest -q \
        -p no:cacheprovider --no-header -p timeout --timeout 60 --timeout-method "$method" $extra \
        "tests/acceptance/W1-07/test_w1_07_envelope.py::test_every_command_returns_the_envelope[doctor]" \
        > "$OUT/a2-$method-$form.txt" 2>&1 )
    e=$?
    sleep 5
    left=$(pgrep -fc "$HANG/src" || true)
    echo "$(date '+%F %T') a2 ($method, $form): exit $e in $(( $(date +%s) - s )) s; children still alive: $left; $(grep -m1 -o 'Timeout[^|]*' "$OUT/a2-$method-$form.txt" | head -c 160)" >> "$OUT/run.txt"
    pkill -f "$HANG/src" 2>/dev/null || true
  done
done
tail -5 "$OUT/run.txt"
