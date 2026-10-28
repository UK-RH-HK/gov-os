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
expect "N2 after 05:00" "started after 05:00" "P1 NIGHTLY-NOT-RUN"
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

# ---- nightly_check.sh: ran, failed, missed, before 05:00, once a night ------------------------------------------
check() { NIGHTLY_ORCH=$work/orch NIGHTLY_PING=$work/ping NIGHTLY_DAY=20261029 NIGHTLY_NOW_HM=$1 bash "$HERE/nightly_check.sh" > /dev/null; }
S=$work/orch/log/nightly/status.txt
check 0430; [ ! -e "$S" ] || fail "K1: checked before 05:00"
check 0530; grep -q "^2026-10-29 MISSED" "$S" || fail "K2: no MISSED line"
grep -q "P1 NIGHTLY-MISSED 2026-10-29" "$work/pings.txt" || fail "K2: no P1 ping"
rm -f "$work/pings.txt"; check 0900; [ "$(grep -c '^2026-10-29' "$S")" -eq 1 ] || fail "K3: checked twice"
[ ! -e "$work/pings.txt" ] || fail "K3: pinged twice"
rm -f "$S"; mkdir -p "$work/orch/log/nightly/20261029-0200"
printf 'x nightly night: estimate {}\nhead abc\nclone failed\n' > "$work/orch/log/nightly/20261029-0200/run.txt"
check 0530; grep -q "^2026-10-29 FAILED | clone failed" "$S" || fail "K4: no FAILED line"
rm -f "$S" "$work/pings.txt"
printf 'x nightly night: estimate {}\nhead abc\nverdict: green\nduration: estimate 5000 s, actual 4800 s\n' > "$work/orch/log/nightly/20261029-0200/run.txt"
check 0530; grep -q "^2026-10-29 ran | verdict: green duration: estimate 5000 s, actual 4800 s" "$S" || fail "K5: no ran line: $(cat "$S")"
[ ! -e "$work/pings.txt" ] || fail "K5: a green night pinged"
rm -f "$S"; printf 'x nightly day: quiet\nverdict: green\n' > "$work/orch/log/nightly/20261029-0200/run.txt"
check 0530; grep -q "^2026-10-29 MISSED" "$S" || fail "K6: a day run counted as the night's"

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
[ "$fails" -eq 0 ] && echo "PASS: nightly.sh N1-N8, nightly_cron.sh C1-C3, nightly_check.sh K1-K6, rotate.sh R1-R3"
exit "$fails"
