#!/usr/bin/env bash
# Tests of heavy_slot.sh (the lighter lane, DEC-979 D3). Every case uses its own slot folder; none touches /tmp's real slots.
HERE=$(cd "$(dirname "$0")" && pwd)
S="$HERE/heavy_slot.sh"
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

rm -rf "$work"
[ "$fails" -eq 0 ] && echo "PASS: heavy_slot.sh H1-H6"
exit "$fails"
