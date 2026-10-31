#!/usr/bin/env bash
# Every ping of the nightly goes through here (owner, DEC-936, DEC-973: a P1 in the quiet hours, 02:00 to 07:30, is
# held unless the owner is already active; held pings go out with the 08:00 check, or as soon as the owner is active).
#   ping_gate.sh "<message>"   from 07:30 to 02:00: pings at once. From 02:00 to 07:30 (the owner's quiet hours, DEC-973): pings at once only if
#                              the owner has used Windows in the last 15 minutes; otherwise holds the message in
#                              log/nightly/pending-pings.txt, with the time it was held.
#   ping_gate.sh --flush       pings every held message, marked "held from <time>", and empties the file.
#   ping_gate.sh --wait-flush  waits (a check every 5 minutes) until the quiet hours end (07:30) or the owner is active,
#                              then flushes; called at 08:00 by the morning check, it flushes at once.
# The owner is "active" when Windows' last input (GetLastInputInfo, read through PowerShell) is under 15 minutes old.
# If that cannot be read, the owner is taken as not active: a held ping still goes out with the 08:00 check, never lost.
ORCH=${NIGHTLY_ORCH:-/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator}
PING=${NIGHTLY_PING:-/home/usain/.local/bin/owner-ping}
PENDING=$ORCH/log/nightly/pending-pings.txt
ACTIVE_S=900
mkdir -p "$ORCH/log/nightly"

now_hm() { echo "${NIGHTLY_NOW_HM:-$(date +%H%M)}"; }

idle_seconds() {  # Windows' seconds since the last input; empty when it cannot be read
  if [ -n "${NIGHTLY_IDLE_S+x}" ]; then echo "$NIGHTLY_IDLE_S"; return; fi
  local ps=/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe
  [ -x "$ps" ] || return
  local script
  script=$(cat <<'PS'
Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class GovIdle {
    [StructLayout(LayoutKind.Sequential)] struct LASTINPUTINFO { public uint cbSize; public uint dwTime; }
    [DllImport("user32.dll")] static extern bool GetLastInputInfo(ref LASTINPUTINFO info);
    public static long Seconds() {
        LASTINPUTINFO i = new LASTINPUTINFO(); i.cbSize = (uint)Marshal.SizeOf(i);
        if (!GetLastInputInfo(ref i)) { return -1; }
        return ((uint)Environment.TickCount - i.dwTime) / 1000;
    }
}
"@
[GovIdle]::Seconds()
PS
)
  timeout 60 "$ps" -NoProfile -NonInteractive -Command "$script" 2>/dev/null | tr -d '\r' | grep -E '^[0-9]+$' | tail -1
}

owner_active() {
  local idle; idle=$(idle_seconds)
  [ -n "$idle" ] && [ "$idle" -lt "$ACTIVE_S" ]
}

daytime() { local hm=$((10#$(now_hm))); [ "$hm" -ge 730 ] || [ "$hm" -lt 200 ]; }  # quiet hours 02:00-07:30 (DEC-973)

flush() {
  [ -s "$PENDING" ] || return 0
  while IFS=$'\t' read -r held message; do
    [ -n "$message" ] && "$PING" "$message (held from $held)"
  done < "$PENDING"
  : > "$PENDING"
}

case "$1" in
  --flush) flush ;;
  --wait-flush)
    [ -s "$PENDING" ] || exit 0
    until daytime || owner_active; do sleep "${NIGHTLY_WAIT_STEP:-300}"; done
    flush ;;
  *)
    if daytime || owner_active; then
      "$PING" "$1"
    else
      printf '%s\t%s\n' "$(date '+%F %H:%M')" "$1" >> "$PENDING"
    fi ;;
esac
