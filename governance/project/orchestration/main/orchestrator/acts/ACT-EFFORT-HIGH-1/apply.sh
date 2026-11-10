#!/bin/bash
# ACT-EFFORT-HIGH-1's apply.sh: check | apply | undo | verify. The one file is the settings file under HOME
# (HOME is honoured, so a planted HOME is rehearsed); list.txt holds its before and after sha256 (root|path|before|after).
# Only the top-level "effortLevel" changes, "xhigh" to "high", by effort.py (a text splice: key order, layout and every
# other byte kept). The bundle is read from the script's own folder; nothing but the one file is touched.
#   check   read-only: prints "state before|applied|other" and the file's sha256 cut to 12; exit 0 for before or applied,
#           exit 3 for anything else (a top-level effortLevel that is neither "xhigh" nor "high", an unreadable file)
#   apply   the edit, atomically (temp file beside the file, then moved into place, mode kept); already applied: no change
#           ACT_BACKUP_BESIDE=1 first copies the file to <file>.bak-<UTC stamp>-ACT-EFFORT-HIGH-1 beside it (an extra copy
#           for a hand run; the operator agent's dry run leaves a clean HOME, so it does not set it)
#   undo    the frozen "before" copy put back, byte for byte, only when the file is as this ACT left it (the after hash)
#   verify  exit 0 only when the file is the after (the expected hash); exit 3 otherwise
set -u
B="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
step="${1:-}"
case "$step" in check|apply|undo|verify) ;; *) echo "usage: apply.sh check|apply|undo|verify" >&2; exit 2 ;; esac
IFS='|' read -r root path before after < "$B/list.txt"
[ "$root" = home ] || { echo "not a HOME path: $root" >&2; exit 9; }
f="${HOME:?HOME is not set}/$path"
h() { if [ -f "$1" ]; then sha256sum "$1" | cut -c1-64; else echo null; fi; }
[ ! -L "$f" ] || { echo "refused: $path is a link" >&2; exit 3; }
now="$(h "$f")"
st="$(python3 -I "$B/effort.py" state "$f")"; rc=$?
case "$step" in
  check)
    if [ "$rc" -ne 0 ]; then echo "state other: ${st#other: } (sha256 ${now:0:12})" >&2; exit 3; fi
    echo "state $st (sha256 ${now:0:12})"; exit 0 ;;
  verify)
    [ "$now" = "$after" ] || { echo "not applied: $path (sha256 ${now:0:12})" >&2; exit 3; }
    exit 0 ;;
  apply)
    if [ "$rc" -ne 0 ]; then echo "refused: ${st#other: } (sha256 ${now:0:12})" >&2; exit 3; fi
    if [ "$st" = applied ]; then echo "state applied (sha256 ${now:0:12}); nothing to do"; exit 0; fi
    if [ "${ACT_BACKUP_BESIDE:-0}" = 1 ]; then
      bak="$f.bak-$(date -u +%Y%m%dT%H%M%SZ)-ACT-EFFORT-HIGH-1"
      cp -p "$f" "$bak" || exit 5
      echo "backup $bak (sha256 $(h "$bak" | cut -c1-12))"
    fi
    mode="$(stat -c %a "$f")"
    python3 -I "$B/effort.py" edit "$f" "$f.act-tmp" || { rm -f "$f.act-tmp"; exit 5; }
    chmod "$mode" "$f.act-tmp" && mv -f "$f.act-tmp" "$f" || { rm -f "$f.act-tmp"; exit 5; }
    echo "state applied (sha256 $(h "$f" | cut -c1-12))"; exit 0 ;;
  undo)
    src="$B/before/$root/$path"
    [ "$(h "$src")" = "$before" ] || { echo "the frozen copy does not hash as listed: $src" >&2; exit 4; }
    if [ "$now" = "$before" ]; then echo "state before (sha256 ${now:0:12}); nothing to undo"; exit 0; fi
    [ "$now" = "$after" ] || { echo "refused: $path is not as this ACT left it (sha256 ${now:0:12}); a later change is not overwritten" >&2; exit 3; }
    mode="$(stat -c %a "$f")"
    cat "$src" > "$f.act-tmp" && chmod "$mode" "$f.act-tmp" && mv -f "$f.act-tmp" "$f" || { rm -f "$f.act-tmp"; exit 5; }
    echo "state before (sha256 $(h "$f" | cut -c1-12))"; exit 0 ;;
esac
