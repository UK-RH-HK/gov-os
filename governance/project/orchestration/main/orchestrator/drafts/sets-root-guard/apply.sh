#!/usr/bin/env bash
# DEC-1082 (3), DEC-1097 (2), the sets-root guard (ACT-GUARD-SETS-1, rebuilt 2026-11-08): the operator's check, apply
# and undo of everything the ACT changes:
#   - .claude/hooks/pretooluse.py          replaced by pretooluse.candidate.py
#   - governance/project/path-map.yaml     patched by path-map.patch (the sets_root_hidden block)
#   - tests/optin-lifted-guard.txt         patched by optin-lifted-guard.patch (W2-84's lines out, DEC-1061 (4))
#   - W2-84's seven hidden-half test files deleted (DEC-1061 (4), DEC-1097 (2)), listed in DEL below
#   bash apply.sh check   every file's hash, which state the tree is in, the candidate and both patches checked
#                         (changes nothing)
#   bash apply.sh apply   back every file up (with their sha256), put the candidate hook in place, patch the map and
#                         the list, delete the seven files, then check the hashes after
#   bash apply.sh undo    put every backed-up file back, byte for byte (the seven deleted files too), and check them
# It changes only those files of the tree it sits in (found from this file's own place:
# <tree>/.gov-runtime/scratch/orchestrator/drafts/sets-root-guard/), and writes its backups beside itself (backup/).
# It runs no hook and reads nothing under the sets root. It commits nothing: the operator's commit follows (ACT §3).
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT=$(cd "$HERE/../../../../.." && pwd)
HOOK=.claude/hooks/pretooluse.py
MAP=governance/project/path-map.yaml
LIST=tests/optin-lifted-guard.txt
CAND=$HERE/pretooluse.candidate.py
PATCH=$HERE/path-map.patch
LPATCH=$HERE/optin-lifted-guard.patch
BACKUP=$HERE/backup
# The hashes as built on 2026-11-08 (w2/integrate e66f2a69; the candidate hook with the line rule of readiness review 5
# F1; the live hook as ACT-G14 left it, unchanged since the first
# build; the map with W2-61h's evaluation_families; the list as D-4 left it). A file that has moved since stops every
# command but undo.
BEFORE_HOOK=e406653ef6c92f014a6b874598b6a3e03fbc270310ecbfdd9c7b079ca43f7cc3
BEFORE_MAP=6d79946fdbbd10e3095d99d13c216f475144b6330cfd8695cfd69bf839cf940b
BEFORE_LIST=98f3b69a8ed96889272256afcd932b6a56a82cf25cd3dfb7048586291da0dde3
AFTER_HOOK=bd545af83198962e6c8ecff59afbf86519ae5f201d6660a34941d6aaaa584449
AFTER_MAP=a9d8b97267c44f519cef37d4b5b702bbb9f2a696a17fa26f68147d2851f04b22
AFTER_LIST=868b6e1c84642fee84811affa285ab42dab2c42a6de428975768ae0a0c810a02
# W2-84's hidden-half cases (tests/optin-lifted-guard.txt, "Decision 4"), each with its sha256 as built.
DEL=(
  "tests/acceptance/W2-84/test_w2_84_code_under_test.py 5c30ab77becbebf7c34119fa93701dbc78ac05e9e00c27e0e3242a6b5c000922"
  "tests/acceptance/W2-84/test_w2_84_every_tree.py 0c6b02904b8905736ac5071bf9b9758634607ee599404f65060e96562d8de1eb"
  "tests/acceptance/W2-84/test_w2_84_fails_closed.py ef6c3dcb0f3e591cd0134ade3b51d1cee9efe136e39288366de695dd32482092"
  "tests/acceptance/W2-84/test_w2_84_git_store.py 789d7f76826794bc48ea07708d2fb09ec1e75a44d21b079053896bf1cd48aaef"
  "tests/acceptance/W2-84/test_w2_84_links.py e268aba3aadd9f5c000b9667e982a1f760dd295ff60a6a4f007f273962544554"
  "tests/acceptance/W2-84/test_w2_84_unchanged.py 54ffe77873568d619b58e3cb433ce173a83ca9a2c6b4240bdcf5efafab4f4478"
  "tests/unit/guard/test_w2_84_trees.py ac2dbd7398a60a28cca4c18f7a363353330efcf9cdee51052af1a5b52a8d274f"
)

die() { echo "apply.sh: $*; nothing more is done" >&2; exit 1; }
sha() { sha256sum "$1" | cut -d' ' -f1; }
[ -d "$ROOT/.git" ] || [ -f "$ROOT/.git" ] || die "$ROOT is not a git tree"
[ -f "$ROOT/$HOOK" ] && [ -f "$ROOT/$MAP" ] && [ -f "$ROOT/$LIST" ] || die "$ROOT has no $HOOK, $MAP or $LIST"

dels() {  # all | none | some: how many of the seven files are present with their hashes as built
  local n=0 gone=0 e p h
  for e in "${DEL[@]}"; do
    p=${e% *}; h=${e#* }
    if [ ! -e "$ROOT/$p" ]; then gone=$((gone + 1))
    elif [ "$(sha "$ROOT/$p")" = "$h" ]; then n=$((n + 1)); fi
  done
  if [ "$n" = "${#DEL[@]}" ]; then echo all; elif [ "$gone" = "${#DEL[@]}" ]; then echo none; else echo some; fi
}
state() {  # before | applied | other, for every file together
  local h m l d; h=$(sha "$ROOT/$HOOK"); m=$(sha "$ROOT/$MAP"); l=$(sha "$ROOT/$LIST"); d=$(dels)
  if [ "$h" = "$BEFORE_HOOK" ] && [ "$m" = "$BEFORE_MAP" ] && [ "$l" = "$BEFORE_LIST" ] && [ "$d" = all ]; then
    echo before
  elif [ "$h" = "$AFTER_HOOK" ] && [ "$m" = "$AFTER_MAP" ] && [ "$l" = "$AFTER_LIST" ] && [ "$d" = none ]; then
    echo applied
  else echo other; fi
}
show() {  # $1: a label
  local e p
  echo "$1: $(sha "$ROOT/$HOOK")  $HOOK"
  echo "$1: $(sha "$ROOT/$MAP")  $MAP"
  echo "$1: $(sha "$ROOT/$LIST")  $LIST"
  for e in "${DEL[@]}"; do
    p=${e% *}
    if [ -e "$ROOT/$p" ]; then echo "$1: $(sha "$ROOT/$p")  $p"; else echo "$1: (absent)  $p"; fi
  done
  echo "$1: state $(state)"
}
patched() {  # file $1 with patch $2 applied, written to $3
  patch --quiet --no-backup-if-mismatch -r /dev/null -o "$3" "$1" "$2" >/dev/null || return 1
}
put() {  # put file $1 at $2 by a rename in $2's folder, with $1's mode (cp -p), or $2's when $2 exists
  local tmp; mkdir -p "$(dirname "$2")"; tmp=$(mktemp "$(dirname "$2")/.sets-root-guard.XXXXXX")
  cp -p "$1" "$tmp" || { rm -f "$tmp"; return 1; }
  if [ -e "$2" ]; then chmod --reference="$2" "$tmp" || { rm -f "$tmp"; return 1; }; fi
  mv -f "$tmp" "$2" || { rm -f "$tmp"; return 1; }
}
backups_ok() {  # every backup present and hashing as before
  local e p h
  [ -f "$BACKUP/pretooluse.py" ] && [ -f "$BACKUP/path-map.yaml" ] && [ -f "$BACKUP/optin-lifted-guard.txt" ] || return 1
  [ "$(sha "$BACKUP/pretooluse.py")" = "$BEFORE_HOOK" ] && [ "$(sha "$BACKUP/path-map.yaml")" = "$BEFORE_MAP" ] \
    && [ "$(sha "$BACKUP/optin-lifted-guard.txt")" = "$BEFORE_LIST" ] || return 1
  for e in "${DEL[@]}"; do
    p=${e% *}; h=${e#* }
    [ -f "$BACKUP/del/$p" ] && [ "$(sha "$BACKUP/del/$p")" = "$h" ] || return 1
  done
}

cmd=${1:-}
echo "apply.sh $cmd: tree $ROOT"
case "$cmd" in
  check)
    show now
    [ "$(sha "$CAND")" = "$AFTER_HOOK" ] && echo "candidate hook: ok ($AFTER_HOOK)" || die "the candidate hook's hash is not $AFTER_HOOK"
    python3 -c 'import ast, sys; ast.parse(open(sys.argv[1]).read())' "$CAND" && echo "candidate hook: parses"
    if [ "$(state)" = before ]; then
      t=$(mktemp); patched "$ROOT/$MAP" "$PATCH" "$t" || { rm -f "$t"; die "the patch does not apply to $MAP"; }
      got=$(sha "$t"); rm -f "$t"
      [ "$got" = "$AFTER_MAP" ] && echo "map patch: applies, gives $AFTER_MAP" || die "the patched map hashes to $got, not $AFTER_MAP"
      t=$(mktemp); patched "$ROOT/$LIST" "$LPATCH" "$t" || { rm -f "$t"; die "the patch does not apply to $LIST"; }
      got=$(sha "$t"); rm -f "$t"
      [ "$got" = "$AFTER_LIST" ] && echo "list patch: applies, gives $AFTER_LIST" || die "the patched list hashes to $got, not $AFTER_LIST"
      echo "W2-84's seven files: present, each as built"
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
    t=$(mktemp); u=$(mktemp)
    patched "$ROOT/$MAP" "$PATCH" "$t" || { rm -f "$t" "$u"; die "the patch does not apply to $MAP"; }
    [ "$(sha "$t")" = "$AFTER_MAP" ] || { rm -f "$t" "$u"; die "the patched map does not hash to $AFTER_MAP"; }
    patched "$ROOT/$LIST" "$LPATCH" "$u" || { rm -f "$t" "$u"; die "the patch does not apply to $LIST"; }
    [ "$(sha "$u")" = "$AFTER_LIST" ] || { rm -f "$t" "$u"; die "the patched list does not hash to $AFTER_LIST"; }
    [ -e "$BACKUP" ] && { rm -f "$t" "$u"; die "$BACKUP exists already (an earlier apply): move it aside first"; }
    mkdir -p "$BACKUP"
    cp -p "$ROOT/$HOOK" "$BACKUP/pretooluse.py"
    cp -p "$ROOT/$MAP" "$BACKUP/path-map.yaml"
    cp -p "$ROOT/$LIST" "$BACKUP/optin-lifted-guard.txt"
    for e in "${DEL[@]}"; do
      p=${e% *}; mkdir -p "$BACKUP/del/$(dirname "$p")"; cp -p "$ROOT/$p" "$BACKUP/del/$p"
    done
    ( cd "$BACKUP" && sha256sum pretooluse.py path-map.yaml optin-lifted-guard.txt && \
      for e in "${DEL[@]}"; do sha256sum "del/${e% *}"; done ) > "$BACKUP/SHA256SUMS.tmp"
    mv "$BACKUP/SHA256SUMS.tmp" "$BACKUP/SHA256SUMS"
    backups_ok || { rm -f "$t" "$u"; die "the backups do not hash as before"; }
    echo "backup: $BACKUP (SHA256SUMS written, $(wc -l < "$BACKUP/SHA256SUMS") files)"
    put "$CAND" "$ROOT/$HOOK" || { rm -f "$t" "$u"; die "the hook could not be put in place (nothing else is changed)"; }
    put "$t" "$ROOT/$MAP" || { rm -f "$t" "$u"; die "the map could not be patched (the hook IS changed: run undo)"; }
    put "$u" "$ROOT/$LIST" || { rm -f "$t" "$u"; die "the list could not be patched (the hook and map ARE changed: run undo)"; }
    rm -f "$t" "$u"
    for e in "${DEL[@]}"; do
      rm -f "$ROOT/${e% *}" || die "${e% *} could not be deleted (run undo)"
    done
    show after
    [ "$(state)" = applied ] || die "the files do not hash as applied: run undo"
    echo "apply: done. The operator's commit stages the three files and the seven deletions:"
    echo "  git add $HOOK $MAP $LIST"
    printf '  git rm -q --'; for e in "${DEL[@]}"; do printf ' %s' "${e% *}"; done; echo ;;
  undo)
    show before-undo
    backups_ok || die "no backup in $BACKUP, or one that does not hash as the files before the apply"
    [ "$(state)" = applied ] || echo "undo: note: the files have changed since the apply (state $(state)); restoring anyway"
    put "$BACKUP/pretooluse.py" "$ROOT/$HOOK" || die "the hook could not be restored"
    put "$BACKUP/path-map.yaml" "$ROOT/$MAP" || die "the map could not be restored (the hook IS restored)"
    put "$BACKUP/optin-lifted-guard.txt" "$ROOT/$LIST" || die "the list could not be restored (the hook and map ARE restored)"
    for e in "${DEL[@]}"; do
      p=${e% *}; put "$BACKUP/del/$p" "$ROOT/$p" || die "$p could not be restored"
    done
    show after-undo
    same=1
    cmp -s "$BACKUP/pretooluse.py" "$ROOT/$HOOK" && cmp -s "$BACKUP/path-map.yaml" "$ROOT/$MAP" \
      && cmp -s "$BACKUP/optin-lifted-guard.txt" "$ROOT/$LIST" || same=0
    for e in "${DEL[@]}"; do
      p=${e% *}; cmp -s "$BACKUP/del/$p" "$ROOT/$p" && [ "$(stat -c %a "$BACKUP/del/$p")" = "$(stat -c %a "$ROOT/$p")" ] || same=0
    done
    [ "$same" = 1 ] && [ "$(state)" = before ] || die "the restored files differ from the backups"
    echo "undo: done; every file is byte for byte as before the apply (the seven deleted files restored, modes kept)" ;;
  *)
    echo "usage: bash apply.sh check|apply|undo" >&2; exit 2 ;;
esac
