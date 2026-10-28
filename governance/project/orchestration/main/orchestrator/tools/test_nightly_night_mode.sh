#!/bin/bash
# Tests nightly.sh's night mode (owner, standing, DEC-933) on a copy: its orchestrator folder, repository, run folder
# and ping are temporary or fake, its 05:00 is the test's, and its estimate comes from a stub. Each case stops before
# the clone (the copy's folder has no disk gate), so no test run starts.
real=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/nightly.sh
work=$(mktemp -d)
mkdir -p "$work/orch/tools" "$work/runs" "$work/repo"
git -C "$work/repo" init -q -b w2/integrate
GIT_COMMITTER_DATE="2026-10-01T00:00:00" git -C "$work/repo" -c user.name=t -c user.email=t@t commit -q --allow-empty -m old
sed -e "s#^ORCH=.*#ORCH=$work/orch#" -e "s#^REPO=.*#REPO=$work/repo#" -e "s#^RUNS=.*#RUNS=$work/runs#" \
    -e "s#^JUNIT=.*#JUNIT=$work/junit#" -e "s#^PING=.*#PING=$work/ping#" \
    -e 's#^  window_end=.*#  window_end=$TEST_WINDOW_END#' "$real" > "$work/nightly.sh"
printf '#!/bin/bash\necho "$*" >> %s/pings.txt\n' "$work" > "$work/ping"; chmod +x "$work/ping"
printf 'import os\nprint(\x27{"estimate_s": \x27 + os.environ["FAKE_EST"] + \x27}\x27)\n' > "$work/orch/tools/nightly_estimate.py"
fails=0
run() {  # $1 = case name, $2 = seconds to the latest start (window end = now + estimate + $2), $3 = estimate
  rm -f "$work/pings.txt"
  local now; now=$(date +%s)
  FAKE_EST=$3 TEST_WINDOW_END=$((now + $3 + $2)) timeout 200 bash "$work/nightly.sh" night > /dev/null 2>&1
  code=$?; took=$(( $(date +%s) - now ))
  last=$(cat "$work/orch/log/nightly/"*/run.txt 2>/dev/null | tail -1); rm -rf "$work/orch/log"
}
expect() {  # $1 case, $2 text expected in the last line of run.txt, $3 ping expected
  [ "$code" -eq 2 ] || { echo "FAIL $1: exit $code"; fails=1; }
  echo "$last" | grep -q "$2" || { echo "FAIL $1: last line '$last'"; fails=1; }
  grep -q "$3" "$work/pings.txt" 2>/dev/null || { echo "FAIL $1: no ping '$3'"; fails=1; }
}
touch "$work/orch/NIGHTLY-RUNNING"
run A 600 600; expect A "another nightly holds" "P1 NIGHTLY-NOT-RUN"
rm -f "$work/orch/NIGHTLY-RUNNING"
rm -f "$work/pings.txt"; now=$(date +%s)
FAKE_EST=600 TEST_WINDOW_END=$((now - 10)) timeout 30 bash "$work/nightly.sh" night > /dev/null 2>&1; code=$?
last=$(cat "$work/orch/log/nightly/"*/run.txt | tail -1); rm -rf "$work/orch/log"
expect B "started after 05:00" "P1 NIGHTLY-NOT-RUN"
touch "$work/orch/CLOSE-RUNNING"
run C 5 600; expect C "by the latest start, a close is running" "P1 NIGHTLY-NOT-RUN"
[ "$took" -ge 55 ] || { echo "FAIL C: it did not wait for the close ($took s)"; fails=1; }
rm -f "$work/orch/CLOSE-RUNNING"
touch "$work/repo/.git/MERGE_HEAD"
run D 5 600; expect D "a merge is in progress" "P1 NIGHTLY-NOT-RUN"
rm -f "$work/repo/.git/MERGE_HEAD"
touch "$work/repo/dirty.txt"
run E 5 600; expect E "the main tree is not clean" "P1 NIGHTLY-NOT-RUN"
rm -f "$work/repo/dirty.txt"
git -C "$work/repo" -c user.name=t -c user.email=t@t commit -q --allow-empty -m new
run F 5 600; expect F "head is under 5 minutes old" "P1 NIGHTLY-NOT-RUN"
git -C "$work/repo" -c user.name=t -c user.email=t@t reset -q --hard HEAD~1
# G: clean, and the estimate does not fit: a package ping, not cut, then it goes on (here to the missing disk gate)
run G -99400 100000; expect G "NOT STARTED: .*disk" "P2 NIGHTLY-WINDOW"
grep -q "P1 NIGHTLY-NOT-RUN" "$work/pings.txt" || { echo "FAIL G: the failed start did not ping P1"; fails=1; }
[ "$took" -lt 30 ] || { echo "FAIL G: a clean state waited ($took s)"; fails=1; }
# H: by day it waits for a quiet machine and never pings
rm -f "$work/pings.txt"
timeout 5 bash "$work/nightly.sh" > /dev/null 2>&1; code=$?
[ "$code" -eq 124 ] && [ ! -e "$work/pings.txt" ] || { echo "FAIL H: exit $code or a day ping"; fails=1; }
[ ! -e "$work/orch/NIGHTLY-RUNNING" ] || { echo "FAIL: NIGHTLY-RUNNING left behind"; fails=1; }
rm -rf "$work"
[ "$fails" -eq 0 ] && echo "PASS: A lock, B after 05:00, C close, D merge, E dirty tree, F young head, G window package, H day"
exit "$fails"
