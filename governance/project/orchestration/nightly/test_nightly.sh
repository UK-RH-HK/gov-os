#!/bin/bash
# The nightly's tests (DEC-933 item 2, DEC-934). Every case runs a copy of a script against a temporary repository,
# orchestrator folder and fake ping; none starts a test run, touches the real logs or pings the owner.
#   bash governance/project/orchestration/nightly/test_nightly.sh
HERE=$(cd "$(dirname "$0")" && pwd)
work=$(mktemp -d)
fails=0
fail() { echo "FAIL $1"; fails=1; }
mkdir -p "$work/orch/log/nightly" "$work/runs" "$work/repo"
printf '#!/bin/bash\necho "$*" >> %s/pings.txt\n' "$work" > "$work/ping"; chmod +x "$work/ping"
git -C "$work/repo" init -q -b w2/integrate
GIT_COMMITTER_DATE="2026-10-01T00:00:00" git -C "$work/repo" -c user.name=t -c user.email=t@t commit -q --allow-empty -m old

# ---- nightly.sh night: the start conditions --------------------------------------------------------------------
mkdir -p "$work/n"
sed -e "s#^HERE=.*#HERE=$work/n#" -e "s#^ORCH=.*#ORCH=$work/orch#" -e "s#^REPO=.*#REPO=$work/repo#" \
    -e "s#^RUNS=.*#RUNS=$work/runs#" -e "s#^JUNIT=.*#JUNIT=$work/junit#" -e "s#^PING=.*#PING=$work/ping#" \
    -e 's#^  window_end=.*#  window_end=$TEST_WINDOW_END#' "$HERE/nightly.sh" > "$work/n/nightly.sh"
printf 'import os\nprint(\x27{"estimate_s": \x27 + os.environ["FAKE_EST"] + \x27}\x27)\n' > "$work/n/nightly_estimate.py"
# no disk_gate.sh in the copy's folder: a clean start stops there, before any clone
run() {  # $1 seconds to the latest start, $2 estimate
  rm -f "$work/pings.txt"; local now; now=$(date +%s)
  FAKE_EST=$2 TEST_WINDOW_END=$((now + $2 + $1)) timeout 200 bash "$work/n/nightly.sh" night > /dev/null 2>&1
  code=$?; took=$(( $(date +%s) - now ))
  last=$(cat "$work/orch/log/nightly/"20*/run.txt 2>/dev/null | tail -1); rm -rf "$work/orch/log/nightly/"20*
}
expect() {  # $1 case, $2 text in run.txt's last line, $3 ping
  [ "$code" -eq 2 ] || fail "$1: exit $code"
  echo "$last" | grep -q "$2" || fail "$1: last line '$last'"
  grep -q "$3" "$work/pings.txt" 2>/dev/null || fail "$1: no ping '$3'"
}
touch "$work/orch/NIGHTLY-RUNNING"; run 600 600; expect "N1 lock held" "another nightly holds" "P1 NIGHTLY-NOT-RUN"
rm -f "$work/orch/NIGHTLY-RUNNING"
rm -f "$work/pings.txt"; FAKE_EST=600 TEST_WINDOW_END=$(( $(date +%s) - 10 )) timeout 30 bash "$work/n/nightly.sh" night > /dev/null 2>&1; code=$?
last=$(cat "$work/orch/log/nightly/"20*/run.txt | tail -1); rm -rf "$work/orch/log/nightly/"20*
expect "N2 after 08:00" "started after 08:00" "P1 NIGHTLY-NOT-RUN"
touch "$work/orch/CLOSE-RUNNING"; run 5 600; expect "N3 close running" "by the latest start, a close is running" "P1 NIGHTLY-NOT-RUN"
[ "$took" -ge 55 ] || fail "N3: it did not wait for the close ($took s)"
rm -f "$work/orch/CLOSE-RUNNING"
touch "$work/repo/.git/MERGE_HEAD"; run 5 600; expect "N4 merge" "a merge is in progress" "P1 NIGHTLY-NOT-RUN"
rm -f "$work/repo/.git/MERGE_HEAD"
touch "$work/repo/dirty.txt"; run 5 600; expect "N5 dirty tree" "the main tree is not clean" "P1 NIGHTLY-NOT-RUN"
rm -f "$work/repo/dirty.txt"
git -C "$work/repo" -c user.name=t -c user.email=t@t commit -q --allow-empty -m new
run 5 600; expect "N6 young head" "head is under 5 minutes old" "P1 NIGHTLY-NOT-RUN"
git -C "$work/repo" reset -q --hard HEAD~1
run -99400 100000; expect "N7 window" "NOT STARTED: .*disk" "P2 NIGHTLY-WINDOW"
grep -q "P1 NIGHTLY-NOT-RUN" "$work/pings.txt" || fail "N7: the failed start did not ping P1"
[ "$took" -lt 30 ] || fail "N7: a clean state waited ($took s)"
[ ! -e "$work/orch/NIGHTLY-RUNNING" ] || fail "N: NIGHTLY-RUNNING left behind"
rm -f "$work/pings.txt"; timeout 5 bash "$work/n/nightly.sh" > /dev/null 2>&1; code=$?
[ "$code" -eq 124 ] && [ ! -e "$work/pings.txt" ] || fail "N8 day: exit $code or a ping"

# N9 (DEC-973, the review): the harness replaces the window line, so the real one is checked here
grep -q 'window_end=$(date -d "today 08:00" +%s)' "$HERE/nightly.sh" || fail "N9: the night window does not end at 08:00"
grep -q 'EST=14400;' "$HERE/nightly.sh" || fail "N9: the no-history estimate is not the whole 04:00-08:00 window"

# ---- nightly.sh: the rebuild scans in full (DEC-966 item 4, W2-107); the suites do not get the setting ---------------
rb=$(grep -n 'gov.cli.main rebuild' "$HERE/nightly.sh")
[ "$(echo "$rb" | grep -c .)" -eq 1 ] || fail "N10: not exactly one rebuild line in nightly.sh"
echo "$rb" | grep -q 'GOV_SECRETS_FULL_SCAN=1 ' || fail "N10: the rebuild line does not set GOV_SECRETS_FULL_SCAN=1"
grep -v 'gov.cli.main rebuild' "$HERE/nightly.sh" | grep -v '^ *#' | grep -q 'GOV_SECRETS_FULL_SCAN' && fail "N11: GOV_SECRETS_FULL_SCAN set outside the rebuild line"

# ---- nightly.sh: the nightly takes all the heavy-job slots while its suites run (DEC-984) ------------------------
sb="$work/slots"; mkdir -p "$sb/dir"
sed -n '/^SLOT_DIR=\${NIGHTLY_SLOT_DIR/,/^setup=/p' "$HERE/nightly.sh" | sed '$d' > "$sb/block.sh"
grep -q 'flock -w' "$sb/block.sh" && grep -q '^noslot()' "$sb/block.sh" || fail "N12: the slot block was not found"
# one slot is busy for 3 s: the block waits for it and then holds all three
flock "$sb/dir/gov-os-heavy-slot-2.lock" sleep 3 & busy=$!
sleep 0.5
printf '%s\n' 'OUT=$1; mkdir -p "$OUT"; MODE=night; latest=$(( $(date +%s) + 30 )); lock_wait=0; NIGHTLY_SLOT_DIR=$2' \
  ". $sb/block.sh" \
  'for i in 1 2 3; do flock -n "$NIGHTLY_SLOT_DIR/gov-os-heavy-slot-$i.lock" true && echo "free $i" >> "$OUT/probe"; done' \
  '( noslot bash -c "ls -l /proc/self/fd" ) > "$OUT/fds" 2>&1' > "$sb/run.sh"
bash "$sb/run.sh" "$sb/out" "$sb/dir"; wait $busy
grep -q "heavy-job slots held: 3 of 3" "$sb/out/run.txt" || fail "N12: not all three slots held: $(cat "$sb/out/run.txt" 2>/dev/null)"
[ ! -s "$sb/out/probe" ] || fail "N12: a slot was free while the nightly held them: $(cat "$sb/out/probe")"
grep -q "heavy-slot" "$sb/out/fds" && fail "N13: a run inherits a slot's lock"
# after the block's script ends, every slot is free again
for i in 1 2 3; do flock -n "$sb/dir/gov-os-heavy-slot-$i.lock" true || fail "N13: slot $i still held after the nightly ended"; done
grep -q 'eval "exec \$f>&-"; done' "$HERE/nightly.sh" && grep -q "heavy-job slots released after the suites" "$HERE/nightly.sh" || fail "N14: the slots are not released after the suites"
# N15: a lock folder that cannot be written: the nightly runs without the slots, says so, and its output is intact
mkdir -p "$sb/ro"; chmod 555 "$sb/ro"
printf '%s\n' 'OUT=$1; mkdir -p "$OUT"; MODE=night; latest=$(( $(date +%s) + 30 )); lock_wait=0; NIGHTLY_SLOT_DIR=$2' \
  ". $sb/block.sh" '( noslot echo still-writes ) > "$OUT/stdout" 2>&1' > "$sb/run_ro.sh"
bash "$sb/run_ro.sh" "$sb/out_ro" "$sb/ro"
grep -q "heavy-job slots held: 0 of 3" "$sb/out_ro/run.txt" || fail "N15: $(cat "$sb/out_ro/run.txt" 2>/dev/null)"
grep -q still-writes "$sb/out_ro/stdout" || fail "N15: a run's output was lost"
chmod 755 "$sb/ro"
# N16: a slot that never frees: the wait stops at its cap, the nightly goes on with the slots it has
flock "$sb/dir/gov-os-heavy-slot-1.lock" sleep 20 & busy=$!
sleep 0.5; t0=$(date +%s)
NIGHTLY_SLOT_WAIT=3 bash "$sb/run.sh" "$sb/out_cap" "$sb/dir"; t=$(( $(date +%s) - t0 ))
kill $busy 2>/dev/null; wait $busy 2>/dev/null
grep -q "heavy-job slots held: 2 of 3" "$sb/out_cap/run.txt" || fail "N16: $(cat "$sb/out_cap/run.txt" 2>/dev/null)"
[ "$t" -le 10 ] || fail "N16: the wait ran $t s past its 3 s cap"
# N17: after the block, the script's own errors still reach its log (no lasting redirect of stderr)
printf '%s\n' 'OUT=$1; mkdir -p "$OUT"; MODE=night; latest=$(( $(date +%s) + 30 )); lock_wait=0; NIGHTLY_SLOT_DIR=$2' \
  ". $sb/block.sh" 'echo err-visible >&2' > "$sb/run_err.sh"
bash "$sb/run_err.sh" "$sb/out_err" "$sb/dir" 2> "$sb/err.txt"
grep -q err-visible "$sb/err.txt" || fail "N17: stderr lost after the slot block"
bash "$sb/run_err.sh" "$sb/out_err2" "$sb/ro" 2> "$sb/err2.txt"
grep -q err-visible "$sb/err2.txt" || fail "N17: stderr lost after a failed open"
[ "$(grep -c '( noslot env' "$HERE/nightly.sh")" -eq 2 ] || fail "N14: not both suites run under noslot"

# ---- nightly_cron.sh: committed code only, a session's PATH, a log ----------------------------------------------
mkdir -p "$work/repo/governance/project/orchestration/nightly"
printf '#!/bin/bash\necho "NIGHTLY RAN $1 PATH=$PATH"\n' > "$work/repo/governance/project/orchestration/nightly/nightly.sh"
printf '#!/bin/bash\necho rotated\n' > "$work/repo/governance/project/orchestration/nightly/rotate.sh"
git -C "$work/repo" add -A && git -C "$work/repo" -c user.name=t -c user.email=t@t commit -q -m code
sed -e "s#^REPO=.*#REPO=$work/repo#" -e "s#^ORCH=.*#ORCH=$work/orch#" -e "s#^PING=.*#PING=$work/ping#" \
    "$HERE/nightly_cron.sh" > "$work/cron.sh"
log() { cat "$work/orch/log/nightly/cron/"*.log 2>/dev/null; }
rm -f "$work/pings.txt"; env -i bash "$work/cron.sh"; code=$?
[ "$code" -eq 0 ] || fail "C1 committed code: exit $code"
log | grep -q "NIGHTLY RAN night PATH=/home/usain/.local/bin:" || fail "C1: the nightly did not run with a session's PATH"
log | grep -q "rotated" || fail "C1: no rotation before the run"
[ ! -e "$work/pings.txt" ] || fail "C1: pinged"
rm -rf "$work/orch/log/nightly/cron"
echo "# changed" >> "$work/repo/governance/project/orchestration/nightly/nightly.sh"
env -i bash "$work/cron.sh"; code=$?
[ "$code" -eq 2 ] || fail "C2 changed code: exit $code"
log | grep -q "REFUSED" || fail "C2: no refusal in the log"
log | grep -q "NIGHTLY RAN" && fail "C2: the changed code ran"
grep -q "P1 NIGHTLY-NOT-RUN" "$work/pings.txt" 2>/dev/null || fail "C2: no P1 ping"
git -C "$work/repo" checkout -q -- . ; rm -rf "$work/orch/log/nightly/cron" "$work/pings.txt"
touch "$work/repo/governance/project/orchestration/nightly/extra.sh"
env -i bash "$work/cron.sh"; code=$?
[ "$code" -eq 2 ] || fail "C3 untracked file: exit $code"
rm -f "$work/repo/governance/project/orchestration/nightly/extra.sh" "$work/pings.txt"

# ---- nightly_check.sh: ran, failed, missed, before 08:00, once a night ------------------------------------------
# The owner is taken as active here (idle 0 s), so the check's pings go at once; K7 and K8 test the hold.
check() { NIGHTLY_ORCH=$work/orch NIGHTLY_PING=$work/ping NIGHTLY_IDLE_S=0 NIGHTLY_WAIT_STEP=1 NIGHTLY_DAY=20261029 NIGHTLY_NOW_HM=$1 bash "$HERE/nightly_check.sh" > /dev/null; }
S=$work/orch/log/nightly/status.txt
check 0730; [ ! -e "$S" ] || fail "K1: checked before 08:00"
check 0800; grep -q "^2026-10-29 MISSED" "$S" || fail "K2: no MISSED line"
grep -q "P1 NIGHTLY-MISSED 2026-10-29" "$work/pings.txt" || fail "K2: no P1 ping"
rm -f "$work/pings.txt"; check 1000; [ "$(grep -c '^2026-10-29' "$S")" -eq 1 ] || fail "K3: checked twice"
[ ! -e "$work/pings.txt" ] || fail "K3: pinged twice"
rm -f "$S"; mkdir -p "$work/orch/log/nightly/20261029-0400"
printf 'x nightly night: estimate {}\nhead abc\nclone failed\n' > "$work/orch/log/nightly/20261029-0400/run.txt"
check 0800; grep -q "^2026-10-29 FAILED | clone failed" "$S" || fail "K4: no FAILED line"
rm -f "$S" "$work/pings.txt"
printf 'x nightly night: estimate {}\nhead abc\nverdict: green\nduration: estimate 5000 s, actual 4800 s\n' > "$work/orch/log/nightly/20261029-0400/run.txt"
check 0800; grep -q "^2026-10-29 ran | verdict: green duration: estimate 5000 s, actual 4800 s" "$S" || fail "K5: no ran line: $(cat "$S")"
[ ! -e "$work/pings.txt" ] || fail "K5: a green night pinged"
rm -f "$S"; printf 'x nightly day: quiet\nverdict: green\n' > "$work/orch/log/nightly/20261029-0400/run.txt"
check 0800; grep -q "^2026-10-29 MISSED" "$S" || fail "K6: a day run counted as the night's"
# K7, K8 (DEC-973: the check runs at 08:00, after the quiet hours): with the owner inactive at 08:00 the line is written
# and the P1 goes at once; a P1 that nightly.sh held during the night goes out with the check, marked held
rm -f "$S" "$work/pings.txt" "$work/orch/log/nightly/pending-pings.txt"; rm -rf "$work/orch/log/nightly/20261029-0400"
NIGHTLY_ORCH=$work/orch NIGHTLY_PING=$work/ping NIGHTLY_IDLE_S=99999 NIGHTLY_WAIT_STEP=1 NIGHTLY_DAY=20261029 NIGHTLY_NOW_HM=0800 \
  timeout 10 bash "$HERE/nightly_check.sh" > /dev/null
grep -q "^2026-10-29 MISSED" "$S" || fail "K7: the line was not written at once"
grep -q "P1 NIGHTLY-MISSED 2026-10-29" "$work/pings.txt" 2>/dev/null || fail "K7: the P1 did not go at 08:00"
rm -f "$S" "$work/pings.txt"; printf '2026-10-29 04:10\tP1 NIGHTLY-RED head abc | verdict: red 1 | x\n' > "$work/orch/log/nightly/pending-pings.txt"
NIGHTLY_ORCH=$work/orch NIGHTLY_PING=$work/ping NIGHTLY_IDLE_S=99999 NIGHTLY_WAIT_STEP=1 NIGHTLY_DAY=20261029 NIGHTLY_NOW_HM=0800 \
  timeout 10 bash "$HERE/nightly_check.sh" > /dev/null
grep -q "P1 NIGHTLY-RED head abc .*(held from " "$work/pings.txt" 2>/dev/null || fail "K8: the night's held P1 did not go at 08:00"
[ ! -s "$work/orch/log/nightly/pending-pings.txt" ] || fail "K8: the held file was not emptied"
[ "$(grep -c '^2026-10-29' "$S")" -eq 1 ] || fail "K8: the night was checked twice"
# K9, K10 (DEC-971 item 6): the run still going at 08:00 (its marker written today, no verdict) is `running`, not
# FAILED; the check waits (here 2 s a step) and writes the night's final line: ran when a verdict comes (no P1),
# FAILED with a P1 when none has come by the last re-check.
R9=$work/orch/log/nightly/20261029-0400
rm -f "$S" "$work/pings.txt" "$work/orch/log/nightly/pending-pings.txt"; mkdir -p "$R9"
printf 'x nightly night: estimate {}\nhead abc\nparallel running\n' > "$R9/run.txt"
echo "2026-10-29 04:00:05 nightly: running (a marker only, DEC-961)" > "$work/orch/NIGHTLY-RUNNING"
( NIGHTLY_ORCH=$work/orch NIGHTLY_PING=$work/ping NIGHTLY_IDLE_S=0 NIGHTLY_WAIT_STEP=2 NIGHTLY_DAY=20261029 NIGHTLY_NOW_HM=0800 \
  NIGHTLY_RECHECK_AT="0830 0900" bash "$HERE/nightly_check.sh" > /dev/null ) & k9=$!
sleep 1
grep -q "^2026-10-29 running | parallel running" "$S" || fail "K9: no running line at 08:00: $(cat "$S" 2>/dev/null)"
grep -q "^2026-10-29 FAILED" "$S" && fail "K9: a running night written as FAILED"
printf 'verdict: green\nduration: estimate 5000 s, actual 9000 s\n' >> "$R9/run.txt"
wait $k9
grep -q "^2026-10-29 ran | verdict: green duration: estimate 5000 s, actual 9000 s" "$S" || fail "K9: no ran line once the verdict came: $(cat "$S")"
[ ! -e "$work/pings.txt" ] || fail "K9: a night that ended with a verdict pinged"
rm -f "$S" "$work/pings.txt"; printf 'x nightly night: estimate {}\nhead abc\nparallel running\n' > "$R9/run.txt"
NIGHTLY_ORCH=$work/orch NIGHTLY_PING=$work/ping NIGHTLY_IDLE_S=0 NIGHTLY_WAIT_STEP=1 NIGHTLY_DAY=20261029 NIGHTLY_NOW_HM=0800 \
  NIGHTLY_RECHECK_AT="0830 0900" timeout 20 bash "$HERE/nightly_check.sh" > /dev/null
grep -q "^2026-10-29 running" "$S" || fail "K10: no running line"
grep -q "^2026-10-29 FAILED | parallel running" "$S" || fail "K10: no FAILED line by 09:00: $(cat "$S")"
grep -q "P1 NIGHTLY-FAILED 2026-10-29" "$work/pings.txt" 2>/dev/null || fail "K10: no P1 for the failed night"
# K11: a stale marker (an earlier day's) does not hold a night that ended without a verdict: FAILED at once
rm -f "$S" "$work/pings.txt"; echo "2026-10-28 04:00:05 nightly: running" > "$work/orch/NIGHTLY-RUNNING"
NIGHTLY_ORCH=$work/orch NIGHTLY_PING=$work/ping NIGHTLY_IDLE_S=0 NIGHTLY_WAIT_STEP=1 NIGHTLY_DAY=20261029 NIGHTLY_NOW_HM=0800 \
  timeout 10 bash "$HERE/nightly_check.sh" > /dev/null
grep -q "^2026-10-29 FAILED" "$S" && ! grep -q "^2026-10-29 running" "$S" || fail "K11: a stale marker held the night: $(cat "$S")"
rm -f "$work/orch/NIGHTLY-RUNNING" "$S" "$work/pings.txt"
# K12 (review F1): two checks at once (the 08:00 job and @reboot) give one final line and one ping
printf 'x nightly night: estimate {}\nhead abc\nparallel running\n' > "$R9/run.txt"
echo "2026-10-29 04:00:05 nightly: running (a marker only, DEC-961)" > "$work/orch/NIGHTLY-RUNNING"
for k in 1 2; do
  ( NIGHTLY_ORCH=$work/orch NIGHTLY_PING=$work/ping NIGHTLY_IDLE_S=0 NIGHTLY_WAIT_STEP=1 NIGHTLY_DAY=20261029 NIGHTLY_NOW_HM=0800 \
    NIGHTLY_RECHECK_AT="0830 0900" timeout 20 bash "$HERE/nightly_check.sh" > /dev/null ) &
done
wait
[ "$(grep -cE '^2026-10-29 (ran|FAILED|MISSED) ' "$S")" -eq 1 ] || fail "K12: not one final line: $(cat "$S")"
[ "$(grep -c 'P1 NIGHTLY-FAILED 2026-10-29' "$work/pings.txt" 2>/dev/null)" -eq 1 ] || fail "K12: not one ping: $(cat "$work/pings.txt" 2>/dev/null)"
rm -f "$work/orch/NIGHTLY-RUNNING" "$S" "$work/pings.txt"
# K13 (review F2): an earlier night left with only a `running` line (its check was killed) is finished FAILED, with a P1
printf 'verdict: green\nduration: estimate 5000 s, actual 4000 s\n' >> "$R9/run.txt"
echo "2026-10-28 running | parallel running" > "$S"
check 0800
grep -q "^2026-10-28 FAILED | its check stopped while it waited" "$S" || fail "K13: the earlier running night was not finished: $(cat "$S")"
grep -q "P1 NIGHTLY-FAILED 2026-10-28" "$work/pings.txt" 2>/dev/null || fail "K13: no P1 for the earlier night"
grep -q "^2026-10-29 ran" "$S" || fail "K13: this night not checked: $(cat "$S")"
rm -f "$S" "$work/pings.txt"
# K14 (review W1): an earlier running-only night whose run reached a verdict after its check died is `ran`, no P1
R8=$work/orch/log/nightly/20261028-0400; mkdir -p "$R8"
printf 'x nightly night: estimate {}\nhead def\nverdict: green\nduration: estimate 5000 s, actual 4100 s\n' > "$R8/run.txt"
echo "2026-10-28 running | parallel running" > "$S"
check 0800
grep -q "^2026-10-28 ran | verdict: green" "$S" || fail "K14: the green earlier night was not written ran: $(cat "$S")"
grep -q "P1 NIGHTLY-FAILED 2026-10-28" "$work/pings.txt" 2>/dev/null && fail "K14: a P1 for a green night"
rm -rf "$R8"; rm -f "$S" "$work/pings.txt"
# K15 (review F3): the marker removed mid-wait with no verdict (the run died) is FAILED at once, not at 09:00
printf 'x nightly night: estimate {}\nhead abc\nparallel running\n' > "$R9/run.txt"
echo "2026-10-29 04:00:05 nightly: running (a marker only, DEC-961)" > "$work/orch/NIGHTLY-RUNNING"
( NIGHTLY_ORCH=$work/orch NIGHTLY_PING=$work/ping NIGHTLY_IDLE_S=0 NIGHTLY_WAIT_STEP=3 NIGHTLY_DAY=20261029 NIGHTLY_NOW_HM=0800 \
  NIGHTLY_RECHECK_AT="0830 0845 0900" bash "$HERE/nightly_check.sh" > /dev/null ) & k15=$!
sleep 1; rm -f "$work/orch/NIGHTLY-RUNNING"; t15=$(date +%s); wait $k15
[ $(( $(date +%s) - t15 )) -lt 10 ] || fail "K15: the check kept waiting after the marker went"
grep -q "^2026-10-29 FAILED" "$S" || fail "K15: no FAILED line: $(cat "$S")"
rm -f "$S" "$work/pings.txt"; rm -rf "$R9"
# K16 (DEC-973, the review's folder edges): the night's run folder is one started 03:55-07:59
for edge in 0354:MISSED 0355:ran 0759:ran 0800:MISSED; do
  stamp=${edge%%:*}; want=${edge##*:}; RE=$work/orch/log/nightly/20261029-$stamp
  rm -f "$S" "$work/pings.txt"; mkdir -p "$RE"
  printf 'x nightly night: estimate {}\nhead abc\nverdict: green\nduration: estimate 5000 s, actual 4800 s\n' > "$RE/run.txt"
  check 0800
  grep -q "^2026-10-29 $want " "$S" || fail "K16: a folder stamped $stamp gave not '$want': $(cat "$S")"
  rm -rf "$RE"
done
rm -f "$S" "$work/pings.txt"
# K17 (the review's catch-up edges): an earlier running-only night is judged from its own night run folder (03:55-07:59,
# its first line "nightly night:"); a folder outside the hours, or a day run, is not the night's
for edge in 0354:FAILED 0759:ran 0430day:FAILED; do
  stamp=${edge%%:*}; want=${edge##*:}; RE=$work/orch/log/nightly/20261028-${stamp%day}
  rm -f "$S" "$work/pings.txt"; mkdir -p "$RE"
  if [ "$stamp" = 0430day ]; then first='x nightly day: quiet'; else first='x nightly night: estimate {}'; fi
  printf '%s\nhead def\nverdict: green\nduration: estimate 5000 s, actual 4100 s\n' "$first" > "$RE/run.txt"
  echo "2026-10-28 running | parallel running" > "$S"
  check 0800
  grep -q "^2026-10-28 $want " "$S" || fail "K17: the earlier night with a folder $stamp gave not '$want': $(cat "$S")"
  if [ "$want" = FAILED ]; then grep -q "P1 NIGHTLY-FAILED 2026-10-28" "$work/pings.txt" 2>/dev/null || fail "K17: no P1 for $stamp"
  else grep -q "P1 NIGHTLY-FAILED 2026-10-28" "$work/pings.txt" 2>/dev/null && fail "K17: a P1 for a green night ($stamp)"; fi
  rm -rf "$RE"
done
rm -f "$S" "$work/pings.txt"

# ---- ping_gate.sh: at once by day or when active; held at night; flushed, marked held ----------------------------
gate() { NIGHTLY_ORCH=$work/g NIGHTLY_PING=$work/ping NIGHTLY_WAIT_STEP=1 "$@"; }
P=$work/g/log/nightly/pending-pings.txt
rm -f "$work/pings.txt"
gate env NIGHTLY_NOW_HM=0900 NIGHTLY_IDLE_S=99999 bash "$HERE/ping_gate.sh" "G1 day"
grep -q "^G1 day$" "$work/pings.txt" || fail "G1: a daytime ping was held"
gate env NIGHTLY_NOW_HM=0100 NIGHTLY_IDLE_S=99999 bash "$HERE/ping_gate.sh" "G7 before quiet hours"
grep -q "^G7 before quiet hours$" "$work/pings.txt" || fail "G7: a ping at 01:00 (before the quiet hours, DEC-973) was held"
gate env NIGHTLY_NOW_HM=0300 NIGHTLY_IDLE_S=10 bash "$HERE/ping_gate.sh" "G2 active"
grep -q "^G2 active$" "$work/pings.txt" || fail "G2: an active owner's ping was held"
gate env NIGHTLY_NOW_HM=0300 NIGHTLY_IDLE_S=99999 bash "$HERE/ping_gate.sh" "G3 asleep"
grep -q "G3 asleep" "$work/pings.txt" && fail "G3: pinged at 03:00 with the owner inactive"
grep -q "G3 asleep" "$P" || fail "G3: not held"
gate env NIGHTLY_NOW_HM=0300 NIGHTLY_IDLE_S= bash "$HERE/ping_gate.sh" "G4 unreadable"
grep -q "G4 unreadable" "$P" || fail "G4: an unreadable idle time did not hold the ping"
gate env NIGHTLY_NOW_HM=0400 NIGHTLY_IDLE_S=99999 timeout 3 bash "$HERE/ping_gate.sh" --wait-flush; code=$?
[ "$code" -eq 124 ] && ! grep -q "G3 asleep" "$work/pings.txt" || fail "G5: --wait-flush did not wait at 04:00 ($code)"
gate env NIGHTLY_NOW_HM=0730 NIGHTLY_IDLE_S=99999 timeout 5 bash "$HERE/ping_gate.sh" --wait-flush
grep -q "^G3 asleep (held from " "$work/pings.txt" && grep -q "^G4 unreadable (held from " "$work/pings.txt" || fail "G6: not flushed at 07:30"
[ ! -s "$P" ] || fail "G6: the held file was not emptied"
# G8-G11 (DEC-973, the review's edges): the quiet hours are 02:00 to 07:30, the owner inactive
rm -f "$work/pings.txt" "$P"
for edge in 0159:once 0200:held 0729:held 0730:once; do
  hm=${edge%%:*}; want=${edge##*:}
  gate env NIGHTLY_NOW_HM=$hm NIGHTLY_IDLE_S=99999 bash "$HERE/ping_gate.sh" "G-edge $hm"
  if [ "$want" = once ]; then grep -q "^G-edge $hm$" "$work/pings.txt" 2>/dev/null || fail "G8-G11: a ping at $hm was held"
  else grep -q "G-edge $hm" "$work/pings.txt" 2>/dev/null && fail "G8-G11: a ping at $hm went at once"
       grep -q "G-edge $hm" "$P" || fail "G8-G11: a ping at $hm was not held"; fi
done
rm -f "$work/pings.txt" "$P"

# ---- nightly_estimate.py: the lock wait recorded apart, and never setup ---------------------------------------------
X=$work/est; mkdir -p "$X/orch/log/nightly"
sed -e "s#^ORCH = .*#ORCH = __import__('pathlib').Path('$X/orch')#" "$HERE/nightly_estimate.py" > "$X/est.py"
printf '<testsuite time="1000"><testcase time="6000"/><testcase time="2000"/></testsuite>' > "$X/p.xml"
printf '<testsuite time="300"><testcase time="300"/></testsuite>' > "$X/s.xml"
python3 "$X/est.py" record "$X/p.xml" "$X/s.xml" 1500 4000 5000 > /dev/null
python3 "$X/est.py" record "$X/p.xml" "$X/s.xml" 600 3000 5000 900 > /dev/null
grep -q '"lock_wait_s": 900.0' "$X/orch/log/nightly/history.jsonl" || fail "E1: the lock wait was not recorded"
python3 "$X/est.py" estimate | grep -q '"setup_s": 600' || fail "E2: the estimate's setup is not the smallest recorded ($(python3 "$X/est.py" estimate))"

# ---- runs_sweep.sh: only old, unheld run clones by their stamp; a red night's kept a week; nothing else ------------
W=$work/sweep; mkdir -p "$W/runs/nightly" "$W/runs/act-runs" "$W/orch/log/nightly" "$W/runs/other"
mk() { mkdir -p "$1" && echo x > "$1/f" && touch -d "$2" "$1/f" "$1"; }
mk "$W/runs/nightly/20261020-0200" "3 days ago"           # old, green night: removed
mk "$W/runs/nightly/20261025-0200" "3 days ago"           # old, red night under 7 days: kept
mkdir -p "$W/orch/log/nightly/20261025-0200"; printf 'verdict: red 1\n' > "$W/orch/log/nightly/20261025-0200/run.txt"
mk "$W/runs/nightly/20261010-0200" "10 days ago"          # red night over 7 days: removed
mkdir -p "$W/orch/log/nightly/20261010-0200"; printf 'verdict: red 2\n' > "$W/orch/log/nightly/20261010-0200/run.txt"
mk "$W/runs/nightly/20261029-0200" "1 hour ago"           # young: kept
mk "$W/runs/act-runs/ACT-X-20261020-0052" "3 days ago"    # old ACT clone: removed
mk "$W/runs/nightly/notastamp" "3 days ago"                # not a stamp: never touched
mk "$W/runs/other/20261020-0200" "3 days ago"              # another folder: never touched
SWEEP_RUNS=$W/runs SWEEP_ORCH=$W/orch bash "$HERE/runs_sweep.sh"
[ ! -e "$W/runs/nightly/20261020-0200" ] || fail "S1: an old green night's clone was kept"
[ -e "$W/runs/nightly/20261025-0200" ] || fail "S2: a red night's clone under 7 days was removed"
[ ! -e "$W/runs/nightly/20261010-0200" ] || fail "S3: a red night's clone over 7 days was kept"
[ -e "$W/runs/nightly/20261029-0200" ] || fail "S4: a clone under 24 h was removed"
[ ! -e "$W/runs/act-runs/ACT-X-20261020-0052" ] || fail "S5: an old ACT clone was kept"
[ -e "$W/runs/nightly/notastamp" ] && [ -e "$W/runs/other/20261020-0200" ] || fail "S6: a folder outside the stamps was touched"
grep -q "removed nightly 20261020-0200" "$W/orch/log/nightly/cron/"runs-sweep-*.log || fail "S7: a removal was not logged"

# ---- rotate.sh: the newest kept, the budget held -----------------------------------------------------------------
rm -rf "$work/orch/log/nightly"; mkdir -p "$work/orch/log/nightly/cron" "$work/junit"
for i in $(seq -w 1 35); do touch -d "2026-10-01 +$i days" "$work/orch/log/nightly/cron/2026-x-$i.log"; done
for i in $(seq -w 1 5); do mkdir -p "$work/junit/2026100$i-0200"; touch -d "2026-10-0$i" "$work/junit/2026100$i-0200"; done
mkdir -p "$work/orch/log/nightly/20261001-0200" "$work/orch/log/nightly/20261002-0200"
head -c 150M /dev/zero > "$work/orch/log/nightly/20261001-0200/big"; touch -d "2026-10-01" "$work/orch/log/nightly/20261001-0200"
head -c 100M /dev/zero > "$work/orch/log/nightly/20261002-0200/big"
NIGHTLY_ORCH=$work/orch NIGHTLY_JUNIT_ROOT=$work/junit bash "$HERE/rotate.sh" > /dev/null
[ "$(ls "$work/orch/log/nightly/cron" | wc -l)" -eq 30 ] || fail "R1: cron logs not cut to 30"
[ -e "$work/orch/log/nightly/cron/2026-x-35.log" ] && [ ! -e "$work/orch/log/nightly/cron/2026-x-01.log" ] || fail "R1: not the oldest removed"
[ "$(ls "$work/junit" | wc -l)" -eq 3 ] || fail "R2: JUnit folders not cut to 3"
[ ! -e "$work/orch/log/nightly/20261001-0200" ] && [ -e "$work/orch/log/nightly/20261002-0200" ] || fail "R3: the budget did not remove the oldest run folder only"

rm -rf "$work"
[ "$fails" -eq 0 ] && echo "PASS: nightly.sh N1-N17, nightly_cron.sh C1-C3, nightly_check.sh K1-K17, ping_gate.sh G1-G11, nightly_estimate.py E1-E2, runs_sweep.sh S1-S7, rotate.sh R1-R3"
exit "$fails"
