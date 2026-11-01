#!/usr/bin/env bash
# Run 3: step 4 (gov check once, this worktree's code), the collection run (DEC-868), the trailer gate, keyword_warn.
W=/home/usain/gov-os-worktrees/W2-76
LOG=$W/.gov-runtime/scratch/lead/log
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
cd "$W" || exit 2
python3 "$ORCH/tools/keyword_warn.py" "$W" > "$LOG/keyword3.out" 2>&1
echo "exit $?" >> "$LOG/keyword3.out"
PYTHONPATH=$W/src python3 "$ORCH/tools/trailer_gate.py" DAEO-tgk2 "$W" > "$LOG/trailer3.out" 2>&1
echo "exit $?" >> "$LOG/trailer3.out"
TMPDIR=/tmp/gov-os-lead-W2-76 PYTHONPATH=$W/src python3 -m gov.cli.main check --json > "$LOG/check3.json" 2> "$LOG/check3.err"
echo $? > "$LOG/check3.exit"
TMPDIR=/tmp/gov-os-lead-W2-76 PYTHONPATH=$W/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header > "$LOG/collect3.out" 2>&1
echo $? > "$LOG/collect3.exit"
echo done > "$LOG/checks3.exit"
