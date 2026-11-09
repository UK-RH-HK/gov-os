#!/usr/bin/env bash
# DEC-1103 (2), ACT-D4-RESTORE-1: D-4's 3 capped and 7 lifted cases back into the gates (DEC-1061's cut amended for
# these ten). The operator's check, apply and undo of the three opt-in lists the ACT changes:
#   - tests/optin-lifted-breadth.txt   patched by optin-lifted-breadth.patch: the three `# cap` lines of K8 (W1-08),
#                                      K9 (W1-27) and K18c (W1-06) commented out with DEC-1103 (2)
#   - tests/optin-lifted-guard.txt     patched by optin-lifted-guard.patch: the four lifted cases of K2 (W1-33 x2, W1-46,
#                                      W1-05) commented out with DEC-1103 (2)
#   - tests/optin-lifted.txt           patched by optin-lifted.patch: K1's W2-71 premise case and K8's two W1-26
#                                      probe-record cases un-lifted; the suite's and the file's lines commented out with
#                                      DEC-1103 (2) and replaced by their other parts, each still lifted
#   bash apply.sh check   every file's hash, which state the tree is in, every patch checked (changes nothing)
#   bash apply.sh apply   back every file up (with their sha256), patch them, then check the hashes after
#   bash apply.sh undo    put every backed-up file back, byte for byte, and check them
# It changes only those files of the tree it sits in (found from this file's own place:
# <tree>/.gov-runtime/scratch/orchestrator/drafts/d4-restore/), and writes its backups beside itself (backup/).
# It runs no test and no hook. It commits nothing: the operator's commit follows (ACT-D4-RESTORE-1 §3).
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT=$(cd "$HERE/../../../../.." && pwd)
BACKUP=$HERE/backup
# file | patch | sha256 before | sha256 after. As built on 2026-11-09 (w2/integrate 8b7bfe867: optin-lifted.txt as
# f551589dd left it, optin-lifted-guard.txt as 15952bbfa left it, optin-lifted-breadth.txt as ACT-SELECT-FIXES-1 left it,
# 8038e0ee6). A file that has moved since stops every command but undo.
FILES=(
  "tests/optin-lifted-breadth.txt|optin-lifted-breadth.patch|332f0a676f0587e5cc3693eb7da09b8655eeb9d963ac88e058e0a1b57d868502|3528cd1ffbb07d1f7ea0d4a50bfe400f937d7702dc60af0718b6a184f6d1ad8b"
  "tests/optin-lifted-guard.txt|optin-lifted-guard.patch|868b6e1c84642fee84811affa285ab42dab2c42a6de428975768ae0a0c810a02|dfdef9b085417a7d8bf4a14439f2f69c0c11cb4d171b5c812a71bca0e9c63610"
  "tests/optin-lifted.txt|optin-lifted.patch|bc67a6f3fe5fa670139aac8649eaf23d49bdb51858ed49a93ec5b4b900191ce1|29a2cc1033b9466a9c54cf8f51de211b5928d6f69c994f6ae1ddef1227223e01"
)
# Variant B (`bash apply.sh <cmd> B`; ACT-D4-RESTORE-1 §5, the CTO's option, not decided): the guard list loses only
# W1-33's orchestrator case; the three K2 cases red by the guard's switched-off features stay lifted.
VARIANT=${2:-A}
case "$VARIANT" in
  A) ;;
  B) FILES[1]="tests/optin-lifted-guard.txt|optin-lifted-guard.B.patch|868b6e1c84642fee84811affa285ab42dab2c42a6de428975768ae0a0c810a02|69a969e803bbb56dec0b37340969e80e740806f7ab42a5722f4078d5579d7501" ;;
  *) echo "usage: bash apply.sh check|apply|undo [A|B]" >&2; exit 2 ;;
esac

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
  local tmp; tmp=$(mktemp "$(dirname "$2")/.d4-restore.XXXXXX")
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
echo "apply.sh $cmd (variant $VARIANT): tree $ROOT"
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
    echo "apply: done. The operator's commit stages the three lists:"
    echo "  git add tests/optin-lifted-breadth.txt tests/optin-lifted-guard.txt tests/optin-lifted.txt" ;;
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
