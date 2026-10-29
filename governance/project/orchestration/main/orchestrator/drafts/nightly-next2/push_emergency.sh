#!/usr/bin/env bash
# One emergency push to the owner's phone through Pushover (owner, DEC-939 item 7; DEC-938 item 6's emergencies only:
# a secret exposed, a risk of losing data or history, the disk below its floor, the guard failing open).
#   push_emergency.sh "<one short status line>"
# - The token and the user key are read from ~/.config/gov-os-notify/pushover.env (PUSHOVER_TOKEN=..., PUSHOVER_USER=...),
#   outside every repository; the file must be the owner's alone (mode 600), or nothing is sent.
# - The message is one line of at most 120 characters from a fixed set (letters, digits, spaces and . , : ; | ( ) + - _ %).
#   Anything else (a path, code, a long token-like string) is replaced by a fixed line: no code, path or secret leaves.
# - Every attempt, sent or not, is logged to pings.log as an "EMERGENCY" line (never the token), so the morning
#   package shows it. Always exits 0: a push that cannot be sent never stops the caller.
ENV=${NIGHTLY_PUSHOVER_ENV:-/home/usain/.config/gov-os-notify/pushover.env}
LOG=${NIGHTLY_PINGS_LOG:-/home/usain/.config/gov-os-notify/pings.log}
SEND=${NIGHTLY_PUSH_SEND:-curl}
FALLBACK="Gov OS emergency: see the morning package"
msg=$1
if [ "${#msg}" -gt 120 ] || ! printf '%s' "$msg" | grep -Eq '^[A-Za-z0-9 .,:;|()+_%-]+$' \
   || printf '%s' "$msg" | grep -Eq '[0-9a-fA-F]{12,}'; then
  msg=$FALLBACK
fi
note() { mkdir -p "$(dirname "$LOG")" && printf '%s EMERGENCY %s\n' "$(date '+%Y-%m-%dT%H:%M:%S%z')" "$1" >> "$LOG"; }
if [ ! -f "$ENV" ] || [ "$(stat -c %a "$ENV" 2>/dev/null)" != "600" ]; then
  note "not pushed (no Pushover file with mode 600): $msg"; exit 0
fi
token=$(grep -E '^PUSHOVER_TOKEN=' "$ENV" | head -1 | cut -d= -f2-)
user=$(grep -E '^PUSHOVER_USER=' "$ENV" | head -1 | cut -d= -f2-)
if [ -z "$token" ] || [ -z "$user" ]; then
  note "not pushed (token or user key missing): $msg"; exit 0
fi
# Everything goes to curl as a configuration on its standard input (--config -): the token and the key never appear
# on a command line (seen by ps) or in any log, and curl URL-encodes each field. The message's fixed character set
# holds no quote or backslash, so it cannot break the configuration's quoting.
if printf '%s\n' 'url = "https://api.pushover.net/1/messages.json"' "data-urlencode = \"token=$token\"" \
     "data-urlencode = \"user=$user\"" 'data = "priority=1"' "data-urlencode = \"message=$msg\"" \
     'silent' 'max-time = 20' 'output = "/dev/null"' 'write-out = "%{http_code}"' \
   | "$SEND" --config - | grep -q '^200$'; then
  note "pushed: $msg"
else
  note "push failed: $msg"
fi
exit 0
