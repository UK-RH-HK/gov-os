#!/bin/bash
# Run 7: re-run alone the node ids listed in a file (one a line), through rerun7.sh.  Usage: rerun7_file.sh <tag> <file>
mapfile -t IDS < "$2"
exec bash /home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead/rerun7.sh "$1" "${IDS[@]}"
