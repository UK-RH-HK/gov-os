#!/bin/bash
# ACT-DISPATCH-NIGHTLY-SLOT-1's rehearsal: bash rehearse.sh <bed folder (new, under /tmp/claude-1000)> <repository>
# A. the bundle; B. a fresh clone of w2/integrate: check, the checks before, apply, verify, the checks after;
# C. a planted nightly, live (real processes, real flock on fds, the real /proc), in planted folders only: before and
# after, and each condition taken away; D. the unit tests (before: the new case red; after: all green; the whole
# dispatcher suite after); E. undo and refusals; F. the main tree untouched. Ends with "failures: N".
set -u
BED=${1:?bed}; REPO=${2:?repository}
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ACT=$REPO/.gov-runtime/scratch/orchestrator/acts/ACT-DISPATCH-NIGHTLY-SLOT-1
HEAVY=$REPO/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh
PROCSH=$REPO/.gov-runtime/scratch/orchestrator/tools/proc.sh
P=governance/project/orchestration/tools/dispatch/dispatcher.py
T=tests/unit/orchestration/test_dispatcher.py
case "$BED" in /tmp/claude-1000/?*) ;; *) echo "the bed must be under /tmp/claude-1000" >&2; exit 2 ;; esac
[ ! -e "$BED" ] || { echo "the bed exists: $BED" >&2; exit 2; }
mkdir -p "$BED/tmp"; export TMPDIR="$BED/tmp"
ok=0; bad=0
mask() { sed -e "s#$BED#<bed>#g" -e "s#$REPO#<repo>#g"; }
r() { if [ "$1" = 0 ]; then echo "ok   $2"; ok=$((ok + 1)); else echo "FAIL $2"; bad=$((bad + 1)); fi; }
is() { [ "$1" = "$2" ]; r $? "$3"; }
IFS='|' read -r root path before after < "$ACT/list.txt"
main_before=$(sha256sum "$REPO/$P" | cut -c1-64)
main_status=$(git -C "$REPO" status --porcelain -- governance tests src | sha256sum | cut -c1-64)

echo "--- A. the bundle"
is "$root|$path" "repo|$P" "A1 list.txt names the one file, root repo"
is "$(sha256sum "$ACT/before/repo/$P" | cut -c1-64)" "$before" "A2 the before copy hashes as listed"
is "$(sha256sum "$ACT/after/repo/$P" | cut -c1-64)" "$after" "A3 the after copy hashes as listed"
is "$before" "$main_before" "A4 the main tree's dispatcher is the frozen before"
bash -n "$ACT/apply.sh"; r $? "A5 apply.sh parses"
diff -u "$ACT/before/repo/$P" "$ACT/after/repo/$P" > "$BED/after-minus-before.diff"
is "$(grep -c '^-[^-]' "$BED/after-minus-before.diff")" 1 "A6 one line removed (in_slot's docstring line, rewritten), the rest added"
echo "     $(grep -c '^+[^+]' "$BED/after-minus-before.diff") lines added"

echo "--- B. a fresh clone of w2/integrate"
git clone -q --no-hardlinks --branch w2/integrate "$REPO" "$BED/clone" || { echo "clone failed"; exit 3; }
cd "$BED/clone" || exit 3
out=$(bash "$ACT/apply.sh" check); rc=$?; echo "     $out"
is "$rc|${out%% (*}" "0|state before" "B1 check: state before (exit 0)"
python3 -I - "$HERE/checks.json" > "$BED/checks-before.txt" <<'EOF'
import json, subprocess, sys
for c in json.load(open(sys.argv[1])):
    print(subprocess.run(["bash", "-c", c], capture_output=True, text=True).returncode)
EOF
is "$(paste -sd, "$BED/checks-before.txt")" "0,1,1" "B2 the checks before the apply: 1 passes (it parses), 2 and 3 refuse (exits 0,1,1)"
mode0=$(stat -c %a "$P")
out=$(bash "$ACT/apply.sh" apply); rc=$?; echo "     $out"
is "$rc" 0 "B3 apply (exit 0)"
cmp -s "$P" "$ACT/after/repo/$P"; r $? "B4 the file is the after, byte for byte"
is "$(stat -c %a "$P")" "$mode0" "B5 its mode kept ($mode0)"
bash "$ACT/apply.sh" verify; r $? "B6 verify (exit 0)"
out=$(bash "$ACT/apply.sh" apply); rc=$?; echo "     $out"
is "$rc|${out##*; }" "0|nothing to do" "B7 apply again: nothing to do"
is "$(git status --porcelain | sed 's/^...//' | paste -sd,)" "$P" "B8 only the dispatcher changed in the clone"
python3 -I - "$HERE/checks.json" > "$BED/checks-after.txt" <<'EOF'
import json, subprocess, sys
for c in json.load(open(sys.argv[1])):
    p = subprocess.run(["bash", "-c", c], capture_output=True, text=True)
    print(p.returncode)
    sys.stderr.write(p.stdout[-300:])
EOF
is "$(paste -sd, "$BED/checks-after.txt")" "0,0,0" "B9 the manifest's three checks after the apply (exits 0,0,0)"

echo "--- C. a planted nightly, live (planted folders; the real slot files are never opened)"
# the probe loads each frozen copy beside the clone's balancer.py (the dispatcher imports it from its own folder)
for s in before after; do mkdir -p "$BED/pb/$s"; cp "$ACT/$s/repo/$P" "$BED/pb/$s/dispatcher.py"; cp "$BED/clone/governance/project/orchestration/tools/dispatch/balancer.py" "$BED/pb/$s/"; done
PN=$BED/planted; mkdir -p "$PN/orch" "$PN/runs/nightly" "$PN/slots" "$PN/state" "$PN/elsewhere"
mkdir -p "$PN/r/governance/project/orchestration/nightly"
cp "$HERE/planted/nightly/nightly.sh" "$PN/r/governance/project/orchestration/nightly/nightly.sh"
export DISPATCH_ORCH="$PN/orch" DISPATCH_STATE="$PN/state" DISPATCH_SLOT_GLOB="$PN/slots/gov-os-heavy-slot-*.lock"
export DISPATCH_NIGHTLY_RUNS="$PN/runs/nightly"
start_nightly() {  # start_nightly <hold 1|0> <run cwd or ''>: sets NPID (nightly.sh) and SPID (its suite stand-in)
  PN_ORCH="$PN/orch" PN_RUNS="$PN/runs/nightly" PN_SLOT_DIR="$PN/slots" PN_HOLD="$1" PN_RUN_CWD="$2" PN_SECONDS=40 \
    setsid bash "$PN/r/governance/project/orchestration/nightly/nightly.sh" night > "$BED/nightly-$1.log" 2>&1 &
  NPID=$!; SPID=""
  for _ in $(seq 1 50); do
    SPID=$(ps -o pid= --ppid "$NPID" | tr -d ' ' | head -1)
    [ -n "$SPID" ] && grep -q pytest "/proc/$SPID/cmdline" 2>/dev/null && break
    sleep 0.1
  done
}
probe() { python3 -I "$HERE/probe_live.py" "$1" "$SPID"; }
end_nightly() { bash "$PROCSH" stop --grace 5 "-$NPID" > /dev/null; bash "$PROCSH" wait --max 30 --every 1 "$NPID" > /dev/null; }
start_nightly 1 ""
echo "     planted nightly.sh pid $NPID, its suite stand-in pid $SPID: $(tr '\0' ' ' < /proc/$SPID/cmdline | cut -c1-60 | mask)"
held=$(for f in /proc/$NPID/fd/*; do l=$(readlink "$f"); case "$l" in "$PN"/slots/*) grep -c '^lock:.*FLOCK.*WRITE' "/proc/$NPID/fdinfo/${f##*/}";; esac; done | awk '{s += $1} END {print s + 0}')
is "$held" 3 "C1 the planted nightly holds its three planted slot locks by flock on its own fds (fdinfo lock lines)"
real=$(for f in /proc/$NPID/fd/* /proc/$SPID/fd/*; do readlink "$f"; done 2>/dev/null | grep -c '^/tmp/gov-os-heavy-slot')
is "$real" 0 "C2 no planted process opens a real /tmp slot file"
is "$(probe "$BED/pb/before/dispatcher.py")" outside "C3 before: the nightly's suite run is outside a slot (the incident, reproduced)"
is "$(probe "$BED/pb/after/dispatcher.py")" in-slot "C4 after: the nightly's suite run is in a slot"
mv "$PN/orch/NIGHTLY-RUNNING" "$PN/orch/NR.kept"
is "$(probe "$BED/pb/after/dispatcher.py")" outside "C5 after, NIGHTLY-RUNNING absent: outside"
mv "$PN/orch/NR.kept" "$PN/orch/NIGHTLY-RUNNING"; touch -d '361 minutes ago' "$PN/orch/NIGHTLY-RUNNING"
is "$(probe "$BED/pb/after/dispatcher.py")" outside "C6 after, NIGHTLY-RUNNING 361 minutes old: outside"
touch "$PN/orch/NIGHTLY-RUNNING"
is "$(probe "$BED/pb/after/dispatcher.py")" in-slot "C7 after, the marker fresh again: in a slot"
end_nightly
start_nightly 0 ""
is "$(probe "$BED/pb/after/dispatcher.py")" outside "C8 after, a nightly that opens the slot files but holds no lock: outside"
end_nightly
start_nightly 1 "$PN/elsewhere"
is "$(probe "$BED/pb/after/dispatcher.py")" outside "C9 after, the nightly's run working outside its run folder: outside"
end_nightly
mkdir -p "$PN/runs/nightly/20261113-0404"
( cd "$PN/runs/nightly/20261113-0404" && exec python3 -c "import time; time.sleep(20)" -m pytest tests ) &
SPID=$!; sleep 0.5
is "$(probe "$BED/pb/after/dispatcher.py")" outside "C10 after, a heavy step in a nightly clone folder with a fresh marker but no nightly.sh above it: outside"
bash "$PROCSH" stop --grace 2 "$SPID" > /dev/null
unset DISPATCH_ORCH DISPATCH_STATE DISPATCH_SLOT_GLOB DISPATCH_NIGHTLY_RUNS

echo "--- D. the unit tests (through heavy_slot.sh, TMPDIR in the bed)"
git apply "$ACT/followup-tests.diff"; r $? "D1 the follow-up tests apply to the clone"
bash "$ACT/apply.sh" undo > /dev/null
bash "$HEAVY" python3 -m pytest -q -p no:cacheprovider "$T" -k nightly_slot --optin=lifted,breadth > "$BED/d-before.txt" 2>&1
echo "     before: $(tail -1 "$BED/d-before.txt" | mask)"
is "$(grep -c '^FAILED' "$BED/d-before.txt")|$(grep -o '[0-9]* passed' "$BED/d-before.txt" | tail -1)" \
   "2|7 passed" "D2 before: the two in-slot cases red (the nightly's run, and beside a step elsewhere), the seven outside cases green"
bash "$ACT/apply.sh" apply > /dev/null
bash "$HEAVY" python3 -m pytest -q -p no:cacheprovider "$T" -k nightly_slot --optin=lifted,breadth > "$BED/d-after.txt" 2>&1
echo "     after: $(tail -1 "$BED/d-after.txt" | mask)"
grep -q '^9 passed' <(tail -1 "$BED/d-after.txt" | sed 's/^=* *//'); r $? "D3 after: the nine new cases green"
bash "$HEAVY" python3 -m pytest -q -p no:cacheprovider "$T" > "$BED/d-all.txt" 2>&1
rc=$?; echo "     the whole dispatcher suite after: $(tail -1 "$BED/d-all.txt" | mask)"
is "$rc" 0 "D4 after: the whole of test_dispatcher.py green"
git checkout -q -- "$T"

echo "--- E. undo and refusals"
out=$(bash "$ACT/apply.sh" undo); rc=$?; echo "     $out"
is "$rc" 0 "E1 undo (exit 0)"
cmp -s "$P" "$ACT/before/repo/$P"; r $? "E2 undone byte for byte"
out=$(bash "$ACT/apply.sh" check); rc=$?; is "$rc|${out%% (*}" "0|state before" "E3 check: state before (exit 0)"
echo "# a later change" >> "$P"
bash "$ACT/apply.sh" apply 2>&1 | mask | sed 's/^/     /'; is "${PIPESTATUS[0]}" 3 "E4 apply refuses a dispatcher changed since the freeze (exit 3)"
cp "$ACT/after/repo/$P" "$P"; echo "# a later change" >> "$P"
bash "$ACT/apply.sh" undo 2>&1 | mask | sed 's/^/     /'; is "${PIPESTATUS[0]}" 3 "E5 undo refuses it too (exit 3)"
bash "$ACT/apply.sh" verify 2>/dev/null; is "$?" 3 "E6 verify refuses it (exit 3)"
git checkout -q -- "$P"
ln -sf "$ACT/after/repo/$P" "$BED/link.py"; mv "$P" "$BED/real.py"; ln -s "$BED/link.py" "$P"
bash "$ACT/apply.sh" check 2>/dev/null; is "$?" 3 "E7 a link in the file's place is refused"
rm "$P"; mv "$BED/real.py" "$P"

echo "--- F. the main tree"
is "$(sha256sum "$REPO/$P" | cut -c1-64)" "$main_before" "F1 the main tree's dispatcher is unchanged"
is "$(git -C "$REPO" status --porcelain -- governance tests src | sha256sum | cut -c1-64)" "$main_status" "F2 the main tree's tracked governance/tests/src status unchanged"
echo "=== $ok ok, $bad failed"
echo "failures: $bad"
