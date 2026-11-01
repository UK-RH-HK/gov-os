"""Summarise measure --json outputs (scores only), side by side.
usage: python3 scores.py <label>=<measure json> [<label>=<measure json>]..."""
import json
import sys

runs = []
for arg in sys.argv[1:]:
    label, path = arg.split("=", 1)
    text = open(path).read()
    runs.append((label, json.loads(text[text.find("{"):])))


def cell(q):
    return "{}, {}, {}, {} ({}/{})".format("yes" if q["hit_at_5"] else "no", q["first_gold_rank"] or "none",
                                         "yes" if q["in_bundle"] else "no", "yes" if q["full_evidence"] else "no",
                                         q["pieces_found"], q["pieces_needed"])


for label, data in runs:
    total = data["total"]
    bundle = sum(1 for q in data["questions"] if q["in_bundle"])
    print(f"{label}: commit {data['commit']} retriever {data['retriever']['gov_file']}")
    print(f"  hit@5 {total['hit_at_5']['count']} of {total['hit_at_5']['of']} ({total['hit_at_5']['percent']} %), "
          f"floor {total['hit_at_5']['floor']}; full evidence {total['full_evidence']['count']} of "
          f"{total['full_evidence']['of']} ({total['full_evidence']['percent']} %), target "
          f"{total['full_evidence']['target']}; in the bundle {bundle} of {total['questions']}")
    if data.get("compare") or data.get("comparison"):
        print("  compare:", json.dumps(data.get("compare") or data.get("comparison"))[:1500])

print("| Q | " + " | ".join(label for label, _ in runs) + " |")
for index, q in enumerate(runs[0][1]["questions"]):
    print(f"| {q['id']} | " + " | ".join(cell(data["questions"][index]) for _, data in runs) + " |")
if len(runs) > 1:
    print("digest differs:", [q["id"] for i, q in enumerate(runs[0][1]["questions"])
                              if q["stacked_digest"] != runs[-1][1]["questions"][i]["stacked_digest"]])
