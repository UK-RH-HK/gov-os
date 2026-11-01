#!/bin/bash
# Re-run W2-54's one serial red alone, in the close's form (DEC-953 item 4: a red that passes alone is a flaky candidate).
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
cd /home/usain/gov-os-worktrees/W2-16 || exit 9
PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH TMPDIR=/tmp/gov-os-lead-W2-16 \
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src:/home/usain/gov-os-worktrees/W2-16/src/gov/close/pytest_plugin \
  GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-16 \
  GOV_CLOSE_SERIAL_ONLY_GIVEN=tests/acceptance/W2-54/test_w2_54_sandboxed_worker.py \
  python3 -m pytest "tests/acceptance/W2-54/test_w2_54_sandboxed_worker.py::test_inside_a_launched_sandboxed_worker_one_text_gets_one_answer_where_the_cache_cannot_be_written" \
  -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rfEs \
  > /home/usain/gov-os-worktrees/W2-16/.gov-runtime/scratch/lead/log/verify-4/w2-54-alone.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-16/.gov-runtime/scratch/lead/log/verify-4/w2-54-alone.exit
