#!/usr/bin/env bash
# DAEO-2azm (W2-74), the lead's checks (DEC-925 item 1): the four revised files alone, then the whole collection
# checked for a keyword of row W2-L423's rule (paths and counts only, never the keyword).
set -u
WT=/home/usain/gov-os-worktrees/W2-74
LOG=$WT/.gov-runtime/scratch/lead/log/checks
KW=/tmp/gov-os-lead-W2-74/kw
TOOL=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/keyword_warn.py
mkdir -p "$LOG" "$KW/.gov-runtime"
cd "$WT" || exit 9
export TMPDIR=/tmp/gov-os-lead-W2-74
export PYTHONPATH=$WT/src

PYTHONPATH=$WT/src python3 -c "import gov; print(gov.__file__)" > "$LOG/gov_file.txt" 2>&1

for f in tests/acceptance/W1-01/test_w1_01_settings_deny.py \
         tests/acceptance/W1-47/test_w1_47_settings_rules.py \
         tests/acceptance/W1-49/test_w1_49_precompact.py \
         tests/acceptance/W2-69/test_w2_69_word_internal_fragments.py; do
  name=$(basename "$f" .py)
  PYTHONPATH=$WT/src python3 -m pytest "$f" -q -p no:cacheprovider -rs --junitxml="$KW/.gov-runtime/$name.xml" > "$LOG/$name.txt" 2>&1
  echo "$f exit=$?" >> "$LOG/summary.txt"
  tail -n 1 "$LOG/$name.txt" >> "$LOG/summary.txt"
done

PYTHONPATH=$WT/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header > "$KW/.gov-runtime/collection.txt" 2>&1
echo "collect exit=$?" >> "$LOG/summary.txt"
tail -n 1 "$KW/.gov-runtime/collection.txt" >> "$LOG/summary.txt"
grep -c '::' "$KW/.gov-runtime/collection.txt" >> "$LOG/summary.txt"
python3 "$TOOL" "$KW" >> "$LOG/summary.txt" 2>&1
echo "keyword_warn exit=$?" >> "$LOG/summary.txt"
echo done > "$LOG/exit"
