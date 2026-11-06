#!/usr/bin/env bash
# ACT-MSET-3's rehearsal (DEC-1057): the operator's steps exactly, with only the home folder substituted (H), then the
# two sessions' write rules and the writer's checks on planted folders. Nothing under the real home is written.
#   bash rehearse.sh <scratch home>
set -u
H=$1; mkdir -p "$H/gov-os-eval/fixtures/evaluation"
R=/home/usain/Dynamic-Agentic-Engineering-OS
P=$R/governance/project/orchestration/packages/ACT-MSET-3
O=$R/.gov-runtime/scratch/orchestrator/drafts/d4b
fail=0; ok() { echo "ok   $1"; }; no() { echo "FAIL $1"; fail=$((fail+1)); }

echo "== step 1: the same two sessions' folders updated (as the operator runs them, HOME=$H; their current files copied in first)"
mkdir -p "$H/gov-os-writer/.claude" "$H/gov-os-checker/.claude"
cp /home/usain/gov-os-writer/.claude/settings.json "$H/gov-os-writer/.claude/"; cp /home/usain/gov-os-writer/CLAUDE.md "$H/gov-os-writer/"
cp /home/usain/gov-os-checker/.claude/settings.json "$H/gov-os-checker/.claude/"; cp /home/usain/gov-os-checker/CLAUDE.md "$H/gov-os-checker/"
V2=$H/gov-os-eval/fixtures/evaluation/memory-verdict-2
# --- the operator's commands, verbatim but for the home folder ---
for s in writer checker; do
  cp -p "$H/gov-os-$s/.claude/settings.json" "$H/gov-os-$s/.claude/settings.json.pre-act-mset-3"
  cp -p "$H/gov-os-$s/CLAUDE.md" "$H/gov-os-$s/CLAUDE.md.pre-act-mset-3"
  cp "$P/$s-settings.json" "$H/gov-os-$s/.claude/settings.json" && cp "$P/$s-CLAUDE.md" "$H/gov-os-$s/CLAUDE.md"
done
mkdir -p -m 700 "$V2/hidden" "$V2/retired" && chmod 700 "$V2"
# --- end ---
[ "$(stat -c %a "$V2")" = 700 ] && [ "$(stat -c %a "$V2/hidden")" = 700 ] && ok "the set's folder and hidden/ are mode 700" || no "modes"
python3 -c "import json,sys; [json.load(open(f)) for f in sys.argv[1:]]" "$H/gov-os-writer/.claude/settings.json" "$H/gov-os-checker/.claude/settings.json" && ok "both settings files parse" || no "settings parse"
cmp -s "$P/writer-settings.json" "$H/gov-os-writer/.claude/settings.json" && cmp -s "$P/checker-settings.json" "$H/gov-os-checker/.claude/settings.json" && ok "copied byte for byte" || no "copies"
cmp -s /home/usain/gov-os-writer/.claude/settings.json "$H/gov-os-writer/.claude/settings.json.pre-act-mset-3" && cmp -s /home/usain/gov-os-checker/.claude/settings.json "$H/gov-os-checker/.claude/settings.json.pre-act-mset-3" && ok "the old settings kept beside them (the rollback)" || no "backups"
python3 - "$P/writer-settings.json" "$P/checker-settings.json" <<'PY' && ok "neither session is denied a read of its own folder" || no "own folder"
import json, sys
w = json.load(open(sys.argv[1]))["permissions"]["deny"]; c = json.load(open(sys.argv[2]))["permissions"]["deny"]
assert not any(d.startswith("Read(//home/usain/gov-os-writer/") for d in w), "writer"
assert not any(d.startswith("Read(//home/usain/gov-os-checker/") for d in c), "checker"
assert "Read(//home/usain/gov-os-checker/**)" in w and "Read(//home/usain/gov-os-writer/**)" in c, "each other's"
PY
echo "== step 2: each session's write rule (its PreToolUse hook, fed the tool input it would see)"
hook() {  # $1 settings, $2 path -> exit code of the hook
  python3 - "$1" "$2" <<'EOF'
import json, subprocess, sys
s = json.load(open(sys.argv[1]))
h = s["hooks"]["PreToolUse"][0]["hooks"][0]
r = subprocess.run([h["command"], *h["args"]], input=json.dumps({"tool_input": {"file_path": sys.argv[2]}}), text=True, capture_output=True)
sys.exit(r.returncode)
EOF
}
RV=/home/usain/gov-os-eval/fixtures/evaluation/memory-verdict-2
W=$P/writer-settings.json; C=$P/checker-settings.json
hook "$W" "$RV/hidden/v01.yaml"; [ $? = 0 ] && ok "writer: a question file is allowed" || no "writer: question file"
hook "$W" "$RV/retired/v01-pre-xcheck.yaml"; [ $? = 0 ] && ok "writer: a retired copy is allowed" || no "writer: retired copy"
hook "$W" "$RV/XCHECK.md"; [ $? = 2 ] && ok "writer: the checker's report is refused" || no "writer: XCHECK refused"
hook "$W" "$R/docs/x.md"; [ $? = 2 ] && ok "writer: the repository is refused" || no "writer: repo refused"
hook "$W" "/home/usain/gov-os-eval/fixtures/evaluation/memory-verdict/hidden/m01.yaml"; [ $? = 2 ] && ok "writer: the spent 60 refused" || no "writer: spent 60"
hook "$W" "$RV/hidden/../../memory-verdict/hidden/m01.yaml"; [ $? = 2 ] && ok "writer: a .. path out of hidden/ refused" || no "writer: dotdot"
hook "$C" "$RV/XCHECK.md"; [ $? = 0 ] && ok "checker: its report is allowed" || no "checker: XCHECK"
hook "$C" "$RV/hidden/v01.yaml"; [ $? = 2 ] && ok "checker: a question file is refused" || no "checker: question refused"
python3 - "$W" "$C" <<'EOF' && ok "denials: the spent 60, the tuning sets, the runs, the misses' records and each other's folder" || no "denials"
import json, sys
need = ["memory-verdict/**", "memory-retrieval/**", "gov-os-eval/runs/**", "gov-os-runs/**", "docs/audit/memory-verdict-*",
        "LIFT-1/D4B-*", "W2-88-memory-practice.md", ".gov-runtime/**", "gov retrieve *"]
for f in sys.argv[1:]:
    d = " ".join(json.load(open(f))["permissions"]["deny"])
    miss = [n for n in need if n not in d]
    assert not miss, (f, miss)
EOF

echo "== step 3: the writer's checks, on planted folders (no hidden question is read or printed)"
E=$H/plant-empty; mkdir -p "$E"
python3 "$O/repin_gold.py" "$E" "$R" | tail -1
# DEC-1084 (ACT-GUARD-SETS-1): the sets root's hidden folders by the sets-root form, never named on the line
out=$(python3 -I "$O/mset_overlap.py" "$E" "$R/fixtures/evaluation/memory-retrieval/visible" --sets-root /home/usain/gov-os-eval --set memory-retrieval --part hidden --set memory-verdict --part hidden); echo "$out"
echo "$out" | grep -q "new questions: 0; overlapping a tuning question's gold source: 0" && ok "overlap check loads all three other sets" || no "overlap check on empty"
python3 -I "$O/mset_quota.py" "$E" | tail -1 | grep -q "NOT YET" && ok "quota check: an empty folder is not yet" || no "quota on empty"
D=$H/plant-dup; mkdir -p "$D"; cp "$R/fixtures/evaluation/memory-retrieval/visible/q01.yaml" "$D/v01.yaml"
python3 -I "$O/mset_overlap.py" "$D" "$R/fixtures/evaluation/memory-retrieval/visible" | grep -q "gold source: 1 (" && ok "overlap check catches a copied tuning question" || no "overlap catch"
B=$H/plant-bad; mkdir -p "$B"; sed 's/^\(    heading: "\)/\1NO SUCH /' "$R/fixtures/evaluation/memory-retrieval/visible/q01.yaml" > "$B/v01.yaml"
python3 "$O/repin_gold.py" "$B" "$R" | tail -1   # falls back to the lines: a mistyped heading passes here (found in the rehearsal)
python3 -I "$O/mset_anchors.py" "$B" "$R"; [ $? = 1 ] && ok "the heading check catches a heading on no line" || no "heading catch"
python3 -I "$O/mset_anchors.py" "$D" "$R"; [ $? = 0 ] && ok "the heading check passes a well-anchored question" || no "heading pass"
python3 -I "$O/mset_anchors.py" "$E" "$R" > /dev/null; [ $? = 0 ] && ok "the heading check passes an empty folder" || no "heading empty"
python3 -I "$O/leak_check.py" "$D" "$D/v01.yaml" > /dev/null; [ $? = 1 ] && ok "leak check catches a copied question" || no "leak catch"
quota() {  # $1 folder, $2 failure-memory count, $3 decision count: a synthetic set with the table's other counts
  mkdir -p "$1"; local n=0 c k
  for c in "contract 8" "plan 8" "ticket 8" "exact-string 8" "callers 8" "code-paraphrase 7" "kernel-template 7" \
           "multi-file 6" "history 2" "nonexistent-id 1" "failure-memory $2" "decision $3"; do
    set -- $c; for k in $(seq 1 "$2"); do n=$((n+1)); echo "category: $1" > "$Q/v$(printf %02d $n).yaml"; done; set -- "$Q"
  done
}
Q=$H/q-exact; mkdir -p "$Q"; quota "$Q" 4 13; python3 -I "$O/mset_quota.py" "$Q" | tail -1 | grep -qx "total: 80 of 80; PASS" && ok "quota: the exact table passes" || no "quota exact"
Q=$H/q-shift; mkdir -p "$Q"; quota "$Q" 2 15; python3 -I "$O/mset_quota.py" "$Q" | tail -1 | grep -q "PASS (failure-memory short by 2" && ok "quota: the allowed shift passes, named" || no "quota shift"
Q=$H/q-short; mkdir -p "$Q"; quota "$Q" 1 16; python3 -I "$O/mset_quota.py" "$Q" | tail -1 | grep -q "NOT YET" && ok "quota: failure-memory below 2 fails" || no "quota short"
echo "$([ $fail = 0 ] && echo "REHEARSAL PASS" || echo "REHEARSAL FAILED $fail")"
