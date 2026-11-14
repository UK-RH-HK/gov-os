#!/usr/bin/env bash
# run 7 (pin run 3): the two changed files, then gov accept W2-130 and W2-175, then the scoped run (DEC-968) of both folders.
set -u
T=/home/usain/gov-os-worktrees/W2-130
L=$T/.gov-runtime/scratch/lead/run7
HS=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh
mkdir -p "$T/.gov-runtime/scratch/empty-home" "$T/.gov-runtime/scratch/tmp/run7"
export TMPDIR=/home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/tmp/run7
export PYTHONUSERBASE=/home/usain/.local
cd "$T" || exit 2
echo "== head $(git rev-parse HEAD)"
echo "== files $(date -Is)"
env HOME=$T/.gov-runtime/scratch/empty-home PYTHONPATH=$T/src bash "$HS" python3 -m pytest \
  tests/acceptance/W2-130/test_w2_130_sources.py tests/acceptance/W2-130/test_w2_130_audit.py \
  -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" \
  --junitxml=$L/junit-files.xml > $L/pytest-files.out 2>&1
echo "files rc=$?"; tail -3 $L/pytest-files.out
echo "== accept W2-130 $(date -Is)"
PYTHONPATH=$T/src gov accept W2-130 --root /home/usain/gov-os-worktrees/W2-130 > $L/accept.out 2>&1
echo "accept rc=$?"; grep -A4 '"totals"' $L/accept.out
echo "== accept W2-175 $(date -Is)"
PYTHONPATH=$T/src gov accept W2-175 --root /home/usain/gov-os-worktrees/W2-130 > $L/accept-w2-175.out 2>&1
echo "accept W2-175 rc=$?"; grep -A4 '"totals"' $L/accept-w2-175.out
echo "== scoped $(date -Is)"
env HOME=$T/.gov-runtime/scratch/empty-home PYTHONPATH=$T/src bash "$HS" python3 -m pytest \
  tests/acceptance/W2-130 tests/acceptance/W2-175 \
  -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" \
  --junitxml=$L/junit-scoped.xml > $L/pytest-scoped.out 2>&1
echo "scoped rc=$?"; tail -5 $L/pytest-scoped.out
echo "== end $(date -Is)"
