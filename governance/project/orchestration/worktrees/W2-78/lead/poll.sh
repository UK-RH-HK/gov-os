#!/bin/bash
# Waits at most $2 seconds (default 540) for the file $1 to be non-empty; prints it or "still waiting".
n=0; max=${2:-540}
while [ ! -s "$1" ] && [ $n -lt $max ]; do sleep 15; n=$((n+15)); done
if [ -s "$1" ]; then cat "$1"; else echo "still waiting $(date +%H:%M) load $(cut -d' ' -f1 /proc/loadavg)"; ls /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/ | grep RUNNING; fi
