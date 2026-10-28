#!/usr/bin/env bash
# The morning check (owner, DEC-934 item 2): did last night's nightly run? The owner's crontab runs it at 05:30 and
# five minutes after WSL starts (@reboot), so a night is checked even when WSL was down at 05:30:
#   30 5 * * * bash /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/nightly/nightly_check.sh
#   @reboot sleep 300 && bash /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/nightly/nightly_check.sh
# It writes one line per night to log/nightly/status.txt, which the morning digest reads:
#   <date> ran | <verdict> head <head> duration ...      the night ran to a verdict;
#   <date> FAILED | <its last line>                         a night run started but ended without a verdict;
#   <date> MISSED | no night run started 01:55-05:00        nothing started (cron down, WSL down, the PC asleep).
# FAILED and MISSED ping P1 at once (a miss is never silent). Before 05:00 it does nothing (the window is open);
# a night already in status.txt is not checked again. The orchestrator's digest also reads status.txt and treats a
# night with no line as MISSED, the backstop when neither cron line could run.
ORCH=${NIGHTLY_ORCH:-/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator}
PING=${NIGHTLY_PING:-/home/usain/.local/bin/owner-ping}
NOW_HM=${NIGHTLY_NOW_HM:-$(date +%H%M)}
DAY=${NIGHTLY_DAY:-$(date +%Y%m%d)}
STATUS=$ORCH/log/nightly/status.txt
mkdir -p "$ORCH/log/nightly"
[ "$((10#$NOW_HM))" -ge 500 ] || exit 0
label=$(date -d "$DAY" +%F)
grep -q "^$label " "$STATUS" 2>/dev/null && exit 0
run=""
for dir in "$ORCH/log/nightly/$DAY"-0[1-4][0-9][0-9]; do
  [ -f "$dir/run.txt" ] || continue
  hm=${dir##*-}
  [ "$((10#$hm))" -ge 155 ] && [ "$((10#$hm))" -lt 500 ] || continue
  head -1 "$dir/run.txt" | grep -q "nightly night:" || continue
  run=$dir
done
if [ -z "$run" ]; then
  line="$label MISSED | no night run started 01:55-05:00 (cron, WSL or the PC was not up)"
  "$PING" "P1 NIGHTLY-MISSED $label | no night run started | the orchestrator's package follows"
elif ! grep -q "^verdict:" "$run/run.txt"; then
  line="$label FAILED | $(tail -1 "$run/run.txt" | cut -c1-160)"
  "$PING" "P1 NIGHTLY-FAILED $label | the run ended without a verdict | the orchestrator's package follows"
else
  line="$label ran | $(grep -E '^(verdict|duration)' "$run/run.txt" | tr '\n' ' ')head $(grep -m1 '^head ' "$run/run.txt" | cut -d' ' -f2)"
fi
echo "$line" >> "$STATUS"
echo "$line"
