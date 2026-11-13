#!/usr/bin/env bash
# usage: win.sh <tag> <N> <SECONDS> <target load>   -- one load window: the real shards, then the planted shards, in this one call
TAG=$1
N=$2
S=$3
TARGET=$4
TD=/home/usain/gov-os-worktrees/W2-111-tests/.gov-runtime/scratch/td
KA="guard_hook"
KB="live_hooks and (Glob or Grep or Edit-engineer) and not Notebook"
KC="designer_read or (live_hooks and (NotebookEdit or Read or Write))"
bash $TD/load_window.sh $N $S
SECONDS=0
until awk -v t=$TARGET 'BEGIN{getline l < "/proc/loadavg"; split(l, a, " "); exit !(a[1] >= t)}'; do
  [ $SECONDS -gt 220 ] && break
  sleep 3
done
echo "target reached at +$SECONDS s, load: $(cat /proc/loadavg)"
bash $TD/run_real2.sh $TAG-a "$KA" &
bash $TD/run_real2.sh $TAG-b "$KB" &
bash $TD/run_real2.sh $TAG-c "$KC" &
wait
echo "real shards done at +$SECONDS s of $S, load: $(cat /proc/loadavg)"
bash $TD/run_real2.sh $TAG-pl-a "$KA" TD_PLANT_S=0.15 TD_ROUNDS=1 TD_SAMPLES=${PS:-8} &
bash $TD/run_real2.sh $TAG-pl-b "$KB" TD_PLANT_S=0.15 TD_ROUNDS=1 TD_SAMPLES=${PS:-8} &
bash $TD/run_real2.sh $TAG-pl-c "$KC" TD_PLANT_S=0.15 TD_ROUNDS=1 TD_SAMPLES=${PS:-8} &
wait
echo "planted shards done at +$SECONDS s of $S, load: $(cat /proc/loadavg)"
