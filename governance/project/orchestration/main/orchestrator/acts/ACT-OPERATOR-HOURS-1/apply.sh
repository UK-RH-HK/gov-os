#!/bin/bash
# ACT-OPERATOR-HOURS-1's apply.sh: check | apply | undo | verify, by list.txt (root|path|before sha256|after sha256).
# The one listed file is the crontab (root "crontab", path "crontab"): its bytes are `crontab -l`'s. The frozen copies are
# in this script's own folder (before/crontab/crontab, after/crontab/crontab); each is hashed against list.txt before it is
# installed with `crontab <file>` (which refuses a file it cannot parse and leaves the old table). Nothing but the crontab
# is touched.
#   check   the install's opcommon.py is ACT-OPERATOR-HOURS-2's after copy (exit 7 otherwise); the live crontab is the "before"
#           (exit 3 "moved: crontab" otherwise)
#   apply   the same gate first (exit 7, nothing touched); then the "after" crontab installed; only over the "before" (or when it is already the "after": nothing to do);
#           over anything else exit 3 and nothing is touched
#   undo    the "before" crontab put back; only over the "after" (or when it is already the "before"); otherwise exit 3
#   verify  the live crontab is the "after" (exit 3 "not applied: crontab" otherwise)
set -u
B="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
step="${1:-}"
case "$step" in check|apply|undo|verify) ;; *) echo "usage: apply.sh check|apply|undo|verify" >&2; exit 2 ;; esac
h() { if [ -f "$1" ]; then sha256sum "$1" | cut -c1-64; else echo null; fi; }
# The gate (round 2): this ACT's crontab guard and the launcher's own G9 must agree, so check and apply refuse (exit 7) until the
# install's opcommon.py is ACT-OPERATOR-HOURS-2's after copy (its list.txt, the home row of gov-os-operator/install/opcommon.py).
# undo and verify never need it (an undo must always work).
HOURS2_AFTER=123e17e5581149725c75babaa9200a09c4854254053df14105b6ce17450bbc87
OPC="$HOME/gov-os-operator/install/opcommon.py"
case "$step" in check|apply)
  if [ -L "$OPC" ] || [ ! -f "$OPC" ] || [ "$(h "$OPC")" != "$HOURS2_AFTER" ]; then
    echo "ACT-OPERATOR-HOURS-2 is not applied: the install's opcommon.py is not its after copy (${HOURS2_AFTER:0:12}); apply it first; $step refused, nothing touched" >&2
    exit 7
  fi ;;
esac
live() { local t; t="$(mktemp)" || exit 5; if crontab -l > "$t" 2>/dev/null; then sha256sum "$t" | cut -c1-64; else echo null; fi; rm -f "$t"; }
while IFS='|' read -r root path before after; do
  [ -z "$root" ] && continue
  [ "$root" = crontab ] && [ "$path" = crontab ] || { echo "not the crontab: $root|$path" >&2; exit 9; }
  case "$step" in
    check) [ "$(live)" = "$before" ] || { echo "moved: crontab" >&2; exit 3; } ;;
    verify) [ "$(live)" = "$after" ] || { echo "not applied: crontab" >&2; exit 3; } ;;
    apply|undo)
      if [ "$step" = apply ]; then want=$after; other=$before; src="$B/after/crontab/crontab"; else want=$before; other=$after; src="$B/before/crontab/crontab"; fi
      now="$(live)"
      [ "$now" = "$want" ] && { echo "already in place: crontab ($step)"; continue; }
      [ "$now" = "$other" ] || { echo "moved: crontab (neither the before nor the after; $step refused, nothing touched)" >&2; exit 3; }
      [ "$(h "$src")" = "$want" ] || { echo "the frozen copy does not hash as listed: $src" >&2; exit 4; }
      crontab "$src" || exit 5 ;;
  esac
done < "$B/list.txt"
exit 0
