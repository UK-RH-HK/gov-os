#!/bin/bash
cd /home/usain/gov-os-worktrees/W2-185
env TMPDIR=/home/usain/gov-os-worktrees/W2-185/.gov-runtime/scratch/tmp PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-185/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-185/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest --optin lifted,breadth \
 tests/unit/gitenv/test_hooks_lifted.py tests/acceptance/W2-59/test_w2_59_hook_lines.py tests/acceptance/W2-59/test_w2_59_hook_lines_worker_env.py tests/acceptance/W1-38/test_w1_38_hooks_any_folder.py tests/acceptance/W1-38/test_w1_38_hooks_source.py tests/unit/hooks/test_w2_106_template_hook_lines.py tests/acceptance/W2-05/test_w2_05_hooks_source.py \
 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" -rf
