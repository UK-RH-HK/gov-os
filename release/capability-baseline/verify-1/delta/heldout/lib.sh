# P2-AR-0049 held-out harness library (family delta, verification iteration 1).
#
# Independent evidence: the administrator/owner domain here is the verifier's own (hc.py), with key material and
# metadata this run generates. Nothing is copied from the product's certification harness; the metadata format is
# read from runtime/src/srr/metadata.rs and runtime/src/human_channel.rs.
#
# The documented first-run path is followed for every scenario machine: provision a throw-away root
# (OWNER-DECISION-P2-0002), bind the machine's T2 authority (P2-ADJ-0002), then install a signed release.
set -u

HELDOUT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WT="$(cd "$HELDOUT_DIR/../../../../.." && pwd)"
GOV="$WT/target/release/gov"
export GOV
HC="python3 $HELDOUT_DIR/hc.py"
SCRATCH="${DELTA_SCRATCH:-/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/1b6c780e-2b37-439f-a969-a8d96b7ad35e/scratchpad/dlt}"
ADMIN="$SCRATCH/admin"           # the administrator domain: outside every project
RELEASE_DIR="$ADMIN/rel-100"

# the close receipt's test status for this synthetic project: no product test runner is configured, and the product
# refuses a "passed" claim it cannot evidence (PRODUCT_TEST_EVIDENCE_REQUIRED), so the contract-valid value is the
# explicit not_applicable_with_reason.
NA_TESTS='{"tests":{"status":"not_applicable_with_reason","reason":"no product test runner is configured in this synthetic project; the governed records and files are the deliverable"}}'

PASS=0; FAIL=0
ok()   { PASS=$((PASS+1)); echo "PASS  $1"; }
bad()  { FAIL=$((FAIL+1)); echo "FAIL  $1"; }
check(){ if [ "$1" = "1" ]; then ok "$2"; else bad "$2${3:+  -- $3}"; fi; }
# check_eq <actual> <expected> <label>
check_eq(){ if [ "$1" = "$2" ]; then ok "$3"; else bad "$3  -- expected '$2', got '$1'"; fi; }
summary(){ echo "---- $(basename "$0"): $PASS passed, $FAIL failed"; [ "$FAIL" = 0 ]; }

admin_domain() {
  mkdir -p "$ADMIN"
  [ -f "$ADMIN/root-1.json" ] || $HC root "$ADMIN/root-1.json"
  [ -f "$ADMIN/bind-auth-1.json" ] || $HC bindauth "$ADMIN/bind-auth-1.json"
  [ -f "$ADMIN/bind-key.json" ] || $HC bindkey "$ADMIN/bind-key.json"
}

# seed_kernel: a staged kernel payload to sign, taken from a bootstrap install (never from the release directory).
seed_kernel() {
  if [ ! -d "$SCRATCH/seed/governance/kernel" ]; then
    mkdir -p "$SCRATCH/seed"; ( cd "$SCRATCH/seed" && git init -q . && git config user.email v@x && git config user.name v )
    XDG_STATE_HOME="$SCRATCH/seedmachine" "$GOV" --json --root "$SCRATCH/seed" --role orchestrator init >/dev/null
  fi
  echo "$SCRATCH/seed/governance/kernel"
}

signed_release() {
  admin_domain
  if [ ! -d "$RELEASE_DIR/kernel" ]; then
    $HC release "$(seed_kernel)" "$RELEASE_DIR" 100 >/dev/null
  fi
  echo "$RELEASE_DIR/kernel"
}

# machine <name> -> sets MROOT (project root) and MSTATE (XDG_STATE_HOME); provisioned, bound, kernel installed.
# DELTA_RUN makes each run's machines distinct, so a re-run never inherits a previous run's state
# (`rm` is denied in this environment; nothing is deleted, each run gets its own directory).
machine() {
  local name="$1-${DELTA_RUN:-1}"; local root="$SCRATCH/m-$name"
  MROOT="$root"; MSTATE="$SCRATCH/state-$name"
  if [ -d "$root/governance" ]; then return 0; fi
  mkdir -p "$root"; ( cd "$root" && git init -q . && git config user.email v@x && git config user.name v && echo "# $name" > README.md && git add -A && git commit -qm init )
  local rel; rel="$(signed_release)"
  XDG_STATE_HOME="$MSTATE" "$GOV" --json --root "$root" --role orchestrator trust provision --anchor "$ADMIN/root-1.json" >/dev/null
  XDG_STATE_HOME="$MSTATE" "$GOV" --json --root "$root" --role orchestrator trust bind --authority "$ADMIN/bind-auth-1.json" --key "$ADMIN/bind-key.json" >/dev/null
  XDG_STATE_HOME="$MSTATE" "$GOV" --json --root "$root" --role orchestrator init --source "$rel" >/dev/null
}

# g <args...> — run gov on the current machine as $ROLE (default orchestrator), session $SESSION (default s1)
g() { XDG_STATE_HOME="$MSTATE" "$GOV" --json --root "$MROOT" --session "${SESSION:-s1}" --role "${ROLE:-orchestrator}" "$@"; }
# gq: same, quiet on stderr
gq() { g "$@" 2>/dev/null; }
# jq-free field read: J <json> <python expression over d>
J() { python3 -c "import json,sys;d=json.load(sys.stdin);print(eval(sys.argv[1]))" "$1"; }
# res <args...> -> the result object; err <args...> -> the error code
res() { g "$@" | python3 -c "import json,sys;print(json.dumps(json.load(sys.stdin).get('result')))"; }
code() { g "$@" | python3 -c "import json,sys;d=json.load(sys.stdin);print('OK' if d.get('ok') else d['error']['code'])"; }
emsg() { g "$@" | python3 -c "import json,sys;d=json.load(sys.stdin);print(json.dumps(d.get('error',{})))"; }

# human_answer <gate> <option> [signer] — the owner signs the exact rendered package, out of band.
human_answer() {
  local gate="$1" option="$2" signer="${3:-owner}"
  local pres inst sha
  pres="$(g gate present "$gate")"
  inst="$(echo "$pres" | python3 -c "import json,sys;print(json.load(sys.stdin)['result']['gate']['gate_instance'])")"
  sha="$(echo "$pres" | python3 -c "import json,sys;print(json.load(sys.stdin)['result']['gate']['package_sha256'])")"
  local f="$SCRATCH/answers/$gate-$option-$RANDOM.json"; mkdir -p "$(dirname "$f")"
  $HC answer "$f" --gate "$gate" --instance "$inst" --package-sha "$sha" --option "$option" --signer "$signer"
  echo "$f"
}
# decide_human <gate> <option> [signer] -> runs gov decide with the signed answer
decide_human() {
  local f; f="$(human_answer "$@")"
  g decide "$1" --option "$2" --answer-file "$f"
}

# seed_spec: a minimal, contract-valid specification on the current machine (feature -> requirement + scenario with
# a complete H4 chain), committed and indexed. Used wherever a probe needs a legitimately green baseline
# (P2-ADJ-0003: a vacuous pass is not a pass).
seed_spec() {
  mkdir -p "$MROOT/spec/features" "$MROOT/spec/requirements" "$MROOT/spec/scenarios" "$MROOT/src" "$MROOT/tests"
  cat > "$MROOT/spec/features/F-0001.yaml" <<'YML'
id: F-0001
type: feature
title: Order totals
status: ACTIVE
capability_category: backend
requirements: [REQ-0001]
scenarios: [SCN-0001]
acceptance_tests: [TST-0001]
YML
  python3 - "$MROOT" "$WT" <<'PY'
import sys, yaml, os
root, wt = sys.argv[1], sys.argv[2]
# every readiness dimension the kernel taxonomy declares is PRESENT, except the ones this library crate genuinely
# has no instance of, which carry an explicit N/A_WITH_REASON (Contract v3 H2: a silent N/A is invalid).
dims = [d["id"] for d in yaml.safe_load(open(os.path.join(wt, "framework/taxonomy/READINESS_DIMENSIONS.yaml")))["dimensions"]]
na = {"ux_interactions": "library crate with no user interface",
      "cost_constraints": "no infrastructure is provisioned by this crate",
      "integrations": "no external system is integrated",
      "devops_runtime": "the crate ships as a library, with no runtime to operate"}
readiness = {d: ({"status": "N/A_WITH_REASON", "reason": na[d]} if d in na else "PRESENT") for d in dims}
f = yaml.safe_load(open(os.path.join(root, "spec/features/F-0001.yaml")))
f["readiness"] = readiness
yaml.safe_dump(f, open(os.path.join(root, "spec/features/F-0001.yaml"), "w"), sort_keys=False)
PY
  cat > "$MROOT/spec/requirements/REQ-0001.yaml" <<'YML'
id: REQ-0001
type: requirement
title: Ledger totals are exact integer cents
status: ACTIVE
feature: F-0001
kind: functional
acceptance_criteria: ["total_cents sums quantity*unit_cents"]
YML
  cat > "$MROOT/spec/scenarios/SCN-0001.yaml" <<'YML'
id: SCN-0001
type: scenario
title: Append two orders and total
status: ACTIVE
feature: F-0001
actor: clerk
given: ["an empty ledger"]
when: ["two orders are appended"]
then: ["total_cents is 399"]
success_criteria: ["exact total"]
failure_criteria: ["duplicate ids accepted"]
acceptance_tests: [TST-0001]
data_requirements_not_applicable: "the scenario's order lines are literal values constructed inside the acceptance test; no external or generated dataset is involved"
YML
  echo 'pub fn total_cents(v: &[(i64,i64)]) -> i64 { v.iter().map(|(q,c)| q*c).sum() }' > "$MROOT/src/lib.rs"
  git -C "$MROOT" add -A >/dev/null 2>&1; git -C "$MROOT" commit -qm "seed spec" >/dev/null 2>&1
  g rebuild-memory >/dev/null 2>&1
}

# seed_acceptance_test: the independent acceptance obligation TST-0001, produced the way the product requires — a
# test-design task claimed and closed by an independent role in its own session, so its authorship is OS-recorded
# rather than self-claimed. Leaves the feature and scenario declaring it.
seed_acceptance_test() {
  local td
  td="$(res task create --class test-design --objective "Author the independent acceptance tests for F-0001" --feature F-0001 --status READY --allowed 'spec/tasks/**,tests/**' --fields '{"requirements":["REQ-0001"],"scenarios":["SCN-0001"],"role":"independent-test-designer"}' | python3 -c "import json,sys;print(json.load(sys.stdin)['id'])")"
  SESSION=td-s ROLE=independent-test-designer g task claim "$td" >/dev/null
  mkdir -p "$MROOT/spec/tasks" "$MROOT/tests"
  cat > "$MROOT/spec/tasks/TST-0001.yaml" <<'YML'
id: TST-0001
type: test-obligation
title: Ledger acceptance tests
status: ACTIVE
feature: F-0001
scenario: SCN-0001
family: acceptance
test_path: tests/ledger_test.rs
author_role: independent-test-designer
independent_of_implementer: true
data_provenance: synthetic
YML
  echo '#[test] fn totals_are_exact() { assert_eq!(2*99 + 1*201, 399); }' > "$MROOT/tests/ledger_test.rs"
  g rebuild-memory --incremental >/dev/null 2>&1
  local r; r="$(SESSION=td-s ROLE=independent-test-designer receipt "$td" td-close "authored the acceptance obligation and its test" "spec/tasks/TST-0001.yaml,tests/ledger_test.rs" not_applicable_with_reason "$NA_TESTS")"
  SESSION=td-s ROLE=independent-test-designer g task close "$td" --report "$r" >/dev/null 2>&1
  git -C "$MROOT" add -A >/dev/null 2>&1; git -C "$MROOT" commit -qm "acceptance obligation" >/dev/null 2>&1
  g rebuild-memory --incremental >/dev/null 2>&1
}

# receipt <task> <name> <work> <files-csv> <tests-status> [extra-json] -> path of a close receipt built from the
# task's own compiled context packet (the receipt contract the OS states), so a close is refused for the reason
# under test, never for a malformed receipt.
receipt() {
  local task="$1" name="$2" work="$3" files="$4" tests="$5" extra="${6:-{\}}"
  local pk; pk="$(res context compile "$task")"
  local out="$MROOT/.governance-runtime/reports/$name.json"; mkdir -p "$(dirname "$out")"
  python3 - "$pk" "$work" "$files" "$tests" "$extra" "$out" <<'PY'
import json,sys
pk=json.loads(sys.argv[1]); work,files,tests,extra,out=sys.argv[2],sys.argv[3].split(',') if sys.argv[3] else [],sys.argv[4],json.loads(sys.argv[5]),sys.argv[6]
rc=pk.get('receipt_contract',{})
inputs=[f"{e.get('id','')}@{e.get('content_hash','')}" for e in rc.get('acknowledge_inputs',[])]
ev=[{"test":t,"result":"passed","evidence":"P2-AR-0049 held-out run"} for t in rc.get('tests_requiring_evidence',[])]
tr=rc.get('trace',{})
v={"work_completed":work,"files_changed":files,"tests":{"status":tests,"reason":"P2-AR-0049 held-out run"},
   "outcome":"success","evidence":[],"context_packet_hash":pk.get('packet_hash'),"inputs_consumed":inputs,
   "outputs_produced":files,"requirements_implemented":tr.get('requirements',[]),
   "scenarios_implemented":tr.get('scenarios',[]),"features_implemented":tr.get('features',[]),
   "decisions_applied":tr.get('decisions',[]),"constraints_applied":tr.get('constraints',[]),
   "acceptance_evidence":ev,"deviations":[],"unresolved":[]}
v.update(extra)
json.dump(v,open(out,'w'))
PY
  echo "$out"
}
