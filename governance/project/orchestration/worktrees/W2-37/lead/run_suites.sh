#!/bin/bash
# Runs each named acceptance suite in its own pytest process, to its end.
# Usage: run_suites.sh <tag> <suite>...   Writes log/<tag>-<suite>.txt and .rc, then log/<tag>.done
W=/home/usain/gov-os-worktrees/W2-37
L=$W/.gov-runtime/scratch/lead/log
tag=$1; shift
cd $W || exit 2
for s in "$@"; do
  PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src \
    python3 -m pytest tests/acceptance/$s -q -p no:cacheprovider -rs > $L/$tag-$s.txt 2>&1
  echo $? > $L/$tag-$s.rc
done
echo done > $L/$tag.done
