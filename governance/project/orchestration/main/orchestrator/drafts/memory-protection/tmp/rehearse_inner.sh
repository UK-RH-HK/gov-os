#!/usr/bin/env bash
# Live rehearsal of mem_guard.py INSIDE a throwaway user scope (TasksMax=300, MemoryHigh=600M, no MemoryMax: no kernel kill).
# Decoys are copies of /bin/sleep named rg (the "storm"), claude and ollama (must never be touched); a python hog stands in
# for a big legitimate process. Thresholds are scaled down (watch 20, mark 40, stop 60). Outputs go to tmp/ only.
M=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/memory-protection
T=$M/tmp/rehearse
rm -rf "$T"; mkdir -p "$T/decoy" "$T/inbox"
exec 2>> "$T/stderr.txt"   # the shell's "Killed" job notices go here, not to the report
for n in rg claude ollama; do cp /bin/sleep "$T/decoy/$n"; done
CG=/sys/fs/cgroup$(cut -d: -f3 /proc/self/cgroup)
echo "scope: ${CG#/sys/fs/cgroup}  pids.max=$(cat $CG/pids.max)"
export MG_CGROUP=$CG MG_LIMIT_MB=1000 MG_PERIOD=0.2 MG_WATCH_RG=20 MG_MARK_RG=40 MG_STOP_RG=60 MG_MARK_MIN_RG=10 MG_STOP_MIN_RG=30 \
  MG_INBOX=$T/inbox MG_LOG=$T/guard.log MG_ALIVE=$T/alive MG_ALERT_EVERY_S=1
"$T/decoy/claude" 120 & CLAUDE=$!
"$T/decoy/ollama" 120 & OLLAMA=$!
python3 -I -c 'import time; b=bytearray(150*1024*1024)
for i in range(0,len(b),4096): b[i]=1
time.sleep(120)' & HOG=$!
sleep 1
echo "--- phase 1: stop OFF (the default). 70 rg appear, 10 per 0.2 s."
MG_STOP=0 python3 -I $M/mem_guard.py & G=$!
sleep 0.5
for i in 1 2 3 4 5 6 7; do for j in 1 2 3 4 5 6 7 8 9 10; do "$T/decoy/rg" 100 & done; sleep 0.2; done
sleep 1.5
RGS=$(ps -eo pid=,comm= | awk '$2=="rg"{print $1}' | while read -r p; do [ "$(tr -d '\0' < /proc/$p/cgroup 2>/dev/null | grep -c "${CG#/sys/fs/cgroup}")" -gt 0 ] && echo $p; done)
set -- $RGS
echo "rg alive: $#  adj of the first rg: $(cat /proc/$1/oom_score_adj)  adj of claude decoy: $(cat /proc/$CLAUDE/oom_score_adj)  ollama decoy: $(cat /proc/$OLLAMA/oom_score_adj)  hog: $(cat /proc/$HOG/oom_score_adj)"
kill $G; wait $G 2>/dev/null
for p in $RGS; do kill $p 2>/dev/null; done
sleep 0.5
echo "--- phase 2: stop ON. 200 rg appear in about 1 s (a storm, 10 per 0.05 s)."
MG_STOP=1 python3 -I $M/mem_guard.py & G=$!
sleep 0.5
START=$(date +%s.%N)
for i in $(seq 1 20); do for j in 1 2 3 4 5 6 7 8 9 10; do "$T/decoy/rg" 100 & done; sleep 0.05; done
sleep 1.5
NRG=$(for p in $(ps -eo pid=,comm= | awk '$2=="rg"{print $1}'); do grep -q "${CG#/sys/fs/cgroup}" /proc/$p/cgroup 2>/dev/null && echo $p; done | wc -l)
echo "rg alive after the storm: $NRG; claude decoy alive: $(kill -0 $CLAUDE 2>/dev/null && echo yes || echo NO); ollama decoy alive: $(kill -0 $OLLAMA 2>/dev/null && echo yes || echo NO); hog alive: $(kill -0 $HOG 2>/dev/null && echo yes || echo NO)"
kill $G; wait $G 2>/dev/null
kill $CLAUDE $OLLAMA $HOG 2>/dev/null
for p in $(ps -eo pid=,comm= | awk '$2=="rg"{print $1}'); do grep -q "${CG#/sys/fs/cgroup}" /proc/$p/cgroup 2>/dev/null && kill $p; done
echo "--- guard log:"; cat "$T/guard.log"
echo "--- inbox items:"; ls "$T/inbox"; for f in "$T"/inbox/*; do echo "== $(basename $f)"; head -12 "$f" | cut -c1-200; done
echo "--- alive file: $(cat $T/alive 2>/dev/null)"
wait 2>/dev/null
