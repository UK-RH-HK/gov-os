import json, sys
d = json.load(sys.stdin)
r = d.get("result") or d.get("error")
fs = []
def walk(x):
    if isinstance(x, dict):
        if "message" in x and "severity" in x:
            fs.append(x)
        for v in x.values():
            walk(v)
    elif isinstance(x, list):
        for v in x:
            walk(v)
walk(r)
hits = [f for f in fs if "Qualification Oracle material" in f.get("message", "")]
seen = set()
uniq = [h for h in hits if not (h.get("message") in seen or seen.add(h.get("message")))]
print("total findings: %d | hidden-oracle findings: %d (%d distinct message(s))" % (len(fs), len(hits), len(uniq)))
for h in uniq:
    print("  -", h.get("severity"), "|", h.get("message")[:200])
