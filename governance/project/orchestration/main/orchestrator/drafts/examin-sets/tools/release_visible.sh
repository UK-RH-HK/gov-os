#!/bin/bash
# The owner's step 6 (FOR-THE-OWNER.md): release EXAMIN's visible half. The walled writer's delivery lands both halves in
# <sets root>/fixtures/evaluation/examin/hidden/ (the only place the launch script delivers to): the measured half as
# hidden/qNN.yaml and the development half as hidden/visible/qNN.yaml. This copies the second into the set's visible/ folder
# (the one `gov.retrieval.measure examin --part visible` reads, and which the guard leaves open), and leaves the originals.
# Nothing else is opened, and no file's text is read (copies only). It refuses unless visible/ is missing or empty,
# hidden/visible/ holds only regular qNN.yaml files (at least 5), and no earlier release record exists.
#   bash release_visible.sh <sets root> <set>        e.g.  bash release_visible.sh "$HOME/gov-os-eval" examin
#   bash release_visible.sh <sets root> <set> --undo  removes the copies this step made (by the record it wrote)
set -u
root="${1:-}"; set_name="${2:-}"; mode="${3:-}"
[ -n "$root" ] && [ -n "$set_name" ] || { echo "usage: release_visible.sh <sets root> <set> [--undo]" >&2; exit 2; }
case "$set_name" in *[!a-z0-9-]*|"") echo "refused: the set name" >&2; exit 2 ;; esac
base="$root/fixtures/evaluation/$set_name"
src="$base/hidden/visible"
dst="$base/visible"
rec="$base/.release-visible.record"
if [ "$mode" = "--undo" ]; then
  [ -f "$rec" ] || { echo "nothing to undo: no record" >&2; exit 3; }
  while read -r name sum; do
    [ -f "$dst/$name" ] && [ "$(sha256sum "$dst/$name" | cut -c1-64)" = "$sum" ] && rm -f "$dst/$name"
  done < "$rec"
  rmdir "$dst" 2>/dev/null
  rm -f "$rec"
  echo "undone"
  exit 0
fi
[ -d "$src" ] && [ ! -L "$src" ] || { echo "refused: no hidden/visible folder for set $set_name" >&2; exit 3; }
[ ! -e "$rec" ] || { echo "refused: already released (record exists)" >&2; exit 3; }
if [ -e "$dst" ]; then
  [ -d "$dst" ] && [ ! -L "$dst" ] && [ -z "$(ls -A "$dst")" ] || { echo "refused: visible/ exists and is not empty" >&2; exit 3; }
fi
n=0
for f in "$src"/*; do
  [ -e "$f" ] || continue
  b="$(basename "$f")"
  case "$b" in q[0-9][0-9].yaml) ;; *) echo "refused: unexpected file in hidden/visible: not a qNN.yaml" >&2; exit 3 ;; esac
  [ -f "$f" ] && [ ! -L "$f" ] || { echo "refused: $b is not a regular file" >&2; exit 3; }
  n=$((n + 1))
done
[ "$n" -ge 5 ] || { echo "refused: fewer than 5 files in hidden/visible ($n)" >&2; exit 3; }
mkdir -p "$dst" || exit 5
: > "$rec"
for f in "$src"/*; do
  b="$(basename "$f")"
  cp "$f" "$dst/$b" && chmod 644 "$dst/$b" || { echo "copy failed at $b" >&2; exit 5; }
  echo "$b $(sha256sum "$dst/$b" | cut -c1-64)" >> "$rec"
done
echo "released $n files into visible/"
