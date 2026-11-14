#!/usr/bin/env bash
# Waits for the resource gate (gate_check.py, each minute, up to 90 min), then relaunches the test designer and the
# marks auditor (the first launches were refused by the load gate: a wait, DEC-1146).
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
L=/home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/lead
for i in $(seq 1 90); do
  if line=$(python3 "$ORCH/tools/gate_check.py"); then break; fi
  echo "$(date '+%F %T') shut: $line"
  sleep 60
done
python3 "$ORCH/tools/gate_check.py" || { echo "gate still shut after 90 min"; exit 3; }
echo "$(date '+%F %T') gate open: launching"
cd /home/usain/gov-os-worktrees/W2-130-tests && env LAUNCH_TREE=/home/usain/gov-os-worktrees/W2-130-tests LAUNCH_TICKET=DAEO-q8cl \
  bash "$ORCH/tools/launch_worker.sh" --class C2 --model claude-opus-5-5 independent-test-designer high "$L/briefs/td-1.md"
sleep 90
cd /home/usain/gov-os-worktrees/W2-130 && env LAUNCH_TREE=/home/usain/gov-os-worktrees/W2-130 LAUNCH_TICKET=DAEO-q8cl \
  bash "$ORCH/tools/launch_worker.sh" --class C2 --model claude-opus-5-5 independent-auditor high "$L/briefs/aud-marks-1.md"
echo done
