#!/usr/bin/env bash
# Watches the main repository's core.bare (set to true once, 2026-11-04 00:31:12, cause not found; restored 00:37:53).
# Every 2 s: if core.bare reads true, log the time and every process whose args name git (with its cwd), set it back
# to false (the state the main tree needs), and drop an inbox item for the CTO. Never exits on its own.
set -u
R=/home/usain/Dynamic-Agentic-Engineering-OS
ORCH=$R/.gov-runtime/scratch/orchestrator
LOG=$ORCH/log/bare-watch.log
echo "$(date '+%F %T') start" >> "$LOG"
while :; do
  if [ "$(git --git-dir="$R/.git" config --get core.bare)" = true ]; then
    {
      echo "$(date '+%F %T.%N') core.bare = true; processes:"
      for p in $(ps -eo pid=); do
        a=$(tr '\0' ' ' < /proc/$p/cmdline 2>/dev/null) || continue
        case "$a" in *git*|*pytest*|*gov*) echo "  $p [$(readlink /proc/$p/cwd 2>/dev/null)] ${a:0:200}";; esac
      done
    } >> "$LOG"
    git --git-dir="$R/.git" config core.bare false
    printf 'log: bare-watch.log\nGit: core.bare was true\nstatus: set back to false; the processes at that moment are in the log\n' \
      > "$ORCH/dispatch/inbox/$(date +%Y%m%d-%H%M%S)-git-bare.txt"
  fi
  sleep 2
done
