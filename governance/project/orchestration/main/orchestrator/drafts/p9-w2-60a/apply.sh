#!/bin/bash
# P-9 (W2-60a and W2-104): the owner's commit of two acceptance_exemptions entries, 5b7941b66aa2 and 349341ab8f03
# (DEC-1173 (1); DEC-1031 item 3's form, DEC-1123 item 3's precedent). Run by the owner's operator in the main tree,
# only when no land is in flight.
set -euo pipefail
cd /home/usain/Dynamic-Agentic-Engineering-OS
grep -q '"land": *"in flight"' .gov-runtime/scratch/orchestrator/dispatch/status.json && { echo "a land is in flight: wait"; exit 3; }
[ -z "$(git status --porcelain)" ] || { echo "the main tree is not clean: stop"; exit 3; }
[ "$(git rev-parse --abbrev-ref HEAD)" = w2/integrate ] || { echo "not on w2/integrate: stop"; exit 3; }
F=governance/project/path-map.yaml
ANCHOR="    decision: DEC-1157  # ACT-OPERATOR-HOURS-3's commit (DEC-1136 (2))"
[ "$(grep -cxF "$ANCHOR" "$F")" = 1 ] || { echo "anchor line not found exactly once: stop"; exit 3; }
grep -q 5b7941b66aa2351e0ddf8cf4fa8f3ac9377fb722 "$F" && { echo "W2-60a's entry already listed: stop"; exit 3; }
grep -q 349341ab8f03562ddb0bff8812770de9e745c397 "$F" && { echo "W2-104's entry already listed: stop"; exit 3; }
python3 -I - "$F" "$ANCHOR" <<'EOF'
import sys
path, anchor = sys.argv[1:3]
text = open(path, encoding="utf-8").read()
add = ('  - commit: "5b7941b66aa2351e0ddf8cf4fa8f3ac9377fb722"\n'
       "    decision: DEC-1173  # W2-60a's WIP merge kept 4 acceptance files' markers for the test designer (b12), as DEC-1031 item 3\n"
       '  - commit: "349341ab8f03562ddb0bff8812770de9e745c397"\n'
       "    decision: DEC-1173  # W2-104 run 3's WIP merge kept the W1-07 and W1-32 files' markers for the test designer, as DEC-1031 item 3\n")
text = text.replace(anchor + "\n", anchor + "\n" + add, 1)
open(path, "w", encoding="utf-8").write(text)
EOF
git diff --stat
python3 -I -c "import yaml,sys; d=yaml.safe_load(open('$F')); print('entries:', len(d['acceptance_exemptions']))"
git add "$F"
git commit -q -F - <<'EOF'
Owner decision DEC-1173 (1) (P-9): acceptance_exemptions lists the WIP merges 5b7941b66aa2 (W2-60a) and 349341ab8f03 (W2-104) (DEC-1031 item 3, DEC-253)

Each merge of w2/integrate into its ticket branch kept acceptance files' conflict markers for the test designer's
resolution, as the brief's merge form said, so W1-01's MR-3 history case reads it as an acceptance change without
the designer's role.

Task: decision-record
Role: owner
EOF
git log -1 --format='%h %s%n%(trailers:key=Role,valueonly)'
