#!/usr/bin/env bash
# W2-88b: after the redis run (pid $1), the workspace full run (code graph on), then grafana's full run with the code
# graph off (its estimate: 1,351,658 nodes, 4,722,026 edges, 38.4 GB peak, over DEC-078's envelope and the machine's
# free memory: recorded, and a proposal for the owner), then the F2 after-snapshot of ~/workspace. Detached (setsid).
set -u
L=/home/usain/gov-os-worktrees/W2-88b/.gov-runtime/scratch/lead
G=/home/usain/gov-os-runs/W2-88b/logs
while kill -0 "$1" 2> /dev/null; do sleep 20; done
bash "$L/run_full.sh" workspace /home/usain/gov-os-runs/W2-88b/workspace --origin "a local clone of ~/workspace (--no-hardlinks)" > "$G/full-workspace.log" 2>&1
PROOF_CODE_GRAPH=0 bash "$L/run_full.sh" grafana /home/usain/gov-os-runs/W2-88b/github/grafana --origin https://github.com/grafana/grafana --licence AGPL-3.0-only > "$G/full-grafana.log" 2>&1
python3 -I "$L/snapshot.py" /home/usain/workspace "$L/f2-workspace-after-runs.json" > /dev/null
echo "chain end $(date -Is)" > "$G/chain.done"
