#!/usr/bin/env bash
# Watches the owner's plan usage (owner, DEC-942 item 6: ping before the limits are close). Every 30 minutes reads
# `claude -p "/usage"`, logs the two figures to log/usage.txt, and pings once per window through the nightly's ping
# gate (held overnight until 07:30 unless the owner is active) when the session window reaches 80 % or the week 70 %
# (and again at 85 %). Runs until stopped.
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
GATE=/home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/nightly/ping_gate.sh
STATE=$ORCH/log/usage-pinged.txt
touch "$STATE"
while true; do
  out=$(/home/usain/.local/bin/claude -p "/usage" 2>&1)
  s=$(echo "$out" | sed -n 's/^Current session: \([0-9]*\)% used · resets \(.*\)$/\1|\2/p' | head -1)
  w=$(echo "$out" | sed -n 's/^Current week (all models): \([0-9]*\)% used · resets \(.*\)$/\1|\2/p' | head -1)
  echo "$(date '+%F %T') session ${s:-unread} week ${w:-unread}" >> "$ORCH/log/usage.txt"
  sp=${s%%|*}; sr=${s#*|}; wp=${w%%|*}; wr=${w#*|}
  if [ -n "$sp" ] && [ "$sp" -ge 80 ] && ! grep -qxF "session 80 $sr" "$STATE"; then
    echo "session 80 $sr" >> "$STATE"
    bash "$GATE" "P1 USAGE | session window at ${sp}% (resets $sr) | I slow new lead starts; say if you want them stopped"
  fi
  for level in 70 85; do
    if [ -n "$wp" ] && [ "$wp" -ge "$level" ] && ! grep -qxF "week $level $wr" "$STATE"; then
      echo "week $level $wr" >> "$STATE"
      bash "$GATE" "P1 USAGE | week at ${wp}% (resets $wr) | lead starts continue unless you say otherwise"
    fi
  done
  sleep 1800
done
