#!/usr/bin/env bash
# Builds W1-01b's lead brief (DEC-1031 item 3). A script file: a command naming the acceptance folder reads to the guard
# as a possible test write (DEC-958).
set -eu
B=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs
cd /home/usain/Dynamic-Agentic-Engineering-OS
python3 .gov-runtime/scratch/orchestrator/tools/build_lead_brief.py "$B/W1-01b-part-run1.md" "$B/W1-01b-A5-run1.md" \
  ID=DAEO-vhad W2=W1-01b PROFILE=LITE \
  "PATHS=tests/acceptance/W1-01/w1_01_support.py, tests/acceptance/W1-01/test_w1_01_integration_merges.py, tests/acceptance/W1-01/README.md" \
  "ROWS=none" "SOURCES=DEC-1031, DEC-906, DEC-253" IMPL=DEC-1031,DEC-906 "EST=20 lines"
python3 .gov-runtime/scratch/orchestrator/tools/placeholder_scan.py "$B/W1-01b-A5-run1.md" | tail -1
