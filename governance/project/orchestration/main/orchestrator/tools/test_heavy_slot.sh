#!/usr/bin/env bash
# Tests of heavy_slot.sh (the lighter lane, DEC-979 D3). Every case uses its own slot folder; none touches /tmp's real slots.
HERE=$(cd "$(dirname "$0")" && pwd)
S="${HEAVY_SLOT_UNDER_TEST:-$HERE/heavy_slot.sh}"
work=$(mktemp -d); fails=0
fail() { echo "FAIL $1"; fails=1; }
export GOV_HEAVY_DIR=$work GOV_HEAVY_SLOTS=2 GOV_HEAVY_WORKERS=6

# H1: the command's exit code comes back (0, 1, 5), and its output
out=$(bash "$S" bash -c 'echo hi; exit 5'); rc=$?
[ "$rc" -eq 5 ] && [ "$out" = hi ] || fail "H1: rc $rc out '$out'"
bash "$S" true || fail "H1: true failed"
bash "$S" false && fail "H1: false passed"

# H2: xdist's -n auto is capped at WORKERS, unless the caller set it
v=$(bash "$S" bash -c 'echo $PYTEST_XDIST_AUTO_NUM_WORKERS'); [ "$v" = 6 ] || fail "H2: got '$v'"
v=$(PYTEST_XDIST_AUTO_NUM_WORKERS=2 bash "$S" bash -c 'echo $PYTEST_XDIST_AUTO_NUM_WORKERS'); [ "$v" = 2 ] || fail "H2: override '$v'"

# H3: two slots: two runs at once; a third waits until one ends
t0=$(date +%s)
bash "$S" sleep 4 & a=$!
bash "$S" sleep 4 & b=$!
sleep 1
bash "$S" true; t3=$(( $(date +%s) - t0 ))
wait $a $b
[ "$t3" -ge 3 ] || fail "H3: the third run did not wait ($t3 s)"
[ "$t3" -le 20 ] || fail "H3: the third run waited too long ($t3 s)"

# H4: a killed run frees its slot
GOV_HEAVY_SLOTS=1 bash "$S" sleep 30 & k=$!
sleep 1; kill $k; wait $k 2>/dev/null; pkill -P $k 2>/dev/null; sleep 1
t0=$(date +%s); GOV_HEAVY_SLOTS=1 timeout 40 bash "$S" true; rc=$?; t=$(( $(date +%s) - t0 ))
[ "$rc" -eq 0 ] && [ "$t" -le 35 ] || fail "H4: rc $rc after $t s"

# H5: a command whose own exit is 213 is not mistaken for a busy slot forever (it returns 213 only if every
# slot is busy; with a free slot the run happens once)
n=$work/count; : > "$n"
GOV_HEAVY_SLOTS=1 timeout 15 bash "$S" bash -c "echo x >> $n; exit 0"; [ "$(wc -l < "$n")" -eq 1 ] || fail "H5: ran $(wc -l < "$n") times"

# H6: a process the run leaves behind (a daemon such as the embedder gov starts on demand) does not keep the slot
GOV_HEAVY_SLOTS=1 bash "$S" bash -c 'setsid sleep 30 >/dev/null 2>&1 < /dev/null & exit 0'
t0=$(date +%s); GOV_HEAVY_SLOTS=1 timeout 25 bash "$S" true; rc=$?; t=$(( $(date +%s) - t0 ))
[ "$rc" -eq 0 ] && [ "$t" -le 5 ] || fail "H6: the slot stayed held by a leftover process (rc $rc, $t s)"
pkill -f "^sleep 30$" 2>/dev/null

# H7 (DEC-1011): with one slot busy, a waiting landing or close (GOV_HEAVY_PRIORITY=1) takes the freed slot before a
# lead's step that started waiting earlier
ord="$work/order"; : > "$ord"
GOV_HEAVY_SLOTS=1 bash "$S" sleep 6 & h=$!
sleep 1; GOV_HEAVY_SLOTS=1 bash "$S" bash -c "echo L >> $ord" & l=$!
sleep 1; GOV_HEAVY_SLOTS=1 GOV_HEAVY_PRIORITY=1 bash "$S" bash -c "echo P >> $ord; sleep 1" & p=$!
wait $h $l $p
[ "$(head -1 "$ord")" = "P" ] || fail "H7: the lead's step took the slot before the waiting landing ($(tr '\n' ' ' < "$ord"))"
ls "$work"/gov-os-heavy-prio-* >/dev/null 2>&1 && fail "H7: a priority registration was left behind"

# H8: while a priority run RUNS (not waits), a lead's step still takes another free slot at once
GOV_HEAVY_SLOTS=2 GOV_HEAVY_PRIORITY=1 bash "$S" sleep 6 & p=$!
sleep 1; t0=$(date +%s); GOV_HEAVY_SLOTS=2 timeout 20 bash "$S" true; t=$(( $(date +%s) - t0 ))
[ "$t" -le 3 ] || fail "H8: a lead waited $t s for a free slot while a priority run ran"
wait $p

# H9 (DEC-1038): the thread budget reaches the run's children: (CPUs / SLOTS) / WORKERS, at least 1
n=$(nproc); want=$(( n / 2 / 6 )); [ "$want" -ge 1 ] || want=1
v=$(bash "$S" bash -c 'bash -c "echo \$GOMAXPROCS \$OMP_NUM_THREADS \$OPENBLAS_NUM_THREADS \$MKL_NUM_THREADS \$RAYON_NUM_THREADS"')
[ "$v" = "$want $want $want $want $want" ] || fail "H9: a grandchild sees '$v', want $want each"
# H10: an inherited large value is overridden; GOV_HEAVY_THREADS sets it
v=$(GOMAXPROCS=20 OMP_NUM_THREADS=20 bash "$S" bash -c 'echo $GOMAXPROCS $OMP_NUM_THREADS'); [ "$v" = "$want $want" ] || fail "H10: inherited '$v'"
v=$(GOV_HEAVY_THREADS=3 bash "$S" bash -c 'echo $GOMAXPROCS $GOV_HEAVY_THREAD_BUDGET'); [ "$v" = "3 3" ] || fail "H10: GOV_HEAVY_THREADS '$v'"
# H11: never 0: more slots x workers than CPUs still gives 1; a nonsense GOV_HEAVY_THREADS gives 1
v=$(GOV_HEAVY_SLOTS=50 GOV_HEAVY_WORKERS=50 bash "$S" bash -c 'echo $GOMAXPROCS'); [ "$v" = 1 ] || fail "H11: '$v'"
v=$(GOV_HEAVY_THREADS=abc bash "$S" bash -c 'echo $GOMAXPROCS'); [ "$v" = 1 ] || fail "H11: nonsense '$v'"

# H12 (review F1, F4): an inherited OMP_NUM_THREADS does not change the CPU count; GOV_HEAVY_THREADS digits only
v=$(OMP_NUM_THREADS=64 OMP_THREAD_LIMIT=64 bash "$S" bash -c 'echo $GOMAXPROCS'); [ "$v" = "$want" ] || fail "H12: OMP_NUM_THREADS=64 gave '$v', want $want"
v=$(GOV_HEAVY_THREADS=" 2" bash "$S" bash -c 'echo "[$GOMAXPROCS]"'); [ "$v" = "[1]" ] || fail "H12: a spaced value '$v'"
v=$(GOV_HEAVY_WORKERS=0 bash "$S" bash -c 'echo $GOMAXPROCS' 2>/dev/null); [ "$v" = 1 ] || fail "H12: WORKERS=0 '$v'"

# H13-H19 (DEC-1038 (4), DEC-1039, EMG-gitleaks): each slot's run is confined to its own share of the CPUs.
# A child program (python3, a grandchild of the gate) prints its CPU set and environment.
if command -v taskset >/dev/null 2>&1; then
  probe='import os; print(",".join(map(str, sorted(os.sched_getaffinity(0)))), os.environ.get("GOV_HEAVY_CPUS"), os.environ["GOMAXPROCS"], os.environ["GOV_HEAVY_THREAD_BUDGET"], os.environ["PYTEST_XDIST_AUTO_NUM_WORKERS"], os.environ.get("GOV_HEAVY_SLOT"))'
  # the expected shares, from this shell's own CPU set: SLOTS=2 -> the first half and the second half
  read -r all half1 half2 n1 n2 < <(python3 -c 'import os; c = sorted(os.sched_getaffinity(0)); h = len(c) // 2; j = lambda x: ",".join(map(str, x)); print(j(c), j(c[:h]), j(c[h:]), h, len(c) - h)')
  b1=$(( n1 / 6 )); [ "$b1" -ge 1 ] || b1=1
  # H13: slot 1's run, and a program it starts, see slot 1's share and the budget from it
  v=$(bash "$S" bash -c "python3 -c '$probe'")
  [ "$v" = "$half1 $half1 $b1 $b1 6 1" ] || fail "H13: slot 1's child sees '$v', want '$half1 $half1 $b1 $b1 6 1'"
  # H14: two runs at once get the two slots' sets: disjoint, together every CPU
  bash "$S" bash -c "python3 -c '$probe'; sleep 3" > "$work/h14a" & a=$!
  sleep 1; bash "$S" bash -c "python3 -c '$probe'" > "$work/h14b"
  wait $a
  sa=$(cut -d' ' -f1 "$work/h14a"); sb=$(cut -d' ' -f1 "$work/h14b")
  [ "$sa" = "$half1" ] && [ "$sb" = "$half2" ] || fail "H14: the two slots' sets are '$sa' and '$sb', want '$half1' and '$half2'"
  python3 -c 'import sys; a, b = (set(x.split(",")) for x in sys.argv[1:3]); sys.exit(0 if not a & b else 1)' "$sa" "$sb" || fail "H14: the sets overlap"
  # H15: an inherited narrower CPU set is what is divided (the process's affinity, not the machine)
  if [ "$(nproc)" -ge 4 ]; then
    first4=$(python3 -c 'import os; print(",".join(map(str, sorted(os.sched_getaffinity(0))[:4])))')
    v=$(taskset -c "$first4" bash "$S" bash -c "python3 -c '$probe'" | cut -d' ' -f1)
    [ "$v" = "$(echo "$first4" | cut -d, -f1-2)" ] || fail "H15: under the CPUs $first4 slot 1 got '$v'"
  fi
  # H16 (--held, the nightly): no lock taken; the union of the held slots' sets, their workers, the budget from it
  v=$(GOV_HEAVY_SLOTS=2 bash "$S" --held 1,2 bash -c "python3 -c '$probe'")
  bh=$(( (n1 + n2) / 12 )); [ "$bh" -ge 1 ] || bh=1
  [ "$v" = "$all $all $bh $bh 12 held:1,2" ] || fail "H16: --held 1,2 gives '$v', want '$all $all $bh $bh 12 held:1,2'"
  v=$(bash "$S" --held 2 bash -c "python3 -c '$probe'" | cut -d' ' -f1,5); [ "$v" = "$half2 6" ] || fail "H16: --held 2 gives '$v'"
  # the budget follows the run's own workers: a serial run (1 worker) gets its whole set; 2 workers half of a share
  v=$(PYTEST_XDIST_AUTO_NUM_WORKERS=1 GOV_HEAVY_SLOTS=2 bash "$S" --held 1,2 bash -c "python3 -c '$probe'" | cut -d' ' -f3,5)
  [ "$v" = "$((n1 + n2)) 1" ] || fail "H16: a serial held run's budget '$v', want '$((n1 + n2)) 1'"
  b2=$(( n1 / 2 )); [ "$b2" -ge 1 ] || b2=1
  v=$(PYTEST_XDIST_AUTO_NUM_WORKERS=2 bash "$S" bash -c "python3 -c '$probe'" | cut -d' ' -f3); [ "$v" = "$b2" ] || fail "H16: 2 workers' budget '$v', want $b2"
  # a held run takes no lock: it runs while every slot is busy
  bash "$S" sleep 4 & a=$!; bash "$S" sleep 4 & b=$!; sleep 1
  t0=$(date +%s); timeout 10 bash "$S" --held 1,2 true; rc=$?; t=$(( $(date +%s) - t0 ))
  wait $a $b
  [ "$rc" -eq 0 ] && [ "$t" -le 2 ] || fail "H16: a held run waited for a lock (rc $rc, $t s)"
  # H17: --held with no slot named: one slot's worker cap and budget, unconfined, said on standard error
  v=$(bash "$S" --held "" bash -c "python3 -c '$probe'" 2> "$work/h17")
  [ "$v" = "$all  $b1 $b1 6 held:" ] || fail "H17: --held '' gives '$v'"
  grep -q "no slot held" "$work/h17" || fail "H17: not said"
  # H18: EXCLUDE_CPUS takes CPUs out before the division; one that leaves none is not applied
  v=$(GOV_HEAVY_EXCLUDE_CPUS="$half2" bash "$S" bash -c "python3 -c '$probe'" | cut -d' ' -f1)
  want18=$(python3 -c 'import sys; c = sys.argv[1].split(","); print(",".join(c[:len(c) // 2]))' "$half1")
  [ "$v" = "$want18" ] || fail "H18: with $half2 excluded slot 1 got '$v', want '$want18'"
  v=$(GOV_HEAVY_EXCLUDE_CPUS="$all" bash "$S" bash -c "python3 -c '$probe'" 2>/dev/null | cut -d' ' -f1)
  [ "$v" = "$half1" ] || fail "H18: excluding every CPU gave '$v'"
else
  echo "SKIP H13-H18: no taskset on this machine"
fi
# H19: a machine with no taskset still runs the command, unconfined, with the budget, and says so (named)
nots="$work/no-taskset"; mkdir -p "$nots"
for t in bash flock sleep date rm seq nproc getconf dirname cat; do p=$(command -v "$t") && ln -s "$p" "$nots/$t"; done
v=$(PATH="$nots" bash "$S" bash -c 'echo "ran [$GOV_HEAVY_CPUS] $GOV_HEAVY_THREAD_BUDGET"; exit 3' 2> "$work/h19"); rc=$?
[ "$rc" -eq 3 ] && [ "$v" = "ran [] ${b1:-1}" ] || fail "H19: without taskset rc $rc out '$v'"
grep -q "no taskset" "$work/h19" || fail "H19: the missing taskset was not said"

rm -rf "$work"
[ "$fails" -eq 0 ] && echo "PASS: heavy_slot.sh H1-H19"
exit "$fails"
