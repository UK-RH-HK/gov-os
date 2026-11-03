#!/usr/bin/env bash
# The heavy-job limit (owner, DEC-979 item 1 D1; CAPACITY-1): a test run takes one of a few machine-wide slots and
# waits for one; everything else runs freely. Each slot's run also caps pytest-xdist's `-n auto` at WORKERS, so the
# slots together keep the load near the number of processors (SLOTS x WORKERS, about 18 of 20).
#   bash heavy_slot.sh <the run's command and arguments>
#   bash heavy_slot.sh --held <slot numbers, comma-separated> <command>   (a caller that holds slots itself)
# Exits with the command's code. The sizes are in heavy_slots.conf beside this script (re-sized from the re-measure
# after W2-107 without a code change); GOV_HEAVY_SLOTS / GOV_HEAVY_WORKERS override them for a test.
# A slot is a lock file held for the whole run (flock -o: the lock is not passed to the run, so a daemon the run leaves
# behind never keeps it); the slot frees when the run's own process ends.
# Rebuilds are not slots here: they already run one at a time on the machine (the rebuild lock, W2-76).
#
# DEC-1038 (4), DEC-1039 (EMG-gitleaks, 2026-11-02): each slot's CPU set. The thread budget alone did not bound the
# load (W2-69's 352 tests: peak runnable 179 with it, 165 without): a program that sizes its own pool to the machine
# (the secret scan's pool, one gitleaks per CPU, in each of 6 workers) ignores every thread variable. So each slot's
# run is confined with `taskset -c` to its own share of the CPUs: the logical CPUs of this script's own CPU set (its
# affinity, /proc/self/status), less EXCLUDE_CPUS, divided evenly among the SLOTS; slot i takes its own contiguous
# range (20 CPUs, 3 slots: 0-5, 6-12, 13-19), and everything the run starts inherits it. The thread budget then
# follows from the share: max(1, the share's CPUs / the run's workers), the run's workers being WORKERS or the
# caller's own PYTEST_XDIST_AUTO_NUM_WORKERS (a serial run that sets 1 gets its whole share). A machine with no
# taskset (or one that refuses the set) still runs the command, unconfined, with the budget, and says so on standard
# error once. GOV_HEAVY_CPUS (exported) names the run's CPU set, empty when unconfined; GOV_HEAVY_SLOT its slot (or
# the held list). A child started with an environment built from scratch loses the budget but never the CPU set.
#
# The embedders' CPU sets (the shared server on 12-19 at nice 10, ACT-OLLAMA-CAP-1; the query server on 8-11,
# ACT-QUERY-CPUS-1) are NOT excluded by default (EXCLUDE_CPUS empty; heavy_slots.conf or GOV_HEAVY_EXCLUDE_CPUS sets
# it, e.g. 8-19). The measurement (EMG-gitleaks, 2026-11-02 19:47-20:01, the incident 2026-11-02-1620's Fix): W2-69's
# 352 tests in slot 1 on CPUs 0-5 kept all 6 busy (5.99 of 6 on average) and ran 72 tests in 827 s, about a third of
# the rate of the 17:45 run that used about 17 of 20 CPUs; the run is CPU-bound, so its time follows its CPUs.
# Excluding 8-19 leaves 8 CPUs for 3 slots (2-3 each, under half of today's share): every slot's run would take more
# than twice as long again, while the 12 CPUs of the embedders stand mostly idle (they are idle between rebuilds and
# queries, and the shared one runs at nice 10, below any slot). The embedders keep their own caps (their sets and
# priority); a slot's share is the machine's CPUs divided, never more.
#
# --held (the nightly, DEC-984: it takes the slots' locks itself): no lock is taken; the run gets the union of the
# named slots' CPU sets, at most (number named) x WORKERS xdist workers and the budget from that union, as a slot's
# run does (the nightly's serial phase sets PYTEST_XDIST_AUTO_NUM_WORKERS=1: one process, the union's budget). An
# empty list (no slot held) gives one slot's worker cap and budget, unconfined (named on standard error).
# heavy-slot: --held   (this line tells a caller the form is supported)
HERE=$(cd "$(dirname "$0")" && pwd)
SLOTS=3 WORKERS=6 DIR=/tmp EXCLUDE_CPUS=""
[ -f "$HERE/heavy_slots.conf" ] && . "$HERE/heavy_slots.conf"
SLOTS=${GOV_HEAVY_SLOTS:-$SLOTS}
WORKERS=${GOV_HEAVY_WORKERS:-$WORKERS}
DIR=${GOV_HEAVY_DIR:-$DIR}
EXCLUDE_CPUS=${GOV_HEAVY_EXCLUDE_CPUS-$EXCLUDE_CPUS}
case "$SLOTS" in ""|*[!0-9]*) SLOTS=1 ;; esac; [ "$SLOTS" -ge 1 ] || SLOTS=1
BUSY=213  # flock's exit when the slot is taken; any other code is the command's own
HELD="" HOLDS=""
if [ "${1:-}" = --held ]; then HOLDS=1; HELD=${2-}; shift 2 2>/dev/null || shift; fi

# A CPU list ("0-5,8,10-12") as one number per line; nothing for anything malformed.
expand() {
  local IFS=, part a b
  for part in $1; do
    case "$part" in
      *[!0-9-]*|"") return 1 ;;
      *-*) a=${part%%-*} b=${part#*-}
           case "$a$b" in ""|*[!0-9]*) return 1 ;; esac
           while [ "$a" -le "$b" ]; do echo "$a"; a=$((a + 1)); done ;;
      *) echo "$part" ;;
    esac
  done
}
# The CPUs this script may use: its own affinity, then the machine's count (`nproc --all`, not `nproc`: GNU nproc
# follows an inherited OMP_NUM_THREADS / OMP_THREAD_LIMIT, review F1).
mine=""
while read -r key value; do [ "$key" = Cpus_allowed_list: ] && mine=$value; done < /proc/self/status 2>/dev/null
mapfile -t ALL < <(expand "$mine" 2>/dev/null)
if [ "${#ALL[@]}" -eq 0 ]; then
  n=$(nproc --all 2>/dev/null || getconf _NPROCESSORS_ONLN 2>/dev/null || echo 1)
  case "$n" in ""|*[!0-9]*) n=1 ;; esac
  mapfile -t ALL < <(seq 0 $((n - 1)))
fi
if [ -n "$EXCLUDE_CPUS" ]; then
  mapfile -t OUT < <(expand "$EXCLUDE_CPUS")
  KEEP=()
  for c in "${ALL[@]}"; do
    skip=""; for x in "${OUT[@]}"; do [ "$c" = "$x" ] && skip=1 && break; done
    [ -z "$skip" ] && KEEP+=("$c")
  done
  if [ "${#KEEP[@]}" -gt 0 ]; then ALL=("${KEEP[@]}")
  else echo "heavy_slot: EXCLUDE_CPUS ($EXCLUDE_CPUS) leaves no CPU; not applied" >&2; fi
fi
N=${#ALL[@]}
# Slot i's share, a comma-separated list: indices [(i-1) N / SLOTS, i N / SLOTS) of the CPUs; at least one CPU.
share() {
  local i=$1 lo hi out="" k
  lo=$(( (i - 1) * N / SLOTS )); hi=$(( i * N / SLOTS ))
  [ "$hi" -gt "$lo" ] || { lo=$(( (i - 1) % N )); hi=$((lo + 1)); }
  for ((k = lo; k < hi; k++)); do out+="${out:+,}${ALL[k]}"; done
  echo "$out"
}
ncpus() { local IFS=, arr; read -ra arr <<< "$1"; echo "${#arr[@]}"; }  # how many CPUs a share lists (shares are disjoint)
TASKSET=$(command -v taskset 2>/dev/null)
[ -n "$TASKSET" ] && ! "$TASKSET" -c "$(IFS=,; echo "${ALL[*]}")" true 2>/dev/null && TASKSET=""
said_cpus=""
# Sets the run's budget for a CPU list of $2 CPUs ($1) and $3 workers; prints the command prefix (taskset or nothing).
budget() {
  local cpus=$1 count=$2 workers=$3 threads
  case "$count$workers" in *[!0-9]*|"") threads=1 ;; *) threads=$(( workers > 0 ? count / workers : 1 )) ;; esac
  case "${GOV_HEAVY_THREADS-}" in "") ;; *[!0-9]*) threads=1 ;; *) threads=$GOV_HEAVY_THREADS ;; esac  # digits only (F4)
  [ "$threads" -ge 1 ] 2>/dev/null || threads=1
  for v in GOMAXPROCS OMP_NUM_THREADS MKL_NUM_THREADS OPENBLAS_NUM_THREADS RAYON_NUM_THREADS NUMEXPR_NUM_THREADS \
           NUMEXPR_MAX_THREADS VECLIB_MAXIMUM_THREADS; do
    export "$v=$threads"
  done
  export GOV_HEAVY_THREAD_BUDGET=$threads
  if [ -n "$TASKSET" ] && [ -n "$cpus" ]; then
    export GOV_HEAVY_CPUS=$cpus; PREFIX=("$TASKSET" -c "$cpus")
  else
    export GOV_HEAVY_CPUS=""; PREFIX=()
    [ -z "$said_cpus" ] && [ -n "$cpus" ] && { echo "heavy_slot: no taskset here (or the CPU set $cpus refused): the run is not confined to its CPUs; the thread budget ($threads) still holds" >&2; said_cpus=1; }
  fi
}
WCAP=$WORKERS

if [ -n "$HOLDS" ]; then  # the caller holds these slots: their union, no lock
  cpus="" held=0 seen=","
  IFS=, read -ra LIST <<< "$HELD"
  for i in "${LIST[@]}"; do
    case "$i" in ""|*[!0-9]*) continue ;; esac
    [ "$i" -ge 1 ] && [ "$i" -le "$SLOTS" ] || continue
    case "$seen" in *",$i,"*) continue ;; esac
    seen+="$i,"; s=$(share "$i"); cpus+="${cpus:+,}$s"; held=$((held + 1))
  done
  if [ "$held" -eq 0 ]; then
    echo "heavy_slot --held: no slot held: one slot's worker cap and budget, not confined to CPUs" >&2
    count=$(( N / SLOTS )); WCAP=$WORKERS cpus=""
  else
    count=$(ncpus "$cpus"); WCAP=$(( held * WORKERS ))
  fi
  export PYTEST_XDIST_AUTO_NUM_WORKERS=${PYTEST_XDIST_AUTO_NUM_WORKERS:-$WCAP}
  export GOV_HEAVY_SLOT="held:$HELD"
  budget "$cpus" "$count" "$PYTEST_XDIST_AUTO_NUM_WORKERS"
  exec "${PREFIX[@]}" "$@"
fi
export PYTEST_XDIST_AUTO_NUM_WORKERS=${PYTEST_XDIST_AUTO_NUM_WORKERS:-$WORKERS}

# DEC-1011 (owner): the merge queue and the closes take the next free slot before any lead's heavy step, and no slot
# is kept idle. A priority caller (GOV_HEAVY_PRIORITY=1, set by merge_queue.py and close_build.py for their whole run)
# registers itself while it waits and checks every 2 s; any other caller does not take a free slot while a live
# priority waiter exists (a file for a dead process is ignored and removed).
PRIO=${GOV_HEAVY_PRIORITY:-}
MINE="$DIR/gov-os-heavy-prio-$$"
prio_waiting() {
  for f in "$DIR"/gov-os-heavy-prio-*; do
    [ -e "$f" ] || continue
    p=${f##*-}
    if kill -0 "$p" 2>/dev/null; then [ "$f" != "$MINE" ] && return 0; else rm -f "$f"; fi
  done
  return 1
}
[ -n "$PRIO" ] && { : > "$MINE"; trap 'rm -f "$MINE"' EXIT; }
said=""
while :; do
  if [ -z "$PRIO" ] && prio_waiting; then
    [ -z "$said" ] && { echo "heavy_slot: a landing or close waits first; waiting ($(date '+%F %T'))" >&2; said=1; }
    sleep 10; continue
  fi
  for ((i = 1; i <= SLOTS; i++)); do
    s=$(share "$i")
    budget "$s" "$(ncpus "$s")" "$PYTEST_XDIST_AUTO_NUM_WORKERS"
    export GOV_HEAVY_SLOT=$i
    if [ -n "$PRIO" ]; then  # the registration ends the moment the slot is taken, not when the run ends
      flock -n -o -E "$BUSY" "$DIR/gov-os-heavy-slot-$i.lock" bash -c 'rm -f "$0"; exec "$@"' "$MINE" "${PREFIX[@]}" "$@"
    else
      flock -n -o -E "$BUSY" "$DIR/gov-os-heavy-slot-$i.lock" "${PREFIX[@]}" "$@"
    fi
    rc=$?
    [ "$rc" -ne "$BUSY" ] && { [ -n "$PRIO" ] && rm -f "$MINE"; exit "$rc"; }
  done
  [ -z "$said" ] && { echo "heavy_slot: all $SLOTS slots taken; waiting ($(date '+%F %T'))" >&2; said=1; }
  if [ -n "$PRIO" ]; then sleep 2; else sleep 10; fi
done
