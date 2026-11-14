#!/usr/bin/env bash
# Launch a worker once the resource gate is open (gate_check.py each minute; DEC-1146: a gate refusal is a wait).
# Usage: launch_when_open.sh <tag> <tree> <model> <role> <effort> <brief>
TAG=$1; TREE=$2; MODEL=$3; ROLE=$4; EFFORT=$5; BRIEF=$6
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
L=/home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/lead/log
echo $$ > $L/gatewait-$TAG.pid
until line=$(python3 "$ORCH/tools/gate_check.py"); do
  echo "$(date '+%F %T') $line" >> $L/gatewait-$TAG.log
  sleep 60
done
echo "$(date '+%F %T') gate open: $line" >> $L/gatewait-$TAG.log
cd "$TREE" || exit 2
LAUNCH_TREE="$TREE" LAUNCH_TICKET=DAEO-03ub bash "$ORCH/tools/launch_worker.sh" --model "$MODEL" --class C3 \
  "$ROLE" "$EFFORT" "$BRIEF" >> $L/gatewait-$TAG.log 2>&1
echo $? > $L/gatewait-$TAG.exit
