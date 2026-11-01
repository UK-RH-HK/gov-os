#!/bin/bash
# Re-run the two timing failures of the serial run alone, after the other suites ended, in the serial form.
cd /home/usain/gov-os-worktrees/W2-95 || exit 9
export TMPDIR=/tmp/gov-os-lead-W2-95
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
python3 -c "import os; print('load at start', os.getloadavg())" > /home/usain/gov-os-worktrees/W2-95/.gov-runtime/scratch/lead/log/rerun-timing.txt
A=tests/acceptance/W2-57/test_w2_57_designer_read_p95.py
B=tests/acceptance/W2-54/test_w2_54_green_here.py::test_gov_check_gives_context_reproducibility_green_here
for T in "$A" "$B"; do
  GIVEN="$T"
  PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-95/src:/home/usain/gov-os-worktrees/W2-95/src/gov/close/pytest_plugin GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-95 GOV_CLOSE_SERIAL_ONLY_GIVEN="$GIVEN" PYTHONDONTWRITEBYTECODE=1 python3 -B -m pytest -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rf "$T" >> /home/usain/gov-os-worktrees/W2-95/.gov-runtime/scratch/lead/log/rerun-timing.txt 2>&1
  echo "exit=$? for $T" >> /home/usain/gov-os-worktrees/W2-95/.gov-runtime/scratch/lead/log/rerun-timing.txt
  python3 -c "import os; print('load after', os.getloadavg())" >> /home/usain/gov-os-worktrees/W2-95/.gov-runtime/scratch/lead/log/rerun-timing.txt
done
echo done > /home/usain/gov-os-worktrees/W2-95/.gov-runtime/scratch/lead/log/rerun-timing.exit
