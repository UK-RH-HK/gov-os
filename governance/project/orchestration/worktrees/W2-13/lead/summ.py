"""summ.py <measure json>...: the totals and per-question cells of each measure run (ids, ranks and counts only)."""
import json
import sys

runs = [json.load(open(path)) for path in sys.argv[1:]]
for run in runs:
    qs = run["questions"]
    print(run["commit"], run["retriever"]["executable"].rsplit("/", 1)[-1],
          "hit@5", sum(q["hit_at_5"] for q in qs), "full", sum(q["full_evidence"] for q in qs),
          "in_bundle", sum(q["in_bundle"] for q in qs), "of", len(qs))
print("Q   " + " | ".join(run["retriever"]["executable"].rsplit("/", 1)[-1] for run in runs))
for index, q in enumerate(runs[0]["questions"]):
    cells = []
    for run in runs:
        r = run["questions"][index]
        cells.append(f"{'yes' if r['hit_at_5'] else 'no'}, {r['first_gold_rank'] or 'none'}, "
                     f"{'yes' if r['in_bundle'] else 'no'}, {'yes' if r['full_evidence'] else 'no'} "
                     f"({r['pieces_found']}/{r['pieces_needed']})")
    print(q["id"], " | ".join(cells))
