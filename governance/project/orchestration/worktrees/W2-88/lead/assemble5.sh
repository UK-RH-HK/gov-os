#!/usr/bin/env bash
# assemble run 5's briefs: head + the binding interface + tail; check them
cd /home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/lead/briefs || exit 2
for n in td-7 eng-4; do
  cat "$n.head.md" run5-interface.md "$n.tail.md" > "$n.md"
  rm "$n.head.md" "$n.tail.md"
  echo "$n: $(wc -c < "$n.md") bytes; slots: $(grep -cE '\{[A-Z_]+\}' "$n.md")"
done
ls ../log | grep -E '^(td-7|eng-4)\.' || echo "log names unused"
test -f /home/usain/gov-os-worktrees/W2-88-tests/.claude/agents/role-lead.md -o -f /home/usain/gov-os-worktrees/W2-88/template/governance/kernel/roles/role-lead.md && echo "role-lead present" || echo "role-lead check: see tree"
