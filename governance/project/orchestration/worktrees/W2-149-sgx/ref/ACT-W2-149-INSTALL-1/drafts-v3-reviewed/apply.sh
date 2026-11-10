#!/usr/bin/env bash
# ACT-W2-149-INSTALL-1 (DEC-1101 (2)-(3), DEC-1112, DEC-1113): the launch script's approved list. Rehearsed (DEC-1057).
#   bash apply.sh check  [--sets-root DIR]   the state of the tree and the list; changes nothing
#   bash apply.sh apply  [--sets-root DIR]   checks first; the list backed up (sha256); the five briefs into the tree;
#                                            the list's new lines; the list checked by the launch script's own parser
#   bash apply.sh undo   [--sets-root DIR]   checks first; the list back byte for byte; the five brief files removed
# --sets-root is for the rehearsal only (a planted root); the default is the real one under $HOME.
# What changes:
#   - the tree (found from this file's place, <tree>/.gov-runtime/scratch/orchestrator/drafts/w2-149-install/): five new
#     files, governance/project/indep-briefs/sgx1/{labeller,labeller-2,writer-tuning,writer-heldout,overlap-auditor}.md,
#     byte for byte the briefs the owner approved (DEC-1113; SANDBOX-GUARD-EXP-DECLARATION §12). The operator commits them.
#   - <sets root>/indep-walls/APPROVED (0400): ACT-INDEP-WALLS-1's text, its two template lines for kinds.yaml and
#     tree-exclude.txt carrying the set-up A wiring's sha256s (the other four as they are), then a comment naming the
#     replaced hashes, one naming the launch script's sha256, five `brief <kind> <path>` lines and the operator agent's
#     two (DEC-1109 (1)).
# It refuses unless ACT-SETS-GLOBS-1 is applied (its four globs in the map's sets_root_hidden, its line keys in the
# hook) and the tree's launch script and the two template files are the set-up A wiring's (W2-149, merged). It reads nothing under the sets root but indep-walls/APPROVED.
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
SETS=$(realpath -m "$SETS")
WALLS=$SETS/indep-walls
LIST=$WALLS/APPROVED
BRIEFS=governance/project/indep-briefs/sgx1
SCRIPT=governance/project/orchestration/tools/indep_launch.py
MAP=governance/project/path-map.yaml
HOOK=.claude/hooks/pretooluse.py
BACKUP=$HERE/backup
# The hashes as built (frozen by freeze.py; see the package §4)
LAUNCH_SHA=95fe78dd49bb493194e33cc6a832bc3674b6998ac06010cc5a5d4f7aade5f1d0
LIST_BEFORE=331e48fa336ef58ba5dc6fd4afcf9c1387ec4bd29e583eb955280a267626bbc9
LIST_AFTER=32f1aab70bc24ac7133f720f4fab071426400e081b8727f4908513fa172de5f6
KINDS_SHA=734b26e261faa81a4de7d4305e33291291d2e0949b4a4ba1c6fadd11672cd6df
EXCLUDE_SHA=e8395088167ed9bc6d01d43e1c6504341a2f06db752d4d3aef969c14718b8537
KINDS_BEFORE=8b50a78f01b316d0bd5d41689cd3730da0e3142ac4c54705dc83bad0ace4d74f
EXCLUDE_BEFORE=21660e1ee5adf793e46d59e601cef662ef8a445399da185bd9397bc6067d47a6
TEMPLATE=governance/project/indep-walls
declare -A BRIEF=(
  [labeller.md]=bbff1249953bd9d3b2596b33a108712bdddd79a7e86723b9e6955e3d6b0e9068
  [labeller-2.md]=e13b5f96d0e058277f3ec3014f13205d7fe0bc950cfc308e81b3ee3d742ac904
  [writer-tuning.md]=82134b3dd6b5a077abfc2eb6fa7481f0f5a73eab60396cfbd655042d53027c57
  [writer-heldout.md]=137a73d1df4c265fd5ce4e24716797703e2b12dcaeb90663c0170834a60fafe6
  [overlap-auditor.md]=b212a424062e402b0a25ee4a157ae14a0af798d0ad973aa33dacd730782be6ab
)
NAMES="labeller.md labeller-2.md writer-tuning.md writer-heldout.md overlap-auditor.md"
SETS_GLOBS=('fixtures/evaluation/*/hidden/**' 'fixtures/evaluation/*/XCHECK-r*.md' 'runs/*/miss-classes.json' 'runs/*/misses.jsonl')

die() { echo "apply.sh: $*; nothing more is done" >&2; exit 1; }
sha() { if [ -f "$1" ] && [ ! -L "$1" ]; then sha256sum "$1" | cut -c1-64; else echo none; fi; }
[ -d "$ROOT/.git" ] || [ -f "$ROOT/.git" ] || die "$ROOT is not a git tree"
[ -d "$SETS" ] || die "the sets root is not a folder"

drafts_ok() {
  local n
  for n in $NAMES; do [ "$(sha "$HERE/briefs/$n")" = "${BRIEF[$n]}" ] || die "the draft briefs/$n is not the approved brief"; done
  [ "$(sha "$HERE/APPROVED.after")" = "$LIST_AFTER" ] || die "APPROVED.after is not as built"
  local h; h=$(mktemp)
  sed -e "s/^$KINDS_BEFORE  template /$KINDS_SHA  template /" -e "s/^$EXCLUDE_BEFORE  template /$EXCLUDE_SHA  template /" \
    "$HERE/APPROVED.before" > "$h"
  head -c "$(stat -c %s "$h")" "$HERE/APPROVED.after" | cmp -s - "$h" \
    || { rm -f "$h"; die "APPROVED.after's head is not APPROVED.before with the two template lines changed"; }
  rm -f "$h"
  [ "$(sha "$HERE/APPROVED.before")" = "$LIST_BEFORE" ] || die "APPROVED.before is not as built"
}
order_ok() {  # ACT-SETS-GLOBS-1 applied; the launch script and the two template files the set-up A wiring's
  [ "$(sha "$ROOT/$SCRIPT")" = "$LAUNCH_SHA" ] \
    || die "the tree's $SCRIPT is not W2-149 with set-up A's wiring (${LAUNCH_SHA:0:12}): merge it first"
  [ "$(sha "$ROOT/$TEMPLATE/kinds.yaml")" = "$KINDS_SHA" ] && [ "$(sha "$ROOT/$TEMPLATE/tree-exclude.txt")" = "$EXCLUDE_SHA" ] \
    || die "the tree's $TEMPLATE/kinds.yaml or tree-exclude.txt is not the set-up A wiring's: merge it first"
  python3 -I -B - "$ROOT/$MAP" "${SETS_GLOBS[@]}" <<'EOF' || die "ACT-SETS-GLOBS-1 is not applied (its globs are not in the map's sets_root_hidden): apply it first"
import sys, yaml
d = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
have = set((d.get("sets_root_hidden") or {}).get("hidden") or [])
sys.exit(0 if all(g in have for g in sys.argv[2:]) else 1)
EOF
  grep -q '^def sets_line_keys(' "$ROOT/$HOOK" \
    || die "ACT-SETS-GLOBS-1 is not applied (the hook has no sets_line_keys): apply it first"
}
tree_state() {  # absent | present | other: the five brief files in the tree
  local n a=0 p=0
  for n in $NAMES; do
    if [ -e "$ROOT/$BRIEFS/$n" ] || [ -L "$ROOT/$BRIEFS/$n" ]; then
      [ "$(sha "$ROOT/$BRIEFS/$n")" = "${BRIEF[$n]}" ] && p=$((p + 1)) || { echo other; return; }
    else a=$((a + 1)); fi
  done
  local extra=0
  [ -d "$ROOT/$BRIEFS" ] && extra=$(find "$ROOT/$BRIEFS" -mindepth 1 | grep -cvE "/($(echo $NAMES | sed 's/ /|/g; s/\./\\./g'))$" || true)
  [ "$extra" = 0 ] || { echo other; return; }
  [ $a = 5 ] && echo absent || { [ $p = 5 ] && echo present || echo other; }
}
list_state() {  # before | applied | other
  local s; s=$(sha "$LIST")
  [ "$s" = "$LIST_BEFORE" ] && echo before || { [ "$s" = "$LIST_AFTER" ] && echo applied || echo other; }
}
state() {
  local t l; t=$(tree_state); l=$(list_state)
  if [ "$t" = absent ] && [ "$l" = before ]; then echo before
  elif [ "$t" = present ] && [ "$l" = applied ]; then echo applied
  else echo "other (briefs $t, list $l)"; fi
}
parse_check() {  # the launch script's own parser reads the list as the launch will: 6 templates, 7 briefs, each matching
  python3 -I -B - "$ROOT/$SCRIPT" "$LIST" "$ROOT" <<'EOF'
import hashlib, importlib.util, os, sys
spec = importlib.util.spec_from_file_location("indep_launch_for_install", sys.argv[1])
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
data = open(sys.argv[2], "rb").read()
t, b = m.parse_approved(data)
bad = [p for p, hs in t.items() if hs != {hashlib.sha256(open(os.path.join(sys.argv[3], p), "rb").read()).hexdigest()}]
miss = [p for h, k, p in b if hashlib.sha256(open(os.path.join(sys.argv[3], p), "rb").read()).hexdigest() != h]
print(f"the list as the launch script reads it: {len(t)} template lines, {len(b)} brief lines "
      f"({', '.join(sorted(set(k for _, k, _ in b)))}); template mismatches {len(bad)}; brief mismatches {len(miss)}")
sys.exit(0 if len(t) == 6 and len(b) == 7 and not bad and not miss else 1)
EOF
}

case "$cmd" in
  check)
    drafts_ok; order_ok
    s=$(state); echo "state: $s (the list $(sha "$LIST" | cut -c1-12))"
    case "$s" in
      before) echo "check: ready to apply" ;;
      applied) parse_check; echo "check: already applied" ;;
      *) die "neither before nor applied: the CTO looks first" ;;
    esac ;;
  apply)
    drafts_ok; order_ok
    [ "$(state)" = before ] || die "not in the before state ($(state))"
    [ ! -e "$BACKUP" ] || die "$BACKUP exists (an earlier apply): the CTO looks first"
    mkdir -p "$BACKUP"; cp -p "$LIST" "$BACKUP/APPROVED"; ( cd "$BACKUP" && sha256sum APPROVED > SHA256SUMS )
    mkdir -p "$ROOT/$BRIEFS"
    for n in $NAMES; do cat "$HERE/briefs/$n" > "$ROOT/$BRIEFS/$n"; chmod 0644 "$ROOT/$BRIEFS/$n"; done
    tmp="$WALLS/.APPROVED.act-w2-149-install.$$"
    rm -f "$tmp"; cat "$HERE/APPROVED.after" > "$tmp"; chmod 0400 "$tmp"; mv -f "$tmp" "$LIST"
    [ "$(state)" = applied ] || die "after the apply the state is $(state): run 'bash apply.sh undo'"
    parse_check || die "the launch script's parser does not read the list as built: run 'bash apply.sh undo'"
    echo "the list $(sha "$LIST")"
    echo "state applied" ;;
  undo)
    [ "$(state)" = applied ] || die "not as this ACT left it ($(state))"
    [ -f "$BACKUP/SHA256SUMS" ] && ( cd "$BACKUP" && sha256sum -c --quiet SHA256SUMS ) || die "no good backup in $BACKUP"
    [ "$(sha "$BACKUP/APPROVED")" = "$LIST_BEFORE" ] || die "the backup is not the before list"
    tmp="$WALLS/.APPROVED.act-w2-149-install.$$"
    rm -f "$tmp"; cat "$BACKUP/APPROVED" > "$tmp"; chmod 0400 "$tmp"; mv -f "$tmp" "$LIST"
    for n in $NAMES; do rm -f "$ROOT/$BRIEFS/$n"; done
    rmdir "$ROOT/$BRIEFS" 2>/dev/null || true
    rmdir "$ROOT/governance/project/indep-briefs" 2>/dev/null || true
    [ "$(state)" = before ] || die "after the undo the state is $(state)"
    mv "$BACKUP" "$BACKUP.undone-$(date -u +%Y%m%dT%H%M%SZ)"
    echo "the list $(sha "$LIST")"
    echo "state before (undone)" ;;
  *) echo "usage: bash apply.sh check|apply|undo [--sets-root DIR]" >&2; exit 2 ;;
esac
