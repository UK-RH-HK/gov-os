#!/usr/bin/env bash
# Which cases of the scoped set the -k/-m filter deselects (collect only).
TREE=/home/usain/gov-os-worktrees/W2-42a
L=$TREE/.gov-runtime/scratch/lead/log
cd "$TREE"
export TMPDIR=/tmp/w2-42a-lead/tmp PYTHONUSERBASE=/home/usain/.local HOME=$TREE/.gov-runtime/scratch/empty-home PYTHONPATH=$TREE/src
S="tests/unit/guard tests/acceptance/W2-42a tests/unit/hooks tests/unit/pause tests/unit/containment/test_w1_50_freeze_flag.py tests/acceptance/W1-50 tests/acceptance/W1-28 tests/acceptance/W2-16"
python3 -m pytest $S -q --collect-only -p no:cacheprovider > $L/collect-all.txt 2>&1
python3 -m pytest $S -q --collect-only -p no:cacheprovider -m "not local_only" -k "not real and not green_here and not time_limit" > $L/collect-sel.txt 2>&1
grep '::' $L/collect-all.txt | sort > $L/c-all.ids
grep '::' $L/collect-sel.txt | sort > $L/c-sel.ids
comm -23 $L/c-all.ids $L/c-sel.ids > $L/c-desel.ids
wc -l $L/c-all.ids $L/c-sel.ids $L/c-desel.ids
sed -E 's/::.*//' $L/c-desel.ids | sort | uniq -c | sort -rn | head -30
