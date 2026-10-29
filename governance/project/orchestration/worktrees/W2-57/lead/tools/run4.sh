#!/usr/bin/env bash
# Run 4's verification, one part per call, each waiting for the gates first:
#   rebuild   full gov rebuild --json (never --no-embeddings)
#   check     gov check --json
#   parallel  tests/acceptance/W2-57 and tests/unit/close in the close's parallel form
#   serial    the serial-only entries in that scope, alone, as gov close's run afterwards
#   collect   pytest tests --collect-only in one process (DEC-868)
cd /home/usain/gov-os-worktrees/W2-57 || exit 1
V=/home/usain/gov-os-worktrees/W2-57/.gov-runtime/scratch/lead/log/run4
O=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
part="$1"
mkdir -p /tmp/gov-os-lead-W2-57
export TMPDIR=/tmp/gov-os-lead-W2-57
until [ ! -e "$O/CLOSE-RUNNING" ] && [ ! -e "$O/NIGHTLY-RUNNING" ]; do sleep 60; done
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
echo "$part start $(date '+%F %T') load $(cut -d' ' -f1-3 /proc/loadavg) | $(bash "$O/tools/disk_gate.sh")" >> "$V/times.txt"
SRC=/home/usain/gov-os-worktrees/W2-57/src
case "$part" in
  rebuild)
    PYTHONPATH=$SRC python3 -m gov.cli.main rebuild --json > "$V/rebuild.json" 2>&1; rc=$? ;;
  check)
    PYTHONPATH=$SRC python3 -m gov.cli.main check --json > "$V/check.json" 2>&1; rc=$? ;;
  parallel)
    PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=$SRC:$SRC/gov/close/pytest_plugin \
      GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-57 \
      flock /tmp/gov-os-verify.lock python3 -m pytest tests/acceptance/W2-57 tests/unit/close -n auto -q \
      -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs --tb=line \
      --junitxml="$V/parallel.xml" > "$V/parallel.txt" 2>&1; rc=$? ;;
  serial)
    mapfile -t E < "$V/serial-entries.txt"
    PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=$SRC:$SRC/gov/close/pytest_plugin \
      GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-57 GOV_CLOSE_SERIAL_ONLY_GIVEN="$(cat "$V/serial-entries.txt")" \
      flock /tmp/gov-os-verify.lock python3 -m pytest "${E[@]}" -q -p no:cacheprovider -p gov_close_serial_only \
      -o tmp_path_retention_policy=failed -rs --tb=line --junitxml="$V/serial.xml" > "$V/serial.txt" 2>&1; rc=$? ;;
  collect)
    PYTHONPATH=$SRC python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header > "$V/collect.txt" 2>&1; rc=$? ;;
  *) echo "unknown part $part"; exit 2 ;;
esac
echo "$part exit $rc end $(date '+%F %T') load $(cut -d' ' -f1-3 /proc/loadavg)" >> "$V/times.txt"
echo $rc > "$V/$part.exit"
