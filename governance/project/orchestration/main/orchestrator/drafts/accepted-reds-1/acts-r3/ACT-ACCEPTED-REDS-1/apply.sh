#!/bin/bash
# ACT-ACCEPTED-REDS-1's apply.sh (round 3): check | apply | undo | verify. The one file is governance/project/path-map.yaml in the
# repository it is run in (its cwd); list.txt holds its before and after sha256 (root|path|before|after). One change,
# frozen in the after copy: the line `accepted_reds: []` becomes two entries (the warm real-model latency cases of W1-19 and W2-13, decision DEC-1134, fixed_by W2-155), and nothing else. The "before" is the map as ACT-EXAMIN-SETS-1 leaves it (sha256 1fe00f43d8ab...): this ACT runs AFTER that one. On any other map it refuses and touches nothing.
# The bundle is read from the script's own folder. The state is decided by the file's sha256 alone:
#   before   the file hashes as the frozen before copy (list.txt's before)
#   applied  the file hashes as the frozen after copy (list.txt's after)
#   other    anything else (changed since the freeze, missing, a link, another path-map ACT applied out of order): refused, nothing touched
#   check   read-only: prints "state before|applied (sha256 <12>)", exit 0; "state other: ..." on stderr and exit 3
#   apply   only from the state before: the frozen after copy put in place atomically (a temp file made by mktemp in the
#           map's own folder, then moved, mode kept); already applied: no change; no backup file is made
#   undo    the frozen before copy put back, byte for byte, only when the file is as this ACT left it (the after hash)
#   verify  exit 0 only when the file is the after (the expected hash); exit 3 otherwise
# The ratchet reads these entries only from a commit with `Role: owner`; this script does not commit. The owner's operator
# commits by hand (ACT-ACCEPTED-REDS-1.md section 5).
# If the map changed after the freeze (state other), nothing is touched: rebuild the after copy from the current map with
#   .gov-runtime/scratch/orchestrator/drafts/accepted-reds-1/tools/insert_reds.py
# (and build_r3.py, the rehearsal scripts beside it) and freeze a new bundle; this one is not edited.
set -u
B="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
step="${1:-}"
case "$step" in check|apply|undo|verify) ;; *) echo "usage: apply.sh check|apply|undo|verify" >&2; exit 2 ;; esac
IFS='|' read -r root path before after < "$B/list.txt"
[ "$root" = repo ] || { echo "not a repository path: $root" >&2; exit 9; }
f="$PWD/$path"
h() { if [ -f "$1" ]; then sha256sum "$1" | cut -c1-64; else echo null; fi; }
[ ! -L "$f" ] || { echo "refused: $path is a link" >&2; exit 3; }
now="$(h "$f")"
if [ "$now" = "$before" ]; then st=before
elif [ "$now" = "$after" ]; then st=applied
else st=other; fi
put() { # put <frozen copy>: replace the map by it, atomically, mode kept; a stray temp file is removed on failure
  local src="$1" mode tmp
  mode="$(stat -c %a "$f")" || return 1
  tmp="$(mktemp "$f.act-tmp.XXXXXX")" || return 1
  if cat "$src" > "$tmp" && chmod "$mode" "$tmp" && mv -f "$tmp" "$f"; then return 0; fi
  rm -f "$tmp"; return 1
}
case "$step" in
  check)
    if [ "$st" = other ]; then
      if [ "$now" = null ]; then why="the file is missing"; else why="not the frozen before (ACT-EXAMIN-SETS-1 not applied yet?) and not the frozen after"; fi
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
