import json, sys
sys.path.insert(0, "/home/usain/gov-os-worktrees/W2-130/tests/acceptance/W2-130")
import w2_130_support as s
L = "/home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/lead/"
d = json.load(open(L + "census-m6.json"))
by = {}
for c, rows in d["drift_examples"].items():
    for r in rows:
        by.setdefault(r["id"], set()).update(r["by"])
key = lambda x: int(x[4:])
census = {i: sorted(v, key=key) for i, v in sorted(by.items(), key=lambda kv: key(kv[0]))}
ids87 = [l.strip() for l in open(L + "census-87.txt") if l.strip()]
print("census", len(census), "87", len(ids87), "87 in census", all(i in census for i in ids87))
lines = {e: line for e, _, line in s.entries(open("/home/usain/gov-os-worktrees/W2-130/docs/DECISION_REGISTER.md").read())}
miss = [(e, c) for e, cs in census.items() for c in cs if not s.names_changer(lines[e], c)]
loose = [(e, c) for e, c in miss if c not in lines[e]]
print("strict miss", len(miss)); print(miss)
print("loose miss", len(loose))
json.dump({"census": census, "ids87": ids87}, open(L + "rec/census.json", "w"), indent=1)
