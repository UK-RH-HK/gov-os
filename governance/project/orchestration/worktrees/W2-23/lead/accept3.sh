cd /home/usain/gov-os-worktrees/W2-23
gov accept W2-23 --root /home/usain/gov-os-worktrees/W2-23 > .gov-runtime/scratch/lead/log/accept-3.txt 2>&1
echo "accept exit $?" >> .gov-runtime/scratch/lead/log/accept-3.txt
env HOME=/home/usain/gov-os-worktrees/W2-23/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-23/src python3 -m pytest tests/acceptance/W1-41/test_w1_41_migration.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed > .gov-runtime/scratch/lead/log/w1-41-3.txt 2>&1
echo "w1-41 exit $?" >> .gov-runtime/scratch/lead/log/w1-41-3.txt
