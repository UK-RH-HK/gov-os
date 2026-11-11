#!/usr/bin/env bash
# ACT-MEMORY-AUDIT-INSTALL-1 (DEC-1129 (2), DEC-1101 (1)-(2), DEC-1125 (2)): the memory audit's three fixed briefs and
# their three lines in the launch script's approved list. Rehearsed (DEC-1057).
#   bash apply.sh check  [--sets-root DIR]   the state of the tree and the list; changes nothing
#   bash apply.sh apply  [--sets-root DIR]   checks first; the list backed up (sha256); the three briefs into the tree;
#                                            the new list; the list read back by the launch script's own parser
#   bash apply.sh undo   [--sets-root DIR]   checks first; the list back byte for byte; the three brief files removed
# --sets-root is for the rehearsal only (a planted root); the default is the real one under $HOME.
# What changes:
#   - the tree (found from this file's place, <tree>/.gov-runtime/scratch/orchestrator/drafts/memaudit-install-1/): three
#     new files, governance/project/indep-briefs/memory-audit/{writer,checker,auditor}.md, byte for byte the briefs the
#     owner approved (DEC-1129 (2)). The operator commits them.
#   - <sets root>/indep-walls/APPROVED (0400): the list as ACT-W2-149-INSTALL-1 left it (sha256 LIST_BEFORE below), then
#     a comment block and three `brief <kind> <path>` lines. No existing line changes.
# It refuses unless the live list is exactly LIST_BEFORE (the only reading of the sets root it makes is that one
# file), ACT-W2-149-INSTALL-1 and ACT-SETS-GLOBS-1 are applied in the tree, ACT-PATHMAP-NS-2 has placed the briefs'
# folder in the path map, and the tree's six template files are the six the list names.
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
BRIEFS=governance/project/indep-briefs/memory-audit
SGX1=governance/project/indep-briefs/sgx1
SCRIPT=governance/project/orchestration/tools/indep_launch.py
MAP=governance/project/path-map.yaml
HOOK=.claude/hooks/pretooluse.py
TEMPLATE=governance/project/indep-walls
BACKUP=$HERE/backup
# The hashes as built (frozen by freeze.py; see the package §4)
LIST_BEFORE=6b923cb4d552077f99924fd5df38f1a448b21f863c4755c9ff4e0dcfb28ed959
LIST_AFTER=41e3969aa969cec58bf6bc09e770f037acf97ca0ebdd2e8d893e8a1ac2d938e0
declare -A BRIEF=(
  [writer.md]=bc0894230e3181e5be27726d60e9fb781f9355da1c4f8e76f69b400af97d379b
  [checker.md]=cea517b8da7d4834bb2a698b9c7023670da36f0ceca6b3350656c6db77c45248
  [auditor.md]=37be41c3fb2fea1654d68f71f1ecfc5ad4b41faaed9356a27ce1f01d8ef94245
)
NAMES="writer.md checker.md auditor.md"
SGX1_NAMES="labeller.md labeller-2.md writer-tuning.md writer-heldout.md overlap-auditor.md"
declare -A SGX1_SHA=(
  [labeller.md]=bbff1249953bd9d3b2596b33a108712bdddd79a7e86723b9e6955e3d6b0e9068
  [labeller-2.md]=e13b5f96d0e058277f3ec3014f13205d7fe0bc950cfc308e81b3ee3d742ac904
  [writer-tuning.md]=82134b3dd6b5a077abfc2eb6fa7481f0f5a73eab60396cfbd655042d53027c57
  [writer-heldout.md]=137a73d1df4c265fd5ce4e24716797703e2b12dcaeb90663c0170834a60fafe6
  [overlap-auditor.md]=b212a424062e402b0a25ee4a157ae14a0af798d0ad973aa33dacd730782be6ab
)
SETS_GLOBS=('fixtures/evaluation/*/hidden/**' 'fixtures/evaluation/*/XCHECK-r*.md' 'runs/*/miss-classes.json' 'runs/*/misses.jsonl')

die() { echo "apply.sh: $*; nothing more is done" >&2; exit 1; }
sha() { if [ -f "$1" ] && [ ! -L "$1" ]; then sha256sum "$1" | cut -c1-64; else echo none; fi; }
[ -d "$ROOT/.git" ] || [ -f "$ROOT/.git" ] || die "$ROOT is not a git tree"
[ -d "$SETS" ] || die "the sets root is not a folder"

drafts_ok() {
  local n
  for n in $NAMES; do [ "$(sha "$HERE/briefs/$n")" = "${BRIEF[$n]}" ] || die "the draft briefs/$n is not the approved brief"; done
  [ "$(sha "$HERE/APPROVED.before")" = "$LIST_BEFORE" ] || die "APPROVED.before is not as built"
  [ "$(sha "$HERE/APPROVED.after")" = "$LIST_AFTER" ] || die "APPROVED.after is not as built"
  # APPROVED.after is APPROVED.before byte for byte, then the new lines only
  head -c "$(stat -c %s "$HERE/APPROVED.before")" "$HERE/APPROVED.after" | cmp -s - "$HERE/APPROVED.before" \
    || die "APPROVED.after does not begin with APPROVED.before"
  [ "$(tail -c +$(( $(stat -c %s "$HERE/APPROVED.before") + 1 )) "$HERE/APPROVED.after" | grep -vc '^#')" = 3 ] \
    || die "APPROVED.after adds other than three lines and comments"
  for n in $NAMES; do
    grep -qxF "${BRIEF[$n]}  brief ${n%.md} $BRIEFS/$n" "$HERE/APPROVED.after" || die "APPROVED.after lacks the line for $n"
  done
}
order_ok() {  # ACT-W2-149-INSTALL-1, ACT-SETS-GLOBS-1 and ACT-PATHMAP-NS-2 applied; the templates the list's six
  local n
  for n in $SGX1_NAMES; do
    [ "$(sha "$ROOT/$SGX1/$n")" = "${SGX1_SHA[$n]}" ] \
      || die "set-up A's brief $SGX1/$n is not in the tree as ACT-W2-149-INSTALL-1 placed it: that ACT first"
  done
  grep -qxF '      - "governance/project/indep-briefs/**"' "$ROOT/$MAP" \
    || die "ACT-PATHMAP-NS-2 is not applied (the map names no governance/project/indep-briefs/**): apply it first"
  python3 -I -B - "$ROOT/$MAP" "${SETS_GLOBS[@]}" <<'EOF' || die "ACT-SETS-GLOBS-1 is not applied (its globs are not in the map's sets_root_hidden): apply it first"
import sys, yaml
d = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
have = set((d.get("sets_root_hidden") or {}).get("hidden") or [])
sys.exit(0 if all(g in have for g in sys.argv[2:]) else 1)
EOF
  grep -q '^def sets_line_keys(' "$ROOT/$HOOK" \
    || die "ACT-SETS-GLOBS-1 is not applied (the hook has no sets_line_keys): apply it first"
  # the tree's six template files are the six the list names (else every launch is refused 11, whatever this ACT does)
  python3 -I -B - "$HERE/APPROVED.before" "$ROOT" <<'EOF' || die "a template file in the tree is not the one the list names: its own ACT first"
import hashlib, os, re, sys
bad = []
n = 0
for line in open(sys.argv[1], encoding="utf-8").read().splitlines():
    m = re.fullmatch(r"([0-9a-f]{64})  template (\S+)", line)
    if m:
        n += 1
        p = os.path.join(sys.argv[2], m.group(2))
        if not os.path.isfile(p) or hashlib.sha256(open(p, "rb").read()).hexdigest() != m.group(1):
            bad.append(m.group(2))
for b in bad:
    print("template differs:", b, file=sys.stderr)
sys.exit(0 if n == 6 and not bad else 1)
EOF
}
tree_state() {  # absent | present | other: the three brief files in the tree
  local n a=0 p=0
  for n in $NAMES; do
    if [ -e "$ROOT/$BRIEFS/$n" ] || [ -L "$ROOT/$BRIEFS/$n" ]; then
      [ "$(sha "$ROOT/$BRIEFS/$n")" = "${BRIEF[$n]}" ] && p=$((p + 1)) || { echo other; return; }
    else a=$((a + 1)); fi
  done
  local extra=0
  [ -d "$ROOT/$BRIEFS" ] && extra=$(find "$ROOT/$BRIEFS" -mindepth 1 | grep -cvE "/(writer|checker|auditor)\.md$" || true)
  [ "$extra" = 0 ] || { echo other; return; }
  [ $a = 3 ] && echo absent || { [ $p = 3 ] && echo present || echo other; }
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
parse_check() {  # the launch script's own parser reads the list as the launch will: 6 templates, 10 briefs, each matching
  python3 -I -B - "$ROOT/$SCRIPT" "$LIST" "$ROOT" <<'EOF'
import hashlib, importlib.util, os, sys
spec = importlib.util.spec_from_file_location("indep_launch_for_install", sys.argv[1])
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
data = open(sys.argv[2], "rb").read()
t, b = m.parse_approved(data)
bad = [p for p, hs in t.items() if hs != {hashlib.sha256(open(os.path.join(sys.argv[3], p), "rb").read()).hexdigest()}]
miss = [p for h, k, p in b if hashlib.sha256(open(os.path.join(sys.argv[3], p), "rb").read()).hexdigest() != h]
mem = sorted(k for h, k, p in b if p.startswith("governance/project/indep-briefs/memory-audit/"))
print(f"the list as the launch script reads it: {len(t)} template lines, {len(b)} brief lines "
      f"({', '.join(sorted(set(k for _, k, _ in b)))}); the memory audit's: {', '.join(mem)}; "
      f"template mismatches {len(bad)}; brief mismatches {len(miss)}")
sys.exit(0 if len(t) == 6 and len(b) == 10 and mem == ["auditor", "checker", "writer"] and not bad and not miss else 1)
EOF
}

case "$cmd" in
  check)
    drafts_ok; order_ok
    [ "$(list_state)" != other ] || die "the live list is not $(echo $LIST_BEFORE | cut -c1-12) (the list ACT-W2-149-INSTALL-1 left; sha256 $(sha "$LIST" | cut -c1-12)): the CTO looks first"
    s=$(state); echo "state: $s (the list $(sha "$LIST" | cut -c1-12))"
    case "$s" in
      before) echo "check: ready to apply" ;;
      applied) parse_check; echo "check: already applied" ;;
      *) die "neither before nor applied: the CTO looks first" ;;
    esac ;;
  apply)
    drafts_ok; order_ok
    [ "$(list_state)" != other ] || die "the live list is not $(echo $LIST_BEFORE | cut -c1-12) (sha256 $(sha "$LIST" | cut -c1-12)): the CTO looks first"
    [ "$(state)" = before ] || die "not in the before state ($(state))"
    [ ! -e "$BACKUP" ] || die "$BACKUP exists (an earlier apply): the CTO looks first"
    mkdir -p "$BACKUP"; cp -p "$LIST" "$BACKUP/APPROVED"; ( cd "$BACKUP" && sha256sum APPROVED > SHA256SUMS )
    mkdir -p "$ROOT/$BRIEFS"
    for n in $NAMES; do cat "$HERE/briefs/$n" > "$ROOT/$BRIEFS/$n"; chmod 0644 "$ROOT/$BRIEFS/$n"; done
    tmp="$WALLS/.APPROVED.act-memaudit-install.$$"
    rm -f "$tmp"; cat "$HERE/APPROVED.after" > "$tmp"; chmod 0400 "$tmp"; mv -f "$tmp" "$LIST"
    [ "$(state)" = applied ] || die "after the apply the state is $(state): run 'bash apply.sh undo'"
    parse_check || die "the launch script's parser does not read the list as built: run 'bash apply.sh undo'"
    echo "the list $(sha "$LIST")"
    echo "state applied" ;;
  undo)
    [ "$(state)" = applied ] || die "not as this ACT left it ($(state))"
    [ -f "$BACKUP/SHA256SUMS" ] && ( cd "$BACKUP" && sha256sum -c --quiet SHA256SUMS ) || die "no good backup in $BACKUP"
    [ "$(sha "$BACKUP/APPROVED")" = "$LIST_BEFORE" ] || die "the backup is not the before list"
    tmp="$WALLS/.APPROVED.act-memaudit-install.$$"
    rm -f "$tmp"; cat "$BACKUP/APPROVED" > "$tmp"; chmod 0400 "$tmp"; mv -f "$tmp" "$LIST"
    for n in $NAMES; do rm -f "$ROOT/$BRIEFS/$n"; done
    rmdir "$ROOT/$BRIEFS" 2>/dev/null || true
    [ "$(state)" = before ] || die "after the undo the state is $(state)"
    mv "$BACKUP" "$BACKUP.undone-$(date -u +%Y%m%dT%H%M%SZ)"
    echo "the list $(sha "$LIST")"
    echo "state before (undone)" ;;
  *) echo "usage: bash apply.sh check|apply|undo [--sets-root DIR]" >&2; exit 2 ;;
esac
