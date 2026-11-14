#!/bin/bash
# ACT-GUARD-FIX-5's apply.sh: check | apply | undo | verify (round 2). The one file is .claude/hooks/bash_writes.py in the
# repository it is run in (its cwd); list.txt holds its before and after sha256 (root|path|before|after). One change,
# frozen in the after copy (P1-GUARD-HEREDOC-OPTS-1, then review round 1's F1): _kind, which says how a command reads a
# heredoc, no longer takes the value of a shell's option (bash -euo pipefail, -o <opt>, -O <opt>, --rcfile <f>,
# --init-file <f>) for a script file; it skips the values, reads - and /dev/stdin and /dev/fd/0 as standard input, and
# reads a shell with an option it does not know as a shell (fail closed); -c is data and -s is shell, as before. And
# the two places that judge a heredoc body for a reader that is a shell: an unquoted body with nothing for the shell to
# expand or join is judged as the quoted one; an unquoted body with expansions has its command substitutions judged, as
# for cat; and a body written to a file the command then runs is still judged as that file's code. Stricter only:
# nothing refused before is allowed after. The hook (pretooluse.py) is not changed. The bundle is read from the
# script's own folder.
# The state is decided by the file's sha256 alone:
#   before   the file hashes as the frozen before copy (list.txt's before)
#   applied  the file hashes as the frozen after copy (list.txt's after)
#   other    anything else (changed since the freeze, missing, a link): refused, nothing is touched
#   check   read-only: prints "state before|applied (sha256 <12>)", exit 0; "state other: ..." on stderr and exit 3
#   apply   only from the state before: the frozen after copy put in place atomically (a temp file made by mktemp beside
#           the file, the mode kept, then moved); already applied: no change; no other file is written
#   undo    the frozen before copy put back, byte for byte, only when the file is as this ACT left it (the after hash)
#   verify  exit 0 only when the file is the after (the expected hash); exit 3 otherwise
# The file is replaced by mv (a new inode): the hook reads it at each call, so a call in flight keeps the module it
# loaded and the next call reads the new file. No other file of the hook or of the settings is read or written here.
# If bash_writes.py changed after the freeze (state other), nothing is touched: rebuild the after copy from the current
# file (the change is drafts/act-guard-fix-5/bash_writes.diff: _kind's shell branch calls _shell_kind, the _SHELL_*
# constants and _shell_kind follow _kind, and body() and the held-body loop of the judgement get the two edits above)
# and freeze a new bundle.
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
put() {  # put <source copy>: the copy in place of the file, atomically, mode kept
  local src="$1" mode tmp
  mode="$(stat -c %a "$f")" || return 1
  tmp="$(mktemp "$f.act-XXXXXX")" || return 1
  if cat "$src" > "$tmp" && chmod "$mode" "$tmp" && mv -f "$tmp" "$f"; then return 0; fi
  rm -f "$tmp"
  return 1
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
