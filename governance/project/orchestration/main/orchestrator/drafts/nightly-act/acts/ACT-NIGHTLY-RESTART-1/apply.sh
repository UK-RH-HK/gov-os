#!/bin/bash
# ACT-NIGHTLY-RESTART-1's apply.sh: check | apply | undo | verify, by list.txt (root|path|before sha256|after sha256).
# The one listed file is the crontab (root "crontab", path "crontab"): its bytes are `crontab -l`'s. The frozen copies are
# in this script's own folder (before/crontab/crontab, after/crontab/crontab); each is hashed against list.txt before it is
# installed with `crontab <file>`. Nothing but the crontab is touched.
#   check   the live crontab is the "before" (exit 3 "moved: crontab" otherwise)
#   apply   the "after" crontab installed       undo   the "before" crontab put back
#   verify  the live crontab is the "after" (exit 3 "not applied: crontab" otherwise)
set -u
B="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
step="${1:-}"
case "$step" in check|apply|undo|verify) ;; *) echo "usage: apply.sh check|apply|undo|verify" >&2; exit 2 ;; esac
h() { if [ -f "$1" ]; then sha256sum "$1" | cut -c1-64; else echo null; fi; }
live() { local t; t="$(mktemp)" || exit 5; if crontab -l > "$t" 2>/dev/null; then sha256sum "$t" | cut -c1-64; else echo null; fi; rm -f "$t"; }
while IFS='|' read -r root path before after; do
  [ -z "$root" ] && continue
  [ "$root" = crontab ] && [ "$path" = crontab ] || { echo "not the crontab: $root|$path" >&2; exit 9; }
  case "$step" in
    check) [ "$(live)" = "$before" ] || { echo "moved: crontab" >&2; exit 3; } ;;
    verify) [ "$(live)" = "$after" ] || { echo "not applied: crontab" >&2; exit 3; } ;;
    apply|undo)
      if [ "$step" = apply ]; then want=$after; src="$B/after/crontab/crontab"; else want=$before; src="$B/before/crontab/crontab"; fi
      [ "$(h "$src")" = "$want" ] || { echo "the frozen copy does not hash as listed: $src" >&2; exit 4; }
      crontab "$src" || exit 5 ;;
  esac
done < "$B/list.txt"
exit 0
