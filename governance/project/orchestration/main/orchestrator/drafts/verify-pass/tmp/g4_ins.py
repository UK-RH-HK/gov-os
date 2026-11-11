import re, sys, json
# usage: g4_ins.py <ticket file> <json file of [[line-start-text, verify-text], ...]>
# line-start-text: text right after the opening quote of the KPI line; verify-text with plain apostrophes (doubled here)
p = sys.argv[1]
V = json.load(open(sys.argv[2]))
lines = open(p).read().split('\n')
for start, verify in V:
    hit = [i for i, l in enumerate(lines) if l.startswith("  - '" + start.replace("'", "''"))]
    assert len(hit) == 1, (start, hit)
    l = lines[hit[0]]
    assert 'Verify:' not in l, start
    v = verify.replace("'", "''")
    m = re.search(r" (\[[^\]]*\](?: \[[^\]]*\]| \([^)]*\))*)'$", l)
    if m:
        l = l[:m.start()] + " Verify: " + v + " " + m.group(1) + "'"
    else:
        assert l.endswith("'"), start
        l = l[:-1] + " Verify: " + v + "'"
    lines[hit[0]] = l
open(p, 'w').write('\n'.join(lines))
print('ok', len(V))
