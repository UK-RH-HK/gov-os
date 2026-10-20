#!/bin/bash
# W2-50 lead verification, run 8, one chain: verify3.sh <tag> <suite>...   (a suite is a folder name under tests/acceptance, or "unit")
# Results under .gov-runtime/scratch/lead/log/<tag>/; a suite with an .exit file is skipped (resume).
# W1-46 and W1-50 run with -m "not local_only" (as in run 7): their live cases launch real claude sessions.
# The real ~/gov-os-runs exists since run 8's first gov launch (the launcher under test made ~/gov-os-runs/W2-50);
# any change to what it holds during a suite is noted in <tag>/RUNS-CHANGED (not a stop).
W=/home/usain/gov-os-worktrees/W2-50
OUT=$W/.gov-runtime/scratch/lead/log/$1
TAG=$1
shift
mkdir -p $OUT
cd $W || exit 9
export PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH
for s in "$@"; do
  [ -e $OUT/$s.exit ] && continue
  before=$(find /home/usain/gov-os-runs 2>/dev/null | sort | md5sum)
  if [ "$s" = unit ]; then
    PYTHONPATH=$W/src python3 -m pytest tests/unit -q -p no:cacheprovider > $OUT/unit.txt 2>&1
  else
    extra=()
    case $s in W1-46|W1-50) extra=(-m "not local_only");; esac
    PYTHONPATH=$W/src python3 -m pytest tests/acceptance/$s -q -p no:cacheprovider -rs "${extra[@]}" > $OUT/$s.txt 2>&1
  fi
  echo $? > $OUT/$s.exit
  after=$(find /home/usain/gov-os-runs 2>/dev/null | sort | md5sum)
  [ "$before" = "$after" ] || echo "$s" >> $OUT/RUNS-CHANGED
done
echo done > $OUT/$(echo "$TAG" | tr '/' '_').chain-done-$(echo "$1" | tr '/' '_')
