#!/bin/bash
# ACT-DISPATCH-1's rehearsal, as the operator will run it: a --no-hardlinks clone of w2/integrate (the main tree's head)
# under /home/usain/gov-os-runs/W2-00/dispatch-1/rclone, a planted HOME, the clean environment of the operator's dry run
# (PATH, LANG, TMPDIR, HOME planted, PYTHONDONTWRITEBYTECODE; nothing GOV_*), every manifest check run EXACTLY as written
# with `bash -c` from the clone, the plain apply (no option). The unit tests run scoped, through the heavy-slot gate,
# with the user's own HOME (the planted one hides the user-site pytest). The dry-tick scenarios run in a planted world
# (tools/dry_tick.py), never against the live dispatch folder. The live files are only read (hashed).
# The log has no head, pid, date or duration, so a second rehearsal against the same bytes is the same log.
#   bash rehearse.sh      the log is ../rehearsal.log (it ends "failures: <n>")
set -u
MAIN=/home/usain/Dynamic-Agentic-Engineering-OS
D=$MAIN/.gov-runtime/scratch/orchestrator/drafts/dispatch-1
ORCH=$MAIN/.gov-runtime/scratch/orchestrator
RUN=/home/usain/gov-os-runs/W2-00/dispatch-1
CL=$RUN/rclone
PH=$D/tmp/home
ACT=$D/acts/ACT-DISPATCH-1
LOG=$D/rehearsal.log
HEAVY=$ORCH/tools/heavy_slot.sh
RELS=(governance/project/orchestration/tools/dispatch/dispatcher.py governance/project/orchestration/tools/dispatch/balancer.py tests/unit/orchestration/test_dispatcher.py tests/unit/orchestration/test_balancer.py)
TESTS=(tests/unit/orchestration/test_dispatcher.py tests/unit/orchestration/test_balancer.py)
mkdir -p "$D/tmp"
: > "$LOG"
exec > >(tee -a "$LOG") 2>&1
FAILS=0
ok() { echo "ok   $1"; }
bad() { echo "FAIL $1"; FAILS=$((FAILS + 1)); }
sha() { sha256sum "$1" | cut -c1-64; }
OUT=$(mktemp "$D/tmp/.rehearsal-out.XXXXXX")
trap 'rm -f "$OUT"' EXIT
USER_HOME=$HOME
cenv() { env -i PATH=/usr/local/bin:/usr/bin:/bin LANG=C.UTF-8 TMPDIR="$D/tmp" HOME="$PH" PYTHONDONTWRITEBYTECODE=1 "$@"; }
penv() { env -i PATH=/usr/local/bin:/usr/bin:/bin LANG=C.UTF-8 TMPDIR="$D/tmp" HOME="$USER_HOME" PYTHONDONTWRITEBYTECODE=1 "$@"; }
expect_exit() { # expect_exit <label> <want> <cmd...>   (run in the clone, clean env)
  local label="$1" want="$2"; shift 2
  (cd "$CL" && cenv "$@") > "$OUT" 2>&1; local rc=$?
  tail -n 6 "$OUT" | cut -c1-200 | sed 's/^/     /'
  [ "$rc" = "$want" ] && ok "$label (exit $rc)" || bad "$label: want exit $want, got $rc"
}
check_cmd() { python3 -I -c "import json,sys; print(json.load(open('$D/tools/checks-dispatch.json'))['checks'][int(sys.argv[1])]['cmd'])" "$1"; }
run_check() { # run_check <n> <want exit> <count or ->: the manifest's check n, as written, bash -c, from the clone
  local cmd; cmd=$(check_cmd "$1")
  (cd "$CL" && cenv bash -c "$cmd") > "$OUT" 2>&1; local rc=$?
  tail -n 3 "$OUT" | cut -c1-200 | sed 's/^/     /'
  if [ "$rc" = "$2" ] && { [ "$3" = - ] || [ "$(tail -n 1 "$OUT")" = "$3" ]; }; then ok "check $1 as written (exit $rc${3:+, count $3})"; else bad "check $1: want exit $2 count $3, got exit $rc"; fi
}
heavy() { # heavy <label> <want exit> <pytest args...>: scoped through the heavy-slot gate; prints the counts, never a time
  local label="$1" want="$2"; shift 2
  (cd "$CL" && penv bash "$HEAVY" env TMPDIR="$D/tmp/rt" PYTHONPATH="$CL/src" python3 -m pytest "$@" -q -p no:cacheprovider \
     -o tmp_path_retention_policy=failed) > "$OUT" 2>&1; local rc=$?
  grep -E "^FAILED" "$OUT" | sed 's/ - .*//' | sort | cut -c1-170 | sed 's/^/     /'
  tail -n 1 "$OUT" | sed -E 's/ in [0-9.]+s( \([0-9:]+\))?//; s/=+//g; s/^ +//' | sed 's/^/     result: /'
  [ "$rc" = "$want" ] && ok "$label: exit $rc" || bad "$label: want exit $want, got $rc"
  LAST_RESULT=$(tail -n 1 "$OUT" | sed -E 's/ in [0-9.]+s( \([0-9:]+\))?//; s/=+//g; s/^ +//')
}
chmod -R u+w "${D:?}/tmp/rt" 2>/dev/null; rm -rf "${D:?}/tmp/rt" 2>/dev/null; mkdir -p "$D/tmp/rt"

echo "--- A. the bundle and the clone"
rm -rf "${CL:?}" "${PH:?}"; mkdir -p "$PH"
git clone -q --no-hardlinks "$MAIN" "$CL" || { echo "FAIL clone"; echo "failures: 1"; exit 1; }
echo "clone of the main tree's w2/integrate: $(git -C "$CL" rev-parse --abbrev-ref HEAD)"
i=0; while IFS='|' read -r root path before after; do
  [ "$(sha "$CL/$path")" = "$before" ] && ok "A0.$i the clone's ${path##*/} is the frozen before (the bundle is not stale)" || bad "A0.$i stale: $path"
  [ "$(sha "$MAIN/$path")" = "$before" ] && ok "A0.$i the main tree's ${path##*/} (read only) is the frozen before" || bad "A0.$i main tree differs: $path"
  [ "$(sha "$ACT/before/repo/$path")" = "$before" ] && [ "$(sha "$ACT/after/repo/$path")" = "$after" ] && ok "A0.$i before/ and after/ copies hash as list.txt says" || bad "A0.$i frozen copies: $path"
  i=$((i + 1))
done < "$ACT/list.txt"
MODES=(); for r in "${RELS[@]}"; do MODES+=("$(stat -c %a "$CL/$r")"); done
expect_exit "A1 check: state before" 0 bash "$ACT/apply.sh" check
expect_exit "A2 verify refused before the apply" 3 bash "$ACT/apply.sh" verify
expect_exit "A3 undo before the apply changes nothing" 0 bash "$ACT/apply.sh" undo

echo "--- B. the existing tests of tests/unit/orchestration on the OLD code (the baseline)"
heavy "B1 tests/unit/orchestration, old code, old tests" 0 tests/unit/orchestration
BASE_RESULT=$LAST_RESULT

echo "--- C. the new test cases on the OLD code: red"
for r in "${TESTS[@]}"; do cp "$ACT/after/repo/$r" "$CL/$r"; done
heavy "C1 the new test files on the old code" 1 "${TESTS[@]}"
RED_RESULT=$LAST_RESULT
[ "$(grep -c '^FAILED' "$OUT")" -ge 10 ] && ok "C2 at least 10 of the new cases fail on the old code ($(grep -c '^FAILED' "$OUT"))" || bad "C2 too few red cases"
for n in 1 2 3; do run_check "$n" 1 -; done
echo "     (checks 1, 2 and 3, the behaviour of the cap, the idle item and the forecast, are red on the old files: they tell the two apart)"
run_check 0 0 -
run_check 4 0 -
(cd "$CL" && git checkout -q -- "${TESTS[@]}")
git -C "$CL" status --porcelain | grep -c . | grep -qx 0 && ok "C3 the clone is clean again (old code, old tests)" || bad "C3 the clone is not clean"

echo "--- D. the plain apply"
git -C "$CL" status --porcelain > "$D/tmp/status.before-apply"
expect_exit "D1 plain apply (no option, no env)" 0 bash "$ACT/apply.sh" apply
i=0; for r in "${RELS[@]}"; do
  cmp -s "$CL/$r" "$ACT/after/repo/$r" && ok "D2.$i ${r##*/} is the frozen after, byte for byte" || bad "D2.$i ${r##*/} is not the frozen after"
  [ "$(stat -c %a "$CL/$r")" = "${MODES[$i]}" ] && ok "D3.$i the mode of ${r##*/} is kept (${MODES[$i]})" || bad "D3.$i mode changed: $r"
  i=$((i + 1))
done
git -C "$CL" status --porcelain | sort > "$OUT"
[ "$(wc -l < "$OUT")" = 4 ] && [ "$(grep -c '^ M ' "$OUT")" = 4 ] && ok "D4 git status shows exactly four modified files and nothing else" || bad "D4 stray change: $(cat "$OUT")"
find "$CL/governance/project/orchestration/tools/dispatch" "$CL/tests/unit/orchestration" -name '*.act-*' | grep -c . | grep -qx 0 && ok "D5 no temp file left beside the files" || bad "D5 a temp file is left"
expect_exit "D6 check refused after the apply" 3 bash "$ACT/apply.sh" check
expect_exit "D7 verify exit 0" 0 bash "$ACT/apply.sh" verify
expect_exit "D8 apply again changes nothing" 0 bash "$ACT/apply.sh" apply

echo "--- E. every manifest check exactly as written, then the tests: green"
run_check 0 0 -
run_check 1 0 4
run_check 2 0 5
run_check 3 0 4
run_check 4 0 -
heavy "E1 tests/unit/orchestration, new code, new tests" 0 tests/unit/orchestration
GREEN_RESULT=$LAST_RESULT
echo "     baseline: $BASE_RESULT | new cases on the old code: $RED_RESULT | after the apply: $GREEN_RESULT"

echo "--- E4. the OLD test files on the NEW code (the code-only route: the tests could land after the code)"
for r in "${TESTS[@]}"; do cp "$ACT/before/repo/$r" "$CL/$r"; done
heavy "E4 tests/unit/orchestration, new code, old test files" 0 tests/unit/orchestration
OLDTESTS_RESULT=$LAST_RESULT
heavy "E5 tests/acceptance/W2-136 (it reads the dispatcher's list rules), new code" 0 tests/acceptance/W2-136
for r in "${TESTS[@]}"; do cp -p "$ACT/after/repo/$r" "$CL/$r"; done
expect_exit "E6 verify: the new test files are back, the ACT is applied again" 0 bash "$ACT/apply.sh" verify
echo "     old test files on the new code: $OLDTESTS_RESULT"

echo "--- F. the dry-tick scenarios in a planted world (the live config.json copied; never the live dispatch folder)"
runworld() { (cd "$D/tmp" && penv env DT_CLONE="$CL" PYTHONPATH= python3 "$D/tools/dry_tick.py" "$1" "$D/tmp/dt-$2" "$ORCH/dispatch/config.json") > "$OUT" 2>&1; return $?; }
echo "the new dispatcher:"
runworld "$CL/governance/project/orchestration/tools/dispatch/dispatcher.py" new; rc=$?
cp "$OUT" "$D/tmp/dry-new.txt"; sed 's/^/     /' "$OUT" | cut -c1-260
[ "$rc" = 0 ] && ok "F0 the planted world ran (new)" || bad "F0 planted world (new) exit $rc"
grep -q "^  W2-6 T-6: lead cap: 5 of 5 running" "$D/tmp/dry-new.txt" && grep -q "started this tick: None" "$D/tmp/dry-new.txt" && ok "F1 CAP: the sixth line waits on the cap and nothing starts" || bad "F1 cap"
grep -q "pass 4, gate open, same waiting set: inbox idle items 1;" "$D/tmp/dry-new.txt" && grep -q "pass 2, one minute later: inbox idle items 1;" "$D/tmp/dry-new.txt" && ok "F2 IDLE: the same waiting set (also across a shut-gate pass) gives one item, not two" || bad "F2 idle"
grep -q "pass 5, 7 hours later: inbox idle items 2;" "$D/tmp/dry-new.txt" && grep -q "reminder: the same cause for 7 h" "$D/tmp/dry-new.txt" && ok "F3 IDLE: after 6 hours the same cause is one reminder" || bad "F3 reminder"
grep -q "forecast lead ok: True | CPU 8.0 of 18 cores (busy 3.0 + running jobs' peaks 3.0, 3 of them at their measured load" "$D/tmp/dry-new.txt" && grep -q "the line: startable (would start)" "$D/tmp/dry-new.txt" && ok "F4 FORECAST: three held slots at a low measured load admit a lead" || bad "F4 forecast"
echo "the old dispatcher, the same three scenarios:"
runworld "$ACT/before/repo/governance/project/orchestration/tools/dispatch/dispatcher.py" old; rc=$?
cp "$OUT" "$D/tmp/dry-old.txt"; sed 's/^/     /' "$OUT" | cut -c1-260
[ "$rc" = 0 ] && ok "F5 the planted world ran (old)" || bad "F5 planted world (old) exit $rc"
grep -q "started this tick: W2-6" "$D/tmp/dry-old.txt" && ok "F6 old: the sixth lead would start (no cap)" || bad "F6 old cap"
grep -q "pass 4, gate open, same waiting set: inbox idle items 2;" "$D/tmp/dry-old.txt" && ok "F7 old: the same waiting set gives a second item after a shut-gate pass" || bad "F7 old idle"
grep -q "forecast lead ok: False | CPU 22.7 of 18 cores" "$D/tmp/dry-old.txt" && ok "F8 old: the same machine is refused on CPU (22.7 of 18)" || bad "F8 old forecast"

echo "--- G. undo, and the apply.sh states"
expect_exit "G1 undo" 0 bash "$ACT/apply.sh" undo
i=0; for r in "${RELS[@]}"; do
  cmp -s "$CL/$r" "$ACT/before/repo/$r" && [ "$(stat -c %a "$CL/$r")" = "${MODES[$i]}" ] && ok "G2.$i ${r##*/} is the original, byte for byte, mode kept" || bad "G2.$i undo differs: $r"
  i=$((i + 1))
done
git -C "$CL" status --porcelain | grep -c . | grep -qx 0 && ok "G3 the clone is clean after the undo" || bad "G3 the clone is not clean"
expect_exit "G4 check: state before" 0 bash "$ACT/apply.sh" check
R0=${RELS[0]}; R2=${RELS[2]}
printf '# a later change\n' >> "$CL/$R0"
expect_exit "G5 check refuses a file that changed" 3 bash "$ACT/apply.sh" check
expect_exit "G6 apply refuses (neither before nor after)" 3 bash "$ACT/apply.sh" apply
cmp -s "$CL/$R2" "$ACT/before/repo/$R2" && ok "G7 apply wrote nothing to the other files" || bad "G7 another file was written"
cp -p "$ACT/before/repo/$R0" "$CL/$R0"
expect_exit "G8 apply" 0 bash "$ACT/apply.sh" apply
cp -p "$ACT/before/repo/$R2" "$CL/$R2"
expect_exit "G9 a half-applied state: verify refuses" 3 bash "$ACT/apply.sh" verify
expect_exit "G10 a half-applied state: apply finishes it" 0 bash "$ACT/apply.sh" apply
expect_exit "G11 verify" 0 bash "$ACT/apply.sh" verify
cp -p "$ACT/before/repo/${RELS[1]}" "$CL/${RELS[1]}"
expect_exit "G12 a half-applied state: undo takes it back" 0 bash "$ACT/apply.sh" undo
i=0; for r in "${RELS[@]}"; do cmp -s "$CL/$r" "$ACT/before/repo/$r" || bad "G13 not restored: $r"; i=$((i + 1)); done
git -C "$CL" status --porcelain | grep -c . | grep -qx 0 && ok "G13 the clone is back to the original" || bad "G13 not restored"
TB=$D/tmp/tampered; rm -rf "${TB:?}"; cp -r "$ACT" "$TB"; echo "# tampered" >> "$TB/after/repo/${RELS[1]}"
expect_exit "G14 a tampered frozen copy: apply refuses (4)" 4 bash "$TB/apply.sh" apply
cmp -s "$CL/${RELS[0]}" "$ACT/before/repo/${RELS[0]}" && ok "G15 nothing was written" || bad "G15 a file was written"
rm -rf "${TB:?}"
mv "$CL/$R2" "$CL/$R2.away"
expect_exit "G16 a missing file: apply refuses" 3 bash "$ACT/apply.sh" apply
[ ! -e "$CL/$R2" ] && ok "G17 nothing was created in its place" || bad "G17 a file was created"
mv "$CL/$R2.away" "$CL/$R2"
mv "$CL/$R2" "$CL/$R2.real"; ln -s "$CL/$R2.real" "$CL/$R2"
expect_exit "G18 a link: apply refuses" 3 bash "$ACT/apply.sh" apply
rm -f "${CL:?}/$R2"; mv "$CL/$R2.real" "$CL/$R2"
git -C "$CL" status --porcelain | grep -c . | grep -qx 0 && ok "G19 the clone is clean again" || bad "G19 not clean"

echo "--- H. the live files are unchanged (read only)"
i=0; while IFS='|' read -r root path before after; do
  [ "$(sha "$MAIN/$path")" = "$before" ] && ok "H1.$i the main tree's ${path##*/} is unchanged" || bad "H1.$i the main tree's file changed: $path"
  i=$((i + 1))
done < "$ACT/list.txt"
[ -z "$(ls -A "$PH")" ] && ok "H2 the planted HOME is empty" || bad "H2 the planted HOME holds files"
[ "$(git -C "$MAIN" status --porcelain -- governance tests | wc -l)" = 0 ] && ok "H3 the main tree's governance/ and tests/ are clean" || bad "H3 the main tree is not clean there"

echo "--- I. the class vote of the operator's own classifier (act_class.py, read only)"
V=$(cd "$D/tmp" && penv python3 -I "$D/tools/class_vote.py" "$ACT" 4 "$D/tmp/vote")
[ "$V" = O ] && ok "I1 the four-file bundle (code and tests) votes O: by hand" || bad "I1 the four-file vote is $V"
V=$(cd "$D/tmp" && penv python3 -I "$D/tools/class_vote.py" "$ACT" 2 "$D/tmp/vote")
[ "$V" = b ] && ok "I2 the two code files alone vote b (row watchers, control path)" || bad "I2 the code-only vote is $V"

echo
[ "$FAILS" = 0 ] && echo "REHEARSAL PASS" || echo "REHEARSAL FAIL"
echo "failures: $FAILS"
