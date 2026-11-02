#!/usr/bin/env bash
# Builds W2-112's lead brief (DEC-1032, the infrastructure sprint, step 1).
set -eu
B=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs
cd /home/usain/Dynamic-Agentic-Engineering-OS
python3 .gov-runtime/scratch/orchestrator/tools/build_lead_brief.py "$B/W2-112-part-run1.md" "$B/W2-112-A5-run1.md" \
  ID=DAEO-clon W2=W2-112 PROFILE=FULL \
  "PATHS=src/gov/retrieval/rerank.py, src/gov/retrieval/rerank_worker.py, src/gov/retrieval/rerank_service.py, tests/unit/retrieval/test_w2_112*, docs/research/W2-112-shared-reranker.md" \
  "ROWS=none" "SOURCES=DEC-979, DEC-374, DEC-397, ADR-0002, DEC-1031, DEC-1032" IMPL=DEC-1032,DEC-979 "EST=200 lines"
python3 .gov-runtime/scratch/orchestrator/tools/placeholder_scan.py "$B/W2-112-A5-run1.md" | tail -1
