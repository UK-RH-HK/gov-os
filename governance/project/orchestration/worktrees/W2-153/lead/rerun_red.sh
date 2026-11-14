cd /home/usain/gov-os-worktrees/W2-153
mkdir -p /home/usain/gov-os-worktrees/W2-153/.gov-runtime/scratch/tmp-red
env TMPDIR=/tmp/w2-153-lead-red HOME=/home/usain/gov-os-worktrees/W2-153/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-153/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-02/test_w2_02_green_here.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed --tb=line
