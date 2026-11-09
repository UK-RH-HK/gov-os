#!/usr/bin/env bash
# DEC-1100 (1), ACT-SELECT-FIXES-1 (P-SELECT-FIXES-1 (i) and (ii); F1 (a), the CTO's choice of 2026-11-09): the
# operator's check, apply and undo of the three files the ACT changes:
#   - governance/project/test-map.yaml       patched by test-map.patch: (i) three couplings and the W1-50 case on W1-28's
#                                            entry; (ii) W2-66's record-only case at the end of record_reading; F1 (a) the
#                                            four records that case finds unplaced, in record_only
#   - tests/optin-lifted-breadth.txt         patched by optin-lifted-breadth.patch: F1 (a) the `rep:` line of W2-66's
#                                            record-only case dropped, so a selection runs all its rows
#   - .gov-runtime/scratch/orchestrator/tools/record_checks.sh   patched by record_checks.patch: (ii) the same case
#                                            before the CTO's record commits (DEC-868 item 2; not tracked)
#   bash apply.sh check   every file's hash, which state the tree is in, every patch checked (changes nothing)
#   bash apply.sh apply   back every file up (with their sha256), patch them, then check the hashes after
#   bash apply.sh undo    put every backed-up file back, byte for byte, and check them
# It changes only those files of the tree it sits in (found from this file's own place:
# <tree>/.gov-runtime/scratch/orchestrator/drafts/select-fixes/act/), and writes its backups beside itself (backup/).
# It runs no test and no hook. It commits nothing: the operator's commit follows (ACT-SELECT-FIXES-1 §3).
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT=$(cd "$HERE/../../../../../.." && pwd)
BACKUP=$HERE/backup
# file | patch | sha256 before | sha256 after. As built on 2026-11-09 (w2/integrate 2e10e8aba: the map as D-4 left it,
# d3d757f3b; the breadth list as D-4's cut round 2 left it, 27cb63070; record_checks.sh as DEC-911 (b) left it). A file
# that has moved since stops every command but undo.
FILES=(
  "governance/project/test-map.yaml|test-map.patch|2001c392a3fbb516d00b01d51e277e137b7becd9df735557c61d12ffce86ba57|42e22dd70a05546e99fd7f2503c109a417ee6d1c11ebfddc42dfee5ff8f1a665"
  "tests/optin-lifted-breadth.txt|optin-lifted-breadth.patch|240bc62a826ddfc1e8dd270b84994f402c4033c97b8242604685613f1c46fd66|332f0a676f0587e5cc3693eb7da09b8655eeb9d963ac88e058e0a1b57d868502"
  ".gov-runtime/scratch/orchestrator/tools/record_checks.sh|record_checks.patch|81b758648843e6093f45b91f705e7d110e1125bc3dfce65ccdd47181aaebb0a6|d80b4eae5c56c066cc5e9b0c327b230390f03766962a566ebf66f2fe427cf14c"
)

die() { echo "apply.sh: $*; nothing more is done" >&2; exit 1; }
sha() { sha256sum "$1" | cut -d' ' -f1; }
field() { local IFS='|'; read -ra f <<< "$1"; echo "${f[$2]}"; }
[ -d "$ROOT/.git" ] || [ -f "$ROOT/.git" ] || die "$ROOT is not a git tree"
for e in "${FILES[@]}"; do [ -f "$ROOT/$(field "$e" 0)" ] || die "$ROOT has no $(field "$e" 0)"; done

state() {  # before | applied | other, for every file together
  local b=0 a=0 e h
  for e in "${FILES[@]}"; do
    h=$(sha "$ROOT/$(field "$e" 0)")
    [ "$h" = "$(field "$e" 2)" ] && b=$((b + 1)); [ "$h" = "$(field "$e" 3)" ] && a=$((a + 1))
  done
  if [ "$b" = "${#FILES[@]}" ]; then echo before; elif [ "$a" = "${#FILES[@]}" ]; then echo applied; else echo other; fi
}
show() { local e; for e in "${FILES[@]}"; do echo "$1: $(sha "$ROOT/$(field "$e" 0)")  $(field "$e" 0)"; done; echo "$1: state $(state)"; }
patched() { patch --quiet --no-backup-if-mismatch -r /dev/null -o "$3" "$1" "$2" >/dev/null || return 1; }  # $1+$2 -> $3
put() {  # file $1 at $2 by a rename in $2's folder, with $2's mode
  local tmp; tmp=$(mktemp "$(dirname "$2")/.select-fixes.XXXXXX")
  cp -p "$1" "$tmp" && chmod --reference="$2" "$tmp" && mv -f "$tmp" "$2" || { rm -f "$tmp"; return 1; }
}
backups_ok() { local e; for e in "${FILES[@]}"; do
  local b; b=$BACKUP/$(basename "$(field "$e" 0)"); [ -f "$b" ] && [ "$(sha "$b")" = "$(field "$e" 2)" ] || return 1; done; }
TMPS=()
cleanup() { [ ${#TMPS[@]} -gt 0 ] && rm -f "${TMPS[@]}"; return 0; }
trap cleanup EXIT
build() {  # every patched file into a temporary, each checked against its hash after; the temporaries in TMPS
  local e t got
  for e in "${FILES[@]}"; do
    t=$(mktemp); TMPS+=("$t")
    patched "$ROOT/$(field "$e" 0)" "$HERE/$(field "$e" 1)" "$t" || die "the patch does not apply to $(field "$e" 0)"
    got=$(sha "$t"); [ "$got" = "$(field "$e" 3)" ] || die "the patched $(field "$e" 0) hashes to $got, not $(field "$e" 3)"
  done
}

cmd=${1:-}
echo "apply.sh $cmd: tree $ROOT"
case "$cmd" in
  check)
    show now
    if [ "$(state)" = before ]; then
      build; for e in "${FILES[@]}"; do echo "$(field "$e" 1): applies, gives $(field "$e" 3)"; done
    fi
    case "$(state)" in
      before) echo "check: ready to apply" ;;
      applied) echo "check: already applied" ;;
      *) die "the files are neither as before nor as applied (they have moved since the build: ask the CTO)" ;;
    esac ;;
  apply)
    show before
    [ "$(state)" = before ] || die "the files are not in the state before (state $(state))"
    build
    [ -e "$BACKUP" ] && die "$BACKUP exists already (an earlier apply): move it aside first"
    mkdir -p "$BACKUP"
    for e in "${FILES[@]}"; do cp -p "$ROOT/$(field "$e" 0)" "$BACKUP/"; done
    ( cd "$BACKUP" && for e in "${FILES[@]}"; do sha256sum "$(basename "$(field "$e" 0)")"; done ) > "$BACKUP/SHA256SUMS"
    backups_ok || die "the backups do not hash as before"
    echo "backup: $BACKUP (SHA256SUMS written, ${#FILES[@]} files)"
    i=0
    for e in "${FILES[@]}"; do
      put "${TMPS[$i]}" "$ROOT/$(field "$e" 0)" || die "$(field "$e" 0) could not be patched ($i before it ARE changed: run undo)"
      i=$((i + 1))
    done
    show after
    [ "$(state)" = applied ] || die "the files do not hash as applied: run undo"
    echo "apply: done. The operator's commit stages the map and the breadth list (record_checks.sh is the CTO's untracked tool):"
    echo "  git add governance/project/test-map.yaml tests/optin-lifted-breadth.txt" ;;
  undo)
    show before-undo
    backups_ok || die "no backup in $BACKUP, or one that does not hash as the files before the apply"
    [ "$(state)" = applied ] || echo "undo: note: the files have changed since the apply (state $(state)); restoring anyway"
    for e in "${FILES[@]}"; do
      put "$BACKUP/$(basename "$(field "$e" 0)")" "$ROOT/$(field "$e" 0)" || die "$(field "$e" 0) could not be restored"
    done
    show after-undo
    for e in "${FILES[@]}"; do cmp -s "$BACKUP/$(basename "$(field "$e" 0)")" "$ROOT/$(field "$e" 0)" || die "$(field "$e" 0) differs from its backup"; done
    [ "$(state)" = before ] || die "the restored files do not hash as before"
    echo "undo: done; every file is byte for byte as before the apply" ;;
  *)
    echo "usage: bash apply.sh check|apply|undo" >&2; exit 2 ;;
esac
