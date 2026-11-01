#!/bin/bash
# W2-61's §8 as W2-86 ran it, for one clone (base or head): the clone's stores by the pinned gov, with embeddings, in a
# heavy-job slot with the clone's own lock (DEC-1001 (d)); then the visible half only, never the hidden half.
# Arguments: <base|head> [<the control's record, for --compare>]
WHICH=$1
CMP=${2:-}
export TMPDIR=/tmp/gov-os-lead-W2-91
cd /home/usain/gov-os-runs/W2-91/$WHICH || exit 90
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh > /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/$WHICH-gate.txt 2>&1 || { echo 91 > /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/$WHICH-measure.exit; exit 91; }
date -u +%FT%TZ > /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/$WHICH-rebuild.start
env -u PYTHONPATH -u GOV_TICKET GOV_REBUILD_PYTHON=/home/usain/.local/share/gov-os/pin-5c401220/bin/python bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/rebuild_slot.sh /home/usain/gov-os-runs/W2-91/$WHICH > /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/$WHICH-rebuild.json 2> /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/$WHICH-rebuild.err
RC=$?
echo $RC > /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/$WHICH-rebuild.exit
date -u +%FT%TZ > /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/$WHICH-rebuild.end
[ "$RC" = 0 ] || { echo 92 > /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/$WHICH-measure.exit; exit 92; }
sha256sum .gov-runtime/store.db .gov-runtime/codeintel/home/code.db .gov-runtime/codeintel/home/_config.db > /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/$WHICH-sha.txt 2>&1
if [ "$CMP" = auto ]; then
  # Wait for the control's measure (up to 100 minutes) and take its record from its JSON output.
  for i in $(seq 1 300); do [ -s /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/base-measure.exit ] && break; sleep 20; done
  CMP=$(python3 /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/record_of.py /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/base-measure.json)
  echo "$CMP" > /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/$WHICH-compare.txt
  [ -n "$CMP" ] || { echo 93 > /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/$WHICH-measure.exit; exit 93; }
fi
date -u +%FT%TZ > /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/$WHICH-measure.start
if [ -n "$CMP" ]; then
  env -u GOV_TICKET PYTHONPATH=/home/usain/gov-os-runs/W2-91/base/src python3 -m gov.retrieval.measure memory-retrieval --root /home/usain/gov-os-runs/W2-91/$WHICH --sets-root /home/usain/gov-os-runs/W2-91/base --part visible --gov /home/usain/.local/bin/gov --out /home/usain/gov-os-runs/W2-91/records --json --compare "$CMP" > /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/$WHICH-measure.json 2> /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/$WHICH-measure.err
else
  env -u GOV_TICKET PYTHONPATH=/home/usain/gov-os-runs/W2-91/base/src python3 -m gov.retrieval.measure memory-retrieval --root /home/usain/gov-os-runs/W2-91/$WHICH --sets-root /home/usain/gov-os-runs/W2-91/base --part visible --gov /home/usain/.local/bin/gov --out /home/usain/gov-os-runs/W2-91/records --json > /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/$WHICH-measure.json 2> /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/$WHICH-measure.err
fi
echo $? > /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/$WHICH-measure.exit
date -u +%FT%TZ > /home/usain/gov-os-worktrees/W2-91/.gov-runtime/scratch/lead/log/$WHICH-measure.end
