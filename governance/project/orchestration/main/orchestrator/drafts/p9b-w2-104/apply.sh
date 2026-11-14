#!/bin/bash
# P-9b (W2-104 run 4): the owner's commit of one acceptance_exemptions entry, 0e469cc379cd (DEC-1031 item 3's form, as
# P-9's two entries, DEC-1173 (1)). Run by the owner's operator in the main tree, only when no land is in flight.
set -euo pipefail
cd /home/usain/Dynamic-Agentic-Engineering-OS
grep -q '"land": *"in flight"' .gov-runtime/scratch/orchestrator/dispatch/status.json && { echo "a land is in flight: wait"; exit 3; }
[ -z "$(git status --porcelain)" ] || { echo "the main tree is not clean: stop"; exit 3; }
[ "$(git rev-parse --abbrev-ref HEAD)" = w2/integrate ] || { echo "not on w2/integrate: stop"; exit 3; }
F=governance/project/path-map.yaml
ANCHOR="    decision: DEC-1173  # W2-104 run 3's WIP merge kept the W1-07 and W1-32 files' markers for the test designer, as DEC-1031 item 3"
[ "$(grep -cxF "$ANCHOR" "$F")" = 1 ] || { echo "anchor line not found exactly once: stop"; exit 3; }
grep -q 0e469cc379cdec81b0fccf3e58f33e171646f95f "$F" && { echo "already listed: stop"; exit 3; }
python3 -I - "$F" "$ANCHOR" <<'EOF'
import sys
path, anchor = sys.argv[1:3]
text = open(path, encoding="utf-8").read()
add = ('  - commit: "0e469cc379cdec81b0fccf3e58f33e171646f95f"\n'
       "    decision: DEC-1175  # W2-104 run 4's merge took integrate's side of the W1-07 and W1-32 conflicts exactly, a resolution all the same\n")
text = text.replace(anchor + "\n", anchor + "\n" + add, 1)
open(path, "w", encoding="utf-8").write(text)
EOF
git diff --stat
python3 -I -c "import yaml,sys; d=yaml.safe_load(open('$F')); print('entries:', len(d['acceptance_exemptions']))"
git add "$F"
git commit -q -F - <<'EOF'
Owner decision DEC-1175 (P-9b): acceptance_exemptions lists W2-104 run 4's merge 0e469cc379cd (DEC-1031 item 3, DEC-253)

The merge of w2/integrate into w2/W2-104 took integrate's side of each conflicted W1-07 and W1-32 file exactly, as the
CTO's merge form of DEC-1173 (1) said; a conflict resolved by one side still differs from git's own merge, so W1-01's
history case and the landing's G-1 read it as an acceptance change without the designer's role.

Task: decision-record
Role: owner
EOF
git log -1 --format='%h %s%n%(trailers:key=Role,valueonly)'
