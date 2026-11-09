#!/usr/bin/env bash
# ACT-OPERATOR-1 (DEC-1104 (2), DEC-1106, DEC-1107, DEC-1108 (5)): the operator agent's install, rehearsed.
#   bash apply.sh check  [--settings FILE]   every draft and source hashes as built; the state of each part; changes
#                                            nothing
#   bash apply.sh apply  [--settings FILE]   checks everything first; backups (sha256s); then the parts below in this
#                                            order, the crontab last
#   bash apply.sh undo                        checks every part first (each as applied or as before, nothing else);
#                                            then every part back byte for byte, the crontab first; refuses while the
#                                            operator holds a run, and never overwrites a file someone else changed
# --settings is for the rehearsal only: the install's operator-settings.json from FILE instead of the built one.
# The parts (the tree is found from this file's place: <tree>/.gov-runtime/scratch/orchestrator/drafts/operator-1/;
# the home is $HOME; the crontab is `crontab` on PATH):
#   code    governance/project/operator/operator_run.py (F26), freeze_gate.py (new), governance/project/orchestration/
#           tools/merge_queue.py (its landing waits on the freeze), tests/unit/operator/test_act_operator_1.py (new)
#   install $HOME/gov-os-operator/install/: the operator code as the tree then holds it (less __pycache__), the
#           install's operator-settings.json, and APPROVED (sha256sum's form); install.sums pins every file's sha256;
#           $HOME/gov-os-operator/queue/ (0700), the CTO's only door (kept by undo once it holds a record)
#   map     governance/project/path-map.yaml: the write_refused block (rule 2d)
#   hook    .claude/hooks/pretooluse.py: rule 2d, on whichever of the two rehearsed hooks is live (before
#           ACT-GUARD-CALLLOG-1, d5be03dbb48e; after it, a7981319f877); any other hook refuses
#   githook .git/hooks/reference-transaction: the commit freeze in the prepared state (freeze_gate.py)
#   tools   the CTO's landing_select.sh and its tests (the freeze honoured; the landing check filed as P1 items)
#   cron    one crontab line (crontab.line), the crontab backed up first
# It commits nothing: the operator's commit follows (the package's message).
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT=$(cd "$HERE/../../../../.." && pwd)
cmd=${1:-}; shift || true
SETTINGS=$HERE/operator-settings.json
while [ $# -gt 0 ]; do
  case "$1" in
    --settings) SETTINGS=$2; shift 2 ;;
    *) echo "usage: bash apply.sh check|apply|undo [--settings FILE]" >&2; exit 2 ;;
  esac
done
OP=$HOME/gov-os-operator
INST=$OP/install
QUEUE=$OP/queue
BACKUP=$HERE/backup
TOOLS=.gov-runtime/scratch/orchestrator/tools
OPDIR=governance/project/operator
MQ=governance/project/orchestration/tools/merge_queue.py
UNIT=tests/unit/operator/test_act_operator_1.py
HOOK=.claude/hooks/pretooluse.py
MAP=governance/project/path-map.yaml
GITHOOK=.git/hooks/reference-transaction
CRONLINE=$(cat "$HERE/crontab.line")
# The hashes as built (2026-11-09, w2/integrate at baebd4fa5)
HOOK_PRE=d5be03dbb48ed6b9a3b60364afc39c61db11cac65a1b93c0889f5999aa6ef74c
HOOK_POST=a7981319f877846d6a62a6768ca036a5014dc7d9f8aadd09e54e61af8251d7d0
HOOK_PRE_AFTER=4b528eb87118c22bb55ce67532eb6f823294c73fd7b0c3a01f3f168d7612bf96
HOOK_POST_AFTER=97a84e770058bb96705ebe41c259c0c1578bdc8ac23fac237e6cdf5f1af43e11
MAP_BEFORE=3f7ae7f83d998c4036e015f9f1b6b8a8c321af2762267ed9d32c524eab81d397
MAP_AFTER=40085090306e9429e1fdc2ef4eb8bb3bd5af26ad3d50db95222950794bf242a5
RUN_BEFORE=fb6092758b0168712d96b01d09dc2f1f7a74e3e0cdc6f1b6a208fb1fac38ecff
RUN_AFTER=41271992b6379ecb77ecabc8b0e81bd543eac749e1cd1ce1ee37301ceb150a95
GATE_AFTER=00e8ce13249e427626765b1c53b54811815276d6fbed4c8dd55c238c29c4122a
MQ_BEFORE=36c8e1573285ce05bbd3c006865f32d6ee4118c0e9bc7122d6cc859f548a4cec
MQ_AFTER=1f3b1d44f507459337361c20308c36d2e6f7cbfcad3d767b027feef8b734d3da
UNIT_AFTER=5ced364cdf0687f5dd8f0a6aec18aebb8faaa17e0dba1d5795efbbf269c426df
GITHOOK_BEFORE=6fbbf312bacde210d376575f17ad556d65d30c192d3f79f23622ac0650b361cc
GITHOOK_AFTER=099de326c45b86aad8530c4dd754c7f730b4ddc5285c4cb9eca2e5a02f5f39db
LS_BEFORE=984d4dfc7f828ac0c89766252a1ef5e0dac768ac93dd887e547e6fe105446f6a
LS_AFTER=9e55c0b880323d30a1903858e22b67fe2bf56db553a5a1d57aa9568a2509dd81
TLS_BEFORE=50515591ffcef813d3b1adead323bbc5ec495bc80558221bd0a8c3c8cecc3028
TLS_AFTER=16aa390131c6ff954907a85f6985fe89acf60404252d543fb79af78bed950dd3
SUMS=29ea262339165096968c1b0b1cb0b512dc624effedfa08018b1ec6a9dafbf9b8
SETTINGS_BUILT=a7d6dcbf40be49a57b56097058a91ec7f652d95711a653f9afa4bb20786fad29
CRONLINE_SHA=77dcf466177792b5cf02e3afa86b251a1084c9d359b5db6123935fc0bd1c6c07

die() { echo "apply.sh: $*; nothing more is done" >&2; exit 1; }
sha() { if [ -L "$1" ]; then echo link; elif [ -f "$1" ]; then sha256sum "$1" | cut -d' ' -f1; else echo absent; fi; }
[ -d "$ROOT/.git" ] || die "$ROOT is not the main tree (no .git folder)"
[ -d "$OP" ] || die "$OP does not exist (the owner's operator folder is expected there)"

drafts_ok() {
  local f h
  while read -r h f; do [ "$(sha "$HERE/$f")" = "$h" ] || die "$f is not as built"; done <<EOF
$HOOK_PRE_AFTER pretooluse.pre.candidate.py
$HOOK_POST_AFTER pretooluse.post.candidate.py
$MAP_AFTER path-map.candidate.yaml
$RUN_AFTER code/operator_run.py
$GATE_AFTER code/freeze_gate.py
$MQ_AFTER code/merge_queue.py
$UNIT_AFTER code/test_act_operator_1.py
$GITHOOK_AFTER reference-transaction.candidate
$LS_AFTER landing_select.candidate.sh
$TLS_AFTER test_landing_select.candidate.sh
$SUMS install.sums
$SETTINGS_BUILT operator-settings.json
$CRONLINE_SHA crontab.line
EOF
  [ -f "$SETTINGS" ] && python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); assert isinstance(d, dict)' "$SETTINGS" \
    || die "the settings file $SETTINGS is not a JSON object"
}
sources_ok() {  # review F8: every file the install copies from the tree hashes as built, before anything is written
  local f h
  while read -r h f; do
    case "$f" in operator_run.py|freeze_gate.py) continue ;; esac
    [ "$(sha "$ROOT/$OPDIR/$f")" = "$h" ] || die "the tree's $OPDIR/$f is not as built (rebuild, re-rehearse)"
  done < "$HERE/install.sums"
}
cron_now() { crontab -l 2>/dev/null || true; }
cron_has() { cron_now | grep -qF "/gov-os-operator/install/operator_launch.py"; }
cron_part() {  # before | applied (the table holds the operator's line; with a backup, byte for byte backup/crontab.after,
  # however it was loaded: by apply.sh, or by the operator through standard input) | other
  if ! cron_has; then echo before; return; fi
  if [ -f "$BACKUP/crontab.after" ] && ! cmp -s <(cron_now) "$BACKUP/crontab.after"; then echo other; return; fi
  echo applied
}
hook_part() {  # before-pre | before-post | applied-pre | applied-post | other
  case "$(sha "$ROOT/$HOOK")" in
    "$HOOK_PRE") echo before-pre ;; "$HOOK_POST") echo before-post ;;
    "$HOOK_PRE_AFTER") echo applied-pre ;; "$HOOK_POST_AFTER") echo applied-post ;; *) echo other ;;
  esac
}
part() {  # $1 file, $2 before hash, $3 after hash: before | applied | other
  local h; h=$(sha "$1")
  if [ "$h" = "$2" ]; then echo before; elif [ "$h" = "$3" ]; then echo applied; else echo other; fi
}
queue_part() {  # absent | empty | record (only the launcher's taken/ done/ rejected/, no request waiting) | other
  if [ ! -e "$QUEUE" ] && [ ! -L "$QUEUE" ]; then echo absent; return; fi
  [ -d "$QUEUE" ] && [ ! -L "$QUEUE" ] || { echo other; return; }
  local top; top=$(ls -A "$QUEUE")
  [ -z "$top" ] && { echo empty; return; }
  echo "$top" | grep -vqxE 'taken|done|rejected' && { echo other; return; }
  echo record
}
install_files() { ( cd "$INST" && find . -path ./__pycache__ -prune -o -path ./wall/__pycache__ -prune -o -type f -print -o -type l -print | sed 's#^\./##' | LC_ALL=C sort ); }
install_part() {  # absent | applied | other
  if [ ! -e "$INST" ] && [ ! -L "$INST" ]; then echo absent; return; fi
  [ -d "$INST" ] && [ ! -L "$INST" ] || { echo other; return; }
  local f h
  while read -r h f; do [ "$(sha "$INST/$f")" = "$h" ] || { echo other; return; }; done < "$HERE/install.sums"
  [ -f "$INST/operator-settings.json" ] && [ -f "$INST/APPROVED" ] || { echo other; return; }
  local extra; extra=$(install_files | grep -vxF -e APPROVED -e operator-settings.json -e act-in-progress.txt \
    | comm -23 - <(cut -c67- "$HERE/install.sums" | LC_ALL=C sort))
  [ -z "$extra" ] && echo applied || echo other
}
states() {
  echo "code operator_run.py: $(part "$ROOT/$OPDIR/operator_run.py" "$RUN_BEFORE" "$RUN_AFTER")"
  echo "code freeze_gate.py: $(part "$ROOT/$OPDIR/freeze_gate.py" absent "$GATE_AFTER")"
  echo "code merge_queue.py: $(part "$ROOT/$MQ" "$MQ_BEFORE" "$MQ_AFTER")"
  echo "code test_act_operator_1.py: $(part "$ROOT/$UNIT" absent "$UNIT_AFTER")"
  echo "install: $(install_part)"
  echo "queue: $(queue_part)"
  echo "map: $(part "$ROOT/$MAP" "$MAP_BEFORE" "$MAP_AFTER")"
  echo "hook: $(hook_part)"
  echo "githook: $(part "$ROOT/$GITHOOK" "$GITHOOK_BEFORE" "$GITHOOK_AFTER")"
  echo "tools landing_select.sh: $(part "$ROOT/$TOOLS/landing_select.sh" "$LS_BEFORE" "$LS_AFTER")"
  echo "tools test_landing_select.sh: $(part "$ROOT/$TOOLS/test_landing_select.sh" "$TLS_BEFORE" "$TLS_AFTER")"
  echo "cron: $(cron_part)"
}
state() {  # before | applied | other (a queue that holds only a record counts as either: review F1)
  local s; s=$(states)
  if ! echo "$s" | grep -vqE ': (before|absent|record|before-pre|before-post)$'; then echo before
  elif ! echo "$s" | grep -vqE ': (applied|empty|record|applied-pre|applied-post)$'; then echo applied
  else echo other; fi
}
show() {
  echo "$1: tree $ROOT; operator folder $OP"
  states | sed "s/^/$1: /"
  for f in "$HOOK" "$MAP" "$OPDIR/operator_run.py" "$MQ" "$GITHOOK" "$TOOLS/landing_select.sh"; do
    echo "$1: $(sha "$ROOT/$f" | cut -c1-12)  $f"
  done
  [ -f "$INST/APPROVED" ] && echo "$1: $(sha "$INST/APPROVED")  install/APPROVED"
  echo "$1: $(cron_now | sha256sum | cut -c1-12)  crontab -l"
  echo "$1: state $(state)"
}
put() {  # put file $1 at $2 by a rename in $2's folder; mode $3 (or $2's, or 0644)
  local tmp; tmp=$(mktemp "$(dirname "$2")/.act-operator-1.XXXXXX")
  cp "$1" "$tmp" || { rm -f "$tmp"; return 1; }
  if [ -n "${3:-}" ]; then chmod "$3" "$tmp"; elif [ -e "$2" ]; then chmod --reference="$2" "$tmp"; else chmod 0644 "$tmp"; fi
  mv -f "$tmp" "$2" || { rm -f "$tmp"; return 1; }
}
operator_busy() {  # a run in progress, a held lock or a waiting request: undo refuses
  [ -e "$INST/act-in-progress.txt" ] && { echo "the commit freeze install/act-in-progress.txt exists"; return 0; }
  [ -e "$OP/log/journal.json" ] && { echo "an unfinished journal log/journal.json exists"; return 0; }
  [ -e "$OP/log/operator.lock" ] && { echo "the operator's lock log/operator.lock is held"; return 0; }
  [ -n "$(find "$QUEUE" -maxdepth 1 -name '*.req' 2>/dev/null)" ] && { echo "a request waits in queue/"; return 0; }
  return 1
}
install_removable() {  # every file in install/ is the ACT's own (install.sums, its settings, its APPROVED): a whole or partial install
  local f h want
  while read -r f; do
    case "$f" in
      APPROVED) [ ! -f "$BACKUP/APPROVED.sha256" ] || [ "$(sha "$INST/APPROVED")" = "$(cat "$BACKUP/APPROVED.sha256")" ] \
                  || { echo "install/APPROVED has changed since the apply"; return 1; } ;;
      operator-settings.json) [ "$(sha "$INST/$f")" = "$(sha "$BACKUP/operator-settings.json")" ] \
                  || { echo "install/operator-settings.json has changed since the apply"; return 1; } ;;
      *) want=$(awk -v f="$f" 'substr($0, 67) == f {print substr($0, 1, 64)}' "$HERE/install.sums")
         [ -n "$want" ] && [ "$(sha "$INST/$f")" = "$want" ] || { echo "install/$f is not the ACT's own"; return 1; } ;;
    esac
  done < <(install_files)
  return 0
}

case "$cmd" in
  check)
    show now
    drafts_ok && sources_ok && echo "drafts and the install's sources: every file as built (settings $(sha "$SETTINGS" | cut -c1-12))"
    case "$(state)" in
      before) echo "check: ready to apply (the hook is $(hook_part | cut -d- -f2)-calllog)" ;;
      applied) echo "check: already applied" ;;
      *) die "the tree is neither as before nor as applied (a file has moved since the build: ask the CTO to rebuild and re-rehearse)" ;;
    esac ;;
  apply)
    show before
    [ "$(state)" = before ] || die "the tree is not in the state before (state $(state))"
    drafts_ok; sources_ok
    [ -e "$BACKUP" ] && die "$BACKUP exists already (an earlier apply): move it aside first"
    kind=$(hook_part | cut -d- -f2)
    mkdir -p "$BACKUP/tools"
    cp -p "$ROOT/$HOOK" "$BACKUP/pretooluse.py"; cp -p "$ROOT/$MAP" "$BACKUP/path-map.yaml"
    cp -p "$ROOT/$OPDIR/operator_run.py" "$BACKUP/operator_run.py"; cp -p "$ROOT/$MQ" "$BACKUP/merge_queue.py"
    cp -p "$ROOT/$GITHOOK" "$BACKUP/reference-transaction"
    cp -p "$ROOT/$TOOLS/landing_select.sh" "$ROOT/$TOOLS/test_landing_select.sh" "$BACKUP/tools/"
    cp -p "$SETTINGS" "$BACKUP/operator-settings.json"
    cron_now > "$BACKUP/crontab.before"
    echo "$kind" > "$BACKUP/hook-kind"
    ( cd "$BACKUP" && sha256sum pretooluse.py path-map.yaml operator_run.py merge_queue.py reference-transaction tools/* \
        operator-settings.json crontab.before ) > "$BACKUP/SHA256SUMS"
    echo "backup: $BACKUP (SHA256SUMS written; the crontab $(sha "$BACKUP/crontab.before" | cut -c1-12))"
    # 1. the code (F26, the freeze gate, the merge queue's wait, the tests)
    put "$HERE/code/operator_run.py" "$ROOT/$OPDIR/operator_run.py" || die "operator_run.py: run undo"
    put "$HERE/code/freeze_gate.py" "$ROOT/$OPDIR/freeze_gate.py" 0644 || die "freeze_gate.py: run undo"
    put "$HERE/code/merge_queue.py" "$ROOT/$MQ" || die "merge_queue.py: run undo"
    put "$HERE/code/test_act_operator_1.py" "$ROOT/$UNIT" 0644 || die "the tests: run undo"
    # 2. the install, from the tree as it now stands, checked file by file against install.sums
    mkdir -m 0755 "$INST" || die "$INST could not be made: run undo"
    while read -r h f; do
      mkdir -p "$(dirname "$INST/$f")"
      cp "$ROOT/$OPDIR/$f" "$INST/$f"
      [ "$(sha "$INST/$f")" = "$h" ] || die "install/$f does not hash as built: run undo"
      chmod 0444 "$INST/$f"
    done < "$HERE/install.sums"
    cp "$SETTINGS" "$INST/operator-settings.json"; chmod 0444 "$INST/operator-settings.json"
    install_files | grep -vxF APPROVED | while read -r f; do ( cd "$INST" && sha256sum "$f" ); done > "$BACKUP/APPROVED.new"
    chmod 0444 "$BACKUP/APPROVED.new"; cp -p "$BACKUP/APPROVED.new" "$INST/APPROVED"
    sha "$INST/APPROVED" > "$BACKUP/APPROVED.sha256"
    if [ -d "$QUEUE" ]; then chmod 0700 "$QUEUE"; else mkdir -m 0700 "$QUEUE" || die "$QUEUE could not be made: run undo"; fi
    ok=$(cd "$INST" && /usr/bin/python3 -I -c 'import sys; sys.path.insert(0, "."); import opcommon as oc; r = oc.approved_state("."); print("ok" if r[0] else "refused: " + r[2])')
    [ "$ok" = ok ] || die "the install's own APPROVED check says $ok: run undo"
    echo "install: $(wc -l < "$INST/APPROVED") files, APPROVED $(sha "$INST/APPROVED"); the install's own check: ok"
    # 3. the map, 4. the hook, 5. the git hook, 6. the CTO's tools
    put "$HERE/path-map.candidate.yaml" "$ROOT/$MAP" || die "the map: run undo"
    put "$HERE/pretooluse.$kind.candidate.py" "$ROOT/$HOOK" || die "the hook: run undo"
    put "$HERE/reference-transaction.candidate" "$ROOT/$GITHOOK" 0755 || die "the git hook: run undo"
    put "$HERE/landing_select.candidate.sh" "$ROOT/$TOOLS/landing_select.sh" || die "landing_select.sh: run undo"
    put "$HERE/test_landing_select.candidate.sh" "$ROOT/$TOOLS/test_landing_select.sh" || die "its tests: run undo"
    # 7. the crontab, last: from here the cron may launch
    { cat "$BACKUP/crontab.before"; echo "$CRONLINE"; } > "$BACKUP/crontab.after"
    # through standard input, never a path argument: Debian's crontab cuts a path argument at 99 characters (found live,
    # 2026-11-09: this backup's path is 115)
    crontab - < "$BACKUP/crontab.after" || die "crontab refused the new table: run undo"
    cmp -s <(cron_now) "$BACKUP/crontab.after" || die "crontab -l is not the new table: run undo"
    show after
    [ "$(state)" = applied ] || die "the tree does not hash as applied: run undo"
    echo "apply: done (the $kind-calllog hook). The operator's commit stages:"
    echo "  git add $HOOK $MAP $OPDIR/operator_run.py $OPDIR/freeze_gate.py $MQ $UNIT" ;;
  undo)
    show before-undo
    [ -f "$BACKUP/SHA256SUMS" ] && ( cd "$BACKUP" && sha256sum -c --quiet SHA256SUMS ) \
      || die "no backup in $BACKUP, or one that does not hash as written"
    kind=$(cat "$BACKUP/hook-kind")
    if why=$(operator_busy); then die "$why: the install stays until the owner clears it"; fi
    # review F8: every part is checked before anything is written; a part neither as applied nor as before stops it
    if [ "$kind" = pre ]; then HB=$HOOK_PRE HA=$HOOK_PRE_AFTER; else HB=$HOOK_POST HA=$HOOK_POST_AFTER; fi
    for spec in "$TOOLS/test_landing_select.sh|$TLS_AFTER|$TLS_BEFORE" "$TOOLS/landing_select.sh|$LS_AFTER|$LS_BEFORE" \
                "$GITHOOK|$GITHOOK_AFTER|$GITHOOK_BEFORE" "$HOOK|$HA|$HB" "$MAP|$MAP_AFTER|$MAP_BEFORE" \
                "$OPDIR/operator_run.py|$RUN_AFTER|$RUN_BEFORE" "$MQ|$MQ_AFTER|$MQ_BEFORE" \
                "$OPDIR/freeze_gate.py|$GATE_AFTER|absent" "$UNIT|$UNIT_AFTER|absent"; do
      IFS='|' read -r p a b <<< "$spec"
      [ "$(part "$ROOT/$p" "$b" "$a")" != other ] || die "$p has changed since the apply (neither as applied nor as before): nothing undone"
    done
    if cron_has; then cmp -s <(cron_now) "$BACKUP/crontab.after" || die "the crontab has changed since the apply: nothing undone (remove the operator's line by hand)"; fi
    if [ -d "$INST" ]; then why=$(install_removable) || die "$why: nothing undone"; fi
    [ "$(queue_part)" != other ] || die "queue/ holds something besides the launcher's record: nothing undone"
    # the crontab first: no launch from here on
    if cron_has; then
      crontab - < "$BACKUP/crontab.before"     # standard input, never a path argument (see apply)
      cmp -s <(cron_now) "$BACKUP/crontab.before" || die "the crontab could not be restored"
    fi
    restore() {  # $1 backup file, $2 live path, $3 after hash
      [ "$(sha "$2")" = "$3" ] || return 0     # already as before (checked above)
      put "$1" "$2" || die "$2 could not be restored"
    }
    restore "$BACKUP/tools/test_landing_select.sh" "$ROOT/$TOOLS/test_landing_select.sh" "$TLS_AFTER"
    restore "$BACKUP/tools/landing_select.sh" "$ROOT/$TOOLS/landing_select.sh" "$LS_AFTER"
    restore "$BACKUP/reference-transaction" "$ROOT/$GITHOOK" "$GITHOOK_AFTER"
    restore "$BACKUP/pretooluse.py" "$ROOT/$HOOK" "$HA"
    restore "$BACKUP/path-map.yaml" "$ROOT/$MAP" "$MAP_AFTER"
    if [ -d "$INST" ]; then
      chmod -R u+w "$INST"
      rm -rf "$INST/__pycache__" "$INST/wall/__pycache__"
      install_files | while read -r f; do rm -f "$INST/$f"; done
      rmdir "$INST/wall" 2>/dev/null || true
      rmdir "$INST" || die "install/ is not empty after its files were removed"
    fi
    case "$(queue_part)" in
      empty) rmdir "$QUEUE"; echo "undo: queue/ removed (empty)" ;;
      record) echo "undo: queue/ kept: it holds the launcher's record of past requests (taken/, done/, rejected/)" ;;
    esac
    restore "$BACKUP/operator_run.py" "$ROOT/$OPDIR/operator_run.py" "$RUN_AFTER"
    restore "$BACKUP/merge_queue.py" "$ROOT/$MQ" "$MQ_AFTER"
    for p in "$OPDIR/freeze_gate.py" "$UNIT"; do [ "$(sha "$ROOT/$p")" = absent ] || rm -f "$ROOT/$p"; done
    show after-undo
    [ "$(state)" = before ] || die "the tree after the undo is not as before"
    echo "undo: done; every part byte for byte as before (acts/, wall/, queue/'s record and the agent's own log files, if any run made them, stay as the record)" ;;
  *)
    echo "usage: bash apply.sh check|apply|undo [--settings FILE]" >&2; exit 2 ;;
esac
