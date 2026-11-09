#!/usr/bin/env bash
# ACT-OPERATOR-2 (DEC-1104 (2), DEC-1108 (2)): the operator agent re-installed to carry W2-148's replay check
# (merged a170641e), and its call set named in the install's settings. Rehearsed (DEC-1057).
#   bash apply.sh check  [--settings-before F --settings-after F]   the state; changes nothing
#   bash apply.sh apply  [--settings-before F --settings-after F]   checks first; backups (sha256s); the swap; APPROVED last
#   bash apply.sh undo   [--settings-before F --settings-after F]   checks first; every file back byte for byte; APPROVED last
# --settings-before/--settings-after are for the rehearsal only (a planted install names the clone and the planted HOME).
# What changes, in $HOME/gov-os-operator/install/ only (nothing in the repository, nothing else on the machine):
#   opcommon.py       1c694692129069cb… -> e392d8a0e177e999…  (the call set's settings: calls, guard_calls, replay_stale_h)
#   operator_run.py   41271992b6379ecb… -> fe2e2f424616b908…  (replay(): the call set checked against the guard's call
#                                                            log by sha256 both ways before anything is re-judged)
#   operator-settings.json a7d6dcbf40be49a5… -> 5a347f36513630dc… (one key added: "calls", the CTO's call set file)
#   APPROVED          157a9dc01fcaab78… -> b4a15c8f3b7c7692…  (sha256sum's form, every install file but itself)
# Every other install file is checked unchanged. It refuses while the operator holds a run (the freeze, the journal, the
# lock of a failed undo, a launch running) or a request waits in queue/. It never writes outside install/ and this
# folder's backup/. It commits nothing.
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT=$(cd "$HERE/../../../../.." && pwd)
cmd=${1:-}; shift || true
S_BEFORE=$HERE/operator-settings.before.json
S_AFTER=$HERE/operator-settings.after.json
while [ $# -gt 0 ]; do
  case "$1" in
    --settings-before) S_BEFORE=$2; shift 2 ;;
    --settings-after) S_AFTER=$2; shift 2 ;;
    *) echo "usage: bash apply.sh check|apply|undo [--settings-before F --settings-after F]" >&2; exit 2 ;;
  esac
done
OP=$HOME/gov-os-operator
INST=$OP/install
BACKUP=$HERE/backup
SRC=$ROOT/governance/project/operator
# The hashes as built (2026-11-09, w2/integrate at f8b242dc9; the install as ACT-OPERATOR-1 left it, 2a6462653)
OLD_COMMON=1c694692129069cb3c5cb8b31bbcb93f464b528d567b01b2c46830c7f2f5c714
OLD_RUN=41271992b6379ecb77ecabc8b0e81bd543eac749e1cd1ce1ee37301ceb150a95
NEW_COMMON=e392d8a0e177e999f5361243a053e386f5fccc0619dec7d5e8c832cd756a1024
NEW_RUN=fe2e2f424616b9083f371fd3e611a91ff9488c2c9d24513b61200cb7beeb4ac2
LIVE_S_BEFORE=a7d6dcbf40be49a57b56097058a91ec7f652d95711a653f9afa4bb20786fad29
LIVE_S_AFTER=5a347f36513630dc7c990160d51bb75c81fa5ada7b7c773dd3e08ddc57fe1536
LIVE_APPROVED_BEFORE=157a9dc01fcaab78b04dc78f153df8b077460a33ffaa9027cb05bc4b8e474ad7
LIVE_APPROVED_AFTER=b4a15c8f3b7c769259f25b8d71406e6c7d387d30c021343f26f4bad6e3831fa4
# The install's other files, unchanged by this ACT (ACT-OPERATOR-1's install.sums less the two code files)
KEEP="c8ce4308aaf7a94975ea872d8eb4cb7bd045ef6415dc5e8c9f286cc63bbcc523  act_class.py
51c459cfbcfec47652df455844480a56a5bc91b5fba3bcf57dc807c5dbf08cc2  brief.md
0f130073bbbd06f7b56c7be44e72d42ffe6460bc49f4c6a684f81f499979bab1  class-rules.yaml
00e8ce13249e427626765b1c53b54811815276d6fbed4c8dd55c238c29c4122a  freeze_gate.py
a0687ebde2365fb2d7b1b63a50cef2c3da94f2d56a4a01eede287e7d9f5afd32  landing_check.py
5bdcfc9bbc9c9707dab7a217a0c4ed6f561c76fcf4d2c1049853a4fd342fbf69  operator_launch.py
e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a  reviewer-brief.md
277c8ca9f06c90906397579f4d5bd144fb506a40b0836eb2a8f9c1443d909378  verdict.py
d1f7b23c1c2dd8f7390f4be97508a7e5ac222729a332634199a8bd17230b02da  wall/operator_wall_hook.py
09fcd4239da357c0d0bb54cb95f64968458d550541ba55841c5dcb63736f0cf6  wall/settings.json.tmpl
ae191d76a7d9ceeeccfcd54ed03b2ce7104840d99e682713a38e014f515b2ee2  win_toast.ps1"
die() { echo "apply.sh: $*" >&2; exit 1; }
sha() { if [ -f "$1" ] && [ ! -L "$1" ]; then sha256sum "$1" | cut -c1-64; else echo none; fi; }

# APPROVED's bytes for a state: KEEP plus the three changing files, sorted as sha256sum's form (C order)
approved_text() {  # $1 common sha, $2 run sha, $3 settings sha
  { printf '%s\n' "$KEEP"; printf '%s  opcommon.py\n%s  operator_run.py\n%s  operator-settings.json\n' "$1" "$2" "$3"; } \
    | LC_ALL=C sort -k2
}
approved_sha() { approved_text "$@" | sha256sum | cut -c1-64; }

drafts_ok() {
  [ "$(sha "$HERE/code/opcommon.py")" = "$NEW_COMMON" ] || { echo "the draft code/opcommon.py is not as built"; return 1; }
  [ "$(sha "$HERE/code/operator_run.py")" = "$NEW_RUN" ] || { echo "the draft code/operator_run.py is not as built"; return 1; }
  [ "$(sha "$SRC/opcommon.py")" = "$NEW_COMMON" ] || { echo "the tree's governance/project/operator/opcommon.py is not the merged one (a170641e)"; return 1; }
  [ "$(sha "$SRC/operator_run.py")" = "$NEW_RUN" ] || { echo "the tree's governance/project/operator/operator_run.py is not the merged one (a170641e)"; return 1; }
  [ -f "$S_BEFORE" ] && [ -f "$S_AFTER" ] || { echo "a settings file is missing"; return 1; }
  if [ "$S_BEFORE" = "$HERE/operator-settings.before.json" ]; then
    [ "$(sha "$S_BEFORE")" = "$LIVE_S_BEFORE" ] && [ "$(sha "$S_AFTER")" = "$LIVE_S_AFTER" ] \
      || { echo "the settings drafts are not as built"; return 1; }
    [ "$(approved_sha "$OLD_COMMON" "$OLD_RUN" "$LIVE_S_BEFORE")" = "$LIVE_APPROVED_BEFORE" ] \
      && [ "$(approved_sha "$NEW_COMMON" "$NEW_RUN" "$LIVE_S_AFTER")" = "$LIVE_APPROVED_AFTER" ] \
      || { echo "APPROVED as computed is not as built"; return 1; }
  fi
  return 0
}

# The install's state: before (as ACT-OPERATOR-1 left it), applied (as this ACT leaves it), or other (anything else)
state() {
  [ -d "$INST" ] && [ ! -L "$INST" ] || { echo other; return; }
  local f s
  while read -r s f; do
    [ "$(sha "$INST/$f")" = "$s" ] || { echo other; return; }
  done <<< "$KEEP"
  local extra; extra=$( cd "$INST" && find . -path ./__pycache__ -prune -o \( -type f -o -type l \) -print | sed 's#^\./##' \
    | grep -vxF -e APPROVED -e opcommon.py -e operator_run.py -e operator-settings.json -e act-in-progress.txt \
    | while read -r f; do printf '%s\n' "$KEEP" | grep -q "  $f\$" || echo "$f"; done )
  [ -z "$extra" ] || { echo other; return; }
  local c r st ap sb sa
  c=$(sha "$INST/opcommon.py"); r=$(sha "$INST/operator_run.py"); st=$(sha "$INST/operator-settings.json")
  ap=$(sha "$INST/APPROVED"); sb=$(sha "$S_BEFORE"); sa=$(sha "$S_AFTER")
  if [ "$c" = "$OLD_COMMON" ] && [ "$r" = "$OLD_RUN" ] && [ "$st" = "$sb" ] && [ "$ap" = "$(approved_sha "$OLD_COMMON" "$OLD_RUN" "$sb")" ]; then
    echo before
  elif [ "$c" = "$NEW_COMMON" ] && [ "$r" = "$NEW_RUN" ] && [ "$st" = "$sa" ] && [ "$ap" = "$(approved_sha "$NEW_COMMON" "$NEW_RUN" "$sa")" ]; then
    echo applied
  else
    echo other
  fi
}

idle_or_die() {  # the operator holds nothing, and nothing waits to be launched
  [ ! -e "$INST/act-in-progress.txt" ] || die "the operator's freeze is held (install/act-in-progress.txt): a run is applying; nothing changed"
  [ ! -e "$OP/log/journal.json" ] || die "the operator's journal exists (log/journal.json): a run is unfinished; nothing changed"
  [ ! -e "$OP/log/operator.lock" ] || die "the operator's lock is held (log/operator.lock): an undo failed, the owner's to clear; nothing changed"
  local q; q=$(find "$OP/queue" -maxdepth 1 -name '*.req' 2>/dev/null | head -1)
  [ -z "$q" ] || die "a request waits in queue/ ($(basename "$q")): let it run first; nothing changed"
}

put() {  # $1 source file, $2 install name: a new file beside it, 0444, then renamed over it
  local tmp="$INST/.$(basename "$2").act-operator-2.$$"
  rm -f "$tmp"; cat "$1" > "$tmp"; chmod 0444 "$tmp"; mv -f "$tmp" "$INST/$2"
}

case "$cmd" in
  check)
    drafts_ok || die "nothing changed"
    s=$(state)
    echo "install: $s (APPROVED $(sha "$INST/APPROVED" | cut -c1-12))"
    case "$s" in
      before) idle_or_die; echo "check: ready to apply" ;;
      applied) echo "check: already applied" ;;
      *) die "the install is neither as ACT-OPERATOR-1 left it nor as this ACT leaves it: the CTO rebuilds; nothing changed" ;;
    esac ;;
  apply)
    drafts_ok || die "nothing changed"
    [ "$(state)" = before ] || die "the install is not in its before state ($(state)); nothing changed"
    idle_or_die
    mkdir -p "$OP/log"
    exec 9>>"$OP/log/launch.lock"
    flock -n 9 || die "a launch is running (log/launch.lock is held); nothing changed"
    [ ! -e "$BACKUP" ] || die "$BACKUP exists: a backup from an earlier apply; the CTO looks first; nothing changed"
    mkdir -p "$BACKUP"
    for f in opcommon.py operator_run.py operator-settings.json APPROVED; do cp -p "$INST/$f" "$BACKUP/$f"; done
    ( cd "$BACKUP" && sha256sum opcommon.py operator_run.py operator-settings.json APPROVED > SHA256SUMS )
    put "$HERE/code/opcommon.py" opcommon.py
    put "$HERE/code/operator_run.py" operator_run.py
    put "$S_AFTER" operator-settings.json
    tmpa="$BACKUP/APPROVED.new"
    approved_text "$NEW_COMMON" "$NEW_RUN" "$(sha "$S_AFTER")" > "$tmpa"
    put "$tmpa" APPROVED; rm -f "$tmpa"
    [ "$(state)" = applied ] || die "after the swap the install is $(state): run 'bash apply.sh undo'"
    ( cd "$INST" && python3 -I -c 'import sys; sys.path.insert(0, "."); import opcommon as oc; r = oc.approved_state("."); print("the install'"'"'s own APPROVED check:", "ok" if r[0] else r[2]); sys.exit(0 if r[0] else 1)' ) \
      || die "the install's own APPROVED check failed: run 'bash apply.sh undo'"
    echo "APPROVED $(sha "$INST/APPROVED")"
    echo "state applied" ;;
  undo)
    [ "$(state)" = applied ] || die "the install is not as this ACT left it ($(state)); nothing changed"
    idle_or_die
    [ -f "$BACKUP/SHA256SUMS" ] || die "no backup in $BACKUP; nothing changed"
    ( cd "$BACKUP" && sha256sum -c --quiet SHA256SUMS ) || die "the backup does not match its SHA256SUMS; nothing changed"
    [ "$(sha "$BACKUP/opcommon.py")" = "$OLD_COMMON" ] && [ "$(sha "$BACKUP/operator_run.py")" = "$OLD_RUN" ] \
      && [ "$(sha "$BACKUP/operator-settings.json")" = "$(sha "$S_BEFORE")" ] \
      || die "the backup is not the before state; nothing changed"
    exec 9>>"$OP/log/launch.lock"
    flock -n 9 || die "a launch is running (log/launch.lock is held); nothing changed"
    put "$BACKUP/opcommon.py" opcommon.py
    put "$BACKUP/operator_run.py" operator_run.py
    put "$BACKUP/operator-settings.json" operator-settings.json
    put "$BACKUP/APPROVED" APPROVED
    [ "$(state)" = before ] || die "after the undo the install is $(state)"
    mv "$BACKUP" "$BACKUP.undone-$(date -u +%Y%m%dT%H%M%SZ)"
    echo "APPROVED $(sha "$INST/APPROVED")"
    echo "state before (undone)" ;;
  *) echo "usage: bash apply.sh check|apply|undo [--settings-before F --settings-after F]" >&2; exit 2 ;;
esac
