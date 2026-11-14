import json, subprocess, collections, glob, yaml, sys, os
# usage: python3 tally2.py <out.json>   (run in the tree root)
outp = sys.argv[1]
r = subprocess.run([sys.executable, "-m", "gov.cli.main", "links", "--all", "--json", "--root", "."],
                   capture_output=True, text=True, env={**os.environ, "PYTHONPATH": "src"})
open(outp, "w").write(r.stdout)
env = json.loads(r.stdout)
data = env["result"]
fs = data.get("findings") or (data.get("new", []) + data.get("standing", []))
st = {}
for p in glob.glob(".tickets/*.md"):
    t = open(p).read()
    fm = yaml.safe_load(t.split("---", 2)[1])
    st[p] = fm.get("status")
c = collections.Counter(f["code"] for f in fs)
print("total", len(fs), dict(c))
for code in ("UNMARKED_CHANGE", "STATUS_CONFLICT"):
    for f in fs:
        if f["code"] == code:
            print(code, json.dumps(f)[:400])
ul = [f for f in fs if f["code"] == "UNLINKED_ID" and st.get(f.get("path")) in ("open", "in_progress")]
print("UNLINKED_ID open/in_progress:", len(ul))
for f in ul:
    print("  ", json.dumps(f)[:300])
for f in fs:
    if f["code"] == "UNKNOWN_ID" and "lessons" in (f.get("path") or ""):
        print("UNKNOWN_ID lesson", json.dumps(f)[:300])
