"""Both figures together from W2-61 measure records (W2-87 lead): totals, per question, gov_file, comparisons.
Scores only: ids, counts, ranks; never a question's text or gold."""
import json
import sys

for path in sys.argv[1:]:
    data = json.load(open(path))
    print("==", path.rsplit("/", 1)[-1])
    print("retriever:", json.dumps(data["retriever"])[:400])
    print("commit:", data.get("commit"), "| budget:", data.get("budget"))
    print("total:", json.dumps(data["total"])[:600])
    for q in data["questions"]:
        keep = {k: q.get(k) for k in ("id", "hit_at_5", "first_gold_rank", "in_bundle", "full_evidence", "found",
                                      "needed", "calls", "compare", "comparison", "same")}
        print("  ", json.dumps({k: v for k, v in keep.items() if v is not None})[:300])
    if len(sys.argv) == 2:
        print("question keys:", sorted(data["questions"][0]))
