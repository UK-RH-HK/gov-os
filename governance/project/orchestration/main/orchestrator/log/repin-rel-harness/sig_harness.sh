#!/usr/bin/env bash
# Harness for the template's on_signal (review r2 F1, F5): the handler's own lines, a fake refresh in its own session.
#     bash sig_harness.sh <case: dies|ignores|early>   (dies: the refresh exits on TERM; ignores: it ignores TERM;
#     early: the signal comes between the fork and rp=$!)
set -Eeuo pipefail
CASE=$1
echo "before any background job: \${!:-} = [${!:-}]"
rp=""; RP_STARTING=""; PHASE=before
stop() { echo "STOP: $1"; exit 1; }
grp_alive() { ps -o stat= -g "$1" 2> /dev/null | awk '$1 !~ /^Z/ {n++} END {exit n ? 0 : 1}'; }  # a live member left
on_signal() {  # $1 the signal
  trap - ERR; trap '' INT TERM HUP PIPE; set +e
  if [ -z "$rp" ] && [ -n "$RP_STARTING" ]; then rp=${!:-}; fi
  if [ -n "$rp" ]; then
    kill -TERM -- "-$rp" 2> /dev/null
    local n=0  # TERM again at each poll: a signal right after the fork can come before the child's setsid made the group
    while grp_alive "$rp" && [ $n -lt 120 ]; do sleep 0.5; n=$((n + 1)); kill -TERM -- "-$rp" 2> /dev/null; done
    if grp_alive "$rp"; then kill -KILL -- "-$rp" 2> /dev/null; sleep 0.5; fi
    wait "$rp" 2> /dev/null
    echo "the store refresh (pid $rp, its process group) was stopped, $((n / 2)) s after the signal$(grp_alive "$rp" && echo ', BUT A PROCESS OF IT IS STILL LIVE')"
  fi
  stop "interrupted ($1) before the switch"
}
trap 'on_signal INT' INT
trap 'on_signal TERM' TERM
trap 'on_signal HUP' HUP
RP_STARTING=1
if [ "$CASE" = ignores ]; then
  setsid bash -c 'trap "" TERM; sleep 300 & wait' > /dev/null 2>&1 < /dev/null &
else
  setsid bash -c 'sleep 300 & wait' > /dev/null 2>&1 < /dev/null &
fi
[ "$CASE" = early ] && kill -TERM $$   # the signal before rp=$! (the trap runs before the next command)
rp=$!
echo "the fake refresh: pid $rp"
sleep 1
kill -TERM $$
sleep 5
echo "NOT REACHED"
