#!/usr/bin/env bash
# DEC-1103 (2), ACT-D4-RESTORE-1: the rehearsal, end to end, in a scratch clone. Changes nothing live.
#   bash rehearse.sh [step ...]      default: every step, in order; the log goes to rehearsal.log beside this file
# Steps: live_before prepare optin_before count_before rows_before check apply collect_ten run_ten rows_after
#        optin_after count_after undo variant_b live_after
# Layout: ~/gov-os-runs/D4-RESTORE-rehearsal (made by this script, marked by its .d4-restore-rehearsal file):
#   Dynamic-Agentic-Engineering-OS   the --no-hardlinks clone at the main tree's HEAD; apply.sh applied there
# The replay is ACT-SELECT-FIXES-1's (its replay.json: what the selection names on each of the 18 culprit trees with
# today's map, the `i+ii` column) and its rows_run.py, read in place; only the opt-in lists differ.
# Tests: scoped pytest only (the ten cases by node id; tests/unit/optin/test_optin_lifted.py), under heavy_slot.sh;
# collect-only for the full run's count. No full run, no GPU, no install, no commit on any live branch.
set -u
MAIN=/home/usain/Dynamic-Agentic-Engineering-OS
SUB=.gov-runtime/scratch/orchestrator
HERE=$MAIN/$SUB/drafts/d4-restore
BASE=$HOME/gov-os-runs/D4-RESTORE-rehearsal
R=$BASE/Dynamic-Agentic-Engineering-OS
RA=$R/$SUB/drafts/d4-restore
SLOT="bash $MAIN/$SUB/tools/heavy_slot.sh"
ROWS=$MAIN/$SUB/drafts/select-fixes/act/rows_run.py
REPLAY=$HOME/gov-os-runs/SELECT-FIXES-rehearsal/replay.json
LOG=${REHEARSAL_LOG:-$HERE/rehearsal.log}
LISTS="tests/optin-lifted-breadth.txt tests/optin-lifted-guard.txt tests/optin-lifted.txt"
LIVE="$LISTS tests/optin-lifted-guard-breadth.txt tests/conftest.py governance/project/test-map.yaml .git/hooks/reference-transaction .claude/settings.json"
TEN=$HERE/ten.txt
exec > >(tee -a "$LOG") 2>&1
FAILS=0

say() { printf '\n== %s (%s)\n' "$1" "$(date '+%H:%M:%S')"; }
bad() { echo "REHEARSAL FAIL: $*"; FAILS=$((FAILS + 1)); }
hashes() { (cd "$MAIN" && sha256sum $LIVE); }
py() {  # the clone's python environment: its own src first (DEC-732), no inherited pytest options
  (cd "$R" && env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS -u GOV_TICKET -u GOV_TESTS_OPTIN PYTHONPATH="$R/src" \
     PYTHONDONTWRITEBYTECODE=1 "$@")
}
count() {  # $1 label, $2.. extra pytest args: the full run's collection (`pytest tests`, no node id), its count
  local out=$BASE/collect-full-$1.txt
  py nice -n 10 python3 -m pytest --collect-only -q -p no:cacheprovider "${@:2}" tests > "$out" 2>&1
  grep -c '::' "$out"
}

step_live_before() {
  say "live_before: the live files' hashes"
  hashes | tee "$BASE.live-before.txt"
  grep -q '^42e22dd70a05' "$BASE.live-before.txt" && echo "the live map is ACT-SELECT-FIXES-1's (the replay's i+ii column)" \
    || bad "the live test map is not ACT-SELECT-FIXES-1's: the replay's i+ii column does not stand for it"
}
step_prepare() {
  say "prepare: the clone"
  if [ -e "$BASE" ]; then
    [ -f "$BASE/.d4-restore-rehearsal" ] || { bad "$BASE exists and is not this script's"; return 1; }
    rm -rf "$BASE"
  fi
  mkdir -p "$BASE" && : > "$BASE/.d4-restore-rehearsal"
  git clone -q --no-hardlinks "$MAIN" "$R" || { bad "clone"; return 1; }
  head=$(git -C "$MAIN" rev-parse HEAD)
  git -C "$R" checkout -q -b d4-restore-rehearsal "$head" || { bad "checkout"; return 1; }
  git -C "$R" branch -f w2/integrate "$head" >/dev/null 2>&1
  mkdir -p "$R/$SUB/drafts"
  cp -a "$HERE" "$R/$SUB/drafts/"
  rm -rf "$RA/backup" "$RA/rehearsal.log" "$RA/__pycache__"
  echo "clone $R at $(git -C "$R" rev-parse --short=12 HEAD) on $(git -C "$R" branch --show-current)"
}
step_optin_before() {
  say "optin_before: the opt-in lists' own tests, scoped"
  py $SLOT python3 -m pytest -q -p no:cacheprovider --no-header tests/unit/optin/test_optin_lifted.py > "$BASE/optin-before.txt" 2>&1 \
    || bad "test_optin_lifted.py before"
  tail -1 "$BASE/optin-before.txt"
}
step_count_before() {
  say "count_before: the full run's collection (no opt-in) and with both suites, before"
  n=$(count before); echo "full run (no opt-in): $n cases"; echo "$n" > "$BASE/count-before"
  m=$(count before-all --optin=lifted,breadth); echo "both suites opted in: $m cases"; echo "$m" > "$BASE/count-before-all"
}
step_rows_before() {
  say "rows_before: of the trial's 34 reds, those today's selection names AND runs, today's lists (rows_run.py)"
  python3 "$ROWS" --tree "$R" --replay "$REPLAY" --sel i+ii --out "$BASE/rows-before.json"
}
step_check() { say "check: apply.sh check in the clone"; bash "$RA/apply.sh" check || bad "apply.sh check"; }
step_apply() {
  say "apply: apply.sh apply in the clone"
  bash "$RA/apply.sh" apply || bad "apply.sh apply"
  git -C "$R" diff --stat
  git -C "$R" -c user.name=rehearsal -c user.email=r@r commit -q -m "ACT-D4-RESTORE-1 (rehearsal)" -- $LISTS \
    || bad "commit in the clone"
  echo "the clone's ACT commit: $(git -C "$R" rev-parse --short=12 HEAD)"
}
step_collect_ten() {
  say "collect_ten: each restored case collected by its file alone, as the full run and a selection collect (no opt-in, no node id)"
  local files; files=$(cut -d: -f1 "$TEN" | sort -u)
  py python3 -m pytest --collect-only -q -p no:cacheprovider $files > "$BASE/collect-ten.txt" 2>&1
  python3 - "$BASE/collect-ten.txt" "$HERE/ten-k.txt" <<'EOF' || bad "a restored case is not collected without opt-in"
import sys
ids = [l.strip() for l in open(sys.argv[1]) if "::" in l]
miss = 0
for line in open(sys.argv[2]):
    k, case = line.split()
    n = sum(1 for i in ids if i == case or i.startswith(case + "["))
    miss += n == 0
    print(f"  {k} {case}: {'collected' if n else 'NOT collected'} ({n} row(s))")
sys.exit(1 if miss else 0)
EOF
}
step_run_ten() {
  say "run_ten: the ten cases at today's head, by node id, scoped, in a heavy slot"
  py nice -n 10 $SLOT python3 -m pytest -p no:cacheprovider --no-header -rA -q -n 6 $(cat "$TEN") \
    > "$BASE/run-ten.txt" 2>&1
  echo "pytest: exit $?: $(tail -1 "$BASE/run-ten.txt")"
  grep -E '^(PASSED|FAILED|ERROR|SKIPPED)' "$BASE/run-ten.txt" | sed 's/ - .*//' | sort | uniq -c | sort -k2 | sed 's/^/  /'
  python3 - "$BASE/run-ten.txt" "$TEN" <<'EOF'
import re, sys
text = open(sys.argv[1]).read().splitlines()
for case in open(sys.argv[2]).read().split():
    rows = [l for l in text if re.match(r"^(PASSED|FAILED|ERROR|SKIPPED) " + re.escape(case) + r"(\[|\s|$)", l)]
    kinds = sorted({l.split()[0] for l in rows})
    verdict = "green" if kinds == ["PASSED"] else ("RED" if {"FAILED", "ERROR"} & set(kinds) else "/".join(kinds) or "NOT RUN")
    print(f"  {verdict:6} {case} ({len(rows)} row(s))")
EOF
}
step_rows_after() {
  say "rows_after: the same count with the restored lists (rows_run.py)"
  python3 "$ROWS" --tree "$R" --replay "$REPLAY" --sel i+ii --out "$BASE/rows-after.json"
  python3 - "$BASE/rows-after.json" <<'EOF' || bad "rows after: not 33 gates with K18a the one not run"
import json, sys
t = json.load(open(sys.argv[1]))
left = [(r["case"], r["red"], r["kind"], r["why"]) for r in t["rows"] if r["kind"] != "gate"]
ok = t["tally"] == {"gate": 33, "report-only": 0, "not run": 1} and left[0][0] == "K18a" and left[0][3] == "not in today's tree"
print("rows after:", t["tally"], "; not a gate:", left, "->", "as expected (33 of 34; K18a gone from the tree)" if ok else "NOT as expected")
sys.exit(0 if ok else 1)
EOF
}
step_optin_after() {
  say "optin_after: the opt-in lists' own tests, scoped, on the restored lists"
  py $SLOT python3 -m pytest -q -p no:cacheprovider --no-header tests/unit/optin/test_optin_lifted.py > "$BASE/optin-after.txt" 2>&1 \
    || bad "test_optin_lifted.py after"
  tail -1 "$BASE/optin-after.txt"
}
step_count_after() {
  say "count_after: the full run's collection after; it rises by the rows restored, and nothing else moves"
  n=$(count after); b=$(cat "$BASE/count-before"); echo "full run (no opt-in): $b -> $n cases (+$((n - b)))"
  m=$(count after-all --optin=lifted,breadth); echo "both suites opted in: $(cat "$BASE/count-before-all") -> $m (unchanged expected)"
  [ "$m" = "$(cat "$BASE/count-before-all")" ] || bad "the collection with both suites moved"
  comm -13 <(grep '::' "$BASE/collect-full-before.txt" | sort) <(grep '::' "$BASE/collect-full-after.txt" | sort) > "$BASE/added.txt"
  comm -23 <(grep '::' "$BASE/collect-full-before.txt" | sort) <(grep '::' "$BASE/collect-full-after.txt" | sort) > "$BASE/removed.txt"
  echo "added to the full run: $(wc -l < "$BASE/added.txt") case(s); removed: $(wc -l < "$BASE/removed.txt")"
  [ -s "$BASE/removed.txt" ] && bad "the full run lost cases"
  python3 - "$BASE/added.txt" "$TEN" <<'EOF' || bad "the full run gained a case outside the ten"
import sys
added = [l.strip() for l in open(sys.argv[1]) if l.strip()]
ten = [l.strip() for l in open(sys.argv[2]) if l.strip()]
outside = [a for a in added if not any(a == t or a.startswith(t + "[") for t in ten)]
per = {t: sum(1 for a in added if a == t or a.startswith(t + "[")) for t in ten}
for t, n in per.items():
    print(f"  +{n} {t}")
print("every added case is one of the ten's rows:", not outside, outside[:5])
sys.exit(1 if outside or 0 in per.values() else 0)
EOF
}
step_undo() {
  say "undo: apply.sh undo in the clone"
  git -C "$R" reset -q --soft HEAD^ && git -C "$R" restore --staged $LISTS
  bash "$RA/apply.sh" undo || bad "apply.sh undo"
  [ -z "$(git -C "$R" status --porcelain -- $LISTS)" ] && echo "git: the three lists clean against HEAD (byte for byte)" \
    || bad "a list differs from HEAD after undo"
  for f in $LISTS; do cmp -s "$R/$f" "$MAIN/$f" || bad "$f differs from the live one after undo"; done
}
step_variant_b() {
  say "variant_b: the CTO's option B (not decided): the seven green today; the three K2 cases red by design stay lifted"
  mv "$RA/backup" "$RA/backup-A" && echo "A's backup moved aside to backup-A (apply refuses over an earlier backup)"
  bash "$RA/apply.sh" check B || bad "B check"
  bash "$RA/apply.sh" apply B || bad "B apply"
  git -C "$R" -c user.name=rehearsal -c user.email=r@r commit -q -m "ACT-D4-RESTORE-1 B (rehearsal)" -- $LISTS || bad "B commit"
  python3 "$ROWS" --tree "$R" --replay "$REPLAY" --sel i+ii --out "$BASE/rows-b.json"
  python3 -c "
import json, sys
t = json.load(open('$BASE/rows-b.json'))['tally']
ok = t == {'gate': 30, 'report-only': 3, 'not run': 1}
print('B rows:', t, '->', 'as expected (30 gates; the 3 red-by-design report-only; K18a gone)' if ok else 'NOT as expected')
sys.exit(0 if ok else 1)" || bad "B rows"
  n=$(count after-b); echo "B full run (no opt-in): $(cat "$BASE/count-before") -> $n"
  py $SLOT python3 -m pytest -q -p no:cacheprovider --no-header tests/unit/optin/test_optin_lifted.py > "$BASE/optin-b.txt" 2>&1 || bad "B optin tests"
  echo "B test_optin_lifted.py: $(tail -1 "$BASE/optin-b.txt")"
  git -C "$R" reset -q --soft HEAD^ && git -C "$R" restore --staged $LISTS
  bash "$RA/apply.sh" undo B || bad "B undo"
  [ -z "$(git -C "$R" status --porcelain -- $LISTS)" ] && echo "B undo: the three lists clean against HEAD" || bad "B undo not clean"
}
step_live_after() {
  say "live_after: the live files' hashes"
  hashes > "$BASE.live-after.txt"; cat "$BASE.live-after.txt"
  cmp -s "$BASE.live-before.txt" "$BASE.live-after.txt" && echo "live files: unchanged" || bad "a live file changed"
}

steps=("$@")
[ ${#steps[@]} -eq 0 ] && steps=(live_before prepare optin_before count_before rows_before check apply collect_ten run_ten rows_after optin_after count_after undo variant_b live_after)
echo "rehearse.sh: $(date '+%F %T'); steps: ${steps[*]}"
for s in "${steps[@]}"; do "step_$s"; done
echo; echo "rehearse.sh: done $(date '+%F %T'): $FAILS failure(s)"
exit $((FAILS > 0))
