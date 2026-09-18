#!/usr/bin/env bash
# O5 tiers G1-G6 (Contract v3 lines 794-799): for each tier, what the product actually runs at that trigger.
source "$(dirname "$0")/lib.sh"
B=$(base_project)
RF=$(readiness_full)
cit_through() { # <root> <manifest-json-file> <title> : propose → (present, decide, approve) → execute; prints each step
  local R="$1" M="$2" T="$3" id gate
  id=$(g "$R" cit propose --proposal "$T" --manifest "$M" --title "$T" 2>/dev/null | python3 -c "import json,sys;d=json.load(sys.stdin);print((d.get('result') or {}).get('id') or 'ERR '+json.dumps(d.get('error'))[:200])")
  echo "propose: $id"
  gate=$(g "$R" cit show "$id" 2>/dev/null | python3 -c "import json,sys;d=json.load(sys.stdin);r=d.get('result') or {};print(r.get('human_gate') or '')")
  echo "radius/gate: $(g "$R" cit show "$id" 2>/dev/null | python3 -c "import json,sys;r=json.load(sys.stdin).get('result') or {};print(r.get('impact',{}).get('radius'), r.get('human_gate'))")"
  if [ -n "$gate" ]; then
    printf 'present: '; gp "$R" "ok" gate present "$gate"
    printf 'decide : '; ROLE=human gp "$R" "ok if ok else e.get('code')" decide "$gate" --option A --by human
  fi
  printf 'approve: '; gp "$R" "ok if ok else (e.get('code'), e.get('message')[:120])" cit approve "$id" --by human
  printf 'execute: '; gp "$R" "{'ok':ok,'err':e.get('code') if e else None,'msg':(e or {}).get('message','')[:200],'prop':(r or {}).get('execution',{}).get('propagation') if r else None}" cit execute "$id"
}

say "G1 (mutation) — via a Change-Impact Transaction: schema/graph/index checks run on the touched set"
R=$(clone "$B" t-g1a)
python3 -c "import json; json.dump([{'op':'write_file','path':'spec/requirements/REQ-0101.yaml','content':'id: REQ-0101\ntype: requirement\ntitle: bad\nstatus: NOT_A_LIFECYCLE_STATUS\n'}],open('$SCRATCH/g1-bad.json','w'))"
cit_through "$R" "$SCRATCH/g1-bad.json" "add requirement with invalid status"
printf 'file left behind after failed CIT-E? '; test -e "$R/spec/requirements/REQ-0101.yaml" && echo yes || echo no
note "G1 secrets at mutation: a CIT manifest carrying a secret is flagged at proposal"
python3 -c "import json; json.dump([{'op':'write_file','path':'docs/cfg.md','content':'key AKIAIOSFODNN7EXAMPLE'}],open('$SCRATCH/g1-sec.json','w'))"
gp "$R" "{'ok':ok,'secret_flagged':(r or {}).get('secret_flagged'),'err':e.get('code') if e else None}" cit propose --proposal "add cfg" --manifest "$SCRATCH/g1-sec.json"

say "G1 (mutation) — via direct file edits inside a task's allowed paths (how workers mutate): what runs?"
R=$(clone "$B" t-g1b)
T=$(new_task "$R" implementation 'src/**,tests/**,spec/**'); ( cd "$R" && git add -A && git commit -qm t ) >/dev/null 2>&1; g "$R" rebuild-memory --incremental >/dev/null 2>&1
gp "$R" "ok" task claim "$T"
printf 'pub const TOKEN: &str = "AKIAIOSFODNN7EXAMPLE";\n' >> "$R/src/lib.rs"
yw "$R" spec/requirements/REQ-0102.yaml "{'id':'REQ-0102','type':'requirement','title':'x','status':'NOT_A_LIFECYCLE_STATUS'}"
note "status / continue immediately after the edits (no command was asked to check anything):"
gp "$R" "{'memory':r['memory'],'next_action':r['next_action']}" status
note "the edits are only examined at task close (G2):"
g "$R" rebuild-memory --incremental >/dev/null 2>&1
report_json "$SCRATCH/g1b.json" passed src/lib.rs,spec/requirements/REQ-0102.yaml
printf 'task close: '; gp "$R" "{'ok':ok,'err':e.get('code') if e else None,'status':(r or {}).get('task_status'),'degraded':(r or {}).get('degraded')}" task close "$T" --report "$SCRATCH/g1b.json"
printf 'after close — doctor: '; doctor_summary "$R"

say "G2 (task close) — what the close gate checks"
R=$(clone "$B" t-g2)
yw "$R" spec/features/F-0001.yaml "{'id':'F-0001','type':'feature','title':'t','status':'ACTIVE','readiness':$RF,'scenarios':['SCN-0001'],'acceptance_tests':['tests/ledger_test.rs']}"
yw "$R" spec/scenarios/SCN-0001.yaml "{'id':'SCN-0001','type':'scenario','title':'s','status':'ACTIVE','feature':'F-0001','given':['g'],'when':['w'],'then':['t']}"
T=$(new_task "$R" implementation 'src/**,spec/features/**' --feature F-0001); ( cd "$R" && git add -A && git commit -qm t ) >/dev/null 2>&1; g "$R" rebuild-memory --incremental >/dev/null 2>&1
gp "$R" "ok" task claim "$T"
printf '\npub fn g2() {}\n' >> "$R/src/lib.rs"
note "(a) tests evidence missing"
report_json "$SCRATCH/g2a.json" "" src/lib.rs; printf '    '; gp "$R" "(ok, e.get('code') if e else None, (e or {}).get('message','')[:100])" task close "$T" --report "$SCRATCH/g2a.json"
note "(b) memory freshness: index stale after the edit"
report_json "$SCRATCH/g2b.json" passed src/lib.rs; printf '    '; gp "$R" "(ok, e.get('code') if e else None)" task close "$T" --report "$SCRATCH/g2b.json"
g "$R" rebuild-memory --incremental >/dev/null 2>&1
note "(c) mutation scope: an undeclared change outside allowed_paths"
echo x > "$R/README.md"; g "$R" rebuild-memory --incremental >/dev/null 2>&1
printf '    '; gp "$R" "(ok, e.get('code') if e else None)" task close "$T" --report "$SCRATCH/g2b.json"
( cd "$R" && git checkout -q README.md ); g "$R" rebuild-memory --incremental >/dev/null 2>&1
note "(d) readiness regressed after the claim (feature readiness cell now MISSING) — re-checked at close?"
ye "$R" spec/features/F-0001.yaml "d['readiness']['security_privacy']='MISSING'"; g "$R" rebuild-memory --incremental >/dev/null 2>&1
note "(e) references: report cites evidence and records that do not exist"
report_json "$SCRATCH/g2e.json" passed src/lib.rs,spec/features/F-0001.yaml "'evidence':['tests/does_not_exist.rs::nope','RPT-9999'],'requirements_implemented':['REQ-9999']"
printf '    close with (d)+(e): '; gp "$R" "(ok, e.get('code') if e else r.get('task_status'))" task close "$T" --report "$SCRATCH/g2e.json"
gp "$R" "{'blocked':r['blocked']}" task dag

say "G3 (checkpoint/handoff) — claims / decisions / gates / checkpoint freshness at handoff"
R=$(clone "$B" t-g3)
T=$(new_task "$R" documentation 'docs/**'); ( cd "$R" && git add -A && git commit -qm t ) >/dev/null 2>&1; g "$R" rebuild-memory --incremental >/dev/null 2>&1
SESS=S-other ROLE=backend-engineer gp "$R" "ok" task claim "$T"
G=$(g "$R" gate create --question "Blocks this task?" --fields "{\"blocks_tasks\":[\"$T\"],\"options\":[{\"id\":\"A\",\"description\":\"a\"},{\"id\":\"B\",\"description\":\"b\"}]}" 2>/dev/null | python3 -c "import json,sys;print(json.load(sys.stdin)['result']['id'])")
ye "$R" "spec/tasks/$T.yaml" "d['human_gate']='$G'"
note "task $T is claimed by S-other and waits on unanswered gate $G; orchestrator hands it off anyway:"
gp "$R" "{'blocked_by_dag':[x for x in r['waiting_human']]}" task dag
printf 'handoff create: '; gp "$R" "{'ok':ok,'id':(r or {}).get('id'),'err':e.get('code') if e else None}" handoff create --to-role backend-engineer --task "$T"
note "checkpoint written by the handoff and its content:"
python3 -c "import yaml; d=yaml.safe_load(open(sorted(__import__('glob').glob('$R/spec/reports/checkpoints/CKPT-*.yaml'))[-1])); print({k:d.get(k) for k in ['trigger','claim','pending_decisions','context_packet_hash']})"
note "an old checkpoint vs changed state: nothing marks it stale or blocks the next handoff"
yw "$R" spec/decisions/D-0007.yaml "{'id':'D-0007','type':'decision','title':'new direction','status':'ACTIVE','question':'q','chosen_option':'B'}"
gp "$R" "r and {k:r.get(k) for k in ['id','trigger','pending_decisions']}" checkpoint latest

say "G4 (milestone) — after CIT-E / architecture / memory-profile changes: is a wider check run?"
R=$(clone "$B" t-g4); n0=$(ls "$R/spec/audits" | grep -c AUD)
python3 -c "import json; json.dump([{'op':'write_file','path':'spec/architecture/ARCH-0101.yaml','content':'id: ARCH-0101\ntype: architecture\ntitle: switch to event sourcing\nstatus: ACTIVE\n'}],open('$SCRATCH/g4.json','w'))"
cit_through "$R" "$SCRATCH/g4.json" "architecture change"
n1=$(ls "$R/spec/audits" | grep -c AUD); echo "governance-suite audit records before/after the architecture CIT-E: $n0 / $n1"
printf 'D021: '; gp "$R" "[c['message'] for c in (r or det)['checks'] if c['id']=='D021'][0]" doctor
note "D021 flips here only because gate and decision records are stored under spec/decisions/ (an inputs_hash input):"
ls "$R/spec/decisions/"
note "memory profile change (memory select requires a benchmark candidate; the overlay path is exercised instead):"
ye "$R" governance/project/PROJECT_POLICY.yaml "d['policy_overrides']={'MEMORY_POLICY.chunking.max_chars':900}"
printf 'status right after: '; gp "$R" "r['memory']" status
n2=$(ls "$R/spec/audits" | grep -c AUD); echo "audit records: $n2 (no run triggered)"

say "G5 (full suite) — at adopt / update / release / full audit"
note "full audit: gov audit runs all TEST_POLICY.governance_families (see O5-scheduler-requirements.out S1: 20 families)"
note "update --apply post-install verification families (runtime/src/update.rs:330-341):"
sed -n 330,341p "$WT/runtime/src/update.rs"
note "release build: certification status is a caller-supplied string; no suite is run"
CAN="$SCRATCH/t-g5-canon"; rm -rf "$CAN" "$SCRATCH/t-g5-out"; mkdir -p "$CAN"; cp -r "$WT/framework" "$WT/migrations" "$WT/tools" "$CAN/" 2>/dev/null
V=$(python3 -c "import yaml;print(yaml.safe_load(open('$WT/framework/KERNEL.yaml'))['version'])")
t0=$(date +%s%N)
XDG_STATE_HOME="$SCRATCH/t-g5.machine" "$GOV" --json release build --version "$V" --canonical "$CAN" --out "$SCRATCH/t-g5-out" --certification CERTIFIED 2>&1 | python3 -c "import json,sys;d=json.load(sys.stdin);r=d.get('result') or {};print({'ok':d.get('ok'),'err':(d.get('error') or {}).get('code'),'msg':(d.get('error') or {}).get('message','')[:200],'certification':r.get('certification')})"
echo "release build wall: $(( ($(date +%s%N)-t0)/1000000 )) ms"
grep -rn 'certification' "$SCRATCH/t-g5-out/releases/$V/manifest.yaml" 2>/dev/null | head -3
note "adopt: a11 runs the full suite + doctor (runtime/src/adopt.rs:1285-1313); exercised by the builder test brownfield::brownfield_adoption_end_to_end (AC15-cargo-test-certification.out)"

say "G6 (qualification) — is there any qualification tier entry point?"
for c in qualify qualification scheduler health; do printf 'gov %s: ' "$c"; "$GOV" --json "$c" 2>&1 | head -2 | tr '\n' ' '; echo; done
git -C "$WT" grep -n -i -E '\bG6\b|qualification tier|chaos|soak' -- runtime cli framework/policies | head -5; echo "(no matches above = none in runtime/cli/policies)"
