#!/bin/bash
# W2-50 lead verification: every acceptance suite, then the builder tests, each to its end.
# Usage: verify.sh <tag>   — results under .gov-runtime/scratch/lead/log/<tag>/; a suite with an .exit file is skipped (resume).
# W1-46 and W1-50 run with -m "not local_only": their live cases launch real sessions with the real HOME,
# which would create the real ~/gov-os-runs (nobody creates it in this run).
W=/home/usain/gov-os-worktrees/W2-50
OUT=$W/.gov-runtime/scratch/lead/log/$1
mkdir -p $OUT
cd $W || exit 9
export PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH
for d in tests/acceptance/W*/; do
  s=$(basename $d)
  [ -e $OUT/$s.exit ] && continue
  extra=()
  case $s in W1-46|W1-50) extra=(-m "not local_only");; esac
  PYTHONPATH=$W/src timeout 5400 python3 -m pytest tests/acceptance/$s -q -p no:cacheprovider -rs "${extra[@]}" > $OUT/$s.txt 2>&1
  echo $? > $OUT/$s.exit
  if [ -e /home/usain/gov-os-runs ]; then echo "REAL ROOT PRESENT after $s" > $OUT/STOP; exit 3; fi
done
if [ ! -e $OUT/unit.exit ]; then
  PYTHONPATH=$W/src python3 -m pytest tests/unit -q -p no:cacheprovider > $OUT/unit.txt 2>&1
  echo $? > $OUT/unit.exit
fi
[ -e /home/usain/gov-os-runs ] && echo "REAL ROOT PRESENT after unit" > $OUT/STOP
echo done > $OUT/ALL.done
