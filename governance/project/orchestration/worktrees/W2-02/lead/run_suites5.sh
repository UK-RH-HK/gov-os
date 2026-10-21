#!/bin/bash
# Lead's run-5 verification runner: each named suite to its end in its own pytest process, one output and one
# exit file per suite (DEC-732: this worktree's src/). Usage: run_suites5.sh <tag> <suite> [<suite> ...]
# (suite = a folder name under tests/acceptance, or "unit")
cd /home/usain/gov-os-worktrees/W2-02 || exit 2
OUT=/home/usain/gov-os-worktrees/W2-02/.gov-runtime/scratch/lead/log/suites5
mkdir -p "$OUT"
tag="$1"; shift
uptime > "$OUT/chunk-$tag.start"
for s in "$@"; do
  if [ "$s" = "unit" ]; then
    PYTHONPATH=/home/usain/gov-os-worktrees/W2-02/src timeout 6000 python3 -m pytest tests/unit -q -p no:cacheprovider > "$OUT/$s.txt" 2>&1
  else
    PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-02/src timeout 6000 python3 -m pytest "tests/acceptance/$s" -q -p no:cacheprovider -rs > "$OUT/$s.txt" 2>&1
  fi
  echo $? > "$OUT/$s.exit"
done
uptime > "$OUT/chunk-$tag.done"
