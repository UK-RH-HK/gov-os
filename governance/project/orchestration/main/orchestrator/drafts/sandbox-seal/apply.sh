#!/usr/bin/env bash
# DEC-1099 (1) Q6, ACT-SANDBOX-SEAL-1: the operator's check, apply and undo of the one file the seal changes:
#   - governance/project/path-map.yaml   patched by path-map.patch: the evaluation set sandbox-guard-exp-1 (its hidden
#                                        glob fixtures/evaluation/sandbox-guard-exp-1/hidden/**, measuring engineer,
#                                        research, product-spec, independent-test-designer, independent-auditor) and
#                                        the same glob added to sets_root_hidden (so the CTO and leads are refused too)
#   The live hook (.claude/hooks/pretooluse.py, as ACT-GUARD-SETS-1 left it, commit 15952bbf) is NOT changed: the seal
#   uses its rules 2 and 2b as they are. check and apply stop unless the hook still hashes as the seal was built on.
#   bash apply.sh check   both files' hashes, which state the tree is in, the patch checked (changes nothing)
#   bash apply.sh apply   back the map up (with its sha256), patch it, then check the hashes after
#   bash apply.sh undo    put the backed-up map back, byte for byte, and check it
# It changes only that file of the tree it sits in (found from this file's own place:
# <tree>/.gov-runtime/scratch/orchestrator/drafts/sandbox-seal/), and writes its backup beside itself (backup/).
# It runs no hook and reads nothing under the sets root. It commits nothing: the operator's commit follows (ACT §3).
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT=$(cd "$HERE/../../../../.." && pwd)
HOOK=.claude/hooks/pretooluse.py
MAP=governance/project/path-map.yaml
PATCH=$HERE/path-map.patch
BACKUP=$HERE/backup
# The hashes as built on 2026-11-09 (w2/integrate 07e463ec8): the live hook as ACT-GUARD-SETS-1 left it (15952bbf),
# the map as that ACT left it. A file that has moved since stops every command but undo.
HOOK_SHA=bd545af83198962e6c8ecff59afbf86519ae5f201d6660a34941d6aaaa584449
BEFORE_MAP=a9d8b97267c44f519cef37d4b5b702bbb9f2a696a17fa26f68147d2851f04b22
AFTER_MAP=ef9952e9ea4f4b88cd44fbb5a2d91e519fb01fc58e213fedb3d7d8bbb3638661
PATCH_SHA=906544ac4afb3543414e44d01b5a06e356ca0a9b9476b912134c0146965a2df6

die() { echo "apply.sh: $*; nothing more is done" >&2; exit 1; }
sha() { sha256sum "$1" | cut -d' ' -f1; }
[ -d "$ROOT/.git" ] || [ -f "$ROOT/.git" ] || die "$ROOT is not a git tree"
[ -f "$ROOT/$HOOK" ] && [ -f "$ROOT/$MAP" ] || die "$ROOT has no $HOOK or $MAP"

state() {  # before | applied | other
  local m; m=$(sha "$ROOT/$MAP")
  if [ "$m" = "$BEFORE_MAP" ]; then echo before
  elif [ "$m" = "$AFTER_MAP" ]; then echo applied
  else echo other; fi
}
show() {  # $1: a label
  echo "$1: $(sha "$ROOT/$HOOK")  $HOOK"
  echo "$1: $(sha "$ROOT/$MAP")  $MAP"
  echo "$1: state $(state)"
}
patched() {  # file $1 with patch $2 applied, written to $3
  patch --quiet --no-backup-if-mismatch -r /dev/null -o "$3" "$1" "$2" >/dev/null || return 1
}
put() {  # put file $1 at $2 by a rename in $2's folder, keeping $2's mode
  local tmp; tmp=$(mktemp "$(dirname "$2")/.sandbox-seal.XXXXXX")
  cp -p "$1" "$tmp" || { rm -f "$tmp"; return 1; }
  if [ -e "$2" ]; then chmod --reference="$2" "$tmp" || { rm -f "$tmp"; return 1; }; fi
  mv -f "$tmp" "$2" || { rm -f "$tmp"; return 1; }
}
hook_ok() { [ "$(sha "$ROOT/$HOOK")" = "$HOOK_SHA" ]; }

cmd=${1:-}
echo "apply.sh $cmd: tree $ROOT"
case "$cmd" in
  check)
    show now
    [ "$(sha "$PATCH")" = "$PATCH_SHA" ] && echo "patch: ok ($PATCH_SHA)" || die "the patch's hash is not $PATCH_SHA"
    hook_ok && echo "hook: as built ($HOOK_SHA), unchanged by the seal" \
      || die "the live hook is not $HOOK_SHA (it has moved since the build: ask the CTO to re-run the rehearsal)"
    if [ "$(state)" = before ]; then
      t=$(mktemp); patched "$ROOT/$MAP" "$PATCH" "$t" || { rm -f "$t"; die "the patch does not apply to $MAP"; }
      got=$(sha "$t"); rm -f "$t"
      [ "$got" = "$AFTER_MAP" ] && echo "map patch: applies, gives $AFTER_MAP" || die "the patched map hashes to $got, not $AFTER_MAP"
    fi
    case "$(state)" in
      before) echo "check: ready to apply" ;;
      applied) echo "check: already applied" ;;
      *) die "the map is neither as before nor as applied (it has moved since the build: ask the CTO)" ;;
    esac ;;
  apply)
    show before
    [ "$(state)" = before ] || die "the map is not in the state before (state $(state))"
    [ "$(sha "$PATCH")" = "$PATCH_SHA" ] || die "the patch's hash is not $PATCH_SHA"
    hook_ok || die "the live hook is not $HOOK_SHA"
    t=$(mktemp)
    patched "$ROOT/$MAP" "$PATCH" "$t" || { rm -f "$t"; die "the patch does not apply to $MAP"; }
    [ "$(sha "$t")" = "$AFTER_MAP" ] || { rm -f "$t"; die "the patched map does not hash to $AFTER_MAP"; }
    [ -e "$BACKUP" ] && { rm -f "$t"; die "$BACKUP exists already (an earlier apply): move it aside first"; }
    mkdir -p "$BACKUP"
    cp -p "$ROOT/$MAP" "$BACKUP/path-map.yaml"
    ( cd "$BACKUP" && sha256sum path-map.yaml ) > "$BACKUP/SHA256SUMS"
    [ "$(sha "$BACKUP/path-map.yaml")" = "$BEFORE_MAP" ] || { rm -f "$t"; die "the backup does not hash as before"; }
    echo "backup: $BACKUP (SHA256SUMS written)"
    put "$t" "$ROOT/$MAP" || { rm -f "$t"; die "the map could not be patched (nothing is changed)"; }
    rm -f "$t"
    show after
    [ "$(state)" = applied ] || die "the map does not hash as applied: run undo"
    hook_ok || die "the hook changed during the apply: run undo"
    echo "apply: done. The operator's commit stages the one file:"
    echo "  git add $MAP" ;;
  undo)
    show before-undo
    [ -f "$BACKUP/path-map.yaml" ] && [ "$(sha "$BACKUP/path-map.yaml")" = "$BEFORE_MAP" ] \
      || die "no backup in $BACKUP, or one that does not hash as the map before the apply"
    [ "$(state)" = applied ] || echo "undo: note: the map has changed since the apply (state $(state)); restoring anyway"
    put "$BACKUP/path-map.yaml" "$ROOT/$MAP" || die "the map could not be restored"
    show after-undo
    cmp -s "$BACKUP/path-map.yaml" "$ROOT/$MAP" && [ "$(state)" = before ] || die "the restored map differs from the backup"
    echo "undo: done; the map is byte for byte as before the apply" ;;
  *)
    echo "usage: bash apply.sh check|apply|undo" >&2; exit 2 ;;
esac
