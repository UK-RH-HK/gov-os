#!/bin/bash
# Run 3, merged head: gates, then the serial-only phase of the full verification in the close's form.
bash /home/usain/gov-os-worktrees/W2-03/.gov-runtime/scratch/lead/gates.sh > /home/usain/gov-os-worktrees/W2-03/.gov-runtime/scratch/lead/log/r3b-gates-serial.txt 2>&1
date > /home/usain/gov-os-worktrees/W2-03/.gov-runtime/scratch/lead/log/r3b-serial.start
python3 /home/usain/gov-os-worktrees/W2-03/.gov-runtime/scratch/lead/verify.py serial r3b
date >> /home/usain/gov-os-worktrees/W2-03/.gov-runtime/scratch/lead/log/r3b-serial.start
