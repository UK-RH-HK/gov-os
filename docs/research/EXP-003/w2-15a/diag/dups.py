import json, subprocess, sys, collections
gov = sys.argv[1]; tok=None; seen=collections.defaultdict(list); n=0
for call in range(4):
    out = subprocess.run([gov,"retrieve","--ticket","DAEO-ym8a","--radius","1","--bundle-budget","8000",*(["--continue",tok] if tok else []),"Which tickets depend on W2-03?","--json"],capture_output=True,text=True,check=True)
    b=json.loads(out.stdout); b=b.get("result",b)
    for e in b["evidence"]:
        seen[e["sha256"]].append((call+1,e["path"],e["start_line"],e["end_line"]))
    tok=b.get("continuation")
for h,v in seen.items():
    if len(v)>1: print(h[:12], v)
