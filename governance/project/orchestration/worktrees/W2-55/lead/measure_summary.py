import json
import sys

def load(p):
    return json.load(open(p, encoding="utf-8"))

control, head = load(sys.argv[1]), load(sys.argv[2])
for name, rec in (("control", control), ("head", head)):
    t = rec["total"]
    inb = sum(1 for q in rec["questions"] if q.get("in_bundle"))
    print(name, rec["retriever"]["version"], "commit", rec["commit"], "hit@5", t["hit_at_5"]["count"], "full",
          t["full_evidence"]["count"], "in bundle", inb)
print("question keys:", sorted(control["questions"][0].keys()))
by_c = {q["id"]: q for q in control["questions"]}
for q in head["questions"]:
    c = by_c[q["id"]]
    diffs = [k for k in ("hit_at_5", "in_bundle", "full_evidence", "first_gold_rank", "found", "needed")
             if q.get(k) != c.get(k)]
    print(q["id"], "head", q.get("hit_at_5"), q.get("first_gold_rank"), q.get("in_bundle"), q.get("full_evidence"),
          f"{q.get('found')}/{q.get('needed')}", "| control", c.get("hit_at_5"), c.get("first_gold_rank"),
          c.get("in_bundle"), c.get("full_evidence"), f"{c.get('found')}/{c.get('needed')}", "| differs:", diffs)
