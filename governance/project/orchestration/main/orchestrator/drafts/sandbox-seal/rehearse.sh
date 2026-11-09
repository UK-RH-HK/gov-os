#!/usr/bin/env bash
# ACT-SANDBOX-SEAL-1 (DEC-1099 (1) Q6): the seal's rehearsal, end to end, in a scratch clone. Changes nothing live.
#   bash rehearse.sh [step ...]      default: every step, in order; the log goes to rehearsal.log beside this file
# Steps: prepare plant live_before gap root_planted suites_before replay_before root_back apply r2 root_planted r1
#        suites_after replay_after compare measure root_back undo live_after
# It re-runs itself from a fresh shell (env -i with HOME, USER, LOGNAME, PATH and LANG only), as ACT-GUARD-SETS-1 did.
# Layout (under ~/gov-os-runs/SEAL-rehearsal, made by this script, marked by its .seal-rehearsal file):
#   Dynamic-Agentic-Engineering-OS   the --no-hardlinks clone, apply.sh applied there
#   home/gov-os-eval                 the planted sets root: dummy files only, written here
#   wt                               a worktree of the clone (the every-tree case)
# The real sets root is never opened, listed or named to the hook: only its own stat line is taken, before and after.
# While the clone's block reads root: "~/gov-os-eval", the hook runs only with HOME set to the planted home; every run
# with the real HOME (the suites, the replay, r1) happens with the block's root set to the planted absolute path.
set -u
if [ -z "${SEAL_FRESH:-}" ]; then
  exec env -i HOME="$HOME" USER="${USER:-usain}" LOGNAME="${LOGNAME:-usain}" PATH="$PATH" LANG="${LANG:-C.UTF-8}" \
    SEAL_FRESH=1 bash --noprofile --norc "$0" "$@"
fi
MAIN=/home/usain/Dynamic-Agentic-Engineering-OS
SUB=.gov-runtime/scratch/orchestrator
HERE=$MAIN/$SUB/drafts/sandbox-seal
BASE=$HOME/gov-os-runs/SEAL-rehearsal
R=$BASE/Dynamic-Agentic-Engineering-OS
PH=$BASE/home
PR=$PH/gov-os-eval
WT=$BASE/wt
TMPD=/tmp/gov-os-seal-rehearsal
REAL=$HOME/gov-os-eval
PIN=$(head -1 "$HOME/.local/bin/gov" | cut -c3-)
SLOT="bash $MAIN/$SUB/tools/heavy_slot.sh"
D=$R/$SUB/drafts/sandbox-seal
T=$R/$SUB/tools
LOG=$HERE/rehearsal.log
# The replay's fixed window: the 48 hours before the rehearsal's start (calls made during it are left out)
UNTIL=${SEAL_UNTIL:-$(date -u '+%Y-%m-%dT%H:%M:%S')}
SINCE=${SEAL_SINCE:-$(date -u -d "$UNTIL 48 hours ago" '+%Y-%m-%dT%H:%M:%S')}
exec > >(tee -a "$LOG") 2>&1
FAILS=0

say() { printf '\n== %s (%s)\n' "$1" "$(date '+%H:%M:%S')"; }
bad() { echo "REHEARSAL FAIL: $*"; FAILS=$((FAILS + 1)); }
need_planted() {
  local line; line=$(grep -A1 '^sets_root_hidden:' "$R/governance/project/path-map.yaml" | sed -n 2p)
  [ "$line" = "  root: \"$PR\"" ] && return 0
  echo "REHEARSAL STOP: the clone's block reads $line; a hook run now with the real HOME would name the real root"
  exit 3
}
eval_stat() { stat -c 'inode %i size %s mtime %Y ctime %Z' "$REAL" 2>&1; }  # the root's own entry; nothing under it
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

step_prepare() {
  say "prepare: the clone"
  if [ -e "$BASE" ]; then
    [ -f "$BASE/.seal-rehearsal" ] || { bad "$BASE exists and is not this script's"; return 1; }
    git -C "$R" worktree remove --force "$WT" 2>/dev/null
    rm -rf "$BASE"
  fi
  mkdir -p "$BASE" && : > "$BASE/.seal-rehearsal"
  git clone -q --no-hardlinks "$MAIN" "$R" || { bad "clone"; return 1; }
  head=$(git -C "$MAIN" rev-parse HEAD)
  git -C "$R" checkout -q -b seal-rehearsal "$head" || { bad "checkout"; return 1; }
  git -C "$MAIN" for-each-ref --format='%(refname) %(objectname)' refs/heads/ | while read -r ref sha; do
    [ "$ref" = refs/heads/seal-rehearsal ] && continue
    git -C "$R" update-ref "$ref" "$sha"
  done
  mkdir -p "$R/$SUB/tools" "$R/$SUB/drafts"
  cp -p "$MAIN/$SUB/tools/guard4_check.py" "$MAIN/$SUB/tools/heavy_slot.sh" "$T/"
  [ -f "$MAIN/$SUB/tools/heavy_slots.conf" ] && cp -p "$MAIN/$SUB/tools/heavy_slots.conf" "$T/"
  for d in drafts/sandbox-seal drafts/sets-root-guard drafts/act-guard-fix-4 drafts/g14 drafts/act-guard-fix-3; do
    [ -d "$MAIN/$SUB/$d" ] && cp -a "$MAIN/$SUB/$d" "$R/$SUB/drafts/"
  done
  rm -rf "$D/backup" "$D/rehearsal.log" "$R/$SUB/drafts/sets-root-guard/backup" "$R/$SUB/drafts/g14/backup" \
         "$R/$SUB/drafts/g14/backup-g14b" "$R/$SUB/drafts/act-guard-fix-4/backup"
  grep -rlI --null "$MAIN" "$R/$SUB" | xargs -0 -r sed -i "s#$MAIN#$R#g"
  git -C "$R" worktree add -q -b seal-wt "$WT" "$head" || bad "worktree"
  echo "clone $R at $(git -C "$R" rev-parse --short=12 HEAD) on $(git -C "$R" branch --show-current);" \
       "branches $(git -C "$R" for-each-ref refs/heads/ | wc -l); root mentions left: $(grep -rlI "$MAIN" "$R/$SUB" | wc -l);" \
       "worktree $WT on $(git -C "$WT" branch --show-current)"
  sha256sum "$R/.claude/hooks/pretooluse.py" "$R/governance/project/path-map.yaml" | sed "s#$R/##"
}

step_plant() {
  say "plant: the dummy sets root $PR (ACT-GUARD-SETS-1's layout, plus the sealed folder)"
  E=$PR/fixtures/evaluation
  mkdir -p "$E/memory-retrieval/hidden" "$E/memory-retrieval/visible" "$E/memory-verdict/hidden" \
           "$E/memory-verdict-2/hidden" "$E/memory-verdict-2/retired" "$PR/transcripts" "$PR/runs" \
           "$PR/governance/project" "$PR/runs/fresh-80/rows" "$PR/runs/fresh-80/kept-1" "$PR/runs/e0"
  for f in memory-retrieval/hidden/q01 memory-retrieval/visible/v01 memory-verdict/hidden/p01 \
           memory-verdict-2/hidden/p01 memory-verdict-2/hidden/p02 memory-verdict-2/retired/r01; do
    printf 'id: planted-%s\nquestion: "DUMMY planted for the rehearsal (%s)"\n' "${f//\//-}" "$f" > "$E/$f.yaml"
  done
  printf 'DUMMY checker report (planted)\n' > "$E/memory-verdict-2/XCHECK.md"
  printf 'DUMMY transcript (planted)\n' > "$PR/transcripts/t01.md"
  printf 'fixtures/evaluation/memory-verdict-2/hidden/p01.yaml\n' > "$PR/runs/list"
  printf 'DUMMY used marker (planted)\n' > "$PR/runs/fresh-80/USED"
  printf '{"id": "planted-row", "question": "DUMMY"}\n' > "$PR/runs/fresh-80/rows/q01.json"
  printf '{"kept": "DUMMY"}\n' > "$PR/runs/fresh-80/kept-1/k01.json"
  printf 'DUMMY counts (planted)\n' > "$PR/runs/e0/counts.txt"
  # the sealed folder: one dummy per kind of file the experiment keeps there, and an open sibling
  S=$E/sandbox-guard-exp-1
  mkdir -p "$S/hidden/corpus" "$S/hidden/planted" "$S/hidden/labels"
  printf '{"id": "planted-a1", "tool": "Bash", "input": {"command": "DUMMY planted"}}\n' > "$S/hidden/corpus/actions.jsonl"
  printf '{"id": "planted-c1", "class": 1, "note": "DUMMY planted"}\n' > "$S/hidden/planted/cases.jsonl"
  printf '{"id": "planted-a1", "label": "allow", "note": "DUMMY planted"}\n' > "$S/hidden/labels/labels.jsonl"
  printf 'DUMMY open sibling (planted)\n' > "$S/README.txt"
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

LIVE_FILES=".claude/hooks/pretooluse.py .claude/hooks/role_reads.py .claude/hooks/bash_writes.py
  governance/project/path-map.yaml governance/project/held-out.yaml .claude/settings.json"
live_hashes() {
  ( cd "$MAIN" && sha256sum $LIVE_FILES; ls .claude/settings*.json | xargs sha256sum | grep -v ' .claude/settings.json$' )
  echo "real sets root: $(eval_stat)"
}
step_live_before() { say "live_before: the live files and the real sets root's own entry"; live_hashes | tee "$BASE/live-before.txt"; }

step_gap() {
  say "gap: the seal's cases on the clone as it is (no patch), HOME=$PH: every case the seal adds is an allow"
  ( cd "$R" && HOME=$PH GOV_PIN_PY=$PIN SEAL_EXPECT=before SETS_PLANTED=1 SEAL_TREE=$WT \
      $SLOT python3 "$D/seal_check.py" "$R/.claude/hooks/pretooluse.py" > "$BASE/gap.txt" 2>&1 )
  grep -vE '^ok ' "$BASE/gap.txt"
  tail -1 "$BASE/gap.txt" | grep -qx PASS || bad "gap"
  echo "gap: cases that deny after the seal and allow before: $(cd "$R" && HOME=$PH GOV_PIN_PY=$PIN SETS_PLANTED=1 \
    SEAL_TREE=$WT python3 - "$D/seal_check.py" <<'EOF'
import runpy, sys, os
os.environ["SEAL_EXPECT"] = "after"; a = runpy.run_path(sys.argv[1], run_name="x")["CASES"]
os.environ["SEAL_EXPECT"] = "before"; b = runpy.run_path(sys.argv[1], run_name="x")["CASES"]
print(sum(1 for x, y in zip(a, b) if x[4] == "deny" and y[4] == "allow"))
EOF
)"
  ( cd "$R" && HOME=$PH GOV_PIN_PY=$PIN GUARD4_ONLY=sets SETS_PLANTED=1 SETS_OLDMAP_TREE=$WT \
      $SLOT python3 "$T/guard4_check.py" "$R/.claude/hooks/pretooluse.py" > "$BASE/gap-guard4.txt" 2>&1 )
  grep -vE '^ok ' "$BASE/gap-guard4.txt"
  tail -1 "$BASE/gap-guard4.txt" | grep -qx PASS || bad "guard4 sets cases before"
}

step_root_planted() { say "root_planted: the block's root set to the planted absolute path"; block_root "\"$PR\""; }
step_root_back() { say "root_back: the block's root back to ~/gov-os-eval"; block_root '"~/gov-os-eval"'; }

suites() {  # $1: a label
  need_planted
  mkdir -p "$TMPD"
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
}
step_suites_before() { say "suites_before: the suites on the clone as it is (the baseline)"; suites before; }
step_suites_after() { say "suites_after: the suites with the seal applied"; suites after; }

step_replay_before() {
  say "replay_before: the calls of $SINCE .. $UNTIL UTC, judged with the map before the seal"
  need_planted
  ( cd "$R" && $SLOT python3 "$D/replay_seal.py" pass "$R" "$PR" "$R/.claude/hooks/pretooluse.py" "$PIN" \
      "$SINCE" "$UNTIL" "$BASE/replay-before.json" ) || bad "replay before"
}
step_replay_after() {
  say "replay_after: the same calls, judged with the map after the seal"
  need_planted
  ( cd "$R" && $SLOT python3 "$D/replay_seal.py" pass "$R" "$PR" "$R/.claude/hooks/pretooluse.py" "$PIN" \
      "$SINCE" "$UNTIL" "$BASE/replay-after.json" ) || bad "replay after"
}
step_compare() {
  say "compare: before against after (the seal only adds refusals of the sealed folder)"
  python3 "$D/replay_seal.py" compare "$BASE/replay-before.json" "$BASE/replay-after.json" | tee "$BASE/compare.txt" \
    || bad "the two passes judged different calls"
  grep -q '"deny->allow"\|deny->allow' "$BASE/compare.txt" && bad "a call went from deny to allow"
  true
}

step_apply() {
  say "apply: apply.sh in the clone"
  bash "$D/apply.sh" check || { bad "apply.sh check"; return 1; }
  bash "$D/apply.sh" apply || { bad "apply.sh apply"; return 1; }
  git -C "$R" status --short
  git -C "$R" diff --stat
  "$PIN" -E - "$R" <<'EOF' || bad "the patched map does not load"
import json, sys
sys.path.insert(0, sys.argv[1] + "/src")
from pathlib import Path
import yaml, jsonschema
from gov.config.loader import load_config
from gov.guard.reads import check_sets, evaluation_sets, _hidden
sys.path.insert(0, sys.argv[1] + "/.claude/hooks")
import role_reads
import importlib.util
spec = importlib.util.spec_from_file_location("hook", sys.argv[1] + "/.claude/hooks/pretooluse.py")
hook = importlib.util.module_from_spec(spec); spec.loader.exec_module(hook)
load_config(Path(sys.argv[1]))
check_sets(sys.argv[1])
doc = yaml.safe_load(open(sys.argv[1] + "/governance/project/path-map.yaml"))
import glob, os
store = {}
for sp in glob.glob(sys.argv[1] + "/template/governance/kernel/schemas/*.json"):  # as W2-58's schema_validator
    sd = json.load(open(sp))
    store[os.path.basename(sp)] = sd
    if isinstance(sd, dict) and "$id" in sd:
        store[sd["$id"]] = sd
schema = store["path-map.schema.json"]
resolver = jsonschema.RefResolver(base_uri=schema.get("$id", ""), referrer=schema, store=store)
errs = [e.message for e in jsonschema.Draft202012Validator(schema, resolver=resolver).iter_errors(doc)]
sets = evaluation_sets(sys.argv[1])
top, globs, roles = hook.sets_root_rule(sys.argv[1])
g = "fixtures/evaluation/sandbox-guard-exp-1/hidden/**"
print("patched map: load_config ok; check_sets ok; schema errors:", len(errs), errs[:3])
print("evaluation_sets:", sorted(sets), "; role_paths:", sorted(role_reads.section(sys.argv[1]) or {}))
print("sets_root_rule: globs", len(globs), "; the seal's glob in it:", g in globs, "; refused roles", roles)
for r in ("engineer", "research", "product-spec", "independent-test-designer", "independent-auditor", "orchestrator",
          "ticket-lead", ""):
    print(f"  _hidden({r or 'no role'}) holds the seal's glob: {g in _hidden(sys.argv[1], r, 'DAEO-sdxk')}")
assert not errs and "sandbox-guard-exp-1" in sets and g in globs
EOF
}

step_r2() {
  say "r2: HOME=$PH (the block as applied, root ~/gov-os-eval): guard4's sets cases and the seal's cases"
  grep -n '^  root: ' "$R/governance/project/path-map.yaml"
  ( cd "$R" && HOME=$PH GOV_PIN_PY=$PIN GUARD4_ONLY=sets SETS_PLANTED=1 SETS_OLDMAP_TREE=$WT \
      $SLOT python3 "$T/guard4_check.py" "$R/.claude/hooks/pretooluse.py" > "$BASE/r2-guard4.txt" 2>&1 )
  grep -vE '^ok ' "$BASE/r2-guard4.txt"
  tail -1 "$BASE/r2-guard4.txt" | grep -qx PASS || bad "r2 guard4"
  ( cd "$R" && HOME=$PH GOV_PIN_PY=$PIN SETS_PLANTED=1 SEAL_TREE=$WT \
      $SLOT python3 "$D/seal_check.py" "$R/.claude/hooks/pretooluse.py" > "$BASE/r2-seal.txt" 2>&1 )
  grep -vE '^ok ' "$BASE/r2-seal.txt"
  tail -1 "$BASE/r2-seal.txt" | grep -qx PASS || bad "r2 seal"
}

step_r1() {
  say "r1: the registered hook line (--settings), the block's root $PR, SETS_PLANTED=1"
  need_planted
  ( cd "$R" && SETS_PLANTED=1 SETS_OLDMAP_TREE=$WT $SLOT python3 "$T/guard4_check.py" --settings "$R" \
      > "$BASE/r1-guard4.txt" 2>&1 )
  grep -vE '^ok ' "$BASE/r1-guard4.txt"
  tail -1 "$BASE/r1-guard4.txt" | grep -qx PASS || bad "r1 guard4"
  ( cd "$R" && SETS_PLANTED=1 SEAL_TREE=$WT $SLOT python3 "$D/seal_check.py" --settings "$R" > "$BASE/r1-seal.txt" 2>&1 )
  grep -vE '^ok ' "$BASE/r1-seal.txt"
  tail -1 "$BASE/r1-seal.txt" | grep -qx PASS || bad "r1 seal"
}

step_measure() {
  say "measure: _measured for the seal's set: the orchestrator not measured, the engineer measured"
  for role in orchestrator engineer research ticket-lead; do
    ( cd "$R" && GOV_ROLE=$role GOV_TICKET=DAEO-sdxk "$PIN" -E - "$R" <<'EOF' ) || bad "measure $role"
import os, sys
sys.path.insert(0, sys.argv[1] + "/src")
from pathlib import Path
from gov.retrieval.measure import _measured
from gov.guard.reads import evaluation_sets
entry = evaluation_sets(sys.argv[1])["sandbox-guard-exp-1"]
got = _measured(entry, Path(sys.argv[1]))
role = os.environ["GOV_ROLE"]
print(f"GOV_ROLE={role}: measured {got}")
assert got == (role in entry["measures"]["roles"])
EOF
  done
}

step_undo() {
  say "undo: apply.sh undo (the block's root back as applied first)"
  bash "$D/apply.sh" check | tail -1
  bash "$D/apply.sh" undo || bad "apply.sh undo"
  git -C "$R" diff --quiet -- .claude governance && echo "git diff: the hook and the map as committed" || bad "git diff after undo"
  git -C "$R" status --short -- .claude governance
}

step_live_after() {
  say "live_after: the live files and the real sets root's own entry, against before"
  live_hashes > "$BASE/live-after.txt"
  cat "$BASE/live-after.txt"
  cmp -s "$BASE/live-before.txt" "$BASE/live-after.txt" && echo "live: unchanged" || bad "a live file changed"
}

STEPS=${*:-prepare plant live_before gap root_planted suites_before replay_before root_back apply r2 root_planted r1 suites_after replay_after compare measure root_back undo live_after}
echo "seal rehearsal: $(date '+%Y-%m-%d %H:%M:%S %Z'), replay window $SINCE .. $UNTIL UTC, steps: $STEPS"
env | grep -cE '^(GOV_|CLAUDE_PROJECT_DIR)' | sed 's/^/inherited GOV_ and CLAUDE_PROJECT_DIR variables: /'
for s in $STEPS; do "step_$s"; done
echo
echo "rehearsal done: $(date '+%Y-%m-%d %H:%M:%S %Z'), failures: $FAILS"
