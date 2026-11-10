#!/bin/bash
# ACT-DEADMAN-WAKE-1's apply.sh: check | apply | undo | verify, by list.txt (root|path|before sha256|after sha256),
# relative to the repository it is run in (its cwd); the bundle is read from the script's own folder. Each frozen copy
# is hashed against list.txt before it is written, then moved into place whole (the running watch keeps its loaded
# code; the sentinel's next watch start reads the new file). Nothing but the listed file is touched.
#   check   the live file is the "before" (exit 3 "moved: <path>" otherwise)
#   apply   the "after" copy put in place          undo   the "before" copy put back
#   verify  the live file is the "after" (exit 3 "not applied: <path>" otherwise)
set -u
B="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
step="${1:-}"
case "$step" in check|apply|undo|verify) ;; *) echo "usage: apply.sh check|apply|undo|verify" >&2; exit 2 ;; esac
h() { if [ -f "$1" ]; then sha256sum "$1" | cut -c1-64; else echo null; fi; }
while IFS='|' read -r root path before after; do
  [ -z "$root" ] && continue
  [ "$root" = repo ] || { echo "not a repository path: $root" >&2; exit 9; }
  f="$PWD/$path"
  case "$step" in
    check) [ "$(h "$f")" = "$before" ] || { echo "moved: $path" >&2; exit 3; } ;;
    verify) [ "$(h "$f")" = "$after" ] || { echo "not applied: $path" >&2; exit 3; } ;;
    apply|undo)
      if [ "$step" = apply ]; then want=$after; src="$B/after/$root/$path"; else want=$before; src="$B/before/$root/$path"; fi
      [ "$(h "$src")" = "$want" ] || { echo "the frozen copy does not hash as listed: $src" >&2; exit 4; }
      cat "$src" > "$f.act-tmp" && chmod 644 "$f.act-tmp" && mv -f "$f.act-tmp" "$f" || exit 5 ;;
  esac
done < "$B/list.txt"
exit 0
