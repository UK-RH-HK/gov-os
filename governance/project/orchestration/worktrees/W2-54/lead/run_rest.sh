#!/bin/sh
# The builder tests, then the load-sensitive cases alone (DEC-372, DEC-760, DEC-762), each to its end.
cd /home/usain/gov-os-worktrees/W2-54 || exit 2
export PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src
uptime > /home/usain/gov-os-worktrees/W2-54/.gov-runtime/scratch/lead/log/v2-unit.load
python3 -m pytest tests/unit -q -p no:cacheprovider > /home/usain/gov-os-worktrees/W2-54/.gov-runtime/scratch/lead/log/v2-unit.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-54/.gov-runtime/scratch/lead/log/v2-unit.exit
export PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH
uptime > /home/usain/gov-os-worktrees/W2-54/.gov-runtime/scratch/lead/log/alone.load
python3 -m pytest "tests/acceptance/W1-02/test_w1_02_guard_hook.py::test_decision_p95_is_under_100_ms" -q -p no:cacheprovider -rs > /home/usain/gov-os-worktrees/W2-54/.gov-runtime/scratch/lead/log/alone-W1-02.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-54/.gov-runtime/scratch/lead/log/alone-W1-02.exit
python3 -m pytest "tests/acceptance/W1-05/test_w1_05_switch_over_record.py::test_the_dependencies_pass_their_acceptance_tests_at_the_switch_over" -q -p no:cacheprovider -rs > /home/usain/gov-os-worktrees/W2-54/.gov-runtime/scratch/lead/log/alone-W1-05.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-54/.gov-runtime/scratch/lead/log/alone-W1-05.exit
python3 -m pytest tests/acceptance/W1-46/test_w1_46_live_sessions.py -q -p no:cacheprovider -rs > /home/usain/gov-os-worktrees/W2-54/.gov-runtime/scratch/lead/log/alone-W1-46.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-54/.gov-runtime/scratch/lead/log/alone-W1-46.exit
uptime >> /home/usain/gov-os-worktrees/W2-54/.gov-runtime/scratch/lead/log/alone.load
echo done > /home/usain/gov-os-worktrees/W2-54/.gov-runtime/scratch/lead/log/rest.exit
