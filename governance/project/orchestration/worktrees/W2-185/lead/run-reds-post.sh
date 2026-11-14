#!/bin/bash
cd /home/usain/gov-os-worktrees/W2-185
F="tests/unit/gitenv/test_hooks_lifted.py tests/acceptance/W2-59/test_w2_59_hook_lines.py tests/acceptance/W2-59/test_w2_59_hook_lines_worker_env.py tests/acceptance/W1-38/test_w1_38_hooks_any_folder.py tests/acceptance/W1-38/test_w1_38_hooks_source.py tests/unit/hooks/test_w2_106_template_hook_lines.py tests/acceptance/W2-05/test_w2_05_hooks_source.py"
E="env TMPDIR=/home/usain/gov-os-worktrees/W2-185/.gov-runtime/scratch/tmp PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-185/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-185/src"
SLOT=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh
echo "== the eight files, opt-in lifted,breadth"
$E bash $SLOT python3 -m pytest --optin lifted,breadth $F tests/acceptance/W2-185 tests/unit/adapters/test_w2_185_hooks_exemption.py tests/unit/gitenv/test_program_env.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" -rf
echo "== the time_limit cases of the eight files"
$E bash $SLOT python3 -m pytest --optin lifted,breadth $F -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "time_limit" -rf
echo "== W2-23 S6 and W1-38 rulesync"
$E bash $SLOT python3 -m pytest tests/acceptance/W2-23/test_w2_23_space.py tests/acceptance/W1-38/test_w1_38_rulesync.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" -rf
