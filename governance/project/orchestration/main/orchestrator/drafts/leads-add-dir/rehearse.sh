#!/bin/bash
# ACT-LEADS-ADD-DIR-1's rehearsal, on a clone of w2/integrate (never the main tree): run the whole script inside ONE
# heavy-job slot (bash heavy_slot.sh bash rehearse.sh <clone> <bundle> <drafts>); the pytest runs below do not take
# their own slot again. Writes only in the clone and in $TMPDIR. Prints the log on stdout.
set -u
C=$1; B=$2; D=$3
MAIN=/home/usain/Dynamic-Agentic-Engineering-OS
P=governance/project/orchestration/tools/dispatch/launch_now.sh
IFS='|' read -r _ _ BEFORE AFTER < "$B/list.txt"
FILES="tests/unit/launch/test_w2_153_template.py tests/acceptance/W2-153/test_w2_153_dispatch.py tests/unit/orchestration/test_dispatcher.py"
pass=0; fail=0
ok()  { echo "ok   $*"; pass=$((pass+1)); }
bad() { echo "FAIL $*"; fail=$((fail+1)); }
h() { sha256sum "$1" | cut -c1-64; }
expect() {  # expect <want exit> <label> <command...>
  local want=$1 label=$2; shift 2
  local out rc; out="$("$@" 2>&1)"; rc=$?
  [ -n "$out" ] && echo "$out" | sed 's/^/     /'
  if [ "$rc" = "$want" ]; then ok "$label (exit $rc)"; else bad "$label (exit $rc, wanted $want)"; fi
}
suites() {  # suites <want exit> <label>: the three files that read the launcher, in this slot
  local want=$1 label=$2 out rc
  out="$(cd "$C" && env PYTHONPATH="$C/src" python3 -m pytest -q -p no:cacheprovider $FILES 2>&1)"; rc=$?
  echo "$out" | grep -E '^(FAILED|ERROR) ' | sed 's/^/     /'
  echo "$out" | tail -1 | sed 's/^/     /'
  if [ "$rc" = "$want" ]; then ok "$label: exit $rc"; else bad "$label: exit $rc, wanted $want"; fi
}
checks() {  # checks <expected exits, space separated>: every manifest check exactly as written, bash -c, clone root
  local want=($1) i=0 c rc out
  while IFS= read -r -d '' c; do
    out="$(cd "$C" && bash -c "$c" 2>&1)"; rc=$?
    [ -n "$out" ] && echo "$out" | tail -2 | sed 's/^/     /'
    if [ "$rc" = "${want[$i]}" ]; then ok "check $i as written: $(echo "$c" | head -1 | cut -c1-90)... (exit $rc)"
    else bad "check $i as written: $(echo "$c" | head -1 | cut -c1-90)... (exit $rc, wanted ${want[$i]})"; fi
    i=$((i+1))
  done < <(python3 -I -c 'import json,sys; [sys.stdout.write(c+"\0") for c in json.load(open(sys.argv[1]))]' "$D/checks.json")
}
A() { (cd "$C" && bash "$B/apply.sh" "$@"); }

echo "ACT-LEADS-ADD-DIR-1 rehearsal, $(date -u '+%F %T') UTC; slot ${GOV_HEAVY_SLOT:-none}, CPUs ${GOV_HEAVY_CPUS:-unconfined}"
echo "--- A. the bundle and the clone"
echo "clone HEAD $(git -C "$C" rev-parse --short=12 HEAD) on $(git -C "$C" rev-parse --abbrev-ref HEAD); main tree head $(git -C "$MAIN" rev-parse --short=12 HEAD)"
[ "$(h "$C/$P")" = "$BEFORE" ] && ok "A0 the clone's launcher is the frozen before (the bundle is not stale)" || bad "A0 the clone's launcher is not the frozen before"
[ "$(h "$MAIN/$P")" = "$BEFORE" ] && ok "A0b the main tree's launcher (read only) is the frozen before" || bad "A0b the main tree's launcher is not the frozen before"
[ "$(h "$B/before/repo/$P")" = "$BEFORE" ] && [ "$(h "$B/after/repo/$P")" = "$AFTER" ] && ok "A0c before/ and after/ hash as list.txt says" || bad "A0c the frozen copies do not hash as listed"
MAIN_STATUS_0="$(git -C "$MAIN" --no-optional-locks status --porcelain -- governance tests src | md5sum)"
expect 0 "A1 check: state before" A check
expect 3 "A2 verify refused before the apply" A verify
expect 0 "A3 undo before the apply says nothing to undo" A undo

echo "--- B. the existing suites on the BEFORE launcher (the baseline)"
suites 0 "B1 the three files that read the launcher (before, no companion)"
checks "0 1 1 1 0"

echo "--- C. the sequencing: the plain apply WITHOUT the companion turns two existing W2-153 tests red (check 3 refuses it)"
expect 0 "C1 plain apply" A apply
checks "0 0 0 1 0"
suites 1 "C2 the existing suites with the ACT and no companion are red, as check 3 says (the two named tests)"
expect 0 "C3 undo" A undo
[ "$(h "$C/$P")" = "$BEFORE" ] && ok "C4 undone byte for byte" || bad "C4 not undone byte for byte"
rm -rf "$TMPDIR"/pytest-of-* 2>/dev/null

echo "--- D. the companion (tolerant of the --add-dir line), then the plain apply"
expect 0 "D0 companion-tests.diff applies to the clone" git -C "$C" apply "$D/companion-tests.diff"
git -C "$C" status --porcelain | sed 's/^/     /'
echo "the old launcher with the companion:"
checks "0 1 1 0 0"
suites 0 "D1 the existing suites, old launcher + companion"
expect 0 "D2 plain apply" A apply
[ "$(h "$C/$P")" = "$AFTER" ] && ok "D3 the launcher is the frozen after, byte for byte" || bad "D3 the launcher is not the frozen after"
[ "$(stat -c %a "$C/$P")" = 755 ] && ok "D4 the mode is kept (755)" || bad "D4 the mode changed"
st="$(git -C "$C" status --porcelain | sort | paste -sd' ')"
[ "$st" = " M $P  M tests/acceptance/W2-153/test_w2_153_dispatch.py  M tests/unit/launch/test_w2_153_template.py" ] \
  && ok "D5 the apply changed the one listed file and wrote nothing else (git status: the launcher and the two companion files)" || bad "D5 git status: $st"
ls "$C/$(dirname "$P")" | grep -q 'act-' && bad "D6 a temp file was left beside the launcher" || ok "D6 no temp file left beside the launcher"
expect 0 "D7 check: state applied" A check
expect 0 "D8 verify" A verify
expect 0 "D9 apply again changes nothing" A apply

echo "--- E. every manifest check, exactly as written, with bash -c, on the applied clone"
checks "0 0 0 0 0"
suites 0 "E1 the existing suites, ACT applied + companion"
# review round 1, F1: check 1 matches the home part by a pattern; show it still refuses a wrong TESTS or RUNS line
C1="$(python3 -I -c 'import json,sys; print(json.load(open(sys.argv[1]))[1])' "$D/checks.json")"
cp -p "$C/$P" "$TMPDIR/launcher.applied"
sed -i 's#/gov-os-runs"$#/gov-os-run"#' "$C/$P"
expect 1 "E2 check 1 refuses a RUNS line that is not <home>/gov-os-runs" bash -c "cd '$C' && $C1"
cp -p "$TMPDIR/launcher.applied" "$C/$P"
sed -i 's#/gov-os-worktrees/\$W2-tests"$#/gov-os-worktrees/x/$W2-tests"#' "$C/$P"
expect 1 "E3 check 1 refuses a TESTS line that is not <home>/gov-os-worktrees/\$W2-tests" bash -c "cd '$C' && $C1"
cp -p "$TMPDIR/launcher.applied" "$C/$P"; rm -f "$TMPDIR/launcher.applied"
[ "$(h "$C/$P")" = "$AFTER" ] && ok "E4 the launcher is the frozen after again" || bad "E4 the launcher is not the frozen after"

echo "--- F. the follow-up tests (the new behaviour, committed after the apply)"
expect 0 "F0 followup-tests.diff applies" git -C "$C" apply "$D/followup-tests.diff"
suites 0 "F1 the suites with the follow-up tests, ACT applied"
expect 0 "F2 undo (to show the follow-up tests are real)" A undo
suites 1 "F3 the follow-up tests are red on the old launcher (the two new tests)"
expect 0 "F4 apply again" A apply
git -C "$C" checkout -q -- tests/unit/launch/test_w2_153_template.py && git -C "$C" apply "$D/companion-tests.diff" --include='tests/unit/*' \
  && ok "F5 the follow-up taken back out (companion only again)" || bad "F5 could not take the follow-up out"

echo "--- G. a dry run of the lead line with a planted W2 (W2-PLANT), stub claude and gov, in a temporary bed"
T="$(mktemp -d)"
mkdir -p "$T/orch/tools" "$T/orch/briefs" "$T/orch/log" "$T/bin" "$T/runs" "$T/trees/W2-PLANT/.claude/templates"
echo 'exit 0' > "$T/orch/tools/disk_gate.sh"; echo brief > "$T/orch/briefs/B.md"; echo '# lead' > "$T/trees/W2-PLANT/.claude/templates/role-lead.md"
sed -e "s#^ORCH=.*#ORCH=$T/orch#" -e "s#/home/[A-Za-z0-9_.-]*/gov-os-worktrees#$T/trees#g" -e "s#/home/[A-Za-z0-9_.-]*/gov-os-runs#$T/runs#g" \
    -e "s#/home/[A-Za-z0-9_.-]*/[.]local/bin#$T/bin#g" "$C/$P" > "$T/launch.sh"
printf '#!/bin/bash\nprintf "%%s\\n" "$@" > "%s/argv.txt"\nexit 0\n' "$T" > "$T/bin/claude"
printf '#!/bin/bash\nexit 0\n' > "$T/bin/gov"; chmod +x "$T/bin/claude" "$T/bin/gov"
bash "$T/launch.sh" W2-PLANT DAEO-plant B.md L.json < /dev/null > /dev/null 2> "$T/stderr.txt"; rc=$?
echo "     the lead's argv (the bed's root shown as <bed>):"
sed "s#$T#<bed>#g" "$T/argv.txt" | awk 'length($0) > 110 {print substr($0,1,100) "...<" length($0) " chars>"; next} {print}' | sed 's/^/       /'
[ "$rc" = 0 ] && grep -qx -- "$T/trees/W2-PLANT-tests" "$T/argv.txt" && grep -qx -- "$T/runs" "$T/argv.txt" && [ "$(grep -cx -- --add-dir "$T/argv.txt")" = 2 ] \
  && ok "G1 the planted lead's line carries --add-dir <W2-PLANT-tests> --add-dir <runs root>, once each" || bad "G1 the planted line (exit $rc)"
[ -d "$T/trees/W2-PLANT-tests" ] && [ -z "$(ls -A "$T/trees/W2-PLANT-tests")" ] && ok "G2 W2-PLANT-tests made, empty" || bad "G2 W2-PLANT-tests"
(cd "$T/trees/W2-PLANT" && git init -q . && git -c user.name=r -c user.email=r@x commit -q --allow-empty -m base && git worktree add -q "$T/trees/W2-PLANT-tests" -b w2/W2-PLANT-tests HEAD) 2>&1 | sed 's/^/     /'
[ -e "$T/trees/W2-PLANT-tests/.git" ] && ok "G3 the lead's own step (git worktree add) takes the empty folder" || bad "G3 git worktree add refused the empty folder"
grep -q LAUNCH_NO_TESTS_DIR "$T/stderr.txt" && bad "G4 the launch said LAUNCH_NO_TESTS_DIR" || ok "G4 no LAUNCH_NO_TESTS_DIR"
rm -rf "$T"

echo "--- H. undo, and the trees"
expect 0 "H1 undo" A undo
[ "$(h "$C/$P")" = "$BEFORE" ] && ok "H2 undone byte for byte" || bad "H2 not undone byte for byte"
expect 0 "H3 check: state before" A check
echo "# drift" >> "$C/$P"
expect 3 "H4 apply refuses a launcher changed since the freeze (state other, untouched)" A apply
expect 3 "H5 undo refuses it too" A undo
git -C "$C" checkout -q -- "$P"
[ "$(h "$MAIN/$P")" = "$BEFORE" ] && ok "H6 the main tree's launcher is unchanged" || bad "H6 the main tree's launcher changed"
[ "$(git -C "$MAIN" --no-optional-locks status --porcelain -- governance tests src | md5sum)" = "$MAIN_STATUS_0" ] && ok "H7 the main tree's tracked governance/tests/src status unchanged" || bad "H7 the main tree's status changed"
echo "=== $pass ok, $fail failed"
echo "failures: $fail"   # G3 reads the last non-blank line (review round 1, F2)
[ "$fail" = 0 ]
