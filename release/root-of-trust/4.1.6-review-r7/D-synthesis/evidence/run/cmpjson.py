import json, sys, hashlib
def leaves(o, p=""):
    if isinstance(o, dict):
        for k, v in o.items(): yield from leaves(v, p + "/" + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o): yield from leaves(v, p + "[%d]" % i)
    else: yield p, o
a, b = sys.argv[1], sys.argv[2]
ra, rb = open(a, 'rb').read(), open(b, 'rb').read()
if ra == rb: print("BYTE_IDENTICAL", a.split('/')[-1]); sys.exit(0)
try:
    ja, jb = dict(leaves(json.loads(ra))), dict(leaves(json.loads(rb)))
except Exception as e:
    print("NOT_JSON_DIFFER", a.split('/')[-1], e); sys.exit(1)
diff = sorted(k for k in set(ja) | set(jb) if ja.get(k, "<absent>") != jb.get(k, "<absent>"))
print("DIFFER", a.split('/')[-1], len(diff), "leaves")
for k in diff[:15]: print("  ", k, "|", str(ja.get(k, "<absent>"))[:120], "|", str(jb.get(k, "<absent>"))[:120])
