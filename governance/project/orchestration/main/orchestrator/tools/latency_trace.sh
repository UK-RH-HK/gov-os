#!/usr/bin/env bash
# DEC-968 item 3: are the batch's 11 latency reds caused by W2-106's merge, or by load? The 11 cases, alternately on
# the close's head (with) and on a copy with only W2-106's merge reverted (without), 3 rounds, with the load each time.
C=/home/usain/gov-os-runs/W2-00/close/W2-106+W2-84+W2-76+W2-49-20261031-115212
W=/home/usain/gov-os-runs/W2-00/close/latency-without-W2-106
O=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/capacity/latency-trace.txt
export TMPDIR=/tmp/gov-os-latency; mkdir -p "$TMPDIR"
rm -rf "$W"; git clone -q --no-hardlinks "$C" "$W" && git -C "$W" checkout -q --detach "$(git -C "$C" rev-parse HEAD)" \
  && git -C "$W" -c user.name=o -c user.email=o@l revert -m 1 --no-edit 0d53c56a1bfcecb3abb6c8bf99d1505c2eb2c58e >/dev/null || { echo "revert failed" > "$O"; exit 2; }
L=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/close-build
D=$(ls -td "$L"/W2-106+W2-84+W2-76+W2-49-* | head -1)
grep -h "caused by the change: " "$D/close.txt" | sed 's/.*caused by the change: //' > "$TMPDIR/cases.txt"
: > "$O"
for round in 1 2 3; do
  for side in with without; do
    tree=$C; [ $side = without ] && tree=$W
    l=$(cut -d' ' -f1 /proc/loadavg)
    res=$(cd "$tree" && PYTHONPATH="$tree/src" python3 -m pytest -q -p no:cacheprovider --no-header $(cat "$TMPDIR/cases.txt") 2>&1 | tail -1)
    echo "round $round $side load $l: $res" | tee -a "$O"
  done
done
