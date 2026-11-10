#!/bin/bash
# ACT-PATHMAP-NS-2's apply.sh: check | apply | undo | verify, by list.txt (root|path|before sha256|after sha256),
# relative to the repository it is run in (its cwd); the bundle is read from the script's own folder. The one file is the
# path map; the change is one comment line and one namespace path (see path-map.patch). The frozen copies are hashed
# against list.txt before they are used, and moved into place whole (temp file beside the map, mode kept).
#   check   read-only: prints "state before|applied|other (sha256 <12>)"; exit 0 for before or applied, exit 3 for other
#   apply   only from "before"; first copies the live map to <bundle>/backup/path-map.yaml.<UTC stamp> (ACT_NO_BACKUP=1
#           skips it); then the "after" copy is put in place. Already applied: no change, exit 0
#   undo    the frozen "before" copy put back, byte for byte, only when the map is as this ACT left it (the after hash);
#           already before: nothing to do. A later change is never overwritten (exit 3)
#   verify  exit 0 only when the map is the after (exit 3 "not applied: <path>" otherwise)
set -u
B="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
step="${1:-}"
case "$step" in check|apply|undo|verify) ;; *) echo "usage: apply.sh check|apply|undo|verify" >&2; exit 2 ;; esac
IFS='|' read -r root path before after < "$B/list.txt"
[ "$root" = repo ] || { echo "not a repository path: $root" >&2; exit 9; }
f="$PWD/$path"
h() { if [ -f "$1" ]; then sha256sum "$1" | cut -c1-64; else echo null; fi; }
[ -f "$f" ] || { echo "state other: no $path under $PWD" >&2; exit 3; }
[ ! -L "$f" ] || { echo "refused: $path is a link" >&2; exit 3; }
now="$(h "$f")"
if [ "$now" = "$before" ]; then st=before; elif [ "$now" = "$after" ]; then st=applied; else st=other; fi
case "$step" in
  check)
    if [ "$st" = other ]; then echo "state other (sha256 ${now:0:12}); expected before ${before:0:12} or applied ${after:0:12}" >&2; exit 3; fi
    echo "state $st (sha256 ${now:0:12})"; exit 0 ;;
  verify)
    [ "$now" = "$after" ] || { echo "not applied: $path (sha256 ${now:0:12})" >&2; exit 3; }
    exit 0 ;;
  apply)
    if [ "$st" = applied ]; then echo "state applied (sha256 ${now:0:12}); nothing to do"; exit 0; fi
    if [ "$st" = other ]; then echo "refused: $path is neither the before nor the after (sha256 ${now:0:12})" >&2; exit 3; fi
    src="$B/after/$root/$path"
    [ "$(h "$src")" = "$after" ] || { echo "the frozen copy does not hash as listed: $src" >&2; exit 4; }
    if [ "${ACT_NO_BACKUP:-0}" != 1 ]; then
      mkdir -p "$B/backup" || exit 5
      bak="$B/backup/$(basename "$path").$(date -u +%Y%m%dT%H%M%SZ)"
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
