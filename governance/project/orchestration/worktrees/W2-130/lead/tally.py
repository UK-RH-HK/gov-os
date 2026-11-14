import json,subprocess,re,collections,glob,yaml,sys
out=subprocess.run(["gov","links","--all","--json","--root","."],capture_output=True,text=True,env={**__import__('os').environ,"PYTHONPATH":"src"}).stdout
env=json.loads(out)
open(".gov-runtime/scratch/lead/links-all-start.json","w").write(out)
data=env["result"]; print(list(data.keys()))
fs=data.get("findings") or (data.get("new",[])+data.get("standing",[]))
print(list(data.keys())[:20], len(fs))
st={}
for p in glob.glob(".tickets/*.md"):
    t=open(p).read(); fm=yaml.safe_load(t.split("---",2)[1]); st[p]=fm.get("status")
c=collections.Counter(); role=collections.Counter()
ul=collections.Counter()
for f in fs:
    c[f["code"]]+=1; role[(f["code"],f.get("role"))]+=1
    if f["code"]=="UNLINKED_ID":
        ul[st.get(f.get("path"),"?")]+=1
print(c); print(ul)
for k,v in sorted(role.items()): print(k,v)
print(json.dumps(fs[0],indent=0)[:800])
