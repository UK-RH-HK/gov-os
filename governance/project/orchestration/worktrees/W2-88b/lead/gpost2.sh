#!/usr/bin/env bash
# run 4: grafana from A6, detached from the harness; writes its own pid and exit files (waits by pid only)
L=/home/usain/gov-os-runs/W2-88b/grafana-logs
echo $$ > $L/post2.pid
bash /home/usain/gov-os-worktrees/W2-88b/.gov-runtime/scratch/lead/stages.sh grafana a6-on > $L/post2-driver.log 2>&1
echo $? > $L/post2.exit
