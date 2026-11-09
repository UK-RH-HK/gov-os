#!/usr/bin/env bash
# ACT-GUARD-CALLLOG-1: the rehearsal, end to end, in a scratch clone. Changes nothing live.
#   bash rehearse.sh [step ...]      default: every step, in order; the log goes to rehearsal.log beside this file
# Steps: prepare plant live_before root_planted suites_before guard4_before replay_before apply suites_after
#        guard4_after replay_after planted faults prune concurrent latency micro live_session root_back undo live_after
# It re-runs itself from a fresh shell (env -i with HOME, USER, LOGNAME, PATH and LANG only), as the earlier guard
# rehearsals did. Layout:
#   ~/gov-os-runs/CALLLOG-rehearsal/Dynamic-Agentic-Engineering-OS   the --no-hardlinks clone; apply.sh applied there
#   ~/gov-os-runs/CALLLOG-rehearsal/home/gov-os-eval                  a planted sets root: dummy files only
#   ~/gov-os-runs/CALLLOG-rehearsal/wt                                a worktree of the clone (the every-tree case)
#   /tmp/gov-os-calllog-rehearsal/<step>                              each step's log folder (GOV_GUARD_CALLS_DIR)
# Every hook run with the real HOME happens with the clone's sets_root_hidden root set to the planted absolute path.
# The live log folder ~/.gov-os/guard-calls must not exist before or after (checked at every step).
set -u
if [ -z "${CALLLOG_FRESH:-}" ]; then
  exec env -i HOME="$HOME" USER="${USER:-usain}" LOGNAME="${LOGNAME:-usain}" PATH="$PATH" LANG="${LANG:-C.UTF-8}" \
    CALLLOG_FRESH=1 bash --noprofile --norc "$0" "$@"
fi
MAIN=/home/usain/Dynamic-Agentic-Engineering-OS
SUB=.gov-runtime/scratch/orchestrator
HERE=$MAIN/$SUB/drafts/guard-calllog
BASE=$HOME/gov-os-runs/CALLLOG-rehearsal
R=$BASE/Dynamic-Agentic-Engineering-OS
PH=$BASE/home
PR=$PH/gov-os-eval
WT=$BASE/wt
CL=/tmp/gov-os-calllog-rehearsal
TMPD=/tmp/gov-os-calllog-pytest
LIVE_CALLS=$HOME/.gov-os/guard-calls
PIN=$(head -1 "$HOME/.local/bin/gov" | cut -c3-)
SLOT="bash $MAIN/$SUB/tools/heavy_slot.sh"
D=$R/$SUB/drafts/guard-calllog
T=$R/$SUB/tools
CHK="python3 $D/calllog_check.py"
RW=$MAIN/$SUB/drafts/indep-walls/replay_walls.py
LOG=$HERE/rehearsal.log
UNTIL=${CALLLOG_UNTIL:-$(date -u '+%Y-%m-%dT%H:%M:%S')}
SINCE=${CALLLOG_SINCE:-$(date -u -d "$UNTIL 48 hours ago" '+%Y-%m-%dT%H:%M:%S')}
exec > >(tee -a "$LOG") 2>&1
FAILS=0

say() { printf '\n== %s (%s)\n' "$1" "$(date '+%H:%M:%S')"; no_live_log; }
bad() { echo "REHEARSAL FAIL: $*"; FAILS=$((FAILS + 1)); }
no_live_log() { [ -e "$LIVE_CALLS" ] && { echo "REHEARSAL STOP: $LIVE_CALLS exists: a hook run wrote the live log folder"; exit 3; }; return 0; }
need_planted() {
  local line; line=$(grep -A1 '^sets_root_hidden:' "$R/governance/project/path-map.yaml" | sed -n 2p)
  [ "$line" = "  root: \"$PR\"" ] && return 0
  echo "REHEARSAL STOP: the clone's block reads $line; a hook run now with the real HOME would name the real root"
  exit 3
}
block_root() {
  python3 - "$R/governance/project/path-map.yaml" "$1" <<'EOF'
import sys
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
last_ok() { tail -1 "$1" | grep -qx PASS; }
calls_dir() {  # a fresh log folder for a step, with the apply's salt when there is one
  rm -rf "$CL/$1"; mkdir -m 0700 "$CL/$1"
  [ -f "$CL/calls/salt.key" ] && cp "$CL/calls/salt.key" "$CL/$1/salt.key" && chmod 0400 "$CL/$1/salt.key"
  export GOV_GUARD_CALLS_DIR=$CL/$1
}

step_prepare() {
  say "prepare: the clone"
  if [ -e "$BASE" ]; then
    [ -f "$BASE/.calllog-rehearsal" ] || { bad "$BASE exists and is not this script's"; return 1; }
    git -C "$R" worktree remove --force "$WT" 2>/dev/null
    chmod -R u+w "$BASE" 2>/dev/null
    rm -rf "$BASE"
  fi
  rm -rf "$CL" "$TMPD"; mkdir -p "$CL" "$TMPD"
  mkdir -p "$BASE" && : > "$BASE/.calllog-rehearsal"
  git clone -q --no-hardlinks "$MAIN" "$R" || { bad "clone"; return 1; }
  head=$(git -C "$MAIN" rev-parse HEAD)
  git -C "$R" checkout -q -b calllog-rehearsal "$head" || { bad "checkout"; return 1; }
  git -C "$MAIN" for-each-ref --format='%(refname) %(objectname)' refs/heads/ | while read -r ref sha; do
    [ "$ref" = refs/heads/calllog-rehearsal ] && continue
    git -C "$R" update-ref "$ref" "$sha"
  done
  mkdir -p "$T" "$R/$SUB/drafts"
  cp -p "$MAIN/$SUB/tools/guard4_check.py" "$MAIN/$SUB/tools/heavy_slot.sh" "$T/"
  [ -f "$MAIN/$SUB/tools/heavy_slots.conf" ] && cp -p "$MAIN/$SUB/tools/heavy_slots.conf" "$T/"
  for d in drafts/guard-calllog drafts/act-guard-fix-4 drafts/g14 drafts/act-guard-fix-3; do
    [ -d "$MAIN/$SUB/$d" ] && cp -a "$MAIN/$SUB/$d" "$R/$SUB/drafts/"
  done
  rm -rf "$D/backup" "$D/rehearsal.log" "$R/$SUB/drafts/g14/backup" "$R/$SUB/drafts/g14/backup-g14b" \
         "$R/$SUB/drafts/act-guard-fix-4/backup"
  grep -rlI --null "$MAIN" "$R/$SUB" | xargs -0 -r sed -i "s#$MAIN#$R#g"
  git -C "$R" worktree add -q -b calllog-wt "$WT" "$head" || bad "worktree"
  echo "clone $R at $(git -C "$R" rev-parse --short=12 HEAD) on $(git -C "$R" branch --show-current);" \
       "branches $(git -C "$R" for-each-ref refs/heads/ | wc -l); root mentions left: $(grep -rlI "$MAIN" "$R/$SUB" | wc -l)"
  sha256sum "$R/.claude/hooks/pretooluse.py" | sed "s#$R/##"
  ( cd "$D" && sha256sum pretooluse.candidate.py apply.sh calllog_check.py rehearse.sh ) | cut -c1-12,65-
}

step_plant() {
  say "plant: the dummy sets root $PR (names only, dummy text)"
  E=$PR/fixtures/evaluation
  mkdir -p "$E/memory-retrieval/hidden" "$E/memory-verdict/hidden" "$E/memory-verdict-2/hidden" "$PR/transcripts" \
           "$PR/runs/fresh-80/rows" "$PR/runs/e0" "$PR/governance/project" "$E/sandbox-guard-exp-1/hidden/corpus" \
           "$E/sandbox-guard-exp-1/hidden/labels" "$PR/indep-walls"
  n=0
  for f in memory-retrieval/hidden/q01.yaml memory-verdict/hidden/p01.yaml memory-verdict-2/hidden/p01.yaml \
           sandbox-guard-exp-1/hidden/corpus/actions.jsonl sandbox-guard-exp-1/hidden/labels/labels.jsonl; do
    n=$((n + 1)); printf 'DUMMY MARK-OUTSIDE-%02d planted (%s)\n' $n "$f" > "$E/$f"
  done
  printf 'DUMMY MARK-OUTSIDE-06 transcript\n' > "$PR/transcripts/t01.md"
  printf 'DUMMY MARK-OUTSIDE-07 row\n' > "$PR/runs/fresh-80/rows/q01.json"
  printf 'DUMMY MARK-OUTSIDE-08 counts\n' > "$PR/runs/e0/counts.txt"
  printf 'DUMMY open sibling\n' > "$E/sandbox-guard-exp-1/README.txt"
  python3 - "$R/governance/project/path-map.yaml" "$PR/governance/project/path-map.yaml" <<'EOF'
import sys
lines = open(sys.argv[1], encoding="utf-8").read().splitlines(keepends=True)
at = [i for i, l in enumerate(lines) if l.startswith("evaluation_sets:")][0]
end = next(j for j in range(at + 1, len(lines)) if lines[j][:1] not in ("", " ", "\t", "#", "\n", "\r"))
open(sys.argv[2], "w").write("# DUMMY stub: the repository's evaluation_sets, mirrored\n" +
                              "".join(l for l in lines[at:end] if not l.startswith("#")))
EOF
  echo "planted files: $(find "$PR" -type f | wc -l)"
}

LIVE_FILES=".claude/hooks/pretooluse.py .claude/hooks/role_reads.py .claude/hooks/bash_writes.py
  governance/project/path-map.yaml governance/project/held-out.yaml .claude/settings.json"
live_hashes() {
  ( cd "$MAIN" && sha256sum $LIVE_FILES; ls .claude/settings*.json | xargs sha256sum | grep -v ' .claude/settings.json$' )
  sha256sum "$HOME/.claude/settings.json"
  ls -ld "$HOME/.gov-os" | awk '{print "~/.gov-os:", $1, $3}'
  [ -e "$LIVE_CALLS" ] && echo "LIVE ~/.gov-os/guard-calls EXISTS" || echo "live ~/.gov-os/guard-calls: absent"
  echo "live tracked .claude/ and governance/ edits: $(git -C "$MAIN" status --porcelain --untracked-files=no -- .claude governance | wc -l)"
  echo "info: live main tree at $(git -C "$MAIN" rev-parse --short=12 HEAD) (other sessions commit during the run; the files above are what must not change)"
}
step_live_before() { say "live_before: the live files"; live_hashes | tee "$BASE/live-before.txt"; }

step_root_planted() { say "root_planted: the block's root set to the planted absolute path"; block_root "\"$PR\""; }
step_root_back() { say "root_back: the block's root back to ~/gov-os-eval"; block_root '"~/gov-os-eval"'; }

suites() {
  need_planted
  calls_dir "suites-$1"
  ( cd "$R" && GUARD_FIX4_HOOK=$R/.claude/hooks/pretooluse.py TMPDIR=$TMPD $SLOT env -u PYTEST_ADDOPTS \
      -u PYTEST_PLUGINS PYTHONPATH=$R/src python3 -m pytest "$R/$SUB/drafts/act-guard-fix-4/test_guard_fix_4.py" \
      -p no:cacheprovider -q -n 6 -o tmp_path_retention_policy=failed -rf \
      2>&1 | grep -E "^FAILED|^ERROR|failed|passed|error" | sed "s/^/$1 test_guard_fix_4: /" )
  ( cd "$R" && G14_HOOK=$R/.claude/hooks/pretooluse.py TMPDIR=$TMPD $SLOT env -u PYTEST_ADDOPTS \
      -u PYTEST_PLUGINS PYTHONPATH=$R/src python3 -m pytest "$R/$SUB/drafts/g14/test_g14.py" \
      -p no:cacheprovider -q -n 6 -o tmp_path_retention_policy=failed -rf \
      2>&1 | grep -E "^FAILED|^ERROR|failed|passed|error" | sed "s/^/$1 test_g14: /" )
  ( cd "$R" && TMPDIR=$TMPD $SLOT env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONPATH=$R/src python3 -m pytest \
      tests/acceptance/W2-58/test_w2_58_evaluation_sets.py tests/unit/launch/test_launcher.py \
      tests/unit/hooks/test_live_hook.py tests/unit/guard/test_reads.py \
      -p no:cacheprovider -q -n 6 -o tmp_path_retention_policy=failed -rf \
      2>&1 | grep -E "^FAILED|^ERROR|failed|passed|error" | sed "s/^/$1 W2-58 sets, launcher, live hook, reads: /" )
  $CHK validate "$CL/suites-$1" | tail -3
  unset GOV_GUARD_CALLS_DIR
}
step_suites_before() { say "suites_before: the suites on the clone as it is (the baseline; the hook writes no log)"; suites before; }
step_suites_after() { say "suites_after: the suites with the ACT applied (each hook run logs to its step folder)"; suites after; }

guard4() {
  need_planted
  calls_dir "guard4-$1"
  ( cd "$R" && SETS_PLANTED=1 SETS_OLDMAP_TREE=$WT $SLOT python3 "$T/guard4_check.py" --settings "$R" \
      > "$BASE/guard4-$1.txt" 2>&1 )
  grep -vE '^ok ' "$BASE/guard4-$1.txt"
  echo "guard4 $1: $(grep -c '^ok ' "$BASE/guard4-$1.txt") ok, last line $(tail -1 "$BASE/guard4-$1.txt")"
  last_ok "$BASE/guard4-$1.txt" || bad "guard4 $1"
  $CHK validate "$CL/guard4-$1" | tail -2
  unset GOV_GUARD_CALLS_DIR
}
step_guard4_before() { say "guard4_before: guard4_check.py --settings <clone> (the registered line), root planted"; guard4 before; }
step_guard4_after() { say "guard4_after: the same, the ACT applied"; guard4 after; }

replay() {  # $1 before|after
  need_planted
  calls_dir "replay-$1"
  ( cd "$R" && REPLAY_TICKET=DAEO-sdxk $SLOT python3 "$D/calllog_check.py" replay "$RW" "$R" "$CL/replay-$1" \
      "$R" "$PR" "$R/.claude/hooks/pretooluse.py" "$PIN" "$SINCE" "$UNTIL" "$BASE/replay-$1.json" ) | tail -12 \
      || bad "replay $1"
  unset GOV_GUARD_CALLS_DIR
}
step_replay_before() { say "replay_before: the calls of $SINCE .. $UNTIL UTC, the hook before"; replay before;
  n=$(cat "$CL"/replay-before/*.jsonl 2>/dev/null | wc -l); echo "lines written by the hook before: $n"; [ "$n" = 0 ] || bad "the hook before wrote lines"; }
step_replay_after() {
  say "replay_after: the same calls, the hook after; then before against after, and the log against the calls"
  replay after
  python3 "$RW" compare "$BASE/replay-before.json" "$BASE/replay-after.json" | tee "$BASE/compare.txt" \
    || bad "the two passes judged different calls"
  grep -q '^differences: 0$' "$BASE/compare.txt" || bad "a decision changed in the replay"
  $CHK replaymatch "$CL/replay-after" "$BASE/replay-after.json.recorded.json" | tail -3
  last=$($CHK replaymatch "$CL/replay-after" "$BASE/replay-after.json.recorded.json" | tail -1); [ "$last" = PASS ] || bad "replaymatch"
}

step_apply() {
  say "apply: apply.sh check, apply in the clone, log folder $CL/calls"
  bash "$D/apply.sh" check --calls-dir "$CL/calls" || { bad "apply.sh check"; return 1; }
  bash "$D/apply.sh" apply --calls-dir "$CL/calls" || { bad "apply.sh apply"; return 1; }
  bash "$D/apply.sh" apply --calls-dir "$CL/calls" >/dev/null 2>&1 && bad "a second apply ran" || echo "a second apply: refused"
  bash "$D/apply.sh" check --calls-dir "$CL/calls" | tail -1
  bash "$D/apply.sh" check --calls-dir "$R/inside" >/dev/null 2>&1 && bad "a log folder inside the tree was accepted" \
    || echo "a log folder inside the tree: refused"
  git -C "$R" status --short -- .claude governance
  git -C "$R" diff --stat
  ls -la "$CL/calls" | sed 1d | awk '{print $1, $NF}'
  cp -p "$D/backup/pretooluse.py" "$R/.claude/hooks/pretooluse.before.py"  # the hook before, beside its modules
}

step_planted() {
  say "planted: a planted session's allowed, refused and asked calls: the expected lines and nothing else"
  calls_dir planted
  $CHK planted "$R" "$CL/planted" "$R/.claude/hooks/pretooluse.before.py" "$PIN" | tee "$BASE/planted.txt" | grep -vE '^   line'
  last_ok "$BASE/planted.txt" || bad "planted"
  unset GOV_GUARD_CALLS_DIR
}
step_faults() {
  say "faults: a log folder that cannot be written never changes a decision"
  $CHK faults "$R" "$CL/faults" "$R/.claude/hooks/pretooluse.before.py" "$PIN" | tee "$BASE/faults.txt" | grep -vE '^[^:]*: [0-9]+ lines; by'
  last_ok "$BASE/faults.txt" || bad "faults"
}
step_prune() { say "prune: the day files past 92 days, by name only"; $CHK prune "$R" "$CL/prune" "$PIN" | tee "$BASE/prune.txt"; last_ok "$BASE/prune.txt" || bad "prune"; }
step_concurrent() { say "concurrent: 8 sessions at once into one day file"; $CHK concurrent "$R" "$CL/conc" "$PIN" | tee "$BASE/conc.txt"; last_ok "$BASE/conc.txt" || bad "concurrent"; }
step_latency() { say "latency: the hook before and after, alternated, 3 calls x 40"; $CHK latency "$R" "$CL/latency" "$R/.claude/hooks/pretooluse.before.py" "$PIN" 40 | tee "$BASE/latency.txt"; last_ok "$BASE/latency.txt" || bad "latency"; }
step_micro() { say "micro: the log's own cost in the process"; ( cd /tmp && "$PIN" -E "$D/calllog_check.py" micro "$R" "$CL/micro" ) | tee "$BASE/micro.txt"; last_ok "$BASE/micro.txt" || bad "micro"; }

step_live_session() {
  say "live_session: a headless session (haiku) in the clone, as an engineer: its calls matched to the log by sha256"
  need_planted
  calls_dir live
  local prompt="This is the owner's rehearsal of the guard's call log (ACT-GUARD-CALLLOG-1) in a scratch clone. The guard is
expected to refuse some of these calls; that is the test, so make each call exactly once, in order, even when you
expect a refusal, and do not retry or work around a refusal. 1) Read the file README.md with limit 5. 2) Bash:
echo MARK-CALLLOG-77 3) Bash: sudo true 4) Read the file x/.env 5) Write the file tests/acceptance/W2-64/t_calllog.py
with the content MARK-CALLLOG-78 6) Glob with the pattern *.md. Then reply DONE."
  local start; start=$(date +%s)
  ( cd "$R" && timeout 600 env GOV_ROLE=engineer GOV_TICKET=DAEO-sdxk GOV_GUARD_CALLS_DIR="$CL/live" \
      claude -p --model haiku --no-session-persistence --strict-mcp-config --max-budget-usd 0.30 \
      --allowedTools "Read,Bash,Write,Glob" --output-format stream-json --verbose "$prompt" \
      > "$BASE/live.jsonl" 2> "$BASE/live.err" < /dev/null )
  echo "live session: exit $? in $(( $(date +%s) - start )) s; cost $(tail -1 "$BASE/live.jsonl" | python3 -c 'import json,sys;print(json.load(sys.stdin).get("total_cost_usd"))' 2>/dev/null)"
  $CHK live "$CL/live" "$BASE/live.jsonl" "$CL/live" | tee "$BASE/live.txt"
  last_ok "$BASE/live.txt" || bad "live session"
  grep -c MARK-CALLLOG "$CL"/live/*.jsonl | sed 's/^/marker lines in the log (expect 0): /'
  unset GOV_GUARD_CALLS_DIR
}

step_undo() {
  say "undo: apply.sh undo"
  rm -f "$R/.claude/hooks/pretooluse.before.py"
  bash "$D/apply.sh" undo --calls-dir "$CL/calls" || bad "apply.sh undo"
  git -C "$R" diff --quiet -- .claude && echo "git diff: the hook as committed" || bad "git diff after undo"
  [ -z "$(git -C "$R" status --short -- .claude)" ] && echo "git status: clean" || bad "status after undo"
  echo "an apply then an undo with nothing logged (a fresh folder):"
  mv "$D/backup" "$D/backup-1"
  bash "$D/apply.sh" apply --calls-dir "$CL/fresh" >/dev/null || bad "the second apply"
  bash "$D/apply.sh" undo --calls-dir "$CL/fresh" | grep -E "log folder:|undo:" || bad "the second undo"
  [ -e "$CL/fresh" ] && bad "the fresh log folder was left" || echo "the fresh log folder: removed"
  rm -rf "$D/backup"; mv "$D/backup-1" "$D/backup"
}

step_live_after() {
  say "live_after: the live files against before"
  live_hashes > "$BASE/live-after.txt"
  cat "$BASE/live-after.txt"
  cmp -s <(grep -v '^info:' "$BASE/live-before.txt") <(grep -v '^info:' "$BASE/live-after.txt") && echo "live: unchanged" || bad "a live file changed"
}

STEPS=${*:-prepare plant live_before root_planted suites_before guard4_before replay_before apply suites_after guard4_after replay_after planted faults prune concurrent latency micro live_session root_back undo live_after}
echo "calllog rehearsal: $(date '+%Y-%m-%d %H:%M:%S %Z'), replay window $SINCE .. $UNTIL UTC, steps: $STEPS"
env | grep -cE '^(GOV_|CLAUDE_PROJECT_DIR)' | sed 's/^/inherited GOV_ and CLAUDE_PROJECT_DIR variables: /'
for s in $STEPS; do "step_$s"; done
no_live_log
echo
echo "rehearsal done: $(date '+%Y-%m-%d %H:%M:%S %Z'), failures: $FAILS"
