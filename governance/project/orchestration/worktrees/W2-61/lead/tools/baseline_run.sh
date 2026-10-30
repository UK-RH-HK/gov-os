#!/bin/bash
# One baseline run of this worktree's measure, visible half only, against the clone (DEC-941, KPI line 7).
# The measure runs this worktree's src (DEC-732); it strips PYTHONPATH and GOV_TICKET from the retrieving process,
# which is the pinned gov (/home/usain/.local/bin/gov, DEC-877). Argument: the run label (run-1, run-2, run-3);
# further arguments are passed to the measure (e.g. --compare <record>).
# Outputs: <label>.json (the JSON document), <label>.err, <label>.exit, <label>.time, and the record in runs/records/.
set -u
label="$1"; shift
out=/home/usain/gov-os-worktrees/W2-61/.gov-runtime/scratch/lead/runs
mkdir -p /home/usain/gov-os-worktrees/W2-61/.gov-runtime/scratch/lead/runs/records
cd /home/usain/gov-os-runs/W2-61/repo || exit 90
date -u +%FT%TZ > "$out/$label.time"
env -u GOV_TICKET PYTHONPATH=/home/usain/gov-os-worktrees/W2-61/src python3 -m gov.retrieval.measure memory-retrieval \
  --root /home/usain/gov-os-runs/W2-61/repo --sets-root /home/usain/gov-os-worktrees/W2-61 --part visible \
  --gov /home/usain/.local/bin/gov --out "$out/records" --json "$@" > "$out/$label.json" 2> "$out/$label.err"
echo $? > "$out/$label.exit"
date -u +%FT%TZ >> "$out/$label.time"
