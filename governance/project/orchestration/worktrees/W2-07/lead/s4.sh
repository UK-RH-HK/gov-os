#!/usr/bin/env bash
# Lead verification, run 4, part C: the serial-only cases under the machine-wide lock (DEC-904), after p4.sh, with the
# retention option (DEC-905). Exit code in log/s4-serial.exit; log/s4.done at the end.
L=/home/usain/gov-os-worktrees/W2-07/.gov-runtime/scratch/lead/log
TMP=/tmp/gov-os-lead-W2-07
CLOSE=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING
rm -f "$L/s4.done"
trap 'echo done > "$L/s4.done"' EXIT
until [ ! -e "$CLOSE" ]; do sleep 60; done
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
{ date -Is; cat /proc/loadavg; bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh; du -s --inodes "$TMP"; du -sh "$TMP"; } > "$L/s4-serial.gate" 2>&1 \
  || { echo 91 > "$L/s4-serial.exit"; exit 91; }
flock /tmp/gov-os-verify.lock bash -c "date -Is > $L/s4-serial.start; exec bash /home/usain/gov-os-worktrees/W2-07/.gov-runtime/scratch/lead/serial3.sh $L/serial4.xml" \
  > "$L/s4-serial.txt" 2>&1; echo $? > "$L/s4-serial.exit"
{ date -Is; du -s --inodes "$TMP"; du -sh "$TMP"; } >> "$L/s4-serial.gate" 2>&1
