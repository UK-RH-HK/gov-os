#!/usr/bin/env bash
# The scoped run once (DEC-968) after P-7 (a): W1-07, W1-32 and W1-26's recorded-command files (with the breadth
# opt-in, else their cases are deselected), then W2-37's folder with its local_only code-graph cases included.
set -u
cd /home/usain/gov-os-worktrees/W2-37
T=/home/usain/gov-os-tmp/w237-scoped-6
mkdir -p "$T" /home/usain/gov-os-worktrees/W2-37/.gov-runtime/scratch/empty-home
L=/home/usain/gov-os-worktrees/W2-37/.gov-runtime/scratch/lead/log/p7
HS=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh
env TMPDIR="$T" HOME=/home/usain/gov-os-worktrees/W2-37/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local \
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src bash "$HS" python3 -m pytest \
  tests/acceptance/W1-07/test_w1_07_recorded_commands.py tests/acceptance/W1-32 \
  tests/acceptance/W1-26/test_w1_26_recorded_commands.py \
  -q -p no:cacheprovider -o tmp_path_retention_policy=failed --optin=breadth -rfEs \
  -m "not local_only" -k "not real and not green_here and not time_limit" \
  --junitxml="$L/scoped-w1.xml" > "$L/scoped-w1.txt" 2>&1
echo "w1 exit=$?"
env TMPDIR="$T" HOME=/home/usain/gov-os-worktrees/W2-37/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local \
  PATH="/home/usain/.local/bin:$PATH" \
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src bash "$HS" python3 -m pytest tests/acceptance/W2-37 \
  -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfEs \
  -k "not real and not green_here and not time_limit" \
  --junitxml="$L/scoped-w237.xml" > "$L/scoped-w237.txt" 2>&1
echo "w237 exit=$?"
tail -3 "$L/scoped-w1.txt"; tail -12 "$L/scoped-w237.txt"
