#!/usr/bin/env bash
# ACT-GUARD-CALLLOG-1 (DEC-1106 (2)): the operator's check, apply and undo.
#   bash apply.sh check  [--calls-dir DIR]   the hook and the draft hash as built; which state the tree is in; changes nothing
#   bash apply.sh apply  [--calls-dir DIR]   the log folder and its salt, a backup of the hook (with sha256s), the hook
#   bash apply.sh undo   [--calls-dir DIR]   the hook back byte for byte; the log folder left as the record (see below)
# The changes:
#   1. ~/.gov-os/guard-calls/ (DIR)         a new folder, mode 0700, outside every tree, the run clones and the sets root,
#      with salt.key (0400): 32 random bytes as 64 hex characters, the key of the log's keyed hashes. It is made before
#      the hook changes, so the first line carries its keyed hash. Never printed. An existing folder with a valid
#      salt (an earlier apply, then undo) is kept as it is, so the keyed hashes stay comparable across the gap.
#   2. .claude/hooks/pretooluse.py          replaced by pretooluse.candidate.py: the call log, nothing else
# undo restores the hook. It removes the log folder only when it holds nothing but the salt this apply wrote; a
# folder holding logged calls is the record and stays (the owner removes it by hand if wanted).
# It changes only the tree it sits in (found from its own place: <tree>/.gov-runtime/scratch/orchestrator/drafts/
# guard-calllog/) and DIR. It commits nothing: the operator's commit follows (ACT §5).
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT=$(cd "$HERE/../../../../.." && pwd)
CALLS=$HOME/.gov-os/guard-calls
cmd=${1:-}; shift || true
while [ $# -gt 0 ]; do
  case "$1" in
    --calls-dir) CALLS=$2; shift 2 ;;
    *) echo "usage: bash apply.sh check|apply|undo [--calls-dir DIR]" >&2; exit 2 ;;
  esac
done
HOOK=.claude/hooks/pretooluse.py
KEY=salt.key
BACKUP=$HERE/backup
# The hashes as built (2026-11-09, on w2/integrate; the hook as ACT-INDEP-WALLS-1 left it, 147706ae)
BEFORE_HOOK=d5be03dbb48ed6b9a3b60364afc39c61db11cac65a1b93c0889f5999aa6ef74c
AFTER_HOOK=a7981319f877846d6a62a6768ca036a5014dc7d9f8aadd09e54e61af8251d7d0

die() { echo "apply.sh: $*; nothing more is done" >&2; exit 1; }
sha() { sha256sum "$1" | cut -d' ' -f1; }
[ -d "$ROOT/.git" ] || [ -f "$ROOT/.git" ] || die "$ROOT is not a git tree"
[ -f "$ROOT/$HOOK" ] || die "$ROOT has no $HOOK"
case "$CALLS" in /*) ;; *) die "--calls-dir must be an absolute path" ;; esac
CALLS=$(realpath -m "$CALLS")
for t in "$ROOT" "$HOME/gov-os-worktrees" "$HOME/gov-os-runs" "$HOME/gov-os-eval"; do  # never in a tree or the sets root
  case "$CALLS/" in "$(realpath -m "$t")"/*) die "the log folder $CALLS is inside $t" ;; esac
done

salt_ok() { [ -f "$CALLS/$KEY" ] && [ ! -L "$CALLS/$KEY" ] && grep -qxE '[0-9a-f]{64}' "$CALLS/$KEY"; }
folder_ok() { [ -d "$CALLS" ] && [ ! -L "$CALLS" ] && [ "$(stat -c %u "$CALLS")" = "$(id -u)" ]; }
calls_state() {  # absent | ready (a 0700 folder with a valid salt) | bad
  if [ ! -e "$CALLS" ] && [ ! -L "$CALLS" ]; then echo absent
  elif folder_ok && salt_ok && [ "$(stat -c %a "$CALLS")" = 700 ]; then echo ready
  else echo bad; fi
}
state() {  # before | applied | other
  local h c; h=$(sha "$ROOT/$HOOK"); c=$(calls_state)
  if [ "$h" = "$BEFORE_HOOK" ] && [ "$c" != bad ]; then echo before
  elif [ "$h" = "$AFTER_HOOK" ] && [ "$c" = ready ]; then echo applied
  else echo other; fi
}
show() {
  echo "$1: $(sha "$ROOT/$HOOK")  $HOOK"
  local c n; c=$(calls_state)
  n=$( [ -d "$CALLS" ] && find "$CALLS" -maxdepth 1 -name '????-??-??.jsonl' | wc -l || echo 0)
  echo "$1: log folder $CALLS: $c ($n day files)"
  echo "$1: state $(state)"
}
drafts_ok() {
  [ "$(sha "$HERE/pretooluse.candidate.py")" = "$AFTER_HOOK" ] || die "pretooluse.candidate.py is not as built"
}
put() {  # put file $1 at $2 by a rename in $2's folder, with $2's mode
  local tmp; tmp=$(mktemp "$(dirname "$2")/.guard-calllog.XXXXXX")
  cp -p "$1" "$tmp" || { rm -f "$tmp"; return 1; }
  [ -e "$2" ] && chmod --reference="$2" "$tmp"
  mv -f "$tmp" "$2" || { rm -f "$tmp"; return 1; }
}

echo "apply.sh $cmd: tree $ROOT, log folder $CALLS"
case "$cmd" in
  check)
    show now
    drafts_ok && echo "drafts: pretooluse.candidate.py as built"
    case "$(state)" in
      before) echo "check: ready to apply" ;;
      applied) echo "check: already applied" ;;
      *) die "the tree is neither as before nor as applied (the hook has moved since the build, or the log folder is not a 0700 folder with a valid salt: ask the CTO to rebuild and re-rehearse)" ;;
    esac ;;
  apply)
    show before
    [ "$(state)" = before ] || die "the tree is not in the state before (state $(state))"
    drafts_ok
    [ -e "$BACKUP" ] && die "$BACKUP exists already (an earlier apply): move it aside first"
    mkdir -p "$BACKUP"
    cp -p "$ROOT/$HOOK" "$BACKUP/pretooluse.py"
    ( cd "$BACKUP" && sha256sum pretooluse.py ) > "$BACKUP/SHA256SUMS"
    [ "$(sha "$BACKUP/pretooluse.py")" = "$BEFORE_HOOK" ] || die "the backup does not hash as before"
    echo "backup: $BACKUP (SHA256SUMS written)"
    if [ "$(calls_state)" = absent ]; then
      mkdir -p "$(dirname "$CALLS")"
      mkdir -m 0700 "$CALLS" || die "$CALLS could not be made"
      ( umask 077; python3 -c 'import secrets; print(secrets.token_hex(32))' > "$CALLS/.salt.tmp" ) \
        && chmod 0400 "$CALLS/.salt.tmp" && mv "$CALLS/.salt.tmp" "$CALLS/$KEY" || die "the salt could not be written"
      echo "log folder: made (0700), salt written (0400; never shown)"
      echo made > "$BACKUP/CALLS"
    else
      echo "log folder: kept as it was (a valid salt from an earlier apply)"
      echo kept > "$BACKUP/CALLS"
    fi
    sha "$CALLS/$KEY" > "$BACKUP/SALT.sha256"  # the salt's hash, not the salt: tells undo it is this apply's
    put "$HERE/pretooluse.candidate.py" "$ROOT/$HOOK" || die "the hook could not be replaced: run undo"
    show after
    [ "$(state)" = applied ] || die "the tree does not hash as applied: run undo"
    echo "apply: done. The operator's commit stages:"
    echo "  git add $HOOK" ;;
  undo)
    show before-undo
    [ -f "$BACKUP/pretooluse.py" ] && [ "$(sha "$BACKUP/pretooluse.py")" = "$BEFORE_HOOK" ] \
      || die "no backup in $BACKUP, or one that does not hash as before the apply"
    [ "$(state)" = applied ] || echo "undo: note: the tree has changed since the apply (state $(state)); restoring anyway"
    put "$BACKUP/pretooluse.py" "$ROOT/$HOOK" || die "the hook could not be restored"
    cmp -s "$BACKUP/pretooluse.py" "$ROOT/$HOOK" || die "the restored hook differs from the backup"
    echo "hook: restored byte for byte"
    if [ -d "$CALLS" ] && [ "$(cat "$BACKUP/CALLS" 2>/dev/null)" = made ] \
       && [ "$(find "$CALLS" -mindepth 1 | wc -l)" = 1 ] && salt_ok \
       && [ "$(sha "$CALLS/$KEY")" = "$(cat "$BACKUP/SALT.sha256")" ]; then
      rm -f "$CALLS/$KEY" && rmdir "$CALLS" && echo "log folder: removed (it held only this apply's salt)"
    elif [ -d "$CALLS" ]; then
      echo "log folder: left in place, the record ($(find "$CALLS" -maxdepth 1 -name '????-??-??.jsonl' | wc -l) day files, $(cat "$CALLS"/*.jsonl 2>/dev/null | wc -l) lines); the hook no longer writes it"
    fi
    show after-undo
    [ "$(sha "$ROOT/$HOOK")" = "$BEFORE_HOOK" ] || die "the hook does not hash as before"
    echo "undo: done; the hook byte for byte as before" ;;
  *)
    echo "usage: bash apply.sh check|apply|undo [--calls-dir DIR]" >&2; exit 2 ;;
esac
