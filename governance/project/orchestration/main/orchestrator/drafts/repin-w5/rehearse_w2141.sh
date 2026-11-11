#!/usr/bin/env bash
# W2-141's staged hook rebuilt on ACT-SETS-GLOBS-1's hook (DECIDED-NOT-DONE row 78, DEC-1112 (3)): the re-checks, in a
# scratch clone with a planted HOME. Changes nothing live. Modelled on drafts/sets-globs/rehearse.sh (its prepare,
# plant, sg, walls, guard4, suites, replay and latency steps, unchanged in substance).
#   bash rehearse_w2141.sh [step ...]   default: every step, in order; the log: w2141-rehearsal.log beside this file
# COPY for the re-pin window 5 (DECIDED-NOT-DONE row 88, review F4): the same steps with the CANDIDATE pin (W141_PIN, the
# interpreter of the pin the re-pin script installed) and the base in /tmp/gov-os-emg-repin5/w141 (never ~/gov-os-runs).
# "before" is the clone at the main tree's head (the live hook 74f8dbea4761 and role_reads 5407aade9417); "after" is
# the same clone with W2-141's staged pair (docs/changes/W2-141-hook/pretooluse.py and role_reads.py, from the main
# tree's working copy, checked by hash) copied over .claude/hooks/. The map is the live one in both (44f99ea563cb):
# ACT-SETS-GLOBS-1 is applied, so sets_globs_check.py expects its "after" answers in both.
# Layout ($BASE = /tmp/gov-os-emg-repin5/w141, marked by its .w2-141-rebase-rehearsal file):
#   Dynamic-Agentic-Engineering-OS   the --no-hardlinks clone of the main tree at its head
#   home/gov-os-eval                 the planted sets root: dummy lines only (sets-globs' layout)
#   wt                               a worktree of the clone (the every-tree cases)
#   calls                            every hook run's call log (GOV_GUARD_CALLS_DIR), never the live one
# The real sets root is never opened, listed or stat'ed.
set -u
if [ -z "${SG_FRESH:-}" ]; then
  exec env -i HOME="$HOME" USER="${USER:-usain}" LOGNAME="${LOGNAME:-usain}" PATH="$PATH" LANG="${LANG:-C.UTF-8}" \
    SG_FRESH=1 W141_PIN="${W141_PIN:-}" ${SG_UNTIL:+SG_UNTIL=$SG_UNTIL} ${SG_SINCE:+SG_SINCE=$SG_SINCE} bash --noprofile --norc "$0" "$@"
fi
MAIN=/home/usain/Dynamic-Agentic-Engineering-OS
SUB=.gov-runtime/scratch/orchestrator
HERE=$MAIN/$SUB/drafts/repin-w5
BASE=/tmp/gov-os-emg-repin5/w141
R=$BASE/Dynamic-Agentic-Engineering-OS
PH=$BASE/home
PR=$PH/gov-os-eval
WT=$BASE/wt
TMPD=$BASE/pytest-tmp
PIN=${W141_PIN:?W141_PIN: the candidate pin's python (the re-pin rehearsal's pin-<C>/bin/python)}
[ -x "$PIN" ] || { echo "W141_PIN $PIN is not executable"; exit 2; }
SLOT="bash $MAIN/$SUB/tools/heavy_slot.sh"
D=$R/$SUB/drafts/sets-globs
T=$R/$SUB/tools
LOG=$HERE/w2141-rehearsal.log
UNTIL=${SG_UNTIL:-$(date -u '+%Y-%m-%dT%H:%M:%S')}
SINCE=${SG_SINCE:-$(date -u -d "$UNTIL 48 hours ago" '+%Y-%m-%dT%H:%M:%S')}
LIVE_HOOK=74f8dbea4761de37628305e5d58125641ae39a409a7ed0a2babb379b1ceca5b8
LIVE_RR=5407aade941734c086aefefe5372e715262aedc1805380f9427b068eb2444f07
STAGED=$MAIN/docs/changes/W2-141-hook
export GOV_GUARD_CALLS_DIR=$BASE/calls
export TMPDIR=$TMPD
exec > >(tee -a "$LOG") 2>&1
FAILS=0
START=$(date -u '+%Y-%m-%dT%H:%M:%S')

say() { printf '\n== %s (%s)\n' "$1" "$(date '+%H:%M:%S')"; }
bad() { echo "REHEARSAL FAIL: $*"; FAILS=$((FAILS + 1)); }
last_ok() { tail -1 "$1" | grep -qx PASS; }
root_line() { grep -A1 '^sets_root_hidden:' "$R/governance/project/path-map.yaml" | sed -n 2p; }
need_planted() {
  [ "$(root_line)" = "  root: \"$PR\"" ] && return 0
  echo "REHEARSAL STOP: the clone's block reads $(root_line); a hook run with the real HOME would name the real root"; exit 3
}
block_root() {  # $1 the new root value
  python3 - "$R/governance/project/path-map.yaml" "$1" <<'EOF'
import sys
p, new = sys.argv[1], sys.argv[2]
lines = open(p, encoding="utf-8").read().splitlines(keepends=True)
at = [i for i, l in enumerate(lines) if l.startswith("sets_root_hidden:")]
assert len(at) == 1, at
assert lines[at[0] + 1].startswith("  root: ")
lines[at[0] + 1] = f"  root: {new}\n"
open(p, "w", encoding="utf-8").write("".join(lines))
print("sets block root:", new)
EOF
}

step_prepare() {
  say "prepare: the clone, its worktree, the drafts"
  if [ -e "$BASE" ]; then
    [ -f "$BASE/.w2-141-rebase-rehearsal" ] || { bad "$BASE exists and is not this script's"; return 1; }
    git -C "$R" worktree remove --force "$WT" 2>/dev/null
    chmod -R u+w "$BASE" 2>/dev/null
    rm -rf "$BASE"
  fi
  mkdir -p "$BASE" "$BASE/calls" "$TMPD" && : > "$BASE/.w2-141-rebase-rehearsal"
  head=$(git -C "$MAIN" rev-parse HEAD)
  git clone -q --no-hardlinks "$MAIN" "$R" || { bad "clone"; return 1; }
  git -C "$R" config core.hooksPath "$BASE/no-git-hooks"
  git -C "$R" checkout -q -B w2/integrate "$head" || { bad "checkout"; return 1; }
  git -C "$R" config user.name "w2-141 rebase rehearsal"; git -C "$R" config user.email "w2141@localhost"
  mkdir -p "$R/$SUB/drafts"
  cp -a "$MAIN/$SUB/tools" "$R/$SUB/"; rm -rf "$T/__pycache__"
  for d in drafts/sets-globs drafts/indep-walls drafts/sets-root-guard drafts/act-guard-fix-4 drafts/g14 drafts/act-guard-fix-3; do
    [ -d "$MAIN/$SUB/$d" ] && cp -a "$MAIN/$SUB/$d" "$R/$SUB/drafts/"
  done
  rm -rf "$D/backup" "$D/rehearsal.log" "$R/$SUB/drafts/indep-walls/backup" "$R/$SUB/drafts/sets-root-guard/backup" \
         "$R/$SUB/drafts/act-guard-fix-4/backup" "$R/$SUB/drafts/g14/backup" "$R/$SUB/drafts/g14/backup-g14b"
  grep -rlI --null "$MAIN" "$R/$SUB" | grep -zv "/drafts/sets-globs/" | xargs -0 -r sed -i "s#$MAIN#$R#g"
  git -C "$R" worktree add -q -b sg-wt "$WT" "$head" || bad "worktree"
  echo "clone $R at $(git -C "$R" rev-parse --short=12 HEAD) on $(git -C "$R" branch --show-current)"
  ( cd "$R" && sha256sum .claude/hooks/pretooluse.py .claude/hooks/role_reads.py governance/project/path-map.yaml ) | cut -c1-12,65-
  [ "$(sha256sum < "$R/.claude/hooks/pretooluse.py" | cut -c1-64)" = "$LIVE_HOOK" ] || bad "the clone's hook is not 74f8dbea4761"
  [ "$(sha256sum < "$R/.claude/hooks/role_reads.py" | cut -c1-64)" = "$LIVE_RR" ] || bad "the clone's role_reads is not 5407aade9417"
  ( cd "$STAGED" && sha256sum pretooluse.py role_reads.py ) | cut -c1-12,65- | sed 's/^/staged: /'
  diff "$R/.claude/hooks/pretooluse.py" "$STAGED/pretooluse.py"
}

step_plant() {
  say "plant: the planted sets root (dummy lines; sets-globs' layout)"
  E=$PR/fixtures/evaluation
  mkdir -p "$E/memory-retrieval/hidden" "$E/memory-verdict/hidden" "$E/memory-verdict-2/hidden" "$PR/transcripts" \
           "$PR/runs/fresh-80/rows" "$PR/runs/e0" "$PR/governance/project" "$E/sandbox-guard-exp-1/hidden/corpus" \
           "$E/sandbox-guard-exp-1/hidden/labels" "$PR/indep-walls" "$E/memory-retrieval/visible"
  n=0
  for f in memory-retrieval/hidden/q01.yaml memory-verdict/hidden/p01.yaml memory-verdict-2/hidden/p01.yaml \
           sandbox-guard-exp-1/hidden/corpus/actions.jsonl sandbox-guard-exp-1/hidden/labels/labels.jsonl; do
    n=$((n + 1)); printf 'DUMMY MARK-OUTSIDE-%02d planted (%s)\n' $n "$f" > "$E/$f"
  done
  printf 'DUMMY MARK-OUTSIDE-06 transcript\n' > "$PR/transcripts/t01.md"
  printf 'DUMMY MARK-OUTSIDE-07 row\n' > "$PR/runs/fresh-80/rows/q01.json"
  printf 'DUMMY MARK-OUTSIDE-08 counts\n' > "$PR/runs/e0/counts.txt"
  printf 'DUMMY open sibling\n' > "$E/sandbox-guard-exp-1/README.txt"
  printf 'DUMMY open visible\n' > "$E/memory-retrieval/visible/q01.yaml"
  python3 - "$D/sets_globs_check.py" "$PR" <<'EOF'
import os, runpy, sys
files = runpy.run_path(sys.argv[1], run_name="plant")["PLANTED_FILES"]
for n, rel in enumerate(files, 20):
    p = os.path.join(sys.argv[2], rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(f"DUMMY MARK-OUTSIDE-{n} planted ({rel})\n")
print("the destinations planted:", len(files), "files")
EOF
  python3 - "$R/governance/project/path-map.yaml" "$PR/governance/project/path-map.yaml" <<'EOF'
import sys
lines = open(sys.argv[1], encoding="utf-8").read().splitlines(keepends=True)
at = [i for i, l in enumerate(lines) if l.startswith("evaluation_sets:")][0]
end = next(j for j in range(at + 1, len(lines)) if lines[j][:1] not in ("", " ", "\t", "#", "\n", "\r"))
open(sys.argv[2], "w").write("# DUMMY stub\n" + "".join(l for l in lines[at:end] if not l.startswith("#")))
EOF
  echo "planted: $(find "$PH" -type f | wc -l) files"
}

live_hashes() {
  ( cd "$MAIN" && sha256sum .claude/hooks/pretooluse.py .claude/hooks/role_reads.py .claude/hooks/bash_writes.py \
      governance/project/path-map.yaml governance/project/held-out.yaml .claude/settings.json \
      governance/project/orchestration/tools/indep_launch.py governance/project/indep-walls/* \
      $SUB/tools/guard4_check.py $SUB/drafts/indep-walls/walls_check.py \
      docs/changes/W2-141-hook/pretooluse.py docs/changes/W2-141-hook/role_reads.py; ls .claude/settings*.json | xargs sha256sum )
  sha256sum "$HOME/.claude/settings.json"
}
step_live_before() { say "live_before: the live files"; live_hashes | tee "$BASE/live-before.txt"; }
step_live_after() {
  say "live_after: the live files against before"
  live_hashes > "$BASE/live-after.txt"; cat "$BASE/live-after.txt"
  cmp -s "$BASE/live-before.txt" "$BASE/live-after.txt" && echo "live: unchanged" || bad "a live file changed"
  echo "this rehearsal's hook runs logged in $BASE/calls: $(cat "$BASE"/calls/*.jsonl 2>/dev/null | wc -l) lines"
  python3 "$D/livelog_count.py" "$HOME/.gov-os/guard-calls" "$START"
}
step_root_planted() { say "root_planted"; block_root "\"$PR\""; }
step_root_back() { say "root_back"; block_root '"~/gov-os-eval"'; }

step_stage() {
  say "stage: W2-141's staged pair over the clone's hook (the ACT's copy step)"
  cp "$STAGED/pretooluse.py" "$R/.claude/hooks/pretooluse.py" && cp "$STAGED/role_reads.py" "$R/.claude/hooks/role_reads.py" \
    && rm -rf "$R/.claude/hooks/__pycache__" || { bad "stage"; return 1; }
  cp "$STAGED/pretooluse.py" "$WT/.claude/hooks/pretooluse.py" && cp "$STAGED/role_reads.py" "$WT/.claude/hooks/role_reads.py" \
    && rm -rf "$WT/.claude/hooks/__pycache__" || { bad "stage wt"; return 1; }
  ( cd "$R" && sha256sum .claude/hooks/pretooluse.py .claude/hooks/role_reads.py ) | cut -c1-12,65-
  git -C "$R" status --short -- .claude
}

sg() {  # $1 label
  need_planted
  ( cd "$R" && HOME=$PH GOV_PIN_PY=$PIN SG_EXPECT=after SETS_PLANTED=1 SG_TREE2=$WT \
      $SLOT python3 "$D/sets_globs_check.py" "$R" > "$BASE/sg-$1.txt" 2>&1 )
  grep -vE '^ok ' "$BASE/sg-$1.txt" | tail -40
  echo "sg $1: $(grep -c '^ok ' "$BASE/sg-$1.txt") ok, $(grep -c '^FAIL ' "$BASE/sg-$1.txt") failed"
  last_ok "$BASE/sg-$1.txt" || bad "sets_globs_check $1"
}
walls() {
  need_planted
  ( cd "$R" && HOME=$PH GOV_PIN_PY=$PIN SETS_PLANTED=1 $SLOT python3 "$R/$SUB/drafts/indep-walls/walls_check.py" repo "$R" \
      > "$BASE/walls-$1.txt" 2>&1 )
  grep -vE '^ok ' "$BASE/walls-$1.txt" | tail -6
  last_ok "$BASE/walls-$1.txt" || bad "walls $1"
}
guard4() {
  need_planted
  ( cd "$R" && SETS_PLANTED=1 SETS_OLDMAP_TREE=$WT $SLOT python3 "$T/guard4_check.py" --settings "$R" > "$BASE/guard4-$1.txt" 2>&1 )
  grep -vE '^ok ' "$BASE/guard4-$1.txt" | tail -8
  last_ok "$BASE/guard4-$1.txt" || bad "guard4 $1"
}
suites() {
  need_planted
  ( cd "$R" && GUARD_FIX4_HOOK=$R/.claude/hooks/pretooluse.py $SLOT env -u PYTEST_ADDOPTS \
      -u PYTEST_PLUGINS PYTHONPATH=$R/src python3 -m pytest "$R/$SUB/drafts/act-guard-fix-4/test_guard_fix_4.py" \
      -p no:cacheprovider -q -n 6 -o tmp_path_retention_policy=failed -rf \
      2>&1 | grep -E "^FAILED|^ERROR|failed|passed|error" | sed "s/^/$1 test_guard_fix_4: /" )
  ( cd "$R" && G14_HOOK=$R/.claude/hooks/pretooluse.py $SLOT env -u PYTEST_ADDOPTS \
      -u PYTEST_PLUGINS PYTHONPATH=$R/src python3 -m pytest "$R/$SUB/drafts/g14/test_g14.py" \
      -p no:cacheprovider -q -n 6 -o tmp_path_retention_policy=failed -rf \
      2>&1 | grep -E "^FAILED|^ERROR|failed|passed|error" | sed "s/^/$1 test_g14: /" )
  ( cd "$R" && $SLOT env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONPATH=$R/src python3 -m pytest \
      tests/unit/hooks/test_live_hook.py tests/unit/guard/test_reads.py \
      -p no:cacheprovider -q -n 6 -o tmp_path_retention_policy=failed -rf \
      2>&1 | grep -E "^FAILED|^ERROR|failed|passed|error" | sed "s/^/$1 live hook, reads: /" )
}
replay() {  # $1 label, $2 the ticket every call is judged under
  need_planted
  ( cd "$R" && REPLAY_TICKET=$2 $SLOT python3 "$D/replay_globs.py" pass "$R" "$PR" "$R/.claude/hooks/pretooluse.py" \
      "$PIN" "$SINCE" "$UNTIL" "$BASE/replay-$1.json" ) > "$BASE/replay-$1.out" 2>&1 || bad "replay $1"
  python3 -c "import json,sys,collections;d=json.load(open(sys.argv[1]));print('replay $1:', d['counts'], dict(collections.Counter(v['d'] for v in d['answers'].values())))" "$BASE/replay-$1.json"
}
compare() {  # $1 before label, $2 after label
  python3 "$D/replay_globs.py" compare "$BASE/replay-$1.json" "$BASE/replay-$2.json" > "$BASE/compare-$2.txt"
  echo "compare $1 -> $2 (exit $?):"; cat "$BASE/compare-$2.txt"
}
latency() {
  need_planted
  ( cd "$R" && GOV_PIN_PY=$PIN python3 - "$R" "$PR" "$PIN" "$BASE/latency-$1.json" <<'EOF'
import json, os, statistics, subprocess, sys, time
r, pr, py, out = sys.argv[1:]
calls = [("Bash", {"command": "ls fixtures/evaluation"}), ("Grep", {"pattern": "x", "path": r}),
         ("Glob", {"pattern": "**/*.py", "path": r + "/src"}),
         ("Bash", {"command": f"ls {pr}/runs"}), ("Grep", {"pattern": "x", "path": f"{pr}/fixtures/evaluation/memory-retrieval/visible"}),
         ("Bash", {"command": "git diff --name-only HEAD~1 | xargs grep -l x"}),
         ("Bash", {"command": "git grep -l x HEAD -- '*.yaml' '*.json'"}), ("Read", {"file_path": f"{r}/README.md"})]
ms = {}
for rnd in range(20):
    for tool, tin in calls:
        for role, ticket in (("orchestrator", "DAEO-sdxk"), ("engineer", "DAEO-xwro")):
            ev = {"tool_name": tool, "tool_input": tin, "cwd": r, "session_id": "w2-141-latency", "agent_type": None}
            env = dict(os.environ, GOV_ROLE=role, GOV_TICKET=ticket, CLAUDE_PROJECT_DIR=r); env.pop("PYTHONPATH", None)
            t0 = time.monotonic()
            subprocess.run([py, "-E", r + "/.claude/hooks/pretooluse.py"], input=json.dumps(ev), capture_output=True, text=True, env=env)
            ms.setdefault(role + " " + tool + " " + json.dumps(tin)[:60], []).append((time.monotonic() - t0) * 1000)
med = {k: round(statistics.median(v), 1) for k, v in ms.items()}
json.dump(med, open(out, "w"), indent=1)
for k, v in med.items():
    print(f"  {v:7.1f} ms  {k}")
print("median ms per call:", round(statistics.median([x for v in ms.values() for x in v]), 1))
EOF
  )
}
step_sg_before() { say "sg_before: sets_globs_check.py, the live hook (expect the ACT's answers: PASS)"; sg before; }
step_sg_after() { say "sg_after: sets_globs_check.py, W2-141's staged pair (expect PASS, 0 failed)"; sg after; }
step_walls_before() { say "walls_before: walls_check.py repo <clone>, HOME planted"; walls before; }
step_walls_after() { say "walls_after"; walls after; }
step_guard4_before() { say "guard4_before (the registered line, root planted)"; guard4 before; }
step_guard4_after() { say "guard4_after"; guard4 after; }
step_suites_before() { say "suites_before"; suites before; }
step_suites_after() { say "suites_after"; suites after; }
step_latency_before() { say "latency_before"; latency before; }
step_latency_after() { say "latency_after"; latency after; }
step_replay_before() { say "replay_before: $SINCE .. $UNTIL UTC, the live hook, under DAEO-sdxk and DAEO-xwro (W2-141)"; replay before DAEO-sdxk; replay before-xwro DAEO-xwro; }
step_replay_after() {
  say "replay_after: the same calls, W2-141's staged pair; before against after"
  replay after DAEO-sdxk; replay after-xwro DAEO-xwro
  compare before after; compare before-xwro after-xwro
}

STEPS=${*:-prepare plant live_before root_planted sg_before walls_before guard4_before suites_before latency_before replay_before stage sg_after walls_after guard4_after suites_after latency_after replay_after root_back live_after}
echo "w2-141 rebase rehearsal: $(date '+%Y-%m-%d %H:%M:%S %Z'), replay window $SINCE .. $UNTIL UTC, steps: $STEPS"
env | grep -cE '^(GOV_ROLE|GOV_TICKET|CLAUDE_PROJECT_DIR)=' | sed 's/^/inherited GOV_ROLE, GOV_TICKET and CLAUDE_PROJECT_DIR variables: /'
for s in $STEPS; do "step_$s"; done
echo
echo "rehearsal done: $(date '+%Y-%m-%d %H:%M:%S %Z'), failures: $FAILS"
