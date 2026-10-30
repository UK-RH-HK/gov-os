#!/bin/bash
# Run 3 (restarted lead): gates, then the full rebuild under the machine's rebuild lock.
bash /home/usain/gov-os-worktrees/W2-03/.gov-runtime/scratch/lead/gates.sh > /home/usain/gov-os-worktrees/W2-03/.gov-runtime/scratch/lead/log/r3-gates-rebuild.txt 2>&1
bash /home/usain/gov-os-worktrees/W2-03/.gov-runtime/scratch/lead/rebuild.sh
date >> /home/usain/gov-os-worktrees/W2-03/.gov-runtime/scratch/lead/log/r3-gates-rebuild.txt
