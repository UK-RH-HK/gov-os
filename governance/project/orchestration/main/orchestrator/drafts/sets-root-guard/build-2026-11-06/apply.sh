#!/usr/bin/env bash
# DEC-1082 (3), the sets-root guard: the operator's apply, check and undo of the two files it changes.
#   bash apply.sh check   the two files' hashes, which state they are in, and the candidate and patch checked (changes
#                         nothing)
#   bash apply.sh apply   back both files up (with their sha256), put the candidate hook in place and patch the map,
#                         then check the hashes after
#   bash apply.sh undo    put both backed-up files back, byte for byte, and check their hashes
# It changes only .claude/hooks/pretooluse.py and governance/project/path-map.yaml of the tree it sits in (found from
# this file's own place: <tree>/.gov-runtime/scratch/orchestrator/drafts/sets-root-guard/), and writes its backups
# beside itself (backup/). It runs no hook and reads nothing under the sets root.
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT=$(cd "$HERE/../../../../.." && pwd)
HOOK=.claude/hooks/pretooluse.py
MAP=governance/project/path-map.yaml
CAND=$HERE/pretooluse.candidate.py
PATCH=$HERE/path-map.patch
BACKUP=$HERE/backup
# The hashes as built on 2026-11-06 (the hook as ACT-G14 left it; the map as at w2/integrate aa999aa607ce, unchanged
# since 8b85bbb90). A file that has moved since stops every command but undo.
BEFORE_HOOK=e406653ef6c92f014a6b874598b6a3e03fbc270310ecbfdd9c7b079ca43f7cc3
BEFORE_MAP=cc8139a1c8f4a267ba55272361006cb7c742b2b671485bc32f7f50d5741ad5c5
AFTER_HOOK=42749e673c50e02c66cd89a5f17ca7faa98cafd32dff341c2617af71989c1511
AFTER_MAP=da095dce9171221df5602f31208176e684f3ace731b1953658e8c198b3c6d559

die() { echo "apply.sh: $*; nothing more is done" >&2; exit 1; }
sha() { sha256sum "$1" | cut -d' ' -f1; }
[ -d "$ROOT/.git" ] || [ -f "$ROOT/.git" ] || die "$ROOT is not a git tree"
[ -f "$ROOT/$HOOK" ] && [ -f "$ROOT/$MAP" ] || die "$ROOT has no $HOOK or $MAP"

state() {  # before | applied | other, for the two files together
  local h m; h=$(sha "$ROOT/$HOOK"); m=$(sha "$ROOT/$MAP")
  if [ "$h" = "$BEFORE_HOOK" ] && [ "$m" = "$BEFORE_MAP" ]; then echo before
  elif [ "$h" = "$AFTER_HOOK" ] && [ "$m" = "$AFTER_MAP" ]; then echo applied
  else echo other; fi
}
show() {  # $1: a label
  echo "$1: $(sha "$ROOT/$HOOK")  $HOOK"
  echo "$1: $(sha "$ROOT/$MAP")  $MAP"
  echo "$1: state $(state)"
}
patched() {  # the map with the patch applied, written to $1
  patch --quiet --no-backup-if-mismatch -r /dev/null -o "$1" "$ROOT/$MAP" "$PATCH" >/dev/null || return 1
}
put() {  # put file $1 at $2 by a rename in $2's folder, with $2's mode
  local tmp; tmp=$(mktemp "$(dirname "$2")/.sets-root-guard.XXXXXX")
  cp "$1" "$tmp" && chmod --reference="$2" "$tmp" && mv -f "$tmp" "$2" || { rm -f "$tmp"; return 1; }
}

cmd=${1:-}
echo "apply.sh $cmd: tree $ROOT"
case "$cmd" in
  check)
    show now
    [ "$(sha "$CAND")" = "$AFTER_HOOK" ] && echo "candidate hook: ok ($AFTER_HOOK)" || die "the candidate hook's hash is not $AFTER_HOOK"
    python3 -c 'import ast, sys; ast.parse(open(sys.argv[1]).read())' "$CAND" && echo "candidate hook: parses"
    if [ "$(state)" = before ]; then
      t=$(mktemp); patched "$t" || { rm -f "$t"; die "the patch does not apply to $MAP"; }
      got=$(sha "$t"); rm -f "$t"
      [ "$got" = "$AFTER_MAP" ] && echo "patch: applies, gives $AFTER_MAP" || die "the patched map hashes to $got, not $AFTER_MAP"
    fi
    case "$(state)" in
      before) echo "check: ready to apply" ;;
      applied) echo "check: already applied" ;;
      *) die "the files are neither as before nor as applied (they have moved since the build: ask the CTO)" ;;
    esac ;;
  apply)
    show before
    [ "$(state)" = before ] || die "the files are not in the state before (state $(state))"
    [ "$(sha "$CAND")" = "$AFTER_HOOK" ] || die "the candidate hook's hash is not $AFTER_HOOK"
    t=$(mktemp); patched "$t" || { rm -f "$t"; die "the patch does not apply to $MAP"; }
    [ "$(sha "$t")" = "$AFTER_MAP" ] || { rm -f "$t"; die "the patched map does not hash to $AFTER_MAP"; }
    mkdir -p "$BACKUP"
    for f in pretooluse.py path-map.yaml; do
      [ -e "$BACKUP/$f" ] && { rm -f "$t"; die "$BACKUP/$f exists already (an earlier apply): move it aside first"; }
    done
    cp -p "$ROOT/$HOOK" "$BACKUP/pretooluse.py"
    cp -p "$ROOT/$MAP" "$BACKUP/path-map.yaml"
    ( cd "$BACKUP" && sha256sum pretooluse.py path-map.yaml > SHA256SUMS )
    [ "$(sha "$BACKUP/pretooluse.py")" = "$BEFORE_HOOK" ] && [ "$(sha "$BACKUP/path-map.yaml")" = "$BEFORE_MAP" ] \
      || { rm -f "$t"; die "the backups do not hash as before"; }
    echo "backup: $BACKUP (SHA256SUMS written)"
    put "$CAND" "$ROOT/$HOOK" || { rm -f "$t"; die "the hook could not be put in place (the map is untouched)"; }
    put "$t" "$ROOT/$MAP" || { rm -f "$t"; die "the map could not be patched (the hook IS changed: run undo)"; }
    rm -f "$t"
    show after
    [ "$(state)" = applied ] || die "the files do not hash as applied: run undo"
    echo "apply: done" ;;
  undo)
    show before-undo
    [ -f "$BACKUP/pretooluse.py" ] && [ -f "$BACKUP/path-map.yaml" ] || die "no backup in $BACKUP"
    [ "$(sha "$BACKUP/pretooluse.py")" = "$BEFORE_HOOK" ] && [ "$(sha "$BACKUP/path-map.yaml")" = "$BEFORE_MAP" ] \
      || die "the backups do not hash as the files before the apply"
    [ "$(state)" = applied ] || echo "undo: note: the files have changed since the apply (state $(state)); restoring anyway"
    put "$BACKUP/pretooluse.py" "$ROOT/$HOOK" || die "the hook could not be restored"
    put "$BACKUP/path-map.yaml" "$ROOT/$MAP" || die "the map could not be restored (the hook IS restored)"
    show after-undo
    cmp -s "$BACKUP/pretooluse.py" "$ROOT/$HOOK" && cmp -s "$BACKUP/path-map.yaml" "$ROOT/$MAP" \
      && [ "$(state)" = before ] || die "the restored files differ from the backups"
    echo "undo: done; both files are byte for byte as before the apply" ;;
  *)
    echo "usage: bash apply.sh check|apply|undo" >&2; exit 2 ;;
esac
