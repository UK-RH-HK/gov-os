"""Print a baseline run's header, totals and per-question figures (visible half only)."""
import json
import sys

doc = json.load(open(sys.argv[1], encoding="utf-8"))
for key in ("retriever", "root", "commit", "set", "part", "budget", "total"):
    print(key, json.dumps(doc.get(key)))
for q in doc["questions"]:
    compare = q.get("compare")
    print(q["id"], "hit5", q["hit_at_5"], "bundle", q["in_bundle"], "full", q["full_evidence"],
          "rank", q["first_gold_rank"], "pieces", q["pieces_found"], "/", q["pieces_needed"], "calls", q["calls"],
          "compare", json.dumps(compare) if compare is not None else "-")
print("keys", sorted(doc))
print("question keys", sorted(doc["questions"][0]))
