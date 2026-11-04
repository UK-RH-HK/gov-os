#!/usr/bin/env bash
# Tonight's handshake with the research agent (DEC-1067's GPU safety; 2026-11-04 04:20). The shared reranker keeps its
# PyTorch peak memory between requests, so GPU memory only climbs. When the agent must wait (memory at or above
# 15,000 MiB) it writes FLAG and sends no reranker request until FLAG is gone. This watcher, on FLAG, checks the GPU is
# idle (no request in flight), restarts the shared reranker with class 3's commands, checks READY on cuda:0, logs, and
# removes FLAG. It restarts nothing without FLAG. Stop it with kill when the experiment ends.
set -u
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
FLAG=${FLAG:-/tmp/gov-os-research-wait.flag}
LOG=$ORCH/log/rerank-reset.log
T=$ORCH/tools/tree_busy.sh
echo "$(date '+%F %T') start: flag $FLAG" >> "$LOG"
while :; do
  if [ -e "$FLAG" ]; then
    idle=0
    for i in 1 2 3 4 5 6; do
      u=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits)
      [ "$u" -lt 5 ] && idle=$((idle+1))
      sleep 2
    done
    m=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits)
    if [ "$idle" -ge 6 ]; then
      for P in $(bash $T --cmd rerank_service.py 2>/dev/null | awk '/^BUSY/{print $2}'); do kill -TERM $P; done
      for i in $(seq 1 15); do bash $T --cmd rerank_service.py 2>/dev/null | grep -q '^BUSY' || break; sleep 2; done
      if bash $T --cmd rerank_service.py 2>/dev/null | grep -q '^BUSY'; then
        echo "$(date '+%F %T') the reranker did not stop on SIGTERM: left as it is, FLAG kept, CTO to act" >> "$LOG"
        printf 'log: rerank-reset.log\nGPU: reranker reset failed\nstatus: the reranker did not stop on SIGTERM\n' \
          > "$ORCH/dispatch/inbox/$(date +%Y%m%d-%H%M%S)-rerank-reset.txt"
        sleep 60; continue
      fi
      (cd /home/usain/gov-os-worktrees/W2-00-store && GOV_RERANK_IDLE_S=43200 ~/.local/bin/gov retrieve "what decides a close" --json > /dev/null 2>&1)
      r=$(tail -1 ~/.cache/gov-os/rerank.log)
      after=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits)
      echo "$(date '+%F %T') reset: $m -> $after MiB; $r" >> "$LOG"
      case "$r" in *READY*cuda*) rm -f "$FLAG";; *) printf 'log: rerank-reset.log\nGPU: reranker not READY after reset\nstatus: %s\n' "$r" > "$ORCH/dispatch/inbox/$(date +%Y%m%d-%H%M%S)-rerank-reset.txt";; esac
    else
      echo "$(date '+%F %T') FLAG seen but the GPU is busy (a request in flight): wait" >> "$LOG"
    fi
  fi
  sleep 5
done
