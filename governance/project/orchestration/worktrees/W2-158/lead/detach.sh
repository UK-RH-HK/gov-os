#!/usr/bin/env bash
# detach.sh <name> <script>: runs <script> in its own session; log/<name>.out, <name>.pid, <name>.exit (written last).
out=/home/usain/gov-os-worktrees/W2-158/.gov-runtime/scratch/lead/log
name=$1 script=$2
rm -f "$out/$name.exit"
setsid bash -c 'bash "$1" > "$2/$3.out" 2>&1; echo $? > "$2/$3.exit.tmp" && mv "$2/$3.exit.tmp" "$2/$3.exit"' _ "$script" "$out" "$name" < /dev/null > /dev/null 2>&1 &
echo $! > "$out/$name.pid"
echo "$name started pid $(cat "$out/$name.pid"); wait on $out/$name.exit"
