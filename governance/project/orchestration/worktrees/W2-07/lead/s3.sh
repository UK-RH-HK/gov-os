#!/usr/bin/env bash
# The serial-only run under the machine-wide lock (DEC-904), after parallel3.sh. Exit code in log/s3-serial.exit.
L=/home/usain/gov-os-worktrees/W2-07/.gov-runtime/scratch/lead/log
TMP=/tmp/gov-os-lead-W2-07
{ date -Is; cat /proc/loadavg; bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh; du -s --inodes "$TMP"; du -sh "$TMP"; } > "$L/s3-serial.gate" 2>&1 \
  || { echo 91 > "$L/s3-serial.exit"; exit 91; }
flock /tmp/gov-os-verify.lock bash -c "date -Is > $L/s3-serial.start; exec bash /home/usain/gov-os-worktrees/W2-07/.gov-runtime/scratch/lead/serial3.sh $L/serial3.xml" \
  > "$L/s3-serial.txt" 2>&1; echo $? > "$L/s3-serial.exit"
{ date -Is; du -s --inodes "$TMP"; du -sh "$TMP"; } >> "$L/s3-serial.gate" 2>&1
