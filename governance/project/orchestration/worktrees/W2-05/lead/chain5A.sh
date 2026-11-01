#!/bin/bash
# Run 5, part A: the rebuild, then the parallel and serial phases of the selection less W1-02 and W2-05.
S=/home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead
LOG=$S/log/v5
bash $S/rebuild5r.sh
[ "$(cat $LOG/rebuild.exit)" = 0 ] || { echo rebuild-failed > $LOG/chainA.done; exit 1; }
bash $S/verify5.sh parallel A
bash $S/verify5.sh serial A
echo done > $LOG/chainA.done
