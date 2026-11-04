#!/usr/bin/env bash
# The owner's GPU backstop for the research agent's experiment (2026-11-04 00:20; an exception over the 13.9 GB
# budget for this experiment only). Every 5 s: if GPU memory crosses 15.5 GiB (15,872 MiB), or memory sits at the
# card's total (the sign of a spill into shared GPU memory: WSL cannot read Windows' shared-usage counter), or an
# embedder's loaded size is not all on the GPU (/api/ps size_vram < size), or an embedder log shows a partial offload,
# the experiment's processes (args naming the research worktree) are paused with SIGSTOP at once, an inbox item wakes
# the CTO (who pings the owner), and the watcher exits. Read-only otherwise. Stop it with kill when the experiment ends.
set -u
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
INBOX=${INBOX:-$ORCH/dispatch/inbox}
LOG=${LOG:-$ORCH/log/gpu-backstop.log}
LIMIT=${LIMIT:-15872}
MARK=${MARK:-research-retrieval}
mkdir -p "$ORCH/log"
start_lines() { for f in /home/usain/.ollama/serve-11434.log /home/usain/.ollama/serve-11435.log; do wc -l < "$f" 2>/dev/null || echo 0; done; }
read -r L1 L2 < <(start_lines | tr '\n' ' ')
echo "$(date '+%F %T') start: limit $LIMIT MiB; logs at lines $L1 $L2" >> "$LOG"
trip() {
  local why=$1 pids
  pids=$(ps -eo pid,args | grep -F "$MARK" | grep -vE "claude|grep|gpu_backstop" | awk '{print $1}')
  [ -n "$pids" ] && kill -STOP $pids 2>/dev/null
  echo "$(date '+%F %T') TRIP: $why; paused: ${pids:-none}" >> "$LOG"
  printf 'log: gpu-backstop.log\nGPU: backstop tripped\nstatus: %s; experiment processes paused (SIGSTOP): %s; resume with kill -CONT on the owner'"'"'s word\n' \
    "$why" "$(echo $pids | tr '\n' ' ')" > "$INBOX/$(date +%Y%m%d-%H%M%S)-gpu-stop.txt"
  exit 0
}
n=0
while :; do
  read -r used total < <(nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits | tr -d ',')
  [ "${used:-0}" -gt "$LIMIT" ] && trip "GPU memory $used MiB > $LIMIT MiB"
  [ "${used:-0}" -ge $(( ${total:-99999} - 64 )) ] && trip "GPU memory $used of $total MiB: at the card's total (a spill into shared memory)"
  for port in 11434 11435; do
    bad=$(curl -s --max-time 3 "http://127.0.0.1:$port/api/ps" | python3 -c "
import json,sys
try: ms=json.load(sys.stdin)['models']
except Exception: ms=[]
print(' '.join(f\"{m['name']} {m['size_vram']}/{m['size']}\" for m in ms if m['size_vram']<m['size']))" 2>/dev/null)
    [ -n "$bad" ] && trip "embedder on :$port not all on the GPU: $bad"
  done
  i=0
  for f in /home/usain/.ollama/serve-11434.log /home/usain/.ollama/serve-11435.log; do
    i=$((i+1)); from=$([ $i = 1 ] && echo $L1 || echo $L2)
    hit=$(tail -n +$((from+1)) "$f" 2>/dev/null | grep -oE "offloaded [0-9]+/[0-9]+ layers to GPU" | awk -F'[ /]' '$2<$3' | head -1)
    [ -n "$hit" ] && trip "embedder log $(basename $f): $hit"
  done
  n=$((n+1)); [ $((n % 60)) = 0 ] && echo "$(date '+%F %T') ok: $used MiB" >> "$LOG"
  sleep 5
done
