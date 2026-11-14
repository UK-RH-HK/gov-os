cd /home/usain/gov-os-worktrees/W2-116
env PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-116/src HOME=/home/usain/gov-os-worktrees/W2-116/.gov-runtime/scratch/empty-home \
 bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/unit/rebuild tests/unit/status tests/unit/retrieval tests/unit/retrieve -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" > .gov-runtime/scratch/eng/units.out 2>&1
echo $? > .gov-runtime/scratch/eng/units.rc
