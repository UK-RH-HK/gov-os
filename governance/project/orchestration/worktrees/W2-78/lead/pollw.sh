#!/bin/bash
# Waits at most $2 seconds (default 540) for the worker log $1 to hold its session's final JSON ("session_id"); prints a status line.
n=0; max=${2:-540}
while ! grep -q '"session_id"' "$1" 2>/dev/null && [ $n -lt $max ]; do sleep 15; n=$((n+15)); done
if grep -q '"session_id"' "$1" 2>/dev/null; then echo "DONE $(date +%H:%M)"; else echo "running $(date +%H:%M) load $(cut -d' ' -f1 /proc/loadavg) log $(wc -c < "$1") bytes"; fi
