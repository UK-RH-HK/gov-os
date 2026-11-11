#!/bin/bash
# ACT-P95-1's apply.sh: check | apply | undo | verify. The one file is the resource gate's configuration under HOME
# (HOME is honoured, so a planted HOME is rehearsed); list.txt holds its before and after sha256 (root|path|before|after).
# The after copy differs from the before in one key, working_size_bytes (the p95 of the sampled sizes, not the maximum).
# The bundle is read from the script's own folder. The state is decided by the file's sha256 alone:
#   before   the file hashes as the frozen before copy (list.txt's before)
#   applied  the file hashes as the frozen after copy (list.txt's after)
#   other    anything else (changed since the freeze, missing, a link): refused, nothing is touched
#   check   read-only: prints "state before|applied (sha256 <12>)", exit 0; "state other: ..." on stderr and exit 3
#   apply   only from the state before: the frozen after copy put in place atomically (a mktemp file beside the file, mode
#           kept, then moved); already applied: no change
#   undo    the frozen before copy put back, byte for byte, only when the file is as this ACT left it (the after hash)
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
if [ "$now" = "$before" ]; then st=before
elif [ "$now" = "$after" ]; then st=applied
else st=other; fi
put() { # put <frozen copy>: replace the file whole, mode kept, through a mktemp file beside it
  local t mode
  mode="$(stat -c %a "$f")" || return 1
  t="$(mktemp "$f.act-XXXXXX")" || return 1
  if cat "$1" > "$t" && chmod "$mode" "$t" && mv -f "$t" "$f"; then return 0; fi
  rm -f "$t"; return 1
}
case "$step" in
  check)
    if [ "$st" = other ]; then
      if [ "$now" = null ]; then why="the file is missing"; else why="changed since the freeze"; fi
      echo "state other: $why (sha256 ${now:0:12})" >&2; exit 3
    fi
    echo "state $st (sha256 ${now:0:12})"; exit 0 ;;
  verify)
    [ "$now" = "$after" ] || { echo "not applied: $path (sha256 ${now:0:12})" >&2; exit 3; }
    exit 0 ;;
  apply)
    if [ "$st" = other ]; then echo "refused: $path is neither the frozen before nor the frozen after (sha256 ${now:0:12})" >&2; exit 3; fi
    if [ "$st" = applied ]; then echo "state applied (sha256 ${now:0:12}); nothing to do"; exit 0; fi
    src="$B/after/$root/$path"
    [ "$(h "$src")" = "$after" ] || { echo "the frozen copy does not hash as listed: $src" >&2; exit 4; }
    put "$src" || exit 5
    echo "state applied (sha256 $(h "$f" | cut -c1-12))"; exit 0 ;;
  undo)
    src="$B/before/$root/$path"
    [ "$(h "$src")" = "$before" ] || { echo "the frozen copy does not hash as listed: $src" >&2; exit 4; }
    if [ "$st" = before ]; then echo "state before (sha256 ${now:0:12}); nothing to undo"; exit 0; fi
    [ "$st" = applied ] || { echo "refused: $path is not as this ACT left it (sha256 ${now:0:12}); a later change is not overwritten" >&2; exit 3; }
    put "$src" || exit 5
    echo "state before (sha256 $(h "$f" | cut -c1-12))"; exit 0 ;;
esac
