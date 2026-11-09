#!/usr/bin/env bash
# ACT-SETS-GLOBS-1: the rehearsal, end to end, in a scratch clone with a planted HOME. Changes nothing live.
#   bash rehearse.sh [step ...]      default: every step, in order; the log: rehearsal.log beside this file
# It re-runs itself from a fresh shell (env -i), as the earlier guard rehearsals did. Layout ($BASE =
# ~/gov-os-runs/SETS-GLOBS-rehearsal, marked by its .sets-globs-rehearsal file):
#   Dynamic-Agentic-Engineering-OS   the --no-hardlinks clone of the main tree at its head; apply.sh applied there
#   home/gov-os-eval                 the planted sets root: dummy lines only (the earlier rehearsals' layout and the
#                                    launch script's three destinations, sets_globs_check.py's PLANTED_FILES)
#   wt                               a worktree of the clone (the every-tree cases)
#   calls                            every hook run's call log (GOV_GUARD_CALLS_DIR), never the live ~/.gov-os/guard-calls
#   e2e-before, e2e-after            deliver_check.py's planted worlds (the W2-149 harness)
# The real sets root is never opened or listed: only its own stat line is taken. While the clone's block reads
# root: "~/gov-os-eval", the hook runs only with HOME planted; every run with the real HOME (guard4's registered line,
# the suites, the replays) happens with the block's root set to the planted absolute path (need_planted).
set -u
if [ -z "${SG_FRESH:-}" ]; then
  exec env -i HOME="$HOME" USER="${USER:-usain}" LOGNAME="${LOGNAME:-usain}" PATH="$PATH" LANG="${LANG:-C.UTF-8}" \
    SG_FRESH=1 ${SG_UNTIL:+SG_UNTIL=$SG_UNTIL} ${SG_SINCE:+SG_SINCE=$SG_SINCE} bash --noprofile --norc "$0" "$@"
fi
MAIN=/home/usain/Dynamic-Agentic-Engineering-OS
SUB=.gov-runtime/scratch/orchestrator
HERE=$MAIN/$SUB/drafts/sets-globs
BASE=$HOME/gov-os-runs/SETS-GLOBS-rehearsal
R=$BASE/Dynamic-Agentic-Engineering-OS
PH=$BASE/home
PR=$PH/gov-os-eval
WT=$BASE/wt
TMPD=/tmp/gov-os-sets-globs-pytest
PIN=$(head -1 "$HOME/.local/bin/gov" | cut -c3-)
SLOT="bash $MAIN/$SUB/tools/heavy_slot.sh"
D=$R/$SUB/drafts/sets-globs
T=$R/$SUB/tools
LOG=$HERE/rehearsal.log
UNTIL=${SG_UNTIL:-$(date -u '+%Y-%m-%dT%H:%M:%S')}
SINCE=${SG_SINCE:-$(date -u -d "$UNTIL 48 hours ago" '+%Y-%m-%dT%H:%M:%S')}
REAL=$HOME/gov-os-eval
export GOV_GUARD_CALLS_DIR=$BASE/calls
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
need_home_root() {
  [ "$(root_line)" = '  root: "~/gov-os-eval"' ] && return 0
  echo "REHEARSAL STOP: the clone's block reads $(root_line), not ~/gov-os-eval"; exit 3
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
eval_stat() { stat -c 'inode %i mode %a size %s mtime %Y ctime %Z' "$REAL" 2>&1; }

step_prepare() {
  say "prepare: the clone, its worktree, the drafts"
  if [ -e "$BASE" ]; then
    [ -f "$BASE/.sets-globs-rehearsal" ] || { bad "$BASE exists and is not this script's"; return 1; }
    git -C "$R" worktree remove --force "$WT" 2>/dev/null
    chmod -R u+w "$BASE" 2>/dev/null
    rm -rf "$BASE"
  fi
  rm -rf "$TMPD"; mkdir -p "$TMPD" "$BASE" "$BASE/calls" && : > "$BASE/.sets-globs-rehearsal"
  head=$(git -C "$MAIN" rev-parse HEAD)
  git clone -q --no-hardlinks "$MAIN" "$R" || { bad "clone"; return 1; }
  git -C "$R" config core.hooksPath "$BASE/no-git-hooks"   # no live git hook ever runs from the clone
  git -C "$R" checkout -q -B w2/integrate "$head" || { bad "checkout"; return 1; }
  git -C "$R" config user.name "sets-globs rehearsal"; git -C "$R" config user.email "sg@localhost"
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
  sha256sum "$R/.claude/hooks/pretooluse.py" "$R/governance/project/path-map.yaml" | sed "s#$R/##" | cut -c1-12,65-
  ( cd "$D" && sha256sum apply.sh pretooluse.candidate.py path-map.candidate.yaml sets_globs_check.py deliver_check.py \
      replay_globs.py rehearse.sh ) | cut -c1-12,65-
}

step_plant() {
  say "plant: the planted sets root (dummy lines; the earlier layout and the three destinations)"
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
print("the three destinations planted:", len(files), "files")
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
      $SUB/tools/guard4_check.py $SUB/drafts/indep-walls/walls_check.py; ls .claude/settings*.json | xargs sha256sum )
  sha256sum "$HOME/.claude/settings.json"
  echo "~/gov-os-operator: $(cd "$HOME/gov-os-operator" && find . -path ./log -prune -o -path ./queue -prune -o -type f -print | sort | xargs sha256sum | sha256sum | cut -c1-12) (all but log/ and queue/)"
  echo "real sets root (its own entry only): $(eval_stat)"
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

sg() {  # $1 label, $2 before|after, [$3 map file to put in place for this run only]
  need_planted
  ( cd "$R" && HOME=$PH GOV_PIN_PY=$PIN SG_EXPECT=$2 SETS_PLANTED=1 SG_TREE2=$WT \
      $SLOT python3 "$D/sets_globs_check.py" "$R" > "$BASE/sg-$1.txt" 2>&1 )
  grep -vE '^ok ' "$BASE/sg-$1.txt" | tail -40
}
step_gap() { say "gap: sets_globs_check.py on the clone as it is (expect before: every N and L case allowed)"; sg gap before; last_ok "$BASE/sg-gap.txt" || bad "gap"; }
step_maponly() {
  say "maponly: the candidate map with the live hook (why the hook changes): the cases expecting after"
  cp -p "$R/governance/project/path-map.yaml" "$BASE/map-saved.yaml"
  cp "$D/path-map.candidate.yaml" "$R/governance/project/path-map.yaml"; block_root "\"$PR\"" >/dev/null
  sg maponly after
  echo "maponly: $(grep -c '^FAIL ' "$BASE/sg-maponly.txt") cases differ from the ACT's answers, of which O (nothing else changed): $(grep -c '^FAIL \[[LR]\] O' "$BASE/sg-maponly.txt")"
  cp -p "$BASE/map-saved.yaml" "$R/governance/project/path-map.yaml"; need_planted
}
step_after() { say "after: sets_globs_check.py with the ACT applied (HOME planted)"; sg after after; last_ok "$BASE/sg-after.txt" || bad "after"; }

walls() {
  need_planted
  ( cd "$R" && HOME=$PH GOV_PIN_PY=$PIN SETS_PLANTED=1 $SLOT python3 "$R/$SUB/drafts/indep-walls/walls_check.py" repo "$R" \
      > "$BASE/walls-$1.txt" 2>&1 )
  grep -vE '^ok ' "$BASE/walls-$1.txt" | tail -4
  last_ok "$BASE/walls-$1.txt" || bad "walls $1"
}
guard4() {
  need_planted
  ( cd "$R" && SETS_PLANTED=1 SETS_OLDMAP_TREE=$WT $SLOT python3 "$T/guard4_check.py" --settings "$R" > "$BASE/guard4-$1.txt" 2>&1 )
  grep -vE '^ok ' "$BASE/guard4-$1.txt" | tail -5
  last_ok "$BASE/guard4-$1.txt" || bad "guard4 $1"
}
suites() {
  need_planted
  ( cd "$R" && GUARD_FIX4_HOOK=$R/.claude/hooks/pretooluse.py TMPDIR=$TMPD $SLOT env -u PYTEST_ADDOPTS \
      -u PYTEST_PLUGINS PYTHONPATH=$R/src python3 -m pytest "$R/$SUB/drafts/act-guard-fix-4/test_guard_fix_4.py" \
      -p no:cacheprovider -q -n 6 -o tmp_path_retention_policy=failed -rf \
      2>&1 | grep -E "^FAILED|^ERROR|failed|passed|error" | sed "s/^/$1 test_guard_fix_4: /" )
  ( cd "$R" && G14_HOOK=$R/.claude/hooks/pretooluse.py TMPDIR=$TMPD $SLOT env -u PYTEST_ADDOPTS \
      -u PYTEST_PLUGINS PYTHONPATH=$R/src python3 -m pytest "$R/$SUB/drafts/g14/test_g14.py" \
      -p no:cacheprovider -q -n 6 -o tmp_path_retention_policy=failed -rf \
      2>&1 | grep -E "^FAILED|^ERROR|failed|passed|error" | sed "s/^/$1 test_g14: /" )
  ( cd "$R" && TMPDIR=$TMPD $SLOT env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONPATH=$R/src python3 -m pytest \
      tests/unit/hooks/test_live_hook.py tests/unit/guard/test_reads.py \
      -p no:cacheprovider -q -n 6 -o tmp_path_retention_policy=failed -rf \
      2>&1 | grep -E "^FAILED|^ERROR|failed|passed|error" | sed "s/^/$1 live hook, reads: /" )
}
w2149() {  # $1 label: the launch script's suites; root ~/gov-os-eval (its guard-line cases plant their own HOME)
  need_home_root
  ( cd "$R" && TMPDIR=$TMPD $SLOT env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONPATH=$R/src PYTHONUSERBASE=$HOME/.local \
      python3 -m pytest tests/unit/orchestration/test_w2_149_indep_launch.py tests/acceptance/W2-149 \
      -p no:cacheprovider -q -n 6 -o tmp_path_retention_policy=failed -rf \
      2>&1 | grep -E "^FAILED|^ERROR|failed|passed|error" | sed "s/^/$1 W2-149 (the launch script): /" )
}
deliver() {  # $1 before|after
  need_home_root
  chmod -R u+w "/tmp/gov-os-sets-globs-e2e-$1" 2>/dev/null; rm -rf "/tmp/gov-os-sets-globs-e2e-$1"
  ( cd /tmp && GOV_PIN_PY=$PIN python3 "$D/deliver_check.py" "$R" "/tmp/gov-os-sets-globs-e2e-$1" "$R/.claude/hooks/pretooluse.py" "$1" \
      > "$BASE/deliver-$1.txt" 2>&1 )
  grep -E '^FAIL|^deliver|^delivered|^PASS|^FAIL$|Traceback|Error' "$BASE/deliver-$1.txt" | head -20
  echo "deliver $1: $(grep -c '^ok ' "$BASE/deliver-$1.txt") ok, $(grep -c '^FAIL ' "$BASE/deliver-$1.txt") failed"
  last_ok "$BASE/deliver-$1.txt" || bad "deliver $1"
}
replay() {
  need_planted
  ( cd "$R" && REPLAY_TICKET=DAEO-sdxk $SLOT python3 "$D/replay_globs.py" pass "$R" "$PR" "$R/.claude/hooks/pretooluse.py" \
      "$PIN" "$SINCE" "$UNTIL" "$BASE/replay-$1.json" ) > "$BASE/replay-$1.out" 2>&1 || bad "replay $1"
  python3 -c "import json,sys,collections;d=json.load(open(sys.argv[1]));print('replay $1:', d['counts'], dict(collections.Counter(v['d'] for v in d['answers'].values())))" "$BASE/replay-$1.json"
}
latency() {  # $1 label: the hook's time on listing and search calls (the walks the new globs widen), 20 rounds
  need_planted
  ( cd "$R" && GOV_PIN_PY=$PIN python3 - "$R" "$PR" "$PIN" "$BASE/latency-$1.json" <<'EOF'
import json, os, statistics, subprocess, sys, time
r, pr, py, out = sys.argv[1:]
calls = [("Bash", {"command": "ls fixtures/evaluation"}), ("Grep", {"pattern": "x", "path": r}),
         ("Bash", {"command": f"ls {pr}/runs"}), ("Grep", {"pattern": "x", "path": f"{pr}/fixtures/evaluation/memory-retrieval/visible"}),
         ("Bash", {"command": "git diff --name-only HEAD~1 | xargs grep -l x"}),
         ("Bash", {"command": "git grep -l x HEAD -- '*.yaml' '*.json'"}), ("Read", {"file_path": f"{r}/README.md"})]
ms = {}
for rnd in range(20):
    for tool, tin in calls:
        ev = {"tool_name": tool, "tool_input": tin, "cwd": r, "session_id": "sets-globs-latency", "agent_type": None}
        env = dict(os.environ, GOV_ROLE="orchestrator", GOV_TICKET="DAEO-sdxk", CLAUDE_PROJECT_DIR=r); env.pop("PYTHONPATH", None)
        t0 = time.monotonic()
        subprocess.run([py, "-E", r + "/.claude/hooks/pretooluse.py"], input=json.dumps(ev), capture_output=True, text=True, env=env)
        ms.setdefault(tool + " " + json.dumps(tin)[:60], []).append((time.monotonic() - t0) * 1000)
med = {k: round(statistics.median(v), 1) for k, v in ms.items()}
json.dump(med, open(out, "w"), indent=1)
for k, v in med.items():
    print(f"  {v:7.1f} ms  {k}")
print("median ms per call:", round(statistics.median([x for v in ms.values() for x in v]), 1))
EOF
  )
}
step_walls_before() { say "walls_before: walls_check.py repo <clone>, HOME planted"; walls before; }
step_walls_after() { say "walls_after"; walls after; }
step_guard4_before() { say "guard4_before (the registered line, root planted)"; guard4 before; }
step_guard4_after() { say "guard4_after"; guard4 after; }
step_suites_before() { say "suites_before"; suites before; }
step_suites_after() { say "suites_after"; suites after; }
step_w2149_before() { say "w2149_before: the launch script's unit and acceptance suites (root ~)"; w2149 before; }
step_w2149_after() { say "w2149_after"; w2149 after; }
step_narrow() {
  say "narrow: the candidate's Narrow walk against the judge's, every tree and the planted root (names only)"
  ( cd "$R" && "$PIN" -E "$D/narrow_check.py" "$D/pretooluse.candidate.py" "$R" "$PR" "$D/path-map.candidate.yaml" > "$BASE/narrow.txt" 2>&1 )
  cat "$BASE/narrow.txt"; last_ok "$BASE/narrow.txt" || bad "narrow"
}
step_scale() {
  say "scale: the hidden part's walk at the real root's scale, under the working load (median of 10)"
  mkdir -p /tmp/gov-os-sets-globs-scale
  ( cd /tmp && "$PIN" -E "$D/scale_check.py" "$D/pretooluse.candidate.py" "$D/path-map.candidate.yaml" /tmp/gov-os-sets-globs-scale > "$BASE/scale.txt" 2>&1 )
  cat "$BASE/scale.txt"; last_ok "$BASE/scale.txt" || bad "scale"
}
step_deliver_before() { say "deliver_before: the launch script delivers (W2-149 harness, planted); the hook before: each file open (the gap)"; deliver before; }
step_deliver_after() { say "deliver_after: the launch script delivers into the new globs; the hook after refuses each file, allows its line"; deliver after; }
step_replay_before() { say "replay_before: the real calls of $SINCE .. $UNTIL UTC, the hook and map before"; replay before; }
step_replay_after() {
  say "replay_after: the same calls, the hook and map after; before against after"
  replay after
  python3 "$D/replay_globs.py" compare "$BASE/replay-before.json" "$BASE/replay-after.json" > "$BASE/compare.txt"
  local rc=$?
  cat "$BASE/compare.txt"
  [ "$rc" = 0 ] || bad "the replay changed a call that does not name the new globs (or judged different calls)"
}
step_latency_before() { say "latency_before"; latency before; }
step_latency_after() { say "latency_after"; latency after; }
step_apply() {
  say "apply: apply.sh check, apply, a second apply, check (the size check on the planted root)"
  need_home_root
  bash "$D/apply.sh" check --sets-root "$PR" || { bad "apply.sh check"; return 1; }
  bash "$D/apply.sh" apply --sets-root "$PR" || { bad "apply.sh apply"; return 1; }
  bash "$D/apply.sh" apply --sets-root "$PR" >/dev/null 2>&1 && bad "a second apply ran" || echo "a second apply: refused"
  bash "$D/apply.sh" check --sets-root "$PR" | tail -1
  git -C "$R" status --short -- .claude governance
  "$PIN" -E - "$R" <<'EOF' || bad "the applied map does not load"
import importlib.util, sys
sys.path.insert(0, sys.argv[1] + "/src")
from pathlib import Path
from gov.config.loader import load_config
from gov.guard.reads import check_sets
spec = importlib.util.spec_from_file_location("hook", sys.argv[1] + "/.claude/hooks/pretooluse.py")
hook = importlib.util.module_from_spec(spec); spec.loader.exec_module(hook)
load_config(Path(sys.argv[1])); check_sets(sys.argv[1])
top, globs, roles = hook.sets_root_rule(sys.argv[1])
print("applied: load_config ok; check_sets ok; hidden globs", len(globs), "; refused roles", len(roles))
for p, n in hook.sets_line_keys(globs)[-3:]:
    print("  line key:", p[:90])
assert len(globs) == 11
EOF
}
step_commit() {
  say "commit: the operator's commit in the clone, as the message gives it"
  ( cd "$R" && bash "$D/apply.sh" check --sets-root "$PR" | tail -1 ) | grep -q "already applied" || { bad "commit: not applied"; return 1; }
  ( cd "$R" && git add .claude/hooks/pretooluse.py governance/project/path-map.yaml \
    && git diff --cached --name-status | tee "$BASE/staged.txt" )
  [ "$(tr '\t' ' ' < "$BASE/staged.txt" | tr '\n' ';')" = "M .claude/hooks/pretooluse.py;M governance/project/path-map.yaml;" ] \
    || bad "the staged list is not the two files"
  ( cd "$R" && git commit -q -m "ACT-SETS-GLOBS-1: the launch script's destinations hidden (fixtures/evaluation/*/hidden/**, fixtures/evaluation/*/XCHECK-r*.md, runs/*/miss-classes.json, runs/*/misses.jsonl); the guard's line rule keys such a glob by its own parts (W2-149 review F2)" \
      --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1101, DEC-1112" --trailer "Role: owner" ) || bad "the commit"
  git -C "$R" log -1 --format='%h %s%n%(trailers)' | cut -c1-160
}
step_undo() {
  say "undo: apply.sh undo after the commit (the working files back; then the clone's commit reverted)"
  need_home_root
  bash "$D/apply.sh" undo || bad "apply.sh undo"
  bash "$D/apply.sh" check --sets-root "$PR" | tail -1
  git -C "$R" diff --quiet HEAD~1 -- .claude/hooks/pretooluse.py governance/project/path-map.yaml \
    && echo "the hook and the map: as before the ACT's commit" || bad "undo: the files differ from before the ACT"
}

STEPS=${*:-prepare plant live_before narrow scale root_planted gap maponly walls_before guard4_before suites_before latency_before replay_before root_back deliver_before w2149_before apply deliver_after w2149_after root_planted after walls_after guard4_after suites_after latency_after replay_after root_back commit undo live_after}
echo "sets-globs rehearsal: $(date '+%Y-%m-%d %H:%M:%S %Z'), replay window $SINCE .. $UNTIL UTC, steps: $STEPS"
env | grep -cE '^(GOV_ROLE|GOV_TICKET|CLAUDE_PROJECT_DIR)=' | sed 's/^/inherited GOV_ROLE, GOV_TICKET and CLAUDE_PROJECT_DIR variables: /'
for s in $STEPS; do "step_$s"; done
echo
echo "rehearsal done: $(date '+%Y-%m-%d %H:%M:%S %Z'), failures: $FAILS"
