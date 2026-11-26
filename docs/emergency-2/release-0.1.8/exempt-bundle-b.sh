#!/usr/bin/env bash
# The owner's exemption of six commits on the held batch B branches (e2/eval-roots, e2/kit-head, e2/w2-207-pre-retire, e2/w2-207-runtime) for W1-01's MR-3 history case (card E-04, page B-2026-11-26-cto).
# Run by the owner in a plain WSL terminal, from anywhere: it adds one acceptance_exemptions entry and commits it as the owner.
# The list is frozen by DEC-1052 Q-10 and only the owner's commit adds to it (path-map.yaml's own note); this is that commit.
set -eu
R=/home/usain/Dynamic-Agentic-Engineering-OS; F=$R/governance/project/path-map.yaml; SHAS="a0cf2fb68 50f278cdd 86a3f29b2 cbbbd5cf9 3624a8d50 6fc0a39d9"
cd "$R"
[ "$(git rev-parse --abbrev-ref HEAD)" = w2/integrate ] || { echo "not on w2/integrate"; exit 1; }
FULL=$(for s in $SHAS; do git rev-parse "$s^{commit}"; done)
for s in $FULL; do grep -q "$s" "$F" && { echo "already exempted: $s"; exit 0; }; done
python3 - "$F" $FULL <<'PY'
import sys,re
f=sys.argv[1]; shas=sys.argv[2:]; lines=open(f).read().split("\n")
i=lines.index("acceptance_exemptions:"); j=i+1
while j<len(lines) and (lines[j].startswith("  ") or lines[j]==""): j+=1
while lines[j-1]=="": j-=1
entry=[]
for s in shas: entry+=['  - commit: "%s"' % s, '    decision: DEC-1254  # item E-04; a batch B lead commit under Role: orchestrator touching tests/acceptance (README maps, one W2-153 line, W2-207 conftest), suites green (DEC-253)']
lines[j:j]=entry; open(f,"w").write("\n".join(lines))
PY
git add "$F"
git commit -q -F - <<MSG
Exempt six batch B commits (eval-roots, kit-head, W2-207 README maps, one W2-153 line, W2-207 conftest) for W1-01's MR-3 history case (DEC-1254 E-04)

Role: owner
Task: decision-record
Decided-by: owner (page B-2026-11-26-cto)
MSG
git log -1 --oneline
