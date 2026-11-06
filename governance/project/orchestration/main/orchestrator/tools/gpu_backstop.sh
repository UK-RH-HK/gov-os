#!/usr/bin/env bash
# The owner's GPU backstop for a GPU job (2026-11-04 00:20; DEC-1067, DEC-1068 (4)).
#   gpu_backstop.sh <pgid> [<pgid> ...]      the process groups of the job to pause on a trip
# Every 5 s: if GPU memory crosses 15.5 GiB (15,872 MiB), or memory sits at the card's total (the sign of a spill into
# shared GPU memory: WSL cannot read Windows' shared-usage counter), or an embedder's loaded size is not all on the GPU
# (/api/ps size_vram < size), or an embedder log shows a partial offload, the named process groups are paused with
# SIGSTOP at once, an inbox item wakes the CTO (who pings the owner), and the watcher exits.
# Only the process groups given are touched: no pattern, no ps | grep, so nothing outside the job can be paused
# (L-0075, DEC-1073 (4); the owner, 2026-11-05). Start the job in its own group (setsid), then arm this with its
# group (`proc.sh pgid <pid>`). When every named group has ended, the watcher logs it and exits by itself.
# Read-only otherwise. Env overrides for tests: INBOX, LOG, LIMIT, EVERY, NVSMI.
set -u
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
INBOX=${INBOX:-$ORCH/dispatch/inbox}
LOG=${LOG:-$ORCH/log/gpu-backstop.log}
LIMIT=${LIMIT:-15872}
EVERY=${EVERY:-5}
NVSMI=${NVSMI:-nvidia-smi}
[ $# -gt 0 ] || { echo "gpu_backstop.sh: name the job's process groups (pgid ...); nothing is matched by name" >&2; exit 2; }
for g in "$@"; do [[ "$g" =~ ^[0-9]+$ ]] && [ "$g" -gt 1 ] || { echo "gpu_backstop.sh: not a process group id: $g" >&2; exit 2; }; done
GROUPS_=("$@")
mkdir -p "$(dirname "$LOG")"
start_lines() { for f in /home/usain/.ollama/serve-11434.log /home/usain/.ollama/serve-11435.log; do wc -l < "$f" 2>/dev/null || echo 0; done; }
read -r L1 L2 < <(start_lines | tr '\n' ' ')
echo "$(date '+%F %T') start: limit $LIMIT MiB; groups ${GROUPS_[*]}; logs at lines $L1 $L2" >> "$LOG"
alive_groups() { local g out=(); for g in "${GROUPS_[@]}"; do kill -0 -- "-$g" 2>/dev/null && out+=("$g"); done; echo "${out[*]:-}"; }
trip() {
  local why=$1 live
  live=$(alive_groups)
  for g in $live; do kill -STOP -- "-$g" 2>/dev/null; done
  echo "$(date '+%F %T') TRIP: $why; paused groups: ${live:-none}" >> "$LOG"
  printf 'log: gpu-backstop.log\nGPU: backstop tripped\nstatus: %s; the job'"'"'s process groups paused (SIGSTOP): %s; resume with kill -CONT -- -<pgid> on the owner'"'"'s word, or stop them with proc.sh stop -<pgid>\n' \
    "$why" "${live:-none}" > "$INBOX/$(date +%Y%m%d-%H%M%S)-gpu-stop.txt"
  exit 0
}
n=0
while :; do
  [ -z "$(alive_groups)" ] && { echo "$(date '+%F %T') end: every watched group has ended (${GROUPS_[*]})" >> "$LOG"; exit 0; }
  read -r used total < <($NVSMI --query-gpu=memory.used,memory.total --format=csv,noheader,nounits | tr -d ',')
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
  sleep "$EVERY"
done
