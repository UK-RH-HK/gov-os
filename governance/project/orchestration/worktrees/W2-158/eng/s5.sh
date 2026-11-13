#!/bin/bash
T=/home/usain/gov-os-worktrees/W2-158
cd "$T"
a=$(date +%s.%N)
PYTHONPATH=$T/src python3 -m gov.cli.main check --structural HEAD~1 --root $T > .gov-runtime/scratch/eng/s5.out 2> .gov-runtime/scratch/eng/s5.err
rc=$?
b=$(date +%s.%N)
echo "exit=$rc wall=$(echo "$b - $a" | bc) s" > .gov-runtime/scratch/eng/s5.time
