#!/bin/bash
# W2-86 supplementary pair: the measure, visible half only, retrieving with the tree's own code.
# usage: tree_measure.sh base|head   (head compared with base's tree record)
L=/home/usain/gov-os-runs/W2-86/logs
case "$1" in
  base) CLONE=/home/usain/gov-os-runs/W2-86/base ;;
  head) CLONE=/home/usain/gov-os-runs/W2-86/head ;;
  *) exit 7 ;;
esac
until [ -s "$L/tree-rebuild-$1.exit" ]; do sleep 30; done
[ "$(cat "$L/tree-rebuild-$1.exit")" = "0" ] || { echo 6 > "$L/tree-measure-$1.exit"; exit 6; }
mkdir -p /home/usain/gov-os-runs/W2-86/records-tree
COMPARE=()
if [ "$1" = head ]; then
  until [ -s "$L/tree-measure-base.exit" ]; do sleep 30; done
  [ "$(cat "$L/tree-measure-base.exit")" = "0" ] || { echo 5 > "$L/tree-measure-$1.exit"; exit 5; }
  COMPARE=(--compare "$(cat "$L/tree-measure-base.record")")
fi
python3 -c "import time; print('start', time.strftime('%H:%M:%S', time.gmtime()))" > "$L/tree-measure-$1.times"
env -u GOV_TICKET PYTHONPATH=/home/usain/gov-os-runs/W2-86/measure/src python3 -m gov.retrieval.measure memory-retrieval --root "$CLONE" --sets-root /home/usain/gov-os-runs/W2-86/measure --part visible --gov /tmp/claude-1000/-home-usain-gov-os-worktrees-W2-86/8032324e-fe9a-455f-b1f8-0ddb0d1ba6d3/scratchpad/bin/gov-"$1" --out /home/usain/gov-os-runs/W2-86/records-tree --json "${COMPARE[@]}" > "$L/tree-measure-$1.json" 2> "$L/tree-measure-$1.err"
RC=$?
python3 -c "import time; print('end', time.strftime('%H:%M:%S', time.gmtime()))" >> "$L/tree-measure-$1.times"
ls -t /home/usain/gov-os-runs/W2-86/records-tree/*.json | head -1 > "$L/tree-measure-$1.record"
echo $RC > "$L/tree-measure-$1.exit"
