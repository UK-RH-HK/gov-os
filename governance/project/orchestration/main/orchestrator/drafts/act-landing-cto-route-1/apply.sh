#!/bin/bash
# ACT-LANDING-CTO-ROUTE-1 (DEC-1167 (5)): the landing check passes a commit of the CTO's own (b) ACT. Class (O): the
# operator's own install is the owner's, by hand (DEC-1104 (4)); the owner's operator runs this in the main tree.
# list.txt (root|path|before sha256|after sha256; "null" = absent) names four files:
#   repo  governance/project/operator/landing_check.py        the source copy of the install's file (byte-equal to it)
#   repo  tests/unit/operator/test_landing_cto_route.py       the unit tests (new)
#   home  gov-os-operator/install/landing_check.py            the landing check itself
#   home  gov-os-operator/install/APPROVED                    its one line (landing_check.py's sha256)
# Run in the main tree (the repository is its cwd; $HOME is the install's), then the owner's commit of the two repository
# paths (Role: owner; the commit changes no tests/acceptance path). Nothing is committed by this script.
#   check   every listed file is the "before" (exit 3 "moved: ..." otherwise); every other install file as built
#           (keep.txt); the source copy equals the install's file; the operator holds nothing (exit 6 when it is busy)
#   apply   only over the "before" (a file already "after" is left; a file that is neither: exit 3, nothing touched): the
#           repository files first, the install's landing_check.py, APPROVED last, under log/launch.lock, then the
#           install's own APPROVED check
#   undo    the "before" put back, the same order, only over the "after" (a file already "before" is left; neither: exit 3)
#   verify  every listed file is the "after", the install's other files as built, the install's own APPROVED check ok
# The frozen copies (before/<root>/<path>, after/<root>/<path>) are hashed against list.txt before any step (exit 4
# otherwise). Every write goes through a mktemp file in the same folder and a rename (no fixed temporary name).
set -u
B="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$PWD"
OP="$HOME/gov-os-operator"
INST="$OP/install"
step="${1:-}"
case "$step" in check|apply|undo|verify) ;; *) echo "usage: apply.sh check|apply|undo|verify" >&2; exit 2 ;; esac

h() { if [ -f "$1" ] && [ ! -L "$1" ]; then sha256sum "$1" | cut -c1-64; else echo null; fi; }
target() { case "$1" in home) echo "$HOME/$2" ;; repo) echo "$ROOT/$2" ;; *) echo "not a root: $1" >&2; exit 9 ;; esac; }

[ -d "$ROOT/.git" ] || { echo "not a repository root: run it in the main tree" >&2; exit 2; }

# 1. the frozen copies hash as listed
while IFS='|' read -r root path before after; do
  [ -z "$root" ] && continue
  for side in before after; do
    want=$before; [ "$side" = after ] && want=$after
    [ "$want" = null ] && continue
    [ "$(h "$B/$side/$root/$path")" = "$want" ] || { echo "the frozen copy does not hash as listed: $side/$root/$path" >&2; exit 4; }
  done
done < "$B/list.txt"

# the state of each listed file: b (before), a (after) or x (neither)
nb=0; na=0; nx=0; n=0
while IFS='|' read -r root path before after; do
  [ -z "$root" ] && continue
  n=$((n+1)); now="$(h "$(target "$root" "$path")")"
  if [ "$now" = "$before" ]; then nb=$((nb+1)); elif [ "$now" = "$after" ]; then na=$((na+1)); else
    nx=$((nx+1)); echo "moved: $root/$path (neither the before nor the after)" >&2; fi
done < "$B/list.txt"

keep_ok() {  # every other install file as built, no stray file in install/
  [ -d "$INST" ] && [ ! -L "$INST" ] || { echo "moved: the install folder" >&2; return 1; }
  local s f extra rc=0
  while read -r s f; do
    [ -z "$s" ] && continue
    [ "$(h "$INST/$f")" = "$s" ] || { echo "moved: install/$f (not as built)" >&2; rc=1; }
  done < "$B/keep.txt"
  extra=$( cd "$INST" && find . -path ./__pycache__ -prune -o \( -type f -o -type l \) -print | sed 's#^\./##' \
    | grep -vxF -e APPROVED -e landing_check.py -e act-in-progress.txt \
    | while read -r f; do grep -q "  $f\$" "$B/keep.txt" || echo "$f"; done )
  [ -z "$extra" ] || { echo "moved: a file in install/ that is not listed: $extra" >&2; rc=1; }
  return $rc
}
idle_ok() {  # the operator holds nothing and nothing waits
  [ ! -e "$INST/act-in-progress.txt" ] || { echo "busy: the operator's freeze is held (install/act-in-progress.txt): a run is applying" >&2; return 1; }
  [ ! -e "$OP/log/journal.json" ] || { echo "busy: the operator's journal exists (log/journal.json): a run is unfinished" >&2; return 1; }
  [ ! -e "$OP/log/operator.lock" ] || { echo "busy: the operator's lock is held (log/operator.lock): an undo failed" >&2; return 1; }
  local q; q="$(find "$OP/queue" -maxdepth 1 -name '*.req' 2>/dev/null | head -1)"
  [ -z "$q" ] || { echo "busy: a request waits in queue/ ($(basename "$q")): let it run first" >&2; return 1; }
  return 0
}
mirror_ok() {  # the source copy is the install's file, on whichever side both stand
  [ "$(h "$ROOT/governance/project/operator/landing_check.py")" = "$(h "$INST/landing_check.py")" ] \
    || { echo "moved: the source copy governance/project/operator/landing_check.py differs from the install's landing_check.py" >&2; return 1; }
}
repo_clean() {  # the listed repository paths have no change that is not committed (the owner's commit takes only the ACT's)
  local p st
  while IFS='|' read -r root path before after; do
    [ "$root" = repo ] || continue
    st="$(git -C "$ROOT" status --porcelain --untracked-files=all -- "$path")"
    [ -z "$st" ] || { echo "moved: $path has a change that is not committed or is untracked ($st)" >&2; return 1; }
  done < "$B/list.txt"
}
own_check() {  # the install's own APPROVED check (python -I -B: it writes no __pycache__)
  ( cd "$INST" && python3 -I -B -c 'import sys; sys.path.insert(0, "."); import opcommon as oc; r = oc.approved_state("."); print("the install'"'"'s own APPROVED check:", "ok" if r[0] else r[2]); sys.exit(0 if r[0] else 1)' )
}
put() {  # $1 source, $2 destination, $3 root: a mktemp file beside it, mode set, renamed over it
  local src="$1" dst="$2" tmp mode
  if [ "$3" = home ]; then mode=0444; elif [ -f "$dst" ]; then mode="$(stat -c %a "$dst")"; else mode=0644; fi
  mkdir -p "$(dirname "$dst")" || return 1
  tmp="$(mktemp "$(dirname "$dst")/.$(basename "$dst").act-landing-cto-route-1.XXXXXX")" || return 1
  cat "$src" > "$tmp" || { rm -f "$tmp"; return 1; }
  chmod "$mode" "$tmp" && mv -f "$tmp" "$dst" || { rm -f "$tmp"; return 1; }
}
swap() {  # $1 apply|undo: every listed file to the wanted side, in list order (APPROVED is last), under the launch lock
  local to="$1" root path before after want other src dst now
  mkdir -p "$OP/log"
  exec 9>>"$OP/log/launch.lock"
  flock -n 9 || { echo "busy: a launch is running (log/launch.lock is held); nothing changed" >&2; exit 6; }
  while IFS='|' read -r root path before after; do
    [ -z "$root" ] && continue
    if [ "$to" = apply ]; then want=$after; other=$before; src="$B/after/$root/$path"; else want=$before; other=$after; src="$B/before/$root/$path"; fi
    dst="$(target "$root" "$path")"; now="$(h "$dst")"
    if [ "$now" = "$want" ]; then echo "already in place: $root/$path"; continue; fi
    [ "$now" = "$other" ] || { echo "moved: $root/$path changed while the swap ran; stopped (the files before it are done: run '$0 check' and send the output to the CTO)" >&2; exit 3; }
    if [ "$want" = null ]; then rm -f "$dst" || exit 5; else put "$src" "$dst" "$root" || { echo "could not write $dst; stopped" >&2; exit 5; }; fi
    echo "$to: $root/$path"
  done < "$B/list.txt"
}

case "$step" in
  check)
    [ "$nx" = 0 ] || exit 3
    if [ "$na" = "$n" ]; then echo "already applied (every listed file is the after): nothing to apply" >&2; exit 3; fi
    [ "$nb" = "$n" ] || { echo "moved: the listed files are partly before, partly after (a half-applied state); run apply or undo to finish it" >&2; exit 3; }
    keep_ok || exit 3
    mirror_ok || exit 3
    repo_clean || exit 3
    idle_ok || exit 6
    echo "check: ready to apply (every listed file is the before; the install's other files as built; the operator holds nothing)" ;;
  apply)
    [ "$nx" = 0 ] || { echo "apply refused, nothing touched" >&2; exit 3; }
    [ "$na" = "$n" ] && { echo "already in place: every listed file is the after (apply: nothing to do)"; exit 0; }
    keep_ok || { echo "apply refused, nothing touched" >&2; exit 3; }
    mirror_ok || { echo "apply refused, nothing touched" >&2; exit 3; }
    repo_clean || { echo "apply refused, nothing touched" >&2; exit 3; }
    idle_ok || { echo "apply refused, nothing touched" >&2; exit 6; }
    swap apply
    own_check || { echo "the install's own APPROVED check failed after the swap: run '$0 undo' and send the output to the CTO" >&2; exit 5; }
    echo "APPROVED $(h "$INST/APPROVED")"
    echo "state applied" ;;
  undo)
    [ "$nx" = 0 ] || { echo "undo refused, nothing touched" >&2; exit 3; }
    [ "$nb" = "$n" ] && { echo "already in place: every listed file is the before (undo: nothing to do)"; exit 0; }
    keep_ok || { echo "undo refused, nothing touched" >&2; exit 3; }
    idle_ok || { echo "undo refused, nothing touched" >&2; exit 6; }
    swap undo
    own_check || { echo "the install's own APPROVED check failed after the undo: send the output to the CTO" >&2; exit 5; }
    echo "APPROVED $(h "$INST/APPROVED")"
    echo "state before (undone)" ;;
  verify)
    [ "$nx" = 0 ] || exit 3
    [ "$na" = "$n" ] || { echo "not applied: $nb of $n listed files are still the before" >&2; exit 3; }
    keep_ok || exit 3
    mirror_ok || exit 3
    own_check || exit 5
    echo "verify: every listed file is the after; the install's other files as built" ;;
esac
exit 0
