cd /home/usain/gov-os-worktrees/W2-146 || exit 1
base=$(git merge-base HEAD w2/integrate)
echo "base $base"
git log --oneline "$base"..HEAD
git diff --stat "$base" HEAD | tail -15
git diff "$base" HEAD -- template/governance/kernel/schemas/path-map.schema.json
