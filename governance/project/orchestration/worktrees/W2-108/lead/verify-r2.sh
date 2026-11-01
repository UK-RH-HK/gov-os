#!/bin/bash
# Run 2 (DEC-977): the named suites, alone and to their end; then collect-only.
cd /home/usain/gov-os-worktrees/W2-108 || exit 9
export TMPDIR=/tmp/gov-os-lead-W2-108
L=/home/usain/gov-os-worktrees/W2-108/.gov-runtime/scratch/lead/log
SRC=/home/usain/gov-os-worktrees/W2-108/src
until python3 /home/usain/gov-os-worktrees/W2-108/.gov-runtime/scratch/lead/loadok.py; do sleep 60; done
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh > /home/usain/gov-os-worktrees/W2-108/.gov-runtime/scratch/lead/log/r2-disk.txt 2>&1
PYTHONPATH=$SRC python3 -c "import gov; print(gov.__file__)" > /home/usain/gov-os-worktrees/W2-108/.gov-runtime/scratch/lead/log/r2-gov-file.txt 2>&1
PYTHONPATH=$SRC python3 -m pytest tests/acceptance/W2-108 tests/unit/retrieval/test_w2_108_freshness_once.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs --junitxml=/home/usain/gov-os-worktrees/W2-108/.gov-runtime/scratch/lead/log/r2-own.xml > /home/usain/gov-os-worktrees/W2-108/.gov-runtime/scratch/lead/log/r2-own.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-108/.gov-runtime/scratch/lead/log/r2-own.exit
PYTHONPATH=$SRC python3 -m pytest tests/acceptance/W1-28/test_w1_28_fixture_copies.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs --junitxml=/home/usain/gov-os-worktrees/W2-108/.gov-runtime/scratch/lead/log/r2-w128.xml > /home/usain/gov-os-worktrees/W2-108/.gov-runtime/scratch/lead/log/r2-w128.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-108/.gov-runtime/scratch/lead/log/r2-w128.exit
PYTHONPATH=$SRC python3 -m pytest tests/acceptance/W1-50/test_w1_50_freeze_fixture_settings.py -v -p no:cacheprovider -o tmp_path_retention_policy=failed -rs --junitxml=/home/usain/gov-os-worktrees/W2-108/.gov-runtime/scratch/lead/log/r2-w150.xml > /home/usain/gov-os-worktrees/W2-108/.gov-runtime/scratch/lead/log/r2-w150.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-108/.gov-runtime/scratch/lead/log/r2-w150.exit
PYTHONPATH=$SRC python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header > /home/usain/gov-os-worktrees/W2-108/.gov-runtime/scratch/lead/log/r2-collect.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-108/.gov-runtime/scratch/lead/log/r2-collect.exit
echo done > /home/usain/gov-os-worktrees/W2-108/.gov-runtime/scratch/lead/log/r2-verify.done
