#!/bin/bash
# The lead's re-run of A9 on the redis copy (S25's verify line), with the ticket branch's code at 4d49108fb or later.
R=/home/usain/gov-os-runs/W2-88/redis
O=/home/usain/gov-os-runs/W2-88/redis-out/a9
L=/home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/lead/log/redis-a9
mkdir -p "$O"
git -C /home/usain/gov-os-worktrees/W2-88 rev-parse HEAD > "$L.head"
git -C "$R" rev-parse HEAD > "$L.before"
env PYTHONPATH=/home/usain/gov-os-worktrees/W2-88/src /usr/bin/time -v -o "$L.time" \
  python3 -m gov.cli.main adopt --lite --stage A9 --out "$O" --root "$R" --session lead-W2-88-run7 > "$L.out" 2> "$L.err"
echo $? > "$L.exit"
git -C "$R" rev-parse HEAD > "$L.after"
git -C "$R" status --short > "$L.status"
