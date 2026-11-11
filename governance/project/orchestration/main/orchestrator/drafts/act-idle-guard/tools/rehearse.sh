#!/bin/bash
# ACT-IDLE-GUARD-1's rehearsal, as the operator will run it: a --no-hardlinks clone of w2/integrate (the main tree's
# head) under drafts/act-idle-guard/tmp/clone, a planted HOME (tmp/home), the clean environment of the operator's dry run
# (PATH, LANG, TMPDIR, HOME planted, PYTHONDONTWRITEBYTECODE; nothing GOV_*), every manifest check run EXACTLY as written
# with `bash -c` from the clone, and the plain apply (no option). Only the root is substituted (the clone for the live
# tree). Nothing live is written: the live files are only hashed. The log (../rehearsal.log) holds no head, pid, date,
# duration or count line, so a rebuild on the same bytes gives the same sha256.
#   bash rehearse.sh      the log ends "failures: <n>"
set -u
D=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/act-idle-guard
MAIN=/home/usain/Dynamic-Agentic-Engineering-OS
ORCH=$MAIN/.gov-runtime/scratch/orchestrator
CL=$D/tmp/clone
PH=$D/tmp/home
ACT=$D/acts/ACT-IDLE-GUARD-1
HOOK=governance/project/orchestration/tools/stop_idle_check.py
DISP=governance/project/orchestration/tools/dispatch/dispatcher.py
TESTS="tests/unit/orchestration/test_stop_idle_check.py tests/unit/orchestration/test_dispatcher.py"
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
USER_HOME=$HOME
cenv() { env -i PATH=/usr/local/bin:/usr/bin:/bin LANG=C.UTF-8 TMPDIR="$D/tmp" HOME="$PH" PYTHONDONTWRITEBYTECODE=1 "$@"; }
penv() { env -i PATH=/usr/local/bin:/usr/bin:/bin LANG=C.UTF-8 TMPDIR="$D/tmp" HOME="$USER_HOME" PYTHONDONTWRITEBYTECODE=1 "$@"; }
expect_exit() { # expect_exit <label> <want> <cmd...>   (run in the clone, clean env)
  local label="$1" want="$2"; shift 2
  (cd "$CL" && cenv "$@") > "$OUT" 2>&1; local rc=$?
  tail -n 6 "$OUT" | cut -c1-200 | sed 's/^/     /'
  [ "$rc" = "$want" ] && ok "$label (exit $rc)" || bad "$label: want exit $want, got $rc"
}
run_check() { # run_check <n> <want exit>: manifest-form check n from tools/checks.json, as written, bash -c, last line = count
  local cmd want_count got
  cmd=$(python3 -I -c "import json,sys; print(json.load(open('$D/tools/checks.json'))[int(sys.argv[1])]['cmd'])" "$1")
  want_count=$(python3 -I -c "import json,sys; print(json.load(open('$D/tools/checks.json'))[int(sys.argv[1])]['count'])" "$1")
  (cd "$CL" && cenv bash -c "$cmd") > "$OUT" 2>&1; local rc=$?
  got=$(grep -v '^$' "$OUT" | tail -n 1)
  if [ "$2" = 0 ]; then
    if [ "$rc" = 0 ] && { [ "$want_count" = None ] || [ "$got" = "$want_count" ]; }; then ok "check $1 as written (exit 0, count $want_count)"; else bad "check $1: exit $rc, last line '$got', want count $want_count"; tail -n 5 "$OUT" | cut -c1-200; fi
  else
    [ "$rc" != 0 ] && ok "check $1 is red on this state (exit $rc), as it must be" || bad "check $1 passed where it must be red"
  fi
}
pytests() { # pytests <want ok|red> <label> <files...>: the scoped files, the dispatcher's through the heavy gate
  local want="$1" label="$2"; shift 2
  (cd "$CL" && penv bash "$ORCH/tools/heavy_slot.sh" python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed "$@") > "$OUT" 2>&1; local rc=$?
  if [ "$want" = ok ]; then
    [ "$rc" = 0 ] && ok "$label: all passed" || { bad "$label: exit $rc"; grep -E "^FAILED" "$OUT" | head -n 8 | cut -c1-200; }
  else
    [ "$rc" != 0 ] && ok "$label: red as expected" || bad "$label: passed where red was expected"
    grep -E "^FAILED" "$OUT" | sed 's/ - .*//' | sort | sed 's/^/     /'
  fi
}

echo "--- A. the bundle and the clone"
rm -rf "$CL" "$PH"
mkdir -p "$PH"
git clone -q --no-hardlinks "$MAIN" "$CL" || { echo "FAIL clone"; echo "failures: 1"; exit 1; }
[ "$(git -C "$CL" rev-parse --abbrev-ref HEAD)" = "w2/integrate" ] && ok "A0 the clone is w2/integrate" || bad "A0 branch"
while IFS='|' read -r root path before after; do
  [ "$(sha "$CL/$path")" = "$before" ] && ok "A1 the clone's $(basename "$path") is the frozen before (the bundle is not stale)" || bad "A1 stale bundle: $path"
  [ "$(sha "$MAIN/$path")" = "$before" ] && ok "A2 the main tree's $(basename "$path") (read only) is the frozen before" || bad "A2 main tree differs: $path"
  [ "$(sha "$ACT/before/repo/$path")" = "$before" ] && [ "$(sha "$ACT/after/repo/$path")" = "$after" ] && ok "A3 before/ and after/ hash as list.txt says: $(basename "$path")" || bad "A3 frozen copies: $path"
done < "$ACT/list.txt"
MODE_H=$(stat -c %a "$CL/$HOOK"); MODE_D=$(stat -c %a "$CL/$DISP")
git -C "$CL" status --porcelain > "$D/tmp/status.before"
[ ! -s "$D/tmp/status.before" ] && ok "A4 the clone's tree is clean" || bad "A4 the clone is not clean"
expect_exit "A5 check: state before" 0 bash "$ACT/apply.sh" check
expect_exit "A6 verify refused before the apply" 3 bash "$ACT/apply.sh" verify
expect_exit "A7 undo before the apply: nothing to undo" 0 bash "$ACT/apply.sh" undo

echo "--- B. the existing tests on the BEFORE code (the baseline), and this ACT's checks on it"
pytests ok "B1 the existing stop-idle and dispatcher tests" $TESTS
run_check 0 0
run_check 1 red
run_check 2 red
run_check 3 0
echo "     (checks 1 and 2, the behaviour of the two files, are red on the old code: they tell the two apart)"

echo "--- C. the companion test change on the OLD code: the two named cases are red"
(cd "$CL" && git apply "$D/companion-tests.diff") && ok "C0 companion-tests.diff applies to the clone" || bad "C0 companion diff"
pytests red "C1 the new tests on the old code" $TESTS -k "section_6 or helper_watch or used_log or returned_log or cap_is_read or idle_reason_while or launchable_block_is_once or no_ready_count or empty_ready_list or idle_with_headroom or cause_that_stops"
(cd "$CL" && git checkout -q -- tests) && ok "C2 the clone's tests back to the committed ones" || bad "C2 tests restore"

echo "--- D. the plain apply"
expect_exit "D1 plain apply (no option, no env)" 0 bash "$ACT/apply.sh" apply
while IFS='|' read -r root path before after; do
  cmp -s "$CL/$path" "$ACT/after/repo/$path" && ok "D2 $(basename "$path") is the frozen after, byte for byte" || bad "D2 not the frozen after: $path"
done < "$ACT/list.txt"
[ "$(stat -c %a "$CL/$HOOK")" = "$MODE_H" ] && [ "$(stat -c %a "$CL/$DISP")" = "$MODE_D" ] && ok "D3 the modes are kept" || bad "D3 mode changed"
git -C "$CL" status --porcelain > "$D/tmp/status.after"
if [ "$(grep -c . "$D/tmp/status.after")" = 2 ] && grep -q "stop_idle_check.py" "$D/tmp/status.after" && grep -q "dispatcher.py" "$D/tmp/status.after"; then ok "D4 git status shows exactly the two listed files changed; no stray temp file"; else bad "D4 stray change: $(cat "$D/tmp/status.after")"; fi
(ls "$CL/governance/project/orchestration/tools"; ls "$CL/governance/project/orchestration/tools/dispatch") | grep -c '\.act-' | grep -qx 0 && ok "D5 no temp file left beside either file" || bad "D5 a temp file is left"
expect_exit "D6 verify exit 0" 0 bash "$ACT/apply.sh" verify
expect_exit "D7 check after the apply: the before it expects is gone (the operator's check runs before the apply)" 3 bash "$ACT/apply.sh" check
expect_exit "D8 apply again changes nothing" 0 bash "$ACT/apply.sh" apply
echo "--- E. every manifest check, exactly as written, with bash -c, on the applied clone"
for n in 0 1 2 3; do run_check "$n" 0; done
pytests ok "E1 the existing tests on the new code" $TESTS
(cd "$CL" && git apply "$D/companion-tests.diff") && ok "E2 companion-tests.diff applies on the applied clone" || bad "E2 companion diff"
pytests ok "E3 the existing and the new tests on the new code" $TESTS
(cd "$CL" && git checkout -q -- tests) && ok "E4 the clone's tests back to the committed ones" || bad "E4 tests restore"

echo "--- F. undo, and the states apply.sh refuses"
expect_exit "F1 undo from the applied state" 0 bash "$ACT/apply.sh" undo
while IFS='|' read -r root path before after; do
  cmp -s "$CL/$path" "$ACT/before/repo/$path" && [ "$(stat -c %a "$CL/$path")" = "$(stat -c %a "$CL/$HOOK")" ] && ok "F2 $(basename "$path") is the original, byte for byte" || bad "F2 undo differs: $path"
done < "$ACT/list.txt"
git -C "$CL" status --porcelain | grep -c . | grep -qx 0 && ok "F3 the clone's tree is clean again" || bad "F3 the clone is not clean"
expect_exit "F4 check: state before" 0 bash "$ACT/apply.sh" check
# one file moved since the freeze: nothing is written to the other
printf '# a later change\n' >> "$CL/$DISP"
expect_exit "F5 check refuses a dispatcher that changed" 3 bash "$ACT/apply.sh" check
expect_exit "F6 apply refuses (one file neither the before nor the after)" 3 bash "$ACT/apply.sh" apply
cmp -s "$CL/$HOOK" "$ACT/before/repo/$HOOK" && ok "F7 the hook, the other file, was not touched by the refused apply" || bad "F7 the hook was written"
expect_exit "F8 undo refuses too" 3 bash "$ACT/apply.sh" undo
cp -p "$ACT/before/repo/$DISP" "$CL/$DISP"
# a half-applied state (the hook applied, the dispatcher not): apply finishes it, undo takes it back
cp -p "$ACT/after/repo/$HOOK" "$CL/$HOOK"
expect_exit "F9 apply over a half-applied state completes it" 0 bash "$ACT/apply.sh" apply
expect_exit "F10 verify" 0 bash "$ACT/apply.sh" verify
expect_exit "F11 undo" 0 bash "$ACT/apply.sh" undo
expect_exit "F12 check" 0 bash "$ACT/apply.sh" check
# a frozen copy that does not hash as listed
cp -p "$ACT/after/repo/$DISP" "$D/tmp/after-disp.keep"
chmod u+w "$ACT/after/repo/$DISP"; printf 'x' >> "$ACT/after/repo/$DISP"
expect_exit "F13 a tampered frozen copy: apply refuses (exit 4)" 4 bash "$ACT/apply.sh" apply
cp -p "$D/tmp/after-disp.keep" "$ACT/after/repo/$DISP"
cmp -s "$CL/$HOOK" "$ACT/before/repo/$HOOK" && cmp -s "$CL/$DISP" "$ACT/before/repo/$DISP" && ok "F14 nothing was written by the refused apply" || bad "F14 a file was written"
[ "$(sha "$ACT/after/repo/$DISP")" = "$(cut -d'|' -f4 "$ACT/list.txt" | tail -n 1)" ] && ok "F15 the bundle's after copy restored as listed" || bad "F15 after copy not restored"
# a missing file, and a link
mv "$CL/$HOOK" "$CL/$HOOK.away"
expect_exit "F16 a missing hook: check refuses" 3 bash "$ACT/apply.sh" check
expect_exit "F17 a missing hook: apply refuses" 3 bash "$ACT/apply.sh" apply
[ ! -e "$CL/$HOOK" ] && ok "F18 nothing was created in its place" || bad "F18 a file was created"
mv "$CL/$HOOK.away" "$CL/$HOOK"
mv "$CL/$DISP" "$CL/$DISP.real"; ln -s "$CL/$DISP.real" "$CL/$DISP"
expect_exit "F19 a link: apply refuses" 3 bash "$ACT/apply.sh" apply
rm -f "$CL/$DISP"; mv "$CL/$DISP.real" "$CL/$DISP"
cmp -s "$CL/$DISP" "$ACT/before/repo/$DISP" && ok "F20 the clone is back to the original" || bad "F20 not restored"

echo "--- G. the live files are unchanged (read only), the main tree clean"
while IFS='|' read -r root path before after; do
  [ "$(sha "$MAIN/$path")" = "$before" ] && ok "G1 the main tree's $(basename "$path") is unchanged" || bad "G1 the main tree's $path changed"
done < "$ACT/list.txt"
[ -z "$(git -C "$MAIN" status --porcelain -- "$HOOK" "$DISP")" ] && ok "G2 neither live file shows a change in git" || bad "G2 a live file changed"
ls "$PH" | grep -c . | grep -qx 0 && ok "G3 nothing was written to the planted HOME" || bad "G3 the planted HOME holds files"

echo
[ "$FAILS" = 0 ] && echo "REHEARSAL PASS" || echo "REHEARSAL FAIL"
echo "failures: $FAILS"
