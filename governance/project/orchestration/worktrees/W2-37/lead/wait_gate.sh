#!/usr/bin/env bash
# Bounded wait (at most 30 min) until the resource gate (gate_check.py) is open; prints its last line.
G=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/gate_check.py
timeout 1800 bash -c "until python3 $G >/dev/null 2>&1; do sleep 30; done"
echo "rc $?"; python3 "$G"; uptime
