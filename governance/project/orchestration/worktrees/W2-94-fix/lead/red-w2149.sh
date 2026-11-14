#!/usr/bin/env bash
cd /home/usain/gov-os-worktrees/W2-94-fix || exit 2
OUT=/home/usain/gov-os-worktrees/W2-94-fix/.gov-runtime/scratch/lead/red-w2149.txt
env HOME=/home/usain/gov-os-worktrees/W2-94-fix/.gov-runtime/scratch/empty-home TMPDIR=/home/usain/gov-os-worktrees/W2-94-fix/.gov-runtime/scratch/tmp \
  PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-94-fix/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest tests/acceptance/W2-149/test_w2_149_seed_content.py::test_s5_the_argument_parser_offers_no_path_or_path_list_option \
  tests/unit/orchestration/test_w2_149_indep_launch.py -q -p no:cacheprovider \
  -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" --tb=short -rf \
  > "$OUT" 2>&1
echo "rc=$?" >> "$OUT"
