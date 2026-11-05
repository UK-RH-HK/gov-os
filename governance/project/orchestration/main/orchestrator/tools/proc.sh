#!/usr/bin/env bash
# Waits and stops by process id or process group only, never by a name match (L-0075; DEC-1073 (4), standing).
#   proc.sh wait --max <seconds> [--every <seconds>] <pid|-pgid> ...   wait until every one has exited
#   proc.sh stop [--grace <seconds>] <pid|-pgid> ...                   SIGTERM, then SIGKILL after the grace (30 s)
#   proc.sh pgid <pid>                                                 the process group of a pid (to wait on later)
# A target "-N" is process group N. `wait` exits 0 when all have exited, 124 at --max (a deterministic timeout,
# never an unbounded wait); `stop` exits 0 when all are gone, 1 if any survived SIGKILL. Only the ids given are
# touched: no pattern, no pgrep, so a waiter can never match itself.
set -u
alive() {  # any of the targets still running?
  local t
  for t in "$@"; do
    if [ "${t#-}" != "$t" ]; then kill -0 -- "$t" 2>/dev/null && return 0
    else kill -0 "$t" 2>/dev/null && [ "$(ps -o stat= -p "$t" 2>/dev/null | cut -c1)" != Z ] && return 0; fi
  done
  return 1
}
check() { local t; for t in "$@"; do [[ "$t" =~ ^-?[0-9]+$ ]] || { echo "proc.sh: not a pid or -pgid: $t" >&2; exit 2; }; done; }
cmd=${1:-}; shift || true
case "$cmd" in
  wait)
    max= every=5
    while [ $# -gt 0 ]; do case "$1" in --max) max=$2; shift 2;; --every) every=$2; shift 2;; *) break;; esac; done
    [ -n "$max" ] || { echo "proc.sh wait: --max is required (L-0075: every wait is bounded)" >&2; exit 2; }
    [ $# -gt 0 ] || { echo "proc.sh wait: no target" >&2; exit 2; }
    check "$@"
    end=$(( $(date +%s) + max ))
    while alive "$@"; do
      [ "$(date +%s)" -ge "$end" ] && { echo "proc.sh wait: timeout after ${max}s: $*"; exit 124; }
      sleep "$every"
    done
    echo "proc.sh wait: exited: $*"; exit 0;;
  stop)
    grace=30
    [ "${1:-}" = --grace ] && { grace=$2; shift 2; }
    [ $# -gt 0 ] || { echo "proc.sh stop: no target" >&2; exit 2; }
    check "$@"
    for t in "$@"; do kill -TERM -- "$t" 2>/dev/null; done
    end=$(( $(date +%s) + grace ))
    while alive "$@" && [ "$(date +%s)" -lt "$end" ]; do sleep 1; done
    if alive "$@"; then for t in "$@"; do kill -KILL -- "$t" 2>/dev/null; done; sleep 1; fi
    alive "$@" && { echo "proc.sh stop: survived SIGKILL: $*"; exit 1; }
    echo "proc.sh stop: stopped: $*"; exit 0;;
  pgid) check "$1"; ps -o pgid= -p "$1" | tr -d ' ';;
  *) sed -n 2,8p "$0"; exit 2;;
esac
