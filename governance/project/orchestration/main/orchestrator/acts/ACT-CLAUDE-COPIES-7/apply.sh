#!/bin/bash
# The copies ACT's apply.sh: reads its bundle from its own folder; check, apply, undo by list.txt, relative to the
# repository it is run in (its cwd). A failed step stops it with a non-zero exit (never a silent partial apply).
set -u
B="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
step="${1:-}"
while IFS='|' read -r root path before after; do
  [ -z "$root" ] && continue
  case "$root" in repo) f="$PWD/$path" ;; *) exit 9 ;; esac
  case "$step" in
    check)
      if [ -f "$f" ]; then h=$(sha256sum "$f" | cut -c1-64); else h=null; fi
      [ "$h" = "$before" ] || { echo "moved: $path" >&2; exit 3; } ;;
    apply)
      if [ "$after" = null ]; then rm -f "$f" || exit 4
      else mkdir -p "$(dirname "$f")" && rm -f "$f" && cat "$B/after/$root/$path" > "$f" || { echo "failed: $path" >&2; exit 4; }; fi ;;
    undo)
      if [ "$before" = null ]; then rm -f "$f" || exit 4
      else mkdir -p "$(dirname "$f")" && rm -f "$f" && cat "$B/before/$root/$path" > "$f" || { echo "failed: $path" >&2; exit 4; }; fi ;;
    *) exit 2 ;;
  esac
done < "$B/list.txt"
exit 0
