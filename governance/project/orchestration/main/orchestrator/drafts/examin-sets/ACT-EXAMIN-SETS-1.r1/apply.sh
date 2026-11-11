#!/bin/bash
# ACT-EXAMIN-SETS-1's apply.sh: check | apply | undo | verify. The one file is governance/project/path-map.yaml in the
# repository it is run in (its cwd); list.txt holds its before and after sha256 (root|path|before|after). One change,
# frozen in the after copy: two entries added at the end of the `evaluation_sets:` block, `examin` and
# `adoption-proving-ground` (visible and hidden globs, measures by the five roles memory-verdict-2 names), and nothing
# else. The bundle is read from the script's own folder. The state is decided by the file's sha256 alone:
#   before   the file hashes as the frozen before copy (list.txt's before)
#   applied  the file hashes as the frozen after copy (list.txt's after)
#   other    anything else (changed since the freeze, missing, a link): refused, nothing is touched
#   check   read-only: prints "state before|applied (sha256 <12>)", exit 0; "state other: ..." on stderr and exit 3
#   apply   only from the state before: the frozen after copy put in place atomically (temp file beside the file, then
#           moved, mode kept); already applied: no change
#           ACT_BACKUP_BESIDE=1 first copies the file to <file>.bak-<UTC stamp>-ACT-EXAMIN-SETS-1 beside it (an extra copy
#           for a hand run; the operator agent's dry run does not set it)
#   undo    the frozen before copy put back, byte for byte, only when the file is as this ACT left it (the after hash)
#   verify  exit 0 only when the file is the after (the expected hash); exit 3 otherwise
# If the map changed after the freeze (state other), nothing is touched: rebuild the after copy from the current map with
# tools/insert_entries.py (beside this bundle) and freeze a new bundle; this one is not edited.
# The sets root's own path map is NOT touched here: it is the owner's by hand (class-rules row walled-sessions);
# see FOR-THE-OWNER.md step 2.
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
    if [ "${ACT_BACKUP_BESIDE:-0}" = 1 ]; then
      bak="$f.bak-$(date -u +%Y%m%dT%H%M%SZ)-ACT-EXAMIN-SETS-1"
      cp -p "$f" "$bak" || exit 5
      echo "backup $bak (sha256 $(h "$bak" | cut -c1-12))"
    fi
    mode="$(stat -c %a "$f")"
    cat "$src" > "$f.act-tmp" && chmod "$mode" "$f.act-tmp" && mv -f "$f.act-tmp" "$f" || { rm -f "$f.act-tmp"; exit 5; }
    echo "state applied (sha256 $(h "$f" | cut -c1-12))"; exit 0 ;;
  undo)
    src="$B/before/$root/$path"
    [ "$(h "$src")" = "$before" ] || { echo "the frozen copy does not hash as listed: $src" >&2; exit 4; }
    if [ "$st" = before ]; then echo "state before (sha256 ${now:0:12}); nothing to undo"; exit 0; fi
    [ "$st" = applied ] || { echo "refused: $path is not as this ACT left it (sha256 ${now:0:12}); a later change is not overwritten" >&2; exit 3; }
    mode="$(stat -c %a "$f")"
    cat "$src" > "$f.act-tmp" && chmod "$mode" "$f.act-tmp" && mv -f "$f.act-tmp" "$f" || { rm -f "$f.act-tmp"; exit 5; }
    echo "state before (sha256 $(h "$f" | cut -c1-12))"; exit 0 ;;
esac
