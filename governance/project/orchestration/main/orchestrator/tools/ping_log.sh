#!/usr/bin/env bash
# DEC-972: the ping's log line, written without the owner's ask rule (owner-ping keeps its ask, the daytime fallback).
#   ping_log.sh "<P1|ACT|...> <id> | gates ... | <need>"    one line, as owner-ping writes it
#   ping_log.sh --result "<sent|not sent>"                  the PushNotification's answer, beside the last line
dir="$HOME/.config/gov-os-notify"; mkdir -p "$dir" && chmod 700 "$dir"
if [ "$1" = "--result" ]; then
  printf '%s   push: %s\n' "$(date '+%Y-%m-%dT%H:%M:%S%z')" "$2" >> "$dir/pings.log"
else
  printf '%s %s\n' "$(date '+%Y-%m-%dT%H:%M:%S%z')" "$*" >> "$dir/pings.log"
fi
exit 0
