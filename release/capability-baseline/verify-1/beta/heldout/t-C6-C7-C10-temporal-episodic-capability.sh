#!/usr/bin/env bash
# C6 temporal memory (:261-266), C7 episodic execution memory (:268-274), C10 capability memory (:294-301).
. "$(dirname "${BASH_SOURCE[0]}")/corpus.sh"

ROOT=$(build_corpus_provisioned c6710)   # a provisioned machine: closing governed work needs a green record
S=$BETA_SCRATCH/c6710

# ================================================================================================= C6 temporal
# b1/b2 what changed, and when — after a real edit committed to the repository
sed -i 's/rounding is prohibited at every step/rounding is prohibited at every step and at the boundary/' "$ROOT/spec/requirements/REQ-0001.yaml"
commit_all "$ROOT" "amend REQ-0001"
gov "$ROOT" rebuild-memory --incremental >/dev/null 2>&1
gov "$ROOT" artefact show REQ-0001 > "$S-req.json" 2>&1
python3 - "$S-req.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))["result"]
vc = r["provenance"]["version_control"]
ok = (vc["available"] and vc["last_changed_by"]["commit"] != vc["introduced_by"]["commit"]
      and vc["last_changed_by"]["at"] and r["content_hash"])
print(json.dumps({"introduced": vc["introduced_by"]["commit"][:8], "last_changed": vc["last_changed_by"]["commit"][:8], "at": vc["last_changed_by"]["at"]}))
sys.exit(0 if ok else 1)
PY
chk C6-b1-what-changed $? "the OS distinguishes the commit that introduced a record from the commit that last changed it, with its content hash" \
                          "no distinct change provenance for an amended record"
python3 -c "
import json,sys
vc=json.load(open(sys.argv[1]))['result']['provenance']['version_control']
sys.exit(0 if vc['last_changed_by'].get('at') else 1)" "$S-req.json"
chk C6-b2-when $? "the change carries its timestamp" "no timestamp on the change"

# b3/b4 why, and the causal decision — a change-impact transaction records both, and the decision that governs the
# changed record is reachable by upstream lineage
MF=$S-cit.json
printf '%s' '[{"op":"set_status","target":"REQ-0001","value":"SUPERSEDED","by":"REQ-0500"}]' > "$MF"
CID=$(gov "$ROOT" cit propose --proposal "supersede REQ-0001 because production totals drifted" \
        --trigger governance_change --targets REQ-0001 --manifest "$MF" | jget 'd["result"]["id"]')
gov "$ROOT" cit simulate "$CID" >/dev/null 2>&1
gov "$ROOT" cit show "$CID" > "$S-cit-show.json" 2>&1
python3 - "$S-cit-show.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))["result"]
ok = ("drifted" in r.get("proposal","") and r.get("trigger")
      and r.get("mutation_manifest") and any(e.get("event")=="proposed" for e in r.get("journal",[]))
      and r.get("materiality", {}).get("derived_classes"))
sys.exit(0 if ok else 1)
PY
chk C6-b3-why $? "the transaction record states why the change is made, what it changes, its derived materiality classes and when each step happened" \
                 "the change record does not carry the reason/materiality/journal"

gov "$ROOT" artefact lineage REQ-0001 --direction up --depth 4 > "$S-lin.json" 2>&1
grep -q "D-0001" "$S-lin.json"
chk C6-b4-causal-decision $? "upstream lineage from the changed requirement reaches the decision that governs it (D-0001)" \
                             "the governing decision is not reachable from the changed record"

# b5 supersession / version lineage
cat > "$ROOT/spec/requirements/REQ-0500.yaml" <<'Y'
id: REQ-0500
type: requirement
title: Successor requirement
status: ACTIVE
kind: functional
feature: F-0001
supersedes: [REQ-0001]
acceptance_criteria: [totals are exact integer cents]
Y
python3 - "$ROOT" <<'PY'
import sys
p = sys.argv[1] + "/spec/requirements/REQ-0001.yaml"
s = open(p).read().replace("status: ACTIVE", "status: SUPERSEDED") + "superseded_by: REQ-0500\n"
open(p, "w").write(s)
PY
commit_all "$ROOT" "supersede"
gov "$ROOT" rebuild-memory >/dev/null 2>&1
gov "$ROOT" artefact show REQ-0001 > "$S-req2.json" 2>&1
python3 -c "
import json,sys
r=json.load(open(sys.argv[1]))['result']
sys.exit(0 if r.get('superseded_by')=='REQ-0500' and r['lifecycle_state']=='SUPERSEDED' else 1)" "$S-req2.json"
chk C6-b5-lineage $? "the supersession lineage of a record is recorded and read back (REQ-0001 → REQ-0500)" \
                     "supersession lineage not recorded"

# ================================================================================================= C7 episodic
# A clean provisioned project: closing governed work needs a CURRENT green governance record, and the C6 section above
# deliberately left this one's inputs changed.
ROOT=$(build_corpus_provisioned c7ep)
TID=$(gov "$ROOT" task create --class specification --objective "write the refund note" --status READY \
        --allowed 'spec/**' --fields '{"role":"product-spec-agent"}' | jget 'd["result"]["id"]')
export GOV_AS_ROLE=product-spec-agent GOV_SESSION_ID=S-episode-1
gov "$ROOT" task claim "$TID" >/dev/null 2>&1
PKT=$(gov "$ROOT" context compile "$TID" | jget 'd["result"]["packet_hash"]')
mkdir -p "$ROOT/spec/reports"
cat > "$ROOT/spec/product/PRJ-note.yaml" <<'Y'
id: PRJ-0002
type: project
title: Refund note
status: ACTIVE
Y
RET=$S-return.json
python3 - "$RET" "$TID" "$PKT" <<'PY'
import json, sys
out, task, pkt = sys.argv[1], sys.argv[2], sys.argv[3]
json.dump({
  "task": task, "status": "success", "work_completed": "wrote the refund note",
  "files_changed": ["spec/product/PRJ-note.yaml"], "files_read": ["spec/decisions/D-0001.yaml"],
  "evidence": ["spec/product/PRJ-note.yaml"],
  "tests": {"command": "probe-suite", "status": "passed", "passed": 3, "failed": 0, "outcome": "passed"},
  "discoveries": ["the refund path was never specified"], "risks": [], "lessons": [],
  "proposed_decisions": [], "unresolved": ["refund currency rounding"],
  "recommended_next_action": "gov continue",
  "context_packet_hash": pkt, "inputs_consumed": [], "outputs_produced": ["spec/product/PRJ-note.yaml"],
  "requirements_implemented": [], "scenarios_implemented": [], "features_implemented": [],
  "decisions_applied": [], "constraints_applied": [], "acceptance_evidence": [], "deviations": [],
  "skills_used": [{"id": "SKL-API-CONTRACT-REVIEW", "version": "1.0.0"}],
  "tools_used": ["TOOL-FS-001", "TOOL-GIT-001"],
}, open(out, "w"))
PY
commit_all "$ROOT" "work of $TID"
gov "$ROOT" rebuild-memory --incremental >/dev/null 2>&1
# the product's own close preconditions, satisfied legitimately (P2-ADJ-0003): the report claims tests passed, so a
# product test run must be on record, and governance-affecting work may not close on stale green evidence
GOV_AS_ROLE=orchestrator GOV_SESSION_ID=S-verify gov "$ROOT" verify product >/dev/null 2>&1
GREENID=$(establish_green "$ROOT")
gov "$ROOT" task close "$TID" --report "$RET" > "$S-close.json" 2>&1
# V1-BETA-04: the close's own G2 run writes memory-quality records into `evidence_records`, a class of its own
# currency key, BEFORE it evaluates currency — so the first close of governance-affecting work is always refused as
# stale. Re-establish and retry once; the retry is itself the evidence for that finding.
if grep -q GOVERNANCE_SUITE_STALE "$S-close.json"; then
  echo "note: first close refused GOVERNANCE_SUITE_STALE (V1-BETA-04); re-establishing green and retrying"
  GREENID=$(establish_green "$ROOT")
  gov "$ROOT" task close "$TID" --report "$RET" > "$S-close.json" 2>&1
fi
RPT=$(python3 -c "
import json,sys
d=json.load(open(sys.argv[1]))
r=d.get('result') or {}
print(r.get('report') or r.get('report_id') or '')" "$S-close.json")
if [ -z "$RPT" ]; then fail C7-close "the task could not be closed, so no episodic record exists: $(head -c 300 "$S-close.json")"
else
  pass C7-close "task $TID closed; episodic record $RPT written by the OS"
  gov "$ROOT" artefact show "$RPT" >/dev/null 2>&1
  REC=$(find "$ROOT/spec/reports" -name "$RPT*" | head -1)
  for f in "session:S-episode-1" "role:product-spec-agent" "task:$TID" "tools_used:TOOL-FS-001" \
           "files_changed:PRJ-note" "files_read:D-0001" "tests:probe-suite" "discoveries:never specified"; do
    k=${f%%:*}; v=${f#*:}
    grep -q "$v" "$REC" 2>/dev/null
    chk "C7-$k" $? "the episodic record carries $k ($v)" "the episodic record does not carry $k ($v): $REC"
  done
fi
unset GOV_AS_ROLE GOV_SESSION_ID

# ================================================================================================= C10 capability
# its own project: the checks below write to governance/project/**, which no claimed task above may mutate
ROOT=$(build_corpus_provisioned c10cap)
gov "$ROOT" tools registry > "$S-reg.json" 2>&1
python3 -c "
import json,sys
r=json.load(open(sys.argv[1]))['result']
t=r['tools']
sys.exit(0 if t and all('version' in x for x in t) and any(x.get('required_permission_classes') for x in t) else 1)" "$S-reg.json"
chk C10-tools $? "capability memory holds the tool registry with declared versions and permission classes" "tool registry incomplete"

mkdir -p "$ROOT/governance/project/mcp"
cat > "$ROOT/governance/project/mcp/registry.yaml" <<'Y'
servers:
  - id: MCP-PROBE-001
    name: probe-mcp
    transport: stdio
    command: [probe-mcp-server]
    capabilities: [search]
    credential_scope: none
    status: active
    version: "0.1.0"
Y
gov "$ROOT" tools registry > "$S-reg2.json" 2>&1
grep -q "MCP-PROBE-001" "$S-reg2.json"
chk C10-mcp $? "capability memory holds registered MCP servers" "a registered MCP server is not held in capability memory"

python3 -c "
import json,sys
r=json.load(open(sys.argv[1]))['result']
ex=r.get('role_exposure') or {}
sys.exit(0 if ex else 1)" "$S-reg2.json"
chk C10-a2a-roles $? "capability memory resolves, per agent role, which tools and MCP servers that agent may use" \
                     "no per-role capability exposure is recorded"

# A2A agents themselves: a registry of the agents a handoff may address
python3 -c "
import json,sys
r=json.load(open(sys.argv[1]))['result']
s=json.dumps(r).lower()
sys.exit(0 if ('a2a' in s or 'agents' in s) else 1)" "$S-reg2.json"
chk C10-a2a-agents $? "capability memory holds an A2A agent inventory" \
                      "capability memory holds no A2A agent inventory (only roles and their tool exposure)"

# packages / dependencies of the detected ecosystems
gov "$ROOT" capabilities ecosystems > "$S-eco.json" 2>&1
python3 - "$S-eco.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))["result"]
ecos = r["ecosystems"] if isinstance(r, dict) else r
has_pkgs = any(e.get("packages") or e.get("dependencies") for e in ecos)
print("ecosystems:", [(e["id"], sorted(k for k in e)) for e in ecos])
sys.exit(0 if has_pkgs else 1)
PY
chk C10-packages $? "capability memory holds the resolved packages/dependencies of the detected ecosystems" \
                    "ecosystem detection records only the metadata COMMAND and its availability; no package/dependency inventory is resolved or held"

# model providers
python3 - "$ROOT" <<'PY'
import sys
p = sys.argv[1] + "/governance/project/MODEL_ROUTING_OVERRIDES.yaml"
s = open(p).read().replace("providers: []",
    "providers:\n  - name: probe-provider\n    models:\n      - {id: probe-model-1, tier: T3, max_reasoning: high}")
open(p, "w").write(s)
PY
gov "$ROOT" route --class implementation > "$S-route.json" 2>&1
grep -q "probe-provider\|probe-model-1" "$S-route.json"
chk C10-providers $? "capability memory holds the configured model providers and resolves them when routing" \
                     "a configured model provider is not held/resolved: $(head -c 250 "$S-route.json")"

python3 -c "
import json,sys
r=json.load(open(sys.argv[1]))['result']
t=r['tools']
sys.exit(0 if any(x.get('credential_scope') for x in t) else 1)" "$S-reg.json"
chk C10-credentials $? "capability memory records each tool's credential scope and permission status" "no credential/permission status"

gov "$ROOT" tools health > "$S-health.json" 2>&1
python3 - "$S-health.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))["result"]
observed = [x for x in r if x.get("observed_version") or x.get("version_observed")]
print("checked:", len(r), "with an observed version:", len(observed))
sys.exit(0 if observed else 1)
PY
chk C10-tool-versions $? "capability memory records the OBSERVED version of each environment tool" \
                         "tool health records only availability/exit status; the observed version of an environment tool is never captured (the registry's 'version' is a declared string such as 'system'/'builtin')"

summary
