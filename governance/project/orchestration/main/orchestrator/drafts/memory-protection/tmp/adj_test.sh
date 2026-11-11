#!/usr/bin/env bash
# Rehearsal 1 (harmless): can an unprivileged process raise, but not lower, its own oom_score_adj; do children inherit it?
T=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/memory-protection/tmp
sleep 30 &
P=$!
echo "start adj: $(cat /proc/$P/oom_score_adj)"
echo 500 > /proc/$P/oom_score_adj && echo "raise to 500: ok, now $(cat /proc/$P/oom_score_adj)"
echo 100 > /proc/$P/oom_score_adj 2>/dev/null && echo "lower to 100: ALLOWED" || echo "lower to 100: refused (as expected)"
echo 0 > /proc/$P/oom_score_adj 2>/dev/null && echo "lower to 0: ALLOWED" || echo "lower to 0: refused (as expected)"
echo -500 > /proc/self/oom_score_adj 2>/dev/null && echo "lower self to -500: ALLOWED" || echo "lower self to -500: refused (as expected)"
# inheritance: a child of a process at 300 starts at 300
( echo 300 > /proc/self/oom_score_adj; sleep 20 & C=$!; echo "child of a 300 process starts at: $(cat /proc/$C/oom_score_adj)"; kill $C )
kill $P
