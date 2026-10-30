#!/bin/bash
# Run 3, merged head: gates, then the parallel phase of the full verification in the close's form.
bash /home/usain/gov-os-worktrees/W2-03/.gov-runtime/scratch/lead/gates.sh > /home/usain/gov-os-worktrees/W2-03/.gov-runtime/scratch/lead/log/r3b-gates-parallel.txt 2>&1
date > /home/usain/gov-os-worktrees/W2-03/.gov-runtime/scratch/lead/log/r3b-parallel.start
python3 /home/usain/gov-os-worktrees/W2-03/.gov-runtime/scratch/lead/verify.py parallel r3b
date >> /home/usain/gov-os-worktrees/W2-03/.gov-runtime/scratch/lead/log/r3b-parallel.start
