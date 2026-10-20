#!/usr/bin/env bash
# Re-verify W2-62's integration in the main tree (DEC-863): a full rebuild, then the suites its lead named, each in
# its own pytest process, then gov check. Literal paths only; one result file per step.
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
OUT=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/reverify-W2-62
mkdir -p "$OUT"
date +%T > "$OUT/rebuild.start"
/usr/bin/time -f "%e s wall" gov rebuild > "$OUT/rebuild.json" 2> "$OUT/rebuild.err"; echo $? > "$OUT/rebuild.exit"
date +%T > "$OUT/rebuild.end"
for suite in W2-62 W1-49 W1-38 W1-30 W2-54; do
  PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/Dynamic-Agentic-Engineering-OS/src \
    python3 -m pytest "tests/acceptance/$suite" -q -p no:cacheprovider -rs > "$OUT/$suite.txt" 2>&1
  echo $? > "$OUT/$suite.exit"
done
gov check --json > "$OUT/check.json" 2> "$OUT/check.err"; echo $? > "$OUT/check.exit"
date +%T > "$OUT/done"
