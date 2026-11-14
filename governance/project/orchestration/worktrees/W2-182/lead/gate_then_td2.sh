#!/usr/bin/env bash
# Waits (bounded, 9 min) for the resource gate to open, then relaunches td-2 (DEC-1146: a gate refusal is a wait).
T=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools
for i in $(seq 1 54); do
  if python3 "$T/gate_check.py" >/dev/null 2>&1; then
    cd /home/usain/gov-os-worktrees/W2-182-tests || exit 2
    bash "$T/launch_worker.sh" --model claude-sonnet-5-5 --class C1 independent-test-designer high \
      /home/usain/gov-os-worktrees/W2-182/.gov-runtime/scratch/lead/briefs/td-2.md 2>&1 | tail -3
    exit 0
  fi
  sleep 10
done
python3 "$T/gate_check.py"; echo "gate still shut after 9 min"; exit 1
