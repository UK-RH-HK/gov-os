#!/bin/bash
B=/home/usain/gov-os-worktrees/W2-185/.gov-runtime/scratch/tmp/base-e2a0d6191
rm -rf "$B"; mkdir -p "$B"
git -C /home/usain/gov-os-worktrees/W2-185 archive e2a0d6191 | tar -x -C "$B"
cd "$B"
env TMPDIR=/home/usain/gov-os-worktrees/W2-185/.gov-runtime/scratch/tmp PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-185/.gov-runtime/scratch/empty-home PYTHONPATH=$B/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest "tests/acceptance/W1-38/test_w1_38_rulesync.py::TestKernelAgainstAdapterSource" -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rf
