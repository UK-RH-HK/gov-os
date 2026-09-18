#!/usr/bin/env bash
# O2 bullet "context reproducibility" — exercise the family's core comparison (two in-process compiles of the same
# task's deterministic block must hash equal). The deterministic block embeds the control mode read from
# .governance-runtime/control.json; a concurrent writer flipping that file while the family runs makes the two
# compiles see different state. The family must report "deterministic authority block not reproducible".
source "$(dirname "$0")/lib.sh"
B=$(base_project)
R=$(clone "$B" o2-ctx-race)
yw "$R" spec/tasks/TASK-0950.yaml "{'id':'TASK-0950','type':'task','title':'ctx race','status':'ACTIVE','task_status':'READY','class':'documentation','objective':'probe','allowed_paths':['docs/**']}"
CJ="$R/.governance-runtime/control.json"
say "control-mode toggler running concurrently with the context_reproducibility family (up to 40 attempts)"
python3 - "$CJ" <<'EOF' &
import json,sys,time
p=sys.argv[1]; end=time.time()+120; i=0
while time.time()<end:
    m="RUNNING" if i%2==0 else "PAUSED"
    tmp=p+".tmp"; json.dump({"mode":m,"writes_frozen":False,"agents_cancelled":False,"updated_at":None,"reason":"probe"},open(tmp,"w"));
    import os; os.replace(tmp,p); i+=1
EOF
TOG=$!
hit=0
for i in $(seq 1 40); do
  out=$(gp "$R" "{'ok':(r or det)['families']['context_reproducibility']['ok'],'findings':[(f['severity'],f['message'][:120]) for f in (r or det)['findings'] if f['family']=='context_reproducibility']}" audit --no-persist --family context_reproducibility)
  case "$out" in *"not reproducible"*) echo "attempt $i: $out"; hit=1; break;; esac
done
kill $TOG 2>/dev/null; wait $TOG 2>/dev/null
[ $hit = 1 ] && note "irreproducible deterministic block detected by the family" || note "no irreproducibility observed in 40 attempts (last: $out)"
say "control: without the toggler the same project is reproducible"
python3 -c "import json; json.dump({'mode':'RUNNING','writes_frozen':False,'agents_cancelled':False,'updated_at':None,'reason':None},open('$CJ','w'))"
gp "$R" "{'ok':r['families']['context_reproducibility']['ok'],'findings':[(f['severity'],f['message'][:120]) for f in r['findings'] if f['family']=='context_reproducibility']}" audit --no-persist --family context_reproducibility
