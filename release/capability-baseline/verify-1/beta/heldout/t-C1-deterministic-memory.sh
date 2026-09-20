#!/usr/bin/env bash
# C1 — deterministic structured memory must represent CURRENT TRUTH for the seventeen record kinds
# (Contract v3:210-227). One check per kind. "Represents current truth" is taken as: the OS holds a structured,
# queryable, current record of that kind that a fresh process reads back — not that a file or schema exists.
. "$(dirname "${BASH_SOURCE[0]}")/corpus.sh"

ROOT=${BETA_REUSE_ROOT:-}
if [ -z "$ROOT" ]; then ROOT=$(build_corpus c1); gov "$ROOT" init --name c1probe >/dev/null 2>&1; fi

Q=$BETA_SCRATCH/c1.out

# structured read-back of a governed record by id (deterministic route), independent of retrieval ranking
has_record() { gov "$ROOT" artefact show "$1" > "$Q" 2>&1; grep -q "\"id\": \"$1\"" "$Q"; }

for kind in "project:PRJ-0001" "feature:F-0001" "requirement:REQ-0001" "decision:D-0001" \
            "scenario:SCN-0001" "test:TST-0001" "interface:API-0001" "release:REL-0001"; do
  id=${kind#*:}; name=${kind%%:*}
  has_record "$id"
  chk "C1-$name" $? "current truth for $name read back as a structured record ($id)" \
                    "no structured current record for $name ($id): $(head -c 200 "$Q")"
done

# tasks — created through the OS, read back with a status
TID=$(gov "$ROOT" task create --class implementation --objective "C1 task kind" --feature F-0001 \
        --status READY --allowed 'src/**' --fields '{"requirements":["REQ-0001"],"role":"backend-engineer"}' \
        | jget 'd["result"]["id"]')
case "$TID" in TASK-*) gov "$ROOT" task show "$TID" | grep -q '"status"'; chk C1-task $? "task $TID created and read back with a status" "task created but unreadable";; *) fail C1-task "no task id returned: $TID";; esac

# experiments — the governed experiment lifecycle
EID=$(gov "$ROOT" experiment design --fields '{"hypothesis":"integer cents avoid drift","method":"replay ledger","data_provenance":"synthetic","outputs":["spec/experiments/EXP-run.md"]}' | jget 'd.get("result",{}).get("experiment",{}).get("id","")')
case "$EID" in EXP-*) pass C1-experiment "experiment $EID recorded (DESIGNED)";; *) fail C1-experiment "gov experiment design returned no id: $EID";; esac

# claims — a claim is current truth about who holds the work (a runnable task, claimed, then read back)
CTID=$(gov "$ROOT" task create --class specification --objective "C1 claim kind" --status READY \
        --allowed 'spec/**' --fields '{"role":"product-spec-agent"}' | jget 'd.get("result",{}).get("id","")')
GOV_AS_ROLE=product-spec-agent GOV_SESSION_ID=hs-claim gov "$ROOT" task claim "$CTID" > "$Q" 2>&1
CL=$(gov "$ROOT" claims list | jget 'json.dumps(d.get("result"))')
case "$CL" in *"$CTID"*) pass C1-claims "claim on $CTID is current truth in the claims store";; *) fail C1-claims "no claim recorded for $CTID: $CL / $(head -c 200 "$Q")";; esac

# transactions — a change-impact transaction
MF=$BETA_SCRATCH/c1-cit.json
printf '%s' '[{"op":"set_status","target":"D-0001","value":"SUPERSEDED"}]' > "$MF"
CID=$(gov "$ROOT" cit propose --proposal "C1 transaction kind" --trigger governance_change --targets D-0001 --manifest "$MF" | jget 'd.get("result",{}).get("id","")')
case "$CID" in CIT-*) gov "$ROOT" cit list | grep -q "$CID"; chk C1-transactions $? "transaction $CID recorded and listed" "transaction $CID not listed";; *) fail C1-transactions "no CIT id returned: $CID";; esac

# statuses — reconstructed project state naming the record statuses
gov "$ROOT" status > "$Q" 2>&1
python3 - "$Q" <<'PY' && pass C1-statuses "gov status reconstructs current statuses of governed records" || fail C1-statuses "gov status carries no per-record status"
import json,sys
d=json.load(open(sys.argv[1]))["result"]
s=json.dumps(d)
sys.exit(0 if ('"status"' in s and ("F-0001" in s or "features" in s)) else 1)
PY

# skill versions
gov "$ROOT" skills list > "$Q" 2>&1
python3 -c "
import json,sys
r=json.load(open(sys.argv[1]))['result']
sys.exit(0 if any(x.get('version') for x in r) else 1)" "$Q"
chk C1-skill-versions $? "skill registry carries versioned skills" "skills carry no version"

# tool versions
gov "$ROOT" tools list > "$Q" 2>&1
python3 -c "
import json,sys
r=json.load(open(sys.argv[1]))['result']
t=r['tools'] if isinstance(r,dict) else r
sys.exit(0 if any(x.get('version') for x in t) else 1)" "$Q"
chk C1-tool-versions $? "tool registry carries versioned tools" "tools carry no version"

# model-routing records — recorded empirical routing evidence, persisted and read back
EV=$BETA_SCRATCH/c1-route.json
printf '%s' '{"model":"m-probe","provider":"p-probe","task_class":"implementation","reasoning_effort":"medium","cost":0.01,"latency_ms":12,"pass":true,"repair_count":0,"reviewer_findings":0}' > "$EV"
gov "$ROOT" route --record "$EV" > "$Q" 2>&1
OKR=$(jget 'd.get("ok")' < "$Q")
if [ "$OKR" = "true" ] && grep -q "m-probe" "$ROOT/.governance-runtime/routing/evidence.jsonl" 2>/dev/null; then
  pass C1-model-routing "a model-routing record is recorded and persisted (routing/evidence.jsonl)"
else
  fail C1-model-routing "no persisted model-routing record: $(head -c 250 "$Q")"
fi

# index manifests
python3 -c "
import json,sys
m=json.load(open(sys.argv[1]))
sys.exit(0 if m.get('embedder') and m.get('artifacts') else 1)" "$ROOT/governance/generated/index-manifest.json"
chk C1-index-manifest $? "index manifest records component identity and artefact digests" "index manifest missing or empty"

summary
