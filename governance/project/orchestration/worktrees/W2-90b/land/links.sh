#!/usr/bin/env bash
T=/home/usain/gov-os-worktrees/W2-90b
cd $T
env PYTHONPATH=$T/src python3 -m gov.cli.main links --since 73c18fea1e1f > $T/.gov-runtime/scratch/land/links.txt 2>&1
echo "exit $?"
head -1 $T/.gov-runtime/scratch/land/links.txt
echo "-- lines naming this ticket or its commits:"
grep -E "nqa2|b3ed3f88d1f2|cb0e69ba57f2|73c18fea1e1f|d2408361d185" $T/.gov-runtime/scratch/land/links.txt
