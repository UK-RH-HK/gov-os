#!/bin/bash
# Tests close_queue.sh's gate (d) (2026-10-29): the tree tool's own exit decides. A crash with no output must stop
# the queue (it passed through `| head`), a dirty tree must stop it naming the paths, and a clean tree goes on.
# Runs the script's own gate lines with a stub python3, and checks stop_after's label on the same stub harness.
script=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/close_queue.sh
work=$(mktemp -d)
start=$(grep -n "The tool's own exit decides" "$script" | cut -d: -f1)
end=$(grep -n 'or the tool failed (exit' "$script" | cut -d: -f1)
[ -n "$start" ] && [ -n "$end" ] || { echo "FAIL: cannot find gate (d)"; exit 1; }
sed -n "${start},${end}p" "$script" > "$work/body.sh"
grep -n '^  stop() \|^  stop_after() ' "$script" | cut -d: -f2- > "$work/stops.sh"
[ "$(wc -l < "$work/stops.sh")" -eq 2 ] || { echo "FAIL: cannot find stop and stop_after"; exit 1; }
fails=0
run() {  # $1 = the stub tool's exit code, $2 = its output
  rm -f "$work/queue.txt"; touch "$work/lock"
  bash -c 'LOG='"$work"'; LOCK='"$work"'/lock; ticket=DAEO-test; source '"$work"'/stops.sh
    python3() { printf "%s" "'"$2"'"; return '"$1"'; }
    source '"$work"'/body.sh; echo REACHED-AFTER-GATE; exit 0' > "$work/out.txt" 2>&1
}
run 2 ""; code=$?
[ "$code" -eq 2 ] || { echo "FAIL: a crashed tool gave exit $code, expected 2"; fails=1; }
grep -q 'STOPPED BEFORE THE CLOSE: .*the tool failed (exit 2)' "$work/queue.txt" || { echo "FAIL: crash not logged"; fails=1; }
grep -q REACHED "$work/out.txt" && { echo "FAIL: went on past a crashed tool"; fails=1; }
[ ! -e "$work/lock" ] || { echo "FAIL: lock left after a crash"; fails=1; }
run 1 "src/x.py"; code=$?
[ "$code" -eq 2 ] && grep -q 'src/x.py' "$work/queue.txt" || { echo "FAIL: a dirty tree did not stop with its path (exit $code)"; fails=1; }
run 0 ""; code=$?
[ "$code" -eq 0 ] && grep -q REACHED "$work/out.txt" || { echo "FAIL: a clean tree did not go on (exit $code)"; fails=1; }
rm -f "$work/queue.txt"; touch "$work/lock"
bash -c 'LOG='"$work"'; LOCK='"$work"'/lock; ticket=DAEO-test; source '"$work"'/stops.sh; stop_after "x"' > /dev/null 2>&1; code=$?
[ "$code" -eq 3 ] && grep -q 'DAEO-test STOPPED AFTER THE CLOSE (exit 0), OUTPUTS NOT COMMITTED: x' "$work/queue.txt" \
  && [ ! -e "$work/lock" ] || { echo "FAIL: stop_after's label, exit or lock (exit $code)"; fails=1; }
rm -rf "$work"
[ "$fails" -eq 0 ] && echo "PASS: gate (d) stops on a crash and on a dirty tree, goes on when clean; stop_after labelled, exit 3"
exit "$fails"
