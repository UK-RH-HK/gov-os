#!/usr/bin/env bash
# DEC-1100 (3), ACT-SELECT-HOOK-1: the operator's check, apply and undo of the one line added to the integration
# repository's reference-transaction hook (W2-116's, installed at re-pin window 4): after W2-116's store refresh, a
# second detached line starts the CTO's tools/landing_select.sh --hook.
#   bash apply.sh check   the hook's hash and state, the candidate's hash, that it is the hook plus exactly that one
#                         line, that it parses (sh -n), and that the tool it calls is there and parses (changes nothing)
#   bash apply.sh apply   back the hook up (with its sha256), put the candidate in place (mode 755), check the hash after
#   bash apply.sh undo    put the backed-up hook back, byte for byte, its mode too, and check it
# It changes only <tree>/.git/hooks/reference-transaction of the tree it sits in (found from this file's own place:
# <tree>/.gov-runtime/scratch/orchestrator/drafts/select-hook/), and writes its backup beside itself (backup/). The
# hook is not tracked: there is nothing to commit (the CTO records the ACT). It runs no hook and no test.
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT=$(cd "$HERE/../../../../.." && pwd)
HOOK=.git/hooks/reference-transaction
CAND=$HERE/reference-transaction.candidate
TOOL=.gov-runtime/scratch/orchestrator/tools/landing_select.sh
BACKUP=$HERE/backup
# As built on 2026-11-09: the live hook as re-pin window 4 installed it (W2-116, 2026-11-07); the candidate is it with
# the one line before its final `exit 0`. A hook that has moved since stops every command but undo.
BEFORE_HOOK=7a21de6dfc51a5d5fa4a5ca56f998e48cb998bdcf577d7ed58156ed3738b0a3e
AFTER_HOOK=6fbbf312bacde210d376575f17ad556d65d30c192d3f79f23622ac0650b361cc
LINE_START='setsid -f env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE -u PYTHONPATH -u PYTHONHOME -u PYTHONSTARTUP bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/landing_select.sh --hook '

die() { echo "apply.sh: $*; nothing more is done" >&2; exit 1; }
sha() { sha256sum "$1" | cut -d' ' -f1; }
[ -d "$ROOT/.git" ] || die "$ROOT has no .git folder"
[ -z "$(git -C "$ROOT" config --get core.hooksPath || true)" ] || die "core.hooksPath is set: git does not run $HOOK here"
[ -f "$ROOT/$HOOK" ] || die "$ROOT has no $HOOK"

state() { local h; h=$(sha "$ROOT/$HOOK"); [ "$h" = "$BEFORE_HOOK" ] && echo before || { [ "$h" = "$AFTER_HOOK" ] && echo applied || echo other; }; }
show() { echo "$1: $(sha "$ROOT/$HOOK")  $HOOK (mode $(stat -c %a "$ROOT/$HOOK"))"; echo "$1: state $(state)"; }
one_line() {  # the candidate is the hook given plus one line, LINE_START..., before the final exit 0
  local d added removed
  d=$(diff "$1" "$CAND" || true)
  added=$(printf '%s\n' "$d" | grep -c '^>' || true); removed=$(printf '%s\n' "$d" | grep -c '^<' || true)
  [ "$added" = 1 ] && [ "$removed" = 0 ] && printf '%s\n' "$d" | grep '^>' | cut -c3- | grep -qF -- "$LINE_START" \
    && [ "$(tail -1 "$CAND")" = "exit 0" ]
}
put() {  # file $1 at $2 by a rename in $2's folder, mode $3
  local tmp; tmp=$(mktemp "$(dirname "$2")/.select-hook.XXXXXX")
  cp "$1" "$tmp" && chmod "$3" "$tmp" && mv -f "$tmp" "$2" || { rm -f "$tmp"; return 1; }
}

cmd=${1:-}
echo "apply.sh $cmd: tree $ROOT"
case "$cmd" in
  check)
    show now
    [ "$(sha "$CAND")" = "$AFTER_HOOK" ] && echo "candidate: ok ($AFTER_HOOK)" || die "the candidate's hash is not $AFTER_HOOK"
    sh -n "$CAND" && echo "candidate: parses (sh -n)"
    if [ "$(state)" = before ]; then
      one_line "$ROOT/$HOOK" && echo "candidate: the hook plus one line, before its final exit 0" || die "the candidate is not the hook plus the one line"
    fi
    [ -f "$ROOT/$TOOL" ] && bash -n "$ROOT/$TOOL" && echo "tool: $TOOL present, parses ($(sha "$ROOT/$TOOL"))" \
      || die "$TOOL is missing or does not parse"
    case "$(state)" in
      before) echo "check: ready to apply" ;;
      applied) echo "check: already applied" ;;
      *) die "the hook is neither as before nor as applied (it has moved since the build: ask the CTO)" ;;
    esac ;;
  apply)
    show before
    [ "$(state)" = before ] || die "the hook is not in the state before (state $(state))"
    [ "$(sha "$CAND")" = "$AFTER_HOOK" ] || die "the candidate's hash is not $AFTER_HOOK"
    one_line "$ROOT/$HOOK" || die "the candidate is not the hook plus the one line"
    [ -f "$ROOT/$TOOL" ] || die "$TOOL is missing"
    [ -e "$BACKUP" ] && die "$BACKUP exists already (an earlier apply): move it aside first"
    mkdir -p "$BACKUP"
    cp -p "$ROOT/$HOOK" "$BACKUP/reference-transaction"
    stat -c %a "$ROOT/$HOOK" > "$BACKUP/mode"
    ( cd "$BACKUP" && sha256sum reference-transaction ) > "$BACKUP/SHA256SUMS"
    [ "$(sha "$BACKUP/reference-transaction")" = "$BEFORE_HOOK" ] || die "the backup does not hash as before"
    echo "backup: $BACKUP (SHA256SUMS written, mode $(cat "$BACKUP/mode"))"
    put "$CAND" "$ROOT/$HOOK" 755 || die "the hook could not be put in place (nothing is changed)"
    show after
    [ "$(state)" = applied ] && [ -x "$ROOT/$HOOK" ] || die "the hook does not hash as applied or is not executable: run undo"
    echo "apply: done. Nothing to commit (the hook is not tracked)." ;;
  undo)
    show before-undo
    [ -f "$BACKUP/reference-transaction" ] && [ "$(sha "$BACKUP/reference-transaction")" = "$BEFORE_HOOK" ] \
      || die "no backup in $BACKUP, or one that does not hash as the hook before the apply"
    [ "$(state)" = applied ] || echo "undo: note: the hook has changed since the apply (state $(state)); restoring anyway"
    put "$BACKUP/reference-transaction" "$ROOT/$HOOK" "$(cat "$BACKUP/mode")" || die "the hook could not be restored"
    show after-undo
    cmp -s "$BACKUP/reference-transaction" "$ROOT/$HOOK" && [ "$(stat -c %a "$ROOT/$HOOK")" = "$(cat "$BACKUP/mode")" ] \
      && [ "$(state)" = before ] || die "the restored hook differs from the backup"
    echo "undo: done; the hook is byte for byte as before the apply, its mode kept" ;;
  *)
    echo "usage: bash apply.sh check|apply|undo" >&2; exit 2 ;;
esac
