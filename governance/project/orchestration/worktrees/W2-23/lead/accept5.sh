cd /home/usain/gov-os-worktrees/W2-23 || exit 2
mkdir -p /tmp/w2-23-lead5
L=/home/usain/gov-os-worktrees/W2-23/.gov-runtime/scratch/lead/log
S=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh
git rev-parse HEAD > $L/accept-5.head
env TMPDIR=/tmp/w2-23-lead5 PYTHONUSERBASE=/home/usain/.local bash $S gov accept W2-23 --root /home/usain/gov-os-worktrees/W2-23 > $L/accept-5.txt 2>&1
echo "accept exit $?" >> $L/accept-5.txt
env TMPDIR=/tmp/w2-23-lead5 HOME=/home/usain/gov-os-worktrees/W2-23/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-23/src bash $S python3 -m pytest tests/acceptance/W1-41/test_w1_41_migration.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed > $L/w1-41-5.txt 2>&1
echo "w1-41 exit $?" >> $L/w1-41-5.txt
echo done > $L/accept-5.exit
