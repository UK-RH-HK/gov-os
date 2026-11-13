#!/usr/bin/env bash
# The nightly's restart wrapper (ACT-NIGHTLY-RESTART-1; owner, DEC-1132 (4): "in the quiet hours, with nothing else
# running, sized to memory so it cannot exhaust it"). The owner's crontab runs it at 04:00 (DEC-973's hour):
#   0 4 * * * /usr/bin/bash /home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/nightly/nightly_restart.sh
# It adds three things in front of nightly_cron.sh, which stays as it is (its own code check, the log rotation, then
# `nightly.sh night`):
#
# 1. Nothing else running. quiet_check.py (beside this file) names what runs: a lead, a close, a landing, a rebuild, a
#    held heavy slot, an ACT, a memory measure, a dirty main tree, load. The wrapper waits for 5 quiet minutes in a row
#    (one look a minute), and gives up at the latest start: 07:30 less one and a half times the measured estimate
#    (nightly_estimate.py; 06:01 today). Giving up writes a night's run.txt whose first line says NOT STARTED and why,
#    so the 08:00 check calls the night FAILED and pings P1, as it does for any night that did not run; the wrapper
#    does not ping on its own. Once quiet it writes dispatch/OFF (the CTO's own off switch: no lead starts, no landing,
#    for the length of the run) and removes it only if the file is still its own; a second look follows the switch.
# 2. Sized to memory. The run is started inside `systemd-run --user --scope` with MemoryMax = the memory available now
#    less the 3 GiB floor, at most 12 GiB (D-10 run 2: the run raised memory in use by 8.1 GB at 16 workers), never
#    under 9 GiB (the clone's rebuild peaks at 7.3 GB), and MemorySwapMax=0, OOMPolicy=kill (the kernel kills the whole
#    run, never a part of it, and never swaps it into the machine's 8 GB), RuntimeMaxSec 3 h. The pytest workers are
#    (cap - 2 GiB) / 0.6 GB, 4 to 16. The run's processes take an oom_score_adj of 500, so the kernel picks them first
#    if the machine itself ever runs short. A watchdog (every 10 s) stops the run's scope when MemAvailable falls below
#    the out-of-memory trip-wire's 2 GiB (gate.json), and writes an inbox item when more than 200 rg processes run
#    (DEC-1132 (3) (a); the same text as tools/oom_watch.sh's, once in 10 minutes). With no user scope (no bus, or the
#    scope refused) the wrapper does not run the nightly at all: a cap that cannot be applied is a night not run.
# 3. A killed run is cleaned up: NIGHTLY-RUNNING (which only nightly.sh's own trap removes, and a kill skips it) is
#    removed by pid-owned logic here, run.txt says what stopped the run, and the clone is kept for the diagnosis.
#
# Test hooks (never set by cron): NR_REPO NR_ORCH NR_INNER NR_CAP_MB NR_CAP_MIN_MB NR_MEMINFO NR_LATEST_EPOCH NR_POLL_S
# NR_QUIET_N NR_OOM_FLOOR_KB NR_EST NR_WATCH_RG NR_RT_MAX_S NR_WATCH_S, and the quiet check's own (NR_PROC NR_STATUS ...).
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=${NR_REPO:-/home/usain/Dynamic-Agentic-Engineering-OS}
ORCH=${NR_ORCH:-$REPO/.gov-runtime/scratch/orchestrator}
REL=governance/project/orchestration/nightly
export HOME=/home/usain
export LANG=C.UTF-8
export PATH=/home/usain/.local/bin:/home/usain/.nvm/versions/node/v18.20.8/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/lib/wsl/lib
# cron has neither: the user manager's bus is reached by its path
export XDG_RUNTIME_DIR=${XDG_RUNTIME_DIR:-/run/user/$(id -u)}
export DBUS_SESSION_BUS_ADDRESS=${DBUS_SESSION_BUS_ADDRESS:-unix:path=$XDG_RUNTIME_DIR/bus}
LOGDIR=$ORCH/log/nightly/restart
mkdir -p "$LOGDIR" "$ORCH/log/nightly"
exec >> "$LOGDIR/$(date +%F).log" 2>&1
say() { echo "$(date '+%F %T') nightly_restart: $*"; }
say "start (pid $$)"

GIB_KB=1048576
FLOOR_KB=$((3 * GIB_KB)); OOM_FLOOR_KB=${NR_OOM_FLOOR_KB:-$((2 * GIB_KB))}
GATE_JSON=/home/usain/.gov-os/machine/gate.json
if [ -z "${NR_OOM_FLOOR_KB:-}" ] && [ -r "$GATE_JSON" ]; then
  read -r f o < <(python3 -I -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d["memory_floor_bytes"]["value"]//1024, d["oom_floor_bytes"]["value"]//1024)' "$GATE_JSON" 2>/dev/null)
  [ -n "${f:-}" ] && FLOOR_KB=$f; [ -n "${o:-}" ] && OOM_FLOOR_KB=$o
fi
CAP_MAX_KB=$((12 * GIB_KB)); CAP_MIN_KB=$((${NR_CAP_MIN_MB:-9216} * 1024))
QUIET_N=${NR_QUIET_N:-5}; POLL_S=${NR_POLL_S:-60}; WATCH_S=${NR_WATCH_S:-10}; RG_TRIP=200
MEMINFO=${NR_MEMINFO:-/proc/meminfo}
avail_kb() { awk '/^MemAvailable:/ {print $2}' "$MEMINFO"; }

# the night's run.txt, when the run does not start: the first line is what nightly_check.sh looks for
refuse() {
  local d f
  d=$ORCH/log/nightly/$(date +%Y%m%d-%H%M); mkdir -p "$d"; f=$d/run.txt
  [ -s "$f" ] || date "+%F %T nightly night: NOT STARTED by nightly_restart.sh: $1" > "$f"
  echo "$(date '+%F %T') NOT STARTED by nightly_restart.sh: $1" >> "$f"
  say "REFUSED: $1"; exit 2
}

# one wrapper at a time (fd 8 is closed for everything it starts)
exec 8> "$ORCH/log/nightly/.restart.lock"
flock -n 8 || { say "another nightly_restart.sh holds the lock; nothing done"; exit 0; }

# committed, reviewed code only (the same rule as nightly_cron.sh's, for this wrapper's own files)
if ! git -C "$REPO" diff --quiet HEAD -- "$REL" || [ -n "$(git -C "$REPO" ls-files --others --exclude-standard -- "$REL")" ]; then
  refuse "$REL in the main tree is not its commit at HEAD; the nightly does not run"
fi

# the latest start: the quiet hours end at 07:30; the run books 1.5 times its measured estimate
if [ -n "${NR_EST:-}" ]; then EST=$NR_EST; else
  EST=$(python3 -I "$HERE/nightly_estimate.py" estimate 2>/dev/null | python3 -I -c "import json, sys; print(json.load(sys.stdin).get('estimate_s') or '')" 2>/dev/null)
fi
[ -n "$EST" ] || EST=14400
LATEST=${NR_LATEST_EPOCH:-$(( $(date -d "today 07:30" +%s) - EST * 3 / 2 ))}
say "estimate ${EST} s; latest start $(date -d "@$LATEST" +%H:%M)"
[ "$(date +%s)" -lt "$LATEST" ] || refuse "it is past the latest start $(date -d "@$LATEST" +%H:%M): the run (estimate $((EST / 60)) min) would not end inside the quiet hours"

# the memory cap can be applied, or the night is not run
if [ ! -S "$XDG_RUNTIME_DIR/bus" ] || ! systemd-run --user --scope --quiet --unit="gov-nightly-probe-$$" -p MemoryMax=64M -p MemorySwapMax=0 true 2>/dev/null; then
  refuse "no systemd user scope (no user manager or bus): the memory cap cannot be applied, so the nightly does not run (loginctl enable-linger)"
fi

OFF=$ORCH/dispatch/OFF; OFFTOK="nightly_restart pid $$ $(date '+%F %T')"; HAVE_OFF=0
WPID=""; UNIT=""; TRIPPED=$LOGDIR/tripped.$$; rm -f "$TRIPPED"
cleanup() {
  [ -n "$WPID" ] && kill "$WPID" 2>/dev/null
  [ "$HAVE_OFF" = 1 ] && [ "$(cat "$OFF" 2>/dev/null)" = "$OFFTOK" ] && rm -f "$OFF"
  rm -f "$TRIPPED"
}
trap cleanup EXIT

# 1. wait for nothing else running
quiet=0; last=""; waited0=$(date +%s)
while :; do
  if out=$(python3 -I "$HERE/quiet_check.py"); then quiet=$((quiet + 1)); else quiet=0; last=$(echo "$out" | head -3 | tr '\n' ';'); fi
  if [ "$quiet" -ge "$QUIET_N" ]; then
    # the dispatcher's own off switch, then a second look (a lead may have started in the last minute)
    if (set -C; echo "$OFFTOK" > "$OFF") 2>/dev/null; then
      HAVE_OFF=1
      if python3 -I "$HERE/quiet_check.py" --no-load --own-off > /dev/null; then break; fi
      last="something started after the quiet minutes"; rm -f "$OFF"; HAVE_OFF=0; quiet=0
    else
      last="dispatch/OFF is there (not this wrapper's)"; quiet=0
    fi
  fi
  [ "$(date +%s)" -ge "$LATEST" ] && refuse "something else was running until the latest start $(date -d "@$LATEST" +%H:%M): ${last:-unknown}"
  sleep "$POLL_S"
done
say "quiet for $QUIET_N looks; waited $(( $(date +%s) - waited0 )) s; dispatch/OFF written"

# 2. size to memory
AV=$(avail_kb)
CAP_KB=$((AV - FLOOR_KB)); [ "$CAP_KB" -gt "$CAP_MAX_KB" ] && CAP_KB=$CAP_MAX_KB
[ -n "${NR_CAP_MB:-}" ] && CAP_KB=$((NR_CAP_MB * 1024))
[ "$CAP_KB" -ge "$CAP_MIN_KB" ] || refuse "memory: ${AV} kB available less the 3 GiB floor leaves $((CAP_KB / 1024)) MB, under the $((CAP_MIN_KB / 1024)) MB the run needs"
W=$(( (CAP_KB - 2 * GIB_KB) * 10 / (6 * GIB_KB) ))   # (cap - 2 GiB) / 0.6 GB (D-10: 0.41 to 0.51 GB a worker)
[ "$W" -gt 16 ] && W=16; [ "$W" -lt 4 ] && W=4
RTMAX=${NR_RT_MAX_S:-10800}
STAMP=$(date +%Y%m%d-%H%M%S); UNIT=gov-nightly-$STAMP
INNER=${NR_INNER:-$HERE/nightly_cron.sh}
say "memory available $((AV / 1024)) MB; cap $((CAP_KB / 1024)) MB (MemoryMax, no swap); $W pytest workers; unit $UNIT.scope; max run ${RTMAX} s"

# the watchdog: the machine's own floor, and the rg tripwire (an item, never a stop of anything by name)
watch() {
  local last_rg=0 n a now f
  while :; do
    a=$(avail_kb)
    if [ "${a:-0}" -lt "$OOM_FLOOR_KB" ]; then
      echo "MemAvailable ${a} kB under ${OOM_FLOOR_KB} kB" > "$TRIPPED"
      say "WATCHDOG: MemAvailable ${a} kB is under ${OOM_FLOOR_KB} kB: stopping $UNIT.scope"
      systemctl --user stop "$UNIT.scope" 2>/dev/null || kill -TERM "$SPID" 2>/dev/null
      return
    fi
    n=${NR_WATCH_RG:-$(ps -eo comm= | grep -cx rg)}
    now=$(date +%s)
    if [ "${n:-0}" -gt "$RG_TRIP" ] && [ $((now - last_rg)) -ge 600 ]; then
      last_rg=$now
      f=$ORCH/dispatch/inbox/$(date '+%Y%m%d-%H%M%S')-rg-tripwire.txt; mkdir -p "$ORCH/dispatch/inbox"
      {
        echo "log: nightly/restart"
        echo "Memory: rg tripwire (during the nightly)"
        echo "status: P1: $n rg processes running (trip at $RG_TRIP); MemAvailable ${a} kB; the nightly's scope $UNIT is running"
        echo
        echo "parents (child count, pid, cwd, command):"
        ps -eo ppid=,comm= | awk '$2=="rg"{print $1}' | sort | uniq -c | sort -rn | head -10 | while read -r c p; do
          echo "  $c  $p  $(readlink /proc/$p/cwd 2>/dev/null)  $(tr '\0' ' ' < /proc/$p/cmdline 2>/dev/null | cut -c1-200)"
        done
      } > "$f"
      say "RG TRIPWIRE: $n rg processes; item $f"
    fi
    sleep "$WATCH_S"
  done
}

# 3. the run, in its scope. fd 8 (the wrapper's lock) is not passed on; the run's processes are the kernel's first pick.
systemd-run --user --scope --quiet --unit="$UNIT" -p MemoryMax="$((CAP_KB / 1024))M" -p MemorySwapMax=0 -p OOMPolicy=kill \
  -p RuntimeMaxSec="$RTMAX" \
  env PYTEST_XDIST_AUTO_NUM_WORKERS="$W" NIGHTLY_RESTART=1 \
  bash -c 'echo 500 > /proc/self/oom_score_adj 2>/dev/null; exec bash "$@"' _ "$INNER" 8>&- &
SPID=$!
watch 8>&- &
WPID=$!
wait "$SPID"; rc=$?
kill "$WPID" 2>/dev/null; wait "$WPID" 2>/dev/null; WPID=""
result=$(systemctl --user show -p Result --value "$UNIT.scope" 2>/dev/null)
systemctl --user reset-failed "$UNIT.scope" 2>/dev/null

why=""
if [ -e "$TRIPPED" ]; then why="stopped by the watchdog: $(cat "$TRIPPED")"
elif [ "$result" = timeout ]; then why="stopped at its ${RTMAX} s limit (a hang?)"
elif [ "$result" = oom-kill ] || [ "$rc" -eq 137 ]; then
  # exit 137 is a SIGKILL of the run's own command: nightly.sh exits 0, 1 or 2, never 137; the unit's Result is read too,
  # but it can still say "success" when systemd-run returns first (seen in the rehearsal), so the exit code decides
  why="KILLED by its memory cap (${CAP_KB} kB, $W workers): the kernel's out-of-memory kill of the whole run (exit $rc, unit result ${result:-none})"
fi
if [ -n "$why" ]; then
  # a kill skips nightly.sh's own trap: the marker and the run's last line are put right here
  rm -f "$ORCH/NIGHTLY-RUNNING"
  last=""; for d in "$ORCH/log/nightly/$(date +%Y%m%d)"-*/; do [ -f "${d}run.txt" ] && last=${d}run.txt; done
  [ -n "$last" ] && echo "$(date '+%F %T') nightly_restart.sh: the run was $why; its clone is kept for the diagnosis" >> "$last"
  say "RUN ENDED: $why (exit $rc)"
else
  say "run ended: exit $rc, unit result ${result:-none}"
fi
exit "$rc"
