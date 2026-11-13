import sys
p = sys.argv[1]
t = open(p, encoding="utf-8").read()
old = 'assert done.returncode == 0 and statuses.get(OPENSPEC_CHECK) == "YELLOW", ('
new = 'assert done.returncode != 0 and statuses.get(OPENSPEC_CHECK) == "RED", ('
assert t.count(old) == 1, "fixture line not found once"
t = t.replace(old, new)
open(p, "w", encoding="utf-8").write(t)
