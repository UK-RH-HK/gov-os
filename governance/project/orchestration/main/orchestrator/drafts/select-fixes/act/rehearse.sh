#!/usr/bin/env bash
# DEC-1100 (1), ACT-SELECT-FIXES-1: the rehearsal, end to end, in a scratch clone. Changes nothing live.
#   bash rehearse.sh [step ...]      default: every step, in order; the log goes to rehearsal.log beside this file
# Steps: live_before prepare suites_before check apply select_cases replay rows record_checks suites_after undo rows_undone
#        live_after
# Layout: ~/gov-os-runs/SELECT-FIXES-rehearsal (made by this script, marked by its .select-fixes-rehearsal file):
#   Dynamic-Agentic-Engineering-OS   the --no-hardlinks clone at the main tree's HEAD; apply.sh applied there
#   replay                           replay_act.py's work folder (a --shared clone of the main repository, no checkout)
# Tests: scoped pytest only (the test selection's own tests: tests/acceptance/W2-66/, tests/unit/close/test_select.py and
# the opt-in lists' tests/unit/optin/test_optin_lifted.py),
# under heavy_slot.sh. No full run, no GPU, no install, no commit on any live branch.
set -u
MAIN=/home/usain/Dynamic-Agentic-Engineering-OS
SUB=.gov-runtime/scratch/orchestrator
HERE=$MAIN/$SUB/drafts/select-fixes/act
BASE=$HOME/gov-os-runs/SELECT-FIXES-rehearsal
R=$BASE/Dynamic-Agentic-Engineering-OS
RA=$R/$SUB/drafts/select-fixes/act
SLOT="bash $MAIN/$SUB/tools/heavy_slot.sh"
LOG=${REHEARSAL_LOG:-$HERE/rehearsal.log}
LIVE="governance/project/test-map.yaml tests/optin-lifted-breadth.txt $SUB/tools/record_checks.sh .git/hooks/reference-transaction .claude/settings.json"
SUITES="tests/acceptance/W2-66 tests/unit/close/test_select.py tests/unit/optin/test_optin_lifted.py"
exec > >(tee -a "$LOG") 2>&1
FAILS=0
W266=tests/acceptance/W2-66/test_w2_66_live_test_map.py::test_every_record_of_each_of_dec_891_s_places_is_record_only

say() { printf '\n== %s (%s)\n' "$1" "$(date '+%H:%M:%S')"; }
bad() { echo "REHEARSAL FAIL: $*"; FAILS=$((FAILS + 1)); }
hashes() { (cd "$MAIN" && sha256sum $LIVE); }
pyt() {  # $1 label; the scoped suites in the clone, the clone's own src first (DEC-732), in a heavy slot
  local out=$BASE/pytest-$1.txt
  (cd "$R" && env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS -u GOV_TICKET PYTHONPATH="$R/src" PYTHONDONTWRITEBYTECODE=1 \
     nice -n 10 $SLOT python3 -m pytest -q -p no:cacheprovider --no-header -n auto $SUITES > "$out" 2>&1)
  local rc=$?
  echo "pytest $1: exit $rc: $(tail -1 "$out")"
  grep -E '^(FAILED|ERROR) ' "$out" | head -20
  return $rc
}
sel() {  # the CTO's selection tool on the clone's HEAD against HEAD^ (as a commit outside a ticket)
  (cd "$R" && env -u GOV_TICKET PYTHONPATH="$R/src" python3 "$MAIN/$SUB/tools/select_tests.py" "$R" W2-00 DAEO-sdxk \
     --base HEAD^)
}
plant() {  # $1 path (relative), $2 text to append; commits it in the clone on the rehearsal branch
  printf '%s' "$2" >> "$R/$1"
  git -C "$R" add -- "$1" && git -C "$R" -c user.name=rehearsal -c user.email=r@r commit -q -m "planted: $1" -- "$1"
}
unplant() { git -C "$R" reset -q --hard HEAD^; }

step_live_before() {
  say "live_before: the live files' hashes"
  hashes | tee "$BASE.live-before.txt"
}
step_prepare() {
  say "prepare: the clone"
  if [ -e "$BASE" ]; then
    [ -f "$BASE/.select-fixes-rehearsal" ] || { bad "$BASE exists and is not this script's"; return 1; }
    rm -rf "$BASE"
  fi
  mkdir -p "$BASE" && : > "$BASE/.select-fixes-rehearsal"
  git clone -q --no-hardlinks "$MAIN" "$R" || { bad "clone"; return 1; }
  head=$(git -C "$MAIN" rev-parse HEAD)
  git -C "$R" checkout -q -b select-fixes-rehearsal "$head" || { bad "checkout"; return 1; }
  git -C "$R" branch -f w2/integrate "$head" >/dev/null 2>&1
  mkdir -p "$R/$SUB/tools" "$R/$SUB/drafts"
  for f in record_checks.sh placeholder_scan.py keyword_warn.py; do cp -p "$MAIN/$SUB/tools/$f" "$R/$SUB/tools/"; done
  cp -a "$MAIN/$SUB/drafts/select-fixes" "$R/$SUB/drafts/"
  rm -rf "$RA/backup" "$RA/rehearsal.log" "$RA/__pycache__"
  echo "clone $R at $(git -C "$R" rev-parse --short=12 HEAD) on $(git -C "$R" branch --show-current)"
}
step_suites_before() { say "suites_before: the selection's own tests, scoped"; pyt before || bad "suites before"; }
step_check() {
  say "check: apply.sh check in the clone"
  bash "$RA/apply.sh" check || bad "apply.sh check"
}
step_apply() {
  say "apply: apply.sh apply in the clone"
  bash "$RA/apply.sh" apply || bad "apply.sh apply"
  git -C "$R" diff --stat
  (cd "$R" && PYTHONPATH="$R/src" python3 -c "
from pathlib import Path
from gov.close import select
m, why = select.load_map(Path('.'))
assert m is not None, why
print('the patched map loads:', len(m['couplings']), 'couplings,', len(m['record_reading']), 'record_reading entries')
") || bad "the patched map does not load"
  git -C "$R" -c user.name=rehearsal -c user.email=r@r commit -q -m "ACT-SELECT-FIXES-1 (rehearsal)" \
    -- governance/project/test-map.yaml tests/optin-lifted-breadth.txt || bad "commit in the clone"
  echo "the clone's ACT commit: $(git -C "$R" rev-parse --short=12 HEAD)"
}
step_select_cases() {
  say "select_cases: today's tree, planted changes, the CTO's selection tool (selection only, nothing run)"
  local j
  plant .claude/settings.json $'\n'
  j=$(sel) || bad "S1 selection refused"
  echo "$j" | python3 -c '
import json, sys
s = json.load(sys.stdin); t = [x["target"] for x in s["selected"]]
want = ["tests/acceptance/W1-33/test_w1_33_guard_and_launcher.py", "tests/acceptance/W1-46/test_w1_46_research_installs.py",
        "tests/acceptance/W2-54/test_w2_54_sandboxed_worker.py"]
miss = [w for w in want if not any(x == w or x.startswith(w + "::") for x in t) and
        not any(w in (d.get("entry") or "") for d in s.get("lifted_reached") or [])]
lr = [d["entry"] for d in s.get("lifted_reached") or []]
print("S1 settings: selected", len(t), "targets; the three files", "all reached" if not miss else f"MISSING {miss}")
print("S1 lifted_reached:", len(lr), "entries; of the three files:", [e for e in lr if any(e.startswith(w) for w in want)])
sys.exit(1 if miss else 0)' || bad "S1"
  unplant
  plant template/governance/kernel/checks/secrets-indexing.yaml $'\n'
  j=$(sel) || bad "S2 selection refused"
  echo "$j" | python3 -c '
import json, sys
s = json.load(sys.stdin); t = [x["target"] for x in s["selected"]]
case = "tests/acceptance/W2-54/test_w2_54_time_limit.py::test_no_hard_block_check_is_weakened"
whole = "tests/acceptance/W2-54/test_w2_54_time_limit.py"
ok = case in t and whole not in t and not any(x.startswith(whole + "::") and x != case for x in t)
print("S2 kernel check: the no-weakening case selected alone of its file:", ok)
sys.exit(0 if ok else 1)' || bad "S2"
  unplant
  mkdir -p "$R/tests/acceptance/W2-00"
  plant tests/acceptance/W2-00/test_planted_rehearsal.py $'def test_planted():\n    pass\n'
  j=$(sel) || bad "S3 selection refused"
  echo "$j" | python3 -c '
import json, sys
s = json.load(sys.stdin); t = [x["target"] for x in s["selected"]]
a = "tests/acceptance/W1-01/test_w1_01_integration_merges.py::test_the_integration_merges_of_this_repository_pass"
b = "tests/acceptance/W1-50/test_w1_50_freeze_fixture_settings.py::test_the_two_whole_tree_fixtures_are_found"
print("S3 acceptance .py: W1-01 case", a in t, "; W1-50 case", b in t)
sys.exit(0 if a in t and b in t else 1)' || bad "S3"
  unplant
  plant governance/project/orchestration/planted-rehearsal.md $'planted\n'
  j=$(sel) || bad "S5 selection refused"
  echo "$j" | W266=$W266 python3 -c '
import json, os, sys
s = json.load(sys.stdin); t = [x["target"] for x in s["selected"]]
print("S5 records-only change: W2-66 record-only case selected:", os.environ["W266"] in t, "; targets", len(t))
sys.exit(0 if os.environ["W266"] in t else 1)' || bad "S5"
  unplant
  git -C "$R" status --short | head -5
  # What a selection's run collects of the targets (it runs `pytest tests` with --ignore/--deselect and names no node id,
  # so the opt-in lists of D-4's cut apply): the fixed red cases' rows, without and with --optin=breadth,lifted.
  local files="tests/acceptance/W2-66/test_w2_66_live_test_map.py tests/acceptance/W1-33/test_w1_33_guard_and_launcher.py
    tests/acceptance/W1-46/test_w1_46_research_installs.py tests/acceptance/W2-54/test_w2_54_sandboxed_worker.py
    tests/acceptance/W2-54/test_w2_54_time_limit.py tests/acceptance/W1-01/test_w1_01_integration_merges.py
    tests/acceptance/W1-50/test_w1_50_freeze_fixture_settings.py"
  for o in "" "--optin=breadth,lifted"; do
    (cd "$R" && env -u PYTEST_ADDOPTS PYTHONPATH="$R/src" PYTHONDONTWRITEBYTECODE=1 python3 -m pytest --collect-only -q \
       -p no:cacheprovider $o $files 2>/dev/null) > "$BASE/collect${o:+-optin}.txt"
    echo "rows collected ${o:-(no opt-in, as a selection runs)}: $(tail -1 "$BASE/collect${o:+-optin}.txt")"
    for f in "dec_891_s_places_is_record_only" "test_the_orchestrator_may_write_anywhere_else" \
             "test_the_auditor_writes_only_the_report_path" "test_an_install_asks_for_the_orchestrator" \
             "test_a_research_install_inside_the_experiment_folder_is_let_through" \
             "test_only_the_test_designer_may_write" "test_inside_a_launched_sandboxed_worker" \
             "test_no_hard_block_check_is_weakened" "test_the_integration_merges_of_this_repository_pass" \
             "test_the_two_whole_tree_fixtures_are_found"; do
      echo "  $f: $(grep -F "$f" "$BASE/collect${o:+-optin}.txt" | sed -n 's/.*\(\[[^]]*\]\)$/\1/p' | paste -sd' ' -)" \
        "($(grep -cF "$f" "$BASE/collect${o:+-optin}.txt") rows)"
    done
  done
}
step_replay() {
  say "replay: the 18 culprit trees, the ACT's own lines (replay_act.py)"
  rm -rf "$BASE/replay"
  nice -n 15 python3 "$RA/replay_act.py" --before "$RA/backup/test-map.yaml" --after "$R/governance/project/test-map.yaml" \
    --work "$BASE/replay" --out "$BASE/replay.json" | tee "$BASE/replay.txt"
  python3 - "$BASE/replay.json" <<'EOF' || bad "replay totals"
import json, statistics, sys
rows = json.load(open(sys.argv[1]))
tot = {k: sum(len(r[k]["caught"]) for r in rows) for k in ("base", "i", "ii", "i+ii")}
reds = sum(r["reds"] for r in rows)
refused = [r["id"] for r in rows if r["i+ii"]["scope"] != "scoped"]
cases = [r["added_cases"] for r in rows]; secs = [r["added_seconds"] for r in rows]
print(f"replay: {len(rows)} trees, {reds} red cases; caught base {tot['base']}, (i) {tot['i']}, (ii) {tot['ii']}, "
      f"(i)+(ii) {tot['i+ii']}; refused {refused or 'none'}; added median {statistics.median(cases)} cases, "
      f"{statistics.median(secs)} s; largest {max(cases)} cases, {max(secs)} s")
sys.exit(0 if (len(rows), reds, tot["base"], tot["i+ii"]) == (18, 34, 22, 34) and not refused else 1)
EOF
}
rc_run() {  # $1 label, $2 record_checks.sh to run (the clone's paths): its lines, and the record-reading failures
  local run=$BASE/record_checks.$1.sh rr=$R/$SUB/log/record-checks/record-reading.out
  sed "s#$MAIN#$R#g" "$2" > "$run"
  bash "$run" > "$BASE/record_checks.$1.txt" 2>&1; local rc=$?
  grep -E ' exit [0-9]' "$BASE/record_checks.$1.txt"; echo "record_checks ($1): exit $rc"
  grep -E '^FAILED' "$rr" | sed 's/^/  /' | tee "$BASE/record_checks.$1.failed"
  grep -E '^E +AssertionError: records of governance/project/orchestration/' "$rr" | cut -c1-400 | sed 's/^/  /'
}
step_record_checks() {
  say "record_checks: record_checks.sh on the clone, before and after the patch, after a record commit, with a planted record (S6)"
  grep -q "$W266" "$R/$SUB/tools/record_checks.sh" || bad "the patched record_checks.sh does not name the case"
  rc_run before "$RA/backup/record_checks.sh"
  rc_run after "$R/$SUB/tools/record_checks.sh"
  local added; added=$(comm -13 <(sort "$BASE/record_checks.before.failed") <(sort "$BASE/record_checks.after.failed"))
  [ -z "$added" ] && echo "S6 after the patch: the patch adds no failure (W2-66's case runs whole and is green)" \
    || bad "S6 after the patch adds: $added"
  plant governance/project/orchestration/planted-record.md $'a record commit (rehearsal)\n'
  rc_run record-commit "$R/$SUB/tools/record_checks.sh"
  if grep -q "dec_891_s_places_is_record_only" "$BASE/record_checks.record-commit.failed"; then bad "S6 record commit: W2-66's case red"
  else
    local other; other=$(grep -v "test_w1_06_approvals.py::test_every_approving_decision_is_accepted_by_the_owner" "$BASE/record_checks.record-commit.failed")
    [ -z "$other" ] && echo "S6 record commit: W2-66's case green; the record-reading line's only failure is W1-06's, red on w2/integrate before the ACT (the CTO's)" \
      || bad "S6 record commit: other failures: $other"
  fi
  (cd "$R" && env -u PYTEST_ADDOPTS PYTHONPATH="$R/src" PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider --no-header \
     tests/acceptance/W2-66/test_w2_66_live_test_map.py -k dec_891_s_places_is_record_only 2>&1 | tail -1) \
     | sed 's/^/the case by its file (as a selection names it, the rep line gone): /'
  unplant
  step_record_planted
}
step_record_planted() {
  plant governance/project/orchestration/planted-rehearsal.foo $'planted\n'
  rc_run planted "$R/$SUB/tools/record_checks.sh"
  if grep -q "planted-rehearsal.foo" "$R/$SUB/log/record-checks/record-reading.out" \
     && grep -q "dec_891_s_places_is_record_only\[governance/project/orchestration/\]" "$BASE/record_checks.planted.failed"; then
    echo "S6 planted .foo: record_checks exits non-zero and names the case and the planted record"
  else bad "S6 planted: the case or the record not named"; fi
  unplant
}
step_rows() {
  say "rows: of the 34 reds, those the patched selection names AND runs today, after the opt-in lists (rows_run.py)"
  python3 "$RA/rows_run.py" --tree "$R" --replay "$BASE/replay.json" --sel i+ii --out "$BASE/rows-after.json"
  python3 -c "
import json, sys
t = json.load(open('$BASE/rows-after.json'))
rows = {(r['case'], r['red']): r['kind'] for r in t['rows']}
w = [k for k in rows if k[0] in ('K3a', 'K4', 'K13')]
ok = all(rows[k] == 'gate' for k in w)
print('K3a, K4, K13 (W2-66\'s orchestration row):', 'gate in all three' if ok else [rows[k] for k in w])
sys.exit(0 if ok else 1)" || bad "W2-66's row does not run as a gate"
}
step_rows_undone() {
  say "rows_undone: the same count on today's map (after undo), the selection as the map names it today"
  python3 "$RA/rows_run.py" --tree "$R" --replay "$BASE/replay.json" --sel base --out "$BASE/rows-before.json"
}
step_suites_after() { say "suites_after: the selection's own tests, scoped, on the patched map"; pyt after || bad "suites after"; }
step_undo() {
  say "undo: apply.sh undo in the clone"
  git -C "$R" reset -q --soft HEAD^ && git -C "$R" restore --staged governance/project/test-map.yaml tests/optin-lifted-breadth.txt
  bash "$RA/apply.sh" undo || bad "apply.sh undo"
  [ -z "$(git -C "$R" status --porcelain -- governance/project/test-map.yaml tests/optin-lifted-breadth.txt)" ] \
    && echo "git: the map and the breadth list clean against HEAD" || bad "the map or the list differs from HEAD after undo"
  cmp -s "$R/$SUB/tools/record_checks.sh" "$MAIN/$SUB/tools/record_checks.sh" \
    && echo "record_checks.sh: byte for byte the live one" || bad "record_checks.sh differs after undo"
}
step_live_after() {
  say "live_after: the live files' hashes"
  hashes > "$BASE.live-after.txt"; cat "$BASE.live-after.txt"
  cmp -s "$BASE.live-before.txt" "$BASE.live-after.txt" && echo "live files: unchanged" || bad "a live file changed"
}

steps=("$@")
[ ${#steps[@]} -eq 0 ] && steps=(live_before prepare suites_before check apply select_cases replay rows record_checks suites_after undo rows_undone live_after)
echo "rehearse.sh: $(date '+%F %T'); steps: ${steps[*]}"
for s in "${steps[@]}"; do "step_$s"; done
echo; echo "rehearse.sh: done $(date '+%F %T'): $FAILS failure(s)"
exit $((FAILS > 0))
