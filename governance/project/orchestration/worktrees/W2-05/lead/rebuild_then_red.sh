#!/bin/bash
# The rebuild after the test designer's commit, then the lead's red check of W2-05 alone (both gated).
bash /home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead/rebuild.sh rebuild6
bash /home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead/run_w205.sh red5-W2-05
