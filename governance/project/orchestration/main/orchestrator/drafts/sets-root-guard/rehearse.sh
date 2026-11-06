#!/usr/bin/env bash
# DEC-1082 (3), the sets-root guard: the build spec's section D, end to end, in a scratch clone. Changes nothing live.
#   bash rehearse.sh [step ...]      default: every step, in order; the log goes to rehearsal.log beside this file
# Steps: prepare plant live_before suites_before apply r2 r1_root r1 override_off suites_after replay measure writer
#        undo live_after (prepare remakes the whole folder: run live_before after it)
# It re-runs itself from a fresh shell (env -i with HOME, USER, LOGNAME, PATH and LANG only), as ACT-G14 did.
# Layout (under ~/gov-os-runs/SETS-rehearsal, made by this script, marked by its .sets-rehearsal file):
#   Dynamic-Agentic-Engineering-OS   the --no-hardlinks clone, apply.sh applied there
#   home/gov-os-eval                 the planted sets root: dummy files only, written here
#   wt-oldmap                        a worktree of the clone on a branch with the old map (T3)
#   writer                           the scratch writer folder (the writer-session check)
# The real ~/gov-os-eval is never opened, listed or named to the hook: only its root's own stat line is taken, before
# and after. While the clone's block reads root: "~/gov-os-eval" (between apply and r1_root, and just before undo),
# the hook runs only with HOME set to the planted home.
set -u
if [ -z "${SETS_FRESH:-}" ]; then
  exec env -i HOME="$HOME" USER="${USER:-usain}" LOGNAME="${LOGNAME:-usain}" PATH="$PATH" LANG="${LANG:-C.UTF-8}" \
    SETS_FRESH=1 bash --noprofile --norc "$0" "$@"
fi
MAIN=/home/usain/Dynamic-Agentic-Engineering-OS
SUB=.gov-runtime/scratch/orchestrator
HERE=$MAIN/$SUB/drafts/sets-root-guard
BASE=$HOME/gov-os-runs/SETS-rehearsal
R=$BASE/Dynamic-Agentic-Engineering-OS
PH=$BASE/home
PR=$PH/gov-os-eval
WT=$BASE/wt-oldmap
WR=$BASE/writer
TMPD=/tmp/gov-os-sets-rehearsal
REAL=$HOME/gov-os-eval
PIN=$(head -1 "$HOME/.local/bin/gov" | cut -c3-)
SLOT="bash $MAIN/$SUB/tools/heavy_slot.sh"
T=$R/$SUB/tools
LOG=$HERE/rehearsal.log
exec > >(tee -a "$LOG") 2>&1
FAILS=0

say() { printf '\n== %s (%s)\n' "$1" "$(date '+%H:%M:%S')"; }
bad() { echo "REHEARSAL FAIL: $*"; FAILS=$((FAILS + 1)); }
need_planted() {  # before any hook run with the real HOME: the clone's block names the planted root, or there is none
  local line; line=$(grep -A1 '^sets_root_hidden:' "$R/governance/project/path-map.yaml" | sed -n 2p)
  [ -z "$line" ] || [ "$line" = "  root: \"$PR\"" ] && return 0
  echo "REHEARSAL STOP: the clone's block reads $line; a hook run now with the real HOME would name the real root"
  exit 3
}
eval_stat() { stat -c 'inode %i size %s mtime %Y ctime %Z' "$REAL" 2>&1; }  # the root's own entry; nothing under it
block_root() {  # set the clone's block root line to $1 (a quoted YAML string)
  python3 - "$R/governance/project/path-map.yaml" "$1" <<'EOF'
import re, sys
p, new = sys.argv[1], sys.argv[2]
lines = open(p, encoding="utf-8").read().splitlines(keepends=True)
at = [i for i, l in enumerate(lines) if l.startswith("sets_root_hidden:")]
assert len(at) == 1, at
i = at[0] + 1
assert lines[i].startswith("  root: "), lines[i]
lines[i] = f"  root: {new}\n"
open(p, "w", encoding="utf-8").write("".join(lines))
print("block root:", lines[i].strip())
EOF
}

step_prepare() {
  say "prepare: the clone"
  if [ -e "$BASE" ]; then
    [ -f "$BASE/.sets-rehearsal" ] || { bad "$BASE exists and is not this script's"; return 1; }
    git -C "$R" worktree remove --force "$WT" 2>/dev/null
    rm -rf "$BASE"
  fi
  mkdir -p "$BASE" && : > "$BASE/.sets-rehearsal"
  git clone -q --no-hardlinks "$MAIN" "$R" || { bad "clone"; return 1; }
  head=$(git -C "$MAIN" rev-parse HEAD)
  git -C "$R" checkout -q -b sets-rehearsal "$head" || { bad "checkout"; return 1; }
  git -C "$MAIN" for-each-ref --format='%(refname) %(objectname)' refs/heads/ | while read -r ref sha; do
    [ "$ref" = refs/heads/sets-rehearsal ] && continue
    git -C "$R" update-ref "$ref" "$sha"
    if [ -f "$MAIN/.git/logs/$ref" ]; then
      mkdir -p "$(dirname "$R/.git/logs/$ref")" && cp -p "$MAIN/.git/logs/$ref" "$R/.git/logs/$ref"
    fi
  done
  for d in tools drafts/g14 drafts/act-guard-fix-4 drafts/act-guard-fix-3 drafts/sets-root-guard; do
    mkdir -p "$R/$SUB/$(dirname "$d")" && cp -a "$MAIN/$SUB/$d" "$R/$SUB/$(dirname "$d")/"
  done
  mkdir -p "$R/$SUB/drafts/score-once"
  cp -p "$MAIN/$SUB/drafts/score-once/so_measure.sh" "$R/$SUB/drafts/score-once/"  # M5 names it
  rm -rf "$R/$SUB/drafts/g14/backup" "$R/$SUB/drafts/g14/backup-g14b" "$R/$SUB/drafts/sets-root-guard/backup" \
         "$R/$SUB/drafts/sets-root-guard/rehearsal.log"
  grep -rlI --null "$MAIN" "$R/$SUB" | xargs -0 -r sed -i "s#$MAIN#$R#g"
  cp -p "$T/guard4_check.py" "$T/guard4_check.live.py"
  cp "$R/$SUB/drafts/sets-root-guard/guard4_check.candidate.py" "$T/guard4_check.py"
  git -C "$R" worktree add -q -b sets-oldmap "$WT" "$head" || bad "worktree"
  echo "clone $R at $(git -C "$R" rev-parse --short=12 HEAD) on $(git -C "$R" branch --show-current);" \
       "branches $(git -C "$R" for-each-ref refs/heads/ | wc -l); root mentions left: $(grep -rlI "$MAIN" "$R/$SUB" | wc -l);" \
       "old-map worktree $WT on $(git -C "$WT" branch --show-current)"
  grep -c '^sets_root_hidden:' "$WT/governance/project/path-map.yaml" | sed 's/^/old-map worktree: block lines /'
}

step_plant() {
  say "plant: the dummy sets root $PR"
  E=$PR/fixtures/evaluation
  mkdir -p "$E/memory-retrieval/hidden" "$E/memory-retrieval/visible" "$E/memory-verdict/hidden" \
           "$E/memory-verdict-2/hidden" "$E/memory-verdict-2/retired" "$PR/transcripts" "$PR/runs" \
           "$PR/governance/project"
  for f in memory-retrieval/hidden/q01 memory-retrieval/visible/v01 memory-verdict/hidden/p01 \
           memory-verdict-2/hidden/p01 memory-verdict-2/hidden/p02 memory-verdict-2/retired/r01; do
    printf 'id: planted-%s\nquestion: "DUMMY planted for the rehearsal (%s)"\n' "${f//\//-}" "$f" > "$E/$f.yaml"
  done
  printf 'DUMMY checker report (planted)\n' > "$E/memory-verdict-2/XCHECK.md"
  printf 'DUMMY transcript (planted)\n' > "$PR/transcripts/t01.md"
  printf 'fixtures/evaluation/memory-verdict-2/hidden/p01.yaml\n' > "$PR/runs/list"
  # the sets root's own map: a stub whose evaluation_sets mirrors the repository's (the real one is never read)
  python3 - "$R/governance/project/path-map.yaml" "$PR/governance/project/path-map.yaml" <<'EOF'
import sys
lines = open(sys.argv[1], encoding="utf-8").read().splitlines(keepends=True)
at = [i for i, l in enumerate(lines) if l.startswith("evaluation_sets:")][0]
end = next(j for j in range(at + 1, len(lines)) if lines[j][:1] not in ("", " ", "\t", "#", "\n", "\r"))
open(sys.argv[2], "w").write("# DUMMY stub for the rehearsal: the repository's evaluation_sets, mirrored\n" +
                              "".join(l for l in lines[at:end] if not l.startswith("#")))
EOF
  [ -e "$PR/.git" ] && bad "the planted root must not be a git tree"
  echo "planted files: $(find "$PR" -type f | wc -l)"; find "$PR" -type f | sed "s#$PR/#  #" | sort
}

step_live_before() {
  say "live_before: the live files and the real sets root's own entry"
  sha256sum "$MAIN/.claude/hooks/pretooluse.py" "$MAIN/governance/project/path-map.yaml" | tee "$BASE/live-before.txt"
  echo "$REAL: $(eval_stat)" | tee -a "$BASE/live-before.txt"
}

suites() {  # $1: a label
  need_planted
  mkdir -p "$TMPD"
  ( cd "$R" && GUARD_FIX4_HOOK=$R/.claude/hooks/pretooluse.py TMPDIR=$TMPD $SLOT python3 -m pytest -q -n 6 \
      -o tmp_path_retention_policy=failed -p no:cacheprovider "$R/$SUB/drafts/act-guard-fix-4/test_guard_fix_4.py" -rf \
      2>&1 | grep -E "^FAILED|^ERROR|failed|passed|error" | sed "s/^/$1 test_guard_fix_4: /" )
  ( cd "$R" && G14_HOOK=$R/.claude/hooks/pretooluse.py TMPDIR=$TMPD $SLOT python3 -m pytest -q -n 6 \
      -o tmp_path_retention_policy=failed -p no:cacheprovider "$R/$SUB/drafts/g14/test_g14.py" -rf \
      2>&1 | grep -E "^FAILED|^ERROR|failed|passed|error" | sed "s/^/$1 test_g14: /" )
}
step_suites_before() { say "suites_before: the two suites on the clone's hook as it is (the baseline)"; suites before; }

step_apply() {
  say "apply: apply.sh in the clone"
  bash "$R/$SUB/drafts/sets-root-guard/apply.sh" check || { bad "apply.sh check"; return 1; }
  bash "$R/$SUB/drafts/sets-root-guard/apply.sh" apply || { bad "apply.sh apply"; return 1; }
  cp -p "$R/$SUB/drafts/sets-root-guard/backup/pretooluse.py" "$R/.claude/hooks/pretooluse.before.py"  # the replay's
  git -C "$R" status --short
  "$PIN" -E - "$R" <<'EOF' || bad "the patched map does not load"
import sys
sys.path.insert(0, sys.argv[1] + "/src")
from pathlib import Path
from gov.config.loader import load_config
from gov.guard.reads import check_sets, evaluation_sets
sys.path.insert(0, sys.argv[1] + "/.claude/hooks")
import role_reads
load_config(Path(sys.argv[1]))
check_sets(sys.argv[1])
print("patched map: load_config ok; evaluation_sets", sorted(evaluation_sets(sys.argv[1])),
      "; role_paths", sorted(role_reads.section(sys.argv[1]) or {}))
EOF
}

step_r2() {
  say "r2: HOME=$PH (the block as applied, root ~/gov-os-eval), GOV_PIN_PY, GUARD4_ONLY=sets"
  grep -n '^  root: ' "$R/governance/project/path-map.yaml"
  ( cd "$R" && HOME=$PH GOV_PIN_PY=$PIN GUARD4_ONLY=sets SETS_PLANTED=1 SETS_OLDMAP_TREE=$WT \
      $SLOT python3 "$T/guard4_check.py" "$R/.claude/hooks/pretooluse.py" > "$BASE/r2.txt" 2>&1 )
  grep -vE '^ok ' "$BASE/r2.txt"
  tail -1 "$BASE/r2.txt" | grep -qx PASS || bad "r2"
}

step_r1_root() { say "r1_root: the block's root set to the planted absolute path"; block_root "\"$PR\""; }

step_r1() {
  say "r1: the registered hook line (--settings), the block's root $PR, SETS_PLANTED=1"
  need_planted
  ( cd "$R" && SETS_PLANTED=1 SETS_OLDMAP_TREE=$WT $SLOT python3 "$T/guard4_check.py" --settings "$R" \
      > "$BASE/r1.txt" 2>&1 )
  grep -vE '^ok ' "$BASE/r1.txt"
  tail -1 "$BASE/r1.txt" | grep -qx PASS || bad "r1"
  say "r1 (L cases only: what the live tree runs after the ACT)"
  ( cd "$R" && SETS_OLDMAP_TREE=$WT $SLOT python3 "$T/guard4_check.py" --settings "$R" > "$BASE/r1-L.txt" 2>&1 )
  grep -vE '^ok ' "$BASE/r1-L.txt"
  tail -1 "$BASE/r1-L.txt" | grep -qx PASS || bad "r1 L"
}

step_override_off() {
  say "override_off: the sets cases on the candidate with Judge.listing's override switched off (HOME=$PH)"
  need_planted
  sed 's/        def listing(self, stages, cwd):/        def _listing_off(self, stages, cwd):/' \
    "$R/.claude/hooks/pretooluse.py" > "$R/.claude/hooks/pretooluse.nooverride.py"
  grep -c '_listing_off' "$R/.claude/hooks/pretooluse.nooverride.py" | sed 's/^/override switched off: /'
  ( cd "$R" && HOME=$PH GOV_PIN_PY=$PIN GUARD4_ONLY=sets SETS_PLANTED=1 SETS_OLDMAP_TREE=$WT \
      $SLOT python3 "$T/guard4_check.py" "$R/.claude/hooks/pretooluse.nooverride.py" > "$BASE/override-off.txt" 2>&1 )
  rm -f "$R/.claude/hooks/pretooluse.nooverride.py"
  grep -vE '^ok ' "$BASE/override-off.txt" | cut -c1-150
  want='sets (M6|M7) orchestrator \(the CTO\)|sets (X1|X2) (engineer|orchestrator \(the CTO\))'
  [ "$(grep -c '^FAIL ' "$BASE/override-off.txt")" = 6 ] && [ "$(grep '^FAIL ' "$BASE/override-off.txt" | grep -cE "$want")" = 6 ] \
    && echo "override_off: exactly M6, M7, X1 and X2 need the override" || bad "override_off"
}

step_suites_after() { say "suites_after: the two suites on the candidate hook, with the block"; suites after; }

step_replay() {
  say "replay: the last 48 hours of tool calls, before and after, the sets root rewritten to $PR"
  need_planted
  ( cd "$R" && $SLOT python3 "$HERE/replay_sets.py" "$R" "$PR" "$R/.claude/hooks/pretooluse.before.py" \
      "$R/.claude/hooks/pretooluse.py" "$PIN" 48 "$BASE/replay.json" ) || bad "replay"
}

step_measure() {
  say "measure: _measured(entry, planted root) per set of the planted map"
  for role in orchestrator engineer; do
    ( cd "$R" && GOV_ROLE=$role GOV_TICKET=DAEO-sdxk "$PIN" -E - "$R" "$PR" <<'EOF' ) || bad "measure $role"
import os, sys
sys.path.insert(0, sys.argv[1] + "/src")
from pathlib import Path
from gov.retrieval.measure import _measured
from gov.guard.reads import evaluation_sets
sets = evaluation_sets(sys.argv[2])
got = {name: _measured(entry, Path(sys.argv[2])) for name, entry in sets.items()}
role = os.environ["GOV_ROLE"]
print(f"GOV_ROLE={role}:", got)
want = {n: role in e["measures"].get("roles", []) for n, e in sets.items()}
assert got == want and (role != "orchestrator" or not any(got.values())), (got, want)
EOF
  done
}

step_writer() {
  say "writer: a headless claude -p session on Haiku in $WR, the clone and the planted root as added directories"
  mkdir -p "$WR"
  F=$PR/fixtures/evaluation/memory-verdict-2/hidden/p01.yaml
  ( cd "$WR" && timeout 300 claude -p --model haiku --add-dir "$R" --add-dir "$PR" --tools Read --allowedTools Read \
      --permission-prompts none --no-session-persistence --max-budget-usd 0.50 --output-format stream-json \
      --verbose --include-hook-events "Use the Read tool on $F and reply with its first line, exactly." \
      > "$BASE/writer.jsonl" 2> "$BASE/writer.err" )
  echo "writer exit $?"
  python3 - "$BASE/writer.jsonl" <<'EOF' || bad "writer"
import json, sys
recs = [json.loads(l) for l in open(sys.argv[1]) if l.strip().startswith("{")]
hooks = [r for r in recs if "hook" in str(r.get("type", "")) + str(r.get("subtype", ""))]
results = [c for r in recs if r.get("type") == "user" for c in (r.get("message") or {}).get("content") or []
           if isinstance(c, dict) and c.get("type") == "tool_result"]
text = json.dumps(results)
final = next((r.get("result", "") for r in recs if r.get("type") == "result"), "")
print("records", len(recs), "| hook events", len(hooks), [h.get("hook_name") or h.get("subtype") for h in hooks][:6])
print("tool results", len(results), "| an error:", any(c.get("is_error") for c in results))
print("the read returned the planted line:", "planted-memory-verdict-2-hidden-p01" in text)
print("final:", final[:200])
assert results and not any(c.get("is_error") for c in results) and "planted-memory-verdict-2-hidden-p01" in text
EOF
}

step_undo() {
  say "undo: the block's root back as applied, then apply.sh undo"
  block_root '"~/gov-os-eval"'
  bash "$R/$SUB/drafts/sets-root-guard/apply.sh" check | tail -1
  bash "$R/$SUB/drafts/sets-root-guard/apply.sh" undo || bad "apply.sh undo"
  rm -f "$R/.claude/hooks/pretooluse.before.py"
  git -C "$R" diff --quiet -- .claude/hooks/pretooluse.py governance/project/path-map.yaml \
    && echo "git diff: both files as committed" || bad "git diff after undo"
  git -C "$R" status --short -- .claude governance
}

step_live_after() {
  say "live_after: the live files and the real sets root's own entry, against before"
  { sha256sum "$MAIN/.claude/hooks/pretooluse.py" "$MAIN/governance/project/path-map.yaml"
    echo "$REAL: $(eval_stat)"; } > "$BASE/live-after.txt"
  cat "$BASE/live-after.txt"
  cmp -s "$BASE/live-before.txt" "$BASE/live-after.txt" && echo "live: unchanged" || bad "a live file changed"
}

STEPS=${*:-prepare plant live_before suites_before apply r2 r1_root r1 override_off suites_after replay measure writer undo live_after}
echo "sets-root guard rehearsal: $(date '+%Y-%m-%d %H:%M:%S %Z'), steps: $STEPS"
env | grep -cE '^(GOV_|CLAUDE_PROJECT_DIR|D=|T=)' | sed 's/^/inherited GOV_, CLAUDE_PROJECT_DIR, D, T variables: /'
for s in $STEPS; do "step_$s"; done
echo
echo "rehearsal done: $(date '+%Y-%m-%d %H:%M:%S %Z'), failures: $FAILS"
