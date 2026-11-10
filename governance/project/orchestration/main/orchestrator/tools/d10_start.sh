#!/usr/bin/env bash
# Starts d10_run.sh from a clean signal state (run 1's SIGHUP cases failed under the detached start's inherited
# dispositions, group F): every signal back to its default, then a new session (setsid, no nohup), output to the run
# folder. Bash cannot undo a signal ignored at entry, so the reset is done by Python before exec.
#   d10_start.sh <run> <workers>        env passes through (e.g. LIFTED_ONLY=1)
set -u
ROOT=/home/usain/Dynamic-Agentic-Engineering-OS; ORCH=$ROOT/.gov-runtime/scratch/orchestrator
RUN=${1:?run}; W=${2:?workers}; mkdir -p "$ORCH/log/d10/$RUN"
cd "$ROOT" && exec setsid python3 -c '
import os, signal, sys
for s in signal.valid_signals():
    if s not in (signal.SIGKILL, signal.SIGSTOP):
        try: signal.signal(s, signal.SIG_DFL)
        except (OSError, ValueError): pass
signal.pthread_sigmask(signal.SIG_SETMASK, [])
os.execvp("bash", ["bash", sys.argv[1], sys.argv[2], sys.argv[3]])
' "$ORCH/tools/d10_run.sh" "$RUN" "$W" > "$ORCH/log/d10/$RUN/start.out" 2>&1 < /dev/null
