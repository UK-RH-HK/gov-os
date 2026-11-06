#!/usr/bin/env bash
# Tests for lead_verify.sh (TPL-3b) in a temporary repository with a stub suite: a stand-in select_tests.py (its JSON
# from a file), the product's own serial phase and serial-only plugin (copied single files), the real heavy_slot.sh
# with private lock files, and a few one-line tests that record where they ran.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
T=$HERE/lead_verify.sh
REAL=/home/usain/Dynamic-Agentic-Engineering-OS/src/gov/close
W=$(mktemp -d "${TMPDIR:-/tmp}/gov-os-test-lead-verify.XXXXXX")
fails=0
ok() { echo "ok   $1"; }
no() { echo "FAIL $1"; fails=$((fails+1)); }
check() { if eval "$2"; then ok "$1"; else no "$1"; fi; }

R=$W/W2-99   # the stub tree
mkdir -p "$R/src/gov/close/pytest_plugin" "$R/tests/acceptance" "$W/rec"
cp "$REAL/serial.py" "$R/src/gov/close/serial.py"
cp "$REAL/pytest_plugin/gov_close_serial_only.py" "$R/src/gov/close/pytest_plugin/"
: > "$R/src/gov/__init__.py"; : > "$R/src/gov/close/__init__.py"; : > "$R/src/gov/close/pytest_plugin/__init__.py"
cat > "$R/src/gov/close/select.py" <<'PY'
def _norm(target):
    return target.rstrip("/")


def runs(entry, ignore, deselect):  # the product's gov.close.select.runs, word for word
    file = entry.partition("::")[0]
    if any(file == _norm(i) or file.startswith(_norm(i) + "/") for i in ignore):
        return False
    return not any(entry == d or entry.startswith(d + "::") or entry.startswith(d + "[") for d in deselect)
PY
printf '[pytest]\n' > "$R/pytest.ini"
cat > "$R/tests/acceptance/serial-only.txt" <<'TXT'
tests/test_serial.py  # serial: load: the stub's serial case
tests/test_night.py  # nightly: real: routed to the nightly, never run here
TXT
cat > "$R/tests/rec.py" <<'PY'
import os, sys
def rec(name):
    with open(os.path.join(os.environ["STUB_REC"], name), "w") as f:
        f.write(f"slot={os.environ.get('GOV_HEAVY_SLOT')} worker={os.environ.get('PYTEST_XDIST_WORKER')} "
                f"tmp={os.environ.get('TMPDIR')}\n")
PY
cat > "$R/tests/test_a.py" <<'PY'
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from rec import rec
def test_one():
    rec("a_one")
    assert not os.environ.get("STUB_RED")
def test_two():
    rec("a_two")
PY
cat > "$R/tests/test_serial.py" <<'PY'
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from rec import rec
def test_s():
    rec("serial")
PY
cat > "$R/tests/test_night.py" <<'PY'
def test_never_here():
    open(__import__("os").environ["STUB_REC"] + "/night", "w").write("ran\n")
    assert False, "a nightly-routed entry ran in a lead's verification"
PY
git -C "$R" init -q && git -C "$R" add -A && git -C "$R" -c user.name=t -c user.email=t@t commit -qm stub
cat > "$W/select.py" <<'PY'
import os, sys
sys.stdout.write(open(os.environ["STUB_SELECT_JSON"]).read())
sys.exit(int(os.environ.get("STUB_SELECT_RC", "0")))
PY
sel() { printf '%s\n' "$1" > "$W/sel.json"; }
export STUB_REC=$W/rec STUB_SELECT_JSON=$W/sel.json LEAD_VERIFY_SELECT=$W/select.py LEAD_VERIFY_TMPDIR=$W/tmp
export GOV_HEAVY_DIR=$W/slots GOV_HEAVY_SLOTS=2; mkdir -p "$GOV_HEAVY_DIR"
OUT=$R/.gov-runtime/scratch/lead/log/verify
run() { rm -f "$W"/rec/*; bash "$T" --fg "$R" W2-99 T-1 > "$W/stdout" 2>&1; }

# 1. usage
bash "$T" > /dev/null 2>&1; check "no arguments: exit 2" '[ $? = 2 ]'
bash "$T" --fg "$W/nowhere" W2-99 T-1 > /dev/null 2>&1; check "no tree: exit 2" '[ $? = 2 ]'

# 2. green: the selection, the parallel run, then the serial phase's own entries, each in a heavy slot
sel '{"scope": "scoped", "nothing_to_run": false, "pytest_options": [], "ignore": [], "deselect": []}'
run; rc=$?
check "green: exit 0" '[ $rc = 0 ]'
check "green: the exit file holds 0" '[ "$(cat "$OUT/verify.exit")" = 0 ]'
check "green: one summary line, GREEN, the head named" '[ "$(wc -l < "$OUT/summary.txt")" = 1 ] && grep -q "lead_verify W2-99 T-1 head [0-9a-f]\{12\}: GREEN" "$OUT/summary.txt"'
check "green: the summary line printed" 'grep -q GREEN "$W/stdout"'
check "green: two JUnit files" '[ -s "$OUT/parallel.xml" ] && [ -s "$OUT/serial.xml" ]'
check "green: the parallel run held test_a's two cases only" 'grep -q "parallel exit 0 in [0-9]* s (2 tests 0 failed" "$OUT/summary.txt"'
check "green: the serial phase ran its one entry" 'grep -q "serial exit 0 in [0-9]* s, 1 entries (1 tests 0 failed" "$OUT/summary.txt"'
check "green: the parallel cases ran in a heavy slot, under xdist" 'grep -q "slot=[0-9] worker=gw" "$W/rec/a_one"'
check "green: the serial case ran in a heavy slot, in one process" 'grep -q "slot=[0-9] worker=None" "$W/rec/serial"'
check "green: the runs used LEAD_VERIFY_TMPDIR" 'grep -q "tmp=$W/tmp" "$W/rec/a_one"'
check "green: the nightly-routed entry ran nowhere" '[ ! -e "$W/rec/night" ]'
check "green: the selection's JSON kept" 'grep -q scoped "$OUT/select.json"'

# 3. the serial phase runs only what the selection runs
sel "{\"scope\": \"scoped\", \"nothing_to_run\": false, \"pytest_options\": [\"--ignore=$R/tests/test_serial.py\"], \"ignore\": [\"tests/test_serial.py\"], \"deselect\": []}"
run; rc=$?
check "a serial entry the selection ignores: not run, exit 0" '[ $rc = 0 ] && [ ! -e "$W/rec/serial" ]'
check "no serial entry: an empty serial.xml, 0 entries" 'grep -q "0 entries (0 tests" "$OUT/summary.txt" && grep -q "tests=\"0\"" "$OUT/serial.xml"'
check "an earlier folder is moved aside, never removed" 'ls -d "$OUT".* > /dev/null 2>&1'
sel '{"scope": "scoped", "nothing_to_run": false, "pytest_options": ["--deselect=tests/test_a.py::test_two"], "ignore": [], "deselect": ["tests/test_a.py::test_two"]}'
run; check "the selection's options reach the parallel run (a deselect)" '[ ! -e "$W/rec/a_two" ] && [ -e "$W/rec/a_one" ]'

# 4. a red
sel '{"scope": "scoped", "nothing_to_run": false, "pytest_options": [], "ignore": [], "deselect": []}'
STUB_RED=1 run; rc=$?
check "red: exit 1, RED, the exit file 1" '[ $rc = 1 ] && grep -q ": RED parallel exit 1" "$OUT/summary.txt" && [ "$(cat "$OUT/verify.exit")" = 1 ]'

# 5. the selection refused
STUB_SELECT_RC=2 run; rc=$?
check "selection refused: exit 2, named, no pytest" '[ $rc = 2 ] && grep -q "selection refused" "$OUT/summary.txt" && [ ! -e "$OUT/parallel.txt" ]'

# 6. nothing to run
sel '{"scope": "scoped", "nothing_to_run": true, "pytest_options": [], "ignore": [], "deselect": []}'
run; rc=$?
check "nothing to run: exit 0, no pytest started, two empty JUnit files" '[ $rc = 0 ] && grep -q "nothing to run" "$OUT/summary.txt" && [ ! -e "$OUT/parallel.txt" ] && [ -s "$OUT/serial.xml" ] && [ ! -e "$W/rec/a_one" ]'

# 7. a run that did not complete (pytest's usage error)
sel '{"scope": "scoped", "nothing_to_run": false, "pytest_options": ["--no-such-option"], "ignore": [], "deselect": []}'
run; rc=$?
check "an incomplete run: exit 3, INCOMPLETE" '[ $rc = 3 ] && grep -q INCOMPLETE "$OUT/summary.txt"'

# 8. detached by default; wait_for.sh reads its exit file, pid and summary
sel '{"scope": "scoped", "nothing_to_run": false, "pytest_options": [], "ignore": [], "deselect": []}'
s=$(date +%s); bash "$T" "$R" W2-99 T-1 > "$W/stdout" 2>&1; rc=$?; e=$(( $(date +%s) - s ))
check "detached: returns at once (${e}s <= 2), exit 0" '[ $rc = 0 ] && [ $e -le 2 ]'
check "detached: prints the wait line" 'grep -q "wait_for.sh $OUT/verify.exit" "$W/stdout"'
pid=$(cat "$OUT/verify.pid")
check "detached: its own process group" '[ "$(ps -o pgid= -p "$pid" | tr -d " ")" = "$pid" ] || [ -s "$OUT/verify.exit" ]'
out=$(WAIT_FOR_EVERY=1 bash "$HERE/wait_for.sh" "$OUT/verify.exit" 120); rc=$?
check "detached: wait_for.sh gives DONE exit 0 and the summary" '[ $rc = 0 ] && grep -q "DONE exit 0" <<< "$out" && grep -q GREEN <<< "$out"'

# 9. the form: under heavy_slot.sh, the product's serial phase, no pgrep
grep -q 'gov.close.serial import phase' "$T"; check "the serial entries come from gov.close.serial.phase" '[ $? = 0 ]'
[ "$(grep -c 'bash "$SLOT" python3 -m pytest' "$T")" = 2 ]; check "both runs go through the heavy slot" '[ $? = 0 ]'
! grep -Eq '(^|[^a-z_])(pgrep|pkill|killall)([^a-z_]|$)' "$T"; check "no pgrep, pkill or killall" '[ $? = 0 ]'

rm -rf "$W"
echo "$([ $fails = 0 ] && echo PASS || echo "FAILED $fails") test_lead_verify.sh"
[ $fails = 0 ]
