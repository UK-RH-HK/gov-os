#!/usr/bin/env bash
# ACT-OPERATOR-ROUNDS-1 (DEC-1131 (3)): READY needs no KPI line marked fail (verdict.py); the two-round cap counts per ACT id
# (operator_run.py, G4). Class (O): the operator's own files, applied by the owner by hand. Rehearsed (DEC-1057).
#   bash apply.sh check   the state; changes nothing
#   bash apply.sh apply   checks first; backups (sha256s); the repository files, then the install, APPROVED last
#   bash apply.sh undo    checks first; every file back byte for byte, APPROVED last
# What changes (nothing else on the machine, nothing committed by this script):
#  1. In the main tree (the working copy of w2/integrate, for the owner's commit):
#       governance/project/operator/verdict.py            277c8ca9f06c... -> 30214f3de29d...
#       governance/project/operator/operator_run.py       fe2e2f424616... -> 334e7a032322...
#       tests/unit/operator/test_w2_148_parts.py           051eec8a3f22... -> bca1d3c5e0e2...  (the pinned verdict.py hash)
#       tests/acceptance/W2-148/w2_148_support.py          b4302cf7aea3... -> 247996d86290...  (the same pin, S4's test)
#       tests/unit/operator/test_dec1131_rounds.py         (new)          -> 0268f5ea43a5...   (the new cases, 13)
#  2. In $HOME/gov-os-operator/install/ (the operator's hashed copies):
#       verdict.py        277c8ca9f06c... -> 30214f3de29d...
#       operator_run.py   fe2e2f424616... -> 334e7a032322...
#       APPROVED          b4a15c8f3b7c... -> (printed by apply; the two lines above change, sha256sum's form)
# Every other install file is checked unchanged. It refuses while the operator holds a run (the freeze, the journal, the lock
# of a failed undo, a launch running) or a request waits in queue/. It writes only the five repository paths above, the
# install's two files and APPROVED, and this folder's backup/. It commits nothing.
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT=$(cd "$HERE/../../../../.." && pwd)
cmd=${1:-}
OP=$HOME/gov-os-operator
INST=$OP/install
BACKUP=$HERE/backup

# The hashes as built (2026-11-11, w2/integrate at df30e3dfd; the install as ACT-OPERATOR-2 left it)
OLD_VERDICT=277c8ca9f06c90906397579f4d5bd144fb506a40b0836eb2a8f9c1443d909378
NEW_VERDICT=30214f3de29dacdf9bb443371c05a4392e8da3c305aeb9b7845b9a433d5cf4a5
OLD_RUN=fe2e2f424616b9083f371fd3e611a91ff9488c2c9d24513b61200cb7beeb4ac2
NEW_RUN=334e7a032322e154e3570e2c945c6c9e90814a8b4e7cb2dd65fa3959583e7879
LIVE_APPROVED_BEFORE=b4a15c8f3b7c769259f25b8d71406e6c7d387d30c021343f26f4bad6e3831fa4
# The repository files: path, before (none = absent), after
REPO="governance/project/operator/verdict.py $OLD_VERDICT $NEW_VERDICT
governance/project/operator/operator_run.py $OLD_RUN $NEW_RUN
tests/unit/operator/test_w2_148_parts.py 051eec8a3f22fa130d71322afdba805c328c9f998af54dff6e336446b1ebee16 bca1d3c5e0e233d55295ae0d2a8574eddf3dd569954ea1691fee4ab4433f6ad6
tests/acceptance/W2-148/w2_148_support.py b4302cf7aea3d274f928e2c1d9bab977b816da6ffbd6eead8a99579960af2208 247996d8629072c29238df1d3c96c87c226176d3ec8b063c79f4b83831415bbc
tests/unit/operator/test_dec1131_rounds.py none 0268f5ea43a52d892979da468b839f26ed3f5e983370e849304570033f08157c"
# The install's other files, unchanged by this ACT (ACT-OPERATOR-2's APPROVED less the two code files)
KEEP="c8ce4308aaf7a94975ea872d8eb4cb7bd045ef6415dc5e8c9f286cc63bbcc523  act_class.py
51c459cfbcfec47652df455844480a56a5bc91b5fba3bcf57dc807c5dbf08cc2  brief.md
0f130073bbbd06f7b56c7be44e72d42ffe6460bc49f4c6a684f81f499979bab1  class-rules.yaml
00e8ce13249e427626765b1c53b54811815276d6fbed4c8dd55c238c29c4122a  freeze_gate.py
a0687ebde2365fb2d7b1b63a50cef2c3da94f2d56a4a01eede287e7d9f5afd32  landing_check.py
e392d8a0e177e999f5361243a053e386f5fccc0619dec7d5e8c832cd756a1024  opcommon.py
5a347f36513630dc7c990160d51bb75c81fa5ada7b7c773dd3e08ddc57fe1536  operator-settings.json
5bdcfc9bbc9c9707dab7a217a0c4ed6f561c76fcf4d2c1049853a4fd342fbf69  operator_launch.py
e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a  reviewer-brief.md
d1f7b23c1c2dd8f7390f4be97508a7e5ac222729a332634199a8bd17230b02da  wall/operator_wall_hook.py
09fcd4239da357c0d0bb54cb95f64968458d550541ba55841c5dcb63736f0cf6  wall/settings.json.tmpl
ae191d76a7d9ceeeccfcd54ed03b2ce7104840d99e682713a38e014f515b2ee2  win_toast.ps1"
die() { echo "apply.sh: $*" >&2; exit 1; }
sha() { if [ -f "$1" ] && [ ! -L "$1" ]; then sha256sum "$1" | cut -c1-64; else echo none; fi; }

# APPROVED's bytes for a state: KEEP plus the two changing files, sha256sum's form (C order)
approved_text() {  # $1 verdict sha, $2 run sha
  { printf '%s\n' "$KEEP"; printf '%s  verdict.py\n%s  operator_run.py\n' "$1" "$2"; } | LC_ALL=C sort -k2
}
approved_sha() { approved_text "$@" | sha256sum | cut -c1-64; }

drafts_ok() {
  [ "$(sha "$HERE/code/governance/project/operator/verdict.py")" = "$NEW_VERDICT" ] || { echo "the draft code verdict.py is not as built"; return 1; }
  [ "$(sha "$HERE/code/governance/project/operator/operator_run.py")" = "$NEW_RUN" ] || { echo "the draft code operator_run.py is not as built"; return 1; }
  local p b a
  while read -r p b a; do
    [ "$(sha "$HERE/code/$p")" = "$a" ] || { echo "the draft code/$p is not as built"; return 1; }
  done <<< "$REPO"
  [ "$(approved_sha "$OLD_VERDICT" "$OLD_RUN")" = "$LIVE_APPROVED_BEFORE" ] || { echo "APPROVED as computed (before) is not as built"; return 1; }
  return 0
}

# The repository files' state: before, applied or other (a mix, or a file moved since the build)
repo_state() {
  local p b a h nb=0 na=0 n=0
  while read -r p b a; do
    n=$((n+1)); h=$(sha "$ROOT/$p")
    [ "$h" = "$b" ] && nb=$((nb+1))
    [ "$h" = "$a" ] && na=$((na+1))
  done <<< "$REPO"
  if [ "$nb" = "$n" ]; then echo before; elif [ "$na" = "$n" ]; then echo applied; else echo other; fi
}

# The install's state: before (as ACT-OPERATOR-2 left it), applied (as this ACT leaves it), or other (anything else)
inst_state() {
  [ -d "$INST" ] && [ ! -L "$INST" ] || { echo other; return; }
  local f s
  while read -r s f; do
    [ "$(sha "$INST/$f")" = "$s" ] || { echo other; return; }
  done <<< "$KEEP"
  local extra; extra=$( cd "$INST" && find . -path ./__pycache__ -prune -o \( -type f -o -type l \) -print | sed 's#^\./##' \
    | grep -vxF -e APPROVED -e verdict.py -e operator_run.py -e act-in-progress.txt \
    | while read -r f; do printf '%s\n' "$KEEP" | grep -q "  $f\$" || echo "$f"; done )
  [ -z "$extra" ] || { echo other; return; }
  local v r ap
  v=$(sha "$INST/verdict.py"); r=$(sha "$INST/operator_run.py"); ap=$(sha "$INST/APPROVED")
  if [ "$v" = "$OLD_VERDICT" ] && [ "$r" = "$OLD_RUN" ] && [ "$ap" = "$(approved_sha "$OLD_VERDICT" "$OLD_RUN")" ]; then
    echo before
  elif [ "$v" = "$NEW_VERDICT" ] && [ "$r" = "$NEW_RUN" ] && [ "$ap" = "$(approved_sha "$NEW_VERDICT" "$NEW_RUN")" ]; then
    echo applied
  else
    echo other
  fi
}

state() {  # before only when both are, applied only when both are
  local r i; r=$(repo_state); i=$(inst_state)
  if [ "$r" = before ] && [ "$i" = before ]; then echo before
  elif [ "$r" = applied ] && [ "$i" = applied ]; then echo applied
  else echo "other (repository $r, install $i)"; fi
}

idle_or_die() {  # the operator holds nothing, and nothing waits to be launched
  [ ! -e "$INST/act-in-progress.txt" ] || die "the operator's freeze is held (install/act-in-progress.txt): a run is applying; nothing changed"
  [ ! -e "$OP/log/journal.json" ] || die "the operator's journal exists (log/journal.json): a run is unfinished; nothing changed"
  [ ! -e "$OP/log/operator.lock" ] || die "the operator's lock is held (log/operator.lock): an undo failed, the owner's to clear; nothing changed"
  local q; q=$(find "$OP/queue" -maxdepth 1 -name '*.req' 2>/dev/null | head -1)
  [ -z "$q" ] || die "a request waits in queue/ ($(basename "$q")): let it run first; nothing changed"
}

put() {  # $1 source file, $2 install name: a new file beside it, 0444, then renamed over it
  local tmp="$INST/.$(basename "$2").act-operator-rounds-1.$$"
  rm -f "$tmp"; cat "$1" > "$tmp"; chmod 0444 "$tmp"; mv -f "$tmp" "$INST/$2"
}
put_repo() {  # $1 source file, $2 path under the main tree: written beside, then renamed over (the file's mode kept)
  local dst="$ROOT/$2" tmp mode
  tmp="$(dirname "$dst")/.$(basename "$dst").act-operator-rounds-1.$$"
  mode=$([ -f "$dst" ] && stat -c %a "$dst" || echo 644)
  rm -f "$tmp"; cat "$1" > "$tmp"; chmod "$mode" "$tmp"; mv -f "$tmp" "$dst"
}

case "$cmd" in
  check)
    drafts_ok || die "nothing changed"
    s=$(state)
    echo "state: $s (install APPROVED $(sha "$INST/APPROVED" | cut -c1-12))"
    case "$s" in
      before) idle_or_die; echo "check: ready to apply" ;;
      applied) echo "check: already applied" ;;
      *) die "the repository and the install are neither as built before nor as this ACT leaves them: the CTO rebuilds; nothing changed" ;;
    esac ;;
  apply)
    drafts_ok || die "nothing changed"
    [ "$(state)" = before ] || die "not in the before state ($(state)); nothing changed"
    idle_or_die
    mkdir -p "$OP/log"
    exec 9>>"$OP/log/launch.lock"
    flock -n 9 || die "a launch is running (log/launch.lock is held); nothing changed"
    [ ! -e "$BACKUP" ] || die "$BACKUP exists: a backup from an earlier apply; the CTO looks first; nothing changed"
    mkdir -p "$BACKUP/install" "$BACKUP/repo"
    for f in verdict.py operator_run.py APPROVED; do cp -p "$INST/$f" "$BACKUP/install/$f"; done
    while read -r p b a; do
      if [ "$b" != none ]; then mkdir -p "$BACKUP/repo/$(dirname "$p")"; cp -p "$ROOT/$p" "$BACKUP/repo/$p"; fi
    done <<< "$REPO"
    ( cd "$BACKUP" && find install repo -type f | LC_ALL=C sort | xargs sha256sum > SHA256SUMS )
    # 1. the repository files (the source; the operator reads none of them)
    while read -r p b a; do put_repo "$HERE/code/$p" "$p"; done <<< "$REPO"
    [ "$(repo_state)" = applied ] || die "after the repository step the files are $(repo_state): run 'bash apply.sh undo'"
    # 2. the install: the two code files, then APPROVED last, under the launch lock taken above
    put "$HERE/code/governance/project/operator/verdict.py" verdict.py
    put "$HERE/code/governance/project/operator/operator_run.py" operator_run.py
    tmpa="$BACKUP/APPROVED.new"
    approved_text "$NEW_VERDICT" "$NEW_RUN" > "$tmpa"
    put "$tmpa" APPROVED; rm -f "$tmpa"
    [ "$(inst_state)" = applied ] || die "after the swap the install is $(inst_state): run 'bash apply.sh undo'"
    ( cd "$INST" && python3 -I -c 'import sys; sys.path.insert(0, "."); import opcommon as oc; r = oc.approved_state("."); print("the install'"'"'s own APPROVED check:", "ok" if r[0] else r[2]); sys.exit(0 if r[0] else 1)' ) \
      || die "the install's own APPROVED check failed: run 'bash apply.sh undo'"
    echo "APPROVED $(sha "$INST/APPROVED")"
    echo "state applied" ;;
  undo)
    [ "$(state)" = applied ] || die "not as this ACT left it ($(state)); nothing changed"
    idle_or_die
    [ -f "$BACKUP/SHA256SUMS" ] || die "no backup in $BACKUP; nothing changed"
    ( cd "$BACKUP" && sha256sum -c --quiet SHA256SUMS ) || die "the backup does not match its SHA256SUMS; nothing changed"
    [ "$(sha "$BACKUP/install/verdict.py")" = "$OLD_VERDICT" ] && [ "$(sha "$BACKUP/install/operator_run.py")" = "$OLD_RUN" ] \
      && [ "$(sha "$BACKUP/install/APPROVED")" = "$LIVE_APPROVED_BEFORE" ] \
      || die "the backup is not the before state; nothing changed"
    exec 9>>"$OP/log/launch.lock"
    flock -n 9 || die "a launch is running (log/launch.lock is held); nothing changed"
    put "$BACKUP/install/verdict.py" verdict.py
    put "$BACKUP/install/operator_run.py" operator_run.py
    put "$BACKUP/install/APPROVED" APPROVED
    while read -r p b a; do
      if [ "$b" = none ]; then rm -f "$ROOT/$p"; else put_repo "$BACKUP/repo/$p" "$p"; fi
    done <<< "$REPO"
    [ "$(state)" = before ] || die "after the undo the state is $(state)"
    mv "$BACKUP" "$BACKUP.undone-$(date -u +%Y%m%dT%H%M%SZ)"
    echo "APPROVED $(sha "$INST/APPROVED")"
    echo "state before (undone)" ;;
  *) echo "usage: bash apply.sh check|apply|undo" >&2; exit 2 ;;
esac
