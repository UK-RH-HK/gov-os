#!/usr/bin/env bash
# The morning check (owner, DEC-934 item 2): did last night's nightly run? The owner's crontab runs it at 08:00 (DEC-973) and
# five minutes after WSL starts (@reboot), so a night is checked even when WSL was down at 08:00:
#   0 8 * * * bash /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/nightly/nightly_check.sh
#   @reboot sleep 300 && bash /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/nightly/nightly_check.sh
# It writes one final line per night to log/nightly/status.txt (a `running` line may come before it; a reader takes
# the night's last line), which the morning digest reads:
#   <date> ran | <verdict> head <head> duration ...      the night ran to a verdict;
#   <date> running | <its last line>                        at 08:00 the run is still going (DEC-971 item 6): the check
#                                                           waits and writes the night's final line by 09:00;
#   <date> FAILED | <its last line>                         a night run started but had no verdict by 09:00;
#   <date> MISSED | no night run started 03:55-08:00        nothing started (cron down, WSL down, the PC asleep).
# FAILED and MISSED ping P1 (a miss is never silent) through the gate (DEC-936): the check runs at 08:00, after the
# quiet hours (02:00 to 07:30, DEC-973), so its pings go at once; the line itself is written at once. Before 08:00 it does nothing (the window is open);
# a night already in status.txt is not checked again. The orchestrator's digest also reads status.txt and treats a
# night with no line as MISSED, the backstop when neither cron line could run.
ORCH=${NIGHTLY_ORCH:-/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator}
# Its pings go through the gate (DEC-936): at 08:00 the quiet hours (02:00 to 07:30, DEC-973) have ended, so a FAILED
# or MISSED night's P1 goes at once. The gate's final ping is owner-ping (NIGHTLY_PING in the tests).
GATE=$(cd "$(dirname "$0")" && pwd)/ping_gate.sh
PING=$GATE
NOW_HM=${NIGHTLY_NOW_HM:-$(date +%H%M)}
DAY=${NIGHTLY_DAY:-$(date +%Y%m%d)}
STATUS=$ORCH/log/nightly/status.txt
mkdir -p "$ORCH/log/nightly"
[ "$((10#$NOW_HM))" -ge 800 ] || exit 0
label=$(date -d "$DAY" +%F)
# One check at a time (DEC-971 item 6's review, F1): the 08:00 job and the @reboot job can overlap during the long
# wait; the second leaves at once, and the first writes the night's one final line and its one ping.
exec 9>"$ORCH/log/nightly/.check.lock"
flock -n 9 || exit 0
# An earlier night left with only a `running` line (its check was killed while it waited, F2) is finished now:
# FAILED with its P1, so no night is ever silent (DEC-934 item 2).
if [ -f "$STATUS" ]; then
  for d in $(awk '$2 == "running" {print $1}' "$STATUS" | sort -u); do
    [ "$d" \< "$label" ] || continue
    grep -qE "^$d (ran|FAILED|MISSED) " "$STATUS" && continue
    # that night's own record decides (review W1): a run that reached its verdict after the check died is `ran`
    r=""  # the same rule as the main check below: a night run started 03:55-07:59 whose first line says so
    for dir2 in "$ORCH/log/nightly/$(echo "$d" | tr -d -)"-0[3-7][0-9][0-9]; do
      [ -f "$dir2/run.txt" ] || continue
      hm2=${dir2##*-}
      [ "$((10#$hm2))" -ge 355 ] && [ "$((10#$hm2))" -lt 800 ] || continue
      head -1 "$dir2/run.txt" | grep -q "nightly night:" || continue
      r=$dir2
    done
    if [ -n "$r" ] && grep -q "^verdict:" "$r/run.txt" 2>/dev/null; then
      echo "$d ran | $(grep -E '^(verdict|duration)' "$r/run.txt" | tr '\n' ' ')head $(grep -m1 '^head ' "$r/run.txt" | cut -d' ' -f2)" >> "$STATUS"
      continue
    fi
    echo "$d FAILED | its check stopped while it waited, no final line written (DEC-971)" >> "$STATUS"
    "$PING" "P1 NIGHTLY-FAILED $d | its check stopped while it waited | the orchestrator's package follows"
  done
fi
# A night already checked is not checked again; its held pings (if any) still go out.
# A `running` line is not a final line: a check that died while it waited (WSL restarted) is done again (DEC-971).
if grep -qE "^$label (ran|FAILED|MISSED) " "$STATUS" 2>/dev/null; then bash "$GATE" --wait-flush 9>&-; exit 0; fi
run=""
for dir in "$ORCH/log/nightly/$DAY"-0[3-7][0-9][0-9]; do
  [ -f "$dir/run.txt" ] || continue
  hm=${dir##*-}
  [ "$((10#$hm))" -ge 355 ] && [ "$((10#$hm))" -lt 800 ] || continue
  head -1 "$dir/run.txt" | grep -q "nightly night:" || continue
  run=$dir
done
if [ -z "$run" ]; then
  line="$label MISSED | no night run started 03:55-08:00 (cron, WSL or the PC was not up)"
  "$PING" "P1 NIGHTLY-MISSED $label | no night run started | the orchestrator's package follows"
elif ! grep -q "^verdict:" "$run/run.txt"; then
  # DEC-971 item 6: a night still running (its marker present, written today, no verdict yet) is not a failure: the
  # check writes `running`, waits in this process and checks again at 08:30 and 09:00, and calls the night FAILED
  # only if no verdict has come by 09:00. The crontab stays as it is. (Tests: NIGHTLY_RECHECK_AT, and with
  # NIGHTLY_NOW_HM set each wait is NIGHTLY_WAIT_STEP seconds instead of the real time.)
  marker=$ORCH/NIGHTLY-RUNNING
  if [ -f "$marker" ] && [ "$(cut -d' ' -f1 "$marker" 2>/dev/null)" = "$label" ]; then
    first="$label running | $(tail -1 "$run/run.txt" | cut -c1-160)"
    echo "$first" >> "$STATUS"
    echo "$first"
    for at in ${NIGHTLY_RECHECK_AT:-0830 0900}; do
      [ "$((10#$at))" -gt "$((10#$NOW_HM))" ] || continue
      [ -f "$marker" ] || break  # the run has ended (its marker gone): judge it now (F3)
      if [ -n "$NIGHTLY_NOW_HM" ]; then
        sleep "${NIGHTLY_WAIT_STEP:-1}" 9>&-
      else
        wait_s=$(( $(date -d "today ${at:0:2}:${at:2:2}" +%s) - $(date +%s) ))
        [ "$wait_s" -gt 0 ] && sleep "$wait_s" 9>&-  # the lock is not held by an orphaned sleep
      fi
      [ -f "$marker" ] || break
      grep -q "^verdict:" "$run/run.txt" && break
    done
  fi
  if grep -q "^verdict:" "$run/run.txt"; then
    line="$label ran | $(grep -E '^(verdict|duration)' "$run/run.txt" | tr '\n' ' ')head $(grep -m1 '^head ' "$run/run.txt" | cut -d' ' -f2)"
  else
    line="$label FAILED | $(tail -1 "$run/run.txt" | cut -c1-160)"
    "$PING" "P1 NIGHTLY-FAILED $label | the run ended without a verdict | the orchestrator's package follows"
  fi
else
  line="$label ran | $(grep -E '^(verdict|duration)' "$run/run.txt" | tr '\n' ' ')head $(grep -m1 '^head ' "$run/run.txt" | cut -d' ' -f2)"
fi
echo "$line" >> "$STATUS"
echo "$line"
# The night's held pings (any nightly.sh held in the quiet hours) go out with this check, at 08:00 or later: no
# process sends them earlier.
bash "$GATE" --wait-flush 9>&-
