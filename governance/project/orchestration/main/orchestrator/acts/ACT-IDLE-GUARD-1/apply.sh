#!/bin/bash
# ACT-IDLE-GUARD-1's apply.sh: check | apply | undo | verify, by list.txt (root|path|before sha256|after sha256), relative
# to the repository it is run in (its cwd); the bundle is read from the script's own folder. Two files: the CTO's Stop
# hook (governance/project/orchestration/tools/stop_idle_check.py) and the dispatcher (.../dispatch/dispatcher.py). The
# state of each file is decided by its sha256 alone:
#   before   hashes as list.txt's before          applied  hashes as its after
#   other    anything else (changed since the freeze, missing, a link): refused, NOTHING is touched (every file is
#            read first; no file is written unless every file is as the step expects)
#   check    read-only: every file is the before; exit 0, else exit 3 "moved: <path>"
#   apply    every file is the before (or the after: left as it is); the frozen after copy of each file that is still
#            the before is written to a temp file made by mktemp beside it, the mode kept, then moved into place whole
#   undo     every file is the after (or the before: left as it is); the frozen before copy put back the same way
#   verify   every file is the after; exit 0, else exit 3 "not applied: <path>"
# Each frozen copy is hashed against list.txt before it is used (exit 4 when it does not hash as listed). Nothing but the
# listed files is touched (a temp file is renamed over its file, so none is left). The running dispatcher tick and the
# running Stop hook each read their file whole at their start: no restart is needed.
set -u
B="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
step="${1:-}"
case "$step" in check|apply|undo|verify) ;; *) echo "usage: apply.sh check|apply|undo|verify" >&2; exit 2 ;; esac
h() { if [ -f "$1" ] && [ ! -L "$1" ]; then sha256sum "$1" | cut -c1-64; else echo null; fi; }
put() {  # put <frozen copy> <file>: the copy in place of the file, atomically, the mode kept
  local src="$1" f="$2" mode tmp
  mode="$(stat -c %a "$f")" || return 1
  tmp="$(mktemp "$f.act-XXXXXX")" || return 1
  if cat "$src" > "$tmp" && chmod "$mode" "$tmp" && mv -f "$tmp" "$f"; then return 0; fi
  rm -f "$tmp"
  return 1
}
roots=(); paths=(); befores=(); afters=()
while IFS='|' read -r root path before after; do
  [ -z "$root" ] && continue
  [ "$root" = repo ] || { echo "not a repository path: $root" >&2; exit 9; }
  roots+=("$root"); paths+=("$path"); befores+=("$before"); afters+=("$after")
done < "$B/list.txt"
[ "${#paths[@]}" -gt 0 ] || { echo "list.txt names no file" >&2; exit 9; }
# the first pass reads every file and refuses before anything is written
states=()
for i in "${!paths[@]}"; do
  now="$(h "$PWD/${paths[$i]}")"
  if [ "$now" = "${befores[$i]}" ]; then st=before; elif [ "$now" = "${afters[$i]}" ]; then st=applied; else st=other; fi
  states+=("$st")
  case "$step" in
    check) [ "$st" = before ] || { echo "moved: ${paths[$i]}" >&2; exit 3; } ;;
    verify) [ "$st" = applied ] || { echo "not applied: ${paths[$i]}" >&2; exit 3; } ;;
    apply|undo) [ "$st" != other ] || { echo "moved: ${paths[$i]} (neither the before nor the after; $step refused, nothing touched)" >&2; exit 3; } ;;
  esac
done
[ "$step" = apply ] || [ "$step" = undo ] || exit 0
if [ "$step" = apply ]; then want=applied; dir=after; else want=before; dir=before; fi
for i in "${!paths[@]}"; do
  [ "${states[$i]}" = "$want" ] && continue
  if [ "$step" = apply ]; then sum="${afters[$i]}"; else sum="${befores[$i]}"; fi
  src="$B/$dir/${roots[$i]}/${paths[$i]}"
  [ "$(h "$src")" = "$sum" ] || { echo "the frozen copy does not hash as listed: $src" >&2; exit 4; }
done
for i in "${!paths[@]}"; do
  if [ "${states[$i]}" = "$want" ]; then echo "already in place: ${paths[$i]} ($step)"; continue; fi
  put "$B/$dir/${roots[$i]}/${paths[$i]}" "$PWD/${paths[$i]}" || { echo "could not write ${paths[$i]}" >&2; exit 5; }
done
exit 0
