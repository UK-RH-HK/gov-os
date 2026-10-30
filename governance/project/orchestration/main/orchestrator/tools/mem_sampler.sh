#!/usr/bin/env bash
# Samples every running lead's process-tree memory and the machine's figures once a minute (DEC-942 items 2 and 6),
# into log/lead-mem.jsonl. Runs until stopped.
while true; do
  python3 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/lead_mem.py --record > /dev/null 2>&1
  sleep 60
done
