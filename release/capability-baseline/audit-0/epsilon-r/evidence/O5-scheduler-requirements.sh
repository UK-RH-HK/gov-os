#!/usr/bin/env bash
# O5 scheduler requirements (Contract v3 lines 801-808) and the AC-5 behaviours of the frozen gate contract §3:
# impacted-test selection from a real mutation; parallel execution; isolation; cache reuse/invalidation; stale
# evidence; RED/YELLOW/GREEN aggregation; hard-block vs warning; provenance; remediation/task generation; and whether a
# trivial mutation re-runs the whole suite serially.
source "$(dirname "$0")/lib.sh"
B=$(base_project)
EVD_DIR="$(dirname "$0")"
# sampler: run gov in the background, poll /proc for threads and child processes until exit
sample() { # <root> <args...>  → prints wall ms, max threads, max children, exit code
  python3 - "$GOV" "$@" <<'EOF'
import os,subprocess,sys,time,json
gov=sys.argv[1]; root=sys.argv[2]; args=sys.argv[3:]
env=dict(os.environ, XDG_STATE_HOME=root+".machine")
t0=time.time()
p=subprocess.Popen([gov,"--json","--root",root,"--session","S-sched","--role","orchestrator",*args],stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env)
maxthr=0; maxkids=0; samples=0
while p.poll() is None:
    try:
        thr=len(os.listdir(f"/proc/{p.pid}/task")); maxthr=max(maxthr,thr)
        kids=0
        for t in os.listdir(f"/proc/{p.pid}/task"):
            try: kids+=len(open(f"/proc/{p.pid}/task/{t}/children").read().split())
            except Exception: pass
        maxkids=max(maxkids,kids); samples+=1
    except FileNotFoundError: pass
    time.sleep(0.002)
out,err=p.communicate(); ms=int((time.time()-t0)*1000)
try:
    d=json.loads(out); r=d.get("result") or (d.get("error") or {}).get("details") or {}
    fams=len(r.get("families",{})) if isinstance(r,dict) else None
    verdict=r.get("verdict") if isinstance(r,dict) else None
except Exception: fams=None; verdict=None
print(json.dumps({"args":" ".join(args),"wall_ms":ms,"max_threads":maxthr,"max_child_processes":maxkids,"samples":samples,"exit":p.returncode,"families_in_result":fams,"verdict":verdict}))
EOF
}

say "S1 impacted-test selection: a trivial (whitespace-only) mutation of one decision record"
R=$(clone "$B" sched-s1)
yw "$R" spec/decisions/D-0001.yaml "{'id':'D-0001','type':'decision','title':'t','status':'ACTIVE','question':'q','chosen_option':'A'}"
g "$R" rebuild-memory --incremental >/dev/null 2>&1; AUDIT_PERSIST=1 audit_summary "$R" >/dev/null
printf 'D021 before: '; gp "$R" "[c['message'] for c in r['checks'] if c['id']=='D021'][0]" doctor
printf '\n' >> "$R/spec/decisions/D-0001.yaml"; g "$R" rebuild-memory --incremental >/dev/null 2>&1
printf 'D021 after trivial mutation: '; gp "$R" "[c['message'] for c in (r or det)['checks'] if c['id']=='D021'][0]" doctor
note "is there any product surface that selects checks from the changed path? (status / continue / doctor output after the mutation)"
gp "$R" "{'next_action':r['next_action']}" status
note "the remedy the product names is 'gov audit' — the whole suite:"
sample "$R" audit --no-persist
note "every family, one at a time (each invocation also runs the family twice for the reproducibility check):"
tot=0
for f in $(python3 -c "import yaml;print(' '.join(yaml.safe_load(open('$WT/framework/policies/TEST_POLICY.yaml'))['governance_families']))"); do
  o=$(sample "$R" audit --no-persist --family "$f"); ms=$(python3 -c "import json,sys;print(json.loads(sys.argv[1])['wall_ms'])" "$o"); tot=$((tot+ms)); echo "  $f ${ms}ms"
done
echo "sum of per-family invocations: ${tot}ms (includes 20 process start-ups)"

say "S2 parallel execution of independent checks: thread/child sampling during a full and a deep audit"
R=$(clone "$B" sched-s2)
sample "$R" audit --no-persist
sample "$R" audit --no-persist --deep
sample "$R" doctor

say "S3 isolation: where does the suite run and what does it touch? (deep audit rebuilds the LIVE index in place)"
R=$(clone "$B" sched-s3)
st() { python3 -c "import os,hashlib;p='$R/.governance-runtime/state.db';s=os.stat(p);print({'inode':s.st_ino,'mtime':int(s.st_mtime_ns/1e6),'sha':hashlib.sha256(open(p,'rb').read()).hexdigest()[:16]})"; }
printf 'state.db before: '; st
python3 -c "import time; time.sleep(1.1)"
gp "$R" "{'verdict':r['verdict'],'audit':r['audit'],'recovery_rebuild':r['families']['recovery_rebuild']['detail']}" audit --deep
printf 'state.db after : '; st
ls "$R/spec/audits/"
note "no worktree, copy or child process is used: see max_threads/max_child_processes in S2"

say "S4 cache keyed by content/policy/framework hashes: two identical runs, then one changed input"
R=$(clone "$B" sched-s4)
sample "$R" audit --no-persist
sample "$R" audit --no-persist
ls -a "$R/.governance-runtime/"
note "change one policy override (an inputs_hash input) and re-run: every family is recomputed, none is reused"
ye "$R" governance/project/PROJECT_POLICY.yaml "d['policy_overrides']={'MEMORY_POLICY.retrieval.default_k':9}"
sample "$R" audit --no-persist
note "inputs_hash is used only to judge an existing green record current/obsolete (D021, task close), never to skip work:"
grep -n 'inputs_hash' "$WT/runtime/src/verification/mod.rs" "$WT/runtime/src/doctor.rs" "$WT/runtime/src/orchestration/tasks.rs" | sed "s|$WT/||"

say "S5 RED/YELLOW/GREEN machine state (HEALTHY / DEGRADED / UNHEALTHY) and aggregation by worst severity"
R=$(clone "$B" sched-s5g); printf 'GREEN  doctor: '; doctor_summary "$R"; printf 'GREEN  audit : '; audit_summary "$R"
R=$(clone "$B" sched-s5y); printf '\nlate note\n' >> "$R/spec/now/NOW.md"
printf 'YELLOW doctor: '; doctor_summary "$R"; printf 'YELLOW audit (family index_freshness): '; audit_summary "$R" --family index_freshness
R=$(clone "$B" sched-s5r); printf 'pub const K: &str = "AKIAIOSFODNN7EXAMPLE";\n' > "$R/src/creds.rs"
printf 'RED    doctor: '; doctor_summary "$R"; printf 'RED    audit : '; audit_summary "$R"
note "doctor and audit are separate verdicts; no command aggregates tiers or both surfaces into one repository state (adopt a11 only, for adoption)"

say "S6 hard-block vs warning: does a RED (UNHEALTHY) repository block governed work?"
R=$(clone "$B" sched-s6); printf 'pub const K: &str = "AKIAIOSFODNN7EXAMPLE";\n' > "$R/src/creds.rs"
( cd "$R" && git add -A && git commit -qm secret ) >/dev/null 2>&1
printf 'doctor: '; doctor_summary "$R"
printf 'task create: '; T=$(new_task "$R" documentation 'docs/**'); echo "$T"
( cd "$R" && git add -A && git commit -qm t ) >/dev/null 2>&1; g "$R" rebuild-memory --incremental >/dev/null 2>&1
printf 'continue --claim: '; gp "$R" "{'ok':ok,'status':(r or {}).get('status'),'task':(r or {}).get('task'),'err':e.get('code') if e else None}" continue --claim
mkdir -p "$R/docs"; echo n > "$R/docs/n.md"; g "$R" rebuild-memory --incremental >/dev/null 2>&1
report_json "$SCRATCH/s6.json" not_applicable_with_reason docs/n.md "'tests':{'status':'not_applicable_with_reason','reason':'doc'}"
printf 'task close: '; gp "$R" "(ok, e.get('code') if e else r.get('task_status'))" task close "$T" --report "$SCRATCH/s6.json"
printf 'cit propose: '; gp "$R" "(ok, e.get('code') if e else r.get('id'))" cit propose --proposal "edit docs" --targets docs/n.md
note "a failed product suite is reported with exit 0 (warning-shaped), see O1-product-families.out G; a stale green is DEGRADED (exit 0)"
note "per-check severity is explicit in output; which states block which commands is not declared anywhere (no block/warn field):"
gp "$B" "sorted(set(k for c in r['checks'] for k in c))" doctor

say "S7 health-result provenance"
R=$(clone "$B" sched-s7)
AUDIT_PERSIST=1 audit_summary "$R" >/dev/null
f=$(ls "$R"/spec/audits/AUD-*.yaml | tail -1); python3 -c "import yaml; d=yaml.safe_load(open('$f')); print('audit record keys:', sorted(k for k in d if k not in ('families','findings'))); print({k:d[k] for k in ('session','auditor_role','inputs_hash','result_hash','run_at')})"
note "doctor: is anything persisted?"
before=$(find "$R/spec" "$R/governance" -type f | sort | xargs sha256sum | sha256sum | cut -c1-16)
g "$R" doctor >/dev/null 2>&1
after=$(find "$R/spec" "$R/governance" -type f | sort | xargs sha256sum | sha256sum | cut -c1-16)
echo "governed tree hash before/after doctor: $before / $after"
grep '"name":"cli.doctor"' "$R/.governance-runtime/telemetry/events.jsonl" | tail -1 | python3 -c "import json,sys; e=json.loads(sys.stdin.read()); print('only trace of the doctor run:', e['name'], e['attributes'])"

say "S8 remediation / task generation from a RED health result"
R=$(clone "$B" sched-s8); printf 'pub const K: &str = "AKIAIOSFODNN7EXAMPLE";\n' > "$R/src/creds.rs"; printf '\n#tamper\n' >> "$R/governance/generated/adapters/api/system-instruction.txt"
n0=$(ls "$R/spec/tasks" | grep -c TASK);
gp "$R" "{'verdict':(r or det)['verdict'],'remediation':(r or det)['remediation']}" doctor
AUDIT_PERSIST=1 audit_summary "$R" >/dev/null
gp "$R" "{'status':r['status'],'suggestion':r.get('suggestion')}" continue
gp "$R" "r" task replan
n1=$(ls "$R/spec/tasks" | grep -c TASK); echo "task records before/after doctor+audit+continue+replan: $n0 / $n1"

say "S9 stale evidence: an obsolete green is surfaced as a warning only (D021 medium → DEGRADED)"
R=$(clone "$B" sched-s9); yw "$R" spec/decisions/D-0005.yaml "{'id':'D-0005','type':'decision','title':'t','status':'ACTIVE','question':'q','chosen_option':'A'}"; g "$R" rebuild-memory --incremental >/dev/null 2>&1
doctor_summary "$R"

say "U<->O5 (AC-16): is any SLO/health breach observed without a human/agent invoking doctor or audit?"
R=$(clone "$B" sched-u); n0=$(ls "$R/spec/audits" | grep -c AUD)
printf 'pub const K: &str = "AKIAIOSFODNN7EXAMPLE";\n' > "$R/src/creds.rs"; ( cd "$R" && git add -A && git commit -qm s ) >/dev/null 2>&1
T=$(new_task "$R" documentation 'docs/**'); gp "$R" "ok" task claim "$T" >/dev/null; gp "$R" "ok" checkpoint create --next-action x >/dev/null; gp "$R" "ok" status >/dev/null
n1=$(ls "$R/spec/audits" | grep -c AUD)
echo "audit records before/after task create+claim+checkpoint+status: $n0 / $n1"
python3 -c "
import json; ev=[json.loads(l) for l in open('$R/.governance-runtime/telemetry/events.jsonl')]
print('telemetry event names in this project:', sorted(set(e['name'] for e in ev)))"
