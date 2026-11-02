#!/bin/bash
# verify_r2.sh: the scoped run once (DEC-952, DEC-968), in the close's form: the parallel part, then the selected
# serial-only cases alone, each under verify_lock.sh, each with JUnit XML, never -x. Output in log/verify-r2/.
T=/home/usain/gov-os-worktrees/W2-123
L=$T/.gov-runtime/scratch/lead
O=$L/log/verify-r2
LOCK=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh
cd "$T" || exit 2
mapfile -t OPTS < <(python3 -c 'import json,sys; [print(o) for o in json.load(open(sys.argv[1]))["pytest_options"]]' "$O/select.json")
mapfile -t SERIAL < <(python3 "$L/serial_kept.py" "$O/select.json" tests/acceptance/serial-only.txt)
printf '%s\n' "${SERIAL[@]}" > "$O/serial-kept.txt"
echo "options: ${#OPTS[@]}; serial kept: ${#SERIAL[@]}" > "$O/plan.txt"
export PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH
export PYTHONPATH=$T/src:$T/src/gov/close/pytest_plugin
export GOV_CLOSE_SERIAL_ONLY_OF=$T
export TMPDIR=/tmp/gov-os-lead-W2-123
bash "$LOCK" python3 -m pytest tests -n auto -q -p no:cacheprovider -p gov_close_serial_only \
  -o tmp_path_retention_policy=failed -rs "${OPTS[@]}" --junitxml="$O/parallel.xml" > "$O/parallel.log" 2>&1
echo $? > "$O/parallel.exit"
if [ "${#SERIAL[@]}" -gt 0 ]; then
  GOV_CLOSE_SERIAL_ONLY_GIVEN="$(printf '%s\n' "${SERIAL[@]}")" bash "$LOCK" python3 -m pytest "${SERIAL[@]}" -q \
    -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs "${OPTS[@]}" \
    --junitxml="$O/serial.xml" > "$O/serial.log" 2>&1
  echo $? > "$O/serial.exit"
else
  echo "no serial-only case selected" > "$O/serial.log"; echo 0 > "$O/serial.exit"
fi
echo done > "$O/DONE"
