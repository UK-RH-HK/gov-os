#!/usr/bin/env bash
# ACT-SETS-GLOBS-1 (W2-149's review F2; DEC-1101, DEC-1112): the operator's check, apply and undo.
#   bash apply.sh check  [--sets-root DIR]   every file hashes as built; which state the tree is in; the hidden part's
#                                            size under the new globs (a count and a time only); changes nothing
#   bash apply.sh apply  [--sets-root DIR]   backups (with sha256s), the two changes below, then the hashes after
#   bash apply.sh undo                       both files back byte for byte from the backups
# The changes:
#   1. governance/project/path-map.yaml   replaced by path-map.candidate.yaml: four globs added to sets_root_hidden
#      (fixtures/evaluation/*/hidden/**, fixtures/evaluation/*/XCHECK-r*.md, runs/*/miss-classes.json,
#      runs/*/misses.jsonl) and a comment
#   2. .claude/hooks/pretooluse.py        replaced by pretooluse.candidate.py: for a glob with a wildcard before its
#      end, the line rule's key is the hidden folder or file itself (sets_line_keys), and the walk of the sets root and
#      of each tree skips the folders the glob cannot match (Narrow); every other rule, every existing key and every
#      existing walk unchanged (pretooluse.diff)
# The size check: the sets root's hidden part walked as the guard walks it (file names only, never their text): the
# pinned judge's own walk with the live globs (the hook today), the candidate hook's Narrow with the candidate globs
# (the hook after); each the median of 5 fresh walks. It prints two counts and two times, never a name. apply refuses
# when the candidate's count is over 8,000 (the launch script's budget; the guard fails closed past 10,000) or its walk
# over 2,000 ms. It changes only the tree it sits in (found from its own place: <tree>/.gov-runtime/scratch/orchestrator/
# drafts/sets-globs/). It commits nothing: the operator's commit follows (ACT §5).
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT=$(cd "$HERE/../../../../.." && pwd)
SETS=
cmd=${1:-}; shift || true
while [ $# -gt 0 ]; do
  case "$1" in
    --sets-root) SETS=$2; shift 2 ;;
    *) echo "usage: bash apply.sh check|apply|undo [--sets-root DIR]" >&2; exit 2 ;;
  esac
done
HOOK=.claude/hooks/pretooluse.py
MAP=governance/project/path-map.yaml
BACKUP=$HERE/backup
MOST_FILES=8000
MOST_MS=2000
# The hashes as built (2026-11-09, w2/integrate b4de529b4: the hook as ACT-OPERATOR-1 left it, the map as that ACT left it)
BEFORE_HOOK=97a84e770058bb96705ebe41c259c0c1578bdc8ac23fac237e6cdf5f1af43e11
BEFORE_MAP=40085090306e9429e1fdc2ef4eb8bb3bd5af26ad3d50db95222950794bf242a5
AFTER_HOOK=74f8dbea4761de37628305e5d58125641ae39a409a7ed0a2babb379b1ceca5b8
AFTER_MAP=44f99ea563cb59ddd2e0f143e7d7f7c6869c358390fc7b18dbaffc1a4fba7f70

die() { echo "apply.sh: $*; nothing more is done" >&2; exit 1; }
sha() { sha256sum "$1" | cut -d' ' -f1; }
[ -d "$ROOT/.git" ] || [ -f "$ROOT/.git" ] || die "$ROOT is not a git tree"
[ -f "$ROOT/$HOOK" ] && [ -f "$ROOT/$MAP" ] || die "$ROOT has no $HOOK or $MAP"
PIN=$(head -1 "$HOME/.local/bin/gov" | cut -c3-)
[ -x "$PIN" ] || die "the pinned interpreter ($PIN) is not there"

state() {  # before | applied | other
  local h m; h=$(sha "$ROOT/$HOOK"); m=$(sha "$ROOT/$MAP")
  if [ "$h" = "$BEFORE_HOOK" ] && [ "$m" = "$BEFORE_MAP" ]; then echo before
  elif [ "$h" = "$AFTER_HOOK" ] && [ "$m" = "$AFTER_MAP" ]; then echo applied
  else echo other; fi
}
show() {
  echo "$1: $(sha "$ROOT/$HOOK")  $HOOK"
  echo "$1: $(sha "$ROOT/$MAP")  $MAP"
  echo "$1: state $(state)"
}
drafts_ok() {
  [ "$(sha "$HERE/pretooluse.candidate.py")" = "$AFTER_HOOK" ] || die "pretooluse.candidate.py is not as built"
  [ "$(sha "$HERE/path-map.candidate.yaml")" = "$AFTER_MAP" ] || die "path-map.candidate.yaml is not as built"
}
size() {  # the hidden part under the live map's globs and the candidate's: counts and times only; exit 1 over a limit
  "$PIN" -E - "$ROOT/$MAP" "$HERE/path-map.candidate.yaml" "$SETS" "$MOST_FILES" "$MOST_MS" "$HERE/pretooluse.candidate.py" <<'EOF'
import importlib.util, os, statistics, sys, time
from gov.guard.heldout import load_yaml_unique
from gov.guard.reads import _Part, HIDDEN_REFUSAL, PolicyError
live, cand, sets, most, most_ms, hook = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
spec = importlib.util.spec_from_file_location("candidate_hook", hook)
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
Narrow = mod.classes()[2]
def block(p):
    lines = open(p, encoding="utf-8").read().splitlines(keepends=True)
    at = [i for i, l in enumerate(lines) if l.startswith("sets_root_hidden:")]
    assert len(at) == 1, p
    end = next((j for j in range(at[0] + 1, len(lines)) if lines[j][:1] not in ("", " ", "\t", "#", "\n", "\r")), len(lines))
    return load_yaml_unique("".join(lines[at[0]:end]))["sets_root_hidden"]
bad = 0
for label, p in (("live", live), ("candidate", cand)):
    b = block(p)
    top = os.path.realpath(sets or os.path.expanduser(b["root"]))
    kind = _Part if label == "live" else Narrow
    times = []
    for _ in range(5):
        for c in Narrow.caches:
            c.clear()
        t0 = time.monotonic()
        try:
            n = len(kind(top, list(b["hidden"]), HIDDEN_REFUSAL).files)
        except PolicyError:
            n = 10001
        times.append((time.monotonic() - t0) * 1000)
    ms = statistics.median(times)
    print(f"size ({label} globs, {len(b['hidden'])}, {'the judge' if label == 'live' else 'Narrow'}): {n} hidden files, "
          f"walked in {ms:.0f} ms (median of 5)")
    if label == "candidate" and (n > most or ms > most_ms):
        print(f"size: over the limit ({most} files, {most_ms} ms)")
        bad = 1
sys.exit(bad)
EOF
}
put() {  # put file $1 at $2 by a rename in $2's folder, keeping $2's mode
  local tmp; tmp=$(mktemp "$(dirname "$2")/.sets-globs.XXXXXX")
  cp -p "$1" "$tmp" || { rm -f "$tmp"; return 1; }
  [ -e "$2" ] && chmod --reference="$2" "$tmp"
  mv -f "$tmp" "$2" || { rm -f "$tmp"; return 1; }
}

echo "apply.sh $cmd: tree $ROOT${SETS:+, sets root $SETS}"
case "$cmd" in
  check)
    show now
    drafts_ok && echo "drafts: both files as built"
    case "$(state)" in
      before) size || die "the hidden part is over a limit with the new globs: ask the CTO"; echo "check: ready to apply" ;;
      applied) echo "check: already applied" ;;
      *) die "the tree is neither as before nor as applied (a file has moved since the build: ask the CTO to rebuild and re-rehearse)" ;;
    esac ;;
  apply)
    show before
    [ "$(state)" = before ] || die "the tree is not in the state before (state $(state))"
    drafts_ok
    size || die "the hidden part is over a limit with the new globs: ask the CTO"
    [ -e "$BACKUP" ] && die "$BACKUP exists already (an earlier apply): move it aside first"
    mkdir -p "$BACKUP"
    cp -p "$ROOT/$HOOK" "$BACKUP/pretooluse.py"; cp -p "$ROOT/$MAP" "$BACKUP/path-map.yaml"
    ( cd "$BACKUP" && sha256sum pretooluse.py path-map.yaml ) > "$BACKUP/SHA256SUMS"
    [ "$(sha "$BACKUP/pretooluse.py")" = "$BEFORE_HOOK" ] && [ "$(sha "$BACKUP/path-map.yaml")" = "$BEFORE_MAP" ] \
      || die "the backups do not hash as before"
    echo "backup: $BACKUP (SHA256SUMS written)"
    put "$HERE/pretooluse.candidate.py" "$ROOT/$HOOK" || die "the hook could not be replaced: run undo"
    put "$HERE/path-map.candidate.yaml" "$ROOT/$MAP" || die "the map could not be replaced: run undo"
    show after
    [ "$(state)" = applied ] || die "the tree does not hash as applied: run undo"
    echo "apply: done. The operator's commit stages:"
    echo "  git add $HOOK $MAP" ;;
  undo)
    show before-undo
    [ -f "$BACKUP/pretooluse.py" ] && [ "$(sha "$BACKUP/pretooluse.py")" = "$BEFORE_HOOK" ] \
      && [ -f "$BACKUP/path-map.yaml" ] && [ "$(sha "$BACKUP/path-map.yaml")" = "$BEFORE_MAP" ] \
      || die "no backup in $BACKUP, or one that does not hash as before the apply"
    [ "$(state)" = applied ] || echo "undo: note: the tree has changed since the apply (state $(state)); restoring anyway"
    put "$BACKUP/path-map.yaml" "$ROOT/$MAP" || die "the map could not be restored"
    put "$BACKUP/pretooluse.py" "$ROOT/$HOOK" || die "the hook could not be restored"
    show after-undo
    cmp -s "$BACKUP/path-map.yaml" "$ROOT/$MAP" && cmp -s "$BACKUP/pretooluse.py" "$ROOT/$HOOK" \
      && [ "$(state)" = before ] || die "the restored files differ from the backups"
    echo "undo: done; the hook and the map byte for byte as before the apply" ;;
  *)
    echo "usage: bash apply.sh check|apply|undo [--sets-root DIR]" >&2; exit 2 ;;
esac
