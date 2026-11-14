#!/usr/bin/env bash
# gov.adapters.portability at the root and inside template/ of the head (f0cb5284d) and its parent (80b19dc16),
# in the trace copies; and whether w2/integrate's root orchestrator source still carries the 'until W2-56' line.
R=/tmp/w2-182-trace
for c in f0cb5284d 80b19dc16; do
  for where in "" template; do
    cd "$R/$c/$where" || exit 2
    out=$(PYTHONPATH="$R/$c/src" python3 -m gov.adapters.portability 2>&1); rc=$?
    codes=$(printf '%s' "$out" | python3 -c 'import json,sys
try:
  d=json.load(sys.stdin); print(sorted(f["code"] for f in d["findings"]))
except Exception as e: print("unparsed", e)')
    echo "$c root/${where}: exit $rc $codes"
    printf '%s' "$out" | grep -o '"hook event[^"]*"' | head -3
  done
done
cd /home/usain/gov-os-worktrees/W2-182
echo "integrate $(git rev-parse --short=12 w2/integrate): until-W2-56 lines in .rulesync/subagents/orchestrator.md: $(git show w2/integrate:.rulesync/subagents/orchestrator.md | grep -c 'until W2-56')"
echo "integrate: in template role-lead: $(git show w2/integrate:template/governance/kernel/templates/role-lead.md | grep -c 'until W2-56')"
