#!/usr/bin/env bash
# Like inbox_wait.sh, but a repeated "server-hung" item does not wake the CTO more than once an hour (DEC-1012: 14 wakes
# for one known, already-escalated condition on 2026-11-02). Every other item wakes at once. A quieted item is filed to
# inbox/read/ and logged in log/inbox-quieted.log, so nothing is lost; the dispatcher still holds starts on each flag.
# DEC-1140 (1)(a) (2026-11-12): an idle-headroom item whose status line equals the last idle item that woke the CTO is quieted
# the same way (filed, logged), with a wake again after IDLE_REMIND_S (6 h); a new cause wakes at once.
# Read-only apart from filing quieted items. Env overrides for tests: INBOX, STATE, ISTATE, QLOG, EVERY, QUIET_S, IDLE_REMIND_S.
set -u
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
INBOX=${INBOX:-$ORCH/dispatch/inbox}
STATE=${STATE:-$ORCH/log/inbox-quiet-last-hung}
QLOG=${QLOG:-$ORCH/log/inbox-quieted.log}
EVERY=${EVERY:-30}
QUIET_S=${QUIET_S:-3600}
ISTATE=${ISTATE:-$ORCH/log/inbox-quiet-last-idle}
IDLE_REMIND_S=${IDLE_REMIND_S:-21600}
idle_status() { sed -n 's/^status: //p' "$1" | head -n 1; }
mkdir -p "$INBOX/read"
while :; do
  mapfile -t items < <(cd "$INBOX" && ls -1 *.txt 2>/dev/null | sort)
  if [ "${#items[@]}" -gt 0 ]; then
    other=()
    now=$(date +%s); last=$(cat "$STATE" 2>/dev/null || echo 0)
    ilast_s=$(sed -n 2p "$ISTATE" 2>/dev/null); ilast_t=$(sed -n 1p "$ISTATE" 2>/dev/null); ilast_t=${ilast_t:-0}
    for f in "${items[@]}"; do
      [[ "$f" == *-server-hung.txt ]] && continue
      if [[ "$f" == *-idle-headroom.txt ]]; then
        s=$(idle_status "$INBOX/$f")
        if [ -n "$s" ] && [ "$s" = "$ilast_s" ] && [ $((now - ilast_t)) -lt "$IDLE_REMIND_S" ]; then
          mv "$INBOX/$f" "$INBOX/read/$f" && echo "$(date '+%F %T') quieted (same idle cause) $f" >> "$QLOG"; continue
        fi
        printf '%s\n%s\n' "$now" "$s" > "$ISTATE"; ilast_s=$s; ilast_t=$now
      fi
      other+=("$f")
    done
    mapfile -t items < <(cd "$INBOX" && ls -1 *.txt 2>/dev/null | sort)
    [ "${#items[@]}" -eq 0 ] && { sleep "$EVERY"; continue; }
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
