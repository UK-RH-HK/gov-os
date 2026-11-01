#!/bin/bash
# Re-run this branch's failing W1-03/W1-46/W1-47/W1-50 cases on w2/integrate (a throwaway detached worktree under the
# lead's temp folder), in the close's form, to tell the reds this ticket causes from those it does not (DEC-968).
cd /tmp/gov-os-lead-W2-110/base-integrate || exit 9
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
git rev-parse --short=12 HEAD
PYTHONPATH=/tmp/gov-os-lead-W2-110/base-integrate/src python3 -c "import gov; print(gov.__file__)"
mapfile -t IDS < /home/usain/gov-os-worktrees/W2-110/.gov-runtime/scratch/lead/log/basecheck-ids.txt
TMPDIR=/tmp/gov-os-lead-W2-110 PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/tmp/gov-os-lead-W2-110/base-integrate/src:/tmp/gov-os-lead-W2-110/base-integrate/src/gov/close/pytest_plugin GOV_CLOSE_SERIAL_ONLY_OF=/tmp/gov-os-lead-W2-110/base-integrate python3 -m pytest -n auto -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs --junitxml=/home/usain/gov-os-worktrees/W2-110/.gov-runtime/scratch/lead/log/basecheck.xml "${IDS[@]}"
