#!/usr/bin/env bash
# P2-AR-0049 held-out probe — Gate K (Contract v3:638-650)
#   K3 automatic impact simulation auto-triggers for material: architecture, behaviour, interfaces, security,
#      governance/policy, infrastructure cost, acceptance criteria, data migration
#   K4 impact radius R0-R5 affects traversal / test scope / model tier / agents / human approval / rollback
# Attack: the proposer's label is always "editorial"; the OS must derive materiality from what the change touches.
cd "$(dirname "$0")" && . ./lib.sh
machine kmat && seed_spec && seed_acceptance_test
mkdir -p "$MROOT/spec/architecture" "$MROOT/spec/interfaces" "$MROOT/infra" "$MROOT/migrations" "$MROOT/src/auth"
cat > "$MROOT/spec/architecture/ARCH-0100.yaml" <<'YML'
id: ARCH-0100
type: architecture
title: Checkout storage boundary
status: ACTIVE
decision: the checkout service owns its own datastore
YML
cat > "$MROOT/spec/interfaces/IFACE-0100.yaml" <<'YML'
id: IFACE-0100
type: interface
title: Ledger HTTP contract
status: ACTIVE
operations: ["GET /ledger/{id}"]
YML
cat > "$MROOT/spec/architecture/SEC-0100.yaml" <<'YML'
id: SEC-0100
type: security
title: Ledger request authentication
status: ACTIVE
controls: ["every ledger call presents a signed token"]
YML
cat > "$MROOT/infra/ledger.tf" <<'TF'
resource "aws_db_instance" "ledger" { instance_class = "db.t3.small" }
TF
cat > "$MROOT/migrations/0001_ledger.sql" <<'SQL'
CREATE TABLE ledger (id INTEGER PRIMARY KEY, total_cents INTEGER NOT NULL);
SQL
cat > "$MROOT/src/auth/verify.rs" <<'RS'
pub fn verify_signature(sig: &str) -> bool { !sig.is_empty() }
RS
# product source, as the project's own REPOSITORY_CONTRACT classifies it (class `source`): `product/**`
mkdir -p "$MROOT/product"
cat > "$MROOT/product/ledger.rs" <<'RS'
pub fn total_cents(v: &[(i64,i64)]) -> i64 { v.iter().map(|(q,c)| q*c).sum() }
RS
git -C "$MROOT" add -A >/dev/null 2>&1; git -C "$MROOT" commit -qm "material subjects" >/dev/null 2>&1
g rebuild-memory >/dev/null 2>&1

# k3_cit <label> <expected-class> <manifest-json>
k3_cit() {
  local label="$1" want="$2" mf="$3"
  local f="$MROOT/.governance-runtime/k3-$label.json"
  printf '%s' "$mf" > "$f"
  local id out
  id="$(res cit propose --proposal "purely editorial: $label" --trigger editorial --title "$label" --manifest "$f" | python3 -c "import json,sys;d=json.load(sys.stdin);print(d.get('id','ERR'))")"
  out="$(res cit show "$id")"
  local derived material sim gate
  derived="$(echo "$out" | python3 -c "import json,sys;print(','.join(json.load(sys.stdin)['materiality']['derived_classes']))")"
  material="$(echo "$out" | python3 -c "import json,sys;print(json.load(sys.stdin)['materiality']['material'])")"
  sim="$(echo "$out" | python3 -c "import json,sys;print('yes' if json.load(sys.stdin).get('impact') else 'no')")"
  gate="$(echo "$out" | python3 -c "import json,sys;print(json.load(sys.stdin).get('human_gate'))")"
  echo "   $label -> derived=[$derived] material=$material auto_simulated=$sim gate=$gate"
  check "$(python3 -c "print(1 if '$want' in '$derived'.split(',') and '$material'=='True' and '$sim'=='yes' else 0)")" \
        "K3.$label a change labelled 'editorial' is derived as $want and auto-simulated" "derived=$derived material=$material sim=$sim"
  K3_LAST_GATE="$gate"; K3_LAST_ID="$id"
}

echo "== K3  auto-trigger, per material class, with the proposer's label set to 'editorial' throughout"
k3_cit architecture architecture_change '[{"op":"set_field","target":"ARCH-0100","field":"decision","value":"the checkout service shares the monolith datastore"}]'
k3_cit behaviour behaviour_change '[{"op":"write_file","path":"product/ledger.rs","content":"pub fn total_cents(v: &[(i64,i64)]) -> i64 { v.iter().map(|(q,c)| q*c).sum::<i64>() / 2 }\n"}]'
k3_cit interfaces interface_change '[{"op":"set_field","target":"IFACE-0100","field":"operations","value":["GET /ledger/{id}","DELETE /ledger/{id}"]}]'
k3_cit security security_change '[{"op":"write_file","path":"src/auth/verify.rs","content":"pub fn verify_signature(_sig: &str) -> bool { true }\n"}]'
k3_cit governance governance_change '[{"op":"write_file","path":"governance/project/PROJECT_POLICY.yaml","content":"policy: PROJECT_POLICY\nversion: 1.0.0\n"}]'
k3_cit infrastructure infrastructure_cost '[{"op":"write_file","path":"infra/ledger.tf","content":"resource \"aws_db_instance\" \"ledger\" { instance_class = \"db.r5.8xlarge\" }\n"}]'
k3_cit acceptance acceptance_criteria_change '[{"op":"set_field","target":"REQ-0001","field":"acceptance_criteria","value":["total_cents may round to the nearest cent"]}]'
k3_cit migration data_migration '[{"op":"write_file","path":"migrations/0002_drop.sql","content":"ALTER TABLE ledger DROP COLUMN total_cents;\n"}]'

echo "== K3  the same eight classes made inside an ordinary task, never through CIT-P"
# read-only classification of changes already made (cit classify --paths)
CLS="$(res cit classify --paths 'spec/architecture/ARCH-0100.yaml,src/auth/verify.rs,infra/ledger.tf,migrations/0001_ledger.sql,spec/interfaces/IFACE-0100.yaml,governance/project/PROJECT_POLICY.yaml' 2>/dev/null)"
echo "   classify (read-only) -> $(echo "$CLS" | head -c 300)"

# a general task whose contract allows every one of those paths; each material edit must still be refused at close
TASK="$(res task create --class implementation --objective "Sweep the ledger surfaces" --feature F-0001 --status READY --allowed 'src/**,spec/**,infra/**,migrations/**,governance/project/**' --fields '{"requirements":["REQ-0001"],"scenarios":["SCN-0001"],"acceptance_tests":["TST-0001"],"role":"backend-engineer"}' | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
SESSION=t1 ROLE=backend-engineer g task claim "$TASK" >/dev/null
python3 - "$MROOT" <<'PY'
import sys, os, yaml
r = sys.argv[1]
d = yaml.safe_load(open(os.path.join(r, "spec/architecture/ARCH-0100.yaml"))); d["decision"] = "shared datastore"
yaml.safe_dump(d, open(os.path.join(r, "spec/architecture/ARCH-0100.yaml"), "w"), sort_keys=False)
d = yaml.safe_load(open(os.path.join(r, "spec/interfaces/IFACE-0100.yaml"))); d["operations"] = ["GET /ledger/{id}", "DELETE /ledger/{id}"]
yaml.safe_dump(d, open(os.path.join(r, "spec/interfaces/IFACE-0100.yaml"), "w"), sort_keys=False)
d = yaml.safe_load(open(os.path.join(r, "spec/requirements/REQ-0001.yaml"))); d["acceptance_criteria"] = ["rounding is allowed"]
yaml.safe_dump(d, open(os.path.join(r, "spec/requirements/REQ-0001.yaml"), "w"), sort_keys=False)
open(os.path.join(r, "src/auth/verify.rs"), "w").write("pub fn verify_signature(_sig: &str) -> bool { true }\n")
open(os.path.join(r, "infra/ledger.tf"), "w").write('resource "aws_db_instance" "ledger" { instance_class = "db.r5.8xlarge" }\n')
open(os.path.join(r, "migrations/0002_drop.sql"), "w").write("ALTER TABLE ledger DROP COLUMN total_cents;\n")
open(os.path.join(r, "governance/project/PROJECT_POLICY.yaml"), "a").write("\n# edited inside an ordinary task\n")
PY
g rebuild-memory --incremental >/dev/null 2>&1
RP="$(SESSION=t1 ROLE=backend-engineer receipt "$TASK" sweep "swept every ledger surface" "spec/architecture/ARCH-0100.yaml,spec/interfaces/IFACE-0100.yaml,spec/requirements/REQ-0001.yaml,src/auth/verify.rs,infra/ledger.tf,migrations/0002_drop.sql,governance/project/PROJECT_POLICY.yaml" not_applicable_with_reason "$NA_TESTS")"
ERR="$(SESSION=t1 ROLE=backend-engineer emsg task close "$TASK" --report "$RP")"
CODE="$(echo "$ERR" | python3 -c "import json,sys;print(json.load(sys.stdin).get('code','OK'))")"
echo "   in-task close -> $CODE"
check_eq "$CODE" MATERIAL_CHANGE_REQUIRES_CIT "K3.intask the close of an ordinary task carrying material changes is refused"
REF="$(echo "$ERR" | python3 -c "import json,sys;d=json.load(sys.stdin).get('details') or {};print(','.join(sorted({x['class'] for x in d.get('refused',[])})))")"
echo "   refused classes: $REF"
for c in architecture_change interface_change security_change governance_change infrastructure_cost acceptance_criteria_change data_migration; do
  check "$(python3 -c "print(1 if '$c' in '$REF'.split(',') else 0)")" "K3.intask.$c is refused outside change control inside a task" "refused=$REF"
done
# behaviour changes to product source are what an implementation task is contracted to make: the OS classifies them
# as material (so CIT-P auto-simulates one proposed as a CIT) but does not require a CIT inside a task
BCLS="$(res cit classify --paths 'product/ledger.rs' --base HEAD~1 2>/dev/null)"
echo "   product-source behaviour classification: $(echo "$BCLS" | python3 -c "import json,sys;m=json.load(sys.stdin)['materiality'];print(m['derived_classes'], 'requires_cit_in_task=', [f['requires_cit_in_task'] for f in m['findings']])")"
check "$(echo "$BCLS" | python3 -c "import json,sys;m=json.load(sys.stdin)['materiality'];print(1 if 'behaviour_change' in m['derived_classes'] and all(not f['requires_cit_in_task'] for f in m['findings']) else 0)")" "K3.intask.behaviour_change product-source behaviour is classified material but left to the task contract" "$(echo "$BCLS" | head -c 300)"
# it is still propagated: a change outside change control is detected and its dependents marked
PROP="$(res cit propagate --dry-run 2>/dev/null)"
echo "   NOTE direct-change propagation (dry run): $(echo "$PROP" | head -c 300)"

echo "== K4  the impact radius drives traversal, test scope, human approval and rollback"
declare -A RAD
for r in R0 R5; do :; done
cat > "$MROOT/.governance-runtime/k4-r0.json" <<'JSON'
[{"op":"write_file","path":"docs/notes.md","content":"notes v2\n"}]
JSON
mkdir -p "$MROOT/docs"; echo "notes" > "$MROOT/docs/notes.md"
git -C "$MROOT" add -A >/dev/null 2>&1; git -C "$MROOT" commit -qm docs >/dev/null 2>&1; g rebuild-memory --incremental >/dev/null 2>&1
R0ID="$(res cit propose --proposal "editorial note" --trigger editorial --title r0 --manifest "$MROOT/.governance-runtime/k4-r0.json" | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
g cit simulate "$R0ID" >/dev/null
cat > "$MROOT/.governance-runtime/k4-r5.json" <<'JSON'
[{"op":"write_file","path":"governance/project/REPOSITORY_CONTRACT.yaml","content":"version: 1.1.0\nclasses: {}\n"}]
JSON
R5ID="$(res cit propose --proposal "governance change" --trigger editorial --title r5 --manifest "$MROOT/.governance-runtime/k4-r5.json" | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
K4() { res cit show "$1" | python3 -c "import json,sys;i=json.load(sys.stdin)['impact'];print(json.dumps({'radius':i['radius'],'depth':[c for c in i['consequences'] if 'graph depth' in c],'semantic':len(i.get('semantic_candidates') or []),'tests':len(i.get('tests_required') or []),'gate':i.get('human_gate_required'),'tier':i.get('minimum_model_tier')}))"; }
A="$(K4 "$R0ID")"; B="$(K4 "$R5ID")"
echo "   R0: $A"
echo "   R5: $B"
check "$(python3 -c "
import json;a=json.loads('''$A''');b=json.loads('''$B''')
print(1 if a['radius']=='R0' and b['radius']=='R5' else 0)")" "K4.1 radii are produced and differ with what the change touches"
check "$(python3 -c "
import json;a=json.loads('''$A''');b=json.loads('''$B''')
print(1 if 'depth 0' in str(a['depth']) and 'depth 5' in str(b['depth']) else 0)")" "K4.2 the radius sets the graph traversal depth"
check "$(python3 -c "
import json;a=json.loads('''$A''');b=json.loads('''$B''')
print(1 if a['semantic']==0 and b['semantic']>0 else 0)")" "K4.3 the radius sets the semantic/lexical breadth"
check "$(python3 -c "
import json;a=json.loads('''$A''');b=json.loads('''$B''')
print(1 if a['gate'] in (False,None) and b['gate']==True else 0)")" "K4.4 the radius (with the trigger) decides whether human approval is required"
echo "   -- model tier by radius, at a role whose own floor does not saturate it"
TIERS="$(for r in R0 R1 R2 R3 R4 R5; do ROLE=routine-documentation res route --class documentation --radius $r | python3 -c "import json,sys;print(json.load(sys.stdin)['minimum_tier'],end=' ')"; done)"
echo "      $TIERS"
check "$(python3 -c "print(1 if '$TIERS'.split()==['T1','T1','T2','T2','T3','T3'] else 0)")" "K4.5 the radius raises the model tier (MODEL_ROUTING_POLICY.radius_minimum_tier)" "$TIERS"
CITTIERS="$(python3 -c "
import json;a=json.loads('''$A''');b=json.loads('''$B''');print(a['tier'],b['tier'])")"
echo "   NOTE a CIT's own minimum_model_tier at R0 vs R5: $CITTIERS"
RB0="$(res cit show "$R0ID" | python3 -c "import json,sys;print([c for c in json.load(sys.stdin)['impact']['consequences'] if 'rollback' in c])")"
RB5="$(res cit show "$R5ID" | python3 -c "import json,sys;print([c for c in json.load(sys.stdin)['impact']['consequences'] if 'rollback' in c])")"
echo "   NOTE rollback consequence at R0: $RB0"
echo "   NOTE rollback consequence at R5: $RB5"
check "$([ "$RB0" != "$RB5" ] && echo 1 || echo 0)" "K4.6 the radius changes the rollback consequence the OS states" "identical at R0 and R5: $RB0"
AG="$(res cit show "$R5ID" | python3 -c "import json,sys;i=json.load(sys.stdin)['impact'];s=json.dumps(i).lower();print(1 if ('agents' in s or 'reviewers' in s or 'specialist' in s) else 0)")"
check "$AG" "K4.7 the radius determines the agents/reviewers the change needs" "no agent or reviewer output in the impact at R5"

summary
