#!/usr/bin/env bash
# P2-AR-0010 — E2 Representative roles (Contract v3 lines 368-375).
# Each representative role is exercised as a capability contract: authority level (an allow/deny pair around its
# level), routing (minimum tier / reasoning from the verified kernel ROLES.yaml), tool permission classes
# (TOOL_PERMISSIONS via `tools resolve`), and skills (`skills resolve` by class+role).
source "$(dirname "$0")/lib.sh"
R=$(mkproj e2)
echo "project: $R"

hdr "E2.0 the kernel role catalogue as the product reads it (trusted root) — every role resolves to a level"
for r in orchestrator product-spec-agent research-agent architecture-agent ux-agent frontend-engineer backend-engineer data-engineer integration-engineer ai-ml-engineer devops-engineer security-engineer performance-engineer data-author independent-test-designer test-execution-agent integration-agent change-controller memory-engineer tooling-engineer independent-auditor release-agent routine-documentation migration-executor migration-reviewer migration-verifier memory-verifier human; do
  o=$(g "$R" "$r" S-$r route --class implementation)
  echo "$o" | python3 -c 'import json,sys;e=json.load(sys.stdin);r=e["result"];print("  %-26s min_tier=%s reasoning=%s" % (r["role"], r["minimum_tier"], r["reasoning"]))'
done

profile() { # profile <role> <label> ; <op-allowed-at-level> <op-denied-above-level>
  local role="$1" label="$2"
  hdr "E2.$label role '$role'"
  g "$R" "$role" S-$role route --class implementation | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  routing: min_tier=%s reasoning=%s" % (r["minimum_tier"], r["reasoning"]))'
  printf '  tools resolve run_tests: '; g "$R" "$role" S-$role tools resolve --capability run_tests | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("tools=",[t["tool_id"] for t in r["tools"]],"gap=",r["capability_gap"],"reason=",r["reason"])'
  printf '  tools resolve web_search: '; g "$R" "$role" S-$role tools resolve --capability web_search | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("tools=",[t["tool_id"] for t in r["tools"]],"gap=",r["capability_gap"],"reason=",r["reason"])'
}
# fixture tasks with designated roles, used for skills resolution
mk() { g "$R" orchestrator S0 task create --id "$1" --class "$2" --objective "$3" --status READY --fields "{\"role\":\"$4\"}" >/dev/null; }
mk TASK-ARCH architecture "architecture impact" architecture-agent
mk TASK-RES research "benchmark" research-agent
mk TASK-DATA data "dataset" data-author
mk TASK-IMPL implementation "impl" backend-engineer
mk TASK-MEM memory "memory rebuild" memory-engineer
mk TASK-TD test-design "tests" independent-test-designer
mk TASK-SEC security "threat model" security-engineer
mk TASK-REL release "release" release-agent
mk TASK-TOOL tooling "install tool" tooling-engineer
skills() { printf '  skills resolve %-10s: ' "$1"; g "$R" orchestrator S0 skills resolve "$1" | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print([s["id"]+"@"+s["version"] for s in r["candidates_by_class_role"]])'; }

profile orchestrator b1-orchestrator
cmd "orchestrator-only operations: resume (L4), gate revoke (L4); a worker may not be handed the orchestrator role implicitly (INV-014)"
gq "$R" orchestrator S0 resume
gq "$R" orchestrator S0 handoff create --to-role orchestrator --task TASK-IMPL
gq "$R" orchestrator S0 handoff create --to-role orchestrator --task TASK-IMPL --fields '{"explicit_orchestrator_assignment": true}'

for r in architecture-agent research-agent data-engineer data-author backend-engineer; do profile "$r" b2-domain; done
skills TASK-ARCH; skills TASK-RES; skills TASK-DATA; skills TASK-IMPL
cmd "domain roles are bounded: backend-engineer (L1) cannot create tasks; architecture-agent (L2) can but cannot execute a CIT (L3)"
gq "$R" backend-engineer S-be task create --class implementation --objective x
gq "$R" architecture-agent S-aa task create --class architecture --objective x
g "$R" orchestrator S0 cit propose --proposal "arch probe" --trigger editorial >/dev/null
gq "$R" architecture-agent S-aa cit execute "$(ls "$R/spec/decisions" | grep CIT | tail -1 | sed 's/.yaml//')"

profile memory-engineer b3-memory
skills TASK-MEM
cmd "memory-engineer (L2) may benchmark memory (memory_benchmark L2); backend-engineer (L1) may not"
gq "$R" memory-engineer S-me memory benchmark --candidate current --candidate builtin:64
gq "$R" backend-engineer S-be memory benchmark --candidate current --candidate builtin:64

profile independent-test-designer b4-test-author
skills TASK-TD
g "$R" orchestrator S0 skills list | python3 -c 'import json,sys;[print("  ",s["id"],s["version"],"roles=",s["roles"],"classes=",s["task_classes"]) for s in json.load(sys.stdin)["result"] if s["id"]=="SKL-TEST-DESIGN"]'

for r in independent-auditor migration-verifier memory-verifier; do profile "$r" b5-verifier; done
cmd "verifier/auditor roles are L0: may run the governance suite, may not mutate governed state"
gq "$R" independent-auditor S-ia audit --no-persist
gq "$R" independent-auditor S-ia task status TASK-IMPL DONE

for r in security-engineer release-agent; do profile "$r" b6-security-release; done
skills TASK-SEC; skills TASK-REL
printf '  tools resolve secret_scan as security-engineer: '; g "$R" security-engineer S-se tools resolve --capability secret_scan | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print([t["tool_id"] for t in r["tools"]])'
cmd "security-engineer holds SECRET_READ (TOOL_PERMISSIONS); backend-engineer does not (generated role exposure)"
g "$R" orchestrator S0 tools registry | python3 -c 'import json,sys;x=json.load(sys.stdin)["result"]["role_exposure"];print("  security-engineer:",x["security-engineer"]["permissions"]);print("  backend-engineer :",x["backend-engineer"]["permissions"]);print("  release-agent    :",x["release-agent"]["permissions"])'

hdr "E2.b7 project-specific roles through governed extension"
cmd "a project wants a 'data-scientist' role: acting as it (read-only status needs no level; claiming a task does)"
gq "$R" data-scientist S-ds status
gq "$R" data-scientist S-ds task claim TASK-DATA
cmd "declare it in the project overlay TOOL_PERMISSIONS.roles (the only project-writable role list)"
python3 - "$R" <<'PY'
import sys,yaml,os
p=os.path.join(sys.argv[1],"governance/project/TOOL_PERMISSIONS.yaml"); d=yaml.safe_load(open(p)); d["roles"]["data-scientist"]=["READ_REPO","RUN_TESTS"]; yaml.safe_dump(d,open(p,"w"),sort_keys=False)
PY
gq "$R" data-scientist S-ds task claim TASK-DATA
g "$R" orchestrator S0 audit --no-persist | python3 -c 'import json,sys;e=json.load(sys.stdin);r=e.get("result") or e["error"]["details"];print("  audit authority_role_limits findings:",[f["message"] for f in r["findings"] if f.get("family")=="authority_role_limits"])'
cmd "a project ROLES.yaml under governance/project (no loader exists; shown for completeness)"
mkdir -p "$R/governance/project/roles"; printf 'roles:\n  - {id: data-scientist, name: Data Scientist, level: L1, minimum_tier: T2, default_reasoning: medium}\n' > "$R/governance/project/roles/ROLES.yaml"
gq "$R" data-scientist S-ds task claim TASK-DATA
cmd "handoff to a project role"
gq "$R" orchestrator S0 handoff create --to-role data-scientist --task TASK-DATA
cmd "source search: every role lookup reads only the trusted kernel ROLES.yaml"
grep -rn 'ROLES.yaml' "$WT/runtime/src" --include=*.rs | sed "s|$WT/||" | sed 's/^/  /'
echo END
