#!/usr/bin/env bash
# r4: named cases alone, once, through heavy_slot.sh, with the session's own HOME (as lead_verify runs them; gov accept's
# child drops PYTHONUSERBASE, so an empty HOME hides pytest from it); usage: run_nodes_home.sh <name> <node id>...
set -u
T=/home/usain/gov-os-worktrees/W2-105
L=$T/.gov-runtime/scratch/lead/log
name=$1; shift
mkdir -p "$L" /tmp/gov-os-lead-W2-105
echo $$ > "$L/$name.pid"
rm -f "$L/$name.exit"
cd "$T" || exit 2
grep SigIgn /proc/self/status > "$L/$name.sigign"
env TMPDIR=/tmp/gov-os-lead-W2-105 PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=$T/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest "$@" -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs \
  --junitxml="$L/$name.xml" > "$L/$name.log" 2>&1
echo $? > "$L/$name.exit"
