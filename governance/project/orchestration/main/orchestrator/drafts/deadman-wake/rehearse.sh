#!/usr/bin/env bash
# ACT-DEADMAN-WAKE-1's rehearsal (DEC-1057; the owner's rule of 2026-11-03): the bundle's apply.sh run end to end as
# the operator will, in a fresh clone of w2/integrate with HOME planted at an empty folder and ORCH pointed at the
# rehearsal's own folder. It never writes the live repository, the live scratch (log, state, inbox) or the real HOME;
# it checks so at the end. Writes the log to the bundle's rehearsal.log, ending "failures: <n>".
#   bash rehearse.sh
set -u
LIVE=/home/usain/Dynamic-Agentic-Engineering-OS
B=$LIVE/.gov-runtime/scratch/orchestrator/acts/ACT-DEADMAN-WAKE-1
D=$(cd "$(dirname "$0")" && pwd)
R=/home/usain/gov-os-runs/DEADMAN-WAKE-1-rehearsal
O=$LIVE/.gov-runtime/scratch/orchestrator
P=governance/project/orchestration/tools/deadman.py
LOG=$B/rehearsal.log
fails=0
say() { echo "$*" | tee -a "$LOG"; }
ok() { say "ok   $1"; }
no() { say "FAIL $1"; fails=$((fails + 1)); }
t() { if eval "$2"; then ok "$1"; else no "$1"; fi; }
: > "$LOG"
rm -rf "$R"; mkdir -p "$R/home" "$R/orch/log" "$R/tmp"
export TMPDIR=$R/tmp ORCH=$R/orch
# the live state before (hashes and counts only)
live_state() {
  sha256sum "$LIVE/$P" "$LIVE/governance/project/orchestration/tools/sentinel-brief.md" "$O/log/deadman-state.json" \
    "$O/log/cto-session.txt" 2> /dev/null | cut -c1-64 | paste -sd' '
  grep -c '"transcript": "s.jsonl"' "$O/log/deadman.log"
  ls "$O/dispatch/inbox" | grep -cE -- '-(deadman-wake|helper-watch|spend-brake)(-[0-9]+)?\.txt$'
  ls "$O/log" | grep -c '^deadman-wake-state'
  (cd "$LIVE" && git status --porcelain --untracked-files=no | sha256sum | cut -c1-12)
}
before=$(live_state)
head=$(git -C "$LIVE" rev-parse --short=12 HEAD)
git clone -q --no-hardlinks --single-branch -b w2/integrate "file://$LIVE" "$R/clone" || { no "clone"; exit 1; }
C=$R/clone
say "ACT-DEADMAN-WAKE-1 rehearsal $(date -u +%FT%TZ); clone of w2/integrate at $(git -C "$C" rev-parse --short=12 HEAD) (live HEAD $head); HOME planted at $R/home; ORCH $R/orch"
say "manifest sha256 before finalize: $(sha256sum "$B/manifest.json" | cut -c1-64)"
run() { (cd "$C" && HOME=$R/home "$@"); }
run bash "$B/apply.sh" check; t "apply.sh check: the clone's deadman.py is the before (exit 0)" '[ $? = 0 ]'
run bash "$B/apply.sh" verify 2> /dev/null; t "apply.sh verify before the apply: not applied (exit 3)" '[ $? = 3 ]'
run bash "$B/apply.sh" apply; t "apply.sh apply: exit 0" '[ $? = 0 ]'
run bash "$B/apply.sh" verify; t "apply.sh verify: the after (exit 0)" '[ $? = 0 ]'
t "the file's mode is 644" '[ "$(stat -c %a "$C/$P")" = 644 ]'
t "the changed set is exactly the touched file" '[ "$(cd "$C" && git status --porcelain)" = " M $P" ]'
# the manifest's checks, each as the operator runs it (cwd the repository, HOME planted)
n=0
while IFS='|' read -r b64 want cnt; do
  n=$((n + 1)); cmd=$(base64 -d <<< "$b64")
  out=$(cd "$C" && env -i PATH="$PATH" LANG=C.UTF-8 HOME="$R/home" TMPDIR="$TMPDIR" bash -c "$cmd" 2>&1); rc=$?
  last=$(printf '%s\n' "$out" | sed '/^[[:space:]]*$/d' | tail -n 1)
  say "check $n: exit $rc; last line: ${last:0:120}"
  t "check $n: exit $want$([ "$cnt" != null ] && echo ", count $cnt")" '[ "$rc" = "$want" ] && { [ "$cnt" = null ] || [ "$last" = "$cnt" ]; }'
done < <(python3 -I -c 'import base64, json, sys
for c in json.load(open(sys.argv[1]))["checks"]:
    print(base64.b64encode(c["cmd"].encode()).decode(), c["exit"], "null" if c["count"] is None else c["count"], sep="|")' "$B/manifest.json")
# the wake's own tests against the clone's applied file, and the safety nets with the post-ACT fixture: pytest is in the
# real HOME's user site, so these two run with the real HOME; every path the tool writes is the tests' own (--log,
# --state, ORCH), and the live-state comparison at the end proves it
out=$(cd "$D" && DEADMAN=$C/$P python3 -m pytest -q -p no:cacheprovider test_deadman_wake.py 2>&1 | tail -n 1)
say "test_deadman_wake.py on the applied file: $out"
t "the wake's tests: 7 passed" 'grep -q "^7 passed" <<< "$out"'
cp "$D/test_cto_safety_nets.py" "$C/tests/unit/orchestration/test_cto_safety_nets.py"
out=$(cd "$C" && python3 -m pytest -q -p no:cacheprovider tests/unit/orchestration/test_cto_safety_nets.py 2>&1 | tail -n 1)
say "test_cto_safety_nets.py with the post-ACT ORCH fixture: $out"
t "the safety nets with the fixture: 9 passed" 'grep -q "^9 passed" <<< "$out"'
(cd "$C" && git checkout -q -- tests/unit/orchestration/test_cto_safety_nets.py)
# a planted fault: a live file that moved since the review is refused by check
cp "$C/$P" "$R/tmp/applied.py"
run bash "$B/apply.sh" undo; t "apply.sh undo: exit 0" '[ $? = 0 ]'
t "undo: byte for byte the before" '[ "$(sha256sum "$C/$P" | cut -c1-64)" = "$(cut -d"|" -f3 "$B/list.txt")" ]'
t "undo: the clone's tree clean" '[ -z "$(cd "$C" && git status --porcelain)" ]'
run bash "$B/apply.sh" check; t "check after the undo: exit 0" '[ $? = 0 ]'
echo "# planted" >> "$C/$P"
run bash "$B/apply.sh" check 2> "$R/tmp/moved.txt"; rc=$?
t "a moved file: check refuses (exit 3, \"moved: $P\")" '[ $rc = 3 ] && grep -q "^moved: $P$" "$R/tmp/moved.txt"'
(cd "$C" && git checkout -q -- "$P")
cp "$B/after/repo/$P" "$R/tmp/after.bak"; printf '# tampered\n' >> "$B/after/repo/$P"
run bash "$B/apply.sh" apply 2> "$R/tmp/tamper.txt"; rc=$?
cp "$R/tmp/after.bak" "$B/after/repo/$P"
t "a tampered frozen copy: apply refuses (exit 4), the clone's file untouched" '[ $rc = 4 ] && [ -z "$(cd "$C" && git status --porcelain)" ]'
t "the bundle's after copy restored as listed" '[ "$(sha256sum "$B/after/repo/$P" | cut -c1-64)" = "$(cut -d"|" -f4 "$B/list.txt")" ]'
# nothing live written
after=$(live_state)
say "live before: $(echo $before)"
say "live after:  $(echo $after)"
t "the live files, the live inbox's wake items, the live wake key and the live tree as before; no planted line in the live log" '[ "$before" = "$after" ]'
t "nothing written to the planted HOME" '[ -z "$(ls -A "$R/home")" ]'
rm -rf "$R/clone" "$R/tmp"
say "failures: $fails"
