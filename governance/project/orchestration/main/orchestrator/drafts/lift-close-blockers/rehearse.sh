#!/usr/bin/env bash
# The rehearsal of ACT-CLOSE-HISTORY-1 on a fresh clone of the main tree's current HEAD (writes only in this folder).
#   bash rehearse.sh            -> rehearsal.log; regenerates entries.yaml, path-map-edit.diff, DEC-1127-draft.md, survey-table.md
set -u
D=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/lift-close-blockers
MAIN=/home/usain/Dynamic-Agentic-Engineering-OS
export PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$MAIN/src
LIFT="DAEO-blwa DAEO-qzrq DAEO-jpr0 DAEO-n0wb DAEO-ouet"
D10="DAEO-vhad DAEO-zuiy DAEO-fu3n"
R=$D/rehearsal
rm -rf "$R" "$D/tmp"; mkdir -p "$D/tmp"
git clone --no-hardlinks -q "$MAIN" "$R"
git -C "$R" config user.name rehearsal
git -C "$R" config user.email rehearsal@localhost
echo "=== clone at $(git -C "$R" rev-parse HEAD) (main tree HEAD $(git -C "$MAIN" rev-parse HEAD))"
python3 "$D/survey.py" "$R" $LIFT $D10 > "$D/rehearsal-before.json"
python3 "$D/containment.py" "$R" $LIFT $D10 > "$D/rehearsal-containment-before.txt" 2>&1
echo "=== BEFORE: pre-measure findings per ticket (lift closes, then D-10's three)"
python3 -I "$D/summarize.py" "$D/rehearsal-before.json"
echo "=== BEFORE: containment (counted)"; cut -c1-200 "$D/rehearsal-containment-before.txt"
# the diff, built from the survey, on the clone's tree and then undone there
python3 -I "$D/gen_entries.py" "$R" DEC-1127 "$D/rehearsal-before.json" > "$D/entries.yaml"
python3 -I "$D/build_edit.py" "$R" "$D/entries.yaml" || { echo "BUILD FAILED"; exit 1; }
git -C "$R" diff -- governance/project/path-map.yaml > "$D/path-map-edit.diff"
git -C "$R" checkout -q -- governance/project/path-map.yaml
echo "=== diff: $(git -C "$R" apply --stat "$D/path-map-edit.diff" | tail -1)"
python3 -I "$D/build_dec.py" "$R" "$D/entries.yaml" "$D/DEC-1127-draft.md"
python3 -I "$D/build_dec.py" "$R" "$D/entries.yaml" "$D/tmp/DEC-1127-accepted.md" --accepted
# 1. the orchestrator's decision-record commit (the draft with the status the CTO writes after the owner's yes)
python3 -I "$D/insert_dec.py" "$R" "$D/tmp/DEC-1127-accepted.md"
git -C "$R" commit -q -m "DEC-1127 (rehearsal): eighteen old merges accepted as history; four entries re-pointed" \
  --trailer "Task: decision-record" --trailer "Implements: DEC-1127" --trailer "Role: orchestrator" -- docs/DECISION_REGISTER.md
echo "=== register commit $(git -C "$R" rev-parse --short=12 HEAD)"
# 2. the owner's commit
git -C "$R" apply "$D/path-map-edit.diff" || { echo "APPLY FAILED"; exit 1; }
python3 -I -c "import yaml; d=yaml.safe_load(open('$R/governance/project/path-map.yaml')); print('yaml-ok accepted_history', len(d['accepted_history']), 'load_sensitive', len(d['load_sensitive']), 'acceptance_exemptions', [e['decision'] for e in d['acceptance_exemptions']])"
git -C "$R" commit -q -m "Owner decision DEC-1127: accepted_history lists eighteen old merges; the W1-19 load_sensitive entry and three acceptance_exemptions entries take DEC-1127 (ACT-CLOSE-HISTORY-1)" \
  --trailer "Task: decision-record" --trailer "Implements: DEC-1127" --trailer "Role: owner" -- governance/project/path-map.yaml
echo "=== owner commit $(git -C "$R" rev-parse --short=12 HEAD); tree status: $(git -C "$R" status --short | wc -l) changed"
python3 "$D/survey.py" "$R" $LIFT $D10 > "$D/rehearsal-after.json"
python3 "$D/containment.py" "$R" $LIFT $D10 > "$D/rehearsal-containment-after.txt" 2>&1
echo "=== AFTER: pre-measure findings per ticket"
python3 -I "$D/summarize.py" "$D/rehearsal-after.json"
echo "=== AFTER: containment (counted; no edit clears these)"; cut -c1-200 "$D/rehearsal-containment-after.txt"
echo "=== lists"
python3 "$D/lists.py" "$R"
python3 "$D/probe_all.py" "$R" DAEO-ouet > "$D/probe-all-ouet.txt" 2>&1
python3 -I "$D/table.py" "$D/rehearsal-before.json" > "$D/survey-table.md"
cat "$D/table-extra.md" >> "$D/survey-table.md"
