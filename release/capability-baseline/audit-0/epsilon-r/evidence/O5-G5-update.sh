#!/usr/bin/env bash
# O5 tier G5 "Full Suite — adopt/update/release/full audit" (Contract v3 line 798), update leg: does `gov update --apply`
# run the full governance suite? Seed a defect only a family outside the update subset detects (graph_integrity: a DAG
# cycle), then update 4.1.1 → candidate.
source "$(dirname "$0")/lib.sh"
P="$SCRATCH/g5-upd"; rm -rf "$P" "$P.machine"; mkdir -p "$P"; echo "# upd" > "$P/README.md"; git_base "$P" >/dev/null 2>&1
printf 'init from previous release 4.1.1: '; gp "$P" "{'ok':ok,'version':(r or {}).get('version'),'err':e.get('code') if e else None}" init --source "$WT/fixtures/update/previous-release/4.1.1" --name upd --alias fx-upd
yw "$P" spec/tasks/TASK-0001.yaml "{'id':'TASK-0001','type':'task','title':'a','status':'ACTIVE','task_status':'READY','class':'documentation','objective':'o','dependencies':['TASK-0002']}"
yw "$P" spec/tasks/TASK-0002.yaml "{'id':'TASK-0002','type':'task','title':'b','status':'ACTIVE','task_status':'READY','class':'documentation','objective':'o','dependencies':['TASK-0001']}"
g "$P" rebuild-memory >/dev/null 2>&1; git_commit "$P" "state with a DAG cycle"
printf 'update --apply (no approval): '; out=$(g "$P" update --apply 2>/dev/null); echo "$out" | python3 -c "import json,sys;d=json.load(sys.stdin);print((d.get('error') or {}).get('code'), (d.get('error') or {}).get('details',{}).get('gate'))"
GID=$(echo "$out" | python3 -c "import json,sys;print(json.load(sys.stdin)['error']['details']['gate'])")
gp "$P" "ok" gate present "$GID" >/dev/null; ROLE=human gp "$P" "ok" decide "$GID" --option A --by owner >/dev/null
printf 'update --apply --approve: '; gp "$P" "{'ok':ok,'applied':(r or {}).get('applied'),'err':e.get('code') if e else None,'post_install_verification':{k:v for k,v in (r or {}).items() if k in ('doctor','audit')} or {k:(v.get('doctor'),v.get('audit')) for k,v in (r or {}).items() if isinstance(v,dict) and ('audit' in v or 'doctor' in v)},'result_keys':sorted(r or {})}" update --apply --approve --by owner
printf 'installed version now: '; gp "$P" "r['framework']['version']" status
printf 'full suite on the updated project: '; audit_summary "$P"
