#!/usr/bin/env bash
set -eu
B=/home/usain/gov-os-worktrees/W2-37/.gov-runtime/scratch/lead/briefs
cat "$B/td-6.head.md" "$B/ctx-td-6.json" > "$B/td-6.md"
cat "$B/eng-6.head.md" "$B/ctx-eng-6.json" > "$B/eng-6.md"
wc -c "$B/td-6.md" "$B/eng-6.md"
grep -nE '\{[A-Z_]{3,}\}' "$B/td-6.md" "$B/eng-6.md" || echo "no slots"
ls /home/usain/gov-os-worktrees/W2-37/.gov-runtime/scratch/lead/log/ | grep -E '^(td-6|eng-6)' || echo "eng-6 unused (main)"
ls /home/usain/gov-os-worktrees/W2-37-tests/.gov-runtime/scratch/lead/log/ 2>/dev/null | grep -E '^td-6' || echo "td-6 unused (tests)"
test -f /home/usain/gov-os-worktrees/W2-37-tests/template/governance/kernel/roles/role-lead.md && echo "tests tree ok" || true
