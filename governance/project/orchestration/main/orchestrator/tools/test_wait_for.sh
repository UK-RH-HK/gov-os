#!/usr/bin/env bash
# Tests for wait_for.sh (TPL-3b): it waits on a file, bounded at 570 s; a pid file is asked of proc.sh by pid only.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
T=$HERE/wait_for.sh
W=$(mktemp -d "${TMPDIR:-/tmp}/gov-os-test-wait-for.XXXXXX")
fails=0
ok() { echo "ok   $1"; }
no() { echo "FAIL $1"; fails=$((fails+1)); }
check() { if eval "$2"; then ok "$1"; else no "$1"; fi; }

# 1. usage
bash "$T" > /dev/null 2>&1; check "no exit file named: exit 2" '[ $? = 2 ]'
bash "$T" "$W/x.exit" soon > /dev/null 2>&1; check "a <max-s> that is no number: exit 2" '[ $? = 2 ]'

# 2. a finished job: its code, its log's tail, its summary
printf 'line one\nline two\nthe last line\n' > "$W/a.log"; echo 0 > "$W/a.exit"; echo "all green" > "$W/a.summary"
out=$(bash "$T" "$W/a.exit" 5); rc=$?
check "done job: exit 0" '[ $rc = 0 ]'
check "done job: DONE and the code printed" 'grep -q "DONE exit 0" <<< "$out"'
check "done job: the log's tail printed" 'grep -q "the last line" <<< "$out"'
check "done job: the summary printed" 'grep -q "all green" <<< "$out"'
echo 3 > "$W/b.exit"; echo "red" > "$W/b.txt"
bash "$T" "$W/b.exit" 5 > /dev/null; check "the job's own code is the exit code (3)" '[ $? = 3 ]'

# 3. a claude -p JSON log after launcher lines: the result's end and the session id
{ echo "gov launch: a launcher line"; echo '{"type":"result","is_error":false,"num_turns":4,"session_id":"sess-42","result":"task: x\nstatus: DONE"}'; } > "$W/c.json"
echo 0 > "$W/c.exit"
out=$(bash "$T" "$W/c.exit" 5)
check "JSON log: the session id" 'grep -q "session_id=sess-42" <<< "$out"'
check "JSON log: the result text" 'grep -q "status: DONE" <<< "$out"'
WAIT_FOR_LOG="$W/a.log" bash "$T" "$W/c.exit" 5 | grep -q "the last line"; check "WAIT_FOR_LOG names the log" '[ $? = 0 ]'

# 4. bounded: no exit file and no pid file: RUNNING at max-s, exit 124
s=$(date +%s); out=$(WAIT_FOR_EVERY=1 bash "$T" "$W/none.exit" 2); rc=$?; e=$(( $(date +%s) - s ))
check "still running: exit 124" '[ $rc = 124 ]'
check "still running: RUNNING printed" 'grep -q RUNNING <<< "$out"'
check "still running: bounded by max-s (${e}s <= 4)" '[ $e -le 4 ]'
err=$(bash "$T" "$W/a.exit" 9999 2>&1 >/dev/null; WAIT_FOR_EVERY=1 bash "$T" "$W/none.exit" 0)
check "max-s above 570 is capped at 570" 'grep -q "9999 capped at 570" <<< "$err"'
check "max-s 0 returns at once" 'grep -q "RUNNING after 0s" <<< "$err"'
grep -q '^CAP=570$' "$T"; check "the ceiling is 570 s" '[ $? = 0 ]'

# 5. a job that ends while waited for
( sleep 2; echo "late log" > "$W/d.log"; echo 5 > "$W/d.exit.tmp"; mv "$W/d.exit.tmp" "$W/d.exit" ) &
s=$(date +%s); out=$(WAIT_FOR_EVERY=1 bash "$T" "$W/d.exit" 30); rc=$?; e=$(( $(date +%s) - s ))
check "a job ending during the wait: its code (5)" '[ $rc = 5 ]'
check "a job ending during the wait: returns soon after (${e}s <= 6)" '[ $e -le 6 ]'
wait

# 6. a pid file: a dead job with no exit file is GONE at once; a live one is waited for, by its pid only
bash -c 'exit 0' & dead=$!; wait $dead
echo "$dead" > "$W/e.pid"; echo "partial" > "$W/e.log"
s=$(date +%s); out=$(WAIT_FOR_EVERY=1 bash "$T" "$W/e.exit" 60); rc=$?; e=$(( $(date +%s) - s ))
check "a dead job without its exit file: exit 125" '[ $rc = 125 ]'
check "a dead job: GONE printed at once (${e}s <= 5)" '[ $e -le 5 ] && grep -q GONE <<< "$out"'
setsid sleep 60 < /dev/null > /dev/null 2>&1 & live=$!
echo "$live" > "$W/f.pid"
WAIT_FOR_EVERY=1 bash "$T" "$W/f.exit" 2 > /dev/null; rc=$?
check "a live job: still waited for, exit 124 at max-s" '[ $rc = 124 ]'
bash "$HERE/proc.sh" stop --grace 2 "$live" > /dev/null
WAIT_FOR_EVERY=1 bash "$T" "$W/f.exit" 10 > /dev/null; rc=$?
check "the same job once stopped: exit 125" '[ $rc = 125 ]'

# 7. an exit file with no number
echo "oops" > "$W/g.exit"; bash "$T" "$W/g.exit" 2 > /dev/null; check "an exit file with no number: exit 2" '[ $? = 2 ]'

# 8. never a name match
! grep -Eq '(^|[^a-z_])(pgrep|pkill|killall|pidof)([^a-z_]|$)' "$T"; check "no pgrep, pkill, killall or pidof in wait_for.sh" '[ $? = 0 ]'

rm -rf "$W"
echo "$([ $fails = 0 ] && echo PASS || echo "FAILED $fails") test_wait_for.sh"
[ $fails = 0 ]
