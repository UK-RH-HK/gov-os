#!/usr/bin/env bash
# DEC-868 item 2: before committing my own edits to the register, the plan, the path map, tickets or briefs, run
# the governance checks those files feed, as the runner runs them (the tree's src until W2-59 lands). Until the
# hooks are back on (W2-08). Prints one line per check; exits non-zero if any is not green.
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
OUT=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/record-checks
mkdir -p "$OUT"
status=0
for pair in "core-pathmap gov.check.pathmap" "core-schema gov.check.schema" "core-mutation gov.check.mutation" \
            "core-authority gov.check.authority" "core-graph gov.check.graph" \
            "context-reproducibility gov.context.context_check"; do
  set -- $pair
  PYTHONPATH=/home/usain/Dynamic-Agentic-Engineering-OS/src timeout 900 python3 -m "$2" > "$OUT/$1.out" 2>&1
  code=$?
  echo "$1 exit $code"
  [ "$code" -eq 0 ] || status=1
done
# P-H-1 (owner, 2026-10-21, DEC-887): the suites that read the records themselves, before my record commits too,
# not only before a close (the queue's gate (f), which also runs W2-54's green-here cases after its rebuild: they
# need a fresh store, which a record edit never has).
env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONPATH=/home/usain/Dynamic-Agentic-Engineering-OS/src timeout 900 \
  python3 -m pytest -q -p no:cacheprovider --no-header tests/acceptance/W1-06/test_w1_06_approvals.py \
  tests/acceptance/W1-08/test_w1_08_path_map.py tests/acceptance/W1-27/test_w1_27_path_compliance_r2.py \
  tests/acceptance/W1-07/test_w1_07_envelope.py tests/acceptance/W1-33/test_w1_33_agent_definitions.py \
  tests/acceptance/W1-49/test_w1_49_threshold.py > "$OUT/record-reading.out" 2>&1
code=$?
echo "record-reading suites exit $code: $(tail -1 "$OUT/record-reading.out")"
[ "$code" -eq 0 ] || status=1
# DEC-893 (owner, standing): no placeholder ("00:2x", "xx", "TBD", "<…>" in an entry) in any prepared entry, patch or
# record before it reaches the owner or a commit: uncommitted changes, untracked files and the prepared patches.
python3 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/placeholder_scan.py > "$OUT/placeholders.out" 2>&1
code=$?
echo "placeholder scan exit $code: $(tail -1 "$OUT/placeholders.out")"
[ "$code" -eq 0 ] || { status=1; grep '^placeholder:' "$OUT/placeholders.out" | head -10; }
exit $status
