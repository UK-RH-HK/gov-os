#!/usr/bin/env bash
# The fresh 80's hold (FRESH-80-1 item 13; readiness-7 F5): begin and end it without touching anyone else's mark.
#   bash hold.sh begin     writes log/act-in-progress.txt with the line "FRESH-80 HOLD ..." only when no such file
#                          exists; when one exists (an ACT's freeze, an "E4-WINDOW NOT RESTORED" mark), it stops and
#                          shows that file's content: nothing is overwritten
#   bash hold.sh end       moves the file to act-in-progress.ended-<HHMM>-fresh80.txt only when it is the FRESH-80
#                          hold this script wrote (its first line starts "FRESH-80 HOLD"); any other mark is shown and
#                          left in place
# --file <path> names another file (tests only). Exit 0 done, 1 stopped.
set -u
F=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/act-in-progress.txt
cmd=${1:-}; shift || true
[ "${1:-}" = --file ] && { F=$2; shift 2; }
case "$cmd" in
  begin)
    if [ -e "$F" ]; then echo "STOP: a mark is in place already; nothing written. Its content:"; cat "$F"; exit 1; fi
    ( set -C; printf 'FRESH-80 HOLD: no commit on w2/integrate, no store rebuild, no GPU window (FRESH-80-1 item 13), from %s\n' "$(date '+%F %T')" > "$F" ) 2>/dev/null \
      || { echo "STOP: the mark could not be written new"; exit 1; }
    echo "the FRESH-80 hold begins: $(head -1 "$F")";;
  end)
    [ -e "$F" ] || { echo "STOP: no mark in place: nothing to end"; exit 1; }
    if head -1 "$F" | grep -q '^FRESH-80 HOLD'; then
      to=$(dirname "$F")/act-in-progress.ended-$(date +%H%M)-fresh80.txt
      mv "$F" "$to" && echo "the FRESH-80 hold ends"
    else
      echo "STOP: the mark in place is not the FRESH-80 hold; left as it is. Its content:"; cat "$F"; exit 1
    fi;;
  *) sed -n 2,9p "$0"; exit 2;;
esac
