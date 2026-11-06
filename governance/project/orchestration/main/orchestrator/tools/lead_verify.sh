#!/usr/bin/env bash
# A lead's verification in one command (TPL-3b: R3-TEMPLATES D, TPL-3 S5; R2-6, R2-9; DEC-1052, DEC-1079): the
# scoped selection (select_tests.py; DEC-952, DEC-968), the parallel run, then the serial phase, only the entries the
# product's own gov.close.serial.phase selects and the selection runs (DEC-1050 T-5; close_build.py's filter), each
# under heavy_slot.sh (DEC-979 D1, DEC-1038 (4)), in the close's form (LEAD-w2-common, the loop's step 4).
#   lead_verify.sh [--fg] <tree> <W2> <ID>
# By default it detaches (its own session and process group, so the Bash tool's limits never cut the run) and prints
# the folder, the exit file and the pid; wait with `wait_for.sh <out>/verify.exit`. --fg runs here and exits with the
# code. <out> is LEAD_VERIFY_OUT, default <tree>/.gov-runtime/scratch/lead/log/verify (an earlier one is moved aside
# to verify.<time>, never removed). It holds select.json, parallel.xml and serial.xml (an empty suite when no entry is
# selected), parallel.txt and serial.txt (pytest's output), verify.log, verify.pid, summary.txt (the one summary line,
# also printed; wait_for.sh prints it as verify.summary) and verify.exit (the code, written last).
# Exit: 0 green; 1 a red (a failure or an error in either JUnit file); 2 the selection refused, or a usage error;
# 3 a run did not complete (pytest's exit not 0 or 1, or a JUnit file missing).
# Env: LEAD_VERIFY_TMPDIR (default /tmp/gov-os-lead-<W2>); LEAD_VERIFY_SELECT, LEAD_VERIFY_SLOT (other tools, tests).
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
NODE=/home/usain/.nvm/versions/node/v22.23.3/bin
fg=""; [ "${1:-}" = --fg ] && { fg=1; shift; }
[ $# = 3 ] || { sed -n 2,15p "$0"; exit 2; }
tree=$(readlink -f "$1") W2=$2 ID=$3
[ -d "$tree/tests" ] && [ -d "$tree/src" ] || { echo "lead_verify: not a tree with src/ and tests/: $1" >&2; exit 2; }
out=${LEAD_VERIFY_OUT:-$tree/.gov-runtime/scratch/lead/log/verify}
SELECT=${LEAD_VERIFY_SELECT:-$HERE/select_tests.py} SLOT=${LEAD_VERIFY_SLOT:-$HERE/heavy_slot.sh}
if [ -z "${LEAD_VERIFY_PREPARED:-}" ]; then  # a fresh folder for this run; the earlier one kept
  [ -e "$out" ] && mv "$out" "$out.$(date -r "$out" +%Y%m%d-%H%M%S)-$$"
  mkdir -p "$out" || exit 2
fi
if [ -z "$fg" ]; then
  LEAD_VERIFY_PREPARED=1 LEAD_VERIFY_OUT=$out setsid bash "$HERE/$(basename "$0")" --fg "$tree" "$W2" "$ID" < /dev/null > "$out/verify.log" 2>&1 &
  echo "$!" > "$out/verify.pid"
  echo "lead_verify: started pid $! (its own process group); folder $out"
  echo "lead_verify: wait with: bash $HERE/wait_for.sh $out/verify.exit"
  exit 0
fi
echo "$$" > "$out/verify.pid"
finish() {  # the summary line, then the exit file, last and whole
  echo "$1" | tee "$out/summary.txt"; cp "$out/summary.txt" "$out/verify.summary"
  echo "$2" > "$out/verify.exit.tmp" && mv "$out/verify.exit.tmp" "$out/verify.exit"; exit "$2"
}
empty() { echo '<?xml version="1.0" encoding="utf-8"?><testsuites><testsuite name="pytest" tests="0" failures="0" errors="0" skipped="0"/></testsuites>' > "$1"; }
head12=$(git -C "$tree" rev-parse HEAD 2>/dev/null | cut -c1-12)
tag="lead_verify $W2 $ID head $head12"
export TMPDIR=${LEAD_VERIFY_TMPDIR:-/tmp/gov-os-lead-$W2}; mkdir -p "$TMPDIR"
cd "$tree" || finish "$tag: cannot enter the tree" 2
# 1. the selection, with the tree's own code first (DEC-732)
PYTHONPATH="$tree/src" python3 "$SELECT" "$tree" "$W2" "$ID" > "$out/select.json" 2> "$out/select.err"
rc=$?
[ $rc = 0 ] || finish "$tag: selection refused (exit $rc; $out/select.json, select.err)" 2
# 2. the plan: the selection's pytest options; the serial phase's entries that the selection runs
plan=$(PYTHONPATH="$tree/src" python3 - "$tree" "$out" <<'PY'
import json, sys
from pathlib import Path
tree, out = Path(sys.argv[1]), Path(sys.argv[2])
sel = json.loads((out / "select.json").read_text())
from gov.close import select as gsel
from gov.close.pytest_plugin.gov_close_serial_only import entries
from gov.close.serial import phase
serial = [e for e in phase(tree, entries(tree)) if gsel.runs(e, sel.get("ignore", []), sel.get("deselect", []))]
(out / "parallel.args").write_text("".join(o + "\n" for o in sel.get("pytest_options", [])))
(out / "serial.entries").write_text("".join(e + "\n" for e in serial))
print("nothing" if sel.get("nothing_to_run") else "run", len(serial))
PY
) || finish "$tag: the plan could not be made (the serial phase or the selection's JSON)" 2
read -r what nser <<< "$plan"
if [ "$what" = nothing ]; then
  empty "$out/parallel.xml"; empty "$out/serial.xml"
  finish "$tag: GREEN nothing to run (the selection's nothing_to_run); no pytest started" 0
fi
mapfile -t opts < "$out/parallel.args"; mapfile -t serial < "$out/serial.entries"
export PATH="$NODE:$PATH" PYTHONPATH="$tree/src:$tree/src/gov/close/pytest_plugin" GOV_CLOSE_SERIAL_ONLY_OF="$tree"
common=(-q -p no:cacheprovider --no-header -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs)
# 3. the parallel run (the plugin keeps every serial-only entry out of it)
t0=$(date +%s)
bash "$SLOT" python3 -m pytest tests -n auto "${common[@]}" "${opts[@]}" --junitxml="$out/parallel.xml" > "$out/parallel.txt" 2>&1
prc=$?
# 4. the serial phase: those entries alone, one process, in a slot
t1=$(date +%s) src=0
if [ "${#serial[@]}" -gt 0 ]; then
  GOV_CLOSE_SERIAL_ONLY_GIVEN=$(printf '%s\n' "${serial[@]}") PYTEST_XDIST_AUTO_NUM_WORKERS=1 \
    bash "$SLOT" python3 -m pytest "${serial[@]}" "${common[@]}" --junitxml="$out/serial.xml" > "$out/serial.txt" 2>&1
  src=$?
else
  empty "$out/serial.xml"; echo "no serial-only entry selected" > "$out/serial.txt"
fi
t2=$(date +%s)
sums=$(python3 -I - "$out/parallel.xml" "$out/serial.xml" <<'PY'
import sys, xml.etree.ElementTree as ET
for p in sys.argv[1:]:
    t = dict.fromkeys(("tests", "failures", "errors", "skipped"), 0)
    try:
        r = ET.parse(p).getroot()
    except (OSError, ET.ParseError):
        print("missing"); continue
    for s in ([r] if r.tag == "testsuite" else r.iter("testsuite")):
        for k in t:
            t[k] += int(s.get(k, 0))
    print(f"{t['tests']} tests {t['failures']} failed {t['errors']} errors {t['skipped']} skipped",
          "red" if t["failures"] or t["errors"] else "ok")
PY
)
psum=$(sed -n 1p <<< "$sums") ssum=$(sed -n 2p <<< "$sums")
line="parallel exit $prc in $((t1 - t0)) s (${psum% *}); serial exit $src in $((t2 - t1)) s, ${#serial[@]} entries (${ssum% *})"
for c in "$prc" "$src"; do [ "$c" = 0 ] || [ "$c" = 1 ] || finish "$tag: INCOMPLETE $line" 3; done
case "$psum $ssum" in *missing*) finish "$tag: INCOMPLETE $line" 3;; esac
[ "$prc$src" = 00 ] && [ "${psum##* }${ssum##* }" = okok ] && finish "$tag: GREEN $line" 0
finish "$tag: RED $line" 1
