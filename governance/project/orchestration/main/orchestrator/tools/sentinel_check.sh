#!/usr/bin/env bash
# The owner's order (2026-11-04 ~15:20): tell the owner when the sentinel's login or Remote Control is down. On
# 2026-11-04 the sentinel's login expired silently at 11:43, so its dead-man alert never reached the owner.
# Every 2 minutes, while dispatch/sentinel-expected exists, the sentinel is judged DOWN if any of:
#   - its watch log (log/deadman.log) has written no line for more than STALE_S seconds (it writes about every 2 min);
#   - its tmux pane shows a login, authentication or Remote Control failure;
#   - its tmux session is gone.
# On a change to DOWN it drops an inbox item (the CTO's inbox waiter wakes the CTO, who pings the owner by push); on
# a change back to UP, one more item. Read-only otherwise. Env overrides for a rehearsal: ORCH, SESSION, STALE_S, EVERY.
set -u
ORCH=${ORCH:-/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator}
SESSION=${SESSION:-cto-sentinel}
STALE_S=${STALE_S:-600}
EVERY=${EVERY:-120}
LOG=$ORCH/log/sentinel-check.log
STATE=$ORCH/log/sentinel-check.state
PATTERN='(please (log|sign) ?in|login (has )?expired|not logged in|authentication (failed|error|required)|unauthori[sz]ed|invalid api key|oauth token (has )?expired|remote control (is )?(off|disconnected|unavailable|failed|ended))'
echo "$(date '+%F %T') start: session $SESSION, stale after $STALE_S s" >> "$LOG"
while :; do
  if [ -e "$ORCH/dispatch/sentinel-expected" ]; then
    why=""
    if ! tmux has-session -t "$SESSION" 2>/dev/null; then why="its tmux session $SESSION is gone"
    else
      pane=$(tmux capture-pane -pt "$SESSION" -S -60 2>/dev/null | tr 'A-Z' 'a-z')
      hit=$(printf '%s' "$pane" | grep -oE "$PATTERN" | head -1)
      [ -n "$hit" ] && why="its pane shows: $hit"
    fi
    if [ -z "$why" ]; then
      last=$(stat -c %Y "$ORCH/log/deadman.log" 2>/dev/null || echo 0); age=$(( $(date +%s) - last ))
      [ "$age" -gt "$STALE_S" ] && why="its watch log has written nothing for $(( age / 60 )) min"
    fi
    now=$([ -n "$why" ] && echo DOWN || echo UP); was=$(cat "$STATE" 2>/dev/null || echo UP)
    if [ "$now" != "$was" ]; then
      echo "$now" > "$STATE"
      echo "$(date '+%F %T') $now${why:+: $why}" >> "$LOG"
      printf 'log: sentinel-check.log\nSentinel: %s\nstatus: %s\n' "$now" \
        "${why:-the sentinel is back: its watch log writes and its pane shows no login or Remote Control failure}" \
        > "$ORCH/dispatch/inbox/$(date +%Y%m%d-%H%M%S)-sentinel-$(echo $now | tr A-Z a-z).txt"
    fi
  fi
  sleep "$EVERY"
done
