#!/bin/bash
# Run 5: the lead's check of W1-02's three revised deadline files on this ticket's head, outside the sandbox,
# after the load gate (DEC-847, DEC-961). Writes log/check5-W1-02.txt and .exit, with JUnit XML.
cd /home/usain/gov-os-worktrees/W2-05 || exit 9
LOG=/home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead/log
rm -f "$LOG/check5-W1-02.exit"
until python3 -c "import os; l=os.getloadavg(); exit(0 if min(l[0], l[2]) < os.cpu_count() else 1)"; do sleep 60; done
date > "$LOG/check5-W1-02.start"
cat /proc/loadavg >> "$LOG/check5-W1-02.start"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -c "import gov; print(gov.__file__)" > "$LOG/check5-import.txt" 2>&1
TMPDIR=/tmp/gov-os-lead-W2-05 PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src \
  python3 -m pytest tests/acceptance/W1-02/test_w1_02_deadline.py tests/acceptance/W1-02/test_w1_02_deadline_in_time.py \
  tests/acceptance/W1-02/test_w1_02_unknown_tools_failure.py -q -p no:cacheprovider -rfEs \
  -o tmp_path_retention_policy=failed --junitxml=/home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead/log/check5-W1-02.xml \
  > "$LOG/check5-W1-02.txt" 2>&1
echo $? > "$LOG/check5-W1-02.exit"
cat /proc/loadavg >> "$LOG/check5-W1-02.start"
date >> "$LOG/check5-W1-02.start"
