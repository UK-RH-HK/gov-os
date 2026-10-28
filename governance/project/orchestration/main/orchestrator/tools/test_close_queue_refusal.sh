#!/bin/bash
# Tests close_queue.sh's refusal path (owner 2026-10-27): a refused close must stop the queue with a non-zero
# status, log "CLOSE REFUSED", remove the lock and commit nothing.
# Runs the script's own lines from the close call to the refusal line, with a stub gov that refuses (exit 3),
# and once more with a stub that passes, to show that path still goes on past the refusal line.
script=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/close_queue.sh
work=$(mktemp -d)
start=$(grep -n '^  gov close "\$ticket"' "$script" | cut -d: -f1)
end=$(grep -n 'CLOSE REFUSED' "$script" | cut -d: -f1)
[ -n "$start" ] && [ -n "$end" ] || { echo "FAIL: cannot find the close call or the refusal line"; exit 1; }
sed -n "${start},${end}p" "$script" > "$work/body.sh"
fails=0
run() {  # $1 = the stub close's exit code
  rm -f "$work/queue.txt"; touch "$work/lock"
  bash -c 'LOG='"$work"'; LOCK='"$work"'/lock; ticket=DAEO-test; lift=; gov() { return '"$1"'; }
    source '"$work"'/body.sh; echo REACHED-AFTER-REFUSAL-LINE; exit 0' > "$work/out.txt" 2>&1
}
run 3; code=$?
[ "$code" -eq 4 ] || { echo "FAIL: refused close gave exit $code, expected 4"; fails=1; }
grep -q 'DAEO-test CLOSE REFUSED (exit 3)' "$work/queue.txt" || { echo "FAIL: no CLOSE REFUSED line"; fails=1; }
[ ! -e "$work/lock" ] || { echo "FAIL: lock left behind"; fails=1; }
grep -q REACHED "$work/out.txt" && { echo "FAIL: went on past a refusal"; fails=1; }
run 0; code=$?
[ "$code" -eq 0 ] && grep -q REACHED "$work/out.txt" || { echo "FAIL: a passing close did not go on (exit $code)"; fails=1; }
grep -q 'CLOSE REFUSED' "$work/queue.txt" && { echo "FAIL: a passing close logged a refusal"; fails=1; }
rm -rf "$work"
[ "$fails" -eq 0 ] && echo "PASS: refused close -> exit 4, logged, lock removed; passing close goes on"
exit "$fails"
