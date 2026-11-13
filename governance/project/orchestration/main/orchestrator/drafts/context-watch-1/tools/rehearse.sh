#!/bin/bash
# ACT-CONTEXT-WATCH-1's rehearsal, as the operator will run it: a --no-hardlinks clone of w2/integrate (the main tree's head),
# W2-176 merged in the clone only (git merge --no-ff --no-edit 3b6c5cb79d39), a planted HOME, the clean environment of the
# operator's dry run (PATH, LANG, TMPDIR, HOME planted, PYTHONDONTWRITEBYTECODE; nothing GOV_*), every manifest check run
# EXACTLY as written with `bash -c` from the clone, the plain apply (no option). The pytest runs go one folder at a time
# through the heavy-slot gate with the user's own HOME (the planted one hides the user-site pytest) and are parsed from
# pytest's own summary line (passed > 0, failed 0). The registered command itself is run on planted PostToolUse events.
# The log has no head, pid, date or duration, so a second rehearsal against the same bytes is the same log.
#   bash rehearse.sh      the log is ../rehearsal.log (it ends "failures: <n>")
set -u
MAIN=/home/usain/Dynamic-Agentic-Engineering-OS
D=$MAIN/.gov-runtime/scratch/orchestrator/drafts/context-watch-1
ORCH=$MAIN/.gov-runtime/scratch/orchestrator
RUN=/home/usain/gov-os-runs/W2-00/context-watch-1
CL=$RUN/rclone
PH=$D/tmp/home
ACT=$ORCH/acts/ACT-CONTEXT-WATCH-1
LOG=$D/rehearsal.log
HEAVY=$ORCH/tools/heavy_slot.sh
W2176=3b6c5cb79d39
HOOK=template/governance/kernel/hooks/context_watch.py
HOOK_SHA=213882efd7b83e9988a50d3a348dc92479d4b402d2f54985db9e6ffd84d2a242
RELS=(.claude/settings.json .rulesync/hooks.jsonc)
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
penv() { env -i PATH=/home/usain/.local/bin:/usr/local/bin:/usr/bin:/bin LANG=C.UTF-8 TMPDIR="$D/tmp" HOME="$USER_HOME" PYTHONDONTWRITEBYTECODE=1 "$@"; }
show() { sed -e "s|/home/usain/.local/share/gov-os/pin-[0-9a-f]*|PINNED|g" -e "s|$CL|CLONE|g" -e "s|$D|DRAFTS|g" | cut -c1-200 | sed 's/^/     /'; }
expect_exit() { # expect_exit <label> <want> <cmd...>   (run in the clone, clean env)
  local label="$1" want="$2"; shift 2
  (cd "$CL" && cenv "$@") > "$OUT" 2>&1; local rc=$?
  tail -n 6 "$OUT" | show
  [ "$rc" = "$want" ] && ok "$label (exit $rc)" || bad "$label: want exit $want, got $rc"
}
check_cmd() { python3 -I -c "import json,sys; print(json.load(open('$D/tools/checks.json'))['checks'][int(sys.argv[1])]['cmd'])" "$1"; }
run_check() { # run_check <n> <want exit> <count or ->: the manifest's check n, as written, bash -c, from the clone
  local cmd; cmd=$(check_cmd "$1")
  (cd "$CL" && cenv bash -c "$cmd") > "$OUT" 2>&1; local rc=$?
  tail -n 3 "$OUT" | show
  if [ "$rc" = "$2" ] && { [ "$3" = - ] || [ "$(tail -n 1 "$OUT")" = "$3" ]; }; then ok "check $1 as written (exit $rc${3:+, count $3})"; else bad "check $1: want exit $2 count $3, got exit $rc"; fi
}
LAST_RESULT=""
gated() { # gated <label> <pytest args...>: one folder through the heavy-slot gate; exit 0, passed > 0, no failed, from pytest's summary
  local label="$1"; shift
  (cd "$CL" && penv bash "$HEAVY" env TMPDIR="$RUN/tmp/rt" PYTHONUSERBASE=/home/usain/.local PYTHONPATH="$CL/src" python3 -m pytest "$@" -q -p no:cacheprovider \
     -o tmp_path_retention_policy=failed) > "$OUT" 2>&1; local rc=$?
  grep -E "^FAILED" "$OUT" | sed 's/ - .*//' | sort | cut -c1-170 | sed 's/^/     /'
  local line; line=$(grep -E "^=*[ ]*[0-9]+ (passed|failed|error)" "$OUT" | tail -n 1 | sed -E 's/ in [0-9.]+s( \([0-9:]+\))?//; s/=+//g; s/^ +//; s/ +$//')
  local passed failed; passed=$(echo "$line" | grep -oE '[0-9]+ passed' | grep -oE '[0-9]+'); failed=$(echo "$line" | grep -oE '[0-9]+ (failed|error)' | grep -oE '[0-9]+' | head -n 1)
  echo "     pytest: ${line:-no summary line}"
  LAST_RESULT="$line"
  if [ "$rc" = 0 ] && [ "${passed:-0}" -gt 0 ] && [ -z "${failed:-}" ]; then ok "$label: exit 0, ${passed} passed"; else bad "$label: exit $rc, summary '${line}'"; fi
}
portab() { # portab <label> <want findings: 0 | CODE>
  (cd "$CL" && penv env PYTHONUSERBASE=/home/usain/.local PYTHONPATH="$CL/src" python3 -m gov.adapters.portability) > "$OUT" 2>&1; local rc=$?
  python3 -I -c "
import json,sys
t=open('$OUT').read(); d=json.loads(t[t.index('{'):])
f=d['findings']; print('     findings:', [x['code']+' '+x.get('file','') for x in f] or 'none', '| compared:', d['compared'])
sys.exit(0 if (str(sys.argv[1])=='0' and not f) or (sys.argv[1]!='0' and any(x['code']==sys.argv[1] for x in f)) else 1)" "$2"
  [ $? = 0 ] && ok "$1" || bad "$1 (exit $rc)"
}
chmod -R u+w "${RUN:?}/tmp/rt" 2>/dev/null; rm -rf "${RUN:?}/tmp/rt" 2>/dev/null; mkdir -p "$RUN/tmp/rt"  # pytest tmp outside the repository (a guard case reads its own path)

echo "--- A. the bundle and the clone (w2/integrate, W2-176 not yet merged)"
chmod -R u+w "${CL:?}" 2>/dev/null; rm -rf "${CL:?}" "${PH:?}"; mkdir -p "$PH"
git clone -q --no-hardlinks "$MAIN" "$CL" || { echo "FAIL clone"; echo "failures: 1"; exit 1; }
git -C "$CL" config user.email rehearsal@example.invalid; git -C "$CL" config user.name rehearsal
echo "clone of the main tree's $(git -C "$CL" rev-parse --abbrev-ref HEAD)"
i=0; while IFS='|' read -r root path before after; do
  [ "$(sha "$CL/$path")" = "$before" ] && ok "A0.$i the clone's $path is the frozen before (the bundle is not stale)" || bad "A0.$i stale: $path"
  [ "$(sha "$MAIN/$path")" = "$before" ] && ok "A0.$i the main tree's $path (read only) is the frozen before" || bad "A0.$i main tree differs: $path"
  [ "$(sha "$ACT/before/repo/$path")" = "$before" ] && [ "$(sha "$ACT/after/repo/$path")" = "$after" ] && ok "A0.$i before/ and after/ copies hash as list.txt says" || bad "A0.$i frozen copies: $path"
  i=$((i + 1))
done < "$ACT/list.txt"
[ ! -e "$CL/$HOOK" ] && ok "A1 the hook file is absent in the clone (W2-176 is not merged)" || bad "A1 the hook file is already there"
MODES=(); for r in "${RELS[@]}"; do MODES+=("$(stat -c %a "$CL/$r")"); done

echo "--- B. the order: the hook file absent (before W2-176's merge)"
expect_exit "B1 check refuses: the hook file is absent" 6 bash "$ACT/apply.sh" check
expect_exit "B2 apply refuses: the hook file is absent" 6 bash "$ACT/apply.sh" apply
i=0; for r in "${RELS[@]}"; do cmp -s "$CL/$r" "$ACT/before/repo/$r" && ok "B3.$i apply wrote nothing to $r" || bad "B3.$i $r was written"; i=$((i + 1)); done
expect_exit "B4 verify refused before the apply" 3 bash "$ACT/apply.sh" verify
expect_exit "B5 undo before the apply changes nothing" 0 bash "$ACT/apply.sh" undo
echo "     what the registration would do with the file absent (the registered command, run as Claude Code runs it):"
AFTER_CMD=$(python3 -I -c "import json; print(json.load(open('$ACT/after/repo/.claude/settings.json'))['hooks']['PostToolUse'][0]['hooks'][0]['command'])")
mkdir -p "$D/tmp/b-proj"
printf '%s' '{"hook_event_name":"PostToolUse","session_id":"b1","transcript_path":"/nonexistent","cwd":"/","tool_name":"Bash"}' > "$D/tmp/b-event.json"
(cd "$CL" && penv env CLAUDE_PROJECT_DIR="$CL" GOV_ROLE=engineer GOV_TICKET=W2-9 bash -c "$AFTER_CMD" < "$D/tmp/b-event.json") > "$OUT" 2>&1; rc=$?
show < "$OUT"
[ "$rc" = 2 ] && grep -q "can't open file" "$OUT" && ok "B6 the registered command on a tree without the file exits 2 with \"can't open file\" (a blocking error on every Bash call)" || bad "B6 absent-file consequence: exit $rc"

echo "--- C. W2-176 merged in the clone only, and the entry criterion"
(cd "$CL" && git fetch -q "$MAIN" w2/W2-176 && git merge --no-ff --no-edit "$W2176" > "$OUT" 2>&1); rc=$?
tail -n 3 "$OUT" | show
[ "$rc" = 0 ] && ok "C1 git merge --no-ff --no-edit of W2-176's head (exit 0)" || bad "C1 merge exit $rc"
[ "$(sha "$CL/$HOOK")" = "$HOOK_SHA" ] && ok "C2 $HOOK is the bytes the owner approves (sha256 $HOOK_SHA)" || bad "C2 the hook file differs"
[ "$(git -C "$CL" status --porcelain | wc -l)" = 0 ] && ok "C3 the clone is clean after the merge" || bad "C3 not clean"
for i in 0 1; do cmp -s "$CL/${RELS[$i]}" "$ACT/before/repo/${RELS[$i]}" && ok "C4.$i the merge left ${RELS[$i]} as the frozen before" || bad "C4.$i the merge moved ${RELS[$i]}"; done
printf '# a later change\n' >> "$CL/$HOOK"
expect_exit "C5 check refuses a hook file that is not the approved bytes" 6 bash "$ACT/apply.sh" check
expect_exit "C6 apply refuses it too" 6 bash "$ACT/apply.sh" apply
(cd "$CL" && git checkout -q -- "$HOOK")
expect_exit "C7 check: state before, the hook file in place" 0 bash "$ACT/apply.sh" check
expect_exit "C8 verify refused before the apply" 3 bash "$ACT/apply.sh" verify
echo "     the checks that are red on the old files (the registration is not there yet):"
run_check 1 1 -
run_check 0 0 -
run_check 2 0 -
run_check 4 0 -

echo "--- D. the baseline on the merged clone, before the apply"
portab "D1 adapter-portability on w2/integrate + W2-176: no findings" 0
gated "D2 tests/unit/hooks (W2-176's cases and the hook suites), before the apply" tests/unit/hooks

echo "--- E. the plain apply"
expect_exit "E1 plain apply (no option, no env)" 0 bash "$ACT/apply.sh" apply
i=0; for r in "${RELS[@]}"; do
  cmp -s "$CL/$r" "$ACT/after/repo/$r" && ok "E2.$i $r is the frozen after, byte for byte" || bad "E2.$i $r is not the frozen after"
  [ "$(stat -c %a "$CL/$r")" = "${MODES[$i]}" ] && ok "E3.$i the mode of $r is kept (${MODES[$i]})" || bad "E3.$i mode changed: $r"
  i=$((i + 1))
done
git -C "$CL" status --porcelain | sort > "$OUT"
[ "$(wc -l < "$OUT")" = 2 ] && [ "$(grep -c '^ M ' "$OUT")" = 2 ] && ok "E4 git status shows exactly two modified files and nothing else" || bad "E4 stray change: $(cat "$OUT")"
find "$CL/.claude" "$CL/.rulesync" -name '*.act-*' | grep -c . | grep -qx 0 && ok "E5 no temp file left beside the files" || bad "E5 a temp file is left"
(cd "$CL" && git diff --name-status) | sed 's/^/     /'
(cd "$CL" && git diff --numstat -- .claude/settings.json .rulesync/hooks.jsonc) | sed 's/^/     added\/removed: /'
expect_exit "E6 check refused after the apply" 3 bash "$ACT/apply.sh" check
expect_exit "E7 verify exit 0" 0 bash "$ACT/apply.sh" verify
expect_exit "E8 apply again changes nothing" 0 bash "$ACT/apply.sh" apply

echo "--- F. every manifest check exactly as written, then portability"
run_check 0 0 -
run_check 1 0 6
run_check 2 0 -
run_check 3 0 8
run_check 4 0 -
portab "F1 adapter-portability after the apply: no findings (settings.json is what rulesync generates from the source)" 0
cp -p "$CL/.rulesync/hooks.jsonc" "$D/tmp/hooks.jsonc.keep"
python3 -I -c "
import re
p='$CL/.rulesync/hooks.jsonc'; t=open(p).read()
i=t.index('\"postToolUse\"'); j=t.index('\"matcher\": \"Bash\"', i)
open(p,'w').write(t[:j]+'\"matcher\": \"*\"'+t[j+len('\"matcher\": \"Bash\"'):])"
portab "F2 the all-tools form (matcher \"*\") in the source is a finding: HOOKS_MATCHER_DIFFERS (and the generated settings differ)" HOOKS_MATCHER_DIFFERS
cp -p "$D/tmp/hooks.jsonc.keep" "$CL/.rulesync/hooks.jsonc"
cmp -s "$CL/.rulesync/hooks.jsonc" "$ACT/after/repo/.rulesync/hooks.jsonc" && ok "F3 the source is the frozen after again" || bad "F3 the source differs"

echo "--- G. the registered command, run on planted PostToolUse events (a worker at 90 % of its model's 1,000,000 window; no cap)"
REGCMD=$(cd "$CL" && python3 -I -c "import json; print(json.load(open('.claude/settings.json'))['hooks']['PostToolUse'][0]['hooks'][0]['command'])")
[ "$REGCMD" = "$AFTER_CMD" ] && ok "G0 the command in the applied settings is the frozen one" || bad "G0 command differs"
PR=$D/tmp/g-proj; rm -rf "${PR:?}"; mkdir -p "$PR"; ln -s "$CL/template" "$PR/template"  # a planted project: the clone's hook by its template path, its own state folder
mk() { python3 -I -c "
import json,sys
tokens=int(sys.argv[1]); line={'type':'assistant','message':{'model':'claude-opus-5-5','usage':{'input_tokens':1,'cache_creation_input_tokens':0,'cache_read_input_tokens':tokens-1}}}
open(sys.argv[2],'w').write(json.dumps({'type':'user','message':{'content':'x'}})+'\n'+json.dumps(line)+'\n')" "$1" "$2"; }
ev() { printf '%s' "{\"hook_event_name\":\"PostToolUse\",\"session_id\":\"g1\",\"transcript_path\":\"$1\",\"cwd\":\"$PR\",\"tool_name\":\"Bash\"}"; }
mk 900000 "$D/tmp/g-t90.jsonl"; mk 400000 "$D/tmp/g-t40.jsonl"
gcall() { (cd "$CL" && penv env CLAUDE_PROJECT_DIR="$PR" GOV_ROLE=engineer GOV_TICKET=W2-9 bash -c "$REGCMD" < "$1") > "$OUT" 2> "$OUT.err"; return $?; }
ev "$D/tmp/g-t90.jsonl" > "$D/tmp/g-e90.json"
gcall "$D/tmp/g-e90.json"; rc=$?
python3 -I -c "
import json,sys
t=open('$OUT').read(); d=json.loads(t); c=d['hookSpecificOutput']['additionalContext']
print('     exit $rc; stdout keys:', list(d), '/', d['hookSpecificOutput']['hookEventName'], '; additionalContext (cut):', c[:150].replace('$PR','PROJECT')+' ...'+c[-62:])" 2>&1 | cut -c1-330
[ "$rc" = 0 ] && grep -q '"additionalContext"' "$OUT" && grep -q 'READ FIRST:' "$OUT" && grep -q 'not a stop' "$OUT" && [ ! -s "$OUT.err" ] && ok "G1 first call at 90 %: one additionalContext, exit 0, no stderr" || bad "G1 first call: exit $rc"
gcall "$D/tmp/g-e90.json"; rc=$?
echo "     second call: exit $rc; stdout $(wc -c < "$OUT") bytes"
[ "$rc" = 0 ] && [ ! -s "$OUT" ] && [ ! -s "$OUT.err" ] && ok "G2 second call in the same window: no output" || bad "G2 second call"
ev "$D/tmp/g-t40.jsonl" > "$D/tmp/g-e40.json"; gcall "$D/tmp/g-e40.json"
gcall "$D/tmp/g-e90.json"; rc=$?
[ "$rc" = 0 ] && grep -q '"additionalContext"' "$OUT" && ok "G3 a fall to 40 % re-arms: the next 90 % call reminds once more" || bad "G3 re-arm"
printf '%s' "{\"hook_event_name\":\"PostToolUse\",\"session_id\":\"g2\",\"transcript_path\":\"$D/tmp/g-t90.jsonl\",\"cwd\":\"$PR\",\"tool_name\":\"Bash\",\"agent_id\":\"a1\"}" > "$D/tmp/g-esub.json"
gcall "$D/tmp/g-esub.json"; rc=$?
[ "$rc" = 0 ] && [ ! -s "$OUT" ] && ok "G4 a subagent's event (agent_id): no output" || bad "G4 subagent"
(cd "$PR" && find . -type f | sed 's|^\./||' | sort) | sed 's/^/     files the hook wrote in the project: /'
[ "$(cd "$PR" && find . -type f | wc -l)" = 1 ] && ok "G5 the hook wrote one file, the session's marker under .gov-runtime/scratch/context_watch/" || bad "G5 stray files"
rm -f "$OUT.err"

echo "--- H. the tests, applied state, one folder per run through the heavy-slot gate"
gated "H1 W2-176's two unit files" tests/unit/hooks/test_w2_176_context_watch.py tests/unit/hooks/test_w2_176_precompact.py
gated "H2 tests/unit/hooks (the hook suites)" tests/unit/hooks
gated "H3 tests/acceptance/W1-29" tests/acceptance/W1-29
gated "H4 tests/acceptance/W1-49" tests/acceptance/W1-49
gated "H5 tests/acceptance/W2-62" tests/acceptance/W2-62
echo "     the suites that read the repository's settings, hooks source and portability:"
gated "H6 tests/unit/adapters" tests/unit/adapters
gated "H7 tests/unit/gitenv" tests/unit/gitenv
for t in W2-05 W2-59 W2-65 W2-106; do [ -d "$CL/tests/acceptance/$t" ] && gated "H8 tests/acceptance/$t" tests/acceptance/$t; done
git -C "$CL" status --porcelain | sort | sed 's/^/     status after the tests: /'
[ "$(git -C "$CL" status --porcelain | wc -l)" = 2 ] && ok "H9 the tests left exactly the two applied files modified" || bad "H9 the tests changed other files"

echo "--- I. undo, re-apply, and the apply.sh states"
expect_exit "I1 undo" 0 bash "$ACT/apply.sh" undo
i=0; for r in "${RELS[@]}"; do
  cmp -s "$CL/$r" "$ACT/before/repo/$r" && [ "$(stat -c %a "$CL/$r")" = "${MODES[$i]}" ] && ok "I2.$i $r is the original, byte for byte, mode kept" || bad "I2.$i undo differs: $r"
  i=$((i + 1))
done
git -C "$CL" status --porcelain | grep -c . | grep -qx 0 && ok "I3 the clone is clean after the undo" || bad "I3 the clone is not clean"
portab "I4 adapter-portability after the undo: no findings" 0
expect_exit "I5 check: state before" 0 bash "$ACT/apply.sh" check
expect_exit "I6 apply again" 0 bash "$ACT/apply.sh" apply
expect_exit "I7 verify" 0 bash "$ACT/apply.sh" verify
portab "I8 adapter-portability after the re-apply: no findings" 0
run_check 1 0 6
run_check 3 0 8
expect_exit "I9 undo, the hook file still in place" 0 bash "$ACT/apply.sh" undo
R0=${RELS[0]}; R1=${RELS[1]}
printf '\n' >> "$CL/$R0"
expect_exit "I10 check refuses a file that changed" 3 bash "$ACT/apply.sh" check
expect_exit "I11 apply refuses (neither before nor after)" 3 bash "$ACT/apply.sh" apply
cmp -s "$CL/$R1" "$ACT/before/repo/$R1" && ok "I12 apply wrote nothing to the other file" || bad "I12 the other file was written"
cp -p "$ACT/before/repo/$R0" "$CL/$R0"
expect_exit "I13 apply" 0 bash "$ACT/apply.sh" apply
cp -p "$ACT/before/repo/$R1" "$CL/$R1"
expect_exit "I14 a half-applied state: verify refuses" 3 bash "$ACT/apply.sh" verify
expect_exit "I15 a half-applied state: apply finishes it" 0 bash "$ACT/apply.sh" apply
expect_exit "I16 verify" 0 bash "$ACT/apply.sh" verify
cp -p "$ACT/before/repo/$R0" "$CL/$R0"
expect_exit "I17 a half-applied state: undo takes it back" 0 bash "$ACT/apply.sh" undo
git -C "$CL" status --porcelain | grep -c . | grep -qx 0 && ok "I18 the clone is back to the original" || bad "I18 not restored"
TB=$D/tmp/tampered; rm -rf "${TB:?}"; cp -r "$ACT" "$TB"; echo "# tampered" >> "$TB/after/repo/$R1"
expect_exit "I19 a tampered frozen copy: apply refuses (4)" 4 bash "$TB/apply.sh" apply
cmp -s "$CL/$R0" "$ACT/before/repo/$R0" && ok "I20 nothing was written" || bad "I20 a file was written"
rm -rf "${TB:?}"
mv "$CL/$R1" "$CL/$R1.away"
expect_exit "I21 a missing file: apply refuses" 3 bash "$ACT/apply.sh" apply
[ ! -e "$CL/$R1" ] && ok "I22 nothing was created in its place" || bad "I22 a file was created"
mv "$CL/$R1.away" "$CL/$R1"
mv "$CL/$R1" "$CL/$R1.real"; ln -s "$CL/$R1.real" "$CL/$R1"
expect_exit "I23 a link: apply refuses" 3 bash "$ACT/apply.sh" apply
rm -f "${CL:?}/$R1"; mv "$CL/$R1.real" "$CL/$R1"
git -C "$CL" status --porcelain | grep -c . | grep -qx 0 && ok "I24 the clone is clean again" || bad "I24 not clean"

echo "--- J. the other ACTs of the night, the live files, the class"
python3 -I - "$ACT/list.txt" <<'PYEOF'
import fnmatch, sys
mine = [l.split("|")[1] for l in open(sys.argv[1]).read().split("\n") if l]
theirs = ["governance/project/orchestration/tools/dispatch/launch_now.sh", "governance/project/orchestration/tools/dispatch/dispatcher.py",
          "governance/project/orchestration/tools/dispatch/balancer.py", "tests/unit/orchestration/test_dispatcher.py",
          "tests/unit/orchestration/test_balancer.py", "governance/project/orchestration/tools/stop_idle_check.py",
          "tests/unit/orchestration/test_stop_idle_check.py", ".claude/templates/role-*.md", ".rulesync/subagents/*.md",
          ".claude/agents/*.md", ".claude/skills/**"]
hits = [m for m in mine if any(fnmatch.fnmatch(m, t) for t in theirs)]
print("     mine:", mine); print("     clashes:", hits or "none")
sys.exit(1 if hits else 0)
PYEOF
[ "$?" = 0 ] && ok "J1 the bundle touches none of the other ACTs' files (ACT A, DISPATCH-1, IDLE-GUARD-2, CLAUDE-COPIES-4)" || bad "J1 the bundle touches a file another ACT of the night touches"
i=0; while IFS='|' read -r root path before after; do
  [ "$(sha "$MAIN/$path")" = "$before" ] && ok "J2.$i the main tree's $path is unchanged" || bad "J2.$i the main tree's file changed: $path"
  i=$((i + 1))
done < "$ACT/list.txt"
[ -z "$(ls -A "$PH")" ] && ok "J3 the planted HOME is empty" || bad "J3 the planted HOME holds files"
V=$(cd "$D/tmp" && penv python3 -I "$D/tools/class_vote.py" "$ACT" 2 "$D/tmp/vote")
[ "$V" = b ] && ok "J4 the operator's own classifier (act_class.py, read only) votes b for the bundle (settings row and .rulesync/**, control paths)" || bad "J4 the vote is $V"

echo
[ "$FAILS" = 0 ] && echo "REHEARSAL PASS" || echo "REHEARSAL FAIL"
echo "failures: $FAILS"
