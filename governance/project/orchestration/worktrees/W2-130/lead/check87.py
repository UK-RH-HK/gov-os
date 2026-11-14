import json,re,sys
sys.path.insert(0,"src")
from gov.store.loader import register_entries
d=json.load(open(".gov-runtime/scratch/lead/census-m6.json"))
ex=d["drift_examples"]
by={}
for c in ex:
    for r in ex[c]:
        by.setdefault(r["id"],set()).update(r["by"])
nh=[l.strip() for l in open(".gov-runtime/scratch/lead/census-87.txt") if l.strip()]
entries,_=register_entries(open("docs/DECISION_REGISTER.md").read())
E={e["id"]:e for e in entries}
def report(ids,label):
    miss=[]
    for i in ids:
        first=E[i]["first"]
        m=[s for s in sorted(by[i],key=lambda x:int(x[4:])) if not re.search(rf"\b{s}(?![0-9])",first)]
        if m: miss.append((i,m))
    print(label,len(ids),"ids; status line misses a changer:",len(miss))
    for i,m in miss: print("  ",i,"<-",",".join(m), "| status:", re.sub(r"\s+"," ",E[i]["first"])[:110])
report(nh,"87")
report(sorted(set(by)-set(nh),key=lambda x:int(x[4:])),"other 128")
