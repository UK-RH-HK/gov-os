#!/usr/bin/env bash
# Like inbox_wait.sh, but a repeated "server-hung" item does not wake the CTO more than once an hour (DEC-1012: 14 wakes
# for one known, already-escalated condition on 2026-11-02). Every other item wakes at once. A quieted item is filed to
# inbox/read/ and logged in log/inbox-quieted.log, so nothing is lost; the dispatcher still holds starts on each flag.
# Read-only apart from filing quieted server-hung items. Env overrides for tests: INBOX, STATE, QLOG, EVERY, QUIET_S.
set -u
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
INBOX=${INBOX:-$ORCH/dispatch/inbox}
STATE=${STATE:-$ORCH/log/inbox-quiet-last-hung}
QLOG=${QLOG:-$ORCH/log/inbox-quieted.log}
EVERY=${EVERY:-30}
QUIET_S=${QUIET_S:-3600}
mkdir -p "$INBOX/read"
while :; do
  mapfile -t items < <(cd "$INBOX" && ls -1 *.txt 2>/dev/null | sort)
  if [ "${#items[@]}" -gt 0 ]; then
    other=()
    for f in "${items[@]}"; do [[ "$f" == *-server-hung.txt ]] || other+=("$f"); done
    now=$(date +%s); last=$(cat "$STATE" 2>/dev/null || echo 0)
    if [ "${#other[@]}" -eq 0 ] && [ $((now - last)) -lt "$QUIET_S" ]; then
      for f in "${items[@]}"; do
        mv "$INBOX/$f" "$INBOX/read/$f" && echo "$(date '+%F %T') quieted $f" >> "$QLOG"
      done
    else
      [ "${#other[@]}" -eq 0 ] && echo "$now" > "$STATE"
      echo "$(date '+%F %T') inbox:"; printf '  %s\n' "${items[@]}"
      exit 0
    fi
  fi
  sleep "$EVERY"
done
