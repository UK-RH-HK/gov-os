#!/usr/bin/env bash
# Cases for nightly_restart.sh and quiet_check.py (ACT-NIGHTLY-RESTART-1's rehearsal). Everything is planted: a fixture
# repository, a scratch orchestrator folder, a process list, slot locks, a fake meminfo. It touches no live file, no
# server and no crontab, and starts nothing outside its own temporary folder. The memory-hog cases run a real
# `systemd-run --user --scope` with a small cap (200 MB) and a planted hog of 600 MB.
#   bash test_nightly_restart.sh [<folder holding nightly_restart.sh, quiet_check.py, nightly_estimate.py>]
# Prints "ok <n>: ..." or "FAIL <n>: ..." a line, and ends with "cases: <n>" and "failures: <n>".
HERE=$(cd "$(dirname "$0")" && pwd)
SRC=${1:-$HERE}
T=$(mktemp -d "${TMPDIR:-/tmp}/nr-rehearsal.XXXXXX") || exit 2
trap 'rm -rf "$T"' EXIT
n=0; fails=0
ok() { n=$((n + 1)); echo "ok $n: $1"; }
bad() { n=$((n + 1)); fails=$((fails + 1)); echo "FAIL $n: $1"; }
check() { local what=$1; shift; if "$@" > /dev/null 2>&1; then ok "$what"; else bad "$what"; fi; }
contains() { grep -qF -- "$2" "$1" 2>/dev/null; }

# ---- the planted world
REL=governance/project/orchestration/nightly
FIX=$T/repo; ORCH=$T/orch; SLOTS=$T/slots; PROC=$T/proc.json
mkdir -p "$FIX/$REL" "$ORCH/dispatch/inbox" "$ORCH/log/nightly" "$SLOTS"
cp "$SRC/nightly_restart.sh" "$SRC/quiet_check.py" "$FIX/$REL/"
[ -f "$SRC/nightly_estimate.py" ] && cp "$SRC/nightly_estimate.py" "$FIX/$REL/"
git -C "$FIX" init -q -b w2/integrate
git -C "$FIX" -c user.name=t -c user.email=t@t add -A
GIT_COMMITTER_DATE="2020-01-01T00:00:00Z" GIT_AUTHOR_DATE="2020-01-01T00:00:00Z" git -C "$FIX" -c user.name=t -c user.email=t@t commit -q -m plant
W=$FIX/$REL/nightly_restart.sh; Q=$FIX/$REL/quiet_check.py
echo '[]' > "$PROC"
status() {  # status.json, fresh, with the given extra JSON fields
  printf '{"time": "%s", "lead_count": 0, "leads": [], "jobs": [], "land_running": false, "close_running": false, "queue_busy": false, "outside_slot": [], "pending_launches": [], "slots_held": [] %s}\n' \
    "$(date '+%F %T')" "${1:+, $1}" > "$ORCH/dispatch/status.json"
}
export NR_REPO=$FIX NR_ORCH=$ORCH NR_SLOT_DIR=$SLOTS NR_REBUILD_GLOB="$SLOTS/gov-os-rebuild*.lock" NR_OPERATOR_FREEZE=$T/none \
       NR_PROC=$PROC NR_LOAD=0.1 NR_RG_COUNT=0
status
status_lead() { status; sed -i 's/"lead_count": 0, "leads": \[\]/"lead_count": 1, "leads": ["W2-999"]/' "$ORCH/dispatch/status.json"; }
runq() { python3 -I "$Q" "$@"; }
qout() { runq "$@" 2>&1; }
reset() { rm -rf "$ORCH/CLOSE-RUNNING" "$ORCH/NIGHTLY-RUNNING" "$ORCH/MEASURE-RUNNING" "$ORCH/log/act-in-progress.txt" "$ORCH/dispatch/OFF"; status; echo '[]' > "$PROC"; }

# ---- quiet_check.py
out=$(qout); rc=$?
[ $rc -eq 0 ] && [ "$out" = quiet ] && ok "nothing planted: quiet, exit 0" || bad "nothing planted: quiet, exit 0 (got $rc: $out)"
status_lead
out=$(qout); rc=$?; [ $rc -eq 1 ] && echo "$out" | grep -q "lead(s) running" && ok "a lead in the dispatcher's status: busy, named" || bad "a lead in the status ($rc: $out)"
reset; echo '[{"cmd": "claude -p work", "cwd": "/home/usain/gov-os-worktrees/W2-999"}]' > "$PROC"
out=$(qout); rc=$?; [ $rc -eq 1 ] && echo "$out" | grep -q "a process works in /home/usain/gov-os-worktrees/W2-999" && ok "a planted lead process in a ticket worktree: busy" || bad "a lead process ($rc: $out)"
echo '[{"cmd": "bash refresh.sh", "cwd": "/home/usain/gov-os-worktrees/W2-00-store-a"}, {"cmd": "python3 x.py", "cwd": "/home/usain/gov-os-runs/W2-00/nightly/20261110-1818"}]' > "$PROC"
out=$(qout); rc=$?; [ $rc -eq 0 ] && ok "the integration store's worktree and the nightly's own clone are not 'something else'" || bad "store worktree / own clone ($rc: $out)"
echo '[{"cmd": "python3 -B -m pytest tests/unit", "cwd": "/somewhere"}]' > "$PROC"
out=$(qout); rc=$?; [ $rc -eq 1 ] && echo "$out" | grep -q "a test run" && ok "a planted pytest run: busy" || bad "pytest ($rc: $out)"
echo '[{"cmd": "grep -r pytest src", "cwd": "/somewhere"}, {"cmd": "pgrep -f pytest", "cwd": "/"}]' > "$PROC"
out=$(qout); rc=$?; [ $rc -eq 0 ] && ok "a grep that only names pytest is not a test run" || bad "grep pytest ($rc: $out)"
reset; ( exec 9> "$SLOTS/gov-os-heavy-slot-2.lock"; flock -n 9 || exit 1; exec sleep 30 ) & HOLD=$!; sleep 0.5
out=$(qout); rc=$?; [ $rc -eq 1 ] && echo "$out" | grep -q "heavy slot 2 is held" && ok "a held heavy slot: busy, named" || bad "slot held ($rc: $out)"
kill "$HOLD" 2>/dev/null; wait "$HOLD" 2>/dev/null
reset; ( exec 9> "$SLOTS/gov-os-rebuild-abc.lock"; flock -n 9 || exit 1; exec sleep 30 ) & HOLD=$!; sleep 0.5
out=$(qout); rc=$?; [ $rc -eq 1 ] && echo "$out" | grep -q "a rebuild lock is held" && ok "a held rebuild lock: busy" || bad "rebuild lock ($rc: $out)"
kill "$HOLD" 2>/dev/null; wait "$HOLD" 2>/dev/null
out=$(qout); [ $? -eq 0 ] && ok "a released slot or lock is quiet again (the probe let go)" || bad "probe let go ($out)"
for f in CLOSE-RUNNING NIGHTLY-RUNNING MEASURE-RUNNING log/act-in-progress.txt; do
  reset; : > "$ORCH/$f"; out=$(qout); rc=$?; [ $rc -eq 1 ] && ok "$f present: busy" || bad "$f ($rc: $out)"
done
reset; : > "$T/none"; out=$(qout); [ $? -eq 1 ] && ok "the operator's commit freeze present: busy" || bad "operator freeze"; rm -f "$T/none"
reset; sed -i 's/"time": "[^"]*"/"time": "2020-01-01 00:00:00"/' "$ORCH/dispatch/status.json"
out=$(qout); rc=$?; [ $rc -eq 1 ] && echo "$out" | grep -q "s old" && ok "a stale dispatcher status: busy (leads cannot be counted)" || bad "stale status ($rc: $out)"
reset; : > "$ORCH/dispatch/OFF"; out=$(qout); [ $? -eq 1 ] && echo "$out" | grep -q "OFF" && ok "the CTO's dispatch/OFF present: busy" || bad "OFF"
reset; out=$(NR_RG_COUNT=150 qout); [ $? -eq 1 ] && echo "$out" | grep -q "150 rg" && ok "150 rg processes: busy" || bad "rg ($out)"
out=$(NR_LOAD=3.4 qout); [ $? -eq 1 ] && echo "$out" | grep -q "load 3.4" && ok "load 3.4: busy" || bad "load"
out=$(NR_LOAD=3.4 qout --no-load); [ $? -eq 0 ] && ok "--no-load leaves the load out" || bad "--no-load"
: > "$FIX/untracked.txt"; out=$(qout); [ $? -eq 1 ] && echo "$out" | grep -q "main tree is not clean" && ok "an untracked file in the main tree: busy" || bad "dirty tree ($out)"; rm -f "$FIX/untracked.txt"

# ---- the wrapper: refusals
NOW=$(date +%s)
wrun() { NR_LATEST_EPOCH=$(( $(date +%s) + ${LATEST_IN:-5} )) NR_POLL_S=1 NR_QUIET_N=${QN:-2} NR_EST=3000 bash "$W"; }
lastrun() { local d last=""; for d in "$ORCH"/log/nightly/2*/; do last=${d}run.txt; done; echo "$last"; }
clean_runs() { rm -rf "$ORCH"/log/nightly/2*/ "$ORCH"/log/nightly/restart; }
INNER=$T/inner.sh
cat > "$INNER" <<'EOF'
#!/usr/bin/env bash
# a stand-in for nightly_cron.sh: records what the wrapper gave it
cg=/sys/fs/cgroup$(cut -d: -f3 /proc/self/cgroup)
{ echo "ran"; echo "workers=$PYTEST_XDIST_AUTO_NUM_WORKERS"; echo "memmax=$(cat $cg/memory.max 2>&1)"; echo "swapmax=$(cat $cg/memory.swap.max 2>&1)";
  echo "oomgroup=$(cat $cg/memory.oom.group 2>&1)"; echo "oomadj=$(cat /proc/self/oom_score_adj)"; echo "off=$([ -e "$NR_ORCH/dispatch/OFF" ] && echo yes || echo no)"; } > "$NR_MARK"
exit 0
EOF
export NR_MARK=$T/mark.txt

reset; clean_runs; status_lead
rm -f "$NR_MARK"; NR_INNER=$INNER wrun; rc=$?
r=$(lastrun)
[ $rc -eq 2 ] && ok "a planted lead running: the wrapper refuses at the latest start (exit 2)" || bad "lead refusal exit ($rc)"
head -1 "$r" | grep -q "nightly night: NOT STARTED by nightly_restart.sh" && contains "$r" "lead(s) running" && ok "run.txt's first line says NOT STARTED, and why (the 08:00 check reads it as FAILED and pings)" || bad "run.txt ($(cat "$r" 2>&1 | head -2))"
[ ! -e "$NR_MARK" ] && [ ! -e "$ORCH/dispatch/OFF" ] && ok "the nightly never started, and no dispatch/OFF was left" || bad "inner ran or OFF left"

reset; clean_runs; ( exec 9> "$SLOTS/gov-os-heavy-slot-1.lock"; flock -n 9 || exit 1; exec sleep 30 ) & HOLD=$!; sleep 0.5
rm -f "$NR_MARK"; NR_INNER=$INNER wrun; rc=$?; r=$(lastrun)
[ $rc -eq 2 ] && contains "$r" "heavy slot 1 is held" && [ ! -e "$NR_MARK" ] && ok "a planted heavy slot held: the wrapper refuses and names the slot" || bad "slot refusal ($rc)"
kill "$HOLD" 2>/dev/null; wait "$HOLD" 2>/dev/null

reset; clean_runs; rm -f "$NR_MARK"; : > "$ORCH/log/act-in-progress.txt"; NR_INNER=$INNER wrun; rc=$?; r=$(lastrun)
[ $rc -eq 2 ] && contains "$r" "an ACT is in progress" && ok "an ACT in progress: refused" || bad "ACT refusal ($rc)"

reset; clean_runs; rm -f "$NR_MARK"; LATEST_IN=-10 NR_INNER=$INNER wrun; rc=$?; r=$(lastrun)
[ $rc -eq 2 ] && contains "$r" "past the latest start" && [ ! -e "$NR_MARK" ] && ok "past the latest start: refused, nothing run" || bad "latest start ($rc)"

reset; clean_runs; rm -f "$NR_MARK"; XDG_RUNTIME_DIR=$T/nobus NR_INNER=$INNER wrun; rc=$?; r=$(lastrun)
[ $rc -eq 2 ] && contains "$r" "no systemd user scope" && [ ! -e "$NR_MARK" ] && ok "no user scope: the cap cannot be applied, so the nightly does not run" || bad "no scope ($rc)"

reset; clean_runs; rm -f "$NR_MARK"; echo "# changed" >> "$FIX/$REL/quiet_check.py"; NR_INNER=$INNER wrun; rc=$?; r=$(lastrun)
[ $rc -eq 2 ] && contains "$r" "is not its commit at HEAD" && [ ! -e "$NR_MARK" ] && ok "code that differs from its commit: refused" || bad "uncommitted code ($rc)"
git -C "$FIX" checkout -q -- "$REL/quiet_check.py"

printf 'MemTotal: 24607392 kB\nMemAvailable: %s kB\n' 12000000 > "$T/meminfo"
reset; clean_runs; rm -f "$NR_MARK"; NR_MEMINFO=$T/meminfo NR_INNER=$INNER wrun; rc=$?; r=$(lastrun)
[ $rc -eq 2 ] && contains "$r" "memory: 12000000 kB available less the 3 GiB floor leaves" && [ ! -e "$NR_MARK" ] && ok "11.4 GiB available (cap would be 8.4 GiB, under 9): refused" || bad "memory refusal ($rc: $(tail -1 "$r"))"

# ---- the wrapper: a quiet machine; the cap, the swap limit, the score, the workers
for avail in 40000000:12288:16 20000000:12288:16 13000000:9623:12; do
  IFS=: read -r kb cap w <<< "$avail"
  printf 'MemAvailable: %s kB\n' "$kb" > "$T/meminfo"
  reset; clean_runs; rm -f "$NR_MARK"; NR_MEMINFO=$T/meminfo NR_INNER=$INNER LATEST_IN=60 wrun; rc=$?
  log=$(ls "$ORCH"/log/nightly/restart/*.log | head -1)
  if [ $rc -eq 0 ] && contains "$log" "cap ${cap} MB (MemoryMax, no swap); ${w} pytest workers"; then ok "${kb} kB available: cap ${cap} MB, ${w} workers"
  else bad "sizing for ${kb} kB ($rc: $(grep 'cap ' "$log" | tail -1))"; fi
done
reset; clean_runs; rm -f "$NR_MARK"; printf 'MemAvailable: 20000000 kB\n' > "$T/meminfo"
status_lead
( sleep 3; status ) & SB=$!
NR_MEMINFO=$T/meminfo NR_INNER=$INNER LATEST_IN=60 wrun; rc=$?
[ $rc -eq 0 ] && [ -f "$NR_MARK" ] && ok "a lead that ends: the wrapper waited, then started the run" || bad "wait then go ($rc)"
contains "$NR_MARK" "memmax=12884901888" && ok "the scope's memory.max is 12 GiB (12884901888)" || bad "memory.max ($(grep memmax "$NR_MARK"))"
contains "$NR_MARK" "swapmax=0" && ok "the scope's memory.swap.max is 0" || bad "swap.max ($(grep swapmax "$NR_MARK"))"
contains "$NR_MARK" "oomgroup=1" && ok "memory.oom.group is 1 (the kernel kills the whole run)" || bad "oom.group ($(grep oomgroup "$NR_MARK"))"
contains "$NR_MARK" "oomadj=500" && ok "the run's processes carry oom_score_adj 500" || bad "oom_score_adj ($(grep oomadj "$NR_MARK"))"
contains "$NR_MARK" "off=yes" && [ ! -e "$ORCH/dispatch/OFF" ] && ok "dispatch/OFF was there during the run and is gone after it" || bad "OFF during/after"
# cron's bare environment: no XDG_RUNTIME_DIR, no bus address, a short PATH
reset; clean_runs; rm -f "$NR_MARK"
envargs=(); while IFS= read -r kv; do envargs+=("$kv"); done < <(env | grep '^NR_')
env -i HOME=/home/usain PATH=/usr/bin:/bin "${envargs[@]}" NR_MEMINFO=$T/meminfo NR_INNER=$INNER NR_LATEST_EPOCH=$(( $(date +%s) + 60 )) NR_POLL_S=1 NR_QUIET_N=2 NR_EST=3000 bash "$W"; rc=$?
[ $rc -eq 0 ] && contains "$NR_MARK" "memmax=12884901888" && ok "cron's bare environment (env -i): the wrapper finds the user bus itself and runs the capped scope" || bad "env -i run ($rc)"
reset; : > "$ORCH/dispatch/OFF"; clean_runs; rm -f "$NR_MARK"
NR_MEMINFO=$T/meminfo NR_INNER=$INNER LATEST_IN=4 wrun; rc=$?
[ $rc -eq 2 ] && [ -e "$ORCH/dispatch/OFF" ] && [ ! -e "$NR_MARK" ] && ok "the CTO's own dispatch/OFF is respected and never removed by the wrapper" || bad "CTO's OFF ($rc)"
rm -f "$ORCH/dispatch/OFF"

# ---- the wrapper: the cap kills a planted memory hog; the session and the servers stay
cat > "$T/hog.py" <<'EOF'
import sys, time
held = []
for i in range(0, int(sys.argv[1]), 16):
    held.append(bytearray(b"x" * (16 * 1024 * 1024))); time.sleep(0.03)
print("hog reached its target", flush=True); time.sleep(60)
EOF
cat > "$T/hog-inner.sh" <<EOF
#!/usr/bin/env bash
: > "\$NR_ORCH/NIGHTLY-RUNNING"
d="\$NR_ORCH/log/nightly/\$(date +%Y%m%d-%H%M)"; mkdir -p "\$d"; echo "\$(date +%F) nightly night: planted" > "\$d/run.txt"
sleep 120 &
echo \$! > "$T/sibling.pid"
python3 -I "$T/hog.py" 600
EOF
servers() { for d in /proc/[0-9]*; do tr '\0' ' ' < "$d/cmdline" 2>/dev/null | grep -E 'ollama serve|llama-server|rerank_service' | grep -v grep > /dev/null && echo "${d#/proc/}"; done | sort | tr '\n' ' '; }
S0=$(servers); ME=$$
reset; clean_runs; rm -f "$T/sibling.pid"; printf 'MemAvailable: 20000000 kB\n' > "$T/meminfo"
NR_CAP_MB=200 NR_CAP_MIN_MB=100 NR_MEMINFO=$T/meminfo NR_INNER=$T/hog-inner.sh LATEST_IN=60 wrun; rc=$?
log=$(ls "$ORCH"/log/nightly/restart/*.log | head -1)
[ $rc -ne 0 ] && ok "a 600 MB hog in a 200 MB cap: the run ended, exit $rc" || bad "hog exit ($rc)"
contains "$log" "KILLED by its memory cap" && ok "the wrapper says the memory cap killed the run (exit 137, the whole run)" || bad "hog message ($(grep 'RUN ENDED' "$log"))"
sib=$(cat "$T/sibling.pid" 2>/dev/null); [ -n "$sib" ] && ! kill -0 "$sib" 2>/dev/null && ok "the hog's sibling process died with it (the whole run, not a part)" || bad "sibling alive ($sib)"
[ ! -e "$ORCH/NIGHTLY-RUNNING" ] && [ ! -e "$ORCH/dispatch/OFF" ] && ok "the marker NIGHTLY-RUNNING and dispatch/OFF are gone after the kill" || bad "marker or OFF left"
kill -0 "$ME" 2>/dev/null && ok "the test's own session (pid $ME) is alive" || bad "session"
gone=""; for p in $S0; do kill -0 "$p" 2>/dev/null || gone="$gone $p"; done
[ -z "$gone" ] && ok "every shared-server process seen before ($(echo $S0 | wc -w) of them) is still alive after" || bad "servers gone:$gone"
r=$(lastrun); [ -n "$r" ] && contains "$r" "the run was KILLED by its memory cap" && ok "run.txt's last line says what stopped the run" || bad "run.txt after kill ($r)"
nf=$(systemctl --user list-units --all --no-legend 'gov-nightly-*' | wc -l); [ "$nf" -eq 0 ] && ok "no gov-nightly unit is left loaded or failed" || bad "$nf gov-nightly unit(s) left"

# ---- the watchdog, the time limit, the rg tripwire
cat > "$T/sleep-inner.sh" <<EOF
#!/usr/bin/env bash
: > "\$NR_ORCH/NIGHTLY-RUNNING"
sleep \${INNER_SLEEP:-60}
EOF
reset; clean_runs; t0=$(date +%s)
INNER_SLEEP=60 NR_WATCH_S=1 NR_OOM_FLOOR_KB=900000000 NR_CAP_MIN_MB=100 NR_INNER=$T/sleep-inner.sh LATEST_IN=60 wrun; rc=$?
log=$(ls "$ORCH"/log/nightly/restart/*.log | head -1)
[ $rc -ne 0 ] && [ $(( $(date +%s) - t0 )) -lt 30 ] && contains "$log" "stopped by the watchdog" && ok "MemAvailable under the trip-wire's floor: the watchdog stops the run's scope within seconds" || bad "watchdog ($rc, $(( $(date +%s) - t0 )) s: $(grep -E 'WATCHDOG|RUN ENDED' "$log" | tail -1))"
[ ! -e "$ORCH/NIGHTLY-RUNNING" ] && ok "the watchdog's stop leaves no NIGHTLY-RUNNING" || bad "marker after watchdog"
reset; clean_runs; t0=$(date +%s)
INNER_SLEEP=60 NR_RT_MAX_S=3 NR_INNER=$T/sleep-inner.sh LATEST_IN=60 wrun; rc=$?
log=$(ls "$ORCH"/log/nightly/restart/*.log | head -1)
[ $rc -ne 0 ] && [ $(( $(date +%s) - t0 )) -lt 40 ] && contains "$log" "limit" && ok "the run's time limit (RuntimeMaxSec) stops a hang" || bad "time limit ($rc: $(grep 'RUN ENDED' "$log"))"
reset; clean_runs; rm -f "$NR_MARK"
INNER_SLEEP=4 NR_WATCH_S=1 NR_WATCH_RG=500 NR_INNER=$T/sleep-inner.sh LATEST_IN=60 wrun; rc=$?
items=$(ls "$ORCH"/dispatch/inbox/*rg-tripwire.txt 2>/dev/null | wc -l)
[ $rc -eq 0 ] && [ "$items" -eq 1 ] && ok "500 rg processes during the run: one inbox item, and the run goes on to its end (the tripwire stops nothing)" || bad "rg tripwire ($rc, $items items)"
grep -q "P1: 500 rg processes" "$ORCH"/dispatch/inbox/*rg-tripwire.txt 2>/dev/null && ok "the item names the count and is a P1" || bad "rg item text"

echo "cases: $n"
echo "failures: $fails"
[ "$fails" -eq 0 ]
