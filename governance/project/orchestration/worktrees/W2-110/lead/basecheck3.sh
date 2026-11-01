#!/bin/bash
# Re-run the scoped run's failing cases (in the close's form) and the serial latency cases alone, on a given tree,
# to tell the reds this ticket causes from those it does not (DEC-968), and to re-run load-sensitive cases alone.
# Usage: basecheck3.sh <tree> <label> [serial-only]
T="$1"
L="$2"
LOG=/home/usain/gov-os-worktrees/W2-110/.gov-runtime/scratch/lead/log/base3
mkdir -p /home/usain/gov-os-worktrees/W2-110/.gov-runtime/scratch/lead/log/base3
cd "$T" || exit 9
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
echo "tree $(git rev-parse --short=12 HEAD) load $(cut -d' ' -f1-3 /proc/loadavg)"
PYTHONPATH="$T/src" python3 -c "import gov; print(gov.__file__)"
export TMPDIR=/tmp/gov-os-lead-W2-110
export PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH
export PYTHONPATH="$T/src:$T/src/gov/close/pytest_plugin"
export GOV_CLOSE_SERIAL_ONLY_OF="$T"
if [ "$3" != "serial-only" ]; then
  mapfile -t IDS < /home/usain/gov-os-worktrees/W2-110/.gov-runtime/scratch/lead/log/basecheck3-ids.txt
  python3 -m pytest -n auto -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs --junitxml="$LOG/$L-parallel.xml" "${IDS[@]}" | tail -n 3
fi
mapfile -t SER < /home/usain/gov-os-worktrees/W2-110/.gov-runtime/scratch/lead/log/serial3-ids.txt
GOV_CLOSE_SERIAL_ONLY_GIVEN="$(cat /home/usain/gov-os-worktrees/W2-110/.gov-runtime/scratch/lead/log/serial3-ids.txt)" python3 -m pytest -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs --junitxml="$LOG/$L-serial.xml" "${SER[@]}" | tail -n 2
echo "end load $(cut -d' ' -f1-3 /proc/loadavg)"
