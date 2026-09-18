#!/usr/bin/env bash
# P2-AR-0010 — G1 Natural-language intent (Contract v3 lines 443-446) and G2 Small explicit human control set (448-454).
source "$(dirname "$0")/lib.sh"
R=$(mkproj g1g2)
echo "project: $R"
intent() { g "$R" orchestrator S0 intent "$1" | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  %-58s -> %-9s plan=%s commands=%s" % (repr(sys.argv[1])[:58], r["intent"], r.get("plan"), r.get("commands")))' "$1"; }

hdr "G1.b1 intent without internal command syntax (gov intent '<plain language>'; deterministic T0 patterns from the kernel COMMAND_CONTRACT)"
for t in "Where are we?" "What should we do next" "Carry on please" "Please hold everything" "Freeze, no more writes" "Undo that last transaction" "Run a health check on the repository" "Discover the best approach for caching and tell me the impact" "I choose option B" "Go ahead"; do intent "$t"; done
cmd "phrasings with no mapping"
for t in "Add a login feature" "Change the ledger to use floating point money" "Refactor the storage layer" "Who approved the last decision?"; do intent "$t"; done
cmd "how the adapters present the NL surface to an agent (generated generic adapter instruction, excerpt)"
for f in "$R"/governance/generated/adapters/*/*; do n=$(grep -c -i 'gov intent\|natural.language' "$f"); echo "  $(basename $(dirname $f))/$(basename $f): mentions of 'gov intent'/'natural language' = $n"; done
grep -n '^## Command surface' -A6 "$R/governance/generated/adapters/generic/SYSTEM_INSTRUCTION.md" | sed 's/^/  /'

hdr "G1.b2 intent maps deterministically to governed operations"
cmd "determinism: the same text twice gives byte-identical results"
a=$(g "$R" orchestrator S0 intent "Discover the best approach for caching and tell me the impact" | python3 -c 'import json,sys;print(json.dumps(json.load(sys.stdin)["result"],sort_keys=True))')
b=$(g "$R" orchestrator S0 intent "Discover the best approach for caching and tell me the impact" | python3 -c 'import json,sys;print(json.dumps(json.load(sys.stdin)["result"],sort_keys=True))')
[ "$a" = "$b" ] && echo "  identical (sha256 $(echo -n "$a" | sha256sum | cut -c1-16))" || echo "  DIFFERENT"
cmd "are the plan steps governed operations? (plan step names vs COMMAND_CONTRACT internal_operations/human_surface)"
python3 - "$R/governance/kernel/commands/COMMAND_CONTRACT.yaml" <<'PY'
import yaml,sys
c=yaml.safe_load(open(sys.argv[1]))
ops={o["operation"] for o in c["internal_operations"]} | {h["operation"] for h in c["human_surface"]}
for ip in c["intent_patterns"]:
    missing=[s for s in ip["plan"] if s not in ops]
    print("  %-9s plan=%s  not-a-governed-operation=%s" % (ip["intent"], ip["plan"], missing))
PY
cmd "negation and conflicting phrasing (longest matching substring wins)"
for t in "Do not approve that" "Don't approve it yet" "Please don't pause" "Don't stop, keep going" "Stop approving things automatically" "The status of the rollback" ; do intent "$t"; done
cmd "with a simulated CIT and a pending gate, the APPROVE/DECIDE plans resolve the pending objects"
printf '{"id":"REQ-0001","type":"requirement","title":"r","status":"ACTIVE","kind":"functional","acceptance_criteria":["a"]}\n' > "$R/spec/requirements.tmp"; mkdir -p "$R/spec/requirements"; mv "$R/spec/requirements.tmp" "$R/spec/requirements/REQ-0001.yaml"
g "$R" orchestrator S0 rebuild-memory >/dev/null
g "$R" orchestrator S0 cit propose --proposal "tighten acceptance criteria" --trigger acceptance_criteria_change --targets REQ-0001 >/dev/null
intent "Approve it"; intent "Do not approve that"; intent "my decision is option A"

hdr "G1.b3 consequential changes automatically invoke required impact/gate logic"
cmd "(a) via the governed operation: cit propose with a consequential trigger auto-simulates and raises a human gate"
out=$(g "$R" orchestrator S0 cit propose --proposal "switch persistence to postgres" --trigger architecture_change --targets REQ-0001)
echo "$out" | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("  cit",r["id"],"status",r.get("cit_status"),"auto_simulated:",bool(r.get("impact")),"radius",(r.get("impact") or {}).get("radius"),"human_gate",r.get("human_gate"))'
cmd "(b) via natural language: the intent layer returns a plan but invokes nothing (no CIT, no gate, no task is created)"
before=$(ls "$R/spec/decisions" "$R/spec/tasks" 2>/dev/null | wc -l)
intent "Discover whether we should switch persistence to postgres and tell me the impact"
intent "Switch persistence to postgres"
after=$(ls "$R/spec/decisions" "$R/spec/tasks" 2>/dev/null | wc -l); echo "  governed records before=$before after=$after"
cmd "(c) a consequential change made through an ordinary task (allowed_paths spec/**) closes with no impact simulation and no gate"
g "$R" orchestrator S0 task create --id TASK-SPEC --class specification --objective "tidy spec" --status READY --allowed 'spec/**' >/dev/null
( cd "$R" && git add -A && git commit -qm g1 )
gq "$R" product-spec-agent S-ps task claim TASK-SPEC
python3 - "$R/spec/requirements/REQ-0001.yaml" <<'PY'
import json,sys; p=sys.argv[1]; d=json.load(open(p)); d["acceptance_criteria"]=["totals may be approximate (floating point)"]; open(p,"w").write(json.dumps(d)+"\n")
PY
g "$R" product-spec-agent S-ps rebuild-memory --incremental >/dev/null
nc=$(ls "$R/spec/decisions" | grep -c CIT)
gq "$R" product-spec-agent S-ps task close TASK-SPEC --report "$(report_file "$R" spec "changed acceptance criteria" spec/requirements/REQ-0001.yaml passed)"
echo "  CIT records before/after close: $nc / $(ls "$R/spec/decisions" | grep -c CIT); REQ-0001 now: $(cat "$R/spec/requirements/REQ-0001.yaml")"

hdr "G2 small explicit human control set"
cmd "human_surface declared by the kernel command contract"
python3 -c 'import yaml,sys;[print("  ",h) for h in yaml.safe_load(open(sys.argv[1]))["human_surface"]]' "$R/governance/kernel/commands/COMMAND_CONTRACT.yaml"
cmd "G2.b1 status"; g "$R" orchestrator S-fresh status | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("   keys:",sorted(r.keys()));print("   next_action:",r["next_action"])'
cmd "G2.b2 continue"; g "$R" orchestrator S-fresh continue | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print("   status:",r["status"],"task:",r.get("task"),"gate presented:",bool(r.get("gate")))'
cmd "G2.b3 decide (the pending CIT gate)"
GID=$(ls "$R/spec/decisions" | grep HDG | head -1 | sed 's/.yaml//')
gq "$R" orchestrator S0 gate present "$GID" >/dev/null
g "$R" human S-owner decide "$GID" --option B --by owner --rationale "not now" | python3 -c 'import json,sys;e=json.load(sys.stdin);print("   ok=",e["ok"],json.dumps(e.get("result",e.get("error")))[:300])'
cmd "G2.b4 audit"; g "$R" orchestrator S0 audit | python3 -c 'import json,sys;e=json.load(sys.stdin);r=e.get("result") or e["error"]["details"];print("   verdict:",r["verdict"],"audit record:",r["audit"],"families:",len(r["families"]))'
cmd "G2.b5 pause / freeze / cancel / resume and their effect on a mutating command"
for c in pause freeze-writes cancel-agents; do
  gq "$R" change-controller S-cc $c --reason probe
  printf '   while %-14s task create -> ' "$c"; gq "$R" orchestrator S0 task create --class research --objective x
  printf '   status.control -> '; g "$R" orchestrator S0 status | python3 -c 'import json,sys;print(json.load(sys.stdin)["result"]["control"])'
  gq "$R" orchestrator S0 resume >/dev/null
done
cmd "G2.b5 rollback: a committed CIT is rolled back"
printf '[{"op":"set_field","target":"REQ-0001","field":"priority","value":"high"}]' > "$R/.governance-runtime/mf.json"
c2=$(g "$R" orchestrator S0 cit propose --proposal "set priority" --trigger editorial --targets REQ-0001 --manifest "$R/.governance-runtime/mf.json" | python3 -c 'import json,sys;print(json.load(sys.stdin)["result"]["id"])')
g "$R" orchestrator S0 cit simulate "$c2" >/dev/null
g "$R" change-controller S-cc cit approve "$c2" --by change-controller --method auto | python3 -c 'import json,sys;e=json.load(sys.stdin);print("   approve:",e["ok"],(e.get("error") or {}).get("code"))'
g "$R" change-controller S-cc cit execute "$c2" | python3 -c 'import json,sys;e=json.load(sys.stdin);print("   execute:",e["ok"],e.get("result",{}).get("cit_status"),(e.get("error") or {}).get("code"))'
echo "   priority now: $(grep -o '"priority": *"[a-z]*"\|priority: [a-z]*' "$R/spec/requirements/REQ-0001.yaml")"
g "$R" change-controller S-cc cit rollback "$c2" --reason probe | python3 -c 'import json,sys;e=json.load(sys.stdin);print("   rollback:",e["ok"],json.dumps(e.get("result",e.get("error")))[:200])'
echo "   priority after rollback: $(grep -o '"priority": *"[a-z]*"\|priority: [a-z]*' "$R/spec/requirements/REQ-0001.yaml" || echo '(absent)')"
cmd "G2 authority on the control set: pause by L1, resume by L3"
gq "$R" backend-engineer S-be pause; gq "$R" change-controller S-cc pause >/dev/null; gq "$R" change-controller S-cc resume; gq "$R" orchestrator S0 resume
echo END
