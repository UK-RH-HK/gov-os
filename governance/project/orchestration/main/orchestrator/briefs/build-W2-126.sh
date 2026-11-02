#!/usr/bin/env bash
# Builds W2-126's run-1 lead brief (DEC-1032; the tests only).
set -eu
B=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs
cd /home/usain/Dynamic-Agentic-Engineering-OS
python3 .gov-runtime/scratch/orchestrator/tools/build_lead_brief.py "$B/W2-126-part-run1.md" "$B/W2-126-A5-run1.md" \
  ID=DAEO-jpr0 W2=W2-126 PROFILE=STANDARD \
  "PATHS=src/gov/retrieval/semantic.py, src/gov/retrieval/vector_cache.py, tests/unit/retrieval/test_w2_126*, docs/changes/W2-126-evidence.md" \
  "ROWS=none" "SOURCES=DEC-1032, DEC-1031, DEC-1015, DEC-374" IMPL=DEC-1032 "EST=150 lines"
python3 .gov-runtime/scratch/orchestrator/tools/placeholder_scan.py "$B/W2-126-A5-run1.md" | tail -1
