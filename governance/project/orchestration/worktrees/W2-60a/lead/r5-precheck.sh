cd /home/usain/gov-os-worktrees/W2-60a
for f in tests/unit/launch tests/acceptance/W2-60a tests/acceptance/W2-153 tests/acceptance/W2-56 tests/acceptance/W2-58 tests/acceptance/W2-50; do
  n=$(echo $f | tr / _)
  env TMPDIR=/tmp/w260a-lead-r5 PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src \
    bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest $f -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" > .gov-runtime/scratch/lead/log/r5-pre-$n.txt 2>&1
  echo "$f rc=$? $(tail -1 .gov-runtime/scratch/lead/log/r5-pre-$n.txt)"
done
