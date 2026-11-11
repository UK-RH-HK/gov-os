#!/bin/bash
# scratch only: install tmp/resolved/{discovery,retrieval,test-design}.md and the given orchestration variant into the
# scratch clone's three places, then run W2-11's folder and W1-35's orchestration cases (through the heavy-job gate).
set -u
T=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/w2-11/tmp
VARIANT=${1:-$T/resolved/orchestration-trim.md}
cd "$T/clone" || exit 2
for p in template/governance/kernel/skills .rulesync/skills template/.rulesync/skills; do
  cp "$T/resolved/discovery.md" $p/discovery/SKILL.md
  cp "$T/resolved/retrieval.md" $p/retrieval/SKILL.md
  cp "$T/resolved/test-design.md" $p/test-design/SKILL.md
  cp "$VARIANT" $p/orchestration/SKILL.md
done
python3 - <<'EOF'
import math, re
t = open("template/governance/kernel/skills/orchestration/SKILL.md").read()
b = re.match(r"---\n(.*?)\n---\n(.*)", t, re.S).group(2)
print("orchestration body chars", len(b), "tokens", math.ceil(len(b) / 4))
EOF
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env TMPDIR=$T/tt PYTHONPATH=$PWD/src python3 -m pytest tests/acceptance/W2-11 tests/acceptance/W1-35/test_w1_35_orchestration.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed --no-header 2>&1 | grep -E "FAILED|passed|failed" | grep -v "brief-\|test_the_launcher\|role_independent_rule"
