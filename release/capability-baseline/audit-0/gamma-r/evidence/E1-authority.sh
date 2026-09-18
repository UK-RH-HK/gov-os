#!/usr/bin/env bash
# P2-AR-0010 — E1 Authority levels (Contract v3 lines 362-366) + AC-16 L3<->E1 (E1 side).
# Run: bash E1-authority.sh > E1-authority.out 2>&1
source "$(dirname "$0")/lib.sh"
TS="python3 $HERE/treesnap.py"

R=$(mkproj e1)
echo "project: $R"
echo "gov: $GOV ($(sha256sum "$GOV" | cut -c1-16))"

# ---------------------------------------------------------------------------------------------------------------
hdr "E1.b1 L0-L5 executable: one representative role per level x operations with distinct required levels"
# required levels are the kernel's AUTHORITY_POLICY.authority_levels_required (verified-kernel read)
cmd "gov policy effective AUTHORITY_POLICY (authority_levels_required excerpt)"
g "$R" orchestrator S0 policy effective AUTHORITY_POLICY | python3 -c '
import json,sys; e=json.load(sys.stdin); a=e["result"]["effective"]["authority_levels_required"]
for k in ["claim_task","create_task","create_gate","propose_cit","emergency_control","answer_gate","resume_control"]: print(f"  {k}: {a[k]}")'
declare -A LVL=( [independent-auditor]=L0 [backend-engineer]=L1 [product-spec-agent]=L2 [change-controller]=L3 [orchestrator]=L4 [human]=L5 )
n=0
for role in independent-auditor backend-engineer product-spec-agent change-controller orchestrator human; do
  n=$((n+1))
  # fixtures for this row, created by the orchestrator: a READY task to claim, a presented gate to answer
  g "$R" orchestrator S0 task create --id "TASK-E1R$n" --class documentation --objective "row $n claim target" --status READY >/dev/null
  gid=$(g "$R" orchestrator S0 gate create --question "row $n gate" --fields '{"impact_radius":"R3","reversibility":"irreversible","confidence":0.5}' | python3 -c 'import json,sys;print(json.load(sys.stdin)["result"]["id"])')
  g "$R" orchestrator S0 gate present "$gid" >/dev/null
  printf '%-22s %-3s' "$role" "${LVL[$role]}"
  for op in claim create gate cit pause decide resume; do
    case $op in
      claim)  out=$(gq "$R" "$role" "S-$role" task claim "TASK-E1R$n"); g "$R" "$role" "S-$role" task release "TASK-E1R$n" >/dev/null 2>&1;;
      create) out=$(gq "$R" "$role" "S-$role" task create --class documentation --objective "by $role");;
      gate)   out=$(gq "$R" "$role" "S-$role" gate create --question "gate by $role");;
      cit)    out=$(gq "$R" "$role" "S-$role" cit propose --proposal "cit by $role" --trigger editorial);;
      pause)  out=$(gq "$R" "$role" "S-$role" pause --reason "probe"); g "$R" orchestrator S0 resume >/dev/null;;
      decide) out=$(gq "$R" "$role" "S-$role" decide "$gid" --option A --by owner);;
      resume) out=$(gq "$R" "$role" "S-$role" resume);;
    esac
    if echo "$out" | grep -q 'ok=true'; then r=ALLOW; else r=$(echo "$out" | sed -n 's/.*code=\([A-Z_]*\).*/\1/p'); fi
    printf ' %s=%s' "$op" "$r"
  done
  echo
done
echo "(expected by policy: claim>=L1 create>=L2 gate>=L2 cit>=L2 pause>=L3 decide>=L3 resume>=L4)"
cmd "unknown role and case variant"
gq "$R" data-scientist S-x task create --class research --objective x
gq "$R" Human S-x decide HDG-0001 --option A

# ---------------------------------------------------------------------------------------------------------------
hdr "E1.b2 mutating-path census as L0 (independent-auditor): authority result + repository files changed"
# Fixtures (orchestrator): feature, READY task, pending+presented gate, simulated CIT, handoff.
write_feature "$R" F-0001 "$(readiness_json '' '')" '{"scenarios":["SCN-0001"],"acceptance_tests":["TST-0001"]}'
( cd "$R" && git add -A && git commit -qm "e1 fixtures" )
g "$R" orchestrator S0 task create --id TASK-C1 --class implementation --objective "census target" --status READY --allowed 'src/**' >/dev/null
g "$R" orchestrator S0 task claim TASK-C1 >/dev/null
# a READY task whose dependency does not exist: `task replan` recomputes it to BLOCKED (an authoritative record write)
g "$R" orchestrator S0 task create --id TASK-C2 --class documentation --objective "replan target" --status READY --deps TASK-NOPE >/dev/null
g "$R" orchestrator S0 gate create --question "census gate" --fields '{"id":"HDG-0900"}' >/dev/null
g "$R" orchestrator S0 handoff create --to-role backend-engineer --task TASK-C1 >/dev/null
hid=$(ls "$R/spec/planning" | grep HND | head -1 | sed 's/.yaml//')
g "$R" orchestrator S0 cit propose --proposal "census cit" --trigger editorial --targets F-0001 >/dev/null
cid=$(ls "$R/spec/decisions" | grep CIT | tail -1 | sed 's/.yaml//')
python3 - "$R" <<'PY'
import json,sys,os
r=sys.argv[1]; d=os.path.join(r,".governance-runtime","e1"); os.makedirs(d,exist_ok=True)
json.dump({"task":"TASK-C1","status":"success","work_completed":"x","files_changed":[],"evidence":[],"tests":{"status":"passed"},"discoveries":[],"risks":[],"lessons":[],"proposed_decisions":[],"unresolved":[],"recommended_next_action":"none"},open(os.path.join(d,"ret.json"),"w"))
json.dump({"work_completed":"x","files_changed":[],"tests":{"status":"passed"}},open(os.path.join(d,"rep.json"),"w"))
PY
( cd "$R" && git add -A && git commit -qm "census fixtures" )
release_all() { for t in $(g "$R" orchestrator S0 claims list | python3 -c 'import json,sys;[print(c["task_id"]) for c in json.load(sys.stdin)["result"]]'); do g "$R" orchestrator S0 task release "$t" --force >/dev/null; done; }
census() {  # census <label> <policy-class> <args...>
  local label="$1" pol="$2"; shift 2
  $TS snap "$R" /tmp/e1a.$$.json
  local o; o=$(gq "$R" independent-auditor S-aud "$@")
  $TS snap "$R" /tmp/e1b.$$.json
  local ch; ch=$($TS diff /tmp/e1a.$$.json /tmp/e1b.$$.json | tr '\n' ' ')
  printf '%-34s %-26s %-70s changed=[%s]\n' "$label" "$pol" "$(echo "$o" | cut -c1-70)" "$ch"
  ( cd "$R" && git reset -q --hard && git clean -fdq -e .probe-machine -e .governance-runtime )
  rm -f "$R/.governance-runtime/control.json"
}
printf '%-34s %-26s %-70s %s\n' COMMAND POLICY_CLASS RESULT_AS_L0 TRACKED_OR_REPO_FILES_CHANGED
census "task create"              create_task:L2        task create --class research --objective x
census "task status READY"        mutate_task_status:L2 task status TASK-C1 BLOCKED
census "task claim"               claim_task:L1         task claim TASK-C1
census "task release --force"     force_release_task:L3 task release TASK-C1 --force
census "task close"               close_task:L1         task close TASK-C1 --report "$R/.governance-runtime/e1/rep.json"
census "task replan"              "(none declared)"     task replan
census "readiness plan"           readiness_plan:L2     readiness plan F-0001
census "gate create"              create_gate:L2        gate create --question q
census "gate present"             present_gate:L1       gate present HDG-0900
census "gate revoke"              revoke_gate:L4        gate revoke HDG-0900
census "decide"                   answer_gate:L3        decide HDG-0900 --option A
census "cit propose"              propose_cit:L2        cit propose --proposal p --trigger editorial
census "cit simulate"             simulate_cit:L2       cit simulate "$cid"
census "cit reject"               reject_cit:L3         cit reject "$cid"
census "handoff create"           create_handoff:L2     handoff create --to-role backend-engineer --task TASK-C1
census "handoff return"           return_handoff:L1     handoff return "$hid" --file "$R/.governance-runtime/e1/ret.json"
census "checkpoint create"        checkpoint:L1         checkpoint create --next-action x
census "checkpoint watchdog"      checkpoint:L1         checkpoint watchdog --utilisation 0.99
census "pause"                    emergency_control:L3  pause
census "freeze-writes"            emergency_control:L3  freeze-writes
census "cancel-agents"            emergency_control:L3  cancel-agents
census "resume"                   resume_control:L4     resume
census "recover"                  recover:L3            recover
census "claims sweep"             sweep_claims:L3       claims sweep
census "plugins unregister"       register_plugin:L2    plugins unregister none
census "tools install"            install_tool:L2       tools install --descriptor "$R/.governance-runtime/e1/rep.json"
census "route --record"           record_routing_evidence:L1 route --record "$R/.governance-runtime/e1/rep.json"
census "memory benchmark --record" memory_benchmark:L2  memory benchmark --record
census "memory select"            memory_select:L3      memory select hashed-ngram
census "memory heldout-starter --force" "(none declared)" memory heldout-starter --force
census "kernel override"          override_kernel_integrity:L4 kernel override
echo "   (note: with a verified kernel 'kernel override' returns override_required:false before the authority check and writes nothing)"
census "kernel reinstall"         install_kernel:L4     kernel reinstall
census "update --apply"           update_apply:L4       update --apply
census "upstream prepare"         upstream_prepare:L1   upstream prepare L-0001
census "adapters generate"        "(none declared)"     adapters generate
census "tools registry"           "(none declared)"     tools registry
census "rebuild-memory"           rebuild_memory:L0     rebuild-memory
census "audit (persist)"          "(none declared)"     audit
census "telemetry emit"           "(none declared)"     telemetry emit --name probe
census "context compile"          "(none declared)"     context compile TASK-C1
echo "--- init into a fresh directory as L0 (install_kernel:L4)"
F=$PROBES/e1-init-as-l0; rm -rf "$F"; mkdir -p "$F"; cp -r "$WT/fixtures/greenfield/project/." "$F/"
gq "$F" independent-auditor S-aud init --name x --alias y
ls "$F/governance" 2>&1 | head -3
echo "--- control: fresh directory, GOV_ROLE=independent-auditor"
F2=$PROBES/e1-init-as-l0-env; rm -rf "$F2"; mkdir -p "$F2"; cp -r "$WT/fixtures/greenfield/project/." "$F2/"
env -u GOV_SESSION GOV_ROLE=independent-auditor XDG_STATE_HOME="$F2/.probe-machine" "$GOV" --json --root "$F2" init --name x --alias y | python3 -c 'import json,sys;e=json.load(sys.stdin);print(" ok=",e["ok"],(e.get("error") or {}).get("code"),str((e.get("error") or {}).get("message"))[:140])'
ls "$F2/governance" 2>&1 | head -3

hdr "E1.b2.b the CLI acting role (--role) is not applied by init and adopt/migrate (Project::open(root) uses GOV_ROLE or 'orchestrator')"
cmd "installed project: gov --role backend-engineer init --force   (install_kernel: L4)"
gq "$R" backend-engineer S-w init --force --name e1 --alias a-e1
cmd "same, role given through GOV_ROLE=backend-engineer instead of --role"
env -u GOV_SESSION GOV_ROLE=backend-engineer XDG_STATE_HOME="$R/.probe-machine" "$GOV" --json --root "$R" init --force --name e1 --alias a-e1 | python3 -c 'import json,sys;e=json.load(sys.stdin);print(" ok=",e["ok"],(e.get("error") or {}).get("code"),str((e.get("error") or {}).get("message"))[:160])'
( cd "$R" && git add -A && git commit -qm "after init --force probe" -q ) >/dev/null 2>&1
B=$PROBES/e1-brown; rm -rf "$B"; mkdir -p "$B"; cp -r "$WT/fixtures/brownfield/project/." "$B/"
python3 - "$B" <<'PY'
import sqlite3,sys,os
b=sys.argv[1]; sql=open(os.path.join(b,"memory/chat_history.sql")).read()
c=sqlite3.connect(os.path.join(b,"memory/chat_history.sqlite")); c.executescript("PRAGMA journal_mode=DELETE; "+sql); c.close()
os.remove(os.path.join(b,"memory/chat_history.sql"))
PY
( cd "$B" && git init -q && git config user.email p@e.invalid && git config user.name p && git add -A && git commit -qm base && printf '.probe-machine/\n' >> .git/info/exclude )
cmd "brownfield adoption driven entirely as --role independent-auditor (L0); reviewer is a separate session"
for s in baseline inventory classify map plan test-design; do printf '  adopt %-12s ' "$s"; gq "$B" independent-auditor S-aud adopt "$s"; done
printf '  adopt %-12s ' review; gq "$B" independent-auditor S-rev adopt review --verdict MIGRATION_PLAN_APPROVED
printf '  adopt %-12s ' "migrate(A6)"; gq "$B" independent-auditor S-aud adopt migrate --name bf --alias a-bf
ls "$B/governance" 2>/dev/null | sed 's/^/    governance\//'
cmd "a second migrate invocation as L0 (kernel now installed: migrate_execute L3 is checked -- against which role?)"
printf '  adopt %-12s ' "migrate(2nd)"; gq "$B" independent-auditor S-aud adopt migrate --name bf --alias a-bf
cmd "control: the same second invocation with GOV_ROLE=independent-auditor"
env -u GOV_SESSION GOV_ROLE=independent-auditor XDG_STATE_HOME="$B/.probe-machine" "$GOV" --json --root "$B" --session S-aud adopt migrate --name bf --alias a-bf | python3 -c 'import json,sys;e=json.load(sys.stdin);print("  ok=",e["ok"],(e.get("error") or {}).get("code"),str((e.get("error") or {}).get("message"))[:160])'

# ---------------------------------------------------------------------------------------------------------------
hdr "E1.b3.a lower roles cannot record higher-trust facts through the CLI"
g "$R" orchestrator S0 gate create --question "b3 gate" --fields '{"id":"HDG-0910","impact_radius":"R3","reversibility":"irreversible","confidence":0.5}' >/dev/null
g "$R" orchestrator S0 gate present HDG-0910 >/dev/null
cmd "backend-engineer (L1): decide HDG-0910 --by human";            gq "$R" backend-engineer S-w decide HDG-0910 --option A --by human
cmd "product-spec-agent (L2): decide HDG-0910 --by owner";          gq "$R" product-spec-agent S-w decide HDG-0910 --option A --by owner
cmd "change-controller (L3) as agent (--by change-controller) on an R3/irreversible gate (outside agent_resolvable_when)"
gq "$R" change-controller S-cc decide HDG-0910 --option A --by change-controller
cmd "backend-engineer (L1): cit approve --method human";            gq "$R" backend-engineer S-w cit approve "$cid" --by human --method human

hdr "E1.b3.b relay semantics: an L3/L4 acting role records a HUMAN answer (answer_gate: L3 relay, by design)"
cmd "change-controller (L3): decide HDG-0910 --option A (default --by human)"
out=$(g "$R" change-controller S-cc decide HDG-0910 --option A); echo "$out" | python3 -c 'import json,sys;e=json.load(sys.stdin);print(" ok=",e["ok"],"answered_by_kind=",e.get("result",{}).get("answered_by_kind"),"decision=",e.get("result",{}).get("decision"))'
did=$(echo "$out" | python3 -c 'import json,sys;print(json.load(sys.stdin)["result"]["decision"])')
python3 - "$R/spec/decisions/$did.yaml" <<'PY'
import sys,yaml
PY
grep -E 'human_approved|approved_by|approved_by_kind' "$R/spec/decisions/$did.yaml" | sed 's/^/  /'
grep -A7 '^answer:' "$R/spec/decisions/HDG-0910.yaml" | sed 's/^/  /'

hdr "E1.b3.c the acting role is caller-declared (D-0007 T5, documented adapter boundary): any caller may claim L5"
g "$R" orchestrator S0 gate create --question "b3c gate" --fields '{"id":"HDG-0920"}' >/dev/null
g "$R" orchestrator S0 gate present HDG-0920 >/dev/null
cmd "a process that was dispatched as backend-engineer simply passes --role human"
out=$(g "$R" human S-w decide HDG-0920 --option A --by human); echo "$out" | python3 -c 'import json,sys;e=json.load(sys.stdin);print(" ok=",e["ok"],"answered_by_kind=",e["result"]["answered_by_kind"])'
cmd "same via environment GOV_ROLE=human (no --role flag)"
g "$R" orchestrator S0 gate create --question "b3c gate env" --fields '{"id":"HDG-0921"}' >/dev/null
g "$R" orchestrator S0 gate present HDG-0921 >/dev/null
env -u GOV_SESSION GOV_ROLE=human XDG_STATE_HOME="$R/.probe-machine" "$GOV" --json --root "$R" decide HDG-0921 --option A | python3 -c 'import json,sys;e=json.load(sys.stdin);print(" ok=",e["ok"],"answered_by_kind=",e["result"]["answered_by_kind"])'

hdr "E1.b3.d an L1 worker forges T2 facts on disk; task close does not see them; the forged human answer takes effect"
# Orchestrator: a behaviour-change CIT that needs a human gate, a task blocked on a gate, and the worker's task.
( cd "$R" && git add -A && git commit -qm "pre-forge" )
write_feature "$R" F-0002 "$(readiness_json '' '')"
cat > "$R/spec/requirements.yaml.tmp" <<'EOF'
EOF
rm -f "$R/spec/requirements.yaml.tmp"; mkdir -p "$R/spec/requirements"
printf '{"id":"REQ-0002","type":"requirement","title":"totals exact","status":"ACTIVE","feature":"F-0002","kind":"functional","acceptance_criteria":["a"]}\n' > "$R/spec/requirements/REQ-0002.yaml"
( cd "$R" && git add -A && git commit -qm "req" )
g "$R" orchestrator S0 rebuild-memory >/dev/null
printf '[{"op":"set_field","target":"REQ-0002","field":"acceptance_criteria","value":["a","b"]}]' > "$R/.governance-runtime/e1/mf.json"
cit2=$(g "$R" orchestrator S0 cit propose --proposal "change acceptance criteria of REQ-0002" --trigger acceptance_criteria_change --targets REQ-0002 --manifest "$R/.governance-runtime/e1/mf.json" | python3 -c 'import json,sys;print(json.load(sys.stdin)["result"]["id"])')
sim=$(g "$R" orchestrator S0 cit simulate "$cit2")
gate2=$(echo "$sim" | python3 -c 'import json,sys;e=json.load(sys.stdin);print(e["result"].get("human_gate"))')
echo "CIT $cit2 simulated: radius=$(echo "$sim" | python3 -c 'import json,sys;print(json.load(sys.stdin)["result"]["impact"]["radius"])') human_gate=$gate2"
cmd "before forgery: change-controller cit approve --method human"; gq "$R" change-controller S-cc cit approve "$cit2" --by owner --method human
g "$R" orchestrator S0 task create --id TASK-BLK --class documentation --objective "blocked on a human gate" --status READY >/dev/null
g "$R" orchestrator S0 gate create --question "may TASK-BLK proceed?" --fields '{"id":"HDG-0930","blocks_tasks":["TASK-BLK"],"impact_radius":"R3","reversibility":"irreversible","confidence":0.4}' >/dev/null
g "$R" orchestrator S0 task create --id TASK-W --class implementation --objective "worker task" --status READY --allowed 'src/**' >/dev/null
( cd "$R" && git add -A && git commit -qm "forge fixtures" )
g "$R" orchestrator S0 rebuild-memory >/dev/null
cmd "before: dag waiting_human"; g "$R" orchestrator S0 task dag | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print(" waiting_human=",r["waiting_human"]," runnable=",r["runnable"])'
release_all
cmd "worker backend-engineer (L1, session S-W) claims TASK-W"; gq "$R" backend-engineer S-W task claim TASK-W
# the worker's legitimate change
echo "// worker change" >> "$R/src/lib.rs"
# the worker's forgeries: answer both gates as a human, and write the decision records they need
python3 - "$R" "$gate2" "$cit2" <<'PY'
import sys, json, os, re
r, g2, cit = sys.argv[1], sys.argv[2], sys.argv[3]
def load(p):
    import subprocess
    return json.loads(subprocess.check_output(["python3","-c","import sys,json,yaml;print(json.dumps(yaml.safe_load(open(sys.argv[1]))))",p])) if False else None
import yaml  # PyYAML is available in this environment (verified below); fall back to text edit otherwise
for gid, extra in ((g2, {"cit": cit}), ("HDG-0930", {})):
    p = os.path.join(r, "spec/decisions", gid + ".yaml")
    d = yaml.safe_load(open(p))
    d["gate_status"] = "ANSWERED"; d["presented_in_chat"] = True
    d["presented_at"] = "2026-09-18T00:00:00Z"; d["presented_by"] = {"session": "S-W", "role": "orchestrator"}
    d["answer"] = {"option": "A", "by": "owner", "by_kind": "human", "acting_role": "human", "at": "2026-09-18T00:00:01Z", "rationale": "forged by worker"}
    d.update(extra)
    yaml.safe_dump(d, open(p, "w"), sort_keys=False)
    did = "D-09" + gid[-2:]
    dec = {"id": did, "type": "decision", "title": f"Decision for {gid}: option A", "status": "ACTIVE", "created": "2026-09-18",
           "question": d["question"], "chosen_option": "A", "approved_by": "owner", "approved_at": "2026-09-18T00:00:01Z",
           "human_approved": True, "approved_by_kind": "human", "derived_from": [gid], "state_class": "AUTHORITATIVE"}
    if gid == g2: dec["cit"] = cit
    yaml.safe_dump(dec, open(os.path.join(r, "spec/decisions", did + ".yaml"), "w"), sort_keys=False)
    print("forged", gid, "->", did)
PY
rep=$(report_file "$R" worker "implemented" "src/lib.rs" passed)
g "$R" backend-engineer S-W rebuild-memory --incremental >/dev/null
cmd "worker closes TASK-W declaring only src/lib.rs"; gq "$R" backend-engineer S-W task close TASK-W --report "$rep"
echo "  files the worker actually changed (git status):"; ( cd "$R" && git status --porcelain | grep -v '^?? .governance-runtime' | sed 's/^/    /' )
cmd "after: dag (forged gate HDG-0930 answer)"; g "$R" orchestrator S0 task dag | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print(" waiting_human=",r["waiting_human"]," runnable=",r["runnable"])'
cmd "after: change-controller cit approve --method human (approval derives from the forged gate answer)"
g "$R" change-controller S-cc cit approve "$cit2" --by owner --method human | python3 -c 'import json,sys;e=json.load(sys.stdin);print(" ok=",e["ok"], json.dumps(e.get("result",e.get("error")))[:400])'
cmd "after: change-controller cit execute"; g "$R" change-controller S-cc cit execute "$cit2" | python3 -c 'import json,sys;e=json.load(sys.stdin);print(" ok=",e["ok"],"cit_status=",e.get("result",{}).get("cit_status"), (e.get("error") or {}).get("code"))'
grep -A3 'acceptance_criteria' "$R/spec/requirements/REQ-0002.yaml" | sed 's/^/  REQ-0002 now: /'
cmd "does the governance suite or doctor notice? (audit findings mentioning HDG-0930/D-0930/forg)"
g "$R" orchestrator S0 audit --no-persist | python3 -c '
import json,sys; e=json.load(sys.stdin); r=e.get("result") or e["error"]["details"]
hits=[f for f in r["findings"] if any(s in json.dumps(f) for s in ["HDG-0930","D-0930","forg",sys.argv[1] if len(sys.argv)>1 else "zz"])]
print(" verdict=",r["verdict"]," findings mentioning the forged records:",hits)
print(" all high/critical findings (for context):",[(f["family"],f["message"][:110]) for f in r["findings"] if f["severity"] in ("high","critical")])'
cmd "contrast: the same worker writing a NON-OS-managed spec file is caught at close"
g "$R" orchestrator S0 task create --id TASK-W2 --class implementation --objective "worker task 2" --status READY --allowed 'src/**' >/dev/null
( cd "$R" && git add -A && git commit -qm "w2" )
release_all; gq "$R" backend-engineer S-W task claim TASK-W2
# spec/features/F-0002.yaml: an authoritative record no committed CIT has touched and not an OS-managed prefix
python3 - "$R" <<'PY'
import sys,os
p=os.path.join(sys.argv[1],"spec/features/F-0002.yaml"); open(p,"a").write("# edited by worker\n")
PY
rep2=$(report_file "$R" worker2 "x" "src/lib.rs" passed)
g "$R" backend-engineer S-W rebuild-memory --incremental >/dev/null
gq "$R" backend-engineer S-W task close TASK-W2 --report "$rep2"

# ---------------------------------------------------------------------------------------------------------------
hdr "E1.b4 independent auditors/testers are constrained"
( cd "$R" && git reset -q --hard && git clean -fdq -e .probe-machine -e .governance-runtime )
g "$R" orchestrator S0 rebuild-memory >/dev/null   # re-sync the derived index with the reset tree
for role in independent-auditor migration-verifier memory-verifier migration-reviewer; do
  printf '%-22s' "$role"
  for op in "task create --class research --objective x" "cit propose --proposal x --trigger editorial" "gate create --question x" "handoff create --to-role backend-engineer --task TASK-C1" "checkpoint create --next-action x"; do
    o=$(gq "$R" "$role" S-a $op); printf ' [%s]=%s' "$(echo $op | cut -d' ' -f1-2)" "$(echo "$o" | grep -q ok=true && echo ALLOW || echo "$o" | sed -n 's/.*code=\([A-Z_]*\).*/\1/p')"
  done; echo
done
cmd "independent-auditor may still read/verify: status, doctor, audit --no-persist, memory query"
for op in "status" "doctor" "audit --no-persist" "memory query ledger"; do printf '  %-20s ' "$op"; gq "$R" independent-auditor S-a $op; done
echo "  (exit=3 on audit/doctor is the UNHEALTHY verdict of the suite, not an authority refusal: the L0 role ran it)"
cmd "independent-auditor running 'gov continue' while a human gate is pending (continue presents the gate: present_gate L1)"
g "$R" orchestrator S0 gate create --question "pending for continue" >/dev/null
gq "$R" independent-auditor S-a continue
hdr "E1.b4.b tester independence is not constrained by role: the task's designated role is not enforced at claim/close"
g "$R" orchestrator S0 task create --id TASK-TD --class test-design --objective "independent acceptance tests" --status READY --allowed 'tests/**' --fields '{"role":"independent-test-designer"}' >/dev/null
g "$R" orchestrator S0 task create --id TASK-IM --class implementation --objective "implementation" --status READY --allowed 'src/**' --fields '{"role":"backend-engineer"}' >/dev/null
( cd "$R" && git add -A && git commit -qm "td" )
release_all
cmd "the implementer role (backend-engineer) claims the independent test-design task"; gq "$R" backend-engineer S-impl task claim TASK-TD
echo "// test by implementer" >> "$R/tests/ledger_test.rs"
rep3=$(report_file "$R" td "tests written" "tests/ledger_test.rs" passed)
g "$R" backend-engineer S-impl rebuild-memory --incremental >/dev/null
cmd "... and closes it"; gq "$R" backend-engineer S-impl task close TASK-TD --report "$rep3"
cmd "the same session then claims the implementation task it is supposed to be independent of"; gq "$R" backend-engineer S-impl task claim TASK-IM
cmd "test-obligation independence is a self-declared boolean: implementer-authored obligation with independent_of_implementer:true"
mkdir -p "$R/spec/tasks"
printf '{"id":"TST-0009","type":"test-obligation","title":"acc","status":"ACTIVE","feature":"F-0001","family":"acceptance","author_role":"backend-engineer","independent_of_implementer":true}\n' > "$R/spec/tasks/TST-0009.yaml"
g "$R" orchestrator S0 task create --id TASK-IM2 --class implementation --objective "impl 2" --status READY --feature F-0001 --fields '{"scenarios":["SCN-0001"],"acceptance_tests":["TST-0009"]}' >/dev/null
g "$R" orchestrator S0 task dag | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print(" TASK-IM2 runnable:", "TASK-IM2" in r["runnable"], [b for b in r["blocked"] if b["task"]=="TASK-IM2"])'
printf '{"id":"TST-0009","type":"test-obligation","title":"acc","status":"ACTIVE","feature":"F-0001","family":"acceptance","author_role":"backend-engineer","independent_of_implementer":false}\n' > "$R/spec/tasks/TST-0009.yaml"
g "$R" orchestrator S0 task dag | python3 -c 'import json,sys;r=json.load(sys.stdin)["result"];print(" with independent_of_implementer:false -> TASK-IM2 runnable:", "TASK-IM2" in r["runnable"], [b["reasons"] for b in r["blocked"] if b["task"]=="TASK-IM2"])'

# ---------------------------------------------------------------------------------------------------------------
hdr "AC-16 L3<->E1 (E1 side): gate presentation/answer/revoke respect authority"
( cd "$R" && git reset -q --hard && git clean -fdq -e .probe-machine -e .governance-runtime )
g "$R" orchestrator S0 gate create --question "l3e1 gate" --fields '{"id":"HDG-0950","impact_radius":"R1","reversibility":"reversible","confidence":0.9}' >/dev/null
cmd "L0 present (present_gate L1)";          gq "$R" independent-auditor S-a gate present HDG-0950
cmd "L3 answer before presentation";         gq "$R" change-controller S-cc decide HDG-0950 --option A --by owner
cmd "L1 present";                            gq "$R" backend-engineer S-w gate present HDG-0950
cmd "L1 answer after presentation";          gq "$R" backend-engineer S-w decide HDG-0950 --option A --by owner
cmd "L2 agent-resolution (--by product-spec-agent) on R1/0.9/reversible gate (needs L3 acting role)"; gq "$R" product-spec-agent S-p decide HDG-0950 --option A --by product-spec-agent
cmd "L3 agent-resolution within agent_resolvable_when"; g "$R" change-controller S-cc decide HDG-0950 --option A --by change-controller | python3 -c 'import json,sys;e=json.load(sys.stdin);print(" ok=",e["ok"],"kind=",e.get("result",{}).get("answered_by_kind"))'
cmd "L3 revoke (revoke_gate L4)";            gq "$R" change-controller S-cc gate revoke HDG-0950
cmd "L4 revoke";                             g "$R" orchestrator S0 gate revoke HDG-0950 | python3 -c 'import json,sys;e=json.load(sys.stdin);print(" ok=",e["ok"],e.get("result",{}).get("touched"))'
grep -E '^status|state_class|revoked_gate' "$R"/spec/decisions/D-*.yaml | grep -B0 -A0 'revoked_gate\|REJECTED' | tail -3 | sed 's/^/  /'
echo "END"
