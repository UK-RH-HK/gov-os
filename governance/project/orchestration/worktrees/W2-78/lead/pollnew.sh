#!/bin/bash
# Waits at most $3 seconds (default 540) for file $1 to be modified after the epoch second $2; prints it or a status.
n=0; max=${3:-540}
while { [ ! -e "$1" ] || [ "$(stat -c %Y "$1")" -le "$2" ]; } && [ $n -lt $max ]; do sleep 15; n=$((n+15)); done
if [ -e "$1" ] && [ "$(stat -c %Y "$1")" -gt "$2" ]; then echo "NEW: $(cat "$1")"; else echo "waiting $(date +%H:%M) load $(cut -d' ' -f1 /proc/loadavg)"; ls /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/ | grep RUNNING; fi
