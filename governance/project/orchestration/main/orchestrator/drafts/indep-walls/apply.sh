#!/usr/bin/env bash
# ACT-INDEP-WALLS-1 (DEC-1101 (2)-(3) step 1; DEC-1099 (1) Q6 folded in): the operator's check, apply and undo.
#   bash apply.sh check  [--sets-root DIR]   every file hashes as built; which state the tree is in; changes nothing
#   bash apply.sh apply  [--sets-root DIR]   backups (with sha256s), then the four changes below, then the hashes after
#   bash apply.sh undo   [--sets-root DIR]   everything back byte for byte; refuses while a wall run exists
# The changes:
#   1. governance/project/path-map.yaml   replaced by path-map.candidate.yaml: the seal (ACT-SANDBOX-SEAL-1's patch:
#      the evaluation set sandbox-guard-exp-1 and its glob in sets_root_hidden), "indep-walls/**" in sets_root_hidden, and
#      the new block session_hidden (the W2-56 tuner refused ~/.claude/projects)
#   2. .claude/hooks/pretooluse.py        replaced by pretooluse.candidate.py: rule 2c (session_hidden), nothing else
#   3. governance/project/indep-walls/    six new files from template/ (the walls' template)
#   4. <sets root>/indep-walls/APPROVED         a new folder and file (mode 0700/0400): the template files' sha256s, the list
#      the launch script checks; the briefs' lines are added at DEC-1101 (3) step 3
# It changes only the tree it sits in (found from its own place: <tree>/.gov-runtime/scratch/orchestrator/drafts/
# indep-walls/) and the sets root (default ~/gov-os-eval). It reads nothing under the sets root but walls/. It commits
# nothing: the operator's commit follows (ACT §3).
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT=$(cd "$HERE/../../../../.." && pwd)
SETS=$HOME/gov-os-eval
cmd=${1:-}; shift || true
while [ $# -gt 0 ]; do
  case "$1" in
    --sets-root) SETS=$2; shift 2 ;;
    *) echo "usage: bash apply.sh check|apply|undo [--sets-root DIR]" >&2; exit 2 ;;
  esac
done
WALLS=$SETS/indep-walls
HOOK=.claude/hooks/pretooluse.py
MAP=governance/project/path-map.yaml
NEWDIR=governance/project/indep-walls
NEWFILES="README.md settings.json.tmpl wall_hook.py CLAUDE.md.tmpl kinds.yaml tree-exclude.txt"
BACKUP=$HERE/backup
# The hashes as built (2026-11-09, on w2/integrate; the hook as ACT-GUARD-SETS-1 left it, the map as that ACT left it)
BEFORE_HOOK=bd545af83198962e6c8ecff59afbf86519ae5f201d6660a34941d6aaaa584449
BEFORE_MAP=a9d8b97267c44f519cef37d4b5b702bbb9f2a696a17fa26f68147d2851f04b22
AFTER_HOOK=d5be03dbb48ed6b9a3b60364afc39c61db11cac65a1b93c0889f5999aa6ef74c
AFTER_MAP=622b0c5b1a7753c44a8c501631a5d5b692b0b7277de8ffca21bb95eda7fce86b
declare -A NEW=(
  [README.md]=65298d3468484515ca18e2dd3db5e6eb867221f1d9d6318e5e07998a2a5aef49
  [settings.json.tmpl]=9b85b9a604d00e5c5aadffedbbb3ff93e51cebe641c73c11dc248374278a609b
  [wall_hook.py]=95638d7d9edb5eb67035248e928652a737e783f39b5860bac93b4958073343d3
  [CLAUDE.md.tmpl]=aee245ce7a8034565d9c304820ece8091946b1d9898d34c20a3fb38f93bd9267
  [kinds.yaml]=8b50a78f01b316d0bd5d41689cd3730da0e3142ac4c54705dc83bad0ace4d74f
  [tree-exclude.txt]=21660e1ee5adf793e46d59e601cef662ef8a445399da185bd9397bc6067d47a6
)

die() { echo "apply.sh: $*; nothing more is done" >&2; exit 1; }
sha() { sha256sum "$1" | cut -d' ' -f1; }
[ -d "$ROOT/.git" ] || [ -f "$ROOT/.git" ] || die "$ROOT is not a git tree"
[ -f "$ROOT/$HOOK" ] && [ -f "$ROOT/$MAP" ] || die "$ROOT has no $HOOK or $MAP"
SETS=$(realpath -m "$SETS"); WALLS=$SETS/indep-walls
[ -d "$SETS" ] || die "the sets root $SETS is not a folder"

approved_text() {  # the APPROVED file's text, from the built template files
  echo "# ACT-INDEP-WALLS-1: the owner's approved list (DEC-1101 (2)). The launch script builds a wall only from files"
  echo "# whose sha256 is here. Written by the owner's operator only; the six refused roles neither read nor write it."
  for n in $NEWFILES; do echo "${NEW[$n]}  template $NEWDIR/$n"; done
}
state() {  # before | applied | other
  local h m n ok=1 none=1
  h=$(sha "$ROOT/$HOOK"); m=$(sha "$ROOT/$MAP")
  for n in $NEWFILES; do
    if [ -e "$ROOT/$NEWDIR/$n" ]; then none=0; [ "$(sha "$ROOT/$NEWDIR/$n")" = "${NEW[$n]}" ] || ok=0; else ok=0; fi
  done
  if [ "$h" = "$BEFORE_HOOK" ] && [ "$m" = "$BEFORE_MAP" ] && [ $none = 1 ] && [ ! -e "$WALLS" ]; then echo before
  elif [ "$h" = "$AFTER_HOOK" ] && [ "$m" = "$AFTER_MAP" ] && [ $ok = 1 ] && [ -f "$WALLS/APPROVED" ]; then echo applied
  else echo other; fi
}
show() {
  echo "$1: $(sha "$ROOT/$HOOK")  $HOOK"
  echo "$1: $(sha "$ROOT/$MAP")  $MAP"
  for n in $NEWFILES; do
    [ -e "$ROOT/$NEWDIR/$n" ] && echo "$1: $(sha "$ROOT/$NEWDIR/$n")  $NEWDIR/$n" || echo "$1: (absent)  $NEWDIR/$n"
  done
  [ -f "$WALLS/APPROVED" ] && echo "$1: $(sha "$WALLS/APPROVED")  <sets root>/indep-walls/APPROVED" \
    || echo "$1: (absent)  <sets root>/indep-walls/APPROVED"
  echo "$1: state $(state)"
}
drafts_ok() {
  [ "$(sha "$HERE/pretooluse.candidate.py")" = "$AFTER_HOOK" ] || die "pretooluse.candidate.py is not as built"
  [ "$(sha "$HERE/path-map.candidate.yaml")" = "$AFTER_MAP" ] || die "path-map.candidate.yaml is not as built"
  for n in $NEWFILES; do [ "$(sha "$HERE/template/$n")" = "${NEW[$n]}" ] || die "template/$n is not as built"; done
}
put() {  # put file $1 at $2 by a rename in $2's folder; mode $3 (or $2's)
  local tmp; tmp=$(mktemp "$(dirname "$2")/.indep-walls.XXXXXX")
  cp -p "$1" "$tmp" || { rm -f "$tmp"; return 1; }
  if [ -n "${3:-}" ]; then chmod "$3" "$tmp"; elif [ -e "$2" ]; then chmod --reference="$2" "$tmp"; fi
  mv -f "$tmp" "$2" || { rm -f "$tmp"; return 1; }
}

echo "apply.sh $cmd: tree $ROOT, sets root $SETS"
case "$cmd" in
  check)
    show now
    drafts_ok && echo "drafts: every file as built"
    case "$(state)" in
      before) echo "check: ready to apply" ;;
      applied) echo "check: already applied" ;;
      *) die "the tree is neither as before nor as applied (a file has moved since the build: ask the CTO to rebuild and re-rehearse)" ;;
    esac ;;
  apply)
    show before
    [ "$(state)" = before ] || die "the tree is not in the state before (state $(state))"
    drafts_ok
    [ -e "$BACKUP" ] && die "$BACKUP exists already (an earlier apply): move it aside first"
    mkdir -p "$BACKUP"
    cp -p "$ROOT/$HOOK" "$BACKUP/pretooluse.py"; cp -p "$ROOT/$MAP" "$BACKUP/path-map.yaml"
    ( cd "$BACKUP" && sha256sum pretooluse.py path-map.yaml ) > "$BACKUP/SHA256SUMS"
    [ "$(sha "$BACKUP/pretooluse.py")" = "$BEFORE_HOOK" ] && [ "$(sha "$BACKUP/path-map.yaml")" = "$BEFORE_MAP" ] \
      || die "the backups do not hash as before"
    echo "backup: $BACKUP (SHA256SUMS written)"
    put "$HERE/path-map.candidate.yaml" "$ROOT/$MAP" || die "the map could not be replaced: run undo"
    put "$HERE/pretooluse.candidate.py" "$ROOT/$HOOK" || die "the hook could not be replaced: run undo"
    mkdir -p "$ROOT/$NEWDIR"
    for n in $NEWFILES; do
      m=0644; [ "$n" = wall_hook.py ] && m=0755
      put "$HERE/template/$n" "$ROOT/$NEWDIR/$n" "$m" || die "$NEWDIR/$n could not be written: run undo"
    done
    mkdir -m 0700 "$WALLS" || die "$WALLS could not be made: run undo"
    approved_text > "$WALLS/APPROVED.tmp" && chmod 0400 "$WALLS/APPROVED.tmp" && mv "$WALLS/APPROVED.tmp" "$WALLS/APPROVED"
    sha "$WALLS/APPROVED" > "$BACKUP/APPROVED.sha256"
    show after
    [ "$(state)" = applied ] || die "the tree does not hash as applied: run undo"
    echo "apply: done. The operator's commit stages:"
    echo "  git add $HOOK $MAP $NEWDIR" ;;
  undo)
    show before-undo
    [ -f "$BACKUP/pretooluse.py" ] && [ "$(sha "$BACKUP/pretooluse.py")" = "$BEFORE_HOOK" ] \
      && [ -f "$BACKUP/path-map.yaml" ] && [ "$(sha "$BACKUP/path-map.yaml")" = "$BEFORE_MAP" ] \
      || die "no backup in $BACKUP, or one that does not hash as before the apply"
    if [ -d "$WALLS" ]; then
      left=$(find "$WALLS" -mindepth 1 -maxdepth 1 ! -name APPROVED | wc -l)
      [ "$left" = 0 ] || die "$WALLS holds $left entries besides APPROVED (wall runs): the walls stay until they are retired"
    fi
    [ "$(state)" = applied ] || echo "undo: note: the tree has changed since the apply (state $(state)); restoring anyway"
    put "$BACKUP/path-map.yaml" "$ROOT/$MAP" || die "the map could not be restored"
    put "$BACKUP/pretooluse.py" "$ROOT/$HOOK" || die "the hook could not be restored"
    for n in $NEWFILES; do
      f=$ROOT/$NEWDIR/$n
      [ -e "$f" ] || continue
      [ "$(sha "$f")" = "${NEW[$n]}" ] || die "$NEWDIR/$n has changed since the apply: left in place"
      rm -f "$f"
    done
    rmdir "$ROOT/$NEWDIR" 2>/dev/null || true
    if [ -f "$WALLS/APPROVED" ]; then
      [ "$(sha "$WALLS/APPROVED")" = "$(cat "$BACKUP/APPROVED.sha256")" ] \
        || die "<sets root>/indep-walls/APPROVED has changed since the apply (briefs added?): left in place"
      rm -f "$WALLS/APPROVED"
    fi
    [ -d "$WALLS" ] && rmdir "$WALLS"
    show after-undo
    cmp -s "$BACKUP/path-map.yaml" "$ROOT/$MAP" && cmp -s "$BACKUP/pretooluse.py" "$ROOT/$HOOK" \
      && [ "$(state)" = before ] || die "the restored tree differs from the backup"
    echo "undo: done; the hook and the map byte for byte as before, the template and indep-walls/ gone" ;;
  *)
    echo "usage: bash apply.sh check|apply|undo [--sets-root DIR]" >&2; exit 2 ;;
esac
