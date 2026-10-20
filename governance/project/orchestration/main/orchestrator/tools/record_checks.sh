#!/usr/bin/env bash
# DEC-868 item 2: before committing my own edits to the register, the plan, the path map, tickets or briefs, run
# the governance checks those files feed, as the runner runs them (the tree's src until W2-59 lands). Until the
# hooks are back on (W2-08). Prints one line per check; exits non-zero if any is not green.
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
OUT=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/record-checks
mkdir -p "$OUT"
status=0
for pair in "core-pathmap gov.check.pathmap" "core-schema gov.check.schema" "core-mutation gov.check.mutation" \
            "core-authority gov.check.authority" "core-graph gov.check.graph" \
            "context-reproducibility gov.context.context_check"; do
  set -- $pair
  PYTHONPATH=/home/usain/Dynamic-Agentic-Engineering-OS/src timeout 900 python3 -m "$2" > "$OUT/$1.out" 2>&1
  code=$?
  echo "$1 exit $code"
  [ "$code" -eq 0 ] || status=1
done
exit $status
