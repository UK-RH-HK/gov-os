#!/usr/bin/env bash
# Dry run of W2-11-A4-skills-premerge.md's steps 1 to 4 in a scratch clone (never the worktree): sparse checkout of the
# 17 paths, two commits made as the brief says, then the merge-tree proof.  Output is short.
set -u
D=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/w2-11/tmp
C=$D/dry
rm -rf "$C"
git clone --shared --no-checkout --branch w2/W2-11 -q /home/usain/Dynamic-Agentic-Engineering-OS "$C" || exit 1
BR="template/governance/kernel/templates/brief-engineer.md template/governance/kernel/templates/brief-lead.md template/governance/kernel/templates/brief-product-spec.md template/governance/kernel/templates/brief-reviewer.md template/governance/kernel/templates/brief-test-designer.md"
SK=""
for s in discovery orchestration retrieval test-design; do
  SK="$SK template/governance/kernel/skills/$s/SKILL.md .rulesync/skills/$s/SKILL.md template/.rulesync/skills/$s/SKILL.md"
done
git -C "$C" sparse-checkout set --no-cone $BR $SK
git -C "$C" checkout -q w2/W2-11 || exit 1
git -C "$C" config user.name dry; git -C "$C" config user.email dry@example.invalid
echo "baseline:"; git -C "$C" merge-tree --write-tree --name-only w2/W2-11 origin/w2/integrate | grep -c '^CONFLICT'
git -C "$C" restore --source=origin/w2/integrate --staged --worktree -- $BR || exit 2
git -C "$C" diff --quiet origin/w2/integrate -- $BR && echo "briefs identical"
git -C "$C" commit -q -m "dry: briefs" -m "body" --trailer "Task: DAEO-k7hz" --trailer "Role: product-spec" --trailer "Implements: DEC-1137" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- $BR || exit 3
git -C "$C" restore --source=origin/w2/integrate --staged --worktree -- $SK || exit 4
git -C "$C" diff --quiet origin/w2/integrate -- $SK && echo "skills identical"
git -C "$C" commit -q -m "dry: skills" -m "body" --trailer "Task: DAEO-k7hz" --trailer "Role: product-spec" --trailer "Implements: DEC-866, DEC-959" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- $SK || exit 5
git -C "$C" log --format='%h %s%n%b' -2 | head -14
echo "files in the two commits:"; git -C "$C" diff --name-only c16dbf41ea77..HEAD | wc -l
echo "proof:"; git -C "$C" merge-tree --write-tree --name-only w2/W2-11 origin/w2/integrate | grep '^CONFLICT'
