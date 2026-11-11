#!/bin/bash
# ACT-LOAD-BALANCER-A's rehearsal, as the operator will run it: a --no-hardlinks clone of w2/integrate (the main tree's
# head) under drafts/act-a/tmp/clone, a planted HOME (tmp/home), the untracked tools the tests read copied into the
# clone's scratch folder, the clean environment of the operator's dry run (PATH, LANG, TMPDIR, HOME planted,
# PYTHONDONTWRITEBYTECODE; nothing GOV_*), every manifest check run EXACTLY as written with `bash -c` from the clone,
# and the plain apply (no option). A stub lead only: no real claude session, no real lead, no dispatcher. The live files
# are only read (hashed). Waits by pid only (tools/proc.sh).
#   bash rehearse.sh      the log is ../rehearsal.log (it ends "failures: <n>")
set -u
D=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/act-a
MAIN=/home/usain/Dynamic-Agentic-Engineering-OS
ORCH=$MAIN/.gov-runtime/scratch/orchestrator
CL=$D/tmp/clone
PH=$D/tmp/home
ACT=$D/acts/ACT-LOAD-BALANCER-A
REL=governance/project/orchestration/tools/dispatch/launch_now.sh
LOG=$D/rehearsal.log
mkdir -p "$D/tmp"
: > "$LOG"
exec > >(tee -a "$LOG") 2>&1
FAILS=0
ok() { echo "ok   $1"; }
bad() { echo "FAIL $1"; FAILS=$((FAILS + 1)); }
sha() { sha256sum "$1" | cut -c1-64; }
OUT=$(mktemp "$D/tmp/.rehearsal-out.XXXXXX")
trap 'rm -f "$OUT"' EXIT
# the operator's clean environment (opcommon.clean_env): PATH, LANG, TMPDIR, HOME planted, no GOV_*
cenv() { env -i PATH=/usr/local/bin:/usr/bin:/bin LANG=C.UTF-8 TMPDIR="$D/tmp" HOME="$PH" PYTHONDONTWRITEBYTECODE=1 "$@"; }
# the same with the user's own HOME, for pytest (the dry run's planted HOME hides the user-site pytest, so no manifest
# check needs it; the rehearsal runs the existing suites and this ACT's tests this way)
penv() { env -i PATH=/usr/local/bin:/usr/bin:/bin LANG=C.UTF-8 TMPDIR="$D/tmp" HOME="$USER_HOME" PYTHONDONTWRITEBYTECODE=1 "$@"; }
USER_HOME=$HOME
expect_exit() { # expect_exit <label> <want> <cmd...>   (run in the clone, clean env)
  local label="$1" want="$2"; shift 2
  (cd "$CL" && cenv "$@") > "$OUT" 2>&1; local rc=$?
  tail -n 12 "$OUT" | cut -c1-220 | sed 's/^/     /'
  [ "$rc" = "$want" ] && ok "$label (exit $rc)" || bad "$label: want exit $want, got $rc"
}
run_check() { # run_check <n> <want exit>: manifest-form check n from tools/checks.json, as written, bash -c
  local cmd
  cmd=$(python3 -I -c "import json,sys; print(json.load(open('$D/tools/checks.json'))[int(sys.argv[1])]['cmd'])" "$1")
  expect_exit "check $1 as written: ${cmd:0:90}..." "$2" bash -c "$cmd"
}
pytests() { # pytests <want exit>: the two existing suites that run the launcher (unit and acceptance dispatch)
  (cd "$CL" && penv env PYTHONPATH=src python3 -m pytest -q -p no:cacheprovider tests/unit/launch/test_w2_153_template.py \
     tests/acceptance/W2-153/test_w2_153_dispatch.py) > "$OUT" 2>&1; local rc=$?
  grep -E "^(FAILED|[0-9]+ (failed|passed))" "$OUT" | cut -c1-170 | sed 's/^/     /'
  [ "$rc" = "$1" ] && ok "existing launcher tests (tests/unit/launch/test_w2_153_template.py, tests/acceptance/W2-153/test_w2_153_dispatch.py): exit $rc" \
    || bad "existing launcher tests: want exit $1, got $rc"
}

echo "--- A. the bundle and the clone"
rm -rf "$CL" "$PH"
mkdir -p "$PH"
git clone -q --no-hardlinks "$MAIN" "$CL" || { echo "FAIL clone"; echo "failures: 1"; exit 1; }
echo "clone HEAD $(git -C "$CL" rev-parse --short=12 HEAD) on $(git -C "$CL" rev-parse --abbrev-ref HEAD); main tree head $(git -C "$MAIN" rev-parse --short=12 HEAD)"
BEFORE=$(cut -d'|' -f3 "$ACT/list.txt"); AFTER=$(cut -d'|' -f4 "$ACT/list.txt")
[ "$(sha "$CL/$REL")" = "$BEFORE" ] && ok "A0 the clone's launcher is the frozen before (the bundle is not stale)" || bad "A0 stale bundle"
[ "$(sha "$MAIN/$REL")" = "$BEFORE" ] && ok "A0b the main tree's launcher (read only) is the frozen before" || bad "A0b main tree differs"
[ "$(sha "$ACT/before/repo/$REL")" = "$BEFORE" ] && [ "$(sha "$ACT/after/repo/$REL")" = "$AFTER" ] && ok "A0c before/ and after/ hash as list.txt says" || bad "A0c frozen copies"
MODE0=$(stat -c %a "$CL/$REL")
mkdir -p "$CL/.gov-runtime/scratch/orchestrator/tools"
cp -p "$ORCH/tools/lead_mem.py" "$ORCH/tools/disk_gate.sh" "$ORCH/tools/proc.sh" "$CL/.gov-runtime/scratch/orchestrator/tools/"
ok "A0d the untracked tools the tests read (lead_mem.py, disk_gate.sh, proc.sh) copied into the clone's scratch folder"
expect_exit "A1 check: state before" 0 bash "$ACT/apply.sh" check
expect_exit "A2 verify refused before the apply" 3 bash "$ACT/apply.sh" verify
expect_exit "A3 undo before the apply says nothing to undo" 0 bash "$ACT/apply.sh" undo

echo "--- B. the existing launcher tests on the BEFORE launcher (the baseline)"
pytests 0

echo "--- C. the sequencing: the plain apply WITHOUT the companion test change turns the existing tests red (the check refuses it)"
expect_exit "C1 plain apply (no option)" 0 bash "$ACT/apply.sh" apply
run_check 0 0
run_check 1 0
run_check 2 0
echo "     (the manifest's check 3, the companion guard, is red here: the ACT refuses itself until the companion has landed)"
run_check 3 1
echo "     and the existing suites are red, as the guard says (the three named tests):"
pytests 1
expect_exit "C2 undo" 0 bash "$ACT/apply.sh" undo
cmp -s "$CL/$REL" "$ACT/before/repo/$REL" && ok "C3 undone byte for byte" || bad "C3 undo differs"

echo "--- D. the companion test change (a stand-in gov in the two beds), then the plain apply"
(cd "$CL" && git apply "$D/companion-tests.diff") && ok "D0 companion-tests.diff applies to the clone" || bad "D0 companion diff"
git -C "$CL" status --porcelain > "$D/tmp/status.before-apply"
sed 's/^/     /' "$D/tmp/status.before-apply"
echo "the old launcher with the companion:"
run_check 3 0
pytests 0
expect_exit "D1 plain apply (no option, no env)" 0 bash "$ACT/apply.sh" apply
cmp -s "$CL/$REL" "$ACT/after/repo/$REL" && ok "D2 the launcher is the frozen after, byte for byte" || bad "D2 not the frozen after"
[ "$(stat -c %a "$CL/$REL")" = "$MODE0" ] && ok "D3 the mode is kept ($MODE0)" || bad "D3 mode changed"
git -C "$CL" status --porcelain > "$D/tmp/status.after-apply"
if diff "$D/tmp/status.before-apply" "$D/tmp/status.after-apply" > "$OUT"; then bad "D4 the apply changed nothing"; else
  [ "$(grep -c '^[<>]' "$OUT")" = 1 ] && grep -q "launch_now.sh" "$OUT" && ok "D4 the apply changed the one listed file and wrote nothing else (git status, no stray temp file)" || bad "D4 stray change: $(cat "$OUT")"
fi
ls "$CL"/governance/project/orchestration/tools/dispatch | grep -c 'act-' | grep -qx 0 && ok "D5 no temp file left beside the launcher" || bad "D5 a temp file is left"
expect_exit "D6 check: state applied" 0 bash "$ACT/apply.sh" check
expect_exit "D7 verify exit 0" 0 bash "$ACT/apply.sh" verify
expect_exit "D8 apply again changes nothing" 0 bash "$ACT/apply.sh" apply

echo "--- E. every manifest check, exactly as written, with bash -c, on the applied clone"
for n in 0 1 2 3; do run_check "$n" 0; done
pytests 0

echo "--- F. this ACT's own tests (test_launch_now_gate.py): green on the new launcher, red on the old"
cp -p "$D/test_launch_now_gate.py" "$D/tmp/test_launch_now_gate.py"
runtests() { # runtests <launcher>
  (cd "$D/tmp" && penv LAUNCH_NOW="$1" LEAD_MEM_PY="$CL/.gov-runtime/scratch/orchestrator/tools/lead_mem.py" \
     python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed test_launch_now_gate.py) > "$OUT" 2>&1
  return $?
}
runtests "$CL/$REL"; rc=$?
tail -n 3 "$OUT" | sed 's/^/     /'
[ "$rc" = 0 ] && grep -q "12 passed" "$OUT" && ok "F1 new launcher: 12 passed" || bad "F1 new launcher (exit $rc)"
runtests "$ACT/before/repo/$REL"; rc=$?
grep -E "^(FAILED|[0-9]+ (failed|passed))" "$OUT" | cut -c1-160 | sed 's/^/     /'
[ "$rc" != 0 ] && grep -q "10 failed, 2 passed" "$OUT" && ok "F2 old launcher: 10 failed, 2 passed (red on the old, as the tests say)" || bad "F2 old launcher (exit $rc)"

echo "--- G. the dispatcher's own start form, end to end, with a stub lead and the real gov under the planted home"
rm -rf "$D/tmp/e2e"; (cd "$D/tmp" && penv python3 "$D/tools/e2e_dispatcher_form.py" "$CL/$REL" "$D/tmp" "$CL/.gov-runtime/scratch/orchestrator/tools/proc.sh" \
   "$CL/.gov-runtime/scratch/orchestrator/tools/lead_mem.py") > "$OUT" 2>&1; rc=$?
sed 's/^/     /' "$OUT" | cut -c1-230
[ "$rc" = 0 ] && ok "G1 end to end (exit 0)" || bad "G1 end to end (exit $rc)"
echo "--- G2. the same end to end on the OLD launcher (it must fail: no registration, no gate)"
rm -rf "$D/tmp/e2e"; (cd "$D/tmp" && penv python3 "$D/tools/e2e_dispatcher_form.py" "$ACT/before/repo/$REL" "$D/tmp" "$CL/.gov-runtime/scratch/orchestrator/tools/proc.sh" \
   "$CL/.gov-runtime/scratch/orchestrator/tools/lead_mem.py") > "$OUT" 2>&1; rc=$?
grep -E "^(ok|FAIL)|failures" "$OUT" | cut -c1-160 | sed 's/^/     /' | head -14
[ "$rc" != 0 ] && ok "G2 the old launcher fails the end-to-end checks (exit $rc)" || bad "G2 the old launcher passed"

echo "--- H. the wider scoped set on the applied clone, and the apply.sh states"
(cd "$CL" && penv env PYTHONPATH=src python3 -m pytest -q -p no:cacheprovider tests/unit/launch tests/acceptance/W2-153) > "$OUT" 2>&1; rc=$?
tail -n 2 "$OUT" | sed 's/^/     /'
[ "$rc" = 0 ] && ok "H1 tests/unit/launch and tests/acceptance/W2-153 (scoped) green with the new launcher" || bad "H1 (exit $rc)"
printf '# a later change\n' >> "$CL/$REL"
expect_exit "H2 check refuses a launcher that changed" 3 bash "$ACT/apply.sh" check
expect_exit "H3 undo refuses (not as this ACT left it)" 3 bash "$ACT/apply.sh" undo
expect_exit "H4 apply refuses (neither before nor after)" 3 bash "$ACT/apply.sh" apply
cp -p "$ACT/after/repo/$REL" "$CL/$REL"; chmod "$MODE0" "$CL/$REL"
expect_exit "H5 undo from the applied state" 0 bash "$ACT/apply.sh" undo
cmp -s "$CL/$REL" "$ACT/before/repo/$REL" && [ "$(stat -c %a "$CL/$REL")" = "$MODE0" ] && ok "H6 the launcher is the original, byte for byte, mode kept" || bad "H6 undo differs"
expect_exit "H7 check: state before" 0 bash "$ACT/apply.sh" check
run_check 1 1
run_check 2 1
echo "     (checks 1 and 2, structure and behaviour, are red on the old launcher: they tell the two apart)"
mv "$CL/$REL" "$CL/$REL.away"
expect_exit "H8 a missing launcher: check refuses" 3 bash "$ACT/apply.sh" check
expect_exit "H9 a missing launcher: apply refuses" 3 bash "$ACT/apply.sh" apply
[ ! -e "$CL/$REL" ] && ok "H10 nothing was created in its place" || bad "H10 a file was created"
mv "$CL/$REL.away" "$CL/$REL"
mv "$CL/$REL" "$CL/$REL.real"; ln -s "$CL/$REL.real" "$CL/$REL"
expect_exit "H11 a link: apply refuses" 3 bash "$ACT/apply.sh" apply
rm -f "$CL/$REL"; mv "$CL/$REL.real" "$CL/$REL"
cmp -s "$CL/$REL" "$ACT/before/repo/$REL" && ok "H12 the clone is back to the original" || bad "H12 not restored"

echo "--- I. the live files are unchanged (read only)"
[ "$(sha "$MAIN/$REL")" = "$BEFORE" ] && ok "I1 the main tree's launcher is unchanged ($(echo "$BEFORE" | cut -c1-12))" || bad "I1 the main tree's launcher changed"
[ "$(git -C "$MAIN" rev-parse --short=12 HEAD)" = "$(git -C "$CL" rev-parse --short=12 HEAD)" ] && ok "I2 the main tree's head is still the clone's" || echo "note: the main tree's head moved since the clone (the bundle's before hash still matches: I1)"

echo
[ "$FAILS" = 0 ] && echo "REHEARSAL PASS" || echo "REHEARSAL FAIL"
echo "failures: $FAILS"
