#!/bin/bash
# Run 2 (resume) step 4: the full rebuild, the import check, the selection, then the scoped set in the close's form
# (one parallel run, then the selected serial-only cases alone), the collection check and gov check.
# Exit codes in log/*5.exit; log/verify5.done written at the end.
set -u
L=/home/usain/gov-os-worktrees/W2-107/.gov-runtime/scratch/lead/log
W=/home/usain/gov-os-worktrees/W2-107
T=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools
cd /home/usain/gov-os-worktrees/W2-107 || exit 4
export TMPDIR=/tmp/gov-os-lead-W2-107
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
bash "$T/disk_gate.sh" > "$L/disk-gate-verify5.txt" 2>&1 || { echo 3 > "$L/verify5.done"; exit 3; }
date -u +%FT%TZ > "$L/rebuild5.start"
flock /tmp/gov-os-rebuild.lock env PYTHONPATH=/home/usain/gov-os-worktrees/W2-107/src python3 -m gov.cli.main rebuild --json > "$L/rebuild5.json" 2> "$L/rebuild5.err"
echo $? > "$L/rebuild5.exit"
date -u +%FT%TZ > "$L/rebuild5.end"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-107/src python3 -c "import gov; print(gov.__file__)" > "$L/govfile5.txt"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-107/src python3 "$T/select_tests.py" /home/usain/gov-os-worktrees/W2-107 W2-107 DAEO-kiar > /tmp/gov-os-lead-W2-107/select.json 2> "$L/select5.err"
echo $? > "$L/select5.exit"
if [ "$(cat "$L/select5.exit")" != 0 ]; then echo 2 > "$L/verify5.done"; exit 2; fi
python3 /home/usain/gov-os-worktrees/W2-107/.gov-runtime/scratch/lead/verify_prep.py > "$L/prep5.txt" 2>&1
mapfile -t OPTS < /tmp/gov-os-lead-W2-107/options.txt
mapfile -t SERIAL < /tmp/gov-os-lead-W2-107/serial.txt
export PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH
export GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-107
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
bash "$T/disk_gate.sh" >> "$L/disk-gate-verify5.txt" 2>&1 || { echo 3 > "$L/verify5.done"; exit 3; }
du -s --inodes /tmp/gov-os-lead-W2-107 "$W/.gov-runtime" "$W/pytest-of-usain" > "$L/measure5-before.txt" 2>&1
du -sh /tmp/gov-os-lead-W2-107 "$W/.gov-runtime" "$W/pytest-of-usain" >> "$L/measure5-before.txt" 2>&1
date -u +%FT%TZ > "$L/parallel5.start"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-107/src:/home/usain/gov-os-worktrees/W2-107/src/gov/close/pytest_plugin bash "$T/verify_lock.sh" python3 -m pytest tests -n auto -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs --junitxml="$L/parallel5.xml" "${OPTS[@]}" > "$L/parallel5.out" 2>&1
echo $? > "$L/parallel5.exit"
date -u +%FT%TZ > "$L/serial5.start"
GOV_CLOSE_SERIAL_ONLY_GIVEN="$(cat /tmp/gov-os-lead-W2-107/serial.txt)" PYTHONPATH=/home/usain/gov-os-worktrees/W2-107/src:/home/usain/gov-os-worktrees/W2-107/src/gov/close/pytest_plugin bash "$T/verify_lock.sh" python3 -m pytest -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs --junitxml="$L/serial5.xml" "${OPTS[@]}" "${SERIAL[@]}" > "$L/serial5.out" 2>&1
echo $? > "$L/serial5.exit"
date -u +%FT%TZ > "$L/serial5.end"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-107/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header > "$L/collect5.out" 2>&1
echo $? > "$L/collect5.exit"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-107/src python3 -m gov.cli.main check --json > "$L/check5.json" 2> "$L/check5.err"
echo $? > "$L/check5.exit"
du -s --inodes /tmp/gov-os-lead-W2-107 "$W/.gov-runtime" "$W/pytest-of-usain" > "$L/measure5-after.txt" 2>&1
du -sh /tmp/gov-os-lead-W2-107 "$W/.gov-runtime" "$W/pytest-of-usain" >> "$L/measure5-after.txt" 2>&1
echo 0 > "$L/verify5.done"
