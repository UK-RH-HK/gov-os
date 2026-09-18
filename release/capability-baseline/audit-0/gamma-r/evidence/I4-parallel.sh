#!/usr/bin/env bash
# P2-AR-0010 — I4 Parallel execution (Contract v3 lines 585-590).
source "$(dirname "$0")/lib.sh"
R=$(mkproj i4)
echo "project: $R"
mk() { g "$R" orchestrator S0 task create --id "$1" --class documentation --objective "$1" --status READY "${@:2}" >/dev/null; }
dag() { g "$R" orchestrator S0 task dag; }

# Feature F-A chain whose dependency order is the REVERSE of id order: TASK-A1 depends on A2, A2 depends on A3 (A3 first)
write_feature "$R" F-A "$(readiness_json '' '')"; write_feature "$R" F-B "$(readiness_json '' '')"
mk TASK-A3 --feature F-A
mk TASK-A2 --feature F-A --deps TASK-A3
mk TASK-A1 --feature F-A --deps TASK-A2
mk TASK-B1 --feature F-B
mk TASK-B2 --feature F-B
mk TASK-G1 --feature F-B
g "$R" orchestrator S0 gate create --question "May TASK-G1 proceed?" --fields '{"id":"HDG-0001","blocks_tasks":["TASK-G1"],"impact_radius":"R3","reversibility":"irreversible","confidence":0.5}' >/dev/null
( cd "$R" && git add -A && git commit -qm i4 )

hdr "I4.b1 runnable / blocked sets"
dag | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  runnable:",r["runnable"]);print("  blocked:",r["blocked"]);print("  waiting_human:",r["waiting_human"]);print("  counts:",r["counts"])'
hdr "I4.b2 critical path (longest open dependency chain; cycles reported)"
dag | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  longest_chain:",r["longest_chain"],"cycles:",r["cycles"])'
mk TASK-CY1 --deps TASK-CY2; mk TASK-CY2 --deps TASK-CY1
dag | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  with a 2-cycle: cycles=",r["cycles"],"longest_chain=",r["longest_chain"])'
g "$R" orchestrator S0 task status TASK-CY1 CANCELLED >/dev/null; g "$R" orchestrator S0 task status TASK-CY2 CANCELLED >/dev/null
hdr "I4.b3 per-feature end-to-end path"
dag | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  per_feature:",r["per_feature"])'
echo "  (F-A end-to-end dependency path is TASK-A3 -> TASK-A2 -> TASK-A1; compare the per_feature entry)"
g "$R" orchestrator S0 status | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  gov status carries per-feature path?:", "per_feature" in json.dumps(r), "features:", r["features"])'
hdr "I4.b4 human-gate dependencies"
dag | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  human_gate_dependencies:",r["human_gate_dependencies"])'
g "$R" orchestrator S0 gate list | python3 -c 'import json,sys;print("  pending gates:",[(x["id"],x["blocks_tasks"],x["priority_score"]) for x in json.load(sys.stdin)["result"]])'
hdr "I4.b5 independent branches continue while one branch waits for human input"
cmd "one session: continue presents the gate AND offers independent work"
g "$R" orchestrator S-one continue | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  status:",r["status"],"task:",r.get("task"),"parallel:",r.get("parallel_runnable"),"gate shown:",bool(r.get("gate")))'
cmd "two agents in turn: S-w1 continue --claim, then S-w2 continue --claim"
g "$R" backend-engineer S-w1 continue --claim | python3 -c 'import json,sys;e=json.load(sys.stdin);r=e.get("result",{});print("  S-w1:",e["ok"],r.get("task"),(r.get("claimed") or {}).get("session_id"),(e.get("error") or {}).get("code"))'
g "$R" backend-engineer S-w2 continue --claim | python3 -c 'import json,sys;e=json.load(sys.stdin);r=e.get("result",{});print("  S-w2:",e["ok"],r.get("task"),(r.get("claimed") or {}).get("session_id"),(e.get("error") or {}).get("code"),str((e.get("error") or {}).get("message",""))[:140])'
dag | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  runnable now (includes tasks already IN_PROGRESS under another session):",r["runnable"])'
cmd "S-w2 without --claim: what does continue offer?"
g "$R" backend-engineer S-w2 continue | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  offered:",r.get("task"),"parallel:",r.get("parallel_runnable"))'
cmd "HUMAN_GATE_POLICY.continue_independent_work=false switches to a global stop (policy-driven)"
python3 - "$R/governance/project/PROJECT_POLICY.yaml" <<'PY'
import yaml,sys; p=sys.argv[1]; d=yaml.safe_load(open(p)); d["policy_overrides"]={"HUMAN_GATE_POLICY.continue_independent_work": False}; yaml.safe_dump(d,open(p,"w"),sort_keys=False)
PY
g "$R" orchestrator S0 policy overrides | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  override applied:",r["applied"],"refused:",r["refused"])'
g "$R" orchestrator S-one continue | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  continue:",r["status"],r.get("message"))'
echo END
