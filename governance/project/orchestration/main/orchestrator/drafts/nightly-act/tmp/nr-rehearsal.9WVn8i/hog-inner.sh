#!/usr/bin/env bash
: > "$NR_ORCH/NIGHTLY-RUNNING"
d="$NR_ORCH/log/nightly/$(date +%Y%m%d-%H%M)"; mkdir -p "$d"; echo "$(date +%F) nightly night: planted" > "$d/run.txt"
sleep 120 &
echo $! > "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/nightly-act/tmp/nr-rehearsal.9WVn8i/sibling.pid"
python3 -I "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/nightly-act/tmp/nr-rehearsal.9WVn8i/hog.py" 600
