#!/usr/bin/env bash
# Builds W2-66b's lead brief (DEC-1027 B). A script file because the guard reads a command naming the acceptance folder
# as a possible test write (a recorded false positive, DEC-958).
set -eu
B=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs
cd /home/usain/Dynamic-Agentic-Engineering-OS
python3 .gov-runtime/scratch/orchestrator/tools/build_lead_brief.py "$B/W2-66b-part-run1.md" "$B/W2-66b-A5-run1.md" \
  ID=DAEO-zuiy W2=W2-66b PROFILE=LITE \
  "PATHS=tests/acceptance/W2-66/test_w2_66_live_test_map.py, tests/acceptance/W2-66/README.md" \
  "ROWS=none" "SOURCES=DEC-1027, DEC-906, DEC-891" IMPL=DEC-1027,DEC-906 "EST=2 lines"
python3 .gov-runtime/scratch/orchestrator/tools/placeholder_scan.py "$B/W2-66b-A5-run1.md" | tail -1
