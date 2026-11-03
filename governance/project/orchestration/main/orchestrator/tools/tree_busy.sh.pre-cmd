#!/usr/bin/env bash
# Is anything running in a worktree? Prints "BUSY <pid> <command>" lines and exits 0, or prints "IDLE" and exits 1.
# Judged by each process's working folder, never by `pgrep -f` on a path (that matches the caller's own shell:
# slipped twice, DEC-1012). The caller's own chain of processes is left out.
# Usage: tree_busy.sh <W2-id | worktree path>
set -u
arg=${1:?usage: tree_busy.sh <W2-id | worktree path>}
case "$arg" in /*) tree=$arg ;; *) tree=$HOME/gov-os-worktrees/$arg ;; esac
tree=$(readlink -f "$tree") || { echo "no such tree: $arg" >&2; exit 2; }
mine=" "; p=$$
while [ -n "$p" ] && [ "$p" -gt 1 ]; do mine="$mine$p "; p=$(awk '/^PPid:/{print $2}' /proc/$p/status 2>/dev/null); done
busy=0
for d in /proc/[0-9]*; do
  pid=${d#/proc/}
  case "$mine" in *" $pid "*) continue ;; esac
  cwd=$(readlink "$d/cwd" 2>/dev/null) || continue
  case "$cwd/" in "$tree"/*) busy=1; echo "BUSY $pid $(tr '\0' ' ' < "$d/cmdline" 2>/dev/null | cut -c1-120)" ;; esac
done
[ $busy = 1 ] && exit 0
echo IDLE; exit 1
