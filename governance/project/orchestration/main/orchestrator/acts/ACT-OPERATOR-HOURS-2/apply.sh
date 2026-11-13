#!/bin/bash
# ACT-OPERATOR-HOURS-2 (DEC-1141 (6)): G9 of the operator agent holds only while the night hold is on. Class (O): the operator's
# own install, applied by the owner by hand (or by the owner's operator). Two stages, two commits (DEC-1136 (2): an ACT whose commit
# changes a file under tests/acceptance/ carries its own acceptance_exemptions entry, by a second Role: owner commit straight after
# the first, listing the first's full id):
#   stage 1  check | apply | undo | verify, then the owner's commit of the four repository paths (the package's section 0)
#   stage 2  exempt | exempt-verify | exempt-undo, after that commit (see the end of this header)
# Stage 1 is decided by sha256 state over the files in list.txt (root|path|before sha256|after sha256; "null" = absent):
#   root home  = $HOME/<path>   (the operator's install: gov-os-operator/install/opcommon.py and its APPROVED)
#   root repo  = <main tree>/<path>   (the source the install is copied from, and its tests; for the owner's commit)
# The frozen copies are in this folder (before/<root>/<path>, after/<root>/<path>); each is hashed against list.txt before it is
# used (exit 4 otherwise). Nothing else on the machine is touched, nothing is committed.
#   check   every listed file is the "before", every other install file is as built (keep.txt), the operator holds nothing
#           (exit 3 "moved: ..." otherwise; exit 6 when the operator is busy)
#   apply   only over the "before" (a file already "after" is left; a file that is neither: exit 3, nothing touched); the repository
#           files first, the install's opcommon.py, APPROVED last, all under log/launch.lock; then the install's own APPROVED check
#   undo    the "before" put back, the same order, only over the "after" (a file already "before" is left; neither: exit 3)
#   verify  every listed file is the "after", the install's other files as built, the install's own APPROVED check ok (exit 3 otherwise)
# Stage 2 (the path map's after bytes hold the first commit's id, so they cannot be frozen; the code is here, the rule is a hash):
#   exempt         HEAD must be the ACT's own commit: one parent, subject starting "ACT-OPERATOR-HOURS-2:", trailer Role: owner, exactly
#                  the four repository paths of list.txt changed, each blob the listed after. The path map must be unmodified at HEAD and
#                  hash as one of the two ALLOWED_BEFORES (the live map; the map ACT-EXAMIN-SETS-1, ACT-ACCEPTED-REDS-1 and ACT-PATHMAP-EXP-1
#                  leave). It adds, after the last entry of acceptance_exemptions (before the comment line that opens the next block), the
#                  two lines `  - commit: "<HEAD's full id>"` and `    decision: DEC-1141  # ...`, by mktemp and rename, the mode kept,
#                  and runs exempt-verify. Run again (the map already holds the entry): no change, exit 0. After the second commit
#                  (HEAD is the exemption commit): no change, exit 0 when the committed map checks. Anything else: exit 3, nothing touched.
#   exempt-verify  read only: the map is an allowed before plus exactly those two lines at that place (removing them gives an allowed
#                  before, and inserting them there again gives the map byte for byte); after the second commit also the committed map
#   exempt-undo    before the second commit only: the two lines taken out (the map is then the allowed before again)
# This script does not commit. Every write goes through a mktemp file in the same folder and a rename (no fixed temporary name).
set -u
B="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$B/../../../../.." && pwd)"
OP="$HOME/gov-os-operator"
INST="$OP/install"
step="${1:-}"
case "$step" in check|apply|undo|verify|exempt|exempt-verify|exempt-undo) ;; *) echo "usage: apply.sh check|apply|undo|verify|exempt|exempt-verify|exempt-undo" >&2; exit 2 ;; esac

h() { if [ -f "$1" ] && [ ! -L "$1" ]; then sha256sum "$1" | cut -c1-64; else echo null; fi; }
target() { case "$1" in home) echo "$HOME/$2" ;; repo) echo "$ROOT/$2" ;; *) echo "not a root: $1" >&2; exit 9 ;; esac; }

# ----------------------------------------------------------------------------------------------------- stage 2 (DEC-1136 (2))
MAPREL="governance/project/path-map.yaml"
MAP="$ROOT/$MAPREL"
ANCHOR='# gov close of this project (DEC-549, DEC-554)'   # the comment line that opens the block after acceptance_exemptions
ALLOWED_BEFORES="f4029cfb49428708a7c7f9ca754bcd50a1c610ccc22966d09c4c581f1abbd971 the live map (the map with ACT-W1-01-EXEMPT-3's entry)
d50884e3633e6e778626a17a0cae62f37778ff7f1903b2a557ad7920e9bbbb4d the map ACT-EXAMIN-SETS-1, ACT-ACCEPTED-REDS-1 and ACT-PATHMAP-EXP-1 leave, in that order"
g() { git -C "$ROOT" "$@"; }
ex_refuse() { echo "$step refused: $*; nothing touched" >&2; exit 3; }
ex_lines() { printf '  - commit: "%s"\n    decision: DEC-1141  # ACT-OPERATOR-HOURS-2'"'"'s commit (DEC-1136 (2))\n' "$1"; }
ex_insert() {  # $1 map file, $2 commit id: the map with the entry before the anchor line (the anchor once, a decision line before it)
  ENTRY="$(ex_lines "$2")" A="$ANCHOR" awk '
    index($0, ENVIRON["A"]) == 1 { n++; if (prev !~ /^    decision: /) bad = 1; print ENVIRON["ENTRY"] }
    { print; prev = $0 }
    END { exit (n == 1 && !bad) ? 0 : 1 }' "$1"
}
ex_remove() {  # $1 map file, $2 commit id: the map without the entry's two lines, which must be there once, one after the other
  ENTRY="$(ex_lines "$2")" awk '
    BEGIN { split(ENVIRON["ENTRY"], e, "\n") }
    hold { hold = 0; if ($0 == e[2]) { n++; next } print e[1] }
    $0 == e[1] { hold = 1; next }
    { print }
    END { if (hold) print e[1]; exit (n == 1) ? 0 : 1 }' "$1"
}
is_allowed_before() { printf '%s\n' "$ALLOWED_BEFORES" | cut -d' ' -f1 | grep -qx -- "$1"; }
is_hours2_commit() {  # $1 rev: the ACT's own commit (sets why)
  local rev="$1" want got root path before after
  g rev-parse --verify -q "$rev^{commit}" > /dev/null || { why="there is no commit $rev"; return 1; }
  [ "$(g rev-list --parents -n 1 "$rev" | wc -w)" = 2 ] || { why="$rev has no parent or has two"; return 1; }
  case "$(g log -1 --format=%s "$rev")" in ACT-OPERATOR-HOURS-2:*) ;; *) why="its subject does not start with ACT-OPERATOR-HOURS-2:"; return 1 ;; esac
  [ "$(g log -1 --format='%(trailers:key=Role,valueonly,unfold)' "$rev")" = owner ] || { why="it has no single trailer Role: owner"; return 1; }
  want="$(awk -F'|' '$1 == "repo" { print $2 }' "$B/list.txt" | LC_ALL=C sort)"
  got="$(g diff-tree --no-commit-id --name-only -r "$rev" | LC_ALL=C sort)"
  [ "$got" = "$want" ] || { why="it does not change exactly the ACT's repository paths"; return 1; }
  while IFS='|' read -r root path before after; do
    [ "$root" = repo ] || continue
    [ "$(g cat-file blob "$rev:$path" 2> /dev/null | sha256sum | cut -c1-64)" = "$after" ] || { why="its $path is not the ACT's after file"; return 1; }
  done < "$B/list.txt"
  return 0
}
ex_target() {  # sets EXID and EXMODE: pre (HEAD is the ACT's commit) or post (HEAD is the exemption commit, HEAD~1 the ACT's)
  local why="" first
  if is_hours2_commit HEAD; then EXID="$(g rev-parse HEAD)"; EXMODE=pre; return 0; fi
  first="$why"
  if g rev-parse --verify -q 'HEAD~1^{commit}' > /dev/null && is_hours2_commit HEAD~1 \
     && [ "$(g rev-list --parents -n 1 HEAD | wc -w)" = 2 ] \
     && [ "$(g log -1 --format='%(trailers:key=Role,valueonly,unfold)' HEAD)" = owner ] \
     && [ "$(g diff-tree --no-commit-id --name-only -r HEAD)" = "$MAPREL" ]; then
    EXID="$(g rev-parse 'HEAD~1')"; EXMODE=post; return 0
  fi
  ex_refuse "HEAD is not the ACT's commit ($first), nor a commit that only adds its exemption"
}
ex_verify() {  # the map is an allowed before plus exactly the entry's two lines at that place (0, or 1 with the reason on stderr)
  local bsha
  [ -f "$MAP" ] && [ ! -L "$MAP" ] || { echo "$MAPREL is missing or a link" >&2; return 1; }
  ex_remove "$MAP" "$EXID" > /dev/null || { echo "the map does not hold the entry for ${EXID:0:12} exactly once" >&2; return 1; }
  bsha="$(ex_remove "$MAP" "$EXID" | sha256sum | cut -c1-64)"
  is_allowed_before "$bsha" || { echo "without the entry the map is not an allowed before (sha256 ${bsha:0:12})" >&2; return 1; }
  cmp -s "$MAP" <(ex_insert <(ex_remove "$MAP" "$EXID") "$EXID") || { echo "the entry is not at the end of acceptance_exemptions, or the map differs elsewhere" >&2; return 1; }
  if [ "$EXMODE" = post ]; then
    [ -z "$(g status --porcelain --untracked-files=no -- "$MAPREL")" ] || { echo "the map is not as committed" >&2; return 1; }
    g show "HEAD:$MAPREL" | cmp -s - "$MAP" || { echo "the committed map is not this map" >&2; return 1; }
  fi
  echo "exempt-verify: the map is the allowed before (sha256 ${bsha:0:12}) plus exactly the entry for ${EXID:0:12}, at the end of acceptance_exemptions"
}
ex_write() {  # $1 the new content's producing command (a function name), $2 commit id: replace the map by it, mode kept
  local tmp mode
  mode="$(stat -c %a "$MAP")" || return 1
  tmp="$(mktemp "$(dirname "$MAP")/.$(basename "$MAP").act-operator-hours-2.XXXXXX")" || return 1
  if "$1" "$MAP" "$2" > "$tmp" && chmod "$mode" "$tmp" && mv -f "$tmp" "$MAP"; then return 0; fi
  rm -f "$tmp"; return 1
}
ex_clean() { [ -z "$(g status --porcelain --untracked-files=no -- "$MAPREL")" ]; }

case "$step" in
  exempt|exempt-verify|exempt-undo)
    ex_target
    [ -f "$MAP" ] && [ ! -L "$MAP" ] || ex_refuse "$MAPREL is missing or a link"
    case "$step" in
      exempt-verify) ex_verify || exit 3; exit 0 ;;
      exempt)
        if [ "$EXMODE" = post ]; then ex_verify || exit 3; echo "already in place: HEAD is the exemption commit (exempt: nothing to do)"; exit 0; fi
        if ex_verify > /dev/null 2>&1; then echo "already in place: the map lists ${EXID:0:12} (exempt: nothing to do)"; exit 0; fi
        now="$(h "$MAP")"
        is_allowed_before "$now" || ex_refuse "$MAPREL is neither allowed before (sha256 ${now:0:12}): ACT-EXAMIN-SETS-1, ACT-ACCEPTED-REDS-1 and ACT-PATHMAP-EXP-1 are applied BEFORE this ACT's commit, or all three are not; another change moved the map"
        ex_clean || ex_refuse "$MAPREL has changes that are not committed"
        ex_write ex_insert "$EXID" || { echo "exempt: could not write $MAPREL; nothing changed (exit 5)" >&2; exit 5; }
        echo "exempt: added the entry for ${EXID:0:12}"
        ex_verify || { echo "exempt: the result does not verify: run '$0 exempt-undo' and send the output to the CTO" >&2; exit 5; }
        exit 0 ;;
      exempt-undo)
        [ "$EXMODE" = pre ] || ex_refuse "the exemption is committed (HEAD is the exemption commit): see the package's undo"
        if ex_remove "$MAP" "$EXID" > /dev/null; then
          ex_verify > /dev/null 2>&1 || ex_refuse "$MAPREL is not an allowed before plus exactly the entry"
          ex_write ex_remove "$EXID" || { echo "exempt-undo: could not write $MAPREL; nothing changed (exit 5)" >&2; exit 5; }
          echo "exempt-undo: took the entry for ${EXID:0:12} out"; exit 0
        fi
        is_allowed_before "$(h "$MAP")" || ex_refuse "$MAPREL is neither an allowed before nor one plus the entry"
        echo "already in place: the map has no entry for ${EXID:0:12} (exempt-undo: nothing to do)"; exit 0 ;;
    esac ;;
esac

# 1. the frozen copies hash as listed
while IFS='|' read -r root path before after; do
  [ -z "$root" ] && continue
  for side in before after; do
    want=$before; [ "$side" = after ] && want=$after
    [ "$want" = null ] && continue
    [ "$(h "$B/$side/$root/$path")" = "$want" ] || { echo "the frozen copy does not hash as listed: $side/$root/$path" >&2; exit 4; }
  done
done < "$B/list.txt"

# 2. the state of each listed file: b (before), a (after) or x (neither)
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
    | grep -vxF -e APPROVED -e opcommon.py -e act-in-progress.txt \
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
own_check() {  # the install's own APPROVED check (python -I -B: it writes no __pycache__)
  ( cd "$INST" && python3 -I -B -c 'import sys; sys.path.insert(0, "."); import opcommon as oc; r = oc.approved_state("."); print("the install'"'"'s own APPROVED check:", "ok" if r[0] else r[2]); sys.exit(0 if r[0] else 1)' )
}
put() {  # $1 source, $2 destination: a mktemp file beside it, mode set, renamed over it
  local src="$1" dst="$2" tmp mode
  if [ "$3" = home ]; then mode=0444; elif [ -f "$dst" ]; then mode="$(stat -c %a "$dst")"; else mode=0644; fi
  mkdir -p "$(dirname "$dst")" || return 1
  tmp="$(mktemp "$(dirname "$dst")/.$(basename "$dst").act-operator-hours-2.XXXXXX")" || return 1
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
    idle_ok || exit 6
    echo "check: ready to apply (every listed file is the before; the install's other files as built; the operator holds nothing)" ;;
  apply)
    [ "$nx" = 0 ] || { echo "apply refused, nothing touched" >&2; exit 3; }
    [ "$na" = "$n" ] && { echo "already in place: every listed file is the after (apply: nothing to do)"; exit 0; }
    keep_ok || { echo "apply refused, nothing touched" >&2; exit 3; }
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
    own_check || exit 5
    echo "verify: every listed file is the after; the install's other files as built" ;;
esac
exit 0
