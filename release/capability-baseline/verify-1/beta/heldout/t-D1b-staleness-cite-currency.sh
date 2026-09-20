#!/usr/bin/env bash
# D1 continued, on a provisioned machine (the paths below need a green governance record and an owner-signed gate):
#   * b6  a required stale index degrades/blocks task close according to MEMORY_POLICY.freshness
#   * BC-P2-29 / AC-16  CIT-E refreshes and verifies the index under the POST-mutation policy and path map
#   * BC-P2-03 / AC-10  green memory/index evidence is invalidated by source, spec and index-manifest changes
. "$(dirname "${BASH_SOURCE[0]}")/corpus.sh"

ROOT=$(build_corpus_provisioned d1b)
S=$BETA_SCRATCH/d1b
DB="$ROOT/.governance-runtime/state.db"
sq() { python3 -c "
import sqlite3,sys
c=sqlite3.connect(sys.argv[1])
print('|'.join(str(x) for r in c.execute(sys.argv[2]) for x in r))" "$DB" "$1"; }

# ================================================================== b6: a stale index blocks the close it protects
TID=$(gov "$ROOT" task create --class specification --objective "stale-close probe" --status READY \
        --allowed 'spec/**' --fields '{"role":"product-spec-agent"}' | jget 'd["result"]["id"]')
export GOV_AS_ROLE=product-spec-agent GOV_SESSION_ID=S-stale
gov "$ROOT" task claim "$TID" >/dev/null 2>&1
PKT=$(gov "$ROOT" context compile "$TID" | jget 'd["result"]["packet_hash"]')
cat > "$ROOT/spec/product/PRJ-stale.yaml" <<'Y'
id: PRJ-0003
type: project
title: Stale-close probe output
status: ACTIVE
Y
python3 - "$S-ret.json" "$TID" "$PKT" <<'PY'
import json, sys
json.dump({"task": sys.argv[2], "status": "success", "work_completed": "wrote the record",
           "files_changed": ["spec/product/PRJ-stale.yaml"], "files_read": [],
           "evidence": ["spec/product/PRJ-stale.yaml"],
           "tests": {"command": "probe", "status": "not_applicable_with_reason",
                     "reason": "a specification record carries no executable test"},
           "discoveries": [], "risks": [], "lessons": [], "proposed_decisions": [], "unresolved": [],
           "recommended_next_action": "gov continue", "context_packet_hash": sys.argv[3],
           "inputs_consumed": [], "outputs_produced": ["spec/product/PRJ-stale.yaml"],
           "requirements_implemented": [], "scenarios_implemented": [], "features_implemented": [],
           "decisions_applied": [], "constraints_applied": [], "acceptance_evidence": [], "deviations": []},
          open(sys.argv[1], "w"))
PY
commit_all "$ROOT" "stale-close work"
# deliberately do NOT rebuild the index: the governed record just written is not indexed
gov "$ROOT" task close "$TID" --report "$S-ret.json" > "$S-close-stale.json" 2>&1
python3 - "$S-close-stale.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
e = json.dumps(d.get("error") or {})
blocked = (not d.get("ok")) and ("STALE" in e or "stale" in e)
print("refused:", not d.get("ok"), "code:", (d.get("error") or {}).get("code"))
sys.exit(0 if blocked else 1)
PY
chk D1-b6-stale-close $? "a task close whose governed writes are not in the index is refused, as MEMORY_POLICY.freshness.on_stale_close=fail requires" \
                         "a task closed on a stale index"
python3 - "$S-close-stale.json" <<'PY'
import json, sys
e = json.dumps(json.load(open(sys.argv[1])).get("error") or {})
sys.exit(0 if ("rebuild-memory" in e or "gov audit" in e or "health run" in e) else 1)
PY
chk D1-b6-remedy-named $? "the refusal names the remedy that clears it" "the refusal names no remedy"
gov "$ROOT" rebuild-memory --incremental >/dev/null 2>&1
GREEN=$(establish_green "$ROOT")
gov "$ROOT" task close "$TID" --report "$S-ret.json" > "$S-close2.json" 2>&1
if grep -q GOVERNANCE_SUITE_STALE "$S-close2.json"; then
  GREEN=$(establish_green "$ROOT"); gov "$ROOT" task close "$TID" --report "$S-ret.json" > "$S-close2.json" 2>&1
fi
jget 'd.get("ok")' < "$S-close2.json" | grep -q true
chk D1-b6-remedy-works $? "after the named remedy the same close succeeds (the block refuses only what it protects)" \
                          "the close still fails after its own remedy: $(head -c 250 "$S-close2.json")"
unset GOV_AS_ROLE GOV_SESSION_ID

# =============================================== BC-P2-29: CIT-E must refresh under the POST-mutation path map
NS_BEFORE=$(sq "select distinct namespace from artifacts where path like 'src/%'")
MF=$S-cit.json
python3 - "$ROOT" "$MF" <<'PY'
import json, sys
p = sys.argv[1] + "/governance/project/REPOSITORY_CONTRACT.yaml"
new = open(p).read().replace(
  "- pattern: src/**\n  class: source\n  owner_role: backend-engineer\n  semantic_index: true\n  lexical_index: true\n  graph_index: true\n  code_index: true\n  namespace: product",
  "- pattern: src/**\n  class: historical\n  owner_role: backend-engineer\n  semantic_index: false\n  lexical_index: true\n  graph_index: false\n  code_index: false\n  default_retrieval: false\n  namespace: archive")
json.dump([{"op": "write_file", "path": "governance/project/REPOSITORY_CONTRACT.yaml", "content": new}],
          open(sys.argv[2], "w"))
PY
CID=$(gov "$ROOT" cit propose --proposal "reclassify src/** as historical" --trigger governance_change \
        --targets "file:governance/project/REPOSITORY_CONTRACT.yaml" --manifest "$MF" | jget 'd["result"]["id"]')
G=$(gov "$ROOT" cit simulate "$CID" | jget 'json.dumps((d.get("result") or {}).get("human_gate"))')
G=${G//\"/}
if [ -n "$G" ] && [ "$G" != "null" ]; then owner_answers "$ROOT" "$G" A >/dev/null 2>&1; fi
gov "$ROOT" cit approve "$CID" >/dev/null 2>&1
gov "$ROOT" cit execute "$CID" > "$S-cite.json" 2>&1
if jget 'd.get("ok")' < "$S-cite.json" | grep -q true; then
  NS_AFTER=$(sq "select distinct namespace from artifacts where path like 'src/%'")
  [ "$NS_AFTER" = "archive" ]
  chk D1-cite-postmutation $? "CIT-E's index refresh uses the path map the transaction just wrote (namespace $NS_BEFORE -> $NS_AFTER)" \
                              "CIT-E refreshed the index under the PRE-mutation path map (namespace still $NS_AFTER)"
else
  fail D1-cite-postmutation "the change-impact transaction could not be executed: $(head -c 300 "$S-cite.json")"
fi

# ==================================================== BC-P2-03: green evidence currency over the inputs that matter
P2=$(build_corpus_provisioned d1c)
green_current() {
  gov "$P2" doctor > "$S-doc.json" 2>&1
  python3 -c "
import json,sys
d=json.load(open(sys.argv[1])); det=d.get('result') or d['error']['details']
c=[x for x in det['checks'] if x['id']=='D021']
print('true' if (c and c[0]['ok']) else 'false')" "$S-doc.json"
}
establish_green "$P2" >/dev/null
[ "$(green_current)" = "true" ] || fail D1-currency-precondition "no current green record to invalidate"

for probe in "source:src/lib.rs:// probe source change" \
             "spec:spec/requirements/REQ-0001.yaml:# probe spec change" \
             "governance_tests:governance/tests/memory/heldout.yaml:# probe heldout change"; do
  name=${probe%%:*}; rest=${probe#*:}; file=${rest%%:*}; line=${rest#*:}
  echo "$line" >> "$P2/$file"
  R=$(green_current)
  [ "$R" = "false" ]
  chk "D1-currency-$name" $? "changing $file invalidates the green governance record" \
                             "changing $file left the green record current"
  establish_green "$P2" >/dev/null
done

# the index manifest is itself an evidence input: a rebuild that changes it must invalidate prior green evidence
python3 - "$P2" <<'PY'
import sys
p = sys.argv[1] + "/src/app/orders.py"
open(p, "a").write("\n# force an index manifest change\n")
PY
gov "$P2" rebuild-memory >/dev/null 2>&1
[ "$(green_current)" = "false" ]
chk D1-currency-index-manifest $? "a rebuild that changes the index manifest invalidates the green governance record" \
                                  "a changed index manifest left the green record current"

summary
