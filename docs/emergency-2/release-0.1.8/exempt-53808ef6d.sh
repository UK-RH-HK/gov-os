#!/usr/bin/env bash
# The owner's exemption of merge 53808ef6d (e2/models-by-role) for W1-01's MR-3 history case (card E-01, page B-2026-11-26-cto).
# Run by the owner in a plain WSL terminal, from anywhere: it adds one acceptance_exemptions entry and commits it as the owner.
# The list is frozen by DEC-1052 Q-10 and only the owner's commit adds to it (path-map.yaml's own note); this is that commit.
set -eu
R=/home/usain/Dynamic-Agentic-Engineering-OS; F=$R/governance/project/path-map.yaml; SHA=53808ef6da8dbd333b207a7e86731e615b20c5d3
cd "$R"
[ "$(git rev-parse --abbrev-ref HEAD)" = w2/integrate ] || { echo "not on w2/integrate"; exit 1; }
grep -q "$SHA" "$F" && { echo "already exempted"; exit 0; }
python3 - "$F" "$SHA" <<'PY'
import sys,re
f,sha=sys.argv[1],sys.argv[2]; lines=open(f).read().split("\n")
i=lines.index("acceptance_exemptions:"); j=i+1
while j<len(lines) and (lines[j].startswith("  ") or lines[j]==""): j+=1
while lines[j-1]=="": j-=1
entry=['  - commit: "%s"' % sha, '    decision: DEC-1254  # item E-01; the merge settled a README conflict (W2-208) keeping both sections word for word, no test code changed (DEC-253)']
lines[j:j]=entry; open(f,"w").write("\n".join(lines))
PY
git add "$F"
git commit -q -F - <<MSG
Exempt merge 53808ef6d (e2/models-by-role, a W2-208 README conflict kept both sections) for W1-01's MR-3 history case (DEC-1254 E-01)

Role: owner
Task: decision-record
Decided-by: owner (page B-2026-11-26-cto)
MSG
git log -1 --oneline
