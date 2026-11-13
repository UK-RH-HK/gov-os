#!/usr/bin/env bash
# Lead: the adapter reds at w2/integrate's head (the main tree, read only: no cache, temp outside the repository).
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 2
git rev-parse --short=12 HEAD
env TMPDIR=/tmp/gov-os-lead-W2-45 PYTHONUSERBASE=/home/usain/.local \
  HOME=/home/usain/gov-os-worktrees/W2-45/.gov-runtime/scratch/empty-home \
  PYTHONPATH=/home/usain/Dynamic-Agentic-Engineering-OS/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed --tb=line \
  "tests/unit/adapters/test_w2_153_compose.py::test_the_twelve_sources_are_the_composition" \
  "tests/unit/adapters/test_w2_153_portability.py::test_this_repositorys_sources_are_the_composition" \
  "tests/unit/ci/test_ci_command.py::test_the_job_gate_names_a_check_whose_tool_is_absent_as_unmeasured_and_refuses"
