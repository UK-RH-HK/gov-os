#!/bin/bash
# gov accept for the two acceptance folders the revision touched (W2-96, W2-56), each through the heavy slot
cd /home/usain/gov-os-worktrees/W2-177 || exit 2
O=/home/usain/gov-os-worktrees/W2-177/.gov-runtime/scratch/lead/accept
mkdir -p $O
for w in W2-96 W2-56; do
  export TMPDIR=$(mktemp -d /tmp/w2-177-accept.XXXXXX) || exit 3
  env PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-177/src \
    bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
    gov accept $w --root /home/usain/gov-os-worktrees/W2-177 > $O/$w.json 2> $O/$w.err
  echo "$w rc=$?" >> $O/rc.txt
  rm -rf -- "$TMPDIR"
done
echo 0 > $O/accept.exit
