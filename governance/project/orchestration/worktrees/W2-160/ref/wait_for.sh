#!/usr/bin/env bash
# Waits for a job's exit file (TPL-3b: R3-TEMPLATES D, TPL-3 S5; R2-6, R2-9; DEC-1052, DEC-1079), bounded.
#   wait_for.sh <exit-file> [<max-s>]
# Blocks until <exit-file> is non-empty or <max-s> pass (default and ceiling 570 s, under the Bash tool's 600 s), then
# prints the job's tail and its exit code. It waits on the file, never on a process name. When a pid file sits beside
# it (<base>.pid, as launch_worker.sh and lead_verify.sh write; <base> is the exit file's path less .exit), the job's
# liveness is asked of proc.sh by that pid only (L-0075, DEC-1073 (4)): a job gone without its exit file is named at
# once, not waited for.
# The tail: WAIT_FOR_LOG, else the first of <base>.log, <base>.json, <base>.txt that exists; for a JSON log (a
# `claude -p --output-format json` one, launcher lines before it) the last object's session_id, is_error and the end of
# its `result`; then <base>.summary, if there.
# Exit: the job's code when its exit file is there; 124 still running at <max-s> ("RUNNING"); 125 the job's process
# is gone and wrote no exit file ("GONE"); 2 a usage error or an exit file that holds no number.
# Env: WAIT_FOR_EVERY (poll, s; 5), WAIT_FOR_LINES (tail lines; 30), WAIT_FOR_PROC (proc.sh; for tests).
set -u
CAP=570
f=${1:-}; max=${2:-$CAP}
[ -n "$f" ] || { sed -n 2,14p "$0"; exit 2; }
case "$max" in ""|*[!0-9]*) echo "wait_for: <max-s> is not a number: $max" >&2; exit 2;; esac
[ "$max" -le "$CAP" ] || { echo "wait_for: <max-s> $max capped at $CAP" >&2; max=$CAP; }
every=${WAIT_FOR_EVERY:-5} lines=${WAIT_FOR_LINES:-30}
PROC=${WAIT_FOR_PROC:-$(cd "$(dirname "$0")" && pwd)/proc.sh}
base=${f%.exit}
gone() {  # the job's process (by its pid file only) has exited
  [ -s "$base.pid" ] || return 1
  local pid; pid=$(head -c 20 "$base.pid" | tr -dc 0-9)
  [ -n "$pid" ] && bash "$PROC" wait --max 0 "$pid" > /dev/null 2>&1
}
tail_of() {
  local log=${WAIT_FOR_LOG:-} c
  if [ -z "$log" ]; then for c in "$base.log" "$base.json" "$base.txt"; do [ -f "$c" ] && { log=$c; break; }; done; fi
  [ -n "$log" ] && [ -f "$log" ] || { echo "wait_for: no log beside $f"; return; }
  echo "--- tail of $log"
  python3 -I - "$log" "$lines" <<'PY' || tail -n "$lines" "$log" | cut -c1-400
import json, sys
path, n = sys.argv[1], int(sys.argv[2])
text = open(path, encoding="utf-8", errors="replace").read()
for line in reversed(text.splitlines()):
    line = line.strip()
    if line.startswith("{"):
        try:
            obj = json.loads(line)
        except ValueError:
            continue
        if isinstance(obj, dict) and "result" in obj:
            print(f"session_id={obj.get('session_id')} is_error={obj.get('is_error')} turns={obj.get('num_turns')}")
            print(str(obj.get("result"))[-4000:])
            sys.exit(0)
print("\n".join(l[:400] for l in text.splitlines()[-n:]))
PY
  [ -f "$base.summary" ] && { echo "--- $base.summary"; cat "$base.summary"; }
}
end=$(( $(date +%s) + max ))
while [ ! -s "$f" ]; do
  if gone; then
    sleep 1; [ -s "$f" ] && break
    tail_of; echo "wait_for: GONE: the job's process ($(cat "$base.pid")) exited without writing $f"; exit 125
  fi
  [ "$(date +%s)" -ge "$end" ] && { echo "wait_for: RUNNING after ${max}s: $f"; exit 124; }
  sleep "$every"
done
code=$(head -n 1 "$f" | tr -d ' \r\n')
tail_of
case "$code" in ""|*[!0-9]*) echo "wait_for: $f holds no exit code: '$code'"; exit 2;; esac
echo "wait_for: DONE exit $code ($f)"
exit $(( code % 256 ))
