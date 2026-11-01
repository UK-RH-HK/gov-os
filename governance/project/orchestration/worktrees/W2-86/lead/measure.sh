#!/bin/bash
# W2-86's re-measure, visible half only (W2-61 §8 step 3), on one clone once its pinned rebuild has ended.
# usage: measure.sh base|head    (head is compared with base's record)
L=/home/usain/gov-os-worktrees/W2-86/.gov-runtime/scratch/lead/log
case "$1" in
  base) CLONE=/home/usain/gov-os-runs/W2-86/base ;;
  head) CLONE=/home/usain/gov-os-runs/W2-86/head ;;
  *) exit 7 ;;
esac
until [ -s "$L/rebuild-$1.exit" ]; do sleep 30; done
[ "$(cat "$L/rebuild-$1.exit")" = "0" ] || { echo 6 > "$L/measure-$1.exit"; exit 6; }
mkdir -p /home/usain/gov-os-runs/W2-86/records
COMPARE=()
if [ "$1" = head ]; then
  until [ -s "$L/measure-base.exit" ]; do sleep 30; done
  [ "$(cat "$L/measure-base.exit")" = "0" ] || { echo 5 > "$L/measure-$1.exit"; exit 5; }
  COMPARE=(--compare "$(cat "$L/measure-base.record")")
fi
python3 -c "import time; print('start', time.strftime('%H:%M:%S', time.gmtime()))" > "$L/measure-$1.times"
env -u GOV_TICKET PYTHONPATH=/home/usain/gov-os-runs/W2-86/measure/src python3 -m gov.retrieval.measure memory-retrieval --root "$CLONE" --sets-root /home/usain/gov-os-runs/W2-86/measure --part visible --gov /home/usain/.local/bin/gov --out /home/usain/gov-os-runs/W2-86/records --json "${COMPARE[@]}" > "$L/measure-$1.json" 2> "$L/measure-$1.err"
RC=$?
python3 -c "import time; print('end', time.strftime('%H:%M:%S', time.gmtime()))" >> "$L/measure-$1.times"
ls -t /home/usain/gov-os-runs/W2-86/records/*.json | head -1 > "$L/measure-$1.record"
echo $RC > "$L/measure-$1.exit"
