#!/usr/bin/env bash
# Round 2's auditor, once the resource gate is open (gate_check.py each minute, as launch_when_gate_opens.sh; DEC-1146).
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
L=/home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/lead/log
echo $$ > $L/gatewait.pid
until line=$(python3 "$ORCH/tools/gate_check.py"); do
  echo "$(date '+%F %T') $line" >> $L/gatewait.log
  sleep 60
done
echo "$(date '+%F %T') gate open: $line" >> $L/gatewait.log
cd /home/usain/gov-os-worktrees/W2-42a || exit 2
LAUNCH_TREE=/home/usain/gov-os-worktrees/W2-42a LAUNCH_TICKET=DAEO-03ub bash "$ORCH/tools/launch_worker.sh" --model opus --class C3 \
  independent-auditor high /home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/lead/briefs/a3-2.md >> $L/gatewait.log 2>&1
echo $? > $L/gatewait.exit
