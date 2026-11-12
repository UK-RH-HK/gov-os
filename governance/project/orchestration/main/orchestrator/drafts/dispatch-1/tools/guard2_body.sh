echo "--- B. the existing tests of test_stop_idle_check.py on the OLD hook (the baseline)"
heavy "B1 test_stop_idle_check.py, old hook, old tests" 0 tests/unit/orchestration/test_stop_idle_check.py
BASE_RESULT=$LAST_RESULT

echo "--- C. the new test cases on the OLD hook: red"
for r in "${TESTS[@]}"; do cp "$ACT/after/repo/$r" "$CL/$r"; done
heavy "C1 the new test file on the old hook" 1 "${TESTS[@]}"
RED_RESULT=$LAST_RESULT
[ "$(grep -c '^FAILED' "$OUT")" -ge 8 ] && ok "C2 at least 8 of the cases fail on the old hook ($(grep -c '^FAILED' "$OUT"))" || bad "C2 too few red cases"
echo "     round 2 (the review's F1): the same new test file on the ROUND-1 hook (the frozen after of acts/ACT-IDLE-GUARD-2.r1):"
cp "$D/acts/ACT-IDLE-GUARD-2.r1/after/repo/governance/project/orchestration/tools/stop_idle_check.py" "$CL/governance/project/orchestration/tools/stop_idle_check.py"
heavy "C4 the round-2 test file on the round-1 hook" 1 "${TESTS[@]}"
R1RED_RESULT=$LAST_RESULT
grep -q "^FAILED .*test_f1_r2_a_claimed_ticket_with_a_fresh_branch" "$OUT" && grep -q "^FAILED .*test_f1_r2_a_fresh_branch_stays_named" "$OUT" && ! grep -q "^FAILED .*test_f1_r2_a_truly_merged" "$OUT" \
  && ok "C5 on the round-1 hook the two fresh-branch cases are red and the truly-merged case is green" || bad "C5 the round-1 hook's red set is not as expected"
(cd "$CL" && git checkout -q -- governance/project/orchestration/tools/stop_idle_check.py)
run_check 1 1 -
echo "     (check 1, the hook's behaviour, is red on the old hook: it tells the two apart)"
run_check 0 0 -
run_check 2 0 -
(cd "$CL" && git checkout -q -- "${TESTS[@]}")
git -C "$CL" status --porcelain | grep -c . | grep -qx 0 && ok "C3 the clone is clean again (old hook, old tests)" || bad "C3 the clone is not clean"

echo "--- D. the plain apply"
expect_exit "D1 plain apply (no option, no env)" 0 bash "$ACT/apply.sh" apply
i=0; for r in "${RELS[@]}"; do
  cmp -s "$CL/$r" "$ACT/after/repo/$r" && ok "D2.$i ${r##*/} is the frozen after, byte for byte" || bad "D2.$i ${r##*/} is not the frozen after"
  [ "$(stat -c %a "$CL/$r")" = "${MODES[$i]}" ] && ok "D3.$i the mode of ${r##*/} is kept (${MODES[$i]})" || bad "D3.$i mode changed: $r"
  i=$((i + 1))
done
git -C "$CL" status --porcelain | sort > "$OUT"
[ "$(wc -l < "$OUT")" = 2 ] && [ "$(grep -c '^ M ' "$OUT")" = 2 ] && ok "D4 git status shows exactly two modified files and nothing else" || bad "D4 stray change: $(cat "$OUT")"
find "$CL/governance/project/orchestration/tools" "$CL/tests/unit/orchestration" -maxdepth 1 -name '*.act-*' | grep -c . | grep -qx 0 && ok "D5 no temp file left beside the files" || bad "D5 a temp file is left"
expect_exit "D6 check refused after the apply" 3 bash "$ACT/apply.sh" check
expect_exit "D7 verify exit 0" 0 bash "$ACT/apply.sh" verify
expect_exit "D8 apply again changes nothing" 0 bash "$ACT/apply.sh" apply

echo "--- E. every manifest check exactly as written, then the tests: green"
run_check 0 0 -
run_check 1 0 4
run_check 2 0 -
heavy "E1 test_stop_idle_check.py, new hook, new tests" 0 tests/unit/orchestration/test_stop_idle_check.py
GREEN_RESULT=$LAST_RESULT
echo "     baseline: $BASE_RESULT | new cases on the old hook: $RED_RESULT | after the apply: $GREEN_RESULT | new file on the round-1 hook: $R1RED_RESULT"
heavy "E2 the other hook suites still green (stop_waiter, safety nets)" 0 tests/unit/orchestration/test_stop_waiter_check.py tests/unit/orchestration/test_cto_safety_nets.py

echo "--- F. the new hook against the real gov plan (a planted orchestrator folder, the real gov, the main tree's branches read only)"
FW=$D/tmp/f2world; rm -rf "${FW:?}"; mkdir -p "$FW/orch/log" "$FW/orch/dispatch" "$FW/tasks"
echo "cto-rehearsal-0000" > "$FW/orch/log/cto-session.txt"
echo '{"max_leads": 3}' > "$FW/orch/dispatch/config.json"
echo '{"leads": [], "lead_count": 0, "pending_launches": [], "jobs": [], "gate_open": true, "disk_open": true, "admit": true, "forecast": {"lead": {"ok": true}}, "ready_count": 0, "ready_waits": {}}' > "$FW/orch/dispatch/status.json"
printf '## 0. T\n| # | item | state |\n|---|---|---|\n| 1 | closed | **DONE 11-08** |\n' > "$FW/dnd.md"
echo '[]' > "$FW/procs.json"
echo '{"type": "user", "uuid": "turn-1", "message": {"content": "go"}}' > "$FW/t.jsonl"
(cd "$CL" && penv env GOV_STOPIDLE_ORCH="$FW/orch" GOV_STOPIDLE_DND="$FW/dnd.md" GOV_STOPIDLE_TASKS="$FW/tasks" \
   GOV_STOPIDLE_SUBAGENTS="$FW/none" GOV_STOPIDLE_PROC="$FW/procs.json" GOV_STOPIDLE_PIDGLOBS="" GOV_STOPIDLE_REPO="$MAIN" \
   python3 -I governance/project/orchestration/tools/stop_idle_check.py \
   < <(printf '{"session_id": "cto-rehearsal-0000", "stop_hook_active": false, "transcript_path": "%s"}' "$FW/t.jsonl")) > "$OUT" 2> "$D/tmp/f2err"
rc=$?
[ "$rc" = 0 ] && [ ! -s "$D/tmp/f2err" ] && ok "F1 the hook ran against the real gov plan: exit 0, nothing on standard error" || bad "F1 hook run (exit $rc)"
[ -z "$(ls "$FW/orch/log" | grep '^plan-ready-')" ] && ok "F2 no plan temp file left" || bad "F2 a plan temp file is left"
MERGED=$(git -C "$MAIN" for-each-ref --merged w2/integrate --format='%(refname:short)' refs/heads/w2/ | sed 's#^w2/##' | tr '\n' ' ')
python3 -I - "$OUT" "$FW/orch/log/stop-idle.log" "$MERGED" <<'PYEOF' && ok "F3 no merged ticket of the main tree is named launchable, W2-00 never, and the plan and the branch listing both read" || bad "F3 the real plan's reading"
import json, sys
out, log, merged = open(sys.argv[1]).read(), open(sys.argv[2]).read(), set(sys.argv[3].split())
ans = json.loads(out) if out.strip() else {}
named = ans.get("reason", "")
head = named.split(" (ready.txt is empty")[0] if "launchable:" in named else ""
tickets = {t.split()[0] for t in head.split("launchable: ", 1)[1].split("; ")} if head else set()
assert not (tickets & merged), tickets & merged
assert "W2-00" not in tickets
assert "gov plan unusable" not in log and "merged branches not read" not in log, log
PYEOF

echo "--- G. undo, and the apply.sh states"
expect_exit "G1 undo" 0 bash "$ACT/apply.sh" undo
i=0; for r in "${RELS[@]}"; do
  cmp -s "$CL/$r" "$ACT/before/repo/$r" && [ "$(stat -c %a "$CL/$r")" = "${MODES[$i]}" ] && ok "G2.$i ${r##*/} is the original, byte for byte, mode kept" || bad "G2.$i undo differs: $r"
  i=$((i + 1))
done
git -C "$CL" status --porcelain | grep -c . | grep -qx 0 && ok "G3 the clone is clean after the undo" || bad "G3 the clone is not clean"
expect_exit "G4 check: state before" 0 bash "$ACT/apply.sh" check
R0=${RELS[0]}; R1=${RELS[1]}
printf '# a later change\n' >> "$CL/$R0"
expect_exit "G5 check refuses a file that changed" 3 bash "$ACT/apply.sh" check
expect_exit "G6 apply refuses (neither before nor after)" 3 bash "$ACT/apply.sh" apply
cmp -s "$CL/$R1" "$ACT/before/repo/$R1" && ok "G7 apply wrote nothing to the other file" || bad "G7 another file was written"
cp -p "$ACT/before/repo/$R0" "$CL/$R0"
expect_exit "G8 apply" 0 bash "$ACT/apply.sh" apply
cp -p "$ACT/before/repo/$R1" "$CL/$R1"
expect_exit "G9 a half-applied state: verify refuses" 3 bash "$ACT/apply.sh" verify
expect_exit "G10 a half-applied state: apply finishes it" 0 bash "$ACT/apply.sh" apply
expect_exit "G11 verify" 0 bash "$ACT/apply.sh" verify
cp -p "$ACT/before/repo/$R0" "$CL/$R0"
expect_exit "G12 a half-applied state: undo takes it back" 0 bash "$ACT/apply.sh" undo
git -C "$CL" status --porcelain | grep -c . | grep -qx 0 && ok "G13 the clone is back to the original" || bad "G13 not restored"
TB=$D/tmp/tampered2; rm -rf "${TB:?}"; cp -r "$ACT" "$TB"; echo "# tampered" >> "$TB/after/repo/$R0"
expect_exit "G14 a tampered frozen copy: apply refuses (4)" 4 bash "$TB/apply.sh" apply
cmp -s "$CL/$R0" "$ACT/before/repo/$R0" && ok "G15 nothing was written" || bad "G15 a file was written"
rm -rf "${TB:?}"
mv "$CL/$R1" "$CL/$R1.away"
expect_exit "G16 a missing file: apply refuses" 3 bash "$ACT/apply.sh" apply
[ ! -e "$CL/$R1" ] && ok "G17 nothing was created in its place" || bad "G17 a file was created"
mv "$CL/$R1.away" "$CL/$R1"
mv "$CL/$R1" "$CL/$R1.real"; ln -s "$CL/$R1.real" "$CL/$R1"
expect_exit "G18 a link: apply refuses" 3 bash "$ACT/apply.sh" apply
rm -f "${CL:?}/$R1"; mv "$CL/$R1.real" "$CL/$R1"
git -C "$CL" status --porcelain | grep -c . | grep -qx 0 && ok "G19 the clone is clean again" || bad "G19 not clean"

echo "--- H. the live files are unchanged (read only)"
i=0; while IFS='|' read -r root path before after; do
  [ "$(sha "$MAIN/$path")" = "$before" ] && ok "H1.$i the main tree's ${path##*/} is unchanged" || bad "H1.$i the main tree's file changed: $path"
  i=$((i + 1))
done < "$ACT/list.txt"
[ -z "$(ls -A "$PH")" ] && ok "H2 the planted HOME is empty" || bad "H2 the planted HOME holds files"
[ "$(git -C "$MAIN" status --porcelain -- governance tests | wc -l)" = 0 ] && ok "H3 the main tree's governance/ and tests/ are clean" || bad "H3 the main tree is not clean there"

echo
[ "$FAILS" = 0 ] && echo "REHEARSAL PASS" || echo "REHEARSAL FAIL"
echo "failures: $FAILS"
