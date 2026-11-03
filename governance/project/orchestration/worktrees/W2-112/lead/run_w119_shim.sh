#!/bin/bash
# Diagnostic re-run of the three W1-19 files whose cases went red with "no gitleaks": the same code, with a folder
# holding only a gitleaks link first on PATH (the test helper drops every PATH folder that holds an ollama, and the
# 18:13 ~/.local/bin/ollama wrapper sits beside ~/.local/bin/gitleaks). Through the gate (DEC-1038 (4)).
cd /home/usain/gov-os-worktrees/W2-112 || exit 99
export PATH=/tmp/gov-os-lead-W2-112/gl:$PATH
export TMPDIR=/tmp/gov-os-lead-W2-112
export PYTHONPATH=/home/usain/gov-os-worktrees/W2-112/src
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W1-19/test_w1_19_embedding_policy.py tests/acceptance/W1-19/test_w1_19_semantic_index.py tests/acceptance/W1-19/test_w1_19_unavailable.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs --junitxml=/home/usain/gov-os-worktrees/W2-112/.gov-runtime/scratch/lead/log/w119-shim.xml
